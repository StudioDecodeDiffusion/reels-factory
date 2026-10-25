// Style « pixel doc » (rétro-ingénierie d'archive66.tv, 80 k vues) : pixel art détaillé centré sur fond chaud vignetté,
// grille fine + coins de viseur, titres en police pixel avec mot-clé jaune, mécanismes animés, sous-titres karaoké en bas.
import React from 'react';
import {AbsoluteFill, Easing, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {repliques} from './dialogue';
import {Scene, Theme} from './types';
import {fontPixel} from './fx';

const JAUNE = '#FFD23F';
const SANS = "'Inter', system-ui, sans-serif";
type Ex<T extends string> = Extract<Scene, {type: T}>;
type C = {fond: string; accent: string; texte: string};
const couleurs = (t: Theme): C => ({fond: t.fond || '#2A170C', accent: t.accent || JAUNE, texte: t.texte || '#FFFFFF'});

const usePop = (delai = 0) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  return spring({frame: f - delai, fps, config: {damping: 12, mass: 0.6}});
};

// Titre pixel, mot(s)-clé(s) en jaune, apparition lettre par lettre
const TitrePixel: React.FC<{texte?: string; mot?: string; c: C; taille?: number; top?: number}> = ({texte, mot, c, taille = 74, top = 300}) => {
  const f = useCurrentFrame();
  if (!texte) return null;
  const net = (x: string) => x.toLowerCase().replace(/[^\p{L}\d%€]/gu, '');
  const forts = new Set((mot ?? '').split(/\s+/).map(net).filter(Boolean));
  const n = Math.floor(interpolate(f, [2, 2 + texte.length * 0.7], [0, texte.length], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  let vu = 0;
  return (
    <div style={{position: 'absolute', left: 70, right: 70, top, textAlign: 'center', fontFamily: fontPixel, fontSize: taille, lineHeight: 1.12, textTransform: 'uppercase', textShadow: '6px 6px 0 rgba(0,0,0,0.55)'}}>
      {texte.split(' ').map((m, i) => {
        const debut = vu;
        vu += m.length + 1;
        const vis = m.slice(0, Math.max(0, n - debut));
        return (
          <span key={i} style={{color: forts.has(net(m)) ? c.accent : c.texte}}>
            {vis}
            {i < texte.split(' ').length - 1 ? ' ' : ''}
          </span>
        );
      })}
    </div>
  );
};

// Image pixel art (générée puis pixelisée au rendu) qui flotte, avec balayage d'apparition
const ObjetPixel: React.FC<{src?: string; taille?: number; y?: number; x?: number; delai?: number; c: C}> = ({src, taille = 640, y = 760, x = 540, delai = 4, c}) => {
  const f = useCurrentFrame();
  const p = usePop(delai);
  const balayage = interpolate(f, [delai, delai + 14], [0, 100], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const flotte = Math.sin(f / 18) * 10;
  return (
    <div style={{position: 'absolute', left: x - taille / 2, top: y - taille / 2 + flotte, width: taille, height: taille, transform: `scale(${0.85 + 0.15 * p})`, clipPath: `inset(${100 - balayage}% 0 0 0)`, filter: 'drop-shadow(0 18px 0 rgba(0,0,0,0.35))'}}>
      {src ? (
        <Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'contain', imageRendering: 'pixelated'}} />
      ) : (
        <svg viewBox="0 0 16 16" width={taille} height={taille} shapeRendering="crispEdges">
          <rect x={3} y={3} width={10} height={10} fill={c.accent} />
          <rect x={5} y={5} width={6} height={6} fill="#000" opacity={0.3} />
        </svg>
      )}
    </div>
  );
};

const Etiquette: React.FC<{texte?: string; y: number; c: C; delai?: number}> = ({texte, y, c, delai = 12}) => {
  const p = usePop(delai);
  if (!texte) return null;
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: y, display: 'flex', justifyContent: 'center', transform: `scale(${p})`}}>
      <span style={{fontFamily: fontPixel, fontSize: 34, color: '#1A1208', backgroundColor: c.accent, padding: '8px 18px', border: '4px solid #1A1208', boxShadow: '6px 6px 0 #1A1208'}}>{texte}</span>
    </div>
  );
};

// Pièces qui circulent d'une boîte à l'autre : mécanisme « où va l'argent »
const Flux: React.FC<{s: Ex<'pd_flux'>; c: C}> = ({s, c}) => {
  const f = useCurrentFrame();
  const boite = (x: number, label: string, src?: string, d = 0) => (
    <div style={{position: 'absolute', left: x - 190, top: 620, width: 380, textAlign: 'center'}}>
      <div style={{height: 380, position: 'relative'}}><ObjetPixel src={src} taille={330} x={190} y={190} delai={d} c={c} /></div>
      <div style={{fontFamily: fontPixel, fontSize: 36, color: c.texte, marginTop: 10, textTransform: 'uppercase'}}>{label}</div>
    </div>
  );
  return (
    <>
      {boite(260, s.de.label, s.de.src, 2)}
      {boite(820, s.vers.label, s.vers.src, 6)}
      {Array.from({length: 7}).map((_, k) => {
        const t = ((f - 10 - k * 6) % 42) / 42;
        if (f < 10 + k * 6) return null;
        const x = interpolate(t, [0, 1], [380, 700]);
        const y = 760 - Math.sin(t * Math.PI) * 170;
        return (
          <svg key={k} viewBox="0 0 8 8" width={56} height={56} shapeRendering="crispEdges" style={{position: 'absolute', left: x - 28, top: y - 28}}>
            <rect x={2} y={0} width={4} height={8} fill="#C98A00" />
            <rect x={0} y={2} width={8} height={4} fill="#C98A00" />
            <rect x={1} y={1} width={6} height={6} fill={JAUNE} />
            <rect x={3} y={2} width={2} height={4} fill="#C98A00" />
          </svg>
        );
      })}
      {s.montant ? <Etiquette texte={s.montant} y={1230} c={c} delai={14} /> : null}
    </>
  );
};

// Compteur arcade + barre qui se remplit
const Chiffre: React.FC<{s: Ex<'pd_chiffre'>; c: C}> = ({s, c}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = interpolate(f, [6, 6 + fps * 1.4], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const v = (s.valeur * p).toLocaleString('fr-FR', {minimumFractionDigits: s.decimales ?? 0, maximumFractionDigits: s.decimales ?? 0});
  return (
    <>
      <div style={{position: 'absolute', left: 0, right: 0, top: 640, textAlign: 'center', fontFamily: fontPixel, fontSize: 150, color: c.accent, textShadow: '8px 8px 0 rgba(0,0,0,0.6)'}}>
        {s.prefixe ?? ''}
        {v}
        {s.suffixe ?? ''}
      </div>
      <div style={{position: 'absolute', left: 140, right: 140, top: 880, height: 46, border: `6px solid ${c.texte}`, padding: 6}}>
        <div style={{height: '100%', width: `${Math.round(p * (s.jauge ?? 100))}%`, background: `repeating-linear-gradient(90deg, ${c.accent} 0 26px, transparent 26px 32px)`}} />
      </div>
      <div style={{position: 'absolute', left: 90, right: 90, top: 970, textAlign: 'center', fontFamily: SANS, fontWeight: 800, fontSize: 44, color: c.texte}}>{s.legende}</div>
      {s.source ? <div style={{position: 'absolute', left: 90, right: 90, top: 1060, textAlign: 'center', fontFamily: SANS, fontSize: 24, color: c.texte, opacity: 0.6}}>Source : {s.source}</div> : null}
    </>
  );
};

const Versus: React.FC<{s: Ex<'pd_versus'>; c: C}> = ({s, c}) => {
  const f = useCurrentFrame();
  const col = (x: number, d: {label: string; valeur: string; src?: string}, delai: number, fort: boolean) => (
    <div style={{position: 'absolute', left: x - 230, top: 600, width: 460, textAlign: 'center'}}>
      <div style={{height: 360, position: 'relative'}}><ObjetPixel src={d.src} taille={320} x={230} y={180} delai={delai} c={c} /></div>
      <div style={{fontFamily: fontPixel, fontSize: 32, color: c.texte, textTransform: 'uppercase', marginTop: 8}}>{d.label}</div>
      <div style={{fontFamily: fontPixel, fontSize: 64, color: fort ? c.accent : c.texte, marginTop: 10, opacity: interpolate(f, [delai + 8, delai + 14], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>{d.valeur}</div>
    </div>
  );
  return (
    <>
      {col(290, s.gauche, 4, false)}
      {col(790, s.droite, 10, true)}
      <div style={{position: 'absolute', left: 500, top: 760, fontFamily: fontPixel, fontSize: 60, color: c.accent}}>VS</div>
    </>
  );
};

const Jauge: React.FC<{s: Ex<'pd_jauge'>; c: C}> = ({s, c}) => {
  const f = useCurrentFrame();
  const v = interpolate(f, [6, 40], [0, s.valeur], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.back(1.4))});
  const a = -120 + (v / 100) * 240 + Math.sin(f / 3) * (v > 80 ? 3 : 0);
  return (
    <>
      <svg viewBox="0 0 200 130" width={760} height={494} style={{position: 'absolute', left: 160, top: 560}} shapeRendering="crispEdges">
        {Array.from({length: 24}).map((_, k) => {
          const ang = ((-120 + k * 10.4) * Math.PI) / 180;
          const col = k < 8 ? '#3FA34D' : k < 16 ? JAUNE : '#E3242B';
          return <rect key={k} x={100 + Math.sin(ang) * 80 - 4} y={110 - Math.cos(ang) * 80 - 4} width={8} height={8} fill={col} />;
        })}
        <g transform={`rotate(${a} 100 110)`}>
          <rect x={98} y={40} width={4} height={70} fill={c.texte} />
        </g>
        <rect x={92} y={102} width={16} height={16} fill={c.accent} />
      </svg>
      <div style={{position: 'absolute', left: 0, right: 0, top: 1080, textAlign: 'center', fontFamily: fontPixel, fontSize: 40, color: c.texte, textTransform: 'uppercase'}}>{s.legende}</div>
    </>
  );
};

const Tampon: React.FC<{s: Ex<'pd_tampon'>; c: C}> = ({s, c}) => {
  const f = useCurrentFrame();
  const p = spring({frame: f - 14, fps: 30, config: {damping: 9, mass: 0.5}});
  return (
    <>
      <ObjetPixel src={s.src} c={c} />
      <div style={{position: 'absolute', left: 0, right: 0, top: 700, display: 'flex', justifyContent: 'center', transform: `rotate(-12deg) scale(${2.2 - 1.2 * p})`, opacity: p}}>
        <span style={{fontFamily: fontPixel, fontSize: 96, color: '#E3242B', border: '12px solid #E3242B', padding: '10px 34px', background: 'rgba(0,0,0,0.25)'}}>{s.tampon}</span>
      </div>
    </>
  );
};

export const ScenePixelDoc: React.FC<{scene: Scene; theme: Theme}> = ({scene, theme}) => {
  const c = couleurs(theme);
  const s = scene as Scene & {titre?: string; mot_fort?: string};
  const titre = <TitrePixel texte={s.titre} mot={s.mot_fort} c={c} />;
  switch (scene.type) {
    case 'pd_objet':
      return (
        <>
          {titre}
          <ObjetPixel src={scene.src} c={c} />
          <Etiquette texte={scene.etiquette} y={1130} c={c} />
        </>
      );
    case 'pd_flux':
      return <>{titre}<Flux s={scene} c={c} /></>;
    case 'pd_chiffre':
      return <>{titre}<Chiffre s={scene} c={c} /></>;
    case 'pd_versus':
      return <>{titre}<Versus s={scene} c={c} /></>;
    case 'pd_jauge':
      return <>{titre}<Jauge s={scene} c={c} /></>;
    case 'pd_tampon':
      return <>{titre}<Tampon s={scene} c={c} /></>;
    default:
      return titre;
  }
};

// Mouvements relevés image par image (25/10, captures toutes les 20 ms) :
// - archive66 : sortie « zoom + flou » 0,2 s en accélération (×1→×1,6, flou 0→18 px), entrée floue 0,13 s qui se
//   resserre ; le cadre (grille, coins, sous-titres) reste fixe, seul le contenu bouge.
// - phyzolof : poussée lente continue sur le sujet (Ken Burns) ; science_in_8bit : coupe sèche en gros plan au milieu
//   d'un plan long (changement visuel toutes les 2-3 s) ; byte.sized.engineering : rayons de vitesse en fond et
//   flash blanc 80 % → 0 en 0,2 s à l'impact (versus, tampon).
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const MouvementPixelDoc: React.FC<{type: string; children: React.ReactNode}> = ({type, children}) => {
  const f = useCurrentFrame();
  const {durationInFrames: d, fps} = useVideoConfig();
  const entree = interpolate(f, [0, 4], [1, 0], {...clamp, easing: Easing.out(Easing.cubic)});
  const sortie = interpolate(f, [d - 6, d], [0, 1], {...clamp, easing: Easing.in(Easing.cubic)});
  const poussee = interpolate(f, [0, d], [1, 1.05], clamp);
  const grosPlan = d > fps * 3.5 && f >= Math.round(d / 2) && !['pd_chiffre', 'pd_jauge'].includes(type) ? 1.12 : 1;
  const echelle = poussee * grosPlan * (1 + 0.25 * entree + 0.6 * sortie);
  return (
    <AbsoluteFill style={{transform: `scale(${echelle})`, transformOrigin: '50% 48%', filter: `blur(${14 * entree + 18 * sortie}px)`}}>
      {children}
    </AbsoluteFill>
  );
};

const Rayons: React.FC<{c: C}> = ({c}) => {
  const f = useCurrentFrame();
  return (
    <svg width={1080} height={1920} style={{position: 'absolute', inset: 0, opacity: 0.35}}>
      {Array.from({length: 40}, (_, i) => {
        const a = (i / 40) * Math.PI * 2;
        const r0 = 180 + ((f * 18 + i * 97) % 700);
        return <line key={i} x1={540 + Math.cos(a) * r0} y1={820 + Math.sin(a) * r0} x2={540 + Math.cos(a) * (r0 + 60)}
          y2={820 + Math.sin(a) * (r0 + 60)} stroke={i % 3 ? c.accent : '#E5133A'} strokeWidth={10} />;
      })}
    </svg>
  );
};

const Flash: React.FC<{a: number}> = ({a}) => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{background: '#FFF', opacity: interpolate(f, [a, a + 1, a + 7], [0, 0.8, 0], clamp), pointerEvents: 'none'}} />;
};

// Cadre commun : fond chaud vignetté, grille, coins de viseur, marque, sous-titres karaoké
export const CadrePixelDoc: React.FC<{scene: Scene; theme: Theme; index: number; total: number; children: React.ReactNode}> = ({scene, theme, index, total, children}) => {
  const c = couleurs(theme);
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = f / fps;
  const rs = repliques(scene);
  const actif = [...rs].reverse().find((r) => t >= (r.debut ?? 0) - 0.05);
  const mots = actif ? actif.texte.split(/\s+/) : [];
  const d0 = actif?.debut ?? 0;
  const d1 = actif?.fin ?? d0 + 2;
  const courant = Math.min(mots.length - 1, Math.floor(((t - d0) / Math.max(0.3, d1 - d0)) * mots.length));
  const bloc = Math.max(0, Math.floor(courant / 5));
  const vis = mots.slice(bloc * 5, bloc * 5 + 5);
  const coin = (st: React.CSSProperties) => <div style={{position: 'absolute', width: 60, height: 60, borderColor: 'rgba(255,255,255,0.35)', borderStyle: 'solid', borderWidth: 0, ...st}} />;
  return (
    <AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 42%, ${c.fond}EE 0%, ${c.fond} 45%, #0B0603 100%)`}}>
      <AbsoluteFill style={{backgroundImage: 'linear-gradient(rgba(255,255,255,0.045) 2px, transparent 2px), linear-gradient(90deg, rgba(255,255,255,0.045) 2px, transparent 2px)', backgroundSize: '60px 60px'}} />
      <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 45%, rgba(255,190,90,0.18), transparent 55%)'}} />
      {coin({left: 60, top: 230, borderLeftWidth: 6, borderTopWidth: 6})}
      {coin({right: 60, top: 230, borderRightWidth: 6, borderTopWidth: 6})}
      {coin({left: 60, top: 1300, borderLeftWidth: 6, borderBottomWidth: 6})}
      {coin({right: 60, top: 1300, borderRightWidth: 6, borderBottomWidth: 6})}
      <div style={{position: 'absolute', left: 80, top: 170, fontFamily: fontPixel, fontSize: 26, color: 'rgba(255,255,255,0.75)', letterSpacing: 2}}>DÉCODÉ · {theme.bandeau ?? ''}</div>
      <div style={{position: 'absolute', right: 80, top: 170, fontFamily: fontPixel, fontSize: 26, color: c.accent}}>{String(index + 1).padStart(2, '0')}/{String(total).padStart(2, '0')}</div>
      {['pd_versus', 'pd_chiffre'].includes(scene.type) ? <Rayons c={c} /> : null}
      <MouvementPixelDoc type={scene.type}>{children}</MouvementPixelDoc>
      {scene.type === 'pd_versus' ? <Flash a={12} /> : scene.type === 'pd_tampon' ? <Flash a={16} /> : null}
      <AbsoluteFill style={{backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.12) 0 2px, transparent 2px 5px)', mixBlendMode: 'multiply', pointerEvents: 'none'}} />
      <div style={{position: 'absolute', left: 70, right: 70, top: 1390, display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '4px 16px'}}>
        {vis.map((m, i) => {
          const idx = bloc * 5 + i;
          return (
            <span key={idx} style={{fontFamily: SANS, fontWeight: 900, fontSize: 60, color: idx === courant ? c.accent : '#FFFFFF', textShadow: '4px 4px 0 rgba(0,0,0,0.8)', opacity: idx <= courant ? 1 : 0.45}}>
              {m}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
