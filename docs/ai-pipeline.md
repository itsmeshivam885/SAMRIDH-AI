# SAMRIDH-AI Multimodal AI & Fraud Pipeline

## 1. Edge Image Quality Gate
Before evidence enters the AI segmentation engine, every photo passes an OpenCV/Pillow validation gate:
1. **Blur Detection**: Discrete Laplacian Kernel variance computation. If variance < 80.0, photo is flagged as blurry.
2. **Luminance Check**: Mean grayscale luminance analysis. Photos with luminance < 35 (too dark) or > 245 (washed out) are flagged.
3. **Resolution Validation**: Minimum 400x400 px required for valid feature extraction.

---

## 2. Multi-Signal Fraud Detection Radar
To prevent claim recycling and geographic spoofing without depending on unverified hardware fingerprinting:

- **Signal 1: GPS PostGIS Geofence**: Validates coordinates against the registered farm polygon.
- **Signal 2: 64-Bit Difference Perceptual Hashing (dHash)**: Computes horizontal luminance gradients and evaluates Hamming distance against all historical claim evidence. Distances $\le 8$ indicate duplicate/reused media.
- **Signal 3: SIFT / ORB Baseline Feature Matching**: Compares visible landmarks (sheds, trees, trenches) against sowing baseline imagery.
- **Signal 4: Temporal Consistency**: Checks upload timestamp against official disaster declaration timelines.

---

## 3. Damage Semantic Segmentation (SegFormer)
Pixel-level semantic classification separates the crop canopy into:
- Healthy standing canopy
- Severely lodged / collapsed crop
- Silted / submerged flood damage
- Hail-shredded foliage
- Desiccated / scorched drought area

$$\text{Damage Ratio (\%)} = \frac{\sum \text{Damaged Area Pixels}}{\text{Total Analyzed Canopy Pixels}} \times 100$$

---

## 4. Multimodal Cross-Validation Fusion
Visual ground evidence is fused with Sentinel-2 NDVI vegetative decline and IMD weather radar data to generate a single explainable confidence score ($0.0 - 1.0$) for officer decision support.
