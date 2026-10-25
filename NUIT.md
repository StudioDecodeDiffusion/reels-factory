# Session de nuit — agents 4, 5, 6, 8 et 7 (une vidéo à valider le matin)

> **Mode économie de quota** : si `state/quota.json` contient `economie_jusqu_a` dans le futur, NE PRODUIRE AUCUNE VIDÉO et s'arrêter immédiatement (quota à 96 %, propriétaire 22/10). Ancienne consigne : un seul tour de pré-critique et de critique, pas de sous-agents en parallèle, modèle sonnet pour tous les agents sauf 5.

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


**Points d'avancement (obligatoire, réguliers et précis) :** dès qu'un agent a fini son étape — et pour l'agent 8
à chaque palier : spec validée, rendu muet terminé, images contrôlées, miniature et story prêtes — envoie un résumé au propriétaire
(mail « Manager - JJ/MM/AA - … ») : 3 à 6 lignes — ce que l'agent a fait, ses choix, ce qui suit.
```bash
python3 -m pipeline.tool etape --agent N --profile <compte> --titre "Agent N terminé : <étape>" "- **Fait :** …\n- **Choix :** …\n- **Suite :** …"
```
Pour les agents qui envoient déjà un rapport complet (1, 2, 3, 8, 10), le point d'avancement reste court.
Le workflow doit être fluide : enchaîne les agents sans temps mort.

## 0000. MODE SOBRE PERMANENT (propriétaire, 24/10 : la production a consommé tout le quota de la semaine)
Budget par vidéo : **une seule session, sans sous-agents**, ≈ 10 recherches web max, 1 seul rendu local de contrôle
(`tool frames` sur la planche, pas de rendus multiples), pré-critique et critique de l'agent 7 en une passe chacune.
Lire seulement : la note du sujet dans `state/file_sujets_actu.json`, les notes non lues des agents 4-6-7, le catalogue.
Ne pas relire tout le dépôt, ne pas produire de fichiers intermédiaires longs. Pas de mail, pas de `tool etape`.
La qualité vient des gabarits visuels (code) : la session remplit une spec courte, elle n'invente pas de code.

## 0001. Durée, authenticité, légende (propriétaire, 24/10 — calé sur les comptes de référence)
- **Durée 55-75 s** (top Reels des comptes de référence : 50-95 s ; archive66 95 s), **12-18 scènes**, un plan toutes
  les 3-4 s, voix rapide sans blanc. L'histoire doit tenir jusqu'au bout : une révélation toutes les ~10 s.
- **Authenticité, zéro bug** : la voix est contrôlée automatiquement au rendu (débit, blancs, reprise ou voix de secours) ;
  l'agent 7 regarde chaque image de la planche : aucun texte qui déborde, aucun objet coupé, aucune scène vide,
  aucune répétition d'image d'une scène à l'autre, sous-titres lisibles. Un défaut = on corrige avant de déposer.
- **Aucune mention d'IA** dans la vidéo, la miniature, la légende (Instagram s'en charge). Seuls les crédits de licence des
  voix restent, automatiquement, en toute fin de légende.
- **Légende façon comptes qui percent** : 1re ligne = l'accroche-histoire (1-2 phrases, le scandale + un chiffre) ;
  2e paragraphe = le contexte en 2 phrases ; puis une **question** (« Tu en penses quoi ? 👇 ») et un **appel au partage
  ciblé** (« Envoie-la à quelqu'un qui… 📤 ») ; sources sur UNE ligne courte (« Sources : X, Y »). Pas de pavé.
- **Hashtags : 4-5, précis** : 1 large du sujet (#retraites), 2 entités nommées (#plfss2027 #assembleenationale),
  1 d'actu (#actufrance), + #decodeactu. Jamais de hashtags génériques (#viral, #fyp, #actu seul).

## 00. Quel créneau ?
```bash
python3 -m pipeline.tool creneau --profile <compte>
```
- `AUCUN` → aucun créneau libre dans les 8 h : **arrête la session sans rien produire** (une ligne de résumé).
- Sinon, la vidéo est pour ce créneau. Si la ligne dit **RÉSUMÉ DE LA SEMAINE OBLIGATOIRE** (dimanche 14 h) :
  la vidéo résume les grandes infos de la semaine (lundi → dimanche), à partir de `state/historique_<compte>.json`
  et des veilles de la semaine, avec une mécanique propre au résumé (top, récap rapide, « ce qu'il fallait retenir »).

## 00ter. Vidéo phare (créneau de 14 h) et vidéos d'info
`tool creneau` l'indique. **14 h = la vidéo phare du jour**, celle qui doit faire décoller le compte :
- le sujet le plus fort du jour (file de sujets ou veille 1), angle **contraste pouvoir / gens** : une figure de pouvoir
  identifiable face aux gens concernés dès la 1re seconde (image + titre-contraste), faits sourcés, aucune accusation non prouvée ;
- **beaucoup de visages et de gens** : personnages cartoon (theme.persos = cartoon) et/ou vraies photos et vidéos de gens
  sous licence libre (voir CATALOGUE_VARIETE.md § Images de gens) ;
- se termine par une **question fermée** à l'écran et en 1re ligne de légende (« À toi de juger : oui ou non ? ») ;
- 45-55 s, effort maximal, agent 7 encore plus sévère (note ≥ 8 exigée).
Les autres créneaux = **vidéos d'info** (le fond de commerce) : actu du jour expliquée, chiffres clés, « 3 choses à
savoir », toujours antipouvoir mais plus sobres et plus courtes (30-40 s). Jamais deux vidéos à moins de 4 h d'écart.
Le visuel change à chaque vidéo : éditorial / cartoon / montage photo-vidéo de gens, jamais deux fois le même d'affilée.

## 00quater. Miniature et titre d'ouverture : la teneur critique dès le premier regard
Dans `4_concept.json` (concept choisi) : `titre_miniature` (8 mots max, **critique et explicite** : la thèse du post,
ex. « Les vitrines d'abord. Toi, après. », « 5,4 milliards pour eux, 2,37 € pour toi »), `mots_choc` (1-3 mots en
rouge), `surtitre_miniature` (qui · quand, ex. « Macron · 18 octobre »). La **1re scène** affiche la même thèse en
titre et la voix l'attaque dès la 1re seconde. `tool story` fabrique la miniature « choc » à partir de ces champs ;
`tool check` refuse une vidéo sans `titre_miniature`.

## 00bis. Spécialisation des agents (modèles par rôle)
(Désactivé par le mode sobre : tout se fait dans la session principale.) Chaque agent travaillait dans son propre sous-agent (outil Agent), avec uniquement son fichier `agents/N_*.md`, ses notes et
les sorties de l'agent précédent ; le Manager (session principale) transmet les fichiers et contrôle chaque sortie.
| Agent | Modèle | Pourquoi |
|---|---|---|
| 4 concept, 5 script, 9 critique (pré et finale) | opus | écriture, angle, esprit critique |
| 6 direction artistique, 11 rétro-ingénierie | opus | goût visuel, analyse fine |
| 1, 2, 10 veilles, 3 chiffres, 12 stratégie | sonnet | recherche et synthèse |
| 7 génération (spec, rendu), 8 community, 13 | sonnet / haiku | exécution |
Si le quota Claude est élevé (relevé > 75 %), tout passer en sonnet sauf 5 et 9.

## 000. File de sujets du propriétaire (prioritaire)
Lire `state/file_sujets_actu.json` : prendre le **premier sujet non fait** compatible avec le créneau (un sujet avec
`creneau` n'est produit que pour ce créneau, et se dépose avec `tool drop … --le <creneau>+02:00`). Utiliser sa trend. Après le dépôt, passer `fait` à true. File vide → choix libre.

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

## 9 (pré-critique). Avant toute génération
Joue la section 0 de `agents/7_critique.md` : critique impitoyable du scénario et de la DA, exigence de
diversité (`agents/CATALOGUE_VARIETE.md`, `state/variete_<compte>.json`) et d'animations travaillées.
`a_revoir` → retour aux agents 5 et 6 (2 tours max). Sans `go`, `tool check` refuse la vidéo.

## 7. Génération
Joue `agents/8_generateur.md` :
```bash
python3 -m pipeline.tool check  travail/$ID/7_spec.json --profile <compte>   # répéter jusqu'à OK
python3 -m pipeline.tool render travail/$ID/7_spec.json travail/$ID/video.mp4
python3 -m pipeline.tool frames travail/$ID/7_spec.json travail/$ID/video.mp4
python3 -m pipeline.tool caption $ID --profile <compte>
python3 -m pipeline.tool story $ID --profile <compte>      # miniature avec titre + « Créé avec l'IA », et story « nouvelle vidéo »
```

## 9. Critique → dépôt → mail de validation
Joue `agents/7_critique.md` : **regarde réellement chaque image** (`travail/$ID/video_scene*.png`),
vérifie la cohérence et les sources, projette la popularité avec `state/rapport_3_<compte>.json`.
Si une correction est nécessaire : retour à l'agent 8 (une fois). Puis `travail/$ID/9_critique.json` et :
```bash
python3 -m pipeline.tool drop $ID --profile <compte>
```
GitHub ajoute les voix de Lou et Déco, fait le rendu final et l'agent 7 envoie le mail de validation
(l'agent 6 envoie son message à part s'il en a un).
En cas d'échec : `python3 -m pipeline.tool abandon $ID --profile <compte> --raison "…"`.

Termine par un résumé de 3 lignes : sujet, décision de l'agent 7, projection.

## Règles permanentes
- Aucun chiffre inventé ; en cas de doute, on retire le chiffre ou on abandonne.
- Respect strict des exclusions du profil. Personnages originaux uniquement.
- Ne modifie jamais `.github/`, `pipeline/` ni `video/src/` pendant une session.
- Pour une vidéo **à la demande** (hors planning), le déroulé est le même.
