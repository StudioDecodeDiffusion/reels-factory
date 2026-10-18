// Scènes « trend » : pancartes du fantôme, SMS anonyme, débat pour/contre, réaction qui monte, conte.
import React from 'react';
import {Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import {encrePour, fontPixel, fontTitre, INK, PixelSprite, Sticker} from './fx';
import {Scene} from './types';
import {VISAGES, MASCOTTE_CORPS} from './sprites';

const TOP = 330;
type Ex<T extends Scene['type']> = Extract<Scene, {type: T}>;

// Fantôme pixel (drap blanc)
const FANTOME = [
  '....wwwwww....',
  '..wwwwwwwwww..',
  '.wwwwwwwwwwww.',
  '.wwwkkwwkkwww.',
  'wwwwkkwwkkwwww',
  'wwwwwwwwwwwwww',
  'wwwwwwkkwwwwww',
  'wwwwwkwwkwwwww',
  'wwwwwwwwwwwwww',
  'wwwwwwwwwwwwww',
  'wwwwwwwwwwwwww',
  'ww.www..www.ww',
  'w...w....w...w',
];

// ───────────────────────── PANCARTES : le fantôme brandit une idée reçue, la réponse chiffrée la tamponne
export const Pancartes: React.FC<{scene: Ex<'pancartes'>; c1: string; c2: string; bg: string}> = ({scene, c1, c2, bg}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const n = scene.items.length;
  const per = Math.floor((scene.duration * fps) / n);
  const k = Math.min(n - 1, Math.floor(frame / per));
  const f = frame - k * per;
  const it = scene.items[k];
  const flip = interpolate(f, [0, 8], [90, 0], {extrapolateRight: 'clamp'});
  const tampon = spring({frame: f - Math.round(per * 0.45), fps, config: {damping: 7, mass: 0.6}});
  const flotte = Math.sin(frame / 8) * 14;
  return (
    <>
      <div style={{position: 'absolute', left: 60, top: TOP - 10, fontFamily: fontPixel, fontSize: 34, color: encrePour(bg)}}>{scene.title ?? 'IDÉES REÇUES'} · {k + 1}/{n}</div>
      <div style={{position: 'absolute', left: 360, top: TOP + 470 + flotte, opacity: 0.95}}>
        <PixelSprite sprite={FANTOME} px={26} couleurs={{w: '#F4F1EA', k: INK}} />
      </div>
      {/* bâton + pancarte */}
      <div style={{position: 'absolute', left: 520, top: TOP + 300 + flotte, width: 14, height: 260, backgroundColor: '#8B5A2B', border: `4px solid ${INK}`}} />
      <div style={{position: 'absolute', left: 90, right: 90, top: TOP + 70 + flotte, transform: `perspective(900px) rotateY(${flip}deg) rotate(-2deg)`}}>
        <div style={{backgroundColor: '#FFF8E1', border: `9px solid ${INK}`, boxShadow: `12px 12px 0 ${INK}`, padding: '26px 30px', minHeight: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center'}}>
          <span style={{fontFamily: fontTitre, fontWeight: 900, fontSize: it.pancarte.length > 40 ? 52 : 64, color: INK, lineHeight: 1.05}}>« {it.pancarte} »</span>
        </div>
      </div>
      <div style={{position: 'absolute', left: 120, right: 120, top: TOP + 330, transform: `rotate(-6deg) scale(${2.2 - 1.2 * tampon})`, opacity: Math.min(1, tampon * 1.4)}}>
        <Sticker couleur={k % 2 ? c2 : c1} rotate={0}>
          <span style={{fontFamily: fontTitre, fontWeight: 900, fontSize: 48, color: INK}}>{it.reponse}</span>
        </Sticker>
      </div>
    </>
  );
};

// ───────────────────────── SMS ANONYME : « Message de : A »
export const SmsAnonyme: React.FC<{scene: Ex<'sms'>}> = ({scene}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = spring({frame: frame - 4, fps, config: {damping: 12}});
  const total = scene.texte.length;
  const n = Math.floor(interpolate(frame, [12, 12 + total * 0.9], [0, total], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  const vibre = frame < 18 ? Math.sin(frame * 3) * 8 : 0;
  return (
    <>
      <div style={{position: 'absolute', left: 0, right: 0, top: 0, bottom: 0, background: 'radial-gradient(circle at 50% 40%, rgba(255,0,80,0.25), rgba(0,0,0,0.85))'}} />
      <div style={{position: 'absolute', left: 110, right: 110, top: TOP + 40, transform: `translateY(${(1 - p) * -300}px) translateX(${vibre}px)`}}>
        <div style={{backgroundColor: 'rgba(20,19,28,0.92)', border: '4px solid #444', borderRadius: 36, padding: '26px 30px', boxShadow: '0 20px 60px rgba(0,0,0,0.6)'}}>
          <div style={{display: 'flex', alignItems: 'center', gap: 16, marginBottom: 14}}>
            <div style={{width: 64, height: 64, borderRadius: 16, backgroundColor: '#E5133A', color: '#fff', fontFamily: fontTitre, fontWeight: 900, fontSize: 44, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>A</div>
            <div>
              <div style={{fontFamily: fontTitre, fontWeight: 800, fontSize: 34, color: '#fff'}}>{scene.expediteur ?? 'Numéro masqué'}</div>
              <div style={{fontFamily: fontPixel, fontSize: 20, color: '#aaa'}}>maintenant</div>
            </div>
          </div>
          <div style={{fontFamily: fontTitre, fontWeight: 700, fontSize: 46, color: '#fff', lineHeight: 1.2, minHeight: 200}}>
            {scene.texte.slice(0, n)}
            <span style={{opacity: Math.floor(frame / 8) % 2 ? 1 : 0}}>▌</span>
          </div>
          <div style={{textAlign: 'right', fontFamily: fontTitre, fontWeight: 900, fontSize: 52, color: '#E5133A', opacity: n >= total ? 1 : 0}}>-{scene.signature ?? 'A'}</div>
        </div>
      </div>
    </>
  );
};

// ───────────────────────── DÉBAT : POUR / CONTRE, la balance penche
export const Debat: React.FC<{scene: Ex<'debat'>; c1: string; c2: string; bg: string}> = ({scene, c1, c2, bg}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const args = [...scene.pour.map((t) => ({t, pour: true})), ...scene.contre.map((t) => ({t, pour: false}))];
  const ordre = args.map((_, i) => i).sort((a, b) => (a % scene.pour.length) - (b % scene.pour.length) || a - b);
  const per = Math.floor((scene.duration * fps * 0.7) / Math.max(1, args.length));
  const vus = ordre.filter((_, j) => frame >= 10 + j * per);
  const poids = vus.reduce((s, i) => s + (args[i].pour ? 1 : -1), 0);
  const angle = interpolate(poids, [-3, 3], [-12, 12], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const ink = encrePour(bg);
  const col = (pour: boolean) => (
    <div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: 18}}>
      <div style={{fontFamily: fontPixel, fontSize: 40, color: INK, backgroundColor: pour ? c1 : c2, border: `6px solid ${INK}`, padding: '6px 0', textAlign: 'center'}}>{pour ? scene.label_pour ?? 'POUR' : scene.label_contre ?? 'CONTRE'}</div>
      {args.map((a, i) =>
        a.pour === pour && vus.includes(i) ? (
          <div key={i} style={{transform: `scale(${spring({frame: frame - 10 - ordre.indexOf(i) * per, fps, config: {damping: 10}})})`}}>
            <div style={{backgroundColor: '#fff', border: `5px solid ${INK}`, borderRadius: 14, padding: '12px 14px', fontFamily: fontTitre, fontWeight: 800, fontSize: 34, color: INK, lineHeight: 1.15, boxShadow: `6px 6px 0 ${INK}`}}>{a.t}</div>
          </div>
        ) : null,
      )}
    </div>
  );
  return (
    <>
      {scene.title ? <div style={{position: 'absolute', left: 60, right: 60, top: TOP - 10, fontFamily: fontTitre, fontWeight: 900, fontSize: 64, color: ink, lineHeight: 1}}>{scene.title}</div> : null}
      {/* balance */}
      <div style={{position: 'absolute', left: 140, right: 140, top: TOP + 170, height: 14, backgroundColor: INK, transform: `rotate(${-angle}deg)`, transition: 'none'}} />
      <div style={{position: 'absolute', left: 528, top: TOP + 170, width: 24, height: 90, backgroundColor: INK}} />
      <div style={{position: 'absolute', left: 50, right: 50, top: TOP + 290, display: 'flex', gap: 30}}>
        {col(true)}
        {col(false)}
      </div>
    </>
  );
};

// ───────────────────────── RÉACTION : chiffres qui montent, Déco réagit de plus en plus fort (trend « My reaction to… »)
export const Reaction: React.FC<{scene: Ex<'reaction'>; c1: string; c2: string; bg: string}> = ({scene, c1, c2, bg}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const n = scene.paliers.length;
  const per = Math.floor((scene.duration * fps) / n);
  const k = Math.min(n - 1, Math.floor(frame / per));
  const f = frame - k * per;
  const intensite = (k + 1) / n;
  const visages = ['neutre', 'pense', 'choc', 'colere', 'choc'];
  const v = VISAGES[visages[Math.min(visages.length - 1, Math.round(intensite * (visages.length - 1)))]] ?? VISAGES.neutre;
  const secousse = Math.sin(frame * 2.2) * intensite * 14 * (f < 12 ? 1 : 0.3);
  const zoom = 1 + intensite * 0.5 * spring({frame: f, fps, config: {damping: 8}});
  const p = spring({frame: f, fps, config: {damping: 9}});
  const ink = encrePour(bg);
  return (
    <>
      <div style={{position: 'absolute', left: 60, top: TOP - 10, fontFamily: fontPixel, fontSize: 36, color: ink}}>MA RÉACTION À…</div>
      <div style={{position: 'absolute', left: 60, right: 60, top: TOP + 50, transform: `scale(${0.6 + 0.4 * p})`, transformOrigin: 'left'}}>
        <Sticker couleur={k % 2 ? c2 : c1} rotate={-3}>
          <span style={{fontFamily: fontTitre, fontWeight: 900, fontSize: 104, color: INK, whiteSpace: 'nowrap'}}>{scene.paliers[k].valeur}</span>
        </Sticker>
        <div style={{marginTop: 18, fontFamily: fontTitre, fontWeight: 800, fontSize: 50, color: ink}}>{scene.paliers[k].label}</div>
      </div>
      {/* « caméra réaction » sur Déco */}
      <div style={{position: 'absolute', left: 250, top: TOP + 470, width: 580, height: 520, border: `10px solid ${INK}`, borderRadius: 20, backgroundColor: k >= n - 1 ? '#FF3B3B' : '#2EC4B6', overflow: 'hidden', transform: `translateX(${secousse}px) rotate(${secousse / 6}deg)`, boxShadow: `14px 14px 0 ${INK}`}}>
        <div style={{position: 'absolute', left: '50%', top: '55%', transform: `translate(-50%, -50%) scale(${zoom})`}}>
          <PixelSprite sprite={MASCOTTE_CORPS} px={18} calques={[{sprite: v, x: 5, y: 8}]} />
        </div>
        <div style={{position: 'absolute', left: 14, top: 10, fontFamily: fontPixel, fontSize: 24, color: INK, backgroundColor: '#fff', padding: '2px 10px'}}>● REC</div>
      </div>
      {/* jauge de réaction */}
      <div style={{position: 'absolute', left: 120, right: 120, top: TOP + 1020, height: 40, border: `6px solid ${INK}`, backgroundColor: '#fff'}}>
        <div style={{width: `${intensite * 100}%`, height: '100%', background: `linear-gradient(90deg, #2BD99F, #FFD23F, #FF3B3B)`}} />
      </div>
    </>
  );
};

// ───────────────────────── CONTE : « il était une fois », texte qui s'écrit, poussières qui flottent
export const Conte: React.FC<{scene: Ex<'conte'>}> = ({scene}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const txt = scene.texte;
  const n = Math.floor(interpolate(frame, [8, Math.max(20, scene.duration * fps * 0.7)], [0, txt.length], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  const lueur = 0.6 + 0.15 * Math.sin(frame / 6) + 0.05 * Math.sin(frame / 2.3);
  return (
    <>
      <div style={{position: 'absolute', inset: 0, background: `radial-gradient(circle at 50% 42%, rgba(255,190,90,${lueur * 0.5}), rgba(10,6,20,0.95) 70%)`}} />
      {Array.from({length: 26}).map((_, i) => {
        const x = (i * 137) % 1080;
        const y = 1500 - ((frame * (0.6 + (i % 5) * 0.2) + i * 90) % 1400);
        return <div key={i} style={{position: 'absolute', left: x + Math.sin((frame + i * 20) / 30) * 20, top: y, width: 6, height: 6, backgroundColor: '#FFE7A8', opacity: 0.5}} />;
      })}
      {scene.titre ? (
        <div style={{position: 'absolute', left: 80, right: 80, top: TOP - 20, textAlign: 'center', fontFamily: fontPixel, fontSize: 40, color: '#FFD98A', letterSpacing: 4, opacity: interpolate(frame, [0, 10], [0, 1], {extrapolateRight: 'clamp'})}}>{scene.titre}</div>
      ) : null}
      <div style={{position: 'absolute', left: 110, right: 110, top: TOP + 90, padding: '40px 44px', backgroundColor: '#F3E3C3', border: `8px solid #5A3B1E`, boxShadow: '0 0 0 6px #2A1A0C, 18px 18px 0 rgba(0,0,0,0.5)', transform: 'rotate(-1.5deg)'}}>
        <div style={{fontFamily: "'Georgia', serif", fontStyle: 'italic', fontSize: 50, lineHeight: 1.35, color: '#2A1A0C', minHeight: 420}}>
          {txt.slice(0, n)}
          <span style={{opacity: n < txt.length && Math.floor(frame / 7) % 2 ? 1 : 0}}>|</span>
        </div>
      </div>
      {scene.chute && n >= txt.length ? (
        <div style={{position: 'absolute', left: 90, right: 90, top: TOP + 780, transform: `scale(${spring({frame: frame - Math.round(scene.duration * fps * 0.72), fps, config: {damping: 7}})}) rotate(-3deg)`}}>
          <Sticker couleur="#FF8A1F" rotate={0}>
            <span style={{fontFamily: fontTitre, fontWeight: 900, fontSize: 56, color: INK}}>{scene.chute}</span>
          </Sticker>
        </div>
      ) : null}
    </>
  );
};

// ───────────────────────── PHOTO : vraie image de l'événement (licence libre), effet Ken Burns, crédit obligatoire
export const Photo: React.FC<{scene: Ex<'photo'>; c1: string}> = ({scene, c1}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const d = scene.duration * fps;
  const z = interpolate(frame, [0, d], [1.08, 1.22]);
  const x = interpolate(frame, [0, d], [-20, 20]);
  const p = spring({frame: frame - 6, fps, config: {damping: 12}});
  return (
    <>
      <div style={{position: 'absolute', left: 40, right: 40, top: 300, height: 980, overflow: 'hidden', border: `10px solid ${INK}`, boxShadow: `16px 16px 0 ${INK}`, backgroundColor: '#222'}}>
        {scene.src ? <Img src={staticFile(scene.src)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${z}) translateX(${x}px)`}} /> : null}
        <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 260, background: 'linear-gradient(transparent, rgba(0,0,0,0.75))'}} />
        {scene.legende ? <div style={{position: 'absolute', left: 30, right: 30, bottom: 50, fontFamily: fontTitre, fontWeight: 800, fontSize: 46, color: '#fff', lineHeight: 1.1}}>{scene.legende}</div> : null}
        <div style={{position: 'absolute', right: 14, bottom: 10, fontFamily: fontPixel, fontSize: 20, color: '#ddd'}}>© {scene.credit}</div>
      </div>
      {scene.titre ? (
        <div style={{position: 'absolute', left: 60, top: 250, transform: `scale(${p}) rotate(-3deg)`, transformOrigin: 'left'}}>
          <Sticker couleur={c1} rotate={0}><span style={{fontFamily: fontTitre, fontWeight: 900, fontSize: 52, color: INK}}>{scene.titre}</span></Sticker>
        </div>
      ) : null}
    </>
  );
};

// ───────────────────────── PENDANT QUE… : écran coupé en deux, le contraste (photo en haut, faits en bas)
export const Pendant: React.FC<{scene: Ex<'pendant'>; c1: string; c2: string}> = ({scene, c1, c2}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const z = interpolate(frame, [0, scene.duration * fps], [1.05, 1.18]);
  const coupe = spring({frame, fps, config: {damping: 14}});
  const lignes = scene.lignes ?? [];
  const per = Math.max(10, Math.floor((scene.duration * fps * 0.5) / Math.max(1, lignes.length)));
  return (
    <>
      <div style={{position: 'absolute', left: 0, right: 0, top: 230, height: 520 * coupe, overflow: 'hidden', borderBottom: `12px solid ${INK}`, backgroundColor: '#2A1240'}}>
        {scene.src ? <Img src={staticFile(scene.src)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${z})`, filter: 'saturate(1.2)'}} /> : null}
        <div style={{position: 'absolute', left: 30, top: 24}}><Sticker couleur={c1} rotate={-3}><span style={{fontFamily: fontTitre, fontWeight: 900, fontSize: 50, color: INK}}>{scene.haut}</span></Sticker></div>
        {scene.credit ? <div style={{position: 'absolute', right: 12, bottom: 8, fontFamily: fontPixel, fontSize: 18, color: '#eee', backgroundColor: 'rgba(0,0,0,0.5)', padding: '2px 6px'}}>© {scene.credit}</div> : null}
      </div>
      <div style={{position: 'absolute', left: 50, right: 50, top: 790, display: 'flex', flexDirection: 'column', gap: 18}}>
        <div><Sticker couleur={c2} rotate={2}><span style={{fontFamily: fontTitre, fontWeight: 900, fontSize: 50, color: INK}}>{scene.bas}</span></Sticker></div>
        {lignes.map((l, i) => {
          const p = spring({frame: frame - 12 - i * per, fps, config: {damping: 10}});
          return (
            <div key={i} style={{opacity: Math.min(1, p * 1.5), transform: `translateX(${(1 - p) * 60}px)`, fontFamily: fontTitre, fontWeight: 900, fontSize: 58, color: '#fff', WebkitTextStroke: `4px ${INK}`, paintOrder: 'stroke fill'}}>{l}</div>
          );
        })}
      </div>
    </>
  );
};
