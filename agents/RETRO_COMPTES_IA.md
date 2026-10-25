# Rétro-ingénierie des comptes IA de référence (relevé du 24/10/2026, navigateur intégré)

Méthode : top Reel de chaque compte (onglet Reels trié par vues), 10 images régulières par vidéo, + règles « short-form »,
« typography » et « sound-design » d'OpenMontage (calesthio/OpenMontage, AGPL-3, cloné dans /home/claude/calesthio/openmontage).

| Compte | Abonnés | Top Reel | Format | Ce qu'on copie |
|---|---|---|---|---|
| **archive66.tv** | 2 957 | **80,9 k vues** (95 s) | Pixel art réaliste très détaillé (armes, calendrier, piston), fond brun chaud vignetté + grille fine et coins de viseur, titre pixel blanc avec mot-clé jaune, sous-titre blanc + mot jaune en bas | **Notre nouveau style « pixel doc »** : un objet détaillé centré par idée, mécanismes animés (le piston bouge) |
| buildcodia | 2 968 | 10,1 k (25 s) | Dioramas 3D voxel façon jouet, néons, bandeau-titre en haut, gros mot jaune contouré noir au centre-bas | Un seul mot géant par plan, bandeau de chapitre en haut |
| askdraha | 6 (!) | **16,9 k** (66 s) | Simulation scientifique schéma lumineux (blueprint), HUD de données en haut, étiquettes, sous-titres 2 lignes avec mots jaunes | Animation de *fonctionnement* = vues même sans abonnés |
| stickopedie | 17 | 4,3 k (67 s) | Bonhomme bâton sur décors illustrés détaillés, 2/3 image + 1/3 bandeau beige avec 1 mot jaune, tampons « VÉRIDIQUE », mème inséré | Tampons, mème court, structure image/bandeau |
| bearus.ia | 11 | 3,3 k (67 s) | Mascotte (orc) qui parle sur un socle, tier list en cartes avec barres de stats, 1 mot par sous-titre | Mascotte + cartes classement |
| geraldoo.ia | 208 | 2,9 k (35 s) | Fond noir, texte qui s'écrit mot à mot, mots en italique serif rouge, avatar cartoon en bas, cartes d'interface | Révélation mot à mot + accent italique |
| phorsys | 523 | 3,0 k (31 s) | Icônes en trame de points (pixel/halftone), alternance fond noir / fond blanc, mot-clé énorme | Icônes « trame de points », alternance N/B |
| laboscope | 73 | 3,7 k (50 s) | Pixel art scientifique (vertèbres, ADN), cadres de texte bordés cyan façon jeu, étiquettes | Boîtes de dialogue RPG, schémas pixel |
| 1gitparjour | 33 | 125 (52 s) | Interface arcade 8-bit (HI-SCORE, STAGE, POWER-UP) | Codes arcade pour les chiffres |
| cqntdp « Ce qu'on ne te dit pas » | 8 | 152 (72 s) | Fond noir, sujets en pixel flat, encadrés, gros mots blancs, effet néon | (même niche que nous, faible audience : à dépasser) |
| leno_dixsept_17 | 2 006 | 662 (30 s) | Motion design sombre, cartes d'interface en orbite, logo | — |

## Deuxième vague (24/10, 14 h 35)
| Compte | Abonnés | Reel analysé | Format | Ce qu'on copie |
|---|---|---|---|---|
| **phyzolof** | **105 k** | « Le glandu » (95 s, #riolo #lyceens #revolte) | Politique FR : fond sombre texturé, extraits TV/TikTok dans un cadre incliné ou un vieux poste « ARCHIVE », fiches papier (dossier, tableau du budget), gros titres condensés rouge/blanc, compteurs (17 % / 00 %), tampons « ANTÉCÉDENT » | **Notre modèle pour l'actu politique** : fiches papier, tampons, compteurs, poste TV d'archive (avec texte exact à la place des images de presse) |
| **science_in_8bit** | 27,1 k | **1,1 M vues** (39 s) | Scène pixel art complète (coucher de soleil synthwave, voiture sur une boucle), **flèches de forces animées**, boîte de texte RPG en haut | Scènes pixel entières (pas seulement un objet), flèches/vecteurs animés |
| belltakesocial | 27,8 k | 50 s, étude JAVMA 1987 | Chat cartoon qui tombe dans un immeuble dessiné, cartes de graphiques façon presse (FT/NYT), sous-titres serif avec mots rouges, tampon « NOT CORRECTED » | Data-journalisme : chaque chiffre = une carte graphique + étude citée |
| nocodealex | **56,5 k** | 36 s | Personnages-cubes 3D low-poly orange dans des décors 3D (bureau, salle), bandeau-chapitre sur ruban papier, badges compteurs, mots sur étiquettes papier | (même style copié par buildcodia et jacky_west : c'est le format qui marche dans la niche IA) |
| jacky_west | 3,3 k | 35 s | Idem cubes 3D, gros mots blancs contour noir avec mot rouge | — |
| byte.sized.engineering | 567 | 56 s | Pixel art d'ingénierie : turbine qui tourne, manomètres, courbe de pression en direct, UI néon | Mécanismes animés + graphe en direct |
| uncode.ia | 373 | 33 s | Mascottes carrées cartoon dans une ville de nuit, boutique, carte, cartes d'interface, sous-titres en pastilles | — |
| clovis.apps | 7,7 k | 22 s | Visage réel face caméra en bas + cartes d'interface animées en haut (mascotte pixel), fond papier quadrillé | La mise en page « présentateur + écran » (sans visage réel chez nous) |

**Légendes** : la moitié des comptes IA font « Commente MOT et je t'envoie… » (déclenche des commentaires = portée) ;
phyzolof : légende très courte + 3 hashtags d'actu. **Durées** : 22-95 s, les plus vus entre 39 et 95 s.

## Les 10 règles qui en sortent (appliquées par les agents 5, 6, 7, 9)
1. **Un visuel détaillé par idée**, centré, qui bouge (balancement, mécanisme animé) : jamais un écran vide de texte seul.
2. **Mécanisme animé** au moins 1 fois par vidéo (flux d'argent, piston, jauge, engrenage) : c'est ce qui fait 16-80 k vues.
3. **Titre de plan en haut** (pixel ou bold), **mot-clé en jaune** ; 3-5 mots max (OpenMontage : top 40 % de l'écran).
4. **Sous-titres en bas, 1 à 6 mots**, mot prononcé en jaune ; jamais de bloc de texte.
5. **Changement visuel toutes les 2-4 s** (OpenMontage : 58 % de rétention contre 41 % sans).
6. **Voix 180-200 mots/min**, aucune pause ; musique dès la 1re image, baissée de 6-12 dB sous la voix.
7. **Durée** : 25-35 s pour la portée, 50-70 s seulement si l'animation tient l'attention (archive66 fait 95 s).
8. **Habillage constant** = reconnaissable : même cadre (grille, coins, vignette, marque) sur toutes les vidéos d'une série.
9. **Tampons / étiquettes** (« VÉRIDIQUE », « FAUX », HUD de chiffres) pour ponctuer.
10. **Accroche = l'objet du scandale à l'écran + 1 chiffre** dès 0,5 s.

## Image par image (25/10, navigateur intégré, captures toutes les 20 ms autour des changements de plan)
Détection des plans par différence d'images (canvas 24×42), puis planches de 24 images à 20 ms (les Reels sont en
30 images/s : 1 image réelle toutes les 33 ms, les captures à 20 ms montrent donc chaque image).

| Compte | Ce qui se passe, mesuré | Codé dans pixeldoc.tsx |
|---|---|---|
| archive66.tv | **Transition zoom + flou** : le contenu grossit (×1 → ×1,6) et se floute en accélérant pendant 0,2 s (6 images), le plan suivant arrive flou et se resserre en 0,1-0,13 s. Le cadre (grille, coins, marque, sous-titres) ne bouge jamais. Entrée d'objet : petit → taille finale avec léger rebond (0,1 s), étiquette tapée lettre par lettre, mots des sous-titres qui passent du gris au blanc. | `MouvementPixelDoc` (sortie 6 images `Easing.in(cubic)`, entrée 4 images `Easing.out(cubic)`, flou 18/14 px) ; fondu noir supprimé |
| science_in_8bit | **Coupes sèches** toutes les 1-1,5 s entre plusieurs cadrages d'une même scène (plan large → gros plan) ; tout bouge en continu (particules, faisceaux, compteur « 18 MPH », interface magnétoscope « ◀◀ REWIND / ❚❚ PAUSE »). | Gros plan ×1,3 en coupe sèche au milieu de chaque plan de plus de 3,5 s |
| phyzolof (vidéo à 211 k vues, illustration vectorielle) | **Poussée continue** vers le sujet (×1 → ×2,5 en 0,5 s en accélérant) qui traverse l'objet pour révéler le plan suivant (coupe raccord par zoom) ; gouttes flottantes, fond en rayons de soleil, mot du sous-titre surligné jaune. | Poussée lente ×1 → ×1,05 sur chaque plan |
| byte.sized.engineering | Fond de **rayons de vitesse** en pixels qui filent vers l'extérieur ; l'élément 2 glisse depuis le bord en 0,12 s ; **flash blanc** 80 % → 0 en 0,2 s au moment du « VS ». | `Rayons` (pd_versus, pd_chiffre) et `Flash` (pd_versus image 12, pd_tampon image 16) |

Idées non codées (à faire si les vues stagnent) : interface magnétoscope (◀◀ / ❚❚) pour les retours en arrière,
coupe raccord par zoom à travers un objet (phyzolof), particules permanentes dans chaque plan.

## Inspiration imposée par le propriétaire (25/10) : science_in_8bit, Reel DefyD-0DWKd (compte science, vidéo Microduck)
- **Format court en boucle : 15 s.** Une seule scène pixel « cosy » : un petit robot mignon avec un casque audio, à un bureau,
  la nuit, fenêtre sur la ville, guirlande lumineuse, poster de planète, chat qui dort.
- **Une émotion, une action** : le robot écoute sa musique, puis tourne la tête vers le spectateur (yeux qui clignent,
  coeur) ; boîte de texte RPG en haut (« HE DIDN'T KNOW YOU WERE WATCHING »).
- **Légende** : le fait scientifique + la source de l'étude entre parenthèses, puis « Send this to someone who… »,
  4 hashtags (#pixelart #robot #cozy #science).
- **À reprendre pour Microduck** : 20-30 s, Microduck dessiné en pixel art (sans logo), scène cosy, il marche,
  trébuche, se rattrape (= l'équilibre appris par simulation), 2-3 bulles RPG avec les vrais chiffres (prix, ventes,
  ce qu'il a dans le ventre), fin en boucle sur la première image, légende avec sources + « Envoie ça à… ».
