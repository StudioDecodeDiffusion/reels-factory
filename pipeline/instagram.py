"""API Instagram officielle (« Instagram API with Instagram Login ») : pas de page Facebook nécessaire.

Le compte doit être un compte professionnel (Créateur ou Business). Un token longue durée par compte,
stocké dans un secret GitHub dont le nom est donné par `instagram_secret` dans le profil.
"""
from __future__ import annotations

import os
import time

import requests

from .config import env

BASE = "https://graph.instagram.com"
VER = os.getenv("IG_API_VERSION", "v23.0")


class IG:
    def __init__(self, profile: dict):
        self.token = env(profile["instagram_secret"])
        self._uid: str | None = None

    def _get(self, path: str, **params):
        r = requests.get(f"{BASE}/{VER}/{path}", params={**params, "access_token": self.token}, timeout=60)
        if r.status_code >= 400:
            raise RuntimeError(f"Instagram GET {path} → {r.status_code} {r.text[:400]}")
        return r.json()

    def _post(self, path: str, **data):
        r = requests.post(f"{BASE}/{VER}/{path}", data={**data, "access_token": self.token}, timeout=120)
        if r.status_code >= 400:
            raise RuntimeError(f"Instagram POST {path} → {r.status_code} {r.text[:400]}")
        return r.json()

    @property
    def uid(self) -> str:
        if not self._uid:
            self._uid = str(self._get("me", fields="user_id,username")["user_id"])
        return self._uid

    def username(self) -> str:
        return self._get("me", fields="username")["username"]

    def publish_reel(self, video_url: str, caption: str, share_to_feed: bool = True, cover_url: str | None = None) -> dict:
        extra = {"cover_url": cover_url} if cover_url else {}
        c = self._post(f"{self.uid}/media", media_type="REELS", video_url=video_url, caption=caption,
                       share_to_feed=str(share_to_feed).lower(), **extra)
        cid = c["id"]
        for _ in range(60):  # jusqu'à ~10 min de traitement côté Instagram
            st = self._get(cid, fields="status_code,status")
            if st.get("status_code") == "FINISHED":
                break
            if st.get("status_code") in ("ERROR", "EXPIRED"):
                raise RuntimeError(f"Traitement Instagram en échec : {st}")
            time.sleep(10)
        else:
            raise RuntimeError("Instagram n'a pas fini de traiter la vidéo à temps")
        pub = self._post(f"{self.uid}/media_publish", creation_id=cid)
        info = self._get(pub["id"], fields="id,permalink,timestamp")
        return info

    def delete(self, media_id: str) -> bool:
        r = requests.delete(f"{BASE}/{VER}/{media_id}", params={"access_token": self.token}, timeout=60)
        if r.status_code >= 400:
            raise RuntimeError(f"Instagram DELETE → {r.status_code} {r.text[:300]}")
        return True

    def publish_story(self, image_url: str) -> dict:
        c = self._post(f"{self.uid}/media", media_type="STORIES", image_url=image_url)
        for _ in range(30):
            st = self._get(c["id"], fields="status_code")
            if st.get("status_code") == "FINISHED":
                break
            if st.get("status_code") in ("ERROR", "EXPIRED"):
                raise RuntimeError(f"Story refusée par Instagram : {st}")
            time.sleep(5)
        pub = self._post(f"{self.uid}/media_publish", creation_id=c["id"])
        return {"id": pub["id"]}

    def recent_media(self, limit: int = 15) -> list[dict]:
        return self._get(f"{self.uid}/media", fields="id,caption,media_product_type,timestamp,permalink",
                         limit=limit).get("data", [])

    def insights(self, media_id: str) -> dict:
        out = {}
        for metric in ("views", "reach", "likes", "comments", "shares", "saved", "total_interactions"):
            try:
                d = self._get(f"{media_id}/insights", metric=metric).get("data", [])
                if d:
                    out[metric] = d[0]["values"][0]["value"] if "values" in d[0] else d[0].get("total_value", {}).get("value")
            except RuntimeError:
                pass  # certaines métriques n'existent pas pour tous les médias
        return out

    def comments(self, media_id: str) -> list[dict]:
        return self._get(f"{media_id}/comments", fields="id,text,username,timestamp").get("data", [])

    def reply(self, comment_id: str, message: str) -> dict:
        return self._post(f"{comment_id}/replies", message=message)

    def content_limit(self) -> dict:
        return self._get(f"{self.uid}/content_publishing_limit", fields="quota_usage,config")


def refresh_token(token: str) -> dict:
    """Prolonge un token longue durée de 60 jours (à faire au moins une fois par mois)."""
    r = requests.get(f"{BASE}/refresh_access_token",
                     params={"grant_type": "ig_refresh_token", "access_token": token}, timeout=60)
    r.raise_for_status()
    return r.json()
