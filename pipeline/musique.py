"""Musique de fond chiptune (8 bits), composée par le code : gratuite, sans droits, assortie au pixel art.

Ambiances : « tension » (mineur, pulsé), « curieux » (léger, sautillant), « joyeux » (majeur, entraînant).
La musique est mixée sous les voix avec un « ducking » : elle baisse automatiquement quand quelqu'un parle.
"""
from __future__ import annotations

import subprocess
import wave
from pathlib import Path

import numpy as np

SR = 44100
AMBIANCES = {
    #          tempo  accords (demi-tons depuis la tonique, 4 mesures)            tonique (Hz)
    "tension": (100, [[0, 3, 7], [-4, 0, 3], [-2, 2, 5], [-5, -1, 2]], 110.0),
    "curieux": (112, [[0, 4, 7], [-3, 0, 4], [5, 9, 12], [7, 11, 14]], 130.8),
    "joyeux":  (124, [[0, 4, 7], [7, 11, 14], [-3, 0, 4], [5, 9, 12]], 146.8),
}


def _onde(freq: float, n: int, forme: str, rapport: float = 0.5) -> np.ndarray:
    t = np.arange(n) / SR
    ph = (t * freq) % 1.0
    if forme == "carre":
        return np.where(ph < rapport, 1.0, -1.0)
    if forme == "triangle":
        return 4 * np.abs(ph - 0.5) - 1
    return np.random.default_rng(int(freq)).uniform(-1, 1, n)  # bruit


def _env(n: int, attaque: float = 0.005, chute: float = 0.6) -> np.ndarray:
    e = np.ones(n)
    a = max(1, int(attaque * SR))
    e[:a] = np.linspace(0, 1, a)
    e *= np.exp(-np.linspace(0, 1, n) / max(chute, 1e-3))
    return e


def composer(duree: float, ambiance: str, sortie: Path, graine: int = 0, tempo: float | None = None) -> Path:
    t0, accords, tonique = AMBIANCES.get(ambiance, AMBIANCES["curieux"])
    tempo = min(150, max(70, float(tempo or t0)))
    rng = np.random.default_rng(graine)
    noire = 60 / tempo
    n_total = int((duree + 1) * SR)
    piste = np.zeros(n_total)
    hz = lambda st: tonique * 2 ** (st / 12)
    motif = rng.permutation([0, 1, 2, 1, 2, 0, 2, 1])  # arpège propre à chaque vidéo
    t, mesure = 0.0, 0
    while t < duree + 1:
        acc = accords[mesure % 4]
        for temps in range(4):  # basse triangle sur chaque temps
            i0, n = int((t + temps * noire) * SR), int(noire * SR)
            if i0 + n > n_total:
                break
            piste[i0:i0 + n] += 0.32 * _onde(hz(acc[0] - 12), n, "triangle") * _env(n, chute=0.5)
            # charleston (bruit court) sur les contretemps, caisse claire sur 2 et 4
            nh = int(0.04 * SR)
            ih = i0 + n // 2
            piste[ih:ih + nh] += 0.06 * _onde(1, nh, "bruit") * _env(nh, chute=0.2)
            if temps % 2 == 1:
                ns = int(0.12 * SR)
                piste[i0:i0 + ns] += 0.10 * _onde(2, ns, "bruit") * _env(ns, chute=0.25)
        for k in range(8):  # arpège carré en croches
            i0, n = int((t + k * noire / 2) * SR), int(noire / 2 * SR)
            if i0 + n > n_total:
                break
            note = acc[motif[k] % 3] + 12 * (k // 4)
            piste[i0:i0 + n] += 0.12 * _onde(hz(note), n, "carre", 0.25) * _env(n, chute=0.35)
        t += 4 * noire
        mesure += 1
    piste = piste[: int(duree * SR)]
    fondu = int(1.5 * SR)
    piste[:fondu] *= np.linspace(0, 1, fondu)
    piste[-fondu:] *= np.linspace(1, 0, fondu)
    piste = piste / max(1e-6, np.abs(piste).max()) * 0.8
    with wave.open(str(sortie), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((piste * 32767).astype("<i2").tobytes())
    return sortie


def _effroi(n: int, graine: int) -> np.ndarray:
    """Nappe inquiétante : bourdon grave, battements de cœur, aigu qui tremble."""
    t = np.arange(n) / SR
    drone = 0.5 * np.sin(2 * np.pi * 55 * t) + 0.35 * np.sin(2 * np.pi * 58.3 * t) + 0.2 * np.sin(2 * np.pi * 110.7 * t)
    aigu = 0.12 * np.sin(2 * np.pi * 932 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 7 * t))
    coeur = np.zeros(n)
    for b in np.arange(0.2, n / SR, 0.9):  # « boum-boum »
        for dt, amp in ((0, 0.9), (0.18, 0.6)):
            i0, m = int((b + dt) * SR), int(0.16 * SR)
            if i0 + m < n:
                coeur[i0:i0 + m] += amp * np.sin(2 * np.pi * 48 * np.arange(m) / SR) * _env(m, chute=0.25)
    return drone * np.linspace(0.6, 1, n) + aigu + coeur


def _sfx(nom: str) -> np.ndarray:
    """Effets sonores 8 bits : whoosh (transition), impact, pop, ding."""
    if nom == "whoosh":
        n = int(0.35 * SR)
        bruit = np.random.default_rng(5).uniform(-1, 1, n)
        k = np.linspace(2, 40, n).astype(int)  # filtre qui s'ouvre puis se referme
        lisse = np.array([bruit[max(0, j - k[j]):j + 1].mean() for j in range(n)])
        return 1.6 * lisse * np.sin(np.linspace(0, np.pi, n))
    if nom == "impact":
        n = int(0.6 * SR)
        f = np.linspace(90, 35, n)
        return 0.9 * np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, chute=0.3)
    if nom == "pop":
        n = int(0.09 * SR)
        f = np.linspace(500, 1400, n)
        return 0.5 * np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * _env(n, chute=0.4)
    n = int(0.5 * SR)  # ding
    return 0.35 * (_onde(1568, n, "carre", 0.5) + 0.5 * _onde(2093, n, "carre", 0.5)) * _env(n, chute=0.3)


def bande_son(scenes: list[dict], defaut: str, sortie: Path, graine: int = 0, genre: str | None = None) -> Path:
    """Musique qui change par scène (fondus enchaînés) + effets sonores aux transitions.
    Chaque scène peut avoir "musique": "effroi|tension|curieux|joyeux" (ou {ambiance, tempo}) et "sfx": ["impact", …]."""
    durees = [float(sc.get("duration", 3)) for sc in scenes]
    total = int((sum(durees) + 0.5) * SR)
    piste, sfx = np.zeros(total), np.zeros(total)
    if genre:
        from .compositeur import GENRES, composer as composer_morceau
        secs, t0 = [], 0.0
        for k, (sc, d) in enumerate(zip(scenes, durees)):
            m = sc.get("musique")
            e = int(sc.get("energie") or (m.get("energie") if isinstance(m, dict) else 0) or
                    {"effroi": 1, "silence": 1, "tension": 2, "curieux": 2, "joyeux": 3}.get(m if isinstance(m, str) else "", 2))
            secs.append({"debut": t0, "fin": t0 + d, "energie": max(1, min(3, e))})
            t0 += d
        tmp = sortie.with_name("_morceau.wav")
        composer_morceau(secs, genre if genre in GENRES else "synthwave", tmp, graine)
        with wave.open(str(tmp), "rb") as w:
            morceau = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(float) / 32767
        tmp.unlink()
        piste[:len(morceau)] += morceau[:total]
        debut = 0.0
        for k, (sc, d) in enumerate(zip(scenes, durees)):  # nappe effrayante en plus là où l'agent 6 l'a demandée
            if sc.get("musique") == "effroi":
                n = int(d * SR)
                seg = _effroi(n, graine + k)
                seg = seg / max(1e-6, np.abs(seg).max()) * 0.6
                i0 = int(debut * SR)
                piste[i0:i0 + n] = piste[i0:i0 + n] * 0.4 + seg[: total - i0]
            debut += d
        scenes_musique = []
    else:
        scenes_musique = list(zip(scenes, durees))
    x = 0.4  # fondu enchaîné (s)
    debut = 0.0
    for k, (sc, d) in enumerate(scenes_musique):
        choix = sc.get("musique") or defaut
        amb, tempo = (choix.get("ambiance", defaut), choix.get("tempo")) if isinstance(choix, dict) else (choix, None)
        n = int((d + x) * SR)
        if amb == "effroi":
            seg = _effroi(n, graine + k)
            seg = seg / max(1e-6, np.abs(seg).max()) * 0.8
        elif amb in ("", "aucune", "silence"):
            seg = np.zeros(n)
        else:
            tmp = sortie.with_name(f"_seg{k}.wav")
            composer(d + x, amb, tmp, graine + k, tempo)
            with wave.open(str(tmp), "rb") as w:
                seg = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(float) / 32767
            tmp.unlink()
        seg = seg[:n]
        f = int(x * SR)
        if k > 0:
            seg[:f] *= np.linspace(0, 1, f)
        seg[-f:] *= np.linspace(1, 0, f)
        i0 = int(debut * SR)
        piste[i0:i0 + len(seg)] += seg[: total - i0]
        debut += d
    debut = 0.0
    for k, (sc, d) in enumerate(zip(scenes, durees)):
        i0 = int(debut * SR)
        effets = list(sc.get("sfx") or []) or (["impact"] if k == 0 else ["whoosh"])
        for e in effets:
            s_ = _sfx(e)
            j0 = i0 if e != "whoosh" else max(0, i0 - int(0.15 * SR))
            sfx[j0:j0 + len(s_)] += s_[: total - j0]
        debut += d
    fin = int(1.2 * SR)
    piste[-fin:] *= np.linspace(1, 0, fin)
    mix = piste / max(1e-6, np.abs(piste).max()) * 0.7 + sfx * 0.5
    mix = np.clip(mix, -1, 1)
    with wave.open(str(sortie), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype("<i2").tobytes())
    return sortie


def ajouter(video: Path, choix="curieux", graine: int = 0, volume: float = 0.8, scenes: list | None = None) -> None:
    """Ajoute la musique sous la voix (remplace le fichier). choix = "tension" ou {"ambiance", "tempo", "volume"}."""
    tempo, genre = None, None
    if isinstance(choix, dict):
        genre = choix.get("genre")
        tempo, volume = choix.get("tempo"), min(1.2, max(0.3, float(choix.get("volume", volume))))
        choix = choix.get("ambiance", "curieux")
    ambiance = choix
    if ambiance in (None, "", "aucune"):
        return
    duree = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                  str(video)], capture_output=True, text=True, check=True).stdout.strip())
    if scenes:
        wav = bande_son(scenes, ambiance, video.with_name("musique.wav"), graine, genre)
    else:
        wav = composer(duree, ambiance, video.with_name("musique.wav"), graine, tempo)
    a_voix = "audio" in subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
                                        "stream=codec_type", "-of", "csv=p=0", str(video)],
                                       capture_output=True, text=True).stdout
    tmp = video.with_name(video.stem + "_musique.mp4")
    if a_voix:
        filtre = (f"[1:a]volume={volume}[m];[0:a]asplit=2[v][sc];"
                  "[m][sc]sidechaincompress=threshold=0.1:ratio=2:attack=20:release=250[md];"
                  "[v][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.95[a]")
    else:
        filtre = f"[1:a]volume={volume * 2}[a]"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(video), "-i", str(wav), "-filter_complex", filtre,
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(tmp)],
                   check=True)
    tmp.replace(video)
    wav.unlink(missing_ok=True)
