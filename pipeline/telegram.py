"""Bot Telegram : t'envoie les vidéos à valider et lit tes réponses (OK / NON / REP)."""
from __future__ import annotations

from pathlib import Path

import requests

from . import state
from .config import env


def _api(method: str) -> str:
    return f"https://api.telegram.org/bot{env('TELEGRAM_BOT_TOKEN')}/{method}"


def send(text: str) -> None:
    for i in range(0, len(text), 3900):  # limite Telegram : 4096 caractères
        requests.post(_api("sendMessage"), data={"chat_id": env("TELEGRAM_CHAT_ID"), "text": text[i:i + 3900],
                                                  "disable_web_page_preview": "true"}, timeout=60).raise_for_status()


def send_video(mp4: Path, caption: str) -> None:
    with mp4.open("rb") as f:
        r = requests.post(_api("sendVideo"),
                          data={"chat_id": env("TELEGRAM_CHAT_ID"), "caption": caption[:1000],
                                "supports_streaming": "true", "width": 1080, "height": 1920},
                          files={"video": (mp4.name, f, "video/mp4")}, timeout=300)
    r.raise_for_status()


def new_messages() -> list[str]:
    """Messages reçus depuis la dernière lecture, uniquement de TON compte Telegram."""
    offset = state.load("telegram_offset", {"offset": 0})["offset"]
    r = requests.get(_api("getUpdates"), params={"offset": offset, "timeout": 0}, timeout=60)
    r.raise_for_status()
    me = str(env("TELEGRAM_CHAT_ID"))
    out = []
    for u in r.json().get("result", []):
        offset = max(offset, u["update_id"] + 1)
        msg = u.get("message") or {}
        if str(msg.get("chat", {}).get("id")) == me and msg.get("text"):
            out.append(msg["text"].strip())
    state.save("telegram_offset", {"offset": offset})
    return out
