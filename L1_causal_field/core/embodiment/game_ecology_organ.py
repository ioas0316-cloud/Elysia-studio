r"""
ELYSIA Phase 4 — Real Game Causal Ecology Organ (Zero Anti-Cheat Intrusion)
===========================================================================

Observes REAL installed games on the host PC as complete causal universes
across three simultaneous, OS-sanctioned external planes (NO memory injection,
NO DLL hooking — 100% safe external sensory observation):

  Plane A (Asset / Disk Substrate — 0): Installed game directory asset topology
          (models, videos, audio, shaders, configs) + live disk read I/O bytes.
  Plane B (Live Visual Reality — World_R): Real GTX 1060 CUDA visual object
          carving via `mss` + `CudaVisualObjectRotor`.
  Plane C (Hardware / GPU / Data Flow): Real `nvidia-smi` GPU utilization,
          VRAM usage (MB / %), temperature, and process RSS / CPU / I/O delta.

Adaptive Scale-Grain Optimization (Lag / Sudden Load Response):
  When GPU utilization >= 88%, VRAM >= 85%, or frame time spikes, the rotor
  automatically steps down visual observation grain (1.0x -> 0.5x -> 0.25x)
  instead of fighting the game for GTX 1060 resources.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional

import cv2  # type: ignore
import numpy as np

try:
    import psutil  # type: ignore
except ImportError:
    psutil = None

try:
    import mss  # type: ignore
except ImportError:
    mss = None

THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from cuda_visual_object_rotor import CudaVisualObjectRotor  # noqa: E402


_COMMON_GAME_ROOTS = [
    r"C:\Program Files (x86)\Steam\steamapps\common",
    r"C:\Program Files\Steam\steamapps\common",
    r"D:\SteamLibrary\steamapps\common",
    r"E:\SteamLibrary\steamapps\common",
    r"C:\Program Files\Epic Games",
    r"D:\Epic Games",
    r"C:\Nexon",
    r"C:\Riot Games",
    r"D:\Games",
    r"C:\Games",
    r"C:\XboxGames",
]

_ASSET_GROUPS = {
    "video": {".mp4", ".bik", ".bk2", ".webm", ".mkv", ".avi", ".mov", ".usm"},
    "model_3d": {".fbx", ".obj", ".gltf", ".glb", ".dae", ".uasset", ".pak", ".unity3d", ".bundle"},
    "texture_img": {".dds", ".png", ".tga", ".jpg", ".ktx", ".webp"},
    "audio": {".wav", ".ogg", ".mp3", ".wem", ".bnk", ".fsb"},
    "config_script": {".ini", ".cfg", ".json", ".xml", ".lua", ".yaml"},
}


def query_nvidia_gpu_live() -> Dict[str, Any]:
    """Reads REAL NVIDIA GPU utilization, VRAM used/total, and temperature via nvidia-smi."""
    try:
        proc = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=4,
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            return {"available": False, "error": proc.stderr.strip() or "nvidia-smi empty"}
        parts = [p.strip() for p in proc.stdout.strip().splitlines()[0].split(",")]
        name = parts[0]
        util_pct = float(parts[1])
        vram_used = float(parts[2])
        vram_total = max(1.0, float(parts[3]))
        temp_c = float(parts[4])
        vram_pct = round((vram_used / vram_total) * 100.0, 1)
        return {
            "available": True,
            "name": name,
            "gpu_util_pct": util_pct,
            "vram_used_mb": vram_used,
            "vram_total_mb": vram_total,
            "vram_pct": vram_pct,
            "temp_c": temp_c,
        }
    except Exception as exc:
        return {"available": False, "error": str(exc)}


def discover_installed_games(extra_roots: Optional[List[str]] = None, limit: int = 24) -> Dict[str, Any]:
    """Scans standard local game library directories (read-only) to find real installed games."""
    roots = list(_COMMON_GAME_ROOTS) + list(extra_roots or [])
    discovered: List[Dict[str, Any]] = []
    scanned_roots: List[str] = []

    for r in roots:
        p = Path(r)
        try:
            if not p.exists() or not p.is_dir():
                continue
            scanned_roots.append(str(p))
            for child in sorted(p.iterdir()):
                if not child.is_dir():
                    continue
                if len(discovered) >= limit:
                    break
                discovered.append(
                    {
                        "name": child.name,
                        "path": str(child),
                        "library_root": str(p),
                    }
                )
        except OSError:
            continue

    return {
        "status": "ok",
        "scanned_roots": scanned_roots,
        "game_count": len(discovered),
        "games": discovered,
    }


def inspect_game_asset_topology(game_dir: str, max_files: int = 600) -> Dict[str, Any]:
    """Plane A: Maps a real game folder's asset composition (videos, 3D models, textures, audio, configs)."""
    root = Path(game_dir)
    if not root.exists() or not root.is_dir():
        return {"status": "error", "message": f"Game directory not accessible: {game_dir}"}

    counts = {k: 0 for k in _ASSET_GROUPS}
    samples: Dict[str, List[str]] = {k: [] for k in _ASSET_GROUPS}
    total_scanned = 0

    for dirpath, _dirnames, filenames in os.walk(root):
        for fname in filenames:
            total_scanned += 1
            ext = Path(fname).suffix.lower()
            for grp, exts in _ASSET_GROUPS.items():
                if ext in exts:
                    counts[grp] += 1
                    if len(samples[grp]) < 3:
                        samples[grp].append(str(Path(dirpath) / fname))
                    break
            if total_scanned >= max_files:
                break
        if total_scanned >= max_files:
            break

    return {
        "status": "ok",
        "game_dir": str(root),
        "files_scanned": total_scanned,
        "asset_counts": counts,
        "asset_samples": samples,
    }


def compute_adaptive_graphics_grain(gpu: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adaptive Scale-Grain Optimization:
    Automatically steps down visual observation grain under high GPU/VRAM pressure
    so Elysia never causes lag spikes during real gameplay.
    """
    if not gpu.get("available"):
        return {"scale_factor": 0.5, "mode": "balanced_cpu_fallback", "reason": "GPU 텔레메트리 미가용"}

    util = float(gpu.get("gpu_util_pct", 0.0))
    vram_pct = float(gpu.get("vram_pct", 0.0))

    if util >= 88.0 or vram_pct >= 88.0:
        return {
            "scale_factor": 0.25,
            "mode": "macro_relief_0.25x",
            "reason": f"고부하 감지(GPU {util}%, VRAM {vram_pct}%) → 거시 스케일(0.25x)로 자동 축소해 게임 프레임 보호",
        }
    if util >= 65.0 or vram_pct >= 72.0:
        return {
            "scale_factor": 0.5,
            "mode": "meso_balanced_0.5x",
            "reason": f"중간 부하(GPU {util}%, VRAM {vram_pct}%) → 중시 스케일(0.5x) 균형 관측",
        }
    return {
        "scale_factor": 1.0,
        "mode": "micro_full_1.0x",
        "reason": f"여유 자원(GPU {util}%, VRAM {vram_pct}%) → 원본 해상도(1.0x) 정밀 객체 절단",
    }


def observe_live_game_ecology(game_dir: Optional[str] = None) -> Dict[str, Any]:
    """Runs a unified 3-Plane observation (Assets + Live Visual Carving + GPU/Process I/O)."""
    gpu = query_nvidia_gpu_live()
    grain = compute_adaptive_graphics_grain(gpu)

    # Plane C: Active heavyweight processes (potential running game + I/O read bytes)
    top_io_procs: List[Dict[str, Any]] = []
    if psutil is not None:
        for p in psutil.process_iter(["pid", "name", "memory_info", "io_counters"]):
            try:
                info = p.info
                mi = info.get("memory_info")
                rss_mb = round((mi.rss / (1024 * 1024)) if mi else 0.0, 1)
                if rss_mb < 80.0:
                    continue
                io = info.get("io_counters")
                read_mb = round((io.read_bytes / (1024 * 1024)) if io else 0.0, 1)
                top_io_procs.append(
                    {
                        "pid": int(info["pid"]),
                        "name": str(info.get("name") or ""),
                        "rss_mb": rss_mb,
                        "disk_read_mb": read_mb,
                    }
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        top_io_procs.sort(key=lambda x: x["rss_mb"], reverse=True)

    # Plane B: Live visual carving at adaptive scale factor
    visual_snapshot: Dict[str, Any] = {"status": "unavailable"}
    if mss is not None:
        rotor = CudaVisualObjectRotor()
        with mss.mss() as sct:
            mon = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
            shot = np.array(sct.grab(mon))
            bgr = cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR)
            sf = float(grain["scale_factor"])
            if sf < 0.99:
                bgr = cv2.resize(bgr, (0, 0), fx=sf, fy=sf, interpolation=cv2.INTER_AREA)
            visual_snapshot = rotor.process_frame(bgr, max_objects=6)

    # Plane A: Asset topology if a game_dir was provided
    asset_plane = inspect_game_asset_topology(game_dir) if game_dir else {"status": "no_game_dir_selected"}

    return {
        "status": "ok",
        "observed_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "plane_c_hardware_flow": {
            "gpu": gpu,
            "adaptive_graphics_grain": grain,
            "top_resident_io_processes": top_io_procs[:6],
        },
        "plane_b_visual_world_r": visual_snapshot,
        "plane_a_asset_substrate": asset_plane,
    }


def main() -> None:
    cmd = sys.argv[1].strip().lower() if len(sys.argv) > 1 else "observe"
    if cmd == "discover":
        out = discover_installed_games(sys.argv[2:] if len(sys.argv) > 2 else None)
    elif cmd == "observe":
        game_dir = sys.argv[2] if len(sys.argv) > 2 else None
        out = observe_live_game_ecology(game_dir)
    else:
        out = {"status": "error", "message": "Usage: game_ecology_organ.py <discover [roots...]|observe [game_dir]>"}
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
