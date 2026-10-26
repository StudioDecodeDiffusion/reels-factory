"""Gemini (offre gratuite Google AI Studio, clé GEMINI_API_KEY, sans facturation) : prépare, sur GitHub, le brouillon du
concept et du scénario des prochaines vidéos. Les agents Claude (haiku) ne font plus que vérifier et corriger."""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests

from . import state
from .config import all_profiles, load_profile

API = "https://generativelanguage.googleapis.com/v1beta"
TZ = state.TZ if hasattr(state, "TZ") else None


def _cle() -> str:
    return os.environ["GEMINI_API_KEY"].strip()


def modeles() -> list[str]:
    """Modèles « flash » gratuits, du plus récent au plus ancien (les « lite » en dernier recours)."""
    noms = [m["name"] for m in requests.get(f"{API}/models", params={"key": _cle()}, timeout=30).json().get("models", [])
            if "generateContent" in m.get("supportedGenerationMethods", [])]
    ok = [n for n in noms if "flash" in n and not any(x in n for x in ("image", "tts", "exp", "audio", "live"))]
    v = lambda n: [float(x) for x in re.findall(r"\d+(?:\.\d+)?", n)[:1]] or [0]
    return sorted([n for n in ok if "lite" not in n], key=v, reverse=True) + sorted([n for n in ok if "lite" in n], key=v, reverse=True)


def modele() -> str:
    return modeles()[0]


def appel(prompt: str, recherche: bool = False) -> str:
    """Essaie chaque modèle gratuit, avec 3 tentatives espacées si Google est saturé (erreur 503/429)."""
    import time
    corps = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.7}}
    if recherche:
        corps["tools"] = [{"google_search": {}}]
    derniere = None
    for m in sorted(modeles()[:5], key=lambda n: '2.5-flash' not in n):  # 2.5 Flash d'abord : la plus large offre gratuite
        for essai in range(3):
            c = dict(corps, generationConfig=dict(corps["generationConfig"], thinkingConfig={"thinkingBudget": 0})) if "2.5-flash" in m else corps
            try:  # sans « réflexion » sur 2.5 Flash : plus rapide, moins de quota
                r = requests.post(f"{API}/{m}:generateContent", params={"key": _cle()}, json=c, timeout=90).json()
            except requests.RequestException as e:  # délai dépassé : on passe au modèle suivant
                derniere = {"code": 0, "message": str(e)[:200]}
                break
            if "candidates" in r:
                return "".join(p.get("text", "") for p in r["candidates"][0]["content"]["parts"])
            derniere = r.get("error", r)
            if (derniere or {}).get("code") not in (429, 500, 503):
                break
            time.sleep(10 * (essai + 1))
    if recherche:  # la recherche Google n'est pas toujours incluse dans l'offre gratuite : on réessaie sans
        return appel(prompt + "\n(Utilise uniquement des faits sûrs que tu connais, avec leur source.)", recherche=False)
    raise RuntimeError(f"Gemini : {derniere}")


def _json(txt: str) -> dict:
    m = re.search(r"\{.*\}", txt, re.S)
    return json.loads(m.group()) if m else {}


SCHEMA_CONCEPT = """{"concepts":[{"titre":"…","accroche":"phrase dite à la 1re seconde","angle":"…","trend":"format/tendance utilisé",
"faits":[{"fait":"chiffre ou fait exact","source":"média","source_url":"https://…"}],"titre_miniature":"≤ 8 mots, thèse critique",
"mots_choc":["1-3 mots"],"surtitre_miniature":"qui · quand"}],"choix":0}"""
SCHEMA_SCENARIO = """{"plans":[{"type":"hook|fait|chiffre|versus|chute|question","duree_s":3.5,"texte_ecran":"≤ 6 mots",
"dialogue":[{"qui":"narrateur","texte":"…","expression":"neutre|choc|ironie|colere|sourire"}]}],
"legende":"accroche + chiffre\\n\\ncontexte 2 phrases\\n\\nquestion 👇\\nEnvoie-la à quelqu'un qui… 📤\\nSources : X, Y","hashtags":["#…"]}"""


def preparer() -> None:
    """Pour chaque compte, prochain créneau dans les 10 h sans brouillon : concept (avec recherche Google) puis scénario."""
    from .tool import _prochain_creneau
    for pid in all_profiles():
        prof = load_profile(pid)
        if not (prof.get("planning") or {}).get("creneaux"):
            continue
        c = _prochain_creneau(pid, horizon_h=10)
        if not c:
            continue
        cle = f"{pid}-{c[:16].replace('-', '').replace(':', '').replace('T', '-')}"
        d = state.STATE / "brouillons" / cle
        if (d / "5_scenario.json").exists():
            continue
        d.mkdir(parents=True, exist_ok=True)
        file = [x for x in state.load(f"file_sujets_{pid}", {}).get("sujets", []) if not x.get("fait")]
        sujet = next((x for x in file if (x.get("creneau") or "")[:16] == c[:16]), None)
        veille = (state.load("veille_brute", {}).get("top_par_compte") or {}).get(pid, [])[:5]
        regles = (Path(__file__).resolve().parent.parent / "agents" / "REGLES_ACTIVES.md").read_text(encoding="utf-8")
        contexte = (f"Compte Instagram « {prof.get('nom_compte')} ». Ligne : {prof.get('ligne_editoriale', '')} Ton : {prof.get('ton', '')} "
                    f"{prof.get('specialite', '')} {prof.get('perimetre', '')}\nRègles :\n{regles}\n")
        demande = (f"Sujet imposé : {json.dumps(sujet, ensure_ascii=False)}" if sujet else
                   "Choisis le meilleur sujet du jour parmi : " + json.dumps([v["sujet"] for v in veille], ensure_ascii=False))
        try:
            concept = _json(appel(contexte + demande + "\nCherche sur le web les faits exacts et récents (chiffres, dates, sources "
                                  "fiables avec URL). Réponds UNIQUEMENT par un JSON au format :\n" + SCHEMA_CONCEPT, recherche=True))
            (d / "4_concept.json").write_text(json.dumps(concept, ensure_ascii=False, indent=1), encoding="utf-8")
            scen = _json(appel(contexte + "Concept retenu :\n" + json.dumps(concept, ensure_ascii=False) +
                               "\nÉcris le scénario : 12-14 plans, dialogue total 160-170 mots, chiffres écrits en toutes lettres, "
                               "uniquement les faits du concept. Réponds UNIQUEMENT par un JSON au format :\n" + SCHEMA_SCENARIO))
            (d / "5_scenario.json").write_text(json.dumps(scen, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"{cle} : brouillon prêt ({len(scen.get('plans', []))} plans)")
        except Exception as e:
            print(f"{cle} : Gemini indisponible ({e}) — les agents Claude feront le travail")


if __name__ == "__main__":
    if sys.argv[1:] == ["test"]:
        m = modele()
        print(f"✅ Clé Gemini valide · modèle : {m}")
        print(appel("Réponds en une phrase : quelle est la capitale de la France ?"))
    else:
        preparer()
