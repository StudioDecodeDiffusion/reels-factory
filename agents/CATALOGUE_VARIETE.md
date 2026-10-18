# Catalogue de variété — CHAQUE vidéo doit être différente

Règle du propriétaire : **accroche différente, trend différente, fonctionnement différent, voix différentes,
musique différente à chaque vidéo.** Chaque `7_spec.json` contient un bloc `variete` ; `tool check` le
compare aux 5 dernières vidéos du compte (`state/variete_<compte>.json`) et **refuse** la vidéo si :
- un des champs `accroche`, `fonctionnement`, `mise_en_page`, `musique`, `voix` est identique à la vidéo précédente ;
- ou si 3 champs ou plus sont identiques à l'une des 5 dernières.

```json
"variete": {"accroche": "chiffre_geant", "trend": "nom de la trend de l'agent 2", "fonctionnement": "vrai_faux",
            "mise_en_page": "jt", "musique": "trap8bit", "voix": "V2+V3", "palette": "nuit_neon"}
```

## Accroches (`accroche`)
chiffre_geant (un chiffre plein écran dans la 1re seconde) · faux_avertissement · question_choc ·
stop_scroll (« Stop. Avant de scroller… ») · pov (« POV : tu touches 1 300 € de retraite ») ·
breaking (« FLASH ») · contre_intuitif (« Tout le monde dit X. C'est faux. ») · compte_a_rebours ·
avant_apres · citation_choc (citation sourcée en grand) · devinette (« Devine combien… »)

## Fonctionnements (`fonctionnement`) — la mécanique de la vidéo
recit_chrono · vrai_faux · top3 · avant_apres · simulateur (« si tu touches X € → voilà ce qui change ») ·
debat (deux camps, arguments sourcés) · enquete (indices, révélation finale) · quiz (le spectateur répond) ·
explication_mecanisme (schéma qui se construit) · chiffres_cles · « 3 choses à savoir » · mythe/réalité

## Mises en page (`mise_en_page`) — l'habillage visuel
- `duo` : Lou à gauche, Déco à droite, bulle en bas (l'habillage historique : à ne pas abuser)
- `jt` : faux journal télévisé pixel : Lou présentatrice derrière un bureau, écran derrière elle, bandeau
  « FLASH » et défilant en bas, Déco en duplex dans une incrustation
- `chat` : conversation façon messagerie : les répliques arrivent en bulles de chat dans un téléphone,
  avatars de Lou et Déco, « … en train d'écrire »
- `quiz` : plateau de jeu : question, 2-3 réponses en boutons, compte à rebours, révélation
- `plein_ecran` : personnages en petit dans un coin, contenu (chiffres, schémas) en grand

## Musique (`musique`) — genre du morceau composé (`"musique": {"genre": …}` dans la spec)
synthwave · lofi · trap8bit · orchestral · funk · house · suspense — + `"energie": 1|2|3` par scène
(1 calme, 2 couplet, 3 refrain) et effets `sfx` (impact, whoosh, pop, ding). Ouverture « effroi » possible.

## Voix (`voix`) — combinaison narrateur+mascotte, jamais la même que la vidéo précédente
- V1 Chatterbox femme naturelle : `chatterbox:fr?exag=0.6&cfg=0.4` (calme : exag 0.4 ; dramatique : 0.9)
- V2 Pierre (Chatterbox, homme expressif) : `chatterbox:fr?ref=pierre&exag=0.6&cfg=0.3`
- V3 Jessica (claire et posée) : `piper:fr_FR-upmc-medium?spk=0&vitesse=1.05&expr=0.85&rythme=1.0`
- V4 Jessica expressive (Chatterbox) : `chatterbox:fr?ref=jessica&exag=0.7&cfg=0.35`
- Effets possibles sur Déco : `mascotte_effet` aigu / tres_aigu / grave / aucun
Mettre le choix dans `"voix_override": {"narrateur": …, "mascotte": …, "mascotte_effet": …}`.

## Palettes (`palette`)
pop (jaune/bleu/rose) · nuit_neon (fond nuit, cyan/magenta) · pastel · retro_tv (beige/orange/brun) ·
vert_terminal · rouge_alerte · papier_journal (crème/noir/rouge) — donner `theme.palette` en conséquence.

## Réglages visuels disponibles dans `theme` (à varier à chaque vidéo)
- `mise_en_page` : duo · jt · chat · plein_ecran (quiz = plein_ecran avec des scènes quiz)
- `transition` : pixels · iris · volet · bandes · glitch
- `camera` : zoom · pan · secousse · respire
- `titre` : texte du bandeau défilant (JT)

## Scènes disponibles (mélanger, ne pas répéter le même enchaînement)
hook · kinetic · counter · bars · timeline · dots · compare · outro · **quiz** (question, options, bonne,
revelation en s) · **bigstat** (value, label, source : chiffre géant avec glitch) · **checklist** (title, items
[{texte, etat: vrai|faux|flou}] avec tampons VRAI/FAUX/FLOU)
