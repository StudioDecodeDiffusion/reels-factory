import React from 'react';
import {spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {ACCESSOIRES, LOU, TENUES, VISAGES_LOU} from './personnages';
import {MASCOTTE_CORPS, VISAGES} from './sprites';
import {Calque, fontTitre, INK, PixelSprite} from './fx';
import {Scene} from './types';
import {SAFE_BOTTOM, H} from './ui';

export type Qui = 'narrateur' | 'mascotte';
export type Replique = {qui: Qui; texte: string; expression?: string; debut?: number; fin?: number};

// Corps de Déco avec le bas recoloré selon la tenue (lettre C)
const DECO = MASCOTTE_CORPS.map((r, y) => (y >= 17 ? r.replace(/v/g, 'C') : r));
const PX = 11;
export const SOL = H - SAFE_BOTTOM - 190; // ligne de pieds des personnages (au-dessus des bulles)

// Répliques d'une scène, avec horaires (réels si sonorisés, sinon estimés)
export const repliques = (s: Scene): Replique[] => {
  const brut: Replique[] = s.dialogue && s.dialogue.length ? (s.dialogue as Replique[]) : s.voix ? [{qui: 'narrateur', texte: s.voix}] : [];
  let t = 0.15;
  return brut.map((r) => {
    if (r.debut !== undefined && r.fin !== undefined) return r;
    const d = r.texte.split(/\s+/).length / 2.5;
    const out = {...r, debut: t, fin: t + d};
    t += d + 0.3;
    return out;
  });
};

// ───────────────────────── Personnage (Lou ou Déco) avec tenue, accessoires et visage
export const Personnage: React.FC<{
  qui: Qui;
  expression: string;
  parle: boolean;
  tenue?: string;
  x: number;
  entree?: number;
}> = ({qui, expression, parle, tenue = 'classique', x, entree = 0}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const f = frame - entree;
  const pop = spring({frame: f, fps, config: {damping: 10, mass: 0.7}});
  const t = TENUES[tenue] ?? TENUES.classique;
  const lou = qui === 'narrateur';
  const corps = lou ? LOU : DECO;
  const bouche = parle && Math.floor(f / 4) % 2 === 0;
  const clignement = f % 95 > 89 && !['choc', 'rire', 'content', 'clin'].includes(expression);
  let visage = parle ? (bouche ? 'parle' : expression === 'neutre' ? 'neutre' : expression) : expression;
  if (clignement) visage = 'clin';
  const visages = lou ? VISAGES_LOU : VISAGES;
  const v = visages[visage] ?? visages.neutre;
  const calques: Calque[] = [{sprite: v, x: lou ? 3 : 5, y: lou ? 7 : 8}];
  for (const slot of ['cou', 'visage', 'tete'] as const) {
    const nom = t[slot];
    const a = nom ? ACCESSOIRES[nom] : undefined;
    if (a) calques.push({sprite: a.sprite, x: (lou ? a.lou : a.deco)[0], y: (lou ? a.lou : a.deco)[1]});
  }
  const couleurs = {C: t.haut, D: t.bas, E: t.detail, h: t.cheveux ?? '#5A3420'};
  // gestes : rebond quand il parle, sursaut quand choqué, penche quand il pense
  const saut = parle ? -Math.abs(Math.round(Math.sin(f / 5) * 2)) * PX : 0;
  const sursaut = expression === 'choc' ? Math.round(Math.sin(f / 2) * 1) * PX : 0;
  const penche = expression === 'pense' ? (lou ? -6 : 6) : 0;
  const respire = Math.round(Math.sin(f / 9)) * PX * 0.5;
  const marge = 6;
  const hauteur = (corps.length + marge * 2) * PX;
  return (
    <div
      style={{
        position: 'absolute',
        left: x - marge * PX,
        top: SOL - hauteur + marge * PX + saut + sursaut + respire + (1 - pop) * 400,
        transform: `rotate(${penche}deg)`,
        transformOrigin: 'bottom center',
        filter: `drop-shadow(8px 8px 0 rgba(20,19,28,0.35))`,
      }}
    >
      <PixelSprite sprite={corps} px={PX} calques={calques} couleurs={couleurs} marge={marge} />
    </div>
  );
};

// ───────────────────────── Bulle de dialogue avec mot prononcé surligné
export const Bulle: React.FC<{r: Replique; t: number}> = ({r, t}) => {
  const frame = useCurrentFrame();
  const debut = r.debut ?? 0;
  const fin = r.fin ?? debut + 2;
  const p = spring({frame: frame - Math.round(debut * 30), fps: 30, config: {damping: 11, mass: 0.5}});
  const mots = r.texte.split(/\s+/).filter(Boolean);
  const poids = mots.map((m) => 1.2 + m.length * 0.35 + (/[.,!?…:;]$/.test(m) ? 2.2 : 0));
  const total = poids.reduce((a, b) => a + b, 0);
  const prog = Math.min(1, Math.max(0, (t - debut) / Math.max(0.3, fin - debut))) * total;
  let acc = 0;
  let courant = mots.length - 1;
  for (let i = 0; i < mots.length; i++) {
    acc += poids[i];
    if (prog < acc) {
      courant = i;
      break;
    }
  }
  const gauche = r.qui === 'narrateur';
  const couleur = gauche ? '#FFFFFF' : '#FFF3B0';
  // longues répliques : on affiche par morceaux de ~9 mots
  const parBloc = 9;
  const bloc = Math.floor(courant / parBloc);
  const visibles = mots.slice(bloc * parBloc, bloc * parBloc + parBloc);
  return (
    <div style={{position: 'absolute', left: 50, width: 900, top: SOL + 30, transform: `scale(${p})`, transformOrigin: gauche ? '140px 0' : '760px 0'}}>
      {/* queue de la bulle, vers le personnage qui parle */}
      <div style={{position: 'absolute', top: -34, left: gauche ? 130 : 740, width: 0, height: 0, borderLeft: '26px solid transparent', borderRight: '26px solid transparent', borderBottom: `40px solid ${INK}`}} />
      <div style={{position: 'absolute', top: -22, left: gauche ? 140 : 750, width: 0, height: 0, borderLeft: '16px solid transparent', borderRight: '16px solid transparent', borderBottom: `28px solid ${couleur}`}} />
      <div style={{backgroundColor: couleur, border: `7px solid ${INK}`, borderRadius: 28, boxShadow: `10px 10px 0 ${INK}`, padding: '18px 26px', display: 'flex', flexWrap: 'wrap', gap: '4px 12px', minHeight: 70}}>
        {visibles.map((m, i) => {
          const idx = bloc * parBloc + i;
          const actif = idx === courant;
          return (
            <span key={idx} style={{fontFamily: fontTitre, fontWeight: 800, fontSize: 46, lineHeight: 1.15, color: INK, opacity: idx <= courant ? 1 : 0.35, backgroundColor: actif ? '#FFD23F' : 'transparent', borderRadius: 8, padding: '0 6px'}}>
              {m}
            </span>
          );
        })}
      </div>
    </div>
  );
};

// ───────────────────────── Le duo : Lou à gauche, Déco à droite, une bulle pour la réplique en cours
export const Duo: React.FC<{scene: Scene; tenues: {narrateur?: string; mascotte?: string}}> = ({scene, tenues}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const rs = repliques(scene);
  // la bulle reste affichée jusqu'à la réplique suivante
  const actif = [...rs].reverse().find((r) => t >= (r.debut ?? 0) - 0.05);
  // la dernière réplique de chacun donne son expression (l'autre « écoute » avec sa dernière humeur)
  const derniere = (qui: Qui) => [...rs].reverse().find((r) => r.qui === qui && (r.debut ?? 0) <= t);
  const expr = (qui: Qui) => derniere(qui)?.expression ?? (qui === 'mascotte' ? 'content' : 'neutre');
  const parle = (qui: Qui) => !!actif && actif.qui === qui && t <= (actif.fin ?? 0);
  return (
    <>
      <Personnage qui="narrateur" expression={expr('narrateur')} parle={parle('narrateur')} tenue={scene.tenue_narrateur ?? tenues.narrateur} x={50} entree={2} />
      <Personnage qui="mascotte" expression={expr('mascotte')} parle={parle('mascotte')} tenue={scene.tenue_mascotte ?? tenues.mascotte} x={700} entree={6} />
      {actif ? <Bulle r={actif} t={t} /> : null}
    </>
  );
};
