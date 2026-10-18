// Mises en page alternatives (habillages) + nouvelles scènes + transitions variées.
// Objectif : que chaque vidéo ait un « fonctionnement » visuel différent (JT, messagerie, quiz, plein écran…).
import React from 'react';
import {AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {Personnage, repliques, Replique, Qui} from './dialogue';
import {fontPixel, fontTitre, INK, Sticker, encrePour} from './fx';
import {Scene} from './types';
import {H, W} from './ui';

export type MiseEnPage = 'duo' | 'jt' | 'chat' | 'quiz' | 'plein_ecran';
type Tenues = {narrateur?: string; mascotte?: string};

const useRepliques = (scene: Scene) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const rs = repliques(scene);
  const actif = [...rs].reverse().find((r) => t >= (r.debut ?? 0) - 0.05);
  const derniere = (qui: Qui) => [...rs].reverse().find((r) => r.qui === qui && (r.debut ?? 0) <= t);
  const expr = (qui: Qui) => derniere(qui)?.expression ?? (qui === 'mascotte' ? 'content' : 'neutre');
  const parle = (qui: Qui) => !!actif && actif.qui === qui && t <= (actif.fin ?? 0);
  return {t, rs, actif, expr, parle, frame};
};

// Sous-titre karaoké compact (pour les habillages sans bulle)
const SousTitre: React.FC<{r?: Replique; t: number; couleur: string; top: number}> = ({r, t, couleur, top}) => {
  if (!r) return null;
  const mots = r.texte.split(/\s+/).filter(Boolean);
  const d = r.debut ?? 0;
  const f = r.fin ?? d + 2;
  const courant = Math.min(mots.length - 1, Math.floor(((t - d) / Math.max(0.3, f - d)) * mots.length));
  const bloc = Math.max(0, Math.floor(courant / 7));
  const vis = mots.slice(bloc * 7, bloc * 7 + 7);
  return (
    <div style={{position: 'absolute', left: 40, right: 40, top, display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '4px 12px'}}>
      {vis.map((m, i) => {
        const idx = bloc * 7 + i;
        return (
          <span key={idx} style={{fontFamily: fontTitre, fontWeight: 900, fontSize: 54, color: idx === courant ? INK : '#fff', backgroundColor: idx === courant ? couleur : 'transparent', padding: '0 8px', borderRadius: 8, WebkitTextStroke: idx === courant ? '0' : `3px ${INK}`, paintOrder: 'stroke fill', opacity: idx <= courant ? 1 : 0.55}}>
            {m}
          </span>
        );
      })}
    </div>
  );
};

// ───────────────────────── JT : plateau télé pixel
export const HabillageJT: React.FC<{scene: Scene; tenues: Tenues; accent: string; titre?: string; children: React.ReactNode}> = ({scene, tenues, accent, titre, children}) => {
  const {t, actif, expr, parle, frame} = useRepliques(scene);
  const defile = (frame * 6) % 2400;
  const live = Math.floor(frame / 18) % 2 === 0;
  return (
    <AbsoluteFill style={{background: `linear-gradient(180deg, #0B1026 0%, #1B1F3B 55%, #0B1026 100%)`}}>
      {/* lumières de plateau */}
      {[0, 1, 2, 3, 4].map((i) => (
        <div key={i} style={{position: 'absolute', top: 0, left: 80 + i * 220, width: 140, height: 900, background: `linear-gradient(180deg, ${accent}33, transparent)`, transform: `skewX(${(i - 2) * 8}deg)`, opacity: 0.6 + 0.2 * Math.sin(frame / 20 + i)}} />
      ))}
      {/* écran géant derrière la présentatrice */}
      <div style={{position: 'absolute', left: 60, top: 230, width: W - 120, height: 980, border: `10px solid ${INK}`, borderRadius: 18, overflow: 'hidden', boxShadow: `0 0 0 6px ${accent}, 16px 16px 0 ${INK}`}}>
        <div style={{position: 'absolute', left: 22, top: -240, width: W, height: H, transform: 'scale(0.82)', transformOrigin: '0 0'}}>{children}</div>
      </div>
      <div style={{position: 'absolute', top: 160, right: 70, fontFamily: fontPixel, fontSize: 34, color: '#fff', backgroundColor: '#E5133A', padding: '6px 16px', opacity: live ? 1 : 0.5, border: `4px solid ${INK}`}}>● EN DIRECT</div>
      {/* bureau + présentatrice */}
      <div style={{position: 'absolute', left: 0, top: 1060, width: 600, height: 420}}>
        <div style={{position: 'absolute', left: -20, top: 0, transform: 'scale(0.82)', transformOrigin: '0 0'}}>
          <div style={{position: 'relative', width: W, height: H, top: -980}}>
            <Personnage qui="narrateur" expression={expr('narrateur')} parle={parle('narrateur')} tenue={scene.tenue_narrateur ?? tenues.narrateur} x={110} entree={2} />
          </div>
        </div>
      </div>
      <div style={{position: 'absolute', left: 30, top: 1370, width: 560, height: 100, backgroundColor: accent, border: `8px solid ${INK}`, boxShadow: `10px 10px 0 ${INK}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: fontPixel, fontSize: 40, color: INK}}>DÉCODÉ INFO</div>
      {/* Déco en duplex */}
      <div style={{position: 'absolute', right: 40, top: 1110, width: 400, height: 340, border: `8px solid ${INK}`, backgroundColor: '#2EC4B6', overflow: 'hidden', boxShadow: `10px 10px 0 ${INK}`}}>
        <div style={{position: 'absolute', left: -560, top: -1090, width: W, height: H, transform: 'scale(0.85)', transformOrigin: '1000px 1250px'}}>
          <Personnage qui="mascotte" expression={expr('mascotte')} parle={parle('mascotte')} tenue={scene.tenue_mascotte ?? tenues.mascotte} x={700} entree={6} />
        </div>
        <div style={{position: 'absolute', left: 0, bottom: 0, right: 0, backgroundColor: INK, color: '#fff', fontFamily: fontPixel, fontSize: 24, padding: '4px 10px'}}>DUPLEX · DÉCO</div>
      </div>
      {/* sous-titres + bandeau FLASH défilant */}
      <SousTitre r={actif} t={t} couleur={accent} top={1490} />
      <div style={{position: 'absolute', left: 0, right: 0, top: 1640, height: 86, backgroundColor: '#fff', borderTop: `6px solid ${INK}`, borderBottom: `6px solid ${INK}`, overflow: 'hidden'}}>
        <div style={{position: 'absolute', left: 0, top: 0, bottom: 0, width: 210, backgroundColor: '#E5133A', color: '#fff', fontFamily: fontPixel, fontSize: 40, display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 2}}>FLASH</div>
        <div style={{position: 'absolute', left: 230 - defile, top: 14, whiteSpace: 'nowrap', fontFamily: fontTitre, fontWeight: 800, fontSize: 44, color: INK}}>
          {`${titre ?? ''}   ★   ${titre ?? ''}   ★   ${titre ?? ''}   ★   ${titre ?? ''}`}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ───────────────────────── Messagerie : les répliques arrivent comme des messages
export const HabillageChat: React.FC<{scene: Scene; accent: string; fond: string; children: React.ReactNode}> = ({scene, accent, fond, children}) => {
  const {t, rs} = useRepliques(scene);
  const {fps} = useVideoConfig();
  const frame = useCurrentFrame();
  const visibles = rs.filter((r) => t >= (r.debut ?? 0) - 0.6);
  const derniers = visibles.slice(-2);
  return (
    <AbsoluteFill style={{backgroundColor: fond}}>
      <div style={{position: 'absolute', left: 0, top: -170, width: W, height: H, transform: 'scale(0.8)', transformOrigin: '50% 20%'}}>{children}</div>
      {/* téléphone */}
      <div style={{position: 'absolute', left: 90, right: 90, top: 1080, height: 520, backgroundColor: '#F4F1EA', border: `10px solid ${INK}`, borderRadius: 48, boxShadow: `14px 14px 0 ${INK}`, overflow: 'hidden'}}>
        <div style={{height: 92, backgroundColor: INK, display: 'flex', alignItems: 'center', gap: 16, padding: '0 28px'}}>
          <div style={{width: 54, height: 54, borderRadius: 27, backgroundColor: accent, border: '4px solid #fff', fontFamily: fontPixel, fontSize: 28, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>D</div>
          <div style={{fontFamily: fontTitre, fontWeight: 800, fontSize: 36, color: '#fff'}}>Lou & Déco</div>
          <div style={{marginLeft: 'auto', fontFamily: fontPixel, fontSize: 22, color: '#9BF6A3'}}>en ligne</div>
        </div>
        <div style={{position: 'absolute', left: 24, right: 24, bottom: 24, display: 'flex', flexDirection: 'column', gap: 16}}>
          {derniers.map((r, i) => {
            const lou = r.qui === 'narrateur';
            const d = r.debut ?? 0;
            const tape = t < d; // « … en train d'écrire »
            const p = spring({frame: frame - Math.round((d - 0.6) * fps), fps, config: {damping: 12, mass: 0.5}});
            const mots = r.texte.split(/\s+/);
            const n = tape ? 0 : Math.ceil(Math.min(1, (t - d) / Math.max(0.3, (r.fin ?? d + 2) - d)) * mots.length);
            return (
              <div key={`${i}-${d}`} style={{alignSelf: lou ? 'flex-end' : 'flex-start', maxWidth: '82%', transform: `scale(${p})`, transformOrigin: lou ? '100% 100%' : '0 100%'}}>
                <div style={{backgroundColor: lou ? accent : '#fff', border: `5px solid ${INK}`, borderRadius: 26, borderBottomRightRadius: lou ? 4 : 26, borderBottomLeftRadius: lou ? 26 : 4, padding: '10px 18px', fontFamily: fontTitre, fontWeight: 700, fontSize: 34, color: INK, lineHeight: 1.2}}>
                  {tape ? <span style={{letterSpacing: 6}}>{'•••'.slice(0, 1 + (Math.floor(frame / 6) % 3))}</span> : (
                    <>
                      <span>{mots.slice(0, n).join(' ')}</span>
                      <span style={{opacity: 0.3}}> {mots.slice(n).join(' ')}</span>
                    </>
                  )}
                </div>
                <div style={{fontFamily: fontPixel, fontSize: 20, color: INK, opacity: 0.6, textAlign: lou ? 'right' : 'left', marginTop: 4}}>{lou ? 'Lou' : 'Déco'}</div>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ───────────────────────── Plein écran : contenu en grand, personnages en médaillons
export const HabillagePleinEcran: React.FC<{scene: Scene; tenues: Tenues; accent: string; children: React.ReactNode}> = ({scene, tenues, accent, children}) => {
  const {t, actif, expr, parle} = useRepliques(scene);
  const medaillon = (qui: Qui, gauche: boolean) => (
    <div style={{position: 'absolute', [gauche ? 'left' : 'right']: 40, top: 1250, width: 230, height: 230, borderRadius: 115, border: `8px solid ${INK}`, backgroundColor: parle(qui) ? accent : '#fff', overflow: 'hidden', boxShadow: `8px 8px 0 ${INK}`, transform: `scale(${parle(qui) ? 1.08 : 0.95})`}}>
      <div style={{position: 'absolute', left: gauche ? -120 : -770, top: -1080, width: W, height: H, transform: 'scale(0.9)', transformOrigin: gauche ? '260px 1250px' : '900px 1250px'}}>
        <Personnage qui={qui} expression={expr(qui)} parle={parle(qui)} tenue={qui === 'narrateur' ? scene.tenue_narrateur ?? tenues.narrateur : scene.tenue_mascotte ?? tenues.mascotte} x={gauche ? 50 : 700} entree={gauche ? 2 : 6} />
      </div>
    </div>
  );
  return (
    <AbsoluteFill>
      <div style={{position: 'absolute', left: 0, top: 0, width: W, height: H}}>{children}</div>
      {medaillon('narrateur', true)}
      {medaillon('mascotte', false)}
      <SousTitre r={actif} t={t} couleur={accent} top={1520} />
    </AbsoluteFill>
  );
};

// ───────────────────────── Nouvelles scènes
type Q = Extract<Scene, {type: 'quiz'}>;
export const Quiz: React.FC<{scene: Q; c1: string; c2: string; bg: string}> = ({scene, c1, c2, bg}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const revel = Math.round((scene.revelation ?? scene.duration * 0.55) * fps);
  const rebours = Math.max(0, Math.ceil((revel - frame) / fps));
  const ink = encrePour(bg);
  return (
    <>
      <div style={{position: 'absolute', left: 70, right: 70, top: 330, fontFamily: fontTitre, fontWeight: 900, fontSize: 70, color: ink, lineHeight: 1.05}}>{scene.question}</div>
      <div style={{position: 'absolute', left: 70, right: 70, top: 640, display: 'flex', flexDirection: 'column', gap: 26}}>
        {scene.options.map((o, i) => {
          const p = spring({frame: frame - 8 - i * 6, fps, config: {damping: 10}});
          const bonne = i === scene.bonne;
          const apres = frame >= revel;
          const coul = apres ? (bonne ? '#2BD99F' : '#9A9AA8') : i % 2 ? c2 : c1;
          return (
            <div key={i} style={{transform: `translateX(${(1 - p) * (i % 2 ? 80 : -80)}px) scale(${apres && bonne ? 1.06 + 0.02 * Math.sin(frame / 3) : 1})`, opacity: Math.min(1, p * 1.5)}}>
              <div style={{backgroundColor: coul, border: `7px solid ${INK}`, borderRadius: 18, boxShadow: `10px 10px 0 ${INK}`, padding: '20px 28px', fontFamily: fontTitre, fontWeight: 800, fontSize: 52, color: INK, display: 'flex', gap: 22, alignItems: 'center'}}>
                <span style={{fontFamily: fontPixel, fontSize: 40, backgroundColor: INK, color: '#fff', padding: '2px 14px', borderRadius: 8}}>{'ABC'[i]}</span>
                {o}
                {apres ? <span style={{marginLeft: 'auto', fontSize: 60}}>{bonne ? '✔' : '✘'}</span> : null}
              </div>
            </div>
          );
        })}
      </div>
      {frame < revel ? (
        <div style={{position: 'absolute', right: 80, top: 1060, width: 130, height: 130, borderRadius: 65, backgroundColor: INK, color: '#fff', fontFamily: fontPixel, fontSize: 70, display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `scale(${1 + 0.15 * ((frame % fps) / fps)})`}}>{rebours}</div>
      ) : null}
    </>
  );
};

type B = Extract<Scene, {type: 'bigstat'}>;
export const BigStat: React.FC<{scene: B; c1: string; bg: string}> = ({scene, c1, bg}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = spring({frame, fps, config: {damping: 7, mass: 0.9}});
  const glitch = frame < 14 ? (frame % 3) * 12 - 12 : 0;
  const ink = encrePour(bg);
  return (
    <>
      <div style={{position: 'absolute', left: 0, right: 0, top: 420, textAlign: 'center', transform: `scale(${0.4 + 0.6 * p}) translateX(${glitch}px)`}}>
        <span style={{fontFamily: fontTitre, fontWeight: 900, fontSize: scene.value.length > 8 ? 150 : scene.value.length > 6 ? 210 : 300, whiteSpace: 'nowrap', color: c1, WebkitTextStroke: `10px ${INK}`, paintOrder: 'stroke fill', textShadow: `16px 16px 0 ${INK}`, letterSpacing: -6}}>{scene.value}</span>
      </div>
      {frame < 14 ? <div style={{position: 'absolute', left: 0, right: 0, top: 470 + glitch * 4, height: 30, backgroundColor: '#FF4F81', opacity: 0.6}} /> : null}
      <div style={{position: 'absolute', left: 80, right: 80, top: 800, textAlign: 'center', opacity: interpolate(frame, [10, 20], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>
        <span style={{fontFamily: fontTitre, fontWeight: 800, fontSize: 60, color: ink, lineHeight: 1.1}}>{scene.label}</span>
      </div>
      {scene.source ? <div style={{position: 'absolute', left: 80, right: 80, top: 1010, textAlign: 'center', fontFamily: fontPixel, fontSize: 26, color: ink, opacity: 0.75}}>Source : {scene.source}</div> : null}
    </>
  );
};

type C = Extract<Scene, {type: 'checklist'}>;
export const Checklist: React.FC<{scene: C; c1: string; c2: string; bg: string}> = ({scene, c1, c2, bg}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const per = Math.max(10, Math.floor((scene.duration * fps * 0.6) / Math.max(1, scene.items.length)));
  const ink = encrePour(bg);
  return (
    <>
      {scene.title ? <div style={{position: 'absolute', left: 70, right: 70, top: 330, fontFamily: fontTitre, fontWeight: 900, fontSize: 72, color: ink}}>{scene.title}</div> : null}
      <div style={{position: 'absolute', left: 70, right: 70, top: 480, display: 'flex', flexDirection: 'column', gap: 30}}>
        {scene.items.map((it, i) => {
          const d = 6 + i * per;
          const p = spring({frame: frame - d, fps, config: {damping: 11}});
          const tampon = spring({frame: frame - d - 10, fps, config: {damping: 6, mass: 0.6}});
          const etat = it.etat ?? 'vrai';
          const couleur = etat === 'vrai' ? '#2BD99F' : etat === 'faux' ? '#FF4F4F' : '#FFC531';
          return (
            <div key={i} style={{position: 'relative', opacity: Math.min(1, p * 1.5), transform: `translateY(${(1 - p) * 40}px)`}}>
              <Sticker couleur={i % 2 ? c2 : c1} rotate={i % 2 ? 1.5 : -1.5}>
                <span style={{fontFamily: fontTitre, fontWeight: 800, fontSize: 46, paddingRight: 190, display: 'inline-block'}}>{it.texte}</span>
              </Sticker>
              <div style={{position: 'absolute', right: 10, top: '50%', transform: `translateY(-50%) rotate(-12deg) scale(${2 - tampon})`, opacity: Math.min(1, tampon), border: `6px solid ${couleur}`, color: couleur, backgroundColor: '#fff', fontFamily: fontPixel, fontSize: 32, padding: '4px 12px'}}>
                {etat === 'vrai' ? 'VRAI' : etat === 'faux' ? 'FAUX' : 'FLOU'}
              </div>
            </div>
          );
        })}
      </div>
    </>
  );
};

// ───────────────────────── Transitions variées
export const Transition: React.FC<{type: string; couleur: string; seed: number; duree?: number}> = ({type, couleur, seed, duree = 12}) => {
  const frame = useCurrentFrame();
  if (frame > duree) return null;
  const p = Easing.inOut(Easing.cubic)(frame / duree);
  if (type === 'iris') {
    const r = (1 - p) * 1400;
    return <AbsoluteFill style={{background: `radial-gradient(circle at 50% 45%, transparent ${Math.max(0, 1400 - r)}px, ${couleur} ${Math.max(0, 1400 - r) + 2}px)`}} />;
  }
  if (type === 'volet') {
    return <AbsoluteFill><div style={{position: 'absolute', top: 0, bottom: 0, left: seed % 2 ? `${p * 100}%` : 0, right: seed % 2 ? 0 : `${p * 100}%`, backgroundColor: couleur}} /></AbsoluteFill>;
  }
  if (type === 'bandes') {
    return (
      <AbsoluteFill>
        {Array.from({length: 8}).map((_, i) => {
          const q = Math.min(1, Math.max(0, p * 1.6 - i * 0.08));
          return <div key={i} style={{position: 'absolute', left: 0, right: 0, top: (i * H) / 8, height: H / 8 + 1, backgroundColor: couleur, transform: `translateX(${(i % 2 ? 1 : -1) * q * W}px)`}} />;
        })}
      </AbsoluteFill>
    );
  }
  if (type === 'glitch') {
    const tranche = Array.from({length: 10}).map((_, i) => ((seed * 13 + i * 7) % 10) / 10);
    return (
      <AbsoluteFill>
        {tranche.map((v, i) => (v > p ? <div key={i} style={{position: 'absolute', left: (v - 0.5) * 120, right: (0.5 - v) * 120, top: (i * H) / 10, height: H / 10 + 1, backgroundColor: i % 3 === 0 ? '#FF4F81' : couleur, opacity: 0.95}} /> : null))}
      </AbsoluteFill>
    );
  }
  return null;
};
