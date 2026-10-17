import React from 'react';
import {AbsoluteFill} from 'remotion';
import '@fontsource/rubik/900.css';
import '@fontsource/silkscreen/400.css';
import {LOU, VISAGES_LOU, TENUES, ACCESSOIRES} from './personnages';
import {MASCOTTE_CORPS, VISAGES} from './sprites';
import {Calque, fontPixel, fontTitre, INK, PixelSprite} from './fx';

// Image carrée 1080×1080 pour les photos de profil (Instagram la recadre en rond : tout est centré)
export type AvatarProps = {
  fond: string;
  motif?: string;
  perso: 'deco' | 'lou' | 'duo';
  tenueDeco?: string;
  tenueLou?: string;
  exprDeco?: string;
  exprLou?: string;
  etiquette?: string;
  couleurEtiquette?: string;
};

const DECO = MASCOTTE_CORPS.map((r, y) => (y >= 17 ? r.replace(/v/g, 'C') : r));

const Perso: React.FC<{qui: 'deco' | 'lou'; tenue: string; expr: string; px: number}> = ({qui, tenue, expr, px}) => {
  const t = TENUES[tenue] ?? TENUES.classique;
  const lou = qui === 'lou';
  const calques: Calque[] = [{sprite: (lou ? VISAGES_LOU : VISAGES)[expr] ?? (lou ? VISAGES_LOU : VISAGES).content, x: lou ? 3 : 5, y: lou ? 7 : 8}];
  for (const slot of ['cou', 'visage', 'tete'] as const) {
    const a = t[slot] ? ACCESSOIRES[t[slot] as string] : undefined;
    if (a) calques.push({sprite: a.sprite, x: (lou ? a.lou : a.deco)[0], y: (lou ? a.lou : a.deco)[1]});
  }
  return (
    <PixelSprite
      sprite={lou ? LOU : DECO}
      px={px}
      calques={calques}
      marge={6}
      couleurs={{C: t.haut, D: t.bas, E: t.detail, h: t.cheveux ?? '#5A3420'}}
      style={{filter: `drop-shadow(${px}px ${px}px 0 rgba(20,19,28,0.35))`}}
    />
  );
};

export const Avatar: React.FC<AvatarProps> = ({fond, motif = INK, perso, tenueDeco = 'classique', tenueLou = 'economie', exprDeco = 'content', exprLou = 'content', etiquette, couleurEtiquette = '#FFD23F'}) => (
  <AbsoluteFill style={{backgroundColor: fond, alignItems: 'center', justifyContent: 'center'}}>
    <AbsoluteFill
      style={{
        opacity: 0.1,
        backgroundImage: `linear-gradient(45deg, ${motif} 25%, transparent 25%, transparent 75%, ${motif} 75%), linear-gradient(45deg, ${motif} 25%, transparent 25%, transparent 75%, ${motif} 75%)`,
        backgroundSize: '72px 72px',
        backgroundPosition: '0 0, 36px 36px',
      }}
    />
    <div style={{display: 'flex', alignItems: 'flex-end', gap: 10, marginTop: etiquette ? (etiquette.includes('\n') ? -150 : -40) : 0}}>
      {perso !== 'deco' ? <Perso qui="lou" tenue={tenueLou} expr={exprLou} px={perso === 'duo' ? 17 : 24} /> : null}
      {perso !== 'lou' ? <Perso qui="deco" tenue={tenueDeco} expr={exprDeco} px={perso === 'duo' ? 17 : 27} /> : null}
    </div>
    {etiquette ? (
      <div style={{position: 'absolute', bottom: etiquette.includes('\n') ? 130 : 150, backgroundColor: couleurEtiquette, border: `10px solid ${INK}`, boxShadow: `14px 14px 0 ${INK}`, padding: '8px 40px', transform: 'rotate(-4deg)', fontFamily: etiquette.length > 8 ? fontTitre : fontPixel, fontWeight: 900, fontSize: etiquette.length > 8 ? 70 : 96, color: INK, textAlign: 'center', lineHeight: 1.05, whiteSpace: 'pre-line'}}>
        {etiquette}
      </div>
    ) : null}
  </AbsoluteFill>
);
