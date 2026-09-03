#!/usr/bin/env python3
"""
SAMRIDH-AI Dataset Downloader
Downloads open-source crop / disease / pest / abiotic image datasets into:

    datasets/train/<source>/<class_or_split>/...

Sources (GitHub, Hugging Face, GitHub Releases — no Kaggle login required):
  1. PlantVillage  — Mohanty et al. 2016 (Hugging Face mohanty/PlantVillage)
  2. PlantDoc      — Singh et al. 2020 (github.com/pratikkayal/PlantDoc-Dataset)
  3. Rice leaf     — Hugging Face rice disease image folders
  4. Cotton leaf   — Project-AgML cotton disease (Hugging Face)
  5. IP102 labels  — Wu et al. 2019 class list (images are Google Drive; see README)
  6. Agriculture-Vision catalog — AWS Open Data (too large to auto-mirror)

Usage:
  python scripts/download_datasets.py
  python scripts/download_datasets.py --dataset plantvillage
  python scripts/download_datasets.py --list
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
DATASETS_ROOT = ROOT / "datasets"
TRAIN_ROOT = DATASETS_ROOT / "train"
STAGING = DATASETS_ROOT / "_staging"

USER_AGENT = "SAMRIDH-AI-dataset-downloader/1.0 (research; PMFBY DSS)"

SOURCES = {
    "plantvillage": {
        "task": "disease",
        "name": "PlantVillage (color, 38 classes)",
        "citation": "Mohanty, S.P., Hughes, D.P., & Salathé, M. (2016). Using Deep Learning for Image-Based Plant Disease Detection. Frontiers in Plant Science, 7, 1419. https://doi.org/10.3389/fpls.2016.01419",
        "github": "https://github.com/spmohanty/plantvillage-dataset",
        "hf": "mohanty/PlantVillage",
        "license": "CC-BY-SA 3.0",
        "dest": "disease/plantvillage",
    },
    "plantdoc": {
        "task": "disease",
        "name": "PlantDoc field disease images",
        "citation": "Singh, D. et al. (2020). PlantDoc: A Dataset for Visual Plant Disease Detection. CODS-COMAD 2020.",
        "github": "https://github.com/pratikkayal/PlantDoc-Dataset",
        "zip_url": "https://github.com/pratikkayal/PlantDoc-Dataset/archive/refs/heads/master.zip",
        "license": "CC-BY-4.0",
        "dest": "disease/plantdoc",
    },
    "rice_leaf": {
        "task": "disease",
        "name": "Rice Leaf Disease (Hugging Face image zip)",
        "citation": "Public rice leaf disease image collection (Hugging Face: sharmin3/Rice-Leaf-Disease).",
        "hf": "sharmin3/Rice-Leaf-Disease",
        "hf_file": "Rice Leaf Disease-20241115T062818Z-001.zip",
        "license": "See dataset card",
        "dest": "disease/rice_leaf",
    },
    "rice_india": {
        "task": "disease",
        "name": "Rice leaf disease (India) — blast, blight, brown spot, tungro",
        "citation": "Sethy et al. rice leaf disease identification; indexed as Project-AgML/rice_leaf_disease_classification_india.",
        "hf": "Project-AgML/rice_leaf_disease_classification_india",
        "license": "CC-BY-4.0",
        "dest": "disease/rice_india",
        "hf_images": True,
    },
    "cotton": {
        "task": "disease",
        "name": "Cotton leaf disease classification",
        "citation": "Project-AgML/cotton_leaf_disease_classification (CC-BY-NC-4.0).",
        "hf": "Project-AgML/cotton_leaf_disease_classification",
        "license": "CC-BY-NC-4.0",
        "dest": "disease/cotton",
        "hf_images": True,
    },
    "ip102": {
        "task": "pest",
        "name": "IP102 insect pest taxonomy (labels; images via Drive)",
        "citation": "Wu, X. et al. (2019). IP102: A Large-Scale Benchmark Dataset for Insect Pest Recognition. CVPR 2019.",
        "github": "https://github.com/xpwu95/IP102",
        "drive": "https://drive.google.com/drive/folders/1svFSy2Da3cVMvekBwe13mzyx38XZ9xWo",
        "classes_url": "https://raw.githubusercontent.com/xpwu95/IP102/master/classes.txt",
        "license": "Academic use (see IP102 README)",
        "dest": "pest/ip102",
    },
    "agriculture_vision": {
        "task": "abiotic",
        "name": "Agriculture-Vision aerial patterns (flood, storm, weeds)",
        "citation": "Chiu, M.T. et al. (2020). Agriculture-Vision: A Large Aerial Image Database for Agricultural Pattern Analysis.",
        "url": "https://registry.opendata.aws/intelinair_agriculture_vision/",
        "license": "Non-commercial research",
        "dest": "abiotic/agriculture_vision",
        "catalog_only": True,
        "note": "Full set is tens of GB on AWS. Not auto-downloaded. Use AWS CLI: aws s3 ls --no-sign-request s3://intelinair-data-releases/agriculture-vision/",
    },
}


def _print(msg: str) -> None:
    print(msg, flush=True)


def count_images(path: Path) -> int:
    if not path.exists():
        return 0
    n = 0
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG", "*.bmp"):
        n += sum(1 for _ in path.rglob(ext))
    return n


def dest_ready(dataset_key: str, min_images: int = 20) -> bool:
    dest = TRAIN_ROOT / SOURCES[dataset_key]["dest"]
    return count_images(dest) >= min_images


def download_url(url: str, dest_file: Path) -> Path:
    dest_file.parent.mkdir(parents=True, exist_ok=True)
    if dest_file.exists() and dest_file.stat().st_size > 1024:
        _print(f"  already have {dest_file.name} ({dest_file.stat().st_size:,} bytes)")
        return dest_file

    _print(f"  downloading {url}")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    tmp = dest_file.with_suffix(dest_file.suffix + ".part")
    with urllib.request.urlopen(req, timeout=120) as resp, open(tmp, "wb") as out:
        total = resp.headers.get("Content-Length")
        total_i = int(total) if total and total.isdigit() else None
        copied = 0
        while True:
            chunk = resp.read(1024 * 256)
            if not chunk:
                break
            out.write(chunk)
            copied += len(chunk)
            if total_i:
                pct = 100.0 * copied / total_i
                _print(f"\r  {copied / 1e6:.1f} / {total_i / 1e6:.1f} MB ({pct:.1f}%)",)
        _print("")
    tmp.replace(dest_file)
    return dest_file


def extract_archive(archive: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    _print(f"  extracting {archive.name} -> {dest}")
    if archive.suffix.lower() == ".zip" or archive.name.endswith(".zip"):
        with zipfile.ZipFile(archive, "r") as zf:
            zf.extractall(dest)
        return
    if archive.suffix in {".gz", ".tgz", ".tar"} or archive.name.endswith(".tar.gz"):
        with tarfile.open(archive, "r:*") as tf:
            tf.extractall(dest)
        return
    raise RuntimeError(f"Unknown archive type: {archive}")


def flatten_single_root(extracted: Path) -> None:
    """If zip contains one top-level folder, keep images under dest as-is."""
    children = [p for p in extracted.iterdir() if p.name not in {".git", "__MACOSX"}]
    if len(children) == 1 and children[0].is_dir():
        return


def ensure_hf_hub():
    try:
        import huggingface_hub  # noqa: F401
        return
    except ImportError:
        _print("  installing huggingface_hub ...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "huggingface_hub>=0.23.0"])


def ensure_datasets_lib():
    try:
        import datasets  # noqa: F401
        from PIL import Image  # noqa: F401
        return
    except ImportError:
        _print("  installing datasets + pillow ...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "datasets>=2.20.0", "pillow>=10.0.0"])


def hf_download_file(repo_id: str, filename: str, dest_file: Path) -> Path:
    ensure_hf_hub()
    from huggingface_hub import hf_hub_download

    dest_file.parent.mkdir(parents=True, exist_ok=True)
    path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        repo_type="dataset",
        local_dir=str(dest_file.parent),
    )
    src = Path(path)
    if src.resolve() != dest_file.resolve() and src.exists():
        if not dest_file.exists():
            shutil.copy2(src, dest_file)
    return dest_file if dest_file.exists() else src


def export_hf_image_dataset(repo_id: str, dest: Path, max_images: Optional[int] = None) -> int:
    """Save Hugging Face image-classification datasets as class folders."""
    ensure_datasets_lib()
    from datasets import load_dataset

    dest.mkdir(parents=True, exist_ok=True)
    _print(f"  loading Hugging Face dataset {repo_id}")
    ds = load_dataset(repo_id, split="train")
    label_feature = ds.features.get("label")
    n = 0
    for row in ds:
        if max_images and n >= max_images:
            break
        img = row.get("image")
        if img is None:
            continue
        if label_feature is not None and hasattr(label_feature, "int2str"):
            label = str(label_feature.int2str(row["label"]))
        else:
            label = str(row.get("label", "unknown"))
        safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in label)[:80]
        class_dir = dest / safe
        class_dir.mkdir(parents=True, exist_ok=True)
        out = class_dir / f"{n:06d}.jpg"
        try:
            img.convert("RGB").save(out, format="JPEG", quality=90)
        except Exception:
            img.save(out)
        n += 1
        if n % 200 == 0:
            _print(f"  saved {n} images ...")
    return n


def download_plantvillage() -> None:
    dest = TRAIN_ROOT / SOURCES["plantvillage"]["dest"]
    if dest_ready("plantvillage", 100):
        _print(f"PlantVillage already present ({count_images(dest)} images)")
        return
    staging = STAGING / "plantvillage"
    staging.mkdir(parents=True, exist_ok=True)
    zip_path = staging / "data.zip"
    _print("PlantVillage: Hugging Face data.zip (~2 GB)")
    try:
        hf_download_file("mohanty/PlantVillage", "data.zip", zip_path)
    except Exception as e:
        _print(f"  HF hub failed ({e}); trying direct URL")
        download_url(
            "https://huggingface.co/datasets/mohanty/PlantVillage/resolve/main/data.zip",
            zip_path,
        )
    extract_dir = staging / "extracted"
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_archive(zip_path, extract_dir)
    dest.mkdir(parents=True, exist_ok=True)
    # Prefer color/ train splits if present
    color = None
    for cand in extract_dir.rglob("*"):
        if cand.is_dir() and cand.name.lower() in {"color", "train"}:
            color = cand
            break
    src = color if color is not None else extract_dir
    # Copy class folders
    copied = 0
    for item in src.rglob("*"):
        if item.is_file() and item.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            rel = item.relative_to(src)
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                shutil.copy2(item, target)
            copied += 1
    _print(f"  PlantVillage images in train/: {count_images(dest)} (copied {copied})")


def download_plantdoc() -> None:
    dest = TRAIN_ROOT / SOURCES["plantdoc"]["dest"]
    if dest_ready("plantdoc", 50):
        _print(f"PlantDoc already present ({count_images(dest)} images)")
        return
    staging = STAGING / "plantdoc"
    staging.mkdir(parents=True, exist_ok=True)
    zip_path = staging / "PlantDoc-Dataset-master.zip"
    _print("PlantDoc: GitHub archive")
    download_url(SOURCES["plantdoc"]["zip_url"], zip_path)
    extract_dir = staging / "extracted"
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_archive(zip_path, extract_dir)
    dest.mkdir(parents=True, exist_ok=True)
    copied = 0
    for item in extract_dir.rglob("*"):
        if item.is_file() and item.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            # keep TRAIN/TEST class folder names
            parts = item.parts
            try:
                idx = next(i for i, p in enumerate(parts) if p.lower() in {"train", "test", "val"})
                rel = Path(*parts[idx:])
            except StopIteration:
                rel = Path(item.parent.name) / item.name
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                shutil.copy2(item, target)
            copied += 1
    _print(f"  PlantDoc images in train/: {count_images(dest)}")


def download_rice_zip() -> None:
    dest = TRAIN_ROOT / SOURCES["rice_leaf"]["dest"]
    if dest_ready("rice_leaf", 20):
        _print(f"Rice leaf zip already present ({count_images(dest)} images)")
        return
    staging = STAGING / "rice_leaf"
    zip_path = staging / "rice_leaf.zip"
    _print("Rice leaf: Hugging Face zip")
    hf_download_file(SOURCES["rice_leaf"]["hf"], SOURCES["rice_leaf"]["hf_file"], zip_path)
    if not zip_path.exists():
        # hf_hub_download may leave file under staging with original name
        found = list(staging.rglob("*.zip"))
        if found:
            zip_path = found[0]
    extract_dir = staging / "extracted"
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_archive(zip_path, extract_dir)
    dest.mkdir(parents=True, exist_ok=True)
    for item in extract_dir.rglob("*"):
        if item.is_file() and item.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            rel = Path(item.parent.name) / item.name
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                shutil.copy2(item, target)
    _print(f"  Rice leaf images in train/: {count_images(dest)}")


def download_hf_images(key: str) -> None:
    dest = TRAIN_ROOT / SOURCES[key]["dest"]
    if dest_ready(key, 20):
        _print(f"{key} already present ({count_images(dest)} images)")
        return
    _print(f"{SOURCES[key]['name']}: Hugging Face image export")
    n = export_hf_image_dataset(SOURCES[key]["hf"], dest)
    _print(f"  saved {n} images -> {dest}")


def download_ip102_labels() -> None:
    dest = TRAIN_ROOT / SOURCES["ip102"]["dest"]
    dest.mkdir(parents=True, exist_ok=True)
    classes = dest / "classes.txt"
    _print("IP102: downloading class list from GitHub")
    download_url(SOURCES["ip102"]["classes_url"], classes)
    (dest / "DOWNLOAD_IMAGES.md").write_text(
        "IP102 classification images (~75k) are hosted on Google Drive, not GitHub.\n\n"
        f"Folder: {SOURCES['ip102']['drive']}\n\n"
        "Optional (install gdown):\n"
        "  pip install gdown\n"
        "  gdown --folder 1svFSy2Da3cVMvekBwe13mzyx38XZ9xWo -O datasets/train/pest/ip102/images\n",
        encoding="utf-8",
    )
    _print(f"  wrote {classes} ({classes.stat().st_size} bytes)")


def write_agriculture_vision_catalog() -> None:
    dest = TRAIN_ROOT / SOURCES["agriculture_vision"]["dest"]
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "CATALOG.md").write_text(
        "# Agriculture-Vision (flood / storm / weed aerial patterns)\n\n"
        f"{SOURCES['agriculture_vision']['citation']}\n\n"
        f"Registry: {SOURCES['agriculture_vision']['url']}\n\n"
        "This dataset is **not** git-cloned (multi-GB AWS Open Data). "
        "To fetch a research copy:\n\n"
        "```bash\n"
        "aws s3 ls --no-sign-request s3://intelinair-data-releases/agriculture-vision/\n"
        "aws s3 sync --no-sign-request s3://intelinair-data-releases/agriculture-vision/ "
        "datasets/train/abiotic/agriculture_vision/\n"
        "```\n",
        encoding="utf-8",
    )
    _print("Agriculture-Vision: catalog only (AWS, not auto-downloaded)")


def write_manifest() -> None:
    DATASETS_ROOT.mkdir(parents=True, exist_ok=True)
    TRAIN_ROOT.mkdir(parents=True, exist_ok=True)
    counts = {}
    for key, cfg in SOURCES.items():
        p = TRAIN_ROOT / cfg["dest"]
        counts[key] = count_images(p)
    payload = {
        "train_root": str(TRAIN_ROOT),
        "sources": {k: {**{kk: vv for kk, vv in v.items() if kk != "zip_url"}, "images_on_disk": counts[k]} for k, v in SOURCES.items()},
        "total_images": sum(counts.values()),
    }
    (DATASETS_ROOT / "catalog.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    readme = """# SAMRIDH-AI training images

Layout: `datasets/train/<task>/<source>/...`

| Source | Task | Paper / origin |
|---|---|---|
| PlantVillage | Crop species + 38 disease/healthy classes | Mohanty et al. 2016, [doi:10.3389/fpls.2016.01419](https://doi.org/10.3389/fpls.2016.01419), [GitHub](https://github.com/spmohanty/plantvillage-dataset) |
| PlantDoc | Field-condition disease | Singh et al. 2020, [GitHub](https://github.com/pratikkayal/PlantDoc-Dataset) |
| Rice leaf | Rice blast/blight/spot/tungro | Hugging Face + AgML India rice set |
| Cotton | Cotton leaf diseases | Project-AgML cotton (CC-BY-NC) |
| IP102 | 102 insect pests | Wu et al. CVPR 2019, [GitHub](https://github.com/xpwu95/IP102) — images on Google Drive |
| Agriculture-Vision | Flood/storm/weed aerial | [AWS Open Data](https://registry.opendata.aws/intelinair_agriculture_vision/) |

Images are gitignored (too large for GitHub). Re-run:

```bash
python scripts/download_datasets.py
```
"""
    (DATASETS_ROOT / "README.md").write_text(readme, encoding="utf-8")
    _print(f"Manifest: {sum(counts.values())} images total -> {DATASETS_ROOT / 'catalog.json'}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        default="all",
        choices=["all", *SOURCES.keys()],
    )
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    if args.list:
        for k, v in SOURCES.items():
            _print(f"[{k}] {v['name']}")
        return 0

    TRAIN_ROOT.mkdir(parents=True, exist_ok=True)
    STAGING.mkdir(parents=True, exist_ok=True)

    wanted = list(SOURCES.keys()) if args.dataset == "all" else [args.dataset]
    errors = []
    for key in wanted:
        _print("\n" + "=" * 60)
        _print(f"DATASET: {key} — {SOURCES[key]['name']}")
        try:
            if key == "plantvillage":
                download_plantvillage()
            elif key == "plantdoc":
                download_plantdoc()
            elif key == "rice_leaf":
                download_rice_zip()
            elif key in ("rice_india", "cotton"):
                download_hf_images(key)
            elif key == "ip102":
                download_ip102_labels()
            elif key == "agriculture_vision":
                write_agriculture_vision_catalog()
        except Exception as e:
            _print(f"FAILED {key}: {e}")
            errors.append((key, str(e)))

    write_manifest()
    _print("\nDone.")
    if errors:
        _print("Failures:")
        for k, msg in errors:
            _print(f"  {k}: {msg}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
