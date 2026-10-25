---
name: produire-video
description: Produire et déposer une vidéo Décodé pour un créneau (sessions programmées ou demande du propriétaire). Le Manager délègue aux agents 4→5+6→9→7→9 avec leurs modèles.
---
# Produire une vidéo (Manager)
**Compte** = celui donné par la tâche (`actu` par défaut ; aussi `science`, `qhse`, `eco`). Chaque agent lit `profiles/<compte>.yaml` (ligne, DA, spécialité) et la file `state/file_sujets_<compte>.json`.
Le détail des règles est dans `NUIT.md` (modes sobre, durée, légende, miniature) ; ici, l'ordre de délégation.

1. `python3 -m pipeline.tool creneau --profile <compte>` → AUCUN = stop. Mode économie dans `state/quota.json` = stop.
2. Créer `travail/<ID>/` (ID = <compte>-AAAAMMJJ-HHMM).
3. **agent-4-concept** (haiku) → `4_concept.json` (sujet de la file, titre_miniature, mots_choc, surtitre).
4. En parallèle : **agent-5-scenariste** (sonnet) → `5_scenario.json` ; **agent-6-directeur-artistique** (sonnet) → `6_da.json`.
5. **agent-9-critique** (sonnet), pré-critique → `9_precritique.json` (« go » sinon retour 5/6, une fois).
6. **agent-7-generateur** (opus) : spec, `tool check`, `PIXELS_HORS_LIGNE=1 tool render`, `tool frames`, `tool caption`, `tool story`.
7. **agent-9-critique**, critique finale sur la planche → `9_critique.json` (« publiable »).
8. Manager : `python3 -m pipeline.tool drop <ID> --profile <compte> [--le <créneau du sujet>]`, puis marquer le sujet `fait`.
Fin : 3 lignes (sujet, décision, créneau). Aucun mail.
