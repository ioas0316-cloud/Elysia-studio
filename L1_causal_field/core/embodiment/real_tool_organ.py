r"""
ELYSIA Phase 0 — RealToolOrgan Protocol & Honest Host Tool Discovery
====================================================================

Strictly enforces ZERO TOY CODE:
- Never substitutes missing external software (Blender, FFmpeg, Photoshop, Krita, GIMP)
  with fake mocks or synthetic loops.
- Every real external tool attaches as an Extended Sensory-Motor Organ (`RealToolOrgan`)
  exposing four causal boundary ports:
    1. sense_world_r()    -> Real external state (pixels, contours, scene graph, files)
    2. enact_reversible() -> Real intervention inside the tool's own Order Fence
    3. reobserve_delta()  -> World_E (+) World_R superposition diff
    4. rewind()           -> Real Undo / Spatiotemporal Rewind
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import glob
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
from typing import Any, Dict, List, Optional


class RealToolOrgan(ABC):
    """Base contract for any real external software/media organ coupled to Elysia."""

    organ_id: str = "organ::base"
    organ_kind: str = "external_tool"

    @abstractmethod
    def is_available(self) -> bool:
        """True ONLY when the actual external binary/hardware substrate exists."""

    @abstractmethod
    def sense_world_r(self, **kwargs: Any) -> Dict[str, Any]:
        """Captures genuine external reality (World_R) from this organ."""

    @abstractmethod
    def enact_reversible(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a reversible intervention inside this organ's Order Fence."""

    @abstractmethod
    def rewind(self) -> Dict[str, Any]:
        """Executes the organ's native Undo / Rewind mechanism."""


def _find_binary(name: str, extra_globs: List[str]) -> Optional[str]:
    found = shutil.which(name)
    if found:
        return found
    for pattern in extra_globs:
        expanded = os.path.expandvars(pattern)
        matches = sorted(glob.glob(expanded), reverse=True)
        for m in matches:
            p = Path(m)
            if p.exists() and p.is_file():
                return str(p)
    return None


def discover_real_tool_organs() -> Dict[str, Any]:
    """Probes THIS PC for real external software & GPU/sensory substrates (zero fakes)."""
    gpu_info: Dict[str, Any] = {"cuda_available": False, "device_name": None, "vram_gb": 0.0}
    if importlib.util.find_spec("torch") is not None:
        try:
            import torch  # type: ignore

            if torch.cuda.is_available():
                props = torch.cuda.get_device_properties(0)
                gpu_info = {
                    "cuda_available": True,
                    "device_name": str(props.name),
                    "vram_gb": round(props.total_memory / (1024 ** 3), 2),
                }
        except Exception as exc:
            gpu_info["error"] = str(exc)

    blender_bin = _find_binary(
        "blender",
        [
            r"C:\Program Files\Blender Foundation\Blender*\blender.exe",
            r"C:\Program Files\Blender Foundation\blender.exe",
        ],
    )
    ffmpeg_bin = _find_binary(
        "ffmpeg",
        [
            r"%LOCALAPPDATA%\Microsoft\WinGet\Links\ffmpeg.exe",
            r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg*\*\bin\ffmpeg.exe",
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\ProgramData\chocolatey\bin\ffmpeg.exe",
        ],
    )
    photoshop_bin = _find_binary(
        "photoshop",
        [r"C:\Program Files\Adobe\Adobe Photoshop*\Photoshop.exe"],
    )
    krita_bin = _find_binary(
        "krita",
        [r"C:\Program Files\Krita (x64)\bin\krita.exe", r"C:\Program Files\Krita*\bin\krita.exe"],
    )
    gimp_bin = _find_binary(
        "gimp",
        [r"C:\Program Files\GIMP*\bin\gimp-*.exe"],
    )

    py_caps = {
        lib: importlib.util.find_spec(lib) is not None
        for lib in ["cv2", "mss", "pyautogui", "PIL", "torch", "numpy", "scipy"]
    }

    organs = {
        "visual_cuda_rotor": {
            "available": bool(py_caps["cv2"] and py_caps["numpy"]),
            "cuda_accelerated": bool(gpu_info["cuda_available"]),
            "gpu": gpu_info,
            "live_screen_capture": bool(py_caps["mss"]),
            "role": "실제 4K 동영상·실시간 화면에서 0000 배경을 생략하고 1 객체 구조체를 절단",
        },
        "blender_3d_cad": {
            "available": blender_bin is not None,
            "binary": blender_bin,
            "install_hint": "choco install blender -y (또는 blender.org 설치)",
            "role": "실제 Blender(bpy) 3D 씬·조명·카메라 직접 개입 및 렌더 재관측",
        },
        "ffmpeg_4k_media": {
            "available": ffmpeg_bin is not None,
            "binary": ffmpeg_bin,
            "install_hint": "choco install ffmpeg -y",
            "role": "실제 4K/HDR 비디오 디코드·인코드 스트림 파이프라인",
        },
        "image_editor": {
            "available": any(x is not None for x in [photoshop_bin, krita_bin, gimp_bin]),
            "photoshop": photoshop_bin,
            "krita": krita_bin,
            "gimp": gimp_bin,
            "install_hint": "choco install krita -y (또는 Photoshop/GIMP 설치)",
            "role": "실제 레이어·색감·브러시 비파괴 개입 및 전/후 시각 재관측",
        },
        "os_motor_game": {
            "available": bool(py_caps["mss"] and py_caps["pyautogui"]),
            "role": "실제 게임·OS 창 포커스 울타리 내 시각 관측 및 가역 입력 작용",
        },
    }

    return {
        "status": "ok",
        "platform": sys.platform,
        "gpu": gpu_info,
        "python_capabilities": py_caps,
        "organs": organs,
    }


if __name__ == "__main__":
    print(json.dumps(discover_real_tool_organs(), ensure_ascii=False, indent=2))
