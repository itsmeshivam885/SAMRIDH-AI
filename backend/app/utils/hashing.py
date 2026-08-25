import hashlib
from PIL import Image
import os


def compute_sha256(file_path_or_bytes) -> str:
    """Compute SHA-256 cryptographic digest of a file or byte stream"""
    sha256 = hashlib.sha256()
    if isinstance(file_path_or_bytes, (str, os.PathLike)):
        with open(file_path_or_bytes, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
    else:
        sha256.update(file_path_or_bytes)
    return sha256.hexdigest()


def compute_phash(image_input) -> str:
    """
    Compute a 64-bit difference perceptual hash (dHash) using Pillow.
    Resizes image to 9x8 grayscale and computes horizontal gradients.
    """
    if isinstance(image_input, (str, os.PathLike)):
        img = Image.open(image_input)
    elif isinstance(image_input, bytes):
        import io
        img = Image.open(io.BytesIO(image_input))
    else:
        img = image_input

    # Convert to grayscale and resize to 9x8
    img = img.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
    pixels = list(img.getdata())

    # Compare adjacent pixels in each row
    difference = []
    for row in range(8):
        for col in range(8):
            pixel_left = pixels[row * 9 + col]
            pixel_right = pixels[row * 9 + col + 1]
            difference.append(pixel_left > pixel_right)

    # Convert binary list to hex string (16 characters = 64 bits)
    decimal_value = 0
    hex_string = []
    for index, value in enumerate(difference):
        if value:
            decimal_value += 2 ** (index % 8)
        if (index % 8) == 7:
            hex_string.append(hex(decimal_value)[2:].rjust(2, "0"))
            decimal_value = 0

    return "".join(hex_string)


def hamming_distance(hash1: str, hash2: str) -> int:
    """
    Calculate the Hamming distance between two hex-encoded perceptual hashes.
    A distance <= 8 indicates duplicate / highly recycled imagery.
    """
    if not hash1 or not hash2:
        return 64
    try:
        # Convert hex strings to integers and XOR
        val1 = int(hash1, 16)
        val2 = int(hash2, 16)
        xor_result = val1 ^ val2
        # Count number of set bits
        return bin(xor_result).count("1")
    except ValueError:
        return 64
