"""
Gera SVGs placeholder para os 45 símbolos extraídos e cria o catalog.json.
"""
import os, json, re

SYMBOLS_DIR = "../src/assets/symbols"
CATALOG_PATH = "../src/assets/catalog.json"

SYMBOLS = [
    # B1 - Sinais de informação
    ("B1-a","atenção","informacao","M50,10 L90,80 L10,80 Z","#f59e0b"),
    ("B1-b","exposição","informacao","M50,15 A35,35,0,1,1,50,85 A35,35,0,1,1,50,15","#ef4444"),
    ("B1-c","pêndulo perigoso","informacao","M50,10 L70,50 L50,90 L30,50 Z","#f97316"),
    ("B1-d","laca solta ou podre","informacao","M20,80 Q50,10 80,80","#a78bfa"),
    ("B1-e","cascalho","informacao","M30,70 A8,8,0,1,1,30,69 M50,75 A6,6,0,1,1,50,74 M70,70 A8,8,0,1,1,70,69","#94a3b8"),
    ("B1-f","bloco solto","informacao","M25,75 L50,30 L75,75 Z","#6b7280"),
    ("B1-g","informações","informacao","M50,20 A30,30,0,1,1,50,80 A30,30,0,1,1,50,20 M50,42 L50,58 M50,36 A3,3,0,1,1,50,35","#3b82f6"),
    # B2 - Referências naturais
    ("B2-a","vegetação arbórea","referencia_natural","M50,15 L70,50 H60 L75,75 H25 L40,50 H30 Z","#22c55e"),
    ("B2-b","vegetação arbustiva","referencia_natural","M30,75 Q50,40 70,75 M20,75 Q50,30 80,75","#86efac"),
    ("B2-c","vegetação espinhosa","referencia_natural","M50,20 L55,40 L70,30 L60,50 L80,55 L60,60 L65,80 L50,70 L35,80 L40,60 L20,55 L40,50 L30,30 L45,40 Z","#4ade80"),
    ("B2-d","totem","referencia_natural","M40,80 L40,50 L35,40 L50,20 L65,40 L60,50 L60,80 Z","#d97706"),
    ("B2-e","bloco de rocha","referencia_natural","M20,75 L35,40 L65,40 L80,75 Z","#78716c"),
    ("B2-f","curso d'água","referencia_natural","M15,50 Q30,35 45,50 Q60,65 75,50 Q90,35 95,50","#38bdf8"),
    ("B2-g","poço ou cacimba","referencia_natural","M25,55 A25,15,0,1,1,75,55 L75,75 A25,15,0,1,1,25,75 Z","#0ea5e9"),
    # B3 - Traçados e Proteções
    ("B3-a","Rota da via ou da variante","protecao","M45,20 L55,20 L55,75 L45,75 Z M30,70 L70,70","#000000"),
    ("B3-b","Rota em Artificial","protecao","M45,20 L55,20 L55,75 L45,75 Z M30,70 L70,70 M35,55 L65,55","#94a3b8"),
    ("B3-c","trecho de caminhada","protecao","M50,20 L60,55 L50,80 L40,55 Z","#c084fc"),
    ("B3-d","corda fixa ou cabo de aço","protecao","M50,15 L85,70 L15,70 Z M50,40 L50,58","#fb923c"),
    ("B3-e","passagem em pendulo a esquerda e a direita","protecao","M20,50 L80,50 L80,65 L20,65 Z","#60a5fa"),
    ("B3-f","buraco de cliff","protecao","M45,15 L55,15 L55,85 L45,85 Z","#a78bfa"),
    ("B3-g","proteção do tipo FIXA","protecao","M50,15 L20,85 M50,15 L80,85","#818cf8"),
    ("B3-h","proteção do tipo MÓVEL","protecao","M20,30 L80,30 L75,70 L25,70 Z","#e2e8f0"),
    ("B3-i","proteção do tipo PITON","protecao","M30,30 L70,30 L70,70 L30,70 Z","#e2e8f0"),
    ("B3-j","proteção em fita","protecao","M40,40 L60,40 L60,60 L40,60 Z","#e2e8f0"),
    # B4 - Reuniões e Ancoragens
    ("B4-a","reunião com grampos","reuniao","M50,50 A15,15,0,1,1,50,49 M35,75 L50,50 L65,75","#fbbf24"),
    ("B4-b","reunião com árvore","reuniao","M50,30 A20,30,0,0,1,50,80 M35,75 L50,55 L65,75","#4ade80"),
    ("B4-c","reunião com blocos","reuniao","M30,45 L50,20 L70,45 L50,80 Z","#a78bfa"),
    ("B4-d","reunião autoequalizante","reuniao","M25,60 L50,35 L75,60 L65,75 L35,75 Z","#f472b6"),
    ("B4-e","parada em pedra","reuniao","M25,60 L50,35 L75,60 L65,75 L35,75 Z","#f472b6"),
    # B5 - Referências naturais escaláveis
    ("B5-a","Aresta","via","M50,10 L50,90","#e2e8f0"),
    ("B5-b","Diedro","via","M50,80 A20,20,0,1,1,50,40 L50,80","#34d399"),
    ("B5-c","Canaleta Seca","via","M50,80 L40,60 L60,60 Z","#f87171"),
    ("B5-d","Pilar ou coluna","via","M50,75 L50,25 M40,40 L50,25 L60,40","#60a5fa"),
    ("B5-e","Rampão ou Laje","via","M30,80 Q50,50 70,20 M50,80 Q65,55 80,30","#fb923c"),
    ("B5-f","Platô","via","M20,20 L80,80 M80,20 L20,80","#fbbf24"),
    ("B5-g","Teto","via","M50,20 L50,80 M35,65 L50,80 L65,65","#a78bfa"),
    ("B5-h","Trecho Negativo","via","M50,20 L50,80 M35,65 L50,80 L65,65","#a78bfa"),
    ("B5-i","Trecho Vertical","via","M50,20 L50,80 M35,65 L50,80 L65,65","#a78bfa"),
    ("B5-j","Cristaleira","via","M50,20 L50,80 M35,65 L50,80 L65,65","#a78bfa"),
    ("B5-k","Chorreira","via","M50,20 L50,80 M35,65 L50,80 L65,65","#a78bfa"),
    ("B5-l","Lance em Barriga","via","M50,20 L50,80 M35,65 L50,80 L65,65","#a78bfa"),
    # B6 - Características do terreno
    ("B6-a","teto ou extraplombo","terreno","M15,50 L85,50 L85,65 L15,65 M15,50 L30,70 M85,50 L70,70","#94a3b8"),
    ("B6-b","rampa ou slab","terreno","M15,80 L85,30 L85,80 Z","#78716c"),
    ("B6-c","diedro","terreno","M25,20 L50,80 L75,20","#6b7280"),
    ("B6-d","aresta","terreno","M50,15 L50,85 M30,30 L50,15 L70,30","#94a3b8"),
    ("B6-e","chaminé","terreno","M30,20 L30,80 L70,80 L70,20","#78716c"),
    ("B6-f","butrino","terreno","M30,25 A20,20,0,0,1,70,25 L70,75 A20,20,0,0,1,30,75 Z","#6b7280"),
    ("B6-g","fissura horizontal","terreno","M15,50 L85,50","#94a3b8"),
    # B7 - Cotações
    ("B7-a","grau numérico","cotacao","M35,20 L35,80 M35,50 L65,50 M65,20 L65,80","#fbbf24"),
    ("B7-b","grau francês","cotacao","M30,30 Q50,15 70,30 Q80,50 50,65 Q20,80 50,80","#fbbf24"),
    ("B7-c","grau UIAA","cotacao","M25,20 L50,75 L75,20","#f59e0b"),
    ("B7-d","grau de exposição E","cotacao","M30,20 L30,80 L70,80 M30,50 L60,50 M30,20 L70,20","#ef4444"),
    ("B7-e","solo integral","cotacao","M25,50 A25,25,0,1,1,75,50 A25,25,0,1,1,25,50","#dc2626"),
]

CATEGORIES = {
    "informacao": "Sinais de informação",
    "referencia_natural": "Referências naturais",
    "protecao": "Traçados e Proteções",
    "reuniao": "Paradas, rapeis e bivaques",
    "via": "Referências naturais escaláveis",
    "terreno": "Fissuras e cavidades",
    "cotacao": "Cotações",
}

def make_svg(code, name, path_d, color):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
  <rect width="100" height="100" fill="none"/>
  <path d="{path_d}" fill="none" stroke="{color}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''

def generate():
    os.makedirs(SYMBOLS_DIR, exist_ok=True)
    catalog = {"symbols": []}

    for code, name, category, path_d, color in SYMBOLS:
        fname = f"{code.replace('-','_')}.svg"
        fpath = os.path.join(SYMBOLS_DIR, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(make_svg(code, name, path_d, color))

        catalog["symbols"].append({
            "id": code.replace("-","_"),
            "code": code,
            "name": name,
            "category": category,
            "categoryLabel": CATEGORIES.get(category, category),
            "file": f"assets/symbols/{fname}",
            "color": color,
            "placeholder": True,
        })

    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print(f"Generated {len(SYMBOLS)} SVGs → {SYMBOLS_DIR}/")
    print(f"catalog.json → {CATALOG_PATH}")

if __name__ == "__main__":
    generate()
