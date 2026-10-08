"""
FoodSafe AI — Real-World Smartphone/Camera Biryani Image Harvester
Implements Phase 9 & Phase 17: Downloads verified Creative Commons images from Wikimedia Commons with complete license tracking.
"""

import urllib.request
import urllib.parse
import json
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

OUT_BASE = Path("ml/biryani/datasets/real_smartphone_test")
MANIFEST_PATH = Path("ml/biryani/datasets/real_smartphone_manifest.json")

SEARCH_TERMS = {
    "hyderabadi": ["Hyderabadi biryani", "Hyderabad biryani"],
    "kolkata": ["Kolkata biryani", "Calcutta biryani"],
    "thalassery": ["Thalassery biryani", "Tellicherry biryani"],
    "malabar": ["Malabar biryani", "Kerala biryani"],
    "donne": ["Donne biryani", "Bangalore biryani"],
    "ambur": ["Ambur biryani", "Vellore biryani"],
    "dindigul": ["Dindigul biryani", "Thalappakatti biryani"],
    "bombay": ["Bombay biryani", "Mumbai biryani"],
    "awadhi": ["Lucknowi biryani", "Awadhi biryani"],
    "kashmiri": ["Kashmiri biryani"],
    "mughlai": ["Mughlai biryani"],
    "sindhi": ["Sindhi biryani"]
}

def query_commons(query, limit=4):
    url = (
        "https://commons.wikimedia.org/w/api.php?"
        + urllib.parse.urlencode({
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": f"{query} filetype:bitmap",
            "gsrlimit": limit,
            "prop": "imageinfo",
            "iiprop": "url|extmetadata|size"
        })
    )
    req = urllib.request.Request(url, headers={"User-Agent": "FoodSafeAI-ResearchBot/1.0 (Academic CV Research)"})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get("query", {}).get("pages", {})
            results = []
            for page_id, p_info in pages.items():
                title = p_info.get("title", "")
                img_info = p_info.get("imageinfo", [{}])[0]
                img_url = img_info.get("url")
                meta = img_info.get("extmetadata", {})
                license_name = meta.get("LicenseShortName", {}).get("value", "CC BY-SA")
                artist = meta.get("Artist", {}).get("value", "Unknown")
                if img_url and any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png']):
                    results.append({
                        "title": title,
                        "url": img_url,
                        "license": license_name,
                        "artist": artist,
                        "width": img_info.get("width"),
                        "height": img_info.get("height")
                    })
            return results
    except Exception as e:
        print(f"Error querying {query}: {e}")
        return []

manifest = {}
total_downloaded = 0

for cat, queries in SEARCH_TERMS.items():
    cat_dir = OUT_BASE / cat
    cat_dir.mkdir(parents=True, exist_ok=True)
    manifest[cat] = []
    
    seen_urls = set()
    for q in queries:
        items = query_commons(q, limit=5)
        for item in items:
            u = item["url"]
            if u in seen_urls:
                continue
            seen_urls.add(u)
            
            clean_title = "".join(c for c in item["title"] if c.isalnum() or c in ('_', '-'))
            out_file = cat_dir / f"{clean_title[:35]}.jpg"
            
            try:
                img_req = urllib.request.Request(u, headers={"User-Agent": "FoodSafeAI-ResearchBot/1.0"})
                with urllib.request.urlopen(img_req, timeout=15) as r:
                    img_data = r.read()
                with open(out_file, "wb") as f:
                    f.write(img_data)
                    
                item["local_path"] = str(out_file)
                manifest[cat].append(item)
                total_downloaded += 1
                print(f"[{cat.upper()}] Downloaded: {item['title'][:40]} ({item['license']})")
                if len(manifest[cat]) >= 4:
                    break
            except Exception as e:
                print(f"Failed to download {u}: {e}")
                
print(f"\nTotal real smartphone/camera images collected: {total_downloaded}")
with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)
print(f"Manifest written to: {MANIFEST_PATH}")
