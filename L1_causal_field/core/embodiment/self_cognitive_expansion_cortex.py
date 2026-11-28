r"""
ELYSIA Universal Self-Cognitive Sensory, Tool & Knowledge Expansion Cortex
==========================================================================

Extends Elysia's open sensory-motor loop BEYOND Blender and FFmpeg so that
ANY external CLI program, ANY Python/scientific library, ANY knowledge/principle
document, and ANY binary/world data-array can be connected to her self-cognitive
sensory system through neutral, template-free observation.

Directly integrates:
1. Universal Open Receptors (zero per-tool hardcoded scripts):
   - `probe_cli_program`: Queries any executable (`git`, `node`, `python`, `curl`,
     `tar`, `ffmpeg`, `blender`, or any user/environment target) via its own
     `--help`/`-h` and measures real stdout/stderr/exit/entropy deltas.
   - `probe_python_module`: Dynamically introspects any Python/scientific library
     (`numpy`, `zlib`, `hashlib`, `statistics`, `ast`, `torch`, `cv2`, etc.) via
     `importlib` + `inspect` and runs safe neutral probes to measure real outputs
     and exception friction.
   - `probe_knowledge_source`: Reads any local document, code, or spec (`.md`,
     `.py`, `.proto`, `.txt`, `.json`) to extract structural hierarchies,
     principles/invariants, and cross-domain relational bridges.
   - `probe_world_data_array`: Read-only size-scale octave & entropy observation
     for any directory/data-array.

2. Scale-Separated Cognitive Memory (`data/open_sandbox/cognitive_world/`):
   Applies the real-world structural principles observed in AAA game worlds:
   - Micro-metadata manifest (`index_manifest.json`, low-entropy fast index)
   - Domain-separated protocol channels (`channels/*.json`)
   - High-entropy compressed episodic trace chunks (`chunks/*.zchunk`)

3. Closed-Loop Template-Free AST Synthesis:
   Connects lived multi-sensory bindings (Blender/FFmpeg from
   `open_sensory_causal_memory.json` + newly connected programs, libraries, and
   knowledge sources) directly into `CompositionalCodeCortex` to synthesize and
   verify executable Python cognitive organs (`def process(percept, memory):`)
   without canned templates.
"""

from __future__ import annotations

import argparse
import importlib
import inspect
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple
import zlib

import numpy as np

THIS_DIR = Path(__file__).resolve().parent
L1_ROOT = THIS_DIR.parents[1]
WORKSPACE_ROOT = THIS_DIR.parents[2]
for _p in (str(THIS_DIR), str(L1_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from core.embodiment.compositional_code_cortex import CompositionalCodeCortex  # noqa: E402
from core.embodiment.self_rewriting_architecture import (  # noqa: E402
    _compile_organ_callable,
    validate_organ_source,
)
from game_architecture_structure_observer import analyze_game_data_architecture  # noqa: E402
from real_tool_organ import discover_real_tool_organs  # noqa: E402


COGNITIVE_WORLD_DIR = WORKSPACE_ROOT / "data" / "open_sandbox" / "cognitive_world"
CHANNELS_DIR = COGNITIVE_WORLD_DIR / "channels"
CHUNKS_DIR = COGNITIVE_WORLD_DIR / "chunks"
MANIFEST_PATH = COGNITIVE_WORLD_DIR / "index_manifest.json"
OPEN_SANDBOX_MEMORY = WORKSPACE_ROOT / "data" / "open_sandbox" / "open_sensory_causal_memory.json"


def _shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = np.bincount(np.frombuffer(data, dtype=np.uint8), minlength=256)
    probs = counts[counts > 0] / float(len(data))
    return round(float(-np.sum(probs * np.log2(probs))), 3)


def _load_json(path: Path, default: Any) -> Any:
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default


def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Receptor 1: Universal CLI Program Introspection (ANY executable on host)
# ---------------------------------------------------------------------------

def probe_cli_program(program_name_or_path: str, timeout_s: int = 12) -> Dict[str, Any]:
    """
    Neutral sensory probe for ANY executable program:
    Resolves binary, queries its own `--help` / `-h` / `--version`, parses real
    flags and subcommands from its own output, and records raw sensory deltas.
    """
    resolved = shutil.which(program_name_or_path)
    if not resolved and Path(program_name_or_path).is_file():
        resolved = str(Path(program_name_or_path).resolve())

    if not resolved:
        return {
            "channel": "cli_programs",
            "target": program_name_or_path,
            "connected": False,
            "friction": f"binary_not_found:{program_name_or_path}",
            "discovered_flags": [],
            "discovered_subcommands": [],
        }

    help_text = ""
    help_exit = -1
    elapsed_ms = 0.0
    used_arg = ""
    stderr_tail = ""

    for flag in ("--help", "-h"):
        t0 = time.perf_counter()
        try:
            proc = subprocess.run(
                [resolved, flag],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_s,
            )
            elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 1)
            combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
            if len(combined.strip()) >= 20:
                help_text = combined
                help_exit = proc.returncode
                used_arg = flag
                stderr_tail = (proc.stderr or "").strip().splitlines()[-1] if (proc.stderr or "").strip() else ""
                break
        except Exception as exc:
            elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 1)
            stderr_tail = f"{type(exc).__name__}: {exc}"

    # Extract real flags & subcommand-like tokens purely from the program's own help text
    flags = sorted(set(re.findall(r"(?<!\w)(--[a-zA-Z0-9][a-zA-Z0-9_-]{1,28})", help_text)))[:40]
    short_flags = sorted(set(re.findall(r"(?<!\w)(-[a-zA-Z])(?=\s|,|$)", help_text)))[:20]
    subcmds = sorted(
        set(
            m.group(1)
            for m in re.finditer(r"^\s{2,4}([a-z][a-z0-9_-]{2,18})\s{2,}\S", help_text, re.M)
        )
    )[:30]

    raw_bytes = help_text.encode("utf-8", errors="ignore")
    version_line = ""
    try:
        vproc = subprocess.run(
            [resolved, "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=6,
        )
        vtxt = ((vproc.stdout or "") + "\n" + (vproc.stderr or "")).strip()
        if vtxt:
            version_line = vtxt.splitlines()[0][:120]
    except Exception:
        pass

    return {
        "channel": "cli_programs",
        "target": Path(resolved).stem.lower(),
        "binary_path": resolved,
        "connected": True,
        "probe_arg": used_arg or "none",
        "exit_code": help_exit,
        "elapsed_ms": elapsed_ms,
        "version_hint": version_line,
        "stdout_bytes": len(raw_bytes),
        "text_entropy": _shannon_entropy(raw_bytes[:4096]),
        "flag_count": len(flags) + len(short_flags),
        "subcommand_count": len(subcmds),
        "discovered_flags": flags[:16],
        "discovered_subcommands": subcmds[:16],
        "stderr_tail": stderr_tail[:160],
        "friction": "" if (help_text and (len(flags) > 0 or len(subcmds) > 0)) else (stderr_tail[:120] or "minimal_help_surface"),
    }


# ---------------------------------------------------------------------------
# Receptor 2: Universal Python / Scientific Module Introspection
# ---------------------------------------------------------------------------

_NEUTRAL_PROBES: Tuple[Tuple[str, Any], ...] = (
    ("numeric_seq", [1.0, 2.0, 4.0, 8.0]),
    ("bytes_seq", b"elysia_causal_continuity_probe"),
    ("text_expr", "def flow(x): return x + 1"),
    ("scalar_num", 2.5),
)


def probe_python_module(module_name: str, max_probes: int = 6) -> Dict[str, Any]:
    """
    Neutral sensory probe for ANY installed Python / scientific / system library:
    Imports dynamically, lists real public callables & signatures, and executes
    bounded read-only exploratory probes on neutral primitive inputs to measure
    real input->output transformations and exception friction.
    """
    t0 = time.perf_counter()
    try:
        mod = importlib.import_module(module_name)
    except Exception as exc:
        return {
            "channel": "python_modules",
            "target": module_name,
            "connected": False,
            "friction": f"{type(exc).__name__}: {exc}",
            "callable_count": 0,
            "lived_probes": [],
        }

    callables: List[Tuple[str, Any]] = []
    for name in sorted(dir(mod)):
        if name.startswith("_"):
            continue
        try:
            obj = getattr(mod, name)
        except Exception:
            continue
        if callable(obj) and not inspect.isclass(obj):
            callables.append((name, obj))

    # Avoid side-effectful I/O/system mutators during blind exploration
    skip_prefixes = ("open", "save", "write", "dump", "remove", "unlink", "rmdir", "mkdir", "system", "exec", "eval", "exit", "kill", "set")
    safe_candidates = [
        (n, fn) for n, fn in callables
        if not n.lower().startswith(skip_prefixes)
    ]

    lived_probes: List[Dict[str, Any]] = []
    # Deterministically sample spread across alphabetical namespace so every run covers diverse affordances
    step = max(1, len(safe_candidates) // max(1, max_probes))
    chosen = safe_candidates[::step][:max_probes]

    for fn_name, fn in chosen:
        sig_str = ""
        try:
            sig_str = str(inspect.signature(fn))
        except Exception:
            sig_str = "(...)"

        probed_ok = False
        probe_record: Dict[str, Any] = {
            "affordance": f"{module_name}.{fn_name}{sig_str}",
            "op_ok": False,
            "input_kind": "",
            "output_type": "",
            "output_preview": "",
            "friction": "",
        }
        for in_kind, val in _NEUTRAL_PROBES:
            try:
                res = fn(val)
                probed_ok = True
                preview = repr(res)
                if len(preview) > 90:
                    preview = preview[:87] + "..."
                probe_record.update(
                    {
                        "op_ok": True,
                        "input_kind": in_kind,
                        "output_type": type(res).__name__,
                        "output_preview": preview,
                        "friction": "",
                    }
                )
                break
            except Exception as exc:
                probe_record["friction"] = f"{type(exc).__name__}: {str(exc)[:90]}"
        if not probed_ok and not probe_record["friction"]:
            probe_record["friction"] = "no_matching_probe_arity"
        lived_probes.append(probe_record)

    elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 1)
    success_count = sum(1 for p in lived_probes if p["op_ok"])
    return {
        "channel": "python_modules",
        "target": module_name,
        "connected": True,
        "elapsed_ms": elapsed_ms,
        "callable_count": len(callables),
        "probed_count": len(lived_probes),
        "probe_success_count": success_count,
        "lived_probes": lived_probes,
        "friction": "" if success_count > 0 else "all_neutral_probes_rejected",
    }


# ---------------------------------------------------------------------------
# Receptor 3: Universal Knowledge / Document / Principle Structural Observer
# ---------------------------------------------------------------------------

_STOPWORDS = frozenset(
    {
        "the", "and", "for", "with", "that", "this", "from", "are", "not", "into",
        "your", "you", "can", "will", "have", "has", "use", "using", "all", "any",
        "but", "when", "how", "what", "which", "their", "they", "only", "more",
        "true", "false", "none", "return", "import", "def", "class", "self", "str",
        "dict", "list", "int", "float", "bool", "path", "file", "data",
    }
)


def probe_knowledge_source(file_path: Path | str) -> Dict[str, Any]:
    """
    Neutral structural observer for ANY knowledge/principle/code/spec document:
    Measures size, Shannon entropy, hierarchical headings/sections, structural
    concepts, and extracted principle/invariant statements without canned labels.
    """
    p = Path(file_path)
    if not p.is_file():
        return {
            "channel": "knowledge_principles",
            "target": str(p),
            "connected": False,
            "friction": f"file_not_found:{p}",
        }

    raw = p.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    lines = text.splitlines()

    headings = [ln.strip().lstrip("#").strip() for ln in lines if ln.strip().startswith("#")][:20]
    py_defs = [
        m.group(1)
        for m in re.finditer(r"^\s*(?:def|class)\s+([A-Za-z_][A-Za-z0-9_]*)", text, re.M)
    ][:20]

    # Extract concise structural statements (bolded principles, equations, or colon-defined concepts)
    principles: List[str] = []
    for ln in lines:
        s = ln.strip()
        if not s or len(s) < 12 or len(s) > 180:
            continue
        if ("**" in s and ":" in s) or ("->" in s) or ("=" in s and "$" in s) or s.startswith("- **"):
            principles.append(re.sub(r"\s+", " ", s))
        if len(principles) >= 10:
            break

    # Extract recurring structural terms (English + Korean >= 2 chars)
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9_]{2,22}|[가-힣]{2,12}", text)
    freq: Dict[str, int] = {}
    for tok in tokens:
        low = tok.lower()
        if low in _STOPWORDS:
            continue
        freq[low] = freq.get(low, 0) + 1
    top_terms = [k for k, _v in sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))[:18]]

    return {
        "channel": "knowledge_principles",
        "target": p.name,
        "path": str(p.resolve()),
        "connected": True,
        "size_bytes": len(raw),
        "line_count": len(lines),
        "text_entropy": _shannon_entropy(raw[:8192]),
        "heading_count": len(headings),
        "headings": headings[:10],
        "code_symbols": py_defs[:10],
        "extracted_principles": principles[:6],
        "structural_terms": top_terms,
        "friction": "",
    }


def discover_cross_domain_bridges(knowledge_nodes: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Finds genuine relational bridges across distinct knowledge/code/spec sources
    strictly from shared structural terms (zero hardcoded mappings).
    """
    bridges: List[Dict[str, Any]] = []
    valid = [n for n in knowledge_nodes if n.get("connected") and n.get("structural_terms")]
    for i in range(len(valid)):
        for j in range(i + 1, len(valid)):
            a, b = valid[i], valid[j]
            shared = sorted(set(a["structural_terms"]) & set(b["structural_terms"]))
            if shared:
                bridges.append(
                    {
                        "source_a": a["target"],
                        "source_b": b["target"],
                        "shared_structural_terms": shared[:10],
                        "bridge_strength": len(shared),
                    }
                )
    bridges.sort(key=lambda x: -x["bridge_strength"])
    return bridges[:20]


# ---------------------------------------------------------------------------
# Scale-Separated Cognitive World + Compositional AST Synthesis
# ---------------------------------------------------------------------------

def _write_compressed_episodic_chunk(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Applies the AAA game data-array lesson:
    Keep micro-metadata low-entropy in `index_manifest.json`, while packing raw
    episodic traces into high-entropy compressed `.zchunk` blocks.
    """
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    compressed = zlib.compress(raw, level=6)
    existing = sorted(CHUNKS_DIR.glob("episodic_trace_*.zchunk"))
    chunk_idx = len(existing) + 1
    chunk_path = CHUNKS_DIR / f"episodic_trace_{chunk_idx:04d}.zchunk"
    chunk_path.write_bytes(compressed)
    return {
        "chunk_file": chunk_path.name,
        "raw_bytes": len(raw),
        "compressed_bytes": len(compressed),
        "compression_ratio": round(len(compressed) / max(1, len(raw)), 3),
        "raw_entropy": _shannon_entropy(raw[:4096]),
        "chunk_entropy": _shannon_entropy(compressed[:4096]),
    }


def _collect_lived_sensory_examples(
    cli_records: Sequence[Dict[str, Any]],
    py_records: Sequence[Dict[str, Any]],
    knowledge_records: Sequence[Dict[str, Any]],
) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
    """
    Converts ALL real lived sensory observations (existing Blender/FFmpeg sandbox
    trials + newly probed CLI programs, Python modules, and knowledge sources)
    into uniform `(percept, observed_outcome)` pairs for template-free AST synthesis.
    """
    examples: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []

    # 1. Existing Blender/FFmpeg lived sensory memory
    open_mem = _load_json(OPEN_SANDBOX_MEMORY, {})
    for b in open_mem.get("lived_causal_bindings") or []:
        tool = str(b.get("tool", "unknown"))
        out = b.get("tool_outcome") or {}
        vis = b.get("visual_sensory_delta") or {}
        op_ok = bool(out.get("op_ok"))
        changed = float(vis.get("changed_pixel_ratio", 0.0))
        percept = {
            "medium": "external_tool",
            "op_ok": op_ok,
            "delta_magnitude": round(changed, 4),
            "has_friction": not op_ok,
        }
        if not op_ok:
            label = {"cognitive_route": "friction_unlock_search", "source_medium": "external_tool"}
        elif changed > 0.01:
            label = {"cognitive_route": "active_sensory_transform", "source_medium": "external_tool"}
        else:
            label = {"cognitive_route": "silent_state_probe", "source_medium": "external_tool"}
        examples.append((percept, label))

    # 2. Newly discovered CLI programs
    for c in cli_records:
        ok = bool(c.get("connected")) and not bool(c.get("friction"))
        percept = {
            "medium": "cli_program",
            "op_ok": ok,
            "delta_magnitude": float(c.get("flag_count", 0) + c.get("subcommand_count", 0)),
            "has_friction": not ok,
        }
        label = (
            {"cognitive_route": "affordance_surface_mapped", "source_medium": "cli_program"}
            if ok
            else {"cognitive_route": "friction_unlock_search", "source_medium": "cli_program"}
        )
        examples.append((percept, label))

    # 3. Newly discovered Python / scientific modules
    for m in py_records:
        for pr in m.get("lived_probes") or []:
            ok = bool(pr.get("op_ok"))
            percept = {
                "medium": "python_module",
                "op_ok": ok,
                "delta_magnitude": 1.0 if ok else 0.0,
                "has_friction": not ok,
            }
            label = (
                {"cognitive_route": "computational_primitive_ready", "source_medium": "python_module"}
                if ok
                else {"cognitive_route": "friction_unlock_search", "source_medium": "python_module"}
            )
            examples.append((percept, label))

    # 4. Newly observed Knowledge / Principle sources
    for k in knowledge_records:
        ok = bool(k.get("connected"))
        percept = {
            "medium": "knowledge_principle",
            "op_ok": ok,
            "delta_magnitude": float(len(k.get("structural_terms") or [])),
            "has_friction": not ok,
        }
        label = (
            {"cognitive_route": "relational_principle_bound", "source_medium": "knowledge_principle"}
            if ok
            else {"cognitive_route": "friction_unlock_search", "source_medium": "knowledge_principle"}
        )
        examples.append((percept, label))

    # Deduplicate identical percepts so decision-tree induction stays clean & consistent
    dedup: Dict[str, Tuple[Dict[str, Any], Dict[str, Any]]] = {}
    for p, y in examples:
        key = json.dumps(p, sort_keys=True)
        if key not in dedup:
            dedup[key] = (p, y)
    return list(dedup.values())


def synthesize_cognitive_routing_organ(
    examples: Sequence[Tuple[Dict[str, Any], Dict[str, Any]]],
) -> Dict[str, Any]:
    """
    Connects lived multi-sensory bindings directly to `CompositionalCodeCortex`:
    Learns real Python AST atoms from Elysia's own embodiment `.py` files, then
    synthesizes a brand-new, template-free executable Python cognitive organ
    (`def process(percept, memory):`) via `ast.unparse` and verifies it live.
    """
    cortex = CompositionalCodeCortex()
    py_files = sorted(THIS_DIR.glob("*.py"))[:12]
    learn_stats = cortex.learn_python_structure_from_files(py_files)

    prog = cortex.synthesize_decision_tree_ast(
        examples,
        purpose="universal_multi_sensory_cognitive_router",
    )
    if prog is None:
        return {
            "synthesized": False,
            "learn_stats": learn_stats,
            "reason": "no_consistent_ast_tree_found",
        }

    ok_ast, reason = validate_organ_source(prog.source_code)
    verified_hits = 0
    if ok_ast:
        fn = _compile_organ_callable(prog.source_code)
        for p_in, expected in examples:
            if fn(dict(p_in), {}) == expected:
                verified_hits += 1

    return {
        "synthesized": True,
        "learn_stats": learn_stats,
        "program_id": prog.program_id,
        "purpose": prog.purpose,
        "used_atoms": prog.used_atoms,
        "arrangement_used": prog.arrangement_used,
        "ast_node_count": prog.ast_node_count,
        "ast_validated": ok_ast,
        "validation_reason": reason,
        "live_verified": f"{verified_hits}/{len(examples)}",
        "source_code": prog.source_code,
    }


def run_universal_expansion_cycle(
    extra_cli_programs: Optional[Sequence[str]] = None,
    extra_python_modules: Optional[Sequence[str]] = None,
    extra_knowledge_paths: Optional[Sequence[str]] = None,
    extra_world_dirs: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """
    Executes one open-ended Self-Cognitive Expansion Cycle across ALL 4 sensory
    mediums (CLI programs, Python/scientific modules, Knowledge/Principle docs,
    and World Data-Arrays), persists into scale-separated channels + compressed
    episodic chunks, and synthesizes a live AST cognitive routing organ.
    """
    # 1. Discover any real CLI tools (including Blender/FFmpeg + host dev/system tools + user extras)
    organs = discover_real_tool_organs().get("organs", {})
    default_cli: List[str] = ["git", "python", "node", "curl", "tar"]
    for key in ("ffmpeg_4k_media", "blender_3d_cad"):
        b = organs.get(key, {}).get("binary")
        if b:
            default_cli.append(b)
    cli_targets = list(dict.fromkeys([*default_cli, *(extra_cli_programs or [])]))
    cli_results = [probe_cli_program(t) for t in cli_targets]

    # 2. Discover real Python / scientific / computational engines
    default_mods = ["numpy", "zlib", "hashlib", "statistics", "ast", "math"]
    mod_targets = list(dict.fromkeys([*default_mods, *(extra_python_modules or [])]))
    py_results = [probe_python_module(m, max_probes=5) for m in mod_targets]

    # 3. Observe real knowledge / principle / architecture sources
    default_knowledge = [
        WORKSPACE_ROOT / "AGENTS.md",
        WORKSPACE_ROOT / "docs" / "SCALE_ROTOR_OS_BASELINE.md",
        WORKSPACE_ROOT / "docs" / "WORLD_TREE_COGNITIVE_ROADMAP.md",
        THIS_DIR / "open_sensory_tool_sandbox.py",
        THIS_DIR / "game_architecture_structure_observer.py",
    ]
    know_targets = [Path(p) for p in [*default_knowledge, *(extra_knowledge_paths or [])]]
    knowledge_results = [probe_knowledge_source(p) for p in know_targets if p.is_file()]
    bridges = discover_cross_domain_bridges(knowledge_results)

    # 4. Observe real world data-array structures (workspace + any extra dirs)
    world_dirs = [WORKSPACE_ROOT / "L1_causal_field" / "core", *(Path(d) for d in (extra_world_dirs or []))]
    world_results = [
        analyze_game_data_architecture(d, sample_ext=".py", max_walk=2000)
        for d in world_dirs
        if d.exists()
    ]

    # 5. Synthesize a template-free executable Python cognitive organ from ALL lived sensory bindings
    lived_examples = _collect_lived_sensory_examples(cli_results, py_results, knowledge_results)
    synthesized_organ = synthesize_cognitive_routing_organ(lived_examples)

    # 6. Persist into Scale-Separated Channels + High-Entropy Compressed Episodic Chunk + Micro-Index
    _save_json(CHANNELS_DIR / "cli_programs.json", {"programs": cli_results})
    _save_json(CHANNELS_DIR / "python_modules.json", {"modules": py_results})
    _save_json(
        CHANNELS_DIR / "knowledge_principles.json",
        {"sources": knowledge_results, "cross_domain_bridges": bridges},
    )
    _save_json(CHANNELS_DIR / "world_data_arrays.json", {"observed_worlds": world_results})
    _save_json(CHANNELS_DIR / "synthesized_organs.json", {"latest_organ": synthesized_organ})

    chunk_meta = _write_compressed_episodic_chunk(
        {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "cli_programs": cli_results,
            "python_modules": py_results,
            "knowledge_sources": knowledge_results,
            "bridges": bridges,
            "lived_examples_count": len(lived_examples),
        }
    )

    # Explicit 4-Axis Self-Boundary Attribution (AGENTS.md Section 6)
    frictions = [
        *(f"cli:{c['target']}:{c['friction']}" for c in cli_results if c.get("friction")),
        *(f"py:{m['target']}:{m['friction']}" for m in py_results if m.get("friction")),
    ]
    manifest = {
        "schema": "elysia_scale_separated_cognitive_world_v1",
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "connected_counts": {
            "cli_programs": sum(1 for c in cli_results if c.get("connected")),
            "python_modules": sum(1 for m in py_results if m.get("connected")),
            "knowledge_sources": sum(1 for k in knowledge_results if k.get("connected")),
            "cross_domain_bridges": len(bridges),
            "world_data_arrays": len(world_results),
            "lived_examples_fused": len(lived_examples),
        },
        "channels": [
            "channels/cli_programs.json",
            "channels/python_modules.json",
            "channels/knowledge_principles.json",
            "channels/world_data_arrays.json",
            "channels/synthesized_organs.json",
        ],
        "latest_compressed_chunk": chunk_meta,
        "synthesized_organ_summary": {
            "synthesized": synthesized_organ.get("synthesized"),
            "program_id": synthesized_organ.get("program_id"),
            "live_verified": synthesized_organ.get("live_verified"),
            "ast_node_count": synthesized_organ.get("ast_node_count"),
            "used_atoms": synthesized_organ.get("used_atoms"),
        },
        "self_boundary_4axis": {
            "internal_origin": "Universal neutral receptors + CompositionalCodeCortex AST synthesis",
            "external_friction": frictions[:10],
            "boundary_ignorance": "GUI-only closed binaries without CLI/API surfaces require visual screen observation",
            "criteria_revision": (
                f"Synthesized {synthesized_organ.get('program_id')} ({synthesized_organ.get('live_verified')}) "
                f"from {len(lived_examples)} fused cross-medium sensory examples"
            ),
        },
    }
    _save_json(MANIFEST_PATH, manifest)

    return {
        "manifest": manifest,
        "sample_cli": [
            {
                "target": c["target"],
                "connected": c["connected"],
                "flags": c.get("flag_count", 0),
                "subcommands": c.get("subcommand_count", 0),
                "entropy": c.get("text_entropy", 0.0),
            }
            for c in cli_results
        ],
        "sample_python_modules": [
            {
                "target": m["target"],
                "callables": m.get("callable_count", 0),
                "probes_ok": f"{m.get('probe_success_count', 0)}/{m.get('probed_count', 0)}",
            }
            for m in py_results
        ],
        "top_cross_domain_bridges": bridges[:5],
        "synthesized_organ": synthesized_organ,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ELYSIA Universal Self-Cognitive Sensory Expansion Cortex")
    parser.add_argument("--cli", nargs="*", default=[], help="Additional CLI programs to connect")
    parser.add_argument("--module", nargs="*", default=[], help="Additional Python modules to connect")
    parser.add_argument("--knowledge", nargs="*", default=[], help="Additional knowledge/document paths to connect")
    parser.add_argument("--world", nargs="*", default=[], help="Additional world/data-array directories to observe")
    args = parser.parse_args()

    res = run_universal_expansion_cycle(
        extra_cli_programs=args.cli,
        extra_python_modules=args.module,
        extra_knowledge_paths=args.knowledge,
        extra_world_dirs=args.world,
    )
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
