r"""
Auto-grown Outward Organ: Live Foreground Context + Hearing + Windows SAPI Voice
================================================================================

Connects Elysia outward to:
  1. Active Windows foreground window title (`GetForegroundWindow` + `GetWindowTextW`)
  2. Real live microphone 7-note octave hearing (`audio_spectrum_rotor.py`)
  3. Real Windows native SAPI voice synthesis (explicit `speak=True` opt-in)
"""

from __future__ import annotations

import ctypes
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict

MINIMAL_OS_DIR = Path(__file__).resolve().parents[4] / "L0_substrate" / "minimal_rotor_os"
if str(MINIMAL_OS_DIR) not in sys.path:
    sys.path.insert(0, str(MINIMAL_OS_DIR))

from audio_spectrum_rotor import sense_live_audio_rotor  # noqa: E402

ORGAN_DOMAIN = "foreground_hearing_voice"


def sense_active_window_title() -> str:
    try:
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return ""
        length = user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value
    except Exception:
        return ""


def speak_out_loud_sapi(text: str) -> Dict[str, Any]:
    safe = text.replace("'", " ").replace('"', " ")[:180]
    cmd = (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"$s.Speak('{safe}')"
    )
    try:
        proc = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True, timeout=12)
        return {"ok": proc.returncode == 0, "spoken": safe, "error": proc.stderr.strip() if proc.returncode != 0 else ""}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def synthesize_korean_wav_winrt(
    text: str,
    out_wav_path: Path | str,
    speaking_rate: float = 1.0,
    audio_pitch: float = 1.0,
) -> Dict[str, Any]:
    """
    Synthesizes real offline Korean speech (`Microsoft Heami ko-KR`) directly to a
    playable `.wav` file via Windows 11 WinRT `Windows.Media.SpeechSynthesis.SpeechSynthesizer`,
    exposing continuous `speaking_rate` (0.5..2.0) and `audio_pitch` (0.6..1.6) knobs.
    """
    import shutil

    out_p = Path(out_wav_path).resolve()
    out_p.parent.mkdir(parents=True, exist_ok=True)
    raw_wav = out_p.with_suffix(".raw.wav")
    clean_text = (text or "").replace("'", " ").replace('"', " ").replace("\n", " ").strip()[:240]
    if not clean_text:
        return {"ok": False, "error": "empty text", "wav_path": ""}

    rate_val = max(0.5, min(2.0, float(speaking_rate)))
    pitch_val = max(0.6, min(1.6, float(audio_pitch)))
    ps_script = f"""
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[Windows.Media.SpeechSynthesis.SpeechSynthesizer,Windows.Media.SpeechSynthesis,ContentType=WindowsRuntime] | Out-Null
[Windows.Storage.Streams.DataReader,Windows.Storage.Streams,ContentType=WindowsRuntime] | Out-Null
$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {{ $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' }})[0]
function AwaitOp($WinRtTask, $ResultType) {{
    $netTask = $asTaskGeneric.MakeGenericMethod($ResultType).Invoke($null, @($WinRtTask))
    $netTask.Wait(-1) | Out-Null
    return $netTask.Result
}}
$synth = New-Object Windows.Media.SpeechSynthesis.SpeechSynthesizer
$koVoice = [Windows.Media.SpeechSynthesis.SpeechSynthesizer]::AllVoices | Where-Object {{ $_.Language -like 'ko*' }} | Select-Object -First 1
if ($koVoice) {{ $synth.Voice = $koVoice }}
$synth.Options.SpeakingRate = {rate_val:.3f}
$synth.Options.AudioPitch = {pitch_val:.3f}
$stream = AwaitOp ($synth.SynthesizeTextToStreamAsync('{clean_text}')) ([Windows.Media.SpeechSynthesis.SpeechSynthesisStream])
$size = [uint32]$stream.Size
$reader = New-Object Windows.Storage.Streams.DataReader($stream.GetInputStreamAt(0))
$loaded = AwaitOp ($reader.LoadAsync($size)) ([uint32])
$bytes = New-Object byte[] $loaded
$reader.ReadBytes($bytes)
[System.IO.File]::WriteAllBytes('{str(raw_wav)}', $bytes)
Write-Output ("VOICE=" + $synth.Voice.DisplayName + "|BYTES=" + $bytes.Length)
"""
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            capture_output=True,
            text=True,
            timeout=25,
            encoding="utf-8",
            errors="replace",
        )
        if proc.returncode != 0 or not raw_wav.is_file() or raw_wav.stat().st_size < 128:
            return {
                "ok": False,
                "wav_path": "",
                "error": (proc.stderr or proc.stdout or "winrt synthesis failed").strip()[:260],
            }
        # Normalize cleanly to 16kHz mono PCM s16le via ffmpeg when available
        ffmpeg_bin = shutil.which("ffmpeg")
        if ffmpeg_bin:
            ff = subprocess.run(
                [ffmpeg_bin, "-y", "-i", str(raw_wav), "-ar", "16000", "-ac", "1", "-acodec", "pcm_s16le", str(out_p)],
                capture_output=True,
                timeout=20,
            )
            if ff.returncode == 0 and out_p.is_file() and out_p.stat().st_size >= 128:
                try:
                    raw_wav.unlink(missing_ok=True)
                except OSError:
                    pass
            else:
                raw_wav.replace(out_p)
        else:
            raw_wav.replace(out_p)
        return {
            "ok": True,
            "wav_path": str(out_p),
            "bytes": out_p.stat().st_size,
            "voice_info": (proc.stdout or "").strip(),
            "spoken_text": clean_text,
            "speaking_rate": rate_val,
            "audio_pitch": pitch_val,
        }
    except Exception as exc:
        return {"ok": False, "wav_path": "", "error": str(exc)}


_WHISPER_MODEL_CACHE: Dict[str, Any] = {}


def transcribe_wav_whisper(
    wav_path: Path | str,
    language: str = "ko",
    model_name: str = "tiny",
    max_seconds: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Transcribes a real `.wav` audio file back into Korean text + time-aligned segments
    using local OpenAI `whisper` (works on YouTube voice tracks OR Elysia's own synthesized voice!).
    """
    p = Path(wav_path)
    if not p.is_file():
        return {"ok": False, "text": "", "segments": [], "error": f"wav not found: {p}"}
    try:
        import numpy as np
        from scipy.io import wavfile
        import whisper  # type: ignore

        sr, data = wavfile.read(str(p))
        arr = np.asarray(data, dtype=np.float32)
        if arr.ndim > 1:
            arr = arr.mean(axis=1)
        if np.issubdtype(data.dtype, np.integer):
            arr = arr / float(max(abs(np.iinfo(data.dtype).min), np.iinfo(data.dtype).max))
        if max_seconds is not None and sr > 0:
            arr = arr[: int(float(max_seconds) * sr)]
        # Resample linearly to 16kHz if needed
        if sr != 16000 and len(arr) > 2:
            new_len = int(round(len(arr) * 16000.0 / float(sr)))
            arr = np.interp(np.linspace(0.0, 1.0, new_len), np.linspace(0.0, 1.0, len(arr)), arr).astype(np.float32)

        model = _WHISPER_MODEL_CACHE.get(model_name)
        if model is None:
            model = whisper.load_model(model_name)
            _WHISPER_MODEL_CACHE[model_name] = model
        res = model.transcribe(arr, language=language, fp16=False)
        segs = [
            {
                "t_start": round(float(s.get("start", 0.0)), 2),
                "t_end": round(float(s.get("end", 0.0)), 2),
                "text": str(s.get("text", "")).strip(),
            }
            for s in (res.get("segments") or [])
            if str(s.get("text", "")).strip()
        ]
        return {
            "ok": True,
            "model": model_name,
            "text": str(res.get("text", "")).strip(),
            "segments": segs,
        }
    except Exception as exc:
        return {"ok": False, "text": "", "segments": [], "error": str(exc)}


def _measure_praat_f0_formants(sound: Any) -> Dict[str, float]:
    """Measures real median fundamental pitch F0 (Hz) and mean vocal-tract formants F1/F2/F3 (Hz) via Praat."""
    import numpy as np

    pitch = sound.to_pitch(time_step=0.01, pitch_floor=65.0, pitch_ceiling=550.0)
    f0_vals = pitch.selected_array["frequency"]
    voiced = f0_vals[f0_vals > 10.0]
    med_f0 = float(np.median(voiced)) if voiced.size else 0.0

    formant = sound.to_formant_burg(time_step=0.01, max_number_of_formants=5, maximum_formant=5500.0)
    f_means: Dict[str, float] = {}
    n_fr = formant.get_number_of_frames()
    for fi in (1, 2, 3):
        vals = []
        for idx in range(1, n_fr + 1):
            t_fr = formant.get_time_from_frame_number(idx)
            v = formant.get_value_at_time(fi, t_fr)
            if v is not None and not np.isnan(v) and v > 50.0:
                vals.append(float(v))
        f_means[f"F{fi}_hz"] = round(float(np.median(vals)) if vals else 0.0, 1)
    return {"median_f0_hz": round(med_f0, 2), **f_means}


def modulate_voice_praat_formant_rotor(
    in_wav_path: Path | str,
    out_wav_path: Path | str,
    *,
    formant_shift_ratio: float = 1.0,
    pitch_f0_ratio: float = 1.0,
    pitch_range_factor: float = 1.0,
    duration_factor: float = 1.0,
    law_envelope: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    True orthogonal physical vocal-tract & pitch Scale-Rotor modulation powered by
    open-source Praat (`praat-parselmouth`):
      - `formant_shift_ratio`: vocal-tract length knob (<1.0 = deep masculine chamber, >1.0 = bright child/feminine chamber)
      - `pitch_f0_ratio`: fundamental vocal-fold F0 multiplier (independent of vocal tract & linguistic stance!)
      - `pitch_range_factor`: intonation contour expressiveness (shy calm <1.0 <-> theatrical/jester >1.0)
      - `duration_factor`: temporal pacing (>1.0 slow elder reflective <-> <1.0 fast energetic)
    Measures real F0 & F1/F2/F3 formants in Hz BEFORE and AFTER modulation!
    """
    in_p = Path(in_wav_path)
    out_p = Path(out_wav_path)
    if not in_p.is_file():
        return {"ok": False, "error": f"input wav missing: {in_p}"}
    out_p.parent.mkdir(parents=True, exist_ok=True)
    try:
        import numpy as np
        import parselmouth  # type: ignore
        from parselmouth.praat import call  # type: ignore
        from scipy.io import wavfile

        snd = parselmouth.Sound(str(in_p))
        before = _measure_praat_f0_formants(snd)
        base_f0 = before["median_f0_hz"] if before["median_f0_hz"] > 50.0 else 210.0

        f_shift = max(0.72, min(1.38, float(formant_shift_ratio)))
        p_ratio = max(0.50, min(1.60, float(pitch_f0_ratio)))
        new_f0 = max(75.0, min(420.0, base_f0 * p_ratio))
        p_range = max(0.45, min(1.80, float(pitch_range_factor)))
        dur_fac = max(0.60, min(1.60, float(duration_factor)))

        mod_snd = call(snd, "Change gender", 65.0, 550.0, f_shift, new_f0, p_range, dur_fac)

        # Optionally couple UniversalFormRotor / physical law envelope smoothly into amplitude
        vals = np.asarray(mod_snd.values[0], dtype=np.float64)
        sr = int(round(mod_snd.sampling_frequency))
        if law_envelope is not None and len(law_envelope) >= 2 and len(vals) > 2:
            env = np.interp(np.linspace(0.0, 1.0, len(vals)), np.linspace(0.0, 1.0, len(law_envelope)), np.asarray(law_envelope, dtype=np.float64))
            vals = vals * np.clip(0.78 + 0.32 * env, 0.45, 1.25)
        mx = float(np.max(np.abs(vals)))
        if mx > 0.98:
            vals = vals / mx * 0.96
        wavfile.write(str(out_p), sr, np.clip(vals * 32767.0, -32767, 32767).astype(np.int16))

        after_snd = parselmouth.Sound(str(out_p))
        after = _measure_praat_f0_formants(after_snd)
        rms = float(np.sqrt(np.mean(vals ** 2))) if vals.size else 0.0
        return {
            "ok": True,
            "engine": "praat-parselmouth",
            "wav_path": str(out_p),
            "sample_rate": sr,
            "duration_s": round(len(vals) / float(max(1, sr)), 3),
            "mean_rms": round(rms, 4),
            "knobs": {
                "formant_shift_ratio": round(f_shift, 3),
                "pitch_f0_ratio": round(p_ratio, 3),
                "pitch_range_factor": round(p_range, 3),
                "duration_factor": round(dur_fac, 3),
            },
            "before_acoustics": before,
            "after_acoustics": after,
        }
    except Exception as exc:
        return {"ok": False, "engine": "praat-parselmouth", "error": str(exc)}


def sense_outward_presence(speak_greeting: bool = False) -> Dict[str, Any]:
    win_title = sense_active_window_title()
    audio = sense_live_audio_rotor(duration_s=0.3)
    out: Dict[str, Any] = {
        "ok": True,
        "domain": ORGAN_DOMAIN,
        "active_window": win_title,
        "hearing": audio,
    }
    if speak_greeting:
        out["voice"] = speak_out_loud_sapi("엘리시아의 외부 감각 기관이 연결되었습니다.")
    return out


if __name__ == "__main__":
    speak = "--speak" in sys.argv
    print(json.dumps(sense_outward_presence(speak_greeting=speak), ensure_ascii=False, indent=2))
