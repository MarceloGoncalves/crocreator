"""
Gera um preview HTML cruzando:
  - Dados textuais extraídos (código, nome, significado)
  - Thumbnails das páginas renderizadas como referência visual

O documento "icon-regras-visuais" define REGRAS para os símbolos (texto),
não contém os ícones como gráficos — por isso o preview mostra o texto
estruturado + página renderizada como contexto visual.
"""
import fitz
import pdfplumber
import os
import re
import base64
from PIL import Image
import io

LIVROS_DIR = "../livros"
TEXT_DIR = "output/text"
RENDERS_DIR = "output/page_renders"
OUTPUT_HTML = "output/preview.html"
DPI = 200
SCALE = DPI / 72

# Regex para códigos tipo B1-a, B2-c, A3-d, [.]
CODE_PATTERN = re.compile(r'^([A-Z]\d+-[a-z])$')

def img_to_base64_thumb(img: Image.Image, max_w: int = 400) -> str:
    ratio = max_w / img.width
    thumb = img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    thumb.save(buf, format="JPEG", quality=75)
    return base64.b64encode(buf.getvalue()).decode()

def extract_sections_from_text(text_path: str) -> list[dict]:
    if not os.path.exists(text_path):
        return []
    with open(text_path, encoding="utf-8") as f:
        text = f.read()
    lines = [l.strip() for l in text.splitlines()]
    sections = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if CODE_PATTERN.match(line):
            code = line
            name = lines[i + 1] if i + 1 < len(lines) else ""
            meaning_lines = []
            j = i + 2
            while j < len(lines) and not CODE_PATTERN.match(lines[j]) and lines[j] != "[.]":
                if lines[j]:
                    meaning_lines.append(lines[j])
                j += 1
            sections.append({"code": code, "name": name, "meaning": " ".join(meaning_lines)})
            i = j
        else:
            i += 1
    return sections

def get_section_title(text_path: str, page_num: int) -> str:
    title = f"Página {page_num + 1}"
    if not os.path.exists(text_path):
        return title
    with open(text_path, encoding="utf-8") as f:
        lines = f.readlines()
    skip = {"Guia", "Federação", "pág", ""}
    for line in lines[2:12]:
        s = line.strip()
        if s and not any(s.startswith(k) for k in skip):
            return s
    return title

def build_preview(target_pdf: str):
    pdf_name = os.path.splitext(target_pdf)[0]
    pdf_path = os.path.join(LIVROS_DIR, target_pdf)
    text_dir = os.path.join(TEXT_DIR, pdf_name)
    renders_dir = os.path.join(RENDERS_DIR, pdf_name)

    print(f"Building preview for {target_pdf}...")

    try:
        doc = fitz.open(pdf_path)
        num_pages = len(doc)
    except Exception as e:
        print(f"Cannot open PDF: {e}")
        return

    all_pages_data = []

    for page_num in range(num_pages):
        text_path = os.path.join(text_dir, f"page-{page_num + 1}.txt")
        sections = extract_sections_from_text(text_path)

        # Load page thumbnail
        page_png = os.path.join(renders_dir, f"page-{page_num + 1}.png")
        page_thumb_b64 = None
        if os.path.exists(page_png):
            try:
                img = Image.open(page_png)
                page_thumb_b64 = img_to_base64_thumb(img, max_w=450)
            except Exception:
                pass

        # Include page if it has symbol rows OR if it has a page render worth showing
        if sections or page_thumb_b64:
            title = get_section_title(text_path, page_num)
            all_pages_data.append({
                "page": page_num + 1,
                "title": title,
                "sections": sections,
                "page_thumb_b64": page_thumb_b64,
            })

    # Filter: only pages with sections (text) or interesting renders
    pages_with_content = [p for p in all_pages_data if p["sections"]]
    pages_render_only = [p for p in all_pages_data if not p["sections"] and p["page_thumb_b64"]]

    html = generate_html(pdf_name, pages_with_content, pages_render_only)
    os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    total_symbols = sum(len(p["sections"]) for p in pages_with_content)
    print(f"Preview generated: {OUTPUT_HTML}")
    print(f"  {total_symbols} símbolos em {len(pages_with_content)} seções de texto")
    print(f"  {len(pages_render_only)} páginas visuais (sem texto de símbolos)")

def generate_html(title: str, pages_data: list[dict], visual_pages: list[dict]) -> str:
    nav_symbol_items = "\n".join(
        f'<li><a href="#section-{p["page"]}">{p["title"]}</a></li>'
        for p in pages_data
    )
    nav_visual_items = "\n".join(
        f'<li><a href="#visual-{p["page"]}">Página {p["page"]}</a></li>'
        for p in visual_pages
    )

    # Render symbol sections
    sections_html = ""
    for p in pages_data:
        rows_html = ""
        for r in p["sections"]:
            rows_html += f"""
            <tr>
              <td class="code">{r["code"]}</td>
              <td class="name">{r["name"]}</td>
              <td class="meaning">{r["meaning"]}</td>
            </tr>"""

        thumb_html = ""
        if p["page_thumb_b64"]:
            thumb_html = f'<div class="page-thumb"><img src="data:image/jpeg;base64,{p["page_thumb_b64"]}" alt="Página {p["page"]}" /><p>Página {p["page"]}</p></div>'

        sections_html += f"""
        <section id="section-{p["page"]}">
          <h2>{p["title"]}</h2>
          <div class="section-content">
            <table>
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Nome</th>
                  <th>Significado</th>
                </tr>
              </thead>
              <tbody>
                {rows_html}
              </tbody>
            </table>
            {thumb_html}
          </div>
        </section>"""

    # Render visual-only pages
    visual_html = ""
    if visual_pages:
        visual_html = '<h2 class="visual-header">Páginas Visuais de Referência</h2>'
        for p in visual_pages:
            if p["page_thumb_b64"]:
                visual_html += f"""
                <div class="visual-page" id="visual-{p["page"]}">
                  <h3>Página {p["page"]}</h3>
                  <img src="data:image/jpeg;base64,{p["page_thumb_b64"]}" alt="Página {p["page"]}" />
                </div>"""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8"/>
  <title>Preview — {title}</title>
  <style>
    :root {{
      --bg: #0f1117; --surface: #1a1d27; --border: #2d3147;
      --accent: #5b7fff; --text: #e2e8f0; --muted: #8892a4;
      --green: #34d399; --yellow: #fbbf24;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: var(--bg); color: var(--text); font-family: 'Segoe UI', system-ui, sans-serif; display: flex; min-height: 100vh; }}

    nav {{
      width: 240px; min-height: 100vh; background: var(--surface);
      border-right: 1px solid var(--border); padding: 24px 14px;
      position: sticky; top: 0; height: 100vh; overflow-y: auto; flex-shrink: 0;
    }}
    nav h1 {{ font-size: 12px; text-transform: uppercase; letter-spacing: 0.1em; color: var(--accent); margin-bottom: 12px; }}
    nav h2 {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--yellow); margin: 18px 0 6px; }}
    nav ul {{ list-style: none; }}
    nav li {{ margin-bottom: 2px; }}
    nav a {{ display: block; padding: 5px 10px; border-radius: 5px; color: var(--muted); text-decoration: none; font-size: 12px; transition: all 0.15s; }}
    nav a:hover {{ background: var(--border); color: var(--text); }}

    main {{ flex: 1; padding: 40px 48px; max-width: 1200px; }}
    main > h1 {{ font-size: 22px; font-weight: 700; margin-bottom: 6px; }}
    main > p {{ color: var(--muted); font-size: 13px; margin-bottom: 36px; line-height: 1.6; }}

    section {{ margin-bottom: 56px; }}
    section h2 {{ font-size: 17px; font-weight: 600; margin-bottom: 14px; padding-bottom: 10px; border-bottom: 1px solid var(--border); color: var(--green); }}
    .section-content {{ display: flex; gap: 24px; align-items: flex-start; }}
    
    table {{ flex: 1; border-collapse: collapse; font-size: 13px; min-width: 0; }}
    thead tr {{ background: var(--surface); }}
    th {{ padding: 9px 12px; text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); border-bottom: 1px solid var(--border); }}
    td {{ padding: 9px 12px; border-bottom: 1px solid var(--border); vertical-align: top; }}
    tr:hover td {{ background: rgba(91,127,255,0.04); }}
    td.code {{ font-family: monospace; color: var(--accent); white-space: nowrap; width: 70px; }}
    td.name {{ width: 160px; font-weight: 500; color: var(--text); }}
    td.meaning {{ color: var(--muted); line-height: 1.5; }}

    .page-thumb {{ flex-shrink: 0; width: 200px; text-align: center; }}
    .page-thumb img {{ width: 100%; border-radius: 6px; border: 1px solid var(--border); }}
    .page-thumb p {{ font-size: 11px; color: var(--muted); margin-top: 6px; }}

    .visual-header {{ font-size: 17px; font-weight: 600; margin: 48px 0 16px; color: var(--yellow); border-bottom: 1px solid var(--border); padding-bottom: 10px; }}
    .visual-page {{ margin-bottom: 32px; }}
    .visual-page h3 {{ font-size: 14px; color: var(--muted); margin-bottom: 10px; }}
    .visual-page img {{ max-width: 600px; border-radius: 8px; border: 1px solid var(--border); display: block; }}
  </style>
</head>
<body>
  <nav>
    <h1>🧗 {title}</h1>
    <ul>{nav_symbol_items}</ul>
    {'<h2>Visuais</h2><ul>' + nav_visual_items + '</ul>' if nav_visual_items else ''}
  </nav>
  <main>
    <h1>Catálogo de Símbolos — Preview</h1>
    <p>
      Gerado automaticamente pelo pipeline. O PDF de regras define os símbolos em texto — 
      use as páginas visuais de referência para ver os exemplos gráficos.<br/>
      Preencha o <code>symbols-manifest.yaml</code> com base nestas informações.
    </p>
    {sections_html}
    {visual_html}
  </main>
</body>
</html>"""

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "icon-regras-visuais.pdf"
    build_preview(target)
