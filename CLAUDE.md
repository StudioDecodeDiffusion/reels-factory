# Décodé Studio — pipeline de Reels

- Pour produire une vidéo (tâche de nuit ou demande ponctuelle) : suivre `NUIT.md` à la lettre.
- Les rôles des 9 agents sont dans `agents/`, les comptes dans `profiles/`.
- La mémoire du pipeline est dans `state/` (écrite par les sessions de nuit et par GitHub Actions).
- Le travail en cours va dans `travail/` (ignoré par git).
- Publication Instagram, e-mails et statistiques : GitHub Actions (`.github/workflows/`), jamais depuis la session.
