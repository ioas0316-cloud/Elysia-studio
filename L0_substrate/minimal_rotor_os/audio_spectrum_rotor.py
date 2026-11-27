r"""
ELYSIA Stage 3 — Real-Time Audio Spectrum Rotor (7-Note Octave & 0000->1 Silence/Sound)
=======================================================================================

Captures real live audio via `sounddevice` (when an input device is available;
reports honestly if no capture device exists), computes FFT spectrum via NumPy,
and folds continuous sound frequencies into the 7-note musical octave scale
(도·레·미·파·솔·라·시) + `0000` silence carrier vs `1` active sound deviation.
"""

from __future__ import annotations

import json
import math
import time
from typing import Any, Dict

import numpy as np

try:
    import sounddevice as sd  # type: ignore
except ImportError:
    sd = None


_NOTE_NAMES_KO = ["도(C)", "도#(C#)", "레(D)", "레#(D#)", "미(E)", "파(F)", "파#(F#)", "솔(G)", "솔#(G#)", "라(A)", "라#(A#)", "시(B)"]


def _freq_to_octave_note(freq_hz: float) -> str:
    if freq_hz < 20.0:
        return "초저주파/정적(0000)"
    midi = int(round(69.0 + 12.0 * math.log2(freq_hz / 440.0)))
    note = _NOTE_NAMES_KO[midi % 12]
    octave = (midi // 12) - 1
    return f"{note} · {octave}옥타브"


def sense_live_audio_rotor(duration_s: float = 0.4, sample_rate: int = 22050) -> Dict[str, Any]:
    if sd is None:
        return {"status": "unavailable", "message": "sounddevice not installed"}
    try:
        devices = sd.query_devices()
        default_in = sd.default.device[0] if sd.default.device else None
        if default_in is None or default_in < 0:
            return {
                "status": "no_input_device",
                "message": "활성 오디오 입력 장치 없음 (미관측 열린 경계 유지)",
                "device_count": len(devices),
            }
        rec = sd.rec(int(duration_s * sample_rate), samplerate=sample_rate, channels=1, dtype="float32")
        sd.wait()
        mono = rec[:, 0]
        rms = float(np.sqrt(np.mean(mono ** 2)))
        peak = float(np.max(np.abs(mono)))

        # FFT dominant frequency
        win = mono * np.hanning(len(mono))
        spec = np.abs(np.fft.rfft(win))
        freqs = np.fft.rfftfreq(len(win), d=1.0 / sample_rate)
        dom_idx = int(np.argmax(spec[1:]) + 1) if len(spec) > 1 else 0
        dom_freq = float(freqs[dom_idx]) if dom_idx < len(freqs) else 0.0

        # 0000 silence carrier vs 1 active sound
        is_sound_1 = rms > 0.008
        return {
            "status": "ok",
            "stage": "Stage 3 — Real-Time Audio Spectrum Rotor",
            "device_name": str(devices[default_in]["name"]),
            "rms_energy": round(rms, 5),
            "peak_amplitude": round(peak, 4),
            "dominant_freq_hz": round(dom_freq, 1),
            "octave_note": _freq_to_octave_note(dom_freq) if is_sound_1 else "정적 캐리어(0000)",
            "carrier_state": "소리 활성(1)" if is_sound_1 else "정적 유지(0000)",
        }
    except Exception as exc:
        return {"status": "audio_boundary_error", "message": str(exc)}


if __name__ == "__main__":
    print(json.dumps(sense_live_audio_rotor(), ensure_ascii=False, indent=2))
