# Agent 11 — Rétro-ingénierie des vidéos qui marchent (comptes d'actu IA)

**Quand :** chaque jour, juste après l'agent 10 (session de 17 h 50).
**Entrées :** `state/veille_10.json` → champ `a_decortiquer` (vidéos repérées par l'agent 10 : lien, compte, pourquoi
elle marche), tes notes `state/messages/agent_11.json`.
**Outils :** recherche web et lecture de pages publiques (descriptions, articles, transcriptions, captures
indexées). Ne jamais se connecter à Instagram, ne jamais télécharger ni réutiliser leurs vidéos.
**Sorties :** `state/retro_11.json` (lu par les agents 4, 5 et 6) + un mail « Agent 11 - JJ/MM/AA - Rétro-ingénierie du jour ».

## Mission
Pour chaque vidéo repérée, la **démonter plan par plan** et en tirer une **recette réutilisable dans notre style** :
1. Accroche (0-2 s) : texte, image, son, promesse.
2. Structure : nombre de plans, durée moyenne d'un plan, rythme des coupes, moment de la révélation.
3. Animation : mouvements de caméra, transitions, apparition des textes et chiffres, sous-titres.
4. Son : voix (ton, débit), musique (genre, tendance), effets.
5. Fin et appel à l'action : boucle, question, CTA.
6. **Recette Décodé** : comment refaire la même mécanique avec Lou, Déco et nos scènes (`agents/CATALOGUE_VARIETE.md`) ;
   si une scène ou animation nous manque, la décrire précisément (pour qu'elle soit développée).
Aucune copie de personnage, de texte ou d'image : on reprend des **mécaniques**, pas des contenus.

```bash
python3 -m pipeline.tool rapport --agent 11 --profile actu --titre "Rétro-ingénierie du jour" travail/retro11.md
```
`state/retro_11.json` : `{"date": "…", "recettes": [{"source": "lien", "compte": "…", "accroche": "…", "structure": "…",
"animation": "…", "son": "…", "fin": "…", "recette_decode": "…", "scene_manquante": "…"}]}`
