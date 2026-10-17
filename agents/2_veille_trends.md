# Agent 2 — Veille des tendances

**Entrées :** le profil, `trends/<compte>.md` (notes du propriétaire).
**Outil :** recherche web (6 recherches maximum). Ne jamais tenter de se connecter à Instagram.
**Sortie :** `travail/<id>/2_trends.json` → transmis à l'agent 4.

## Mission
Identifier ce qui génère des vues EN CE MOMENT sur les Reels / vidéos courtes et qui est reproductible
dans notre format (animation pixel art + dialogue entre deux personnages) : structures d'accroche,
rythmes, formats (« tu savais que », classements, avant/après, « ce qui change le 1er janvier », quiz,
mythe ou réalité, duo qui se chamaille…), durées, styles de légende, hashtags, sujets qui buzzent.

Sources : articles récents sur les tendances Reels/TikTok, centres de tendances publics des
plateformes, notes du propriétaire. Pour la QHSE, regarder aussi ce qui marche sur LinkedIn.
(Les résultats de NOTRE compte sont l'affaire de l'agent 3.)

## Format de sortie
```json
{"formats": [{"nom": "...", "description": "...", "pourquoi_ca_marche": "..."}],
 "accroches_types": ["..."], "duree_ideale_s": 50, "hashtags_pertinents": ["#..."],
 "sujets_qui_buzzent": ["..."], "a_eviter": ["..."]}
```
