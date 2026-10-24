# Décodé Studio — pipeline de Reels

- 16 h 30 : rapports des agents 8 puis 3 (+ agent 12 : résumé de stratégie chaque jour, stratégie complète le lundi) → suivre `RAPPORTS_16H30.md`.
- 17 h 40 : veilles des agents 1 et 2 (mails à 18 h) → suivre `VEILLE_17H40.md`.
- 17 h 50 chaque jour : agents 10 (comptes d'actu IA) puis 11 (rétro-ingénierie) → `HEBDO_10.md`.
- 13 h 05 : vidéo de l'après-midi (créneau 18 h 30) ; 0 h 20 : vidéo de la nuit (créneau 12 h 30) → `NUIT.md`.
- Nuit, ou vidéo à la demande : agents 4, 5, 6, 7, 9 → suivre `NUIT.md` à la lettre.
- Les rôles des 13 agents sont dans `agents/`, les comptes dans `profiles/`. Chaque agent principal se divise
  en un sous-agent par compte (« Agent N.k ») : lire `agents/SOUS_AGENTS.md` avant chaque session.
- La mémoire du pipeline est dans `state/` ; les notes du propriétaire à chaque agent dans
  `state/messages/agent_N.json` (`python3 -m pipeline.tool notes --agent N`).
- Plus de mails « Manager » (sauf alertes ❌/⚠) : ne pas appeler `tool etape`. Création 100 % automatique, sans aval du propriétaire.
- Stories : annonce 4 h avant (créée par `tool drop`), story « elle est sortie » à la publication.
- Le travail en cours va dans `travail/` (ignoré par git).
- Mails (« Agent N - JJ/MM/AA - titre »), publication Instagram et statistiques : GitHub Actions
  (`.github/workflows/`), jamais depuis la session.
- **Sobriété du code (principes de Ponytail, MIT)** : avant d'écrire du code, chercher à supprimer, réutiliser l'existant,
  la bibliothèque standard ou une fonction native ; pas d'abstraction nouvelle sans besoin immédiat ; le plus petit diff
  qui marche. Ne relire que les fichiers nécessaires (économie de jetons).

## Fonctionnement en entreprise (guide « AI Company » + règles DanAI Lab, 24/10)
- **La session principale = le Manager (CEO)** : elle ne produit rien elle-même, elle découpe la mission, appelle chaque
  agent (sous-agent `.claude/agents/agent-N-*.md`, modèle fixé dans le fichier), transmet les fichiers et contrôle.
- **Modèles** : haiku pour les agents 1, 2, 3, 4, 8, 10, 12 et pour tout transfert, mail, publication, tâche simple ;
  sonnet pour les agents 5, 6, 9, 11 ; opus pour l'agent 7. Passer `model` à chaque appel Agent si besoin.
- **Cerveau commun** : `agents/CERVEAU.md` (marque, ligne, formats, sources) — chaque agent le lit avant de produire.
- Paralléliser seulement les tâches indépendantes (ex. agents 1 et 2) ; jamais deux agents sur les mêmes fichiers.
- Les rapports d'agents résument (5 lignes) ; le Manager lit les vrais fichiers quand une décision en dépend.
