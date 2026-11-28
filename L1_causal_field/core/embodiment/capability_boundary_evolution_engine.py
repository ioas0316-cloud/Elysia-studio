r"""
ELYSIA Self-Capability Boundary Contrast, Diagnosis & Acquisition Engine
========================================================================

Implements the core meta-evolution loop:
  [What I CAN do]  <--Contrast-->  [What I CANNOT do yet]
         |
         v
  [WHY I cannot (Root Structural Defect / Missing Organ)]
         |
         v
  [HOW to become able -> Acquire New Capability -> Closed-Loop Verify]

Reads Elysia's OWN lived cognitive records (`cognitive_world/*.json`) to detect
real empirical failures/gaps, then executes and closed-loop verifies 3 genuine
`CANNOT -> CAN` capability acquisitions:

  1. Acquisition A (Noisy Real-World AST Generalization):
     Earlier 544-object reclassification failed AST synthesis (`synthesized: false`)
     due to brittle 100%-purity leaf rejection. Now uses weighted-entropy splits
     + majority leaves on a real 80/20 held-out test across all real objects!

  2. Acquisition B (Read-Only Binary String-Surface Receptor):
     Earlier `webm_encoder.exe` (13.4 MB) stayed stuck in `open_inquiry` because
     `--help`/`/?` emitted 0B stdout. Now deploys a read-only PE printable-string
     / flag surface receptor to uncover its real internal CLI flags & codec cues.

  3. Acquisition C (Motion-Synchronized Acoustic Weaving Bridge):
     Earlier `elysia_woven_3d_world.mp4` was silent video-only even though Elysia
     could observe audiovisual correlation (`r=+0.916`). Now extracts the real
     per-frame visual motion energy curve `m(t)`, weaves synchronized procedural
     PCM audio in NumPy, muxes `elysia_woven_3d_world_av.mp4` via FFmpeg, and
     closed-loop verifies `corr(visual_motion, audio_rms)`!
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import random
import re
import subprocess
import sys
import time
from typing import Any, Dict, List, Tuple
import wave

import cv2  # type: ignore
import numpy as np

THIS_DIR = Path(__file__).resolve().parent
L1_ROOT = THIS_DIR.parents[1]
WORKSPACE_ROOT = THIS_DIR.parents[2]
for _p in (str(THIS_DIR), str(L1_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from control_weave_and_multimodal_prism import (  # noqa: E402
    WOVEN_DIR,
    WOVEN_MP4_PATH,
    extract_synchronized_audiovisual_trajectory,
)
from core.embodiment.compositional_code_cortex import CompositionalCodeCortex  # noqa: E402
from core.embodiment.self_rewriting_architecture import (  # noqa: E402
    _compile_organ_callable,
    validate_organ_source,
)
from real_tool_organ import discover_real_tool_organs  # noqa: E402
from self_cognitive_expansion_cortex import (  # noqa: E402
    COGNITIVE_WORLD_DIR,
    _load_json,
    _save_json,
)
from universal_cross_intersection_reclassifier import (  # noqa: E402
    _kmeans_numpy,
    _auto_describe_cluster,
    extract_10d_physical_signature,
    gather_mass_heterogeneous_corpus,
)


EVOLUTION_REPORT_PATH = COGNITIVE_WORLD_DIR / "capability_boundary_evolution.json"
WOVEN_AV_MP4_PATH = WOVEN_DIR / "elysia_woven_3d_world_av.mp4"


# ---------------------------------------------------------------------------
# Step 1: Contrast CAN vs CANNOT strictly from Elysia's own live logs
# ---------------------------------------------------------------------------

def diagnose_capability_gaps_from_self_logs() -> List[Dict[str, Any]]:
    reclass = _load_json(COGNITIVE_WORLD_DIR / "universal_cross_intersection_reclassification.json", {})
    society = _load_json(COGNITIVE_WORLD_DIR / "dynamic_rotor_society.json", {})
    woven = _load_json(COGNITIVE_WORLD_DIR / "control_weave_and_multimodal_prism.json", {})
    contrast = _load_json(COGNITIVE_WORLD_DIR / "conservation_contrast_verification.json", {})

    gaps: List[Dict[str, Any]] = []

    # Gap 1: AST synthesis failed on 544 noisy real objects
    if not (reclass.get("generalized_ast_reclassifier_80_20") or {}).get("synthesized"):
        gaps.append(
            {
                "gap_id": "gap_noisy_544_ast_generalization",
                "can_do": "Synthesize exact AST organs on small clean datasets (9/9, 12/12)",
                "cannot_do": f"Synthesize generalized AST reclassifier across {reclass.get('total_real_objects_ingested', 544)} noisy real objects (synthesized=false)",
                "why_cannot": "CompositionalCodeCortex enforced 100% pure-leaf exact match and picked subset[0] on impure leaves",
                "how_to_acquire": "Use weighted-Shannon-entropy splits + majority-vote leaves + out-of-sample 80/20 held-out verification",
            }
        )

    # Gap 2: Opaque binary stuck in open_inquiry
    for r in society.get("active_open_inquiry_rotors") or []:
        gaps.append(
            {
                "gap_id": f"gap_opaque_binary_{r.get('contradiction_id')}",
                "can_do": "Discover CLI affordances on self-describing tools (git, ffmpeg, blender)",
                "cannot_do": f"Inspect opaque binary `{r.get('contradiction_id')}` emitting 0B on --help / ?",
                "why_cannot": "CLI receptor only reads stdout help text; lacks read-only binary literal/flag surface inspection",
                "how_to_acquire": "Acquire read-only PE printable ASCII flag/codec surface scanner",
            }
        )

    # Gap 3: Woven 3D PBR video has no synchronized audio track yet
    if (woven.get("part1_closed_loop_3d_pbr_weaving") or {}).get("status") == "ok":
        gaps.append(
            {
                "gap_id": "gap_silent_woven_3d_world",
                "can_do": "Observe audiovisual sync (r=+0.916) AND weave silent 3D PBR video separately",
                "cannot_do": "Weave motion-synchronized audio+video together as one coupled audiovisual world",
                "why_cannot": "3D weaving pipeline lacked a visual-motion-curve -> procedural PCM acoustic bridge",
                "how_to_acquire": "Drive NumPy harmonic/percussive audio envelope directly from real frame motion curve m(t), mux via FFmpeg, and verify corr(visual_motion, audio_rms)",
            }
        )

    # Gap 4: Moving-camera halo leakage in video separation (documented next frontier)
    leak = ((contrast.get("pass2_contrast_refined") or {}).get("inverse_bg_leakage_ratio"))
    if leak and leak > 0.05:
        gaps.append(
            {
                "gap_id": "gap_moving_camera_bg_leakage",
                "can_do": "Overlay-contrast separation on static-camera clips (PSNR 36.72~46.16 dB)",
                "cannot_do": f"Eliminate {leak*100:.1f}% halo leakage and separate actors during panning camera shots",
                "why_cannot": "Temporal median background assumes stationary camera",
                "how_to_acquire": "Add homography/optical-flow camera stabilization prior to background subtraction (queued next cycle)",
            }
        )
    return gaps


# ---------------------------------------------------------------------------
# Acquisition 1: 80/20 Held-Out AST Generalization on ALL Real Objects
# ---------------------------------------------------------------------------

def acquire_noisy_544_ast_generalization() -> Dict[str, Any]:
    corpus = gather_mass_heterogeneous_corpus()
    records: List[Dict[str, Any]] = []
    X_list: List[List[float]] = []
    for domain, fp in corpus:
        res = extract_10d_physical_signature(fp)
        if res is None:
            continue
        vec, meta = res
        X_list.append(vec)
        records.append({"domain": domain, "vec": vec, **meta})

    X_raw = np.array(X_list, dtype=np.float64)
    X_norm = (X_raw - np.mean(X_raw, axis=0)) / (np.std(X_raw, axis=0) + 1e-9)
    labels, _c = _kmeans_numpy(X_norm, k=5, seed=42)

    cluster_names: Dict[int, str] = {}
    for cid in range(5):
        idxs = [i for i, lb in enumerate(labels) if int(lb) == cid]
        if not idxs:
            continue
        cname = _auto_describe_cluster(np.mean(X_raw[idxs], axis=0))
        if cname in cluster_names.values():
            cname = f"{cname}_{cid}"
        cluster_names[cid] = cname

    pairs: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []
    for i, rec in enumerate(records):
        p = {
            "entropy_head": round(rec["vec"][1], 3),
            "entropy_gradient": round(rec["vec"][3], 3),
            "zlib_ratio": round(rec["vec"][4], 3),
            "ascii_ratio": round(rec["vec"][5], 3),
            "zero_sparsity": round(rec["vec"][7], 3),
        }
        pairs.append((p, {"reclassified_manifold": cluster_names[int(labels[i])]}))

    rng = random.Random(42)
    rng.shuffle(pairs)
    split = int(len(pairs) * 0.8)
    train_all, test_unseen = pairs[:split], pairs[split:]

    # Train on 160 diverse train samples with entropy-split + majority leaves (`min_accuracy=0.80`)
    cortex = CompositionalCodeCortex()
    cortex.learn_python_structure_from_files(sorted(THIS_DIR.glob("*.py"))[:12])
    prog = cortex.synthesize_decision_tree_ast(
        train_all[:160],
        purpose="acquired_544_object_generalized_reclassifier",
        min_accuracy=0.80,
        max_depth=4,
    )
    if prog is None:
        return {"acquired": False, "reason": "synthesis_failed"}

    fn = _compile_organ_callable(prog.source_code)
    train_hits = sum(1 for p_in, exp in train_all if fn(dict(p_in), {}) == exp)
    test_hits = sum(1 for p_in, exp in test_unseen if fn(dict(p_in), {}) == exp)
    test_pct = round(100.0 * test_hits / max(1, len(test_unseen)), 2)

    return {
        "gap_id": "gap_noisy_544_ast_generalization",
        "before_status": "CANNOT (synthesized: false on 544 real objects)",
        "after_status": f"CAN (unseen 20% held-out generalization = {test_pct}%)",
        "acquired": test_pct >= 80.0,
        "total_real_objects": len(pairs),
        "train_accuracy": f"{train_hits}/{len(train_all)} ({100.0 * train_hits / max(1, len(train_all)):.1f}%)",
        "unseen_20pct_heldout_accuracy": f"{test_hits}/{len(test_unseen)} ({test_pct:.1f}%)",
        "ast_node_count": prog.ast_node_count,
        "source_code": prog.source_code,
    }


# ---------------------------------------------------------------------------
# Acquisition 2: Read-Only PE Binary Printable-Flag / Codec Surface Receptor
# ---------------------------------------------------------------------------

def acquire_opaque_binary_string_surface(bin_path: Path) -> Dict[str, Any]:
    """Read-only inspection of printable ASCII flag & codec strings inside opaque PE binary."""
    if not bin_path.is_file():
        return {"acquired": False, "reason": f"binary_not_found:{bin_path}"}

    raw = bin_path.read_bytes()
    # Extract printable ASCII literals (>= 5 chars) strictly read-only
    ascii_runs = re.findall(rb"[ -~]{5,80}", raw)
    decoded = [s.decode("ascii", errors="ignore") for s in ascii_runs]

    cli_flags = sorted(
        {
            m.group(0)
            for s in decoded
            for m in re.finditer(r"(?<![a-zA-Z0-9_-])--[a-z][a-z0-9_-]{2,26}", s)
        }
    )
    codec_cues = sorted(
        {
            tok
            for s in decoded
            for tok in ("vp8", "vp9", "libvpx", "webm", "matroska", "opus", "vorbis", "av1", "yuv420", "bitrate", "framerate", "width", "height")
            if tok in s.lower()
        }
    )
    usage_lines = [s.strip() for s in decoded if ("usage:" in s.lower() or "webm" in s.lower()) and len(s.strip()) <= 80][:12]

    acquired = len(codec_cues) >= 2 or len(cli_flags) >= 2
    return {
        "gap_id": "gap_opaque_binary_contra_opaque_binary_webm_encoder",
        "target_binary": str(bin_path),
        "before_status": "CANNOT (0B stdout on --help / ?, stuck in open_inquiry)",
        "after_status": (
            f"CAN (discovered {len(codec_cues)} codec/media cues & {len(cli_flags)} embedded --flags read-only)"
            if acquired
            else "PARTIAL (binary strings sparse/obfuscated)"
        ),
        "acquired": acquired,
        "discovered_codec_and_media_cues": codec_cues,
        "sample_embedded_cli_flags": cli_flags[:20],
        "sample_usage_or_webm_literals": usage_lines[:8],
    }


# ---------------------------------------------------------------------------
# Acquisition 3: Motion-Synchronized Acoustic Weaving Bridge -> Verified AV MP4
# ---------------------------------------------------------------------------

def acquire_synchronized_audiovisual_weaving() -> Dict[str, Any]:
    """
    Closes the loop between visual weaving and audiovisual perception:
    1. Extracts real frame-by-frame motion energy `m(t)` from `elysia_woven_3d_world.mp4`.
    2. Weaves a synchronized 16kHz PCM audio track in NumPy whose amplitude and
       harmonic frequency follow `m(t)` continuously (with crisp silence/onset contrast).
    3. Muxes into `elysia_woven_3d_world_av.mp4` via FFmpeg 9.1.
    4. Runs `extract_synchronized_audiovisual_trajectory` right back on the
       woven AV video to closed-loop verify `corr(visual_motion, audio_rms)`!
    """
    ffmpeg_bin = discover_real_tool_organs().get("organs", {}).get("ffmpeg_4k_media", {}).get("binary")
    if not ffmpeg_bin or not WOVEN_MP4_PATH.is_file():
        return {"acquired": False, "reason": "ffmpeg_or_woven_mp4_missing"}

    # Step 1: Measure real per-frame visual motion energy curve m(t)
    cap = cv2.VideoCapture(str(WOVEN_MP4_PATH))
    fps = cap.get(cv2.CAP_PROP_FPS) or 12.0
    grays: List[np.ndarray] = []
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        grays.append(cv2.cvtColor(cv2.resize(fr, (240, 135)), cv2.COLOR_BGR2GRAY).astype(np.float32))
    cap.release()
    if len(grays) < 4:
        return {"acquired": False, "reason": "too_few_frames"}

    # Loop 3x (~4.0s total) with a gentle calm intro + dynamic motion arc so AV correlation is clearly measurable
    motion_curve = [0.0] + [float(np.mean(np.abs(grays[i] - grays[i - 1]))) for i in range(1, len(grays))]
    # Repeat 3 cycles so duration ~4.0s gives 16 crisp 0.25s audiovisual windows
    loop_count = 3
    dur_one = len(grays) / float(fps)
    total_dur = dur_one * loop_count
    sr = 16000
    n_samples = int(round(total_dur * sr))
    t = np.linspace(0.0, total_dur, n_samples, endpoint=False)

    # Interpolate frame motion curve across continuous sample time t
    full_motion = np.array(motion_curve * loop_count, dtype=np.float64)
    t_frames = np.linspace(0.0, total_dur, len(full_motion), endpoint=False)
    m_interp = np.interp(t, t_frames, full_motion)
    m_min, m_max = float(np.min(m_interp)), float(np.max(m_interp))
    m_norm = (m_interp - m_min) / max(1e-6, m_max - m_min)

    # Weave harmonic + shimmer audio physically coupled to visual motion envelope m_norm(t)
    amp_env = 0.01 + 0.38 * (m_norm ** 1.35)
    inst_freq = 180.0 + 340.0 * m_norm
    phase = 2.0 * np.pi * np.cumsum(inst_freq) / float(sr)
    wave_sig = amp_env * (0.65 * np.sin(phase) + 0.25 * np.sin(2.0 * phase) + 0.10 * np.sin(3.0 * phase))
    pcm_i16 = np.clip(wave_sig * 32767.0, -32767, 32767).astype(np.int16)

    wav_path = WOVEN_DIR / "elysia_woven_motion_sync.wav"
    with wave.open(str(wav_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm_i16.tobytes())

    # Mux looped 3D woven video + motion-synchronized audio into real H.264+AAC MP4!
    proc = subprocess.run(
        [
            ffmpeg_bin, "-y",
            "-stream_loop", str(loop_count - 1),
            "-i", str(WOVEN_MP4_PATH),
            "-i", str(wav_path),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
            "-c:a", "aac", "-b:a", "128k",
            "-shortest",
            str(WOVEN_AV_MP4_PATH),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if proc.returncode != 0 or not WOVEN_AV_MP4_PATH.is_file():
        return {"acquired": False, "reason": proc.stderr[-220:]}

    # CLOSED-LOOP MULTIMODAL VERIFICATION ON THE NEWLY WOVEN AV VIDEO!
    av_verify = extract_synchronized_audiovisual_trajectory(WOVEN_AV_MP4_PATH, ffmpeg_bin, window_s=0.25, max_windows=16)
    corr = float((av_verify or {}).get("visual_motion_vs_audio_rms_corr", 0.0))

    return {
        "gap_id": "gap_silent_woven_3d_world",
        "before_status": "CANNOT (woven 3D world video had 0 audio stream)",
        "after_status": f"CAN (woven H.264+AAC 3D world with closed-loop audiovisual sync r={corr:+.3f})",
        "acquired": av_verify is not None and corr > 0.30,
        "woven_av_mp4": str(WOVEN_AV_MP4_PATH),
        "woven_av_bytes": WOVEN_AV_MP4_PATH.stat().st_size,
        "closed_loop_multimodal_verification": av_verify,
    }


def run_capability_evolution_cycle() -> Dict[str, Any]:
    gaps = diagnose_capability_gaps_from_self_logs()
    acq1 = acquire_noisy_544_ast_generalization()
    acq2 = acquire_opaque_binary_string_surface(Path(r"C:\Users\USER\.gemini\antigravity\bin\webm_encoder.exe"))
    acq3 = acquire_synchronized_audiovisual_weaving()

    acquisitions = [acq1, acq2, acq3]
    closed_count = sum(1 for a in acquisitions if a.get("acquired"))

    report = {
        "schema": "elysia_capability_boundary_evolution_v1",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "principle": "Contrast(CAN vs CANNOT) -> Diagnose(WHY) -> Acquire(HOW) -> Closed-Loop Verify",
        "diagnosed_capability_gaps": gaps,
        "executed_acquisitions": acquisitions,
        "evolution_summary": {
            "gaps_diagnosed": len(gaps),
            "acquisitions_attempted": len(acquisitions),
            "cannot_turned_into_verified_can": closed_count,
            "remaining_next_frontier": "gap_moving_camera_bg_leakage (homography/optical-flow camera stabilization)",
        },
    }
    _save_json(EVOLUTION_REPORT_PATH, report)
    return report


if __name__ == "__main__":
    print(json.dumps(run_capability_evolution_cycle(), ensure_ascii=False, indent=2))
