"""Les 8 agents. Chacun = un prompt (dossier prompts/) + un modèle + éventuellement la recherche web."""
from __future__ import annotations

import json

import yaml

from . import state
from .config import MODEL_FAST, MODEL_SMART, TRENDS, prompt, today_fr
from .llm import ask_json


def _p(profile: dict) -> str:
    keep = {k: v for k, v in profile.items() if k not in ("charte_initiale", "instagram_secret")}
    return yaml.safe_dump(keep, allow_unicode=True, sort_keys=False)


def _j(x) -> str:
    return json.dumps(x, ensure_ascii=False, indent=1)


def _hist(pid: str, n: int = 30) -> str:
    h = state.history(pid)[-n:]
    txt = "\n".join(f"- {x.get('date', '')} : {x.get('titre', '')}" for x in h) or "(aucun)"
    refus = state.load(f"refus_{pid}", [])[-10:]
    if refus:
        txt += "\n\nVidéos REFUSÉES par le propriétaire (tiens compte de ses raisons) :\n" + "\n".join(
            f"- {r['titre']} → raison : {r.get('raison') or 'non précisée'}" for r in refus)
    return txt


# 1 ─ Veille actualité
def veille_actu(profile: dict) -> dict:
    if profile.get("veille", {}).get("actualite", True) is False:
        return {"sujets": [], "note": "veille d'actualité désactivée pour ce profil"}
    return ask_json(MODEL_FAST, prompt("1_veille_actu", profil=_p(profile), date=today_fr(),
                                       historique=_hist(profile["id"])),
                    web_search=8, country=profile.get("veille", {}).get("pays", "FR"))


# 2 ─ Analyste trends
def trends(profile: dict) -> dict:
    notes_path = TRENDS / f"{profile['id']}.md"
    notes = notes_path.read_text(encoding="utf-8") if notes_path.exists() else "(aucune note)"
    stats = state.load(f"stats_{profile['id']}", {})
    reco = stats.get("recommandations", [])
    top = sorted(stats.get("posts", []), key=lambda p: p.get("vues", 0), reverse=True)[:8]
    return ask_json(MODEL_FAST, prompt("2_trends", profil=_p(profile), date=today_fr(), notes_manuelles=notes,
                                       stats=_j({"meilleures": top, "recommandations_community_manager": reco})
                                       if top or reco else "(pas encore de publications)"),
                    web_search=6, country=profile.get("veille", {}).get("pays", "FR"))


# 3 ─ Corrélation sujets × trends
def correlation(profile: dict, sujets: dict, tr: dict) -> dict:
    sujets_txt = _j(sujets) if sujets.get("sujets") else (
        "(pas de veille d'actualité pour ce compte : invente des sujets intemporels adaptés à la niche, "
        "sans aucun chiffre inventé ; si un fait est nécessaire, il doit être universellement connu)")
    return ask_json(MODEL_SMART, prompt("3_correlation", profil=_p(profile), sujets=sujets_txt, trends=_j(tr),
                                        historique=_hist(profile["id"]),
                                        scenes_autorisees=", ".join(profile["video"]["scenes_autorisees"])))


# 4 ─ Scénariste
def scenariste(profile: dict, concept: dict, tr: dict, retour: dict | None = None) -> dict:
    retour_txt = ""
    if retour:
        retour_txt = ("Le validateur a demandé des corrections sur ta version précédente. Applique-les toutes :\n"
                      + _j(retour))
    v = profile["video"]
    return ask_json(MODEL_SMART, prompt("4_scenariste", profil=_p(profile), concept=_j(concept), trends=_j(tr),
                                        retour_validateur=retour_txt, duree=v["duree_cible_s"],
                                        scenes_autorisees=", ".join(v["scenes_autorisees"]), cta=v["cta"],
                                        hashtags_max=profile["publication"].get("hashtags_max", 5)))


# 5 ─ Directeur artistique
def directeur_artistique(profile: dict, script: dict, corrections: list[str] | None = None) -> dict:
    ch = state.charte(profile)
    extra = ""
    if corrections:
        extra = "\n\nCorrections demandées par le validateur :\n" + "\n".join(f"- {c}" for c in corrections)
    da = ask_json(MODEL_SMART, prompt("5_directeur_artistique", profil=_p(profile), charte=_j(ch),
                                      script=_j(script), date=today_fr()) + extra)
    evo = (da.get("evolution_charte") or "aucune").strip()
    if evo.lower() != "aucune":
        ch = dict(ch)
        ch.update({k: da["theme"][k] for k in ("fond", "texte", "accent", "police_titre", "police_texte")
                   if k in da.get("theme", {})})
        ch.setdefault("journal", []).append({"date": today_fr(), "changement": evo})
        state.set_charte(profile["id"], ch)
    return da


# 6 ─ Validateur
def validateur(profile: dict, concept: dict, script: dict, da: dict) -> dict:
    is_actu = profile.get("veille", {}).get("actualite", True) and profile["id"] == "actu"
    verif = ("Utilise la recherche web pour revérifier les 2 ou 3 chiffres les plus importants du script "
             "auprès de sources fiables avant de noter l'exactitude.") if is_actu else ""
    return ask_json(MODEL_SMART, prompt("6_validateur", profil=_p(profile), concept=_j(concept), script=_j(script),
                                        da=_j(da), verification=verif),
                    web_search=4 if is_actu else 0)


# 7 ─ Générateur (script → spécification vidéo)
def generateur(profile: dict, script: dict, da: dict, erreurs: list[str] | None = None) -> dict:
    err = ""
    if erreurs:
        err = "Ta spécification précédente avait ces problèmes, corrige-les :\n" + "\n".join(f"- {e}" for e in erreurs)
    return ask_json(MODEL_SMART, prompt("7_generateur", script=_j(script), theme=_j(da["theme"]),
                                        consignes=da.get("consignes_animation", ""), erreurs_precedentes=err,
                                        scenes_autorisees=", ".join(profile["video"]["scenes_autorisees"])))


def controle_visuel(script: dict, images) -> dict:
    return ask_json(MODEL_SMART, prompt("7b_controle_visuel", script=_j(script)), images=list(images))


# 8 ─ Community manager
def community_manager(profile: dict, stats: list[dict], commentaires: list[dict]) -> dict:
    return ask_json(MODEL_SMART, prompt("8_community_manager", profil=_p(profile), stats=_j(stats),
                                        commentaires=_j(commentaires) if commentaires else "(aucun)"))
