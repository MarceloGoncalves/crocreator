"""
Extrai texto de cada página do PDF, salvando em arquivos .txt por página.
Inclui também o texto dentro de células de tabelas para dar contexto máximo.
"""
import fitz  # PyMuPDF
import pdfplumber
import os

LIVROS_DIR = "../livros"
OUTPUT_DIR = "output/text"

def extract_text(target_pdf: str | None = None):
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
        pdf_out_dir = os.path.join(OUTPUT_DIR, pdf_name)
        os.makedirs(pdf_out_dir, exist_ok=True)

        print(f"Extracting text from {filename}...")

        # Full-document text for easy reading
        full_text_path = os.path.join(pdf_out_dir, "full_text.txt")

        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            print(f"Failed to open {filename}: {e}")
            continue

        full_lines = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text("text")

            # Per-page text file
            page_path = os.path.join(pdf_out_dir, f"page-{page_num + 1}.txt")
            with open(page_path, "w", encoding="utf-8") as f:
                f.write(f"=== Página {page_num + 1} ===\n\n")
                f.write(page_text)

            full_lines.append(f"=== Página {page_num + 1} ===\n\n{page_text}\n")

        with open(full_text_path, "w", encoding="utf-8") as f:
            f.writelines(full_lines)

        # Extract table text with structure using pdfplumber
        tables_text_path = os.path.join(pdf_out_dir, "tables_text.txt")
        try:
            with pdfplumber.open(pdf_path) as pdf, open(tables_text_path, "w", encoding="utf-8") as tf:
                for i, page in enumerate(pdf.pages):
                    tables = page.extract_tables()
                    for j, table in enumerate(tables):
                        if not table:
                            continue
                        tf.write(f"\n=== Página {i + 1} — Tabela {j + 1} ===\n")
                        for row in table:
                            row_str = " | ".join(
                                (cell.strip() if isinstance(cell, str) else "") 
                                for cell in (row or [])
                            )
                            tf.write(row_str + "\n")
        except Exception as e:
            print(f"Failed to extract table text from {filename}: {e}")

        print(f"  → {len(doc)} páginas extraídas em {pdf_out_dir}/")

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else None
    extract_text(target)
