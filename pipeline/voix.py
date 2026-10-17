"""Voix off par IA, gratuite et open source, exécutée dans GitHub Actions.

Moteurs :
- Piper (rhasspy) : voix françaises légères (siwis, tom, upmc, gilles).
- Kokoro (82M, Apache 2.0) via kokoro-onnx : voix française « ff_siwis ».

Usage :
  python -m pipeline.voix echantillons <texte.txt> <dossier_sortie>
  python -m pipeline.voix scenes <narration.json> <dossier_sortie> --voix piper:fr_FR-siwis-medium
"""
from __future__ import annotations

import subprocess
import sys
import urllib.request
from pathlib import Path

CACHE = Path.home() / ".cache" / "decode-voix"

PIPER_VOICES = ["fr_FR-siwis-medium", "fr_FR-tom-medium", "fr_FR-upmc-medium", "fr_FR-gilles-low"]
KOKORO_FILES = {
    "kokoro-v1.0.onnx": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx",
    "voices-v1.0.bin": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin",
}


def _piper(text: str, voice: str, wav: Path, speaker: int | None = None, length_scale: float = 1.0) -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    if not (CACHE / f"{voice}.onnx").exists():
        subprocess.run([sys.executable, "-m", "piper.download_voices", "--data-dir", str(CACHE), voice], check=True)
    cmd = [sys.executable, "-m", "piper", "-m", str(CACHE / f"{voice}.onnx"), "-f", str(wav),
           "--length-scale", str(length_scale)]
    if speaker is not None:
        cmd += ["--speaker", str(speaker)]
    subprocess.run([*cmd, "--", text], check=True)


_kokoro = None


def _kokoro_say(text: str, voice: str, wav: Path, speed: float = 1.0) -> None:
    global _kokoro
    import soundfile as sf
    from kokoro_onnx import Kokoro
    CACHE.mkdir(parents=True, exist_ok=True)
    for name, url in KOKORO_FILES.items():
        if not (CACHE / name).exists():
            urllib.request.urlretrieve(url, CACHE / name)
    if _kokoro is None:
        _kokoro = Kokoro(str(CACHE / "kokoro-v1.0.onnx"), str(CACHE / "voices-v1.0.bin"))
    samples, sr = _kokoro.create(text, voice=voice, speed=speed, lang="fr-fr")
    sf.write(str(wav), samples, sr)


def say(text: str, voix: str, wav: Path, vitesse: float = 1.0) -> Path:
    """voix = « piper:fr_FR-siwis-medium », « piper:fr_FR-upmc-medium#1 » (locuteur 1) ou « kokoro:ff_siwis »."""
    moteur, nom = voix.split(":", 1)
    if moteur == "piper":
        nom, _, spk = nom.partition("#")
        _piper(text, nom, wav, int(spk) if spk else None, length_scale=1 / vitesse)
    elif moteur == "kokoro":
        _kokoro_say(text, nom, wav, speed=vitesse)
    else:
        raise ValueError(f"moteur de voix inconnu : {moteur}")
    return wav


def duree(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def to_mp3(wav: Path) -> Path:
    mp3 = wav.with_suffix(".mp3")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(wav), "-ar", "44100", "-b:a", "128k", str(mp3)],
                   check=True)
    return mp3


def echantillons(texte: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    text = texte.read_text(encoding="utf-8").strip()
    voix = ["kokoro:ff_siwis", "piper:fr_FR-siwis-medium", "piper:fr_FR-tom-medium",
            "piper:fr_FR-upmc-medium#0", "piper:fr_FR-upmc-medium#1", "piper:fr_FR-gilles-low"]
    for v in voix:
        nom = v.replace(":", "_").replace("#", "_")
        try:
            mp3 = to_mp3(say(text, v, out / f"{nom}.wav"))
            (out / f"{nom}.wav").unlink()
            print(f"{v} → {mp3.name} ({duree(mp3):.1f} s)")
        except Exception as e:
            print(f"{v} : échec ({e})")


if __name__ == "__main__":
    if sys.argv[1:2] == ["echantillons"]:
        echantillons(Path(sys.argv[2]), Path(sys.argv[3]))
    else:
        sys.exit(__doc__)
