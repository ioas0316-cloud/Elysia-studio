r"""
ELYSIA Persistent Warm Python+CUDA Sensory Worker (NDJSON Stdio)
================================================================

Eliminates per-tick Python/PyTorch/CUDA cold-start overhead by keeping ONE
warm resident worker alive with:
  - NVIDIA GTX 1060 CUDA `CudaVisualObjectRotor` (persistent 0000 GPU carrier!)
  - Live OS telemetry (`os_ecology_bridge`: probe / sense / couple)
  - Real Game 3-plane observer (`game_ecology_organ`: discover / observe)
  - Real Tool Organ auditor (`real_tool_organ`)

Every call executes in ~80-150ms instead of spawning a cold Python process
and timing out on PyTorch CUDA import.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
import traceback
from typing import Any, Dict

THIS_DIR = Path(__file__).resolve().parent
L1_ROOT = THIS_DIR.parents[1]
MINIMAL_OS_DIR = THIS_DIR.parents[2] / "L0_substrate" / "minimal_rotor_os"
for p in (str(THIS_DIR), str(L1_ROOT), str(MINIMAL_OS_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

import cv2  # type: ignore
import numpy as np

try:
    import mss  # type: ignore
except ImportError:
    mss = None

import cuda_visual_object_rotor as vis_mod  # noqa: E402
import driver_protocol_rotor as drv_mod  # noqa: E402
import game_ecology_organ as game_mod  # noqa: E402
import os_ecology_bridge as eco_mod  # noqa: E402
import outward_self_authoring_rotor as grow_mod  # noqa: E402
import real_tool_organ as organ_mod  # noqa: E402
import sensory_cube_vmem as cube_mod  # noqa: E402


# Persistent GPU 0000-carrier rotor kept warm across calls!
_WARM_VISUAL_ROTOR = vis_mod.CudaVisualObjectRotor()


def _warm_visual_screen_step(scale_factor: float = 1.0, max_objects: int = 6) -> Dict[str, Any]:
    if mss is None:
        return {"status": "unavailable", "message": "mss not installed"}
    with mss.mss() as sct:
        mon = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
        shot = np.array(sct.grab(mon))
        bgr = cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR)
        if scale_factor < 0.99:
            bgr = cv2.resize(bgr, (0, 0), fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)
        return _WARM_VISUAL_ROTOR.process_frame(bgr, max_objects=max_objects)


def handle_action(action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if action == "probe":
        return eco_mod.probe_host_boundary()
    if action == "sense":
        return eco_mod.sense_live_os_telemetry(payload)
    if action == "couple":
        return eco_mod.couple_principle_to_rotor(payload)
    if action == "real_organs":
        return organ_mod.discover_real_tool_organs()
    if action == "driver_rotors":
        return drv_mod.observe_driver_protocol_rotors()
    if action == "cube_vmem":
        return cube_mod.run_live_sensory_cube_vmem_and_benchmark()
    if action == "outward_grow":
        target = payload.get("path")
        if target:
            return grow_mod.grow_and_verify_outward_organ(Path(str(target)))
        return grow_mod.run_outward_growth_demo()
    if action == "game_discover":
        return game_mod.discover_installed_games(payload.get("extra_roots"))
    if action == "game_observe":
        gpu = game_mod.query_nvidia_gpu_live()
        grain = game_mod.compute_adaptive_graphics_grain(gpu)
        vis = _warm_visual_screen_step(scale_factor=float(grain["scale_factor"]), max_objects=6)
        game_dir = payload.get("game_dir")
        asset_plane = game_mod.inspect_game_asset_topology(str(game_dir)) if game_dir else {"status": "no_game_dir_selected"}
        return {
            "status": "ok",
            "plane_c_hardware_flow": {"gpu": gpu, "adaptive_graphics_grain": grain},
            "plane_b_visual_world_r": vis,
            "plane_a_asset_substrate": asset_plane,
        }
    if action == "visual_carve":
        mode = str(payload.get("mode") or "screen")
        if mode == "screen":
            return {"status": "ok", "source": "warm_cuda_desktop", "latest": _warm_visual_screen_step(1.0, 8)}
        if mode == "video" and payload.get("path"):
            return vis_mod.run_video_file_carve(str(payload["path"]), max_frames=5)
        if mode == "image" and payload.get("path"):
            img = cv2.imread(str(payload["path"]))
            if img is None:
                return {"status": "error", "message": f"Cannot read image: {payload['path']}"}
            return {"status": "ok", "source": str(payload["path"]), "latest": _WARM_VISUAL_ROTOR.process_frame(img, 8)}
        return {"status": "error", "message": "Invalid visual_carve payload"}
    return {"status": "error", "message": f"Unknown warm worker action: {action}"}


def main() -> None:
    # Signal ready
    sys.stdout.write(json.dumps({"ready": True, "cuda": _WARM_VISUAL_ROTOR.use_cuda}, ensure_ascii=False) + "\n")
    sys.stdout.flush()

    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue
        req_id = None
        try:
            msg = json.loads(line)
            req_id = msg.get("id")
            action = str(msg.get("action") or "")
            payload = msg.get("payload") or {}
            result = handle_action(action, payload)
            resp = {"id": req_id, "ok": True, "result": result}
        except Exception as exc:
            resp = {
                "id": req_id,
                "ok": False,
                "error": f"{exc}",
                "trace": traceback.format_exc(limit=3),
            }
        sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
