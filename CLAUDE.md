# Décodé Studio — pipeline de Reels

- 16 h 30 : rapports des agents 9 puis 3 (+ agent 10 : résumé de stratégie chaque jour, stratégie complète le lundi) → suivre `RAPPORTS_16H30.md`.
- 17 h 40 : veilles des agents 1, 2 (Instagram) et 13 (TikTok) → suivre `VEILLE_17H40.md`.
- 17 h 50 chaque jour : agents 11 (comptes d'actu IA) puis 12 (rétro-ingénierie) → `HEBDO_10.md`.
- 13 h 05 : vidéo de l'après-midi (créneau 18 h 30) ; 0 h 20 : vidéo de la nuit (créneau 12 h 30) → `NUIT.md`.
- Nuit, ou vidéo à la demande : agents 4, 5, 6, 8, 7 → suivre `NUIT.md` à la lettre.
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
- **Modèles (mode sobre maximal, 25/10)** : haiku pour tous les agents (y compris l'agent 8, la spec étant assemblée par script) ; jamais opus. Passer `model` à chaque appel Agent si besoin.
- **Règles en 1 page** : `agents/REGLES_ACTIVES.md` (remplace NUIT.md et CERVEAU.md pour les agents) ; chaque vidéo a son `travail/<ID>/0_dossier.md` (`tool dossier`).
- Paralléliser seulement les tâches indépendantes (ex. agents 1 et 2) ; jamais deux agents sur les mêmes fichiers.
- Les rapports d'agents résument (5 lignes) ; le Manager lit les vrais fichiers quand une décision en dépend.

## Numérotation des agents (propriétaire, 25/10)
1 veille actu · 2 veille tendances Instagram · 3 chiffres · 4 concept · 5 scénario · 6 DA · **7 critique** · **8 générateur** ·
**9 community manager** · **10 stratégie monétaire** · **11 veille comptes IA** · **12 rétro-ingénierie** · **13 veille TikTok**.
L'ancien agent 13 (gestion Gmail) est supprimé.

## Organisation en étages (propriétaire, 25/10)
Voir `agents/ORGANIGRAMME.md` : 0 secrétaire (seul interlocuteur du propriétaire), 14 coordinateur, 15 manager (= la session qui orchestre),
départements par étage, sous-agents (1.1-1.5, 2.1-2.5, 3.1-3.5, 6.1-6.4, 7.1-7.5, 12.1-12.3), salles de réunion.
Studio en direct : abandonné (propriétaire, 25/10) — ne plus appeler `tool activite`.
