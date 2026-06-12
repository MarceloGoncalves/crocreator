import yaml
import json
import os

MANIFEST_FILE = "symbols-manifest.yaml"
CATALOG_OUTPUT = "../src/assets/catalog.json"
RAW_SYMBOLS_DIR = "../src/assets/symbols/raw"
FINAL_SYMBOLS_DIR = "../src/assets/symbols"

def generate_catalog():
    if not os.path.exists(MANIFEST_FILE):
        print(f"Manifest not found: {MANIFEST_FILE}")
        return

    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)

    if not manifest or "symbols" not in manifest or not manifest["symbols"]:
        print("No symbols defined in manifest.")
        return

    catalog = {
        "symbols": []
    }

    os.makedirs(FINAL_SYMBOLS_DIR, exist_ok=True)

    for sym in manifest["symbols"]:
        source_file = sym.get("source")
        if not source_file:
            print(f"Symbol {sym.get('id')} missing 'source'. Skipping.")
            continue
            
        source_path = os.path.join(RAW_SYMBOLS_DIR, source_file)
        
        # Copy to final directory
        final_file = f"{sym['id']}.svg"
        final_path = os.path.join(FINAL_SYMBOLS_DIR, final_file)
        
        if os.path.exists(source_path):
            with open(source_path, "rb") as s, open(final_path, "wb") as d:
                d.write(s.read())
                
            catalog["symbols"].append({
                "id": sym["id"],
                "name": sym["name"],
                "category": sym.get("category", "undefined"),
                "file": f"assets/symbols/{final_file}",
                "source": source_file
            })
        else:
            print(f"Warning: Source file not found: {source_path}")

    # Write catalog.json
    with open(CATALOG_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
        
    print(f"Catalog generated with {len(catalog['symbols'])} symbols.")

if __name__ == "__main__":
    generate_catalog()
