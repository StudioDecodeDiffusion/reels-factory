"""Veille externalisée (propriétaire, 25/10) : aucun jeton Claude.
1. Collecte : flux RSS des médias, Google Actualités, Google Trends FR, 
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

import time

import feedparser
import requests

ETAT = Path(__file__).resolve().parent.parent / "state"
UA = {"User-Agent": "Mozilla/5.0 (DecodeStudio veille; contact studiodecodediffusion@gmail.com)"}
MEDIAS = {
    # sources diversifiées (presse, médias indépendants, institutions, science) — celles qui échouent sont journalisées puis retirées
    "BFM": "https://www.bfmtv.com/rss/news-24-7/", "France 24": "https://www.france24.com/fr/rss", "RFI": "https://www.rfi.fr/fr/rss",
    "La Croix": "https://www.la-croix.com/RSS", "L'Express": "https://www.lexpress.fr/rss/alaune.xml",
    "Courrier international": "https://www.courrierinternational.com/feed/all/rss.xml",
    "Politis": "https://www.politis.fr/feed/", "Reporterre": "https://reporterre.net/spip.php?page=backend",
    "Basta": "https://basta.media/spip.php?page=backend", "Alternatives économiques": "https://www.alternatives-economiques.fr/rss.xml",
    "Challenges": "https://www.challenges.fr/rss.xml", "La Tribune": "https://www.latribune.fr/rss/rubriques/actualite.html",
    "The Conversation": "https://theconversation.com/fr/articles.atom", "CNRS Le journal": "https://lejournal.cnrs.fr/rss",
    "NASA": "https://www.nasa.gov/news-release/feed/", "ESA": "https://www.esa.int/rssfeed/Our_Activities/Space_News",
    "Vie publique": "https://www.vie-publique.fr/rss/actualites", "Actu-Environnement": "https://www.actu-environnement.com/flux/rss/environnement/",
    "franceinfo": "https://www.francetvinfo.fr/titres.rss", "Le Monde": "https://www.lemonde.fr/rss/une.xml",
    "Libération": "https://www.liberation.fr/arc/outboundfeeds/rss-all/?outputType=xml",
    "Mediapart": "https://www.mediapart.fr/articles/feed", "Le Figaro": "https://www.lefigaro.fr/rss/figaro_actualites.xml",
    "20 Minutes": "https://www.20minutes.fr/feeds/rss-une.xml", "Ouest-France": "https://www.ouest-france.fr/rss/une",
"L'Humanité": "https://www.humanite.fr/feed",
    "Futura": "https://www.futura-sciences.com/rss/actualites.xml", "Sciences et Avenir": "https://www.sciencesetavenir.fr/rss.xml",
    "L'Usine Nouvelle": "https://www.usinenouvelle.com/rss/", "Numerama": "https://www.numerama.com/feed/",
}
GNEWS = "https://news.google.com/rss{}?hl=fr&gl=FR&ceid=FR:fr"
GNEWS_SITES = ["lesechos.fr", "lemonde.fr", "mediapart.fr", "legifrance.gouv.fr", "inrs.fr", "insee.fr", "banque-france.fr", "lepoint.fr"]
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
    kw["headers"] = {**UA, **kw.get("headers", {})}
    for essai in range(3):  # 429 / 503 : on attend un peu (GDELT limite à 1 requête / 5 s)
        r = requests.get(url, timeout=25, **kw)
        if r.status_code not in (429, 503) or essai == 2:
            break
        time.sleep(6 * (essai + 1))
    r.raise_for_status()
    return r


def collecter() -> tuple[list[dict], dict, dict]:
    items, signaux, erreurs = [], {"trends": [], "tiktok_hashtags": [], "tiktok_sons": []}, {}
    flux = dict(MEDIAS, **{"Google Actualités": GNEWS.format("")})
    for c, qs in REQUETES.items():
        for q in qs:
            flux[f"Google Actualités · {c} · {q}"] = GNEWS.format("/search") + "&q=" + requests.utils.quote(q + " when:2d")
    for site in GNEWS_SITES:  # sites qui bloquent les robots : on passe par Google Actualités
        flux[f"Google Actualités · site · {site}"] = GNEWS.format("/search") + "&q=" + requests.utils.quote(f"site:{site} when:2d")
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
    # TikTok Creative Center : accès refusé sans compte publicitaire (« no permission ») — retiré, pas de fausse donnée
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
    lab = AgglomerativeClustering(n_clusters=None, distance_threshold=0.42, metric="cosine", linkage="average").fit_predict(E)
    termes = [("trends", s["terme"], math.log10(1 + s["volume"])) for s in signaux["trends"]] + \
             [("tiktok", s["terme"], 2.0) for s in signaux["tiktok_hashtags"] if s["terme"]]
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
            if sim > 0.62:
                preuves.append(f"{typ} : {terme}")
                bonus += poids * sim
        rep = max(idx, key=lambda i: float(E[i] @ cen))
        base = math.log2(1 + len(sources)) * 2 + math.log2(1 + len(idx)) + 3 * recents / len(idx) + bonus
        sujets.append({"sujet": uniques[rep]["titre"], "score_base": round(base, 2), "nb_articles": len(idx),
                       "sources": sorted(sources)[:12], "vitesse_8h": round(recents / len(idx), 2), "preuves_tendance": preuves[:8],
                       "titres": [uniques[i]["titre"] for i in idx[:6]], "liens": [uniques[i]["lien"] for i in idx[:14]],
                       "adequation": {k: round(float(C[j] @ cen), 3) for j, k in enumerate(COMPTES)}})
    out = {}
    for k in COMPTES:
        tri = sorted(sujets, key=lambda s: s["score_base"] * max(0.0, s["adequation"][k] - 0.22) ** 1.5 * 10, reverse=True)
        out[k] = [dict(s, score=round(s["score_base"] * max(0.0, s["adequation"][k] - 0.22) ** 1.5 * 10, 2)) for s in tri[:8]]
    return out


def _og_image(url: str) -> str | None:
    """Image principale (og:image) d'un article source. Les liens Google Actualités sont d'abord décodés."""
    try:
        if "news.google.com" in url:
            from googlenewsdecoder import gnewsdecoder
            d = gnewsdecoder(url, interval=1)
            if not d.get("status"):
                time.sleep(2)
                d = gnewsdecoder(url, interval=2)
            if not d.get("status"):
                return None
            url = d["decoded_url"]
        html = _get(url).text[:200_000]
        m = re.search(r'<meta[^>]+(?:property|name)=["\'](?:og:image|twitter:image)["\'][^>]+content=["\']([^"\']+)', html) \
            or re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\'](?:og:image|twitter:image)["\']', html)
        img = m.group(1).replace("&amp;", "&") if m else None
        return img if img and img.startswith("http") else None
    except Exception:
        return None


def ajouter_images(top: dict) -> None:
    """Pour les meilleurs sujets de chaque compte : images des articles sources (pour illustrer la vidéo avec du réel)."""
    for liste in top.values():
        for sujet in liste[:8]:
            imgs = []
            for lien in sujet.get("liens", [])[:14]:
                img = _og_image(lien)
                if img and img not in imgs:
                    imgs.append(img)
                if len(imgs) >= 3:
                    break
            sujet["images"] = imgs


def main() -> None:
    items, signaux, erreurs = collecter()
    top = correler(items, signaux)
    ajouter_images(top)
    (ETAT / "veille_brute.json").write_text(json.dumps({
        "maj": datetime.now(timezone.utc).isoformat(timespec="minutes"), "nb_articles": len(items), "erreurs": erreurs,
        "top_par_compte": top, "tendances": {k: v[:30] for k, v in signaux.items()}}, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    print(f"{len(items)} articles, {sum(len(v) for v in signaux.values())} signaux, erreurs : {list(erreurs)}")


if __name__ == "__main__":
    main()
