r"""
ELYSIA Read-Only Commercial Game Architecture & Data-Array Structure Observer
=============================================================================

Strictly READ-ONLY, ZERO decryption/cracking, ZERO copyrighted asset extraction:
Observes HOW real commercial AAA games (`AzurPromilia`, `SwordofConvallaria`)
structurally organize massive multi-gigabyte worlds:
  1. Size-Scale Octave Distribution (<1KB, 1-16KB, 16-256KB, 256KB-4MB, >4MB)
  2. Header Signature & Shannon Byte-Entropy Spectrum (structured metadata vs compressed blocks)
  3. Directory Scale Hierarchy
  4. Real `ffprobe` media encoding structure on open `.mp4` streams & `.proto` schema structure
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Dict, List

import numpy as np

THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from real_tool_organ import discover_real_tool_organs  # noqa: E402


def _shannon_entropy(sample: bytes) -> float:
    if not sample:
        return 0.0
    counts = np.bincount(np.frombuffer(sample, dtype=np.uint8), minlength=256)
    probs = counts[counts > 0] / float(len(sample))
    return round(float(-np.sum(probs * np.log2(probs))), 3)


def _size_octave(sz: int) -> str:
    if sz < 1024:
        return "<1KB (미시 메타)"
    if sz < 16 * 1024:
        return "1~16KB (소형 블록)"
    if sz < 256 * 1024:
        return "16~256KB (중형 에셋)"
    if sz < 4 * 1024 * 1024:
        return "256KB~4MB (대형 리소스)"
    return ">4MB (거시 스트림/팩)"


def analyze_game_data_architecture(root_dir: Path, sample_ext: str = ".r", max_walk: int = 12000) -> Dict[str, Any]:
    if not root_dir.exists():
        return {"status": "not_found", "path": str(root_dir)}

    top_dirs = sorted(p.name for p in root_dir.iterdir() if p.is_dir())[:20]
    octave_counts: Dict[str, int] = {}
    ext_bytes: Dict[str, int] = {}
    sampled_headers: List[Dict[str, Any]] = []
    total_files = 0
    total_bytes = 0

    for dirpath, _dirnames, filenames in os.walk(root_dir):
        for fname in filenames:
            fpath = Path(dirpath) / fname
            try:
                sz = fpath.stat().st_size
            except OSError:
                continue
            total_files += 1
            total_bytes += sz
            ext = fpath.suffix.lower() or "(none)"
            ext_bytes[ext] = ext_bytes.get(ext, 0) + sz
            oct_lbl = _size_octave(sz)
            octave_counts[oct_lbl] = octave_counts.get(oct_lbl, 0) + 1

            if ext == sample_ext and len(sampled_headers) < 10 and sz >= 16:
                try:
                    with open(fpath, "rb") as fh:
                        head = fh.read(4096)
                    magic_hex = head[:8].hex()
                    ascii_hint = "".join(chr(b) if 32 <= b < 127 else "." for b in head[:8])
                    sampled_headers.append(
                        {
                            "file": fpath.name,
                            "size_kb": round(sz / 1024.0, 1),
                            "magic_8b_hex": magic_hex,
                            "magic_ascii": ascii_hint,
                            "entropy_4kb": _shannon_entropy(head),
                        }
                    )
                except OSError:
                    pass
            if total_files >= max_walk:
                break
        if total_files >= max_walk:
            break

    top_ext_mb = sorted(
        ((k, round(v / (1024 ** 2), 2)) for k, v in ext_bytes.items()),
        key=lambda x: -x[1],
    )[:8]

    return {
        "status": "ok",
        "root": str(root_dir),
        "top_directories": top_dirs,
        "files_walked": total_files,
        "total_size_gb_walked": round(total_bytes / (1024 ** 3), 2),
        "size_octave_distribution": octave_counts,
        "top_extensions_by_mb": top_ext_mb,
        "sampled_shard_headers": sampled_headers[:6],
    }


def inspect_open_proto_and_mp4(conv_dir: Path) -> Dict[str, Any]:
    if not conv_dir.exists():
        return {"status": "not_found"}

    proto_samples: List[Dict[str, Any]] = []
    for p in list(conv_dir.rglob("*.proto"))[:4]:
        try:
            raw = p.read_bytes()[:4096]
            ent = _shannon_entropy(raw)
            txt = raw.decode("utf-8", errors="ignore")
            msgs = re.findall(r"\bmessage\s+([A-Za-z0-9_]+)", txt)
            proto_samples.append({"file": p.name, "size_b": p.stat().st_size, "entropy": ent, "messages_found": msgs[:8]})
        except OSError:
            continue

    mp4_probe: Dict[str, Any] = {"status": "no_mp4"}
    ff_bin = discover_real_tool_organs()["organs"]["ffmpeg_4k_media"].get("binary")
    ffprobe_bin = str(Path(ff_bin).with_name("ffprobe.exe")) if ff_bin else None
    first_mp4 = next(conv_dir.rglob("*.mp4"), None)
    if first_mp4 and ffprobe_bin and Path(ffprobe_bin).exists():
        proc = subprocess.run(
            [ffprobe_bin, "-v", "quiet", "-print_format", "json", "-show_streams", str(first_mp4)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            data = json.loads(proc.stdout)
            vstreams = [s for s in data.get("streams", []) if s.get("codec_type") == "video"]
            if vstreams:
                vs = vstreams[0]
                mp4_probe = {
                    "file": first_mp4.name,
                    "codec": vs.get("codec_name"),
                    "resolution": [vs.get("width"), vs.get("height")],
                    "pix_fmt": vs.get("pix_fmt"),
                    "fps": vs.get("r_frame_rate"),
                    "bit_rate_kbps": round(int(vs.get("bit_rate", 0)) / 1000.0, 1) if vs.get("bit_rate") else None,
                }

    return {"status": "ok", "proto_structure_samples": proto_samples, "mp4_ffprobe_structure": mp4_probe}


if __name__ == "__main__":
    out = {
        "azur_promilia_structure": analyze_game_data_architecture(Path(r"C:\Nexon\AzurPromilia"), sample_ext=".r", max_walk=15000),
        "sword_of_convallaria_protocols": inspect_open_proto_and_mp4(Path(r"C:\Program Files\SwordofConvallaria")),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
