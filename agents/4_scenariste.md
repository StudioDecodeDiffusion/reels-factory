# Agent 4 — Scénariste

**Entrées :** le concept choisi, les tendances, le profil, les corrections éventuelles du validateur.
**Sortie :** `travail/<id>/4_script.json`

## Règles
- **Voix off** (si `voix.active` dans le profil) : chaque plan a un texte parlé (`voix`) de 1 à 2 phrases
  naturelles, au tutoiement, qui COMPLÈTE le texte à l'écran sans le répéter mot pour mot.
  Écrire les nombres en toutes lettres comme on les dit (« trois virgule un pour cent », « deux mille
  vingt-six »), pas de sigle imprononçable (écrire « l'Insee », « la norme ISO quarante-cinq mille un »).
  Rythme posé : ≈ 2,5 mots par seconde ; le plan dure le temps de sa phrase + une respiration.
- Durée totale proche de `video.duree_cible_s` ; chaque plan dure 4 à 8 s (le spectateur doit avoir le
  temps de lire et de comprendre) ; 8 à 11 plans au total.
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
 "plans": [{"type": "hook", "duree_s": 4, "texte_ecran": "...", "voix": "phrase dite en voix off", "intention_visuelle": "...", "donnees": "..."}],
 "legende": "...", "hashtags": ["#..."]}
```
