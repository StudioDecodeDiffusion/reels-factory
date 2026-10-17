import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import {Scene, Theme} from './types';
import {AnimatedSprite, encrePour, Etincelles, fontPixel, fontTitre, INK, PixelSprite, Sticker} from './fx';
import {SPRITES} from './sprites';
import {Highlight, rng} from './ui';

// Zone de contenu (au-dessus de la mascotte et des sous-titres)
const TOP = 330;

export type Ctx = {theme: Theme; bg: string; c1: string; c2: string; index: number; mascotteDroite: boolean};
// x d'un sprite placé en bas : du côté opposé à la mascotte
const xBas = (ctx: Ctx, gauche = 90, droite = 760) => (ctx.mascotteDroite ? gauche : droite);
type P<T extends Scene['type']> = {scene: Extract<Scene, {type: T}>; ctx: Ctx};

const big = (color: string, size: number): React.CSSProperties => ({
  fontFamily: fontTitre,
  fontWeight: 900,
  fontSize: size,
  lineHeight: 0.98,
  color,
  letterSpacing: -2,
});

const fmt = (n: number, d: number) => n.toLocaleString('fr-FR', {minimumFractionDigits: d, maximumFractionDigits: d});

// Garde « : ? ! % € » collés au mot précédent (typographie française)
const mots = (t: string) =>
  t.split(' ').reduce<string[]>((acc, w) => {
    if (acc.length && /^[%:?!€;»]+\.?$/.test(w)) acc[acc.length - 1] += ' ' + w;
    else acc.push(w);
    return acc;
  }, []);

const usePop = (delay = 0, damping = 9) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return spring({frame: frame - delay, fps, config: {damping, mass: 0.6}});
};

const SpriteDeScene: React.FC<{scene: Scene; x: number; y: number; px?: number; delay?: number; rotate?: number}> = ({scene, x, y, px = 16, delay = 6, rotate = 0}) =>
  scene.sprite && SPRITES[scene.sprite] ? (
    <AnimatedSprite name={scene.sprite} anim={scene.sprite_anim ?? 'bounce'} px={px} x={x} y={y} delay={delay} rotate={rotate} />
  ) : null;

// ───────────────────────── HOOK : mots qui claquent, gros, penchés, ferrés à gauche
export const Hook: React.FC<P<'hook'>> = ({scene, ctx}) => {
  const frame = useCurrentFrame();
  const ink = encrePour(ctx.bg);
  const ws = mots(scene.title);
  const sub = usePop(ws.length * 4 + 8);
  const shake = frame < 30 && frame > ws.length * 4 ? (frame % 4 < 2 ? 4 : -4) : 0;
  return (
    <>
      <div style={{position: 'absolute', left: 70, right: 70, top: TOP + 60, transform: `rotate(-4deg) translateX(${shake}px)`}}>
        <div style={{display: 'flex', flexWrap: 'wrap', gap: '0 26px'}}>
          {ws.map((w, i) => {
            const d = i * 4;
            const p = spring({frame: frame - d, fps: 30, config: {damping: 7, mass: 0.5}});
            const chiffre = /\d|\?/.test(w);
            return (
              <span key={i} style={{...big(chiffre ? ctx.c1 : ink, 124), display: 'inline-block', transform: `scale(${p}) rotate(${(1 - p) * -20}deg)`, WebkitTextStroke: chiffre ? `5px ${INK}` : '0', textShadow: chiffre ? `8px 8px 0 ${INK}` : 'none', paintOrder: 'stroke fill'}}>
                {w}
              </span>
            );
          })}
        </div>
        {scene.subtitle ? (
          <div style={{marginTop: 50, display: 'inline-block', transform: `scale(${sub}) rotate(3deg)`}}>
            <Sticker couleur={ctx.c2} rotate={3} delay={ws.length * 4 + 8}>
              <span style={{fontFamily: fontTitre, fontWeight: 800, fontSize: 52}}>{scene.subtitle}</span>
            </Sticker>
          </div>
        ) : null}
      </div>
      {ws.length * 4 < 40 ? <Etincelles x={760} y={TOP + 140} couleur={ctx.c1} delay={ws.length * 4} /> : null}
      <SpriteDeScene scene={scene} x={760} y={TOP + 330} px={15} rotate={8} delay={ws.length * 4} />
    </>
  );
};

// ───────────────────────── KINETIC : lignes surlignées au marqueur, alternées gauche / droite
export const Kinetic: React.FC<P<'kinetic'>> = ({scene, ctx}) => {
  const {fps} = useVideoConfig();
  const ink = encrePour(ctx.bg);
  const per = Math.max(12, Math.floor((scene.duration * fps * 0.55) / Math.max(1, scene.lines.length)));
  return (
    <>
      <div style={{position: 'absolute', left: 60, right: 60, top: TOP + 40, display: 'flex', flexDirection: 'column', gap: 34}}>
        {scene.lines.map((l, i) => {
          // eslint-disable-next-line react-hooks/rules-of-hooks
          const p = usePop(i * per, 10);
          const droite = i % 2 === 1;
          const marque = l.toLowerCase().includes((scene.highlight ?? '§').toLowerCase());
          return (
            <div key={i} style={{alignSelf: droite ? 'flex-end' : 'flex-start', transform: `translateX(${(1 - p) * (droite ? 500 : -500)}px) rotate(${droite ? 2 : -2}deg)`}}>
              <span style={{...big(marque ? INK : ink, l.length > 22 ? 72 : 88), backgroundColor: marque ? ctx.c1 : 'transparent', padding: marque ? '4px 18px' : 0, boxShadow: marque ? `10px 10px 0 ${INK}` : 'none', border: marque ? `6px solid ${INK}` : 'none', borderRadius: 10, display: 'inline-block'}}>
                <Highlight text={l} word={marque ? undefined : scene.highlight} color={ctx.c1} />
              </span>
            </div>
          );
        })}
      </div>
      <SpriteDeScene scene={scene} x={xBas(ctx)} y={TOP + 520} px={14} delay={per} />
    </>
  );
};

// ───────────────────────── COUNTER : chiffre géant dans un autocollant, sprites en pluie
export const Counter: React.FC<P<'counter'>> = ({scene, ctx}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const from = scene.from ?? 0;
  const end = fps * Math.min(2.4, scene.duration * 0.5);
  const v = interpolate(frame, [6, end], [from, scene.to], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.exp)});
  const txt = `${scene.prefix ?? ''}${fmt(v, scene.decimals ?? 0)}${scene.suffix ?? ''}`;
  const lab = usePop(14);
  return (
    <>
      {scene.sprite && scene.sprite_anim === 'rain' ? <SpriteDeScene scene={scene} x={0} y={0} /> : null}
      <div style={{position: 'absolute', left: 60, top: TOP + 80}}>
        <Sticker couleur={ctx.c1} rotate={-5}>
          <span style={{...big(encrePour(ctx.c1), txt.length > 9 ? 140 : 200), whiteSpace: 'nowrap', fontVariantNumeric: 'tabular-nums'}}>{txt}</span>
        </Sticker>
      </div>
      <Etincelles x={520} y={TOP + 200} couleur={ctx.c2} delay={Math.round(end)} />
      <div style={{position: 'absolute', left: 120, right: 260, top: TOP + 470, transform: `translateY(${(1 - lab) * 60}px)`, opacity: lab}}>
        <span style={{fontFamily: fontTitre, fontWeight: 800, fontSize: 58, color: encrePour(ctx.bg), lineHeight: 1.15}}>{scene.label}</span>
      </div>
      {scene.sprite && scene.sprite_anim !== 'rain' ? <SpriteDeScene scene={scene} x={xBas(ctx, 120, 800)} y={TOP + 560} px={14} delay={10} /> : null}
    </>
  );
};

// ───────────────────────── BARS : barres pixel qui montent par paliers, horizontales, désaxées
export const Bars: React.FC<P<'bars'>> = ({scene, ctx}) => {
  const frame = useCurrentFrame();
  const ink = encrePour(ctx.bg);
  const items = scene.items.slice(0, 6);
  const max = Math.max(...items.map((i) => i.value), 1);
  const head = usePop(0);
  const block = 30;
  const maxBlocks = 24;
  return (
    <>
      <div style={{position: 'absolute', left: 70, top: TOP, transform: `rotate(-3deg) scale(${head})`, transformOrigin: 'left'}}>
        <span style={{...big(ink, 76)}}>{scene.title}</span>
      </div>
      <div style={{position: 'absolute', left: 70, right: 60, top: TOP + 150}}>
        {items.map((it, i) => {
          const n = Math.max(1, Math.round((it.value / max) * maxBlocks));
          const shown = Math.min(n, Math.max(0, Math.floor((frame - 10 - i * 8) / 1.5)));
          const isMax = it.value === max;
          const col = isMax ? ctx.c1 : ctx.c2;
          return (
            <div key={i} style={{marginBottom: 26, marginLeft: i % 2 ? 30 : 0}}>
              <div style={{display: 'flex', alignItems: 'baseline', gap: 16, marginBottom: 6}}>
                <span style={{fontFamily: fontPixel, fontSize: 36, color: ink}}>{it.label}</span>
                <span style={{fontFamily: fontTitre, fontWeight: 900, fontSize: 46, color: ink, opacity: shown >= n ? 1 : 0}}>
                  {fmt(it.value, Number.isInteger(it.value) ? 0 : 1)}
                  {scene.unit ?? ''}
                </span>
              </div>
              <div style={{display: 'flex', gap: 3}}>
                {Array.from({length: shown}).map((_, b) => (
                  <div key={b} style={{width: block, height: block + 12, backgroundColor: col, border: `4px solid ${INK}`, boxSizing: 'border-box'}} />
                ))}
              </div>
            </div>
          );
        })}
      </div>
      <SpriteDeScene scene={scene} x={790} y={TOP - 40} px={11} delay={20} />
    </>
  );
};

// ───────────────────────── TIMELINE : chemin en zigzag avec étapes-autocollants
export const Timeline: React.FC<P<'timeline'>> = ({scene, ctx}) => {
  const {fps} = useVideoConfig();
  const ink = encrePour(ctx.bg);
  const n = Math.min(scene.events.length, 5);
  const per = Math.floor((scene.duration * fps * 0.6) / n);
  return (
    <>
      {scene.title ? <div style={{position: 'absolute', left: 70, top: TOP - 10, ...big(ink, 70), transform: 'rotate(-2deg)'}}>{scene.title}</div> : null}
      {scene.events.slice(0, n).map((e, i) => {
        const gauche = i % 2 === 0;
        return (
          <div key={i} style={{position: 'absolute', top: TOP + 120 + i * 150, left: gauche ? 70 : 400, width: 600}}>
            <Sticker couleur={i % 2 ? ctx.c2 : ctx.c1} rotate={gauche ? -3 : 3} delay={i * per} style={{padding: '14px 26px'}}>
              <div style={{fontFamily: fontPixel, fontSize: 34}}>{e.date}</div>
              <div style={{fontFamily: fontTitre, fontWeight: 800, fontSize: 44, lineHeight: 1.1}}>{e.text}</div>
            </Sticker>
          </div>
        );
      })}
    </>
  );
};

// ───────────────────────── DOTS : 100 petits humains pixel, X sont colorés
export const Dots: React.FC<P<'dots'>> = ({scene, ctx}) => {
  const frame = useCurrentFrame();
  const ink = encrePour(ctx.bg);
  const total = Math.min(Math.max(scene.total, 1), 100);
  const hi = Math.min(scene.highlighted, total);
  const lab = usePop(Math.min(total / 2 + 20, 60));
  const humain = SPRITES.humain;
  const recolor = (c: string) => humain.map((r) => r.replace(/c/g, c));
  const allume = recolor('p');
  const eteint = humain.map((r) => r.replace(/[cs]/g, 'g'));
  return (
    <>
      <div style={{position: 'absolute', left: 230, top: TOP + 10, display: 'grid', gridTemplateColumns: 'repeat(10, 42px)', gap: '8px 14px', transform: 'rotate(-2deg)'}}>
        {Array.from({length: total}).map((_, i) => {
          const visible = frame > i * 0.5;
          const on = i < hi && frame > 25 + i * 1.2;
          return (
            <div key={i} style={{opacity: visible ? 1 : 0, transform: on ? `translateY(${-Math.abs(Math.round(Math.sin((frame + i * 5) / 6) * 2)) * 4}px)` : 'none'}}>
              <PixelSprite sprite={on ? allume : eteint} px={6} />
            </div>
          );
        })}
      </div>
      <div style={{position: 'absolute', left: 80, right: 80, top: TOP + 660, opacity: lab, transform: `scale(${0.8 + lab * 0.2}) rotate(2deg)`}}>
        <span style={{fontFamily: fontTitre, fontWeight: 800, fontSize: 52, color: ink}}>
          <Highlight text={scene.label} word={String(hi)} color={ctx.c1} />
        </span>
      </div>
    </>
  );
};

// ───────────────────────── COMPARE : deux autocollants à des hauteurs différentes + tampon VS
export const Compare: React.FC<P<'compare'>> = ({scene, ctx}) => {
  const frame = useCurrentFrame();
  const ink = encrePour(ctx.bg);
  const vs = spring({frame: frame - 26, fps: 30, config: {damping: 6}});
  const card = (side: typeof scene.left, col: string, rot: number, delay: number) => (
    <Sticker couleur={col} rotate={rot} delay={delay} style={{width: 400, textAlign: 'center'}}>
      <div style={{fontFamily: fontPixel, fontSize: 38}}>{side.label}</div>
      <div style={{...big(encrePour(col), side.value.length > 7 ? 84 : 110), margin: '14px 0', whiteSpace: 'nowrap'}}>{side.value}</div>
      {side.caption ? <div style={{fontFamily: fontTitre, fontWeight: 700, fontSize: 34}}>{side.caption}</div> : null}
    </Sticker>
  );
  return (
    <>
      {scene.title ? <div style={{position: 'absolute', left: 70, top: TOP - 20, ...big(ink, 78), transform: 'rotate(-3deg)'}}>{scene.title}</div> : null}
      <div style={{position: 'absolute', left: 60, top: TOP + 150}}>{card(scene.left, ctx.c2, -6, 4)}</div>
      <div style={{position: 'absolute', right: 60, top: TOP + 360}}>{card(scene.right, ctx.c1, 5, 16)}</div>
      <div style={{position: 'absolute', left: 430, top: TOP + 330, transform: `scale(${vs}) rotate(${-12 + Math.floor(frame / 10) * 0}deg)`, backgroundColor: INK, color: '#fff', fontFamily: fontPixel, fontSize: 60, padding: '10px 22px', border: `6px solid #fff`}}>VS</div>
      <SpriteDeScene scene={scene} x={xBas(ctx, 140, 700)} y={TOP + 620} px={12} delay={30} />
    </>
  );
};

// ───────────────────────── PARTICLES : simulation colorée (reprend les modes existants)
export const Particles: React.FC<P<'particles'>> = ({scene, ctx}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const R = rng(42);
  const cols = [ctx.c1, ctx.c2, INK];
  const n = Math.min(scene.count ?? 40, 60);
  const cx = 540;
  const cy = TOP + 380;
  const items = Array.from({length: n}).map((_, i) => {
    const rad = 80 + (i / n) * 360;
    const a = R() * Math.PI * 2 + t * (3 / Math.pow(rad / 80, 1.5));
    return {x: cx + Math.cos(a) * rad, y: cy + Math.sin(a) * rad * 0.8, s: Math.round((1 + R() * 2)) * 10, c: cols[i % 3]};
  });
  return (
    <>
      {items.map((it, i) => (
        <div key={i} style={{position: 'absolute', left: Math.round(it.x / 6) * 6, top: Math.round(it.y / 6) * 6, width: it.s, height: it.s, backgroundColor: it.c, border: `3px solid ${INK}`}} />
      ))}
      <SpriteDeScene scene={scene} x={cx - 128} y={cy - 128} px={16} />
      <div style={{position: 'absolute', left: 80, right: 80, top: TOP + 790}}>
        <Sticker couleur={ctx.c2} rotate={-2} delay={10}>
          <span style={{fontFamily: fontTitre, fontWeight: 800, fontSize: 46}}>{scene.caption}</span>
        </Sticker>
      </div>
    </>
  );
};

// ───────────────────────── OUTRO : chute en gros + bouton d'abonnement qui pulse
export const Outro: React.FC<P<'outro'>> = ({scene, ctx}) => {
  const frame = useCurrentFrame();
  const ink = encrePour(ctx.bg);
  const a = usePop(0);
  const pulse = 1 + 0.05 * Math.round(Math.sin(frame / 5));
  return (
    <>
      <div style={{position: 'absolute', left: 70, right: 90, top: TOP + 40, transform: `rotate(-3deg) scale(${a})`, transformOrigin: 'left'}}>
        <span style={{...big(ink, 104)}}>{scene.text}</span>
      </div>
      <div style={{position: 'absolute', left: 90, right: 90, top: TOP + 520, transform: `scale(${pulse})`}}>
        <Sticker couleur={ctx.c1} rotate={2} delay={14} style={{textAlign: 'center'}}>
          <span style={{fontFamily: fontTitre, fontWeight: 900, fontSize: 50}}>{scene.cta}</span>
        </Sticker>
      </div>
      <SpriteDeScene scene={scene} x={xBas(ctx, 120, 760)} y={TOP + 330} px={12} delay={10} />
    </>
  );
};

export const SceneViewPixel: React.FC<{scene: Scene; ctx: Ctx}> = ({scene, ctx}) => {
  switch (scene.type) {
    case 'hook':
      return <Hook scene={scene} ctx={ctx} />;
    case 'kinetic':
      return <Kinetic scene={scene} ctx={ctx} />;
    case 'counter':
      return <Counter scene={scene} ctx={ctx} />;
    case 'bars':
      return <Bars scene={scene} ctx={ctx} />;
    case 'timeline':
      return <Timeline scene={scene} ctx={ctx} />;
    case 'dots':
      return <Dots scene={scene} ctx={ctx} />;
    case 'compare':
      return <Compare scene={scene} ctx={ctx} />;
    case 'particles':
      return <Particles scene={scene} ctx={ctx} />;
    case 'outro':
      return <Outro scene={scene} ctx={ctx} />;
    default:
      return null;
  }
};
