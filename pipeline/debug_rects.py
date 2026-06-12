import pdfplumber
import re
import fitz
from PIL import Image

CODE_PATTERN = re.compile(r'^[A-Z]\d+-[a-z]$')

def extract_symbols(pdf_path, page_num):
    print(f"Buscando retângulos e textos na página {page_num+1}...")
    
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_num]
        
        # Encontrar todas as palavras para ver os códigos
        words = page.extract_words()
        codes = [w for w in words if CODE_PATTERN.match(w['text'])]
        
        print(f"Códigos encontrados na pág {page_num+1}: {[c['text'] for c in codes]}")
        
        # Encontrar retângulos ou formas que agrupam
        print(f"Total rects: {len(page.rects)}")
        print(f"Total curves: {len(page.curves)}")
        
        # Vamos tentar cruzar as coordenadas dos códigos encontrados com o desenho da página
        doc = fitz.open(pdf_path)
        fitz_page = doc[page_num]
        
        # Render a página em alta resolução
        pix = fitz_page.get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Para cada código encontrado, vamos pegar uma caixa ao redor dele (ex: 150x150 pixels)
        # como fallback caso não achemos o retângulo exato.
        # No PDF, as coordenadas do pdfplumber são baseadas na altura e largura originais.
        scale_x = pix.width / page.width
        scale_y = pix.height / page.height
        
        for code in codes:
            # pdfplumber bbox: (x0, top, x1, bottom)
            x0, top, x1, bottom = code['x0'], code['top'], code['x1'], code['bottom']
            
            # Vamos estimar uma caixa ao redor do código (tentativa visual)
            # Geralmente o símbolo está acima ou ao lado do código.
            box_width = 100
            box_height = 100
            
            # Converter coordenadas para pixels do render
            px0 = max(0, (x0 - box_width/2) * scale_x)
            ptop = max(0, (top - box_height) * scale_y)
            px1 = min(pix.width, (x1 + box_width/2) * scale_x)
            pbottom = min(pix.height, (bottom + 20) * scale_y)
            
            crop = img.crop((px0, ptop, px1, pbottom))
            crop.save(f"debug_{code['text']}.png")
            print(f"Salvo crop de debug para {code['text']}")

if __name__ == "__main__":
    extract_symbols("../livros/icon-regras-visuais.pdf", 2) # página 3 (index 2)
