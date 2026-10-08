import torch
from torchvision import models, transforms
from PIL import Image
import json

def get_imagenet_classes():
    # We will just fetch the classes or use a tiny subset
    import urllib.request
    url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
    try:
        req = urllib.request.urlopen(url)
        classes = [line.decode('utf-8').strip() for line in req.readlines()]
        return classes
    except Exception as e:
        print(e)
        return None

classes = get_imagenet_classes()

def is_food_class(class_name):
    food_keywords = [
        'food', 'meal', 'plate', 'dish', 'fruit', 'vegetable', 'meat', 'fish', 'bread', 'cake', 'pie', 'pizza',
        'burger', 'sandwich', 'hotdog', 'soup', 'salad', 'pasta', 'noodle', 'rice', 'egg', 'cheese', 'ice cream',
        'chocolate', 'candy', 'cookie', 'coffee', 'tea', 'juice', 'beer', 'wine', 'water', 'milk', 'apple',
        'banana', 'orange', 'lemon', 'grape', 'strawberry', 'melon', 'peach', 'cherry', 'pineapple', 'mango',
        'pomegranate', 'coconut', 'broccoli', 'carrot', 'potato', 'biryani', 'onion', 'garlic', 'pepper', 'corn',
        'mushroom', 'cucumber', 'cabbage', 'lettuce', 'spinach', 'celery', 'beef', 'pork', 'chicken', 'lamb',
        'turkey', 'duck', 'sausage', 'bacon', 'ham', 'shrimp', 'crab', 'lobster', 'clam', 'oyster', 'squid',
        'octopus', 'salmon', 'tuna', 'trout', 'bass', 'flounder', 'mackerel', 'halibut', 'snapper', 'cod',
        'pastry', 'doughnut', 'croissant', 'muffin', 'bagel', 'bun', 'pancake', 'waffle', 'toast', 'cereal',
        'pretzel', 'granny smith', 'strawberry', 'orange', 'lemon', 'fig', 'pineapple', 'banana', 'jackfruit', 
        'custard apple', 'pomegranate', 'acorn squash', 'head cabbage', 'broccoli', 'cauliflower', 'zucchini', 
        'spaghetti squash', 'acorn squash', 'butternut squash', 'cucumber', 'artichoke', 'bell pepper', 
        'cardoon', 'mushroom', 'hot pot', 'consomme', 'trifle', 'ice cream', 'ice lolly', 'french loaf', 'bagel',
        'pretzel', 'cheeseburger', 'hotdog', 'mashed potato', 'head cabbage', 'broccoli', 'cauliflower', 'zucchini',
        'spaghetti squash', 'acorn squash', 'butternut squash', 'cucumber', 'artichoke', 'bell pepper', 'cardoon',
        'mushroom', 'granny smith', 'strawberry', 'orange', 'lemon', 'fig', 'pineapple', 'banana', 'jackfruit',
        'custard apple', 'pomegranate', 'meat loaf', 'carbonara', 'chocolate sauce', 'dough', 'meat loaf', 'pizza',
        'potpie', 'burrito', 'red wine', 'espresso', 'cup', 'eggnog', 'guacamole', 'consomme', 'hot pot', 'trifle',
        'ice cream', 'ice lolly', 'french loaf', 'bagel', 'pretzel',
        'cheeseburger', 'hotdog', 'mashed potato', 'head cabbage', 'broccoli', 'cauliflower', 'zucchini', 'spaghetti squash',
        'acorn squash', 'butternut squash', 'cucumber', 'artichoke', 'bell pepper', 'cardoon', 'mushroom', 'granny smith',
        'strawberry', 'orange', 'lemon', 'fig', 'pineapple', 'banana', 'jackfruit', 'custard apple', 'pomegranate', 'plate',
        'bowl', 'frying pan', 'wok', 'cauldron', 'teapot', 'coffee mug', 'pitcher'
    ]
    return any(keyword in class_name.lower() for keyword in food_keywords)

if classes:
    food_classes = [c for c in classes if is_food_class(c)]
    print(f"Total food classes found: {len(food_classes)}")
    
model = models.mobilenet_v2(pretrained=True)
model.eval()

transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

print("Model loaded.")
