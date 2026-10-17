"""Appels à l'API Claude, avec recherche web optionnelle et extraction JSON robuste."""
from __future__ import annotations

import base64
import json
import re
import time
from pathlib import Path

import anthropic

_client: anthropic.Anthropic | None = None
USAGE = {"input_tokens": 0, "output_tokens": 0, "web_searches": 0}


def client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()  # lit ANTHROPIC_API_KEY
    return _client


def _text(resp) -> str:
    return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")


def ask(model: str, user: str, *, web_search: int = 0, images: list[Path] | None = None,
        max_tokens: int = 8000, country: str = "FR") -> str:
    """Envoie une requête. web_search = nombre max de recherches web (0 = aucune)."""
    content: list = []
    for img in images or []:
        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                                     "data": base64.b64encode(img.read_bytes()).decode()}})
    content.append({"type": "text", "text": user})
    messages = [{"role": "user", "content": content}]
    tools = []
    if web_search:
        tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": web_search,
                  "user_location": {"type": "approximate", "country": country}}]

    out = ""
    for attempt in range(4):
        try:
            kwargs = dict(model=model, max_tokens=max_tokens, messages=messages)
            if tools:
                kwargs["tools"] = tools
            resp = client().messages.create(**kwargs)
            # La recherche web peut mettre le tour en pause : on relance avec la réponse partielle.
            while resp.stop_reason == "pause_turn":
                messages = messages + [{"role": "assistant", "content": resp.content}]
                kwargs["messages"] = messages
                _count(resp)
                resp = client().messages.create(**kwargs)
            _count(resp)
            out = _text(resp)
            return out
        except (anthropic.RateLimitError, anthropic.APIConnectionError, anthropic.InternalServerError) as e:
            wait = 15 * (attempt + 1)
            print(f"  ! API indisponible ({type(e).__name__}), nouvel essai dans {wait}s")
            time.sleep(wait)
    raise RuntimeError("API Claude injoignable après plusieurs essais")


def _count(resp) -> None:
    u = resp.usage
    USAGE["input_tokens"] += u.input_tokens or 0
    USAGE["output_tokens"] += u.output_tokens or 0
    stu = getattr(u, "server_tool_use", None)
    if stu is not None:
        USAGE["web_searches"] += getattr(stu, "web_search_requests", 0) or 0


def extract_json(text: str):
    m = re.search(r"<json>(.*?)</json>", text, re.S)
    raw = m.group(1) if m else text
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.M).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}")
        if start != -1 and end > start:
            return json.loads(raw[start:end + 1])
        raise


def ask_json(model: str, user: str, **kw):
    """Comme ask(), mais renvoie le JSON parsé ; redemande une fois si le JSON est invalide."""
    text = ask(model, user, **kw)
    try:
        return extract_json(text)
    except (json.JSONDecodeError, ValueError):
        fix = ask(model, "Le texte suivant devait contenir un JSON valide entre <json></json>. "
                         "Renvoie uniquement le JSON corrigé entre <json></json>.\n\n" + text[-12000:])
        return extract_json(fix)
