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
import {encrePour, FondPixel, fontPixel, INK, palette, TransitionPixel} from './fx';
import {Duo} from './dialogue';
import {HabillageChat, HabillageJT, HabillagePleinEcran, Transition} from './layouts';
import {CadreEditorial, SceneEditoriale} from './editorial';
import {FondCartoon, StylePerso} from './cartoon';


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
  const pal = palette(theme);
  const [c1, c2] = accents(pal, bg, i);
  const droite = i % 2 === 0;
  const cam = theme.camera ?? 'zoom';
  const zoom = interpolate(frame, [0, dur], cam === 'respire' ? [1.04, 1] : [1, 1.035]);
  const pan = cam === 'pan' ? interpolate(frame, [0, dur], [i % 2 ? -30 : 30, i % 2 ? 30 : -30]) : 0;
  const choc = cam === 'secousse' && frame < 10 ? Math.sin(frame * 2.5) * (10 - frame) * 2 : 0;
  const mep = theme.mise_en_page ?? 'duo';
  const plein = mep !== 'duo';
  const contenu = (
    <AbsoluteFill>
      {theme.persos === 'cartoon' ? <FondCartoon couleur={bg} seed={i + 1} /> : <FondPixel couleur={bg} seed={i + 1} />}
      <AbsoluteFill style={{transform: `translate(${pan + choc}px, ${choc / 2}px) scale(${(plein ? 1 : 0.9) * zoom})`, transformOrigin: '50% 12%'}}>
        <SceneViewPixel scene={s} ctx={{theme, bg, c1, c2, index: i, mascotteDroite: droite}} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
  const tenues = theme.tenues ?? {};
  const tr = theme.transition ?? 'pixels';
  return (
    <AbsoluteFill>
      {mep === 'jt' ? (
        <HabillageJT scene={s} tenues={tenues} accent={theme.accent2 ?? c1} titre={theme.titre ?? theme.bandeau ?? ''}>{contenu}</HabillageJT>
      ) : mep === 'chat' ? (
        <HabillageChat scene={s} accent={theme.accent} fond={bg}>{contenu}</HabillageChat>
      ) : mep === 'plein_ecran' || mep === 'quiz' ? (
        <HabillagePleinEcran scene={s} tenues={tenues} accent={c1}>{contenu}</HabillagePleinEcran>
      ) : (
        <>
          {contenu}
          <Duo scene={s} tenues={tenues} />
        </>
      )}
      {prevBg ? (tr === 'pixels' ? <TransitionPixel couleur={prevBg} seed={i} /> : <Transition type={tr} couleur={prevBg} seed={i} />) : null}
    </AbsoluteFill>
  );
};

export const ReelVideo: React.FC<VideoSpec> = ({theme, scenes, music}) => {
  const {fps, durationInFrames} = useVideoConfig();
  const hasVoice = scenes.some((s) => s.audio);
  const musicLevel = hasVoice ? 0.12 : 0.6; // musique discrète sous la voix off
  const pixel = theme.style !== 'sobre' && theme.style !== 'editorial';
  const pal = palette(theme);
  const bgs = scenes.map((s, i) => s.fond ?? pal[i % pal.length]);
  let from = 0;
  return (
    <StylePerso.Provider value={theme.persos === 'cartoon' ? 'cartoon' : 'pixel'}>
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
            {theme.style === 'editorial' ? (
              <AbsoluteFill>
                <CadreEditorial scene={s} theme={theme} index={i} total={scenes.length}>
                  <SceneEditoriale scene={s} theme={theme} />
                </CadreEditorial>
                {i > 0 ? <Transition type={theme.transition ?? 'volet'} couleur={theme.accent} seed={i} duree={10} /> : null}
              </AbsoluteFill>
            ) : pixel ? (
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
      {theme.style === 'editorial' ? null : pixel ? (['jt', 'chat'].includes(theme.mise_en_page ?? '') ? null : <BandeauPixel theme={theme} />) : <Bandeau theme={theme} />}
    </AbsoluteFill>
    </StylePerso.Provider>
  );
};

export {encrePour};
