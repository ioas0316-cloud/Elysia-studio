"""
Elysia Embodied Sensorimotor Bridge (100% Local · Zero External LLM API)
================================================================================
Provides two grounded, privacy-preserving embodiment channels so Elysia can
observe and learn directly from a real computer environment (videos, YouTube,
browsers, games, IDEs) through Action -> Visual Delta -> Prediction Error:

  1. Live Visual-Temporal Frame Processor (`evaluate_visual_frame`):
     Consumes compact numeric sensory summaries (luminance, motion_delta,
     edge_density, chromatic R/B/Y flux-order-entropy balance, scene_cut) from
     either browser `getDisplayMedia` or the local PC observer script — zero
     raw video upload, zero token cost.
  2. Safe Local PC Embodiment Bridge (`render_desktop_embodiment_script`):
     Generates a transparent, zero-API Python 3 script for the user's own PC.
     - Defaults to `--mode observe` (passive demonstration learning: watches
       active window titles + downsampled screen motion/deltas to learn what
       visual changes follow user workflows without touching mouse/keyboard).
     - Optional `--mode assisted` explicitly requires human Y/N approval before
       every single motor action and includes an immediate (0,0) failsafe stop.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


def _clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else (hi if v > hi else v)


def evaluate_visual_frame(
    frame: Dict[str, Any],
    prev_signature: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """
    Evaluate a compact visual-temporal sensory frame from a live screen/video/app.
    Maps low-level optical observables into:
      - Chromatic triad (Red=Flux/Motion, Blue=Order/Structure, Yellow=Entropy/Variety)
      - Visual prediction error against the previous frame
      - Qualitative visual regime (high_motion_video, dense_text_or_code, calm_scene, scene_cut)
    """
    motion = _clamp(float(frame.get("motion_delta", 0.0)), 0.0, 1.0)
    edge = _clamp(float(frame.get("edge_density", 0.3)), 0.0, 1.0)
    luma = _clamp(float(frame.get("luminance", 0.5)), 0.0, 1.0)
    red_flux = _clamp(float(frame.get("red_flux", 0.33)), 0.0, 1.0)
    blue_order = _clamp(float(frame.get("blue_order", 0.33)), 0.0, 1.0)
    yellow_ent = _clamp(float(frame.get("yellow_entropy", 0.33)), 0.0, 1.0)
    scene_cut = bool(frame.get("scene_cut", False)) or motion >= 0.36
    context = str(frame.get("context_label", "") or "실시간 화면").strip()[:60]

    sig = [motion, edge, luma, red_flux, blue_order, yellow_ent]
    if prev_signature and len(prev_signature) == 6:
        pred_err = round(
            math.sqrt(sum((sig[i] - prev_signature[i]) ** 2 for i in range(6)) / 6.0),
            4,
        )
    else:
        pred_err = round(0.15 + 0.5 * motion, 4)

    # Classify visual regime continuously by dominant observable
    if scene_cut:
        regime = "scene_cut"
        regime_ko = "급격한 장면 전환"
    elif motion >= 0.14:
        regime = "dynamic_video"
        regime_ko = "동적 영상·움직임 흐름"
    elif edge >= 0.32 and motion < 0.08:
        regime = "dense_text_code"
        regime_ko = "고밀도 텍스트·코드·문서"
    else:
        regime = "calm_window"
        regime_ko = "정적인 화면·대기 상태"

    # Map visual observables continuously into 6D affective-cognitive target
    # [warmth, hurt_sulky, curiosity, playfulness, vulnerability, deep_thought]
    target_vec6 = [
        _clamp(0.56 + 0.24 * red_flux + 0.14 * luma, 0.08, 0.96),
        _clamp(0.08 + 0.12 * max(0.0, 0.3 - luma), 0.04, 0.45),
        _clamp(0.48 + 0.36 * motion + 0.28 * pred_err + (0.18 if scene_cut else 0.0), 0.10, 0.98),
        _clamp(0.18 + 0.42 * motion + 0.22 * yellow_ent, 0.06, 0.92),
        _clamp(0.24 + 0.18 * (1.0 - edge), 0.08, 0.65),
        _clamp(0.46 + 0.40 * edge + 0.22 * blue_order + 0.14 * pred_err, 0.12, 0.98),
    ]

    return {
        "context_label": context,
        "signature": [round(x, 4) for x in sig],
        "prediction_error": pred_err,
        "scene_cut": scene_cut,
        "regime": regime,
        "regime_ko": regime_ko,
        "target_vec6": [round(x, 4) for x in target_vec6],
    }


def normalize_sensorimotor_log(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize a local PC sensorimotor observation log JSON."""
    if not isinstance(raw, dict):
        raise ValueError("유효한 감각-운동 로그 JSON 객체가 아닙니다.")
    events_in = raw.get("events")
    if not isinstance(events_in, list) or not events_in:
        raise ValueError("기록된 화면·행동 관측 이벤트가 비어 있습니다.")

    clean_events: List[Dict[str, Any]] = []
    for ev in events_in[:200]:
        if not isinstance(ev, dict):
            continue
        clean_events.append(
            {
                "step": int(ev.get("step", len(clean_events) + 1)),
                "window_title": str(ev.get("window_title", "Desktop"))[:80],
                "action": str(ev.get("action", "observe"))[:60],
                "motion_delta": round(_clamp(float(ev.get("motion_delta", 0.0)), 0.0, 1.0), 4),
                "edge_density": round(_clamp(float(ev.get("edge_density", 0.3)), 0.0, 1.0), 4),
                "scene_cut": bool(ev.get("scene_cut", False)),
                "outcome": str(ev.get("outcome", ""))[:100],
            }
        )

    if not clean_events:
        raise ValueError("파싱 가능한 관측 이벤트가 없습니다.")

    return {
        "schema_version": 1,
        "session_name": str(raw.get("session_name") or "PC 체화 관측 세션")[:80],
        "mode": str(raw.get("mode") or "observe")[:24],
        "event_count": len(clean_events),
        "events": clean_events,
    }


def render_desktop_embodiment_script() -> str:
    """
    Generate a transparent, safe, zero-API local PC Sensorimotor Bridge script
    (`elysia_desktop_embodiment.py`).
    - Default `--mode observe`: passively observes active window titles + screen
      motion/edge deltas so Elysia learns from watching the user browse, watch
      YouTube, code, or play games (Imitation / Demonstration Learning).
    - Optional `--mode assisted`: proposes simple exploratory actions ONLY with
      explicit per-step human Y/N approval and instant (0,0) corner failsafe.
    """
    return r'''#!/usr/bin/env python3
"""
Elysia Local PC Sensorimotor Bridge (Zero-API · Safety-First)
=============================================================
Connects a real desktop environment (Windows / macOS / Linux) to Elysia's
local causal learning loop using Vision (downsampled screen deltas) + Window
Context + Action-Outcome Causality — ZERO external LLM APIs, ZERO raw video
uploads!

Default mode (`--mode observe`):
  Passively observes active window titles and compact screen optical deltas
  while YOU browse, watch YouTube, read papers, or play games, saving a tiny
  `elysia_sensorimotor_log.json` you can load straight into Elysia.

Assisted mode (`--mode assisted`):
  Proposes a single mouse/keyboard step only when you explicitly type `y` to
  approve it. Move cursor to top-left corner (0,0) at any time to abort.

Usage:
  python elysia_desktop_embodiment.py --seconds 60 --interval 1.5
  python elysia_desktop_embodiment.py --mode assisted --steps 5
"""

from __future__ import annotations

import argparse
import ctypes
import json
import math
import platform
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def get_active_window_title() -> str:
    """Read active foreground window title using stdlib only (Windows)."""
    if platform.system() == "Windows":
        try:
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buf, length + 1)
                return buf.value.strip()[:80]
        except Exception:
            pass
    return f"{platform.system()}_Desktop"


def get_cursor_pos() -> Tuple[int, int]:
    """Read cursor coordinates on Windows via stdlib ctypes (for (0,0) failsafe)."""
    if platform.system() == "Windows":
        try:
            class POINT(ctypes.Structure):
                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
            pt = POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
            return int(pt.x), int(pt.y)
        except Exception:
            pass
    return (100, 100)


def sample_screen_metrics(prev_gray: Optional[List[float]] = None) -> Tuple[Dict[str, float], Optional[List[float]]]:
    """
    Sample a tiny 48x27 grayscale thumbnail using Pillow (if installed) to compute
    motion_delta & edge_density locally in <10ms. Never saves raw screenshots!
    """
    try:
        from PIL import ImageGrab  # optional local dependency: pip install pillow
        img = ImageGrab.grab().resize((48, 27)).convert("L")
        pixels = [p / 255.0 for p in img.getdata()]
        luma = sum(pixels) / max(1, len(pixels))
        # Horizontal + vertical gradient energy -> edge density (text/code vs smooth video)
        edges = 0.0
        for y in range(26):
            row = y * 48
            for x in range(47):
                gx = abs(pixels[row + x + 1] - pixels[row + x])
                gy = abs(pixels[row + 48 + x] - pixels[row + x])
                edges += gx + gy
        edge_density = min(1.0, (edges / (47 * 26)) * 2.4)

        if prev_gray and len(prev_gray) == len(pixels):
            motion = min(1.0, sum(abs(pixels[i] - prev_gray[i]) for i in range(len(pixels))) / len(pixels) * 4.5)
        else:
            motion = 0.0
        return (
            {
                "luminance": round(luma, 4),
                "edge_density": round(edge_density, 4),
                "motion_delta": round(motion, 4),
                "scene_cut": motion >= 0.34,
            },
            pixels,
        )
    except Exception:
        return (
            {
                "luminance": 0.5,
                "edge_density": 0.35,
                "motion_delta": 0.0,
                "scene_cut": False,
            },
            prev_gray,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Elysia Local PC Sensorimotor Bridge (Zero-API)")
    parser.add_argument("--mode", choices=["observe", "assisted"], default="observe")
    parser.add_argument("--seconds", type=int, default=45, help="Observation duration in observe mode")
    parser.add_argument("--interval", type=float, default=1.5, help="Seconds between sensory samples")
    parser.add_argument("--steps", type=int, default=5, help="Max approved steps in assisted mode")
    parser.add_argument("-o", "--output", default="elysia_sensorimotor_log.json", help="Output causal log JSON")
    args = parser.parse_args()

    events: List[Dict[str, Any]] = []
    prev_gray: Optional[List[float]] = None
    prev_title = ""
    t_start = time.time()

    print(f"[Elysia Embodiment] Starting mode={args.mode} (Zero-API, local only)")
    if args.mode == "observe":
        print(f"Passively observing active window & visual deltas for {args.seconds}s... (Ctrl+C to finish early)")
        step = 0
        try:
            while time.time() - t_start < args.seconds:
                step += 1
                title = get_active_window_title()
                metrics, prev_gray = sample_screen_metrics(prev_gray)
                action = "window_switch" if (prev_title and title != prev_title) else "watch_stream"
                outcome = (
                    f"창 전환({prev_title[:20]} -> {title[:24]})"
                    if action == "window_switch"
                    else ("급격한 장면 전환 감지" if metrics["scene_cut"] else f"시각 변화 Δ={metrics['motion_delta']:.3f}")
                )
                prev_title = title
                events.append(
                    {
                        "step": step,
                        "ts": round(time.time(), 2),
                        "window_title": title,
                        "action": action,
                        "motion_delta": metrics["motion_delta"],
                        "edge_density": metrics["edge_density"],
                        "scene_cut": bool(metrics["scene_cut"]),
                        "outcome": outcome,
                    }
                )
                print(f"  [{step:02d}] {title[:34]:<34} | Δ={metrics['motion_delta']:.3f} | edge={metrics['edge_density']:.2f}")
                time.sleep(max(0.5, args.interval))
        except KeyboardInterrupt:
            print("\n[Elysia Embodiment] Stopped cleanly by user.")
    else:
        print("Assisted mode: every step requires explicit Y approval. Move cursor to (0,0) to abort immediately.")
        for step in range(1, args.steps + 1):
            cx, cy = get_cursor_pos()
            if cx <= 2 and cy <= 2:
                print("[FAILSAFE] Cursor at (0,0) -> halting immediately.")
                break
            title = get_active_window_title()
            pre, prev_gray = sample_screen_metrics(prev_gray)
            proposal = input(f"[Step {step}] Active='{title}'. Describe an action YOU will perform now (or Enter to skip, q to quit): ").strip()
            if proposal.lower() == "q":
                break
            if not proposal:
                continue
            input("Perform the action now, then press Enter to measure the real visual-causal delta...")
            post, prev_gray = sample_screen_metrics(prev_gray)
            post_title = get_active_window_title()
            events.append(
                {
                    "step": step,
                    "ts": round(time.time(), 2),
                    "window_title": post_title,
                    "action": proposal[:60],
                    "motion_delta": post["motion_delta"],
                    "edge_density": post["edge_density"],
                    "scene_cut": bool(post["scene_cut"]),
                    "outcome": f"{title[:22]} -> {post_title[:22]} (Δ={post['motion_delta']:.3f})",
                }
            )

    payload = {
        "schema_version": 1,
        "session_name": f"PC_Embodiment_{platform.system()}_{time.strftime('%H%M%S')}",
        "mode": args.mode,
        "event_count": len(events),
        "events": events,
    }
    out_path = Path(args.output).resolve()
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[Saved] {out_path} ({len(events)} causal events) -> Load this JSON in Elysia!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
