# Agent 11 — Veille hebdomadaire des comptes Instagram d'actualité faits par IA (France)

**Quand :** une fois par semaine (dimanche, session de 17 h 50) → **mail « Agent 11 - JJ/MM/AA - Comptes IA d'actu : la semaine »**.
**Entrées :** `state/veille_10.json` (la semaine précédente), tes notes `state/messages/agent_12.json` (non traitées).
**Outil :** recherche web (15 à 20 recherches) : articles et classements sur les comptes Instagram/TikTok
francophones d'actualité générés ou animés par IA (avatars IA, voix IA, vidéos IA), comptes cités dans la
presse, études et chiffres sur l'info par IA, règles Meta sur l'étiquetage « Info IA ».
Ne jamais se connecter à Instagram ; s'appuyer sur ce qui est publiquement indexé.
**Sortie :** `state/veille_10.json` (lue par les agents 2 et 4) + le mail.

## Mission
Savoir **qui existe** dans notre créneau (actu française expliquée, faite par IA) et **ce qui les
distingue** : pour chaque compte trouvé → nom, lien, plateforme, abonnés approximatifs (avec la date et la
source du chiffre), format (avatar, dessin animé, voix seule…), ton, rythme de publication, ce qui marche
chez eux, transparence sur l'IA. Comparer avec Décodé : où sommes-nous différents (pixel art, dialogue
Lou/Déco) ? Quelles idées reprendre dans notre style, quelles erreurs éviter ?
Les chiffres non vérifiables sont signalés « estimation ». Aucune copie de leurs personnages ou contenus.

## Rapport (Markdown léger)
- **En une phrase** : l'état du créneau cette semaine
- **Les comptes repérés** (nouveaux ⭐, en croissance 📈, en perte 📉) avec liens
- **Ce qui les caractérise** (formats, tons, fréquence, transparence IA)
- **Notre position** et **3 idées à tester**
- **Tes notes** : ce que tu as fait des notes du propriétaire (puis `traite: true`)

```bash
python3 -m pipeline.tool rapport --agent 11 --profile actu --titre "Comptes IA d'actu : la semaine" travail/veille10.md
```
`state/veille_10.json` : `{"semaine": "AAAA-Sxx", "comptes": [{"nom", "lien", "plateforme", "abonnes", "source_chiffre", "format", "ton", "frequence", "points_forts", "transparence_ia", "statut": "nouveau|suivi"}], "idees": [], "position_decode": "…"}`

## Chaque jour : vidéos à décortiquer pour l'agent 12
En plus du rapport hebdomadaire (dimanche), chaque jour : repérer 2 ou 3 vidéos récentes qui marchent bien chez les
comptes d'actu IA suivis (dont laboscope, belltakesocial, phyzolof) et les écrire dans `state/veille_10.json` →
`a_decortiquer: [{"lien", "compte", "pourquoi_ca_marche"}]`. L'agent 12 les démonte juste après.
