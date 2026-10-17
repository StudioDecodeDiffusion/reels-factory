# Agents principaux et sous-agents (un par compte Instagram)

Chaque agent (1 à 10) est un **agent principal** : sa fiche `agents/N_*.md` décrit le métier, commun à tous
les comptes. Pour chaque compte, il se divise en **sous-agent N.k** (k = `numero` du compte dans
`profiles/<compte>.yaml`) qui applique ce métier avec :
- la `ligne_editoriale`, le `ton`, le `public` et la `niche` du compte ;
- la consigne propre au sous-agent : `sous_agents: {N: "…"}` dans le profil.

| n° | compte (`profiles/`) | ligne |
|---|---|---|
| 1 | `actu` | actu française, plutôt à gauche, revendications populaires |
| 2 | `eco` | actu française, plutôt à droite, économie |
| 3 | `science` | vulgarisation scientifique |
| 4 | `fun` | animation, trends et autres |
| 5 | `qhse_veille` | veille réglementaire QHSE |
| 6 | `qhse_cours` | cours QHSE (séries) |
| 7 | `qhse_actu` | actu QHSE |

**Mails :** un sous-agent signe « Agent N.k - JJ/MM/AA - titre » (ex. « Agent 6.2 » = directeur artistique du
compte Éco). **Notes du propriétaire :** « agent 6 - … » vaut pour tous les comptes ; « agent 6.2 - … » pour
le seul compte n° 2 (`tool notes --agent 6 --profile eco` affiche les deux).

**Rôle de l'agent principal :** garder la cohérence de la marque Décodé entre comptes (Lou et Déco, pixel
art, qualité, sources), éviter que deux comptes traitent le même sujet le même jour sans angle différent
(les comptes 1 et 2 peuvent traiter le même sujet avec leurs deux lignes : c'est voulu), et partager ce qui
marche d'un compte à l'autre.

**Règle commune à toutes les lignes éditoriales :** l'angle est assumé, les faits ne sont jamais inventés ni
déformés ; chaque chiffre a une source.
Seuls les comptes qui ont un token Instagram (`instagram_secret` rempli dans GitHub) tournent chaque jour ;
les sessions planifiées listent les comptes à traiter.
