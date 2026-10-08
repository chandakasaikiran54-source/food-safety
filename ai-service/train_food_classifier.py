import os
import shutil
import kagglehub
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D, Dropout, Dense
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import numpy as np
import math

def download_and_organize_data():
    base_dir = "food_dataset"
    raw_dir = os.path.join(base_dir, "raw")
    hygienic_dir = os.path.join(raw_dir, "Hygienic")
    not_hygienic_dir = os.path.join(raw_dir, "Not Hygienic")
    
    os.makedirs(hygienic_dir, exist_ok=True)
    os.makedirs(not_hygienic_dir, exist_ok=True)
    
    datasets_used = []
    
    # 1. kagglehub: maheen00shahid/fresh-and-spoiled-food-image-dataset
    try:
        path1 = kagglehub.dataset_download("maheen00shahid/fresh-and-spoiled-food-image-dataset")
        print(f"Dataset 1 downloaded to {path1}")
        process_directory(path1, hygienic_dir, not_hygienic_dir)
        datasets_used.append("maheen00shahid/fresh-and-spoiled-food-image-dataset")
    except Exception as e:
        print(f"Skipping Dataset 1 due to error: {e}")

    # 2. kagglehub: muhriddinmuxiddinov/fruits-and-vegetables-dataset
    try:
        path2 = kagglehub.dataset_download("muhriddinmuxiddinov/fruits-and-vegetables-dataset")
        print(f"Dataset 2 downloaded to {path2}")
        process_directory(path2, hygienic_dir, not_hygienic_dir)
        datasets_used.append("muhriddinmuxiddinov/fruits-and-vegetables-dataset")
    except Exception as e:
        print(f"Skipping Dataset 2 due to error: {e}")

    # For bread mold, we'll try to download using huggingface datasets
    try:
        from datasets import load_dataset
        ds = load_dataset("marescanog/breadMold", split="train")
        print(f"Dataset 3 downloaded. Processing {len(ds)} images.")
        
        features = ds.features
        label_key = 'label' if 'label' in features else 'labels'
        
        if label_key in features:
            label_names = features[label_key].names
            for i, item in enumerate(ds):
                label_name = label_names[item[label_key]].lower()
                image = item['image']
                
                if 'mold' in label_name or 'spoil' in label_name or 'bad' in label_name:
                    dest = os.path.join(not_hygienic_dir, f"bread_{i}.jpg")
                else:
                    dest = os.path.join(hygienic_dir, f"bread_{i}.jpg")
                    
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                image.save(dest)
        datasets_used.append("marescanog/breadMold")
    except Exception as e:
        print(f"Skipping Dataset 3 due to error: {e}")
        
    print(f"Datasets used: {datasets_used}")
    
    # Cap total files so this fits in memory/time constraints
    for cls_dir in [hygienic_dir, not_hygienic_dir]:
        files = os.listdir(cls_dir)
        if len(files) > 2000:
            for f in files[2000:]:
                os.remove(os.path.join(cls_dir, f))
            
    # Now split into train/val/test (80/10/10)
    split_dir = os.path.join(base_dir, "split")
    for split in ['train', 'val', 'test']:
        os.makedirs(os.path.join(split_dir, split, "Hygienic"), exist_ok=True)
        os.makedirs(os.path.join(split_dir, split, "Not Hygienic"), exist_ok=True)
        
    for cls in ["Hygienic", "Not Hygienic"]:
        cls_dir = os.path.join(raw_dir, cls)
        files = os.listdir(cls_dir)
        np.random.shuffle(files)
        
        n = len(files)
        train_n = int(n * 0.8)
        val_n = int(n * 0.1)
        
        train_files = files[:train_n]
        val_files = files[train_n:train_n+val_n]
        test_files = files[train_n+val_n:]
        
        for f in train_files:
            shutil.copy(os.path.join(cls_dir, f), os.path.join(split_dir, 'train', cls, f))
        for f in val_files:
            shutil.copy(os.path.join(cls_dir, f), os.path.join(split_dir, 'val', cls, f))
        for f in test_files:
            shutil.copy(os.path.join(cls_dir, f), os.path.join(split_dir, 'test', cls, f))
            
    print(f"Data split complete.")
    for cls in ["Hygienic", "Not Hygienic"]:
        print(f"{cls} - Train: {len(os.listdir(os.path.join(split_dir, 'train', cls)))}, Val: {len(os.listdir(os.path.join(split_dir, 'val', cls)))}, Test: {len(os.listdir(os.path.join(split_dir, 'test', cls)))}")
        
    return split_dir, datasets_used

def process_directory(src, hygienic_dir, not_hygienic_dir):
    for root, dirs, files in os.walk(src):
        for file in files:
            if not file.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
            
            filepath = os.path.join(root, file)
            lower_path = root.lower()
            if 'fresh' in lower_path and 'half-fresh' not in lower_path and 'non-fresh' not in lower_path:
                shutil.copy(filepath, os.path.join(hygienic_dir, f"{len(os.listdir(hygienic_dir))}_{file}"))
            elif 'rotten' in lower_path or 'spoil' in lower_path or 'stale' in lower_path or 'half-fresh' in lower_path or 'mold' in lower_path or 'non-fresh' in lower_path:
                shutil.copy(filepath, os.path.join(not_hygienic_dir, f"{len(os.listdir(not_hygienic_dir))}_{file}"))
            else:
                if 'fresh' in file.lower():
                    shutil.copy(filepath, os.path.join(hygienic_dir, f"{len(os.listdir(hygienic_dir))}_{file}"))
                elif 'rotten' in file.lower() or 'spoil' in file.lower():
                    shutil.copy(filepath, os.path.join(not_hygienic_dir, f"{len(os.listdir(not_hygienic_dir))}_{file}"))


def train_model(split_dir):
    IMG_SIZE = (224, 224)
    BATCH_SIZE = 32
    
    train_dir = os.path.join(split_dir, 'train')
    val_dir = os.path.join(split_dir, 'val')
    test_dir = os.path.join(split_dir, 'test')
    
    train_datagen = ImageDataGenerator(
        preprocessing_function=tf.keras.applications.mobilenet_v2.preprocess_input,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        zoom_range=0.2
    )
    
    test_datagen = ImageDataGenerator(
        preprocessing_function=tf.keras.applications.mobilenet_v2.preprocess_input
    )
    
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='binary'
    )
    
    val_generator = test_datagen.flow_from_directory(
        val_dir,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='binary',
        shuffle=False
    )
    
    test_generator = test_datagen.flow_from_directory(
        test_dir,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='binary',
        shuffle=False
    )
    
    base_model = MobileNetV2(input_shape=IMG_SIZE + (3,), include_top=False, weights='imagenet')
    base_model.trainable = False
    
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.2)(x)
    predictions = Dense(1, activation='sigmoid')(x)
    
    model = Model(inputs=base_model.input, outputs=predictions)
    
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy', tf.keras.metrics.AUC(name='auc')])
    
    print("Training head...")
    model.fit(
        train_generator,
        epochs=1,
        validation_data=val_generator
    )
    
    base_model.trainable = True
    fine_tune_at = 100
    for layer in base_model.layers[:fine_tune_at]:
        layer.trainable = False
        
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001), loss='binary_crossentropy', metrics=['accuracy', tf.keras.metrics.AUC(name='auc')])
    
    callbacks = [
        EarlyStopping(monitor='val_auc', mode='max', patience=3, restore_best_weights=True),
        ModelCheckpoint('food_hygiene_model.keras', monitor='val_auc', mode='max', save_best_only=True)
    ]
    
    print("Fine-tuning end-to-end...")
    model.fit(
        train_generator,
        epochs=3,
        validation_data=val_generator,
        callbacks=callbacks
    )
    
    print("Evaluating on test set...")
    test_generator.reset()
    y_pred_probs = model.predict(test_generator)
    y_pred = (y_pred_probs > 0.5).astype(int).flatten()
    y_true = test_generator.classes
    
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred)
    rec = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    cm = confusion_matrix(y_true, y_pred)
    
    print(f"Accuracy: {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall: {rec:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print("Confusion Matrix:")
    print(cm)
    
    model.save('food_hygiene_model.h5')
    
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()
    with open('food_hygiene_model.tflite', 'wb') as f:
        f.write(tflite_model)
        
    print("Saved food_hygiene_model.h5 and food_hygiene_model.tflite")
    print("Class indices:", train_generator.class_indices)
    
    return acc, f1

if __name__ == '__main__':
    print("Starting data acquisition...")
    split_dir, datasets_used = download_and_organize_data()
    print("Starting training...")
    acc, f1 = train_model(split_dir)
    print(f"Training Complete! Test Accuracy: {acc:.4f}, Test F1: {f1:.4f}")
