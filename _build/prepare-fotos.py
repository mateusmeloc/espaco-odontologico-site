#!/usr/bin/env python3
"""Converte as fotos de fotos-originais/ para WebP otimizado em assets/fotos/.

    python3 _build/prepare-fotos.py

Gera duas larguras por foto — 900px para a grade e 1600px para o lightbox —
mais uma miniatura base64 usada como placeholder enquanto a imagem carrega.
Só reprocessa o que mudou. Depende de sips e cwebp, ambos já no macOS
(cwebp vem do Homebrew: brew install webp).
"""
import pathlib
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


def executar(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode:
        raise SystemExit(f"falhou: {' '.join(cmd)}\n{r.stderr.decode()[:400]}")


def main() -> int:
    for ferramenta in ("sips", "cwebp"):
        if not shutil.which(ferramenta):
            print(f"ERRO: {ferramenta} não encontrado."
                  f"{' Instale com: brew install webp' if ferramenta == 'cwebp' else ''}",
                  file=sys.stderr)
            return 1

    if not ORIGINAIS.is_dir():
        print(f"ERRO: {ORIGINAIS} não existe.", file=sys.stderr)
        return 1

    fontes = sorted(f for f in ORIGINAIS.iterdir() if f.suffix in EXTS)
    if not fontes:
        print(f"Nenhuma imagem em {ORIGINAIS.name}/. Salve as fotos lá e rode de novo.")
        return 1

    DESTINO.mkdir(parents=True, exist_ok=True)
    tmp = RAIZ / "_build" / ".tmp"
    tmp.mkdir(exist_ok=True)
    total = 0

    for i, origem in enumerate(fontes, 1):
        base = slug(origem.stem) or f"foto-{i:02d}"
        for sufixo, largura in LARGURAS.items():
            saida = DESTINO / f"{base}{sufixo}.webp"
            if saida.exists() and saida.stat().st_mtime > origem.stat().st_mtime:
                continue
            inter = tmp / f"{base}{sufixo}.png"
            executar(["sips", "-Z", str(largura), str(origem), "--out", str(inter)])
            executar(["cwebp", "-quiet", "-q", str(QUALIDADE), str(inter), "-o", str(saida)])
            inter.unlink(missing_ok=True)
            total += saida.stat().st_size
        grade = DESTINO / f"{base}.webp"
        print(f"  {base:<28} {grade.stat().st_size // 1024:>4} KB")

    shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n{len(fontes)} fotos · {total / 1024:,.0f} KB no total em assets/fotos/")
    print("Agora rode: python3 _build/build.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
