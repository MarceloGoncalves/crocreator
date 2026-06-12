import os
import glob
import json
import vtracer
from PIL import Image
from generate_placeholders import SYMBOLS, CATEGORIES

INPUT_DIR = "../livros/img"
OUTPUT_DIR = "../public/assets/symbols"
CATALOG_PATH = "../public/assets/catalog.json"

def preprocess_image(img_path, temp_path):
    with Image.open(img_path) as img:
        img = img.convert("RGBA")
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        combined = Image.alpha_composite(bg, img)
        gray = combined.convert('L')
        threshold = 200
        bw = gray.point(lambda x: 0 if x < threshold else 255, '1')
        bw.save(temp_path)

def get_symbol_info(code_prefix):
    # Try to find exact match first
    for s in SYMBOLS:
        if s[0].lower() == code_prefix.lower():
            return s
    # Try to find prefix match (e.g. b4-a from b4-a-parada-fixa)
    for s in SYMBOLS:
        if code_prefix.lower().startswith(s[0].lower()):
            return s
    return None

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    temp_dir = "output/temp_manual"
    os.makedirs(temp_dir, exist_ok=True)
    
    files = glob.glob(f"{INPUT_DIR}/*.png") + glob.glob(f"{INPUT_DIR}/*.jpg")
    print(f"Processing {len(files)} manual images...")
    
    catalog = {"symbols": []}
    
    for f in sorted(files):
        basename = os.path.basename(f).rsplit('.', 1)[0] # e.g. b4-a-parada-fixa
        svg_name = f"{basename}.svg"
        svg_path = os.path.join(OUTPUT_DIR, svg_name)
        temp_img_path = os.path.join(temp_dir, os.path.basename(f))
        
        # Vectorize
        try:
            preprocess_image(f, temp_img_path)
            vtracer.convert_image_to_svg_py(
                temp_img_path,
                svg_path,
                colormode='binary',
                hierarchical='stacked',
                mode='polygon',
                filter_speckle=4,
                color_precision=6,
                layer_difference=16,
                corner_threshold=60,
                length_threshold=4.0,
                max_iterations=10,
                splice_threshold=45,
                path_precision=8
            )
        except Exception as e:
            print(f"Error vectorizing {basename}: {e}")
            continue
            
        # Build Catalog Entry
        info = get_symbol_info(basename)
        if info:
            code, orig_name, category, _, color = info
            # Make a nice name
            if basename.lower() != code.lower():
                if basename.lower() == 'b4-d-arvore':
                    name = "Parada em Arvore"
                else:
                    suffix = basename[len(code):].strip('-').replace('-', ' ').title()
                    if suffix.lower() == orig_name.lower() or suffix.lower() == orig_name.replace('ô', 'o').lower():
                        name = orig_name
                    elif category == "reuniao" or category == "terreno" or category == "via":
                        name = suffix
                    else:
                        name = f"{orig_name} ({suffix})"
            else:
                name = orig_name
        else:
            # Fallback
            code = basename
            name = basename.replace('-', ' ')
            category = "undefined"
            color = "#fff"
            # Try to guess category from prefix
            prefix = basename.split('-')[0].upper()
            if prefix == "B1": category = "informacao"
            elif prefix == "B2": category = "referencia_natural"
            elif prefix == "B3": category = "protecao"
            elif prefix == "B4": category = "reuniao"
            elif prefix == "B5": category = "via"
            elif prefix == "B6": category = "terreno"
            elif prefix == "B7": category = "cotacao"
            
        catalog["symbols"].append({
            "id": basename,
            "code": code,
            "name": name,
            "category": category,
            "categoryLabel": CATEGORIES.get(category, category),
            "file": f"assets/symbols/{svg_name}",
            "color": color,
            "placeholder": False,
        })

    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
        
    print(f"Catalog generated with {len(catalog['symbols'])} real SVGs!")

if __name__ == "__main__":
    main()
