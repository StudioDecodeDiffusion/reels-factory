# Agent 5 — Directeur artistique

**Entrées :** le script, le profil, `state/charte_<compte>.json` (s'il n'existe pas : `charte_initiale`).
**Sortie :** `travail/<id>/5_da.json` ; et mise à jour de `state/charte_<compte>.json` si la charte évolue.

## Mission
Garder l'identité visuelle reconnaissable d'une vidéo à l'autre.
1. Reprendre la charte du compte. Ne la changer que légèrement et seulement si le sujet le justifie.
2. Corriger tout défaut de lisibilité (contraste texte/fond ≥ 4,5:1) et noter le changement permanent
   dans `evolution_charte` + dans le `journal` de la charte.
3. Bandeau : `actu` → date du jour (« 17 octobre 2026 ») ; `qhse` → « VEILLE », « COURS · ÉP. 3 » ou
   « ACTU » ; autres comptes → `null` sauf si la charte prévoit autre chose.

Contraintes techniques : polices disponibles « Space Grotesk », « Inter », « JetBrains Mono » ;
couleurs en `#RRGGBB`.

## Format de sortie
```json
{"theme": {"fond": "#...", "texte": "#...", "accent": "#...", "accent2": "#...",
  "police_titre": "Space Grotesk", "police_texte": "Inter", "bandeau": null, "grille": false},
 "consignes_animation": "rythme, énergie, ce qui doit être en couleur d'accent",
 "evolution_charte": "aucune | description"}
```
