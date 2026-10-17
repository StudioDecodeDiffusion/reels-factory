// Personnages originaux du studio : « Lou » (narrateur·rice, à gauche) et « Déco » (mascotte, à droite).
// Chibi pixel art : grosse tête, visages très expressifs, tenues interchangeables.
import {Sprite} from './sprites';

// Lettres spéciales recolorées selon la tenue : h = cheveux, C = haut, D = bas, E = détail du haut
export const LOU: Sprite = [
  '.......kkkkkkkk.......',
  '.....kkhhhhhhhhkk.....',
  '....khhhhhhhhhhhhk....',
  '...khhhhhhhhhhhhhhk...',
  '..khhhhhhhhhhhhhhhhk..',
  '..khhhhhssssshhhhhhk..',
  '..khhhsssssssssshhhk..',
  '.khhsssssssssssssshhk.',
  '.khssssssssssssssssk..',
  '.khssssssssssssssssk..',
  '.kssssssssssssssssssk.',
  '.kssssssssssssssssssk.',
  '.kssssssssssssssssssk.',
  '..ksssssssssssssssk...',
  '...kkssssssssssskk....',
  '.....kkkkkkkkkkk......',
  '.......kssssk.........',
  '.....kkCCCCCCkk.......',
  '....kCCCCEECCCCk......',
  '...kCCCCCEECCCCCk.....',
  '...ksCCCCEECCCCsk.....',
  '...kskCCCCCCCCksk.....',
  '....kkCCCCCCCCkk......',
  '.....kDDDDkDDDDk......',
  '.....kDDDk.kDDDk......',
  '.....kkkk..kkkkk......',
];

// Visages de Lou : 14×7, posés en (x=3, y=7)
export const VISAGES_LOU: Record<string, Sprite> = {
  neutre: ['..............', '...kk....kk...', '...kk....kk...', '..............', '..............', '.....kkkk.....', '..............'],
  parle: ['..............', '...kk....kk...', '...kk....kk...', '..............', '.....kkkk.....', '.....kRRk.....', '......kk......'],
  content: ['..............', '..k..k..k..k..', '...kk....kk...', '..pp......pp..', '....k....k....', '.....kkkk.....', '..............'],
  rire: ['..............', '..kkk....kkk..', '..............', '..pp......pp..', '....kkkkkk....', '....kRRRRk....', '.....kkkk.....'],
  choc: ['..kkk....kkk..', '..kwk....kwk..', '..kkk....kkk..', '..............', '......kk......', '.....kRRk.....', '......kk......'],
  pense: ['....kk....kk..', '....kk....kk..', '..............', '..............', '..............', '......kkk.....', '..............'],
  clin: ['..............', '...kk.........', '...kk...kkk...', '..pp......pp..', '....k....k....', '.....kkkk.....', '..............'],
  triste: ['....k....k....', '...kk....kk...', '...kk....kk...', '..............', '.....kkkk.....', '....k....k....', '..............'],
  colere: ['..k........k..', '...kk....kk...', '...kk....kk...', '..............', '..............', '....kkkkkk....', '..............'],
};

// Tenues : couleurs + accessoires (tête / visage / cou), communes à Lou et Déco
export type Tenue = {haut: string; bas: string; detail: string; tete?: string; visage?: string; cou?: string; cheveux?: string};

export const TENUES: Record<string, Tenue> = {
  classique: {haut: '#3D5AFE', bas: '#2733A8', detail: '#FFFFFF'},
  economie: {haut: '#FFFFFF', bas: '#3B3F55', detail: '#FF3B3B', cou: 'cravate'},
  qhse: {haut: '#FFD23F', bas: '#2733A8', detail: '#C9CCD6', tete: 'casque_chantier'},
  science: {haut: '#FFFFFF', bas: '#3D5AFE', detail: '#4FD6FF', visage: 'lunettes'},
  detective: {haut: '#A0652F', bas: '#6B3E17', detail: '#FFD23F', tete: 'chapeau_detective'},
  sport: {haut: '#8BE04E', bas: '#2E9E4F', detail: '#FFFFFF', tete: 'casquette'},
  hiver: {haut: '#FF3B3B', bas: '#2733A8', detail: '#FFFFFF', tete: 'bonnet', cou: 'echarpe'},
  fete: {haut: '#FF4F81', bas: '#8E5CFF', detail: '#FFD23F', tete: 'couronne', cou: 'noeud'},
  musique: {haut: '#14131C', bas: '#14131C', detail: '#FF4F81', tete: 'casque_audio'},
  ecologie: {haut: '#2EC4B6', bas: '#168A80', detail: '#8BE04E', tete: 'feuille_tete'},
};

// Accessoires (posés par rapport au coin haut-gauche du personnage)
export const ACCESSOIRES: Record<string, {sprite: Sprite; lou: [number, number]; deco: [number, number]}> = {
  casque_chantier: {
    sprite: ['......kkkkkkkkkk......', '....kkyyyyyyyyyykk....', '...kyyyyyyykyyyyyyk...', '..kyyyyyyyykyyyyyyyk..', '..kyyyyyyyykyyyyyyyk..', 'kkkkkkkkkkkkkkkkkkkkkk', 'kYYYYYYYYYYYYYYYYYYYYk', 'kkkkkkkkkkkkkkkkkkkkkk'],
    lou: [0, -3],
    deco: [-1, -1],
  },
  casquette: {
    sprite: ['.....kkkkkkkkkk.......', '...kkllllllllllkk.....', '..klllllllllllllk.....', '..kllllllwwllllllk....', '..kkkkkkkkkkkkkkkkkkkk', '..............kLLLLLLk', '...............kkkkkk.'],
    lou: [0, -2],
    deco: [-1, 0],
  },
  chapeau_detective: {
    sprite: ['......kkkkkkkk........', '....kknnnnnnnnkk......', '...knnnnnnnnnnnnk.....', '...kNNNNNNNNNNNNk.....', '.kkkkkkkkkkkkkkkkkk...', 'knnnnnnnnnnnnnnnnnnk..', '.kkkkkkkkkkkkkkkkkk...'],
    lou: [1, -3],
    deco: [0, -1],
  },
  bonnet: {
    sprite: ['.........kk...........', '........kwwk..........', '......kkkwwkkk........', '....kkrrrrrrrrkk......', '...krrrrrrrrrrrrk.....', '..krrrrrrrrrrrrrrk....', '..kwwwwwwwwwwwwwwk....', '..kkkkkkkkkkkkkkkk....'],
    lou: [1, -3],
    deco: [0, -2],
  },
  couronne: {
    sprite: ['..k...k...k...k...', '.kyk.kyk.kyk.kyk..', '.kyykyyykyyykyyk..', '.kyyyyyryyyyyyyk..', '.kyyyyyyyyyyyyyk..', '.kkkkkkkkkkkkkkk..'],
    lou: [2, -3],
    deco: [1, -1],
  },
  casque_audio: {
    sprite: ['.....kkkkkkkkkk.....', '...kkGGGGGGGGGGkk...', '..kGk..........kGk..', '.kGk............kGk.', '.kk..............kk.', 'kppk............kppk', 'kppk............kppk', 'kppk............kppk', '.kk..............kk.'],
    lou: [1, 1],
    deco: [0, 4],
  },
  feuille_tete: {
    sprite: ['.........kk...', '.......kkllk..', '......kllllk..', '.....kllLlk...', '....kllLlk....', '.....kLkk.....', '......k.......'],
    lou: [6, -5],
    deco: [6, -3],
  },
  lunettes: {
    sprite: ['kkkkkk..kkkkkk', 'kcwcck..kcwcck', 'kcccckkkkcccck', 'kkkkkk..kkkkkk'],
    lou: [4, 7],
    deco: [3, 8],
  },
  cravate: {
    sprite: ['..kk..', '.krrk.', '..kk..', '.krrk.', '.krrk.', '.krrk.', '..kk..'],
    lou: [7, 17],
    deco: [7, 15],
  },
  noeud: {
    sprite: ['kk..kk', 'kyykyyk', 'kyyyyyk', 'kyykyyk', 'kk..kk'],
    lou: [7, 16],
    deco: [7, 15],
  },
  echarpe: {
    sprite: ['.kkkkkkkkkkk..', 'kwwrrwwrrwwrk.', '.kkkkkkkkwrk..', '........kwrk..', '........kkk...'],
    lou: [4, 15],
    deco: [3, 15],
  },
};
