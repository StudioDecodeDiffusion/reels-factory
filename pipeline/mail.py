"""Messagerie des agents par le Gmail du studio (gratuit) : envoi SMTP, lecture IMAP.

Secrets GitHub nécessaires : GMAIL_ADDRESS (variable ou secret) et GMAIL_APP_PASSWORD (mot de passe
d'application Google, 16 lettres). Tous les mails partent de l'adresse du studio vers elle-même.

- Objet de chaque mail : « Agent N - JJ/MM/AA - titre ».
- Chaque mail se termine par « comment répondre » + le rappel du système de notes.
- Les mails envoyés par les agents portent l'en-tête X-Decode-Agent : le facteur les ignore à la lecture.
"""
from __future__ import annotations

import email
import html as htmllib
import imaplib
import json
import os
import re
import smtplib
from datetime import datetime
from email.header import decode_header, make_header
from email.message import EmailMessage
from email.utils import make_msgid
from pathlib import Path

from . import state
from .config import OUTPUT, TZ

SMTP = ("smtp.gmail.com", 465)
IMAP = "imap.gmail.com"
LABEL_TRAITE = "Decode-traite"   # tes mails déjà lus par le facteur
LABEL_AGENTS = "Decode-agents"
RENDUS = "Decode/Manager - rendus finaux"   # vidéos finales : à valider, montées, publiées   # mails envoyés par les agents

NOMS = {1: "Veille actualité", 2: "Veille tendances", 3: "Résultats du compte", 4: "Concept & critique",
        5: "Scénario", 6: "Directeur artistique", 7: "Générateur vidéo", 8: "Community manager", 9: "Critique",
        10: "Veille comptes IA"}

RAPPEL = ("💬 <b>Pour parler à un agent :</b> envoie-toi un mail avec l'objet "
          "<b>« agent N° - ta note »</b> (ex. « agent 6 - plus de couleurs vives » pour tous les comptes, "
          "« agent 6.2 - … » pour le sous-agent du compte n° 2). Il la lira avant son prochain travail.")


def adresse() -> str:
    return os.getenv("GMAIL_ADDRESS") or "studiodecodediffusion@gmail.com"


def date_courte() -> str:
    return datetime.now(TZ).strftime("%d/%m/%y")


def numero_agent(agent, profil: str | None = None) -> str:
    """« 6 » pour l'agent principal, « 6.2 » pour son sous-agent du compte n° 2."""
    if not str(agent).isdigit():
        return str(agent)  # « Manager »
    if profil:
        try:
            from .config import load_profile
            n = load_profile(profil).get("numero")
            if n:
                return f"{agent}.{n}"
        except Exception:
            pass
    return str(agent)


def objet(agent, titre: str, profil: str | None = None) -> str:
    n = numero_agent(agent, profil)
    return f"{'Agent ' + n if n[0].isdigit() else n} - {date_courte()} - {titre}"


def normaliser(sujet: str) -> str:
    """Retire « Re: », « TR: », « Fwd: »… et les espaces multiples."""
    s = sujet or ""
    while True:
        n = re.sub(r"^\s*(re|tr|fw|fwd|réf|aw)\s*:\s*", "", s, flags=re.I)
        if n == s:
            break
        s = n
    return re.sub(r"\s+", " ", s).strip().lower()


def _gabarit(agent, corps_html: str, reponse_html: str, label: str | None = None) -> str:
    a = str(agent).split(".")[0]
    nom = NOMS.get(int(a), "") if a.isdigit() else "Suivi du pipeline"
    return f"""<div style="font-family:Arial,Helvetica,sans-serif;max-width:640px;margin:auto;color:#14131C">
<div style="background:#14131C;color:#fff;padding:12px 18px;border-radius:12px 12px 0 0;font-weight:bold">
🤖 {"Agent " if str(agent)[0].isdigit() else ""}{label or agent} · {nom} <span style="float:right;color:#FFD23F">Studio Decode et diffusion</span></div>
<div style="border:3px solid #14131C;border-top:none;padding:18px;border-radius:0 0 12px 12px">
{corps_html}
<hr style="border:none;border-top:2px dashed #ccc;margin:22px 0">
<div style="background:#FFF3B0;border:2px solid #14131C;border-radius:10px;padding:12px 14px">
<b>↩️ Comment répondre à ce mail</b><br>{reponse_html}<br><br>
<span style="font-size:13px">⚠️ Réponds <b>depuis la boîte studiodecodediffusion@gmail.com</b> (connecté à ce compte Gmail) :
une réponse envoyée depuis une autre adresse est bloquée par Gmail et n'arrive jamais aux agents.</span></div>
<p style="font-size:13px;color:#444;margin-top:14px">{RAPPEL}</p>
</div></div>"""


def envoyer(agent: int, titre: str, corps_html: str, reponse_html: str, ref: dict | None = None,
            images: dict[str, Path] | None = None, pieces: list[Path] | None = None) -> str:
    """Envoie un mail d'agent. images = {cid: chemin PNG} (à appeler dans le HTML par <img src="cid:…">)."""
    profil = (ref or {}).get("profil")
    sujet = objet(agent, titre, profil)
    msg = EmailMessage()
    msg["Subject"] = sujet
    lab = numero_agent(agent, profil)
    msg["From"] = f"{'Agent ' + lab if lab[0].isdigit() else lab} · Décodé <{adresse()}>"
    msg["To"] = adresse()
    msg["X-Decode-Agent"] = str(agent)
    msg["X-Decode-Ref"] = json.dumps(ref or {}, ensure_ascii=False)
    texte = re.sub(r"<[^>]+>", "", corps_html.replace("<br>", "\n").replace("</p>", "\n"))
    msg.set_content(htmllib.unescape(texte) + "\n\n" + htmllib.unescape(re.sub(r"<[^>]+>", "", reponse_html)))
    cids = {k: make_msgid()[1:-1] for k in (images or {})}
    html_final = _gabarit(agent, corps_html, reponse_html, numero_agent(agent, profil))
    for k, cid in cids.items():
        html_final = html_final.replace(f"cid:{k}", f"cid:{cid}")
    msg.add_alternative(html_final, subtype="html")
    html_part = msg.get_payload()[-1]
    for k, p in (images or {}).items():
        html_part.add_related(Path(p).read_bytes(), maintype="image", subtype="png", cid=f"<{cids[k]}>")
    for p in pieces or []:
        p = Path(p)
        typ = ("video", "mp4") if p.suffix == ".mp4" else ("application", "octet-stream")
        msg.add_attachment(p.read_bytes(), maintype=typ[0], subtype=typ[1], filename=p.name)

    # mémorise l'objet pour reconnaître les réponses
    retenir(sujet, agent, ref)

    if os.getenv("MAIL_DRY_RUN"):
        d = OUTPUT / "mails"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{len(list(d.glob('*.eml'))):03d}.eml").write_bytes(bytes(msg))
        return sujet
    with smtplib.SMTP_SSL(*SMTP) as s:
        s.login(adresse(), os.environ["GMAIL_APP_PASSWORD"])
        s.send_message(msg)
    return sujet


def retenir(sujet: str, agent, ref: dict | None) -> None:
    """Un fichier par mail envoyé (state/mails/<empreinte>.json) : jamais de conflit entre deux GitHub Actions."""
    import hashlib
    cle = normaliser(sujet)
    (state.STATE / "mails").mkdir(exist_ok=True)
    state.save(f"mails/{hashlib.sha1(cle.encode()).hexdigest()[:16]}",
               {"objet": cle, "agent": agent, "ref": ref or {}, "date": state.now_iso()})


def carnet() -> dict:
    """Objets des mails envoyés → {agent, ref} (ancien fichier unique + un fichier par mail)."""
    import json as _j
    c = dict(state.load("mails", {})) if (state.STATE / "mails.json").exists() else {}
    d = state.STATE / "mails"
    if d.is_dir():
        for f in d.glob("*.json"):
            try:
                e = _j.loads(f.read_text(encoding="utf-8"))
                c[e["objet"]] = e
            except Exception:
                pass
    return c


def _texte(msg) -> str:
    if msg.is_multipart():
        parts = [p for p in msg.walk() if p.get_content_type() == "text/plain" and not p.get_filename()]
        if not parts:
            parts = [p for p in msg.walk() if p.get_content_type() == "text/html"]
        if not parts:
            return ""
        p = parts[0]
    else:
        p = msg
    brut = p.get_payload(decode=True) or b""
    t = brut.decode(p.get_content_charset() or "utf-8", errors="replace")
    if p.get_content_type() == "text/html":
        t = htmllib.unescape(re.sub(r"<[^>]+>", "\n", t))
    return t


def sans_citation(texte: str) -> str:
    """Garde seulement ce que tu as écrit (coupe la citation du mail d'origine)."""
    coupe = re.split(r"\n\s*(?:Le .{3,120}a écrit\s*:|On .{3,120}wrote:|-----\s*Original|De\s*:\s|From\s*:\s)", texte, maxsplit=1)[0]
    lignes = [ln for ln in coupe.splitlines() if not ln.strip().startswith(">")]
    return "\n".join(lignes).strip()


def dossier(agent: str) -> str:
    a = str(agent).split(".")[0]
    return f"Decode/Agent {a}" if a.isdigit() else "Decode/Manager"


def _ranger(m, i, msg) -> None:
    """Étiquette « Decode/Agent N » et sort de la boîte de réception, sauf ce qui demande une action
    (vidéo à valider, échecs, token) qui reste AUSSI dans la boîte de réception."""
    sujet = str(make_header(decode_header(msg.get("Subject", ""))))
    lab = dossier(msg.get("X-Decode-Agent", ""))
    try:
        m.create(f'"{lab}"')
    except Exception:
        pass
    labels = [LABEL_AGENTS, lab]
    if any(k in sujet for k in ("Vidéo prête à valider", "Vidéo montée", "Vidéo publiée")):
        labels.append(RENDUS)  # copie dans « Manager - rendus finaux »
        try:
            m.create(f'"{RENDUS}"')
        except Exception:
            pass
    try:
        m.store(i, "+X-GM-LABELS", "(" + " ".join(f'"{x}"' for x in labels) + ")")
        important = any(k in sujet for k in ("à valider", "❌", "Échec", "Token", "⚠"))
        if not important:
            m.store(i, "-X-GM-LABELS", "\\Inbox")
    except Exception as e:
        print(f"rangement impossible : {e}")
        raise


def lire_nouveaux() -> list[dict]:
    """Mails non traités de la boîte du studio (hors mails envoyés par les agents)."""
    out = []
    m = imaplib.IMAP4_SSL(IMAP)
    m.login(adresse(), os.environ["GMAIL_APP_PASSWORD"])
    m.select("INBOX")
    # non lus, ni déjà traités, ni envoyés par un agent (Gmail X-GM-RAW = même syntaxe que la recherche Gmail)
    # à chaque passage : tout mail d'agent encore dans la boîte de réception (lu ou non) est rangé
    bilan = {"ranges": 0, "erreurs": [], "date": state.now_iso()}
    requete = '"in:inbox from:me"' if state.load("rangement_dossiers", {}).get("rendus_v1") else '"from:me"'
    _, tous = m.search(None, "X-GM-RAW", requete)
    for i in tous[0].split()[-400:]:
        try:
            _, data = m.fetch(i, "(BODY.PEEK[HEADER.FIELDS (X-DECODE-AGENT SUBJECT)])")
            h = email.message_from_bytes(data[0][1])
            if h.get("X-Decode-Agent"):
                _ranger(m, i, h)
                bilan["ranges"] += 1
        except Exception as e:
            bilan["erreurs"].append(str(e)[:120])
    state.save("rangement_dossiers", {**bilan, "erreurs": bilan["erreurs"][:5], "rendus_v1": True})
    _, ids = m.search(None, "X-GM-RAW", f'"in:inbox is:unread -label:{LABEL_TRAITE} -label:{LABEL_AGENTS}"')
    for i in ids[0].split():
        _, data = m.fetch(i, "(BODY.PEEK[])")
        msg = email.message_from_bytes(data[0][1])
        if msg.get("X-Decode-Agent"):
            # mail d'un agent : rangé dans le dossier de l'agent (Decode/Agent N, Decode/Manager), il reste « non lu »
            _ranger(m, i, msg)
            continue
        sujet = str(make_header(decode_header(msg.get("Subject", ""))))
        out.append({"uid": i, "objet": sujet, "texte": sans_citation(_texte(msg)), "date": msg.get("Date", ""),
                    "id": msg.get("Message-ID", i.decode())})
        m.store(i, "+FLAGS", "\\Seen")
        try:
            m.store(i, "+X-GM-LABELS", f'"{LABEL_TRAITE}"')
        except Exception:
            pass
    m.logout()
    return out


def fil(texte: str) -> str:
    """Texte brut → HTML lisible."""
    return htmllib.escape(texte).replace("\n", "<br>")
