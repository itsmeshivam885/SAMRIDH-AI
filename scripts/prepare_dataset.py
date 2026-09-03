#!/usr/bin/env python3
"""
SAMRIDH-AI Dataset Preparation & Structuring Script
===================================================
Prepares training images in `datasets/train/` with 15 key crop conditions
for PMFBY insurance crop analysis.
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import random

CLASSES = [
    "Rice_Bacterial_Blight",
    "Rice_Blast",
    "Wheat_Yellow_Rust",
    "Wheat_Healthy",
    "Soybean_Rust",
    "Soybean_Yellow_Mosaic",
    "Soybean_Healthy",
    "Cotton_Bollworm",
    "Cotton_Bacterial_Blight",
    "Potato_Early_Blight",
    "Potato_Late_Blight",
    "Tomato_Early_Blight",
    "Tomato_Healthy",
    "Flood_Submerged_Canopy",
    "Drought_Desiccated_Scorch"
]

def generate_synthetic_samples(target_dir: Path, num_per_class: int = 20):
    print(f"Generating training dataset structured across {len(CLASSES)} classes in {target_dir}...")
    target_dir.mkdir(parents=True, exist_ok=True)

    for cls_name in CLASSES:
        cls_folder = target_dir / cls_name
        cls_folder.mkdir(parents=True, exist_ok=True)

        for i in range(num_per_class):
            img = Image.new("RGB", (224, 224), color=(30, 80, 30))
            draw = ImageDraw.Draw(img)

            # Draw base foliage pattern
            if "Healthy" in cls_name:
                for _ in range(30):
                    x = random.randint(10, 200)
                    y = random.randint(10, 200)
                    r = random.randint(15, 40)
                    draw.ellipse([x, y, x+r, y+r], fill=(random.randint(40, 100), random.randint(140, 220), random.randint(40, 90)))
            elif "Rust" in cls_name or "Blight" in cls_name:
                for _ in range(25):
                    x = random.randint(10, 200)
                    y = random.randint(10, 200)
                    r = random.randint(10, 30)
                    draw.ellipse([x, y, x+r, y+r], fill=(random.randint(140, 210), random.randint(70, 130), random.randint(20, 60)))
            elif "Flood" in cls_name:
                draw.rectangle([0, 100, 224, 224], fill=(40, 80, 150))
            elif "Drought" in cls_name:
                draw.rectangle([0, 0, 224, 224], fill=(160, 130, 70))
            else:
                for _ in range(20):
                    x = random.randint(10, 200)
                    y = random.randint(10, 200)
                    r = random.randint(10, 35)
                    draw.ellipse([x, y, x+r, y+r], fill=(random.randint(80, 180), random.randint(100, 180), random.randint(30, 80)))

            img_path = cls_folder / f"sample_{i+1:03d}.jpg"
            img.save(img_path, quality=90)

    print(f"Created {len(CLASSES) * num_per_class} training images in {target_dir}")

if __name__ == "__main__":
    base_dir = Path(__file__).parent.parent / "datasets" / "train"
    generate_synthetic_samples(base_dir)
