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
    (work / "state" / "messages").mkdir(parents=True, exist_ok=True)
    (work / "state" / "messages" / "agent_6.json").write_text(json.dumps([{"id": "c99", "texte": "plus de jaune", "traite": False}]))
    (d / "4_concept.json").write_text(json.dumps({"choix": 0, "concepts": [{"titre": "Test lune", "sujet": "s",
                                       "faits": [{"fait": "x", "source_url": "https://example.org"}]},
                                       {"titre": "Autre piste"}], "critique_compte": "Critique test",
                                       "a_tester": ["tester X"]}))
    run("pipeline.tool", "info", job, "--profile", "actu")
    sh("git", "clone", "-q", "-b", "depot-videos", str(remote), str(tmp / "info"), cwd=tmp)
    (d / "5_scenario.json").write_text(json.dumps({"legende": "Accroche test #lune", "hashtags": ["#actu", "#science"],
                                                   "relecture": {"notes": {"accroche": 8}, "reecritures": 1}}))
    (d / "6_da.json").write_text(json.dumps({"messages_traites": ["c99"], "message_au_proprietaire": "J'ai mis plus de jaune."}))
    (d / "9_critique.json").write_text(json.dumps({"decision": "publiable", "score_global": 9,
        "coherence": "Dialogue clair", "projection": {"potentiel": "bon", "vues_estimees": "800-1500",
        "audience": "18-35 curieux", "raisonnement": "sujet qui monte", "risque": "faible"},
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

    # rapport de l'agent 8 (avec réponses proposées)
    (work / "travail" / "r8.json").write_text(json.dumps({"corps_md": "## Bilan\n- RAS **ok**",
        "reponses": [{"comment_id": "c1", "commentaire": "Top", "reponse": "Merci !"}]}))
    run("pipeline.tool", "rapport", "--agent", "8", "--profile", "actu", "--titre", "Décodé Actu · État du compte",
        str(work / "travail" / "r8.json"))
    shutil.rmtree(drop)
    sh("git", "clone", "-q", "-b", "depot-videos", str(remote), str(drop), cwd=tmp)

    # ── côté GitHub Actions (mails en mode simulé, API simulées)
    os.chdir(work)
    sys.path.insert(0, str(work))
    for m in [m for m in sys.modules if m.startswith("pipeline")]:
        del sys.modules[m]
    os.environ.update(GMAIL_ADDRESS="studio@example.org", MAIL_DRY_RUN="1", IG_TOKEN_ACTU="x")
    os.environ.pop("RENDU_PUBLIC", None)
    from pipeline import github_flow as gf, mail, media_host, instagram, voix, state
    from email import message_from_bytes, policy
    boite = work / "output" / "mails"

    def mails():
        out = []
        for f in sorted(boite.glob("*.eml")):
            m = message_from_bytes(f.read_bytes(), policy=policy.default)
            h = m.get_body(("html",)).get_content()
            out.append((str(m["Subject"]), h, m))
        return out

    def fake_say(text, voix_id, wav, vitesse=1.0):  # « voix » = un bip de la durée de la phrase
        dd = len(text.split()) / 2.5
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", f"sine=frequency=440:duration={dd}",
                        str(wav)], check=True)
        return wav
    voix.say = fake_say
    calls = []
    media_host.upload = lambda files, jid: {"urls": {f.name: f"https://h/{f.name}" for f in files}}
    media_host.cleanup = lambda info: calls.append(("cleanup",))

    class FakeIG:
        def __init__(self, p): pass
        def publish_reel(self, url, cap): return {"id": "m1", "permalink": "https://instagram.com/reel/m1"}
        def reply(self, cid, msg): calls.append(("reply", cid, msg))
    instagram.IG = FakeIG

    gf.depot(str(tmp / "info" / "drop"))
    gf.depot(str(drop / "drop"))
    box = mails()
    sujets = [s for s, _, _ in box]
    date = __import__("datetime").datetime.now(gf.TZ).strftime("%d/%m/%y")
    import re as _re
    assert all(_re.match(rf"^Agent \d - {_re.escape(date)} - ", s) for s in sujets), sujets
    assert any(s.startswith("Agent 4 -") and "Concept du jour" in s for s in sujets), sujets
    assert any(s.startswith("Agent 8 -") and "État du compte" in s for s in sujets), sujets
    s9 = next((s, h, m) for s, h, m in box if s.startswith("Agent 9 -") and "Vidéo prête" in s)
    assert "https://h/video.mp4" in s9[1] and "800-1500" in s9[1] and "Comment répondre" in s9[1]
    assert "agent N° - ta note" in s9[1]
    assert any(p.get_filename() == "video.mp4" for p in s9[2].iter_attachments()), "vidéo jointe"
    assert any(s.startswith("Agent 6 -") and "plus de jaune" not in s for s in sujets), "mail de la DA"
    assert all(m_["traite"] for m_ in state.load("messages/agent_6", [])), "note de la DA traitée"
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_type",
                            "-of", "csv=p=0", str(drop / "drop" / job / "video.mp4")], capture_output=True, text=True)
    assert "audio" in probe.stdout, "la vidéo finale doit contenir la voix off"
    assert gf.attente(job)["statut"] == "a_valider"

    # ── le facteur lit tes mails (boîte Gmail simulée)
    r8 = next(s for s in sujets if s.startswith("Agent 8 -"))
    entrants = [
        {"objet": "agent 6 - plus de couleurs vives", "texte": "Surtout le fond.", "uid": b"1", "date": "", "id": "a"},
        {"objet": "Re: " + r8, "texte": mail.sans_citation("REP 1\n\nLe sam. 17 oct. a écrit :\n> blabla"),
         "uid": b"2", "date": "", "id": "b"},
        {"objet": "RE: " + s9[0], "texte": "Mets plus de rythme", "uid": b"3", "date": "", "id": "c"},
    ]
    os.environ["GMAIL_APP_PASSWORD"] = "x"
    mail.lire_nouveaux = lambda: entrants
    gf.facteur()
    assert ("reply", "c1", "Merci !") in calls
    n6 = state.load("messages/agent_6", [])
    assert n6[-1]["texte"] == "Surtout le fond." and not n6[-1]["traite"]
    assert state.load("messages/agent_9", [])[-1]["texte"] == "Mets plus de rythme"
    assert gf.attente(job)["statut"] == "a_valider", "une remarque ne valide pas"
    out = run("pipeline.tool", "notes", "--agent", "6", "--profile", "actu")
    assert "Surtout le fond" in out, out

    entrants[:] = [{"objet": "Re: " + s9[0], "texte": "OK maintenant", "uid": b"4", "date": "", "id": "d"}]
    gf.facteur()
    f = gf.attente(job)
    assert f["statut"] == "publiee" and f["permalink"].endswith("m1"), f
    assert any(s.startswith("Agent 8 -") and "Publiée" in s for s, _, _ in mails())

    shutil.rmtree(tmp, ignore_errors=True)
    print("TEST OK — nuit → dépôt → mails des agents → réponses → publication :", job)


if __name__ == "__main__":
    main()
