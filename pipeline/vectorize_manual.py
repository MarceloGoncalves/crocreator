import os
import glob
from PIL import Image
import vtracer

INPUT_DIR = "../livros/img"
OUTPUT_DIR = "../public/assets/symbols"

def preprocess_image(img_path, temp_path):
    with Image.open(img_path) as img:
        # Convert to RGBA first to handle transparency
        img = img.convert("RGBA")
        
        # Create a white background
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        # Composite the image onto the white background
        combined = Image.alpha_composite(bg, img)
        
        # Convert to grayscale
        gray = combined.convert('L')
        # Threshold
        threshold = 200
        bw = gray.point(lambda x: 0 if x < threshold else 255, '1')
        bw.save(temp_path)

def vectorize():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    temp_dir = "output/temp_manual"
    os.makedirs(temp_dir, exist_ok=True)
    
    files = glob.glob(f"{INPUT_DIR}/*.png") + glob.glob(f"{INPUT_DIR}/*.jpg")
    print(f"Vectorizing {len(files)} manual images...")
    
    for f in files:
        # e.g., "b1-a.png" -> "B1-a" -> "B1_a"
        basename = os.path.basename(f).rsplit('.', 1)[0].upper()
        # Some might have "-direita", we keep it but replace all dashes with underscores for consistency with our SVG naming conventions.
        # Wait, our catalog has B1_a.svg. The user named it b1-a.png.
        # So we upper case it and replace '-' with '_'.
        # Exception: if it's like b1-c-direita, we get B1_C_DIREITA.
        # Let's see what the catalog has. The catalog uses e.g. "B1_a.svg".
        # So we just upper case the whole string except the extension, and replace '-' with '_'.
        # Wait! The catalog code is "B1-a" and id is "B1_a".
        
        # We need to map the user's name format (e.g. b1-a) to our format (B1_a).
        # Actually, let's just make it upper-case for the first letter?
        # b1-a -> B1-a -> B1_a.
        if '-' in basename:
            parts = basename.split('-')
            # First part like B1, B2...
            # The rest is the letter (a, b) and maybe "direita"
            # We want B1_a instead of B1_A.
            # So:
            prefix = parts[0].upper()
            suffix = "_".join(parts[1:]).lower()
            svg_name = f"{prefix}_{suffix}.svg"
        else:
            svg_name = basename + ".svg"
            
        svg_path = os.path.join(OUTPUT_DIR, svg_name)
        temp_img_path = os.path.join(temp_dir, f"{os.path.basename(f)}")
        
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
            print(f"Vectorized {basename} -> {svg_name}")
        except Exception as e:
            print(f"Error {basename}: {e}")
            
    print("Vectorization complete.")

if __name__ == "__main__":
    vectorize()
