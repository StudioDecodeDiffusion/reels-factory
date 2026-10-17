# Déroulé de la session de nuit (à suivre par Claude)

Ce fichier est lu par la **tâche planifiée Claude** qui tourne chaque nuit avec l'abonnement Claude
du propriétaire (aucune API payante). Tu joues successivement les 8 agents décrits dans `agents/`.
Personne ne regarde pendant la nuit : ne pose pas de question, prends les décisions raisonnables
et note-les dans les fichiers de travail. Rien n'est jamais publié directement : le propriétaire
valide chaque vidéo par e-mail le matin.

Le compte à traiter est indiqué dans le message de la tâche (`actu`, `qhse`, …).

```
 1 Veille actualité ─┐
 2 Veille tendances ─┼─► 4 Concept + critique ─► (e-mail d'info au propriétaire)
 3 Résultats compte ─┘           │
          ▲                      ├─► 5 Scénario ─┐
          │                      └─► 6 Direction artistique (discussion ouverte avec le propriétaire)
          │                                      ▼
          │                         7 Générateur + contrôle qualité ─► e-mail de VALIDATION
          │                                      │ (le propriétaire répond OK)
          └──── retour quotidien ◄── 8 Community manager ◄── publication par GitHub
```

## 0. Préparation
```bash
cd <dossier du dépôt> && git pull -q
python3 -m pip install -q --break-system-packages -r requirements.txt
python3 -m pipeline.tool setup                 # installe le moteur vidéo (≈ 1 min)
ID=$(python3 -m pipeline.tool new --profile <compte>)
```
Lis : `profiles/<compte>.yaml`, `trends/<compte>.md` et, s'ils existent dans `state/` :
`historique_`, `refus_`, `charte_`, `stats_`, `commentaires_`, `feedback_cm_`, `da_`, `series_<compte>.json`.

## 8 (d'abord). Community manager — retour quotidien
Joue `agents/8_community_manager.md` sur les stats et commentaires de la veille : écris
`travail/$ID/8_community.json` (réponses proposées) et `state/feedback_cm_<compte>.json` (retour pour
l'agent 3). S'il n'y a pas encore de données, écris un retour « pas encore de données ».

## 1, 2, 3. Les trois veilles
Joue `agents/1_veille_actualite.md`, `agents/2_veille_trends.md`, `agents/3_resultats_compte.md`.

## 4. Concept + critique → e-mail d'information
Joue `agents/4_concept_et_critique.md`, puis :
```bash
python3 -m pipeline.tool info $ID --profile <compte>
```

## 5 et 6. Scénario et direction artistique (en parallèle)
Joue `agents/5_scenario.md` et `agents/6_directeur_artistique.md` en les faisant dialoguer : la DA lit
d'abord les messages du propriétaire (`state/da_<compte>.json`), le scénario tient compte des choix de
mise en scène et des tenues. Le scénariste se relit et revérifie les chiffres sur le web avant de
transmettre (2 réécritures max, sinon `abandon`).

## 7. Génération + contrôle qualité → e-mail de validation
Joue `agents/7_generateur.md` :
```bash
python3 -m pipeline.tool check  travail/$ID/7_spec.json --profile <compte>   # répéter jusqu'à OK
python3 -m pipeline.tool render travail/$ID/7_spec.json travail/$ID/video.mp4
python3 -m pipeline.tool frames travail/$ID/7_spec.json travail/$ID/video.mp4
python3 -m pipeline.tool caption $ID --profile <compte>
```
**Regarde réellement chaque image** (`travail/$ID/video_scene*.png`) avec l'outil de lecture
d'images, écris `travail/$ID/7_controle.json`, corrige si besoin (une fois), puis :
```bash
python3 -m pipeline.tool drop $ID --profile <compte>
```
Le rendu de la session est muet : GitHub ajoute les voix de Lou et Déco, fait le rendu final et
envoie l'e-mail de validation (avec le message du directeur artistique sur sa fiche de discussion).
En cas d'échec à n'importe quelle étape : `python3 -m pipeline.tool abandon $ID --profile <compte> --raison "…"`.

Termine par un résumé de 3 lignes : sujet, notes de relecture, décision du contrôle qualité.

## Règles permanentes
- Aucun chiffre inventé ; en cas de doute, on retire le chiffre ou on abandonne.
- Respect strict des exclusions du profil.
- Ne modifie jamais `.github/`, `pipeline/` ni `video/src/` pendant une session de nuit.
- Pour une vidéo **à la demande** (hors planning), le déroulé est le même.
