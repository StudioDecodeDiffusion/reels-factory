"""Compositeur v2 : un vrai morceau par vidéo (pas une boucle).

- 7 genres : synthwave, lofi, trap8bit, orchestral, funk, suspense, house.
- Structure calée sur les scènes : chaque scène = une section avec une énergie (1 calme, 2 normal, 3 refrain).
- Couches selon l'énergie : nappe/accords → + basse et batterie → + mélodie, arpèges, crash.
- Mélodie A (couplets) et mélodie B (refrains) générées pour chaque vidéo, variées à chaque retour
  (transposition, rythme décalé, octave), montée d'un ton au dernier refrain, roulements et montées avant les refrains.
Tout est synthétisé par le code : gratuit, sans droits.
"""
from __future__ import annotations

import wave
from pathlib import Path

import numpy as np

SR = 44100

GAMMES = {"mineur": [0, 2, 3, 5, 7, 8, 10], "majeur": [0, 2, 4, 5, 7, 9, 11], "dorien": [0, 2, 3, 5, 7, 9, 10],
          "phrygien": [0, 1, 3, 5, 7, 8, 10]}

#            tempo  gamme      tonique  progression (degrés)      swing  lead      basse
GENRES = {
    "synthwave": (104, "mineur", 57, [0, 5, 2, 6], 0.0, "scie", "octaves"),
    "lofi":      (82, "dorien", 60, [1, 4, 0, 5], 0.18, "triangle", "ronde"),
    "trap8bit":  (140, "phrygien", 53, [0, 0, 5, 6], 0.0, "carre", "808"),
    "orchestral": (92, "mineur", 55, [0, 5, 3, 4], 0.0, "cordes", "ronde"),
    "funk":      (112, "dorien", 52, [0, 3, 0, 4], 0.1, "carre", "funk"),
    "suspense":  (76, "phrygien", 50, [0, 1, 0, 6], 0.0, "sinus", "pulse"),
    "house":     (122, "majeur", 57, [5, 3, 0, 4], 0.0, "carre", "octaves"),
}


def hz(midi: float) -> float:
    return 440.0 * 2 ** ((midi - 69) / 12)


def _t(n):
    return np.arange(n) / SR


def osc(forme: str, f, n: int, rng=None) -> np.ndarray:
    f = np.broadcast_to(np.asarray(f, dtype=float), (n,))
    ph = np.cumsum(f) / SR % 1.0
    if forme == "carre":
        return np.where(ph < 0.5, 1.0, -1.0)
    if forme == "carre25":
        return np.where(ph < 0.25, 1.0, -1.0)
    if forme == "scie":
        return 2 * ph - 1
    if forme == "triangle":
        return 4 * np.abs(ph - 0.5) - 1
    if forme == "cordes":  # scies désaccordées adoucies
        p2 = np.cumsum(f * 1.004) / SR % 1.0
        p3 = np.cumsum(f * 0.996) / SR % 1.0
        x = (2 * ph - 1 + 2 * p2 - 1 + 2 * p3 - 1) / 3
        return np.convolve(x, np.ones(12) / 12, mode="same")
    return np.sin(2 * np.pi * ph)  # sinus


def adsr(n: int, a=0.005, d=0.08, s=0.6, r=0.05) -> np.ndarray:
    e = np.full(n, s)
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    na = min(na, n)
    e[:na] = np.linspace(0, 1, na) if na else e[:na]
    nd2 = min(nd, max(0, n - na))
    e[na:na + nd2] = np.linspace(1, s, nd2) if nd2 else e[na:na + nd2]
    nr = min(nr, n)
    if nr:
        e[n - nr:] *= np.linspace(1, 0, nr)
    return e


class Piste:
    def __init__(self, duree: float):
        self.n = int(duree * SR) + SR
        self.x = np.zeros(self.n)

    def ajoute(self, debut: float, son: np.ndarray, gain: float = 1.0):
        i = int(debut * SR)
        if i >= self.n or i < 0:
            return
        m = min(len(son), self.n - i)
        self.x[i:i + m] += gain * son[:m]


# ── percussions
def kick(rng):
    n = int(0.28 * SR)
    f = 45 + 110 * np.exp(-_t(n) * 28)
    return osc("sinus", f, n) * np.exp(-_t(n) * 9)


def snare(rng):
    n = int(0.18 * SR)
    bruit = rng.uniform(-1, 1, n)
    return (0.7 * bruit + 0.4 * osc("triangle", 190, n)) * np.exp(-_t(n) * 22)


def hat(rng, ouvert=False):
    n = int((0.16 if ouvert else 0.04) * SR)
    b = rng.uniform(-1, 1, n)
    b = np.diff(b, prepend=0)
    return b * np.exp(-_t(n) * (14 if ouvert else 70))


def clap(rng):
    n = int(0.15 * SR)
    b = rng.uniform(-1, 1, n)
    e = np.zeros(n)
    for k in (0, 0.012, 0.024):
        i = int(k * SR)
        e[i:] += np.exp(-_t(n - i) * 30)
    return b * e * 0.6


def crash(rng):
    n = int(1.4 * SR)
    b = np.diff(rng.uniform(-1, 1, n), prepend=0)
    return b * np.exp(-_t(n) * 3)


def montee(rng, duree):  # bruit qui monte avant un refrain
    n = int(duree * SR)
    b = rng.uniform(-1, 1, n)
    k = np.linspace(30, 2, n).astype(int)
    c = np.cumsum(b)
    lisse = (c - np.concatenate([np.zeros(30), c[:-30]])[:n]) / 30
    return (b - lisse) * np.linspace(0, 1, n) ** 2


# ── composition
def _motif(rng, longueur=8, saut=3):
    m, d = [], rng.integers(0, 5)
    for _ in range(longueur):
        d = int(np.clip(d + rng.integers(-saut, saut + 1), -2, 9))
        m.append(d if rng.random() > 0.18 else None)  # silences
    return m


def _note(gamme, tonique, degre):
    o, i = divmod(degre, len(gamme))
    return tonique + 12 * o + gamme[i]


def composer(sections: list[dict], genre: str, sortie: Path, graine: int = 0, transpo: int = 0) -> Path:
    """sections = [{"debut": s, "fin": s, "energie": 1|2|3}] (une par scène). Écrit un WAV mono."""
    rng = np.random.default_rng(graine)
    tempo, nom_gamme, tonique, prog, swing, lead, basse = GENRES.get(genre, GENRES["synthwave"])
    tempo *= 1 + rng.uniform(-0.04, 0.04)
    tonique += transpo + int(rng.integers(-2, 3))
    gamme = GAMMES[nom_gamme]
    duree = sections[-1]["fin"]
    P = {k: Piste(duree) for k in ("bat", "basse", "nappe", "lead", "arp", "fx")}
    noire = 60 / tempo
    double = noire / 4
    motif_a, motif_b = _motif(rng), _motif(rng, saut=2)
    rythme_a = rng.random(16) < 0.55
    n_ref = sum(1 for s in sections if s["energie"] >= 3)
    ref_vus = 0

    for si, sec in enumerate(sections):
        e = sec["energie"]
        refrain = e >= 3
        if refrain:
            ref_vus += 1
        monte = 2 if (refrain and ref_vus == n_ref and n_ref > 1) else 0  # dernier refrain un ton plus haut
        variation = si % 3
        t = sec["debut"]
        mesure = 0
        # montée + roulement avant un refrain
        if si + 1 < len(sections) and sections[si + 1]["energie"] >= 3 and sec["fin"] - sec["debut"] > 2:
            P["fx"].ajoute(sec["fin"] - 1.6, montee(rng, 1.6), 0.25)
        if refrain:
            P["fx"].ajoute(t, crash(rng), 0.35)
        while t < sec["fin"] - 0.05:
            deg = prog[(mesure + si) % len(prog)]
            racine = _note(gamme, tonique, deg) + monte
            accord = [_note(gamme, tonique, deg + k) + monte for k in (0, 2, 4)]
            fin_mesure = min(t + 4 * noire, sec["fin"])
            lm = fin_mesure - t
            n = int(lm * SR)
            # nappe / accords
            forme_nappe = "cordes" if genre in ("orchestral", "synthwave") else ("triangle" if genre == "lofi" else "carre25")
            for i, note in enumerate(accord):
                son = osc(forme_nappe, hz(note), n) * adsr(n, a=0.08 if genre != "funk" else 0.005, d=0.3, s=0.5, r=0.2)
                if genre == "funk":  # accords piqués
                    for k in (1, 3, 6, 9, 11, 14):
                        st = t + k * double
                        if st < fin_mesure:
                            m = int(double * 0.8 * SR)
                            P["nappe"].ajoute(st, osc("carre25", hz(note + 12), m) * adsr(m, d=0.05, s=0.2), 0.05)
                    continue
                P["nappe"].ajoute(t, son, 0.07 if e == 1 else 0.05)
            # basse
            if e >= 2 or genre in ("suspense", "orchestral"):
                for k in range(16):
                    st = t + k * double + (swing * double if k % 2 else 0)
                    if st >= fin_mesure:
                        break
                    if basse == "octaves" and k % 2 == 0:
                        m = int(double * 0.9 * SR)
                        P["basse"].ajoute(st, osc("scie", hz(racine - 24 + (12 if k % 4 == 2 else 0)), m) * adsr(m, d=0.06, s=0.4), 0.22)
                    elif basse == "ronde" and k in (0, 8):
                        m = int(noire * 1.8 * SR)
                        P["basse"].ajoute(st, osc("triangle", hz(racine - 24), m) * adsr(m, d=0.4, s=0.5, r=0.1), 0.35)
                    elif basse == "808" and k in (0, 6, 10):
                        m = int(noire * 1.5 * SR)
                        glisse = hz(racine - 24) * (1 + 0.06 * np.exp(-_t(m) * 20))
                        P["basse"].ajoute(st, np.tanh(2 * osc("sinus", glisse, m)) * adsr(m, d=0.6, s=0.4, r=0.1), 0.4)
                    elif basse == "funk" and k in (0, 3, 6, 7, 10, 12, 14):
                        m = int(double * 0.7 * SR)
                        sautn = [0, 0, 12, 7, 0, 10, 12][[0, 3, 6, 7, 10, 12, 14].index(k)]
                        P["basse"].ajoute(st, osc("carre", hz(racine - 24 + sautn), m) * adsr(m, d=0.05, s=0.3), 0.16)
                    elif basse == "pulse" and k % 4 == 0:
                        m = int(double * 1.5 * SR)
                        P["basse"].ajoute(st, osc("sinus", hz(racine - 24), m) * adsr(m, d=0.2, s=0.2), 0.45)
            # batterie
            if e >= 2 or genre == "trap8bit":
                for k in range(16):
                    st = t + k * double + (swing * double if k % 2 else 0)
                    if st >= fin_mesure:
                        break
                    if genre in ("house", "synthwave", "funk"):
                        if k % 4 == 0:
                            P["bat"].ajoute(st, kick(rng), 0.5)
                        if k % 8 == 4:
                            P["bat"].ajoute(st, snare(rng) if genre != "house" else clap(rng), 0.35)
                        if k % 2 == 1 or (e >= 3 and genre == "house"):
                            P["bat"].ajoute(st, hat(rng, ouvert=(genre == "house" and k % 4 == 2)), 0.12)
                    elif genre == "trap8bit":
                        if k in (0, 7, 10):
                            P["bat"].ajoute(st, kick(rng), 0.5)
                        if k == 8:
                            P["bat"].ajoute(st, clap(rng), 0.4)
                        if e >= 2:
                            P["bat"].ajoute(st, hat(rng), 0.1)
                            if e >= 3 and k in (13, 14, 15):  # roulements
                                P["bat"].ajoute(st + double / 2, hat(rng), 0.08)
                    elif genre == "lofi":
                        if k in (0, 10):
                            P["bat"].ajoute(st, kick(rng), 0.35)
                        if k in (4, 12):
                            P["bat"].ajoute(st, snare(rng), 0.18)
                        if k % 2 == 0:
                            P["bat"].ajoute(st, hat(rng), 0.06)
                    elif genre == "orchestral":
                        if k in (0, 8) and e >= 3:
                            m = int(0.6 * SR)
                            P["bat"].ajoute(st, osc("sinus", 70 * (1 + 0.3 * np.exp(-_t(m) * 10)), m) * np.exp(-_t(m) * 5), 0.5)
                    elif genre == "suspense":
                        if k in (0, 3):  # battement de cœur
                            P["bat"].ajoute(st, kick(rng), 0.45)
                # roulement de fin de section
                if fin_mesure >= sec["fin"] - 0.01 and si + 1 < len(sections) and genre not in ("orchestral", "suspense", "lofi"):
                    for k in range(4):
                        P["bat"].ajoute(fin_mesure - (4 - k) * double, snare(rng), 0.15 + 0.05 * k)
            # mélodie (énergie 3 ; un peu en énergie 2 pour certains genres)
            if e >= 3 or (e == 2 and genre in ("lofi", "orchestral", "synthwave") and variation == 1):
                motif = motif_b if refrain else motif_a
                dec = [0, 2, -1][variation]
                for k in range(8):
                    d = motif[(k + mesure * 3) % 8]
                    if d is None or not (refrain or rythme_a[k * 2]):
                        continue
                    st = t + k * 2 * double
                    if st >= fin_mesure:
                        break
                    note = _note(gamme, tonique, d + dec) + 12 + monte
                    m = int(2 * double * (0.9 if genre != "trap8bit" else 0.6) * SR)
                    vib = hz(note) * (1 + 0.006 * np.sin(2 * np.pi * 5.5 * _t(m)))
                    son = osc(lead if lead != "carre" else ("carre25" if refrain else "carre"), vib, m) * adsr(m, d=0.1, s=0.6, r=0.04)
                    P["lead"].ajoute(st, son, 0.11)
                    P["lead"].ajoute(st + 3 * double, son, 0.035)  # écho
            # arpège (refrains, genres électroniques)
            if refrain and genre in ("synthwave", "house", "trap8bit", "funk"):
                for k in range(16):
                    st = t + k * double
                    if st >= fin_mesure:
                        break
                    note = accord[k % 3] + 12 * (1 + (k // 8) % 2)
                    m = int(double * 0.8 * SR)
                    P["arp"].ajoute(st, osc("carre25", hz(note), m) * adsr(m, d=0.05, s=0.2), 0.045)
            t = fin_mesure
            mesure += 1

    if genre == "lofi":  # craquements de vinyle
        b = rng.uniform(-1, 1, P["fx"].n)
        P["fx"].x += 0.012 * b * (rng.random(P["fx"].n) > 0.9995) * 8 + 0.004 * b
    mix = sum(p.x for p in P.values())
    fond = int(1.0 * SR)
    mix[:int(0.05 * SR)] *= np.linspace(0, 1, int(0.05 * SR))
    fin = int(duree * SR)
    mix = mix[:fin]
    mix[-fond:] *= np.linspace(1, 0, fond)
    mix = np.tanh(1.3 * mix / max(1e-6, np.percentile(np.abs(mix), 99.5)))  # compression douce
    mix = mix / max(1e-6, np.abs(mix).max()) * 0.85
    with wave.open(str(sortie), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype("<i2").tobytes())
    return sortie
