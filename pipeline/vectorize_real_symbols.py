import os
import glob
from PIL import Image
import vtracer

INPUT_DIR = "extracted_icons"
OUTPUT_DIR = "../public/assets/symbols"

def preprocess_image(img_path, temp_path):
    with Image.open(img_path) as img:
        gray = img.convert('L')
        threshold = 200
        bw = gray.point(lambda x: 0 if x < threshold else 255, '1')
        bw.save(temp_path)

def vectorize():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    temp_dir = "output/temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    files = glob.glob(f"{INPUT_DIR}/*.png")
    print(f"Vectorizing {len(files)} files...")
    
    for f in files:
        basename = os.path.basename(f).replace(".png", "") # e.g. "B1-a"
        svg_name = basename.replace("-", "_") + ".svg"
        svg_path = os.path.join(OUTPUT_DIR, svg_name)
        temp_img_path = os.path.join(temp_dir, f"{basename}.png")
        
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
            print(f"Error {basename}: {e}")
            
    print("Done! Check your browser, the icons should be updated.")

if __name__ == "__main__":
    vectorize()
