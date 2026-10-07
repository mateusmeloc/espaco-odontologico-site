#!/usr/bin/env python3
"""Converts the photos in fotos-originais/ to optimized WebP in assets/fotos/.

    python3 _build/prepare-fotos.py

Produces two widths per photo — 900px for the grid and 1600px (@2x) for the
lightbox. Only reprocesses what changed. Needs sips and cwebp: sips ships with
macOS, cwebp comes from Homebrew (brew install webp).
"""
import pathlib
import re
import shutil
import subprocess
import sys
import unicodedata

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ORIGINAIS = RAIZ / "fotos-originais"
DESTINO = RAIZ / "assets" / "fotos"

LARGURAS = {"": 900, "@2x": 1600}
QUALIDADE = 76
EXTS = {".jpg", ".jpeg", ".png", ".heic", ".webp", ".JPG", ".JPEG", ".PNG", ".HEIC"}


def slug(nome: str) -> str:
    n = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode().lower()
    return "".join(c if c.isalnum() else "-" for c in n).strip("-").replace("--", "-")


def medir(caminho: pathlib.Path) -> tuple[int, int]:
    saida = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(caminho)],
                           capture_output=True, text=True).stdout
    achados = [int(n) for n in re.findall(r"pixel(?:Width|Height): (\d+)", saida)]
    return (achados[0], achados[1]) if len(achados) == 2 else (0, 0)


def executar(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode:
        raise SystemExit(f"failed: {' '.join(cmd)}\n{r.stderr.decode()[:400]}")


def main() -> int:
    for ferramenta in ("sips", "cwebp"):
        if not shutil.which(ferramenta):
            print(f"ERROR: {ferramenta} not found."
                  f"{' Install it with: brew install webp' if ferramenta == 'cwebp' else ''}",
                  file=sys.stderr)
            return 1

    if not ORIGINAIS.is_dir():
        print(f"ERROR: {ORIGINAIS} does not exist.", file=sys.stderr)
        return 1

    fontes = sorted(f for f in ORIGINAIS.iterdir() if f.suffix in EXTS)
    if not fontes:
        print(f"No images in {ORIGINAIS.name}/. Save the photos there and run again.")
        return 1

    DESTINO.mkdir(parents=True, exist_ok=True)
    tmp = RAIZ / "_build" / ".tmp"
    tmp.mkdir(exist_ok=True)
    total = 0

    for i, origem in enumerate(fontes, 1):
        base = slug(origem.stem) or f"foto-{i:02d}"
        maior = max(medir(origem))
        for sufixo, largura in LARGURAS.items():
            saida = DESTINO / f"{base}{sufixo}.webp"
            if saida.exists() and saida.stat().st_mtime > origem.stat().st_mtime:
                continue
            # never upscale: a small photo would become a blurry, heavy @2x
            alvo = min(largura, maior)
            inter = tmp / f"{base}{sufixo}.png"
            executar(["sips", "-Z", str(alvo), str(origem), "--out", str(inter)])
            executar(["cwebp", "-quiet", "-q", str(QUALIDADE), str(inter), "-o", str(saida)])
            inter.unlink(missing_ok=True)
            total += saida.stat().st_size
        grade = DESTINO / f"{base}.webp"
        print(f"  {base:<28} {grade.stat().st_size // 1024:>4} KB")

    shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n{len(fontes)} photos · {total / 1024:,.0f} KB total in assets/fotos/")
    print("Now run: python3 _build/build.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
