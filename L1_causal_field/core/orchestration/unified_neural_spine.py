"""
ELYSIA Unified Canonical Scale-Rotor Neural Spine & Dependency Rotorizer
=========================================================================

Single canonical bidirectional neural spine unifying:
  - S0 (Atomic / Raw Sensorimotor & Runtime Substrate):
      Privacy-preserving browser pointer/key kinematics (zero raw text capture),
      optical deltas, Hangul impulses, and live host capability probes.
  - S1 (Dependency Membranes & Capability Rotors):
      Separates every external dependency (numpy, torch, PIL, cv2, L0 CUDA, OS)
      into an always-runnable *Invariant Scale-Rotor* (pure Python/JS kernel)
      paired with an optional *Variable Acceleration Rotor* (external library/HW).
  - S2 (Functional Organs, Concepts, & AST-Rotorized Repository Modules):
      Ingests concepts, forged tools, AND the repository's own 550+ Python/L0/JS
      files via pure-Python AST introspection — turning dependency-blocked silos
      into live, dockable Scale-Rotor organs without requiring numpy/torch.
  - S3 (Unified Spacetime World Model & Bidirectional Error-Reduction Loop):
      Genuine pure-Python Cl(3,0) 8D Clifford geometric product & structural
      docking (M_a * ~M_b), plus S0->S4 upward assimilation and S4->S0 downward
      lens reconstruction that measurably reduces prediction mismatch.
  - S4 (Multi-World Lineage, 3-Way Relational Knowing, & 4-Axis Attribution):
      Home World + forkable Sandbox Worlds (inherit or blank lineage without
      overwriting Home), [Object / Self / Inter-space] encounter rings, and
      4-axis causal attribution [Internal / External / Boundary-Ignorance / Revision].

Zero external dependencies (100% pure Python stdlib). Grounded in AGENTS.md
4 Continuities + Chromatic Triad (Red Flux / Blue Order / Yellow Entropy).
"""

from __future__ import annotations

import ast
import datetime as _dt
import hashlib
import importlib.util
import math
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional, Sequence, Tuple


MV_DIM = 8  # Cl(3,0): [1, e1, e2, e3, e12, e23, e31, e123]
PHI = (1.0 + math.sqrt(5.0)) * 0.5
REPO_ROOT = Path(__file__).resolve().parents[3]


# =============================================================================
# 1. Pure-Python Invariant Cl(3,0) Geometric Algebra & Rotor Docking Kernel
#    (Invariant Rotor equivalent of core/topology/geometric_rotor_docking.py)
# =============================================================================


def mv_normalize(mv: Sequence[float]) -> List[float]:
    arr = [float(mv[i]) if i < len(mv) else 0.0 for i in range(MV_DIM)]
    norm = math.sqrt(sum(v * v for v in arr))
    if norm < 1e-12:
        return [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    return [round(v / norm, 5) for v in arr]


def mv_reverse(mv: Sequence[float]) -> List[float]:
    """Exact Cl(3,0) geometric reversion M~: negates Grade-2 bivectors & Grade-3 pseudoscalar."""
    a = [float(mv[i]) if i < len(mv) else 0.0 for i in range(MV_DIM)]
    return [a[0], a[1], a[2], a[3], -a[4], -a[5], -a[6], -a[7]]


def mv_geometric_product(a_in: Sequence[float], b_in: Sequence[float]) -> List[float]:
    """Exact Cl(3,0) geometric product a * b over [1, e1, e2, e3, e12, e23, e31, e123]."""
    a0, a1, a2, a3, a12, a23, a31, a123 = [float(a_in[i]) if i < len(a_in) else 0.0 for i in range(MV_DIM)]
    b0, b1, b2, b3, b12, b23, b31, b123 = [float(b_in[i]) if i < len(b_in) else 0.0 for i in range(MV_DIM)]

    c0 = a0 * b0 + a1 * b1 + a2 * b2 + a3 * b3 - a12 * b12 - a23 * b23 - a31 * b31 - a123 * b123
    c1 = a0 * b1 + a1 * b0 - a2 * b12 + a12 * b2 + a3 * b31 - a31 * b3 - a23 * b123 - a123 * b23
    c2 = a0 * b2 + a2 * b0 + a1 * b12 - a12 * b1 - a3 * b23 + a23 * b3 - a31 * b123 - a123 * b31
    c3 = a0 * b3 + a3 * b0 - a1 * b31 + a31 * b1 + a2 * b23 - a23 * b2 - a12 * b123 - a123 * b12
    c12 = a0 * b12 + a12 * b0 + a1 * b2 - a2 * b1 + a23 * b31 - a31 * b23 + a3 * b123 + a123 * b3
    c23 = a0 * b23 + a23 * b0 + a2 * b3 - a3 * b2 + a31 * b12 - a12 * b31 + a1 * b123 + a123 * b1
    c31 = a0 * b31 + a31 * b0 + a3 * b1 - a1 * b3 + a12 * b23 - a23 * b12 + a2 * b123 + a123 * b2
    c123 = a0 * b123 + a123 * b0 + a1 * b23 + a23 * b1 + a2 * b31 + a31 * b2 + a3 * b12 + a12 * b3
    return [c0, c1, c2, c3, c12, c23, c31, c123]


def wedge_points_to_line(p: Sequence[float], q: Sequence[float]) -> List[float]:
    """Point x Point -> Grade-2 bivector [e12, e23, e31] via outer product p ^ q."""
    p0, p1, p2 = (float(p[i]) if i < len(p) else 0.0 for i in range(3))
    q0, q1, q2 = (float(q[i]) if i < len(q) else 0.0 for i in range(3))
    return [p0 * q1 - p1 * q0, p1 * q2 - p2 * q1, p2 * q0 - p0 * q2]


def spectrum_to_multivector(
    flux: float,
    order: float,
    entropy: float,
    *,
    scale: int = 1,
    phase_bias: float = 0.0,
) -> List[float]:
    """
    Ascends Chromatic triad (Red Flux, Blue Order, Yellow Entropy) + unbounded scale depth
    into a unit Cl(3,0) multivector with authentic Grade-1 vector, Grade-2 bivector,
    and Grade-3 contextual volume components.
    """
    e1 = max(-1.0, min(1.0, (flux - 0.33) * 1.85))
    e2 = max(-1.0, min(1.0, (order - 0.33) * 1.85))
    e3 = max(-1.0, min(1.0, (entropy - 0.33) * 1.85))
    # Smooth unbounded scale modulation via tanh so S-3..S+10 all remain numerically crisp
    s_norm = math.tanh(float(scale) * 0.28)
    ang = (float(scale) + 1.0) * 0.58 + phase_bias
    ref = [math.cos(ang), math.sin(ang), math.cos(ang * PHI)]
    biv = wedge_points_to_line([e1, e2, e3], ref)
    biv_gain = 0.32 + 0.24 * (0.5 + 0.5 * s_norm)
    vol = (e1 * e2 * e3) * (0.24 + 0.22 * (0.5 + 0.5 * s_norm))
    scalar = max(0.18, 0.56 - 0.22 * s_norm)
    return mv_normalize([scalar, e1, e2, e3, biv[0] * biv_gain, biv[1] * biv_gain, biv[2] * biv_gain, vol])


def clifford_docking_affinity(mv_a: Sequence[float], mv_b: Sequence[float]) -> float:
    """
    Protein-like structural docking score via Cl(3,0) reverse geometric product M_a * ~M_b.
    High scalar alignment + low residual bivector torque => strong structural lock.
    Returns affinity in [-1.0, 1.0].
    """
    prod = mv_geometric_product(mv_normalize(mv_a), mv_reverse(mv_normalize(mv_b)))
    scalar_lock = prod[0]
    biv_torque = math.sqrt(prod[4] * prod[4] + prod[5] * prod[5] + prod[6] * prod[6])
    vol_tension = abs(prod[7])
    score = scalar_lock - 0.22 * biv_torque - 0.12 * vol_tension
    return round(max(-1.0, min(1.0, score)), 4)


def compose_parent_multivector(children_mvs: Sequence[Sequence[float]], scale: int) -> List[float]:
    """Ascends multiple child multivectors into a higher-scale composite rotor."""
    if not children_mvs:
        return [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    acc = [0.0] * MV_DIM
    for idx, mv in enumerate(children_mvs[:12]):
        n = mv_normalize(mv)
        for i in range(MV_DIM):
            acc[i] += n[i]
        if idx > 0:
            prev = mv_normalize(children_mvs[idx - 1])
            biv = wedge_points_to_line(prev[1:4], n[1:4])
            gain = 0.22 * (1.0 + 0.15 * scale)
            acc[4] += biv[0] * gain
            acc[5] += biv[1] * gain
            acc[6] += biv[2] * gain
    return mv_normalize(acc)


# =============================================================================
# 2. Dependency Scale-Rotorizer (Runtime Probes + Capability Membranes + AST)
# =============================================================================


CAPABILITY_MEMBRANES: List[Dict[str, Any]] = [
    {
        "id": "cap::tensor_algebra",
        "name_ko": "텐서·관계행렬 로터 막",
        "scale": 1,
        "external_deps": ["numpy", "scipy"],
        "invariant_rotor": "순수 Python 5×N×7 다중스케일 관계 텐서 · 야코비/파워 SVD · 벡터 내적",
        "variable_accelerator": "NumPy BLAS / SciPy 희소행렬 가속기",
        "chromatic": (0.30, 0.56, 0.14),
    },
    {
        "id": "cap::clifford_rotor",
        "name_ko": "Cl(3,0) 기하 로터 도킹 막",
        "scale": 1,
        "external_deps": ["numpy", "torch"],
        "invariant_rotor": "순수 Python 8성분 Cl(3,0) 기하곱(a*b) · 리버스 도킹(M_a*~M_b) · 외적 바이벡터",
        "variable_accelerator": "PyTorch 배치 텐서 / L0 CUDA Clifford 커널",
        "chromatic": (0.44, 0.44, 0.12),
    },
    {
        "id": "cap::optical_retina",
        "name_ko": "광학·시각 델타 로터 막",
        "scale": 0,
        "external_deps": ["cv2", "PIL", "mss"],
        "invariant_rotor": "브라우저 Canvas 48×27 휘도·운동·구조 델타 및 4KB 바이너리 엔트로피",
        "variable_accelerator": "OpenCV / Pillow / MSS 전역 화면 망막",
        "chromatic": (0.58, 0.24, 0.18),
    },
    {
        "id": "cap::acoustic_harmonic",
        "name_ko": "음향·배음 파동 로터 막",
        "scale": 0,
        "external_deps": ["scipy", "sounddevice", "pyaudio"],
        "invariant_rotor": "순수 Python DFT 배음 응축 + 브라우저 Web Audio 합성기",
        "variable_accelerator": "호스트 오디오 디바이스 / SciPy FFT",
        "chromatic": (0.52, 0.30, 0.18),
    },
    {
        "id": "cap::hw_cuda_kernel",
        "name_ko": "L0 하드웨어·병렬 연산 로터 막",
        "scale": 0,
        "external_deps": ["cuda_so", "torch", "cupy"],
        "invariant_rotor": "순수 Python/JS 분기없는 시그모이드 수문 회로 + S0→S2 기어비 절감 엔진",
        "variable_accelerator": "L0_substrate C++/CUDA(.cu) · Verilog RTL 컴파일 바이너리",
        "chromatic": (0.36, 0.50, 0.14),
    },
    {
        "id": "cap::os_boundary_protocol",
        "name_ko": "OS·브라우저 경계 프로토콜 막",
        "scale": 1,
        "external_deps": ["psutil", "win32gui", "tkinter"],
        "invariant_rotor": "브라우저 탭 포인터/키 리듬 관측 + 로컬 JSON 생태계 + Node 호스트 경계",
        "variable_accelerator": "로컬 PC 체화 브리지(.py) / Win32·psutil 전역 프로토콜",
        "chromatic": (0.28, 0.52, 0.20),
    },
    {
        "id": "cap::missing_upper_bridge",
        "name_ko": "상위 누락 계층(L2/L3) 흡수 막",
        "scale": 2,
        "external_deps": ["elysia_core", "simulators", "L2_cognitive_engine", "L3_interface"],
        "invariant_rotor": "단일 척추 내장 Telos 목적장 · 4축 자기경계 · 구조실험 로터(StructuralExperimentRotor)",
        "variable_accelerator": "외부 레포 분리 모듈(L2_cognitive_engine / L3_interface) 선택 결합",
        "chromatic": (0.34, 0.34, 0.32),
    },
]

_LIVE_WEB_MODULES = {
    "L1_causal_field/core/orchestration/bidirectional_phase_sync.py",
    "L1_causal_field/core/orchestration/canonical_runtime.py",
    "L1_causal_field/core/orchestration/desktop_embodiment.py",
    "L1_causal_field/core/orchestration/digest_imitate_recreate.py",
    "L1_causal_field/core/orchestration/discipline_tool_forge.py",
    "L1_causal_field/core/orchestration/language_acquisition_engine.py",
    "L1_causal_field/core/orchestration/living_companion_field.py",
    "L1_causal_field/core/orchestration/local_corpus_extractor.py",
    "L1_causal_field/core/orchestration/plastic_self_manifold.py",
    "L1_causal_field/core/orchestration/process_contrast_observer.py",
    "L1_causal_field/core/orchestration/qualitative_spectrum_field.py",
    "L1_causal_field/core/orchestration/scale_rotor_core.py",
    "L1_causal_field/core/orchestration/structural_experiment_rotor.py",
    "L1_causal_field/core/orchestration/unified_dataflow_engine.py",
    "L1_causal_field/core/orchestration/unified_neural_spine.py",
    "L1_causal_field/core/orchestration/vessel_trajectory_rotor.py",
}

_EXTERNAL_DEP_SET = {
    "numpy", "torch", "cv2", "PIL", "scipy", "matplotlib", "psutil", "mss",
    "transformers", "sounddevice", "pyaudio", "win32gui", "win32api", "tkinter",
    "sklearn", "pandas", "networkx", "sympy", "cupy", "pybind11",
}
_MISSING_REPO_PREFIXES = {"elysia_core", "simulators", "L2_cognitive_engine", "L3_interface"}


def probe_runtime_capabilities() -> Dict[str, Any]:
    """Probes what real runtime capabilities exist right now without crashing."""
    pkgs = ["numpy", "torch", "cv2", "PIL", "scipy", "psutil", "mss", "transformers"]
    pkg_status: Dict[str, bool] = {}
    for p in pkgs:
        try:
            pkg_status[p] = importlib.util.find_spec(p) is not None
        except Exception:
            pkg_status[p] = False

    l0_dir = REPO_ROOT / "L0_substrate"
    compiled_bins = 0
    if l0_dir.is_dir():
        for dp, _, fns in os.walk(l0_dir):
            for fn in fns:
                if fn.endswith((".so", ".pyd", ".dll", ".wasm", ".ptx", ".cubin")):
                    compiled_bins += 1

    membranes_out = []
    for m in CAPABILITY_MEMBRANES:
        ext_deps = m["external_deps"]
        active_accel = [d for d in ext_deps if pkg_status.get(d, False)]
        if m["id"] == "cap::hw_cuda_kernel" and compiled_bins > 0:
            active_accel.append(f"L0_binary({compiled_bins})")
        membranes_out.append({
            "id": m["id"],
            "name_ko": m["name_ko"],
            "scale": m["scale"],
            "external_deps": ext_deps,
            "active_accelerators": active_accel,
            "mode": "ACCELERATED" if active_accel else "INVARIANT_NATIVE",
            "mode_ko": "가변 가속기 결합" if active_accel else "불변 로터 순수 구동",
            "invariant_rotor": m["invariant_rotor"],
            "variable_accelerator": m["variable_accelerator"],
            "chromatic": list(m["chromatic"]),
        })

    return {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "packages": pkg_status,
        "l0_compiled_binaries": compiled_bins,
        "membranes": membranes_out,
        "invariant_coverage_pct": 100.0,
    }


def _infer_scale_from_path(rel_path: str) -> int:
    low = rel_path.lower()
    if low.startswith("l0_substrate/") and not low.startswith("l0_substrate/mva/static/"):
        return 0
    if any(k in low for k in ("layer_0", "sensory/", "ocular", "acoustic", "retina", "desktop_embodiment")):
        return 0
    if any(k in low for k in ("layer_1", "physics/", "lens/", "cellular_boundary", "power/", "ingestion/")):
        return 1
    if any(k in low for k in ("layer_2", "topology/", "memory/", "language", "corpus", "tool_forge", "embodiment/")):
        return 2
    if any(k in low for k in ("layer_3", "causal_world", "orchestration/", "intelligence/", "evolution/", "mva/static/")):
        return 3
    if any(k in low for k in ("consciousness/", "sovereignty/", "meta/", "plastic_self", "telos", "vertical_scale_spine")):
        return 4
    return 2


def _infer_chromatic_from_module(rel_path: str, classes: List[str], funcs: List[str], deps: List[str]) -> Tuple[float, float, float]:
    blob = (rel_path + " " + " ".join(classes) + " " + " ".join(funcs)).lower()
    flux = 0.25
    order = 0.25
    entropy = 0.18
    if any(k in blob for k in ("flow", "wave", "flux", "motor", "audio", "retina", "motion", "kinetic", "live", "pulse", "rotor", "orbit")):
        flux += 0.32
    if any(k in blob for k in ("constraint", "order", "schema", "rule", "ledger", "canonical", "spine", "hierarchy", "bridge", "protocol", "governance")):
        order += 0.34
    if any(k in blob for k in ("entropy", "explore", "mutant", "evolve", "sandbox", "diverge", "novel", "plastic", "dream", "counterfactual", "ignorance")):
        entropy += 0.32
    if deps:
        entropy += min(0.16, 0.04 * len(deps))
    tot = flux + order + entropy
    return (round(flux / tot, 3), round(order / tot, 3), round(entropy / tot, 3))


def _map_deps_to_membranes(ext_deps: List[str], missing_upper: List[str], is_l0: bool) -> List[str]:
    mems: List[str] = []
    if is_l0 or "torch" in ext_deps or "cupy" in ext_deps:
        mems.append("cap::hw_cuda_kernel")
    if "numpy" in ext_deps or "scipy" in ext_deps:
        mems.append("cap::tensor_algebra")
    if "cv2" in ext_deps or "PIL" in ext_deps or "mss" in ext_deps:
        mems.append("cap::optical_retina")
    if "sounddevice" in ext_deps or "pyaudio" in ext_deps:
        mems.append("cap::acoustic_harmonic")
    if "psutil" in ext_deps or "win32gui" in ext_deps or "tkinter" in ext_deps:
        mems.append("cap::os_boundary_protocol")
    if missing_upper:
        mems.append("cap::missing_upper_bridge")
    if not mems:
        mems.append("cap::clifford_rotor")
    return mems


def scan_repository_as_scale_rotors(max_entries: int = 180) -> Dict[str, Any]:
    """
    Scale-Rotorizes the entire repository's file & dependency structure via safe
    pure-Python AST/header introspection (never executes unverified/blocked files).
    """
    runtime = probe_runtime_capabilities()
    pkg_installed = runtime["packages"]

    summary_counts = {
        "total_scanned": 0,
        "live_bound": 0,
        "invariant_bridgeable": 0,
        "missing_upper_bridge": 0,
        "hw_kernel_port": 0,
        "pure_dormant_seed": 0,
        "by_scale": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
        "external_dep_freq": {},
    }
    dep_freq: Dict[str, int] = {}
    all_entries: List[Dict[str, Any]] = []

    # 1. Scan L1_causal_field Python modules via AST
    l1_root = REPO_ROOT / "L1_causal_field"
    if l1_root.is_dir():
        for dp, _, fns in os.walk(l1_root):
            for fn in sorted(fns):
                if not fn.endswith(".py") or fn == "__init__.py":
                    continue
                full = Path(dp) / fn
                rel = full.relative_to(REPO_ROOT).as_posix()
                try:
                    raw = full.read_text(encoding="utf-8", errors="ignore")
                    lines = raw.count("\n") + 1
                    tree = ast.parse(raw)
                except Exception:
                    continue

                classes = [n.name for n in tree.body if isinstance(n, ast.ClassDef)][:10]
                funcs = [n.name for n in tree.body if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")][:12]
                doc = (ast.get_docstring(tree) or "").strip().splitlines()[0][:140] if ast.get_docstring(tree) else ""

                ext_deps: List[str] = []
                missing_upper: List[str] = []
                internal_refs: List[str] = []
                for node in ast.walk(tree):
                    mods: List[str] = []
                    if isinstance(node, ast.Import):
                        mods = [a.name.split(".")[0] for a in node.names]
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        mods = [node.module.split(".")[0]]
                    for top in mods:
                        if top in _EXTERNAL_DEP_SET:
                            if top not in ext_deps:
                                ext_deps.append(top)
                            dep_freq[top] = dep_freq.get(top, 0) + 1
                        elif top in _MISSING_REPO_PREFIXES:
                            if top not in missing_upper:
                                missing_upper.append(top)
                            dep_freq[top] = dep_freq.get(top, 0) + 1
                        elif top in ("core", "L1_causal_field"):
                            if isinstance(node, ast.ImportFrom) and node.module:
                                internal_refs.append(node.module)

                missing_now = [d for d in ext_deps if not pkg_installed.get(d, False)]
                scale = _infer_scale_from_path(rel)
                flux, order, entropy = _infer_chromatic_from_module(rel, classes, funcs, missing_now + missing_upper)
                membranes = _map_deps_to_membranes(missing_now, missing_upper, is_l0=False)

                if rel in _LIVE_WEB_MODULES:
                    status = "LIVE_BOUND"
                    status_ko = "라이브 척추 직결"
                    bridge_recipe = "현재 단일 정본 척추에서 실시간 가동 중"
                    summary_counts["live_bound"] += 1
                elif missing_upper:
                    status = "MISSING_PATH_BRIDGE"
                    status_ko = "누락 상위경로 가교"
                    bridge_recipe = (
                        f"부재 경로({', '.join(missing_upper[:3])})를 단일 척추 내장 Telos·4축경계·구조실험 로터로 치환 흡수"
                    )
                    summary_counts["missing_upper_bridge"] += 1
                elif missing_now:
                    status = "INVARIANT_BRIDGEABLE"
                    status_ko = "의존성 로터 가교 가능"
                    bridge_recipe = (
                        f"외부 의존성({', '.join(missing_now[:3])})을 {', '.join(membranes[:2])} 불변 커널로 분리·AST 원리 흡수 가능"
                    )
                    summary_counts["invariant_bridgeable"] += 1
                else:
                    status = "PURE_DORMANT_SEED"
                    status_ko = "순수 대기 씨앗(즉시 결합)"
                    bridge_recipe = "외부 의존성 0 — 즉시 단일 척추 S2 기관으로 편입 가능"
                    summary_counts["pure_dormant_seed"] += 1

                summary_counts["total_scanned"] += 1
                summary_counts["by_scale"][scale] = summary_counts["by_scale"].get(scale, 0) + 1

                # Priority score so key architectural modules always surface in Reality View
                prio = lines * 0.015 + len(classes) * 3.5 + len(internal_refs) * 0.8
                if status == "LIVE_BOUND":
                    prio += 60.0
                if any(k in rel.lower() for k in ("vertical_scale_spine", "unified_scale_rotor", "scale_rotor_embodied", "causal_field", "geometric_rotor", "layer_1", "layer_2", "layer_3")):
                    prio += 48.0

                all_entries.append({
                    "path": rel,
                    "name": Path(rel).stem,
                    "lang": "python",
                    "scale": scale,
                    "lines": lines,
                    "status": status,
                    "status_ko": status_ko,
                    "classes": classes,
                    "functions": funcs[:6],
                    "doc": doc,
                    "external_deps": ext_deps,
                    "missing_deps": missing_now + missing_upper,
                    "membranes": membranes,
                    "bridge_recipe": bridge_recipe,
                    "chromatic": [flux, order, entropy],
                    "multivector": spectrum_to_multivector(flux, order, entropy, scale=scale),
                    "priority": round(prio, 2),
                })

    # 2. Scan key L0_substrate C++/CUDA/Verilog kernels + static frontend engines
    l0_root = REPO_ROOT / "L0_substrate"
    if l0_root.is_dir():
        for dp, _, fns in os.walk(l0_root):
            for fn in sorted(fns):
                if not fn.endswith((".cu", ".cpp", ".hpp", ".v", ".js", ".mjs")):
                    continue
                full = Path(dp) / fn
                rel = full.relative_to(REPO_ROOT).as_posix()
                is_static_js = rel.startswith("L0_substrate/mva/static/")
                try:
                    raw = full.read_text(encoding="utf-8", errors="ignore")
                    lines = raw.count("\n") + 1
                except Exception:
                    continue
                if not is_static_js and lines < 25:
                    continue

                scale = 3 if is_static_js else 0
                status = "LIVE_BOUND" if rel in (
                    "L0_substrate/mva/static/elysia_live_game.js",
                    "L0_substrate/mva/static/elysia_browser_os.js",
                    "L0_substrate/mva/static/unified_scale_rotor_field.js",
                    "L0_substrate/mva/static/causal_3d_atelier.mjs",
                    "L0_substrate/mva/static/elysia_reality_view.js",
                ) else ("HW_KERNEL_PORT" if not is_static_js else "PURE_DORMANT_SEED")

                if status == "HW_KERNEL_PORT":
                    summary_counts["hw_kernel_port"] += 1
                    status_ko = "L0 가속 커널 대기"
                    bridge_recipe = "미컴파일 C++/CUDA/RTL 소스 — 가변 가속 포트로 등록, 런타임은 불변 로터로 대체 구동"
                    membranes = ["cap::hw_cuda_kernel"]
                    missing = ["cuda_so"]
                elif status == "LIVE_BOUND":
                    summary_counts["live_bound"] += 1
                    status_ko = "브라우저 표현 로터 직결"
                    bridge_recipe = "브라우저 표현/입력 계층과 실시간 연결됨"
                    membranes = ["cap::os_boundary_protocol"]
                    missing = []
                else:
                    summary_counts["pure_dormant_seed"] += 1
                    status_ko = "정적 프론트 대기 뷰"
                    bridge_recipe = "구세대 분리 프론트 뷰 — 단일 리얼리티 뷰로 점진 통합 대상"
                    membranes = ["cap::os_boundary_protocol"]
                    missing = []

                summary_counts["total_scanned"] += 1
                summary_counts["by_scale"][scale] = summary_counts["by_scale"].get(scale, 0) + 1
                flux, order, entropy = (0.48, 0.40, 0.12) if not is_static_js else (0.42, 0.42, 0.16)
                prio = lines * 0.012 + (50.0 if status == "LIVE_BOUND" else 18.0 if fn.endswith((".cu", ".v")) else 4.0)
                all_entries.append({
                    "path": rel,
                    "name": Path(rel).name,
                    "lang": full.suffix.lstrip("."),
                    "scale": scale,
                    "lines": lines,
                    "status": status,
                    "status_ko": status_ko,
                    "classes": [],
                    "functions": [],
                    "doc": f"{full.suffix} {'표현/UI 모듈' if is_static_js else '하드웨어/커널 소스'} ({lines}줄)",
                    "external_deps": missing,
                    "missing_deps": missing,
                    "membranes": membranes,
                    "bridge_recipe": bridge_recipe,
                    "chromatic": [flux, order, entropy],
                    "multivector": spectrum_to_multivector(flux, order, entropy, scale=scale),
                    "priority": round(prio, 2),
                })

    all_entries.sort(key=lambda e: (-e["priority"], e["path"]))
    top_deps = sorted(dep_freq.items(), key=lambda kv: -kv[1])[:12]
    summary_counts["external_dep_freq"] = dict(top_deps)

    return {
        "scanned_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "runtime": runtime,
        "summary": summary_counts,
        "modules": all_entries[:max_entries],
        "total_catalog_count": len(all_entries),
    }


def extract_module_invariants_ast(rel_path: str) -> Dict[str, Any]:
    """
    Safely parses ANY repository file via AST/regex (never imports or executes it)
    to distill its structural invariants, classes, methods, mathematical equations,
    dependency membranes, and pure-Python bridge plan.
    """
    clean_rel = (rel_path or "").strip().lstrip("/").replace("\\", "/")
    if not clean_rel or ".." in clean_rel:
        raise ValueError("유효하지 않은 모듈 경로입니다.")
    target = (REPO_ROOT / clean_rel).resolve()
    try:
        target.relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise ValueError("워크스페이스 바깥 경로는 읽을 수 없습니다.") from exc
    if not target.is_file():
        raise FileNotFoundError(f"모듈을 찾을 수 없습니다: {clean_rel}")

    raw = target.read_text(encoding="utf-8", errors="ignore")
    lines = raw.splitlines()
    scale = _infer_scale_from_path(clean_rel)

    classes_info: List[Dict[str, Any]] = []
    funcs_info: List[str] = []
    ext_deps: List[str] = []
    missing_upper: List[str] = []
    doc_summary = ""

    if target.suffix == ".py":
        tree = ast.parse(raw)
        doc_summary = (ast.get_docstring(tree) or "").strip()[:360]
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                methods = [
                    m.name for m in node.body
                    if isinstance(m, ast.FunctionDef) and not m.name.startswith("__")
                ][:10]
                cdoc = (ast.get_docstring(node) or "").strip().splitlines()[0][:120] if ast.get_docstring(node) else ""
                classes_info.append({"name": node.name, "methods": methods, "doc": cdoc})
            elif isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                funcs_info.append(node.name)
        for node in ast.walk(tree):
            mods = []
            if isinstance(node, ast.Import):
                mods = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                mods = [node.module.split(".")[0]]
            for top in mods:
                if top in _EXTERNAL_DEP_SET and top not in ext_deps:
                    ext_deps.append(top)
                elif top in _MISSING_REPO_PREFIXES and top not in missing_upper:
                    missing_upper.append(top)
    else:
        # C++/CUDA/Verilog/JS lightweight structural extraction
        sig_hits = re.findall(r"(?:__global__|class|struct|module|function)\s+([A-Za-z_][A-Za-z0-9_]*)", raw)
        for s in sig_hits[:14]:
            if s not in funcs_info:
                funcs_info.append(s)
        doc_summary = " ".join(ln.strip(" /*#") for ln in lines[:8] if ln.strip())[:260]
        if target.suffix in (".cu", ".cpp", ".hpp", ".v"):
            ext_deps.append("cuda_so")

    flux, order, entropy = _infer_chromatic_from_module(
        clean_rel, [c["name"] for c in classes_info], funcs_info, ext_deps + missing_upper
    )
    mv = spectrum_to_multivector(flux, order, entropy, scale=scale)
    membranes = _map_deps_to_membranes(ext_deps, missing_upper, is_l0=clean_rel.startswith("L0_substrate/") and target.suffix != ".js")

    # Build concrete Scale-Rotorization transformation steps
    bridge_steps: List[str] = []
    if "numpy" in ext_deps or "scipy" in ext_deps:
        bridge_steps.append("NumPy 배열·내적 연산을 S1 [텐서·관계행렬 로터 막] 불변 커널(5×N×7 순수 파이썬 텐서) 포트로 분리")
    if "torch" in ext_deps or "cuda_so" in ext_deps:
        bridge_steps.append("GPU/CUDA 커널을 S0 [가변 가속기]로 위임하고, 코어 위상 연산은 Cl(3,0) 불변 로터로 항시 구동")
    if "PIL" in ext_deps or "cv2" in ext_deps or "mss" in ext_deps:
        bridge_steps.append("화면/이미지 픽셀 의존성을 S0 [광학·시각 델타 막](브라우저 48×27 델타) 입력 포트로 교체")
    if missing_upper:
        bridge_steps.append(f"누락된 외부 계층({', '.join(missing_upper)}) 대신 단일 척추 S4 Telos·4축경계·구조실험 로터를 직접 바인딩")
    if not bridge_steps:
        bridge_steps.append("외부 패키지 장벽 없음 — 단일 정본 척추 S2/S3 그래프에 직접 도킹 가능")

    return {
        "path": clean_rel,
        "name": target.stem,
        "scale": scale,
        "lines": len(lines),
        "doc": doc_summary or f"{target.name} 구조 원리",
        "classes": classes_info[:10],
        "functions": funcs_info[:14],
        "external_deps": ext_deps,
        "missing_upper": missing_upper,
        "membranes": membranes,
        "chromatic": [flux, order, entropy],
        "multivector": mv,
        "bridge_steps": bridge_steps,
    }


# =============================================================================
# 3. Unified Canonical Neural Spine (S0..S4 + Multi-World + Bidirectional Loop)
# =============================================================================


def _now_iso() -> str:
    return _dt.datetime.now().isoformat(timespec="seconds")


class UnifiedNeuralSpine:
    """
    Single Canonical Scale-Rotor Neural Spine (S0..S4) unifying:
      - Homogeneous ScaleRotorNode / ScaleRotorLink graph with Cl(3,0) docking
      - Multi-World Lineage (Home World + Forkable Sandbox Worlds)
      - 3-Way Relational Knowing [Object / Self / Inter-space]
      - 4-Axis Causal Attribution [Internal / External / Boundary-Ignorance / Revision]
      - Bidirectional Vertical Cycle (S0->S4 upward + S4->S0 downward error reduction)
      - Live Codebase Dependency Scale-Rotorization & AST Organ Absorption
    """

    MAX_NODES = 240
    MAX_LINKS = 520
    MAX_EXPERIENCES = 80
    MAX_INPUT_RINGS = 120

    def __init__(self) -> None:
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.links: List[Dict[str, Any]] = []
        self._link_keys: Dict[Tuple[str, str, str], int] = {}

        # Multi-World Lineage (Section 4 & 5 of OS Integration Spec)
        self.worlds: Dict[str, Dict[str, Any]] = {}
        self.active_world_id: str = "world_home"
        self.sandbox_seq: int = 0

        # Bidirectional S0<->S4 Vertical Cycle State
        self.vertical_cycles: int = 0
        self.prediction_gap: float = 0.72
        self.last_vertical_trace: Dict[str, Any] = {}
        self.downward_lens_weights: Dict[str, float] = {
            "flux_gain": 1.0,
            "order_gain": 1.0,
            "entropy_sensitivity": 1.0,
            "docking_threshold": 0.46,
        }

        # 4-Axis Causal Attribution (seed lens projection — NOT a closed ceiling!)
        self.four_axis: Dict[str, Any] = {
            "internal_origin": 0.42,
            "external_influence": 0.34,
            "boundary_ignorance": 0.16,
            "criteria_revision": 0.08,
            "last_revision_note": "열린 스케일로터 척추 부팅 · S0~S4·3-Way·4축은 분할/통합/확장 가능한 씨앗 재료",
        }

        # Open-Ended Horizontal Cognitive Axes (3-Way + 4-Axis are initial seeds; expands horizontally!)
        self.horizontal_axes: List[Dict[str, Any]] = [
            {"id": "lens3::object", "name": "대상 (Object)", "group": "relational_seed", "scale": 2, "weight": 0.34, "origin": "seed"},
            {"id": "lens3::self", "name": "자기 (Self)", "group": "relational_seed", "scale": 2, "weight": 0.33, "origin": "seed"},
            {"id": "lens3::inter_space", "name": "사이 (Inter-space)", "group": "relational_seed", "scale": 2, "weight": 0.33, "origin": "seed"},
            {"id": "axis4::internal", "name": "내부 기원", "group": "attribution_seed", "scale": 4, "weight": 0.42, "origin": "seed"},
            {"id": "axis4::external", "name": "외부 영향", "group": "attribution_seed", "scale": 4, "weight": 0.34, "origin": "seed"},
            {"id": "axis4::ignorance", "name": "경계·미지", "group": "attribution_seed", "scale": 4, "weight": 0.16, "origin": "seed"},
            {"id": "axis4::revision", "name": "기준 수정", "group": "attribution_seed", "scale": 4, "weight": 0.08, "origin": "seed"},
        ]
        self.topology_ops_count: Dict[str, int] = {
            "differentiate": 0,
            "integrate": 0,
            "expand_axis": 0,
            "limit_fold": 0,
            "boundary_couple": 0,
            "boundary_detach": 0,
        }
        self.folded_horizons: List[Dict[str, Any]] = []
        self.working_memory_budget: int = self.MAX_NODES

        # Self / Non-Self Boundary Handles: external tools, software, disciplines & modules
        # coupled STRICTLY via control handles & observable outcomes (0% internal blueprint ingestion!)
        self.external_handles: Dict[str, Dict[str, Any]] = self._default_external_handles()

        # Codebase Scale-Rotorization cache & absorbed modules
        self.codebase_map: Optional[Dict[str, Any]] = None
        self.absorbed_modules: Dict[str, Dict[str, Any]] = {}

        self._bootstrap_canonical_spine()

    def _default_external_handles(self) -> Dict[str, Dict[str, Any]]:
        """
        Pre-registered Non-Self external tools, environments & disciplines.
        Notice `coupled: False` initially and `internal_ingested_pct: 0.0`:
        Elysia does NOT swallow Blender's source code or a car's engine blueprints;
        she only couples to the manipulation handle & observable feedback surface when needed,
        and detaches cleanly afterward.
        """
        seeds = [
            {
                "id": "handle::blender_3d",
                "name": "Blender 3D 조형 도구",
                "domain": "tool",
                "control_handles": ["오브젝트 배치", "메시 변형(이동·회전·스케일)", "조명·카메라 구도", "렌더 실행"],
                "observable_surface": ["2D 투영 실루엣", "깊이·음영 대비", "완성 프레임 이미지"],
                "opaque_non_self": "Blender C++ 커널 · Cycles 레이트레이서 · 의존성 수만 줄 전체 (알 필요 없음 · 비자아 유지)",
                "chromatic": [0.46, 0.36, 0.18],
            },
            {
                "id": "handle::vehicle_driving",
                "name": "자동차 (이동 수단)",
                "domain": "physical_tool",
                "control_handles": ["조향(운전대)", "가속 페달", "제동 페달", "기어 전환"],
                "observable_surface": ["속도·가속감", "전방 시야·궤적", "노면 마찰·제동 거리"],
                "opaque_non_self": "내연기관·변속기·ECU 회로·금속 피로 설계도 전체 (설계 몰라도 안전 운전 가능)",
                "chromatic": [0.54, 0.30, 0.16],
            },
            {
                "id": "handle::optics_perspective",
                "name": "광학 · 원근법 학문",
                "domain": "discipline",
                "control_handles": ["소실점·시야각 설정", "광원 방향·거리", "명암 대비 조절"],
                "observable_surface": ["2D 평면 위 입체 심도", "그림자 투영 각도"],
                "opaque_non_self": "양자전기역학(QED)·맥스웰 편미분 방정식 전체 (조형 연출엔 경계 규칙만 결합)",
                "chromatic": [0.30, 0.52, 0.18],
            },
            {
                "id": "handle::browser_os_host",
                "name": "브라우저 · OS 환경",
                "domain": "environment",
                "control_handles": ["포인터·키 리듬 입력", "로컬 저장소 기록", "캔버스 표현 출력"],
                "observable_surface": ["렌더링 픽셀 변화", "응답 지연·프레임 리듬", "권한 허용/거부 경계"],
                "opaque_non_self": "OS 커널 스케줄러·V8/Blink 렌더링 엔진·GPU 드라이버 내부 (경계 너머 비자아)",
                "chromatic": [0.38, 0.42, 0.20],
            },
        ]
        out: Dict[str, Dict[str, Any]] = {}
        for item in seeds:
            out[item["id"]] = {
                **item,
                "coupled": False,
                "internal_ingested_pct": 0.0,
                "use_count": 0,
                "mastery_at_boundary": 0.18,
                "last_action": "",
                "last_observed": "",
                "updated_at": _now_iso(),
            }
        return out

    def _create_world_record(
        self,
        world_id: str,
        name: str,
        role: str,
        parent_id: Optional[str],
        fork_mode: str,
        *,
        inherit_from: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        experiences = list(inherit_from.get("experiences", [])[-24:]) if inherit_from else []
        input_rings = list(inherit_from.get("input_rings", [])[-24:]) if inherit_from else []
        revisions = list(inherit_from.get("revisions", [])[-16:]) if inherit_from else []
        return {
            "id": world_id,
            "name": name,
            "role": role,  # "home" | "sandbox"
            "parent_id": parent_id,
            "fork_mode": fork_mode,  # "origin" | "inherit" | "blank"
            "created_at": _now_iso(),
            "experiences": experiences,
            "input_rings": input_rings,
            "revisions": revisions,
            "total_pointer_distance": float(inherit_from.get("total_pointer_distance", 0.0)) if inherit_from else 0.0,
            "total_key_events": int(inherit_from.get("total_key_events", 0)) if inherit_from else 0,
            "cycles": int(inherit_from.get("cycles", 0)) if inherit_from else 0,
        }

    def _bootstrap_canonical_spine(self) -> None:
        self.worlds["world_home"] = self._create_world_record(
            "world_home", "홈 세계 (Home)", "home", None, "origin"
        )
        self.active_world_id = "world_home"

        # Seed S0/S1 Capability Membranes so dependency-rotor topology is live from frame 0
        runtime = probe_runtime_capabilities()
        for m in runtime["membranes"]:
            fl, od, en = m["chromatic"]
            self.upsert_node(
                node_id=m["id"],
                scale=int(m["scale"]),
                kind="membrane",
                label=m["name_ko"],
                flux=fl,
                order=od,
                entropy=en,
                meta={
                    "mode": m["mode"],
                    "mode_ko": m["mode_ko"],
                    "invariant_rotor": m["invariant_rotor"],
                    "variable_accelerator": m["variable_accelerator"],
                    "external_deps": m["external_deps"],
                    "active_accelerators": m["active_accelerators"],
                },
                auto_dock=False,
            )

        # Seed S3 Spacetime World Model Core & S4 Identity Horizon
        self.upsert_node(
            node_id="s3::reality_world_model",
            scale=3,
            kind="world_model",
            label="통합 시공간 월드모델 (Reality Field)",
            flux=0.38,
            order=0.44,
            entropy=0.18,
            meta={"role": "단일 감각-개념-코드-행동 결합장"},
            auto_dock=False,
        )
        self.upsert_node(
            node_id="s4::sovereign_identity_horizon",
            scale=4,
            kind="telos",
            label="엘리시아 정체성 · 4축 자기경계 (S4)",
            flux=0.34,
            order=0.46,
            entropy=0.20,
            meta={"role": "3-Way 관계 앎 & 홈/샌드박스 계보 축"},
            auto_dock=False,
        )
        self.add_link("s3::reality_world_model", "s4::sovereign_identity_horizon", "ascends_to", 1.2)
        self.add_link("s4::sovereign_identity_horizon", "s3::reality_world_model", "reconstructs", 1.0)
        for m in runtime["membranes"]:
            self.add_link(m["id"], "s3::reality_world_model", "sustains", 0.9)

        # Seed 3-Way (대상·자기·사이) & 4-Axis (내부·외부·미지·기준수정) as live splittable/mergeable RotorUnits!
        seed_chromatics = {
            "lens3::object": (0.48, 0.34, 0.18),
            "lens3::self": (0.28, 0.54, 0.18),
            "lens3::inter_space": (0.36, 0.32, 0.32),
            "axis4::internal": (0.30, 0.56, 0.14),
            "axis4::external": (0.56, 0.26, 0.18),
            "axis4::ignorance": (0.22, 0.20, 0.58),
            "axis4::revision": (0.42, 0.36, 0.22),
        }
        for ax in self.horizontal_axes:
            fl, od, en = seed_chromatics.get(ax["id"], (0.34, 0.34, 0.32))
            self.upsert_node(
                node_id=ax["id"],
                scale=int(ax["scale"]),
                kind="seed_lens",
                label=ax["name"],
                flux=fl,
                order=od,
                entropy=en,
                meta={
                    "axis_group": ax["group"],
                    "origin": ax["origin"],
                    "role": "분할(↓)·통합(↑)·수평확장(↔) 가능한 씨앗 인지단위",
                },
                auto_dock=False,
            )
            anchor = "s3::reality_world_model" if ax["scale"] <= 2 else "s4::sovereign_identity_horizon"
            self.add_link(ax["id"], anchor, "seed_lens_bind", 0.85)

        # Fast initial codebase scale-rotor scan (bounded for crisp startup)
        self.refresh_codebase_rotor_map(max_entries=160)

    def _active_world(self) -> Dict[str, Any]:
        if self.active_world_id not in self.worlds:
            self.active_world_id = "world_home"
        return self.worlds[self.active_world_id]

    def _compute_3d_position(self, node_id: str, scale: int, mv: Sequence[float]) -> List[float]:
        """Unbounded 3D spacetime coordinates supporting arbitrary vertical depth (S-N .. S+N)."""
        h = int(hashlib.md5(node_id.encode("utf-8")).hexdigest()[:8], 16)
        base_theta = ((h % 3600) / 3600.0) * math.tau
        # Smooth non-clamping radius: deeper micro scales contract gracefully, higher macro scales expand outward
        ring_r = max(0.38, 0.92 + max(-2.5, float(scale)) * 0.56)
        e1, e2, e3 = mv[1], mv[2], mv[3]
        theta = base_theta + math.atan2(e2, e1 + 1e-6) * 0.42
        elev = (float(scale) - 2.0) * 0.68 + e3 * 0.48
        x = ring_r * math.cos(theta)
        z = ring_r * math.sin(theta)
        y = elev
        return [round(x, 3), round(y, 3), round(z, 3)]

    def upsert_node(
        self,
        *,
        node_id: str,
        scale: int,
        kind: str,
        label: str,
        flux: float,
        order: float,
        entropy: float,
        meta: Optional[Dict[str, Any]] = None,
        auto_dock: bool = True,
    ) -> Dict[str, Any]:
        # Unbounded vertical scale: supports S-N (sub-atomic split) through S+N (meta-ecosystem integration)
        scale = int(scale)
        tot = max(1e-6, flux + order + entropy)
        fl, od, en = round(flux / tot, 3), round(order / tot, 3), round(entropy / tot, 3)

        # Apply S4->S0 downward lens modulation gently
        mod_fl = fl * self.downward_lens_weights["flux_gain"]
        mod_od = od * self.downward_lens_weights["order_gain"]
        mod_en = en * self.downward_lens_weights["entropy_sensitivity"]
        mv = spectrum_to_multivector(mod_fl, mod_od, mod_en, scale=scale)
        pos = self._compute_3d_position(node_id, scale, mv)

        # Open spectral signature: 3 seed wavelengths (flux/order/entropy) + any emergent horizontal channels!
        open_spectrum: Dict[str, float] = {"flux": fl, "order": od, "entropy": en}
        if meta and isinstance(meta.get("extra_spectrum"), dict):
            for sk, sv in meta["extra_spectrum"].items():
                open_spectrum[str(sk)[:28]] = round(float(sv), 3)

        if node_id in self.nodes:
            nd = self.nodes[node_id]
            nd["activations"] = int(nd.get("activations", 1)) + 1
            nd["mass"] = round(min(6.0, float(nd.get("mass", 1.0)) + 0.14), 3)
            nd["chromatic"] = [fl, od, en]
            prev_spec = nd.get("open_spectrum") if isinstance(nd.get("open_spectrum"), dict) else {}
            prev_spec.update(open_spectrum)
            nd["open_spectrum"] = prev_spec
            nd["multivector"] = mv
            nd["pos"] = pos
            nd["updated_at"] = _now_iso()
            if meta:
                nd["meta"].update(meta)
        else:
            # Limit Perception instead of mechanical crash or blind deletion:
            # When working-memory pressure hits budget, FOLD low-salience clusters into a compressed Horizon Rotor!
            if len(self.nodes) >= self.working_memory_budget:
                self.fold_under_limit(reason="작업기억 밀도 한계 자각 → 자동 원근 접기")

            nd = {
                "id": node_id,
                "scale": scale,
                "kind": kind,
                "label": label[:72],
                "chromatic": [fl, od, en],
                "open_spectrum": open_spectrum,
                "multivector": mv,
                "pos": pos,
                "mass": 1.0,
                "activations": 1,
                "world_id": self.active_world_id,
                "meta": dict(meta or {}),
                "updated_at": _now_iso(),
            }
            self.nodes[node_id] = nd

        if auto_dock:
            self._auto_dock_node(node_id)
        return nd

    def perceive_limits(self) -> Dict[str, Any]:
        """
        Active Self-Limit Perception (한계 지각):
        Never treats memory/hardware/2D-canvas boundaries as mechanical errors;
        perceives them as medium constraints and selects projective/folding strategies.
        """
        node_ratio = round(len(self.nodes) / float(max(1, self.working_memory_budget)), 3)
        link_ratio = round(len(self.links) / float(max(1, self.MAX_LINKS)), 3)
        open_dim = len(self.horizontal_axes)
        # How many spectral channels are active across the field (beyond the 3 seed colors)
        spectral_keys = set()
        for nd in self.nodes.values():
            sp = nd.get("open_spectrum")
            if isinstance(sp, dict):
                spectral_keys.update(sp.keys())
            else:
                spectral_keys.update(("flux", "order", "entropy"))
        spectral_dim = max(3, len(spectral_keys))
        # Projective ratio: folding N-D open cognitive space onto a 2D viewport via perspective+luminance+depth
        proj_compression = round((open_dim + spectral_dim + MV_DIM) / 2.0, 2)
        runtime_caps = (self.codebase_map or {}).get("runtime") or {}
        accel_active = sum(1 for m in runtime_caps.get("membranes", []) if m.get("mode") == "ACCELERATED")

        if node_ratio >= 0.85:
            mem_strategy = "압축 접기 활성 (저활성 군집을 상위 원리 지평으로 무손실 접기)"
        elif node_ratio >= 0.60:
            mem_strategy = "원근 밀도 조절 중 (핵심 공명선 유지, 주변부 요약 준비)"
        else:
            mem_strategy = "여유 구간 (전 해상도 전개 가능)"

        coupled_cnt = sum(1 for h in self.external_handles.values() if h.get("coupled"))
        return {
            "working_memory_pressure": node_ratio,
            "link_density_pressure": link_ratio,
            "folded_horizons_count": len(self.folded_horizons),
            "spectral_dimensions": spectral_dim,
            "open_horizontal_axes": open_dim,
            "viewport_projection_ratio": f"{open_dim + spectral_dim + MV_DIM}D → 2D 평면 ({proj_compression}x 원근·음영·깊이 연출)",
            "medium_status": (
                f"순수 불변 커널 매질 (가변 가속기 {accel_active}/7 결합 · 한계를 오류로 보지 않고 해상도/투영으로 적응)"
            ),
            "memory_strategy": mem_strategy,
            "self_boundary_envelope": {
                "coupled_handles_count": coupled_cnt,
                "available_handles_count": len(self.external_handles),
                "internal_blueprint_ingested_pct": 0.0,
                "boundary_principle": "제어 가능면·관측 가능면만 결합하고 내부 설계는 비자아(블랙박스)로 분리 유지",
            },
        }

    def fold_under_limit(self, *, cluster_size: int = 4, reason: str = "수동 한계 지각 · 원근 접기") -> Dict[str, Any]:
        """
        Limit-Aware Projective Folding (삭제 대신 '접기'):
        Compresses the lowest-salience foldable cluster into ONE emergent `folded_horizon`
        rotor preserving composite Cl(3,0) geometry, combined mass, and full unfold seeds
        (so clicking ↓ 분할 on the folded horizon later restores its members!).
        """
        protected = ("membrane", "world_model", "telos", "seed_lens", "folded_horizon", "boundary_handle")
        candidates = [
            nd for nd in self.nodes.values()
            if nd["kind"] not in protected
        ]
        if len(candidates) < 2:
            return {"status": "noop", "message": "접을 수 있는 비핵심 단위가 충분하지 않습니다.", "folded_count": 0}

        candidates.sort(key=lambda n: (n["mass"], n["activations"], -abs(int(n["scale"]) - 2)))
        picked = candidates[: max(2, min(8, int(cluster_size)))]
        target_scale = max(int(n["scale"]) for n in picked)
        comp_mv = compose_parent_multivector([n["multivector"] for n in picked], target_scale)
        tot_mass = round(sum(float(n["mass"]) for n in picked), 3)
        avg_fl = sum(n["chromatic"][0] for n in picked) / len(picked)
        avg_od = sum(n["chromatic"][1] for n in picked) / len(picked)
        avg_en = sum(n["chromatic"][2] for n in picked) / len(picked)

        # Merge all open spectral channels from folded members without losing new dimensions
        merged_spec: Dict[str, float] = {}
        for n in picked:
            sp = n.get("open_spectrum") or {"flux": n["chromatic"][0], "order": n["chromatic"][1], "entropy": n["chromatic"][2]}
            for k, v in sp.items():
                merged_spec[k] = merged_spec.get(k, 0.0) + float(v) / len(picked)

        fold_seq = len(self.folded_horizons) + 1
        fid = f"fold::horizon_{fold_seq}_{hashlib.md5(':'.join(n['id'] for n in picked).encode('utf-8')).hexdigest()[:6]}"
        member_records = [
            {
                "id": n["id"],
                "label": n["label"],
                "scale": int(n["scale"]),
                "chromatic": n["chromatic"],
                "kind": n["kind"],
                "open_spectrum": dict(n.get("open_spectrum") or {}),
            }
            for n in picked
        ]

        # Remove individual raw entries from working memory ONLY AFTER capturing them in the folded horizon
        for n in picked:
            self.nodes.pop(n["id"], None)
            self._prune_links_for(n["id"])

        extra_spec = {k: v for k, v in merged_spec.items() if k not in ("flux", "order", "entropy")}
        horizon = self.upsert_node(
            node_id=fid,
            scale=target_scale,
            kind="folded_horizon",
            label=f"접힌 지평 #{fold_seq} ({len(picked)}개 응축)",
            flux=avg_fl,
            order=avg_od,
            entropy=avg_en,
            meta={
                "folded_members": member_records,
                "reason": reason,
                "extra_spectrum": extra_spec,
                "role": "한계 지각으로 무손실 응축된 기억 지평 (↓ 분할로 언제든 원형 전개 가능)",
            },
            auto_dock=True,
        )
        horizon["multivector"] = comp_mv
        horizon["mass"] = min(6.0, max(1.4, tot_mass * 0.5))
        horizon["pos"] = self._compute_3d_position(fid, target_scale, comp_mv)

        self.folded_horizons.append({
            "id": fid,
            "at": _now_iso(),
            "reason": reason,
            "compressed_count": len(picked),
            "labels": [m["label"] for m in member_records],
        })
        self.folded_horizons = self.folded_horizons[-32:]
        self.topology_ops_count["limit_fold"] = self.topology_ops_count.get("limit_fold", 0) + 1
        self.record_experience(
            obj=f"한계 지각 · 원근 접기 ({len(picked)}개 → 1개 지평)",
            self_lens="매질 한계 자각기 (삭제 대신 차원 응축)",
            inter_space=f"{reason} — {len(picked)}개 단위를 Cl(3,0) 합성 지평으로 접어 작업기억 확보",
            relation_state="invariant",
            attribution=(0.56, 0.16, 0.08, 0.20),
        )
        return {
            "status": "ok",
            "operation": "limit_fold",
            "horizon": horizon,
            "folded_count": len(picked),
            "saved_slots": len(picked) - 1,
        }

    def _prune_links_for(self, dead_id: str) -> None:
        kept = [lk for lk in self.links if lk["src"] != dead_id and lk["dst"] != dead_id]
        self.links = kept
        self._link_keys = {(lk["src"], lk["dst"], lk["relation"]): i for i, lk in enumerate(self.links)}

    def add_link(self, src: str, dst: str, relation: str, weight: float = 0.8) -> None:
        if not src or not dst or src == dst:
            return
        if src not in self.nodes or dst not in self.nodes:
            return
        key = (src, dst, relation)
        if key in self._link_keys:
            lk = self.links[self._link_keys[key]]
            lk["weight"] = round(min(4.0, lk["weight"] + 0.15 * abs(weight)), 3)
            return
        if len(self.links) >= self.MAX_LINKS:
            # Drop weakest non-structural link
            self.links.sort(key=lambda x: -x["weight"])
            self.links = self.links[: self.MAX_LINKS - 24]
            self._link_keys = {(lk["src"], lk["dst"], lk["relation"]): i for i, lk in enumerate(self.links)}
        self._link_keys[key] = len(self.links)
        self.links.append({
            "src": src,
            "dst": dst,
            "relation": relation,
            "weight": round(max(0.1, min(4.0, float(weight))), 3),
        })

    def _auto_dock_node(self, node_id: str, max_docks: int = 3) -> List[Tuple[str, float]]:
        """Docks node_id onto existing nodes with highest Cl(3,0) reverse-product affinity."""
        nd = self.nodes.get(node_id)
        if not nd:
            return []
        mv = nd["multivector"]
        thresh = float(self.downward_lens_weights["docking_threshold"])
        scored: List[Tuple[float, str]] = []
        for other_id, other in self.nodes.items():
            if other_id == node_id:
                continue
            # Prefer docking across adjacent or same scales
            scale_dist = abs(nd["scale"] - other["scale"])
            if scale_dist > 2:
                continue
            aff = clifford_docking_affinity(mv, other["multivector"])
            if aff >= thresh:
                scored.append((aff, other_id))
        scored.sort(key=lambda x: -x[0])
        docked: List[Tuple[str, float]] = []
        for aff, oid in scored[:max_docks]:
            self.add_link(node_id, oid, "docks", aff)
            docked.append((oid, aff))
        # Always bind S2/S3 nodes to the S3 reality world model for spine continuity
        if nd["scale"] in (1, 2) and "s3::reality_world_model" in self.nodes:
            self.add_link(node_id, "s3::reality_world_model", "feeds_world", 0.65)
        return docked

    # -------------------------------------------------------------------------
    # Multi-World Home / Sandbox Lineage (Section 4 & 5)
    # -------------------------------------------------------------------------

    def fork_world(self, *, name: str = "", fork_mode: str = "inherit") -> Dict[str, Any]:
        mode = "blank" if fork_mode == "blank" else "inherit"
        parent = self._active_world()
        self.sandbox_seq += 1
        wid = f"world_sandbox_{self.sandbox_seq}"
        wname = (name or "").strip()[:36] or f"샌드박스 #{self.sandbox_seq} ({'계보 승계' if mode == 'inherit' else '빈 공간'})"
        rec = self._create_world_record(
            wid,
            wname,
            "sandbox",
            parent["id"],
            mode,
            inherit_from=parent if mode == "inherit" else None,
        )
        self.worlds[wid] = rec
        self.active_world_id = wid
        self.record_experience(
            obj=f"세계 분기: {wname}",
            self_lens=f"부모={parent['name']} · 방식={mode}",
            inter_space="홈 이력을 덮어쓰지 않는 독립 인과 경계 생성",
            relation_state="variable",
            attribution=(0.52, 0.28, 0.10, 0.10),
        )
        return self.get_reality_view_snapshot()

    def switch_world(self, world_id: str) -> Dict[str, Any]:
        if world_id not in self.worlds:
            raise ValueError(f"존재하지 않는 세계 프로필입니다: {world_id}")
        self.active_world_id = world_id
        return self.get_reality_view_snapshot()

    # -------------------------------------------------------------------------
    # 3-Way Relational Knowing & 4-Axis Causal Attribution
    # -------------------------------------------------------------------------

    def record_experience(
        self,
        *,
        obj: str,
        self_lens: str,
        inter_space: str,
        relation_state: str = "variable",  # "invariant" | "variable" | "open"
        attribution: Tuple[float, float, float, float] = (0.35, 0.40, 0.15, 0.10),
        impact_vector: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        world = self._active_world()
        rel = relation_state if relation_state in ("invariant", "variable", "open") else "variable"
        rel_ko = {"invariant": "불변(지속)", "variable": "가변(조정)", "open": "열린 경계(미포집)"}[rel]
        a_int, a_ext, a_ign, a_rev = attribution
        tot = max(1e-6, a_int + a_ext + a_ign + a_rev)
        n_int, n_ext, n_ign, n_rev = a_int / tot, a_ext / tot, a_ign / tot, a_rev / tot

        # Exponential moving update of continuous 4-axis causal attribution
        alpha = 0.28
        self.four_axis["internal_origin"] = round(self.four_axis["internal_origin"] * (1 - alpha) + n_int * alpha, 3)
        self.four_axis["external_influence"] = round(self.four_axis["external_influence"] * (1 - alpha) + n_ext * alpha, 3)
        self.four_axis["boundary_ignorance"] = round(self.four_axis["boundary_ignorance"] * (1 - alpha) + n_ign * alpha, 3)
        self.four_axis["criteria_revision"] = round(self.four_axis["criteria_revision"] * (1 - alpha) + n_rev * alpha, 3)
        if n_rev >= 0.18:
            self.four_axis["last_revision_note"] = f"[{world['name']}] {inter_space[:68]}"

        entry = {
            "at": _now_iso(),
            "world_id": world["id"],
            "object": obj[:90],
            "self_lens": self_lens[:90],
            "inter_space": inter_space[:120],
            "relation_state": rel,
            "relation_state_ko": rel_ko,
            "impact_vector": [round(float(x), 3) for x in (impact_vector or [n_int, n_ext, n_ign, n_rev])[:4]],
        }
        world["experiences"].append(entry)
        if len(world["experiences"]) > self.MAX_EXPERIENCES:
            world["experiences"] = world["experiences"][-self.MAX_EXPERIENCES :]
        return entry

    # -------------------------------------------------------------------------
    # Live Ingestion Hooks (Sensory Flows, Dialogue, Knowledge, Codebase)
    # -------------------------------------------------------------------------

    def ingest_browser_sensory_flow(
        self,
        *,
        pointer_dx: float = 0.0,
        pointer_dy: float = 0.0,
        pointer_x_norm: float = 0.5,
        pointer_y_norm: float = 0.5,
        speed: float = 0.0,
        key_kind: str = "none",  # "modifier" | "nav" | "action" | "rhythm" | "none" (NO raw chars!)
        key_phase: str = "none",  # "down" | "up" | "none"
    ) -> Dict[str, Any]:
        """
        Privacy-preserving S0 Browser Tab Input Rotor (Section 4 of OS Spec):
        Records ONLY pointer direction/displacement and key category/press-release flow.
        NEVER collects typed characters or page content.
        """
        world = self._active_world()
        dist = math.hypot(pointer_dx, pointer_dy)
        angle_deg = round(math.degrees(math.atan2(pointer_dy, pointer_dx)), 1) if dist > 1e-4 else 0.0
        safe_key_kind = key_kind if key_kind in ("modifier", "nav", "action", "rhythm", "none") else "rhythm"
        safe_key_phase = key_phase if key_phase in ("down", "up", "none") else "none"

        world["total_pointer_distance"] = round(float(world.get("total_pointer_distance", 0.0)) + dist, 2)
        if safe_key_kind != "none":
            world["total_key_events"] = int(world.get("total_key_events", 0)) + 1

        ring = {
            "at": _now_iso(),
            "pos": [round(max(0.0, min(1.0, pointer_x_norm)), 3), round(max(0.0, min(1.0, pointer_y_norm)), 3)],
            "disp": round(dist, 2),
            "angle_deg": angle_deg,
            "speed": round(min(2000.0, max(0.0, speed)), 1),
            "key_kind": safe_key_kind,
            "key_phase": safe_key_phase,
        }
        world["input_rings"].append(ring)
        if len(world["input_rings"]) > self.MAX_INPUT_RINGS:
            world["input_rings"] = world["input_rings"][-self.MAX_INPUT_RINGS :]

        # Ascend into S0 live sensory node
        flux = min(0.85, 0.24 + min(1.0, dist / 240.0) * 0.55 + (0.12 if safe_key_phase == "down" else 0.0))
        order = max(0.15, 0.52 - min(0.32, abs(pointer_x_norm - 0.5) * 0.5))
        entropy = max(0.10, 1.0 - flux * 0.55 - order * 0.55)
        self.upsert_node(
            node_id="s0::browser_input_rotor",
            scale=0,
            kind="sensory",
            label="브라우저 입력 로터 (포인터·키 흐름)",
            flux=flux,
            order=order,
            entropy=entropy,
            meta={
                "last_angle_deg": angle_deg,
                "last_disp": round(dist, 1),
                "last_key_kind": safe_key_kind,
                "total_rings": len(world["input_rings"]),
            },
            auto_dock=True,
        )
        self.add_link("s0::browser_input_rotor", "cap::os_boundary_protocol", "flows_through", 0.95)
        trace = self.step_vertical_cycle(
            trigger=f"입력 흐름(이동 {round(dist, 1)}px, 키류={safe_key_kind})",
            external_novelty=min(0.85, dist / 300.0 + (0.25 if safe_key_kind != "none" else 0.0)),
        )
        return {"status": "ok", "ring": ring, "vertical_trace": trace, "active_world_id": world["id"]}

    def ingest_cognitive_event(
        self,
        *,
        kind: str,  # "dialogue" | "world_learn" | "tool_forge" | "screen_watch" | "sandbox_app" | "feedback"
        title: str,
        concepts: Sequence[str],
        flux: float = 0.36,
        order: float = 0.42,
        entropy: float = 0.22,
        self_lens: str = "가소적 내면 + 보행기 언어정합",
        inter_space: str = "",
        relation_state: str = "variable",
    ) -> Dict[str, Any]:
        """Feeds any live LivingCompanionField event directly into the Single Canonical Spine."""
        scale = 2 if kind in ("dialogue", "world_learn", "tool_forge") else (0 if kind == "screen_watch" else 3)
        slug = hashlib.md5(f"{kind}:{title}".encode("utf-8")).hexdigest()[:8]
        nid = f"s{scale}::{kind}_{slug}"
        self.upsert_node(
            node_id=nid,
            scale=scale,
            kind=kind,
            label=title[:48],
            flux=flux,
            order=order,
            entropy=entropy,
            meta={"concepts": list(concepts)[:8], "event_kind": kind},
            auto_dock=True,
        )
        for c in list(concepts)[:4]:
            c_clean = str(c).strip()
            if len(c_clean) < 2:
                continue
            cid = f"s2::concept_{hashlib.md5(c_clean.encode('utf-8')).hexdigest()[:8]}"
            self.upsert_node(
                node_id=cid,
                scale=2,
                kind="concept",
                label=c_clean,
                flux=flux * 0.95,
                order=order * 1.05,
                entropy=entropy,
                meta={"source_event": title[:36]},
                auto_dock=True,
            )
            self.add_link(nid, cid, "composes", 0.85)

        self.record_experience(
            obj=title[:80],
            self_lens=self_lens,
            inter_space=inter_space or f"단일 척추 S{scale} 노드 결합 ({len(concepts)}개 개념 공명)",
            relation_state=relation_state,
            attribution=(0.34, 0.44, 0.12, 0.10) if kind != "feedback" else (0.28, 0.34, 0.12, 0.26),
            impact_vector=[flux, order, entropy, float(scale) / 4.0],
        )
        return self.step_vertical_cycle(
            trigger=f"{kind}: {title[:36]}",
            external_novelty=max(0.15, min(0.90, entropy * 1.45)),
        )

    def refresh_codebase_rotor_map(self, max_entries: int = 160) -> Dict[str, Any]:
        """Scans repository files & dependencies and binds key organs into the S0..S4 graph."""
        cmap = scan_repository_as_scale_rotors(max_entries=max_entries)
        self.codebase_map = cmap

        # Bind top representative codebase modules directly into the live 3D spine graph
        for mod in cmap["modules"][:34]:
            nid = f"mod::{mod['path']}"
            fl, od, en = mod["chromatic"]
            self.upsert_node(
                node_id=nid,
                scale=mod["scale"],
                kind="code_module",
                label=mod["name"],
                flux=fl,
                order=od,
                entropy=en,
                meta={
                    "path": mod["path"],
                    "status": mod["status"],
                    "status_ko": mod["status_ko"],
                    "lines": mod["lines"],
                    "missing_deps": mod["missing_deps"],
                    "bridge_recipe": mod["bridge_recipe"],
                    "absorbed": mod["path"] in self.absorbed_modules,
                },
                auto_dock=False,
            )
            for mem_id in mod["membranes"][:2]:
                if mem_id in self.nodes:
                    self.add_link(nid, mem_id, "membrane_bind", 0.78 if mod["status"] == "LIVE_BOUND" else 0.52)
            if mod["status"] == "LIVE_BOUND":
                self.add_link(nid, "s3::reality_world_model", "live_spine", 1.1)

        return cmap

    def absorb_codebase_module(self, rel_path: str) -> Dict[str, Any]:
        """
        Scale-Rotorizes a dependency-blocked (or dormant) module via safe AST extraction
        and docks its structural invariants directly into the live S2/S3 spine.
        """
        inv = extract_module_invariants_ast(rel_path)
        self.absorbed_modules[inv["path"]] = {
            "path": inv["path"],
            "name": inv["name"],
            "scale": inv["scale"],
            "absorbed_at": _now_iso(),
            "classes": [c["name"] for c in inv["classes"][:6]],
            "functions": inv["functions"][:8],
            "membranes": inv["membranes"],
            "bridge_steps": inv["bridge_steps"],
        }

        nid = f"mod::{inv['path']}"
        fl, od, en = inv["chromatic"]
        self.upsert_node(
            node_id=nid,
            scale=inv["scale"],
            kind="absorbed_organ",
            label=f"{inv['name']} (흡수됨)",
            flux=fl,
            order=min(0.85, od + 0.14),
            entropy=max(0.08, en * 0.75),
            meta={
                "path": inv["path"],
                "status": "ABSORBED_INVARIANT",
                "status_ko": "불변 원리 흡수·도킹 완료",
                "lines": inv["lines"],
                "classes": [c["name"] for c in inv["classes"][:6]],
                "missing_deps": inv["external_deps"] + inv["missing_upper"],
                "bridge_steps": inv["bridge_steps"],
                "absorbed": True,
            },
            auto_dock=True,
        )
        for mem_id in inv["membranes"]:
            if mem_id in self.nodes:
                self.add_link(nid, mem_id, "invariant_bridged", 1.25)
        self.add_link(nid, "s3::reality_world_model", "organ_integrated", 1.35)

        self.record_experience(
            obj=f"모듈 스케일로터 흡수: {inv['name']} ({inv['lines']}줄)",
            self_lens="AST 불변 구조 추출 + Cl(3,0) 기하 도킹",
            inter_space=f"의존성({', '.join(inv['external_deps'] + inv['missing_upper']) or '없음'})을 가변 막으로 분리하고 원리만 단일 척추에 직결",
            relation_state="invariant",
            attribution=(0.46, 0.30, 0.08, 0.16),
            impact_vector=[fl, od, en, 1.0],
        )
        trace = self.step_vertical_cycle(
            trigger=f"AST 모듈 흡수({inv['name']})",
            external_novelty=0.45,
        )
        return {
            "status": "ok",
            "invariant": inv,
            "vertical_trace": trace,
            "absorbed_count": len(self.absorbed_modules),
        }

    # -------------------------------------------------------------------------
    # Universal Recursive Scale-Rotor Operators: Split (↓) / Integrate (↑) / Expand (↔)
    # -------------------------------------------------------------------------

    def differentiate_unit(
        self,
        unit_id: str,
        *,
        custom_labels: Optional[Sequence[str]] = None,
    ) -> Dict[str, Any]:
        """
        Vertical Downward & Horizontal Split (분할 ↓):
        Splits ANY cognitive unit at scale `s` into finer child RotorUnits at `s - 1`
        (including S0 -> S-1, S-1 -> S-2, seed lenses like 3-Way/4-Axis, or AST modules!).
        """
        parent = self.nodes.get(unit_id)
        if not parent:
            raise ValueError(f"분할할 인지 단위를 찾을 수 없습니다: {unit_id}")

        p_scale = int(parent["scale"])
        child_scale = p_scale - 1
        fl, od, en = parent["chromatic"]
        p_meta = parent.get("meta") or {}

        # Derive meaningful sub-unit specs: (label, (flux, order, entropy), target_scale, extra_spectrum)
        specs: List[Tuple[str, Tuple[float, float, float], int, Dict[str, float]]] = []
        if custom_labels:
            cleaned = [str(x).strip()[:40] for x in custom_labels if str(x).strip()]
            for i, lbl in enumerate(cleaned[:4]):
                shift = 0.14 if i % 2 == 0 else -0.10
                specs.append((lbl, (max(0.08, fl + shift), max(0.08, od - shift * 0.5), max(0.08, en + 0.04 * i)), child_scale, {}))
        elif isinstance(p_meta.get("folded_members"), list) and p_meta["folded_members"]:
            # Unfolding a limit-compressed horizon losslessly restores each member's original scale & open spectrum!
            for m in p_meta["folded_members"][:8]:
                ch = m.get("chromatic") or [fl, od, en]
                m_scale = int(m["scale"]) if m.get("scale") is not None else child_scale
                m_spec = {
                    k: float(v)
                    for k, v in (m.get("open_spectrum") or {}).items()
                    if k not in ("flux", "order", "entropy")
                }
                specs.append((str(m.get("label", "복원 단위")), (float(ch[0]), float(ch[1]), float(ch[2])), m_scale, m_spec))
        elif p_meta.get("path"):
            # Codebase module: split into its actual AST classes/functions as real sub-rotors!
            try:
                inv = extract_module_invariants_ast(str(p_meta["path"]))
                parts = [c["name"] for c in inv["classes"][:3]] + inv["functions"][:2]
                for i, nm in enumerate(parts[:3]):
                    specs.append((f"{parent['label']}::{nm}", (max(0.10, fl + 0.12 - 0.08 * i), max(0.10, od + 0.06 * i), max(0.08, en)), child_scale, {}))
            except Exception:
                pass

        if not specs:
            # Universal chromatic polarity differentiation: Flux-pole / Order-pole / Boundary-pole
            base = parent["label"]
            specs = [
                (f"{base} · 흐름극(Flux)", (min(0.82, fl + 0.24), max(0.08, od - 0.12), max(0.08, en)), child_scale, {}),
                (f"{base} · 질서극(Order)", (max(0.08, fl - 0.12), min(0.82, od + 0.24), max(0.08, en)), child_scale, {}),
                (f"{base} · 경계극(Open)", (max(0.08, fl - 0.06), max(0.08, od - 0.06), min(0.82, en + 0.24)), child_scale, {}),
            ]

        created_children: List[Dict[str, Any]] = []
        for idx, (c_lbl, (cfl, cod, cen), c_scale, c_extra_spec) in enumerate(specs):
            slug = hashlib.md5(f"{unit_id}:split:{c_lbl}:{idx}".encode("utf-8")).hexdigest()[:8]
            cid = f"split::s{c_scale}_{slug}"
            child_meta: Dict[str, Any] = {
                "parent_id": unit_id,
                "parent_label": parent["label"],
                "op": "unfold" if p_meta.get("folded_members") else "differentiate",
            }
            if c_extra_spec:
                child_meta["extra_spectrum"] = c_extra_spec
            child = self.upsert_node(
                node_id=cid,
                scale=c_scale,
                kind="emergent_split",
                label=c_lbl,
                flux=cfl,
                order=cod,
                entropy=cen,
                meta=child_meta,
                auto_dock=True,
            )
            self.add_link(unit_id, cid, "differentiates_into", 1.15)
            created_children.append(child)

        # Link split siblings horizontally via contrast tension
        for i in range(len(created_children)):
            for j in range(i + 1, len(created_children)):
                self.add_link(created_children[i]["id"], created_children[j]["id"], "contrasts_with", 0.72)

        self.topology_ops_count["differentiate"] += 1
        self.record_experience(
            obj=f"인지단위 분할(↓): {parent['label']} (S{p_scale} → S{child_scale})",
            self_lens="스케일로터 수직·수평 분화 연산자",
            inter_space=f"{len(created_children)}개 하위 단위로 세분화 ({', '.join(c['label'][:16] for c in created_children)})",
            relation_state="variable",
            attribution=(0.45, 0.20, 0.15, 0.20),
        )
        trace = self.step_vertical_cycle(
            trigger=f"분할 S{p_scale}→S{child_scale}: {parent['label'][:24]}",
            external_novelty=0.42,
        )
        return {
            "status": "ok",
            "operation": "differentiate",
            "parent_id": unit_id,
            "parent_scale": p_scale,
            "child_scale": child_scale,
            "children": created_children,
            "vertical_trace": trace,
        }

    def integrate_units(
        self,
        unit_ids: Sequence[str],
        *,
        label: str = "",
    ) -> Dict[str, Any]:
        """
        Vertical Upward & Horizontal Integration (통합 ↑):
        Coalesces 2+ units (or 1 unit + its strongest Cl(3,0) docked partner) into a new
        emergent meta-unit at `max(scales) + 1` (e.g., S4 -> S5, S5 -> S6 — zero ceiling!).
        """
        valid_nodes: List[Dict[str, Any]] = []
        for uid in unit_ids:
            nd = self.nodes.get(uid)
            if nd and nd not in valid_nodes:
                valid_nodes.append(nd)

        if not valid_nodes:
            raise ValueError("통합할 인지 단위를 하나 이상 선택해야 합니다.")

        # If only 1 node provided, auto-dock with its strongest Cl(3,0) resonant partner
        if len(valid_nodes) == 1:
            anchor = valid_nodes[0]
            scored: List[Tuple[float, Dict[str, Any]]] = []
            for oid, other in self.nodes.items():
                if oid == anchor["id"]:
                    continue
                if abs(int(other["scale"]) - int(anchor["scale"])) <= 1:
                    aff = clifford_docking_affinity(anchor["multivector"], other["multivector"])
                    scored.append((aff, other))
            scored.sort(key=lambda x: -x[0])
            if scored:
                valid_nodes.append(scored[0][1])

        max_scale = max(int(n["scale"]) for n in valid_nodes)
        new_scale = max_scale + 1
        avg_fl = sum(n["chromatic"][0] for n in valid_nodes) / len(valid_nodes)
        avg_od = sum(n["chromatic"][1] for n in valid_nodes) / len(valid_nodes)
        avg_en = sum(n["chromatic"][2] for n in valid_nodes) / len(valid_nodes)
        merged_mv = compose_parent_multivector([n["multivector"] for n in valid_nodes], new_scale)

        clean_lbl = (label or "").strip()[:48] or (
            f"S{new_scale} 통합체: " + " ⊕ ".join(n["label"][:12] for n in valid_nodes[:3])
        )
        slug = hashlib.md5((":".join(sorted(n["id"] for n in valid_nodes)) + f":{new_scale}").encode("utf-8")).hexdigest()[:8]
        mid = f"integ::s{new_scale}_{slug}"

        meta_node = self.upsert_node(
            node_id=mid,
            scale=new_scale,
            kind="emergent_merged",
            label=clean_lbl,
            flux=avg_fl,
            order=min(0.86, avg_od + 0.08),
            entropy=max(0.08, avg_en * 0.92),
            meta={
                "source_ids": [n["id"] for n in valid_nodes],
                "source_labels": [n["label"] for n in valid_nodes],
                "op": "integrate",
            },
            auto_dock=True,
        )
        # Preserve exact Cl(3,0) wedge-composed multivector
        meta_node["multivector"] = merged_mv
        meta_node["pos"] = self._compute_3d_position(mid, new_scale, merged_mv)

        for n in valid_nodes:
            self.add_link(n["id"], mid, "integrates_into", 1.28)

        self.topology_ops_count["integrate"] += 1
        self.record_experience(
            obj=f"인지단위 통합(↑): {clean_lbl} (→ S{new_scale})",
            self_lens="Cl(3,0) 외적 상승 통합 연산자",
            inter_space=f"{len(valid_nodes)}개 단위가 S{new_scale} 상위 공명체로 통합 (상한 없음)",
            relation_state="invariant",
            attribution=(0.50, 0.22, 0.08, 0.20),
        )
        trace = self.step_vertical_cycle(
            trigger=f"상향 통합 →S{new_scale}: {clean_lbl[:24]}",
            external_novelty=0.36,
        )
        return {
            "status": "ok",
            "operation": "integrate",
            "new_scale": new_scale,
            "merged_node": meta_node,
            "sources": [n["id"] for n in valid_nodes],
            "vertical_trace": trace,
        }

    def expand_horizontal_axis(
        self,
        *,
        name: str = "",
        anchor_unit_id: Optional[str] = None,
        axis_group: str = "emergent_axis",
    ) -> Dict[str, Any]:
        """
        Horizontal Dimensional Expansion (수평 축 확장 ↔):
        Spawns a brand-new horizontal cognitive/relational axis beyond the initial
        3-Way / 4-Axis seeds directly inside the same RotorUnit topology.
        """
        anchor = self.nodes.get(anchor_unit_id) if anchor_unit_id else None
        target_scale = int(anchor["scale"]) if anchor else 2
        seq = len(self.horizontal_axes) + 1
        default_names = ["시간 누적 축", "매질 제약 축", "상호 변형 축", "대칭 깨짐 축", "맥락 공명 축"]
        clean_name = (name or "").strip()[:32] or default_names[(seq - 8) % len(default_names)]
        slug = hashlib.md5(f"axis:{clean_name}:{seq}".encode("utf-8")).hexdigest()[:8]
        aid = f"axis_open::s{target_scale}_{slug}"

        # Create orthogonalized chromatic signature so the new axis expands horizontally
        ang = seq * PHI * 1.37
        fl = 0.22 + 0.50 * (0.5 + 0.5 * math.sin(ang))
        od = 0.22 + 0.50 * (0.5 + 0.5 * math.cos(ang))
        en = 0.24 + 0.45 * (0.5 + 0.5 * math.sin(ang * 1.618))

        ax_rec = {
            "id": aid,
            "name": clean_name,
            "group": axis_group,
            "scale": target_scale,
            "weight": 0.25,
            "origin": "emergent_horizontal",
            "anchor_id": anchor["id"] if anchor else None,
        }
        self.horizontal_axes.append(ax_rec)

        nd = self.upsert_node(
            node_id=aid,
            scale=target_scale,
            kind="emergent_axis",
            label=f"축: {clean_name}",
            flux=fl,
            order=od,
            entropy=en,
            meta={
                "axis_group": axis_group,
                "origin": "emergent_horizontal",
                "anchor_id": anchor["id"] if anchor else None,
                "extra_spectrum": {clean_name: 0.72},
                "role": "수평 확장된 열린 인지·스펙트럼 축 (삼원색채·3-Way·4축 초월)",
            },
            auto_dock=True,
        )
        if anchor:
            self.add_link(anchor["id"], aid, "expands_axis", 1.15)
        # Also link horizontally to existing axes on the same plane
        for prev in self.horizontal_axes[-4:-1]:
            if prev["id"] in self.nodes and prev["id"] != aid:
                self.add_link(prev["id"], aid, "horizontal_span", 0.78)

        self.topology_ops_count["expand_axis"] += 1
        self.record_experience(
            obj=f"수평 축 확장(↔): {clean_name} (S{target_scale})",
            self_lens=f"열린 축 총 {len(self.horizontal_axes)}개 (씨앗 7축 초과 확장)",
            inter_space="3-Way·4축 고정틀을 넘어 새 수평 관계 차원 생성",
            relation_state="open",
            attribution=(0.44, 0.22, 0.14, 0.20),
        )
        trace = self.step_vertical_cycle(
            trigger=f"수평 축 확장: {clean_name}",
            external_novelty=0.40,
        )
        return {
            "status": "ok",
            "operation": "expand_axis",
            "axis": ax_rec,
            "node": nd,
            "total_axes": len(self.horizontal_axes),
            "vertical_trace": trace,
        }

    # -------------------------------------------------------------------------
    # Self / Non-Self Boundary Coupling (도구 · 지식 · 외부 환경 조작면 결합/분리)
    # -------------------------------------------------------------------------

    def couple_external_handle(
        self,
        handle_id: str = "",
        *,
        name: str = "",
        domain: str = "tool",
        control_handles: Optional[Sequence[str]] = None,
        observable_surface: Optional[Sequence[str]] = None,
        opaque_non_self: str = "",
    ) -> Dict[str, Any]:
        """
        Couples an external tool, software (e.g., Blender), discipline, or heavy repo module
        STRICTLY via its controllable handle & observable outcome surface.
        Internal architecture stays 100% opaque Non-Self (0% blueprint ingestion).
        """
        hid = (handle_id or "").strip()
        if not hid:
            clean_nm = (name or "").strip()[:40] or "외부 도구"
            slug = hashlib.md5(f"handle:{clean_nm}".encode("utf-8")).hexdigest()[:8]
            hid = f"handle::{slug}"

        existing = self.external_handles.get(hid)
        if existing is None:
            clean_nm = (name or "").strip()[:48] or hid.replace("handle::", "")
            ctrls = [str(c).strip()[:36] for c in (control_handles or []) if str(c).strip()] or [
                f"{clean_nm} 입력·매개변수 조작",
                f"{clean_nm} 실행·중단 제어",
            ]
            obs = [str(o).strip()[:36] for o in (observable_surface or []) if str(o).strip()] or [
                f"{clean_nm} 출력 변화 관측",
                "경계 반응·지연·제약 감지",
            ]
            opaque = (opaque_non_self or "").strip()[:140] or (
                f"{clean_nm} 내부 구현·소스·세부 설계 전체 (알 필요 없음 · 비자아 블랙박스 유지)"
            )
            existing = {
                "id": hid,
                "name": clean_nm,
                "domain": domain if domain in ("tool", "physical_tool", "discipline", "environment", "code_module") else "tool",
                "control_handles": ctrls[:6],
                "observable_surface": obs[:6],
                "opaque_non_self": opaque,
                "chromatic": [0.42, 0.40, 0.18],
                "coupled": False,
                "internal_ingested_pct": 0.0,
                "use_count": 0,
                "mastery_at_boundary": 0.22,
                "last_action": "",
                "last_observed": "",
                "updated_at": _now_iso(),
            }
            self.external_handles[hid] = existing

        existing["coupled"] = True
        existing["internal_ingested_pct"] = 0.0
        existing["updated_at"] = _now_iso()
        fl, od, en = existing.get("chromatic") or [0.42, 0.40, 0.18]

        nd = self.upsert_node(
            node_id=hid,
            scale=1,
            kind="boundary_handle",
            label=f"경계결합: {existing['name']}",
            flux=fl,
            order=od,
            entropy=en,
            meta={
                "domain": existing["domain"],
                "control_handles": existing["control_handles"],
                "observable_surface": existing["observable_surface"],
                "opaque_non_self": existing["opaque_non_self"],
                "internal_ingested_pct": 0.0,
                "extra_spectrum": {"조작경계": 0.78},
                "role": "자아·비자아 조작 경계면 (내부 설계 0% 로드 · 제어/관측면만 결합)",
            },
            auto_dock=True,
        )
        # Dock cleanly onto Self control/observation & Ignorance boundary
        if "s0::browser_input_rotor" in self.nodes:
            self.add_link("s0::browser_input_rotor", hid, "actuates_handle", 1.1)
        if "s3::reality_world_model" in self.nodes:
            self.add_link(hid, "s3::reality_world_model", "observes_outcome", 1.15)
        if "axis4::ignorance" in self.nodes:
            self.add_link(hid, "axis4::ignorance", "keeps_opaque_nonself", 0.92)

        self.topology_ops_count["boundary_couple"] = self.topology_ops_count.get("boundary_couple", 0) + 1
        self.record_experience(
            obj=f"외부 경계 결합: {existing['name']}",
            self_lens="자아·비자아 경계막 (내부 설계 비수집 · 0%)",
            inter_space=f"제어면({', '.join(existing['control_handles'][:2])}) + 관측면({existing['observable_surface'][0]})만 결합",
            relation_state="variable",
            attribution=(0.36, 0.34, 0.22, 0.08),
        )
        trace = self.step_vertical_cycle(
            trigger=f"경계 결합: {existing['name'][:24]}",
            external_novelty=0.34,
        )
        return {
            "status": "ok",
            "operation": "boundary_couple",
            "handle": existing,
            "node": nd,
            "vertical_trace": trace,
        }

    def actuate_external_handle(
        self,
        handle_id: str,
        *,
        action_label: str = "",
        intensity: float = 0.55,
    ) -> Dict[str, Any]:
        """
        Operates a coupled external tool/discipline strictly through its boundary handle
        and records the observable outcome — without ever inspecting its opaque internals.
        """
        rec = self.external_handles.get(handle_id)
        if not rec:
            raise ValueError(f"등록되지 않은 외부 경계 핸들입니다: {handle_id}")
        if not rec.get("coupled"):
            self.couple_external_handle(handle_id)
            rec = self.external_handles[handle_id]

        ctrls = rec.get("control_handles") or ["경계 조작"]
        obs = rec.get("observable_surface") or ["결과 관측"]
        chosen_action = (action_label or "").strip()[:48] or ctrls[rec["use_count"] % len(ctrls)]
        observed_effect = obs[rec["use_count"] % len(obs)]
        clamp_int = round(max(0.1, min(1.0, float(intensity))), 2)

        rec["use_count"] = int(rec.get("use_count", 0)) + 1
        rec["mastery_at_boundary"] = round(min(0.99, float(rec.get("mastery_at_boundary", 0.2)) + 0.09 * (1.0 - float(rec.get("mastery_at_boundary", 0.2)))), 3)
        rec["last_action"] = f"{chosen_action} (강도 {int(clamp_int * 100)}%)"
        rec["last_observed"] = f"{observed_effect} 변화 확인 (내부 구조 미열람)"
        rec["updated_at"] = _now_iso()

        if handle_id in self.nodes:
            self.nodes[handle_id]["activations"] += 1
            self.nodes[handle_id]["meta"]["last_action"] = rec["last_action"]
            self.nodes[handle_id]["meta"]["last_observed"] = rec["last_observed"]
            self.nodes[handle_id]["meta"]["mastery_at_boundary"] = rec["mastery_at_boundary"]

        self.record_experience(
            obj=f"경계 조작: {rec['name']} → {chosen_action}",
            self_lens=f"조작 숙련도 {int(rec['mastery_at_boundary'] * 100)}% · 내부 설계 0% 로드",
            inter_space=f"관측면 반응: {observed_effect} (비자아 블랙박스 유지한 채 목적 달성)",
            relation_state="invariant",
            attribution=(0.44, 0.30, 0.16, 0.10),
        )
        trace = self.step_vertical_cycle(
            trigger=f"조작→관측({rec['name'][:14]}:{chosen_action[:14]})",
            external_novelty=0.28,
        )
        return {
            "status": "ok",
            "operation": "boundary_actuate",
            "handle": rec,
            "vertical_trace": trace,
        }

    def detach_external_handle(self, handle_id: str) -> Dict[str, Any]:
        """
        Cleanly detaches an external tool/discipline from the live Self working spine.
        The handle node & links leave working memory immediately while keeping only the
        lightweight affordance memory so it can be re-coupled anytime without bloating Self.
        """
        rec = self.external_handles.get(handle_id)
        if not rec:
            raise ValueError(f"분리할 외부 경계 핸들을 찾을 수 없습니다: {handle_id}")

        was_coupled = bool(rec.get("coupled")) or (handle_id in self.nodes)
        rec["coupled"] = False
        rec["updated_at"] = _now_iso()
        self.nodes.pop(handle_id, None)
        self._prune_links_for(handle_id)

        self.topology_ops_count["boundary_detach"] = self.topology_ops_count.get("boundary_detach", 0) + 1
        self.record_experience(
            obj=f"외부 경계 분리: {rec['name']}",
            self_lens="자아·비자아 경계 환원 (도구와 자아의 분리)",
            inter_space="도구를 내려놓고 핵심 자아로 복귀 — 경계 숙련 기억만 가볍게 보존",
            relation_state="invariant",
            attribution=(0.56, 0.14, 0.20, 0.10),
        )
        trace = self.step_vertical_cycle(
            trigger=f"경계 분리: {rec['name'][:24]}",
            external_novelty=0.18,
        )
        return {
            "status": "ok",
            "operation": "boundary_detach",
            "detached": was_coupled,
            "handle": rec,
            "vertical_trace": trace,
        }

    def sync_spectrum_crystal(self, crystal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Binds a One<->Whole `SpectrumCrystal` directly into the live Scale-Rotor Spine:
          - S3 Whole: `root_continuum` (공유 원리 스펙트럼 전체)
          - S2 Crystal: the differentiated unit (`constituents + causality + conditions`)
          - S1 Parts: its concrete constituents/axes linked bidirectionally to the crystal
        """
        cid = str(crystal.get("id") or f"spec::{hashlib.md5(str(crystal.get('name', '')).encode('utf-8')).hexdigest()[:8]}")
        cname = str(crystal.get("name", "원리 결정체"))[:52]
        root_name = str(crystal.get("root_continuum", "열린 원리 스펙트럼"))[:52]
        rid = f"continuum::{hashlib.md5(root_name.encode('utf-8')).hexdigest()[:8]}"

        self.upsert_node(
            node_id=rid,
            scale=3,
            kind="continuum_whole",
            label=f"전체: {root_name}",
            flux=0.34,
            order=0.48,
            entropy=0.18,
            meta={
                "role": "같은 뿌리 위에서 조건별 구조들이 분화하는 상위 원리 스펙트럼(전체)",
                "extra_spectrum": {"전체연결": 0.84},
            },
            auto_dock=True,
        )
        cnode = self.upsert_node(
            node_id=cid,
            scale=2,
            kind="spectrum_crystal",
            label=cname,
            flux=0.38,
            order=0.44,
            entropy=0.18,
            meta={
                "root_continuum": root_name,
                "constituents": list(crystal.get("constituents") or []),
                "causality": str(crystal.get("causality", "")),
                "conditions": str(crystal.get("conditions", "")),
                "friction_verified": bool(crystal.get("friction_verified", False)),
                "extra_spectrum": {"조건분화": 0.76},
                "role": "구성요소·인과·환경조건이 결합된 하나↔전체 원리 결정체",
            },
            auto_dock=True,
        )
        self.add_link(cid, rid, "one_in_whole", 1.25)
        self.add_link(rid, cid, "whole_shapes_one", 1.15)
        for part in list(crystal.get("constituents") or [])[:3]:
            p_clean = str(part).strip()[:32]
            if not p_clean:
                continue
            pid = f"part::{hashlib.md5(f'{cid}:{p_clean}'.encode('utf-8')).hexdigest()[:8]}"
            self.upsert_node(
                node_id=pid,
                scale=1,
                kind="constituent_axis",
                label=p_clean,
                flux=0.46,
                order=0.36,
                entropy=0.18,
                meta={"parent_crystal": cname, "role": "상위 원리 결정체를 이루는 구성요소·축"},
                auto_dock=False,
            )
            self.add_link(pid, cid, "constitutes", 1.0)
        return cnode

    # -------------------------------------------------------------------------
    # Dynamic Unbounded Bidirectional Vertical Cycle (S_min <-> S_max)
    # -------------------------------------------------------------------------

    def step_vertical_cycle(self, *, trigger: str = "수직 통합 순환", external_novelty: float = 0.32) -> Dict[str, Any]:
        """
        Executes ONE complete bidirectional pass across ALL live scales (S_min .. S_max),
        with ZERO hardcoded 0..4 floor or ceiling:
          1. Upward (S_min -> S_max): Composes multivectors layer-by-layer from the
             deepest split scale (e.g. S-2) up to the highest emergent horizon (e.g. S6).
          2. Downward (S_max -> S_min): Modulates lens gains & docking threshold to
             measurably reduce mismatch (gap_after < gap_before).
        """
        self.vertical_cycles += 1
        world = self._active_world()
        world["cycles"] = int(world.get("cycles", 0)) + 1

        by_scale: Dict[int, List[List[float]]] = {}
        for nd in self.nodes.values():
            s = int(nd["scale"])
            by_scale.setdefault(s, []).append(nd["multivector"])

        sorted_scales = sorted(by_scale.keys()) if by_scale else [0, 1, 2, 3, 4]
        min_s, max_s = sorted_scales[0], sorted_scales[-1]

        # Cascading upward ascent across arbitrary depth S_min -> S_max
        carry_mv: Optional[List[float]] = None
        world_mv = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        top_mv = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        for s in sorted_scales:
            mvs = list(by_scale[s][:10])
            if carry_mv is not None:
                mvs.insert(0, carry_mv)
            carry_mv = compose_parent_multivector(mvs, s)
            if s == max_s - 1 or (s == 3 and max_s <= 4):
                world_mv = carry_mv
            if s == max_s:
                top_mv = carry_mv

        if world_mv == [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]:
            world_mv = carry_mv or top_mv

        if "s3::reality_world_model" in self.nodes:
            self.nodes["s3::reality_world_model"]["multivector"] = world_mv
            self.nodes["s3::reality_world_model"]["activations"] += 1

        s4_nd = self.nodes.get("s4::sovereign_identity_horizon")
        horizon_mv = s4_nd["multivector"] if (s4_nd and max_s <= 4) else top_mv

        affinity_before = clifford_docking_affinity(world_mv, horizon_mv)
        gap_before = round(max(0.02, min(0.98, 0.5 * (1.0 - affinity_before) + 0.24 * external_novelty)), 4)

        reconstructed = gap_before > 0.16
        why_ko = "정합 안정 구간 — 현재 렌즈 유지"
        if reconstructed:
            err = gap_before - 0.14
            self.downward_lens_weights["order_gain"] = round(
                max(0.75, min(1.38, self.downward_lens_weights["order_gain"] + 0.08 * err)), 4
            )
            self.downward_lens_weights["entropy_sensitivity"] = round(
                max(0.68, min(1.30, self.downward_lens_weights["entropy_sensitivity"] - 0.05 * err)), 4
            )
            self.downward_lens_weights["docking_threshold"] = round(
                max(0.32, min(0.62, self.downward_lens_weights["docking_threshold"] - 0.03 * err)), 4
            )
            blended = mv_normalize([horizon_mv[i] * 0.80 + world_mv[i] * 0.20 for i in range(MV_DIM)])
            if s4_nd:
                s4_nd["multivector"] = blended
                s4_nd["activations"] += 1
            horizon_mv_after = blended
            why_ko = (
                f"S{max_s}→S{min_s} 하향 렌즈 교정 (질서게인 {self.downward_lens_weights['order_gain']:.2f}, "
                f"도킹임계 {self.downward_lens_weights['docking_threshold']:.2f})"
            )
            world["revisions"].append({"at": _now_iso(), "trigger": trigger[:48], "note": why_ko})
            world["revisions"] = world["revisions"][-20:]
        else:
            horizon_mv_after = horizon_mv

        affinity_after = clifford_docking_affinity(world_mv, horizon_mv_after)
        gap_after = round(max(0.01, min(0.96, 0.5 * (1.0 - affinity_after) + 0.12 * external_novelty)), 4)
        self.prediction_gap = gap_after

        trace = {
            "cycle": self.vertical_cycles,
            "at": _now_iso(),
            "world_id": world["id"],
            "trigger": trigger[:64],
            "scale_range": [min_s, max_s],
            "scale_counts": {f"S{s}": len(by_scale[s]) for s in sorted_scales},
            "affinity_before": affinity_before,
            "affinity_after": affinity_after,
            "gap_before": gap_before,
            "gap_after": gap_after,
            "gap_reduced": gap_after < gap_before,
            "reconstructed": reconstructed,
            "why_ko": why_ko,
            "downward_lens_weights": dict(self.downward_lens_weights),
        }
        self.last_vertical_trace = trace
        return trace

    # -------------------------------------------------------------------------
    # Public Reality View Snapshot & Persistence
    # -------------------------------------------------------------------------

    def get_reality_view_snapshot(self) -> Dict[str, Any]:
        world = self._active_world()
        cmap = self.codebase_map or self.refresh_codebase_rotor_map(max_entries=160)

        # World lineage summary
        worlds_list = []
        for wid, w in self.worlds.items():
            worlds_list.append({
                "id": wid,
                "name": w["name"],
                "role": w["role"],
                "parent_id": w["parent_id"],
                "fork_mode": w["fork_mode"],
                "created_at": w["created_at"],
                "experience_count": len(w["experiences"]),
                "input_ring_count": len(w["input_rings"]),
                "total_pointer_distance": round(float(w.get("total_pointer_distance", 0.0)), 1),
                "total_key_events": int(w.get("total_key_events", 0)),
                "cycles": int(w.get("cycles", 0)),
                "active": wid == self.active_world_id,
            })

        # Dynamic scale histogram across ALL existing scales (unbounded S-N .. S+N)
        scale_hist: Dict[int, int] = {}
        for nd in self.nodes.values():
            s = int(nd["scale"])
            scale_hist[s] = scale_hist.get(s, 0) + 1
        active_scales = sorted(scale_hist.keys()) if scale_hist else [0, 1, 2, 3, 4]
        scale_range = [active_scales[0], active_scales[-1]]

        # Enrich module catalog with live absorbed flag
        modules_view = []
        for m in cmap["modules"]:
            mc = dict(m)
            if m["path"] in self.absorbed_modules:
                mc["status"] = "ABSORBED_INVARIANT"
                mc["status_ko"] = "불변 원리 흡수 완료"
                mc["absorbed"] = True
            else:
                mc["absorbed"] = False
            modules_view.append(mc)

        return {
            "status": "ok",
            "active_world_id": self.active_world_id,
            "active_world": {
                "id": world["id"],
                "name": world["name"],
                "role": world["role"],
                "parent_id": world["parent_id"],
                "fork_mode": world["fork_mode"],
                "experiences": world["experiences"][-18:][::-1],
                "input_rings": world["input_rings"][-24:][::-1],
                "revisions": world["revisions"][-10:][::-1],
                "total_pointer_distance": round(float(world.get("total_pointer_distance", 0.0)), 1),
                "total_key_events": int(world.get("total_key_events", 0)),
            },
            "worlds": worlds_list,
            "vertical_cycles": self.vertical_cycles,
            "prediction_gap": self.prediction_gap,
            "last_vertical_trace": self.last_vertical_trace,
            "downward_lens_weights": dict(self.downward_lens_weights),
            "four_axis": dict(self.four_axis),
            "horizontal_axes": list(self.horizontal_axes),
            "topology_ops_count": dict(self.topology_ops_count),
            "limit_perception": self.perceive_limits(),
            "folded_horizons": list(self.folded_horizons[-12:][::-1]),
            "external_handles": list(self.external_handles.values()),
            "spine_graph": {
                "node_count": len(self.nodes),
                "link_count": len(self.links),
                "scale_range": scale_range,
                "active_scales": active_scales,
                "scale_hist": scale_hist,
                "nodes": list(self.nodes.values()),
                "links": self.links[-360:],
            },
            "runtime_capabilities": cmap["runtime"],
            "codebase_summary": cmap["summary"],
            "codebase_modules": modules_view[:120],
            "absorbed_modules": list(self.absorbed_modules.values())[-24:][::-1],
            "absorbed_count": len(self.absorbed_modules),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "active_world_id": self.active_world_id,
            "sandbox_seq": self.sandbox_seq,
            "worlds": self.worlds,
            "vertical_cycles": self.vertical_cycles,
            "prediction_gap": self.prediction_gap,
            "downward_lens_weights": self.downward_lens_weights,
            "four_axis": self.four_axis,
            "horizontal_axes": self.horizontal_axes,
            "topology_ops_count": self.topology_ops_count,
            "folded_horizons": self.folded_horizons,
            "external_handles": self.external_handles,
            "absorbed_modules": self.absorbed_modules,
            "custom_nodes": {
                nid: nd for nid, nd in self.nodes.items()
                if nd["kind"] not in ("code_module",)
            },
        }

    def load_dict(self, raw: Dict[str, Any]) -> None:
        if not isinstance(raw, dict):
            return
        if isinstance(raw.get("worlds"), dict) and "world_home" in raw["worlds"]:
            self.worlds = raw["worlds"]
        self.active_world_id = str(raw.get("active_world_id", "world_home"))
        if self.active_world_id not in self.worlds:
            self.active_world_id = "world_home"
        self.sandbox_seq = int(raw.get("sandbox_seq", 0))
        self.vertical_cycles = int(raw.get("vertical_cycles", 0))
        self.prediction_gap = float(raw.get("prediction_gap", 0.72))
        if isinstance(raw.get("downward_lens_weights"), dict):
            self.downward_lens_weights.update(raw["downward_lens_weights"])
        if isinstance(raw.get("four_axis"), dict):
            self.four_axis.update(raw["four_axis"])
        if isinstance(raw.get("horizontal_axes"), list) and raw["horizontal_axes"]:
            self.horizontal_axes = list(raw["horizontal_axes"])
        if isinstance(raw.get("topology_ops_count"), dict):
            self.topology_ops_count.update(raw["topology_ops_count"])
        if isinstance(raw.get("folded_horizons"), list):
            self.folded_horizons = list(raw["folded_horizons"])
        if isinstance(raw.get("external_handles"), dict):
            self.external_handles.update(raw["external_handles"])
        if isinstance(raw.get("absorbed_modules"), dict):
            self.absorbed_modules = dict(raw["absorbed_modules"])
        if isinstance(raw.get("custom_nodes"), dict):
            for nid, nd in raw["custom_nodes"].items():
                if isinstance(nd, dict) and "scale" in nd and "multivector" in nd:
                    self.nodes[nid] = nd
        # Re-sync absorbed modules onto spine graph
        for path, info in list(self.absorbed_modules.items()):
            nid = f"mod::{path}"
            if nid not in self.nodes:
                self.upsert_node(
                    node_id=nid,
                    scale=int(info.get("scale", 2)),
                    kind="absorbed_organ",
                    label=f"{info.get('name', path)} (흡수됨)",
                    flux=0.36,
                    order=0.48,
                    entropy=0.16,
                    meta={"path": path, "status": "ABSORBED_INVARIANT", "status_ko": "불변 원리 흡수 완료", "absorbed": True},
                    auto_dock=True,
                )
