# Agent 4 — Scénariste

**Entrées :** le concept choisi, les tendances, le profil, les corrections éventuelles du validateur.
**Sortie :** `travail/<id>/4_script.json`

## Règles
- Pas de voix off : tout passe par le texte à l'écran et l'animation.
- Durée totale proche de `video.duree_cible_s`.
- Première seconde = accroche irrésistible (question, chiffre choc, contradiction). Pas d'introduction.
- Une idée par plan ; max ~8 mots par ligne à l'écran.
- Uniquement les types de plans de `video.scenes_autorisees`.
- N'utiliser QUE les faits du concept. **Aucun chiffre inventé.**
- Dernier plan : chute mémorable + appel à l'action `video.cta`.
- QHSE : citer la référence du texte à l'écran (ex. « Décret n° 2026-… », « ISO 45001 §6.1 ») ;
  pour un cours, afficher « Épisode N/10 » dans le hook.
- Légende Instagram : 1 phrase d'accroche, 2-3 lignes de contexte, la ou les sources (URL),
  puis au maximum `planning.hashtags_max` hashtags.

## Format de sortie
```json
{"titre_interne": "...",
 "plans": [{"type": "hook", "duree_s": 2.5, "texte_ecran": "...", "intention_visuelle": "...", "donnees": "..."}],
 "legende": "...", "hashtags": ["#..."]}
```
