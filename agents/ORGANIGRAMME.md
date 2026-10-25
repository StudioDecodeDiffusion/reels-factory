# Organigramme de Décodé Studio (propriétaire, 25/10)

Visualisation en direct : https://studiodecodediffusion.github.io/reels-media/studio/
(chaque étape est signalée par `python3 -m pipeline.tool activite --agent N --etat "…" [--salle …] [--profile …]`).

| Étage | Département | Agents | Salle de réunion (`--salle`) |
|---|---|---|---|
| 0 | Accueil | **0 secrétaire** | — |
| 0 | Management général | **15 manager**, **14 coordinateur**, 9 community manager, 10 stratégie monétaire, 3 chiffres | `reunion-0` |
| 1 | Veille | 1 veille actu, 2 tendances Instagram, 13 tendances TikTok | `reunion-1-veille` |
| 1 | Artistique | 6 direction artistique, 7 critique | `reunion-1-art` |
| 2 | Production (chaîne linéaire, de gauche à droite) | 4 concept → 5 scénario → 8 générateur | `reunion-2` |
| 3 | R&D | 11 veille comptes IA, 12 rétro-ingénierie | `reunion-3` |

## Sous-agents (un même fichier d'agent, appelé avec son rôle précis : « rôle 6.2 »)
- **1.1 à 1.5**, **2.1 à 2.5**, **3.1 à 3.5** : un par compte (1 actu, 2 science, 3 QSE, 4 éco, 5 fun).
- **6.1** son · **6.2** voix · **6.3** couleurs · **6.4** animations.
- **7.1** critique du concept · **7.2** critique de la tendance · **7.3** corrélation veille/tendances ·
  **7.4** critique avant génération · **7.5** critique après génération.
- **12.1** rétro-ingénierie des images · **12.2** du son · **12.3** des légendes, statistiques et le reste.

## Rôles nouveaux
- **Agent 0 · secrétaire (accueil)** : seul interlocuteur du propriétaire. Lit ses messages (mails « agent 0 - … »),
  répond (réponses dans le journal de 20 h 40), transmet à l'agent 14 toute demande de changement.
- **Agent 14 · coordinateur** : fluidifie les échanges entre agents ; applique les demandes du propriétaire rapportées
  par l'agent 0 (fiches d'agents, profils, files de sujets), puis rend compte à l'agent 0.
- **Agent 15 · manager** : la session qui orchestre ; anime chaque salle de réunion (validations et concertations),
  signale l'activité de chaque agent, ne produit rien lui-même.

## Réunions (animées par l'agent 15)
- Étage 1 veille : 1 + 2 + 13 croisent actu et tendances (point de départ : `state/veille_brute.json`) → 7.3 valide.
- Étage 2 production, en ligne : 4 présente le concept → 7.1/7.2 valident → 5 (avec 6.1-6.4 de l'étage 1) → 7.4 feu vert → 8 génère → 7.5 valide.
- Étage 1 artistique : 6.1-6.4 accordent son, voix, couleurs et animations avec 7.
- Étage 3 R&D : 11 signale, 12.1-12.3 décortiquent, résultat transmis à 6 et 8.
- Étage 0 : 3, 9, 10 et 14 font le point du jour pour le journal de 20 h 40.
