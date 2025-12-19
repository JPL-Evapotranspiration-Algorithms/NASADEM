#!/usr/bin/env python3
"""
Test script for querying elevation values from NASADEM.

This script demonstrates how to retrieve elevation data from NASADEM
using geometry points, including single points and multipoints.
"""
import numpy as np
import rasters as rt
from NASADEM import NASADEM
from ECOv002_calval_tables import load_calval_table

def main():
    # Load calibration/validation table for test coordinates
    print("Loading calibration/validation table for test coordinates...")
    calval_df = load_calval_table()
    print(f"Loaded {len(calval_df)} records from calval table")
    
    # Take a small subset for testing (first 10 records)
    test_df = calval_df.head(10).copy()
    print(f"\nTesting with first {len(test_df)} records")
    print(f"Sites: {test_df['ID'].unique()}\n")
    
    # Extract geometries from the test dataframe
    if 'geometry' not in test_df.columns:
        print("ERROR: 'geometry' column not found in calval table")
        return
    
    geometries = test_df['geometry'].values
    x_coords = [g.x for g in geometries]
    y_coords = [g.y for g in geometries]
    
    # Test 1: Query elevation for multiple points using MultiPoint
    print("=" * 60)
    print("Test 1: Query elevation for multiple points")
    print("=" * 60)
    
    multipoint_geometry = rt.MultiPoint(x=x_coords, y=y_coords)
    print(f"Created MultiPoint with {len(geometries)} points")
    
    print("\nQuerying NASADEM for elevation...")
    elevation_km = NASADEM.elevation_km(geometry=multipoint_geometry)
    elevation_m = elevation_km * 1000.0
    
    print(f"\nRetrieved elevation shape: {elevation_m.shape}")
    print(f"Elevation (m): {elevation_m}")
    print(f"Min elevation: {np.min(elevation_m):.2f} m")
    print(f"Max elevation: {np.max(elevation_m):.2f} m")
    print(f"Mean elevation: {np.mean(elevation_m):.2f} m")
    
    # Compare with table values if available
    if 'elevation_m' in test_df.columns:
        table_elevation = test_df['elevation_m'].values
        print(f"\nTable elevation (m): {table_elevation}")
        diff = elevation_m - table_elevation
        print(f"Difference from table: {diff}")
        print(f"Max absolute difference: {np.max(np.abs(diff)):.2f} m")
        print(f"Mean absolute difference: {np.mean(np.abs(diff)):.2f} m")
    
    # Test 2: Query elevation for a single point
    print("\n" + "=" * 60)
    print("Test 2: Query elevation for a single point")
    print("=" * 60)
    
    first_record = test_df.iloc[0]
    single_point = first_record['geometry']
    print(f"Testing site: {first_record['ID']}")
    print(f"Location: ({single_point.y:.4f}, {single_point.x:.4f})")
    
    single_geometry = rt.Point(single_point.x, single_point.y)
    
    print("\nQuerying NASADEM for single point elevation...")
    single_elevation_km = NASADEM.elevation_km(geometry=single_geometry)
    single_elevation = single_elevation_km * 1000.0
    
    print(f"Retrieved elevation: {single_elevation} m")
    
    # Compare with multipoint result for first point
    if isinstance(elevation_m, np.ndarray):
        first_elevation_mp = elevation_m[0]
    else:
        first_elevation_mp = elevation_m
    
    print(f"Multipoint result for first point: {first_elevation_mp} m")
    
    # Verify they match
    if np.isclose(single_elevation, first_elevation_mp):
        print("✓ Single point elevation matches multipoint result")
    else:
        print(f"⚠ Difference: {abs(single_elevation - first_elevation_mp):.2f} m")
    
    # Compare with table value if available
    if 'elevation_m' in test_df.columns:
        table_value = first_record['elevation_m']
        print(f"Table value: {table_value} m")
        print(f"Difference from table: {single_elevation - table_value:.2f} m")
    
    # Test 3: Query elevation for specific geographic locations
    print("\n" + "=" * 60)
    print("Test 3: Query elevation for known locations")
    print("=" * 60)
    
    # Test locations with known approximate elevations
    test_locations = [
        {"name": "Death Valley, CA", "lon": -116.8667, "lat": 36.5, "expected": -86},
        {"name": "Denver, CO", "lon": -104.9903, "lat": 39.7392, "expected": 1609},
        {"name": "Mount Everest Base Camp", "lon": 86.8528, "lat": 27.9881, "expected": 5364},
    ]
    
    for location in test_locations:
        point = rt.Point(location["lon"], location["lat"])
        elevation_km = NASADEM.elevation_km(geometry=point)
        elevation = elevation_km * 1000.0
        expected = location["expected"]
        diff = elevation - expected
        
        print(f"\n{location['name']}:")
        print(f"  Coordinates: ({location['lat']:.4f}, {location['lon']:.4f})")
        print(f"  Retrieved elevation: {elevation:.2f} m")
        print(f"  Expected elevation: {expected} m")
        print(f"  Difference: {diff:.2f} m")
    
    print("\n" + "=" * 60)
    print("NASADEM elevation query tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
