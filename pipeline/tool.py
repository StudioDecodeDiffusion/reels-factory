"""Outils utilisés par la session Claude de nuit (voir NUIT.md).

  python -m pipeline.tool setup                              installe le moteur vidéo
  python -m pipeline.tool new --profile actu                 crée travail/<id>/ et affiche l'id
  python -m pipeline.tool check <spec.json> --profile actu   valide une spécification vidéo
  python -m pipeline.tool render <spec.json> <video.mp4>     rend la vidéo
  python -m pipeline.tool frames <spec.json> <video.mp4>     extrait 1 image par scène + planche aperçu
  python -m pipeline.tool caption <id> --profile actu        assemble la légende finale (legende.txt)
  python -m pipeline.tool info <id> --profile actu           agent 4 → e-mail d'information (concept + critique)
  python -m pipeline.tool drop <id> --profile actu           envoie le tout à GitHub (→ e-mail de validation)
  python -m pipeline.tool rapport --agent 3 --profile actu --titre "…" rapport.md   rapport quotidien → mail
  python -m pipeline.tool abandon <id> --profile actu --raison "…"   prévient le propriétaire, pas de vidéo
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from . import state
from .config import ROOT, TZ, VIDEO, load_profile, today_fr
from .render import contact_sheet, frames_per_scene, render, validate_spec

WORK = ROOT / "travail"


def _git(*args: str, cwd: Path = ROOT, check: bool = True) -> str:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} a échoué :\n{r.stderr}")
    return r.stdout.strip()


def cmd_setup(_a) -> None:
    subprocess.run(["npm", "ci", "--no-audit", "--no-fund"], cwd=VIDEO, check=True)
    print("Moteur vidéo prêt.")


def cmd_new(a) -> None:
    load_profile(a.profile)
    job = f"{a.profile}-{datetime.now(TZ):%Y%m%d-%H%M}"
    (WORK / job).mkdir(parents=True, exist_ok=True)
    print(job)


def cmd_check(a) -> None:
    spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    prof = load_profile(a.profile)
    errs = validate_spec(spec, prof["video"]["scenes_autorisees"],
                         voix_obligatoire=bool(prof.get("voix", {}).get("active")))
    from .variete import controler
    errs += controler(spec, a.profile)
    pre = Path(a.spec).parent / "9_precritique.json"
    if not pre.exists():
        errs.append("9_precritique.json manquant : l'agent 7 doit critiquer le scénario et la DA AVANT la génération")
    else:
        d9 = json.loads(pre.read_text(encoding="utf-8"))
        if str(d9.get("decision")).lower() != "go":
            errs.append(f"l'agent 7 n'a pas donné son feu vert (décision : {d9.get('decision')}) : appliquer ses demandes")
    if (Path(a.spec).parent / "4_concept.json").exists():
        cc = _concept(Path(a.spec).parent)
        tm = str(cc.get("titre_miniature", "")).strip()
        if not tm:
            errs.append("4_concept.json : titre_miniature manquant (titre CRITIQUE qui donne la teneur du post, 8 mots max) "
                        "+ mots_choc (mots en rouge) + surtitre_miniature (qui · quand)")
        elif len(tm.split()) > 9:
            errs.append(f"titre_miniature trop long ({len(tm.split())} mots) : 8 mots max")
    if errs:
        print("ERREURS :\n- " + "\n- ".join(errs))
        sys.exit(1)
    Path(a.spec).write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")  # version normalisée
    print("OK")


def cmd_render(a) -> None:
    spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    render(spec, Path(a.out))
    print(f"Vidéo rendue : {a.out}")


def cmd_frames(a) -> None:
    spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    imgs = frames_per_scene(spec, Path(a.video))
    sheet = contact_sheet(imgs, Path(a.video).with_name("apercu.png"))
    print("\n".join(str(i) for i in imgs))
    print(f"Planche : {sheet}")


def cmd_caption(a) -> None:
    profile = load_profile(a.profile)
    d = WORK / a.id
    script = json.loads((d / "5_scenario.json").read_text(encoding="utf-8"))
    tags = " ".join(script.get("hashtags", [])[: profile["planning"].get("hashtags_max", 5)])
    cap = re.sub(r"(\s#[\wÀ-ÿ]+)+\s*$", "", script.get("legende", "").strip()).strip()
    from .voix import mention
    v = profile.get("voix", {})
    credits = " ".join(sorted({m for m in (mention(v.get("narrateur", "")), mention(v.get("mascotte", ""))) if m}))
    # propriétaire (24/10) : aucune mention IA dans le contenu (Instagram étiquette déjà) ; seuls restent les crédits
    # de licence obligatoires (voix CC BY-SA), en fin de légende.
    text = f"{cap}\n\n{tags}\n\n{credits}".strip()[:2200]
    (d / "legende.txt").write_text(text, encoding="utf-8")
    print(text)


def _push_drop(job: str, files: dict[str, Path | str]) -> None:
    """Ajoute les fichiers sur la branche `depot-videos` (les dépôts de plus de 3 jours sont retirés :
    la branche reste légère, et un envoi ne peut pas en écraser un autre pas encore traité)."""
    origin = _git("remote", "get-url", "origin")
    tmp = Path(tempfile.mkdtemp())
    r = subprocess.run(["git", "clone", "-q", "--depth", "1", "-b", "depot-videos", origin, str(tmp)],
                       capture_output=True, text=True)
    if r.returncode != 0:  # première fois : la branche n'existe pas encore
        _git("init", "-q", "-b", "depot-videos", cwd=tmp)
    limite = datetime.now(TZ).timestamp() - 3 * 86400
    for old in (tmp / "drop").glob("*") if (tmp / "drop").exists() else []:
        if old.is_dir() and old.stat().st_mtime and _age_depot(old) < limite:
            shutil.rmtree(old)
    dest = tmp / "drop" / job
    dest.mkdir(parents=True, exist_ok=True)
    for name, src in files.items():
        if isinstance(src, Path):
            shutil.copy(src, dest / name)
        else:
            (dest / name).write_text(src, encoding="utf-8")
    _git("add", "-A", cwd=tmp)
    _git("-c", "user.name=reels-bot", "-c", "user.email=reels-bot@users.noreply.github.com",
         "commit", "-q", "--allow-empty", "-m", f"dépôt {job}", cwd=tmp)
    _git("push", "-q", "--force", origin, "HEAD:depot-videos", cwd=tmp)
    shutil.rmtree(tmp, ignore_errors=True)


def _age_depot(d: Path) -> float:
    """Date de création d'un dépôt (lue dans sa fiche)."""
    try:
        return datetime.fromisoformat(json.loads((d / "fiche.json").read_text(encoding="utf-8"))["cree"]).timestamp()
    except Exception:
        return 0.0


def _commit_state(msg: str) -> None:
    _git("add", "state/")
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode == 0:
        return  # rien de nouveau
    _git("-c", "user.name=reels-bot", "-c", "user.email=reels-bot@users.noreply.github.com", "commit", "-q", "-m", msg)
    _git("pull", "-q", "--rebase", "-X", "theirs", "origin", "main")
    _git("push", "-q")


def _read(d: Path, name: str, default=None):
    p = d / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def _concept(d: Path) -> dict:
    c = _read(d, "4_concept.json")
    choisi = dict(c["concepts"][int(c.get("choix", 0))])
    for k, v in c.items():  # champs ajoutés au niveau racine (titre_miniature, plateforme, compte…)
        if k not in ("concepts", "choix") and v and not choisi.get(k):
            choisi[k] = v
    return choisi


def _marquer_lus(agent: int, ids) -> int:
    fil = state.load(f"messages/agent_{agent}", [])
    ids, n = set(map(str, ids)), 0
    for m in fil:
        if str(m.get("id")) in ids or "tout" in ids:
            n += not m.get("traite")
            m["traite"] = True
    state.save(f"messages/agent_{agent}", fil)
    return n


def cmd_activite(a) -> None:
    """Studio en direct : met à jour l'état d'un agent dans reels-media/studio/activite.json (lu par la page
    https://studiodecodediffusion.github.io/reels-media/studio/). Jamais de titre ni de donnée sensible : agent, étape, salle."""
    d = WORK / ".reels-media"
    g = lambda *c: subprocess.run(["git", "-C", str(d), *c], capture_output=True, text=True)
    try:
        if not (d / ".git").exists():
            subprocess.run(["git", "clone", "-q", "--depth", "1", "https://github.com/StudioDecodeDiffusion/reels-media", str(d)],
                           capture_output=True, text=True, timeout=120)
        f = d / "studio" / "activite.json"
        for _ in range(4):
            g("pull", "-q", "--rebase", "-X", "theirs")
            data = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {"agents": {}, "journal": []}
            t = datetime.now(TZ).isoformat(timespec="seconds")
            data["agents"][a.agent] = {"etat": a.etat, "salle": a.salle or "", "compte": a.profile or "", "depuis": t}
            data["journal"] = (data.get("journal", []) + [{"t": t, "agent": a.agent, "etat": a.etat, "salle": a.salle or "",
                                                            "compte": a.profile or ""}])[-60:]
            data["maj"] = t
            f.parent.mkdir(exist_ok=True)
            f.write_text(json.dumps(data, ensure_ascii=False, indent=0), encoding="utf-8")
            g("add", "studio/activite.json")
            g("-c", "user.name=reels-bot", "-c", "user.email=reels-bot@users.noreply.github.com", "commit", "-q", "-m",
              f"studio : agent {a.agent} · {a.etat[:40]}")
            if g("push", "-q").returncode == 0:
                print(f"studio : agent {a.agent} → {a.etat}")
                return
            g("reset", "-q", "--hard", "origin/main")
    except Exception as e:
        print(f"(studio non mis à jour : {e} — sans conséquence)")
        return
    print("(studio non mis à jour — sans conséquence)")


def cmd_notes(a) -> None:
    """Affiche les notes non traitées que le propriétaire a envoyées à un agent (mails « agent N - … »)."""
    fil = [m for m in state.load(f"messages/agent_{a.agent}", []) if not m.get("traite")]
    if a.profile:
        fil = [m for m in fil if m.get("profil") in (None, "", "tous", a.profile)]
    print(json.dumps(fil, ensure_ascii=False, indent=1) if fil else f"Aucune note en attente pour l'agent {a.agent}.")


def cmd_lu(a) -> None:
    """Marque des notes comme traitées : tool lu --agent N id1 id2 … (ou « tout »)."""
    print(f"{_marquer_lus(int(a.agent), a.ids)} note(s) marquée(s) comme traitée(s).")


def _da_suivi(d: Path, pid: str) -> str:
    """Marque comme traités les messages du propriétaire lus par le directeur artistique ; renvoie sa réponse."""
    da = _read(d, "6_da.json", {})
    faits = set(map(str, da.get("messages_traites", [])))
    if faits:
        _marquer_lus(6, faits)
    return str(da.get("message_au_proprietaire") or "").strip()


def cmd_info(a) -> None:
    """Agent 4 → propriétaire, pour information : concept du jour + critique du compte (sans validation)."""
    load_profile(a.profile)
    d = WORK / a.id
    c = _read(d, "4_concept.json")
    if not c:
        raise SystemExit(f"{d / '4_concept.json'} manquant")
    res = _read(d, "3_resultats.json", {}) or state.load(f"rapport_3_{a.profile}", {})
    fiche = {"id": f"{a.id}-info", "profil": a.profile, "statut": "info", "cree": state.now_iso(),
             "titre": _concept(d).get("titre"), "concept": _concept(d),
             "autres": [x.get("titre") for i, x in enumerate(c.get("concepts", [])) if i != int(c.get("choix", 0))],
             "justification": c.get("justification"), "critique": c.get("critique_compte"),
             "a_tester": c.get("a_tester", []), "enseignements": res.get("enseignements", [])}
    _push_drop(fiche["id"], {"fiche.json": json.dumps(fiche, ensure_ascii=False, indent=2)})
    state.save("dernier_depot", {"id": fiche["id"], "profil": a.profile, "date": state.now_iso()})
    _commit_state(f"état : concept {a.id}")
    print("Concept du jour envoyé pour information.")


def _creneaux_du_jour(prof: dict, jour) -> list[str]:
    c = prof["planning"].get("creneaux")
    if isinstance(c, dict):  # par jour de la semaine : {"lun": [...], ...}
        cle = ["lun", "mar", "mer", "jeu", "ven", "sam", "dim"][jour.weekday()]
        return c.get(cle, [])
    return c or []


def _prochain_creneau(pid: str, horizon_h: float | None = None) -> str | None:
    """Prochain créneau libre au moins 1 h 30 après maintenant (planning.creneaux du profil, par jour de la semaine).
    horizon_h : ne cherche pas au-delà (pour savoir si une session doit produire)."""
    from datetime import timedelta
    prof = load_profile(pid)
    pris = set()
    d = state.STATE / "attente"
    for f in (d.glob("*.json") if d.exists() else []):
        x = json.loads(f.read_text(encoding="utf-8"))
        if x.get("profil") == pid and x.get("statut") in ("a_valider", "approuvee", "rendu_en_cours", "publiee") and x.get("publication_le"):
            pris.add(x["publication_le"][:16])
    maintenant = datetime.now(TZ)
    t0 = maintenant + timedelta(minutes=40)  # le rendu final GitHub prend ~20-25 min
    for jour in range(0, 8):
        base = maintenant + timedelta(days=jour)
        for c in sorted(_creneaux_du_jour(prof, base)):
            h, m = map(int, c.split(":"))
            t = base.replace(hour=h, minute=m, second=0, microsecond=0)
            if horizon_h is not None and t > maintenant + timedelta(hours=horizon_h):
                return None
            if t >= t0 and t.isoformat()[:16] not in pris:
                return t.isoformat()
    return None


def cmd_creneau(a) -> None:
    """Créneau que la session doit remplir (dans les 8 h), ou AUCUN → la session s'arrête sans produire."""
    c = _prochain_creneau(a.profile, horizon_h=getattr(a, "horizon", None) or 8)
    if not c:
        print("AUCUN")
        return
    from datetime import datetime as _dt
    t = _dt.fromisoformat(c)
    jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    impose = next((x["id"] for x in state.load(f"file_sujets_{a.profile}", {}).get("sujets", []) if not x.get("fait")
                   and (x.get("creneau") or "")[:16] == c[:16]), None)  # sujet placé par le propriétaire
    resume = t.weekday() == 6 and t.hour == 14 and not impose
    phare = 13 <= t.hour <= 15
    print(f"{c} ({jours[t.weekday()]} {t:%H h %M})" + (" — RÉSUMÉ DE LA SEMAINE OBLIGATOIRE" if resume else "")
          + (f" — SUJET IMPOSÉ : {impose}" if impose else "")
          + (" — VIDÉO PHARE DU JOUR (voir NUIT.md § Vidéo phare)" if phare else " — vidéo d'info (fond de commerce)"))


def cmd_avance(a) -> None:
    """Session de 20 h : peut-on prendre de l'avance ? (règle du propriétaire, 18/10)
    OUI si quota du jour < 25 % ET quota de la semaine < part de semaine écoulée (semaine = vendredi 23 h → vendredi 23 h).
    STOP (+ mail d'alerte) si jour ou semaine > 75 %. Sinon NON. Sans relevé du jour (mail « quota - J S ») : NON."""
    from datetime import timedelta
    q = state.load("quota", {})
    now = datetime.now(TZ)
    debut = now.replace(hour=23, minute=0, second=0, microsecond=0) - timedelta(days=(now.weekday() - 4) % 7)
    if debut > now:
        debut -= timedelta(days=7)
    attendu = round(100 * (now - debut).total_seconds() / (7 * 86400))
    if not q or q.get("date") != now.strftime("%Y-%m-%d"):
        print(f"NON — pas de relevé de quota aujourd'hui (attendu semaine : {attendu} %). Ne prendre aucune avance.")
        return
    j, w = q["jour"], q["semaine"]
    if j > 75 or w > 75:
        import argparse
        cmd_etape(argparse.Namespace(agent="Manager", profile="actu", titre="⚠ Quota Claude élevé : avance suspendue",
                  resume=f"Relevé du jour : **{j} %** (jour) · **{w} %** (semaine, attendu {attendu} %).\n\n"
                         "Au-dessus de 75 % : je ne fais **que les tâches programmées**, aucune vidéo d'avance."))
        print(f"STOP — quota élevé (jour {j} %, semaine {w} %) : uniquement les tâches programmées, alerte envoyée.")
    elif j < 25 and w < attendu:
        print(f"OUI — jour {j} % < 25 %, semaine {w} % < {attendu} % attendus : produire en avance jusqu'à 23 h.")
    else:
        print(f"NON — jour {j} %, semaine {w} % (attendu {attendu} %) : pas d'avance.")


STYLES_ANNONCE = ["flash", "reaction", "pancarte"]  # styles génériques (notif/amende/parchemin sont propres à d'anciens sujets)


def _annonce_4h(d, job: str, pid: str, fiche: dict, concept: dict) -> None:
    """Règle du propriétaire (19/10) : story d'annonce 4 h avant la sortie, story « elle est sortie » à la publication."""
    from datetime import timedelta
    from .affiches import creer
    quand_pub = fiche.get("publication_le")
    if not quand_pub:
        return
    t = datetime.fromisoformat(quand_pub)
    t = t if t.tzinfo else t.replace(tzinfo=TZ)  # « --le 2026-10-24T20:00 » sans fuseau = heure de Paris
    jours =["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    quand_txt = ("AUJOURD'HUI" if t.date() == datetime.now(TZ).date() else jours[t.weekday()].upper()) + f" {t:%H}H{t:%M}".replace("H00", "H")
    liste = state.load("stories_programmees", [])
    style = STYLES_ANNONCE[len(liste) % len(STYLES_ANNONCE)]
    img = state.STATE / "stories_annonce" / f"{job}.png"
    titre = concept.get("titre") or fiche.get("titre") or "Nouvelle vidéo"
    creer(style, "story", titre, concept.get("accroche_story") or concept.get("accroche") or titre, quand_txt,
          d / "video_scene0.png", img)
    envoi = max(t - timedelta(hours=4), datetime.now(TZ) + timedelta(minutes=10))
    liste = [x for x in liste if not (x.get("image", "").endswith(f"{job}.png") and not x.get("faite"))]
    liste.append({"image": f"stories_annonce/{job}.png", "quand": envoi.isoformat(timespec="minutes"), "profil": pid,
                  "titre": f"Annonce 4 h avant : {titre}"})
    state.save("stories_programmees", liste)


def cmd_drop(a) -> None:
    load_profile(a.profile)  # vérifie que le compte existe
    d = WORK / a.id
    needed = ["video.mp4", "apercu.png", "legende.txt", "4_concept.json", "5_scenario.json", "7_spec.json",
              "9_critique.json"]
    missing = [n for n in needed if not (d / n).exists()]
    if missing:
        raise SystemExit(f"Fichiers manquants dans {d} : {missing}")
    controle = _read(d, "9_critique.json")
    if controle.get("decision") != "publiable":
        raise SystemExit("L'agent 7 n'a pas déclaré la vidéo « publiable » : corriger ou utiliser `abandon`.")
    concept = _concept(d)
    relecture = _read(d, "5_scenario.json", {}).get("relecture", {})
    fiche = {
        "id": a.id, "profil": a.profile, "statut": "a_valider", "titre": concept.get("titre"),
        "son_tendance": _read(d, "7_spec.json", {}).get("son_tendance"),
        **({"publication_le": a.le} if getattr(a, "le", None) else {"publication_heure": a.heure} if getattr(a, "heure", None) is not None else {"publication_le": _prochain_creneau(a.profile)}),
        "format_qhse": concept.get("format_qhse"), "episode": concept.get("episode"),
        "plateforme": concept.get("plateforme"),  # "tiktok" = brouillon TikTok seulement
        "legende": (d / "legende.txt").read_text(encoding="utf-8"),
        "sources": sorted({f.get("source_url") for f in concept.get("faits", []) if f.get("source_url")}
                          | set(controle.get("sources_verifiees", []))),
        "validation": {"notes": relecture.get("notes", {})},
        "tours_validation": int(relecture.get("reecritures", 0)) + 1,
        "critique": controle,
        "community": _read(d, "8_community.json", {}),
        "da_message": _da_suivi(d, a.profile),
        "cree": state.now_iso(),
    }
    if concept.get("plateforme") != "tiktok":  # vidéo réservée à TikTok : pas de story Instagram
        _annonce_4h(d, a.id, a.profile, fiche, concept)
    from .variete import enregistrer
    enregistrer(json.loads((d / "7_spec.json").read_text(encoding="utf-8")), a.profile, fiche.get("titre") or "", a.id)
    extra = {"couverture.png": d / "couverture.png"} if (d / "couverture.png").exists() else {}
    _push_drop(a.id, {**extra, "video.mp4": d / "video.mp4", "apercu.png": d / "apercu.png",
                      "7_spec.json": d / "7_spec.json",
                      "fiche.json": json.dumps(fiche, ensure_ascii=False, indent=2)})

    state.add_history(a.profile, {"date": today_fr(), "titre": concept.get("titre"), "job": a.id,
                                  "format_qhse": concept.get("format_qhse"), "episode": concept.get("episode")})
    # Série de cours QHSE : on avance l'épisode
    if concept.get("format_qhse") == "cours" and concept.get("episode"):
        prog = state.load(f"series_{a.profile}", {})
        prog[concept.get("serie", "en_cours")] = int(concept["episode"]) + 1
        state.save(f"series_{a.profile}", prog)
    if (d / "8_community.json").exists():
        state.save(f"commentaires_{a.profile}", [])  # commentaires traités : ils sont dans la fiche
    # Ce fichier sur « main » déclenche le workflow « Nouvelle vidéo » (GitHub n'exécute pas de workflow
    # pour une branche qui n'en contient pas, comme depot-videos).
    state.save("dernier_depot", {"id": a.id, "profil": a.profile, "date": state.now_iso()})
    _commit_state(f"état : vidéo {a.id}")
    print(f"Envoyé à GitHub : {a.id}. L'e-mail de validation part dans 1-2 minutes.")


def cmd_rapport(a) -> None:
    """Rapport quotidien d'un agent (1, 2, 3 ou 8) → mail « Agent N - date - titre »."""
    load_profile(a.profile)
    src = Path(a.fichier)
    data = json.loads(src.read_text(encoding="utf-8")) if src.suffix == ".json" else {"corps_md": src.read_text(encoding="utf-8")}
    job = f"{a.profile}-rapport{a.agent}-{datetime.now(TZ):%Y%m%d-%H%M}"
    fiche = {"id": job, "profil": a.profile, "statut": "rapport", "agent": int(a.agent), "cree": state.now_iso(),
             "titre": a.titre, "corps_md": data.get("corps_md", ""), "reponses": data.get("reponses", [])}
    _push_drop(job, {"fiche.json": json.dumps(fiche, ensure_ascii=False, indent=2)})
    state.save("dernier_depot", {"id": job, "profil": a.profile, "date": state.now_iso()})
    _commit_state(f"état : rapport agent {a.agent}")
    print(f"Rapport de l'agent {a.agent} envoyé.")


def cmd_story(a) -> None:
    """Miniature du Reel (couverture.png) + story « nouvelle vidéo » publiée juste après le Reel."""
    from .story import couverture, creer
    prof = load_profile(a.profile)
    d = WORK / a.id
    concept = _concept(d)
    titre = a.titre or concept.get("titre") or "Nouvelle vidéo"
    # Miniature « choc » (propriétaire, 19/10) : titre critique qui donne la teneur du post, image la plus parlante
    from .affiches import couverture_choc
    spec = _read(d, "7_spec.json", {})
    scenes = spec.get("scenes", [])
    idx = next((i for i, sc in enumerate(scenes) if sc.get("type") in ("ed_photo", "ed_allocution", "photo", "pendant")), None)
    if idx is None:
        idx = next((i for i, sc in enumerate(scenes) if sc.get("dialogue") and not str(sc.get("type", "")).startswith("ed_")), 0)
    img = d / f"video_scene{idx}.png"
    if not img.exists():
        img = d / "video_scene0.png"
    accent = (spec.get("theme") or {}).get("accent", "#E3242B").lstrip("#")
    couverture_choc(img, concept.get("titre_miniature") or titre, concept.get("mots_choc"), d / "couverture.png",
                    tuple(int(accent[i:i + 2], 16) for i in (0, 2, 4)), concept.get("surtitre_miniature", ""))
    out = creer(d / "video_scene0.png", titre, prof.get("instagram") or prof["nom_compte"],
                state.STATE / "stories" / f"{a.id}.png", (prof.get("charte_initiale") or {}).get("palette"))
    print(out)


def cmd_story_now(a) -> None:
    """Publie tout de suite une image en story : tool story_now --profile p --titre "…" image.png"""
    load_profile(a.profile)
    job = f"{a.profile}-story-{datetime.now(TZ):%Y%m%d-%H%M%S}"
    fiche = {"id": job, "profil": a.profile, "statut": "story", "cree": state.now_iso(), "titre": a.titre}
    _push_drop(job, {"fiche.json": json.dumps(fiche, ensure_ascii=False, indent=2), "story.png": Path(a.image)})
    state.save("dernier_depot", {"id": job, "profil": a.profile, "date": state.now_iso()})
    _commit_state("état : story")
    print("Story envoyée.")


def cmd_etape(a) -> None:
    """Point d'avancement → mail du « Manager ». Désactivé (propriétaire, 19/10) sauf alertes ❌/⚠."""
    if not any(k in (a.titre or "") for k in ("❌", "⚠")):
        print("(points d'avancement désactivés : rien envoyé)")
        return
    load_profile(a.profile)
    job = f"{a.profile}-etape{a.agent}-{datetime.now(TZ):%Y%m%d-%H%M%S}"
    fiche = {"id": job, "profil": a.profile, "statut": "etape", "agent": a.agent, "cree": state.now_iso(),
             "titre": a.titre, "corps_md": a.resume}
    _push_drop(job, {"fiche.json": json.dumps(fiche, ensure_ascii=False, indent=2)})
    state.save("dernier_depot", {"id": job, "profil": a.profile, "date": state.now_iso()})
    _commit_state(f"état : étape agent {a.agent}")
    print("Point d'avancement envoyé.")


def cmd_abandon(a) -> None:
    fiche = {"id": a.id, "profil": a.profile, "statut": "abandonnee", "titre": "Pas de vidéo aujourd'hui",
             "raison": a.raison, "cree": state.now_iso()}
    d = WORK / a.id
    comm = _read(d, "8_community.json", {}) if d.exists() else {}
    fiche["community"] = comm
    if comm:
        state.save(f"commentaires_{a.profile}", [])
    _push_drop(a.id, {"fiche.json": json.dumps(fiche, ensure_ascii=False, indent=2)})
    state.save("dernier_depot", {"id": a.id, "profil": a.profile, "date": state.now_iso()})
    _commit_state(f"état : {a.id} abandonnée")
    print("Propriétaire prévenu.")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup")
    p = sub.add_parser("new"); p.add_argument("--profile", required=True)
    p = sub.add_parser("check"); p.add_argument("spec"); p.add_argument("--profile", required=True)
    p = sub.add_parser("render"); p.add_argument("spec"); p.add_argument("out")
    p = sub.add_parser("frames"); p.add_argument("spec"); p.add_argument("video")
    p = sub.add_parser("caption"); p.add_argument("id"); p.add_argument("--profile", required=True)
    p = sub.add_parser("drop"); p.add_argument("id"); p.add_argument("--profile", required=True); p.add_argument("--le", help="publication à une date précise (ISO, ex. 2026-10-19T10:50:00+02:00)")
    p.add_argument("--heure", type=int, help="heure de publication de CETTE vidéo (sinon celle du profil)")
    p = sub.add_parser("info"); p.add_argument("id"); p.add_argument("--profile", required=True)
    p = sub.add_parser("rapport"); p.add_argument("--agent", required=True); p.add_argument("--profile", required=True)
    p.add_argument("--titre", required=True); p.add_argument("fichier")
    p = sub.add_parser("abandon"); p.add_argument("id"); p.add_argument("--profile", required=True)
    p.add_argument("--raison", required=True)
    p = sub.add_parser("story"); p.add_argument("id"); p.add_argument("--profile", required=True); p.add_argument("--titre")
    p = sub.add_parser("story_now"); p.add_argument("--profile", required=True); p.add_argument("--titre", required=True); p.add_argument("image")
    p = sub.add_parser("creneau"); p.add_argument("--profile", required=True); p.add_argument("--horizon", type=float)
    p = sub.add_parser("avance")
    p = sub.add_parser("etape"); p.add_argument("--agent", required=True); p.add_argument("--profile", required=True)
    p.add_argument("--titre", required=True); p.add_argument("resume")
    p = sub.add_parser("activite"); p.add_argument("--agent", required=True); p.add_argument("--etat", required=True)
    p.add_argument("--salle", help="ex. reunion-1-veille, reunion-2-production"); p.add_argument("--profile")
    p = sub.add_parser("notes"); p.add_argument("--agent", required=True); p.add_argument("--profile")
    p = sub.add_parser("lu"); p.add_argument("--agent", required=True); p.add_argument("ids", nargs="+")
    a = ap.parse_args()
    globals()[f"cmd_{a.cmd}"](a)


if __name__ == "__main__":
    main()
