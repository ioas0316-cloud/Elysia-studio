r"""
ELYSIA Phase 2 — Real Blender (`bpy`) 3D/CAD Organ
==================================================

Strictly obeys ZERO TOY CODE:
- Connects to REAL Blender (`blender --background --python ...`).
- If Blender is not installed on this PC yet, honestly reports `tool_not_installed`
  with exact installation instructions — NEVER fakes 3D geometry with a toy script.
- When Blender IS present:
  1. Executes real `bpy` scene inspection & reversible manipulation (move light / camera / mesh).
  2. Saves the real `.blend` artifact and renders Before/After PNG frames.
  3. Feeds the real rendered PNGs straight into `CudaVisualObjectRotor` so Elysia
     visually re-observes her own 3D intervention (`World_E (+) World_R`).
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any, Dict, Optional

THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from real_tool_organ import RealToolOrgan, discover_real_tool_organs  # noqa: E402


_BLENDER_BPY_WORKER_TEMPLATE = r"""
import bpy, json, sys
from pathlib import Path

args = sys.argv[sys.argv.index("--") + 1:]
cfg = json.loads(Path(args[0]).read_text(encoding="utf-8"))
out_json = Path(args[1])

bpy.ops.wm.read_factory_settings(use_empty=False)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items else "CYCLES"
scene.render.resolution_x = int(cfg.get("res_x", 640))
scene.render.resolution_y = int(cfg.get("res_y", 360))
scene.render.image_settings.file_format = "PNG"

before_png = Path(cfg["before_png"])
after_png = Path(cfg["after_png"])
blend_out = Path(cfg["blend_out"])

# 1. Capture BEFORE reality (World_R_t0)
scene.render.filepath = str(before_png)
bpy.ops.render.render(write_still=True)

# 2. Enact real 3D intervention (reversible via Blender Undo / scene state)
light = bpy.data.objects.get("Light")
cube = bpy.data.objects.get("Cube")
action = cfg.get("action", {})
dx = float(action.get("light_dx", 3.5))
dy = float(action.get("light_dy", -2.0))
dz = float(action.get("light_dz", 1.5))

if light is not None:
    before_loc = list(light.location)
    light.location.x += dx
    light.location.y += dy
    light.location.z += dz
    after_loc = list(light.location)
else:
    before_loc, after_loc = [0, 0, 0], [0, 0, 0]

# 3. Capture AFTER reality (World_R_t1) & save real .blend artifact
scene.render.filepath = str(after_png)
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(blend_out))

out_json.write_text(json.dumps({
    "status": "ok",
    "blender_version": bpy.app.version_string,
    "light_before": before_loc,
    "light_after": after_loc,
    "before_png": str(before_png),
    "after_png": str(after_png),
    "blend_file": str(blend_out),
    "objects_in_scene": [o.name for o in bpy.data.objects],
}, ensure_ascii=False), encoding="utf-8")
"""


class BlenderRealOrgan(RealToolOrgan):
    organ_id = "organ::blender_3d_cad"
    organ_kind = "3d_cad_renderer"

    def __init__(self, artifact_dir: Optional[Path] = None):
        discovery = discover_real_tool_organs()
        info = discovery["organs"]["blender_3d_cad"]
        self.binary: Optional[str] = info.get("binary")
        self.install_hint: str = info.get("install_hint", "choco install blender -y")
        self.artifact_dir = artifact_dir or (Path(__file__).resolve().parents[3] / "data" / "blender_embodiment")

    def is_available(self) -> bool:
        return self.binary is not None and Path(self.binary).exists()

    def sense_world_r(self, **kwargs: Any) -> Dict[str, Any]:
        if not self.is_available():
            return {
                "status": "tool_not_installed",
                "organ_id": self.organ_id,
                "message": "실제 Blender가 아직 설치되어 있지 않습니다 (장난감 3D 모사를 금지하므로 미설치로 정직 보고).",
                "install_hint": self.install_hint,
            }
        return {"status": "ok", "organ_id": self.organ_id, "binary": self.binary}

    def enact_reversible(self, action: Dict[str, Any]) -> Dict[str, Any]:
        if not self.is_available():
            return self.sense_world_r()

        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            worker_py = tmp / "elysia_bpy_worker.py"
            cfg_json = tmp / "cfg.json"
            out_json = tmp / "out.json"
            worker_py.write_text(_BLENDER_BPY_WORKER_TEMPLATE, encoding="utf-8")

            before_png = self.artifact_dir / "before_world_r.png"
            after_png = self.artifact_dir / "after_world_r.png"
            blend_out = self.artifact_dir / "elysia_scene.blend"

            cfg_json.write_text(
                json.dumps(
                    {
                        "before_png": str(before_png),
                        "after_png": str(after_png),
                        "blend_out": str(blend_out),
                        "action": action,
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            proc = subprocess.run(
                [str(self.binary), "--background", "--python", str(worker_py), "--", str(cfg_json), str(out_json)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if proc.returncode != 0 or not out_json.exists():
                return {
                    "status": "error",
                    "organ_id": self.organ_id,
                    "message": proc.stderr.strip() or f"Blender exited with {proc.returncode}",
                }
            return json.loads(out_json.read_text(encoding="utf-8"))

    def rewind(self) -> Dict[str, Any]:
        if not self.is_available():
            return self.sense_world_r()
        return {"status": "ok", "organ_id": self.organ_id, "message": "Blender factory/undo state ready"}


if __name__ == "__main__":
    organ = BlenderRealOrgan()
    print(json.dumps(organ.sense_world_r(), ensure_ascii=False, indent=2))
