import zlib

# -------------------------------
# Compression / Decompression
# -------------------------------

def compress_data(data: bytes) -> bytes:
    """
    Compress raw data using zlib.
    """
    return zlib.compress(data)

def decompress_data(data: bytes) -> bytes:
    """
    Decompress raw data using zlib.
    """
    return zlib.decompress(data)


