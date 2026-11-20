#!/usr/bin/env python3
"""
Integration test script for querying elevation values from NASADEM.

Demonstrates how to retrieve elevation data from NASADEM using geometry points,
including single points and multipoints against ECOv002 calval sites.
"""
import earthaccess
import numpy as np
import pytest
import rasters as rt

from NASADEM import NASADEM


@pytest.mark.integration
def test_nasadem_elevation_calval():
    calval_tables = pytest.importorskip("ECOv002_calval_tables")

    # Trigger lazy initialization of NASADEM and ensure Earthdata auth succeeded
    _ = NASADEM.download_directory
    if not getattr(earthaccess, "__store__", None):
        pytest.skip("NASA Earthdata authentication required for integration test")

    calval_df = calval_tables.load_calval_table()
    test_df = calval_df.head(10).copy()

    assert "geometry" in test_df.columns
    geometries = test_df["geometry"].values
    x_coords = [g.x for g in geometries]
    y_coords = [g.y for g in geometries]

    multipoint_geometry = rt.MultiPoint(x=x_coords, y=y_coords)
    elevation_km = NASADEM.elevation_km(geometry=multipoint_geometry)
    elevation_m = elevation_km * 1000.0
    assert elevation_m.shape[0] == len(test_df)
    assert not np.all(np.isnan(elevation_m)), "All queried elevations are NaN"

    first_record = test_df.iloc[0]
    single_point = first_record["geometry"]
    single_geometry = rt.Point(single_point.x, single_point.y)
    single_elevation = NASADEM.elevation_km(geometry=single_geometry) * 1000.0

    first_elevation_mp = elevation_m[0] if isinstance(elevation_m, np.ndarray) else elevation_m
    assert np.isclose(single_elevation, first_elevation_mp, equal_nan=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])