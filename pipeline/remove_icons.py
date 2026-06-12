import json
import os

CODES_TO_REMOVE = [
    "B1-c", "B3-a", "B3-b", "B3-c", "B3-d", "B3-e", "B3-f", "B3-g", "B3-h",
    "B4-a", "B4-b", "B4-c", "B4-d", "B6-c", "B6-d", "B6-e"
]

def main():
    cat_path = "../public/assets/catalog.json"
    with open(cat_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    original_count = len(data["symbols"])
    filtered_symbols = [s for s in data["symbols"] if s["code"] not in CODES_TO_REMOVE]
    
    data["symbols"] = filtered_symbols
    
    with open(cat_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Removed {original_count - len(filtered_symbols)} icons.")

if __name__ == "__main__":
    main()
