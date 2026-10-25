// Style « éditorial » : motion design soigné façon médias d'info (pas de pixel art, pas de personnages).
// Voix off seule, sous-titres karaoké propres, typographie serif + grotesque, photos sous licence libre.
import React from 'react';
import '@fontsource/dm-serif-display/400.css';
import '@fontsource/archivo-black/400.css';
import {AbsoluteFill, Easing, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig, OffthreadVideo} from 'remotion';
import {repliques} from './dialogue';
import {Scene, Theme} from './types';
import {H, W} from './ui';

const SERIF = "'DM Serif Display', Georgia, serif";
const GROT = "'Archivo Black', 'Inter', sans-serif";
const SANS = "'Inter', system-ui, sans-serif";

type C = {fond: string; encre: string; accent: string; papier: string};
const couleurs = (t: Theme): C => ({fond: t.fond || '#0E0E12', encre: t.texte || '#F5F2EA', accent: t.accent || '#E63946', papier: t.accent2 || '#F5F2EA'});

const useP = (delai = 0, damping = 18) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  return spring({frame: f - delai, fps, config: {damping, mass: 0.8}});
};

// Mot par mot (révélation du titre)
const Revele: React.FC<{texte: string; taille: number; couleur: string; police?: string; delai?: number; accent?: string; mot?: string}> = ({texte, taille, couleur, police = SERIF, delai = 0, accent, mot}) => {
  const f = useCurrentFrame();
  const mots = texte.split(' ');
  const net = (x: string) => x.toLowerCase().replace(/[^\p{L}\d]/gu, '');
  const forts = new Set((mot ?? '').split(/\s+/).map(net).filter(Boolean));
  return (
    <div style={{display: 'flex', flexWrap: 'wrap', gap: `0 ${taille * 0.25}px`, lineHeight: 1.02}}>
      {mots.map((m, i) => {
        const p = interpolate(f - delai - i * 3, [0, 10], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
        const fort = forts.size > 0 && forts.has(net(m));
        return (
          <span key={i} style={{overflow: 'hidden', display: 'inline-block'}}>
            <span style={{display: 'inline-block', transform: `translateY(${(1 - p) * 110}%)`, fontFamily: police, fontSize: taille, color: fort && accent ? accent : couleur, fontStyle: fort ? 'italic' : 'normal'}}>{m}</span>
          </span>
        );
      })}
    </div>
  );
};

const Kicker: React.FC<{texte?: string; c: C; delai?: number}> = ({texte, c, delai = 0}) => {
  const p = useP(delai);
  if (!texte) return null;
  return (
    <div style={{display: 'flex', alignItems: 'center', gap: 16, opacity: p}}>
      <div style={{width: 60 * p, height: 8, backgroundColor: c.accent}} />
      <span style={{fontFamily: GROT, fontSize: 30, letterSpacing: 4, color: c.accent, textTransform: 'uppercase'}}>{texte}</span>
    </div>
  );
};

// ───────────────────────── Scènes éditoriales
type Ex<T extends Scene['type']> = Extract<Scene, {type: T}>;

const Titre: React.FC<{s: Ex<'ed_titre'>; c: C}> = ({s, c}) => (
  <div style={{position: 'absolute', left: 80, right: 80, top: 420, display: 'flex', flexDirection: 'column', gap: 40}}>
    <Kicker texte={s.kicker} c={c} />
    <Revele texte={s.titre} taille={s.titre.length > 60 ? 92 : 118} couleur={c.encre} delai={4} accent={c.accent} mot={s.mot_fort} />
    {s.sous_titre ? <div style={{fontFamily: SANS, fontWeight: 600, fontSize: 44, color: c.encre, opacity: useP(20) * 0.85, lineHeight: 1.25}}>{s.sous_titre}</div> : null}
  </div>
);

const Chiffre: React.FC<{s: Ex<'ed_chiffre'>; c: C}> = ({s, c}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const n = f >= fps * 1.6 ? s.valeur : interpolate(f, [4, fps * 1.6], [0, s.valeur], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.exp)}); // Easing.exp n'atteint que 99,9 % : valeur exacte à la fin
  const txt = `${s.prefixe ?? ''}${n.toLocaleString('fr-FR', {maximumFractionDigits: s.decimales ?? 0, minimumFractionDigits: s.decimales ?? 0})}${s.suffixe ?? ''}`;
  const trait = useP(fps * 1.2);
  return (
    <div style={{position: 'absolute', left: 80, right: 80, top: 440, display: 'flex', flexDirection: 'column', gap: 26}}>
      <Kicker texte={s.kicker} c={c} />
      <div style={{fontFamily: GROT, fontSize: txt.length > 8 ? 170 : 230, color: c.encre, letterSpacing: -6, lineHeight: 1, fontVariantNumeric: 'tabular-nums'}}>{txt}</div>
      <div style={{width: `${trait * 100}%`, height: 6, backgroundColor: c.accent}} />
      <div style={{fontFamily: SERIF, fontSize: 60, color: c.encre, lineHeight: 1.1, opacity: trait}}>{s.legende}</div>
      {s.source ? <div style={{fontFamily: SANS, fontSize: 26, color: c.encre, opacity: 0.6}}>Source : {s.source}</div> : null}
    </div>
  );
};

const Citation: React.FC<{s: Ex<'ed_citation'>; c: C}> = ({s, c}) => {
  const p = useP(2);
  return (
    <div style={{position: 'absolute', left: 80, right: 80, top: 380, display: 'flex', flexDirection: 'column', gap: 30}}>
      <div style={{fontFamily: SERIF, fontSize: 260, color: c.accent, lineHeight: 0.6, height: 120, transform: `scale(${p})`, transformOrigin: 'left top'}}>“</div>
      <Revele texte={s.texte} taille={s.texte.length > 90 ? 64 : 80} couleur={c.encre} delai={6} />
      <div style={{fontFamily: GROT, fontSize: 32, color: c.accent, letterSpacing: 2, textTransform: 'uppercase', opacity: useP(24)}}>— {s.auteur}</div>
    </div>
  );
};

const Photo: React.FC<{s: Ex<'ed_photo'>; c: C}> = ({s, c}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const z = interpolate(f, [0, s.duration * fps], [1.1, 1.25]);
  const volet = interpolate(f, [0, 14], [0, 100], {extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  return (
    <AbsoluteFill>
      <div style={{position: 'absolute', inset: 0, clipPath: `inset(0 ${100 - volet}% 0 0)`}}>
        {s.src && /\.(mp4|webm|mov)$/i.test(s.src) ? (
          <OffthreadVideo src={staticFile(s.src)} muted startFrom={Math.round((s.debut_s ?? 0) * fps)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${1.02 + (z - 1.1) * 0.3})`}} />
        ) : s.src ? <Img src={staticFile(s.src)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${z})`}} /> : <div style={{width: '100%', height: '100%', backgroundColor: '#333'}} />}
        <div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0) 30%, rgba(0,0,0,0) 45%, rgba(0,0,0,0.85) 100%)'}} />
      </div>
      <div style={{position: 'absolute', left: 80, right: 80, top: 300, display: 'flex', flexDirection: 'column', gap: 24}}>
        <Kicker texte={s.kicker} c={{...c, accent: c.accent}} delai={8} />
        {s.titre ? <Revele texte={s.titre} taille={84} couleur="#FFFFFF" delai={10} /> : null}
      </div>
      <div style={{position: 'absolute', right: 30, top: 230, fontFamily: SANS, fontSize: 20, color: '#ddd', backgroundColor: 'rgba(0,0,0,0.45)', padding: '4px 10px'}}>© {s.credit}</div>
    </AbsoluteFill>
  );
};

const Liste: React.FC<{s: Ex<'ed_liste'>; c: C}> = ({s, c}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const per = Math.max(10, Math.floor((s.duration * fps * 0.6) / Math.max(1, s.points.length)));
  return (
    <div style={{position: 'absolute', left: 80, right: 80, top: 360, display: 'flex', flexDirection: 'column', gap: 34}}>
      <Kicker texte={s.kicker} c={c} />
      {s.titre ? <Revele texte={s.titre} taille={76} couleur={c.encre} delai={4} /> : null}
      {s.points.map((pt, i) => {
        const p = interpolate(f - 14 - i * per, [0, 12], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
        return (
          <div key={i} style={{display: 'flex', gap: 26, alignItems: 'baseline', opacity: p, transform: `translateX(${(1 - p) * -40}px)`}}>
            <span style={{fontFamily: GROT, fontSize: 64, color: c.accent, minWidth: 70, fontVariantNumeric: 'tabular-nums'}}>{String(i + 1).padStart(2, '0')}</span>
            <span style={{fontFamily: SANS, fontWeight: 700, fontSize: 50, color: c.encre, lineHeight: 1.15}}>{pt}</span>
          </div>
        );
      })}
    </div>
  );
};

const Versus: React.FC<{s: Ex<'ed_versus'>; c: C}> = ({s, c}) => {
  const pg = useP(4);
  const pd = useP(14);
  const bloc = (x: {label: string; valeur: string}, p: number, fort: boolean) => (
    <div style={{flex: 1, borderTop: `8px solid ${fort ? c.accent : c.encre}`, paddingTop: 24, opacity: p, transform: `translateY(${(1 - p) * 50}px)`}}>
      <div style={{fontFamily: GROT, fontSize: 30, letterSpacing: 3, color: fort ? c.accent : c.encre, textTransform: 'uppercase'}}>{x.label}</div>
      <div style={{fontFamily: GROT, fontSize: x.valeur.length > 7 ? 92 : 120, color: c.encre, letterSpacing: -3, marginTop: 10}}>{x.valeur}</div>
    </div>
  );
  return (
    <div style={{position: 'absolute', left: 80, right: 80, top: 400, display: 'flex', flexDirection: 'column', gap: 50}}>
      <Kicker texte={s.kicker} c={c} />
      {s.titre ? <Revele texte={s.titre} taille={80} couleur={c.encre} delai={2} /> : null}
      <div style={{display: 'flex', gap: 40}}>
        {bloc(s.gauche, pg, false)}
        {bloc(s.droite, pd, true)}
      </div>
    </div>
  );
};


// Reconstitution dessinée d'une allocution télévisée (salon doré, drapeaux, pupitre, bandeau TV) :
// le texte exact du discours défile en bandeau. Aucune image tierce.
const Allocution: React.FC<{s: Ex<'ed_allocution'>; c: C}> = ({s, c}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const zoom = interpolate(f, [0, s.duration * fps], [1, 1.12]);
  const n = Math.floor(interpolate(f, [8, 8 + s.texte.length * 0.9], [0, s.texte.length], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  const live = Math.floor(f / 15) % 2 === 0;
  const drap = (x: number, couleurs: string[], eu = false) => (
    <g transform={`translate(${x} 520)`}>
      <rect x={0} y={0} width={10} height={760} fill="#C9A227" />
      <path d={`M10 20 Q${110 + Math.sin(f / 9) * 12} ${60} 210 30 L210 330 Q${110 + Math.sin(f / 9 + 1) * 12} 360 10 330 Z`} fill={eu ? '#1F3FA0' : couleurs[1]} />
      {eu ? null : <path d={`M10 20 Q45 30 75 26 L75 336 Q45 340 10 330 Z`} fill={couleurs[0]} />}
      {eu ? null : <path d={`M145 26 Q180 26 210 30 L210 330 Q180 340 145 338 Z`} fill={couleurs[2]} />}
      {eu ? Array.from({length: 12}).map((_, k) => <circle key={k} cx={110 + Math.cos((k / 12) * 6.283) * 60} cy={180 + Math.sin((k / 12) * 6.283) * 60} r={7} fill="#F2C200" />) : null}
    </g>
  );
  return (
    <AbsoluteFill style={{backgroundColor: '#1B1A2E'}}>
      <AbsoluteFill style={{transform: `scale(${zoom})`, transformOrigin: '50% 45%'}}>
        <svg viewBox="0 0 1080 1920" width={W} height={H}>
          <defs>
            <linearGradient id="mur" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#E9DDBE" /><stop offset="1" stopColor="#B9A57A" /></linearGradient>
            <radialGradient id="lustre" cx="0.5" cy="0.2" r="0.7"><stop offset="0" stopColor="#FFF6D8" stopOpacity="0.55" /><stop offset="1" stopColor="#FFF6D8" stopOpacity="0" /></radialGradient>
          </defs>
          <rect x={0} y={0} width={1080} height={1920} fill="url(#mur)" />
          {[90, 400, 710].map((x) => <rect key={x} x={x} y={260} width={280} height={900} rx={8} fill="none" stroke="#C9A227" strokeWidth={10} />)}
          {[110, 420, 730].map((x) => <rect key={x} x={x} y={280} width={240} height={860} rx={4} fill="none" stroke="#D9BF6A" strokeWidth={3} />)}
          <rect x={0} y={1160} width={1080} height={40} fill="#C9A227" />
          {drap(80, ['#1F3FA0', '#FFFFFF', '#D7263D'])}
          {drap(790, [], true)}
          {/* silhouette de dos : l'orateur n'est pas représenté */}
          <rect x={0} y={0} width={1080} height={1920} fill="url(#lustre)" />
          <path d="M300 1250 L780 1250 L740 1560 L340 1560 Z" fill="#3A2A1A" stroke="#1E140C" strokeWidth={6} />
          <rect x={290} y={1230} width={500} height={34} rx={6} fill="#5A4026" />
          <circle cx={540} cy={1300} r={34} fill="#C9A227" />
          <rect x={0} y={1560} width={1080} height={360} fill="#2A1E14" />
        </svg>
      </AbsoluteFill>
      {/* habillage TV */}
      <div style={{position: 'absolute', left: 60, top: 300, display: 'flex', gap: 14, alignItems: 'center'}}>
        <span style={{fontFamily: GROT, fontSize: 30, color: '#fff', backgroundColor: c.accent, padding: '6px 14px'}}>{live ? '● ' : '  '}ALLOCUTION</span>
        <span style={{fontFamily: SANS, fontWeight: 700, fontSize: 28, color: '#141414', backgroundColor: '#fff', padding: '6px 14px'}}>{s.quand}</span>
      </div>
      <div style={{position: 'absolute', left: 40, right: 40, top: 1000, backgroundColor: 'rgba(14,14,18,0.92)', borderLeft: `14px solid ${c.accent}`, padding: '26px 30px'}}>
        <div style={{fontFamily: SERIF, fontSize: 62, color: '#fff', lineHeight: 1.08}}>« {s.texte.slice(0, n)}{n < s.texte.length ? '▌' : ' »'}</div>
        <div style={{fontFamily: GROT, fontSize: 26, color: c.accent, marginTop: 14, letterSpacing: 2, textTransform: 'uppercase'}}>— {s.auteur}</div>
      </div>
      <div style={{position: 'absolute', right: 40, top: 235, fontFamily: SANS, fontSize: 20, color: '#333', backgroundColor: 'rgba(255,255,255,0.8)', padding: '4px 10px'}}>Reconstitution · texte exact du discours</div>
    </AbsoluteFill>
  );
};

export const SceneEditoriale: React.FC<{scene: Scene; theme: Theme}> = ({scene, theme}) => {
  const c = couleurs(theme);
  switch (scene.type) {
    case 'ed_titre':
      return <Titre s={scene} c={c} />;
    case 'ed_chiffre':
      return <Chiffre s={scene} c={c} />;
    case 'ed_citation':
      return <Citation s={scene} c={c} />;
    case 'ed_photo':
      return <Photo s={scene} c={c} />;
    case 'ed_liste':
      return <Liste s={scene} c={c} />;
    case 'ed_versus':
      return <Versus s={scene} c={c} />;
    case 'ed_allocution':
      return <Allocution s={scene} c={c} />;
    default:
      return null;
  }
};

// ───────────────────────── Cadre éditorial : fond, marque, barre de progression, sous-titres karaoké
export const CadreEditorial: React.FC<{scene: Scene; theme: Theme; index: number; total: number; children: React.ReactNode}> = ({scene, theme, index, total, children}) => {
  const c = couleurs(theme);
  const f = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const t = f / fps;
  const rs = repliques(scene);
  const actif = [...rs].reverse().find((r) => t >= (r.debut ?? 0) - 0.05);
  const mots = actif ? actif.texte.split(/\s+/) : [];
  const d0 = actif?.debut ?? 0;
  const d1 = actif?.fin ?? d0 + 2;
  const courant = Math.min(mots.length - 1, Math.floor(((t - d0) / Math.max(0.3, d1 - d0)) * mots.length));
  const bloc = Math.max(0, Math.floor(courant / 6));
  const vis = mots.slice(bloc * 6, bloc * 6 + 6);
  const entree = interpolate(f, [0, 10], [0, 1], {extrapolateRight: 'clamp'});
  const surPhoto = scene.type === 'ed_photo' || scene.type === 'ed_allocution';
  return (
    <AbsoluteFill style={{backgroundColor: c.fond}}>
      {/* grain + lignes de grille fines */}
      <AbsoluteFill style={{backgroundImage: `linear-gradient(${c.encre}0A 1px, transparent 1px), linear-gradient(90deg, ${c.encre}0A 1px, transparent 1px)`, backgroundSize: '90px 90px', opacity: 0.6}} />
      <AbsoluteFill style={{opacity: entree, transform: `translateY(${(1 - entree) * 30}px)`}}>{children}</AbsoluteFill>
      {/* marque + date */}
      <div style={{position: 'absolute', left: 80, top: 160, display: 'flex', alignItems: 'center', gap: 18}}>
        <span style={{fontFamily: GROT, fontSize: 34, color: c.fond, backgroundColor: c.encre, padding: '4px 12px', letterSpacing: 1}}>DÉCODÉ</span>
        <span style={{fontFamily: SANS, fontWeight: 600, fontSize: 26, color: c.encre, opacity: 0.75, textTransform: 'uppercase', letterSpacing: 2}}>{theme.bandeau ?? ''}</span>
      </div>
      {/* progression de la vidéo (segments) */}
      <div style={{position: 'absolute', left: 80, right: 80, top: 225, display: 'flex', gap: 8}}>
        {Array.from({length: total}).map((_, i) => (
          <div key={i} style={{flex: 1, height: 5, backgroundColor: `${c.encre}33`}}>
            <div style={{height: '100%', width: i < index ? '100%' : i === index ? `${(f / durationInFrames) * 100}%` : '0%', backgroundColor: c.accent}} />
          </div>
        ))}
      </div>
      {/* sous-titres */}
      <div style={{position: 'absolute', left: 70, right: 70, top: 1380, display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '6px 14px'}}>
        {vis.map((m, i) => {
          const idx = bloc * 6 + i;
          return (
            <span key={idx} style={{fontFamily: GROT, fontSize: 58, textTransform: 'uppercase', color: idx === courant ? '#FFFFFF' : surPhoto ? '#FFFFFF' : c.encre, backgroundColor: idx === courant ? c.accent : 'transparent', padding: '0 10px', WebkitTextStroke: idx === courant || !surPhoto ? '0' : '2px rgba(0,0,0,0.6)', paintOrder: 'stroke fill', opacity: idx <= courant ? 1 : 0.5}}>
              {m}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

export {W, H};
