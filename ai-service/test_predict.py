import requests
import os

# Create a dummy image for testing if we don't have one handy
test_img_path = 'test_food.jpg'

print(f"Testing with image: {test_img_path}")
url = 'http://localhost:8000/predict'

try:
    with open(test_img_path, 'rb') as f:
        files = {'image': f}
        response = requests.post(url, files=files)
        
    print("Response status code:", response.status_code)
    print("Response JSON:", response.json())
except FileNotFoundError:
    print(f"Test image {test_img_path} not found.")
except Exception as e:
    print(f"Error connecting to service: {e}")
