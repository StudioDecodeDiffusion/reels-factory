# Déroulé de la session de nuit (à suivre par Claude)

Ce fichier est lu par la **tâche planifiée Claude** qui tourne chaque nuit avec l'abonnement Claude
du propriétaire (aucune API payante). Tu joues successivement les 9 agents décrits dans `agents/`.
Personne ne regarde pendant la nuit : ne pose pas de question, prends les décisions raisonnables
et note-les dans les fichiers de travail. Rien n'est jamais publié directement : le propriétaire
valide chaque vidéo par e-mail le matin.

Le compte à traiter est indiqué dans le message de la tâche (`actu`, `qhse`, …).

## 0. Préparation
```bash
cd <dossier du dépôt> && git pull -q
python3 -m pip install -q --break-system-packages -r requirements.txt
python3 -m pipeline.tool setup                 # installe le moteur vidéo (≈ 1 min)
ID=$(python3 -m pipeline.tool new --profile <compte>)
```
Lis : `profiles/<compte>.yaml`, `trends/<compte>.md`, et s'ils existent dans `state/` :
`historique_<compte>.json`, `refus_<compte>.json`, `charte_<compte>.json`, `stats_<compte>.json`,
`commentaires_<compte>.json`, `series_<compte>.json`.

## 1 → 3. Idée
Joue `agents/1_veille.md`, puis `agents/2_trends.md`, puis `agents/3_correlation.md`.
Écris chaque sortie JSON dans `travail/$ID/` sous le nom indiqué par l'agent.

## 4 → 6. Script, charte, validation (3 tours maximum)
Joue `4_scenariste` → `5_directeur_artistique` → `6_validateur`. Sois un validateur honnête : ne
valide pas ton propre travail par complaisance ; relis le script comme si un autre l'avait écrit et
revérifie réellement les chiffres sur le web.
Si `a_retravailler`, recommence au scénariste avec les corrections. Après 3 refus :
```bash
python3 -m pipeline.tool abandon $ID --profile <compte> --raison "<résumé du dernier avis>"
```
et arrête-toi là.

## 7. Fabrication
Joue `agents/7_generateur.md` :
```bash
python3 -m pipeline.tool check  travail/$ID/7_spec.json --profile <compte>   # répéter jusqu'à OK
python3 -m pipeline.tool render travail/$ID/7_spec.json travail/$ID/video.mp4
python3 -m pipeline.tool frames travail/$ID/7_spec.json travail/$ID/video.mp4
python3 -m pipeline.tool caption $ID --profile <compte>
```

## 8. Community manager
Si `state/stats_<compte>.json` ou `state/commentaires_<compte>.json` existent, joue
`agents/8_community_manager.md` (sinon écris `{"bilan": "pas encore de données", "recommandations": [], "reponses": []}`).

## 9. Vérification finale
Joue `agents/9_verificateur.md` : **regarde réellement chaque image** extraite
(`travail/$ID/video_scene*.png`) avec l'outil de lecture d'images, relis la légende
(`travail/$ID/legende.txt`) et revérifie les faits.
- `a_corriger` : corrige la spec, refais `check`, `render`, `frames`, `caption`, puis revérifie (une fois).
- `rejetee` : `abandon` avec la raison, puis arrête-toi.

## 10. Envoi pour validation
```bash
python3 -m pipeline.tool drop $ID --profile <compte>
```
GitHub crée alors une fiche et envoie l'e-mail de validation au propriétaire. Termine par un
résumé de 3 lignes : sujet, notes du validateur, décision du vérificateur.

## Règles permanentes
- Aucun chiffre inventé ; en cas de doute, on retire le chiffre ou on abandonne.
- Respect strict des exclusions du profil.
- Ne modifie jamais `.github/`, `pipeline/` ni `video/src/` pendant une session de nuit.
- Pour une vidéo **à la demande** (hors planning), le déroulé est le même.
