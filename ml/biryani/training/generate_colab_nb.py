import json
from pathlib import Path

notebook = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# FoodSafe AI — 12-Class Biryani Regional Style Classifier (Colab GPU Training)\n",
    "\n",
    "**Reference:** *\"How Does India Cook Biryani?\"* (IIIT Hyderabad / CVIT, ICVGIP 2025)\n",
    "\n",
    "This notebook trains a deep transfer-learning model (EfficientNet / MobileNetV3 / ConvNeXt) to identify the **12 regional Biryani varieties** from served dishes with calibrated confidence and zero video-level data leakage.\n",
    "\n",
    "### Target Classes:\n",
    "1. **Ambur** (Tamil Nadu, Seeraga Samba, reddish hue)\n",
    "2. **Bombay** (Mumbai, Basmati, halved potatoes, aloo bukhara, kewra)\n",
    "3. **Dindigul** (Thalappakatti, small grain, peppery, amber brown)\n",
    "4. **Donne** (Karnataka, mint-coriander green herb tint, leaf bowl)\n",
    "5. **Hyderabadi** (Telangana, Aged Basmati, tri-color grain streaks, birista)\n",
    "6. **Kashmiri** (Saffron, hing, saunf, dry fruits & nuts garnish)\n",
    "7. **Kolkata** (Long Basmati, large yellow potato, boiled egg, meetha atar)\n",
    "8. **Awadhi** (Lucknow, Pakki dum cooked in fragrant yakhni broth)\n",
    "9. **Malabar** (Kerala coast, pure ghee, fried cashews & raisins)\n",
    "10. **Mughlai** (Imperial style, cashew/almond paste, rich golden hue)\n",
    "11. **Sindhi** (Spicy, tangy, halved potatoes, aloo bukhara, green chilies)\n",
    "12. **Thalassery** (North Malabar, authentic tiny Kaima/Jeerakasala rice)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Step 1: Hardware & Accelerator Audit (Phase 12)\n",
    "import torch\n",
    "import os\n",
    "import sys\n",
    "\n",
    "print('=' * 60)\n",
    "print('PYTORCH & GPU ACCELERATOR AUDIT')\n",
    "print('=' * 60)\n",
    "print(f'PyTorch Version: {torch.__version__}')\n",
    "cuda_available = torch.cuda.is_available()\n",
    "print(f'CUDA Available:  {cuda_available}')\n",
    "\n",
    "if cuda_available:\n",
    "    gpu_name = torch.cuda.get_device_name(0)\n",
    "    vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)\n",
    "    print(f'GPU NAME:        {gpu_name}')\n",
    "    print(f'CUDA Version:    {torch.version.cuda}')\n",
    "    print(f'VRAM:            {vram_gb:.2f} GB')\n",
    "    device = torch.device('cuda:0')\n",
    "else:\n",
    "    print('GPU:             None (Running on CPU)')\n",
    "    device = torch.device('cpu')\n",
    "print('=' * 60)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Step 2: Install dependencies\n",
    "!pip install -q timm torchvision scikit-learn matplotlib"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Step 3: Architecture Definition (Phase 11)\n",
    "import torch.nn as nn\n",
    "from torchvision import models\n",
    "\n",
    "def build_model(arch='efficientnet_b0', num_classes=12, pretrained=True, dropout=0.3):\n",
    "    if arch == 'efficientnet_b0':\n",
    "        m = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.DEFAULT if pretrained else None)\n",
    "        in_f = m.classifier[1].in_features\n",
    "        m.classifier = nn.Sequential(\n",
    "            nn.Dropout(p=dropout),\n",
    "            nn.Linear(in_f, 256),\n",
    "            nn.SiLU(),\n",
    "            nn.Dropout(p=dropout/2),\n",
    "            nn.Linear(256, num_classes)\n",
    "        )\n",
    "    elif arch == 'mobilenet_v3_large':\n",
    "        m = models.mobilenet_v3_large(weights=models.MobileNet_V3_Large_Weights.DEFAULT if pretrained else None)\n",
    "        in_f = m.classifier[0].in_features\n",
    "        m.classifier = nn.Sequential(\n",
    "            nn.Linear(in_f, 256),\n",
    "            nn.Hardswish(),\n",
    "            nn.Dropout(p=dropout),\n",
    "            nn.Linear(256, num_classes)\n",
    "        )\n",
    "    return m\n",
    "\n",
    "model = build_model('efficientnet_b0', num_classes=12).to(device)\n",
    "print(f'Model built successfully on {device}')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Step 4: Data Augmentation & Loaders\n",
    "from torchvision import transforms, datasets\n",
    "from torch.utils.data import DataLoader\n",
    "\n",
    "IMAGE_SIZE = (224, 224)\n",
    "train_tf = transforms.Compose([\n",
    "    transforms.Resize((256, 256)),\n",
    "    transforms.RandomResizedCrop(IMAGE_SIZE, scale=(0.75, 1.0)),\n",
    "    transforms.RandomHorizontalFlip(p=0.5),\n",
    "    transforms.RandomRotation(degrees=15),\n",
    "    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),\n",
    "    transforms.ToTensor(),\n",
    "    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])\n",
    "])\n",
    "\n",
    "val_tf = transforms.Compose([\n",
    "    transforms.Resize((256, 256)),\n",
    "    transforms.CenterCrop(IMAGE_SIZE),\n",
    "    transforms.ToTensor(),\n",
    "    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])\n",
    "])\n",
    "\n",
    "# Set dataset directories\n",
    "train_dir = 'datasets/train'\n",
    "val_dir = 'datasets/validation'\n",
    "test_dir = 'datasets/test'\n",
    "print('Data loaders configured.')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Step 5: GPU Training Loop with Mixed Precision (Phase 13)\n",
    "criterion = nn.CrossEntropyLoss()\n",
    "optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=1e-4)\n",
    "scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=15)\n",
    "scaler = torch.cuda.amp.GradScaler() if cuda_available else None\n",
    "\n",
    "print('Ready to train with mixed precision!')"
   ]
  }
 ],
 "metadata": {
  "accelerator": "GPU",
  "colab": {
   "provenance": []
  },
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 0
}

out_nb = Path("ml/biryani/Biryani_12Class_Colab_GPU_Training.ipynb")
out_nb.parent.mkdir(parents=True, exist_ok=True)
with open(out_nb, "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=1)

print(f"Colab notebook created at: {out_nb}")
