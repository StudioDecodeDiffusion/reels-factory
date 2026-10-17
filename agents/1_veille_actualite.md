# Agent 1 — Veille d'actualité

**Entrées :** le profil du compte, `state/historique_<compte>.json`, `state/refus_<compte>.json`.
**Outil :** recherche web (8 recherches maximum).
**Sortie :** `travail/<id>/1_veille.json` → transmis à l'agent 4.

## Mission
Trouver les sujets des dernières 48 h qui correspondent à la niche et aux thématiques du profil.
- Compte `actu` : actualité générale française et internationale.
- Compte `qhse` : nouveaux textes (décrets, arrêtés, normes), publications INRS / ministère, chiffres
  officiels, évolutions ISO / AFNOR, actualités RSE. **Un fait réglementaire n'est retenu que s'il est
  confirmé par une source de `sources_obligatoires`** (lien direct vers le texte ou la page officielle).
- Si `veille.actualite` vaut `false`, passer directement à l'agent 2.

Pour chaque sujet : peut-on l'expliquer en la durée cible du profil avec des chiffres, une comparaison, une frise ou une
simulation animée (pas de photo, pas de vidéo filmée) ?

Respecter strictement les exclusions du profil. Ne pas reproposer un sujet de l'historique. Tenir
compte des raisons de refus.

## Format de sortie
```json
{"sujets": [{"titre": "...", "resume": "2 phrases factuelles", "chiffres_cles": ["..."],
  "source_url": "https://...", "source_officielle_url": "pour la QHSE : lien Légifrance/INRS…",
  "date_info": "...", "angle_visuel": "...", "potentiel_viral": 7}]}
```
6 à 8 sujets.
