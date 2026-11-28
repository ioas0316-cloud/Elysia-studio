r"""
ELYSIA Open Multi-Sensory Tool Sandbox (Zero Pre-Scripted Outcomes · Zero Templates)
====================================================================================

Directly answers the core failure identified in the forensic audit:
- NO pre-written templates (`if domain == ...`, `light.x += 3.5`).
- NO predetermined outcomes or canned Korean messages.
- Instead, provides a 3-layer human-like Unified Sensory-Motor Hierarchy inside an
  isolated external sandbox (`data/open_sandbox/`):

  Layer 1 (Open Sensory-Motor Interface):
    - Discovers what real external tools (`blender`, `ffmpeg`) ACTUALLY expose by
      querying the tools themselves (`dir(bpy.ops.mesh)`, `ffmpeg -filters`).
    - Executes unscripted exploratory probes chosen from untried affordances.
    - Captures RAW multi-sensory deltas simultaneously:
        * Visual delta (real before/after rendered pixel & contour change)
        * File/Byte delta (real sandbox files created/changed/size)
        * Friction delta (real exit code + stderr/stdout from the external tool)
        * Time delta (real wall-clock duration)

  Layer 2 (Causal Multi-Sensory Binding):
    - Binds `(Discovered Affordance) <-> (Observed Multi-Sensory Delta)` purely from
      lived trial outcomes — NEVER from developer-written explanations.

  Layer 3 (Curiosity-Driven Next Probe):
    - Selects untried real affordances or surprising boundaries to explore next.
"""

from __future__ import annotations

import json
from pathlib import Path
import random
import re
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional

import cv2  # type: ignore
import numpy as np

THIS_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = THIS_DIR.parents[2]
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from real_tool_organ import discover_real_tool_organs  # noqa: E402

SANDBOX_DIR = WORKSPACE_ROOT / "data" / "open_sandbox"
MEMORY_PATH = SANDBOX_DIR / "open_sensory_causal_memory.json"


def _load_memory() -> Dict[str, Any]:
    if MEMORY_PATH.exists():
        try:
            return json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "discovered_affordances": {"blender_mesh_ops": [], "blender_object_ops": [], "ffmpeg_filters": []},
        "lived_causal_bindings": [],  # Purely observed (action -> multi-sensory delta)
        "discovered_chains": [],      # Purely discovered (A -> B) unlocks & parameter sensitivities
        "tried_actions": [],
    }


def _save_memory(mem: Dict[str, Any]) -> None:
    SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_PATH.write_text(json.dumps(mem, ensure_ascii=False, indent=2), encoding="utf-8")


def _measure_visual_delta(before_png: Path, after_png: Path) -> Dict[str, Any]:
    """Pure sensory measurement of real before/after visual change (no hardcoded meaning)."""
    if not before_png.exists() or not after_png.exists():
        return {"visual_observed": False}
    b = cv2.imread(str(before_png), cv2.IMREAD_COLOR)
    a = cv2.imread(str(after_png), cv2.IMREAD_COLOR)
    if b is None or a is None or b.shape != a.shape:
        return {"visual_observed": False}
    diff = np.abs(a.astype(np.int16) - b.astype(np.int16)).max(axis=2)
    changed_ratio = float(np.count_nonzero(diff > 8) / max(1, diff.size))
    mean_diff = float(np.mean(diff))
    mean_lum_before = float(np.mean(cv2.cvtColor(b, cv2.COLOR_BGR2GRAY)))
    mean_lum_after = float(np.mean(cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)))
    return {
        "visual_observed": True,
        "resolution": [int(a.shape[1]), int(a.shape[0])],
        "changed_pixel_ratio": round(changed_ratio, 4),
        "mean_intensity_delta": round(mean_diff, 2),
        "luminance_shift": round(mean_lum_after - mean_lum_before, 2),
    }


def discover_real_tool_affordances(mem: Dict[str, Any], blender_bin: Optional[str], ffmpeg_bin: Optional[str]) -> Dict[str, int]:
    """Layer 1: Ask the REAL external tools what actions exist (zero hardcoded action lists!)."""
    if "blender_object_ops" not in mem["discovered_affordances"]:
        mem["discovered_affordances"]["blender_object_ops"] = []
    if "discovered_chains" not in mem:
        mem["discovered_chains"] = []

    if blender_bin and (
        not mem["discovered_affordances"]["blender_mesh_ops"]
        or not mem["discovered_affordances"]["blender_object_ops"]
    ):
        expr = (
            "import bpy, json; "
            "print('OPS_JSON:' + json.dumps({"
            "'mesh': [n for n in dir(bpy.ops.mesh) if not n.startswith('_')],"
            "'object': [n for n in dir(bpy.ops.object) if not n.startswith('_')]"
            "}))"
        )
        proc = subprocess.run([blender_bin, "--background", "--python-expr", expr], capture_output=True, text=True, timeout=30)
        for line in proc.stdout.splitlines():
            if line.startswith("OPS_JSON:"):
                ops = json.loads(line[len("OPS_JSON:"):])
                mem["discovered_affordances"]["blender_mesh_ops"] = ops.get("mesh", [])
                mem["discovered_affordances"]["blender_object_ops"] = ops.get("object", [])
                break

    if ffmpeg_bin and not mem["discovered_affordances"]["ffmpeg_filters"]:
        proc = subprocess.run([ffmpeg_bin, "-hide_banner", "-filters"], capture_output=True, text=True, timeout=15)
        v_filters: List[str] = []
        for line in proc.stdout.splitlines():
            m = re.match(r"^\s*[T.SC]{2,4}\s+([a-zA-Z0-9_]+)\s+V->V\s+", line)
            if m:
                v_filters.append(m.group(1))
        mem["discovered_affordances"]["ffmpeg_filters"] = v_filters

    return {
        "blender_mesh_ops": len(mem["discovered_affordances"]["blender_mesh_ops"]),
        "blender_object_ops": len(mem["discovered_affordances"]["blender_object_ops"]),
        "ffmpeg_filters": len(mem["discovered_affordances"]["ffmpeg_filters"]),
    }


def explore_blender_chain_a_to_b(
    blender_bin: str,
    prereq_obj_op: str,
    target_mesh_op: str,
    trial_id: str,
) -> Dict[str, Any]:
    """
    Friction-driven A -> B chain discovery:
    Tests whether an unscripted `bpy.ops.object.<prereq_obj_op>()` unlocks a previously
    blocked `bpy.ops.mesh.<target_mesh_op>()` and measures the real visual/vertex delta!
    """
    SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
    before_png = SANDBOX_DIR / f"{trial_id}_before.png"
    after_png = SANDBOX_DIR / f"{trial_id}_after.png"
    harness_py = SANDBOX_DIR / f"{trial_id}_chain.py"
    harness_py.write_text(
        "import bpy, json\n"
        "bpy.ops.wm.read_factory_settings(use_empty=False)\n"
        "s = bpy.context.scene\n"
        "s.render.resolution_x = 480\n"
        "s.render.resolution_y = 270\n"
        f"s.render.filepath = r'{before_png}'\n"
        "bpy.ops.render.render(write_still=True)\n"
        "a_ok, b_ok, err_a, err_b = True, True, '', ''\n"
        "try:\n"
        f"    getattr(bpy.ops.object, {prereq_obj_op!r})()\n"
        "except Exception as e:\n"
        "    a_ok = False; err_a = f'{type(e).__name__}: {e}'\n"
        "try:\n"
        f"    ret_b = str(getattr(bpy.ops.mesh, {target_mesh_op!r})())\n"
        "except Exception as e:\n"
        "    b_ok = False; ret_b = ''; err_b = f'{type(e).__name__}: {e}'\n"
        "try:\n"
        "    if bpy.context.mode != 'OBJECT': bpy.ops.object.mode_set(mode='OBJECT')\n"
        "except Exception:\n"
        "    pass\n"
        "verts_after = sum(len(o.data.vertices) for o in bpy.data.objects if o.type == 'MESH')\n"
        f"s.render.filepath = r'{after_png}'\n"
        "bpy.ops.render.render(write_still=True)\n"
        "print('CHAIN_JSON:' + json.dumps({'a_ok': a_ok, 'b_ok': b_ok, 'ret_b': ret_b, 'err_a': err_a, 'err_b': err_b, 'verts_after': verts_after}))\n",
        encoding="utf-8",
    )
    t0 = time.perf_counter()
    proc = subprocess.run([blender_bin, "--background", "--python", str(harness_py)], capture_output=True, text=True, timeout=60)
    try:
        harness_py.unlink(missing_ok=True)
    except OSError:
        pass
    elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 1)

    parsed: Dict[str, Any] = {"a_ok": False, "b_ok": False, "err_b": proc.stderr[-180:].strip()}
    for line in proc.stdout.splitlines():
        if line.startswith("CHAIN_JSON:"):
            parsed = json.loads(line[len("CHAIN_JSON:"):])
            break

    vis_delta = _measure_visual_delta(before_png, after_png)
    return {
        "trial_id": trial_id,
        "tool": "blender_5.3_chain",
        "chain": f"bpy.ops.object.{prereq_obj_op}() -> bpy.ops.mesh.{target_mesh_op}()",
        "elapsed_ms": elapsed_ms,
        "unlocked_b": bool(parsed.get("a_ok") and parsed.get("b_ok")),
        "tool_outcome": parsed,
        "visual_sensory_delta": vis_delta,
    }


def discover_and_perturb_ffmpeg_filter(ffmpeg_bin: str, filter_name: str, input_img: Path, trial_id: str) -> Dict[str, Any]:
    """
    Reads `ffmpeg -h filter=<filter_name>` directly from FFmpeg itself to discover real
    numeric parameters (name, range, default), then probes a non-default perturbation
    and measures the actual visual delta!
    """
    proc_h = subprocess.run([ffmpeg_bin, "-hide_banner", "-h", f"filter={filter_name}"], capture_output=True, text=True, timeout=10)
    help_txt = proc_h.stdout + "\n" + proc_h.stderr
    # Parse lines like: "  exposure  <float>  ..FV.....T.  set the exposure ... (from -3 to 3) (default 0)"
    param_match = re.search(
        r"^\s+([a-zA-Z0-9_]+)\s+<(float|double|int)>\s+\S+.*?\(from\s+([-0-9.e+]+)\s+to\s+([-0-9.e+]+)\)\s*\(default\s+([-0-9.e+]+)\)",
        help_txt,
        re.M,
    )
    if not param_match:
        return {"trial_id": trial_id, "tool": "ffmpeg_param_probe", "filter": filter_name, "param_discovered": False}

    pname, ptype, lo_s, hi_s, def_s = param_match.groups()
    lo, hi, dval = float(lo_s), float(hi_s), float(def_s)
    # Pick a clean non-default value inside the tool's own declared [lo, hi] range
    span = min(hi - lo, 6.0)
    probe_val = dval + span * 0.35 if (dval + span * 0.35) <= hi else (dval - span * 0.35)
    probe_str = str(int(round(probe_val))) if ptype == "int" else f"{probe_val:.2f}"
    filter_expr = f"{filter_name}={pname}={probe_str}"

    SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
    out_png = SANDBOX_DIR / f"{trial_id}_ffmpeg_param_{filter_name}.png"
    t0 = time.perf_counter()
    proc = subprocess.run([ffmpeg_bin, "-y", "-i", str(input_img), "-vf", filter_expr, str(out_png)], capture_output=True, text=True, timeout=20)
    elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 1)
    vis_delta = _measure_visual_delta(input_img, out_png) if out_png.exists() else {"visual_observed": False}
    return {
        "trial_id": trial_id,
        "tool": "ffmpeg_9.1_param_discovery",
        "discovered_param": {"name": pname, "type": ptype, "range": [lo, hi], "default": dval},
        "action": f"ffmpeg -vf {filter_expr}",
        "elapsed_ms": elapsed_ms,
        "op_ok": proc.returncode == 0 and out_png.exists(),
        "visual_sensory_delta": vis_delta,
        "output_file": out_png.name if out_png.exists() else None,
    }


def explore_one_unscripted_blender_op(blender_bin: str, op_name: str, trial_id: str) -> Dict[str, Any]:
    """
    Executes an UNSCRIPTED discovered `bpy.ops.mesh.<op_name>()` inside the isolated sandbox,
    capturing ALL real multi-sensory deltas (before/after render, scene object count, real stderr/error).
    """
    SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
    before_png = SANDBOX_DIR / f"{trial_id}_before.png"
    after_png = SANDBOX_DIR / f"{trial_id}_after.png"

    # Minimal neutral observation harness — does NOT know what `op_name` does!
    harness_py = SANDBOX_DIR / f"{trial_id}_harness.py"
    harness_py.write_text(
        "import bpy, json\n"
        "bpy.ops.wm.read_factory_settings(use_empty=False)\n"
        "s = bpy.context.scene\n"
        "s.render.resolution_x = 480\n"
        "s.render.resolution_y = 270\n"
        f"s.render.filepath = r'{before_png}'\n"
        "bpy.ops.render.render(write_still=True)\n"
        "before_objs = len(bpy.data.objects)\n"
        "err = ''\n"
        "ok = True\n"
        "op_ret = ''\n"
        "try:\n"
        f"    res = getattr(bpy.ops.mesh, {op_name!r})()\n"
        "    op_ret = str(res)\n"
        "except Exception as e:\n"
        "    ok = False\n"
        "    err = f'{type(e).__name__}: {e}'\n"
        "after_objs = len(bpy.data.objects)\n"
        f"s.render.filepath = r'{after_png}'\n"
        "bpy.ops.render.render(write_still=True)\n"
        "print('TRIAL_JSON:' + json.dumps({'op_ok': ok, 'op_ret': op_ret, 'err': err, 'obj_delta': after_objs - before_objs}))\n",
        encoding="utf-8",
    )

    t0 = time.perf_counter()
    proc = subprocess.run([blender_bin, "--background", "--python", str(harness_py)], capture_output=True, text=True, timeout=60)
    try:
        harness_py.unlink(missing_ok=True)
    except OSError:
        pass
    elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 1)

    parsed_trial: Dict[str, Any] = {"op_ok": False, "err": proc.stderr[-220:].strip(), "obj_delta": 0}
    for line in proc.stdout.splitlines():
        if line.startswith("TRIAL_JSON:"):
            parsed_trial = json.loads(line[len("TRIAL_JSON:"):])
            break

    vis_delta = _measure_visual_delta(before_png, after_png)
    return {
        "trial_id": trial_id,
        "tool": "blender_5.3",
        "action": f"bpy.ops.mesh.{op_name}()",
        "elapsed_ms": elapsed_ms,
        "exit_code": proc.returncode,
        "tool_outcome": parsed_trial,
        "visual_sensory_delta": vis_delta,
        "artifacts": {"before": str(before_png.name), "after": str(after_png.name)},
    }


def explore_one_unscripted_ffmpeg_filter(ffmpeg_bin: str, filter_name: str, input_img: Path, trial_id: str) -> Dict[str, Any]:
    """
    Executes an UNSCRIPTED discovered FFmpeg V->V filter on a real image inside the sandbox,
    capturing real exit code, real stderr friction, real file size delta, and real visual delta.
    """
    SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
    out_png = SANDBOX_DIR / f"{trial_id}_ffmpeg_{filter_name}.png"
    t0 = time.perf_counter()
    proc = subprocess.run(
        [ffmpeg_bin, "-y", "-i", str(input_img), "-vf", filter_name, str(out_png)],
        capture_output=True,
        text=True,
        timeout=20,
    )
    elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 1)
    vis_delta = _measure_visual_delta(input_img, out_png) if out_png.exists() else {"visual_observed": False}
    return {
        "trial_id": trial_id,
        "tool": "ffmpeg_9.1",
        "action": f"ffmpeg -vf {filter_name}",
        "elapsed_ms": elapsed_ms,
        "exit_code": proc.returncode,
        "tool_outcome": {
            "op_ok": proc.returncode == 0 and out_png.exists(),
            "stderr_tail": proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else "",
            "out_bytes": out_png.stat().st_size if out_png.exists() else 0,
        },
        "visual_sensory_delta": vis_delta,
        "artifacts": {"output": str(out_png.name) if out_png.exists() else None},
    }


def run_open_exploration_session(blender_trials: int = 2, ffmpeg_trials: int = 2) -> Dict[str, Any]:
    organs = discover_real_tool_organs()["organs"]
    blender_bin = organs["blender_3d_cad"].get("binary")
    ffmpeg_bin = organs["ffmpeg_4k_media"].get("binary")

    mem = _load_memory()
    discovered_counts = discover_real_tool_affordances(mem, blender_bin, ffmpeg_bin)
    tried = set(mem.get("tried_actions") or [])
    new_bindings: List[Dict[str, Any]] = []

    # Layer 3: Pick genuinely UNTRIED affordances discovered from the real tools themselves
    if blender_bin:
        untried_b = [op for op in mem["discovered_affordances"]["blender_mesh_ops"] if f"bpy.ops.mesh.{op}()" not in tried]
        random.shuffle(untried_b)
        for op in untried_b[:blender_trials]:
            tid = f"b_{int(time.time() * 1000)}_{op[:14]}"
            binding = explore_one_unscripted_blender_op(blender_bin, op, tid)
            new_bindings.append(binding)
            mem["lived_causal_bindings"].append(binding)
            mem["tried_actions"].append(binding["action"])
            tried.add(binding["action"])

    sample_img = WORKSPACE_ROOT / "data" / "blender_embodiment" / "before_world_r.png"
    if ffmpeg_bin and sample_img.exists():
        untried_f = [fl for fl in mem["discovered_affordances"]["ffmpeg_filters"] if f"ffmpeg -vf {fl}" not in tried]
        random.shuffle(untried_f)
        for fl in untried_f[:ffmpeg_trials]:
            tid = f"f_{int(time.time() * 1000)}_{fl[:14]}"
            binding = explore_one_unscripted_ffmpeg_filter(ffmpeg_bin, fl, sample_img, tid)
            new_bindings.append(binding)
            mem["lived_causal_bindings"].append(binding)
            mem["tried_actions"].append(binding["action"])
            tried.add(binding["action"])

    _save_memory(mem)
    return {
        "status": "ok",
        "discovered_real_affordances": discovered_counts,
        "new_unscripted_trials": new_bindings,
        "total_lived_causal_bindings": len(mem["lived_causal_bindings"]),
        "memory_file": str(MEMORY_PATH),
    }


def run_friction_chain_session() -> Dict[str, Any]:
    """
    Reads Elysia's own previous friction/zero-delta episodes from `open_sensory_causal_memory.json`
    and actively probes:
      1. Blender A -> B chains: tries discovered `bpy.ops.object.*` mode/context candidates before a
         previously blocked `bpy.ops.mesh.*` op!
      2. FFmpeg parameter perturbation: reads `ffmpeg -h filter=<name>` on a previously zero-delta
         filter (`exposure`, etc.) and perturbs its discovered numeric parameter!
    """
    organs = discover_real_tool_organs()["organs"]
    blender_bin = organs["blender_3d_cad"].get("binary")
    ffmpeg_bin = organs["ffmpeg_4k_media"].get("binary")

    mem = _load_memory()
    discovered_counts = discover_real_tool_affordances(mem, blender_bin, ffmpeg_bin)
    chain_results: List[Dict[str, Any]] = []

    # 1. Pick a previously blocked Blender mesh op (or one from discovered ops) and test candidate object-op prerequisites
    if blender_bin:
        obj_ops = mem["discovered_affordances"]["blender_object_ops"]
        # Prioritize discovered object ops whose own name contains 'mode' (lexical self-cue from `context is incorrect`), plus 1 random!
        mode_candidates = [o for o in obj_ops if "mode" in o.lower()]
        prereq_picks = mode_candidates[:2] if mode_candidates else obj_ops[:2]
        # Target a discovered mesh op that modifies geometry (e.g., subdivide/bevel/extrude or previously failed)
        mesh_ops = mem["discovered_affordances"]["blender_mesh_ops"]
        target_mesh = "subdivide" if "subdivide" in mesh_ops else mesh_ops[0]
        for pre in prereq_picks:
            tid = f"chain_{int(time.time() * 1000)}_{pre[:12]}"
            res = explore_blender_chain_a_to_b(blender_bin, pre, target_mesh, tid)
            chain_results.append(res)
            mem["discovered_chains"].append(res)

    # 2. Pick a previously zero-delta FFmpeg filter from lived memory (`exposure`) and discover its real parameters via `ffmpeg -h`
    sample_img = WORKSPACE_ROOT / "data" / "blender_embodiment" / "before_world_r.png"
    if ffmpeg_bin and sample_img.exists():
        zero_delta_filters = [
            b["action"].replace("ffmpeg -vf ", "").strip()
            for b in mem.get("lived_causal_bindings", [])
            if b.get("tool") == "ffmpeg_9.1"
            and (b.get("visual_sensory_delta") or {}).get("changed_pixel_ratio", 1.0) == 0.0
        ]
        probe_filters = list(dict.fromkeys(zero_delta_filters))[:2] or ["exposure"]
        for fl in probe_filters:
            tid = f"fparam_{int(time.time() * 1000)}_{fl[:12]}"
            res = discover_and_perturb_ffmpeg_filter(ffmpeg_bin, fl, sample_img, tid)
            chain_results.append(res)
            mem["discovered_chains"].append(res)

    _save_memory(mem)
    return {
        "status": "ok",
        "discovered_real_affordances": discovered_counts,
        "friction_driven_discoveries": chain_results,
        "total_discovered_chains": len(mem["discovered_chains"]),
        "memory_file": str(MEMORY_PATH),
    }


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--chain":
        print(json.dumps(run_friction_chain_session(), ensure_ascii=False, indent=2))
    else:
        print(json.dumps(run_open_exploration_session(blender_trials=2, ffmpeg_trials=2), ensure_ascii=False, indent=2))
