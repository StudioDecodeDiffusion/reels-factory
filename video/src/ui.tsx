import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {Theme} from './types';

// Zone sûre Instagram : l'interface du Reel couvre le haut (~220px) et le bas (~380px).
export const SAFE_TOP = 240;
export const SAFE_BOTTOM = 400;
export const W = 1080;
export const H = 1920;

export const fontStack = (name: string) => {
  const map: Record<string, string> = {
    'Space Grotesk': "'Space Grotesk', 'Inter', sans-serif",
    Inter: "'Inter', sans-serif",
    'JetBrains Mono': "'JetBrains Mono', monospace",
  };
  return map[name] ?? "'Inter', sans-serif";
};

// Générateur pseudo-aléatoire déterministe : même vidéo à chaque rendu.
export const rng = (seed: number) => () => {
  seed = (seed * 16807) % 2147483647;
  return (seed - 1) / 2147483646;
};

export const usePop = (delay = 0, damping = 14) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return spring({frame: frame - delay, fps, config: {damping, mass: 0.7}});
};

export const FadeOut: React.FC<{durationInFrames: number; children: React.ReactNode}> = ({
  durationInFrames,
  children,
}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [durationInFrames - 8, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

export const SafeArea: React.FC<{children: React.ReactNode; justify?: string}> = ({
  children,
  justify = 'center',
}) => (
  <AbsoluteFill
    style={{
      paddingTop: SAFE_TOP,
      paddingBottom: SAFE_BOTTOM,
      paddingLeft: 80,
      paddingRight: 80,
      justifyContent: justify,
      alignItems: 'center',
      display: 'flex',
      flexDirection: 'column',
    }}
  >
    {children}
  </AbsoluteFill>
);

export const Background: React.FC<{theme: Theme}> = ({theme}) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{backgroundColor: theme.fond}}>
      {theme.grille ? (
        <svg width={W} height={H} style={{position: 'absolute', opacity: 0.12}}>
          {Array.from({length: 28}).map((_, i) => (
            <line key={'v' + i} x1={i * 40 + ((frame * 0.3) % 40)} y1={0} x2={i * 40 + ((frame * 0.3) % 40)} y2={H} stroke={theme.texte} strokeWidth={1} />
          ))}
          {Array.from({length: 50}).map((_, i) => (
            <line key={'h' + i} x1={0} y1={i * 40} x2={W} y2={i * 40} stroke={theme.texte} strokeWidth={1} />
          ))}
        </svg>
      ) : null}
    </AbsoluteFill>
  );
};

export const Bandeau: React.FC<{theme: Theme}> = ({theme}) => {
  const p = usePop(0, 20);
  if (!theme.bandeau) return null;
  return (
    <div
      style={{
        position: 'absolute',
        top: SAFE_TOP - 20,
        left: 80,
        transform: `translateX(${(1 - p) * -600}px)`,
        backgroundColor: theme.accent,
        color: theme.fond,
        fontFamily: fontStack(theme.police_titre),
        fontWeight: 700,
        fontSize: 34,
        letterSpacing: 2,
        padding: '10px 22px',
        textTransform: 'uppercase',
      }}
    >
      {theme.bandeau}
    </div>
  );
};

// Met en couleur un mot dans une phrase.
export const Highlight: React.FC<{text: string; word?: string; color: string}> = ({text, word, color}) => {
  if (!word || !text.toLowerCase().includes(word.toLowerCase())) return <>{text}</>;
  const i = text.toLowerCase().indexOf(word.toLowerCase());
  return (
    <>
      {text.slice(0, i)}
      <span style={{color}}>{text.slice(i, i + word.length)}</span>
      {text.slice(i + word.length)}
    </>
  );
};
