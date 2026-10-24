"""Validation de la spécification vidéo et rendu Remotion."""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

from .config import VIDEO

HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
FONTS = {"Space Grotesk", "Inter", "JetBrains Mono", "Rubik", "Silkscreen"}
MODES = {"gravity", "orbit", "bounce", "swarm", "pendulum_wave"}
EXPRESSIONS = {"neutre", "content", "rire", "choc", "pense", "clin", "triste", "colere", "peur", "sarcasme", "degout"}  # les 3 dernières : persos cartoon (repli neutre en pixel)
TENUES = {"classique", "economie", "qhse", "science", "detective", "sport", "hiver", "fete", "musique", "ecologie",
          "gilet_jaune", "ouvrier", "infirmier", "milliardaire", "roi", "manifestant", "etudiant", "robe"}  # nouvelles : persos cartoon
ANIMS = {"bounce", "float", "shake", "spin", "grow", "rain", "orbit"}
MASCOTTE = {"neutre", "content", "choc", "pense", "clin", "aucune"}
SPRITES = {"pompe", "goutte", "piece", "billet", "caddie", "maison", "usine", "voiture", "eclair", "flamme",
           "thermometre", "fleche_haut", "fleche_bas", "loupe", "document", "casque", "danger", "extincteur",
           "horloge", "globe", "ampoule", "check", "croix", "calendrier", "graphique", "feuille"}

REQUIRED = {
    "hook": ["title"], "kinetic": ["lines"], "counter": ["to", "label"],
    "bars": ["title", "items"], "timeline": ["events"], "dots": ["total", "highlighted", "label"],
    "compare": ["left", "right"], "particles": ["mode", "caption"], "outro": ["text", "cta"],
    "quiz": ["question", "options", "bonne"], "bigstat": ["value", "label"], "checklist": ["items"],
    "photo": ["src", "credit"], "ed_titre": ["titre"], "ed_chiffre": ["valeur", "legende"], "ed_citation": ["texte", "auteur"],
    "ed_photo": ["src", "credit"], "ed_liste": ["points"], "ed_versus": ["gauche", "droite"], "ed_allocution": ["texte", "auteur"], "pd_objet": [], "pd_flux": ["de", "vers"], "pd_chiffre": ["valeur", "legende"], "pd_versus": ["gauche", "droite"], "pd_jauge": ["valeur", "legende"], "pd_tampon": ["tampon"], "pendant": ["haut", "bas"], "pancartes": ["items"], "sms": ["texte"], "debat": ["pour", "contre"], "reaction": ["paliers"], "conte": ["texte"],
}


def validate_spec(spec: dict, allowed: list[str], voix_obligatoire: bool = False) -> list[str]:
    """Renvoie la liste des erreurs (vide = OK). Corrige au passage ce qui est corrigeable."""
    errs: list[str] = []
    th = spec.get("theme") or {}
    for k in ("fond", "texte", "accent", "accent2"):
        if not HEX.match(str(th.get(k, ""))):
            errs.append(f"theme.{k} doit être une couleur #RRGGBB")
    for k in ("police_titre", "police_texte"):
        if th.get(k) not in FONTS:
            th[k] = "Space Grotesk" if k == "police_titre" else "Inter"
    th.setdefault("bandeau", None)
    th.setdefault("style", "pixel")
    if "palette" in th:
        th["palette"] = [c for c in th["palette"] if HEX.match(str(c))][:8]
        if len(th["palette"]) < 3:
            errs.append("theme.palette doit contenir au moins 3 couleurs #RRGGBB")
    th["grille"] = bool(th.get("grille", False))
    for k, ok in (("mise_en_page", {"duo", "jt", "chat", "quiz", "plein_ecran"}), ("transition", {"pixels", "iris", "volet", "bandes", "glitch"}),
                  ("camera", {"zoom", "pan", "secousse", "respire"})):
        if th.get(k) is not None and th[k] not in ok:
            errs.append(f"theme.{k} doit être parmi {sorted(ok)}")

    scenes = spec.get("scenes") or []
    if not 3 <= len(scenes) <= 18:
        errs.append("il faut entre 3 et 18 scènes")
    for i, s in enumerate(scenes):
        t = s.get("type")
        if t not in REQUIRED:
            errs.append(f"scène {i} : type inconnu « {t} »")
            continue
        dia = s.get("dialogue")
        if dia is not None:
            if not isinstance(dia, list) or not dia:
                errs.append(f"scène {i} : « dialogue » doit être une liste de répliques")
                dia = []
            for j, r in enumerate(dia):
                if r.get("qui") not in ("narrateur", "mascotte"):
                    errs.append(f"scène {i} réplique {j} : « qui » doit valoir narrateur ou mascotte")
                if not str(r.get("texte", "")).strip():
                    errs.append(f"scène {i} réplique {j} : texte vide")
                if r.get("expression") and r["expression"] not in EXPRESSIONS:
                    errs.append(f"scène {i} réplique {j} : expression parmi {sorted(EXPRESSIONS)}")
        if voix_obligatoire and not dia and not str(s.get("voix", "")).strip():
            errs.append(f"scène {i} ({t}) : il faut un « dialogue » (ou une « voix ») pour la voix off")
        for cle in ("tenue_narrateur", "tenue_mascotte"):
            if s.get(cle) and s[cle] not in TENUES:
                errs.append(f"scène {i} : {cle} parmi {sorted(TENUES)}")
        if t not in allowed:
            errs.append(f"scène {i} : type « {t} » non autorisé pour ce compte")
        for f in REQUIRED[t]:
            if f not in s:
                errs.append(f"scène {i} ({t}) : champ « {f} » manquant")
        try:
            s["duration"] = float(s.get("duration", 3))
        except (TypeError, ValueError):
            errs.append(f"scène {i} : duration doit être un nombre")
            continue
        paroles = [str(r.get("texte", "")) for r in (s.get("dialogue") or [])] or ([str(s["voix"])] if s.get("voix") else [])
        if paroles:
            # ≈ 2,5 mots par seconde à l'oral + 0,3 s entre répliques : la scène dure au moins le temps du dialogue
            s["duration"] = max(s["duration"], sum(len(p.split()) / 2.5 + 0.3 for p in paroles) + 0.6)
        s["duration"] = round(min(max(s["duration"], 2.5), 16.0), 2)
        for f in ("to", "from", "total", "highlighted", "decimals", "count"):
            if f in s:
                try:
                    s[f] = float(s[f]) if f in ("to", "from") else int(float(s[f]))
                except (TypeError, ValueError):
                    errs.append(f"scène {i} : {f} doit être un nombre")
        if t == "bars":
            for it in s.get("items", []):
                try:
                    it["value"] = float(it["value"])
                except (KeyError, TypeError, ValueError):
                    errs.append(f"scène {i} : chaque item de bars doit avoir une value numérique")
        if s.get("sprite") and s["sprite"] not in SPRITES:
            errs.append(f"scène {i} : sprite « {s['sprite']} » inconnu (choisir parmi : {', '.join(sorted(SPRITES))})")
        if s.get("sprite_anim") and s["sprite_anim"] not in ANIMS:
            errs.append(f"scène {i} : sprite_anim doit être parmi {sorted(ANIMS)}")
        if s.get("mascotte") and s["mascotte"] not in MASCOTTE:
            errs.append(f"scène {i} : mascotte doit être parmi {sorted(MASCOTTE)}")
        if s.get("fond") and not HEX.match(str(s["fond"])):
            errs.append(f"scène {i} : fond doit être une couleur #RRGGBB")
        if t == "particles" and s.get("mode") not in MODES:
            errs.append(f"scène {i} : mode doit être parmi {sorted(MODES)}")
    total = sum(s.get("duration", 0) for s in scenes if isinstance(s.get("duration"), float))
    if total > 110:
        errs.append(f"durée totale {total:.0f}s trop longue (max 110)")
    tn = th.get("tenues") or {}
    for k, v in tn.items():
        if k not in ("narrateur", "mascotte") or v not in TENUES:
            errs.append(f"theme.tenues : {k} → {v} invalide (tenues : {sorted(TENUES)})")
    return errs


def _browser_args() -> list[str]:
    """Navigateur pour le rendu. Dans les sessions Claude, le téléchargement habituel de Remotion est
    bloqué : on utilise le Chromium livré par le paquet npm @sparticuz/chromium."""
    exe = os.getenv("REMOTION_BROWSER")
    if not exe and os.getenv("GITHUB_ACTIONS"):
        return []  # sur GitHub, Remotion utilise son propre navigateur (npx remotion browser ensure)
    if not exe and (VIDEO / "node_modules" / "@sparticuz" / "chromium").exists():
        r = subprocess.run(["node", "-e", "require('@sparticuz/chromium').default.executablePath()"
                            ".then(p=>console.log(p))"], cwd=VIDEO, capture_output=True, text=True)
        exe = r.stdout.strip().splitlines()[-1] if r.returncode == 0 and r.stdout.strip() else None
    return [f"--browser-executable={exe}", "--chrome-mode=headless-shell"] if exe else []


def _credit_commons(sc: dict) -> None:
    """Image de Wikimedia Commons : auteur et licence lus automatiquement (attribution obligatoire)."""
    import re as _re
    import urllib.parse
    import urllib.request
    m = _re.search(r"Special:FilePath/([^?]+)", sc.get("src", ""))
    if not m:
        return
    nom = urllib.parse.unquote(m.group(1))
    url = ("https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=extmetadata&format=json&titles="
           + urllib.parse.quote("File:" + nom))
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "DecodeStudio/1.0 (studiodecodediffusion@gmail.com)"})
        data = json.loads(urllib.request.urlopen(req, timeout=30).read())
        meta = next(iter(data["query"]["pages"].values()))["imageinfo"][0]["extmetadata"]
        auteur = _re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value", "")).strip()[:60]
        lic = meta.get("LicenseShortName", {}).get("value", "")
        sc["credit"] = f"{auteur} · {lic} · Wikimedia Commons".strip(" ·")
    except Exception as e:
        print(f"crédit Commons non lu ({e}) : crédit de la spec conservé")


def _photos(spec: dict) -> None:
    """Scènes « photo » : télécharge l'image (licence libre : Wikimedia Commons, sites publics…) dans video/public/photos/."""
    import hashlib
    import urllib.request
    for sc in spec.get("scenes", []):
        if sc.get("type") == "pendant" and str(sc.get("src", "")).startswith("http"):
            tmp = {"type": "photo", "src": sc["src"], "credit": sc.get("credit", "")}
            _photos({"scenes": [tmp]})
            sc["src"], sc["credit"] = tmp["src"], tmp["credit"]
            continue
        src = str(sc.get("src", ""))
        if sc.get("type") in ("photo", "ed_photo") and src.startswith("http"):
            _credit_commons(sc)
            nom = hashlib.sha1(src.encode()).hexdigest()[:16] + (Path(src.split("?")[0]).suffix or ".jpg")
            dest = VIDEO / "public" / "photos" / nom
            dest.parent.mkdir(parents=True, exist_ok=True)
            if not dest.exists():
                try:
                    req = urllib.request.Request(src, headers={"User-Agent": "DecodeStudio/1.0 (studiodecodediffusion@gmail.com)"})
                    dest.write_bytes(urllib.request.urlopen(req, timeout=60).read())
                except Exception as e:
                    print(f"photo non téléchargée ({e}) : remplacée par un fond")
                    sc["src"] = ""
                    continue
            sc["src"] = f"photos/{nom}"


PIXEL_STYLE = ("detailed realistic pixel art, 64-bit retro game sprite, crisp pixels, rich shading, warm lighting, "
               "single object centered, isolated on a plain pure black background, no text, no watermark")


def _generer_pixel(prompt: str, graine: int) -> str:
    """Objet pixel art généré (FLUX via Pollinations, gratuit et sans compte), puis pixelisé et détouré.
    Retourne le chemin relatif dans video/public, ou "" si la génération échoue (repli graphique dans le rendu)."""
    import hashlib
    import io
    import urllib.parse
    import urllib.request
    from PIL import Image
    if os.getenv("PIXELS_HORS_LIGNE"):  # session locale : le générateur n'est joignable que depuis GitHub
        return ""
    nom = "px_" + hashlib.sha1(f"{prompt}|{graine}".encode()).hexdigest()[:16] + ".png"
    dest = VIDEO / "public" / "photos" / nom
    if dest.exists():
        return f"photos/{nom}"
    url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(f"{prompt}, {PIXEL_STYLE}")
           + f"?width=768&height=768&nologo=true&model=flux&seed={graine}")
    import time
    im = None
    for essai in range(4):  # l'offre gratuite limite le débit : on patiente et on réessaie
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "DecodeStudio/1.0"})
            im = Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=150).read())).convert("RGBA")
            break
        except Exception as e:
            print(f"génération pixel, essai {essai + 1} : {e}")
            time.sleep(20 * (essai + 1))
    if im is None:
        return ""
    time.sleep(8)
    petit = im.resize((128, 128), Image.LANCZOS)
    q = petit.convert("RGB").quantize(colors=40, method=Image.Quantize.MEDIANCUT).convert("RGBA")
    px = q.load()
    # détourage : remplissage depuis les bords sur les couleurs proches du fond
    coins = [px[0, 0], px[127, 0], px[0, 127], px[127, 127]]
    fond = tuple(sum(c[k] for c in coins) // 4 for k in range(3))
    proche = lambda c: sum(abs(c[k] - fond[k]) for k in range(3)) < 70
    pile = [(x, y) for x in range(128) for y in (0, 127)] + [(x, y) for y in range(128) for x in (0, 127)]
    vu = set()
    while pile:
        x, y = pile.pop()
        if (x, y) in vu or not (0 <= x < 128 and 0 <= y < 128):
            continue
        vu.add((x, y))
        if proche(px[x, y]):
            px[x, y] = (0, 0, 0, 0)
            pile += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    dest.parent.mkdir(parents=True, exist_ok=True)
    q.resize((768, 768), Image.NEAREST).save(dest)
    return f"photos/{nom}"


def _pixels(spec: dict) -> None:
    for i, sc in enumerate(spec.get("scenes", [])):
        if not str(sc.get("type", "")).startswith("pd_"):
            continue
        for cible in [sc] + [sc.get(k) for k in ("de", "vers", "gauche", "droite") if isinstance(sc.get(k), dict)]:
            if cible.get("prompt") and not cible.get("src"):
                cible["src"] = _generer_pixel(cible["prompt"], 1000 + i)


def render(spec: dict, out_mp4: Path) -> Path:
    spec = json.loads(json.dumps(spec))
    _photos(spec)
    _pixels(spec)
    out_mp4 = Path(out_mp4).resolve()  # Remotion tourne dans video/ : chemins absolus obligatoires
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    props = out_mp4.with_suffix(".json")
    props.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    cmd = ["npx", "remotion", "render", "src/index.ts", "Reel", str(out_mp4),
           f"--props={props}", "--codec=h264", "--crf=20", "--log=warn", *_browser_args()]
    subprocess.run(cmd, cwd=VIDEO, check=True)
    return out_mp4


def frames_per_scene(spec: dict, mp4: Path) -> list[Path]:
    """Extrait une image au milieu de chaque scène, pour le contrôle visuel."""
    out = []
    mp4 = Path(mp4).resolve()
    t = 0.0
    for i, s in enumerate(spec["scenes"]):
        mid = t + s["duration"] * 0.7
        png = mp4.with_name(f"{mp4.stem}_scene{i}.png")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{mid:.2f}", "-i", str(mp4),
                        "-frames:v", "1", "-vf", "scale=540:-1", str(png)], check=True)
        out.append(png)
        t += s["duration"]
    return out


def contact_sheet(images: list[Path], out: Path) -> Path:
    """Planche d'aperçu : les images des scènes côte à côte (affichée dans l'e-mail de validation)."""
    imgs = images[:8]
    inputs = []
    for i in imgs:
        inputs += ["-i", str(i)]
    filt = "".join(f"[{k}:v]scale=240:-1[s{k}];" for k in range(len(imgs)))
    filt += "".join(f"[s{k}]" for k in range(len(imgs))) + f"hstack=inputs={len(imgs)}"
    if len(imgs) == 1:
        filt = "[0:v]scale=240:-1"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *inputs, "-filter_complex", filt, str(out)], check=True)
    return out
