"""Veille externalisée (propriétaire, 25/10) : aucun jeton Claude.
1. Collecte : flux RSS des médias, Google Actualités, Google Trends FR, Wikipédia FR (pages les plus vues),
   GDELT (base mondiale des articles), Reddit r/france, TikTok Creative Center (hashtags et sons FR, si accessible).
2. Corrélation : regroupement des titres par sens (modèle Sentence-Transformers multilingue, open source),
   puis score de potentiel = diversité des sources × vitesse × tendance Google/Wikipédia/TikTok/Reddit × adéquation au compte.
Sortie : state/veille_brute.json (top sujets par compte, avec preuves) — lue par les agents 1, 2, 4 et 13."""
from __future__ import annotations

import json
import math
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import feedparser
import requests

ETAT = Path(__file__).resolve().parent.parent / "state"
UA = {"User-Agent": "Mozilla/5.0 (DecodeStudio veille; contact studiodecodediffusion@gmail.com)"}
MEDIAS = {
    "franceinfo": "https://www.francetvinfo.fr/titres.rss", "Le Monde": "https://www.lemonde.fr/rss/une.xml",
    "Libération": "https://www.liberation.fr/arc/outboundfeeds/rss-all/?outputType=xml",
    "Mediapart": "https://www.mediapart.fr/articles/feed", "Le Figaro": "https://www.lefigaro.fr/rss/figaro_actualites.xml",
    "20 Minutes": "https://www.20minutes.fr/feeds/rss-une.xml", "Ouest-France": "https://www.ouest-france.fr/rss/une",
    "Les Echos": "https://syndication.lesechos.fr/rss/rss_une.xml", "L'Humanité": "https://www.humanite.fr/feed",
    "Futura": "https://www.futura-sciences.com/rss/actualites.xml", "Sciences et Avenir": "https://www.sciencesetavenir.fr/rss.xml",
    "L'Usine Nouvelle": "https://www.usinenouvelle.com/rss/", "Numerama": "https://www.numerama.com/feed/",
}
GNEWS = "https://news.google.com/rss{}?hl=fr&gl=FR&ceid=FR:fr"
REQUETES = {  # Google Actualités ciblé par compte
    "actu": ["gouvernement", "manifestation", "Assemblée nationale", "pouvoir d'achat"],
    "eco": ["économie France", "inflation", "impôts", "budget de l'État", "salaires"],
    "science": ["robot", "ingénierie", "physique découverte", "énergie innovation"],
    "qhse": ["norme ISO", "accident industriel", "Seveso", "inspection du travail", "Qualiopi", "sécurité au travail"],
    "fun": ["insolite", "record du monde", "vidéo virale"],
}
COMPTES = {  # description servant à mesurer l'adéquation sujet ↔ compte
    "actu": "politique française, gouvernement, manifestations, libertés, inégalités, milliardaires, pouvoir d'achat, police, justice sociale",
    "eco": "économie, impôts, dette publique, inflation, salaires, retraites, budget de l'État, entreprises, épargne, prix",
    "science": "science, ingénierie, robots, physique, technologie, énergie, espace, inventions, machines, comment ça marche",
    "qhse": "qualité, sécurité au travail, environnement, normes ISO, audit, accident industriel, Seveso, Code du travail, risques",
    "fun": "insolite, satisfaisant, record, animaux, vidéos virales, objets étonnants, défis",
}


def _get(url, **kw):
    r = requests.get(url, headers=UA, timeout=25, **kw)
    r.raise_for_status()
    return r


def collecter() -> tuple[list[dict], dict, dict]:
    items, signaux, erreurs = [], {"trends": [], "wiki": [], "tiktok_hashtags": [], "tiktok_sons": [], "reddit": []}, {}
    flux = dict(MEDIAS, **{"Google Actualités": GNEWS.format("")})
    for c, qs in REQUETES.items():
        for q in qs:
            flux[f"Google Actualités · {c} · {q}"] = GNEWS.format("/search") + "&q=" + requests.utils.quote(q + " when:2d")
    for src, url in flux.items():
        try:
            for e in feedparser.parse(_get(url).content).entries[:40]:
                d = e.get("published_parsed") or e.get("updated_parsed")
                items.append({"titre": re.sub(r"\s+-\s+[^-]+$", "", e.get("title", "")) if "Google" in src else e.get("title", ""),
                              "lien": e.get("link"), "source": (e.get("source") or {}).get("title") or src.split(" · ")[0],
                              "date": datetime(*d[:6], tzinfo=timezone.utc).isoformat() if d else None})
        except Exception as ex:
            erreurs[src] = str(ex)[:120]
    try:  # GDELT : articles français des 24 dernières heures
        g = _get("https://api.gdeltproject.org/api/v2/doc/doc", params={
            "query": "sourcecountry:france sourcelang:french", "mode": "artlist", "maxrecords": 250,
            "timespan": "24h", "format": "json", "sort": "datedesc"}).json()
        for a in g.get("articles", []):
            items.append({"titre": a.get("title", ""), "lien": a.get("url"), "source": a.get("domain"),
                          "date": datetime.strptime(a["seendate"], "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc).isoformat()
                          if a.get("seendate") else None})
    except Exception as ex:
        erreurs["GDELT"] = str(ex)[:120]
    try:  # Google Trends : recherches qui explosent en France (avec volume approximatif)
        for e in feedparser.parse(_get("https://trends.google.com/trending/rss?geo=FR").content).entries:
            vol = re.sub(r"\D", "", e.get("ht_approx_traffic", "0")) or "0"
            signaux["trends"].append({"terme": e.get("title"), "volume": int(vol)})
    except Exception as ex:
        erreurs["Google Trends"] = str(ex)[:120]
    try:  # Wikipédia FR : articles les plus consultés hier
        j = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y/%m/%d")
        w = _get(f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/fr.wikipedia/all-access/{j}").json()
        signaux["wiki"] = [{"terme": a["article"].replace("_", " "), "vues": a["views"]}
                           for a in w["items"][0]["articles"][:80] if ":" not in a["article"] and a["article"] != "Wikipédia"]
    except Exception as ex:
        erreurs["Wikipédia"] = str(ex)[:120]
    try:
        r = _get("https://www.reddit.com/r/france/hot.json", params={"limit": 60}).json()
        signaux["reddit"] = [{"terme": p["data"]["title"], "score": p["data"]["score"]} for p in r["data"]["children"]]
    except Exception as ex:
        erreurs["Reddit"] = str(ex)[:120]
    base = "https://ads.tiktok.com/creative_radar_api/v1/popular_trend"
    for cle, chemin in (("tiktok_hashtags", "/hashtag/list"), ("tiktok_sons", "/sound/rank_list")):
        try:  # TikTok Creative Center (France, 7 jours) : accès public non garanti
            t = _get(base + chemin, params={"page": 1, "limit": 30, "period": 7, "country_code": "FR", "sort_by": "popular"},
                     headers={**UA, "Referer": "https://ads.tiktok.com/business/creativecenter/"}).json()
            liste = (t.get("data") or {}).get("list") or (t.get("data") or {}).get("sound_list") or []
            signaux[cle] = [{"terme": x.get("hashtag_name") or x.get("title"), "rang": x.get("rank"),
                             "vues": x.get("video_views") or x.get("publish_cnt")} for x in liste]
            if not liste:
                erreurs["TikTok " + cle] = f"réponse vide ({t.get('msg') or t.get('code')})"
        except Exception as ex:
            erreurs["TikTok " + cle] = str(ex)[:120]
    return items, signaux, erreurs


def correler(items: list[dict], signaux: dict) -> dict:
    """Regroupe les titres par sens et note chaque sujet pour chaque compte."""
    from sentence_transformers import SentenceTransformer
    from sklearn.cluster import AgglomerativeClustering
    import numpy as np
    vus, uniques = set(), []
    for it in items:
        k = re.sub(r"\W+", " ", it["titre"].lower()).strip()[:90]
        if len(k) > 25 and k not in vus:
            vus.add(k)
            uniques.append(it)
    if len(uniques) < 5:
        return {}
    m = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    E = m.encode([u["titre"] for u in uniques], normalize_embeddings=True, batch_size=64)
    lab = AgglomerativeClustering(n_clusters=None, distance_threshold=0.55, metric="cosine", linkage="average").fit_predict(E)
    termes = [("trends", s["terme"], math.log10(1 + s["volume"])) for s in signaux["trends"]] + \
             [("wiki", s["terme"], math.log10(1 + s["vues"]) / 2) for s in signaux["wiki"]] + \
             [("tiktok", s["terme"], 2.0) for s in signaux["tiktok_hashtags"] if s["terme"]] + \
             [("reddit", s["terme"], math.log10(1 + s["score"]) / 2) for s in signaux["reddit"]]
    T = m.encode([t[1] for t in termes], normalize_embeddings=True) if termes else np.zeros((0, E.shape[1]))
    C = m.encode(list(COMPTES.values()), normalize_embeddings=True)
    maintenant = datetime.now(timezone.utc)
    sujets = []
    for c in set(lab):
        idx = [i for i in range(len(uniques)) if lab[i] == c]
        if len(idx) < 2:
            continue
        cen = E[idx].mean(0)
        cen /= np.linalg.norm(cen)
        sources = {uniques[i]["source"] for i in idx}
        recents = sum(1 for i in idx if uniques[i]["date"] and maintenant - datetime.fromisoformat(uniques[i]["date"]) < timedelta(hours=8))
        preuves, bonus = [], 0.0
        for (typ, terme, poids), sim in zip(termes, T @ cen if len(T) else []):
            if sim > 0.55:
                preuves.append(f"{typ} : {terme}")
                bonus += poids * sim
        rep = max(idx, key=lambda i: float(E[i] @ cen))
        base = math.log2(1 + len(sources)) * 2 + math.log2(1 + len(idx)) + 3 * recents / len(idx) + bonus
        sujets.append({"sujet": uniques[rep]["titre"], "score_base": round(base, 2), "nb_articles": len(idx),
                       "sources": sorted(sources)[:12], "vitesse_8h": round(recents / len(idx), 2), "preuves_tendance": preuves[:8],
                       "titres": [uniques[i]["titre"] for i in idx[:6]], "liens": [uniques[i]["lien"] for i in idx[:6]],
                       "adequation": {k: round(float(C[j] @ cen), 3) for j, k in enumerate(COMPTES)}})
    out = {}
    for k in COMPTES:
        tri = sorted(sujets, key=lambda s: s["score_base"] * max(0.0, s["adequation"][k] - 0.15) * 4, reverse=True)
        out[k] = [dict(s, score=round(s["score_base"] * max(0.0, s["adequation"][k] - 0.15) * 4, 2)) for s in tri[:8]]
    return out


def main() -> None:
    items, signaux, erreurs = collecter()
    top = correler(items, signaux)
    (ETAT / "veille_brute.json").write_text(json.dumps({
        "maj": datetime.now(timezone.utc).isoformat(timespec="minutes"), "nb_articles": len(items), "erreurs": erreurs,
        "top_par_compte": top, "tendances": {k: v[:30] for k, v in signaux.items()}}, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    print(f"{len(items)} articles, {sum(len(v) for v in signaux.values())} signaux, erreurs : {list(erreurs)}")


if __name__ == "__main__":
    main()
