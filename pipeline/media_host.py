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


def archiver(fichiers: dict[str, Path], mois: str) -> str:
    """Range des fichiers dans la release privée « archive-AAAA-MM » du dépôt reels-factory (accès : toi seul).
    fichiers = {nom_dans_l_archive: chemin}. Renvoie le lien de la page d'archive."""
    repo = os.getenv("GITHUB_REPOSITORY") or "StudioDecodeDiffusion/reels-factory"
    tag = f"archive-{mois}"
    r = requests.get(f"{GH}/repos/{repo}/releases/tags/{tag}", headers=_h(), timeout=60)
    if r.status_code == 404:
        r = requests.post(f"{GH}/repos/{repo}/releases", headers=_h(), timeout=60,
                          json={"tag_name": tag, "name": f"Archive {mois}",
                                "body": "Vidéos publiées : vidéo finale, miniature, story et sources."})
    if not r.ok:
        raise RuntimeError(f"Archive GitHub {r.status_code} : {r.text[:300]}")
    rel = r.json()
    up = rel["upload_url"].split("{")[0]
    deja = {a["name"]: a["id"] for a in rel.get("assets", [])}
    for nom, p in fichiers.items():
        if nom in deja:
            requests.delete(f"{GH}/repos/{repo}/releases/assets/{deja[nom]}", headers=_h(), timeout=60)
        ctype = {".mp4": "video/mp4", ".png": "image/png"}.get(Path(p).suffix, "text/plain; charset=utf-8")
        with open(p, "rb") as fh:
            a = requests.post(f"{up}?name={nom}", headers={**_h(), "Content-Type": ctype}, data=fh, timeout=600)
        if not a.ok:
            raise RuntimeError(f"Archive ({nom}) {a.status_code} : {a.text[:200]}")
    return rel["html_url"]
