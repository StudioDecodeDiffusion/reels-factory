"""Outils utilisés par la session Claude de nuit (voir NUIT.md).

  python -m pipeline.tool setup                              installe le moteur vidéo
  python -m pipeline.tool new --profile actu                 crée travail/<id>/ et affiche l'id
  python -m pipeline.tool check <spec.json> --profile actu   valide une spécification vidéo
  python -m pipeline.tool render <spec.json> <video.mp4>     rend la vidéo
  python -m pipeline.tool frames <spec.json> <video.mp4>     extrait 1 image par scène + planche aperçu
  python -m pipeline.tool caption <id> --profile actu        assemble la légende finale (legende.txt)
  python -m pipeline.tool info <id> --profile actu           agent 4 → e-mail d'information (concept + critique)
  python -m pipeline.tool drop <id> --profile actu           envoie le tout à GitHub (→ e-mail de validation)
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
    text = f"{cap}\n\n{tags}\n\n{profile.get('mention_ia', 'Animation créée avec l’IA.')} {credits}".strip()[:2200]
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
    _git("pull", "-q", "--rebase")
    _git("push", "-q")


def _read(d: Path, name: str, default=None):
    p = d / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def _concept(d: Path) -> dict:
    c = _read(d, "4_concept.json")
    return c["concepts"][int(c.get("choix", 0))]


def _da_suivi(d: Path, pid: str) -> str:
    """Marque comme traités les messages du propriétaire lus par le directeur artistique ; renvoie sa réponse."""
    da = _read(d, "6_da.json", {})
    faits = set(map(str, da.get("messages_traites", [])))
    if faits:
        fil = state.load(f"da_{pid}", [])
        for m in fil:
            if str(m.get("id")) in faits:
                m["traite"] = True
        state.save(f"da_{pid}", fil)
    return str(da.get("message_au_proprietaire") or "").strip()


def cmd_info(a) -> None:
    """Agent 4 → propriétaire, pour information : concept du jour + critique du compte (sans validation)."""
    load_profile(a.profile)
    d = WORK / a.id
    c = _read(d, "4_concept.json")
    if not c:
        raise SystemExit(f"{d / '4_concept.json'} manquant")
    res = _read(d, "3_resultats.json", {})
    fiche = {"id": f"{a.id}-info", "profil": a.profile, "statut": "info", "cree": state.now_iso(),
             "titre": _concept(d).get("titre"), "concept": _concept(d),
             "autres": [x.get("titre") for i, x in enumerate(c.get("concepts", [])) if i != int(c.get("choix", 0))],
             "justification": c.get("justification"), "critique": c.get("critique_compte"),
             "a_tester": c.get("a_tester", []), "enseignements": res.get("enseignements", [])}
    _push_drop(fiche["id"], {"fiche.json": json.dumps(fiche, ensure_ascii=False, indent=2)})
    state.save("dernier_depot", {"id": fiche["id"], "profil": a.profile, "date": state.now_iso()})
    _commit_state(f"état : concept {a.id}")
    print("Concept du jour envoyé pour information.")


def cmd_drop(a) -> None:
    load_profile(a.profile)  # vérifie que le compte existe
    d = WORK / a.id
    needed = ["video.mp4", "apercu.png", "legende.txt", "4_concept.json", "5_scenario.json", "7_spec.json",
              "7_controle.json"]
    missing = [n for n in needed if not (d / n).exists()]
    if missing:
        raise SystemExit(f"Fichiers manquants dans {d} : {missing}")
    controle = _read(d, "7_controle.json")
    if controle.get("decision") != "publiable":
        raise SystemExit("Le contrôle qualité n'a pas déclaré la vidéo « publiable » : corriger ou utiliser `abandon`.")
    concept = _concept(d)
    relecture = _read(d, "5_scenario.json", {}).get("relecture", {})
    fiche = {
        "id": a.id, "profil": a.profile, "statut": "a_valider", "titre": concept.get("titre"),
        "format_qhse": concept.get("format_qhse"), "episode": concept.get("episode"),
        "legende": (d / "legende.txt").read_text(encoding="utf-8"),
        "sources": sorted({f.get("source_url") for f in concept.get("faits", []) if f.get("source_url")}
                          | set(controle.get("sources_verifiees", []))),
        "validation": {"notes": relecture.get("notes", {})},
        "tours_validation": int(relecture.get("reecritures", 0)) + 1,
        "verification": controle,
        "community": _read(d, "8_community.json", {}),
        "da_message": _da_suivi(d, a.profile),
        "cree": state.now_iso(),
    }
    _push_drop(a.id, {"video.mp4": d / "video.mp4", "apercu.png": d / "apercu.png",
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
    p = sub.add_parser("drop"); p.add_argument("id"); p.add_argument("--profile", required=True)
    p = sub.add_parser("info"); p.add_argument("id"); p.add_argument("--profile", required=True)
    p = sub.add_parser("abandon"); p.add_argument("id"); p.add_argument("--profile", required=True)
    p.add_argument("--raison", required=True)
    a = ap.parse_args()
    globals()[f"cmd_{a.cmd}"](a)


if __name__ == "__main__":
    main()
