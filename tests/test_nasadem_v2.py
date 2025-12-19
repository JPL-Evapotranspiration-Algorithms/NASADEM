"""
Tests for NASADEM v2.0.0 with earthaccess integration.

These tests verify the core functionality without requiring actual
NASA Earthdata credentials (using mocking where appropriate).
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from pathlib import Path


def test_import_nasadem():
    """Test that NASADEM can be imported."""
    import NASADEM
    assert hasattr(NASADEM, 'NASADEMConnection')
    assert hasattr(NASADEM, 'NASADEM')
    assert hasattr(NASADEM, 'NASADEMGranule')


def test_version():
    """Test that version is accessible."""
    from NASADEM import __version__
    # Version is dynamically loaded from pyproject.toml
    assert __version__ is not None
    assert isinstance(__version__, str)


def test_connection_init():
    """Test NASADEMConnection initialization."""
    with patch('earthaccess.login') as mock_login:
        from NASADEM import NASADEMConnection
        
        # Test with explicit skip_auth=True (for testing)
        conn = NASADEMConnection(skip_auth=True)
        mock_login.assert_not_called()  # Should not call login when skip_auth=True
        assert conn.download_directory is not None
        assert conn.working_directory is not None


def test_connection_with_credentials():
    """Test NASADEMConnection with explicit credentials."""
    with patch('earthaccess.login') as mock_login:
        from NASADEM import NASADEMConnection
        
        conn = NASADEMConnection(
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
        
        conn = NASADEMConnection()
        filename = conn.tile_filename("n34w118")
        
        assert "NASADEM_HGT_N34W118.zip" in filename
        assert filename.endswith(".zip")


def test_tiles_intersecting_bbox():
    """Test finding tiles that intersect a bounding box."""
    with patch('earthaccess.login'):
        from NASADEM import NASADEMConnection
        
        conn = NASADEMConnection()
        
        # Los Angeles area
        tiles = conn.tiles_intersecting_bbox(-118.5, 33.5, -117.5, 34.5)
        
        assert isinstance(tiles, list)
        assert len(tiles) > 0
        assert "n33w119" in tiles or "n34w118" in tiles
        
        # Check tiles are sorted
        assert tiles == sorted(tiles)


def test_tiles_from_point():
    """Test finding tile for a single point."""
    with patch('earthaccess.login'):
        from NASADEM import NASADEMConnection
        from rasters import Point
        
        conn = NASADEMConnection()
        
        # Point in Los Angeles
        point = Point(-118.0, 34.0)
        tiles = conn.tiles(point)
        
        assert isinstance(tiles, list)
        assert "n34w118" in tiles


def test_search_tile():
    """Test tile search functionality."""
    with patch('earthaccess.login'):
        with patch('earthaccess.search_data') as mock_search:
            from NASADEM import NASADEMConnection
            
            # Mock a successful search result
            mock_granule = Mock()
            mock_search.return_value = [mock_granule]
            
            conn = NASADEMConnection()
            result = conn.search_tile("n34w118")
            
            assert result is not None
            mock_search.assert_called_once()
            call_kwargs = mock_search.call_args[1]
            assert call_kwargs['short_name'] == 'NASADEM_HGT'
            assert call_kwargs['version'] == '001'
            assert 'N34W118' in call_kwargs['granule_name']


def test_search_tile_not_found():
    """Test tile search when tile doesn't exist."""
    with patch('earthaccess.login'):
        with patch('earthaccess.search_data') as mock_search:
            from NASADEM import NASADEMConnection
            
            # Mock an empty search result
            mock_search.return_value = []
            
            conn = NASADEMConnection()
            result = conn.search_tile("n90w180")  # Invalid tile
            
            assert result is None


def test_tile_not_available_exception():
    """Test that TileNotAvailable exception exists and works."""
    from NASADEM import TileNotAvailable
    
    with pytest.raises(TileNotAvailable):
        raise TileNotAvailable("Test tile not available")


@pytest.mark.integration
def test_download_tile_mock():
    """Test tile search and download flow (simplified)."""
    # This test verifies the tile search logic works correctly
    # Actual download testing would require real files
    with patch('earthaccess.login'):
        with patch('earthaccess.search_data') as mock_search:
            from NASADEM import NASADEMConnection
            
            # Mock a successful search
            mock_granule = Mock()
            mock_search.return_value = [mock_granule]
            
            conn = NASADEMConnection()
            result = conn.search_tile("n34w118")
            
            # Verify search was called correctly
            assert result is not None
            mock_search.assert_called_once()
            call_kwargs = mock_search.call_args[1]
            assert call_kwargs['short_name'] == 'NASADEM_HGT'
            assert 'N34W118' in call_kwargs['granule_name']


def test_granule_properties():
    """Test NASADEMGranule basic properties (without actual file)."""
    # This test would require a real NASADEM file to work properly
    # Skipping actual granule tests as they require real data
    pass


def test_connection_repr():
    """Test string representation of connection."""
    with patch('earthaccess.login'):
        from NASADEM import NASADEMConnection
        import json
        
        conn = NASADEMConnection()
        repr_str = repr(conn)
        
        # Should be valid JSON
        data = json.loads(repr_str)
        assert 'download_directory' in data
        assert 'working_directory' in data


def test_tiles_for_different_geometries():
    """Test tile finding for various geometry types."""
    with patch('earthaccess.login'):
        from NASADEM import NASADEMConnection
        from rasters import Point, MultiPoint
        from shapely.geometry import Polygon
        
        conn = NASADEMConnection()
        
        # Test with Polygon
        polygon = Polygon([
            (-118.5, 33.5),
            (-117.5, 33.5),
            (-117.5, 34.5),
            (-118.5, 34.5),
            (-118.5, 33.5)
        ])
        tiles = conn.tiles(polygon)
        assert len(tiles) > 0
        
    # Test with MultiPoint - use tuples instead of Point objects
    multipoint = MultiPoint([
        (-118.0, 34.0),
        (-117.5, 33.8)
    ])
    tiles = conn.tiles(multipoint)
    assert len(tiles) > 0
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
