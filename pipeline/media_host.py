"""Hébergement temporaire de la vidéo : Instagram exige une URL publique pour récupérer le MP4.

Deux modes (variable MEDIA_HOST) :
- "github" (défaut, gratuit) : release sur un petit dépôt PUBLIC dédié (MEDIA_REPO, ex. "moncompte/reels-media"),
  supprimée après publication.
- "s3" : n'importe quel stockage compatible S3 avec URL publique (Cloudflare R2 a un niveau gratuit).
"""
from __future__ import annotations

import os
from pathlib import Path

import requests

from .config import env

GH = "https://api.github.com"


def _gh_headers() -> dict:
    return {"Authorization": f"Bearer {env('GH_PAT')}", "Accept": "application/vnd.github+json"}


def upload(mp4: Path, job_id: str) -> dict:
    mode = os.getenv("MEDIA_HOST", "github")
    if mode == "s3":
        return _upload_s3(mp4, job_id)
    repo = env("MEDIA_REPO")
    tag = f"reel-{job_id}"
    r = requests.post(f"{GH}/repos/{repo}/releases", headers=_gh_headers(),
                      json={"tag_name": tag, "name": tag, "body": "Vidéo temporaire, supprimée après publication."},
                      timeout=60)
    r.raise_for_status()
    rel = r.json()
    up = rel["upload_url"].split("{")[0]
    with mp4.open("rb") as f:
        a = requests.post(f"{up}?name={job_id}.mp4", headers={**_gh_headers(), "Content-Type": "video/mp4"},
                          data=f, timeout=300)
    a.raise_for_status()
    return {"mode": "github", "url": a.json()["browser_download_url"], "release_id": rel["id"], "tag": tag}


def cleanup(info: dict) -> None:
    try:
        if info.get("mode") == "github":
            repo = env("MEDIA_REPO")
            requests.delete(f"{GH}/repos/{repo}/releases/{info['release_id']}", headers=_gh_headers(), timeout=60)
            requests.delete(f"{GH}/repos/{repo}/git/refs/tags/{info['tag']}", headers=_gh_headers(), timeout=60)
        elif info.get("mode") == "s3":
            _s3().delete_object(Bucket=env("S3_BUCKET"), Key=info["key"])
    except Exception as e:  # le nettoyage n'est jamais bloquant
        print(f"  ! nettoyage média impossible : {e}")


def _s3():
    import boto3  # installé seulement si MEDIA_HOST=s3
    return boto3.client("s3", endpoint_url=env("S3_ENDPOINT"), aws_access_key_id=env("S3_KEY"),
                        aws_secret_access_key=env("S3_SECRET"), region_name=os.getenv("S3_REGION", "auto"))


def _upload_s3(mp4: Path, job_id: str) -> dict:
    key = f"reels/{job_id}.mp4"
    _s3().upload_file(str(mp4), env("S3_BUCKET"), key, ExtraArgs={"ContentType": "video/mp4"})
    return {"mode": "s3", "url": f"{env('S3_PUBLIC_BASE').rstrip('/')}/{key}", "key": key}
