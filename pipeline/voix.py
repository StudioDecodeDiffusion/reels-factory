"""Voix off par IA, gratuite et open source, exécutée dans GitHub Actions.

Une voix se décrit par « moteur:nom?param=valeur&… » :
- Piper (léger, rapide) : « piper:fr_FR-gilles-low?vitesse=1.2&expr=0.85&rythme=1.0 »
    spk = numéro du locuteur (voix multi-locuteurs), vitesse (1 = normal),
    expr = variations d'intonation (0.667 par défaut, plus haut = plus expressif),
    rythme = variations de durée des sons (0.8 par défaut).
- Chatterbox multilingue (Resemble AI, MIT, plus naturel et expressif, plus lent) :
  « chatterbox:fr?ref=gilles&exag=0.6&cfg=0.3 »
    ref = voix dont on reprend le timbre (gilles, pierre, jessica ou une voix Piper complète),
    exag = expressivité (0.5 par défaut), cfg = fidélité au rythme de la référence (plus bas = plus libre).
- Kokoro : « kokoro:ff_siwis?vitesse=1.0 »

Licences : Gilles (données CC0), UPMC Pierre/Jessica (CC BY-SA 4.0 → mention dans la légende),
MLS (CC BY 4.0 → mention), Chatterbox (MIT, filigrane audio inaudible « Perth » intégré), Kokoro (Apache 2.0).

Usage :
  python -m pipeline.voix echantillons <texte.txt> <essais.json> <dossier_sortie>
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path
from urllib.parse import parse_qsl

CACHE = Path.home() / ".cache" / "decode-voix"
KOKORO_FILES = {
    "kokoro-v1.0.onnx": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx",
    "voices-v1.0.bin": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin",
}
REFS = {
    "gilles": "piper:fr_FR-gilles-low?vitesse=1.15",
    "pierre": "piper:fr_FR-upmc-medium?spk=1",
    "jessica": "piper:fr_FR-upmc-medium?spk=0",
}
REF_TEXTE = ("Bonjour à toutes et à tous. Aujourd'hui, on prend deux minutes pour comprendre l'actualité, "
             "simplement, avec des chiffres clairs et des exemples concrets. C'est parti !")
MENTIONS = {
    "upmc": "Voix : UPMC Pierre/Jessica, CC BY-SA 4.0.",
    "mls": "Voix : Multilingual LibriSpeech, CC BY 4.0.",
    "siwis": "Voix : SIWIS, CC BY 4.0.",
}


def parse(voix: str) -> tuple[str, str, dict]:
    moteur, reste = voix.split(":", 1)
    nom, _, q = reste.partition("?")
    if "#" in nom:  # ancien format « …#1 »
        nom, spk = nom.split("#", 1)
        q = f"spk={spk}&{q}"
    return moteur, nom, dict(parse_qsl(q))


def mention(voix: str) -> str:
    """Mention de licence à ajouter en fin de légende (vide si aucune n'est requise)."""
    for cle, txt in MENTIONS.items():
        if cle in voix:
            return txt
    if voix.startswith("chatterbox") and "ref=pierre" in voix or "ref=jessica" in voix:
        return MENTIONS["upmc"]
    return ""


# ───────────────────────────────────────── Piper
def _piper(text: str, nom: str, wav: Path, p: dict) -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    if not (CACHE / f"{nom}.onnx").exists():
        subprocess.run([sys.executable, "-m", "piper.download_voices", "--data-dir", str(CACHE), nom], check=True)
    base = [sys.executable, "-m", "piper", "-m", str(CACHE / f"{nom}.onnx"), "-f", str(wav),
            "--length-scale", str(round(1 / float(p.get("vitesse", 1.0)), 3))]
    if "spk" in p:
        base += ["--speaker", str(p["spk"])]
    expressif = ["--noise-scale", str(p.get("expr", 0.667)), "--noise-w-scale", str(p.get("rythme", 0.8))]
    r = subprocess.run([*base, *expressif, "--", text], capture_output=True, text=True)
    if r.returncode != 0:  # version de Piper sans ces options : on retombe sur les réglages par défaut
        subprocess.run([*base, "--", text], check=True)


# ───────────────────────────────────────── Kokoro
_kokoro = None


def _kokoro_say(text: str, nom: str, wav: Path, p: dict) -> None:
    global _kokoro
    import soundfile as sf
    from kokoro_onnx import Kokoro
    CACHE.mkdir(parents=True, exist_ok=True)
    for name, url in KOKORO_FILES.items():
        if not (CACHE / name).exists():
            urllib.request.urlretrieve(url, CACHE / name)
    if _kokoro is None:
        _kokoro = Kokoro(str(CACHE / "kokoro-v1.0.onnx"), str(CACHE / "voices-v1.0.bin"))
    samples, sr = _kokoro.create(text, voice=nom, speed=float(p.get("vitesse", 1.0)), lang="fr-fr")
    sf.write(str(wav), samples, sr)


# ───────────────────────────────────────── Chatterbox
_chatter = None


def _phrases(text: str, maxlen: int = 220) -> list[str]:
    parts = re.split(r"(?<=[.!?…])\s+", text.strip())
    out, cur = [], ""
    for s in parts:
        if len(cur) + len(s) < maxlen:
            cur = f"{cur} {s}".strip()
        else:
            if cur:
                out.append(cur)
            cur = s
    if cur:
        out.append(cur)
    return out


def _chatterbox(text: str, lang: str, wav: Path, p: dict) -> None:
    global _chatter
    import torch
    import torchaudio as ta
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    if _chatter is None:
        _chatter = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
    ref = None
    if p.get("ref"):
        ref_voix = REFS.get(p["ref"], p["ref"])
        ref = CACHE / f"ref_{re.sub(r'[^a-z0-9]+', '_', ref_voix.lower())}.wav"
        if not ref.exists():
            say(REF_TEXTE, ref_voix, ref)
    kw = {"exaggeration": float(p.get("exag", 0.5)), "cfg_weight": float(p.get("cfg", 0.5))}
    if ref:
        kw["audio_prompt_path"] = str(ref)
    morceaux = []
    for phrase in _phrases(text):
        try:
            w = _chatter.generate(phrase, language_id=lang, **kw)
        except TypeError:  # version sans certains réglages
            w = _chatter.generate(phrase, language_id=lang)
        morceaux += [w, torch.zeros(1, int(_chatter.sr * 0.18))]
    ta.save(str(wav), torch.cat(morceaux, dim=1), _chatter.sr)


# ───────────────────────────────────────── commun
def say(text: str, voix: str, wav: Path, vitesse: float = 1.0) -> Path:
    moteur, nom, p = parse(voix)
    if vitesse != 1.0:
        p["vitesse"] = float(p.get("vitesse", 1.0)) * vitesse
    if moteur == "piper":
        _piper(text, nom, wav, p)
    elif moteur == "kokoro":
        _kokoro_say(text, nom, wav, p)
    elif moteur == "chatterbox":
        _chatterbox(text, nom, wav, p)
    else:
        raise ValueError(f"moteur de voix inconnu : {moteur}")
    return wav


def duree(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def to_mp3(wav: Path) -> Path:
    """MP3 normalisé en volume (les voix ont des niveaux différents)."""
    mp3 = wav.with_suffix(".mp3")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(wav), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-ar", "44100", "-b:a", "128k", str(mp3)], check=True)
    return mp3


def sonoriser(spec: dict, job: str, profile: dict, public_dir: Path) -> dict:
    """Génère la voix off de chaque scène, cale la durée des scènes dessus et renvoie la spec sonorisée.
    Les fichiers audio vont dans video/public/voix/<job>/ (lus par Remotion via staticFile)."""
    reglages = profile.get("voix", {})
    voix_id, vitesse = reglages.get("id", "piper:fr_FR-gilles-low"), float(reglages.get("vitesse", 1.0))
    dest = public_dir / "voix" / job
    dest.mkdir(parents=True, exist_ok=True)
    for i, sc in enumerate(spec["scenes"]):
        texte = str(sc.get("voix") or "").strip()
        if not texte:
            continue
        wav = dest / f"scene{i}.wav"
        say(texte, voix_id, wav, vitesse)
        mp3 = to_mp3(wav)
        wav.unlink()
        d = duree(mp3)
        sc["voix_duree"] = round(d, 2)  # sert à caler les sous-titres mot à mot
        # la scène dure le temps de la phrase + une respiration (0,6 s), jamais moins que prévu à l'image
        sc["duration"] = round(max(float(sc.get("duration", 3)), d + 0.6), 2)
        sc["audio"] = f"voix/{job}/{mp3.name}"
    return spec


def echantillons(texte: Path, essais: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    text = texte.read_text(encoding="utf-8").strip()
    for e in json.loads(essais.read_text(encoding="utf-8")):
        wav = out / f"{e['nom']}.wav"
        try:
            mp3 = to_mp3(say(text, e["voix"], wav))
            wav.unlink()
            print(f"{e['nom']} ({e['voix']}) → {duree(mp3):.1f} s", flush=True)
        except Exception as ex:
            print(f"{e['nom']} : échec ({type(ex).__name__}: {ex})", flush=True)


if __name__ == "__main__":
    if sys.argv[1:2] == ["echantillons"]:
        echantillons(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]))
    else:
        sys.exit(__doc__)
