"""Test de bout en bout sans aucun compte : session de nuit simulée → dépôt → fiche → OK → publication.

GitHub, l'hébergement et Instagram sont simulés ; le rendu vidéo et git sont réels (dépôt temporaire).
Lancer depuis la racine : python -m tests.test_offline
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def sh(*args, cwd):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True)


def main():
    tmp = Path(tempfile.mkdtemp())
    remote, work = tmp / "remote.git", tmp / "repo"
    sh("git", "init", "-q", "--bare", "-b", "main", str(remote), cwd=tmp)
    shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns("node_modules", "travail", "output", ".git", "__pycache__"))
    os.symlink(ROOT / "video" / "node_modules", work / "video" / "node_modules")
    sh("git", "init", "-q", "-b", "main", cwd=work)
    sh("git", "remote", "add", "origin", str(remote), cwd=work)
    sh("git", "add", "-A", cwd=work)
    sh("git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init", cwd=work)
    sh("git", "push", "-q", "-u", "origin", "main", cwd=work)

    py = [sys.executable, "-m"]
    run = lambda *a: subprocess.run([*py, *a], cwd=work, check=True, capture_output=True, text=True).stdout.strip()

    # ── session de nuit (les agents sont remplacés par des fichiers tout faits)
    job = run("pipeline.tool", "new", "--profile", "actu")
    d = work / "travail" / job
    spec = json.loads((ROOT / "video" / "sample-spec.json").read_text())
    spec["scenes"] = [s for s in spec["scenes"] if s["type"] != "particles"]  # non autorisé pour actu
    (d / "7_spec.json").write_text(json.dumps(spec))
    assert run("pipeline.tool", "check", str(d / "7_spec.json"), "--profile", "actu") == "OK"
    (d / "3_correlation.json").write_text(json.dumps({"choix": 0, "concepts": [{"titre": "Test lune",
                                       "faits": [{"fait": "x", "source_url": "https://example.org"}]}]}))
    (d / "4_script.json").write_text(json.dumps({"legende": "Accroche test #lune", "hashtags": ["#actu", "#science"]}))
    (d / "6_validation_tour1.json").write_text(json.dumps({"notes": {"accroche": 8}, "verdict": "valide"}))
    (d / "8_community.json").write_text(json.dumps({"bilan": "RAS", "recommandations": ["plus de chiffres"],
                                                   "reponses": [{"comment_id": "c1", "commentaire": "Top", "reponse": "Merci !"}]}))
    (d / "9_verification.json").write_text(json.dumps({"decision": "publiable", "score_global": 9,
                                                      "resume_pour_le_proprietaire": "RAS"}))
    run("pipeline.tool", "render", str(d / "7_spec.json"), str(d / "video.mp4"))
    run("pipeline.tool", "frames", str(d / "7_spec.json"), str(d / "video.mp4"))
    cap = run("pipeline.tool", "caption", job, "--profile", "actu")
    assert cap.count("#actu") == 1 and "IA" in cap
    run("pipeline.tool", "drop", job, "--profile", "actu")

    drop = tmp / "drop"
    sh("git", "clone", "-q", "-b", "depot-videos", str(remote), str(drop), cwd=tmp)
    assert (drop / "drop" / job / "video.mp4").exists()
    hist = json.loads(subprocess.run(["git", "show", "origin/main:state/historique_actu.json"], cwd=work,
                                     capture_output=True, text=True, check=True).stdout)
    assert hist[-1]["job"] == job

    # ── côté GitHub Actions (API simulées)
    os.chdir(work)
    sys.path.insert(0, str(work))
    for m in [m for m in sys.modules if m.startswith("pipeline")]:
        del sys.modules[m]
    os.environ.update(GITHUB_REPOSITORY="moi/reels-factory", REPO_OWNER="moi", GITHUB_TOKEN="x",
                      IG_TOKEN_ACTU="x")
    from pipeline import github_flow as gf, media_host, instagram

    calls = []
    gf.gh = lambda method, path, **kw: calls.append((method, path, kw.get("json"))) or {"number": 7}
    media_host.upload = lambda files, jid: {"urls": {f.name: f"https://h/{f.name}" for f in files}}
    media_host.cleanup = lambda info: calls.append(("cleanup",))

    class FakeIG:
        def __init__(self, p): pass
        def publish_reel(self, url, cap): return {"id": "m1", "permalink": "https://instagram.com/reel/m1"}
        def reply(self, cid, msg): calls.append(("reply", cid, msg))
    instagram.IG = FakeIG

    gf.on_drop(str(drop / "drop"))
    body = calls[0][2]["body"]
    assert "@moi" in body and "https://h/video.mp4" in body and "REP 1 3" in body

    os.environ.update(ISSUE_NUMBER="7", COMMENT_AUTHOR="quelquun", COMMENT_BODY="OK")
    gf.on_comment()
    assert gf.attente(job)["statut"] == "a_valider", "un inconnu ne doit pas pouvoir valider"

    os.environ.update(COMMENT_AUTHOR="moi", COMMENT_BODY="REP 1\n\nLe sam. 17 oct. a écrit :\n> blabla")
    gf.on_comment()
    assert ("reply", "c1", "Merci !") in calls

    os.environ["COMMENT_BODY"] = "OK maintenant"
    gf.on_comment()
    f = gf.attente(job)
    assert f["statut"] == "publiee" and f["permalink"].endswith("m1"), f

    shutil.rmtree(tmp, ignore_errors=True)
    print("TEST OK — nuit → dépôt → e-mail → réponse → publication :", job)


if __name__ == "__main__":
    main()
