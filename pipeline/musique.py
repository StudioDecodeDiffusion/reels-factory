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


def composer(duree: float, ambiance: str, sortie: Path, graine: int = 0) -> Path:
    tempo, accords, tonique = AMBIANCES.get(ambiance, AMBIANCES["curieux"])
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


def ajouter(video: Path, ambiance: str = "curieux", graine: int = 0, volume: float = 0.2) -> None:
    """Ajoute la musique sous la voix de la vidéo (remplace le fichier)."""
    if ambiance in (None, "", "aucune"):
        return
    duree = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                  str(video)], capture_output=True, text=True, check=True).stdout.strip())
    wav = composer(duree, ambiance, video.with_name("musique.wav"), graine)
    a_voix = "audio" in subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
                                        "stream=codec_type", "-of", "csv=p=0", str(video)],
                                       capture_output=True, text=True).stdout
    tmp = video.with_name(video.stem + "_musique.mp4")
    if a_voix:
        filtre = (f"[1:a]volume={volume}[m];[0:a]asplit=2[v][sc];"
                  "[m][sc]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=350[md];"
                  "[v][md]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]")
    else:
        filtre = f"[1:a]volume={volume * 2}[a]"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(video), "-i", str(wav), "-filter_complex", filtre,
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(tmp)],
                   check=True)
    tmp.replace(video)
    wav.unlink(missing_ok=True)
