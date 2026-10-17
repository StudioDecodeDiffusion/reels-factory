"""Mémoire du pipeline : fichiers JSON versionnés dans le dépôt (dossier state/)."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from .config import STATE

STATE.mkdir(exist_ok=True)


def _path(name: str):
    return STATE / f"{name}.json"


def load(name: str, default):
    p = _path(name)
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


def save(name: str, data) -> None:
    _path(name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --- historique des sujets traités, pour éviter les doublons
def history(pid: str) -> list[dict]:
    return load(f"historique_{pid}", [])


def add_history(pid: str, item: dict) -> None:
    h = history(pid)
    h.append(item)
    save(f"historique_{pid}", h[-200:])


# --- charte graphique vivante du compte
def charte(profile: dict) -> dict:
    return load(f"charte_{profile['id']}", profile.get("charte_initiale", {}))


def set_charte(pid: str, data: dict) -> None:
    save(f"charte_{pid}", data)


# --- file d'attente des vidéos en attente de validation / publiées
def queue() -> list[dict]:
    return load("file_attente", [])


def save_queue(q: list[dict]) -> None:
    save("file_attente", q)
