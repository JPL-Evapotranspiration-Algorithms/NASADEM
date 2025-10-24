from typing import Union
import json
import logging
import os
import posixpath
from os import makedirs
from os.path import exists, splitext, basename, join, expanduser, abspath, dirname
from typing import List
from zipfile import ZipFile

import numpy as np
from shapely.geometry import Polygon

import colored_logging as cl
from .LPDAAC import LPDAACDataPool
from rasters import Raster, RasterGeometry, RasterGrid, Point, MultiPoint
import rasters

from .timer import Timer
import pandas as pd

DEFAULT_WORKING_DIRECTORY = join("~", "data", "NASADEM")
DEFAULT_DOWNLOAD_DIRECTORY = DEFAULT_WORKING_DIRECTORY

SRTM_FILENAMES_CSV = join(abspath(dirname(__file__)), "filenames.csv")

logger = logging.getLogger(__name__)

class NASADEMGranule:
    def __init__(self, filename: str):
        if not exists(filename):
            raise IOError(f"SRTM file not found: {filename}")

        self.filename = filename
        self._geometry = None

    @property
    def tile(self):
        return splitext(basename(self.filename))[0].split("_")[-1]

    @property
    def hgt_URI(self) -> str:
        return f"zip://{self.filename}!/{self.tile.lower()}.hgt"


    def get_elevation_m(self, geometry: Union[RasterGeometry, Point, MultiPoint] = None) -> Raster:
        URI = self.hgt_URI
        logger.info(f"loading elevation: {cl.URL(URI)}")
        data = Raster.open(URI, geometry=geometry)

        if isinstance(data, Raster):
            data = rasters.where(data == data.nodata, np.nan, data.astype(np.float32))
            data.nodata = np.nan

        return data

    elevation_m = property(get_elevation_m)

    # @property
    # def ocean(self) -> Raster:
    #     return self.elevation_m == 0

    @property
    def geometry(self) -> RasterGrid:
        if self._geometry is None:
            self._geometry = RasterGrid.open(self.hgt_URI)

        return self._geometry

    @property
    def swb_URI(self) -> str:
        return f"zip://{self.filename}!/{self.tile.lower()}.swb"

    def get_swb(self, geometry: Union[RasterGeometry, Point, MultiPoint] = None) -> Raster:
        URI = self.swb_URI
        
        if geometry is None:
            geometry = self.geometry

        filename = self.filename
        member_name = f"{self.tile.lower()}.swb"
        logger.info(f"loading swb: {cl.URL(URI)}")

        with ZipFile(filename, "r") as zip_file:
            with zip_file.open(member_name, "r") as file:
                data = Raster(np.frombuffer(file.read(), dtype=np.int8).reshape(geometry.shape), geometry=geometry)

        data = data != 0

        return data
    
    swb = property(get_swb)


class TileNotAvailable(ValueError):
    pass


class NASADEMConnection(LPDAACDataPool):
    # logger = logging.getLogger(__name__)

    def __init__(
            self,
            username: str = None,
            password: str = None,
            remote: str = None,
            working_directory: str = None,
            download_directory: str = None,
            offline_ok: bool = True):
        super(NASADEMConnection, self).__init__(username=username, password=password, remote=remote, offline_ok=offline_ok)

        if working_directory is None:
            working_directory = DEFAULT_WORKING_DIRECTORY
        self.working_directory = abspath(expanduser(working_directory))
        logger.info(f"SRTM working directory: {cl.dir(working_directory)}")

        if download_directory is None:
            download_directory = DEFAULT_DOWNLOAD_DIRECTORY
        self.download_directory = abspath(expanduser(download_directory))
        logger.info(f"SRTM download directory: {cl.dir(download_directory)}")

        self._filenames = None

    def __repr__(self):
        display_dict = {
            "URL": self.remote,
            "download_directory": self.download_directory
        }

        display_string = json.dumps(display_dict, indent=2)

        return display_string

    @property
    def filenames(self) -> List[str]:
        if self._filenames is None:
            self._filenames = list(pd.read_csv(SRTM_FILENAMES_CSV)["filename"])

        return self._filenames

    def tile_URL(self, tile: str) -> str:
        return posixpath.join(
            self.remote,
            "MEASURES",
            "NASADEM_HGT.001",
            "2000.02.11",
            f"NASADEM_HGT_{tile.lower()}.zip"
        )
    
    def tile_filename(self, tile: str) -> str:
        return join(
            self.download_directory,
            f"NASADEM_HGT_{tile.lower()}.zip"
        )

    def tiles_intersecting_bbox(self, lon_min, lat_min, lon_max, lat_max):
        tiles = []

        for lat in range(int(np.floor(lat_min)), int(np.floor(lat_max)) + 1):
            for lon in range(int(np.floor(lon_min)), int(np.floor(lon_max)) + 1):
                tiles.append(f"{'s' if lat < 0 else 'n'}{abs(lat):02d}{'w' if lon < 0 else 'e'}{abs(lon):03d}")

        tiles = sorted(tiles)

        return tiles

    def tiles_intersecting_polygon(self, polygon: Polygon):
        lons, lats = polygon.exterior.xy
        lon_min, lon_max = np.nanmin(lons), np.nanmax(lons)
        lat_min, lat_max = np.nanmin(lats), np.nanmax(lats)

        return self.tiles_intersecting_bbox(lon_min, lat_min, lon_max, lat_max)

    def tiles_intersecting_point(self, point: Point):
        return self.tiles_intersecting_bbox(point.x, point.y, point.x, point.y)

    def tiles_intersecting_multipoint(self, multipoint: MultiPoint):
        return self.tiles_intersecting_bbox(multipoint.xmin, multipoint.ymin, multipoint.xmax, multipoint.ymax)

    def tiles(self, geometry: Union[Polygon, RasterGeometry, Point, MultiPoint]) -> List[str]:
        if isinstance(geometry, Polygon):
            return self.tiles_intersecting_polygon(geometry)
        elif isinstance(geometry, RasterGeometry):
            return self.tiles_intersecting_polygon(geometry.boundary_latlon)
        elif isinstance(geometry, Point):
            return self.tiles_intersecting_point(geometry)
        elif isinstance(geometry, MultiPoint):
            return self.tiles_intersecting_multipoint(geometry)
        else:
            raise ValueError("invalid target geometry")

    def download_tile(self, tile: str, enforce_checksum: bool = False) -> NASADEMGranule:
        filename = self.tile_filename(tile)

        if not exists(filename):
            URL = self.tile_URL(tile)
            filename_base = posixpath.basename(URL)

            if filename_base not in self.filenames:
                raise TileNotAvailable(f"SRTM does not cover tile {tile}")

            directory = self.download_directory
            makedirs(directory, exist_ok=True)
            logger.info(f"acquiring SRTM tile: {cl.val(tile)} URL: {cl.URL(URL)}")
            filename = self.download_URL(URL, directory, enforce_checksum=enforce_checksum)

        granule = NASADEMGranule(filename)

        return granule

    def swb(self, geometry: Union[RasterGeometry, Point, MultiPoint]):
        """
        digital elevation model surface water body from the Shuttle Rader Topography Mission (SRTM)
        :param geometry: target geometry
        :return: raster of elevation for RasterGeometry, values for Point/MultiPoint
        """
        if isinstance(geometry, (Point, MultiPoint)):
            return self._extract_point_values(geometry, 'swb')
        
        result = Raster(np.full(geometry.shape, np.nan, dtype=np.float32), geometry=geometry)
        tiles = self.tiles(geometry)

        for tile in tiles:
            # logger.info(f"acquiring SRTM tile {tile}")
            try:
                granule = self.download_tile(tile)
            except TileNotAvailable as e:
                logger.warning(e)
                continue
            
            image = granule.swb.astype(np.float32)
            image_projected = image.to_geometry(geometry)
            result = rasters.where(np.isnan(result), image_projected, result)

        result = rasters.where(np.isnan(result), 1, result)
        result = result.astype(bool)

        return result

    def elevation_m(self, geometry: Union[RasterGeometry, Point, MultiPoint]):
        """
        digital elevation model (elevation_km) in meters from the Shuttle Rader Topography Mission (SRTM)
        :param geometry: target geometry
        :return: raster of elevation for RasterGeometry, values for Point/MultiPoint
        """
        if isinstance(geometry, MultiPoint):
            return self._extract_point_values(geometry, 'elevation_m')
        
        result = None
        tiles = self.tiles(geometry)

        for tile in tiles:
            # logger.info(f"acquiring SRTM tile {tile}")
            try:
                granule = self.download_tile(tile)
            except TileNotAvailable as e:
                logger.warning(e)
                continue

            elevation_m = granule.get_elevation_m(geometry=geometry)
            print(elevation_m)
            # elevation_projected = elevation_m.to_geometry(geometry)

            if result is None:
                result = elevation_m
            elif isinstance(result, Raster):
                result = rasters.where(np.isnan(result), elevation_m, result)

        return result

    def elevation_km(self, geometry: Union[RasterGeometry, Point, MultiPoint]):
        """
        digital elevation model (elevation_km) in kilometers from the Shuttle Rader Topography Mission (SRTM)
        :param geometry: target geometry
        :return: raster of elevation for RasterGeometry, values for Point/MultiPoint
        """
        return self.elevation_m(geometry=geometry) / 1000

    def _extract_point_values(self, geometry: Union[Point, MultiPoint], data_type: str):
        """
        Extract values at point locations from NASADEM data
        :param geometry: Point or MultiPoint geometry
        :param data_type: 'elevation_m' or 'swb'
        :return: single value for Point, array of values for MultiPoint
        """
        tiles = self.tiles(geometry)
        
        if isinstance(geometry, Point):
            points = [geometry]
        else:
            points = [Point(geom.x, geom.y) for geom in geometry.geoms]
        
        values = []
        
        for point in points:
            point_value = np.nan
            
            for tile in tiles:
                try:
                    granule = self.download_tile(tile)
                except TileNotAvailable as e:
                    logger.warning(e)
                    continue
                
                # Get the appropriate data layer
                if data_type == 'elevation_m':
                    data_layer = granule.elevation_m
                elif data_type == 'swb':
                    data_layer = granule.swb.astype(np.float32)
                else:
                    raise ValueError(f"Unknown data type: {data_type}")
                
                # Check if point is within this tile's bounds
                tile_geometry = data_layer.geometry
                if (tile_geometry.x_min <= point.x <= tile_geometry.x_max and 
                    tile_geometry.y_min <= point.y <= tile_geometry.y_max):
                    
                    # Extract value at point location
                    try:
                        point_raster = data_layer.to_point(point)
                        if hasattr(point_raster, 'values') and len(point_raster.values) > 0:
                            point_value = point_raster.values[0]
                        else:
                            point_value = np.nan
                        if not np.isnan(point_value):
                            break  # Found valid value, stop searching tiles
                    except Exception as e:
                        logger.warning(f"Failed to sample point ({point.x}, {point.y}) from tile {tile}: {e}")
                        continue
            
            values.append(point_value)
        
        # Apply post-processing for swb
        if data_type == 'swb':
            values = [bool(v != 0) if not np.isnan(v) else False for v in values]
        
        # Return single value for Point, array for MultiPoint
        if isinstance(geometry, Point):
            return values[0]
        else:
            return np.array(values)

NASADEM = NASADEMConnection()
