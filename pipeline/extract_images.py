import fitz  # PyMuPDF
import os
import io
from PIL import Image

LIVROS_DIR = "../livros"
OUTPUT_DIR = "output/raw"
SKIPPED_LOG = "output/skipped.log"
MIN_WIDTH = 50
MIN_HEIGHT = 50

def extract_images(target_pdf: str | None = None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(SKIPPED_LOG, "w") as log_file:
        pass # Clear previous log

    if not os.path.exists(LIVROS_DIR):
        print(f"Directory not found: {LIVROS_DIR}")
        return

    all_files = os.listdir(LIVROS_DIR)
    files_to_process = [target_pdf] if target_pdf else all_files

    for filename in files_to_process:
        if not filename.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(LIVROS_DIR, filename)
        pdf_name = os.path.splitext(filename)[0]
        pdf_out_dir = os.path.join(OUTPUT_DIR, pdf_name)
        
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            print(f"Failed to open {filename}: {e}")
            continue

        print(f"Extracting images from {filename}...")
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images(full=True)
            
            if image_list:
                page_out_dir = os.path.join(pdf_out_dir, f"page-{page_num + 1}")
                os.makedirs(page_out_dir, exist_ok=True)
                
                for img_index, img in enumerate(image_list, start=1):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    try:
                        image = Image.open(io.BytesIO(image_bytes))
                    except Exception:
                        continue
                    
                    width, height = image.size
                    
                    if width < MIN_WIDTH or height < MIN_HEIGHT:
                        with open(SKIPPED_LOG, "a") as log_file:
                            log_file.write(f"Skipped {filename} Page {page_num + 1} Image {img_index} - Size: {width}x{height}\n")
                        continue
                    
                    img_filename = f"img-{img_index}.{image_ext}"
                    img_path = os.path.join(page_out_dir, img_filename)
                    
                    with open(img_path, "wb") as f:
                        f.write(image_bytes)

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else None
    extract_images(target)
