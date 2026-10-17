# Décodé Studio — pipeline de Reels

- 16 h 30 : rapports des agents 8 puis 3 → suivre `RAPPORTS_16H30.md`.
- 17 h 40 : veilles des agents 1 et 2 (mails à 18 h) → suivre `VEILLE_17H40.md`.
- Nuit, ou vidéo à la demande : agents 4, 5, 6, 7, 9 → suivre `NUIT.md` à la lettre.
- Les rôles des 9 agents sont dans `agents/`, les comptes dans `profiles/`.
- La mémoire du pipeline est dans `state/` ; les notes du propriétaire à chaque agent dans
  `state/messages/agent_N.json` (`python3 -m pipeline.tool notes --agent N`).
- Le travail en cours va dans `travail/` (ignoré par git).
- Mails (« Agent N - JJ/MM/AA - titre »), publication Instagram et statistiques : GitHub Actions
  (`.github/workflows/`), jamais depuis la session.
