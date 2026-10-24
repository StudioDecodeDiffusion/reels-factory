"""Miniatures et stories d'annonce, avec un style DIFFÉRENT par vidéo (règle de variété du propriétaire).

Styles : pancarte · amende · notif · parchemin · reaction · une (journal) · neon
Chaque style produit une image 1080×1920 ; `kind="couverture"` (titre seul) ou
`kind="story"` (accroche d'annonce + horaire).
"""
from __future__ import annotations

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from .story import _police

W, H = 1080, 1920
INK = (20, 19, 28)


def _sticker(im, d, xy, texte, police, bg, fg, rot=0, pad=(30, 16), ombre=True, bord=7):
    l, t, r, b = d.textbbox((0, 0), texte, font=police)
    w, h = r - l + 2 * pad[0], b - t + 2 * pad[1]
    s = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0))
    sd = ImageDraw.Draw(s)
    if ombre:
        sd.rectangle([12, 12, w + 11, h + 11], fill=INK)
    sd.rectangle([0, 0, w - 1, h - 1], fill=bg, outline=INK, width=bord)
    sd.text((pad[0] - l, pad[1] - t), texte, font=police, fill=fg)
    s = s.rotate(rot, expand=True, resample=Image.BICUBIC)
    x = xy[0] if xy[0] >= 0 else (W - s.size[0]) // 2
    im.paste(s, (x, xy[1]), s)
    return s.size


def _lignes(t, n):
    return textwrap.wrap(t, n, break_long_words=False)


def _perso(image, box_y, im, cadre=True, h=300):
    fr = Image.open(image).convert("RGB").resize((W, H)).crop((0, 1000, W, 1340)).resize((900, int(900 * 340 / W)))
    d = ImageDraw.Draw(im)
    if cadre:
        d.rectangle([84, box_y - 6, 996, box_y + fr.size[1] + 6], fill=INK)
    im.paste(fr, (90, box_y))


def creer(style: str, kind: str, titre: str, accroche: str, quand: str, image: Path, sortie: Path) -> Path:
    im = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(im)
    if style == "pancarte":
        im.paste((255, 233, 199), [0, 0, W, H])
        for y in range(0, H, 40):
            d.line([(0, y), (W, y)], fill=(245, 220, 185), width=2)
        d.rectangle([524, 1000, 556, 1560], fill=(139, 90, 43), outline=INK, width=5)
        d.rectangle([110, 330, 970, 1010], fill=(255, 248, 225), outline=INK, width=12)
        d.rectangle([122, 1012, 982, 1024], fill=INK)
        lig = _lignes(titre if kind == "couverture" else accroche, 13)[:4]
        y = 680 - len(lig) * 60
        for li in lig:
            d.text((W // 2, y), li.upper(), font=_police("Black", 72), fill=INK, anchor="mm")
            y += 115
        _sticker(im, d, (-1, 150), "« IDÉES REÇUES »" if kind == "couverture" else quand, _police("Black", 58), (255, 107, 53), (255, 255, 255), -3)
        _perso(image, 1600, im)
    elif style == "amende":
        im.paste((236, 236, 228), [0, 0, W, H])
        d.rectangle([90, 220, 990, 1450], fill=(255, 255, 250), outline=INK, width=6)
        for x in range(90, 990, 30):
            d.ellipse([x, 205, x + 18, 223], fill=(236, 236, 228))
        d.text((W // 2, 300), "AVIS DE PAIEMENT", font=_police("Black", 64), fill=(192, 57, 43), anchor="mm")
        d.text((W // 2, 370), "N° 17-10-2026 · MANIFESTATION", font=_police("Bold", 34), fill=INK, anchor="mm")
        d.line([(130, 420), (950, 420)], fill=INK, width=4)
        d.text((150, 470), "MONTANT MAXIMUM", font=_police("Bold", 40), fill=INK)
        d.text((W // 2, 640), "10 000 €", font=_police("Black", 190), fill=INK, anchor="mm")
        lig = _lignes(titre if kind == "couverture" else accroche, 26)[:3]
        y = 860
        for li in lig:
            d.text((W // 2, y), li, font=_police("ExtraBold", 60), fill=INK, anchor="mm")
            y += 80
        tampon = Image.new("RGBA", (620, 170), (0, 0, 0, 0))
        td = ImageDraw.Draw(tampon)
        td.rectangle([6, 6, 614, 164], outline=(192, 57, 43), width=10)
        td.text((310, 85), "PROJET DE LOI" if kind == "couverture" else quand.upper(), font=_police("Black", 64), fill=(192, 57, 43), anchor="mm")
        tampon = tampon.rotate(-12, expand=True)
        im.paste(tampon, (300, 1150), tampon)
        d.text((W // 2, 1560), "Loi « casseurs-payeurs » : on décode", font=_police("ExtraBold", 54), fill=INK, anchor="mm")
    elif style == "notif":
        for y in range(H):
            c = int(13 + 30 * y / H)
            d.line([(0, y), (W, y)], fill=(c, 8, c + 25))
        d.text((W // 2, 300), "14:58" if kind == "story" else "05/11", font=_police("Bold", 200), fill=(255, 255, 255), anchor="mm")
        d.text((W // 2, 430), "jeudi 5 novembre", font=_police("Bold", 50), fill=(200, 200, 220), anchor="mm")
        d.rounded_rectangle([70, 560, 1010, 1060], radius=40, fill=(40, 38, 56), outline=(90, 90, 110), width=4)
        d.rounded_rectangle([110, 600, 190, 680], radius=18, fill=(229, 19, 58))
        d.text((150, 640), "A", font=_police("Black", 56), fill=(255, 255, 255), anchor="mm")
        d.text((220, 615), "Numéro masqué", font=_police("Bold", 42), fill=(255, 255, 255))
        lig = _lignes(titre if kind == "couverture" else accroche, 26)[:4]
        y = 720
        for li in lig:
            d.text((110, y), li, font=_police("Bold", 52), fill=(255, 255, 255))
            y += 68
        d.text((960, 1000), "-A", font=_police("Black", 70), fill=(229, 19, 58), anchor="rm")
        if kind == "story":
            _sticker(im, d, (-1, 1180), quand, _police("Black", 66), (0, 229, 255), INK, 2)
        d.text((W // 2, 1500), "Qui t'écrit ? On enquête.", font=_police("ExtraBold", 60), fill=(0, 229, 255), anchor="mm")
    elif style == "parchemin":
        im.paste((16, 10, 6), [0, 0, W, H])
        lueur = Image.new("RGB", (W, H), (0, 0, 0))
        ImageDraw.Draw(lueur).ellipse([140, 300, 940, 1200], fill=(255, 170, 70))
        im = Image.blend(im, lueur.filter(ImageFilter.GaussianBlur(160)), 0.45)
        d = ImageDraw.Draw(im)
        d.rectangle([120, 380, 960, 1180], fill=(243, 227, 195), outline=(90, 59, 30), width=12)
        d.text((W // 2, 300), "IL ÉTAIT UNE FOIS…", font=_police("Black", 60), fill=(255, 217, 138), anchor="mm")
        lig = _lignes(titre if kind == "couverture" else accroche, 18)[:5]
        y = 520
        for li in lig:
            d.text((W // 2, y), li, font=_police("ExtraBold", 72), fill=(42, 26, 12), anchor="mm")
            y += 100
        if kind == "story":
            d.text((W // 2, 1100), quand, font=_police("Black", 54), fill=(150, 60, 20), anchor="mm")
        _perso(image, 1350, im, cadre=False)
    elif style == "flash":  # annonce façon alerte info : bandeau rouge, heure géante, titre
        im.paste((12, 12, 16), [0, 0, W, H])
        vign = Image.open(image).convert("RGB").resize((W, H)).resize((380, 676))
        d.rectangle([W // 2 - 196, 1146, W // 2 + 196, 1146 + 688], fill=(229, 19, 58))
        im.paste(vign, (W // 2 - 190, 1152))
        d.rectangle([0, 210, W, 330], fill=(229, 19, 58))
        d.text((W // 2, 270), "BIENTÔT SUR DÉCODÉ" if kind == "story" else "DÉCODÉ", font=_police("Black", 70), fill=(255, 255, 255), anchor="mm")
        if kind == "story":
            d.text((W // 2, 520), quand, font=_police("Black", 130), fill=(255, 214, 0), anchor="mm")
        lig = _lignes(titre if kind == "couverture" else accroche, 20)[:4]
        y = 720
        for li in lig:
            d.text((W // 2, y), li, font=_police("Black", 78), fill=(255, 255, 255), anchor="mm")
            y += 100
        if kind == "story":
            d.text((W // 2, 1080), "Active les notifs", font=_police("ExtraBold", 52), fill=(255, 214, 0), anchor="mm")
    else:  # reaction / une / neon : bandeau simple coloré
        im.paste((22, 5, 31), [0, 0, W, H])
        lig = _lignes(titre if kind == "couverture" else accroche, 14)[:4]
        y = 420
        for k, li in enumerate(lig):
            _sticker(im, d, (-1, y), li, _police("Black", 100), (255, 138, 31) if k % 2 == 0 else (142, 92, 255), INK, 2 if k % 2 == 0 else -2)
            y += 170
        if kind == "story":
            _sticker(im, d, (-1, 160), quand, _police("Black", 60), (255, 255, 255), INK, -3)
        _perso(image, 1250, im)
    if kind != "couverture":
        d.text((W // 2, 1860), "@decodeactu", font=_police("Bold", 44), fill=(255, 255, 255) if style in ("notif", "parchemin", "reaction", "flash") else INK, anchor="mm")
    sortie.parent.mkdir(parents=True, exist_ok=True)
    im.save(sortie)
    return sortie


def couverture_choc(image: Path, titre: str, mots_choc: list[str] | None, sortie: Path, accent=(227, 36, 43),
                    surtitre: str = "") -> Path:
    """Miniature « choc » : image de la vidéo en plein cadre assombrie, titre critique énorme (zone visible dans la
    grille du profil, centre 3:4), mots choc en rouge."""
    import re as _re
    fond = Image.open(image).convert("RGB").resize((W, H))
    fond = fond.filter(ImageFilter.GaussianBlur(9))
    noir = Image.new("RGB", (W, H), (8, 8, 12))
    im = Image.blend(fond, noir, 0.62)
    # dégradé sombre derrière le titre
    grad = Image.new("L", (1, H))
    for y in range(H):
        grad.putpixel((0, y), int(230 * max(0, 1 - abs(y - 820) / 700)))
    im.paste(noir, (0, 0), grad.resize((W, H)))
    d = ImageDraw.Draw(im)
    net = lambda m: _re.sub(r"[^\w]", "", m.lower())
    choc = {net(m) for m in (mots_choc or []) for m in m.split()}
    taille = 132 if len(titre) <= 28 else 112 if len(titre) <= 45 else 94
    pol = _police("Black", taille)
    lignes, cour = [], ""
    for mot in titre.split():
        essai = (cour + " " + mot).strip()
        if d.textlength(essai.upper(), font=pol) > W - 140 and cour:
            lignes.append(cour)
            cour = mot
        else:
            cour = essai
    lignes.append(cour)
    lignes = lignes[:5]
    h_ligne = int(taille * 1.08)
    y = 820 - len(lignes) * h_ligne // 2
    if surtitre:
        pst = _police("Black", 46)
        lw = d.textlength(surtitre.upper(), font=pst)
        d.rectangle([(W - lw) / 2 - 20, y - 110, (W + lw) / 2 + 20, y - 40], fill=accent)
        d.text((W // 2, y - 75), surtitre.upper(), font=pst, fill=(255, 255, 255), anchor="mm")
    for li in lignes:
        mots = li.split()
        larg = d.textlength(li.upper(), font=pol)
        x = (W - larg) / 2
        for k, m in enumerate(mots):
            t = m.upper() + (" " if k < len(mots) - 1 else "")
            coul = accent if net(m) in choc else (255, 255, 255)
            d.text((x + 5, y + 6), t, font=pol, fill=(0, 0, 0))
            d.text((x, y), t, font=pol, fill=coul)
            x += d.textlength(t, font=pol)
        y += h_ligne
    sortie.parent.mkdir(parents=True, exist_ok=True)
    im.save(sortie)
    return sortie
