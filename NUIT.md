# Session de nuit — agents 4, 5, 6, 7 et 9 (une vidéo à valider le matin)

Lancée par une tâche planifiée Claude (abonnement du propriétaire, aucune API payante), ou à la demande
pour une vidéo ponctuelle. Personne ne regarde : ne pose pas de question, prends les décisions
raisonnables et note-les. **Rien n'est jamais publié sans le OK du propriétaire.**
Le compte est indiqué dans le message de la tâche (`actu`, `qhse`, …).

```
 16 h 30   8 Community manager ──► 3 Résultats du compte            (mails 8 et 3)
 17 h 40   1 Veille actualité  ·  2 Veille tendances (+ retour du 8) (mails 1 et 2 à 18 h)
 la nuit   4 Concept + critique (mail d'info)
             ├─► 5 Scénario ─────────┐   (en parallèle, ils se parlent)
             └─► 6 Direction artistique (discute avec le propriétaire par mail)
                       ▼
           7 Générateur ─► 9 Critique (+ projection avec le rapport du 3) ─► mail de VALIDATION
 le matin  le propriétaire répond OK ─► 9 transmet à 8 ─► publication par GitHub à l'heure prévue
```

**Sous-agents :** pour chaque compte, joue le sous-agent N.k décrit dans `agents/SOUS_AGENTS.md` (ligne
éditoriale et consigne `sous_agents` du profil). Notes : `tool notes --agent N --profile <compte>`.


**Points d'avancement (obligatoire) :** dès qu'un agent a fini son étape, envoie un résumé au propriétaire
(mail « Manager - JJ/MM/AA - … ») : 3 à 6 lignes — ce que l'agent a fait, ses choix, ce qui suit.
```bash
python3 -m pipeline.tool etape --agent N --profile <compte> --titre "Agent N terminé : <étape>" "- **Fait :** …\n- **Choix :** …\n- **Suite :** …"
```
Pour les agents qui envoient déjà un rapport complet (1, 2, 3, 8, 10), le point d'avancement reste court.
Le workflow doit être fluide : enchaîne les agents sans temps mort.

## 0. Préparation
```bash
cd <dossier du dépôt> && git pull -q
python3 -m pip install -q --break-system-packages -r requirements.txt
python3 -m pipeline.tool setup                 # installe le moteur vidéo (≈ 1 min)
ID=$(python3 -m pipeline.tool new --profile <compte>)
```
Lis : `profiles/<compte>.yaml`, `trends/<compte>.md` et dans `state/` : `veille_1_`, `veille_2_`,
`rapport_3_`, `feedback_cm_`, `historique_`, `refus_`, `charte_`, `series_<compte>.json`.
Si une veille du jour manque (session de 17 h 40 ratée), fais une veille rapide toi-même.

Avant chaque agent N : `python3 -m pipeline.tool notes --agent N --profile <compte>` — les notes du
propriétaire passent avant tout. Ensuite `python3 -m pipeline.tool lu --agent N <id>…`.

## 4. Concept + critique → mail d'information
Joue `agents/4_concept_et_critique.md` → `travail/$ID/4_concept.json`, puis :
```bash
python3 -m pipeline.tool info $ID --profile <compte>
```

## 5 et 6. Scénario et direction artistique (en parallèle)
Joue `agents/5_scenario.md` et `agents/6_directeur_artistique.md` en les faisant dialoguer. La DA lit
d'abord ses notes (`state/messages/agent_6.json`) et répond au propriétaire dans
`message_au_proprietaire` (envoyé par mail avec la vidéo). Le scénariste se relit et revérifie les
chiffres sur le web (2 réécritures max, sinon `abandon`).

## 7. Génération
Joue `agents/7_generateur.md` :
```bash
python3 -m pipeline.tool check  travail/$ID/7_spec.json --profile <compte>   # répéter jusqu'à OK
python3 -m pipeline.tool render travail/$ID/7_spec.json travail/$ID/video.mp4
python3 -m pipeline.tool frames travail/$ID/7_spec.json travail/$ID/video.mp4
python3 -m pipeline.tool caption $ID --profile <compte>
python3 -m pipeline.tool story $ID --profile <compte>      # miniature avec titre + « Créé avec l'IA », et story « nouvelle vidéo »
```

## 9. Critique → dépôt → mail de validation
Joue `agents/9_critique.md` : **regarde réellement chaque image** (`travail/$ID/video_scene*.png`),
vérifie la cohérence et les sources, projette la popularité avec `state/rapport_3_<compte>.json`.
Si une correction est nécessaire : retour à l'agent 7 (une fois). Puis `travail/$ID/9_critique.json` et :
```bash
python3 -m pipeline.tool drop $ID --profile <compte>
```
GitHub ajoute les voix de Lou et Déco, fait le rendu final et l'agent 9 envoie le mail de validation
(l'agent 6 envoie son message à part s'il en a un).
En cas d'échec : `python3 -m pipeline.tool abandon $ID --profile <compte> --raison "…"`.

Termine par un résumé de 3 lignes : sujet, décision de l'agent 9, projection.

## Règles permanentes
- Aucun chiffre inventé ; en cas de doute, on retire le chiffre ou on abandonne.
- Respect strict des exclusions du profil. Personnages originaux uniquement.
- Ne modifie jamais `.github/`, `pipeline/` ni `video/src/` pendant une session.
- Pour une vidéo **à la demande** (hors planning), le déroulé est le même.
