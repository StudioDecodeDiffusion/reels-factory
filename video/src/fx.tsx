import React, {useMemo} from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import {MASCOTTE_CORPS, PIX, Sprite, SPRITES, VISAGES} from './sprites';
import {Theme} from './types';
import {H, rng, W, SAFE_BOTTOM} from './ui';

export const INK = '#14131C';
export const fontTitre = "'Rubik', 'Space Grotesk', sans-serif";
export const fontPixel = "'Silkscreen', 'Rubik', monospace";

// Palette vive dérivée du thème (le thème peut fournir sa propre palette)
export const palette = (t: Theme): string[] =>
  t.palette && t.palette.length >= 3 ? t.palette : [t.accent, t.accent2, '#FFD23F', '#2EC4B6', '#FF4F81', '#8E5CFF'];

// Couleur de texte lisible sur un fond donné
export const encrePour = (hex: string): string => {
  const h = hex.replace('#', '');
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16) / 255);
  const lum = 0.2126 * r + 0.7152 * g + 0.0722 * b;
  return lum > 0.55 ? INK : '#FFFFFF';
};

// ───────────────────────── Sprite pixel art
export type Calque = {sprite: Sprite; x: number; y: number};

export const PixelSprite: React.FC<{
  sprite: Sprite;
  px: number;
  style?: React.CSSProperties;
  overlay?: Calque;
  calques?: Calque[]; // accessoires, visages… dessinés par-dessus
  couleurs?: Record<string, string>; // recoloration (tenues)
  marge?: number; // pixels de marge autour (pour les accessoires qui dépassent)
}> = ({sprite, px, style, overlay, calques = [], couleurs = {}, marge = 0}) => {
  const w = Math.max(...sprite.map((r) => r.length)) + marge * 2;
  const h = sprite.length + marge * 2;
  const tous = overlay ? [overlay, ...calques] : calques;
  const rects = useMemo(() => {
    const out: React.ReactNode[] = [];
    const draw = (s: Sprite, ox: number, oy: number, key: string) =>
      s.forEach((row, y) =>
        [...row].forEach((ch, x) => {
          const col = couleurs[ch] ?? PIX[ch];
          if (ch !== '.' && col) out.push(<rect key={`${key}${x}-${y}`} x={x + ox + marge} y={y + oy + marge} width={1.02} height={1.02} fill={col} />);
        }),
      );
    draw(sprite, 0, 0, 's');
    tous.forEach((c, i) => draw(c.sprite, c.x, c.y, `c${i}-`));
    return out;
  }, [sprite, JSON.stringify(tous), JSON.stringify(couleurs), marge]);
  return (
    <svg width={w * px} height={h * px} viewBox={`0 0 ${w} ${h}`} shapeRendering="crispEdges" style={style}>
      {rects}
    </svg>
  );
};

export type SpriteAnim = 'bounce' | 'float' | 'shake' | 'spin' | 'grow' | 'rain' | 'orbit';

// Sprite animé (entrée « pop » + mouvement continu), en pixels « durs » (pas de flou)
export const AnimatedSprite: React.FC<{
  name: string;
  anim?: SpriteAnim;
  px?: number;
  x: number;
  y: number;
  delay?: number;
  rotate?: number;
}> = ({name, anim = 'bounce', px = 14, x, y, delay = 0, rotate = 0}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const sprite = SPRITES[name];
  if (!sprite) return null;
  const f = frame - delay;
  const pop = spring({frame: f, fps, config: {damping: 9, mass: 0.6}});
  const step = (v: number) => Math.round(v / 4) * 4; // mouvement par paliers = effet pixel
  let dx = 0;
  let dy = 0;
  let rot = rotate;
  let sc = pop;
  if (anim === 'bounce') dy = step(-Math.abs(Math.sin(f / 7)) * 40);
  if (anim === 'float') dy = step(Math.sin(f / 14) * 18);
  if (anim === 'shake') dx = f % 6 < 3 ? -6 : 6;
  if (anim === 'spin') rot += Math.floor(f / 6) * 15;
  if (anim === 'grow') sc = pop * (1 + 0.08 * Math.round(Math.sin(f / 5)));
  if (anim === 'orbit') {
    dx = step(Math.cos(f / 12) * 40);
    dy = step(Math.sin(f / 12) * 25);
  }
  if (anim === 'rain') {
    // pluie de sprites qui tombent
    const R = rng(name.length * 31 + Math.round(x));
    return (
      <>
        {Array.from({length: 9}).map((_, i) => {
          const sx = R() * (W - 160);
          const speed = 9 + R() * 8;
          const start = R() * 60;
          const yy = ((f * speed + start * 40) % 1200) - 200; // s'arrête au-dessus des personnages
          return (
            <div key={i} style={{position: 'absolute', left: sx, top: step(yy), transform: `rotate(${Math.floor((f + i * 10) / 8) * 20}deg)`, opacity: Math.min(0.55, f / 8) * (yy > 850 ? Math.max(0, (1000 - yy) / 150) : 1)}}>
              <PixelSprite sprite={sprite} px={7 + (i % 3) * 2} />
            </div>
          );
        })}
      </>
    );
  }
  return (
    <div style={{position: 'absolute', left: x + dx, top: y + dy, transform: `scale(${sc}) rotate(${rot}deg)`, transformOrigin: 'center bottom', filter: `drop-shadow(${px / 2}px ${px / 2}px 0 rgba(20,19,28,0.35))`}}>
      <PixelSprite sprite={sprite} px={px} />
    </div>
  );
};

// ───────────────────────── Mascotte « Déco »
export type Expression = 'neutre' | 'parle' | 'content' | 'choc' | 'pense' | 'clin';

export const Mascotte: React.FC<{
  expression?: Expression;
  parle?: boolean; // la bouche bouge (pendant la voix off)
  dureeParole?: number; // en images
  x: number;
  y: number;
  px?: number;
  miroir?: boolean;
  entree?: number;
}> = ({expression = 'neutre', parle = false, dureeParole = 0, x, y, px = 12, miroir = false, entree = 0}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const f = frame - entree;
  const pop = spring({frame: f, fps, config: {damping: 10, mass: 0.7}});
  const bob = Math.round(Math.sin(f / 8) * 2) * px; // respiration en paliers pixel
  const enTrainDeParler = parle && f < dureeParole && Math.floor(f / 4) % 2 === 0;
  const clignement = f % 90 > 84; // clin d'œil naturel toutes les 3 s
  let visage: Expression = expression;
  if (enTrainDeParler) visage = 'parle';
  if (clignement && (visage === 'neutre' || visage === 'parle')) visage = 'clin';
  return (
    <div style={{position: 'absolute', left: x, top: y + bob + (1 - pop) * 300, transform: `scaleX(${miroir ? -1 : 1})`, opacity: Math.min(1, pop * 1.5)}}>
      <PixelSprite sprite={MASCOTTE_CORPS} px={px} overlay={{sprite: VISAGES[visage], x: 5, y: 8}} />
    </div>
  );
};

// ───────────────────────── Fond animé : couleur vive + motif pixel qui défile + confettis carrés
export const FondPixel: React.FC<{couleur: string; seed: number}> = ({couleur, seed}) => {
  const frame = useCurrentFrame();
  const encre = encrePour(couleur);
  const R = rng(seed * 97 + 13);
  const deco = Array.from({length: 18}).map(() => ({x: R() * W, y: R() * H, s: 10 + Math.floor(R() * 4) * 8, v: 0.4 + R() * 1.2}));
  const off = Math.round((frame * 1.5) / 8) * 8;
  return (
    <AbsoluteFill style={{backgroundColor: couleur, overflow: 'hidden'}}>
      <AbsoluteFill
        style={{
          opacity: encre === INK ? 0.08 : 0.1,
          backgroundImage: `linear-gradient(45deg, ${encre} 25%, transparent 25%, transparent 75%, ${encre} 75%), linear-gradient(45deg, ${encre} 25%, transparent 25%, transparent 75%, ${encre} 75%)`,
          backgroundSize: '64px 64px',
          backgroundPosition: `${off}px ${off}px, ${off + 32}px ${off + 32}px`,
        }}
      />
      {deco.map((d, i) => (
        <div key={i} style={{position: 'absolute', left: d.x, top: (d.y - Math.round((frame * d.v) / 4) * 4 + H) % H, width: d.s, height: d.s, backgroundColor: encre, opacity: 0.12}} />
      ))}
    </AbsoluteFill>
  );
};

// ───────────────────────── Transition : dissolution en gros pixels
export const TransitionPixel: React.FC<{couleur: string; seed: number; duree?: number}> = ({couleur, seed, duree = 12}) => {
  const frame = useCurrentFrame();
  if (frame > duree) return null;
  const cols = 9;
  const rows = 16;
  const cw = W / cols;
  const ch = H / rows;
  const R = rng(seed * 7 + 3);
  const cells = Array.from({length: cols * rows}).map(() => R());
  const p = frame / duree;
  return (
    <AbsoluteFill>
      {cells.map((t, i) =>
        t > p ? <div key={i} style={{position: 'absolute', left: (i % cols) * cw, top: Math.floor(i / cols) * ch, width: cw + 1, height: ch + 1, backgroundColor: couleur}} /> : null,
      )}
    </AbsoluteFill>
  );
};

// ───────────────────────── Autocollant : carte penchée, bord épais, ombre décalée
export const Sticker: React.FC<{
  couleur: string;
  rotate?: number;
  delay?: number;
  style?: React.CSSProperties;
  children: React.ReactNode;
}> = ({couleur, rotate = -3, delay = 0, style, children}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = spring({frame: frame - delay, fps, config: {damping: 8, mass: 0.6}});
  return (
    <div
      style={{
        backgroundColor: couleur,
        color: encrePour(couleur),
        border: `7px solid ${INK}`,
        boxShadow: `14px 14px 0 ${INK}`,
        borderRadius: 18,
        padding: '22px 34px',
        transform: `rotate(${rotate * p}deg) scale(${0.4 + 0.6 * p})`,
        opacity: Math.min(1, p * 2),
        ...style,
      }}
    >
      {children}
    </div>
  );
};

// ───────────────────────── Sous-titres mot à mot (karaoké) calés sur la voix off
export const SousTitres: React.FC<{texte?: string; duree: number; fond: string}> = ({texte, duree, fond}) => {
  const accent = fond.toLowerCase() === '#ffd23f' ? '#FF4F81' : '#FFD23F';
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (!texte) return null;
  const mots = texte.split(/\s+/).filter(Boolean);
  // durée de chaque mot proportionnelle à sa longueur (approximation de la parole)
  const poids = mots.map((m) => 1.2 + m.length * 0.35 + (/[.,!?…:;]$/.test(m) ? 2.2 : 0));
  const total = poids.reduce((a, b) => a + b, 0);
  const t = (frame / fps / Math.max(0.5, duree)) * total;
  let acc = 0;
  let courant = mots.length - 1;
  for (let i = 0; i < mots.length; i++) {
    acc += poids[i];
    if (t < acc) {
      courant = i;
      break;
    }
  }
  if (frame / fps > duree + 0.4) return null;
  const parGroupe = 4;
  const debut = Math.floor(courant / parGroupe) * parGroupe;
  const groupe = mots.slice(debut, debut + parGroupe);
  return (
    <div style={{position: 'absolute', left: 60, right: 60, bottom: SAFE_BOTTOM - 10, display: 'flex', justifyContent: 'center', flexWrap: 'wrap', gap: '6px 16px'}}>
      {groupe.map((m, i) => {
        const idx = debut + i;
        const actif = idx === courant;
        return (
          <span
            key={idx}
            style={{
              fontFamily: fontTitre,
              fontWeight: 900,
              fontSize: 62,
              color: actif ? INK : '#FFFFFF',
              backgroundColor: actif ? accent : 'transparent',
              padding: '0 10px',
              borderRadius: 8,
              WebkitTextStroke: actif ? '0px' : `3px ${INK}`,
              paintOrder: 'stroke fill',
              textShadow: actif ? 'none' : `5px 5px 0 ${INK}`,
              transform: actif ? 'scale(1.08) rotate(-2deg)' : 'none',
              opacity: idx <= courant ? 1 : 0.85,
            }}
          >
            {m}
          </span>
        );
      })}
    </div>
  );
};

// ───────────────────────── Étincelles pixel (accentuer un chiffre)
export const Etincelles: React.FC<{x: number; y: number; couleur: string; delay?: number}> = ({x, y, couleur, delay = 0}) => {
  const frame = useCurrentFrame() - delay;
  if (frame < 0 || frame > 24) return null;
  const p = interpolate(frame, [0, 24], [0, 1], {easing: Easing.out(Easing.cubic)});
  return (
    <>
      {Array.from({length: 12}).map((_, i) => {
        const a = (i / 12) * Math.PI * 2;
        const d = 40 + p * 190;
        const s = Math.round((1 - p) * 4) * 6 + 6;
        return <div key={i} style={{position: 'absolute', left: x + Math.cos(a) * d, top: y + Math.sin(a) * d, width: s, height: s, backgroundColor: i % 2 ? couleur : INK}} />;
      })}
    </>
  );
};
