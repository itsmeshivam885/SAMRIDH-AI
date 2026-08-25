import io
from PIL import Image, ImageDraw
from app.utils.image import analyze_image_quality
from app.utils.hashing import compute_phash, hamming_distance


def test_sharp_image_passes_quality_gate():
    # Create high-contrast sharp test pattern
    img = Image.new("RGB", (600, 600), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    for i in range(0, 600, 20):
        draw.line([(i, 0), (i, 600)], fill=(0, 0, 0), width=4)
        draw.line([(0, i), (600, i)], fill=(0, 0, 0), width=4)
    
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    bytes_data = buf.getvalue()

    res = analyze_image_quality(bytes_data)
    assert res["passed_quality_gate"] is True
    assert res["is_blurry"] is False
    assert res["blur_score"] > 80.0


def test_phash_and_hamming_duplicate_detection():
    # Base image
    img1 = Image.new("RGB", (400, 400), color=(120, 200, 100))
    draw = ImageDraw.Draw(img1)
    draw.rectangle([50, 50, 200, 200], fill=(50, 100, 50))
    
    buf1 = io.BytesIO()
    img1.save(buf1, format="JPEG")
    hash1 = compute_phash(buf1.getvalue())

    # Exact duplicate
    dist_exact = hamming_distance(hash1, hash1)
    assert dist_exact == 0

    # Slight modification (still duplicate)
    img2 = img1.copy()
    draw2 = ImageDraw.Draw(img2)
    draw2.point((10, 10), fill=(255, 255, 255))
    buf2 = io.BytesIO()
    img2.save(buf2, format="JPEG")
    hash2 = compute_phash(buf2.getvalue())

    dist_near = hamming_distance(hash1, hash2)
    assert dist_near <= 4 # Within duplicate threshold
