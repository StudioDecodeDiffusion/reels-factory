"""Test de bout en bout SANS API : les agents renvoient des réponses factices, le rendu vidéo est réel.

Lancer : python -m tests.test_offline
"""
from __future__ import annotations

import json
import os

from pipeline import llm, run, state
from pipeline.config import OUTPUT

FAKE = {
    "VEILLE ACTUALITÉ": {"sujets": [{"titre": "Record de chaleur océanique", "resume": "…", "chiffres_cles": ["21,1 °C"],
                                    "source_url": "https://example.org", "date_info": "aujourd'hui",
                                    "angle_visuel": "compteur", "potentiel_viral": 8}]},
    "ANALYSTE TRENDS": {"formats": [{"nom": "Tu savais que", "description": "…", "pourquoi_ca_marche": "…",
                                     "adaptable_en_animation": True}], "accroches_types": ["question"],
                        "duree_ideale_s": 20, "styles_legende": [], "hashtags_pertinents": ["#science"],
                        "a_eviter": [], "apprentissages_du_compte": "pas encore de données"},
    "CORRÉLATION": {"concepts": [{"titre": "Pourquoi la Lune ne tombe pas", "sujet": "orbites", "format": "question",
                                  "idee_animation": "orbite", "source_url": "", "faits": ["3 683 km/h"],
                                  "notes": {}, "total": 32}], "choix": 0, "justification": "…"},
    "SCÉNARISTE": {"titre_interne": "lune", "plans": [], "legende": "La Lune tombe en permanence 🌙 #lune",
                   "hashtags": ["#science", "#espace", "#physique"]},
    "DIRECTEUR ARTISTIQUE": {"theme": {"fond": "#05070F", "texte": "#E8ECFF", "accent": "#7CF5D4",
                                       "accent2": "#B28CFF", "police_titre": "Space Grotesk",
                                       "police_texte": "Inter", "bandeau": None, "grille": True},
                             "consignes_animation": "calme", "evolution_charte": "aucune"},
    "VALIDATEUR": {"notes": {"accroche": 8, "clarte": 8, "exactitude": 9, "rythme": 8, "charte": 9, "conformite": 9},
                   "verdict": "valide", "corrections_script": [], "corrections_charte": [], "commentaire": "ok"},
    "contrôleur qualité visuel": {"ok": True, "problemes": []},
}


def fake_ask(model, user, **kw):
    if "GÉNÉRATEUR" in user:
        spec = json.loads(open("video/sample-spec.json", encoding="utf-8").read())
        return "<json>" + json.dumps(spec, ensure_ascii=False) + "</json>"
    for key, val in FAKE.items():
        if key in user:
            return "<json>" + json.dumps(val, ensure_ascii=False) + "</json>"
    raise AssertionError("prompt inattendu : " + user[:80])


if __name__ == "__main__":
    llm.ask = fake_ask
    run.agents.ask_json = lambda model, user, **kw: llm.extract_json(fake_ask(model, user, **kw))
    before = len(state.history("science"))
    run.generate("science", local=True)
    jobs = sorted(p for p in OUTPUT.glob("science-*") if p.is_dir())
    mp4 = next(jobs[-1].glob("*.mp4"))
    assert mp4.stat().st_size > 500_000, "vidéo trop petite"
    assert (jobs[-1] / "legende.txt").read_text(encoding="utf-8").count("#science") == 1
    # on remet l'historique dans l'état initial
    h = state.history("science")[:before]
    state.save("historique_science", h) if h else os.remove(state.STATE / "historique_science.json")
    print("TEST OK :", mp4)
