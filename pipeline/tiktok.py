"""TikTok (Login Kit + Content Posting API) : connexion d'un compte, puis envoi de chaque vidéo en brouillon
dans l'appli (tant que l'app n'est pas validée par TikTok, l'envoi direct est forcé en privé)."""
from __future__ import annotations

import base64
import hashlib
import os
import urllib.parse

import requests
from cryptography.fernet import Fernet

from . import state

API = "https://open.tiktokapis.com/v2"
RETOUR = "https://studiodecodediffusion.github.io/reels-media/tiktok/retour.html"
SCOPES = "user.info.basic,user.info.profile,user.info.stats,video.list,video.publish,video.upload"


def _cles():
    k, s = os.environ["TIKTOK_CLIENT_KEY"].strip(), os.environ["TIKTOK_CLIENT_SECRET"].strip()
    return k, s, Fernet(base64.urlsafe_b64encode(hashlib.sha256(s.encode()).digest()))


def lien(compte: str) -> str:
    # GitHub masque les secrets (« *** ») dans le résumé : la clé est écrite caractère par caractère en %XX
    cle = "".join(f"%{ord(ch):02X}" for ch in _cles()[0])
    return f"https://www.tiktok.com/v2/auth/authorize/?client_key={cle}&" + urllib.parse.urlencode(
        {"scope": SCOPES, "response_type": "code", "redirect_uri": RETOUR, "state": compte})


def _jeton(donnees: dict) -> dict:
    k, s, _ = _cles()
    r = requests.post(f"{API}/oauth/token/", data={"client_key": k, "client_secret": s, **donnees}, timeout=30).json()
    if "access_token" not in r:
        raise RuntimeError(f"TikTok refuse : {r.get('error_description') or r}")
    return r


def _sauver(compte: str, r: dict) -> None:
    comptes = state.load("tiktok", {})
    comptes[compte] = {"open_id": r.get("open_id"), "refresh": _cles()[2].encrypt(r["refresh_token"].encode()).decode(),
                       "maj": state.now_iso()}  # clé chiffrée (secret de l'app) : jamais en clair dans le dépôt
    state.save("tiktok", comptes)


def connecter(compte: str, code: str) -> dict:
    r = _jeton({"code": code.strip(), "grant_type": "authorization_code", "redirect_uri": RETOUR})
    _sauver(compte, r)
    u = requests.get(f"{API}/user/info/", params={"fields": "display_name,username,follower_count"},
                     headers={"Authorization": f"Bearer {r['access_token']}"}, timeout=30).json()
    return (u.get("data") or {}).get("user", {})


def acces(compte: str) -> str | None:
    c = state.load("tiktok", {}).get(compte)
    if not c:
        return None
    r = _jeton({"grant_type": "refresh_token", "refresh_token": _cles()[2].decrypt(c["refresh"].encode()).decode()})
    _sauver(compte, r)  # TikTok renvoie un nouveau jeton de renouvellement à chaque fois
    return r["access_token"]


def brouillon(compte: str, video_url: str) -> str | None:
    """Envoie la vidéo dans les notifications TikTok du compte (brouillon à publier dans l'appli)."""
    jeton = acces(compte)
    if not jeton:
        return None
    video = requests.get(video_url, timeout=300).content
    n = len(video)
    init = requests.post(f"{API}/post/publish/inbox/video/init/", timeout=60,
                         json={"source_info": {"source": "FILE_UPLOAD", "video_size": n, "chunk_size": n, "total_chunk_count": 1}},
                         headers={"Authorization": f"Bearer {jeton}", "Content-Type": "application/json; charset=UTF-8"}).json()
    d = init.get("data") or {}
    if not d.get("upload_url"):
        raise RuntimeError(f"TikTok refuse l'envoi : {init.get('error')}")
    up = requests.put(d["upload_url"], data=video, timeout=600,
                      headers={"Content-Type": "video/mp4", "Content-Range": f"bytes 0-{n - 1}/{n}"})
    if up.status_code >= 300:
        raise RuntimeError(f"TikTok : envoi refusé ({up.status_code}) {up.text[:200]}")
    return d.get("publish_id")


def publier(compte: str, video_url: str, legende: str) -> dict:
    """Publication directe (propriétaire, 25/10 : tout automatique). Publique si TikTok l'autorise ; tant que l'app
    n'est pas validée par TikTok, seule la visibilité « moi uniquement » est permise : la vidéo est alors sur le profil, en privé."""
    jeton = acces(compte)
    if not jeton:
        return {}
    h = {"Authorization": f"Bearer {jeton}", "Content-Type": "application/json; charset=UTF-8"}
    info = (requests.post(f"{API}/post/publish/creator_info/query/", headers=h, timeout=30).json().get("data") or {})
    options = info.get("privacy_level_options") or ["SELF_ONLY"]
    vis = "PUBLIC_TO_EVERYONE" if "PUBLIC_TO_EVERYONE" in options else options[0]
    video = requests.get(video_url, timeout=300).content
    n = len(video)
    init = requests.post(f"{API}/post/publish/video/init/", headers=h, timeout=60, json={
        "post_info": {"title": legende[:2200], "privacy_level": vis, "disable_duet": False, "disable_comment": False,
                      "disable_stitch": False, "is_aigc": False},
        "source_info": {"source": "FILE_UPLOAD", "video_size": n, "chunk_size": n, "total_chunk_count": 1}}).json()
    d = init.get("data") or {}
    if not d.get("upload_url"):
        raise RuntimeError(f"TikTok refuse la publication : {init.get('error')}")
    up = requests.put(d["upload_url"], data=video, timeout=600,
                      headers={"Content-Type": "video/mp4", "Content-Range": f"bytes 0-{n - 1}/{n}"})
    if up.status_code >= 300:
        raise RuntimeError(f"TikTok : envoi refusé ({up.status_code}) {up.text[:200]}")
    return {"publish_id": d.get("publish_id"), "visibilite": vis, "compte": info.get("creator_username")}
