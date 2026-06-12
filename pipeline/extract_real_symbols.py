import pdfplumber
import re
import fitz
import os
from PIL import Image

CODE_PATTERN = re.compile(r'^[A-Z]\d+-[a-z]$')

def extract_symbols(pdf_path):
    os.makedirs("extracted_icons", exist_ok=True)
    doc = fitz.open(pdf_path)
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            # Encontrar tabelas para saber a área delas
            tables = page.find_tables()
            table_bboxes = [t.bbox for t in tables]
            
            words = page.extract_words()
            codes = [w for w in words if CODE_PATTERN.match(w['text'])]
            
            # Filtrar apenas os códigos que estão FORA das tabelas
            drawing_labels = []
            for code in codes:
                x0, top, x1, bottom = code['x0'], code['top'], code['x1'], code['bottom']
                in_table = False
                for (tx0, ttop, tx1, tbottom) in table_bboxes:
                    # Checar se o centro da palavra está dentro da tabela
                    cx, cy = (x0+x1)/2, (top+bottom)/2
                    if tx0 <= cx <= tx1 and ttop <= cy <= tbottom:
                        in_table = True
                        break
                if not in_table:
                    drawing_labels.append(code)
            
            if not drawing_labels:
                continue
                
            print(f"Pág {page_num+1}: Encontrados {len(drawing_labels)} labels gráficos: {[l['text'] for l in drawing_labels]}")
            
            fitz_page = doc[page_num]
            pix = fitz_page.get_pixmap(dpi=300)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            scale_x = pix.width / page.width
            scale_y = pix.height / page.height
            
            # Para cada label encontrado, procurar a "caixa" ou simplesmente recortar a área em volta.
            # Como a usuária mencionou "dentro de retângulos", vamos tentar achar os retângulos da página!
            rects = page.rects + page.curves
            
            for label in drawing_labels:
                lx0, ltop, lx1, lbottom = label['x0'], label['top'], label['x1'], label['bottom']
                
                # Encontrar o retângulo que engloba esse label, ou o retângulo mais próximo.
                # Como alternativa visual segura: recortar uma área acima e em volta do label.
                # A usuária diz "dentro de retangulos com uma marcação". 
                # Vamos recortar um pedaço que pegue o label e o que está logo acima/lado dele.
                box_width = 250
                box_height = 250
                
                px0 = max(0, (lx0 - box_width/2) * scale_x)
                ptop = max(0, (ltop - box_height + 20) * scale_y) # mais para cima
                px1 = min(pix.width, (lx1 + box_width/2) * scale_x)
                pbottom = min(pix.height, (lbottom + 20) * scale_y)
                
                crop = img.crop((px0, ptop, px1, pbottom))
                out_path = f"extracted_icons/{label['text']}.png"
                crop.save(out_path)

if __name__ == "__main__":
    extract_symbols("../livros/icon-regras-visuais.pdf")
    print("Processo finalizado!")
