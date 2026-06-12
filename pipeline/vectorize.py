import os
import glob
from PIL import Image
import vtracer

INPUT_DIR = "output/raw"
OUTPUT_DIR = "../src/assets/symbols/raw"

def preprocess_image(img_path, temp_path):
    # Convert to grayscale and apply threshold
    with Image.open(img_path) as img:
        gray = img.convert('L')
        # Simple binary threshold
        threshold = 200
        bw = gray.point(lambda x: 0 if x < threshold else 255, '1')
        bw.save(temp_path)

def vectorize_images():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    temp_dir = "output/temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Find all image files in output/raw (png, jpg, jpeg)
    all_files = (
        glob.glob(f"{INPUT_DIR}/**/*.png", recursive=True) +
        glob.glob(f"{INPUT_DIR}/**/*.jpg", recursive=True) +
        glob.glob(f"{INPUT_DIR}/**/*.jpeg", recursive=True)
    )
    
    print(f"Found {len(all_files)} images to vectorize.")
    
    for img_path in all_files:
        # Create a unique filename for the output SVG
        rel_path = os.path.relpath(img_path, INPUT_DIR)
        base_name = rel_path.replace(os.sep, "_").rsplit('.', 1)[0]
        svg_filename = f"{base_name}.svg"
        svg_path = os.path.join(OUTPUT_DIR, svg_filename)
        temp_img_path = os.path.join(temp_dir, f"{base_name}.png")
        
        try:
            # Preprocess
            preprocess_image(img_path, temp_img_path)
            
            # Vectorize using vtracer
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
            print(f"Failed to vectorize {img_path}: {e}")

if __name__ == "__main__":
    vectorize_images()
