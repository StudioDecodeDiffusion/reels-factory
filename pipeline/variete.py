"""Carnet de variété : chaque vidéo doit différer des précédentes (règle du propriétaire)."""
from __future__ import annotations

from . import state

CHAMPS = ["accroche", "trend", "fonctionnement", "mise_en_page", "musique", "voix", "palette"]
JAMAIS_DEUX_FOIS = ["accroche", "fonctionnement", "mise_en_page", "musique", "voix"]


def controler(spec: dict, compte: str) -> list[str]:
    v = spec.get("variete") or {}
    errs = [f"variete.{c} manquant (voir agents/CATALOGUE_VARIETE.md)" for c in CHAMPS if not str(v.get(c, "")).strip()]
    if errs:
        return errs
    hist = state.load(f"variete_{compte}", [])[-5:]
    norm = lambda x: str(x).strip().lower()
    if hist:
        prec = hist[-1]
        for c in JAMAIS_DEUX_FOIS:
            if norm(prec.get(c)) == norm(v[c]) and not (c == "mise_en_page" and norm(v[c]) == "pixeldoc"):
                # pixeldoc = habillage constant de la série (règle 8 de RETRO_COMPTES_IA.md), il peut se répéter
                errs.append(f"variete.{c} = « {v[c]} » : identique à la vidéo précédente ({prec.get('titre', '')}). Change-le.")
    for h in hist:
        communs = [c for c in CHAMPS if norm(h.get(c)) == norm(v[c])]
        if len(communs) >= 3:
            errs.append(f"trop proche de « {h.get('titre', '')} » ({', '.join(communs)}) : il faut une vidéo vraiment différente.")
    g = spec.get("musique")
    if not (isinstance(g, dict) and g.get("genre")):
        errs.append("musique.genre manquant : la musique doit être un morceau composé (voir CATALOGUE_VARIETE.md)")
    elif norm(g["genre"]) != norm(v["musique"]):
        errs.append("variete.musique doit être le genre de musique.genre")
    return errs


def enregistrer(spec: dict, compte: str, titre: str, job: str) -> None:
    hist = state.load(f"variete_{compte}", [])
    hist = [h for h in hist if h.get("job") != job]
    hist.append({**(spec.get("variete") or {}), "titre": titre, "job": job, "date": state.now_iso()[:10]})
    state.save(f"variete_{compte}", hist[-30:])
