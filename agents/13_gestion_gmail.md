# Agent 13 — Gestion de la boîte Gmail du studio

**Quand :** à chaque passage du facteur (toutes les 30 min, 7 h → 23 h), automatiquement (code : `pipeline/mail.py`, `REGLES_13`).
**Bilan :** `state/gmail_13.json` (rangés, archivés, mis à la corbeille, erreurs).

## Règles
- Mails des agents → `Decode/Agent N` ; Manager → `Decode/Manager` ; vidéos finales → `Decode/Manager - rendus finaux`.
  Restent aussi dans la boîte de réception : vidéos à valider, échecs (❌), alertes token.
- GitHub → `Decode/GitHub` (les « Run failed » restent visibles 3 jours puis sont archivés).
- Meta / Instagram → `Decode/Meta-Instagram` (codes et alertes de sécurité restent dans la boîte de réception).
- Google → `Decode/Google` (alertes de sécurité restent visibles).
- **Corbeille** (récupérable 30 jours) : accusés de réception des agents après 3 jours, points d'étape 📍 après 14 jours,
  « Voix générées / Vidéo montée / Rendu lancé / Publication en cours » après 7 jours.
- Jamais supprimés : vidéos à valider, publications, rapports des agents, échecs, mails de sécurité, tes propres notes.
Pour changer une règle : « agent 13 - ta règle » (elle sera ajoutée au code par la session suivante).
