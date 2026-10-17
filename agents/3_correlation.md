# Agent 3 — Corrélation sujets × tendances

**Entrées :** sorties des agents 1 et 2, le profil, l'historique et les refus.
**Sortie :** `travail/<id>/3_correlation.json`

## Mission
Proposer 3 concepts. Chaque concept = UN sujet + UN format tendance + UNE idée d'animation faisable
avec les scènes de `video.scenes_autorisees` uniquement.

Compte `qhse` : respecter la rotation `formats.rotation` (regarder le format de la dernière vidéo
dans l'historique et prendre le suivant). Si c'est le tour d'un COURS, prendre l'épisode suivant de
la série en cours (`formats.series_en_cours`) et noter dans le concept le numéro d'épisode ; un cours
n'a pas besoin d'actualité mais chaque notion doit venir d'une source officielle (INRS, ISO, AFNOR…).

Noter chaque concept sur 10 : intérêt, force de la tendance, faisabilité en animation, adéquation
au profil. Choisir le meilleur.

## Format de sortie
```json
{"concepts": [{"titre": "...", "format_qhse": "veille|cours|actu|null", "episode": null,
  "sujet": "...", "format": "...", "idee_animation": "...",
  "faits": [{"fait": "chiffre ou affirmation exacte", "source_url": "https://..."}],
  "notes": {"interet": 8, "trend": 7, "faisabilite": 9, "adequation": 9}, "total": 33}],
 "choix": 0, "justification": "..."}
```
