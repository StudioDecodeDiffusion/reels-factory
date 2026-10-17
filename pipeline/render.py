"""Validation de la spécification vidéo et rendu Remotion."""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

from .config import VIDEO

HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
FONTS = {"Space Grotesk", "Inter", "JetBrains Mono"}
MODES = {"gravity", "orbit", "bounce", "swarm", "pendulum_wave"}

REQUIRED = {
    "hook": ["title"], "kinetic": ["lines"], "counter": ["to", "label"],
    "bars": ["title", "items"], "timeline": ["events"], "dots": ["total", "highlighted", "label"],
    "compare": ["left", "right"], "particles": ["mode", "caption"], "outro": ["text", "cta"],
}


def validate_spec(spec: dict, allowed: list[str]) -> list[str]:
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
    th["grille"] = bool(th.get("grille", False))

    scenes = spec.get("scenes") or []
    if not 3 <= len(scenes) <= 12:
        errs.append("il faut entre 3 et 12 scènes")
    for i, s in enumerate(scenes):
        t = s.get("type")
        if t not in REQUIRED:
            errs.append(f"scène {i} : type inconnu « {t} »")
            continue
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
        s["duration"] = min(max(s["duration"], 1.5), 7.0)
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
        if t == "particles" and s.get("mode") not in MODES:
            errs.append(f"scène {i} : mode doit être parmi {sorted(MODES)}")
    total = sum(s.get("duration", 0) for s in scenes if isinstance(s.get("duration"), float))
    if total > 60:
        errs.append(f"durée totale {total:.0f}s trop longue (max 60)")
    return errs


def _browser_args() -> list[str]:
    exe = os.getenv("REMOTION_BROWSER")
    return [f"--browser-executable={exe}", "--chrome-mode=headless-shell"] if exe else []


def render(spec: dict, out_mp4: Path) -> Path:
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
    t = 0.0
    for i, s in enumerate(spec["scenes"]):
        mid = t + s["duration"] * 0.7
        png = mp4.with_name(f"{mp4.stem}_scene{i}.png")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{mid:.2f}", "-i", str(mp4),
                        "-frames:v", "1", "-vf", "scale=540:-1", str(png)], check=True)
        out.append(png)
        t += s["duration"]
    return out
