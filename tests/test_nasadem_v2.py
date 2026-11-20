"""
Tests for NASADEM v2.2.0 with earthaccess integration.

These tests verify the core functionality without requiring actual
NASA Earthdata credentials (using mocking and synthetic archives).
"""

import json
import zipfile
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np
import pytest


def _create_synthetic_granule_zip(zip_path: Path, tile: str = "n34w118", shape=(4, 4)):
    """Create a synthetic NASADEM zip archive containing .hgt and .swb rasters."""
    hgt_data = np.arange(1, shape[0] * shape[1] + 1, dtype=">i2").reshape(shape)
    hgt_data[0, 0] = -32768  # standard SRTM/NASADEM nodata value

    swb_data = np.zeros(shape, dtype=np.int8)
    swb_data[1, 1] = 1  # water pixel

    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr(f"{tile.lower()}.hgt", hgt_data.tobytes())
        zf.writestr(f"{tile.lower()}.swb", swb_data.tobytes())


def test_import_nasadem():
    """Test that NASADEM can be imported."""
    import NASADEM
    assert hasattr(NASADEM, 'NASADEMConnection')
    assert hasattr(NASADEM, 'NASADEM')
    assert hasattr(NASADEM, 'NASADEMGranule')


def test_version():
    """Test that version is accessible."""
    from NASADEM import __version__
    assert __version__ is not None
    assert isinstance(__version__, str)


def test_connection_init():
    """Test NASADEMConnection initialization."""
    with patch('earthaccess.login') as mock_login:
        from NASADEM import NASADEMConnection

        conn = NASADEMConnection(skip_auth=True)
        mock_login.assert_not_called()
        assert conn.download_directory is not None
        assert conn.working_directory is not None


def test_connection_with_credentials():
    """Test NASADEMConnection with explicit credentials."""
    with patch('earthaccess.login') as mock_login:
        from NASADEM import NASADEMConnection

        NASADEMConnection(
            username="test_user",
            password="test_pass",
            persist_credentials=True
        )

        mock_login.assert_called_once_with(
            username="test_user",
            password="test_pass",
            persist=True
        )


def test_tile_filename():
    """Test tile filename generation."""
    with patch('earthaccess.login'):
        from NASADEM import NASADEMConnection

        conn = NASADEMConnection(skip_auth=True)
        filename = conn.tile_filename("n34w118")

        assert "NASADEM_HGT_N34W118.zip" in filename
        assert filename.endswith(".zip")


def test_tiles_intersecting_bbox():
    """Test finding tiles that intersect a bounding box."""
    with patch('earthaccess.login'):
        from NASADEM import NASADEMConnection

        conn = NASADEMConnection(skip_auth=True)

        tiles = conn.tiles_intersecting_bbox(-118.5, 33.5, -117.5, 34.5)

        assert isinstance(tiles, list)
        assert len(tiles) > 0
        assert "n33w119" in tiles or "n34w118" in tiles
        assert tiles == sorted(tiles)


def test_tiles_intersecting_bbox_exact_integer_boundaries():
    """Exact integer upper bounds must not spill into adjacent tiles."""
    with patch('earthaccess.login'):
        from NASADEM import NASADEMConnection

        conn = NASADEMConnection(skip_auth=True)

        # Single tile spanning [-118, -117] x [34, 35]
        tiles = conn.tiles_intersecting_bbox(-118.0, 34.0, -117.0, 35.0)
        assert tiles == ["n34w118"]

        # Zero-area point on integer coordinates should still resolve to one tile
        point_tiles = conn.tiles_intersecting_bbox(-118.0, 34.0, -118.0, 34.0)
        assert point_tiles == ["n34w118"]


def test_tiles_from_point():
    """Test finding tile for a single point."""
    with patch('earthaccess.login'):
        from rasters import Point

        from NASADEM import NASADEMConnection

        conn = NASADEMConnection(skip_auth=True)

        point = Point(-118.0, 34.0)
        tiles = conn.tiles(point)

        assert isinstance(tiles, list)
        assert "n34w118" in tiles


def test_search_tile():
    """Test tile search functionality."""
    with patch('earthaccess.login'), patch('earthaccess.search_data') as mock_search:
        from NASADEM import NASADEMConnection

        mock_granule = Mock()
        mock_search.return_value = [mock_granule]

        conn = NASADEMConnection(skip_auth=True)
        result = conn.search_tile("n34w118")

        assert result is not None
        mock_search.assert_called_once()
        call_kwargs = mock_search.call_args[1]
        assert call_kwargs['short_name'] == 'NASADEM_HGT'
        assert call_kwargs['version'] == '001'
        assert 'N34W118' in call_kwargs['granule_name']


def test_search_tile_not_found():
    """Test tile search when tile doesn't exist."""
    with patch('earthaccess.login'), patch('earthaccess.search_data') as mock_search:
        from NASADEM import NASADEMConnection

        mock_search.return_value = []

        conn = NASADEMConnection(skip_auth=True)
        result = conn.search_tile("n90w180")

        assert result is None


def test_tile_not_available_exception():
    """Test that TileNotAvailable exception exists and works."""
    from NASADEM import TileNotAvailable

    with pytest.raises(TileNotAvailable):
        raise TileNotAvailable("Test tile not available")


def test_download_tile_path_handling(tmp_path):
    """Test download_tile handles pathlib.Path return values without redundant move."""
    from NASADEM import NASADEMConnection

    conn = NASADEMConnection(download_directory=str(tmp_path), skip_auth=True)
    target_path = Path(conn.tile_filename("n34w118"))

    def fake_download(granule, local_path):
        _create_synthetic_granule_zip(target_path, tile="n34w118")
        return [target_path]  # earthaccess returns Path objects

    with patch('earthaccess.search_data', return_value=[Mock()]), \
         patch('earthaccess.download', side_effect=fake_download), \
         patch('shutil.move') as mock_move:
        granule = conn.download_tile("n34w118")
        assert granule.tile == "N34W118"
        mock_move.assert_not_called()


def test_granule_properties(tmp_path):
    """Test NASADEMGranule properties and raster extraction with synthetic zip."""
    from rasters import Raster, RasterGrid

    from NASADEM import NASADEMGranule

    zip_path = tmp_path / "NASADEM_HGT_N34W118.zip"
    _create_synthetic_granule_zip(zip_path, tile="n34w118", shape=(4, 4))

    granule = NASADEMGranule(str(zip_path))
    assert granule.tile == "N34W118"
    assert granule.hgt_URI == f"zip://{zip_path}!/n34w118.hgt"
    assert granule.swb_URI == f"zip://{zip_path}!/n34w118.swb"

    grid = RasterGrid.from_bbox(
        xmin=-118.0, ymin=34.0, xmax=-117.0, ymax=35.0,
        cell_size=0.25, crs="EPSG:4326"
    )
    raw_array = np.arange(1, 17, dtype=np.float32).reshape((4, 4))
    raw_array[0, 0] = -32768.0
    mock_raster = Raster(raw_array, geometry=grid)
    mock_raster.nodata = -32768.0

    with patch('rasters.Raster.open', return_value=mock_raster):
        elev = granule.get_elevation_m()
        assert np.isnan(elev.array[0, 0])
        assert elev.array[0, 1] == 2.0

    swb = granule.get_swb(geometry=grid)
    assert swb.dtype == bool
    assert bool(swb.array[1, 1]) is True
    assert bool(swb.array[0, 0]) is False


def test_connection_repr():
    """Test string representation of connection."""
    with patch('earthaccess.login'):
        from NASADEM import NASADEMConnection

        conn = NASADEMConnection(skip_auth=True)
        repr_str = repr(conn)

        data = json.loads(repr_str)
        assert 'download_directory' in data
        assert 'working_directory' in data


def test_tiles_for_different_geometries():
    """Test tile finding for various geometry types."""
    with patch('earthaccess.login'):
        from rasters import MultiPoint
        from shapely.geometry import Polygon

        from NASADEM import NASADEMConnection

        conn = NASADEMConnection(skip_auth=True)

        polygon = Polygon([
            (-118.5, 33.5),
            (-117.5, 33.5),
            (-117.5, 34.5),
            (-118.5, 34.5),
            (-118.5, 33.5)
        ])
        tiles = conn.tiles(polygon)
        assert len(tiles) > 0

        multipoint = MultiPoint([
            (-118.0, 34.0),
            (-117.5, 33.8)
        ])
        tiles = conn.tiles(multipoint)
        assert len(tiles) > 0


def test_multipoint_extraction_constructors(tmp_path):
    """Test _extract_point_values supports multiple MultiPoint constructor styles."""
    from rasters import MultiPoint, Point, Raster, RasterGrid

    from NASADEM import NASADEMConnection

    conn = NASADEMConnection(download_directory=str(tmp_path), skip_auth=True)
    zip_path = Path(conn.tile_filename("n34w118"))
    _create_synthetic_granule_zip(zip_path, tile="n34w118", shape=(4, 4))

    grid = RasterGrid.from_bbox(
        xmin=-118.0, ymin=34.0, xmax=-117.0, ymax=35.0,
        cell_size=0.25, crs="EPSG:4326"
    )
    elev_array = np.full((4, 4), 250.0, dtype=np.float32)
    mock_raster = Raster(elev_array, geometry=grid)
    mock_raster.nodata = np.nan

    mp_tuples = MultiPoint([(-117.8, 34.2), (-117.2, 34.8)])
    mp_xy = MultiPoint(x=[-117.8, -117.2], y=[34.2, 34.8])

    with patch('rasters.Raster.open', return_value=mock_raster):
        vals_tuples = conn.elevation_m(mp_tuples)
        vals_xy = conn.elevation_m(mp_xy)
        val_single = conn.elevation_m(Point(-117.8, 34.2))

    assert np.allclose(vals_tuples, [250.0, 250.0])
    assert np.allclose(vals_xy, [250.0, 250.0])
    assert np.isclose(val_single, 250.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])