export type Theme = {
  fond: string;
  texte: string;
  accent: string;
  accent2: string;
  police_titre: string;
  police_texte: string;
  bandeau?: string | null; // texte du bandeau signature (ex. date), optionnel
  grille?: boolean; // grille fine en fond
  palette?: string[]; // couleurs vives des fonds de scène (style v2)
  style?: 'pixel' | 'sobre'; // pixel = style coloré animé (défaut), sobre = ancien style
  tenues?: {narrateur?: string; mascotte?: string}; // tenues de l'épisode (voir personnages.ts)
  mise_en_page?: 'duo' | 'jt' | 'chat' | 'quiz' | 'plein_ecran'; // habillage de la vidéo
  transition?: 'pixels' | 'iris' | 'volet' | 'bandes' | 'glitch'; // transition entre scènes
  camera?: 'zoom' | 'pan' | 'secousse' | 'respire'; // mouvement de caméra
  titre?: string; // titre (bandeau défilant du JT)
};

type Base = {
  duration: number;
  voix?: string; // texte de la voix off (sert aussi aux sous-titres)
  voix_duree?: number; // durée réelle de la voix (s), ajoutée au rendu final
  audio?: string | null; // fichier dans video/public/
  sprite?: string; // élément pixel art (voir sprites.ts)
  sprite_anim?: 'bounce' | 'float' | 'shake' | 'spin' | 'grow' | 'rain' | 'orbit';
  mascotte?: 'neutre' | 'content' | 'choc' | 'pense' | 'clin' | 'aucune';
  fond?: string; // couleur de fond de la scène (#RRGGBB) ; sinon palette du thème
  // Format dialogue : Lou (narrateur, à gauche) pose les questions, Déco (mascotte, à droite) répond
  dialogue?: {qui: 'narrateur' | 'mascotte'; texte: string; expression?: string; debut?: number; fin?: number}[];
  tenue_narrateur?: string;
  tenue_mascotte?: string;
};

export type Scene =
  | (Base & {type: 'hook'; title: string; subtitle?: string})
  | (Base & {type: 'kinetic'; lines: string[]; highlight?: string})
  | (Base & {
      type: 'counter';
      from?: number;
      to: number;
      prefix?: string;
      suffix?: string;
      decimals?: number;
      label: string;
    })
  | (Base & {
      type: 'bars';
      title: string;
      items: {label: string; value: number}[];
      unit?: string;
    })
  | (Base & {type: 'timeline'; title?: string; events: {date: string; text: string}[]})
  | (Base & {type: 'dots'; total: number; highlighted: number; label: string})
  | (Base & {
      type: 'compare';
      title?: string;
      left: {label: string; value: string; caption?: string};
      right: {label: string; value: string; caption?: string};
    })
  | (Base & {
      type: 'particles';
      mode: 'gravity' | 'orbit' | 'bounce' | 'swarm' | 'pendulum_wave';
      count?: number;
      caption: string;
    })
  | (Base & {type: 'outro'; text: string; cta: string})
  | (Base & {type: 'quiz'; question: string; options: string[]; bonne: number; revelation?: number})
  | (Base & {type: 'bigstat'; value: string; label: string; source?: string})
  | (Base & {type: 'checklist'; title?: string; items: {texte: string; etat?: 'vrai' | 'faux' | 'flou'}[]})
  | (Base & {type: 'pancartes'; title?: string; items: {pancarte: string; reponse: string}[]})
  | (Base & {type: 'sms'; texte: string; signature?: string; expediteur?: string})
  | (Base & {type: 'debat'; title?: string; pour: string[]; contre: string[]; label_pour?: string; label_contre?: string})
  | (Base & {type: 'reaction'; paliers: {valeur: string; label: string}[]})
  | (Base & {type: 'conte'; titre?: string; texte: string; chute?: string})
  | (Base & {type: 'photo'; src: string; credit: string; titre?: string; legende?: string})
  | (Base & {type: 'pendant'; src?: string; credit?: string; haut: string; bas: string; lignes?: string[]});

export type VideoSpec = {
  fps?: number;
  music?: string | null; // fichier dans video/public/music/
  theme: Theme;
  scenes: Scene[];
};
