#!/usr/bin/env python3
"""Builds index.html by inlining the files in assets/ as data URIs.

Source of truth: _build/template.html. Never edit index.html directly —
it is generated and overwritten.

    python3 _build/build.py

Each __NAME_B64__ placeholder in the template is replaced by the base64 of the
matching file in assets/ (see MAPA). A missing file or an orphan placeholder
aborts the build instead of producing a broken site.
"""
import base64
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = RAIZ / "_build" / "template.html"
SAIDA = RAIZ / "index.html"
ASSETS = RAIZ / "assets"

# placeholder -> file in assets/
# Only the brand assets are inlined. The clinic photos stay as separate files in
# assets/fotos/ — they load on demand, get cached, and do not bloat the HTML.
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
            print(f"ERROR: {ph} points to {rel}, which does not exist in assets/", file=sys.stderr)
            return 1
        html = html.replace(ph, base64.b64encode(caminho.read_bytes()).decode())
        usados += 1

    orfaos = sorted(set(re.findall(r"__[A-Z0-9_]+_B64__", html)))
    if orfaos:
        print(f"ERROR: placeholders with no matching asset: {', '.join(orfaos)}", file=sys.stderr)
        return 1

    SAIDA.write_text(html, encoding="utf-8")
    kb = len(html.encode()) / 1024
    fotos = sorted((ASSETS / "fotos").glob("*.webp")) if (ASSETS / "fotos").is_dir() else []
    grade = [f for f in fotos if not f.stem.endswith("@2x")]
    print(f"index.html built: {kb:,.1f} KB · {usados} assets inlined"
          f" · {len(grade)} photos in assets/fotos/")
    if kb > 250:
        print(f"WARNING: {kb:,.0f} KB of HTML is heavy on 4G — photos should be files, not base64.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
