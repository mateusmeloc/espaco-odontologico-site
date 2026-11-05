# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow==13.0.0"]  # pinned: another version may write different bytes
# ///
"""Generates the site icons (favicon) from assets/logo-original.png.

    uv run _build/make-icons.py

Why files and not base64 like the logo: Google only shows a favicon next to the
site in search results when the icon is a SQUARE image that Googlebot-Image can
download from a URL. A data URI has no file to download, so the icons live as
real files at the site root, where crawlers also probe /favicon.ico by default.

Outputs (site root):
    favicon.ico           16, 32 and 48 px in one file
    icon-192.png          192 px, the one Google prefers (larger than 48 px)
    apple-touch-icon.png  180 px, iPhone home screen

The flower is cut from the logo automatically, at any logo size: it starts at
the first column with ink and ends at the next fully transparent column (the
gap before the text). If there is no such gap, or the cut is not roughly
square (it took text along), the script aborts instead of writing a broken
icon.
"""

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
LOGO = ROOT / "assets" / "logo-original.png"

ALPHA_EMPTY = 8  # alpha below this counts as transparent (antialiasing noise)
MAX_ASPECT = 1.25  # the flower is roughly square; a wider cut took text along
BACKGROUND = (255, 255, 255, 255)  # white: the navy flower stays visible in dark mode


class IconError(Exception):
    """The logo does not look like what this script expects."""


def cut_flower(logo: Image.Image) -> Image.Image:
    alpha = logo.getchannel("A")
    width, height = logo.size

    def empty(x: int) -> bool:
        return alpha.crop((x, 0, x + 1, height)).getextrema()[1] < ALPHA_EMPTY

    start = next((x for x in range(width) if not empty(x)), None)
    if start is None:
        raise IconError("the logo is fully transparent")
    end = next((x for x in range(start, width) if empty(x)), None)
    if end is None:
        raise IconError("no transparent column between the flower and the text")

    mask = alpha.crop((0, 0, end, height)).point(lambda v: 255 if v >= ALPHA_EMPTY else 0)
    flower = logo.crop(mask.getbbox())
    if not 1 / MAX_ASPECT <= flower.width / flower.height <= MAX_ASPECT:
        raise IconError(
            f"the cut is {flower.width}x{flower.height} px, not square:"
            " it probably took part of the text along"
        )
    return flower


def square_icon(flower: Image.Image, side: int, margin: float) -> Image.Image:
    canvas = Image.new("RGBA", (side, side), BACKGROUND)
    inner = round(side * (1 - 2 * margin))
    art = flower.copy()
    art.thumbnail((inner, inner), Image.Resampling.LANCZOS)
    canvas.alpha_composite(art, ((side - art.width) // 2, (side - art.height) // 2))
    return canvas.convert("RGB")


def main() -> int:
    try:
        if not LOGO.is_file():
            raise IconError(f"{LOGO.relative_to(ROOT)} does not exist")
        with Image.open(LOGO) as logo:
            flower = cut_flower(logo.convert("RGBA"))
    except IconError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    # Tiny sizes get a thinner margin so the flower is not a dot in the tab.
    ico = {side: square_icon(flower, side, 0.04) for side in (16, 32, 48)}
    ico[48].save(
        ROOT / "favicon.ico",
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48)],
        append_images=[ico[16], ico[32]],
    )
    square_icon(flower, 192, 0.08).save(ROOT / "icon-192.png", optimize=True)
    # iOS rounds the corners of the home screen icon: keep the petals inside.
    square_icon(flower, 180, 0.12).save(ROOT / "apple-touch-icon.png", optimize=True)

    print(f"flower cut at {flower.size[0]}x{flower.size[1]} px from {LOGO.name}")
    print("icons written: favicon.ico (16/32/48), icon-192.png, apple-touch-icon.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
