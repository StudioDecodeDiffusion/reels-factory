"""Hébergement de la vidéo le temps qu'Instagram la récupère (Instagram exige une URL publique).

Mode par défaut (gratuit) : une « release » sur le petit dépôt PUBLIC `MEDIA_REPO`
(ex. « en30s-studio/reels-media »), supprimée après publication.
"""
from __future__ import annotations

from pathlib import Path

import os

import requests

from .config import env

GH = "https://api.github.com"


def _h() -> dict:
    return {"Authorization": f"Bearer {env('GH_PAT')}", "Accept": "application/vnd.github+json"}


def upload(files: list[Path], job_id: str) -> dict:
    repo = os.getenv("MEDIA_REPO") or "StudioDecodeDiffusion/reels-media"
    tag = f"reel-{job_id}"
    corps = {"tag_name": tag, "name": tag, "body": "Fichiers temporaires, supprimés après publication."}
    r = requests.post(f"{GH}/repos/{repo}/releases", headers=_h(), timeout=60, json=corps)
    if r.status_code == 422:  # une release du même nom existe déjà (essai précédent) : on la remplace
        old = requests.get(f"{GH}/repos/{repo}/releases/tags/{tag}", headers=_h(), timeout=60)
        if old.ok:
            requests.delete(f"{GH}/repos/{repo}/releases/{old.json()['id']}", headers=_h(), timeout=60)
        requests.delete(f"{GH}/repos/{repo}/git/refs/tags/{tag}", headers=_h(), timeout=60)
        r = requests.post(f"{GH}/repos/{repo}/releases", headers=_h(), timeout=60, json=corps)
    if not r.ok:
        raise RuntimeError(f"GitHub (hébergement) {r.status_code} : {r.text[:300]}")
    rel = r.json()
    up = rel["upload_url"].split("{")[0]
    urls = {}
    for f in files:
        ctype = "video/mp4" if f.suffix == ".mp4" else "image/png"
        with f.open("rb") as fh:
            a = requests.post(f"{up}?name={f.name}", headers={**_h(), "Content-Type": ctype}, data=fh, timeout=300)
        if not a.ok:
            raise RuntimeError(f"GitHub (envoi de {f.name}) {a.status_code} : {a.text[:300]}")
        urls[f.name] = a.json()["browser_download_url"]
    return {"repo": repo, "release_id": rel["id"], "tag": tag, "urls": urls}


def cleanup(info: dict | None) -> None:
    if not info:
        return
    try:
        requests.delete(f"{GH}/repos/{info['repo']}/releases/{info['release_id']}", headers=_h(), timeout=60)
        requests.delete(f"{GH}/repos/{info['repo']}/git/refs/tags/{info['tag']}", headers=_h(), timeout=60)
    except Exception as e:  # jamais bloquant
        print(f"  ! nettoyage impossible : {e}")
