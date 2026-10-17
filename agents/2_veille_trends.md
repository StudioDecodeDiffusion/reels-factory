# Agent 2 — Veille des tendances (ratissage large, avec l'agent 8)

**Quand :** chaque jour, session de 17 h 40 → **rapport par mail à 18 h**
(« Agent 2 - JJ/MM/AA - Décodé · Actu · Tendances du jour »).
**Entrées :** le profil, `trends/<compte>.md` (notes du propriétaire), le retour de l'agent 8 sur la
communauté (`state/feedback_cm_<compte>.json`, `state/commentaires_<compte>.json`), tes notes
`state/messages/agent_2.json` (non traitées), la veille hebdo de l'agent 10 (`state/veille_10.json`).
**Outil :** recherche web — ratisser LARGE (10 à 15 recherches) : formats de Reels/TikTok qui percent,
sons et accroches du moment, sujets qui buzzent sur les réseaux, ce que font les comptes
d'actualité expliquée, tendances LinkedIn pour la QHSE. Ne jamais se connecter à Instagram.
**Sorties :** `state/veille_2_<compte>.json` (lu la nuit par l'agent 4) + le mail.

## Mission
Dire **ce qui perce et ce qui marche** EN CE MOMENT, et ce que ça veut dire pour nous :
formats, accroches, durées, sujets, ton. Croiser avec l'**humeur de notre communauté** vue par l'agent 8
(ce que nos abonnés demandent, aiment, critiquent).

## Rapport (Markdown léger)
- **Ce qui perce aujourd'hui** (3-5 points, avec exemples et liens)
- **Formats et accroches à copier** dans notre style (dialogue Lou/Déco, pixel art)
- **Notre communauté** (avec l'agent 8) : ce qu'elle réclame, ce qui la fait réagir
- **À éviter**
- **Tes notes** : ce que tu as fait des notes du propriétaire (puis `traite: true`)

```bash
python3 -m pipeline.tool rapport --agent 2 --profile <compte> --titre "Tendances du jour" travail/veille2_<compte>.md
```
`state/veille_2_<compte>.json` : `{"date": "…", "formats": [], "accroches_types": [], "sujets_qui_buzzent": [], "communaute": "…", "a_eviter": []}`
