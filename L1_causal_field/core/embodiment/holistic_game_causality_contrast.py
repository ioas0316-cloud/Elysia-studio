r"""
ELYSIA Holistic 3-Layer Game Structure-to-Phenomenon Contrast Engine
====================================================================

Strictly READ-ONLY, ZERO decryption/cracking, ZERO copyrighted asset extraction.
Observes and cross-contrasts HOW real commercial games turn:

  [Layer A: Asset & Data-Array Containers] (Scale octaves, magic headers, entropy, catalogs)
      -->
  [Layer B: Runtime Engine & Coupling Principles] (Unity/IL2CPP/Addressables/Audio/Physics/Network)
      -->
  [Layer C: Resulting Phenomenon] (Video stream encoding + Bidirectional Overlay-Contrast motion/residual)

Across 3 real commercial titles on this host:
  1. Eternal Return (`C:\Program Files (x86)\Steam\steamapps\common\Eternal Return`)
  2. Azur Promilia (`C:\Nexon\AzurPromilia`)
  3. Sword of Convallaria (`C:\Program Files\SwordofConvallaria`)
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Dict, List

import numpy as np

THIS_DIR = Path(__file__).resolve().parent
for _p in (str(THIS_DIR),):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from real_tool_organ import discover_real_tool_organs  # noqa: E402
from self_cognitive_expansion_cortex import (  # noqa: E402
    COGNITIVE_WORLD_DIR,
    _load_json,
    _save_json,
    _shannon_entropy,
)


ETERNAL_RETURN_ROOT = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Eternal Return")
AZUR_PROMILIA_ROOT = Path(r"C:\Nexon\AzurPromilia")
SWORD_CONVALLARIA_ROOT = Path(r"C:\Program Files\SwordofConvallaria")
HOLISTIC_REPORT_PATH = COGNITIVE_WORLD_DIR / "holistic_game_causality_contrast.json"


def _size_octave(sz: int) -> str:
    if sz < 1024:
        return "<1KB_micro_meta"
    if sz < 16 * 1024:
        return "1_16KB_small_block"
    if sz < 256 * 1024:
        return "16_256KB_mid_asset"
    if sz < 4 * 1024 * 1024:
        return "256KB_4MB_large_resource"
    return ">4MB_macro_stream_pack"


def _classify_subsystem(path_str: str, ext: str) -> str:
    low = path_str.lower()
    if ext in (".mp4", ".webm", ".mov", ".avi"):
        return "video_phenomenon_streams"
    if ext in (".bank", ".wem", ".bnk", ".ogg", ".wav", ".fsb"):
        return "audio_banks_and_streams"
    if ext in (".dll", ".so", ".exe", ".pdb", ".dat") and ("il2cpp" in low or "managed" in low or "plugins" in low or ext == ".dll"):
        return "runtime_engine_and_code"
    if ext in (".json", ".xml", ".proto", ".yaml", ".ini", ".cfg", ".txt", ".catalog", ".hash"):
        return "schema_catalog_and_metadata"
    if ext in (".bundle", ".assets", ".ress", ".resource", ".r", ".pak", ".ab", ".unity3d"):
        return "3d_asset_and_world_containers"
    return "other_supporting_files"


def audit_game_holistically(name: str, root: Path, max_walk: int = 20000) -> Dict[str, Any]:
    if not root.exists():
        return {"game": name, "status": "not_found", "root": str(root)}

    octave_counts: Dict[str, int] = {}
    subsystem_stats: Dict[str, Dict[str, Any]] = {}
    runtime_markers: List[str] = []
    header_samples: Dict[str, Dict[str, Any]] = {}
    gadget_links: List[str] = []

    total_files = 0
    total_bytes = 0

    for dirpath, dirnames, filenames in os.walk(root):
        dlow = dirpath.lower()
        for dn in dirnames:
            dnl = dn.lower()
            if dnl in ("il2cpp_data", "managed", "streamingassets", "aa", "plugins", "wwise", "fmod"):
                marker = f"{Path(dirpath).name}/{dn}"
                if marker not in runtime_markers and len(runtime_markers) < 16:
                    runtime_markers.append(marker)

        for fname in filenames:
            fpath = Path(dirpath) / fname
            try:
                sz = fpath.stat().st_size
            except OSError:
                continue
            total_files += 1
            total_bytes += sz
            ext = fpath.suffix.lower() or "(none)"

            # Detect key runtime DLL/metadata landmarks
            fl = fname.lower()
            if fl in ("unityplayer.dll", "gameassembly.dll", "global-metadata.dat", "catalog.json", "settings.json", "fmodstudio.dll", "akSoundEngine.dll".lower()):
                if fname not in runtime_markers:
                    runtime_markers.append(fname)
            if "8300400" in fl or ("gadgetskill" in fl and len(gadget_links) < 6):
                gadget_links.append(str(fpath.relative_to(root)))

            oct_k = _size_octave(sz)
            octave_counts[oct_k] = octave_counts.get(oct_k, 0) + 1

            sub_k = _classify_subsystem(str(fpath), ext)
            st = subsystem_stats.setdefault(sub_k, {"files": 0, "bytes": 0, "sample_exts": set()})
            st["files"] += 1
            st["bytes"] += sz
            if len(st["sample_exts"]) < 6:
                st["sample_exts"].add(ext)

            # Sample 1 header signature + Shannon entropy per subsystem
            if sub_k not in header_samples and sz >= 32:
                try:
                    with open(fpath, "rb") as fh:
                        head = fh.read(4096)
                    header_samples[sub_k] = {
                        "sample_file": fname,
                        "size_kb": round(sz / 1024.0, 1),
                        "magic_ascii": "".join(chr(b) if 32 <= b < 127 else "." for b in head[:8]),
                        "magic_hex": head[:8].hex(),
                        "entropy_4kb": _shannon_entropy(head),
                    }
                except OSError:
                    pass

            if total_files >= max_walk:
                break
        if total_files >= max_walk:
            break

    # Format subsystem stats cleanly
    subsystems_clean: Dict[str, Any] = {}
    for k, v in sorted(subsystem_stats.items(), key=lambda kv: -kv[1]["bytes"]):
        subsystems_clean[k] = {
            "files": v["files"],
            "size_mb": round(v["bytes"] / (1024 ** 2), 2),
            "share_pct": round(100.0 * v["bytes"] / max(1, total_bytes), 2),
            "extensions": sorted(v["sample_exts"]),
            "header_and_entropy": header_samples.get(k),
        }

    # Infer engine architecture from real disk landmarks
    m_lower = {m.lower() for m in runtime_markers}
    if "unityplayer.dll" in m_lower or any("unityfs" in (h.get("magic_ascii", "").lower()) for h in header_samples.values()):
        engine_arch = "Unity Engine" + (" (IL2CPP Native)" if "gameassembly.dll" in m_lower else " (Managed/Hybrid)")
    else:
        engine_arch = "Custom / Multi-Container Engine"

    return {
        "game": name,
        "status": "ok",
        "root": str(root),
        "files_walked": total_files,
        "total_size_gb": round(total_bytes / (1024 ** 3), 2),
        "layer_b_runtime_architecture": {
            "inferred_engine": engine_arch,
            "detected_runtime_markers": sorted(runtime_markers),
        },
        "layer_a_scale_octaves": octave_counts,
        "layer_a_subsystems": subsystems_clean,
        "linked_phenomenon_assets": gadget_links[:6],
    }


def probe_video_stream_spec(video_path: Path) -> Dict[str, Any]:
    ff_bin = discover_real_tool_organs().get("organs", {}).get("ffmpeg_4k_media", {}).get("binary")
    ffprobe = str(Path(ff_bin).with_name("ffprobe.exe")) if ff_bin else None
    if not video_path.is_file() or not ffprobe or not Path(ffprobe).is_file():
        return {"status": "unavailable"}
    proc = subprocess.run(
        [ffprobe, "-v", "quiet", "-print_format", "json", "-show_streams", str(video_path)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        return {"status": "probe_failed"}
    data = json.loads(proc.stdout)
    vs = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    if not vs:
        return {"status": "no_video_stream"}
    return {
        "file": video_path.name,
        "codec": vs.get("codec_name"),
        "resolution": [vs.get("width"), vs.get("height")],
        "pix_fmt": vs.get("pix_fmt"),
        "fps": vs.get("r_frame_rate"),
        "bit_rate_kbps": round(int(vs.get("bit_rate", 0)) / 1000.0, 1) if vs.get("bit_rate") else None,
    }


def run_holistic_game_causality_contrast() -> Dict[str, Any]:
    er = audit_game_holistically("Eternal Return", ETERNAL_RETURN_ROOT, max_walk=20000)
    ap = audit_game_holistically("Azur Promilia", AZUR_PROMILIA_ROOT, max_walk=15000)
    sc = audit_game_holistically("Sword of Convallaria", SWORD_CONVALLARIA_ROOT, max_walk=15000)

    er_video = ETERNAL_RETURN_ROOT / "EternalReturn_Data" / "StreamingAssets" / "GadgetSkillVideo" / "GadgetSkill8300400.mp4"
    er_video_spec = probe_video_stream_spec(er_video)
    contrast_verif = _load_json(COGNITIVE_WORLD_DIR / "conservation_contrast_verification.json", {})

    # Extract cross-game structural invariants strictly from observed telemetry
    observed_games = [g for g in (er, ap, sc) if g.get("status") == "ok"]
    invariants: List[Dict[str, Any]] = []
    for g in observed_games:
        subs = g.get("layer_a_subsystems") or {}
        meta_ent = ((subs.get("schema_catalog_and_metadata") or {}).get("header_and_entropy") or {}).get("entropy_4kb")
        pack_ent = ((subs.get("3d_asset_and_world_containers") or {}).get("header_and_entropy") or {}).get("entropy_4kb")
        invariants.append(
            {
                "game": g["game"],
                "engine": g["layer_b_runtime_architecture"]["inferred_engine"],
                "total_size_gb": g["total_size_gb"],
                "metadata_entropy_4kb": meta_ent,
                "container_entropy_4kb": pack_ent,
                "container_share_pct": (subs.get("3d_asset_and_world_containers") or {}).get("share_pct", 0.0),
                "audio_share_pct": (subs.get("audio_banks_and_streams") or {}).get("share_pct", 0.0),
                "video_share_pct": (subs.get("video_phenomenon_streams") or {}).get("share_pct", 0.0),
            }
        )

    report = {
        "schema": "elysia_holistic_game_causality_contrast_v1",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "causal_chain_model": "Layer A (Asset/Data-Array Containers) -> Layer B (Runtime Engine & Coupling Principles) -> Layer C (Rendered Phenomenon & Overlay-Contrast Residual)",
        "games": {
            "eternal_return": er,
            "azur_promilia": ap,
            "sword_of_convallaria": sc,
        },
        "eternal_return_layer_c_phenomenon": {
            "video_stream_spec": er_video_spec,
            "bidirectional_overlay_contrast": contrast_verif.get("contrast_self_correction_delta"),
            "pass2_refined_metrics": contrast_verif.get("pass2_contrast_refined"),
        },
        "cross_game_structural_contrast": invariants,
    }
    _save_json(HOLISTIC_REPORT_PATH, report)
    return report


if __name__ == "__main__":
    print(json.dumps(run_holistic_game_causality_contrast(), ensure_ascii=False, indent=2))
