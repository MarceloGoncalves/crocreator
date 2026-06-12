import sys
from extract_images import extract_images
from extract_tables import extract_tables
from extract_text import extract_text
from extract_page_renders import extract_page_renders

def main(target_pdf: str | None = None):
    if target_pdf:
        print(f"--- Starting Pipeline (target: {target_pdf}) ---")
    else:
        print("--- Starting Pipeline (all PDFs) ---")

    print("\n[1/4] Extracting embedded raster images...")
    extract_images(target_pdf)

    print("\n[2/4] Extracting tables as CSV...")
    extract_tables(target_pdf)

    print("\n[3/4] Extracting text per page...")
    extract_text(target_pdf)

    print("\n[4/4] Rendering pages and cropping table cells (pictograms)...")
    extract_page_renders(target_pdf)

    print("\n--- Pipeline Completed ---")
    print("Outputs:")
    print("  output/raw/          → embedded raster images")
    print("  output/tables/       → table CSVs")
    print("  output/text/         → text per page + table text")
    print("  output/page_renders/ → full page PNGs")
    print("  output/cell_crops/   → individual table cell crops (pictograms)")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    main(target)
