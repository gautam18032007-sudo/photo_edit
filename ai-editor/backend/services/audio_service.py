"""
Audio processing service using librosa and soundfile.
"""
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def load_audio(path: str):
    """Returns (audio_array, sample_rate)."""
    audio, sr = librosa.load(path, sr=None, mono=False)
    return audio, sr

def save_audio(audio: np.ndarray, sr: int, output_path: str):
    if audio.ndim == 2:
        audio = audio.T  # (channels, samples) -> (samples, channels)
    sf.write(output_path, audio, sr)

def noise_reduction(input_path: str, output_path: str, strength: float = 0.75) -> str:
    """Spectral subtraction-based noise reduction."""
    audio, sr = load_audio(input_path)
    if audio.ndim > 1:
        audio = librosa.to_mono(audio)
    # Estimate noise from first 0.5s
    noise_sample = audio[:int(sr * 0.5)]
    noise_stft = np.abs(librosa.stft(noise_sample))
    noise_profile = np.mean(noise_stft, axis=1, keepdims=True)
    # Apply spectral subtraction
    stft = librosa.stft(audio)
    mag = np.abs(stft)
    phase = np.angle(stft)
    mag_clean = np.maximum(mag - strength * noise_profile, 0.0)
    clean_stft = mag_clean * np.exp(1j * phase)
    clean_audio = librosa.istft(clean_stft)
    save_audio(clean_audio, sr, output_path)
    return output_path

def trim_silence(input_path: str, output_path: str, top_db: float = 20.0) -> str:
    audio, sr = load_audio(input_path)
    if audio.ndim > 1:
        audio = librosa.to_mono(audio)
    trimmed, _ = librosa.effects.trim(audio, top_db=top_db)
    save_audio(trimmed, sr, output_path)
    return output_path

def adjust_volume(input_path: str, output_path: str, gain_db: float = 0.0) -> str:
    audio, sr = load_audio(input_path)
    factor = 10 ** (gain_db / 20.0)
    audio = np.clip(audio * factor, -1.0, 1.0)
    save_audio(audio, sr, output_path)
    return output_path

def analyze_audio(input_path: str) -> dict:
    audio, sr = load_audio(input_path)
    if audio.ndim > 1:
        mono = librosa.to_mono(audio)
    else:
        mono = audio
    duration = librosa.get_duration(y=mono, sr=sr)
    rms = float(np.sqrt(np.mean(mono ** 2)))
    tempo, _ = librosa.beat.beat_track(y=mono, sr=sr)
    return {
        "duration_seconds": round(duration, 2),
        "sample_rate": sr,
        "channels": audio.ndim,
        "rms_level": round(rms, 4),
        "estimated_tempo_bpm": round(float(tempo), 1),
    }
