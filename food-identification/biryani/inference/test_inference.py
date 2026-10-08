import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.biryani_inference import identify_biryani

def test_samples():
    dataset_dir = BASE_DIR / "dataset"
    test_biryani = list((dataset_dir / "test" / "biryani").glob("*.jpg"))
    test_other = list((dataset_dir / "test" / "not_biryani").glob("*.jpg"))

    print("=== TEST 1: Clear Biryani Image ===")
    if test_biryani:
        res = identify_biryani(str(test_biryani[0]))
        print("Image:", test_biryani[0].name)
        print("Result:", res)

    print("\n=== TEST 2: Another Biryani Image ===")
    if len(test_biryani) > 1:
        res = identify_biryani(str(test_biryani[1]))
        print("Image:", test_biryani[1].name)
        print("Result:", res)

    print("\n=== TEST 3: Non-Biryani Dish (Other Food) ===")
    if test_other:
        res = identify_biryani(str(test_other[0]))
        print("Image:", test_other[0].name)
        print("Result:", res)

    print("\n=== TEST 4: Another Non-Biryani Dish ===")
    if len(test_other) > 1:
        res = identify_biryani(str(test_other[1]))
        print("Image:", test_other[1].name)
        print("Result:", res)

if __name__ == "__main__":
    test_samples()
