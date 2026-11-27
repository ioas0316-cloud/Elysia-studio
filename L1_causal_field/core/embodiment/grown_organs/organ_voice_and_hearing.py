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
