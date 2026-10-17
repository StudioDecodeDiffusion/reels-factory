"""Chef d'orchestre du pipeline.

Commandes :
  python -m pipeline.run generate  --profile science [--local]   agents 1→7, rendu, envoi Telegram
  python -m pipeline.run approvals                                lit tes réponses Telegram, publie / refuse
  python -m pipeline.run community --profile science [--local]   stats + commentaires (agent 8)
  python -m pipeline.run render-sample                            rend video/sample-spec.json (test sans API)

--local : n'envoie rien (pas de Telegram, pas d'hébergement, pas d'Instagram) ; tout reste dans output/.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

from . import agents, state
from .config import OUTPUT, TZ, VIDEO, load_profile, today_fr
from .llm import USAGE
from .render import frames_per_scene, render, validate_spec


def log(msg: str) -> None:
    print(msg, flush=True)


def summary(md: str) -> None:
    p = os.getenv("GITHUB_STEP_SUMMARY")
    if p:
        with open(p, "a", encoding="utf-8") as f:
            f.write(md + "\n")


def save_debug(job_id: str, name: str, data) -> None:
    d = OUTPUT / job_id
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def build_caption(profile: dict, script: dict) -> str:
    tags = " ".join(script.get("hashtags", [])[: profile["publication"].get("hashtags_max", 5)])
    cap = script.get("legende", "").strip()
    # On retire les hashtags éventuellement déjà présents dans la légende pour ne pas les doubler.
    cap = re.sub(r"(\s#\w+)+\s*$", "", cap).strip()
    footer = profile.get("mention_ia", "Animation créée avec l'IA (Claude).")
    return f"{cap}\n\n{tags}\n\n{footer}".strip()[:2200]


# ──────────────────────────────────────────────────────────────── generate
def generate(pid: str, local: bool) -> None:
    profile = load_profile(pid)
    job_id = f"{pid}-{datetime.now(TZ):%Y%m%d-%H%M}"
    log(f"▶ Nouvelle vidéo {job_id}")

    log("1/8 Veille actualité…")
    sujets = agents.veille_actu(profile)
    save_debug(job_id, "1_veille", sujets)

    log("2/8 Analyse des trends…")
    tr = agents.trends(profile)
    save_debug(job_id, "2_trends", tr)

    log("3/8 Corrélation…")
    corr = agents.correlation(profile, sujets, tr)
    save_debug(job_id, "3_correlation", corr)
    concept = corr["concepts"][int(corr.get("choix", 0))]
    log(f"    concept retenu : {concept.get('titre')}")

    retour, corrections_da = None, None
    script = da = verdict = None
    for tour in range(3):  # 1 version + jusqu'à 2 corrections
        log(f"4/8 Scénario (version {tour + 1})…")
        script = agents.scenariste(profile, concept, tr, retour)
        log("5/8 Direction artistique…")
        da = agents.directeur_artistique(profile, script, corrections_da)
        log("6/8 Validation…")
        verdict = agents.validateur(profile, concept, script, da)
        save_debug(job_id, f"4-6_tour{tour + 1}", {"script": script, "da": da, "verdict": verdict})
        log(f"    notes : {verdict.get('notes')} → {verdict.get('verdict')}")
        if verdict.get("verdict") == "valide":
            break
        retour = {"corrections": verdict.get("corrections_script", []), "commentaire": verdict.get("commentaire")}
        corrections_da = verdict.get("corrections_charte") or None
    else:
        msg = (f"⚠️ {profile['nom_compte']} : aucune version n'a passé la validation pour « {concept.get('titre')} ».\n"
               f"Dernier avis : {verdict.get('commentaire')}\nRien n'est publié aujourd'hui.")
        log(msg)
        if not local:
            from . import telegram
            telegram.send(msg)
        summary(msg)
        return

    log("7/8 Génération de la vidéo…")
    allowed = profile["video"]["scenes_autorisees"]
    erreurs, spec = None, None
    for essai in range(3):
        spec = agents.generateur(profile, script, da, erreurs)
        spec["theme"] = {**da["theme"], **spec.get("theme", {})}
        erreurs = validate_spec(spec, allowed)
        if not erreurs:
            break
        log(f"    spécification invalide ({len(erreurs)} erreurs), correction…")
    if erreurs:
        raise SystemExit("Spécification vidéo invalide après 3 essais : " + "; ".join(erreurs))
    music = VIDEO / "public" / "music" / f"{pid}.mp3"
    spec["music"] = music.name if music.exists() else None
    save_debug(job_id, "7_spec", spec)

    mp4 = OUTPUT / job_id / f"{job_id}.mp4"
    render(spec, mp4)

    # Contrôle visuel : une image par scène relue par Claude ; un seul re-rendu si besoin.
    qa = agents.controle_visuel(script, frames_per_scene(spec, mp4))
    save_debug(job_id, "7b_controle", qa)
    if not qa.get("ok", True) and qa.get("problemes"):
        log(f"    contrôle visuel : {len(qa['problemes'])} problème(s), correction et nouveau rendu…")
        spec2 = agents.generateur(profile, script, da,
                                  [f"scène {p.get('scene')} : {p.get('description')} → {p.get('correction_suggeree')}"
                                   for p in qa["problemes"]])
        spec2["theme"] = {**da["theme"], **spec2.get("theme", {})}
        spec2["music"] = spec.get("music")
        if not validate_spec(spec2, allowed):
            spec = spec2
            save_debug(job_id, "7_spec_corrigee", spec)
            render(spec, mp4)

    caption = build_caption(profile, script)
    (OUTPUT / job_id / "legende.txt").write_text(caption, encoding="utf-8")
    state.add_history(pid, {"date": today_fr(), "titre": concept.get("titre"), "job": job_id})

    cost = f"tokens in/out {USAGE['input_tokens']}/{USAGE['output_tokens']}, recherches web {USAGE['web_searches']}"
    log(f"✔ Vidéo prête : {mp4} ({cost})")
    summary(f"### {job_id}\n**{concept.get('titre')}**\n\n```\n{caption}\n```\n\n{cost}")

    if local:
        return

    from . import media_host, telegram
    media = media_host.upload(mp4, job_id)
    q = state.queue()
    q.append({"id": job_id, "profil": pid, "statut": "en_attente", "titre": concept.get("titre"),
              "legende": caption, "media": media, "cree": state.now_iso(),
              "notes": verdict.get("notes"), "source": concept.get("source_url")})
    state.save_queue(q)
    telegram.send_video(mp4, f"🎬 {profile['nom_compte']} — {concept.get('titre')}\n\n"
                             f"Réponds :\nOK {job_id}\nou\nNON {job_id} ta raison")
    telegram.send(f"Légende prévue pour {job_id} :\n\n{caption}\n\nSource : {concept.get('source_url') or '—'}")


# ──────────────────────────────────────────────────────────────── approvals
def approvals() -> None:
    from . import media_host, telegram
    from .instagram import IG

    q = state.queue()
    msgs = telegram.new_messages()
    changed = False
    for text in msgs:
        m = re.match(r"^(OK|NON|REP)\s+(\S+)\s*(.*)$", text, re.I | re.S)
        if not m:
            if text.lower() in ("aide", "help", "/start", "/aide"):
                telegram.send("Commandes :\nOK <id> → publier\nNON <id> raison → refuser\n"
                              "REP <code> → envoyer une réponse à un commentaire\nREP TOUT <profil> → toutes")
            continue
        cmd, arg, rest = m.group(1).upper(), m.group(2), m.group(3).strip()
        if cmd == "REP":
            _send_replies(arg, rest)
            continue
        job = next((j for j in q if j["id"] == arg), None)
        if not job:
            telegram.send(f"Je ne trouve pas la vidéo {arg}.")
            continue
        if job["statut"] != "en_attente":
            telegram.send(f"{arg} est déjà « {job['statut']} ».")
            continue
        profile = load_profile(job["profil"])
        if cmd == "NON":
            job.update(statut="refuse", raison=rest, traite=state.now_iso())
            media_host.cleanup(job["media"])
            fb = state.load(f"refus_{job['profil']}", [])
            fb.append({"titre": job["titre"], "raison": rest, "date": today_fr()})
            state.save(f"refus_{job['profil']}", fb[-50:])
            telegram.send(f"🗑️ {arg} refusée. Raison notée pour les prochaines vidéos.")
        else:
            try:
                info = IG(profile).publish_reel(job["media"]["url"], job["legende"])
                job.update(statut="publie", media_id=info["id"], permalink=info.get("permalink"),
                           traite=state.now_iso())
                telegram.send(f"✅ Publié sur {profile['nom_compte']} : {info.get('permalink', '')}")
                media_host.cleanup(job["media"])
            except Exception as e:
                job.update(statut="en_attente", derniere_erreur=str(e)[:500])
                telegram.send(f"❌ Échec de publication de {arg} : {str(e)[:500]}\n"
                              f"Tu peux renvoyer OK {arg} pour réessayer.")
        changed = True

    # Expiration des vidéos non validées après 48 h
    limit = datetime.now(timezone.utc) - timedelta(hours=48)
    for job in q:
        if job["statut"] == "en_attente" and datetime.fromisoformat(job["cree"]) < limit:
            job.update(statut="expire")
            media_host.cleanup(job["media"])
            changed = True
    if changed:
        state.save_queue(q[-300:])
    log(f"{len(msgs)} message(s) traité(s)")


def _send_replies(code: str, rest: str) -> None:
    from . import telegram
    from .instagram import IG

    if code.upper() == "TOUT":
        pids = [rest.strip()] if rest.strip() else []
    else:
        pids = [code.split("-")[0]]
    for pid in pids:
        pend = state.load(f"reponses_{pid}", [])
        todo = pend if code.upper() == "TOUT" else [r for r in pend if r["code"] == code]
        if not todo:
            telegram.send(f"Aucune réponse en attente pour {code} {rest}".strip())
            continue
        ig = IG(load_profile(pid))
        for r in todo:
            try:
                ig.reply(r["comment_id"], r["reponse"])
                r["envoye"] = True
            except Exception as e:
                telegram.send(f"❌ Réponse {r['code']} non envoyée : {str(e)[:300]}")
        state.save(f"reponses_{pid}", [r for r in pend if not r.get("envoye")])
        telegram.send(f"💬 {sum(1 for r in todo if r.get('envoye'))} réponse(s) envoyée(s).")


# ──────────────────────────────────────────────────────────────── community
def community(pid: str, local: bool) -> None:
    from .instagram import IG

    profile = load_profile(pid)
    if not os.getenv(profile["instagram_secret"]):
        log(f"{pid} : pas de token Instagram ({profile['instagram_secret']}), compte ignoré")
        return
    ig = IG(profile)
    seen = set(state.load(f"commentaires_vus_{pid}", []))
    posts, new_comments = [], []
    me = ig.username()
    for m in ig.recent_media(15):
        ins = ig.insights(m["id"])
        posts.append({"id": m["id"], "date": m.get("timestamp"), "lien": m.get("permalink"),
                      "legende": (m.get("caption") or "")[:120], **ins})
        for c in ig.comments(m["id"]):
            if c["id"] not in seen and c.get("username") != me:
                new_comments.append({"comment_id": c["id"], "auteur": c.get("username"), "texte": c.get("text"),
                                     "post": (m.get("caption") or "")[:60]})
                seen.add(c["id"])
    cm = agents.community_manager(profile, posts, new_comments[:40])
    state.save(f"stats_{pid}", {"maj": state.now_iso(), "posts": posts, "bilan": cm.get("bilan"),
                                "recommandations": cm.get("recommandations", [])})
    state.save(f"commentaires_vus_{pid}", sorted(seen)[-2000:])

    pend = state.load(f"reponses_{pid}", [])
    n0 = len(pend)
    for i, r in enumerate(cm.get("reponses", [])):
        pend.append({**r, "code": f"{pid}-{datetime.now(TZ):%m%d}{n0 + i + 1}"})
    state.save(f"reponses_{pid}", pend)

    text = (f"📊 {profile['nom_compte']} — bilan\n{cm.get('bilan', '')}\n\nPistes :\n"
            + "\n".join(f"• {x}" for x in cm.get("recommandations", [])))
    if pend[n0:]:
        text += "\n\n💬 Réponses proposées :\n" + "\n\n".join(
            f"[{r['code']}] « {str(r.get('commentaire', ''))[:120]} »\n→ {r['reponse']}" for r in pend[n0:])
        text += f"\n\nRéponds REP <code> pour en envoyer une, ou REP TOUT {pid} pour toutes."
    log(text)
    summary(text)
    if not local:
        from . import telegram
        telegram.send(text)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["generate", "approvals", "community", "render-sample"])
    ap.add_argument("--profile")
    ap.add_argument("--local", action="store_true")
    a = ap.parse_args()
    if a.cmd in ("generate", "community") and not a.profile:
        sys.exit("--profile est obligatoire (actu, science ou fun)")
    if a.cmd == "generate":
        generate(a.profile, a.local)
    elif a.cmd == "approvals":
        approvals()
    elif a.cmd == "community":
        community(a.profile, a.local)
    else:
        spec = json.loads((VIDEO / "sample-spec.json").read_text(encoding="utf-8"))
        print(validate_spec(spec, list({s["type"] for s in spec["scenes"]})) or "spec OK")
        render(spec, OUTPUT / "sample" / "sample.mp4")


if __name__ == "__main__":
    main()
