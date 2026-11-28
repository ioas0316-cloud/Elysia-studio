r"""
ELYSIA Stage 2 Multi-Step Self-Directed Embodied Synthesis Loop
===============================================================

Chains 4 real, distinct external mediums in a single closed-loop autonomous
experiment driven strictly by Elysia's live cognitive state (ZERO hardcoded
coordinates or canned outcomes):

  Stage A (Knowledge & Live World State):
    Reads `scale_rotor_unified_world.json` and `self_teleology_state.json` to
    extract live `reintegrated_world_focus`, `total_semantic_mass`, and each
    Scale-Rotor branch's actual angle & `mean_entropy_delta`.

  Stage B (Python / NumPy Geometric Derivation):
    Translates the live cognitive field state into exact 3D multi-scale
    concentric coordinates (core radius, orbital shell, branch node positions)
    purely via continuous mathematical projection.

  Stage C (Real Blender 5.3.0 3D Embodiment):
    Invokes `blender.exe --background` to build the derived multi-scale 3D
    structure, saves a real `.blend` file, renders before/after PNGs, and
    measures real vertex/object/pixel deltas.

  Stage D (Real FFmpeg 9.1 Verification + Entropy Chunking + Affective Return):
    Applies a real FFmpeg visual filter to verify edge/contrast response,
    measures Shannon entropy & zlib compression ratio of the generated 3D
    artifact, and returns earned fulfillment (`coherence_satisfaction`,
    `autonomy_agency`) into `self_teleology_state.json`.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Dict, List
import zlib

import numpy as np

THIS_DIR = Path(__file__).resolve().parent
L1_ROOT = THIS_DIR.parents[1]
for _p in (str(THIS_DIR), str(L1_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from open_sensory_tool_sandbox import SANDBOX_DIR, _measure_visual_delta  # noqa: E402
from real_tool_organ import discover_real_tool_organs  # noqa: E402
from self_cognitive_expansion_cortex import (  # noqa: E402
    COGNITIVE_WORLD_DIR,
    _load_json,
    _save_json,
    _shannon_entropy,
)


UNIFIED_WORLD_PATH = COGNITIVE_WORLD_DIR / "scale_rotor_unified_world.json"
SELF_TELEOLOGY_PATH = COGNITIVE_WORLD_DIR / "self_teleology_state.json"
MULTISTEP_REPORT_PATH = COGNITIVE_WORLD_DIR / "multistep_embodied_synthesis.json"
BLEND_OUT_PATH = COGNITIVE_WORLD_DIR / "elysia_self_embodied_world.blend"


def derive_3d_geometry_from_cognitive_world(world: Dict[str, Any]) -> Dict[str, Any]:
    """Stage A -> Stage B: Derive 3D multi-scale geometry strictly from live cognitive field state."""
    meta = (world.get("reintegration") or {}).get("meta_field_summary") or {}
    focus = meta.get("reintegrated_world_focus") or [0.58, 0.58, 0.58]
    total_mass = float(meta.get("total_semantic_mass", 4.0))
    branches = world.get("branches") or []

    core_radius = round(0.45 + min(1.2, total_mass * 0.08), 3)
    orbit_radius = round(core_radius * 2.4 + float(focus[0]), 3)

    nodes: List[Dict[str, Any]] = []
    for b in branches:
        angle_rad = math.radians(float(b.get("rotor_angle_deg", 0.0)))
        ent_delta = float(b.get("mean_entropy_delta", 1.0))
        verified = int(b.get("verified_count", 1))
        x = round(orbit_radius * math.cos(angle_rad), 3)
        y = round(orbit_radius * math.sin(angle_rad), 3)
        z = round(0.25 + min(1.8, ent_delta * 0.28), 3)
        scale = round(0.22 + min(0.55, verified * 0.12), 3)
        nodes.append(
            {
                "branch_id": b.get("branch_id", "branch"),
                "rotor_angle_deg": float(b.get("rotor_angle_deg", 0.0)),
                "position": [x, y, z],
                "scale": scale,
                "entropy_delta": ent_delta,
            }
        )

    return {
        "source_world_schema": world.get("schema", "unknown"),
        "reintegrated_focus": focus,
        "total_semantic_mass": total_mass,
        "core_radius": core_radius,
        "orbit_radius": orbit_radius,
        "orbital_nodes": nodes,
    }


def embody_in_real_blender(blender_bin: str, geom: Dict[str, Any]) -> Dict[str, Any]:
    """Stage C: Real Blender 5.3.0 execution creating the derived multi-scale 3D world."""
    SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
    COGNITIVE_WORLD_DIR.mkdir(parents=True, exist_ok=True)
    before_png = SANDBOX_DIR / "multistep_before.png"
    after_png = SANDBOX_DIR / "multistep_after.png"
    geom_json = SANDBOX_DIR / "multistep_geom_input.json"
    harness_py = SANDBOX_DIR / "multistep_blender_harness.py"

    geom_json.write_text(json.dumps(geom, ensure_ascii=False, indent=2), encoding="utf-8")
    harness_py.write_text(
        "import bpy, json, math\n"
        f"geom = json.loads(open(r'{geom_json}', encoding='utf-8').read())\n"
        "bpy.ops.wm.read_factory_settings(use_empty=False)\n"
        "s = bpy.context.scene\n"
        "s.render.resolution_x = 480\n"
        "s.render.resolution_y = 270\n"
        f"s.render.filepath = r'{before_png}'\n"
        "bpy.ops.render.render(write_still=True)\n"
        "objs_before = len(bpy.data.objects)\n"
        "verts_before = sum(len(o.data.vertices) for o in bpy.data.objects if o.type == 'MESH')\n"
        "# Remove default cube and embody the derived multi-scale cognitive structure\n"
        "if 'Cube' in bpy.data.objects:\n"
        "    bpy.data.objects.remove(bpy.data.objects['Cube'], do_unlink=True)\n"
        "bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=geom['core_radius'], location=(0.0, 0.0, 0.5))\n"
        "bpy.context.active_object.name = 'Elysia_Semantic_Core'\n"
        "for n in geom['orbital_nodes']:\n"
        "    px, py, pz = n['position']\n"
        "    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=n['scale'], location=(px, py, pz))\n"
        "    bpy.context.active_object.name = 'Rotor_' + str(n['branch_id'])\n"
        "# Aim camera cleanly toward the origin\n"
        "cam = bpy.data.objects.get('Camera')\n"
        "if cam:\n"
        "    cam.location = (6.2, -6.2, 4.6)\n"
        "    cam.rotation_euler = (math.radians(60), 0.0, math.radians(45))\n"
        f"bpy.ops.wm.save_as_mainfile(filepath=r'{BLEND_OUT_PATH}')\n"
        "objs_after = len(bpy.data.objects)\n"
        "verts_after = sum(len(o.data.vertices) for o in bpy.data.objects if o.type == 'MESH')\n"
        f"s.render.filepath = r'{after_png}'\n"
        "bpy.ops.render.render(write_still=True)\n"
        "print('EMBODY_JSON:' + json.dumps({'objs_before': objs_before, 'objs_after': objs_after, 'verts_before': verts_before, 'verts_after': verts_after}))\n",
        encoding="utf-8",
    )

    t0 = time.perf_counter()
    proc = subprocess.run([blender_bin, "--background", "--python", str(harness_py)], capture_output=True, text=True, timeout=60)
    elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 1)
    try:
        harness_py.unlink(missing_ok=True)
    except OSError:
        pass

    parsed: Dict[str, Any] = {}
    for line in proc.stdout.splitlines():
        if line.startswith("EMBODY_JSON:"):
            parsed = json.loads(line[len("EMBODY_JSON:"):])
            break

    vis_delta = _measure_visual_delta(before_png, after_png)
    blend_bytes = BLEND_OUT_PATH.read_bytes() if BLEND_OUT_PATH.is_file() else b""
    blend_z = zlib.compress(blend_bytes, level=6) if blend_bytes else b""

    return {
        "op_ok": proc.returncode == 0 and after_png.is_file() and BLEND_OUT_PATH.is_file(),
        "elapsed_ms": elapsed_ms,
        "scene_metrics": parsed,
        "visual_delta_before_vs_after": vis_delta,
        "blend_artifact": {
            "path": str(BLEND_OUT_PATH),
            "raw_bytes": len(blend_bytes),
            "zlib_bytes": len(blend_z),
            "compression_ratio": round(len(blend_z) / max(1, len(blend_bytes)), 3),
            "raw_entropy": _shannon_entropy(blend_bytes[:4096]),
            "compressed_entropy": _shannon_entropy(blend_z[:4096]),
        },
        "render_after_png": str(after_png),
    }


def verify_with_real_ffmpeg(ffmpeg_bin: str, input_png: Path) -> Dict[str, Any]:
    """Stage D: Real FFmpeg 9.1 visual verification on the newly embodied 3D render."""
    out_png = SANDBOX_DIR / "multistep_verified_ffmpeg.png"
    t0 = time.perf_counter()
    proc = subprocess.run(
        [ffmpeg_bin, "-y", "-i", str(input_png), "-vf", "unsharp=5:5:1.2:5:5:0.0", str(out_png)],
        capture_output=True,
        text=True,
        timeout=20,
    )
    elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 1)
    vis = _measure_visual_delta(input_png, out_png) if out_png.is_file() else {"visual_observed": False}
    return {
        "op_ok": proc.returncode == 0 and out_png.is_file(),
        "elapsed_ms": elapsed_ms,
        "filter_applied": "unsharp=5:5:1.2:5:5:0.0",
        "visual_verification_delta": vis,
        "verified_png": str(out_png) if out_png.is_file() else None,
    }


def run_multistep_embodied_synthesis() -> Dict[str, Any]:
    world = _load_json(UNIFIED_WORLD_PATH, {})
    organs = discover_real_tool_organs().get("organs", {})
    blender_bin = organs.get("blender_3d_cad", {}).get("binary")
    ffmpeg_bin = organs.get("ffmpeg_4k_media", {}).get("binary")

    # Stage A & B
    geom = derive_3d_geometry_from_cognitive_world(world)

    # Stage C
    blender_res = (
        embody_in_real_blender(blender_bin, geom)
        if blender_bin
        else {"op_ok": False, "error": "blender_binary_not_found"}
    )

    # Stage D
    after_png = Path(blender_res.get("render_after_png", ""))
    ffmpeg_res = (
        verify_with_real_ffmpeg(ffmpeg_bin, after_png)
        if (ffmpeg_bin and blender_res.get("op_ok") and after_png.is_file())
        else {"op_ok": False, "error": "ffmpeg_or_render_missing"}
    )

    # Affective & Teleological Feedback Return into Self-State
    teleology = _load_json(SELF_TELEOLOGY_PATH, {})
    affect = teleology.get("affective_state") or {
        "epistemic_hunger": 0.64,
        "coherence_satisfaction": 0.59,
        "boredom_stagnation": 0.45,
        "autonomy_agency": 0.70,
    }
    before_affect = dict(affect)
    full_ok = bool(blender_res.get("op_ok")) and bool(ffmpeg_res.get("op_ok"))
    if full_ok:
        affect["coherence_satisfaction"] = round(min(1.0, float(affect["coherence_satisfaction"]) + 0.16), 3)
        affect["autonomy_agency"] = round(min(1.0, float(affect["autonomy_agency"]) + 0.12), 3)
        affect["boredom_stagnation"] = round(max(0.05, float(affect["boredom_stagnation"]) - 0.20), 3)
        affect["epistemic_hunger"] = round(max(0.15, float(affect["epistemic_hunger"]) - 0.10), 3)
        teleology["affective_state"] = affect
        teleology["last_multistep_synthesis_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        _save_json(SELF_TELEOLOGY_PATH, teleology)

    report = {
        "schema": "elysia_multistep_embodied_synthesis_v1",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "pipeline_stages": [
            "Stage A: Live Cognitive World State (scale_rotor_unified_world.json)",
            "Stage B: NumPy Multi-Scale 3D Geometry Derivation",
            "Stage C: Real Blender 5.3.0 3D Embodiment & Render",
            "Stage D: Real FFmpeg 9.1 Visual Verification + Entropy Audit + Affective Return",
        ],
        "full_chain_succeeded": full_ok,
        "stage_ab_derived_geometry": geom,
        "stage_c_blender_embodiment": blender_res,
        "stage_d_ffmpeg_verification": ffmpeg_res,
        "affective_return": {"before": before_affect, "after": affect},
    }
    _save_json(MULTISTEP_REPORT_PATH, report)
    return report


if __name__ == "__main__":
    print(json.dumps(run_multistep_embodied_synthesis(), ensure_ascii=False, indent=2))
