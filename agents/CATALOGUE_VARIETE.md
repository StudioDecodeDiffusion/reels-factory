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
· **pancartes** (title, items [{pancarte, reponse}] : le fantôme brandit une idée reçue, la réponse chiffrée la tamponne)
· **sms** (texte, signature, expediteur : SMS anonyme « -A » qui s'écrit) · **debat** (title, pour[], contre[],
label_pour, label_contre : balance qui penche) · **reaction** (paliers [{valeur, label}] : trend « My reaction to… »,
Déco réagit de plus en plus fort) · **conte** (titre, texte, chute : « il était une fois », parchemin, boîte à musique)
Genres de musique en plus : **boite_a_musique** · **epique**
· **photo** (src = URL d'une image sous licence libre, credit = auteur + licence, titre, legende : vraie photo avec
effet Ken Burns — de temps en temps, pour sortir du pixel art)

## Style « éditorial » (prioritaire désormais) — motion design soigné façon médias d'info
`theme.style = "editorial"` : plus de personnages pixel, voix off seule, typographie serif (DM Serif Display) + grotesque
(Archivo Black), grille fine, barre de progression, sous-titres karaoké en capitales, transitions nettes.
Scènes : **ed_titre** (kicker, titre, mot_fort, sous_titre) · **ed_chiffre** (valeur, decimales, prefixe, suffixe, legende,
source) · **ed_citation** (texte, auteur) · **ed_photo** (src Wikimedia/licence libre, credit, kicker, titre) · **ed_liste**
(kicker, titre, points[]) · **ed_versus** (kicker, titre, gauche{label,valeur}, droite{label,valeur}).
Couleurs : `theme.fond` (fond), `theme.texte` (encre), `theme.accent` (couleur d'alerte) — varier d'une vidéo à l'autre.
Le pixel art reste possible en exception (1 vidéo sur 4 au plus).

## Personnages « cartoon » (remplacent peu à peu le pixel art)
`theme.persos = "cartoon"` (avec `style: "pixel"`, mises en page duo, jt, plein_ecran) : personnages vectoriels ORIGINAUX
(jamais de personnage existant), fond dégradé doux. Expressions par réplique : neutre, content, rire, choc, peur, colere,
triste, pense, clin, sarcasme, degout (sourcils, yeux, bouche, larmes, sueur, rougeurs, gestes des bras assortis).
Tenues (`theme.tenues` ou `tenue_narrateur` / `tenue_mascotte` par scène) : classique, economie, qhse, science, detective,
sport, hiver, fete, musique, ecologie, gilet_jaune, ouvrier, infirmier, milliardaire, roi, manifestant, etudiant, robe.
Changer d'expression à CHAQUE réplique et de tenue selon le rôle joué (ex. Déco en milliardaire, Lou en gilet jaune).
Répartition visée : éditorial 1 vidéo sur 2, cartoon 1 sur 3, pixel au plus 1 sur 6.

## Images de gens (prioritaire : les visages font cliquer)
- **Vraies photos et vidéos de gens sous licence libre**, URL directe du fichier dans une scène `ed_photo`
  (`src` .jpg/.png ou .mp4 ; `debut_s` pour démarrer un extrait) : Pexels (images.pexels.com, videos.pexels.com),
  Unsplash (images.unsplash.com), Pixabay — licences gratuites, usage commercial permis, crédit « Pexels / Nom » quand connu.
  Chercher avec WebSearch « pexels manifestation france », « pexels station essence », « pexels retraités »,
  « pexels caissière », etc. Préférer des gens reconnaissables comme « monsieur/madame tout-le-monde », pas des
  personnes privées présentées comme impliquées dans le sujet.
- **Figures de pouvoir** (président, ministres, PDG) : photos Wikimedia Commons sous licence libre ; discours officiels :
  scène `ed_allocution` (reconstitution + texte exact).
- **Interdit** : images de presse et d'agences (AFP, Reuters, BFM, franceinfo…), captures de JT, vidéos YouTube.
