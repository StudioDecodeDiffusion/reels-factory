"""Story Instagram « nouvelle vidéo » (1080×1920) à partir de l'image d'accroche de la vidéo."""
from __future__ import annotations

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
INK = (27, 31, 59)
POLICES = ["/usr/share/fonts/opentype/inter/Inter-{}.otf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]


def _police(graisse: str, taille: int):
    for p in POLICES:
        try:
            return ImageFont.truetype(p.format(graisse), taille)
        except OSError:
            continue
    return ImageFont.load_default()


def _rgb(h: str):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def creer(image_accroche: Path, titre: str, compte: str, sortie: Path, palette: list[str] | None = None,
          bandeau: str = "NOUVELLE VIDÉO EN LIGNE", chute: str = "Va voir la vidéo sur") -> Path:
    pal = [_rgb(c) for c in (palette or ["#FFD23F", "#3D5AFE", "#FF4F81", "#2EC4B6"])]
    fond, accent, accent2 = pal[0], pal[2], pal[3]
    im = Image.new("RGB", (W, H), fond)
    d = ImageDraw.Draw(im)
    sombre = tuple(max(0, c - 8) for c in fond)
    for y in range(0, H, 60):
        for x in range(0, W, 60):
            if (x // 60 + y // 60) % 2 == 0:
                d.rectangle([x, y, x + 59, y + 59], fill=sombre)

    def sticker(xy, texte, police, bg, fg, rot=0, pad=(34, 18)):
        l, t, r, b = d.textbbox((0, 0), texte, font=police)
        w, h = r - l + 2 * pad[0], b - t + 2 * pad[1]
        s = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0))
        sd = ImageDraw.Draw(s)
        sd.rectangle([12, 12, w + 11, h + 11], fill=INK)
        sd.rectangle([0, 0, w - 1, h - 1], fill=bg, outline=INK, width=7)
        sd.text((pad[0] - l, pad[1] - t), texte, font=police, fill=fg)
        s = s.rotate(rot, expand=True, resample=Image.BICUBIC)
        im.paste(s, xy, s)

    sticker((70, 150), bandeau, _police("Black", 62), accent, (255, 255, 255), 3)
    fr = Image.open(image_accroche).convert("RGB").resize((1080, 1920)).crop((0, 0, 1080, 1500)).resize((640, 889))
    x0, y0 = 220, 330
    d.rectangle([x0 + 16, y0 + 16, x0 + 668, y0 + 921], fill=INK)
    d.rectangle([x0 - 12, y0 - 12, x0 + 652, y0 + 901], fill=INK)
    im.paste(fr, (x0, y0))
    y = 1270
    for k, ligne in enumerate(textwrap.wrap(titre, 22)[:3]):
        sticker((60 + 50 * (k % 2), y), ligne, _police("ExtraBold", 66), (255, 255, 255) if k % 2 == 0 else accent2, INK,
                -2 if k % 2 == 0 else 2)
        y += 125
    d.text((W // 2, 1790), f"{chute} {compte}", font=_police("Bold", 44), fill=INK, anchor="mm")
    sortie.parent.mkdir(parents=True, exist_ok=True)
    im.save(sortie)
    return sortie
