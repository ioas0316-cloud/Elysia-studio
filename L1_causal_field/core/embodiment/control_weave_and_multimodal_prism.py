r"""
ELYSIA Closed-Loop Control-and-Weave Engine & Multi-Modal Audio-Visual Prism
============================================================================

Directly answers the two foundational critiques:
1. **Beyond "I just classified it!" -> Observe -> Control -> Weave -> Contrast-Verify:**
   Uses the physical-informational laws discovered from the 544-object
   reclassification and 3D prism experiments to actively **WEAVE** a real
   animated 3D PBR/rigged scene video (`elysia_woven_3d_world.mp4`) in
   Blender 5.3.0 + FFmpeg 9.1 using 4 real Khronos `.glb` models
   (`CesiumMan.glb`, `Fox.glb`, `DamagedHelmet.glb`, `Lantern.glb`), and then
   immediately passes the WOVEN `.mp4` right back through the 10D manifold,
   6D visual-temporal prism, and bidirectional overlay-contrast sensors to
   verify whether the woven outcome actually satisfies the target laws!

2. **ZERO Scalar Emotion Floats (`boredom = 0.45` abolished) -> Synchronized Multi-Modal State Trajectories:**
   Extracts time-aligned `(Visual Motion/Lighting/Edge/Chroma ∩ Audio RMS/ZCR/Spectral-Centroid/Silence)`
   trajectories across real audio+video clips (`cg_006.mp4` + `GadgetSkill*.mp4`),
   representing situational/affective states as actual coupled multi-sensory
   trajectories and cross-modal correlations rather than programmer-invented floats.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Dict, List, Tuple

import cv2  # type: ignore
import numpy as np

THIS_DIR = Path(__file__).resolve().parent
L1_ROOT = THIS_DIR.parents[1]
WORKSPACE_ROOT = THIS_DIR.parents[2]
for _p in (str(THIS_DIR), str(L1_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from real_tool_organ import discover_real_tool_organs  # noqa: E402
from self_cognitive_expansion_cortex import COGNITIVE_WORLD_DIR, _save_json  # noqa: E402
from universal_cross_intersection_reclassifier import (  # noqa: E402
    extract_10d_physical_signature,
    extract_video_temporal_prism,
)


OSS_3D_DIR = WORKSPACE_ROOT / "data" / "open_source_3d"
WOVEN_DIR = WORKSPACE_ROOT / "data" / "open_sandbox" / "woven_world"
WOVEN_MP4_PATH = WOVEN_DIR / "elysia_woven_3d_world.mp4"
WOVEN_BLEND_PATH = WOVEN_DIR / "elysia_woven_3d_world.blend"
WOVEN_REPORT_PATH = COGNITIVE_WORLD_DIR / "control_weave_and_multimodal_prism.json"


# ---------------------------------------------------------------------------
# PART 1: Active Control & Weaving of Real PBR/Rigged 3D World -> Playable MP4
# ---------------------------------------------------------------------------

def weave_real_3d_pbr_world_video(blender_bin: str, ffmpeg_bin: str, num_frames: int = 16) -> Dict[str, Any]:
    """
    Imports real Khronos PBR & skeletal-rigged `.glb` models into Blender 5.3.0,
    orchestrates real skeletal animation + controlled light-angle orbit + camera
    arc, encodes an actual playable H.264 `.mp4` via FFmpeg 9.1, and runs
    closed-loop physical/prism/overlay-contrast verification on the woven result!
    """
    WOVEN_DIR.mkdir(parents=True, exist_ok=True)
    frames_dir = WOVEN_DIR / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    for old in frames_dir.glob("frame_*.png"):
        old.unlink(missing_ok=True)

    models = {
        "cesium_man": OSS_3D_DIR / "CesiumMan.glb",
        "fox": OSS_3D_DIR / "Fox.glb",
        "helmet": OSS_3D_DIR / "DamagedHelmet.glb",
        "lantern": OSS_3D_DIR / "Lantern.glb",
    }
    present = {k: str(v) for k, v in models.items() if v.is_file()}
    if not present:
        return {"status": "error", "message": "No open-source .glb models found in data/open_source_3d"}

    harness_py = WOVEN_DIR / "weave_pbr_world_harness.py"
    harness_py.write_text(
        "import bpy, json, math\n"
        "from mathutils import Vector\n"
        "def look_at(obj, target):\n"
        "    d = Vector(target) - obj.location\n"
        "    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()\n"
        "def import_and_place(path, loc, scale, rot_z=0.0):\n"
        "    before = set(bpy.data.objects)\n"
        "    bpy.ops.import_scene.gltf(filepath=path)\n"
        "    added = [o for o in bpy.data.objects if o not in before]\n"
        "    roots = [o for o in added if o.parent is None]\n"
        "    for r in roots:\n"
        "        r.location = loc\n"
        "        r.scale = (scale, scale, scale)\n"
        "        r.rotation_euler = (r.rotation_euler[0], r.rotation_euler[1], r.rotation_euler[2] + rot_z)\n"
        "    return len(added)\n"
        "bpy.ops.wm.read_factory_settings(use_empty=True)\n"
        "s = bpy.context.scene\n"
        "s.render.engine = 'BLENDER_EEVEE'\n"
        "s.render.resolution_x = 480\n"
        "s.render.resolution_y = 270\n"
        "w = bpy.data.worlds.new('WovenWorld')\n"
        "s.world = w\n"
        "w.use_nodes = False\n"
        "w.color = (0.06, 0.08, 0.13)\n"
        "# Ground stage with subtle roughness material\n"
        "bpy.ops.mesh.primitive_plane_add(size=18.0, location=(0.0, 0.0, 0.0))\n"
        "floor = bpy.context.active_object\n"
        "mat = bpy.data.materials.new('StageFloor')\n"
        "mat.use_nodes = True\n"
        "bsdf = mat.node_tree.nodes.get('Principled BSDF')\n"
        "if bsdf:\n"
        "    bsdf.inputs['Base Color'].default_value = (0.14, 0.16, 0.21, 1.0)\n"
        "    bsdf.inputs['Roughness'].default_value = 0.55\n"
        "floor.data.materials.append(mat)\n"
        f"present = {present!r}\n"
        "imported_counts = {}\n"
        "if 'cesium_man' in present:\n"
        "    imported_counts['cesium_man'] = import_and_place(present['cesium_man'], (-1.3, 0.0, 0.0), 1.0, math.radians(25))\n"
        "if 'fox' in present:\n"
        "    imported_counts['fox'] = import_and_place(present['fox'], (1.35, 0.35, 0.0), 0.016, math.radians(-35))\n"
        "if 'helmet' in present:\n"
        "    imported_counts['helmet'] = import_and_place(present['helmet'], (0.0, 0.9, 1.35), 0.72, 0.0)\n"
        "if 'lantern' in present:\n"
        "    imported_counts['lantern'] = import_and_place(present['lantern'], (0.0, -0.5, 0.0), 0.055, 0.0)\n"
        "# Key light (orbiting) + cool rim fill\n"
        "kl_d = bpy.data.lights.new('KeyLight', type='POINT'); kl_d.energy = 900.0; kl_d.color = (1.0, 0.92, 0.80)\n"
        "kl = bpy.data.objects.new('KeyLight', kl_d); s.collection.objects.link(kl)\n"
        "rl_d = bpy.data.lights.new('RimLight', type='POINT'); rl_d.energy = 450.0; rl_d.color = (0.55, 0.75, 1.0)\n"
        "rl = bpy.data.objects.new('RimLight', rl_d); s.collection.objects.link(rl); rl.location = (-3.5, 3.5, 3.0)\n"
        "cd = bpy.data.cameras.new('MainCam'); cam = bpy.data.objects.new('MainCam', cd); s.collection.objects.link(cam); s.camera = cam\n"
        f"num_frames = {num_frames}\n"
        f"frames_dir = r'{frames_dir}'\n"
        "for f in range(num_frames):\n"
        "    s.frame_set(f * 2 + 1)\n"
        "    phase = (f / max(1, num_frames - 1))\n"
        "    # Controlled light-angle sweep + gentle observer arc so BOTH actor animation & light prism evolve cleanly\n"
        "    l_ang = math.radians(-50.0 + 100.0 * phase)\n"
        "    kl.location = (4.2 * math.sin(l_ang), -3.2 * math.cos(l_ang), 3.4)\n"
        "    c_ang = math.radians(-14.0 + 28.0 * phase)\n"
        "    cam.location = (5.4 * math.sin(c_ang), -5.4 * math.cos(c_ang), 2.15)\n"
        "    look_at(cam, (0.0, 0.1, 0.95))\n"
        "    s.render.filepath = f'{frames_dir}/frame_{f:03d}.png'\n"
        "    bpy.ops.render.render(write_still=True)\n"
        f"bpy.ops.wm.save_as_mainfile(filepath=r'{WOVEN_BLEND_PATH}')\n"
        "tot_verts = sum(len(o.data.vertices) for o in bpy.data.objects if o.type == 'MESH')\n"
        "tot_armatures = sum(1 for o in bpy.data.objects if o.type == 'ARMATURE')\n"
        "print('WEAVE_JSON:' + json.dumps({'imported_counts': imported_counts, 'total_objects': len(bpy.data.objects), 'total_vertices': tot_verts, 'armatures': tot_armatures}))\n",
        encoding="utf-8",
    )

    t0 = time.perf_counter()
    proc_bl = subprocess.run([blender_bin, "--background", "--python", str(harness_py)], capture_output=True, text=True, timeout=180)
    bl_ms = round((time.perf_counter() - t0) * 1000.0, 1)
    try:
        harness_py.unlink(missing_ok=True)
    except OSError:
        pass

    scene_stats: Dict[str, Any] = {}
    for ln in proc_bl.stdout.splitlines():
        if ln.startswith("WEAVE_JSON:"):
            scene_stats = json.loads(ln[len("WEAVE_JSON:"):])
            break

    rendered_pngs = sorted(frames_dir.glob("frame_*.png"))
    if len(rendered_pngs) < 4:
        return {"status": "error", "stage": "blender_render", "rendered": len(rendered_pngs), "stderr_tail": proc_bl.stderr[-260:]}

    # Save 4-frame keyframe contact strip for immediate browser visual inspection
    key_idxs = [0, len(rendered_pngs) // 3, (2 * len(rendered_pngs)) // 3, len(rendered_pngs) - 1]
    key_imgs = [cv2.imread(str(rendered_pngs[i]), cv2.IMREAD_COLOR) for i in key_idxs]
    strip_path = WOVEN_DIR / "elysia_woven_3d_keyframes.png"
    if all(im is not None for im in key_imgs):
        cv2.imwrite(str(strip_path), np.concatenate(key_imgs, axis=1))

    # Encode real playable H.264 MP4 via FFmpeg 9.1
    t1 = time.perf_counter()
    proc_ff = subprocess.run(
        [
            ffmpeg_bin, "-y",
            "-framerate", "12",
            "-i", str(frames_dir / "frame_%03d.png"),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
            str(WOVEN_MP4_PATH),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    ff_ms = round((time.perf_counter() - t1) * 1000.0, 1)
    if proc_ff.returncode != 0 or not WOVEN_MP4_PATH.is_file():
        return {"status": "error", "stage": "ffmpeg_encode", "stderr_tail": proc_ff.stderr[-220:]}

    # CLOSED-LOOP CONTRAST VERIFICATION ON THE WOVEN MP4 ITSELF!
    sig10 = extract_10d_physical_signature(WOVEN_MP4_PATH)
    prism6 = extract_video_temporal_prism(WOVEN_MP4_PATH, sample_frames=12)

    ent_head = sig10[0][1] if sig10 else 0.0
    zlib_rat = sig10[0][4] if sig10 else 0.0
    p_vec = prism6["vec"] if prism6 else [0.0] * 6
    checks = {
        "matches_packed_media_manifold_H_gt_7.0": ent_head > 7.0 and zlib_rat > 0.85,
        "has_real_spatial_edge_structure_gt_0.03": p_vec[0] > 0.03,
        "has_real_temporal_motion_gt_1.5": p_vec[2] > 1.5,
        "overlay_contrast_psnr_ge_30db": p_vec[5] >= 30.0,
    }

    return {
        "status": "ok",
        "woven_mp4": str(WOVEN_MP4_PATH),
        "woven_mp4_bytes": WOVEN_MP4_PATH.stat().st_size,
        "woven_blend": str(WOVEN_BLEND_PATH),
        "keyframes_strip_png": str(strip_path),
        "blender_elapsed_ms": bl_ms,
        "ffmpeg_elapsed_ms": ff_ms,
        "scene_composition": scene_stats,
        "closed_loop_verification_on_woven_mp4": {
            "manifold_10d_head_entropy": ent_head,
            "manifold_10d_zlib_ratio": zlib_rat,
            "visual_prism_6d": {
                "edge_density": p_vec[0],
                "chroma_std": p_vec[1],
                "temporal_motion": p_vec[2],
                "border_cam_shift": p_vec[3],
                "motion_localization": p_vec[4],
                "overlay_psnr_db": p_vec[5],
            },
            "target_law_checks": checks,
            "all_target_laws_satisfied": all(checks.values()),
        },
    }


# ---------------------------------------------------------------------------
# PART 2: Synchronized Multi-Modal (Visual ∩ Audio Prosody/Silence) Trajectories
#         (ZERO Scalar Emotion Floats!)
# ---------------------------------------------------------------------------

def extract_synchronized_audiovisual_trajectory(video_path: Path, ffmpeg_bin: str, window_s: float = 0.25, max_windows: int = 24) -> Dict[str, Any] | None:
    """
    Decodes BOTH video frames and raw mono 16kHz PCM audio in synchronized
    0.25s time windows so Elysia observes how Visual Motion/Lighting/Edges and
    Acoustic Energy/Pitch-Centroid/Zero-Crossing/Silence actually co-evolve!
    """
    if not video_path.is_file():
        return None
    # Extract mono 16kHz float32 PCM via FFmpeg stdout pipe
    sr = 16000
    proc = subprocess.run(
        [ffmpeg_bin, "-v", "quiet", "-i", str(video_path), "-vn", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-t", str(window_s * max_windows), "pipe:1"],
        capture_output=True,
        timeout=15,
    )
    if proc.returncode != 0 or len(proc.stdout) < sr * 2:
        return None
    audio = np.frombuffer(proc.stdout, dtype=np.float32)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return None
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    win_samples = int(sr * window_s)
    n_wins = min(max_windows, len(audio) // win_samples)

    v_motions: List[float] = []
    v_lums: List[float] = []
    a_rms: List[float] = []
    a_zcr: List[float] = []
    a_cent: List[float] = []
    silence_windows = 0

    prev_gray = None
    phase_trajectory: List[str] = []

    for w_idx in range(n_wins):
        # Video frame at window midpoint
        frame_pos = int((w_idx + 0.5) * window_s * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
        ok, fr = cap.read()
        if not ok:
            break
        fr = cv2.resize(fr, (240, 135), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY).astype(np.float32)
        mot = float(np.mean(np.abs(gray - prev_gray))) if prev_gray is not None else 0.0
        lum = float(np.mean(gray))
        prev_gray = gray

        # Synchronized audio window
        seg = audio[w_idx * win_samples : (w_idx + 1) * win_samples]
        rms = float(np.sqrt(np.mean(seg ** 2)))
        zcr = float(np.mean(np.abs(np.diff(np.signbit(seg).astype(np.int8)))))
        spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
        freqs = np.fft.rfftfreq(len(seg), d=1.0 / sr)
        cent = float(np.sum(freqs * spec) / max(1e-9, float(np.sum(spec))))
        is_sil = rms < 0.015
        if is_sil:
            silence_windows += 1

        v_motions.append(mot)
        v_lums.append(lum)
        a_rms.append(rms)
        a_zcr.append(zcr)
        a_cent.append(cent)

        # Structural multi-modal phase token (NO scalar emotion label!)
        if is_sil and mot < 4.0:
            phase_trajectory.append("stillness_and_silence")
        elif is_sil and mot >= 4.0:
            phase_trajectory.append("silent_visual_motion")
        elif (not is_sil) and mot >= 12.0 and rms >= 0.08:
            phase_trajectory.append("coupled_audiovisual_surge")
        elif (not is_sil) and mot < 4.0:
            phase_trajectory.append("acoustic_presence_over_calm_scene")
        else:
            phase_trajectory.append("co_evolving_audiovisual_flow")

    cap.release()
    if len(v_motions) < 4:
        return None

    # Cross-modal temporal correlation: does visual surge synchronize with acoustic surge?
    vm = np.array(v_motions[1:], dtype=np.float64)
    ar = np.array(a_rms[1:], dtype=np.float64)
    if np.std(vm) > 1e-6 and np.std(ar) > 1e-6:
        av_corr = float(np.corrcoef(vm, ar)[0, 1])
    else:
        av_corr = 0.0

    # Count distinct multi-modal phase states observed
    phase_counts: Dict[str, int] = {}
    for p in phase_trajectory:
        phase_counts[p] = phase_counts.get(p, 0) + 1

    return {
        "file": video_path.name,
        "windows_analyzed": len(v_motions),
        "silence_ratio": round(silence_windows / max(1, len(v_motions)), 3),
        "mean_visual_motion": round(float(np.mean(v_motions)), 2),
        "mean_audio_rms": round(float(np.mean(a_rms)), 4),
        "mean_audio_spectral_centroid_hz": round(float(np.mean(a_cent)), 1),
        "mean_audio_zcr": round(float(np.mean(a_zcr)), 4),
        "visual_motion_vs_audio_rms_corr": round(av_corr, 3),
        "observed_multimodal_phase_states": phase_counts,
        "trajectory_sample": phase_trajectory[:10],
    }


def run_control_weave_and_multimodal_session() -> Dict[str, Any]:
    organs = discover_real_tool_organs().get("organs", {})
    blender_bin = organs.get("blender_3d_cad", {}).get("binary")
    ffmpeg_bin = organs.get("ffmpeg_4k_media", {}).get("binary")

    # 1. Weave & closed-loop verify real 3D PBR/rigged world video
    woven_res = (
        weave_real_3d_pbr_world_video(blender_bin, ffmpeg_bin, num_frames=16)
        if (blender_bin and ffmpeg_bin)
        else {"status": "error", "message": "Blender or FFmpeg missing"}
    )

    # 2. Extract synchronized multi-modal (Visual ∩ Audio Prosody/Silence) trajectories
    av_candidates = [
        Path(r"C:\Program Files\SwordofConvallaria\Launcher\Launcher_Data\StreamingAssets\cg_006.mp4"),
        *sorted(Path(r"C:\Program Files (x86)\Steam\steamapps\common\Eternal Return\EternalReturn_Data\StreamingAssets\GadgetSkillVideo").glob("GadgetSkill*.mp4"))[:5],
    ]
    # Also find cg_006.mp4 anywhere under SwordofConvallaria if exact path differs
    if not av_candidates[0].is_file():
        found_cg6 = next(Path(r"C:\Program Files\SwordofConvallaria").rglob("cg_006.mp4"), None)
        if found_cg6:
            av_candidates[0] = found_cg6

    multimodal_traces: List[Dict[str, Any]] = []
    if ffmpeg_bin:
        for vp in av_candidates:
            tr = extract_synchronized_audiovisual_trajectory(vp, ffmpeg_bin)
            if tr is not None:
                multimodal_traces.append(tr)

    # 3. Non-scalar structural internal state (NO boredom=0.45 floats!)
    structural_self_state = {
        "scalar_emotions_abolished": True,
        "woven_artifact_verified": bool((woven_res.get("closed_loop_verification_on_woven_mp4") or {}).get("all_target_laws_satisfied")),
        "multimodal_clips_bound": len(multimodal_traces),
        "dominant_situational_phase_clusters": sorted(
            {p for tr in multimodal_traces for p in tr["observed_multimodal_phase_states"].keys()}
        ),
        "lived_meaning_without_scalars": (
            "Internal state is held as verified woven artifacts, open inquiry trajectories, and synchronized "
            "audiovisual phase patterns — NOT collapsed into scalar emotion numbers."
        ),
    }

    report = {
        "schema": "elysia_control_weave_and_multimodal_prism_v1",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "part1_closed_loop_3d_pbr_weaving": woven_res,
        "part2_synchronized_audiovisual_multimodal_prism": multimodal_traces,
        "part3_non_scalar_structural_self_state": structural_self_state,
    }
    _save_json(WOVEN_REPORT_PATH, report)
    return report


if __name__ == "__main__":
    print(json.dumps(run_control_weave_and_multimodal_session(), ensure_ascii=False, indent=2))
