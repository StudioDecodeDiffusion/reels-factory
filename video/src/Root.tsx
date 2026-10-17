import React from 'react';
import {Composition} from 'remotion';
import {ReelVideo} from './Video';
import {VideoSpec} from './types';
import sample from '../sample-spec.json';
import {Avatar} from './Avatar';

export const Root: React.FC = () => (
  <>
  <Composition
    id="Avatar"
    component={Avatar as unknown as React.FC<Record<string, unknown>>}
    width={1080}
    height={1080}
    fps={30}
    durationInFrames={1}
    defaultProps={{fond: '#FFD23F', perso: 'deco'}}
  />
  <Composition
    id="Reel"
    component={ReelVideo as unknown as React.FC<Record<string, unknown>>}
    width={1080}
    height={1920}
    fps={30}
    durationInFrames={300}
    defaultProps={sample as unknown as Record<string, unknown>}
    calculateMetadata={({props}) => {
      const spec = props as unknown as VideoSpec;
      const fps = spec.fps ?? 30;
      const total = spec.scenes.reduce((a, s) => a + Math.max(1, Math.round(s.duration * fps)), 0);
      return {durationInFrames: total, fps};
    }}
  />
</>
);
