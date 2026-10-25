---
name: produire-video
description: Produire et déposer une vidéo Décodé pour un créneau (sessions programmées ou demande du propriétaire). Le Manager délègue aux agents 4→5+6→7 (critique)→8 (générateur)→7 avec leurs modèles.
---
# Produire une vidéo (Manager)
**Compte** = celui donné par la tâche (`actu` par défaut ; aussi `science`, `qhse`, `eco`). Chaque agent lit `profiles/<compte>.yaml` (ligne, DA, spécialité) et la file `state/file_sujets_<compte>.json`.
Le détail des règles est dans `NUIT.md` (modes sobre, durée, légende, miniature) ; ici, l'ordre de délégation.

1. `python3 -m pipeline.tool creneau --profile <compte>` → AUCUN = stop. Mode économie dans `state/quota.json` = stop.
2. Créer `travail/<ID>/` (ID = <compte>-AAAAMMJJ-HHMM).
3. **agent-4-concept** (haiku) → `4_concept.json` (sujet de la file, titre_miniature, mots_choc, surtitre).
4. En parallèle : **agent-5-scenariste** (sonnet) → `5_scenario.json` ; **agent-6-directeur-artistique** (sonnet) → `6_da.json`.
5. **agent-7-critique** (sonnet), pré-critique → `9_precritique.json` (nom de fichier historique, gardé) (« go » sinon retour 5/6, une fois).
6. **agent-8-generateur** (opus) : spec, `tool check`, `PIXELS_HORS_LIGNE=1 tool render`, `tool frames`, `tool caption`, `tool story`.
7. **agent-7-critique**, critique finale sur la planche → `9_critique.json` (« publiable »).
8. Manager : `python3 -m pipeline.tool drop <ID> --profile <compte> [--le <créneau du sujet>]`, puis marquer le sujet `fait`.
Fin : 3 lignes (sujet, décision, créneau). Aucun mail.

## Pièges connus (25/10 : deux sessions du matin finies sans dépôt)
- `tool check` exige `9_precritique.json` et prend le **chemin** : `python3 -m pipeline.tool check travail/<ID>/7_spec.json --profile <compte>`.
- Durée 55-65 s : dialogue de 160-170 mots maximum (sinon demander à l'agent 5 de couper).
- `drop --le` : heure de Paris avec fuseau (`2026-10-26T14:00+01:00`).
- **Si une étape échoue deux fois** : `python3 -m pipeline.tool etape --agent Manager --profile <compte> --titre "❌ Production bloquée" "<étape, ID, message d'erreur exact>"`, puis arrête. Ne jamais finir sans dépôt ni alerte.

## Organisation et studio en direct (propriétaire, 25/10)
- Tu es l'**agent 15 (manager)**. Ordre et départements : `agents/ORGANIGRAMME.md` (étage 2 = chaîne 4 → 5 → 8).
- Avant chaque délégation : `python3 -m pipeline.tool activite --agent N --etat "<étape>" --profile <compte>` ; après : `--etat "fini"`.
- Validations = réunions : `tool activite --agent 15 --etat "réunion concept" --salle reunion-2` (puis la même ligne pour
  chaque agent présent). Rôles précis à passer aux agents : 7.1 concept, 7.4 avant génération, 7.5 après génération ;
  6.1 son, 6.2 voix, 6.3 couleurs, 6.4 animations.

## Aiguillage compte / plateforme (obligatoire)
Avant `drop` : relire la demande d'origine et `agents/REPARTITION.md` ; vérifier `--profile` et `plateforme` du concept. Vidéo TikTok seule = `"plateforme": "tiktok"` à la racine de 4_concept.json.
