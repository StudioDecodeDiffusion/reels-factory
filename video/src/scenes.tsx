import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import {Scene, Theme} from './types';
import {fontStack, Highlight, rng, SafeArea, usePop, W, H, SAFE_TOP, SAFE_BOTTOM} from './ui';

type P<T extends Scene['type']> = {scene: Extract<Scene, {type: T}>; theme: Theme};

const title = (t: Theme, size: number): React.CSSProperties => ({
  fontFamily: fontStack(t.police_titre),
  fontWeight: 700,
  fontSize: size,
  lineHeight: 1.05,
  color: t.texte,
  textAlign: 'center',
  letterSpacing: -1,
});
const body = (t: Theme, size: number): React.CSSProperties => ({
  fontFamily: fontStack(t.police_texte),
  fontWeight: 500,
  fontSize: size,
  lineHeight: 1.3,
  color: t.texte,
  textAlign: 'center',
});

// ---------- HOOK : grosse question / affirmation choc ----------
export const Hook: React.FC<P<'hook'>> = ({scene, theme}) => {
  const words = scene.title.split(' ');
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const sub = usePop(Math.min(words.length * 3 + 6, 30));
  return (
    <SafeArea>
      <div style={{...title(theme, 104), display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '0 26px'}}>
        {words.map((w, i) => {
          const d = i * 3;
          const o = interpolate(frame - d, [0, 6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
          const y = interpolate(frame - d, [0, 8], [40, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
          const isQ = w.includes('?');
          return (
            <span key={i} style={{opacity: o, transform: `translateY(${y}px)`, color: isQ ? theme.accent : theme.texte}}>
              {w}
            </span>
          );
        })}
      </div>
      {scene.subtitle ? (
        <div style={{...body(theme, 46), marginTop: 48, opacity: sub, transform: `scale(${0.9 + 0.1 * sub})`, color: theme.accent2}}>
          {scene.subtitle}
        </div>
      ) : null}
      <div style={{position: 'absolute', bottom: SAFE_BOTTOM - 40, width: interpolate(frame, [0, fps * scene.duration], [0, 700], {extrapolateRight: 'clamp'}), height: 8, backgroundColor: theme.accent, borderRadius: 4}} />
    </SafeArea>
  );
};

// ---------- KINETIC : texte qui arrive ligne par ligne ----------
export const Kinetic: React.FC<P<'kinetic'>> = ({scene, theme}) => {
  const {fps} = useVideoConfig();
  const per = Math.max(10, Math.floor((scene.duration * fps * 0.7) / Math.max(1, scene.lines.length)));
  return (
    <SafeArea>
      {scene.lines.map((l, i) => {
        // eslint-disable-next-line react-hooks/rules-of-hooks
        const p = usePop(i * per);
        return (
          <div key={i} style={{...title(theme, l.length > 28 ? 68 : 84), margin: '18px 0', opacity: p, transform: `translateX(${(1 - p) * (i % 2 ? 300 : -300)}px)`}}>
            <Highlight text={l} word={scene.highlight} color={theme.accent} />
          </div>
        );
      })}
    </SafeArea>
  );
};

// ---------- COUNTER : chiffre qui défile ----------
const fmt = (n: number, d: number) =>
  n.toLocaleString('fr-FR', {minimumFractionDigits: d, maximumFractionDigits: d});

export const Counter: React.FC<P<'counter'>> = ({scene, theme}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const from = scene.from ?? 0;
  const v = interpolate(frame, [4, fps * Math.min(2.2, scene.duration * 0.6)], [from, scene.to], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.exp),
  });
  const lab = usePop(10);
  const big = `${scene.prefix ?? ''}${fmt(v, scene.decimals ?? 0)}${scene.suffix ?? ''}`;
  return (
    <SafeArea>
      <div style={{...title(theme, big.length > 12 ? 110 : big.length > 8 ? 140 : 190), color: theme.accent, fontVariantNumeric: 'tabular-nums', whiteSpace: 'nowrap'}}>{big}</div>
      <div style={{...body(theme, 52), marginTop: 40, opacity: lab, maxWidth: 880}}>{scene.label}</div>
    </SafeArea>
  );
};

// ---------- BARS : histogramme horizontal ----------
export const Bars: React.FC<P<'bars'>> = ({scene, theme}) => {
  const frame = useCurrentFrame();
  const max = Math.max(...scene.items.map((i) => i.value), 1);
  const head = usePop(0);
  return (
    <SafeArea>
      <div style={{...title(theme, 70), marginBottom: 60, opacity: head}}>{scene.title}</div>
      <div style={{width: 900}}>
        {scene.items.slice(0, 6).map((it, i) => {
          const p = interpolate(frame - 8 - i * 6, [0, 24], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
          const isMax = it.value === max;
          return (
            <div key={i} style={{marginBottom: 34}}>
              <div style={{...body(theme, 40), textAlign: 'left', marginBottom: 10, display: 'flex', justifyContent: 'space-between'}}>
                <span>{it.label}</span>
                <span style={{color: isMax ? theme.accent : theme.texte, fontWeight: 700}}>
                  {fmt(it.value * p, Number.isInteger(it.value) ? 0 : 1)}
                  {scene.unit ?? ''}
                </span>
              </div>
              <div style={{height: 40, width: `${(it.value / max) * 100 * p}%`, backgroundColor: isMax ? theme.accent : theme.accent2, borderRadius: 8}} />
            </div>
          );
        })}
      </div>
    </SafeArea>
  );
};

// ---------- TIMELINE ----------
export const Timeline: React.FC<P<'timeline'>> = ({scene, theme}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const n = Math.min(scene.events.length, 5);
  const per = Math.floor((scene.duration * fps * 0.75) / n);
  const lineH = interpolate(frame, [0, per * n], [0, 100], {extrapolateRight: 'clamp'});
  return (
    <SafeArea justify="center">
      {scene.title ? <div style={{...title(theme, 66), marginBottom: 50}}>{scene.title}</div> : null}
      <div style={{position: 'relative', width: 880, paddingLeft: 70}}>
        <div style={{position: 'absolute', left: 20, top: 0, width: 6, height: `${lineH}%`, backgroundColor: theme.accent2, borderRadius: 3}} />
        {scene.events.slice(0, n).map((e, i) => {
          // eslint-disable-next-line react-hooks/rules-of-hooks
          const p = usePop(i * per);
          return (
            <div key={i} style={{marginBottom: 46, opacity: p, transform: `translateY(${(1 - p) * 30}px)`, position: 'relative'}}>
              <div style={{position: 'absolute', left: -62, top: 10, width: 30, height: 30, borderRadius: 15, backgroundColor: theme.accent}} />
              <div style={{...title(theme, 50), textAlign: 'left', color: theme.accent}}>{e.date}</div>
              <div style={{...body(theme, 40), textAlign: 'left'}}>{e.text}</div>
            </div>
          );
        })}
      </div>
    </SafeArea>
  );
};

// ---------- DOTS : "X sur 100" ----------
export const Dots: React.FC<P<'dots'>> = ({scene, theme}) => {
  const frame = useCurrentFrame();
  const total = Math.min(Math.max(scene.total, 1), 100);
  const hi = Math.min(scene.highlighted, total);
  const cols = 10;
  const lab = usePop(Math.min(total + 10, 40));
  return (
    <SafeArea>
      <div style={{display: 'grid', gridTemplateColumns: `repeat(${cols}, 64px)`, gap: 18}}>
        {Array.from({length: total}).map((_, i) => {
          const appear = interpolate(frame - i * 0.4, [0, 6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
          const lit = i < hi && frame > 20 + i * 0.6;
          return (
            <div key={i} style={{width: 64, height: 64, borderRadius: 32, transform: `scale(${appear})`, backgroundColor: lit ? theme.accent : theme.texte, opacity: lit ? 1 : 0.18}} />
          );
        })}
      </div>
      <div style={{...body(theme, 50), marginTop: 60, opacity: lab, maxWidth: 900}}>
        <Highlight text={scene.label} word={String(hi)} color={theme.accent} />
      </div>
    </SafeArea>
  );
};

// ---------- COMPARE : A vs B ----------
export const Compare: React.FC<P<'compare'>> = ({scene, theme}) => {
  const l = usePop(4);
  const r = usePop(14);
  const vs = usePop(24, 8);
  const card = (side: typeof scene.left, p: number, color: string, dir: number) => (
    <div style={{width: 420, padding: '50px 30px', borderRadius: 32, border: `5px solid ${color}`, opacity: p, transform: `translateX(${(1 - p) * dir * 300}px)`}}>
      <div style={{...body(theme, 40), opacity: 0.8}}>{side.label}</div>
      <div style={{...title(theme, side.value.length > 8 ? 64 : side.value.length > 5 ? 80 : 104), color, margin: '20px 0', whiteSpace: 'nowrap'}}>{side.value}</div>
      {side.caption ? <div style={{...body(theme, 34)}}>{side.caption}</div> : null}
    </div>
  );
  return (
    <SafeArea>
      {scene.title ? <div style={{...title(theme, 70), marginBottom: 60}}>{scene.title}</div> : null}
      <div style={{display: 'flex', gap: 40, alignItems: 'center', position: 'relative'}}>
        {card(scene.left, l, theme.accent2, -1)}
        {card(scene.right, r, theme.accent, 1)}
        <div style={{position: 'absolute', left: '50%', top: '50%', transform: `translate(-50%,-50%) scale(${vs})`, backgroundColor: theme.texte, color: theme.fond, ...title(theme, 44), padding: '14px 22px', borderRadius: 40}}>
          <span style={{color: theme.fond}}>VS</span>
        </div>
      </div>
    </SafeArea>
  );
};

// ---------- PARTICLES : simulations ----------
const Sim: React.FC<{mode: string; count: number; theme: Theme}> = ({mode, count, theme}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const R = rng(42);
  const cx = W / 2;
  const cy = H / 2 - 80;
  const items: {x: number; y: number; r: number; c: string; o?: number}[] = [];
  const colors = [theme.accent, theme.accent2, theme.texte];

  if (mode === 'orbit') {
    items.push({x: cx, y: cy, r: 46, c: theme.accent});
    for (let i = 0; i < count; i++) {
      const rad = 90 + (i / count) * 380;
      const speed = 3.2 / Math.pow(rad / 90, 1.5); // 3e loi de Kepler
      const a = R() * Math.PI * 2 + t * speed;
      items.push({x: cx + Math.cos(a) * rad, y: cy + Math.sin(a) * rad * 0.9, r: 6 + R() * 10, c: colors[i % 2 ? 1 : 2]});
    }
  } else if (mode === 'pendulum_wave') {
    // Vue de dessus d'une "vague de pendules" : chaque ligne oscille un peu plus vite que la précédente
    const n = Math.min(count, 18);
    const top = SAFE_TOP + 60;
    const bottom = H - SAFE_BOTTOM - 260;
    for (let i = 0; i < n; i++) {
      const cycles = 51 + i; // nombre d'oscillations en 60 s
      const x = cx + 400 * Math.cos((2 * Math.PI * cycles * t) / 60);
      const y = top + (i * (bottom - top)) / (n - 1);
      items.push({x, y, r: 22, c: colors[i % 2]});
    }
  } else {
    // gravity / bounce / swarm : intégration simple, recalculée de façon déterministe
    const n = Math.min(count, 120);
    const ps = Array.from({length: n}).map(() => ({
      x: 140 + R() * (W - 280),
      y: SAFE_TOP + 60 + R() * 500,
      vx: (R() - 0.5) * 14,
      vy: (R() - 0.5) * 6,
      r: 10 + R() * 16,
    }));
    const dt = 1;
    const floor = H - SAFE_BOTTOM - 40;
    for (let f = 0; f < frame; f++) {
      for (const p of ps) {
        if (mode === 'swarm') {
          const ang = Math.atan2(cy - p.y, cx - p.x) + Math.PI / 2.4;
          p.vx = p.vx * 0.96 + Math.cos(ang) * 0.9;
          p.vy = p.vy * 0.96 + Math.sin(ang) * 0.9;
        } else {
          p.vy += mode === 'gravity' ? 0.9 : 0.6;
        }
        p.x += p.vx * dt;
        p.y += p.vy * dt;
        if (p.y + p.r > floor) {
          p.y = floor - p.r;
          p.vy *= mode === 'gravity' ? -0.55 : -0.92;
        }
        if (p.x - p.r < 60 || p.x + p.r > W - 60) {
          p.vx *= -1;
          p.x = Math.min(Math.max(p.x, 60 + p.r), W - 60 - p.r);
        }
      }
    }
    ps.forEach((p, i) => items.push({x: p.x, y: p.y, r: p.r, c: colors[i % 3]}));
  }

  return (
    <svg width={W} height={H} style={{position: 'absolute'}}>
      {mode === 'orbit'
        ? [140, 260, 380, 470].map((r) => <ellipse key={r} cx={cx} cy={cy} rx={r} ry={r * 0.9} fill="none" stroke={theme.texte} strokeOpacity={0.12} strokeWidth={2} />)
        : null}
      {mode === 'pendulum_wave'
        ? items.map((it, i) => <line key={'l' + i} x1={cx - 420} y1={it.y} x2={cx + 420} y2={it.y} stroke={theme.texte} strokeOpacity={0.15} strokeWidth={2} />)
        : null}
      {items.map((it, i) => (
        <circle key={i} cx={it.x} cy={it.y} r={it.r} fill={it.c} opacity={it.o ?? 0.95} />
      ))}
    </svg>
  );
};

export const Particles: React.FC<P<'particles'>> = ({scene, theme}) => {
  const cap = usePop(12);
  return (
    <AbsoluteFill>
      <Sim mode={scene.mode} count={scene.count ?? 40} theme={theme} />
      <div style={{position: 'absolute', bottom: SAFE_BOTTOM + 20, left: 80, right: 80, ...body(theme, 48), opacity: cap, backgroundColor: theme.fond + 'CC', padding: '18px 24px', borderRadius: 20}}>
        {scene.caption}
      </div>
    </AbsoluteFill>
  );
};

// ---------- OUTRO ----------
export const Outro: React.FC<P<'outro'>> = ({scene, theme}) => {
  const a = usePop(0);
  const b = usePop(12, 9);
  return (
    <SafeArea>
      <div style={{...title(theme, 80), opacity: a, transform: `scale(${0.85 + 0.15 * a})`}}>{scene.text}</div>
      <div style={{marginTop: 70, transform: `scale(${b})`, backgroundColor: theme.accent, color: theme.fond, ...body(theme, 44), fontWeight: 700, padding: '24px 40px', borderRadius: 60}}>
        <span style={{color: theme.fond}}>{scene.cta}</span>
      </div>
    </SafeArea>
  );
};

export const SceneView: React.FC<{scene: Scene; theme: Theme}> = ({scene, theme}) => {
  switch (scene.type) {
    case 'hook':
      return <Hook scene={scene} theme={theme} />;
    case 'kinetic':
      return <Kinetic scene={scene} theme={theme} />;
    case 'counter':
      return <Counter scene={scene} theme={theme} />;
    case 'bars':
      return <Bars scene={scene} theme={theme} />;
    case 'timeline':
      return <Timeline scene={scene} theme={theme} />;
    case 'dots':
      return <Dots scene={scene} theme={theme} />;
    case 'compare':
      return <Compare scene={scene} theme={theme} />;
    case 'particles':
      return <Particles scene={scene} theme={theme} />;
    case 'outro':
      return <Outro scene={scene} theme={theme} />;
    default:
      return null;
  }
};
