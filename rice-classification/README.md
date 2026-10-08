# 🌾 FoodSafe AI — Biryani Rice Variety Classifier

This directory contains the complete GPU-accelerated training pipeline, dataset loader, and inference engine for the **Rice Variety Classification Module** in FoodSafe AI.

---

## 🎯 Target Classification Schema
The classifier maps input grain visual features into 4 mutually exclusive target classes:
1. **`basmati`**: Basmati extra-long slender rice
2. **`sona_masuri`**: Sona Masuri / HMT medium slender rice
3. **`other_rice`**: Other rice varieties (Arborio, Jasmine, Ipsala, Karacadag, Masuri, Jhili)
4. **`unknown`**: Out-of-distribution / Non-rice / Insufficient visual evidence

---

## 📁 Directory Structure
```
rice-classification/
├── colab_train_rice_classifier.ipynb    # Complete Google Colab GPU training notebook
├── README.md                            # Comprehensive execution and integration guide
├── config/
│   └── rice_config.py                   # Centralized paths, classes, and hyperparameters
├── dataset/
│   └── dataset_loader.py                # Verified dataset downloader, QC, and leakage-free split
├── models/
│   └── rice_model_builder.py            # EfficientNet-B0, MobileNet-V3, ResNet-18 architectures
├── preprocessing/
│   └── rice_preprocessor.py             # Quality checks, transforms, normalization
├── training/
│   └── train_rice_classifier.py         # Headless PyTorch GPU trainer with CUDA enforcement
├── inference/
│   └── rice_inference.py                # Production inference engine for FoodSafe AI
└── export/                              # Model artifacts destination
    ├── rice_classifier.pth              # Best trained PyTorch weights
    ├── class_names.json                 # Class index mapping
    ├── preprocessing_config.json        # Preprocessing & hardware metadata
    └── metrics.json                     # Test accuracy, precision, recall, F1, confusion matrix
```

---

## 🚀 How to Run the Google Colab Training Notebook

### 1. Open Google Colab
1. Navigate to [Google Colab](https://colab.research.google.com/).
2. Click **Upload** and select `colab_train_rice_classifier.ipynb` from this folder (`foodsafe-ai/rice-classification/colab_train_rice_classifier.ipynb`).

### 2. Enable Free T4 GPU
1. In Colab, go to top menu: **Runtime** ➔ **Change runtime type**.
2. Select **T4 GPU** under Hardware accelerator.
3. Click **Save**.

### 3. Run All Cells
1. Click **Runtime** ➔ **Run all** (`Ctrl + F9`).
2. The notebook will automatically:
   - Install required dependencies (`py7zr`, `torchvision`, `scikit-learn`, `seaborn`).
   - Run strict hardware diagnostics (detects NVIDIA T4 GPU and CUDA).
   - Download the verified Mendeley Data archive (**DOI: 10.17632/c5y6gjwdzh.1**, 152 MB).
   - Perform quality control: quarantines corrupt images and filters duplicate images via MD5 hashing.
   - Generate stratified, leakage-free splits: **Train (75%)**, **Validation (12.5%)**, **Test (12.5%)**.
   - Print the mandatory pre-training diagnostic block:
     ```
     GPU: Tesla T4
     CUDA: 12.x
     PyTorch: 2.x
     Dataset: Mendeley Data (Milled Rice Grain - Prabira Sethy DOI: 10.17632/c5y6gjwdzh.1)
     Classes: ['basmati', 'sona_masuri', 'other_rice', 'unknown']
     Train images: ...
     Validation images: ...
     Test images: ...
     ```
   - Train `EfficientNet-B0` with mixed precision (`torch.cuda.amp.autocast`) and Cosine Annealing scheduler.
   - Evaluate on the untouched test set and display accuracy, precision, recall, F1-score, and confusion matrix.
   - Automatically bundle all deployment artifacts into `foodsafe_rice_model.zip` and download it to your browser.

---

## 🔄 Integrating Trained Artifacts into FoodSafe AI

Once the Colab run completes and downloads `foodsafe_rice_model.zip`:
1. Extract the zip file contents:
   - `rice_classifier.pth`
   - `class_names.json`
   - `preprocessing_config.json`
   - `metrics.json`
2. Place them into either:
   - `foodsafe-ai/rice-classification/export/` **OR**
   - `foodsafe-ai/ai-service/models/`
3. The FoodSafe AI inference engine ([rice_inference.py](file:///c:/Users/chand/Music/main%20project/foodsafe-ai/rice-classification/inference/rice_inference.py)) and backend service ([variety_classifier.py](file:///c:/Users/chand/Music/main%20project/foodsafe-ai/ai-service/rice_intelligence/variety_classifier.py)) will detect the checkpoint and transition to neural classification.
