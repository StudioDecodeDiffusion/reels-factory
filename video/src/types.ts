export type Theme = {
  fond: string;
  texte: string;
  accent: string;
  accent2: string;
  police_titre: string;
  police_texte: string;
  bandeau?: string | null; // texte du bandeau signature (ex. date), optionnel
  grille?: boolean; // grille fine en fond
};

type Base = {duration: number};

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
  | (Base & {type: 'outro'; text: string; cta: string});

export type VideoSpec = {
  fps?: number;
  music?: string | null; // fichier dans video/public/music/
  theme: Theme;
  scenes: Scene[];
};
