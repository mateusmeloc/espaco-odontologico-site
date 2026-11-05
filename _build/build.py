#!/usr/bin/env python3
"""Builds index.html by inlining the files in assets/ as data URIs.

Source of truth: _build/template.html. Never edit index.html directly —
it is generated and overwritten.

    python3 _build/build.py

Each __NAME_B64__ placeholder in the template is replaced by the base64 of the
matching file in assets/ (see MAPA). A missing file or an orphan placeholder
aborts the build instead of producing a broken site.

It also checks the favicon links: each one must point to a square PNG/ICO file
that exists, never to inline base64 — otherwise Google stops showing the icon
in search results, and nothing else would notice.
"""
import base64
import pathlib
import re
import struct
import sys
from typing import List, Optional, Tuple

RAIZ = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = RAIZ / "_build" / "template.html"
SAIDA = RAIZ / "index.html"
ASSETS = RAIZ / "assets"

# placeholder -> file in assets/
# Only the logo is inlined. The clinic photos stay as separate files in
# assets/fotos/ — they load on demand, get cached, and do not bloat the HTML.
# The favicon is NOT inlined either: Google only shows it in search results when
# it is a file it can download (see _build/make-icons.py).
MAPA = {
    "__LOGO_B64__": "logo.webp",
}

REL_ICONE = re.compile(r'\brel="(?:icon|shortcut icon|apple-touch-icon)"')
HREF = re.compile(r'\bhref="([^"]*)"')


def lados(caminho: pathlib.Path) -> List[Tuple[int, int]]:
    """Width x height of a PNG, or of every image inside an ICO. Stdlib only."""
    dados = caminho.read_bytes()
    if dados[:8] == b"\x89PNG\r\n\x1a\n":
        return [struct.unpack(">II", dados[16:24])]
    if dados[:4] == b"\x00\x00\x01\x00":
        total = struct.unpack("<H", dados[4:6])[0]
        # In an ICO directory entry, 0 means 256 px.
        return [(dados[6 + 16 * i] or 256, dados[7 + 16 * i] or 256) for i in range(total)]
    return []


def conferir_icones(html: str) -> Optional[str]:
    """Returns what is wrong with the favicon links, or None when all is fine."""
    links = [tag for tag in re.findall(r"<link\b[^>]*>", html) if REL_ICONE.search(tag)]
    if not links:
        return 'no <link rel="icon"> in the template'
    for tag in links:
        achado = HREF.search(tag)
        href = achado.group(1) if achado else ""
        if not href or href.startswith("data:") or "://" in href:
            return f"icon must be a relative path to a file in this repo, not inline: {tag[:90]}"
        caminho = RAIZ / href.split("?")[0].lstrip("/")
        if not caminho.is_file():
            return f"icon {href} does not exist (run: uv run _build/make-icons.py)"
        medidas = lados(caminho)
        if not medidas or any(largura != altura for largura, altura in medidas):
            return f"icon {href} is not a square PNG/ICO: {medidas or 'unknown format'}"
    return None


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

    problema = conferir_icones(html)
    if problema:
        print(f"ERROR: {problema}", file=sys.stderr)
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
