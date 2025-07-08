"""
Pure Python implementation of POSIX cksum algorithm.

This module provides a replacement for the pycksum package that is compatible
with Python 3.12 and later versions.
"""


def cksum(data_or_file):
    """
    Calculate POSIX cksum checksum for data or file-like object.
    
    Args:
        data_or_file: Either bytes data or a file-like object opened in binary mode
        
    Returns:
        int: The POSIX cksum checksum value
    """
    # Handle file-like objects
    if hasattr(data_or_file, 'read'):
        data = data_or_file.read()
    else:
        data = data_or_file
    
    # Ensure we have bytes
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    # Initialize CRC with 0
    crc = 0
    
    # Process each byte of data
    for byte in data:
        # XOR the byte with the current CRC (shifted left 8 bits) 
        crc ^= byte << 24
        
        # Process 8 bits
        for _ in range(8):
            if crc & 0x80000000:  # If MSB is set
                crc = (crc << 1) ^ 0x04c11db7  # CRC-32 polynomial
            else:
                crc = crc << 1
            crc &= 0xffffffff  # Keep it 32-bit
    
    # Append the length in bytes as a big-endian value
    length = len(data)
    length_bytes = []
    while length > 0:
        length_bytes.insert(0, length & 0xff)
        length >>= 8
    
    # Process the length bytes
    for byte in length_bytes:
        crc ^= byte << 24
        for _ in range(8):
            if crc & 0x80000000:
                crc = (crc << 1) ^ 0x04c11db7
            else:
                crc = crc << 1
            crc &= 0xffffffff
    
    # Final XOR and return as signed 32-bit integer equivalent
    result = crc ^ 0xffffffff
    
    # Convert to match expected return type (unsigned 32-bit integer)
    return result