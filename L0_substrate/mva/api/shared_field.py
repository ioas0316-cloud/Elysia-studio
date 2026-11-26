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
# Sparse fallback storage: rotor_index -> (math_t, lang_t, spatial_t, temporal_t, light_mass, byte_val, pad)
_FALLBACK_ROTORS: Dict[int, tuple] = {}


def write_rotor_tension(tension: float, observation_axis: str = "spatial", rotor_idx: int | None = None) -> bool:
    """Write continuous tension value into the shared rotor field (cross-platform)."""
    base_tension = int(min(255, max(0.0, tension * 10.0)))
    num_rotors = (_BUFFER_SIZE - _HEADER_SIZE) // _ROTOR_STRUCT.size
    idx = (num_rotors // 2) if rotor_idx is None else (rotor_idx % num_rotors)

    if platform.system() == "Windows":
        try:
            shm = mmap.mmap(0, _BUFFER_SIZE, tagname="Local\\ElysiaTopologyField", access=mmap.ACCESS_WRITE)
            offset = _HEADER_SIZE + (idx * _ROTOR_STRUCT.size)
            shm.seek(offset)
            raw = shm.read(_ROTOR_STRUCT.size)
            if len(raw) == _ROTOR_STRUCT.size:
                math_t, lang_t, spatial_t, temporal_t, light_mass, byte_val, pad = _ROTOR_STRUCT.unpack(raw)
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
                shm.seek(offset)
                shm.write(_ROTOR_STRUCT.pack(math_t, lang_t, spatial_t, temporal_t, light_mass, byte_val, pad))
            shm.close()
            return True
        except Exception:
            pass

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
        _FALLBACK_ROTORS[idx] = (math_t, lang_t, spatial_t, temporal_t, light_mass, byte_val, pad)
    return True


def read_active_rotors(stride: int = 100) -> List[Dict]:
    """Read active non-zero tension rotors from Windows shared memory or cross-platform fallback."""
    points: List[Dict] = []
    if platform.system() == "Windows":
        try:
            shm = mmap.mmap(0, _BUFFER_SIZE, tagname="Local\\ElysiaTopologyField", access=mmap.ACCESS_READ)
            max_rotors = (_BUFFER_SIZE - _HEADER_SIZE) // _ROTOR_STRUCT.size
            for i in range(0, max_rotors, max(1, stride)):
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
            shm.close()
            return points
        except Exception:
            pass

    with _LOCK:
        for _, (math_t, lang_t, spatial_t, temporal_t, _, byte_val, _) in _FALLBACK_ROTORS.items():
            if math_t > 0 or lang_t > 0 or spatial_t > 0:
                points.append({
                    "position": [math_t / 10.0, lang_t / 10.0, spatial_t / 10.0],
                    "velocity": [0.0, 0.0, 0.0],
                    "phase": temporal_t / 255.0 * 3.14159265,
                    "token": chr(byte_val) if 32 <= byte_val <= 126 else "*",
                })
    return points
