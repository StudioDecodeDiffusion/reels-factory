"""Côté GitHub Actions (gratuit) : courrier des agents par Gmail, rendu final, publication, statistiques.

  python -m pipeline.github_flow depot <dossier drop/>          nouveaux dépôts de la session Claude → mails
                                                                (les vidéos partent au rendu dans le dépôt public)
  python -m pipeline.github_flow rendre <dossier drop/> <job>   voix + rendu final + mail de validation (agent 7)
  python -m pipeline.github_flow facteur                        lit tes mails (OK / NON / REP / notes « agent N - … »),
                                                                publie ce qui est validé à l'heure prévue
  python -m pipeline.github_flow stats                          stats + commentaires + abonnés (avant les rapports)
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

from . import mail, media_host, state
from .config import OUTPUT, TZ, all_profiles, env, load_profile

API = "https://api.github.com"

R_VALIDATION = ("<b>Aucune action nécessaire : la vidéo part toute seule.</b> Pour intervenir, réponds, <b>première ligne</b> :<br>"
                "• <b>OK</b> → je transmets à l'agent 9, publication à l'heure prévue<br>"
                "• <b>OK MAINTENANT</b> → publication immédiate<br>"
                "• <b>NON</b> + ta raison → vidéo abandonnée, ta raison sert aux prochaines idées<br>"
                "• n'importe quel autre texte → remarque transmise à l'agent 7 (la vidéo reste en attente)<br>"
                "<b>Sans réponse, la vidéo est publiée automatiquement à son créneau</b> (avec miniature et story) ; "
                "réponds NON avant pour l'arrêter.")
R_INFO = "Pas besoin de répondre. Un avis sur ce concept ? Réponds à ce mail : l'agent {n} lira ta remarque."
R_MANAGER = ("Pas besoin de répondre : c'est un point d'avancement. Pour réagir, réponds à ce mail "
             "(ta remarque ira à l'agent concerné) ou écris « agent N° - ta note ».")
R_NOTE = "Réponds simplement à ce mail avec ta remarque : l'agent {n} la lira avant son prochain travail."
R_RAPPORT8 = ("• <b>REP 1 3</b> (ou <b>REP TOUT</b>) → j'envoie les réponses proposées aux commentaires choisis<br>"
              "• n'importe quel autre texte → remarque pour l'agent 9")


# ────────────────────────────────────────────── mémoire des vidéos en cours
def attente(job_id: str):
    return state.load(f"attente/{job_id}", None)


def save_attente(fiche: dict) -> None:
    (state.STATE / "attente").mkdir(exist_ok=True)
    state.save(f"attente/{fiche['id']}", fiche)


def all_attente() -> list[dict]:
    d = state.STATE / "attente"
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(d.glob("*.json"))] if d.exists() else []


def _slot(profile: dict, fiche: dict | None = None) -> str:
    h = (fiche or {}).get("publication_heure", profile["planning"].get("publication_heure", 18))
    return f"aujourd'hui vers {h} h" if datetime.now(TZ).hour < h else f"demain vers {h} h"


def md(texte: str) -> str:
    """Mini-markdown → HTML : ## titres, - puces, **gras**, [lien](url), lignes."""
    out, liste = [], False
    for ln in (texte or "").splitlines():
        s = mail.fil(ln.strip())
        s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
        s = re.sub(r"\[(.+?)\]\((https?://[^)\s]+)\)", r'<a href="\2">\1</a>', s)
        if s.startswith("- ") or s.startswith("• "):
            if not liste:
                out.append("<ul style='padding-left:20px'>")
                liste = True
            out.append(f"<li>{s[2:]}</li>")
            continue
        if liste:
            out.append("</ul>")
            liste = False
        if s.startswith("### "):
            out.append(f"<h4 style='margin:16px 0 6px'>{s[4:]}</h4>")
        elif s.startswith("## "):
            out.append(f"<h3 style='margin:18px 0 8px'>{s[3:]}</h3>")
        elif s:
            out.append(f"<p style='margin:6px 0'>{s}</p>")
    if liste:
        out.append("</ul>")
    return "\n".join(out)


# ────────────────────────────────────────────── dépôts de la session Claude
def depot(drop_dir: str) -> None:
    for d in sorted(Path(drop_dir).iterdir()):
        f = d / "fiche.json"
        if not f.exists():
            continue
        fiche = json.loads(f.read_text(encoding="utf-8"))
        if attente(fiche["id"]):
            continue
        profile = load_profile(fiche["profil"])
        nom = profile["nom_compte"]
        statut = fiche["statut"]

        if statut == "info":  # agent 4 → pour information
            c = fiche.get("concept", {})
            faits = "\n".join(f"- {x.get('fait')} ([source]({x.get('source_url')}))" for x in c.get("faits", []))
            corps = md(f"""Pour info, voici le concept retenu pour la vidéo de cette nuit sur **{nom}**.
## 💡 {fiche.get('titre')}
- **Sujet :** {c.get('sujet', '')}
- **Format :** {c.get('format', '')}
- **Mise en scène :** {c.get('mise_en_scene', '')}
- **Pourquoi :** {fiche.get('justification', '')}
### Faits retenus
{faits or '- (aucun)'}
**Pistes écartées :** {', '.join(x for x in fiche.get('autres', []) if x) or '—'}
## 🔎 Critique du compte et de son audience
{fiche.get('critique') or '—'}
### À tester
""" + "\n".join(f"- {x}" for x in fiche.get("a_tester", [])))
            mail.envoyer(4, f"{nom} · Concept du jour : {fiche.get('titre')}", corps, R_INFO.format(n=4),
                         ref={"type": "info", "job": fiche["id"], "profil": fiche["profil"]})

        elif statut == "rapport":  # rapports des agents 1, 2, 3, 9 (quotidiens) et 10 (hebdo)
            n = int(fiche["agent"])
            images = graphiques(fiche["profil"]) if n == 8 else {}
            corps = md(fiche.get("corps_md", ""))
            if images:
                corps = "".join(f'<p><img src="cid:{k}" style="width:100%;max-width:600px;border-radius:8px"></p>'
                                for k in images) + corps
            rep = (fiche.get("reponses") or [])
            if n == 8 and rep:
                corps += md("## 💬 Réponses proposées aux commentaires\n" + "\n".join(
                    f"- **{i}.** « {str(r.get('commentaire', ''))[:140]} » → {r.get('reponse')}" for i, r in enumerate(rep, 1)))
            # propriétaire (24/10) : plus de mail par agent, le rapport part dans le journal quotidien (digest)
            print(f"rapport de l'agent {n} gardé pour le journal du soir")

        elif statut == "etape":  # point d'avancement du Manager après chaque agent
            mail.envoyer("Manager", f"📍 {fiche.get('titre', 'Avancement')} · {nom}", md(fiche.get("corps_md", "")), R_MANAGER,
                         ref={"type": "manager", "job": fiche["id"], "profil": fiche["profil"], "agent": fiche.get("agent")})

        elif statut == "envoi_videos":  # un mail par vidéo finie, vidéo en pièce jointe
            import tempfile
            for job in fiche.get("jobs", []):
                f = attente(job) or {}
                url = (f.get("media") or {}).get("urls", {}).get("video.mp4")
                if not url:
                    continue
                tmp = Path(tempfile.mkdtemp()) / f"{job}.mp4"
                tmp.write_bytes(requests.get(url, timeout=300).content)
                quand = f.get("publication_le", "")
                mail.envoyer("Manager", f"🎬 Vidéo finie · {nom} · {f.get('titre', '')}",
                             md(f"La vidéo finale est en pièce jointe.\n\n- **Lien :** [{url}]({url})\n- **Publication prévue :** {quand or 'à valider'}"),
                             R_MANAGER, ref={"type": "manager", "job": job, "profil": fiche["profil"]},
                             pieces=[nom_fichier_video(f, tmp)] if tmp.stat().st_size < 24_000_000 else [])

        elif statut == "relance":  # relancer des rendus annulés
            for job in fiche.get("jobs", []):
                _envoyer_au_rendu(job)
            mail.envoyer("Manager", f"⏳ Rendus relancés · {nom} · {len(fiche.get('jobs', []))} vidéo(s)",
                         md("Rendus relancés : " + ", ".join(fiche.get("jobs", []))), R_MANAGER,
                         ref={"type": "manager", "job": fiche["id"], "profil": fiche["profil"]})

        elif statut == "story":  # story immédiate (image fournie par la session)
            png = d / "story.png"
            try:
                h = media_host.upload([png], fiche["id"])
                from .instagram import IG
                IG(profile).publish_story(h["urls"]["story.png"])
                media_host.cleanup(h)
                txt, etat = "📣 La story est en ligne.", "✅ Story publiée"
            except BaseException as e:
                txt, etat = f"⚠️ Story non publiée : {str(e)[:300]}", "❌ Échec story"
            mail.envoyer("Manager", f"{etat} · {nom} · {fiche.get('titre', '')}", md(txt), R_MANAGER,
                         ref={"type": "manager", "job": fiche["id"], "profil": fiche["profil"], "agent": 9})

        elif statut == "archive":  # archiver une vidéo déjà publiée
            _archiver(fiche, d)
            continue

        elif statut == "pret":  # vidéo finale déjà montée (ex. retouche du son) : hébergement + publication directe
            fiche["media"] = media_host.upload([d / "video.mp4"] + ([d / "couverture.png"] if (d / "couverture.png").exists() else []),
                                               fiche["id"])
            fiche["statut"] = "approuvee"
            save_attente(fiche)
            if fiche.get("publier_maintenant"):
                _publier(fiche, profile)
            continue

        elif statut == "abandonnee":
            mail.envoyer(7, f"{nom} · Pas de vidéo cette nuit", md(f"Aucune vidéo n'a été produite pour **{nom}**.\n\n"
                                                                  f"**Raison :** {fiche.get('raison')}"),
                         R_NOTE.format(n=7), ref={"type": "abandon", "job": fiche["id"], "profil": fiche["profil"]})

        elif statut == "a_valider":
            if os.getenv("RENDU_PUBLIC") == "1":
                _envoyer_au_rendu(fiche["id"])
                fiche["statut"] = "rendu_en_cours"
                mail.envoyer("Manager", f"⏳ Rendu lancé · {nom} · {fiche['titre']}",
                             md("La session de nuit a terminé (agents 4, 5, 6, 8 et 7). **GitHub ajoute maintenant les voix et la "
                                "musique** et monte la vidéo finale (≈ 20 min). L'agent 7 t'enverra ensuite la vidéo à valider."),
                             R_MANAGER, ref={"type": "manager", "job": fiche["id"], "profil": fiche["profil"]})
            else:
                rendre_un(d, fiche)
                continue
        save_attente(fiche)


def _envoyer_au_rendu(job: str) -> None:
    """Le rendu (voix + vidéo, ~20 min) tourne dans le dépôt PUBLIC reels-media : minutes illimitées."""
    r = requests.post(f"{API}/repos/{env('MEDIA_REPO')}/dispatches", timeout=60,
                      headers={"Authorization": f"Bearer {env('GH_PAT')}", "Accept": "application/vnd.github+json"},
                      json={"event_type": "rendu", "client_payload": {"job": job}})
    r.raise_for_status()
    print(f"{job} envoyé au rendu public")


def rendre(drop_dir: str, job: str) -> None:
    d = Path(drop_dir) / job
    rendre_un(d, json.loads((d / "fiche.json").read_text(encoding="utf-8")))


def rendre_un(d: Path, fiche: dict) -> None:
    """Agent 8 (rendu final avec voix) puis agent 7 : mail de validation ; agent 6 : son message."""
    profile = load_profile(fiche["profil"])
    nom = profile["nom_compte"]
    _sonoriser(d, fiche, profile)
    media = media_host.upload([d / "video.mp4", d / "apercu.png"] + ([d / "couverture.png"] if (d / "couverture.png").exists() else []),
                              fiche["id"])
    v = media["urls"]["video.mp4"]
    crit = fiche.get("critique", {}) or fiche.get("verification", {})
    proj = crit.get("projection", {})
    sources = "\n".join(f"- [{s}]({s})" for s in fiche.get("sources", [])) or "- (aucune)"
    corps = (f'<p><img src="cid:apercu" style="width:100%;border-radius:8px;border:2px solid #14131C"></p>'
             f'<p style="text-align:center;font-size:18px"><a href="{v}"><b>▶️ Regarder la vidéo ({fiche.get("duree_s", "?")} s)</b></a></p>'
             + md(f"""## ✅ Vidéo prête : {fiche['titre']}
Publication **automatique {_slot(profile, fiche)}** sur **{nom}** (story d'annonce 4 h avant, story « elle est sortie » à la publication). Rien à faire.
## 🧐 Mon évaluation
- **Verdict :** {crit.get('decision', '?')} — **{crit.get('score_global', '?')}/10**
- {crit.get('resume_pour_le_proprietaire', '')}
- **Cohérence et qualité :** {crit.get('coherence', crit.get('controles', {}).get('images', '—'))}
## 📈 Projection (avec l'agent 3)
- **Potentiel :** {proj.get('potentiel', '—')}
- **Vues attendues :** {proj.get('vues_estimees', '—')}
- **Audience visée :** {proj.get('audience', '—')}
- **Pourquoi :** {proj.get('raisonnement', '—')}
## 📝 Légende prévue
{fiche['legende']}
## 🔗 Sources
{sources}"""))
    piece = [nom_fichier_video(fiche, d / "video.mp4")] if (d / "video.mp4").stat().st_size < 18_000_000 else []
    mail.envoyer(7, f"{nom} · Vidéo prête, sortie auto : {fiche['titre']}", corps, R_VALIDATION,
                 ref={"type": "validation", "job": fiche["id"], "profil": fiche["profil"]},
                 images={"apercu": d / "apercu.png"}, pieces=piece)
    if fiche.get("da_message"):
        mail.envoyer(6, f"{nom} · Mes choix pour « {fiche['titre']} »", md(fiche["da_message"]), R_NOTE.format(n=6),
                     ref={"type": "da", "job": fiche["id"], "profil": fiche["profil"]})
    fiche.update(statut="a_valider", media=media, envoyee=state.now_iso())
    save_attente(fiche)


def _sonoriser(d: Path, fiche: dict, profile: dict) -> None:
    """Ajoute les voix : synthèse, recalage des durées, rendu final (remplace la version muette)."""
    spec_path = d / "7_spec.json"
    if not profile.get("voix", {}).get("active") or not spec_path.exists():
        return
    from .config import VIDEO
    from .render import contact_sheet, frames_per_scene, render
    from .voix import sonoriser
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if not any(sc.get("voix") or sc.get("dialogue") for sc in spec["scenes"]):
        return
    spec = sonoriser(spec, fiche["id"], profile, VIDEO / "public")
    _manager(fiche, "🎙️ Voix générées", f"Les {sum(len(sc.get('dialogue') or []) for sc in spec['scenes'])} répliques de Lou et Déco sont "
             f"enregistrées ({round(sum(sc['duration'] for sc in spec['scenes']))} s). Montage final en cours (≈ 5 min).")
    render(spec, d / "video.mp4")
    from .musique import ajouter  # musique de fond sous les voix (choisie par l'agent 6)
    ajouter(d / "video.mp4", spec.get("musique") or profile.get("musique", "curieux"), sum(map(ord, fiche["id"])),
            scenes=spec["scenes"])
    contact_sheet(frames_per_scene(spec, d / "video.mp4"), d / "apercu.png")
    _manager(fiche, "🎬 Vidéo montée", "Voix, musique et effets sont mixés. Hébergement de la vidéo puis mail de validation de l'agent 7.")
    fiche["duree_s"] = round(sum(sc["duration"] for sc in spec["scenes"]), 1)
    fiche["voix"] = profile["voix"].get("narrateur") or profile["voix"].get("id")


# ────────────────────────────────────────────── le facteur : tes mails
def note(agent: int, objet: str, texte: str, profil: str | None = None) -> None:
    """Range une note pour un agent ; il la lit avant son prochain travail."""
    (state.STATE / "messages").mkdir(exist_ok=True)
    fil = state.load(f"messages/agent_{agent}", [])
    if not profil:
        t = f"{objet} {texte}".lower()
        profil = "tous"
    fil.append({"id": f"{agent}-{len(fil) + 1}-{datetime.now(TZ):%m%d%H%M}", "date": state.now_iso(),
                "objet": objet, "texte": texte, "profil": profil, "traite": False})
    state.save(f"messages/agent_{agent}", fil[-200:])


def facteur() -> None:
    lus = []
    if os.getenv("GMAIL_APP_PASSWORD"):
        try:
            lus = mail.lire_nouveaux()
        except Exception as e:
            print(f"lecture Gmail impossible : {e}")
    carnet = mail.carnet()
    for m in lus:
        cle = mail.normaliser(m["objet"])
        texte = m["texte"].strip()
        lien = carnet.get(cle)
        if lien:  # réponse à un mail d'agent
            n, ref = lien["agent"], lien.get("ref", {})
            n = int(n) if str(n).isdigit() else n
            if ref.get("type") == "validation":
                _validation(ref["job"], texte)
            elif ref.get("type") == "test" and texte:
                mail.envoyer(9, "Bien reçu !", md(f"Ta réponse est arrivée ✅ La messagerie marche dans les deux sens.\n\n> {texte[:400]}"),
                             R_NOTE.format(n=9))
            elif ref.get("type") == "rapport8" and re.match(r"^\s*REP\b", texte, re.I):
                _reponses_commentaires(ref, texte)
            elif texte:
                n = int(ref.get("agent") or 7) if not str(n).isdigit() else n
                note(n, m["objet"], texte, ref.get("profil"))
                mail.envoyer(n, "Remarque bien reçue", md(f"Merci ! J'ai bien noté :\n\n> {texte[:600]}\n\n"
                                                          "Je l'appliquerai dès mon prochain travail."), R_NOTE.format(n=n))
            continue
        mq = re.match(r"^\s*quota\s*[-–—:]?\s*(\d{1,3})\s*%?\s*[ /,;-]+\s*(\d{1,3})\s*%?", m["objet"], re.I)
        if mq:
            q = {"date": datetime.now(TZ).strftime("%Y-%m-%d"), "heure": datetime.now(TZ).strftime("%H:%M"),
                 "jour": int(mq.group(1)), "semaine": int(mq.group(2))}
            state.save("quota", q)
            mail.envoyer("Manager", f"📍 Quota noté : jour {q['jour']} % · semaine {q['semaine']} %",
                         md("Bien reçu. À 20 h, je prends de l'avance seulement si le jour est **sous 25 %** et la semaine "
                            "sous la part de semaine écoulée (vendredi 23 h → vendredi 23 h). Au-dessus de 75 % : "
                            "uniquement les tâches programmées."), R_MANAGER, ref={"type": "manager", "profil": "actu"})
            continue
        mm = re.match(r"^\s*agent\s*(?:n\s*[°o]?\s*)?(\d+)(?:[.,](\d+))?\s*[-–—:]?\s*(.*)$", m["objet"], re.I)
        if mm and 1 <= int(mm.group(1)) <= 13:
            n, sous = int(mm.group(1)), mm.group(2)
            profil = next((p for p in all_profiles() if str(load_profile(p).get("numero")) == sous), None) if sous else "tous"
            sujet_note = mm.group(3).strip()
            note(n, sujet_note, texte, profil or "tous")
            mail.envoyer(n, f"Note reçue : {sujet_note[:60]}",
                         md(f"Bien reçu ✅\n\n**Ta note :** {sujet_note}\n\n{texte[:800]}\n\n"
                            "Je l'appliquerai dès mon prochain travail et te dirai ce que j'en ai fait."),
                         R_NOTE.format(n=n), ref={"profil": profil} if profil not in (None, "tous") else None)
    ecg()
    publier_ce_qui_est_du()
    releve_horaire()


def _validation(job: str, texte: str) -> None:
    fiche = attente(job)
    if not fiche:
        return
    profile = load_profile(fiche["profil"])
    nom = profile["nom_compte"]
    lignes = [ln.strip() for ln in texte.splitlines() if ln.strip()]
    premiere = lignes[0] if lignes else ""
    m = re.match(r"^(OK|NON)\b[\s:!.,-]*(.*)$", premiere, re.I)
    if not m:
        note(9, f"Remarque sur « {fiche['titre']} »", texte, fiche["profil"])
        mail.envoyer(7, f"{nom} · Remarque notée sur « {fiche['titre']} »",
                     md(f"J'ai noté ta remarque :\n\n> {texte[:600]}\n\nLa vidéo **reste en attente** de ton OK ou NON."),
                     R_VALIDATION, ref={"type": "validation", "job": job, "profil": fiche["profil"]})
        return
    if fiche["statut"] not in ("a_valider", "approuvee"):
        return
    cmd, reste = m.group(1).upper(), m.group(2).strip()
    if cmd == "NON":
        raison = " ".join([reste] + lignes[1:]).strip()
        fiche.update(statut="refusee", raison=raison)
        media_host.cleanup(fiche.get("media"))
        refus = state.load(f"refus_{fiche['profil']}", [])
        refus.append({"titre": fiche["titre"], "raison": raison, "date": fiche["cree"][:10]})
        state.save(f"refus_{fiche['profil']}", refus[-50:])
        save_attente(fiche)
        mail.envoyer(7, f"{nom} · Vidéo abandonnée : {fiche['titre']}",
                     md(f"C'est noté, la vidéo est abandonnée.\n\n**Ta raison :** {raison or '(non précisée)'}\n\n"
                        "Les agents 3 et 4 en tiendront compte pour les prochaines idées."), R_NOTE.format(n=7))
        return
    fiche["statut"] = "approuvee"
    save_attente(fiche)
    if "MAINTENANT" in reste.upper():
        _publier(fiche, profile)
    else:
        mail.envoyer(7, f"{nom} · Validée, transmise à l'agent 9 : {fiche['titre']}",
                     md(f"Merci ! Je transmets à l'**agent 9**, qui publiera **{_slot(profile, fiche)}**."),
                     R_NOTE.format(n=7))


def _reponses_commentaires(ref: dict, texte: str) -> None:
    from .instagram import IG
    fiche = attente(ref["job"]) or {}
    rep = fiche.get("reponses") or []
    profile = load_profile(ref["profil"])
    if not rep:
        return
    idx = range(1, len(rep) + 1) if re.search(r"TOUT", texte, re.I) else [int(x) for x in re.findall(r"\d+", texte.splitlines()[0])]
    ig, ok, ko = IG(profile), [], []
    for i in idx:
        if 1 <= i <= len(rep) and not rep[i - 1].get("envoyee"):
            try:
                ig.reply(rep[i - 1]["comment_id"], rep[i - 1]["reponse"])
                rep[i - 1]["envoyee"] = True
                ok.append(str(i))
            except Exception as e:
                ko.append(f"{i} ({str(e)[:120]})")
    save_attente(fiche)
    mail.envoyer(9, f"{profile['nom_compte']} · Réponses aux commentaires envoyées",
                 md(f"Réponses envoyées : **{', '.join(ok) or 'aucune'}**" + (f"\n\nÉchecs : {'; '.join(ko)}" if ko else "")),
                 R_NOTE.format(n=9))


# ────────────────────────────────────────────── publication (agent 9)
def _manager(fiche: dict, titre: str, texte: str) -> None:
    """Point d'avancement court (jamais bloquant)."""
    try:
        nom = load_profile(fiche["profil"])["nom_compte"]
        mail.envoyer("Manager", f"{titre} · {nom} · {fiche.get('titre', '')}", md(texte), R_MANAGER,
                     ref={"type": "manager", "job": fiche["id"], "profil": fiche["profil"]})
    except BaseException as e:
        print(f"point d'avancement non envoyé : {e}")


def _publier(fiche: dict, profile: dict) -> None:
    from .instagram import IG
    nom = profile["nom_compte"]
    _manager(fiche, "⏳ Publication en cours", "J'envoie la vidéo et sa miniature à Instagram (traitement 1 à 5 min), "
             "puis la story. Prochain mail : « Vidéo publiée » avec le lien.")
    if fiche.get("plateforme") == "tiktok":  # vidéo réservée à TikTok : brouillon seulement, pas d'Instagram
        _tiktok(fiche)
        fiche.update(statut="publiee", publiee=state.now_iso(), tiktok_fait=True)
        save_attente(fiche)
        media_host.cleanup(fiche["media"])
        return
    try:  # garde-fou : média déjà supprimé = vidéo déjà publiée par un passage concurrent
        if requests.head(fiche["media"]["urls"]["video.mp4"], allow_redirects=True, timeout=30).status_code == 404:
            print(f"{fiche['id']} : média absent (déjà publié ?) : rien à faire")
            return
    except Exception:
        pass
    try:
        cover = fiche["media"]["urls"].get("couverture.png")
        neuve = state.STATE / "couvertures" / f"{fiche['id']}.png"
        if neuve.exists():  # miniature refaite après le rendu
            hc = media_host.upload([neuve], f"{fiche['id']}-couv")
            cover = hc["urls"][neuve.name]
        info = IG(profile).publish_reel(fiche["media"]["urls"]["video.mp4"], fiche["legende"], cover_url=cover)
    except BaseException as e:
        fiche["erreur"] = str(e)[:500]
        fiche["erreurs"] = fiche.get("erreurs", 0) + 1
        save_attente(fiche)
        mail.envoyer("Manager", f"❌ Échec publication · {nom} · {fiche['titre']}",
                     md(f"La publication a échoué :\n\n{str(e)[:500]}\n\nJe réessaierai à la prochaine heure."),
                     R_NOTE.format(n=9))
        return
    fiche.update(statut="publiee", media_id=info["id"], permalink=info.get("permalink"), publiee=state.now_iso())
    save_attente(fiche)
    _archiver(fiche)
    h_tt = (profile.get("tiktok") or {}).get("heure")
    if h_tt:  # le compte publie sur TikTok à une autre heure (propriétaire 25/10) : envoi au passage du facteur
        fiche["tiktok_le"] = datetime.now(TZ).strftime(f"%Y-%m-%dT{h_tt}%z")
        fiche["tiktok_le"] = fiche["tiktok_le"][:-2] + ":" + fiche["tiktok_le"][-2:]
        save_attente(fiche)
    else:
        _tiktok(fiche)
        media_host.cleanup(fiche["media"])
    story = _publier_story(fiche, profile)
    etat_story = "+ story publiée" if "publiée aussi" in story else ("(échec story)" if "non publiée" in story else "")
    if fiche.get("son_tendance"):
        st = fiche["son_tendance"]
        story += (f"\n\n🎵 **À faire dans l'app** : ajoute le son tendance « {st.get('nom', '')} » ({st.get('createur', '')}) "
                  "au Reel (Modifier → Audio), volume bas. Pourquoi : " + str(st.get("pourquoi", "")))
    mail.envoyer("Manager", f"✅ Vidéo publiée {etat_story} · {nom} · {fiche['titre']}",
                 md(f"🎉 **La vidéo est en ligne** sur {profile.get('instagram') or nom} : "
                    f"[{info.get('permalink', '')}]({info.get('permalink', '')})\n\n- {story}\n"
                    "- **Suite :** l'agent 9 suit les vues et les commentaires (rapport demain à 16 h 30)."),
                 R_MANAGER, ref={"type": "manager", "job": fiche["id"], "profil": fiche["profil"], "agent": 9})
    mail.envoyer(9, f"{nom} · Publiée : {fiche['titre']}",
                 md(f"✅ La vidéo est en ligne : [{info.get('permalink', '')}]({info.get('permalink', '')})\n\n"
                    f"{story}\n\nJe surveille les commentaires et te fais le bilan dans mon rapport quotidien."),
                 R_NOTE.format(n=9), ref={"type": "publication", "job": fiche["id"], "profil": fiche["profil"]})


def _archiver(fiche: dict, dossier: Path | None = None) -> None:
    """Archive privée : vidéo finale, miniature, story et sources (rien d'autre)."""
    import tempfile
    try:
        tmp = Path(tempfile.mkdtemp())
        import unicodedata
        compte = (load_profile(fiche["profil"]).get("instagram") or fiche["profil"]).lstrip("@")
        titre = unicodedata.normalize("NFKD", fiche.get("titre") or "video").encode("ascii", "ignore").decode()
        titre = re.sub(r"[^A-Za-z0-9]+", "-", titre).strip("-").lower()[:60]
        base = f"{fiche['cree'][:10]}_{compte}_{titre}"  # date _ compte _ titre
        fichiers = {}
        urls = (fiche.get("media") or {}).get("urls", {})
        for nom, cible in (("video.mp4", "video.mp4"), ("couverture.png", "miniature.png")):
            src = (dossier / nom) if dossier and (dossier / nom).exists() else None
            if not src and urls.get(nom):
                src = tmp / nom
                src.write_bytes(requests.get(urls[nom], timeout=300).content)
            if src:
                fichiers[f"{base}_{cible}"] = src
        story = (dossier / "story.png") if dossier and (dossier / "story.png").exists() else state.STATE / "stories" / f"{fiche['id']}.png"
        if story.exists():
            fichiers[f"{base}_story.png"] = story
        src_txt = tmp / "sources.txt"
        src_txt.write_text(f"{fiche.get('titre', '')}\nPublié : {fiche.get('permalink', '')}\n\nSources :\n"
                           + "\n".join(fiche.get("sources", [])) + "\n", encoding="utf-8")
        fichiers[f"{base}_sources.txt"] = src_txt
        lien = media_host.archiver(fichiers, fiche["cree"][:7], remplacer=fiche.get("remplace_noms"))
        fiche["archive"] = lien
        save_attente(fiche)
        _manager(fiche, "🗄️ Archivée", f"Vidéo finale, miniature, story et sources rangées dans l'archive privée : [{lien}]({lien})")
    except BaseException as e:
        _manager(fiche, "❌ Échec archive", f"L'archivage a échoué ({str(e)[:300]}). La publication, elle, est faite.")


def _publier_story(fiche: dict, profile: dict) -> str:
    """Story « nouvelle vidéo » (state/stories/<job>.png), publiée juste après le Reel."""
    from .instagram import IG
    png = state.STATE / "stories" / f"{fiche['id']}.png"
    if not png.exists():
        return "(pas de story prévue pour cette vidéo)"
    try:
        h = media_host.upload([png], f"{fiche['id']}-story")
        IG(profile).publish_story(h["urls"][png.name])
        media_host.cleanup(h)
        fiche["story"] = "publiee"
        save_attente(fiche)
        return "📣 La story « nouvelle vidéo » est publiée aussi."
    except BaseException as e:
        return f"⚠️ Story non publiée : {str(e)[:300]}"


def _stories_programmees(now) -> None:
    """state/stories_programmees.json : [{"image": "stories_annonce/x.png", "quand": ISO, "profil", "titre"}]"""
    from .instagram import IG
    liste = state.load("stories_programmees", [])
    reste = []
    for st in liste:
        if st.get("faite") or datetime.fromisoformat(st["quand"]) > now:
            reste.append(st)
            continue
        prof = load_profile(st["profil"])
        png = state.STATE / st["image"]
        try:
            h = media_host.upload([png], f"annonce-{png.stem}")
            IG(prof).publish_story(h["urls"][png.name])
            media_host.cleanup(h)
            etat, txt = "✅ Story publiée", "📣 Story d'annonce en ligne."
        except BaseException as e:
            etat, txt = "❌ Échec story", f"Story d'annonce non publiée : {str(e)[:300]}"
        st["faite"] = state.now_iso()
        reste.append(st)
        mail.envoyer("Manager", f"{etat} · {prof['nom_compte']} · {st.get('titre', '')}", md(txt), R_MANAGER,
                     ref={"type": "manager", "profil": st["profil"]})
    state.save("stories_programmees", reste[-60:])


def ecg() -> None:
    """Électrocardiogramme du pipeline (à chaque passage du facteur) : répare tout seul les états bloqués.
    1. Publication faite mais non enregistrée (passages concurrents) → retrouvée dans les derniers Reels et notée.
    2. Rendu bloqué plus de 50 min → relancé. Tout est journalisé dans state/ecg.json."""
    from .instagram import IG
    now = datetime.now(timezone.utc)
    journal = []
    d = state.STATE / "attente"
    fiches = [json.loads(f.read_text(encoding="utf-8")) for f in d.glob("*.json")] if d.exists() else []
    a_verifier = [f for f in fiches if f.get("statut") in ("approuvee", "a_valider") and f.get("media")
                  and f.get("publication_le") and datetime.fromisoformat(f["publication_le"]) < now - timedelta(minutes=10)]
    if a_verifier:
        try:
            recents = IG(load_profile("actu")).recent_media(8)
        except BaseException as e:
            recents = []
            journal.append(f"lecture Instagram impossible : {str(e)[:80]}")
        for f in a_verifier:
            debut = re.sub(r"\s+", " ", (f.get("legende") or ""))[:50]
            m = next((r for r in recents if debut and re.sub(r"\s+", " ", r.get("caption") or "").startswith(debut)), None)
            if m:
                f.update(statut="publiee", permalink=m.get("permalink"), media_id=m.get("id"), publiee=m.get("timestamp"))
                save_attente(f)
                journal.append(f"{f['id']} : publication retrouvée et enregistrée ({m.get('permalink')})")
    for f in fiches:
        if f.get("statut") == "rendu_en_cours" and datetime.fromisoformat(f.get("envoyee", f["cree"])) < now - timedelta(minutes=50) \
                and f.get("relances", 0) < 2:
            f["relances"] = f.get("relances", 0) + 1
            f["envoyee"] = now.isoformat(timespec="seconds")
            save_attente(f)
            try:
                _envoyer_au_rendu(f["id"])
                journal.append(f"{f['id']} : rendu bloqué, relancé")
            except BaseException as e:
                journal.append(f"{f['id']} : relance impossible ({str(e)[:80]})")
    if journal:
        hist = state.load("ecg", [])
        hist += [{"date": now.isoformat(timespec="seconds"), "evenement": j} for j in journal]
        state.save("ecg", hist[-200:])
        print("\n".join(journal))


def publier_ce_qui_est_du() -> None:
    now = datetime.now(TZ)
    demande = state.load("publier_maintenant", {})
    for job in demande.get("supprimer", []):  # ancien post à retirer (demande du propriétaire)
        f = attente(job)
        if f and f.get("media_id"):
            from .instagram import IG
            prof = load_profile(f["profil"])
            # Instagram ne permet pas aux outils externes de supprimer un post : on le signale simplement
            txt = (f"Le nouveau post est publié. Instagram ne permet pas aux outils de supprimer un post : "
                   f"retire l'ancien toi-même (ouvre-le puis ⋯ → Supprimer) : {f.get('permalink', '')}")
            save_attente(f)
            mail.envoyer("Manager", f"🗑️ Ancien post à supprimer · {prof['nom_compte']}", md(txt), R_MANAGER,
                         ref={"type": "manager", "job": job, "profil": f["profil"], "agent": 9})
    for job in demande.get("jobs", []):
        f = attente(job)
        if f and f["statut"] in ("a_valider", "approuvee"):
            f["statut"] = "approuvee"
            save_attente(f)
            _publier(f, load_profile(f["profil"]))
    state.save("publier_maintenant", {"jobs": [], "supprimer": []})
    for fiche in all_attente():
        profile = load_profile(fiche["profil"])
        p = profile["planning"]
        quand = fiche.get("publication_le")  # date + heure précises (ISO), prioritaires sur l'heure
        h_pub = fiche.get("publication_heure", p.get("publication_heure", 18))
        m_pub = fiche.get("publication_minute", 0) if "publication_heure" in fiche else p.get("publication_minute", 0)
        pret = (datetime.fromisoformat(quand) <= now) if quand else (now.hour, now.minute) >= (h_pub, m_pub)
        if fiche["statut"] == "approuvee" and pret \
                and now.isoweekday() in p.get("publication_jours", range(1, 8)) and fiche.get("erreurs", 0) < 3:
            _publier(fiche, profile)
        elif fiche["statut"] == "a_valider" and quand and pret and p.get("auto_publication") and fiche.get("erreurs", 0) < 3:
            # sans réponse du propriétaire : publiée automatiquement à son créneau (il peut dire NON avant)
            fiche.update(statut="approuvee", valide_par="automatique (sans réponse)")
            save_attente(fiche)
            _publier(fiche, profile)
        elif fiche["statut"] == "a_valider" and not (quand and p.get("auto_publication")) and \
                datetime.fromisoformat(fiche.get("envoyee", fiche["cree"])) < datetime.now(timezone.utc) - timedelta(hours=36):
            fiche["statut"] = "expiree"
            media_host.cleanup(fiche.get("media"))
            save_attente(fiche)
            mail.envoyer(7, f"{profile['nom_compte']} · Vidéo expirée : {fiche['titre']}",
                         md("Pas de réponse sous 36 h : la vidéo est abandonnée."), R_NOTE.format(n=7))
    for fiche in all_attente():  # brouillons TikTok programmés à l'heure TikTok du compte
        if fiche.get("statut") == "publiee" and fiche.get("tiktok_le") and not fiche.get("tiktok_fait") \
                and datetime.fromisoformat(fiche["tiktok_le"]) <= now:
            fiche["tiktok_fait"] = True
            save_attente(fiche)
            _tiktok(fiche)
            media_host.cleanup(fiche.get("media"))
    _stories_programmees(now)
    limite = datetime.now(timezone.utc) - timedelta(days=60)
    for fiche in all_attente():
        if fiche["statut"] in ("publiee", "refusee", "expiree", "abandonnee", "info", "rapport") and \
                datetime.fromisoformat(fiche["cree"]) < limite:
            (state.STATE / "attente" / f"{fiche['id']}.json").unlink(missing_ok=True)


# ────────────────────────────────────────────── statistiques, abonnés, graphiques
def stats() -> None:
    from .instagram import IG
    for pid in all_profiles():
        profile = load_profile(pid)
        if not os.getenv(profile["instagram_secret"]):
            print(f"{pid} : pas de token, ignoré")
            continue
        try:
            ig = IG(profile)
            try:
                me = ig.username()
            except BaseException as e:
                if "190" in str(e) or "access token" in str(e).lower():
                    mail.envoyer("Manager", f"❌ Token Instagram à refaire · {profile['nom_compte']}",
                                 md("Instagram refuse le token (mot de passe changé ou session expirée) : **aucune publication "
                                    "ne pourra partir**.\n\nÀ faire (2 min) : developers.facebook.com → ton app → Cas "
                                    "d'utilisation → Personnaliser → Configuration de l'API avec la connexion Instagram → "
                                    f"**Générer le token** (ligne du compte) → GitHub reels-factory → Settings → Secrets → "
                                    f"**{profile['instagram_secret']}** → ✏️ → coller → Update secret."), R_MANAGER,
                                 ref={"type": "manager", "profil": pid})
                raise
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
            try:
                prof = ig._get("me", fields="followers_count,media_count")
                hist = state.load(f"abonnes_{pid}", [])
                hist = [h for h in hist if h["date"] != datetime.now(TZ).strftime("%Y-%m-%d")]
                hist.append({"date": datetime.now(TZ).strftime("%Y-%m-%d"), "abonnes": prof.get("followers_count", 0),
                             "publications": prof.get("media_count", 0)})
                state.save(f"abonnes_{pid}", hist[-365:])
            except Exception as e:
                print(f"{pid} : abonnés indisponibles ({e})")
            state.save(f"stats_{pid}", {"maj": state.now_iso(), "posts": posts,
                                        "recommandations": old.get("recommandations", [])})
            _suivi(ig, pid, posts)
            pending = state.load(f"commentaires_{pid}", [])
            state.save(f"commentaires_{pid}", (pending + new)[-60:])
            state.save(f"commentaires_vus_{pid}", sorted(seen)[-3000:])
            print(f"{pid} : {len(posts)} posts, {len(new)} nouveaux commentaires")
        except Exception as e:
            print(f"{pid} : erreur {e}")


def _tiktok(fiche: dict) -> None:
    """Même vidéo publiée sur le TikTok du compte (s'il est connecté) ; n'empêche jamais Instagram."""
    if not os.getenv("TIKTOK_CLIENT_KEY") or fiche["profil"] not in state.load("tiktok", {}):
        return
    from . import tiktok
    try:
        try:
            r = tiktok.publier(fiche["profil"], fiche["media"]["urls"]["video.mp4"], fiche.get("legende", ""))
        except RuntimeError as e:  # app pas encore validée par TikTok et compte public : seul le brouillon passe
            print(f"TikTok direct refusé ({e}) : envoi en brouillon")
            r = {"publish_id": tiktok.brouillon(fiche["profil"], fiche["media"]["urls"]["video.mp4"]), "visibilite": "BROUILLON",
                 "raison": str(e)[:200]}
        fiche["tiktok"] = r
        save_attente(fiche)
        if r.get("visibilite") != "PUBLIC_TO_EVERYONE":  # seule action restante pour le propriétaire
            mail.envoyer(9, f"🎵 TikTok · à finaliser : {fiche['titre']}",
                         md("Tant que TikTok n'a pas validé l'app, il refuse la publication publique automatique. "
                            + ("La vidéo est **sur ton profil, en privé** : ouvre-la → ⋯ → Confidentialité → **Tout le monde**."
                               if r.get("visibilite") == "SELF_ONLY" else
                               "La vidéo est dans l'**appli TikTok du téléphone** : Boîte de réception → notifications système "
                               "(ou Profil → Brouillons). Colle la légende puis Publier :")
                            + f"\n\n```\n{fiche.get('legende', '')}\n```"),
                         R_NOTE.format(n=9), ref={"type": "tiktok", "profil": fiche["profil"]})
    except Exception as e:
        print(f"TikTok : {e}")
        fiche["tiktok"] = {"erreur": str(e)[:300]}
        save_attente(fiche)
        mail.envoyer(9, f"❌ TikTok · envoi impossible : {fiche['titre']}", md(f"Instagram n'est pas touché, TikTok non publié :\n\n{str(e)[:400]}"),
                     R_NOTE.format(n=9), ref={"type": "tiktok", "profil": fiche["profil"]})


def republier(job: str, profil: str, plateforme: str = "instagram") -> None:
    """Republie une vidéo déjà archivée sur un autre compte (Instagram, ou brouillon TikTok seul)."""
    import tempfile, unicodedata
    src = attente(job)
    if not src:
        raise SystemExit(f"{job} introuvable")
    compte = (load_profile(src["profil"]).get("instagram") or src["profil"]).lstrip("@")
    titre = unicodedata.normalize("NFKD", src.get("titre") or "video").encode("ascii", "ignore").decode()
    titre = re.sub(r"[^A-Za-z0-9]+", "-", titre).strip("-").lower()[:60]
    nom = f"{src['cree'][:10]}_{compte}_{titre}_video.mp4"
    repo = os.getenv("GITHUB_REPOSITORY") or "StudioDecodeDiffusion/reels-factory"
    h = {"Authorization": f"Bearer {os.environ['GH_PAT'] if os.getenv('GH_PAT') else os.environ['GITHUB_TOKEN']}"}
    rel = requests.get(f"https://api.github.com/repos/{repo}/releases/tags/archive-{src['cree'][:7]}", headers=h, timeout=60).json()
    asset = next(a for a in rel["assets"] if a["name"] == nom)
    tmp = Path(tempfile.mkdtemp()) / "video.mp4"
    tmp.write_bytes(requests.get(asset["url"], headers={**h, "Accept": "application/octet-stream"}, timeout=300).content)
    nouveau = dict(src, id=f"{profil}-{datetime.now(TZ):%Y%m%d-%H%M}-repub", profil=profil, statut="approuvee",
                   publication_le=datetime.now(TZ).isoformat(timespec="minutes"), plateforme=plateforme if plateforme == "tiktok" else None,
                   cree=state.now_iso(), reprise_de=job)
    for k in ("permalink", "media_id", "publiee", "archive", "tiktok_le", "tiktok_fait", "erreur", "erreurs"):
        nouveau.pop(k, None)
    nouveau["media"] = media_host.upload([tmp], nouveau["id"])
    save_attente(nouveau)
    _publier(nouveau, load_profile(profil))
    print(f"{job} republiée sur {profil} ({plateforme}) : {attente(nouveau['id']).get('permalink') or 'brouillon TikTok'}")


def tiktok_connexion() -> None:
    """Sans code : affiche le lien d'autorisation. Avec code : enregistre la connexion du compte."""
    from . import tiktok
    compte, code = os.getenv("TIKTOK_COMPTE", "actu"), os.getenv("TIKTOK_CODE", "").strip()
    resume = os.getenv("GITHUB_STEP_SUMMARY")
    if not code:
        txt = (f"### 1. Ouvre ce lien, connecte-toi au TikTok du compte « {compte} » et clique sur Autoriser\n\n"
               f"{tiktok.lien(compte)}\n\n### 2. Copie le code affiché, puis relance ce workflow avec le code (dans les 5 min)")
    else:
        u = tiktok.connecter(compte, code)
        txt = f"### ✅ TikTok connecté : {u.get('display_name', '')} (@{u.get('username', '?')}), {u.get('follower_count', 0)} abonnés"
    print(txt)
    if resume:
        Path(resume).write_text(txt, encoding="utf-8")


def releve_horaire() -> None:
    """Agent 3 : vues de chaque vidéo + abonnés, une fois par heure, pendant le passage du facteur (aucune minute
    GitHub ni aucun jeton en plus). → state/horaire_<pid>.json, puis classeur Excel régénéré."""
    from .instagram import IG
    from .suivi_excel import construire
    h = datetime.now(TZ).strftime("%Y-%m-%d %H:00")
    for pid in all_profiles():
        profile = load_profile(pid)
        if not os.getenv(profile["instagram_secret"]):
            continue
        hor = state.load(f"horaire_{pid}", {"titres": {}, "heures": {}})
        if h in hor["heures"]:
            continue
        try:
            ig = IG(profile)
            ligne = {"_abonnes": ig._get("me", fields="followers_count").get("followers_count")}
            for m in ig.recent_media(12):
                hor["titres"][m["id"]] = [(m.get("timestamp") or "")[:16], (m.get("caption") or "").split("\n")[0][:40]]
                d = ig._get(f"{m['id']}/insights", metric="views").get("data", [])
                if d:
                    ligne[m["id"]] = d[0]["values"][0]["value"] if "values" in d[0] else d[0].get("total_value", {}).get("value")
            hor["heures"][h] = ligne
            hor["heures"] = dict(sorted(hor["heures"].items())[-24 * 30:])
            state.save(f"horaire_{pid}", hor)
            construire(pid, state.load(f"suivi_{pid}", {"jours": {}, "stories": {}}), profile["nom_compte"])
            print(f"{pid} : relevé horaire {h} ({len(ligne) - 1} vidéos)")
        except Exception as e:
            print(f"{pid} : relevé horaire impossible ({e})")


def nom_fichier_video(fiche: dict, source: Path) -> Path:
    """Copie la vidéo sous le nom demandé par le propriétaire : « Vidéo 0012 - 20-10-26 - Titre court.mp4 »
    (numéro = ordre de création depuis le début du compte ; « / » interdit dans un nom de fichier → « - »)."""
    import shutil
    import tempfile
    pid = fiche.get("profil", "actu")
    nums = state.load(f"numeros_videos_{pid}", {})
    if not nums:  # amorçage : ordre de l'historique
        for h in state.history(pid):
            if h.get("job") and h["job"] not in nums:
                nums[h["job"]] = len(nums) + 1
    if fiche["id"] not in nums:
        nums[fiche["id"]] = max(nums.values(), default=0) + 1
        state.save(f"numeros_videos_{pid}", nums)
    d = datetime.fromisoformat(fiche.get("cree", state.now_iso())).astimezone(TZ)
    titre = re.sub(r'[\\/:*?"<>|«»]', "", fiche.get("titre") or "Vidéo").strip()
    if len(titre) > 45:
        titre = titre[:45].rsplit(" ", 1)[0]
    dest = Path(tempfile.mkdtemp()) / f"Vidéo {nums[fiche['id']]:04d} - {d:%d-%m-%y} - {titre}.mp4"
    shutil.copy(source, dest)
    return dest


def _suivi(ig, pid: str, posts: list[dict]) -> None:
    """Agent 3 : relevé quotidien fin (vidéos, stories, compte) → state/suivi_<pid>.json, puis CSV par mail
    (le Google Sheets « Décodé · Suivi » les importe tout seul, voir docs/suivi_google_sheets.gs)."""
    jour = datetime.now(TZ).strftime("%Y-%m-%d")
    suivi = state.load(f"suivi_{pid}", {"jours": {}, "stories": {}})
    # stories en ligne (leurs stats disparaissent après 24 h : on garde le dernier relevé)
    try:
        for st in ig._get("me/stories", fields="id,timestamp,media_type,permalink").get("data", []):
            met = {}
            for k in ("views", "reach", "replies", "shares", "follows", "profile_visits", "total_interactions", "navigation"):
                try:
                    d = ig._get(f"{st['id']}/insights", metric=k).get("data", [])
                    if d:
                        met[k] = d[0]["values"][0]["value"] if "values" in d[0] else d[0].get("total_value", {}).get("value")
                except Exception:
                    pass
            suivi["stories"][st["id"]] = {"date": st.get("timestamp"), "lien": st.get("permalink"), **met}
    except Exception as e:
        print(f"{pid} : stories indisponibles ({e})")
    compte = {}
    for k in ("reach", "views", "profile_views", "accounts_engaged", "follows_and_unfollows", "total_interactions", "website_clicks"):
        try:
            d = ig._get("me/insights", metric=k, period="day", metric_type="total_value").get("data", [])
            if d:
                compte[k] = d[0].get("total_value", {}).get("value")
        except Exception:
            pass
    ab = state.load(f"abonnes_{pid}", [])
    compte["abonnes"] = ab[-1]["abonnes"] if ab else None
    suivi["jours"][jour] = {"compte": compte, "videos": {p["id"]: {k: v for k, v in p.items() if k != "id"} for p in posts}}
    state.save(f"suivi_{pid}", suivi)
    from .suivi_excel import construire
    construire(pid, suivi, load_profile(pid)["nom_compte"])


def _envoyer_suivi(pid: str, suivi: dict) -> None:
    import csv, tempfile
    tmp = Path(tempfile.mkdtemp())
    jours = sorted(suivi["jours"])
    with open(tmp / f"quotidien_{pid}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["jour", "abonnés", "abonnés gagnés", "vues totales vidéos", "vues du jour (vidéos)", "portée compte",
                    "vues profil", "comptes engagés", "interactions", "clics lien bio", "vues stories du jour"])
        prec_ab, prec_v = None, None
        for j in jours:
            c = suivi["jours"][j]["compte"]
            vt = sum((v.get("views") or 0) for v in suivi["jours"][j]["videos"].values())
            sv = sum((s.get("views") or s.get("reach") or 0) for s in suivi["stories"].values() if (s.get("date") or "")[:10] == j)
            w.writerow([j, c.get("abonnes"), (c["abonnes"] - prec_ab) if c.get("abonnes") is not None and prec_ab is not None else "",
                        vt, (vt - prec_v) if prec_v is not None else "", c.get("reach"), c.get("profile_views"),
                        c.get("accounts_engaged"), c.get("total_interactions"), c.get("website_clicks"), sv])
            prec_ab, prec_v = c.get("abonnes"), vt
    der = suivi["jours"][jours[-1]]["videos"] if jours else {}
    with open(tmp / f"videos_{pid}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["publiée le", "titre", "lien", "vues", "comptes touchés", "likes", "commentaires", "partages",
                    "enregistrements", "interactions", "taux d'engagement %"])
        for v in sorted(der.values(), key=lambda x: x.get("date") or ""):
            inter = sum((v.get(k) or 0) for k in ("likes", "comments", "shares", "saved"))
            w.writerow([(v.get("date") or "")[:16].replace("T", " "), v.get("legende", "")[:70].replace("\n", " "), v.get("lien"),
                        v.get("views"), v.get("reach"), v.get("likes"), v.get("comments"), v.get("shares"), v.get("saved"),
                        v.get("total_interactions"), round(100 * inter / max(1, v.get("reach") or v.get("views") or 1), 1)])
    with open(tmp / f"historique_videos_{pid}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["jour du relevé", "vidéo", "vues", "likes", "partages", "enregistrements"])
        for j in jours:
            for v in suivi["jours"][j]["videos"].values():
                w.writerow([j, v.get("legende", "")[:40].replace("\n", " "), v.get("views"), v.get("likes"), v.get("shares"), v.get("saved")])
    with open(tmp / f"stories_{pid}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["publiée le", "vues", "comptes touchés", "réponses", "partages", "abonnements", "visites profil", "interactions"])
        for s in sorted(suivi["stories"].values(), key=lambda x: x.get("date") or ""):
            w.writerow([(s.get("date") or "")[:16].replace("T", " "), s.get("views"), s.get("reach"), s.get("replies"),
                        s.get("shares"), s.get("follows"), s.get("profile_visits"), s.get("total_interactions")])
    nom = load_profile(pid)["nom_compte"]
    mail.envoyer(3, f"Données de suivi · {nom}",
                 md("Relevé du jour en pièces jointes (CSV). Le Google Sheets **« Décodé · Suivi »** les importe "
                    "automatiquement et met à jour les graphiques."), R_NOTE.format(n=3),
                 ref={"type": "suivi", "profil": pid}, pieces=sorted(tmp.glob("*.csv")))


def graphiques(pid: str) -> dict[str, Path]:
    """Graphiques du rapport de l'agent 9 (PNG intégrés au mail)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    out = OUTPUT / "graphes"
    out.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
    images: dict[str, Path] = {}
    posts = list(reversed(state.load(f"stats_{pid}", {}).get("posts", [])))[-10:]
    if posts:
        etiquettes = [p.get("date", "")[5:10].replace("-", "/") for p in posts]
        fig, ax = plt.subplots(figsize=(7, 3.2), dpi=110)
        ax.bar(etiquettes, [p.get("views") or p.get("reach") or 0 for p in posts], color="#3D5AFE")
        ax.set_title("Vues par vidéo (10 dernières)", loc="left", fontweight="bold")
        fig.tight_layout()
        fig.savefig(out / f"vues_{pid}.png")
        plt.close(fig)
        images["vues"] = out / f"vues_{pid}.png"
        fig, ax = plt.subplots(figsize=(7, 3.2), dpi=110)
        taux = []
        for p in posts:
            base = max(1, p.get("reach") or p.get("views") or 1)
            taux.append(100 * ((p.get("likes") or 0) + (p.get("comments") or 0) + (p.get("shares") or 0)
                               + (p.get("saved") or 0)) / base)
        ax.bar(etiquettes, taux, color="#FF4F81")
        ax.set_title("Taux d'engagement (%)", loc="left", fontweight="bold")
        fig.tight_layout()
        fig.savefig(out / f"engagement_{pid}.png")
        plt.close(fig)
        images["engagement"] = out / f"engagement_{pid}.png"
    hist = state.load(f"abonnes_{pid}", [])[-30:]
    if len(hist) >= 2:
        fig, ax = plt.subplots(figsize=(7, 3.2), dpi=110)
        ax.plot([h["date"][5:].replace("-", "/") for h in hist], [h["abonnes"] for h in hist], color="#2EC4B6",
                marker="o", linewidth=2.5)
        ax.set_title("Abonnés (30 derniers jours)", loc="left", fontweight="bold")
        ax.tick_params(axis="x", labelrotation=45)
        fig.tight_layout()
        fig.savefig(out / f"abonnes_{pid}.png")
        plt.close(fig)
        images["abonnes"] = out / f"abonnes_{pid}.png"
    return images


def digest() -> None:
    """Journal quotidien (un seul mail par jour) : vidéos publiées + rapports des agents 1, 2, 3, 9, 10, 11, 12."""
    now = datetime.now(TZ)
    jour = now.strftime("%Y%m%d")
    d = state.STATE / "attente"
    fiches = [json.loads(f.read_text(encoding="utf-8")) for f in d.glob("*.json")]
    pub = []
    for f in fiches:
        if f.get("statut") == "publiee" and f.get("publiee"):
            t = datetime.fromisoformat(f["publiee"]).astimezone(TZ)
            if t.date() == now.date():
                pub.append((t, f))
    lignes = ["## 🎬 Publié aujourd'hui"]
    lignes += [f"- **{t:%H h %M}** · {f.get('titre')} · [voir le Reel]({f.get('permalink')})" for t, f in sorted(pub, key=lambda x: x[0])] or ["- Aucune vidéo publiée aujourd'hui."]
    try:
        file = state.load("file_sujets_actu", {}).get("sujets", [])
        demain = (now + timedelta(days=1)).strftime("%Y-%m-%d")
        prog = [s for s in file if not s.get("fait") and str(s.get("creneau", "")).startswith(demain)]
        if prog:
            lignes += ["", "## 📅 Demain"] + [f"- **{s['creneau'][11:16].replace(':', ' h ')}** · {s['titre']}" for s in prog]
    except Exception:
        pass
    sec = [x for x in state.load("secretariat", []) if (x.get("date") or "")[:10] == now.strftime("%Y-%m-%d")]
    if sec:  # réponses de l'agent 0 (secrétaire) aux messages du propriétaire
        lignes += ["", "## 💬 Agent 0 · Secrétariat"] + [f"- **{x.get('question', '')}** → {x.get('reponse', '')}" for x in sec]
    noms = {1: "Agent 1 · Actualité", 2: "Agent 2 · Tendances", 3: "Agent 3 · Chiffres", 9: "Agent 9 · Communauté",
            10: "Agent 10 · Stratégie", 11: "Agent 11 · Veille des comptes IA", 12: "Agent 12 · Rétro-ingénierie",
            13: "Agent 13 · Veille TikTok"}
    for n, titre in noms.items():
        rap = [f for f in fiches if f.get("statut") == "rapport" and str(f.get("agent")) == str(n)
               and f.get("id", "").split("-")[2:3] == [jour]]
        rap.sort(key=lambda f: f.get("cree", ""))
        lignes += ["", "---", f"# {titre}"]
        lignes += [rap[-1].get("corps_md", "")] if rap else ["_Pas de rapport aujourd'hui._"]
    images = graphiques("actu")
    corps = md("\n".join(lignes))
    if images:
        corps = corps.replace("<h1>Agent 9", "".join(f'<p><img src="cid:{k}" style="width:100%;max-width:600px"></p>' for k in images) + "<h1>Agent 9", 1)
    mail.envoyer("Manager", f"📰 Journal du {now:%d/%m}", corps, R_MANAGER, images=images,
                 ref={"type": "digest", "profil": "actu"})


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "depot":
        depot(sys.argv[2])
    elif cmd == "rendre":
        rendre(sys.argv[2], sys.argv[3])
    elif cmd == "facteur":
        facteur()
    elif cmd == "digest":
        digest()
    elif cmd == "stats":
        stats()
    elif cmd == "republier":
        republier(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "instagram")
    elif cmd == "tiktok_connexion":
        tiktok_connexion()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
