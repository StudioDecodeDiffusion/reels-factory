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
    for sc in spec["scenes"]:
        sc["dialogue"] = [{"qui": "narrateur", "texte": "Alors, c'est quoi ce chiffre ?", "expression": "pense"},
                          {"qui": "mascotte", "texte": "Un chiffre incroyable, tu vas voir !", "expression": "choc"}]
    (d / "7_spec.json").write_text(json.dumps(spec))
    assert run("pipeline.tool", "check", str(d / "7_spec.json"), "--profile", "actu") == "OK"
    (d / "3_resultats.json").write_text(json.dumps({"enseignements": ["pas encore de données"]}))
    (d / "4_concept.json").write_text(json.dumps({"choix": 0, "concepts": [{"titre": "Test lune", "sujet": "s",
                                       "faits": [{"fait": "x", "source_url": "https://example.org"}]},
                                       {"titre": "Autre piste"}], "critique_compte": "Critique test",
                                       "a_tester": ["tester X"]}))
    run("pipeline.tool", "info", job, "--profile", "actu")
    sh("git", "clone", "-q", "-b", "depot-videos", str(remote), str(tmp / "info"), cwd=tmp)
    (d / "5_scenario.json").write_text(json.dumps({"legende": "Accroche test #lune", "hashtags": ["#actu", "#science"],
                                                   "relecture": {"notes": {"accroche": 8}, "reecritures": 1}}))
    (d / "6_da.json").write_text(json.dumps({"messages_traites": ["c99"], "message_au_proprietaire": "J'ai mis plus de jaune."}))
    (d / "8_community.json").write_text(json.dumps({"bilan": "RAS", "recommandations": ["plus de chiffres"],
                                                   "reponses": [{"comment_id": "c1", "commentaire": "Top", "reponse": "Merci !"}]}))
    (d / "7_controle.json").write_text(json.dumps({"decision": "publiable", "score_global": 9,
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
    from pipeline import github_flow as gf, media_host, instagram, voix

    def fake_say(text, voix_id, wav, vitesse=1.0):  # « voix » = un bip de la durée de la phrase
        d = len(text.split()) / 2.5
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", f"sine=frequency=440:duration={d}",
                        str(wav)], check=True)
        return wav
    voix.say = fake_say

    calls = []
    gf.gh = lambda method, path, **kw: calls.append((method, path, kw.get("json"))) or {"number": 6}
    media_host.upload = lambda files, jid: {"urls": {f.name: f"https://h/{f.name}" for f in files}}
    media_host.cleanup = lambda info: calls.append(("cleanup",))

    class FakeIG:
        def __init__(self, p): pass
        def publish_reel(self, url, cap): return {"id": "m1", "permalink": "https://instagram.com/reel/m1"}
        def reply(self, cid, msg): calls.append(("reply", cid, msg))
    instagram.IG = FakeIG

    gf.on_drop(str(tmp / "info" / "drop"))
    assert "Concept du jour" in calls[0][2]["title"] and "Critique test" in calls[0][2]["body"]
    calls.clear()
    gf.gh = lambda method, path, **kw: calls.append((method, path, kw.get("json"))) or (
        [] if path.startswith("/issues?labels=da") else {"number": 7, "labels": []})
    gf.on_drop(str(drop / "drop"))
    body = calls[0][2]["body"]
    assert any("plus de jaune" in str(c[2]) for c in calls), "le message du DA doit être publié"
    assert "@moi" in body and "https://h/video.mp4" in body and "REP 1 3" in body
    assert "voix off :** chatterbox:fr" in body, body
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_type",
                            "-of", "csv=p=0", str(drop / "drop" / job / "video.mp4")], capture_output=True, text=True)
    assert "audio" in probe.stdout, "la vidéo finale doit contenir la voix off"

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
