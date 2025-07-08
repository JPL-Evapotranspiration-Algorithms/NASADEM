import pytest
import io
import tempfile
import os
import subprocess


def test_cksum_import():
    """Test that the cksum module can be imported."""
    from NASADEM.cksum import cksum


def test_cksum_with_bytes():
    """Test cksum function with bytes input."""
    from NASADEM.cksum import cksum
    
    test_data = b'Hello World'
    result = cksum(test_data)
    
    # This should be a positive integer
    assert isinstance(result, int)
    assert result > 0
    
    # Known checksum for "Hello World"
    assert result == 3576645817


def test_cksum_with_file_object():
    """Test cksum function with file-like object."""
    from NASADEM.cksum import cksum
    
    test_data = b'Hello World'
    file_obj = io.BytesIO(test_data)
    result = cksum(file_obj)
    
    assert isinstance(result, int)
    assert result == 3576645817


def test_cksum_matches_system_cksum():
    """Test that our cksum implementation matches system cksum command."""
    from NASADEM.cksum import cksum
    
    # Create a temporary file with known content
    test_data = b'Test data for checksum verification'
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(test_data)
        tmp_file.flush()
        
        try:
            # Get system cksum result
            result = subprocess.run(['cksum', tmp_file.name], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                system_cksum = int(result.stdout.split()[0])
                
                # Get our implementation result
                with open(tmp_file.name, 'rb') as f:
                    our_cksum = cksum(f)
                
                assert our_cksum == system_cksum
            else:
                pytest.skip("System cksum command not available")
        finally:
            os.unlink(tmp_file.name)


def test_cksum_empty_data():
    """Test cksum with empty data."""
    from NASADEM.cksum import cksum
    
    result = cksum(b'')
    assert isinstance(result, int)
    # Empty file should have a specific checksum
    assert result == 4294967295  # 0xFFFFFFFF for empty input