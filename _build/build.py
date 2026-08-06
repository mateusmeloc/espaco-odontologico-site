#!/usr/bin/env python3
"""Monta o index.html embutindo os assets de assets/ como data URI.

Fonte de verdade: _build/template.html. Nunca edite index.html direto —
ele é gerado e sobrescrito.

    python3 _build/build.py

Cada placeholder __NOME_B64__ no template é trocado pelo base64 do arquivo
correspondente em assets/ (ver MAPA). Falta de arquivo ou placeholder órfão
aborta o build em vez de gerar um site quebrado.
"""
import base64
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = RAIZ / "_build" / "template.html"
SAIDA = RAIZ / "index.html"
ASSETS = RAIZ / "assets"

# placeholder -> arquivo em assets/
# Só a marca é embutida. As fotos da clínica ficam como arquivos soltos em
# assets/fotos/ — carregam sob demanda, ficam em cache e não engordam o HTML.
MAPA = {
    "__LOGO_B64__": "logo.webp",
    "__FAV_B64__": "favicon.png",
}


def main() -> int:
    html = TEMPLATE.read_text(encoding="utf-8")

    usados = 0
    for ph, rel in MAPA.items():
        if ph not in html:
            continue
        caminho = ASSETS / rel
        if not caminho.is_file():
            print(f"ERRO: {ph} usa {rel}, que não existe em assets/", file=sys.stderr)
            return 1
        html = html.replace(ph, base64.b64encode(caminho.read_bytes()).decode())
        usados += 1

    orfaos = sorted(set(re.findall(r"__[A-Z0-9_]+_B64__", html)))
    if orfaos:
        print(f"ERRO: placeholders sem asset correspondente: {', '.join(orfaos)}", file=sys.stderr)
        return 1

    SAIDA.write_text(html, encoding="utf-8")
    kb = len(html.encode()) / 1024
    fotos = sorted((ASSETS / "fotos").glob("*.webp")) if (ASSETS / "fotos").is_dir() else []
    grade = [f for f in fotos if not f.stem.endswith("@2x")]
    print(f"index.html gerado: {kb:,.1f} KB · {usados} assets embutidos"
          f" · {len(grade)} fotos em assets/fotos/")
    if kb > 250:
        print(f"AVISO: {kb:,.0f} KB de HTML é pesado para 4G — fotos deveriam ser arquivos, não base64.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
