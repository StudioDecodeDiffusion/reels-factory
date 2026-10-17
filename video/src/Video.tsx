import React from 'react';
import {AbsoluteFill, Audio, interpolate, Sequence, staticFile, useVideoConfig} from 'remotion';
import '@fontsource/inter/500.css';
import '@fontsource/inter/700.css';
import '@fontsource/space-grotesk/700.css';
import '@fontsource/jetbrains-mono/500.css';
import {VideoSpec} from './types';
import {Background, Bandeau, FadeOut} from './ui';
import {SceneView} from './scenes';

export const ReelVideo: React.FC<VideoSpec> = ({theme, scenes, music}) => {
  const {fps, durationInFrames} = useVideoConfig();
  const hasVoice = scenes.some((s) => s.audio);
  const musicLevel = hasVoice ? 0.12 : 0.6; // musique discrète sous la voix off
  let from = 0;
  return (
    <AbsoluteFill>
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
      <Background theme={theme} />
      {scenes.map((s, i) => {
        const dur = Math.max(1, Math.round(s.duration * fps));
        const seq = (
          <Sequence key={i} from={from} durationInFrames={dur}>
            {s.audio ? <Audio src={staticFile(s.audio)} /> : null}
            <FadeOut durationInFrames={i === scenes.length - 1 ? dur + 100 : dur}>
              <SceneView scene={s} theme={theme} />
            </FadeOut>
          </Sequence>
        );
        from += dur;
        return seq;
      })}
      <Bandeau theme={theme} />
    </AbsoluteFill>
  );
};
