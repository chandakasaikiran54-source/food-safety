import os
import shutil
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D, Dropout, Dense
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from datasets import load_dataset
import numpy as np
from PIL import Image

def prepare_food_type_data():
    base_dir = "food_type_dataset"
    categories = ['rice', 'bread', 'biryani', 'vegetables', 'fruit', 'meat', 'dairy', 'mixed', 'non_food']
    
    for split in ['train', 'val']:
        for cat in categories:
            os.makedirs(os.path.join(base_dir, split, cat), exist_ok=True)
            
    print("Loading a small subset of Food-101 for food type classification...")
    try:
        # Load a tiny subset just to build the architecture and demonstrate the pipeline
        ds = load_dataset("food101", split="train[:2%]")
        
        # Broad mapping heuristic for Food-101 classes
        # food101 has 101 classes. We'll do a simple keyword mapping.
        names = ds.features['label'].names
        
        for i, item in enumerate(ds):
            img = item['image']
            label_name = names[item['label']].lower()
            
            cat = 'mixed'
            if 'biryani' in label_name: cat = 'biryani'
            elif 'rice' in label_name: cat = 'rice'
            elif 'bread' in label_name or 'toast' in label_name or 'sandwich' in label_name: cat = 'bread'
            elif 'salad' in label_name or 'carrot' in label_name or 'onion' in label_name: cat = 'vegetables'
            elif 'apple' in label_name or 'fruit' in label_name or 'strawberry' in label_name: cat = 'fruit'
            elif 'steak' in label_name or 'pork' in label_name or 'chicken' in label_name or 'beef' in label_name or 'meat' in label_name: cat = 'meat'
            elif 'cheese' in label_name or 'ice_cream' in label_name or 'macaroni_and_cheese' in label_name: cat = 'dairy'
            
            # 80/20 train/val split
            split = 'train' if i % 5 != 0 else 'val'
            dest = os.path.join(base_dir, split, cat, f"{i}.jpg")
            
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(dest)
            
    except Exception as e:
        print(f"Error loading Food-101: {e}. Generating synthetic data instead.")
        # Fallback to synthetic if download fails
        for cat in categories:
            for i in range(10):
                img = Image.new('RGB', (224, 224), color=(np.random.randint(0,255), np.random.randint(0,255), np.random.randint(0,255)))
                img.save(os.path.join(base_dir, 'train', cat, f"synth_{i}.jpg"))
                img.save(os.path.join(base_dir, 'val', cat, f"synth_{i}.jpg"))
                
    # Add non-food (generate random noise or solid colors)
    for i in range(50):
        img = Image.new('RGB', (224, 224), color=(100, 100, 100))
        img.save(os.path.join(base_dir, 'train', 'non_food', f"nf_{i}.jpg"))
        if i < 10:
            img.save(os.path.join(base_dir, 'val', 'non_food', f"nf_{i}.jpg"))

    return base_dir

def train_food_type_model(base_dir):
    IMG_SIZE = (224, 224)
    BATCH_SIZE = 32
    
    train_datagen = ImageDataGenerator(preprocessing_function=tf.keras.applications.mobilenet_v2.preprocess_input, rotation_range=20)
    val_datagen = ImageDataGenerator(preprocessing_function=tf.keras.applications.mobilenet_v2.preprocess_input)
    
    train_gen = train_datagen.flow_from_directory(
        os.path.join(base_dir, 'train'),
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )
    
    val_gen = val_datagen.flow_from_directory(
        os.path.join(base_dir, 'val'),
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )
    
    num_classes = len(train_gen.class_indices)
    
    base_model = MobileNetV2(input_shape=IMG_SIZE + (3,), include_top=False, weights='imagenet')
    base_model.trainable = False
    
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.2)(x)
    predictions = Dense(num_classes, activation='softmax')(x)
    
    model = Model(inputs=base_model.input, outputs=predictions)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    
    print("Training food type model...")
    model.fit(train_gen, epochs=1, validation_data=val_gen)
    
    model.save('food_type_model.h5')
    
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    with open('food_type_model.tflite', 'wb') as f:
        f.write(converter.convert())
        
    print("Saved food_type_model.tflite")
    
    # Save class indices
    import json
    with open('food_type_classes.json', 'w') as f:
        json.dump({v: k for k, v in train_gen.class_indices.items()}, f)

if __name__ == '__main__':
    d = prepare_food_type_data()
    train_food_type_model(d)
