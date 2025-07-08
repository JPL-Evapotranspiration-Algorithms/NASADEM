#!/usr/bin/env python3
"""
Simple test script to verify that the pycksum replacement works correctly.
This script can be run without installing external dependencies.
"""

import sys
import os
import tempfile
import subprocess

# Add NASADEM to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'NASADEM'))

def test_cksum_import():
    """Test that our cksum module can be imported."""
    print("Testing cksum import...")
    try:
        from cksum import cksum
        print("✓ cksum module imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import cksum: {e}")
        return False

def test_cksum_functionality():
    """Test that cksum produces correct results."""
    print("Testing cksum functionality...")
    try:
        from cksum import cksum
        
        # Test with known data
        test_data = b'Hello World'
        result = cksum(test_data)
        expected = 3576645817
        
        if result == expected:
            print(f"✓ cksum(b'Hello World') = {result} (expected {expected})")
        else:
            print(f"✗ cksum(b'Hello World') = {result} (expected {expected})")
            return False
            
        # Test with empty data
        empty_result = cksum(b'')
        empty_expected = 4294967295
        
        if empty_result == empty_expected:
            print(f"✓ cksum(b'') = {empty_result} (expected {empty_expected})")
        else:
            print(f"✗ cksum(b'') = {empty_result} (expected {empty_expected})")
            return False
            
        return True
    except Exception as e:
        print(f"✗ cksum functionality test failed: {e}")
        return False

def test_system_compatibility():
    """Test that our cksum matches system cksum."""
    print("Testing system cksum compatibility...")
    try:
        from cksum import cksum
        
        # Create temporary file
        test_data = b'Testing system compatibility'
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(test_data)
            tmp_file.flush()
            
            try:
                # Get system cksum
                result = subprocess.run(['cksum', tmp_file.name], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    print("⚠ System cksum command not available, skipping compatibility test")
                    return True
                    
                system_cksum = int(result.stdout.split()[0])
                
                # Get our cksum
                with open(tmp_file.name, 'rb') as f:
                    our_cksum = cksum(f)
                
                if our_cksum == system_cksum:
                    print(f"✓ Our cksum matches system cksum: {our_cksum}")
                    return True
                else:
                    print(f"✗ Mismatch: our={our_cksum}, system={system_cksum}")
                    return False
                    
            finally:
                os.unlink(tmp_file.name)
                
    except Exception as e:
        print(f"✗ System compatibility test failed: {e}")
        return False

def test_lpdaac_import_path():
    """Test that the import path change works (without external deps)."""
    print("Testing LPDAACDataPool import path...")
    
    # Read the file and check the import statement
    lpdaac_file = os.path.join(os.path.dirname(__file__), 'NASADEM', 'LPDAAC', 'LPDAACDataPool.py')
    
    try:
        with open(lpdaac_file, 'r') as f:
            content = f.read()
            
        if 'from pycksum import cksum' in content:
            print("✗ Still using pycksum import")
            return False
        elif 'from ..cksum import cksum' in content:
            print("✓ Using relative import for cksum")
            return True
        else:
            print("✗ No cksum import found")
            return False
            
    except Exception as e:
        print(f"✗ Failed to check import path: {e}")
        return False

def test_pyproject_toml():
    """Test that pycksum was removed from dependencies."""
    print("Testing pyproject.toml dependencies...")
    
    pyproject_file = os.path.join(os.path.dirname(__file__), 'pyproject.toml')
    
    try:
        with open(pyproject_file, 'r') as f:
            content = f.read()
            
        if 'pycksum' in content:
            print("✗ pycksum still in pyproject.toml")
            return False
        else:
            print("✓ pycksum removed from pyproject.toml")
            return True
            
    except Exception as e:
        print(f"✗ Failed to check pyproject.toml: {e}")
        return False

def main():
    """Run all tests."""
    print("NASADEM Python 3.12 pycksum compatibility test")
    print("=" * 50)
    
    tests = [
        test_cksum_import,
        test_cksum_functionality, 
        test_system_compatibility,
        test_lpdaac_import_path,
        test_pyproject_toml
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Python 3.12 compatibility fix successful.")
        return 0
    else:
        print("❌ Some tests failed.")
        return 1

if __name__ == '__main__':
    sys.exit(main())