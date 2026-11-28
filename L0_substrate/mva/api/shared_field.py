"""
Cross-Platform Shared Topology Field Buffer for MVA.
Uses Windows named shared memory (Local\\ElysiaTopologyField) when available,
and falls back seamlessly to a thread-safe in-process rotor buffer on Linux/macOS.
"""
from __future__ import annotations

import mmap
import platform
import struct
import threading
from typing import Dict, List

_HEADER_SIZE = 12
_BUFFER_SIZE = 1024 * 1024 * 16
_ROTOR_STRUCT = struct.Struct("<BBBBHBB")

_LOCK = threading.Lock()
# Sparse fallback & active-index mirror: rotor_index -> (math_t, lang_t, spatial_t, temporal_t, light_mass, byte_val, pad)
_FALLBACK_ROTORS: Dict[int, tuple] = {}
_WIN_SHM: mmap.mmap | None = None


def _get_win_shm() -> mmap.mmap | None:
    global _WIN_SHM
    if platform.system() != "Windows":
        return None
    if _WIN_SHM is not None:
        return _WIN_SHM
    try:
        _WIN_SHM = mmap.mmap(0, _BUFFER_SIZE, tagname="Local\\ElysiaTopologyField", access=mmap.ACCESS_WRITE)
        return _WIN_SHM
    except Exception:
        return None


def write_rotor_tension(tension: float, observation_axis: str = "spatial", rotor_idx: int | None = None) -> bool:
    """Write continuous tension value into the shared rotor field (cross-platform)."""
    base_tension = int(min(255, max(0.0, tension * 10.0)))
    num_rotors = (_BUFFER_SIZE - _HEADER_SIZE) // _ROTOR_STRUCT.size
    idx = (num_rotors // 2) if rotor_idx is None else (rotor_idx % num_rotors)

    with _LOCK:
        prev = _FALLBACK_ROTORS.get(idx, (0, 0, 0, 0, 0, ord("*"), 0))
        math_t, lang_t, spatial_t, temporal_t, light_mass, byte_val, pad = prev
        if observation_axis == "math":
            math_t = base_tension
        elif observation_axis == "lang":
            lang_t = base_tension
        elif observation_axis == "spatial":
            spatial_t = base_tension
        elif observation_axis == "temporal":
            temporal_t = base_tension
        if base_tension < 10:
            light_mass = min(65535, light_mass + 1)
        packed = _ROTOR_STRUCT.pack(math_t, lang_t, spatial_t, temporal_t, light_mass, byte_val, pad)
        _FALLBACK_ROTORS[idx] = (math_t, lang_t, spatial_t, temporal_t, light_mass, byte_val, pad)

        shm = _get_win_shm()
        if shm is not None:
            try:
                offset = _HEADER_SIZE + (idx * _ROTOR_STRUCT.size)
                shm.seek(offset)
                shm.write(packed)
            except Exception:
                pass
    return True


def read_active_rotors(stride: int = 100) -> List[Dict]:
    """Read active non-zero tension rotors from Windows shared memory & active index mirror."""
    points: List[Dict] = []
    seen_indices: set[int] = set()
    with _LOCK:
        shm = _get_win_shm()
        if shm is not None:
            try:
                max_rotors = (_BUFFER_SIZE - _HEADER_SIZE) // _ROTOR_STRUCT.size
                # Sample both strided slots and any explicit active rotor indices
                probe_indices = list(range(0, max_rotors, max(1, stride)))
                for explicit_idx in _FALLBACK_ROTORS:
                    if explicit_idx not in seen_indices and explicit_idx % max(1, stride) != 0:
                        probe_indices.append(explicit_idx)
                for i in probe_indices:
                    if i in seen_indices:
                        continue
                    seen_indices.add(i)
                    shm.seek(_HEADER_SIZE + i * _ROTOR_STRUCT.size)
                    raw = shm.read(_ROTOR_STRUCT.size)
                    if len(raw) == _ROTOR_STRUCT.size:
                        math_t, lang_t, spatial_t, temporal_t, _, byte_val, _ = _ROTOR_STRUCT.unpack(raw)
                        if math_t > 0 or lang_t > 0 or spatial_t > 0:
                            points.append({
                                "position": [math_t / 10.0, lang_t / 10.0, spatial_t / 10.0],
                                "velocity": [0.0, 0.0, 0.0],
                                "phase": temporal_t / 255.0 * 3.14159265,
                                "token": chr(byte_val) if 32 <= byte_val <= 126 else "*",
                            })
                if points:
                    return points
            except Exception:
                pass

        for _, (math_t, lang_t, spatial_t, temporal_t, _, byte_val, _) in _FALLBACK_ROTORS.items():
            if math_t > 0 or lang_t > 0 or spatial_t > 0:
                points.append({
                    "position": [math_t / 10.0, lang_t / 10.0, spatial_t / 10.0],
                    "velocity": [0.0, 0.0, 0.0],
                    "phase": temporal_t / 255.0 * 3.14159265,
                    "token": chr(byte_val) if 32 <= byte_val <= 126 else "*",
                })
    return points
