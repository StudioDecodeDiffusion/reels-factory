// Personnages « cartoon » vectoriels (style dessin animé détaillé, personnages ORIGINAUX) :
// expressions du visage riches, tenues variées, gestes, clignements, synchro labiale, respiration.
// Remplace les sprites pixel quand theme.persos === 'cartoon' (contexte StylePerso).
import React, {createContext, useContext} from 'react';
import {spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {INK} from './fx';

export const StylePerso = createContext<'pixel' | 'cartoon'>('pixel');
export const useStylePerso = () => useContext(StylePerso);

type Tenue = {
  haut: string; bas: string; detail: string; type: 'chemise' | 'costume' | 'sweat' | 'gilet' | 'blouse' | 'bleu' | 'tshirt' | 'doudoune' | 'imper' | 'survet' | 'robe';
  chapeau?: 'casque_chantier' | 'casquette' | 'bonnet' | 'detective' | 'couronne' | 'casque_audio' | 'haut_de_forme';
  lunettes?: boolean;
};

export const TENUES_CARTOON: Record<string, Tenue> = {
  classique: {type: 'chemise', haut: '#4C7BD9', bas: '#2B2F45', detail: '#FFFFFF'},
  economie: {type: 'costume', haut: '#2E3A59', bas: '#232A40', detail: '#D7263D'},
  qhse: {type: 'gilet', haut: '#F2C200', bas: '#2B2F45', detail: '#E6E6E6', chapeau: 'casque_chantier'},
  science: {type: 'blouse', haut: '#F4F4F4', bas: '#3A3F58', detail: '#4C7BD9', lunettes: true},
  detective: {type: 'imper', haut: '#B08A57', bas: '#3B3328', detail: '#5A4630', chapeau: 'detective'},
  sport: {type: 'survet', haut: '#E63946', bas: '#1D3557', detail: '#FFFFFF'},
  hiver: {type: 'doudoune', haut: '#2A9D8F', bas: '#264653', detail: '#E9C46A', chapeau: 'bonnet'},
  fete: {type: 'tshirt', haut: '#FF4F81', bas: '#3D2C8D', detail: '#FFD23F'},
  musique: {type: 'sweat', haut: '#6C4AB6', bas: '#1F1D36', detail: '#FFD23F', chapeau: 'casque_audio'},
  ecologie: {type: 'tshirt', haut: '#3FA34D', bas: '#5C4033', detail: '#C7F9CC'},
  gilet_jaune: {type: 'gilet', haut: '#E6F500', bas: '#3A3A4A', detail: '#D9D9D9'},
  ouvrier: {type: 'bleu', haut: '#1F4E9A', bas: '#1F4E9A', detail: '#F2A900', chapeau: 'casquette'},
  infirmier: {type: 'blouse', haut: '#7FC8C2', bas: '#7FC8C2', detail: '#FFFFFF'},
  milliardaire: {type: 'costume', haut: '#111111', bas: '#111111', detail: '#C9A227', chapeau: 'haut_de_forme'},
  roi: {type: 'costume', haut: '#5B1A8B', bas: '#2B0F45', detail: '#F2C200', chapeau: 'couronne'},
  manifestant: {type: 'sweat', haut: '#D7263D', bas: '#2B2F45', detail: '#FFFFFF', chapeau: 'casquette'},
  etudiant: {type: 'sweat', haut: '#3E8EDE', bas: '#495057', detail: '#FFD23F'},
  robe: {type: 'robe', haut: '#C2185B', bas: '#C2185B', detail: '#FFD6E7'},
};

type Morpho = {peau: string; ombre: string; cheveux: string; coiffure: 'carre' | 'boucles' | 'chignon' | 'court'; levres: string};
const LOU: Morpho = {peau: '#F2C9A8', ombre: '#DCA584', cheveux: '#3B2416', coiffure: 'carre', levres: '#C25B5B'};
const DECO: Morpho = {peau: '#A8704B', ombre: '#8A5838', cheveux: '#17120F', coiffure: 'boucles', levres: '#7A3E2E'};

// ───────── visage
const Yeux: React.FC<{e: string; cligne: boolean; regard: number; m: Morpho}> = ({e, cligne, regard, m}) => {
  const ouvert = cligne ? 0.08 : e === 'sarcasme' ? 0.45 : e === 'choc' || e === 'peur' ? 1.25 : e === 'rire' ? 0.15 : e === 'colere' ? 0.7 : 1;
  const px = regard * 4 + (e === 'pense' ? 5 : 0);
  const py = e === 'pense' ? -6 : e === 'triste' ? 3 : 0;
  const oeil = (cx: number, droit: boolean) => {
    if (e === 'clin' && droit) return <path d={`M${cx - 15} ${150} Q${cx} ${140} ${cx + 15} ${150}`} stroke={INK} strokeWidth={5} fill="none" strokeLinecap="round" />;
    if (e === 'rire' || (e === 'content' && !cligne)) return <path d={`M${cx - 15} ${152} Q${cx} ${136} ${cx + 15} ${152}`} stroke={INK} strokeWidth={5.5} fill="none" strokeLinecap="round" />;
    return (
      <g>
        <ellipse cx={cx} cy={148} rx={15} ry={17 * ouvert} fill="#fff" stroke={INK} strokeWidth={3.5} />
        {ouvert > 0.2 ? <circle cx={cx + px} cy={148 + py} r={e === 'choc' || e === 'peur' ? 5 : 8} fill="#2A1C14" /> : null}
        {ouvert > 0.2 ? <circle cx={cx + px + 3} cy={145 + py} r={2.4} fill="#fff" /> : null}
      </g>
    );
  };
  // sourcils : angle par expression
  const s = {neutre: [0, 0], parle: [-2, 0], content: [-4, 0], rire: [-6, 0], choc: [-14, 0], peur: [-10, 12], colere: [6, 22], triste: [-6, -18], pense: [-8, 10], clin: [-4, 0], sarcasme: [-12, -10], degout: [4, 14]}[e] ?? [0, 0];
  const sourcil = (cx: number, signe: number) => (
    <rect x={cx - 17} y={124 + s[0]} width={34} height={7} rx={3.5} fill={m.cheveux} transform={`rotate(${s[1] * signe} ${cx} ${127 + s[0]})`} />
  );
  return (
    <g>
      {oeil(124, false)}
      {oeil(196, true)}
      {sourcil(124, 1)}
      {sourcil(196, -1)}
    </g>
  );
};

const Bouche: React.FC<{e: string; ouverture: number; m: Morpho}> = ({e, ouverture, m}) => {
  if (ouverture > 0.05) {
    const h = 6 + ouverture * 22;
    const w = e === 'choc' || e === 'peur' ? 16 : 24;
    return (
      <g>
        <ellipse cx={160} cy={198} rx={w} ry={h} fill="#5A1E1E" stroke={INK} strokeWidth={3.5} />
        <ellipse cx={160} cy={198 + h * 0.55} rx={w * 0.6} ry={h * 0.35} fill="#E57373" />
        <rect x={160 - w * 0.7} y={198 - h + 1} width={w * 1.4} height={Math.min(7, h * 0.4)} rx={2} fill="#fff" />
      </g>
    );
  }
  const P: Record<string, string> = {
    neutre: 'M140 198 Q160 204 180 198',
    content: 'M134 192 Q160 222 186 192',
    rire: 'M130 188 Q160 236 190 188 Z',
    choc: '',
    peur: 'M142 204 Q151 196 160 204 Q169 212 178 204',
    colere: 'M138 206 Q160 192 182 206',
    triste: 'M138 208 Q160 192 182 208',
    pense: 'M146 200 Q164 196 178 202',
    clin: 'M136 194 Q160 216 184 192',
    sarcasme: 'M140 202 Q166 202 184 190',
    degout: 'M138 202 Q148 194 160 202 Q172 210 182 198',
  };
  if (e === 'choc') return <ellipse cx={160} cy={202} rx={12} ry={15} fill="#5A1E1E" stroke={INK} strokeWidth={3.5} />;
  const d = P[e] ?? P.neutre;
  return <path d={d} stroke={INK} strokeWidth={5} fill={e === 'rire' ? '#5A1E1E' : 'none'} strokeLinecap="round" strokeLinejoin="round" />;
};

const Cheveux: React.FC<{m: Morpho; arriere: boolean}> = ({m, arriere}) => {
  const c = m.cheveux;
  if (m.coiffure === 'carre')
    return arriere ? (
      <path d="M78 140 Q70 60 160 52 Q250 60 242 140 L246 232 Q220 246 206 226 L114 226 Q100 246 74 232 Z" fill={c} />
    ) : (
      <path d="M92 132 Q100 74 160 70 Q226 74 230 136 Q196 104 150 102 Q118 104 92 132 Z" fill={c} stroke={INK} strokeWidth={3} />
    );
  if (m.coiffure === 'boucles')
    return arriere ? null : (
      <g fill={c} stroke={INK} strokeWidth={3}>
        {[[100, 108, 26], [126, 86, 28], [160, 78, 30], [194, 86, 28], [220, 108, 26], [112, 128, 18], [208, 128, 18]].map(([x, y, r], i) => (
          <circle key={i} cx={x} cy={y} r={r} />
        ))}
      </g>
    );
  return arriere ? null : <path d="M94 128 Q104 72 160 70 Q218 72 226 128 Q190 98 160 104 Q128 98 94 128 Z" fill={c} stroke={INK} strokeWidth={3} />;
};

const Chapeau: React.FC<{t?: Tenue['chapeau']; d: string}> = ({t, d}) => {
  if (!t) return null;
  const s = {stroke: INK, strokeWidth: 4};
  switch (t) {
    case 'casque_chantier':
      return <g><path d="M86 112 Q90 52 160 48 Q230 52 234 112 Z" fill="#F2C200" {...s} /><rect x={72} y={106} width={176} height={16} rx={8} fill="#F2C200" {...s} /></g>;
    case 'casquette':
      return <g><path d="M92 108 Q96 58 160 56 Q224 58 228 108 Z" fill={d} {...s} /><path d="M196 104 Q250 100 262 116 L200 118 Z" fill={d} {...s} /></g>;
    case 'bonnet':
      return <g><path d="M90 116 Q92 50 160 46 Q228 50 230 116 Z" fill={d} {...s} /><rect x={84} y={104} width={152} height={22} rx={10} fill="#fff" {...s} /><circle cx={160} cy={44} r={16} fill="#fff" {...s} /></g>;
    case 'detective':
      return <g><ellipse cx={160} cy={104} rx={102} ry={18} fill="#5A4630" {...s} /><path d="M106 102 Q108 50 160 48 Q212 50 214 102 Z" fill="#7A6040" {...s} /><rect x={108} y={86} width={104} height={12} fill="#2B2118" /></g>;
    case 'couronne':
      return <path d="M104 96 L112 46 L136 76 L160 36 L184 76 L208 46 L216 96 Z" fill="#F2C200" {...s} />;
    case 'haut_de_forme':
      return <g><ellipse cx={160} cy={98} rx={92} ry={14} fill="#111" {...s} /><rect x={112} y={20} width={96} height={80} rx={6} fill="#111" {...s} /><rect x={112} y={78} width={96} height={12} fill="#C9A227" /></g>;
    case 'casque_audio':
      return <g fill={INK}><path d="M92 150 Q92 60 160 58 Q228 60 228 150" fill="none" stroke={INK} strokeWidth={10} /><rect x={78} y={132} width={26} height={44} rx={10} fill={d} stroke={INK} strokeWidth={4} /><rect x={216} y={132} width={26} height={44} rx={10} fill={d} stroke={INK} strokeWidth={4} /></g>;
  }
  return null;
};

// ───────── corps et tenue
const Torse: React.FC<{t: Tenue}> = ({t}) => {
  const s = {stroke: INK, strokeWidth: 4.5, strokeLinejoin: 'round' as const};
  const base = <path d="M86 268 Q90 240 130 232 L190 232 Q230 240 234 268 L242 404 L78 404 Z" fill={t.haut} {...s} />;
  const det: React.ReactNode[] = [];
  switch (t.type) {
    case 'costume':
      det.push(<path key="c" d="M134 234 L160 300 L186 234 Z" fill="#F5F5F5" stroke={INK} strokeWidth={3} />);
      det.push(<path key="t" d="M154 246 L166 246 L172 318 L160 334 L148 318 Z" fill={t.detail} stroke={INK} strokeWidth={3} />);
      det.push(<path key="l" d="M130 234 L160 330 L112 270 Z M190 234 L160 330 L208 270 Z" fill={t.haut} stroke={INK} strokeWidth={3} />);
      break;
    case 'chemise':
      det.push(<path key="c" d="M136 232 L160 258 L184 232 L176 250 L160 262 L144 250 Z" fill={t.detail} stroke={INK} strokeWidth={3} />);
      [290, 322, 354].forEach((y) => det.push(<circle key={y} cx={160} cy={y} r={4} fill={t.detail} />));
      break;
    case 'sweat':
      det.push(<path key="h" d="M118 236 Q160 278 202 236" fill="none" stroke={INK} strokeWidth={4} />);
      det.push(<rect key="p" x={118} y={330} width={84} height={40} rx={14} fill="rgba(0,0,0,0.12)" stroke={INK} strokeWidth={3} />);
      det.push(<path key="f" d="M146 250 L144 296 M174 250 L176 296" stroke={t.detail} strokeWidth={4} strokeLinecap="round" />);
      break;
    case 'gilet':
      det.push(<path key="s" d="M88 330 L232 330 M86 360 L234 360" stroke={t.detail} strokeWidth={12} />);
      det.push(<path key="v" d="M160 236 L160 404" stroke={INK} strokeWidth={3} />);
      break;
    case 'blouse':
      det.push(<path key="r" d="M132 234 L160 290 L188 234" fill="none" stroke={INK} strokeWidth={3.5} />);
      det.push(<rect key="p" x={186} y={300} width={30} height={34} rx={4} fill="none" stroke={INK} strokeWidth={3} />);
      det.push(<path key="s" d="M196 292 L196 318" stroke={t.detail} strokeWidth={5} strokeLinecap="round" />);
      break;
    case 'bleu':
      det.push(<path key="z" d="M160 236 L160 404" stroke={t.detail} strokeWidth={4} />);
      det.push(<rect key="p1" x={104} y={290} width={36} height={30} rx={4} fill="none" stroke={t.detail} strokeWidth={3} />);
      det.push(<rect key="p2" x={180} y={290} width={36} height={30} rx={4} fill="none" stroke={t.detail} strokeWidth={3} />);
      break;
    case 'tshirt':
      det.push(<circle key="l" cx={160} cy={310} r={26} fill={t.detail} stroke={INK} strokeWidth={3} />);
      break;
    case 'doudoune':
      [276, 312, 348, 384].forEach((y) => det.push(<path key={y} d={`M84 ${y} Q160 ${y + 8} 236 ${y}`} fill="none" stroke={INK} strokeWidth={3} />));
      det.push(<path key="z" d="M160 236 L160 404" stroke={t.detail} strokeWidth={4} />);
      break;
    case 'imper':
      det.push(<path key="c" d="M126 232 L160 290 L194 232 L210 262 L160 300 L110 262 Z" fill={t.detail} stroke={INK} strokeWidth={3} />);
      det.push(<rect key="ce" x={84} y={340} width={152} height={14} fill={t.detail} stroke={INK} strokeWidth={3} />);
      break;
    case 'survet':
      det.push(<path key="b" d="M100 250 L92 400 M220 250 L228 400" stroke={t.detail} strokeWidth={8} />);
      det.push(<path key="z" d="M160 236 L160 404" stroke={t.detail} strokeWidth={4} />);
      break;
    case 'robe':
      det.push(<path key="c" d="M130 236 Q160 262 190 236" fill="none" stroke={t.detail} strokeWidth={6} />);
      break;
  }
  return <g>{base}{det}</g>;
};

// bras : angles (épaule, coude) selon le geste
const GESTES: Record<string, [number, number, number, number]> = {
  // [épaule gauche, coude gauche, épaule droite, coude droit] en degrés (0 = bras le long du corps)
  repos: [8, 0, -8, 0],
  parle: [22, -40, -10, 0],
  explique: [40, -70, -40, 70],
  choc: [150, 20, -150, -20],
  colere: [30, -110, -30, 110],
  pense: [10, 0, -40, 140],
  content: [140, -20, -10, 0],
  triste: [4, 0, -4, 0],
  montre: [8, 0, -95, 0],
  hausse: [60, -100, -60, 100],
};

const Bras: React.FC<{cote: 1 | -1; epaule: number; coude: number; t: Tenue; peau: string}> = ({cote, epaule, coude, t, peau}) => {
  const x = cote === 1 ? 96 : 224;
  const manche = t.type === 'tshirt' || t.type === 'robe' ? peau : t.haut;
  return (
    <g transform={`rotate(${epaule} ${x} 250)`}>
      <rect x={x - 16} y={244} width={32} height={78} rx={16} fill={t.haut} stroke={INK} strokeWidth={4} />
      <g transform={`rotate(${coude} ${x} 314)`}>
        <rect x={x - 14} y={306} width={28} height={70} rx={14} fill={manche} stroke={INK} strokeWidth={4} />
        <circle cx={x} cy={384} r={17} fill={peau} stroke={INK} strokeWidth={4} />
      </g>
    </g>
  );
};

const GESTE_PAR_EXPR: Record<string, string> = {choc: 'choc', peur: 'choc', colere: 'colere', pense: 'pense', content: 'content', rire: 'content', triste: 'triste', sarcasme: 'hausse', degout: 'hausse', clin: 'montre'};

export const PersoCartoon: React.FC<{qui: 'narrateur' | 'mascotte'; expression: string; parle: boolean; tenue?: string; x: number; sol: number; entree?: number; echelle?: number}> = ({qui, expression, parle, tenue = 'classique', x, sol, entree = 0, echelle = 1}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const f = frame - entree;
  const lou = qui === 'narrateur';
  const m = lou ? LOU : DECO;
  const t = TENUES_CARTOON[tenue] ?? TENUES_CARTOON.classique;
  const pop = spring({frame: f, fps, config: {damping: 12, mass: 0.8}});
  const seed = lou ? 0 : 37;
  const cligne = (f + seed) % 96 > 90 && !['rire', 'clin'].includes(expression);
  // synchro labiale : ouverture pseudo-aléatoire rythmée par syllabes
  const ouverture = parle ? Math.max(0, Math.sin(f * 1.3 + seed) * 0.6 + Math.sin(f * 0.47) * 0.4) : expression === 'choc' || expression === 'peur' ? 0 : 0;
  const geste = parle ? (Math.floor((f + seed) / 45) % 2 === 0 ? 'parle' : 'explique') : GESTE_PAR_EXPR[expression] ?? 'repos';
  const g = GESTES[geste];
  const balance = Math.sin((f + seed) / 11) * (parle ? 6 : 3);
  const respire = 1 + Math.sin((f + seed) / 14) * 0.012;
  const tete = Math.sin((f + seed) / 17) * (parle ? 5 : 2.5) + (expression === 'pense' ? 9 : expression === 'triste' ? -6 : 0);
  const hoche = parle ? Math.abs(Math.sin(f / 4)) * -5 : 0;
  const sursaut = expression === 'choc' && f < 12 ? -Math.sin((f / 12) * Math.PI) * 40 : 0;
  const tremble = expression === 'peur' || expression === 'colere' ? Math.sin(f * 2.1) * 2.5 : 0;
  const regard = lou ? 1 : -1;
  const L = 320 * echelle;
  const Hh = 560 * echelle;
  return (
    <div style={{position: 'absolute', left: x, top: sol - Hh + (1 - pop) * 500 + sursaut, width: L, height: Hh, transform: `rotate(${balance * 0.3 + tremble}deg) scaleY(${respire})`, transformOrigin: 'bottom center', filter: 'drop-shadow(10px 12px 0 rgba(20,19,28,0.28))'}}>
      <svg viewBox="0 0 320 560" width={L} height={Hh}>
        {/* jambes */}
        <rect x={112} y={396} width={42} height={130} rx={16} fill={t.bas} stroke={INK} strokeWidth={4.5} />
        <rect x={166} y={396} width={42} height={130} rx={16} fill={t.bas} stroke={INK} strokeWidth={4.5} />
        <path d="M100 520 Q104 506 156 508 L158 540 L98 540 Z" fill="#2B2118" stroke={INK} strokeWidth={4} />
        <path d="M164 508 Q216 506 222 520 L224 540 L162 540 Z" fill="#2B2118" stroke={INK} strokeWidth={4} />
        {/* bras arrière + torse + bras avant */}
        <Bras cote={1} epaule={g[0]} coude={g[1]} t={t} peau={m.peau} />
        <Torse t={t} />
        <Bras cote={-1} epaule={g[2]} coude={g[3]} t={t} peau={m.peau} />
        {/* cou + tête */}
        <rect x={142} y={210} width={36} height={34} fill={m.ombre} stroke={INK} strokeWidth={4} />
        <g transform={`translate(0 ${hoche}) rotate(${tete} 160 230)`}>
          <Cheveux m={m} arriere />
          <ellipse cx={86} cy={160} rx={14} ry={20} fill={m.peau} stroke={INK} strokeWidth={4} />
          <ellipse cx={234} cy={160} rx={14} ry={20} fill={m.peau} stroke={INK} strokeWidth={4} />
          <path d="M88 150 Q88 72 160 72 Q232 72 232 150 Q232 236 160 236 Q88 236 88 150 Z" fill={expression === 'colere' ? '#E8907A' : m.peau} stroke={INK} strokeWidth={4.5} />
          {['content', 'rire', 'clin'].includes(expression) || (lou && expression === 'neutre') ? (
            <g fill="#FF8FA3" opacity={0.55}><ellipse cx={110} cy={186} rx={16} ry={9} /><ellipse cx={210} cy={186} rx={16} ry={9} /></g>
          ) : null}
          <Yeux e={expression} cligne={cligne} regard={regard} m={m} />
          <path d="M156 160 Q150 180 160 184 Q168 184 166 178" fill="none" stroke={m.ombre} strokeWidth={4} strokeLinecap="round" />
          <Bouche e={parle && ouverture > 0.05 ? expression : expression} ouverture={parle ? ouverture : 0} m={m} />
          {lou ? <path d="M146 198 Q160 196 174 198" stroke={m.levres} strokeWidth={0} /> : null}
          {expression === 'peur' || expression === 'choc' ? <path d="M226 112 Q236 128 226 136 Q216 128 226 112 Z" fill="#7FD1FF" stroke={INK} strokeWidth={2.5} /> : null}
          {expression === 'triste' ? <path d={`M118 ${168 + (f % 30)} q-5 10 0 14 q5 -4 0 -14 Z`} fill="#7FD1FF" stroke={INK} strokeWidth={2} /> : null}
          {expression === 'colere' ? <path d="M206 86 l10 10 m0 -10 l-10 10" stroke="#C0392B" strokeWidth={5} strokeLinecap="round" /> : null}
          {t.lunettes ? (
            <g fill="rgba(255,255,255,0.15)" stroke={INK} strokeWidth={4}><circle cx={124} cy={148} r={24} /><circle cx={196} cy={148} r={24} /><path d="M148 146 L172 146" /></g>
          ) : null}
          <Cheveux m={m} arriere={false} />
          <Chapeau t={t.chapeau} d={t.detail === '#FFFFFF' ? t.haut : t.detail} />
        </g>
      </svg>
    </div>
  );
};

// Fond doux (dégradé + formes floues qui dérivent) pour le style cartoon
export const FondCartoon: React.FC<{couleur: string; seed: number}> = ({couleur, seed}) => {
  const frame = useCurrentFrame();
  const formes = [0, 1, 2, 3].map((k) => {
    const a = (seed * 1.7 + k * 2.1) % 6.28;
    return {x: 540 + Math.cos(a + frame / 160) * (260 + k * 60), y: 700 + Math.sin(a * 1.3 + frame / 190) * (380 + k * 40), r: 260 + k * 70, o: 0.16 + k * 0.03};
  });
  return (
    <div style={{position: 'absolute', inset: 0, background: `linear-gradient(170deg, ${couleur} 0%, ${couleur} 55%, rgba(0,0,0,0.22) 100%), ${couleur}`, overflow: 'hidden'}}>
      {formes.map((fo, i) => (
        <div key={i} style={{position: 'absolute', left: fo.x - fo.r, top: fo.y - fo.r, width: fo.r * 2, height: fo.r * 2, borderRadius: '50%', background: i % 2 ? '#ffffff' : '#000000', opacity: fo.o * (i % 2 ? 1 : 0.5), filter: 'blur(60px)'}} />
      ))}
      <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 420, background: 'linear-gradient(0deg, rgba(0,0,0,0.25), transparent)'}} />
    </div>
  );
};
