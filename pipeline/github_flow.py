"""Côté GitHub Actions (gratuit) : fiches de validation par e-mail, publication Instagram, statistiques.

  python -m pipeline.github_flow on-drop <dossier drop/>   nouvelle vidéo → fiche (issue) → e-mail
  python -m pipeline.github_flow on-comment                ta réponse (OK / NON / REP) → action
  python -m pipeline.github_flow publish                   toutes les heures : publie ce qui est validé
  python -m pipeline.github_flow stats                     chaque soir : stats + nouveaux commentaires
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

from . import media_host, state
from .config import TZ, all_profiles, env, load_profile

API = "https://api.github.com"
REPO = os.getenv("GITHUB_REPOSITORY", "")
OWNER = os.getenv("REPO_OWNER") or REPO.split("/")[0]


def gh(method: str, path: str, **kw):
    r = requests.request(method, f"{API}/repos/{REPO}{path}", timeout=60,
                         headers={"Authorization": f"Bearer {env('GITHUB_TOKEN')}",
                                  "Accept": "application/vnd.github+json"}, **kw)
    if r.status_code >= 400:
        raise RuntimeError(f"GitHub {method} {path} → {r.status_code} {r.text[:300]}")
    return r.json() if r.text else {}


def comment(issue: int, body: str) -> None:
    gh("POST", f"/issues/{issue}/comments", json={"body": body})


def set_labels(issue: int, labels: list[str]) -> None:
    gh("PUT", f"/issues/{issue}/labels", json={"labels": labels})


def close(issue: int) -> None:
    gh("PATCH", f"/issues/{issue}", json={"state": "closed"})


def attente(job_id: str):
    return state.load(f"attente/{job_id}", None)


def save_attente(fiche: dict) -> None:
    (state.STATE / "attente").mkdir(exist_ok=True)
    state.save(f"attente/{fiche['id']}", fiche)


def all_attente() -> list[dict]:
    d = state.STATE / "attente"
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(d.glob("*.json"))] if d.exists() else []


def _replies_md(comm: dict) -> str:
    rep = comm.get("reponses") or []
    out = ""
    if comm.get("bilan"):
        out += f"\n### 📊 Bilan du compte\n{comm['bilan']}\n"
        if comm.get("recommandations"):
            out += "\n" + "\n".join(f"- {r}" for r in comm["recommandations"]) + "\n"
    if rep:
        out += "\n### 💬 Réponses proposées aux commentaires\n"
        for i, r in enumerate(rep, 1):
            out += f"{i}. « {str(r.get('commentaire', ''))[:140]} »\n   → {r.get('reponse')}\n"
        out += "\nPour les envoyer : réponds `REP 1 3` (numéros choisis) ou `REP TOUT`.\n"
    return out


def _publication_slot(profile: dict) -> str:
    h = profile["planning"].get("publication_heure", 18)
    return f"aujourd'hui vers {h} h" if datetime.now(TZ).hour < h else f"demain vers {h} h"


# ────────────────────────────────────────────── nouvelle vidéo déposée par la session de nuit
def on_drop(drop_dir: str) -> None:
    for d in sorted(Path(drop_dir).iterdir()):
        f = d / "fiche.json"
        if not f.exists():
            continue
        fiche = json.loads(f.read_text(encoding="utf-8"))
        if attente(fiche["id"]):
            print(f"{fiche['id']} déjà traité")
            continue
        profile = load_profile(fiche["profil"])
        name = profile["nom_compte"]

        if fiche["statut"] == "abandonnee":
            issue = gh("POST", "/issues", json={
                "title": f"[{name}] Pas de vidéo cette nuit",
                "body": f"@{OWNER} aucune vidéo n'a été produite pour **{name}**.\n\n**Raison :** {fiche.get('raison')}\n"
                        + _replies_md(fiche.get("community") or {}),
                "labels": [f"compte:{fiche['profil']}", "abandonnee"]})
            fiche.update(issue=issue["number"], media=None)
            save_attente(fiche)
            if not (fiche.get("community") or {}).get("reponses"):
                close(issue["number"])
            continue

        media = media_host.upload([d / "video.mp4", d / "apercu.png"], fiche["id"])
        v, ap = media["urls"]["video.mp4"], media["urls"]["apercu.png"]
        verif = fiche.get("verification", {})
        notes = fiche.get("validation", {}).get("notes", {})
        notes_txt = " · ".join(f"{k} {v_}/10" for k, v_ in notes.items())
        sources = "\n".join(f"- {s}" for s in fiche.get("sources", [])) or "- (aucune)"
        body = f"""@{OWNER} nouvelle vidéo à valider pour **{name}** — publication prévue **{_publication_slot(profile)}**.

![aperçu]({ap})

### ▶️ [Regarder la vidéo]({v})

### Légende prévue
```
{fiche['legende']}
```

### Vérification
- **Vérificateur final :** {verif.get('decision', '?')} ({verif.get('score_global', '?')}/10) — {verif.get('resume_pour_le_proprietaire', '')}
- **Validateur :** {notes_txt} ({fiche.get('tours_validation', 1)} tour(s))

### Sources
{sources}
{_replies_md(fiche.get('community') or {})}
---
**Réponds simplement à cet e-mail** (ou commente ici), première ligne :
- `OK` → publication à l'heure prévue
- `OK MAINTENANT` → publication immédiate
- `NON` suivi de ta raison → vidéo abandonnée, la raison sert aux prochaines idées

Sans réponse sous 36 h, la vidéo est abandonnée automatiquement.
<!-- job:{fiche['id']} -->"""
        issue = gh("POST", "/issues", json={"title": f"[{name}] {fiche['titre']}", "body": body,
                                            "labels": [f"compte:{fiche['profil']}", "a-valider"]})
        fiche.update(issue=issue["number"], media=media)
        fiche.pop("verification", None)
        save_attente(fiche)
        print(f"Fiche #{issue['number']} créée pour {fiche['id']}")


# ────────────────────────────────────────────── ta réponse
def _job_from_issue(n: int):
    return next((f for f in all_attente() if f.get("issue") == n), None)


def on_comment() -> None:
    author = os.getenv("COMMENT_AUTHOR", "")
    if author.lower() != OWNER.lower():
        print(f"Commentaire de {author} ignoré (seul {OWNER} peut valider)")
        return
    n = int(env("ISSUE_NUMBER"))
    fiche = _job_from_issue(n)
    if not fiche:
        print("Pas de vidéo liée à cette fiche")
        return
    body = os.getenv("COMMENT_BODY", "")
    # Réponse par e-mail : on ne garde que ce qui précède la citation de l'e-mail d'origine
    lines = [ln.strip() for ln in re.split(r"\n\s*(?:On .+wrote:|Le .+a écrit\s*:|>)", body)[0].splitlines() if ln.strip()]
    if not lines:
        return
    first = lines[0]
    m = re.match(r"^(OK|NON|REP)\b\s*(.*)$", first, re.I)
    if not m:
        comment(n, "Je n'ai pas compris. Première ligne attendue : `OK`, `OK MAINTENANT`, `NON raison` ou `REP 1 3`.")
        return
    cmd, rest = m.group(1).upper(), m.group(2).strip()
    profile = load_profile(fiche["profil"])

    if cmd == "REP":
        _send_replies(fiche, rest, n, profile)
    elif fiche["statut"] not in ("a_valider", "approuvee"):
        comment(n, f"Cette vidéo est déjà « {fiche['statut']} ».")
    elif cmd == "NON":
        raison = rest + (" " + " ".join(lines[1:]) if len(lines) > 1 else "")
        fiche.update(statut="refusee", raison=raison.strip())
        media_host.cleanup(fiche.get("media"))
        refus = state.load(f"refus_{fiche['profil']}", [])
        refus.append({"titre": fiche["titre"], "raison": raison.strip(), "date": fiche["cree"][:10]})
        state.save(f"refus_{fiche['profil']}", refus[-50:])
        set_labels(n, [f"compte:{fiche['profil']}", "refusee"])
        comment(n, "🗑️ Vidéo abandonnée. Ta raison est notée : les agents en tiendront compte.")
        close(n)
    else:  # OK
        fiche["statut"] = "approuvee"
        set_labels(n, [f"compte:{fiche['profil']}", "approuvee"])
        if "MAINTENANT" in rest.upper():
            save_attente(fiche)
            _publish(fiche, profile)
            return
        comment(n, f"👍 Validée. Publication {_publication_slot(profile)}.")
    save_attente(fiche)


def _send_replies(fiche: dict, rest: str, n: int, profile: dict) -> None:
    from .instagram import IG
    rep = (fiche.get("community") or {}).get("reponses") or []
    if not rep:
        comment(n, "Aucune réponse proposée sur cette fiche.")
        return
    idx = range(1, len(rep) + 1) if rest.upper().startswith("TOUT") else [int(x) for x in re.findall(r"\d+", rest)]
    ig, ok, ko = IG(profile), [], []
    for i in idx:
        if not 1 <= i <= len(rep) or rep[i - 1].get("envoyee"):
            continue
        try:
            ig.reply(rep[i - 1]["comment_id"], rep[i - 1]["reponse"])
            rep[i - 1]["envoyee"] = True
            ok.append(str(i))
        except Exception as e:
            ko.append(f"{i} ({str(e)[:120]})")
    save_attente(fiche)
    comment(n, f"💬 Réponses envoyées : {', '.join(ok) or 'aucune'}" + (f"\n❌ Échecs : {'; '.join(ko)}" if ko else ""))


# ────────────────────────────────────────────── publication
def _publish(fiche: dict, profile: dict) -> None:
    from .instagram import IG
    n = fiche["issue"]
    try:
        info = IG(profile).publish_reel(fiche["media"]["urls"]["video.mp4"], fiche["legende"])
    except Exception as e:
        fiche["erreur"] = str(e)[:500]
        save_attente(fiche)
        comment(n, f"❌ Échec de publication : {str(e)[:500]}\n\nRéponds `OK MAINTENANT` pour réessayer.")
        return
    fiche.update(statut="publiee", media_id=info["id"], permalink=info.get("permalink"), publiee=state.now_iso())
    save_attente(fiche)
    media_host.cleanup(fiche["media"])
    set_labels(n, [f"compte:{fiche['profil']}", "publiee"])
    comment(n, f"✅ Publiée sur {profile['nom_compte']} : {info.get('permalink', '')}")
    if not any(not r.get("envoyee") for r in (fiche.get("community") or {}).get("reponses") or []):
        close(n)


def publish() -> None:
    now = datetime.now(TZ)
    for fiche in all_attente():
        profile = load_profile(fiche["profil"])
        p = profile["planning"]
        if (fiche["statut"] == "approuvee" and now.hour >= p.get("publication_heure", 18)
                and now.isoweekday() in p.get("publication_jours", range(1, 8))):
            _publish(fiche, profile)
        elif fiche["statut"] == "a_valider" and \
                datetime.fromisoformat(fiche["cree"]) < datetime.now(timezone.utc) - timedelta(hours=36):
            fiche["statut"] = "expiree"
            media_host.cleanup(fiche.get("media"))
            save_attente(fiche)
            set_labels(fiche["issue"], [f"compte:{fiche['profil']}", "expiree"])
            comment(fiche["issue"], "⌛ Pas de réponse sous 36 h : vidéo abandonnée.")
            close(fiche["issue"])
    # ménage : on ne garde que 60 jours de fiches terminées
    limit = datetime.now(timezone.utc) - timedelta(days=60)
    for fiche in all_attente():
        if fiche["statut"] in ("publiee", "refusee", "expiree", "abandonnee") and \
                datetime.fromisoformat(fiche["cree"]) < limit:
            (state.STATE / "attente" / f"{fiche['id']}.json").unlink(missing_ok=True)


# ────────────────────────────────────────────── statistiques et commentaires
def stats() -> None:
    from .instagram import IG
    for pid in all_profiles():
        profile = load_profile(pid)
        if not os.getenv(profile["instagram_secret"]):
            print(f"{pid} : pas de token, ignoré")
            continue
        try:
            ig = IG(profile)
            me = ig.username()
            seen = set(state.load(f"commentaires_vus_{pid}", []))
            old = state.load(f"stats_{pid}", {})
            posts, new = [], []
            for m in ig.recent_media(15):
                posts.append({"id": m["id"], "date": m.get("timestamp"), "lien": m.get("permalink"),
                              "legende": (m.get("caption") or "")[:120], **ig.insights(m["id"])})
                for c in ig.comments(m["id"]):
                    if c["id"] not in seen and c.get("username") != me:
                        new.append({"comment_id": c["id"], "auteur": c.get("username"), "texte": c.get("text"),
                                    "post": (m.get("caption") or "")[:60], "date": c.get("timestamp")})
                        seen.add(c["id"])
            state.save(f"stats_{pid}", {"maj": state.now_iso(), "posts": posts,
                                        "recommandations": old.get("recommandations", [])})
            pending = state.load(f"commentaires_{pid}", [])
            state.save(f"commentaires_{pid}", (pending + new)[-60:])
            state.save(f"commentaires_vus_{pid}", sorted(seen)[-3000:])
            print(f"{pid} : {len(posts)} posts, {len(new)} nouveaux commentaires")
        except Exception as e:
            print(f"{pid} : erreur {e}")


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "on-drop":
        on_drop(sys.argv[2])
    elif cmd == "on-comment":
        on_comment()
    elif cmd == "publish":
        publish()
    elif cmd == "stats":
        stats()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
