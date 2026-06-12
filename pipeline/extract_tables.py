import pdfplumber
import os
import csv

LIVROS_DIR = "../livros"
OUTPUT_DIR = "output/tables"

def extract_tables(target_pdf: str | None = None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
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
        
        print(f"Extracting tables from {filename}...")
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    tables = page.extract_tables()
                    for j, table in enumerate(tables):
                        if not table:
                            continue
                            
                        csv_filename = f"{pdf_name}-page-{i + 1}-table-{j + 1}.csv"
                        csv_path = os.path.join(OUTPUT_DIR, csv_filename)
                        
                        with open(csv_path, "w", newline="", encoding="utf-8") as f:
                            writer = csv.writer(f)
                            writer.writerows(table)
        except Exception as e:
            print(f"Failed to extract tables from {filename}: {e}")

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else None
    extract_tables(target)
