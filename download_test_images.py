"""
Script to download 1 close-up leaf image for each of the 47 plant classes in plant_classes.json
and evaluate predictions using PlantMLEngine.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
from PIL import Image

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plantcare_project.settings')
import django
django.setup()

from identification.ml_engine import PlantMLEngine

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_plant_images')
os.makedirs(OUTPUT_DIR, exist_ok=True)

JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'identification', 'plant_classes.json')
with open(JSON_PATH, 'r', encoding='utf-8') as f:
    meta = json.load(f)

classes = meta.get('classes', [])
species_info = meta.get('species_info', {})

headers = {
    'User-Agent': 'PlantCareTestScript/1.0 (contact@plantcare.local)'
}


def get_image_url_for_plant(plant_name, sci_name=""):
    search_terms = [plant_name, sci_name, f"{plant_name} plant", f"{plant_name} leaf"]
    for term in search_terms:
        if not term:
            continue
        try:
            # 1. Search Wikipedia page title
            search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(term)}&format=json"
            req = urllib.request.Request(search_url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                sdata = json.loads(resp.read().decode('utf-8'))
                results = sdata.get('query', {}).get('search', [])
                if not results:
                    continue
                title = results[0]['title']

            # 2. Get thumbnail URL
            img_url_api = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=pageimages&pithumbsize=800&format=json"
            req = urllib.request.Request(img_url_api, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                idata = json.loads(resp.read().decode('utf-8'))
                pages = idata.get('query', {}).get('pages', {})
                for pid, pdata in pages.items():
                    if 'thumbnail' in pdata and 'source' in pdata['thumbnail']:
                        return pdata['thumbnail']['source']
        except Exception as e:
            pass

    # Unsplash fallback for general terms
    try:
        clean_name = urllib.parse.quote(plant_name.replace(" ", "-").lower())
        return f"https://source.unsplash.com/600x600/?{clean_name},plant,leaf"
    except Exception:
        return None


def main():
    print(f"[*] Total plant classes to download: {len(classes)}")
    print(f"[*] Target directory: {OUTPUT_DIR}\n")

    success_count = 0
    results_summary = []

    for i, plant_name in enumerate(classes, start=1):
        filename = plant_name.lower().replace(" ", "_").replace("'", "") + ".jpg"
        filepath = os.path.join(OUTPUT_DIR, filename)

        info = species_info.get(plant_name, {})
        sci_name = info.get("scientific_name", "")

        print(f"[{i:02d}/{len(classes):02d}] Fetching image for '{plant_name}' ({sci_name})...", end=" ", flush=True)

        if not os.path.exists(filepath) or os.path.getsize(filepath) < 1000:
            url = get_image_url_for_plant(plant_name, sci_name)
            if url:
                try:
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, timeout=12) as resp, open(filepath, 'wb') as out_file:
                        out_file.write(resp.read())

                    # Verify image can be opened by PIL
                    with Image.open(filepath) as img:
                        img.verify()
                    print(f"Downloaded -> {filename}")
                    time.sleep(0.3)
                except Exception as e:
                    print(f"FAILED ({e})")
                    if os.path.exists(filepath):
                        os.remove(filepath)
            else:
                print("URL not found")
        else:
            print(f"Already exists -> {filename}")

        if os.path.exists(filepath):
            success_count += 1
            # Run inference
            try:
                res = PlantMLEngine.identify_plant(filepath)
                pred_name = res.get('name', 'Unknown')
                conf = res.get('confidence_score', 0.0)
                results_summary.append((plant_name, pred_name, conf, filename))
            except Exception as e:
                results_summary.append((plant_name, f"Error ({e})", 0.0, filename))

    print(f"\n[+] Complete! Downloaded {success_count}/{len(classes)} plant images into '{OUTPUT_DIR}'.\n")

    print(f"{'#':<3} {'Target Class':<24} {'Predicted Class':<24} {'Conf %':<8} {'Filename':<30}")
    print("-" * 92)
    for idx, (target, pred, conf, fname) in enumerate(results_summary, start=1):
        match_flag = "✓" if target == pred else "x"
        print(f"{idx:<3} {target:<24} {pred:<24} {conf:<8.1f} {fname:<30} {match_flag}")


if __name__ == "__main__":
    main()
