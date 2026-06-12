"""
Renderiza cada página do PDF como imagem de alta resolução (DPI configurável)
e recorta as células das tabelas individualmente para capturar pictogramas/ícones
que são vetores no PDF e não aparecem como imagens embedadas.
"""
import fitz  # PyMuPDF
import pdfplumber
import os
from PIL import Image

LIVROS_DIR = "../livros"
OUTPUT_DIR = "output/page_renders"
CELL_OUTPUT_DIR = "output/cell_crops"
DPI = 200  # 200 DPI é suficiente para ícones com qualidade; use 300 para mais detalhe

def dpi_to_matrix(dpi):
    scale = dpi / 72  # PDF native is 72 DPI
    return fitz.Matrix(scale, scale)

def extract_page_renders(target_pdf: str | None = None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(CELL_OUTPUT_DIR, exist_ok=True)

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
        page_out_dir = os.path.join(OUTPUT_DIR, pdf_name)
        cell_out_dir = os.path.join(CELL_OUTPUT_DIR, pdf_name)
        os.makedirs(page_out_dir, exist_ok=True)
        os.makedirs(cell_out_dir, exist_ok=True)

        print(f"Rendering pages from {filename} at {DPI} DPI...")

        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            print(f"Failed to open {filename}: {e}")
            continue

        mat = dpi_to_matrix(DPI)
        scale = DPI / 72  # to convert PDF coords → pixel coords

        # Also open with pdfplumber to get table cell bounding boxes
        try:
            plumber_pdf = pdfplumber.open(pdf_path)
        except Exception as e:
            print(f"Failed to open {filename} with pdfplumber: {e}")
            plumber_pdf = None

        for page_num in range(len(doc)):
            page = doc[page_num]

            # Render full page as PNG
            pix = page.get_pixmap(matrix=mat)
            page_img_path = os.path.join(page_out_dir, f"page-{page_num + 1}.png")
            pix.save(page_img_path)

            # Crop individual table cells using pdfplumber bounding boxes
            if plumber_pdf:
                try:
                    pl_page = plumber_pdf.pages[page_num]
                    tables = pl_page.extract_tables()
                    table_objects = pl_page.find_tables()

                    for t_idx, table_obj in enumerate(table_objects):
                        cells = table_obj.cells  # list of (x0, top, x1, bottom) in PDF points

                        # Load rendered page image
                        page_img = Image.open(page_img_path)

                        page_height_pts = pl_page.height  # PDF page height in points

                        for c_idx, cell in enumerate(cells):
                            x0, top, x1, bottom = cell

                            # Convert PDF coords (origin bottom-left) to image coords (origin top-left)
                            px0 = int(x0 * scale)
                            py0 = int(top * scale)
                            px1 = int(x1 * scale)
                            py1 = int(bottom * scale)

                            # Avoid degenerate crops
                            if px1 - px0 < 5 or py1 - py0 < 5:
                                continue

                            crop = page_img.crop((px0, py0, px1, py1))
                            cell_dir = os.path.join(cell_out_dir, f"page-{page_num + 1}", f"table-{t_idx + 1}")
                            os.makedirs(cell_dir, exist_ok=True)
                            crop_path = os.path.join(cell_dir, f"cell-{c_idx + 1}.png")
                            crop.save(crop_path)

                except Exception as e:
                    print(f"  Cell crop error on page {page_num + 1}: {e}")

        if plumber_pdf:
            plumber_pdf.close()

        print(f"  → {len(doc)} páginas renderizadas em {page_out_dir}/")
        print(f"  → Células recortadas em {cell_out_dir}/")

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else None
    extract_page_renders(target)
