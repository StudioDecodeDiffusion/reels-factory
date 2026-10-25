# Répartition des sujets entre les comptes (propriétaire, 25/10 — après deux erreurs d'aiguillage)

**Règle n° 1 : la demande du propriétaire décide.** S'il nomme un compte (« pour l'éco ») ou une plateforme
(« pour TikTok », « TikTok seulement »), c'est ce compte et cette plateforme, sans exception :
- `--profile <compte>` au dépôt, et `"plateforme": "tiktok"` à la racine de `4_concept.json` pour une vidéo TikTok seule
  (le dépôt refuse alors toute publication Instagram et toute story).
- Avant le dépôt, le Manager relit la demande d'origine et vérifie compte + plateforme (contrôle obligatoire, une ligne dans le rapport).

**Règle n° 2 : sinon, le sujet va au compte dont c'est le cœur.**

| Sujet | Compte |
|---|---|
| Gouvernement, Président, lois, police, manifestations, libertés, scandales politiques | **actu** |
| Entreprises, emplois, **plans sociaux et fermetures d'usines**, budget, impôts, dette, salaires, prix, inflation, épargne | **eco** |
| Normes, audits, sécurité au travail, accidents industriels, Seveso, Qualiopi, sanitaire | **qhse** |
| Comment ça marche, robots, ingénierie, énergie, physique, comparatifs de systèmes | **science** |
| Insolite, satisfaisant, records | **fun** |

Un sujet à cheval (ex. un plan social décidé par l'État) : compte du **fait principal** (l'usine qui ferme → eco).
`state/veille_brute.json` donne aussi un score d'adéquation par compte (`adequation`) : le plus haut l'emporte en cas de doute.
