from typing import Union
import json
import logging
import os
from os import makedirs
from os.path import exists, splitext, basename, join, expanduser, abspath
from typing import List
from zipfile import ZipFile

import earthaccess
import numpy as np
from shapely.geometry import Polygon

import colored_logging as cl
from rasters import Raster, RasterGeometry, RasterGrid, Point, MultiPoint
import rasters


DEFAULT_WORKING_DIRECTORY = join("~", "data", "NASADEM")
DEFAULT_DOWNLOAD_DIRECTORY = DEFAULT_WORKING_DIRECTORY

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
        logger.info(f"elevation data shape: {data.shape}, nodata: {data.nodata}")

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


class NASADEMConnection:
    """
    Connection to NASADEM data using NASA's earthaccess package.
    
    This class provides methods to search, download, and extract elevation data
    from the NASADEM dataset via NASA's Earthdata Cloud infrastructure.
    """

    def __init__(
            self,
            username: str = None,
            password: str = None,
            working_directory: str = None,
            download_directory: str = None,
            persist_credentials: bool = False,
            skip_auth: bool = False):
        """
        Initialize NASADEM connection.
        
        Args:
            username: NASA Earthdata username (optional, can use .netrc or env vars)
            password: NASA Earthdata password (optional, can use .netrc or env vars)
            working_directory: Directory for working files
            download_directory: Directory for downloaded tiles
            persist_credentials: Whether to persist credentials to .netrc file
            skip_auth: Skip authentication (useful for testing or when auth is handled separately)
        """
        # Authenticate with earthaccess (unless explicitly skipped)
        if not skip_auth:
            # Check if we're in a non-interactive environment (like CI)
            # by checking for common CI environment variables
            is_ci = any([
                os.environ.get('CI'),
                os.environ.get('GITHUB_ACTIONS'),
                os.environ.get('TRAVIS'),
                os.environ.get('CIRCLECI'),
            ])
            
            # Only attempt login if we have credentials or are not in CI
            if username and password:
                earthaccess.login(username=username, password=password, persist=persist_credentials)
            elif not is_ci:
                # Will use .netrc, environment variables, or prompt interactively
                earthaccess.login(persist=persist_credentials)

        if working_directory is None:
            working_directory = DEFAULT_WORKING_DIRECTORY
        self.working_directory = abspath(expanduser(working_directory))

        if download_directory is None:
            download_directory = DEFAULT_DOWNLOAD_DIRECTORY
        self.download_directory = abspath(expanduser(download_directory))
        makedirs(self.download_directory, exist_ok=True)

    def __repr__(self):
        display_dict = {
            "download_directory": self.download_directory,
            "working_directory": self.working_directory
        }
        return json.dumps(display_dict, indent=2)
    
    def tile_filename(self, tile: str) -> str:
        """Get the local filename for a tile."""
        return join(
            self.download_directory,
            f"NASADEM_HGT_{tile.upper()}.zip"
        )

    def search_tile(self, tile: str):
        """
        Search for a NASADEM tile using earthaccess.
        
        Args:
            tile: Tile identifier (e.g., 'n34w118', 's10e142')
            
        Returns:
            earthaccess granule result or None if not found
        """
        try:
            # Search for the granule by tile name
            results = earthaccess.search_data(
                short_name='NASADEM_HGT',
                version='001',
                granule_name=f'*{tile.upper()}*'
            )
            
            if results:
                return results[0]
            return None
            
        except Exception as e:
            logger.warning(f"Error searching for tile {tile}: {e}")
            return None

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

    def download_tile(self, tile: str) -> NASADEMGranule:
        """
        Download a NASADEM tile using earthaccess.
        
        Args:
            tile: Tile identifier (e.g., 'n34w118', 's10e142')
            
        Returns:
            NASADEMGranule object for the downloaded tile
            
        Raises:
            TileNotAvailable: If the tile doesn't exist or can't be downloaded
        """
        filename = self.tile_filename(tile)

        if not exists(filename):
            logger.info(f"acquiring NASADEM tile: {cl.val(tile)}")
            
            # Search for the granule
            granule = self.search_tile(tile)
            
            if not granule:
                raise TileNotAvailable(f"NASADEM does not cover tile {tile}")
            
            try:
                # Download the file using earthaccess
                files = earthaccess.download(
                    granule,
                    local_path=self.download_directory
                )
                
                if files:
                    # earthaccess returns a list of downloaded files
                    downloaded_file = files[0]
                    
                    # Rename to our expected filename if different
                    if downloaded_file != filename:
                        import shutil
                        shutil.move(downloaded_file, filename)
                    
                    logger.info(f"downloaded NASADEM tile: {cl.file(filename)}")
                else:
                    raise TileNotAvailable(f"Failed to download tile {tile}")
                    
            except Exception as e:
                logger.error(f"Error downloading tile {tile}: {e}")
                raise TileNotAvailable(f"Failed to download tile {tile}: {e}")

        return NASADEMGranule(filename)

    def swb(self, geometry: Union[RasterGeometry, Point, MultiPoint]):
        """
        Surface water body from NASADEM.
        
        Args:
            geometry: Target geometry (RasterGeometry, Point, or MultiPoint)
            
        Returns:
            Boolean raster for RasterGeometry, boolean value(s) for Point/MultiPoint
        """
        if isinstance(geometry, (Point, MultiPoint)):
            return self._extract_point_values(geometry, 'swb')
        
        result = Raster(np.full(geometry.shape, np.nan, dtype=np.float32), geometry=geometry)
        tiles = self.tiles(geometry)

        for tile in tiles:
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
        Digital elevation model in meters from NASADEM.
        
        Args:
            geometry: Target geometry (RasterGeometry, Point, or MultiPoint)
            
        Returns:
            Elevation raster for RasterGeometry, elevation value(s) for Point/MultiPoint
        """
        if isinstance(geometry, (Point, MultiPoint)):
            return self._extract_point_values(geometry, 'elevation_m')
        
        result = None
        tiles = self.tiles(geometry)

        for tile in tiles:
            try:
                granule = self.download_tile(tile)
            except TileNotAvailable as e:
                logger.warning(e)
                continue

            elevation_m = granule.get_elevation_m(geometry=geometry)

            if result is None:
                result = elevation_m
            elif isinstance(result, Raster):
                result = rasters.where(np.isnan(result), elevation_m, result)

        return result

    def elevation_km(self, geometry: Union[RasterGeometry, Point, MultiPoint]):
        """
        Digital elevation model in kilometers from NASADEM.
        
        Args:
            geometry: Target geometry (RasterGeometry, Point, or MultiPoint)
            
        Returns:
            Elevation raster in km for RasterGeometry, elevation value(s) in km for Point/MultiPoint
        """
        return self.elevation_m(geometry=geometry) / 1000

    def _extract_point_values(self, geometry: Union[Point, MultiPoint], data_type: str):
        """
        Extract values at point locations from NASADEM data.
        
        Args:
            geometry: Point or MultiPoint geometry
            data_type: 'elevation_m' or 'swb'
            
        Returns:
            Single value for Point, array of values for MultiPoint
        """
        if isinstance(geometry, Point):
            points = [geometry]
        else:
            points = [Point(geom.x, geom.y) for geom in geometry.geoms]
        
        # Group points by tile to minimize data loading
        from collections import defaultdict
        points_by_tile = defaultdict(list)
        
        for i, point in enumerate(points):
            # Calculate which tile this point belongs to
            lat, lon = point.y, point.x
            tile = f"{'s' if lat < 0 else 'n'}{abs(int(np.floor(lat))):02d}{'w' if lon < 0 else 'e'}{abs(int(np.floor(lon))):03d}"
            points_by_tile[tile].append((i, point))
        
        # Initialize results array
        values = [np.nan] * len(points)
        
        # Process each tile only once
        for tile, point_list in points_by_tile.items():
            try:
                granule = self.download_tile(tile)
            except TileNotAvailable as e:
                logger.warning(e)
                continue
            
            # Load the full tile data
            try:
                if data_type == 'elevation_m':
                    data_layer = granule.get_elevation_m(geometry=None)
                elif data_type == 'swb':
                    data_layer = granule.get_swb(geometry=None)
                else:
                    raise ValueError(f"Unknown data type: {data_type}")
                
                if not isinstance(data_layer, Raster):
                    logger.warning(f"Expected Raster, got {type(data_layer)}")
                    continue
                
                # Extract values for all points in this tile
                for idx, point in point_list:
                    try:
                        # Check if point is within tile bounds
                        tile_geometry = data_layer.geometry
                        if not (tile_geometry.x_min <= point.x <= tile_geometry.x_max and 
                                tile_geometry.y_min <= point.y <= tile_geometry.y_max):
                            continue
                        
                        # Convert geographic coordinates to pixel indices
                        row = int((tile_geometry.y_max - point.y) / abs(tile_geometry.cell_height))
                        col = int((point.x - tile_geometry.x_min) / abs(tile_geometry.cell_width))
                        
                        # Clip to array bounds
                        row = max(0, min(row, data_layer.shape[0] - 1))
                        col = max(0, min(col, data_layer.shape[1] - 1))
                        
                        # Extract the value
                        value = float(data_layer.array[row, col])
                        
                        # Store if valid
                        if not np.isnan(value) and value != data_layer.nodata:
                            values[idx] = value
                            
                    except Exception as e:
                        logger.warning(f"Failed to sample point ({point.x}, {point.y}) from tile {tile}: {e}")
                        continue
                        
            except Exception as e:
                logger.warning(f"Failed to load data from tile {tile}: {e}")
                continue
        
        # Apply post-processing for swb
        if data_type == 'swb':
            values = [bool(v != 0) if not np.isnan(v) else False for v in values]
        
        # Return single value for Point, array for MultiPoint
        if isinstance(geometry, Point):
            return values[0]
        else:
            return np.array(values)


# Lazy-loaded global instance for convenience
_NASADEM_INSTANCE = None

def _get_default_instance():
    """Get or create the default NASADEM instance."""
    global _NASADEM_INSTANCE
    if _NASADEM_INSTANCE is None:
        # In CI or testing environments, skip authentication by default
        is_ci = any([
            os.environ.get('CI'),
            os.environ.get('GITHUB_ACTIONS'),
            os.environ.get('TRAVIS'),
            os.environ.get('CIRCLECI'),
        ])
        _NASADEM_INSTANCE = NASADEMConnection(skip_auth=is_ci)
    return _NASADEM_INSTANCE

# Create a proxy class that lazily initializes the connection
class _NASADEMProxy:
    """Proxy to lazily initialize the default NASADEM connection."""
    
    def __getattr__(self, name):
        return getattr(_get_default_instance(), name)
    
    def __call__(self, *args, **kwargs):
        return _get_default_instance()(*args, **kwargs)

NASADEM = _NASADEMProxy()
