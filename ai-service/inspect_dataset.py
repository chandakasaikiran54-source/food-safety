import os
from PIL import Image
import json

def inspect_dataset(data_dir):
    print("Inspecting dataset at:", data_dir)
    total_images = 0
    classes = set()
    class_distribution = {}
    splits = ['train', 'val', 'test']
    split_counts = {'train': 0, 'val': 0, 'test': 0}
    formats = set()
    corrupted = 0
    dimensions = set()
    
    for split in splits:
        split_dir = os.path.join(data_dir, split)
        if not os.path.exists(split_dir):
            continue
            
        for class_name in os.listdir(split_dir):
            class_dir = os.path.join(split_dir, class_name)
            if not os.path.isdir(class_dir):
                continue
                
            classes.add(class_name)
            if class_name not in class_distribution:
                class_distribution[class_name] = 0
                
            for img_name in os.listdir(class_dir):
                img_path = os.path.join(class_dir, img_name)
                total_images += 1
                class_distribution[class_name] += 1
                split_counts[split] += 1
                
                try:
                    with Image.open(img_path) as img:
                        img.verify()
                    with Image.open(img_path) as img:
                        formats.add(img.format)
                        dimensions.add(img.size)
                except Exception as e:
                    corrupted += 1

    print("\n========================================")
    print("DATASET REPORT")
    print("========================================")
    print(f"Dataset path: {data_dir}")
    print(f"Total images: {total_images}")
    print(f"Number of classes: {len(classes)}")
    print(f"Corrupted images: {corrupted}")
    print(f"Image formats: {list(formats)}")
    print(f"Image dimensions: {list(dimensions)}")
    
    print("\nSplit counts:")
    for split, count in split_counts.items():
        print(f"  {split}: {count}")
        
    print("\nClass distribution:")
    for cls, count in sorted(class_distribution.items()):
        print(f"  {cls}: {count}")

    # Save to file
    report = {
        "dataset_path": data_dir,
        "total_images": total_images,
        "number_of_classes": len(classes),
        "corrupted_images": corrupted,
        "image_formats": list(formats),
        "image_dimensions": list(dimensions),
        "split_counts": split_counts,
        "class_distribution": class_distribution
    }
    
    os.makedirs("results", exist_ok=True)
    with open("results/dataset_report.json", "w") as f:
        json.dump(report, f, indent=4)
        
    print("\nReport saved to results/dataset_report.json")

if __name__ == "__main__":
    inspect_dataset("data/plantvillage/PlantVillageDataset/train_val_test")
