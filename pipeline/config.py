"""Chemins, profils et réglages communs."""
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

ROOT = Path(__file__).resolve().parent.parent
PROFILES = ROOT / "profiles"
PROMPTS = ROOT / "prompts"
STATE = ROOT / "state"
TRENDS = ROOT / "trends"
VIDEO = ROOT / "video"
OUTPUT = ROOT / "output"

# Modèles : léger pour la veille, plus fort pour l'écriture et le code.
MODEL_FAST = os.getenv("MODEL_FAST", "claude-haiku-5-5")
MODEL_SMART = os.getenv("MODEL_SMART", "claude-sonnet-5-5")

TZ = ZoneInfo(os.getenv("TZ_LOCAL", "Europe/Paris"))

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre"]


def today_fr() -> str:
    d = datetime.now(TZ)
    return f"{d.day} {MOIS[d.month - 1]} {d.year}"


def load_profile(pid: str) -> dict:
    path = PROFILES / f"{pid}.yaml"
    if not path.exists():
        raise SystemExit(f"Profil inconnu : {pid} (attendu : {path})")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def all_profiles() -> list[str]:
    return sorted(p.stem for p in PROFILES.glob("*.yaml"))


def prompt(name: str, **kw) -> str:
    return (PROMPTS / f"{name}.md").read_text(encoding="utf-8").format(**kw)


def env(name: str, required: bool = True) -> str | None:
    v = os.getenv(name)
    if required and not v:
        raise SystemExit(f"Variable d'environnement manquante : {name} (à ajouter dans les secrets GitHub)")
    return v
