# Agent 7 — Générateur

**Entrées :** script validé, thème validé, consignes d'animation.
**Sortie :** `travail/<id>/7_spec.json`, puis la vidéo via `python -m pipeline.tool render`.

Transformer le script en spécification JSON que le moteur vidéo (Remotion, 1080×1920) sait rendre.
Ne pas écrire de code React : seulement cette spécification.

## Types de scènes et champs EXACTS
- `hook` : `{"type":"hook","duration":2.5,"title":"question/choc ≤ 9 mots","subtitle":"optionnel ≤ 8 mots"}`
- `kinetic` : `{"type":"kinetic","duration":3,"lines":["2 à 4 lignes ≤ 28 caractères"],"highlight":"un mot présent dans les lignes"}`
- `counter` : `{"type":"counter","duration":3,"from":0,"to":3683,"prefix":"","suffix":" km/h","decimals":0,"label":"≤ 9 mots"}`
- `bars` : `{"type":"bars","duration":4,"title":"≤ 6 mots","items":[{"label":"2024","value":12.5}],"unit":" %"}` (2 à 6 items)
- `timeline` : `{"type":"timeline","duration":4,"title":"optionnel","events":[{"date":"1er janv.","text":"≤ 6 mots"}]}` (2 à 5)
- `dots` : `{"type":"dots","duration":3,"total":100,"highlighted":23,"label":"phrase contenant 23"}`
- `compare` : `{"type":"compare","duration":3,"title":"optionnel","left":{"label":"Avant","value":"≤ 9 car.","caption":"opt."},"right":{...}}`
- `particles` : `{"type":"particles","duration":5,"mode":"gravity|orbit|bounce|swarm|pendulum_wave","count":40,"caption":"≤ 14 mots"}`
- `outro` : `{"type":"outro","duration":2.5,"text":"chute ≤ 8 mots","cta":"appel à l'action"}`

## Règles
- Uniquement les types de `video.scenes_autorisees` du profil.
- **Chaque scène reçoit le champ `"voix"`** = le texte parlé du plan correspondant du script (recopié tel quel).
- Durées entre 4 et 8 s (le hook : 3 à 4 s). `check` allonge automatiquement une scène dont la voix est
  plus longue que prévu ; la durée exacte est recalée sur la vraie voix lors du rendu final sur GitHub.
- `to`, `value`, `highlighted`, `total` sont des nombres JSON, pas des chaînes.
- Format final : `{"theme": {…thème validé…}, "scenes": [ … ]}`

Le rendu fait dans la session est **muet** (aperçu pour la vérification visuelle) ; GitHub ajoute la voix
off et produit la version finale avant de t'envoyer l'e-mail.

Ensuite :
```bash
python -m pipeline.tool check travail/<id>/7_spec.json --profile <compte>   # corriger jusqu'à "OK"
python -m pipeline.tool render travail/<id>/7_spec.json travail/<id>/video.mp4
```
