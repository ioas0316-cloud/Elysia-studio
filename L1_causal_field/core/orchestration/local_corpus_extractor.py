"""
Elysia Multi-Scale Local Corpus & Cross-Modal Invariant Extractor
================================================================================
Extracts Common Information (공통정보) and Cross-Modal Bindings (교차정보) from
arbitrary local directories — including multi-gigabyte PC game installations
(e.g. 85GB Unreal/Unity titles) — WITHOUT loading files into RAM or using any
external LLM API:

  S0 — Directory Topology Pass:
       Streams filenames, folder hierarchy, extensions, and byte sizes.
  S1 — Bounded Header Slice Probe (<= 8KB per sampled file):
       Detects real binary container/asset magic signatures (UnityFS, Unreal
       PAK/UAsset, Wwise BKHD/WEM, CRIWARE CPK/AFS2, DDS, KTX2, GLB, PNG, etc.),
       computes exact Shannon entropy (bits/byte) to honestly separate readable
       symbolic data from compressed/encrypted archives, and extracts recurring
       ASCII identifier symbols (bones, animation states, shaders, config keys).
  S2 — Cross-Modal Entity Alignment (교차정보화):
       Strips engine modality prefixes/suffixes (SK_, SM_, T_, M_, A_, VO_,
       _Albedo, _Normal, _LOD0, _Idle, etc.) so files sharing the same entity
       stem across distinct modalities (Geometry x Texture x Motion x Audio x
       Logic) bind into unified Cross-Modal Entity Nodes & Coupling Matrices.
"""

from __future__ import annotations

import json
import math
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


MODALITY_LABELS_KO: Dict[str, str] = {
    "geometry_3d": "3D 형상·메시",
    "visual_texture": "시각·텍스처·이미지",
    "motion_anim": "움직임·애니메이션",
    "audio_wave": "음향·보이스·파동",
    "logic_script": "로직·스크립트·코드",
    "config_data": "설정·테이블·데이터",
    "archive_container": "압축·패키지 컨테이너",
    "binary_runtime": "실행·라이브러리 바이너리",
}

EXT_TO_MODALITY: Dict[str, str] = {
    # 3D geometry / shaders
    ".fbx": "geometry_3d", ".obj": "geometry_3d", ".glb": "geometry_3d",
    ".gltf": "geometry_3d", ".mesh": "geometry_3d", ".vrm": "geometry_3d",
    ".pmx": "geometry_3d", ".smd": "geometry_3d", ".usd": "geometry_3d",
    ".usdc": "geometry_3d", ".hlsl": "geometry_3d", ".glsl": "geometry_3d",
    ".shader": "geometry_3d", ".mat": "geometry_3d",
    # Visual / Textures
    ".png": "visual_texture", ".jpg": "visual_texture", ".jpeg": "visual_texture",
    ".webp": "visual_texture", ".tga": "visual_texture", ".dds": "visual_texture",
    ".ktx": "visual_texture", ".ktx2": "visual_texture", ".astc": "visual_texture",
    ".bmp": "visual_texture", ".exr": "visual_texture", ".hdr": "visual_texture",
    ".svg": "visual_texture", ".mp4": "visual_texture", ".webm": "visual_texture",
    ".usm": "visual_texture", ".bik": "visual_texture",
    # Motion / Animation
    ".anim": "motion_anim", ".bvh": "motion_anim", ".vmd": "motion_anim",
    ".hkx": "motion_anim", ".motion": "motion_anim", ".clip": "motion_anim",
    # Audio / Voice
    ".wav": "audio_wave", ".ogg": "audio_wave", ".mp3": "audio_wave",
    ".flac": "audio_wave", ".wem": "audio_wave", ".bnk": "audio_wave",
    ".awb": "audio_wave", ".acb": "audio_wave", ".hca": "audio_wave",
    ".fsb": "audio_wave", ".pck": "audio_wave",
    # Logic / Scripts / Code
    ".lua": "logic_script", ".py": "logic_script", ".js": "logic_script",
    ".mjs": "logic_script", ".ts": "logic_script", ".cs": "logic_script",
    ".cpp": "logic_script", ".h": "logic_script", ".c": "logic_script",
    ".cdsl": "logic_script",
    # Config / Structured Data / Text
    ".json": "config_data", ".xml": "config_data", ".yaml": "config_data",
    ".yml": "config_data", ".ini": "config_data", ".cfg": "config_data",
    ".csv": "config_data", ".tsv": "config_data", ".txt": "config_data",
    ".md": "config_data", ".db": "config_data", ".sqlite": "config_data",
    ".locres": "config_data", ".po": "config_data",
    # Archives / Engine Bundles
    ".pak": "archive_container", ".ucas": "archive_container", ".utoc": "archive_container",
    ".uasset": "archive_container", ".uexp": "archive_container", ".umap": "archive_container",
    ".bundle": "archive_container", ".ab": "archive_container", ".assets": "archive_container",
    ".ress": "archive_container", ".cpk": "archive_container", ".zip": "archive_container",
    ".7z": "archive_container", ".blk": "archive_container", ".vpk": "archive_container",
    # Runtime binaries
    ".dll": "binary_runtime", ".exe": "binary_runtime", ".so": "binary_runtime",
    ".dylib": "binary_runtime", ".bin": "binary_runtime", ".dat": "binary_runtime",
}

ENTITY_PREFIX_RE = re.compile(
    r"^(?:sk|sm|t|tx|tex|m|mi|mt|mat|a|am|an|anim|vo|sfx|bgm|se|fx|vfx|ui|ico|icon|char|npc|mon|env|wp|wep|eff|bp|dt|da|w)_+",
    re.IGNORECASE,
)
ENTITY_SUFFIX_RE = re.compile(
    r"(?:_+(?:lod\d+|albedo|basecolor|diffuse|diff|normal|nrm|norm|roughness|rough|metallic|metal|orm|ao|mask|emissive|emit|specular|spec|mesh|skel|skeleton|rig|anim|idle|walk|run|attack|smile|blink|hurt|voice|vo|sfx|bgm|ai|ctrl|controller|script|cfg|config|data|info|mat|material|shader|v\d+|\d{1,4}))+$",
    re.IGNORECASE,
)
SYMBOL_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]{3,28}")
NOISE_SYMBOLS: Set[str] = {
    "true", "false", "null", "none", "self", "this", "return", "const", "function",
    "import", "export", "from", "class", "default", "public", "private", "static",
    "void", "int", "float", "double", "string", "bool", "http", "https", "utf8",
    "width", "height", "size", "length", "name", "type", "value", "data", "index",
    "count", "item", "list", "dict", "none", "init", "main", "file", "path",
}


def shannon_entropy_bits(buf: bytes) -> float:
    """Exact byte-level Shannon entropy in [0.0, 8.0] bits/byte."""
    n = len(buf)
    if n == 0:
        return 0.0
    counts = Counter(buf)
    ent = 0.0
    for c in counts.values():
        p = c / n
        ent -= p * math.log2(p)
    return round(ent, 3)


def detect_magic_signature(header: bytes, ext: str) -> str:
    """Detect real binary container & media magic headers from a small slice."""
    if not header:
        return f"Empty({ext or 'none'})"
    if header.startswith(b"UnityFS"):
        return "UnityFS_Bundle"
    if header.startswith(b"UnityWeb") or header.startswith(b"UnityRaw"):
        return "Unity_Archive"
    if header.startswith(b"\xc1\x83\x2a\x9e"):
        return "Unreal_UAsset"
    if header.startswith(b"BKHD"):
        return "Wwise_SoundBank"
    if header.startswith(b"RIFF"):
        return "RIFF_Wave_WEM"
    if header.startswith(b"OggS"):
        return "Ogg_Audio"
    if header.startswith(b"CPK "):
        return "CRIWARE_CPK"
    if header.startswith(b"AFS2"):
        return "CRIWARE_AFS2"
    if header.startswith(b"@UTF"):
        return "CRIWARE_UTF_Table"
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "PNG_Image"
    if header.startswith(b"\xff\xd8\xff"):
        return "JPEG_Image"
    if header.startswith(b"DDS "):
        return "DDS_Texture"
    if header.startswith(b"\xabKTX "):
        return "KTX_Texture"
    if header.startswith(b"glTF"):
        return "GLB_3D_Model"
    if header.startswith(b"Kaydara FBX"):
        return "FBX_3D_Model"
    if header.startswith(b"SQLite format 3"):
        return "SQLite_DB"
    if header.startswith(b"PK\x03\x04"):
        return "ZIP_Container"
    if header.startswith(b"MZ"):
        return "PE_Binary_DLL_EXE"
    if header.startswith(b"\x7fELF"):
        return "ELF_Binary"
    if header.startswith(b"DXBC"):
        return "DirectX_Shader"
    if ext == ".pak":
        return "Unreal_PAK_Container"
    if ext in (".ucas", ".utoc"):
        return "Unreal_IOStore"
    if ext in (".json", ".lua", ".py", ".js", ".mjs", ".ts", ".md", ".txt", ".ini", ".cfg", ".xml", ".yaml", ".yml", ".csv"):
        return f"Readable_{ext.lstrip('.').upper()}"
    return f"Binary({ext or 'raw'})"


def classify_modality(ext: str, rel_path: str, magic: str) -> str:
    """Map an asset file into its canonical sensory/structural modality."""
    low_path = rel_path.lower()
    if magic in ("PNG_Image", "JPEG_Image", "DDS_Texture", "KTX_Texture"):
        return "visual_texture"
    if magic in ("GLB_3D_Model", "FBX_3D_Model", "DirectX_Shader"):
        return "geometry_3d"
    if magic in ("Wwise_SoundBank", "RIFF_Wave_WEM", "Ogg_Audio", "CRIWARE_AFS2"):
        return "audio_wave"
    if magic in ("Unreal_UAsset",):
        # Refine Unreal UAssets by standard naming/folder conventions!
        fname = os.path.basename(low_path)
        if fname.startswith(("t_", "tex_")) or "/texture" in low_path:
            return "visual_texture"
        if fname.startswith(("a_", "am_", "anim_")) or "/anim" in low_path or "/motion" in low_path:
            return "motion_anim"
        if fname.startswith(("sk_", "sm_", "mesh_")) or "/mesh" in low_path or "/model" in low_path:
            return "geometry_3d"
        if fname.startswith(("vo_", "sfx_", "bgm_", "w_")) or "/audio" in low_path or "/sound" in low_path:
            return "audio_wave"
        if fname.startswith(("bp_", "ai_")) or "/blueprint" in low_path or "/script" in low_path:
            return "logic_script"
        return "archive_container"
    return EXT_TO_MODALITY.get(ext.lower(), "binary_runtime")


def extract_entity_stem(filename: str, parent_dir: str = "") -> str:
    """
    Normalize cross-modal entity stem so:
      SK_AzurChar_LOD0.uasset + T_AzurChar_Albedo.dds + A_AzurChar_Smile.anim + VO_AzurChar_01.wem
    all converge to the exact same entity stem: 'azurchar'!
    """
    base = os.path.splitext(filename)[0].strip()
    if not base:
        return ""
    cleaned = ENTITY_PREFIX_RE.sub("", base)
    # Apply suffix stripping iteratively for compound suffixes like _Albedo_LOD0_01
    for _ in range(3):
        nxt = ENTITY_SUFFIX_RE.sub("", cleaned)
        if nxt == cleaned:
            break
        cleaned = nxt
    cleaned = re.sub(r"[^0-9A-Za-z가-힣_]+", "_", cleaned).strip("_").lower()
    if len(cleaned) < 3 or cleaned.isdigit():
        # Fall back to meaningful parent folder if filename is purely numeric (e.g. Char_01/001.wem)
        p_clean = re.sub(r"[^0-9A-Za-z가-힣_]+", "_", (parent_dir or "").strip()).strip("_").lower()
        if len(p_clean) >= 3 and p_clean not in ("assets", "static", "textures", "audio", "models", "scripts", "data", "content", "paks"):
            return p_clean[:32]
        return ""
    return cleaned[:36]


def extract_ascii_symbols(header: bytes, max_symbols: int = 16) -> List[str]:
    """Extract clean readable structural identifiers from text or uncompressed binary headers."""
    if not header:
        return []
    try:
        text = header.decode("latin-1", errors="ignore")
    except Exception:
        return []
    out: List[str] = []
    seen: Set[str] = set()
    for m in SYMBOL_TOKEN_RE.findall(text):
        low = m.lower()
        if low in NOISE_SYMBOLS or len(m) < 4:
            continue
        # Favor structured symbols (CamelCase, snake_case, or domain words)
        if low not in seen:
            seen.add(low)
            out.append(m)
            if len(out) >= max_symbols:
                break
    return out


def infer_engine_fingerprint(magic_counts: Counter, ext_counts: Counter) -> str:
    unreal_hits = (
        magic_counts.get("Unreal_UAsset", 0)
        + magic_counts.get("Unreal_PAK_Container", 0)
        + magic_counts.get("Unreal_IOStore", 0)
        + ext_counts.get(".uasset", 0)
        + ext_counts.get(".pak", 0)
        + ext_counts.get(".ucas", 0)
    )
    unity_hits = (
        magic_counts.get("UnityFS_Bundle", 0)
        + magic_counts.get("Unity_Archive", 0)
        + ext_counts.get(".bundle", 0)
        + ext_counts.get(".assets", 0)
        + ext_counts.get(".ab", 0)
    )
    if unreal_hits > 0 and unreal_hits >= unity_hits:
        return "Unreal Engine Asset Pipeline"
    if unity_hits > 0:
        return "Unity AssetBundle Pipeline"
    if ext_counts.get(".py", 0) + ext_counts.get(".js", 0) > 5:
        return "Python/JS Causal Runtime Workspace"
    return "Mixed Multi-Modal Local Corpus"


def analyze_local_directory(
    root_dir: Path,
    *,
    corpus_name: str = "",
    max_files: int = 80000,
    max_header_probes: int = 400,
    header_bytes_len: int = 4096,
) -> Dict[str, Any]:
    """
    Stream-scan a local directory using O(1) memory per file (bounded header slices)
    to extract cross-modal common invariants without ever loading full files!
    """
    root = Path(root_dir).resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Directory does not exist: {root}")

    skip_dirs = {"node_modules", ".git", "__pycache__", ".venv", "venv", "dist", ".next"}
    total_files = 0
    total_bytes = 0
    probed_files = 0

    modality_counts: Counter = Counter()
    modality_bytes: Counter = Counter()
    ext_counts: Counter = Counter()
    magic_counts: Counter = Counter()
    symbol_counts: Counter = Counter()

    # entity_stem -> { modalities: set, files: int, total_bytes: int, examples: list }
    entity_map: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {"modalities": set(), "files": 0, "bytes": 0, "examples": []}
    )

    entropy_buckets = {"readable_symbolic": 0, "structured_media": 0, "compressed_or_encrypted": 0}
    entropy_sum = 0.0
    entropy_n = 0

    stack = [root]
    while stack and total_files < max_files:
        cur = stack.pop()
        try:
            with os.scandir(cur) as it:
                for entry in it:
                    if total_files >= max_files:
                        break
                    name = entry.name
                    if entry.is_dir(follow_symlinks=False):
                        if name not in skip_dirs and not name.startswith("."):
                            stack.append(Path(entry.path))
                        continue
                    if not entry.is_file(follow_symlinks=False):
                        continue

                    total_files += 1
                    try:
                        fsize = entry.stat(follow_symlinks=False).st_size
                    except OSError:
                        fsize = 0
                    total_bytes += fsize
                    ext = os.path.splitext(name)[1].lower()
                    ext_counts[ext or "(none)"] += 1
                    rel = os.path.relpath(entry.path, root).replace("\\", "/")
                    parent_name = os.path.basename(os.path.dirname(entry.path))

                    header = b""
                    if probed_files < max_header_probes and fsize > 0:
                        try:
                            with open(entry.path, "rb") as fh:
                                header = fh.read(header_bytes_len)
                            probed_files += 1
                        except OSError:
                            header = b""

                    magic = detect_magic_signature(header, ext) if header else f"Ext({ext or 'raw'})"
                    if header:
                        magic_counts[magic] += 1
                        ent = shannon_entropy_bits(header)
                        entropy_sum += ent
                        entropy_n += 1
                        if ent < 5.5:
                            entropy_buckets["readable_symbolic"] += 1
                            for sym in extract_ascii_symbols(header, max_symbols=12):
                                symbol_counts[sym] += 1
                        elif ent < 7.35:
                            entropy_buckets["structured_media"] += 1
                            for sym in extract_ascii_symbols(header, max_symbols=6):
                                symbol_counts[sym] += 1
                        else:
                            entropy_buckets["compressed_or_encrypted"] += 1

                    mod = classify_modality(ext, rel, magic)
                    modality_counts[mod] += 1
                    modality_bytes[mod] += fsize

                    stem = extract_entity_stem(name, parent_name)
                    if stem:
                        em = entity_map[stem]
                        em["modalities"].add(mod)
                        em["files"] += 1
                        em["bytes"] += fsize
                        if len(em["examples"]) < 4:
                            em["examples"].append(name)
        except OSError:
            continue

    # Build Cross-Modal Entity list (entities bound across >= 2 distinct modalities!)
    cross_entities: List[Dict[str, Any]] = []
    pair_couplings: Counter = Counter()

    for stem, info in entity_map.items():
        mods = sorted(info["modalities"])
        if len(mods) >= 2:
            cross_entities.append(
                {
                    "entity": stem,
                    "modalities": mods,
                    "modality_count": len(mods),
                    "file_count": info["files"],
                    "size_mb": round(info["bytes"] / (1024 * 1024), 2),
                    "examples": info["examples"],
                }
            )
            for i in range(len(mods)):
                for j in range(i + 1, len(mods)):
                    pair_couplings[f"{mods[i]}<->{mods[j]}"] += 1

    cross_entities.sort(key=lambda x: (x["modality_count"], x["file_count"], x["size_mb"]), reverse=True)

    engine_fp = infer_engine_fingerprint(magic_counts, ext_counts)
    avg_entropy = round(entropy_sum / max(1, entropy_n), 3)
    encrypted_pct = round(
        100.0 * entropy_buckets["compressed_or_encrypted"] / max(1, entropy_n),
        1,
    )

    return {
        "schema_version": 1,
        "corpus_name": corpus_name or root.name,
        "engine_fingerprint": engine_fp,
        "total_files": total_files,
        "total_size_gb": round(total_bytes / (1024 ** 3), 4),
        "total_size_mb": round(total_bytes / (1024 ** 2), 2),
        "probed_headers": probed_files,
        "modality_counts": dict(modality_counts),
        "modality_size_mb": {k: round(v / (1024 ** 2), 2) for k, v in modality_bytes.items()},
        "top_magic_signatures": [
            {"magic": m, "count": c} for m, c in magic_counts.most_common(10)
        ],
        "cross_modal_entities": cross_entities[:24],
        "modality_couplings": [
            {"pair": p, "shared_entities": c} for p, c in pair_couplings.most_common(12)
        ],
        "common_symbols": [
            {"symbol": s, "count": c} for s, c in symbol_counts.most_common(24)
        ],
        "entropy_boundary": {
            "avg_entropy_bits": avg_entropy,
            "compressed_or_encrypted_pct": encrypted_pct,
            "buckets": entropy_buckets,
        },
    }


def normalize_client_digest(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Safely validate & normalize a compact JSON digest from browser or PC scanner."""
    if not isinstance(raw, dict):
        raise ValueError("유효한 코퍼스 JSON 다이제스트 객체가 아닙니다.")
    name = str(raw.get("corpus_name") or "로컬 코퍼스").strip()[:80]
    total_files = max(0, int(raw.get("total_files", 0)))
    if total_files <= 0:
        raise ValueError("스캔된 파일이 0개입니다. 파일이 들어 있는 폴더나 다이제스트 JSON을 선택해 주세요.")

    cross_raw = raw.get("cross_modal_entities")
    cross_entities: List[Dict[str, Any]] = []
    if isinstance(cross_raw, list):
        for item in cross_raw[:30]:
            if not isinstance(item, dict) or not item.get("entity"):
                continue
            mods = [str(m) for m in (item.get("modalities") or []) if str(m) in MODALITY_LABELS_KO]
            cross_entities.append(
                {
                    "entity": str(item["entity"])[:40],
                    "modalities": mods,
                    "modality_count": len(mods),
                    "file_count": max(1, int(item.get("file_count", len(mods)))),
                    "size_mb": round(max(0.0, float(item.get("size_mb", 0.0))), 2),
                    "examples": [str(x)[:60] for x in (item.get("examples") or [])[:4]],
                }
            )

    couplings_raw = raw.get("modality_couplings")
    couplings: List[Dict[str, Any]] = []
    if isinstance(couplings_raw, list):
        for c in couplings_raw[:15]:
            if isinstance(c, dict) and c.get("pair"):
                couplings.append(
                    {
                        "pair": str(c["pair"])[:60],
                        "shared_entities": max(1, int(c.get("shared_entities", 1))),
                    }
                )

    symbols_raw = raw.get("common_symbols")
    symbols: List[Dict[str, Any]] = []
    if isinstance(symbols_raw, list):
        for s in symbols_raw[:30]:
            if isinstance(s, dict) and s.get("symbol"):
                symbols.append(
                    {
                        "symbol": str(s["symbol"])[:40],
                        "count": max(1, int(s.get("count", 1))),
                    }
                )

    eb = raw.get("entropy_boundary") if isinstance(raw.get("entropy_boundary"), dict) else {}
    return {
        "schema_version": 1,
        "corpus_name": name,
        "engine_fingerprint": str(raw.get("engine_fingerprint") or "Local Multi-Modal Corpus")[:80],
        "total_files": total_files,
        "total_size_gb": round(max(0.0, float(raw.get("total_size_gb", 0.0))), 4),
        "total_size_mb": round(max(0.0, float(raw.get("total_size_mb", 0.0))), 2),
        "probed_headers": max(0, int(raw.get("probed_headers", 0))),
        "modality_counts": {
            str(k): max(0, int(v))
            for k, v in (raw.get("modality_counts") or {}).items()
            if isinstance(raw.get("modality_counts"), dict)
        },
        "modality_size_mb": {
            str(k): round(max(0.0, float(v)), 2)
            for k, v in (raw.get("modality_size_mb") or {}).items()
            if isinstance(raw.get("modality_size_mb"), dict)
        },
        "top_magic_signatures": [
            {"magic": str(m.get("magic", ""))[:40], "count": max(1, int(m.get("count", 1)))}
            for m in (raw.get("top_magic_signatures") or [])[:12]
            if isinstance(m, dict) and m.get("magic")
        ],
        "cross_modal_entities": cross_entities,
        "modality_couplings": couplings,
        "common_symbols": symbols,
        "entropy_boundary": {
            "avg_entropy_bits": round(float(eb.get("avg_entropy_bits", 0.0)), 3),
            "compressed_or_encrypted_pct": round(float(eb.get("compressed_or_encrypted_pct", 0.0)), 1),
            "buckets": eb.get("buckets") if isinstance(eb.get("buckets"), dict) else {},
        },
    }


def render_standalone_scanner_script() -> str:
    """
    Generate a zero-dependency standalone Python 3 script the user can run on
    their Windows/macOS/Linux PC to scan an 85GB game directory (e.g. C:\\...)
    in seconds without loading files into RAM, producing a compact ~30KB JSON
    cross-modal digest ready to load straight into Elysia!
    """
    src_path = Path(__file__).resolve()
    core_code = src_path.read_text(encoding="utf-8")
    # Strip the render_standalone_scanner_script function itself and append clean CLI entrypoint
    marker = "def render_standalone_scanner_script()"
    trimmed = core_code.split(marker)[0].rstrip()
    cli_tail = '''

def main() -> int:
    import argparse
    import time

    parser = argparse.ArgumentParser(
        description="Elysia 85GB+ Local Game/Folder Cross-Modal Invariant Scanner (Zero-Upload, Zero-API)"
    )
    parser.add_argument("target_dir", help='Target folder path (e.g. "C:\\\\Games\\\\AzurPromilia")')
    parser.add_argument("-o", "--output", default="elysia_corpus_digest.json", help="Output compact JSON digest path")
    parser.add_argument("--name", default="", help="Optional display name for this corpus")
    parser.add_argument("--max-probes", type=int, default=800, help="Max binary header slices (4KB each) to probe")
    args = parser.parse_args()

    t0 = time.time()
    target = Path(args.target_dir)
    print(f"[Elysia Scanner] Streaming directory topology & 4KB header slices: {target}")
    digest = analyze_local_directory(
        target,
        corpus_name=args.name or target.name,
        max_files=250000,
        max_header_probes=args.max_probes,
        header_bytes_len=4096,
    )
    out_path = Path(args.output).resolve()
    out_path.write_text(json.dumps(digest, ensure_ascii=False, indent=2), encoding="utf-8")
    dt = time.time() - t0
    print(
        f"[Done in {dt:.2f}s] Files={digest['total_files']:,} ({digest['total_size_gb']:.2f} GB) | "
        f"Engine={digest['engine_fingerprint']} | "
        f"Cross-Modal Entities={len(digest['cross_modal_entities'])} | "
        f"Encrypted/Compressed={digest['entropy_boundary']['compressed_or_encrypted_pct']}%"
    )
    print(f"[Saved] {out_path} ({out_path.stat().st_size / 1024:.1f} KB) -> Load this JSON in Elysia!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
    return trimmed + "\n" + cli_tail
