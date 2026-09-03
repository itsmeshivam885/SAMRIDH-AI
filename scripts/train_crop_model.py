#!/usr/bin/env python3
"""
SAMRIDH-AI PyTorch Crop Vision Model Trainer
=============================================
Trains a lightweight MobileNetV3-Small model on PlantVillage / PlantDoc / Structured crop dataset
for offline real-time crop disease & crop type classification.

Saves TorchScript model to: backend/app/ai/models/crop_disease_model.pt
"""

import os
import sys
import time
import json
from pathlib import Path

def train_and_export():
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torchvision import transforms, datasets, models
    from torch.utils.data import DataLoader

    print("=" * 65)
    print("SAMRIDH-AI Model Trainer - PyTorch MobileNetV3-Small")
    print("=" * 65)

    base_dir = Path(__file__).parent.parent
    pv_dir = base_dir / "datasets" / "plantvillage_raw" / "raw" / "color"
    pd_dir = base_dir / "datasets" / "plantdoc_raw" / "train"
    synth_dir = base_dir / "datasets" / "train"
    output_dir = base_dir / "backend" / "app" / "ai" / "models"
    output_dir.mkdir(parents=True, exist_ok=True)

    data_dir = None
    if pv_dir.exists() and len(list(pv_dir.iterdir())) > 0:
        data_dir = pv_dir
    elif pd_dir.exists() and len(list(pd_dir.iterdir())) > 0:
        data_dir = pd_dir
    elif synth_dir.exists():
        data_dir = synth_dir
    else:
        print(f"Error: Dataset directory not found.")
        sys.exit(1)

    print(f"Loading dataset from: {data_dir}")

    # Data transforms
    transform_train = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    dataset = datasets.ImageFolder(root=str(data_dir), transform=transform_train)
    num_classes = len(dataset.classes)
    class_names = dataset.classes

    print(f"Found {len(dataset)} images across {num_classes} classes.")

    # Save class mapping
    class_map = {i: name for i, name in enumerate(class_names)}
    with open(output_dir / "class_labels.json", "w", encoding="utf-8") as f:
        json.dump(class_map, f, indent=2)
    print(f"Saved class labels mapping to {output_dir / 'class_labels.json'}")

    # DataLoader
    train_size = min(len(dataset), 5000)
    subset_indices = torch.randperm(len(dataset))[:train_size]
    train_subset = torch.utils.data.Subset(dataset, subset_indices)
    loader = DataLoader(train_subset, batch_size=16, shuffle=True, num_workers=0)

    # Initialize MobileNetV3 Small (pretrained)
    print("Initializing MobileNetV3-Small architecture...")
    model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.DEFAULT)
    
    # Replace classification head
    in_features = model.classifier[3].in_features
    model.classifier[3] = nn.Linear(in_features, num_classes)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on device: {device}")
    model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)

    # Training loop
    epochs = 3
    model.train()
    start_time = time.time()

    for epoch in range(epochs):
        running_loss = 0.0
        correct = 0
        total = 0

        for i, (inputs, labels) in enumerate(loader):
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

            if (i + 1) % 10 == 0 or (i + 1) == len(loader):
                acc = 100.0 * correct / total
                print(f"  Epoch [{epoch+1}/{epochs}] Step [{i+1}/{len(loader)}] - Loss: {running_loss/(i+1):.4f} | Acc: {acc:.2f}%")

    elapsed = time.time() - start_time
    print(f"Training finished in {elapsed:.1f} seconds!")

    # Export TorchScript Model
    model.eval()
    model.to("cpu")
    dummy_input = torch.randn(1, 3, 224, 224)
    traced_model = torch.jit.trace(model, dummy_input)
    
    model_path = output_dir / "crop_disease_model.pt"
    traced_model.save(str(model_path))
    size_mb = os.path.getsize(model_path) / (1024 * 1024)

    print("=" * 65)
    print(f"TorchScript model successfully saved: {model_path} ({size_mb:.2f} MB)")
    print("=" * 65)

if __name__ == "__main__":
    train_and_export()
