import React from 'react';
import {AbsoluteFill, Audio, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import '@fontsource/inter/500.css';
import '@fontsource/inter/700.css';
import '@fontsource/space-grotesk/700.css';
import '@fontsource/jetbrains-mono/500.css';
import '@fontsource/rubik/700.css';
import '@fontsource/rubik/800.css';
import '@fontsource/rubik/900.css';
import '@fontsource/silkscreen/400.css';
import {Scene, Theme, VideoSpec} from './types';
import {Background, Bandeau, FadeOut, SAFE_TOP} from './ui';
import {SceneView} from './scenes';
import {SceneViewPixel} from './scenesPixel';
import {encrePour, Expression, FondPixel, fontPixel, INK, Mascotte, palette, SousTitres, TransitionPixel} from './fx';

const dureeVoix = (s: Scene) => s.voix_duree ?? (s.voix ? s.voix.split(/\s+/).length / 2.5 : 0);

const expressionPar: Record<string, Expression> = {hook: 'choc', counter: 'choc', compare: 'pense', outro: 'content', dots: 'pense'};

// Choisit deux couleurs d'accent de la palette, différentes du fond
const accents = (pal: string[], bg: string, i: number): [string, string] => {
  const autres = pal.filter((c) => c.toLowerCase() !== bg.toLowerCase());
  return [autres[i % autres.length], autres[(i + 2) % autres.length]];
};

const BandeauPixel: React.FC<{theme: Theme}> = ({theme}) => {
  const frame = useCurrentFrame();
  if (!theme.bandeau) return null;
  const blink = Math.floor(frame / 15) % 2 === 0;
  return (
    <div style={{position: 'absolute', top: SAFE_TOP - 30, left: 60, display: 'flex', alignItems: 'center', gap: 14, backgroundColor: INK, color: '#fff', fontFamily: fontPixel, fontSize: 34, padding: '10px 20px', border: '5px solid #fff', transform: 'rotate(-2deg)'}}>
      <span style={{width: 18, height: 18, backgroundColor: blink ? '#FF3B3B' : 'transparent', display: 'inline-block'}} />
      {theme.bandeau}
    </div>
  );
};

const ScenePixel: React.FC<{s: Scene; i: number; theme: Theme; bg: string; prevBg: string | null; dur: number}> = ({s, i, theme, bg, prevBg, dur}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const pal = palette(theme);
  const [c1, c2] = accents(pal, bg, i);
  const zoom = interpolate(frame, [0, dur], [1, 1.035]);
  const droite = i % 2 === 0;
  const parole = Math.round(dureeVoix(s) * fps);
  return (
    <AbsoluteFill>
      <FondPixel couleur={bg} seed={i + 1} />
      <AbsoluteFill style={{transform: `scale(${zoom})`}}>
        <SceneViewPixel scene={s} ctx={{theme, bg, c1, c2, index: i, mascotteDroite: droite}} />
      </AbsoluteFill>
      {s.mascotte !== 'aucune' ? (
        <Mascotte
          expression={(s.mascotte as Expression) ?? expressionPar[s.type] ?? 'neutre'}
          parle={parole > 0}
          dureeParole={parole}
          x={droite ? 800 : 40}
          y={1110}
          px={11}
          entree={4}
        />
      ) : null}
      <SousTitres texte={s.voix} duree={dureeVoix(s)} fond={bg} />
      {prevBg ? <TransitionPixel couleur={prevBg} seed={i} /> : null}
    </AbsoluteFill>
  );
};

export const ReelVideo: React.FC<VideoSpec> = ({theme, scenes, music}) => {
  const {fps, durationInFrames} = useVideoConfig();
  const hasVoice = scenes.some((s) => s.audio);
  const musicLevel = hasVoice ? 0.12 : 0.6; // musique discrète sous la voix off
  const pixel = theme.style !== 'sobre';
  const pal = palette(theme);
  const bgs = scenes.map((s, i) => s.fond ?? pal[i % pal.length]);
  let from = 0;
  return (
    <AbsoluteFill style={{backgroundColor: INK}}>
      {music ? (
        <Audio
          src={staticFile(`music/${music}`)}
          volume={(f) =>
            interpolate(f, [0, 15, durationInFrames - 30, durationInFrames], [0, musicLevel, musicLevel, 0], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            })
          }
        />
      ) : null}
      {pixel ? null : <Background theme={theme} />}
      {scenes.map((s, i) => {
        const dur = Math.max(1, Math.round(s.duration * fps));
        const seq = (
          <Sequence key={i} from={from} durationInFrames={dur}>
            {s.audio ? <Audio src={staticFile(s.audio)} /> : null}
            {pixel ? (
              <ScenePixel s={s} i={i} theme={theme} bg={bgs[i]} prevBg={i > 0 ? bgs[i - 1] : null} dur={dur} />
            ) : (
              <FadeOut durationInFrames={i === scenes.length - 1 ? dur + 100 : dur}>
                <SceneView scene={s} theme={theme} />
              </FadeOut>
            )}
          </Sequence>
        );
        from += dur;
        return seq;
      })}
      {pixel ? <BandeauPixel theme={theme} /> : <Bandeau theme={theme} />}
    </AbsoluteFill>
  );
};

export {encrePour};
