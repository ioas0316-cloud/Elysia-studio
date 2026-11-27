r"""
ELYSIA #2 — Self-Rotating Code Rotor (Zero if/else · 64-Bit Bitwise Execution Graph)
====================================================================================

Dissolves static sequential `if ext == '.py': ... elif ext == '.json': ...` code:
- Every executable capability (Python AST Compiler, JSON Structural Parser, CUDA Image
  Object Carver, Raw Byte Entropy Analyzer) is a 64-bit `4x4x4` Code-Rotor Word:
    - Core (8 bits):  Input Medium / Physical Structural Invariant
    - Shell (56 bits): Capability & Output Transformation Spectrum
- Given ANY real file on this PC (with ZERO filename/extension `if/else` rules!):
    1. Reads raw bytes and projects physical byte-structure directly into a 64-bit Input Word.
    2. Meta-Rotor ranks Code-Rotors purely via `AND / XOR / POPCNT` bitwise resonance.
    3. Executes the highest-resonance Code-Rotor.
    4. If REAL execution fails (e.g. `SyntaxError` or `JSONDecodeError`), the Meta-Rotor
       **rotates the execution graph itself** (XOR-masking the repelled port) and automatically
       re-couples to the next resonant rotor until reality accepts the transformation!
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
import json
import math
from pathlib import Path
import sys
from typing import Any, Callable, Dict, List

import cv2  # type: ignore
import numpy as np

THIS_DIR = Path(__file__).resolve().parent
EMBODIMENT_DIR = THIS_DIR.parents[1] / "L1_causal_field" / "core" / "embodiment"
for p in (str(THIS_DIR), str(EMBODIMENT_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from cuda_visual_object_rotor import CudaVisualObjectRotor  # noqa: E402


# Bit positions encoding raw physical byte-structure (NO filename/extension cheating!)
BIT_TEXT_PRINTABLE   = 1 << 0
BIT_BRACE_STRUCTURED = 1 << 1
BIT_CODE_KEYWORDS    = 1 << 2
BIT_BINARY_MAGIC_IMG = 1 << 3
BIT_HIGH_ENTROPY     = 1 << 4
BIT_NEWLINE_DENSE    = 1 << 5
BIT_COLON_KEYVAL     = 1 << 6
BIT_DEF_CLASS_IMPORT = 1 << 7


def sense_raw_bytes_to_word64(raw: bytes) -> int:
    """Projects raw physical bytes (NOT file extension!) into a 64-bit structural word."""
    sample = raw[:4096]
    if not sample:
        return 0
    word = 0

    # Check binary image magic headers (JPEG / PNG / BMP) purely from raw bytes
    if sample.startswith((b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"BM")):
        word |= BIT_BINARY_MAGIC_IMG

    # Shannon byte entropy
    counts = np.bincount(np.frombuffer(sample, dtype=np.uint8), minlength=256)
    probs = counts[counts > 0] / float(len(sample))
    entropy = float(-np.sum(probs * np.log2(probs)))
    if entropy > 6.8:
        word |= BIT_HIGH_ENTROPY

    # Printable UTF-8 ratio
    try:
        txt = sample.decode("utf-8")
        printable = sum(1 for c in txt if c.isprintable() or c in "\r\n\t")
        if printable / max(1, len(txt)) > 0.92:
            word |= BIT_TEXT_PRINTABLE
        stripped = txt.lstrip()
        if stripped.startswith(("{", "[")) and ":" in txt:
            word |= BIT_BRACE_STRUCTURED | BIT_COLON_KEYVAL
        if txt.count("\n") >= 4:
            word |= BIT_NEWLINE_DENSE
        if any(kw in txt for kw in ("def ", "class ", "import ", "function ", "const ")):
            word |= BIT_CODE_KEYWORDS
        if any(kw in txt for kw in ("def ", "class ", "from ")):
            word |= BIT_DEF_CLASS_IMPORT
    except UnicodeDecodeError:
        pass

    return word


@dataclass
class CodeRotor:
    rotor_id: str
    word64: int
    enact: Callable[[bytes, Path], Dict[str, Any]]


def _enact_python_ast(raw: bytes, path: Path) -> Dict[str, Any]:
    txt = raw.decode("utf-8")
    tree = ast.parse(txt, filename=str(path))
    funcs = sum(1 for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))
    classes = sum(1 for n in ast.walk(tree) if isinstance(n, ast.ClassDef))
    return {"ok": True, "rotor": "python_ast", "summary": f"Python AST 수용 (함수 {funcs}개, 클래스 {classes}개)"}


def _enact_json_parse(raw: bytes, _path: Path) -> Dict[str, Any]:
    obj = json.loads(raw.decode("utf-8"))
    keys = list(obj.keys())[:5] if isinstance(obj, dict) else [f"list[{len(obj)}]"]
    return {"ok": True, "rotor": "json_structure", "summary": f"JSON 구조 수용 (최상위 키: {keys})"}


_SHARED_VIS_ROTOR = CudaVisualObjectRotor()


def _enact_cuda_visual(raw: bytes, _path: Path) -> Dict[str, Any]:
    arr = np.frombuffer(raw, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Not a decodable image buffer")
    res = _SHARED_VIS_ROTOR.process_frame(img, max_objects=5)
    return {
        "ok": True,
        "rotor": "cuda_visual_carver",
        "summary": f"GTX 1060 CUDA 이미지 절단 ({res['resolution'][0]}x{res['resolution'][1]}, 객체 {res['carved_object_count']}개, {res['elapsed_ms']}ms)",
    }


def _enact_js_text_topology(raw: bytes, _path: Path) -> Dict[str, Any]:
    txt = raw.decode("utf-8")
    lines = txt.splitlines()
    fn_cnt = sum(1 for ln in lines if "function " in ln or "=>" in ln)
    return {"ok": True, "rotor": "code_text_topology", "summary": f"일반 코드/텍스트 위상 수용 ({len(lines)}행, 함수/화살표 패턴 {fn_cnt}개)"}


CODE_ROTORS: List[CodeRotor] = [
    CodeRotor(
        "rotor::python_ast",
        BIT_TEXT_PRINTABLE | BIT_CODE_KEYWORDS | BIT_DEF_CLASS_IMPORT | BIT_NEWLINE_DENSE,
        _enact_python_ast,
    ),
    CodeRotor(
        "rotor::json_structure",
        BIT_TEXT_PRINTABLE | BIT_BRACE_STRUCTURED | BIT_COLON_KEYVAL,
        _enact_json_parse,
    ),
    CodeRotor(
        "rotor::cuda_visual_carver",
        BIT_BINARY_MAGIC_IMG | BIT_HIGH_ENTROPY,
        _enact_cuda_visual,
    ),
    CodeRotor(
        "rotor::code_text_topology",
        BIT_TEXT_PRINTABLE | BIT_CODE_KEYWORDS | BIT_NEWLINE_DENSE,
        _enact_js_text_topology,
    ),
]


def execute_self_rotating_graph(target_path: Path) -> Dict[str, Any]:
    """
    Executes a self-rotating code graph on a real file WITHOUT inspecting its filename/extension
    and WITHOUT any `if/else` routing tree — pure 64-bit bitwise resonance + friction rotation!
    """
    raw = target_path.read_bytes()
    in_word = sense_raw_bytes_to_word64(raw)

    # Rank rotors purely by bitwise resonance (AND popcnt) minus dissonance (XOR popcnt)
    ranked = sorted(
        CODE_ROTORS,
        key=lambda r: ((in_word & r.word64).bit_count() * 3) - (in_word ^ r.word64).bit_count(),
        reverse=True,
    )

    rotations: List[Dict[str, Any]] = []
    for attempt, rotor in enumerate(ranked):
        res_bits = (in_word & rotor.word64).bit_count()
        dis_bits = (in_word ^ rotor.word64).bit_count()
        try:
            out = rotor.enact(raw, target_path)
            rotations.append(
                {
                    "attempt": attempt + 1,
                    "rotor_id": rotor.rotor_id,
                    "and_resonance": res_bits,
                    "xor_dissonance": dis_bits,
                    "accepted": True,
                    "summary": out["summary"],
                }
            )
            return {
                "target": target_path.name,
                "input_word64_hex": f"0x{in_word:016x}",
                "rotations_needed": attempt + 1,
                "final_rotor": rotor.rotor_id,
                "summary": out["summary"],
                "trace": rotations,
            }
        except Exception as exc:
            # Real external friction -> Meta-Rotor rotates to the next resonant code rotor!
            rotations.append(
                {
                    "attempt": attempt + 1,
                    "rotor_id": rotor.rotor_id,
                    "and_resonance": res_bits,
                    "xor_dissonance": dis_bits,
                    "accepted": False,
                    "friction": f"{type(exc).__name__}: {str(exc)[:60]}",
                }
            )

    return {"target": target_path.name, "input_word64_hex": f"0x{in_word:016x}", "accepted": False, "trace": rotations}


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    real_targets = [
        root / "L1_causal_field" / "core" / "embodiment" / "driver_protocol_rotor.py",
        root / "L1_causal_field" / "core" / "embodiment" / "ecology_octave_ledger.json",
        root / "src" / "assets" / "images" / "elysia_smile_idle_1795779034636.jpg",
        root / "server.js",
    ]
    results = [execute_self_rotating_graph(p) for p in real_targets if p.exists()]
    print(json.dumps({"status": "ok", "targets_tested": len(results), "results": results}, ensure_ascii=False, indent=2))
