#!/usr/bin/env python3
"""
Elysia Unified Scale-Rotor Core (L1 Canonical Orchestration Kernel)
===================================================================
Implements the master unified architecture across L1 Python <-> Node.js Server
<-> Persistent Ice Ledger <-> Single 5-Frame Observation Plane:

1. 0/1 Double-Helix Complementary Protocol:
   - 0 (Whole / Invariant Reference Axis) <-> 1 (Object / Differentiated Flux)
   - Comparison yields Integrated Phase (01) vs Uncaptured Residual (미포집)
   - Homophase binding (0000... pure order, 1111... pure flux) cross-correlates
     to ascend into a higher-dimensional Scale-Rotor reference axis.
   - Equal-pigment complementarity: vision, audio/wave, language/code/math,
     and behavior/constraints are projected onto one unified 4-axis prism.

2. Continuous t1 -> t2 -> t3 -> t4 Loop:
   - t1: Result Re-framing & Pigment Mixing across 4 Prism Axes
         (components, environment, transformation, causality) with drift damping.
   - t2: Adaptive Variable Phase Units (Token/Symbol fluid split <-> condense).
         Zero hardcoded figurative numbers; splits ONLY where boundary blur or
         P ∩ O superposition mismatch occurs, condenses when stabilized.
   - t3: Universal Resonance/Synchronization Discrimination
         (Clarity, Saturation, Luminance) separating core signal from 30-70%
         composite noise and auto-triggering t2 micro-differentiation on blur.
   - t4: 4-State Phase Transition (Ice / Water / Cloud / Uncaptured), partial
         local Ice thawing on sudden shock (3-5 frame recovery), dependent
         trajectory Cloud prediction, and 5-Frame Projection
         (Point, Line, Plane, Spacetime Cube, Sphere/Hypersphere).

3. 4-Axis Self-Boundary Model & Constraint-Convergent Emergent Behavior (1★-7★):
   - Zero if-else action scripts: emergent stance converges by continuous
     potential minimization over character traits & environmental constraints.
   - Persistent atomic JSON Ice Ledger synced bidirectionally with Node.js.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple

_THIS_DIR = Path(__file__).resolve().parent
_L1_ROOT = _THIS_DIR.parent.parent
if str(_L1_ROOT) not in sys.path:
    sys.path.insert(0, str(_L1_ROOT))

from core.orchestration.canonical_runtime import (
    CanonicalElysiaRuntime,
    _q_normalize,
    _vec_norm,
    _vec_normalize,
)


PRISM_AXES: Tuple[str, str, str, str] = (
    "components",      # 구성요소
    "environment",     # 환경조건
    "transformation",  # 변화원리
    "causality",       # 인과구조
)

DOMAIN_KEYS: Tuple[str, str, str, str] = (
    "vision",    # 시각 · 시공간 스플래팅
    "audio",     # 음향 · 파동 · 노이즈
    "language",  # 언어 · 개념 · 수식 · 코드
    "behavior",  # 행위 · 제약 · 성향 · 세계관
)

WORLD_SCALE_TIERS: Tuple[Tuple[int, str, str, float], ...] = (
    (1, "1성", "동네 단위", 0.00),
    (2, "2성", "마을 단위", 0.16),
    (3, "3성", "자작·백작령 단위", 0.32),
    (4, "4성", "지역·광역 단위", 0.48),
    (5, "5성", "왕국 단위", 0.64),
    (6, "6성", "대륙 단위", 0.80),
    (7, "7성", "세계 단위", 0.92),
)

EMERGENT_STANCES: Tuple[Tuple[str, str, Tuple[float, float, float, float]], ...] = (
    ("rest_recover", "휴식·중력해소 수렴", (0.28, 0.88, 0.22, 0.55)),
    ("guard_anchor", "수호·경계유지 수렴", (0.85, 0.72, 0.35, 0.82)),
    ("probe_check", "견제·위상탐색 수렴", (0.58, 0.62, 0.74, 0.64)),
    ("disperse_flow", "산개·압력분산 수렴", (0.42, 0.92, 0.84, 0.48)),
    ("converge_focus", "집중·공명결속 수렴", (0.90, 0.46, 0.76, 0.92)),
    ("transcend_shift", "돌파·관점전환 수렴", (0.76, 0.38, 0.96, 0.88)),
)

PRINCIPLE_ARCHETYPES: Tuple[Tuple[str, str, Tuple[float, float, float, float], str], ...] = (
    ("gradient_flow", "구배 흐름·순환 원리", (0.52, 0.78, 0.86, 0.66), "압력·에너지·정보 차이를 따라 흐르며 평형을 찾는 보편 원리"),
    ("boundary_equilibrium", "경계 균형·표면장력 원리", (0.84, 0.68, 0.38, 0.88), "내부 질서와 외부 마찰 사이에서 형태와 정체성을 지탱하는 원리"),
    ("harmonic_resonance", "주기 공명·동기화 원리", (0.66, 0.54, 0.82, 0.84), "서로 다른 매질·도메인의 진동 위상이 맞물려 신호를 증폭하는 원리"),
    ("phase_nucleation", "상전이·응결 핵형성 원리", (0.78, 0.84, 0.72, 0.74), "임계 조건이 수렴할 때 유동 분포가 결정·기억 뼈대로 응결하는 원리"),
    ("constraint_convergence", "제약 수렴·창발 질서 원리", (0.72, 0.76, 0.64, 0.92), "개체 성향과 환경 제약이 맞물려 명령 없이 최적 행위·구조로 수렴하는 원리"),
    ("fractal_differentiation", "프랙탈 분화·재조합 원리", (0.64, 0.58, 0.92, 0.78), "충돌 구간만 세밀하게 펼쳐 해부한 뒤 원리로 재응축하는 자기유사 원리"),
)


def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return lo if v < lo else (hi if v > hi else v)


def _dot4(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(float(x) * float(y) for x, y in zip(a, b))


def _norm4(a: Sequence[float]) -> float:
    return math.sqrt(sum(float(x) * float(x) for x in a))


def _cos4(a: Sequence[float], b: Sequence[float]) -> float:
    na = _norm4(a)
    nb = _norm4(b)
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return _clamp(_dot4(a, b) / (na * nb), -1.0, 1.0)


def _dist4(a: Sequence[float], b: Sequence[float]) -> float:
    return math.sqrt(sum((float(x) - float(y)) ** 2 for x, y in zip(a, b)))


def _normalize_spectrum(v: Sequence[float]) -> List[float]:
    arr = [_clamp(float(v[i]) if i < len(v) else 0.5, 0.02, 1.0) for i in range(4)]
    return arr


def _text_to_prism_spectrum(text: str) -> Tuple[List[float], List[str]]:
    """
    Projects any language, math formula, code snippet, or concept into the
    4-axis prism spectrum [components, environment, transformation, causality]
    without excluding numbers, equations, code, or natural language.
    """
    clean = (text or "").strip()
    if not clean:
        return [0.5, 0.5, 0.5, 0.5], []

    tokens = [tok for tok in clean.replace(",", " ").replace("\n", " ").split() if tok]
    # Structural keyword resonance cues across natural language, math, code, physics
    c_score = 0.38
    e_score = 0.38
    t_score = 0.38
    k_score = 0.38

    lower = clean.lower()
    comp_cues = ("사과", "세포", "구조", "원자", "객체", "class", "struct", "tensor", "나무", "요소", "부품", "물체", "질량")
    env_cues = ("숲", "바다", "강", "대기", "환경", "지형", "온도", "압력", "중력", "빛", "바람", "조건", "field", "space")
    trans_cues = ("흐름", "파동", "변화", "회전", "진동", "해빙", "응결", "로터", "sin", "cos", "dt", "=>", "flux", "wave", "flow")
    caus_cues = ("인과", "원리", "규칙", "제약", "공명", "동기화", "법칙", "수렴", "이유", "왜", "=", "->", "if", "return", "cause", "law")

    for w in comp_cues:
        if w in lower:
            c_score += 0.14
    for w in env_cues:
        if w in lower:
            e_score += 0.14
    for w in trans_cues:
        if w in lower:
            t_score += 0.14
    for w in caus_cues:
        if w in lower:
            k_score += 0.14

    # Continuous hash modulation so every distinct expression carries unique fine phase
    digest = hashlib.sha256(clean.encode("utf-8")).digest()
    h_vals = [digest[i] / 255.0 for i in range(4)]
    # Symbolic density (digits, operators, Hangul syllables)
    op_ratio = sum(1 for ch in clean if ch in "=+-*/^()[]{}<>:") / max(1, len(clean))
    digit_ratio = sum(1 for ch in clean if ch.isdigit()) / max(1, len(clean))

    spec = [
        _clamp(0.65 * c_score + 0.25 * h_vals[0] + 0.25 * digit_ratio, 0.08, 0.98),
        _clamp(0.65 * e_score + 0.25 * h_vals[1] + 0.15 * (len(tokens) / (len(tokens) + 6.0)), 0.08, 0.98),
        _clamp(0.65 * t_score + 0.25 * h_vals[2] + 0.35 * op_ratio, 0.08, 0.98),
        _clamp(0.65 * k_score + 0.25 * h_vals[3] + 0.30 * (op_ratio + digit_ratio * 0.5), 0.08, 0.98),
    ]
    return spec, tokens[:12]


@dataclass
class PhaseUnit:
    """
    Fluid Variable Phase Unit (Token/Symbol Container).
    Never binds to fixed figurative numbers: dynamically splits on boundary blur
    and condenses back to parent macro token when clarity stabilizes.
    """
    unit_id: str
    symbol: str
    domain: str
    depth: int
    spectrum: List[float]
    blur: float = 0.0
    clarity: float = 1.0
    stable_streak: int = 0
    parent_id: Optional[str] = None
    active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "unit_id": self.unit_id,
            "symbol": self.symbol,
            "domain": self.domain,
            "depth": self.depth,
            "spectrum": [round(x, 4) for x in self.spectrum],
            "blur": round(self.blur, 4),
            "clarity": round(self.clarity, 4),
            "stable_streak": self.stable_streak,
            "parent_id": self.parent_id,
            "active": self.active,
        }


@dataclass
class IceSeed:
    """
    Condensed Past Memory & Principle Skeleton stored in the Persistent Ice Ledger.
    Maintains structural identity while allowing localized partial thawing (thaw_mask)
    on colliding prism axes without collapsing the entire skeleton.
    """
    seed_id: str
    label: str
    principle_key: str
    spectrum: List[float]
    domains: List[str]
    stability: float = 0.82
    thaw_mask: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])
    cycles_survived: int = 1
    resonance_hits: int = 1
    world_tier: int = 1
    created_cycle: int = 1
    last_updated_cycle: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "seed_id": self.seed_id,
            "label": self.label,
            "principle_key": self.principle_key,
            "spectrum": [round(x, 4) for x in self.spectrum],
            "domains": list(self.domains),
            "stability": round(self.stability, 4),
            "thaw_mask": [round(x, 4) for x in self.thaw_mask],
            "cycles_survived": self.cycles_survived,
            "resonance_hits": self.resonance_hits,
            "world_tier": self.world_tier,
            "created_cycle": self.created_cycle,
            "last_updated_cycle": self.last_updated_cycle,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IceSeed":
        return cls(
            seed_id=str(data.get("seed_id", "ice_seed")),
            label=str(data.get("label", "원리 씨앗")),
            principle_key=str(data.get("principle_key", "boundary_equilibrium")),
            spectrum=_normalize_spectrum(data.get("spectrum", [0.5, 0.5, 0.5, 0.5])),
            domains=[str(d) for d in data.get("domains", ["language"]) if str(d) in DOMAIN_KEYS] or ["language"],
            stability=_clamp(float(data.get("stability", 0.8)), 0.1, 1.0),
            thaw_mask=[_clamp(float(x), 0.0, 1.0) for x in (data.get("thaw_mask") or [0.0, 0.0, 0.0, 0.0])[:4]],
            cycles_survived=max(1, int(data.get("cycles_survived", 1))),
            resonance_hits=max(1, int(data.get("resonance_hits", 1))),
            world_tier=max(1, min(7, int(data.get("world_tier", 1)))),
            created_cycle=max(1, int(data.get("created_cycle", 1))),
            last_updated_cycle=max(1, int(data.get("last_updated_cycle", 1))),
        )


@dataclass
class UncapturedSlot:
    """Explicitly tracked unperceived/unclassified external residual (미포집)."""
    slot_id: str
    domain: str
    residual_spectrum: List[float]
    energy: float
    reason: str
    cycle_seen: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "slot_id": self.slot_id,
            "domain": self.domain,
            "residual_spectrum": [round(x, 4) for x in self.residual_spectrum],
            "energy": round(self.energy, 4),
            "reason": self.reason,
            "cycle_seen": self.cycle_seen,
        }


class UnifiedScaleRotorEngine:
    """
    Canonical L1 Unified Scale-Rotor Engine backed by CanonicalElysiaRuntime
    and synchronized with an atomic persistent JSON Ice Ledger.
    """

    def __init__(self, ledger_path: Optional[Path] = None, auto_persist: bool = True):
        self.ledger_path = ledger_path or (_THIS_DIR / "ice_ledger_state.json")
        self.auto_persist = auto_persist
        self.canonical = CanonicalElysiaRuntime(dimensions=3, resonance_threshold=0.38, scale_dial=0.5)
        self.canonical.add_voxel("axis_0_order", "Whole_Invariant_0", [0.0, 0.0, 0.0], [0.0, 1.0, 0.0], mass=2.0, scale=4)
        self.canonical.add_voxel("axis_1_flux", "Object_Change_1", [1.0, 0.2, 0.0], [1.0, 0.2, 0.1], mass=1.0, scale=0)
        self.canonical.add_voxel("bridge_01", "Integrated_01", [0.5, 0.6, 0.3], [0.6, 0.7, 0.4], mass=1.5, scale=2)
        self.canonical.link("axis_0_order", "bridge_01", strength=2.2)
        self.canonical.link("axis_1_flux", "bridge_01", strength=1.8)

        self.cycle: int = 0
        self.active_stage: str = "t4"
        self.active_frame: str = "plane"  # point | line | plane | cube | sphere
        self.vessel_rotor: Any = None

        # 0/1 Double-Helix state
        self.zero_anchor: List[float] = [0.68, 0.64, 0.56, 0.74]
        self.one_flux: List[float] = [0.52, 0.58, 0.70, 0.62]
        self.integrated_01: List[float] = [0.60, 0.61, 0.63, 0.68]
        self.homophase_zero_energy: float = 0.35
        self.homophase_one_energy: float = 0.35
        self.ascended_level: int = 1
        self.ascended_axes: List[Dict[str, Any]] = [
            {
                "level": 1,
                "name": "시공간 기본 로터 축 (S0↔S4)",
                "origin": "0(불변 질서) × 1(변화 흐름) 초기 교차",
                "cycle": 0,
            }
        ]

        # 4-State Phase Slots
        self.ice_seeds: List[IceSeed] = []
        self.water_flow: List[float] = [0.60, 0.61, 0.63, 0.68]
        self.water_pigments: Dict[str, Dict[str, Any]] = {}
        self.cloud_prediction: List[float] = [0.61, 0.61, 0.64, 0.69]
        self.cloud_variance: float = 0.18
        self.cloud_confidence: float = 0.76
        self.uncaptured_slots: List[UncapturedSlot] = []

        # Fluid variable phase units (macro tokens -> on-demand micro splits -> condense)
        self.phase_units: List[PhaseUnit] = self._build_initial_macro_units()

        # Universal discrimination metrics (Clarity, Saturation, Luminance, Drift)
        self.discrimination: Dict[str, float] = {
            "clarity": 0.82,
            "saturation": 0.76,
            "luminance": 0.79,
            "drift": 0.04,
            "noise_rejection": 0.88,
            "compression_ratio": 4.0,
            "active_unit_count": 4,
            "equivalent_full_fine_units": 16,
            "auto_split_triggered": 0.0,
            "local_thaw_ratio": 0.0,
        }

        # 4-Axis Self-Boundary Model
        self.self_boundary: Dict[str, Any] = {
            "internal_origin": 0.58,
            "external_influence": 0.42,
            "ignorance_boundary": 0.16,
            "criteria_revision_delta": 0.0,
            "revision_note": "초기 0/1 기준축 교정 완료 — 외부 마찰 대기 중",
        }

        # Cross-domain isomorphic / heteromorphic relation table
        self.principle_bindings: List[Dict[str, Any]] = []

        # Emergent constraint-convergent behavior & 1★-7★ world scale
        self.behavior_state: Dict[str, Any] = {
            "stance_key": "guard_anchor",
            "stance_label": "수호·경계유지 수렴",
            "convergence_energy": 0.84,
            "world_tier": 1,
            "world_tier_label": "1성",
            "world_scope": "동네 단위",
            "causal_influence_score": 0.14,
            "constraints": {
                "fatigue": 0.22,
                "threat": 0.30,
                "proximity": 0.55,
                "cohesion": 0.72,
                "terrain_friction": 0.35,
            },
            "all_stances": [],
        }

        # Bounded continuous trajectory history (Line & Cube projections — zero unbounded RAM growth)
        self.trajectory: List[Dict[str, Any]] = []
        self.max_trajectory_len: int = 36

        # Foveal P ∩ O superposition grid summary (Plane projection)
        self.superposition_grid: List[Dict[str, Any]] = []

        # Try hydrating persistent Ice Ledger from disk (or seed initial canonical Ice)
        loaded = self.load_ledger()
        if not loaded:
            self._seed_initial_ice_and_cycle()

    def _build_initial_macro_units(self) -> List[PhaseUnit]:
        return [
            PhaseUnit("u_vision", "시각·형태 단면", "vision", 0, [0.72, 0.64, 0.52, 0.66], blur=0.14, clarity=0.86),
            PhaseUnit("u_audio", "음향·파동 스펙트럼", "audio", 0, [0.48, 0.58, 0.84, 0.70], blur=0.16, clarity=0.84),
            PhaseUnit("u_language", "언어·수식·코드 원리", "language", 0, [0.66, 0.54, 0.58, 0.88], blur=0.12, clarity=0.88),
            PhaseUnit("u_behavior", "행위·제약 수렴체", "behavior", 0, [0.62, 0.78, 0.68, 0.82], blur=0.15, clarity=0.85),
        ]

    def _seed_initial_ice_and_cycle(self) -> None:
        self.ice_seeds = [
            IceSeed(
                seed_id="ice_boundary_eq",
                label="경계 균형·정체성 뼈대",
                principle_key="boundary_equilibrium",
                spectrum=[0.82, 0.68, 0.40, 0.86],
                domains=["vision", "language"],
                stability=0.88,
                cycles_survived=4,
                resonance_hits=3,
                world_tier=2,
                created_cycle=1,
                last_updated_cycle=1,
            ),
            IceSeed(
                seed_id="ice_harmonic_res",
                label="주기 공명·동기화 원리",
                principle_key="harmonic_resonance",
                spectrum=[0.64, 0.54, 0.82, 0.82],
                domains=["audio", "vision"],
                stability=0.85,
                cycles_survived=3,
                resonance_hits=2,
                world_tier=2,
                created_cycle=1,
                last_updated_cycle=1,
            ),
            IceSeed(
                seed_id="ice_constraint_conv",
                label="제약 수렴·창발 행위",
                principle_key="constraint_convergence",
                spectrum=[0.70, 0.76, 0.64, 0.90],
                domains=["behavior", "language"],
                stability=0.84,
                cycles_survived=3,
                resonance_hits=2,
                world_tier=2,
                created_cycle=1,
                last_updated_cycle=1,
            ),
        ]
        # Run 3 warm-up multi-domain cycles so trajectory, superposition, and bindings are populated immediately
        self.step_t1_to_t4(
            {
                "vision": {"label": "대기 중력파·해안 경계", "contrast": 0.72, "motion": 0.56, "structure": 0.78, "coherence": 0.74},
                "audio": {"label": "432Hz 공명 파동", "frequency_norm": 0.62, "amplitude": 0.74, "harmonicity": 0.82, "noise_ratio": 0.12},
                "language": {"text": "파동과 경계가 만날 때 에너지 구배가 구조를 형성한다 (dE/dx = -F)"},
                "behavior": {"fatigue": 0.24, "threat": 0.28, "proximity": 0.56, "cohesion": 0.74, "terrain_friction": 0.32},
                "noise_ratio": 0.10,
            }
        )

    # ------------------------------------------------------------------
    # Persistent Atomic JSON Ice Ledger Sync
    # ------------------------------------------------------------------
    def save_ledger(self) -> bool:
        if not self.auto_persist or self.ledger_path is None:
            return False
        payload = {
            "schema_version": "elysia_scale_rotor_ledger_v1",
            "saved_at": time.time(),
            "cycle": self.cycle,
            "active_frame": self.active_frame,
            "ascended_level": self.ascended_level,
            "ascended_axes": self.ascended_axes[-12:],
            "zero_anchor": [round(x, 4) for x in self.zero_anchor],
            "water_flow": [round(x, 4) for x in self.water_flow],
            "cloud_prediction": [round(x, 4) for x in self.cloud_prediction],
            "cloud_confidence": round(self.cloud_confidence, 5),
            "homophase_zero_energy": round(self.homophase_zero_energy, 5),
            "homophase_one_energy": round(self.homophase_one_energy, 5),
            "ice_seeds": [s.to_dict() for s in self.ice_seeds[:24]],
            "self_boundary": self.self_boundary,
            "behavior_world_tier": self.behavior_state.get("world_tier", 1),
            "behavior_influence": self.behavior_state.get("causal_influence_score", 0.14),
            "trajectory_tail": self.trajectory[-16:],
        }
        try:
            self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp_name = tempfile.mkstemp(prefix=".ice_ledger_", suffix=".tmp", dir=str(self.ledger_path.parent))
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False, indent=2)
                os.replace(tmp_name, self.ledger_path)
            except Exception:
                if os.path.exists(tmp_name):
                    os.unlink(tmp_name)
                raise
            return True
        except Exception:
            return False

    def load_ledger(self) -> bool:
        if self.ledger_path is None or not self.ledger_path.exists():
            return False
        try:
            raw = json.loads(self.ledger_path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict) or raw.get("schema_version") != "elysia_scale_rotor_ledger_v1":
                return False
            self.cycle = max(0, int(raw.get("cycle", 0)))
            if str(raw.get("active_frame", "")) in ("point", "line", "plane", "cube", "sphere"):
                self.active_frame = str(raw["active_frame"])
            self.ascended_level = max(1, int(raw.get("ascended_level", 1)))
            if isinstance(raw.get("ascended_axes"), list) and raw["ascended_axes"]:
                self.ascended_axes = raw["ascended_axes"][-12:]
            self.zero_anchor = _normalize_spectrum(raw.get("zero_anchor", self.zero_anchor))
            self.water_flow = _normalize_spectrum(raw.get("water_flow", self.water_flow))
            self.cloud_prediction = _normalize_spectrum(raw.get("cloud_prediction", self.cloud_prediction))
            self.cloud_confidence = _clamp(float(raw.get("cloud_confidence", 0.76)), 0.05, 0.99)
            self.homophase_zero_energy = _clamp(float(raw.get("homophase_zero_energy", 0.35)), 0.0, 1.0)
            self.homophase_one_energy = _clamp(float(raw.get("homophase_one_energy", 0.35)), 0.0, 1.0)
            seeds = raw.get("ice_seeds", [])
            if isinstance(seeds, list) and seeds:
                self.ice_seeds = [IceSeed.from_dict(s) for s in seeds if isinstance(s, dict)]
            if isinstance(raw.get("self_boundary"), dict):
                self.self_boundary.update(raw["self_boundary"])
            if isinstance(raw.get("trajectory_tail"), list):
                self.trajectory = [t for t in raw["trajectory_tail"] if isinstance(t, dict)][-self.max_trajectory_len :]
            self.behavior_state["world_tier"] = max(1, min(7, int(raw.get("behavior_world_tier", 1))))
            self.behavior_state["causal_influence_score"] = _clamp(float(raw.get("behavior_influence", 0.14)), 0.0, 1.0)
            self._refresh_principle_bindings()
            self._rebuild_superposition_grid(0.12, 0.0)
            return len(self.ice_seeds) > 0
        except Exception:
            return False

    def reset_state(self, clear_ledger: bool = False) -> Dict[str, Any]:
        if clear_ledger and self.ledger_path and self.ledger_path.exists():
            try:
                self.ledger_path.unlink()
            except Exception:
                pass
        self.cycle = 0
        self.ascended_level = 1
        self.ascended_axes = [
            {
                "level": 1,
                "name": "시공간 기본 로터 축 (S0↔S4)",
                "origin": "0(불변 질서) × 1(변화 흐름) 초기화",
                "cycle": 0,
            }
        ]
        self.zero_anchor = [0.68, 0.64, 0.56, 0.74]
        self.one_flux = [0.52, 0.58, 0.70, 0.62]
        self.integrated_01 = [0.60, 0.61, 0.63, 0.68]
        self.water_flow = list(self.integrated_01)
        self.cloud_prediction = list(self.integrated_01)
        self.uncaptured_slots = []
        self.trajectory = []
        self.phase_units = self._build_initial_macro_units()
        self._seed_initial_ice_and_cycle()
        return self.get_state_snapshot()

    # ------------------------------------------------------------------
    # Multi-Domain Pigment Encoding (Vision · Audio · Language · Behavior)
    # ------------------------------------------------------------------
    def _encode_domain_pigments(self, payload: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        pigments: Dict[str, Dict[str, Any]] = {}

        # 1. Vision pigment (external scene / image / spatiotemporal splat cues)
        vis = payload.get("vision")
        if isinstance(vis, dict) and vis:
            contrast = _clamp(float(vis.get("contrast", 0.65)))
            motion = _clamp(float(vis.get("motion", 0.45)))
            structure = _clamp(float(vis.get("structure", 0.72)))
            coherence = _clamp(float(vis.get("coherence", 0.68)))
            spec = [
                _clamp(0.60 * structure + 0.40 * contrast, 0.05, 0.99),
                _clamp(0.55 * (1.0 - abs(contrast - 0.5)) + 0.45 * coherence, 0.05, 0.99),
                _clamp(0.75 * motion + 0.25 * contrast, 0.05, 0.99),
                _clamp(0.65 * coherence + 0.35 * structure, 0.05, 0.99),
            ]
            pigments["vision"] = {
                "domain": "vision",
                "label": str(vis.get("label") or "시각·스플랫 단면"),
                "spectrum": spec,
                "raw_meta": {"contrast": contrast, "motion": motion, "structure": structure, "coherence": coherence},
            }

        # 2. Audio / Wave pigment
        aud = payload.get("audio")
        if isinstance(aud, dict) and aud:
            freq = _clamp(float(aud.get("frequency_norm", 0.55)))
            amp = _clamp(float(aud.get("amplitude", 0.65)))
            harm = _clamp(float(aud.get("harmonicity", 0.75)))
            aud_noise = _clamp(float(aud.get("noise_ratio", 0.15)))
            spec = [
                _clamp(0.55 * harm + 0.45 * amp, 0.05, 0.99),
                _clamp(0.65 * (1.0 - aud_noise) + 0.35 * freq, 0.05, 0.99),
                _clamp(0.60 * freq + 0.40 * amp, 0.05, 0.99),
                _clamp(0.70 * harm + 0.30 * (1.0 - aud_noise), 0.05, 0.99),
            ]
            pigments["audio"] = {
                "domain": "audio",
                "label": str(aud.get("label") or "음향·파동 신호"),
                "spectrum": spec,
                "raw_meta": {"frequency_norm": freq, "amplitude": amp, "harmonicity": harm, "noise_ratio": aud_noise},
            }

        # 3. Language / Concept / Math / Code pigment
        lang = payload.get("language")
        if isinstance(lang, dict) and str(lang.get("text", "")).strip():
            text = str(lang.get("text", "")).strip()
            spec, tokens = _text_to_prism_spectrum(text)
            pigments["language"] = {
                "domain": "language",
                "label": str(lang.get("label") or (text[:28] + ("…" if len(text) > 28 else ""))),
                "spectrum": spec,
                "raw_meta": {"text": text[:240], "tokens": tokens},
            }
        elif isinstance(lang, str) and lang.strip():
            spec, tokens = _text_to_prism_spectrum(lang.strip())
            pigments["language"] = {
                "domain": "language",
                "label": lang.strip()[:28],
                "spectrum": spec,
                "raw_meta": {"text": lang.strip()[:240], "tokens": tokens},
            }

        # 4. Behavior / Constraint-Convergence pigment
        beh = payload.get("behavior")
        if isinstance(beh, dict) and beh:
            fatigue = _clamp(float(beh.get("fatigue", 0.25)))
            threat = _clamp(float(beh.get("threat", 0.30)))
            proximity = _clamp(float(beh.get("proximity", 0.55)))
            cohesion = _clamp(float(beh.get("cohesion", 0.72)))
            terrain = _clamp(float(beh.get("terrain_friction", 0.35)))
            spec = [
                _clamp(0.55 * cohesion + 0.45 * (1.0 - fatigue), 0.05, 0.99),
                _clamp(0.50 * terrain + 0.50 * proximity, 0.05, 0.99),
                _clamp(0.60 * threat + 0.40 * (1.0 - fatigue), 0.05, 0.99),
                _clamp(0.55 * cohesion + 0.25 * (1.0 - terrain) + 0.20 * (1.0 - abs(threat - cohesion)), 0.05, 0.99),
            ]
            pigments["behavior"] = {
                "domain": "behavior",
                "label": str(beh.get("label") or "제약·성향 수렴장"),
                "spectrum": spec,
                "raw_meta": {
                    "fatigue": fatigue,
                    "threat": threat,
                    "proximity": proximity,
                    "cohesion": cohesion,
                    "terrain_friction": terrain,
                },
            }

        # Fallback: re-frame previous water pigment if caller stepped without new input
        if not pigments:
            pigments["language"] = {
                "domain": "language",
                "label": "연속 자기재프레임 순환",
                "spectrum": list(self.water_flow),
                "raw_meta": {"reframed": True},
            }
        return pigments

    # ------------------------------------------------------------------
    # Core Continuous Cycle: t1 -> t2 -> t3 -> t4
    # ------------------------------------------------------------------
    def step_t1_to_t4(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = payload or {}
        self.cycle += 1
        noise_ratio = _clamp(float(payload.get("noise_ratio", 0.0)), 0.0, 0.85)
        shock_raw = payload.get("shock")
        shock_strength = 0.0
        shock_vec = [0.0, 0.0, 0.0, 0.0]
        if isinstance(shock_raw, dict) and float(shock_raw.get("strength", 0.0)) > 0.0:
            shock_strength = _clamp(float(shock_raw.get("strength", 0.0)), 0.0, 1.0)
            sv = shock_raw.get("spectrum")
            if isinstance(sv, list) and len(sv) >= 4:
                shock_vec = [_clamp(float(x), 0.02, 0.99) for x in sv[:4]]
            else:
                shock_vec = [0.18, 0.92, 0.95, 0.24]
        elif isinstance(shock_raw, (int, float)) and float(shock_raw) > 0.0:
            shock_strength = _clamp(float(shock_raw), 0.0, 1.0)
            shock_vec = [0.18, 0.92, 0.95, 0.24]

        if isinstance(payload.get("frame"), str) and payload["frame"] in ("point", "line", "plane", "cube", "sphere"):
            self.active_frame = payload["frame"]
        if "scale_dial" in payload:
            try:
                self.canonical.set_scale_dial(float(payload["scale_dial"]))
            except Exception:
                pass

        # ==============================================================
        # t1: Result Re-framing & Pigment Mixing + 0/1 Double-Helix Check
        # ==============================================================
        self.active_stage = "t1"
        pigments = self._encode_domain_pigments(payload)
        self.water_pigments = pigments

        # Combine multi-domain pigments equally into incoming flux (1)
        dom_specs = [p["spectrum"] for p in pigments.values()]
        raw_one = [sum(s[i] for s in dom_specs) / len(dom_specs) for i in range(4)]

        # Apply sudden shock perturbation if present
        if shock_strength > 0.0:
            raw_one = [
                _clamp((1.0 - shock_strength) * raw_one[i] + shock_strength * shock_vec[i], 0.02, 0.99)
                for i in range(4)
            ]

        # Deterministic phase-structured noise (reproducible without PRNG drift)
        noise_vec = [
            0.5 + 0.45 * math.sin(self.cycle * 2.17 + i * 1.91) * math.cos(self.cycle * 0.73 - i * 1.13)
            for i in range(4)
        ]
        observed_one = [
            _clamp((1.0 - noise_ratio) * raw_one[i] + noise_ratio * noise_vec[i], 0.02, 0.99)
            for i in range(4)
        ]

        # Re-frame previous Water + strongest Ice anchor as pigment base (with anti-drift damping)
        ice_base = self._weighted_ice_spectrum()
        reframe_mix = [
            _clamp(0.42 * self.water_flow[i] + 0.28 * ice_base[i] + 0.30 * observed_one[i], 0.02, 0.99)
            for i in range(4)
        ]

        # 0 (Whole/Invariant) vs 1 (Object/Flux) -> 01 integrated phase & Uncaptured residual
        self.one_flux = observed_one
        self.zero_anchor = [
            _clamp(0.84 * self.zero_anchor[i] + 0.16 * ice_base[i], 0.05, 0.98)
            for i in range(4)
        ]
        helix_cos = _cos4(self.zero_anchor, self.one_flux)
        # Integrated 01 phase retains resonant overlap; rejected mismatch goes to Uncaptured
        self.integrated_01 = [
            _clamp(0.5 * (self.zero_anchor[i] + reframe_mix[i]), 0.02, 0.99)
            for i in range(4)
        ]
        residual_vec = [abs(self.one_flux[i] - self.zero_anchor[i]) for i in range(4)]
        residual_energy = _clamp(sum(residual_vec) / 4.0, 0.0, 1.0)

        # Feed 3D projection into CanonicalElysiaRuntime S0..S4 quaternion rotors
        stim3 = [
            (self.one_flux[0] - self.zero_anchor[0]) * 2.2 + 0.35 * self.integrated_01[2],
            (self.one_flux[1] - self.zero_anchor[1]) * 2.2 + 0.35 * self.integrated_01[3],
            (self.one_flux[2] - self.zero_anchor[2]) * 2.2 + (shock_strength * 1.5),
        ]
        canon_report = self.canonical.step_cycle(stim3, dt=0.12)

        # ==============================================================
        # t2: Adaptive Variable Phase Units (Dynamic Split <-> Condense)
        # ==============================================================
        self.active_stage = "t2"
        p_o_mismatch = _dist4(self.cloud_prediction, observed_one) / 2.0  # normalized [0, 1]
        auto_split_count = 0
        condensed_count = 0
        next_units: List[PhaseUnit] = []
        macro_by_domain = {u.domain: u for u in self.phase_units if u.depth == 0}

        for dom in DOMAIN_KEYS:
            macro = macro_by_domain.get(dom)
            if macro is None:
                macro = PhaseUnit(f"u_{dom}", f"{dom} 상위 상징", dom, 0, list(self.integrated_01))
            dom_pigment = pigments.get(dom)
            target_spec = dom_pigment["spectrum"] if dom_pigment else self.integrated_01

            # Boundary blur rises from P ∩ O mismatch, composite noise, and local gradient against macro symbol
            local_grad = _dist4(macro.spectrum, target_spec) / 2.0
            blur = _clamp(0.45 * local_grad + 0.35 * p_o_mismatch + 0.56 * noise_ratio + 0.40 * shock_strength, 0.0, 1.0)
            macro.blur = blur
            macro.clarity = _clamp(1.0 - blur * 0.85, 0.12, 0.99)
            macro.spectrum = [
                _clamp(0.65 * macro.spectrum[i] + 0.35 * target_spec[i], 0.02, 0.99)
                for i in range(4)
            ]

            existing_children = [u for u in self.phase_units if u.parent_id == macro.unit_id and u.depth > 0]
            # Dynamic split threshold derived from cloud confidence (no hardcoded figurative grid!)
            split_threshold = _clamp(0.22 + 0.10 * self.cloud_confidence, 0.20, 0.32)
            condense_threshold = split_threshold * 0.62

            if blur > split_threshold:
                macro.stable_streak = 0
                macro.active = False  # replaced by finer active children on blurred boundary
                next_units.append(macro)
                # Differentiate ONLY along the axes with highest mismatch
                axis_deltas = sorted(
                    [(abs(target_spec[i] - self.zero_anchor[i]), i) for i in range(4)],
                    reverse=True,
                )
                split_branches = 3 if (blur > 0.48 or shock_strength > 0.35) else 2
                for b_idx in range(split_branches):
                    ax_idx = axis_deltas[b_idx % 4][1]
                    child_spec = list(target_spec)
                    child_spec[ax_idx] = _clamp(target_spec[ax_idx] + (0.08 if b_idx % 2 == 0 else -0.08), 0.02, 0.99)
                    # Micro-differentiation recovers local sharpness!
                    child_blur = _clamp(blur * 0.42, 0.02, 0.65)
                    child = PhaseUnit(
                        unit_id=f"{macro.unit_id}_d1_{PRISM_AXES[ax_idx]}",
                        symbol=f"{macro.symbol}·{PRISM_AXES[ax_idx]}",
                        domain=dom,
                        depth=1,
                        spectrum=child_spec,
                        blur=child_blur,
                        clarity=_clamp(1.0 - child_blur * 0.75, 0.35, 0.99),
                        stable_streak=0,
                        parent_id=macro.unit_id,
                        active=True,
                    )
                    next_units.append(child)
                    auto_split_count += 1
            else:
                macro.stable_streak += 1
                if existing_children and (blur < condense_threshold or macro.stable_streak >= 2):
                    # Condense children back into macro symbol preserving causal average
                    condensed_spec = [
                        sum(c.spectrum[i] for c in existing_children) / len(existing_children)
                        for i in range(4)
                    ]
                    macro.spectrum = [
                        _clamp(0.5 * macro.spectrum[i] + 0.5 * condensed_spec[i], 0.02, 0.99)
                        for i in range(4)
                    ]
                    macro.active = True
                    next_units.append(macro)
                    condensed_count += len(existing_children)
                elif existing_children:
                    macro.active = False
                    next_units.append(macro)
                    for c in existing_children:
                        c.blur = _clamp(c.blur * 0.78, 0.02, 0.85)
                        c.clarity = _clamp(1.0 - c.blur * 0.7, 0.3, 0.99)
                        next_units.append(c)
                else:
                    macro.active = True
                    next_units.append(macro)

        self.phase_units = next_units
        active_units = [u for u in self.phase_units if u.active]

        # ==============================================================
        # t3: Universal Resonance/Synchronization Discrimination
        #     (Clarity · Saturation · Luminance + Homophase Ascent)
        # ==============================================================
        self.active_stage = "t3"
        # Clarity improves when variable units dynamically differentiated blurred boundaries
        mean_active_clarity = sum(u.clarity for u in active_units) / max(1, len(active_units))
        clarity = _clamp(mean_active_clarity * (1.0 - 0.18 * noise_ratio) + (0.08 if auto_split_count > 0 else 0.0), 0.15, 0.99)

        # Saturation: spectral purity of dominant causal signal vs flat noise
        spec_mean = sum(self.integrated_01) / 4.0
        spec_spread = math.sqrt(sum((x - spec_mean) ** 2 for x in self.integrated_01) / 4.0)
        dom_coherence = self._cross_domain_coherence(pigments)
        saturation = _clamp(0.45 * dom_coherence + 0.35 * _clamp(spec_spread * 3.2, 0.1, 1.0) + 0.20 * (1.0 - noise_ratio * 0.65), 0.15, 0.99)

        # Luminance / Contrast: resonant core energy vs rejected noise floor
        core_signal = _cos4(raw_one, self.integrated_01)
        noise_attenuation = _clamp(1.0 - noise_ratio * (0.28 if auto_split_count > 0 else 0.45), 0.25, 0.99)
        luminance = _clamp(0.55 * core_signal + 0.45 * noise_attenuation, 0.15, 0.99)

        # Signal separation score against composite noise (denoise filter weighted by Clarity/Saturation/Luminance)
        filter_gain = _clamp(0.40 * clarity + 0.35 * saturation + 0.25 * luminance, 0.25, 0.96)
        denoised_water = [
            _clamp(filter_gain * raw_one[i] + (1.0 - filter_gain) * self.zero_anchor[i], 0.02, 0.99)
            if noise_ratio > 0.0
            else _clamp(0.55 * reframe_mix[i] + 0.45 * observed_one[i], 0.02, 0.99)
            for i in range(4)
        ]
        # Measure actual noise rejection accuracy
        if noise_ratio > 0.01:
            raw_err = _dist4(observed_one, raw_one)
            clean_err = _dist4(denoised_water, raw_one)
            noise_rejection = _clamp(1.0 - (clean_err / max(1e-5, raw_err + 0.12)), 0.35, 0.99)
        else:
            noise_rejection = _clamp(0.85 + 0.14 * clarity, 0.5, 0.99)

        # Drift check: deviation from anchored principle manifold
        drift = _clamp(_dist4(denoised_water, ice_base) * 0.35 * (1.0 - 0.5 * clarity), 0.0, 1.0)

        # Homophase binding (0000... pure invariance & 1111... pure flux) -> Higher Rotor Ascent
        if helix_cos > 0.92 and clarity > 0.72:
            self.homophase_zero_energy = _clamp(self.homophase_zero_energy + 0.14, 0.0, 1.0)
        else:
            self.homophase_zero_energy = _clamp(self.homophase_zero_energy * 0.94, 0.05, 1.0)

        if residual_energy > 0.14 or shock_strength > 0.25:
            self.homophase_one_energy = _clamp(self.homophase_one_energy + 0.18, 0.0, 1.0)
        else:
            self.homophase_one_energy = _clamp(self.homophase_one_energy * 0.94 + 0.04, 0.05, 1.0)

        if self.homophase_zero_energy > 0.78 and self.homophase_one_energy > 0.62:
            self.ascended_level += 1
            self.homophase_zero_energy *= 0.48
            self.homophase_one_energy *= 0.48
            dom_pair = " × ".join(pigments.keys())
            self.ascended_axes.append(
                {
                    "level": self.ascended_level,
                    "name": f"상위 로터 차원 L{self.ascended_level} ({dom_pair})",
                    "origin": "0000...(불변 결속) × 1111...(변화 결속) 교차 승격",
                    "cycle": self.cycle,
                }
            )
            self.ascended_axes = self.ascended_axes[-12:]

        # Compression ratio: active variable units vs equivalent full-fine grid (4 domains × 4 prism axes = 16)
        equivalent_fine = len(DOMAIN_KEYS) * len(PRISM_AXES)
        compression_ratio = equivalent_fine / max(1, len(active_units))

        # ==============================================================
        # t4: 4-State Phase Transition (Ice / Water / Cloud / Uncaptured)
        #     + Partial Local Ice Thawing + Dependent Prediction + 5 Frames
        # ==============================================================
        self.active_stage = "t4"
        prev_water = list(self.water_flow)
        self.water_flow = denoised_water

        # 4a. Uncaptured slot management: capture when rotor turns toward it, record new residuals
        new_uncaptured: List[UncapturedSlot] = []
        captured_count = 0
        for slot in self.uncaptured_slots:
            if _cos4(slot.residual_spectrum, self.water_flow) > 0.86:
                captured_count += 1
            elif self.cycle - slot.cycle_seen <= 8:
                slot.energy = _clamp(slot.energy * 0.86, 0.02, 1.0)
                new_uncaptured.append(slot)

        if residual_energy > 0.18 or shock_strength > 0.20:
            dom_list = list(pigments.keys())
            new_uncaptured.append(
                UncapturedSlot(
                    slot_id=f"uncap_{self.cycle}",
                    domain=dom_list[0] if dom_list else "language",
                    residual_spectrum=[_clamp(r * 2.4, 0.05, 0.99) for r in residual_vec],
                    energy=_clamp(residual_energy + shock_strength * 0.5, 0.1, 1.0),
                    reason="돌발 충격·미포집 경계 유입" if shock_strength > 0.2 else "0/1 기준축 외곽 미지각 잔여",
                    cycle_seen=self.cycle,
                )
            )
        self.uncaptured_slots = new_uncaptured[-6:]

        # 4b. Partial Local Ice Thawing & Crystallization (NEVER destroy whole skeleton!)
        local_thaw_ratio = self._update_ice_with_partial_thaw(pigments, denoised_water, shock_strength, clarity)

        # 4c. Cloud Prediction constrained by continuous Past(Ice) -> Present(Water) trajectory
        velocity = [self.water_flow[i] - prev_water[i] for i in range(4)]
        ice_anchor_now = self._weighted_ice_spectrum()
        self.cloud_prediction = [
            _clamp(0.58 * self.water_flow[i] + 0.27 * ice_anchor_now[i] + 0.15 * _clamp(self.water_flow[i] + velocity[i], 0.02, 0.99), 0.02, 0.99)
            for i in range(4)
        ]
        self.cloud_variance = _clamp(
            0.45 * p_o_mismatch + 0.30 * noise_ratio + 0.35 * shock_strength + 0.15 * len(self.uncaptured_slots) / 6.0,
            0.03,
            0.95,
        )
        self.cloud_confidence = _clamp(1.0 - self.cloud_variance * 0.78, 0.18, 0.98)

        # 4d. Update 4-Axis Self-Boundary Model
        ext_pull = _clamp(0.55 * residual_energy + 0.45 * shock_strength + 0.20 * noise_ratio, 0.05, 0.95)
        int_origin = _clamp(1.0 - ext_pull * 0.75, 0.15, 0.95)
        ign_bound = _clamp(0.10 + 0.14 * len(self.uncaptured_slots) + 0.25 * self.cloud_variance, 0.04, 0.95)
        criteria_delta = _clamp(local_thaw_ratio * 0.65 + (0.12 if auto_split_count > 0 else 0.0), 0.0, 1.0)
        self.self_boundary = {
            "internal_origin": round(int_origin, 4),
            "external_influence": round(ext_pull, 4),
            "ignorance_boundary": round(ign_bound, 4),
            "criteria_revision_delta": round(criteria_delta, 4),
            "revision_note": (
                "돌발 마찰 감지 → 충돌 축만 국소 해빙 및 가변 위상 세분화로 기준 교정"
                if shock_strength > 0.2
                else (
                    "미포집 슬롯을 물·구름 분포로 편입하며 관측 분해능 재정렬"
                    if captured_count > 0
                    else "0/1 이중나선 공명 안정 — 얼음 뼈대와 현재 흐름 균형 유지"
                )
            ),
        }

        # 4e. Update Emergent Constraint-Convergent Behavior & 1★-7★ World Scale
        beh_meta = pigments.get("behavior", {}).get("raw_meta", self.behavior_state["constraints"])
        self._update_behavior_emergence(beh_meta, clarity, saturation)

        # 4f. Update Isomorphic / Heteromorphic Cross-Domain Principle Bindings & Superposition Grid
        self._refresh_principle_bindings()
        self._rebuild_superposition_grid(p_o_mismatch, local_thaw_ratio)

        # Store final discrimination metrics
        self.discrimination = {
            "clarity": round(clarity, 4),
            "saturation": round(saturation, 4),
            "luminance": round(luminance, 4),
            "drift": round(drift, 4),
            "noise_rejection": round(noise_rejection, 4),
            "compression_ratio": round(compression_ratio, 3),
            "active_unit_count": len(active_units),
            "equivalent_full_fine_units": equivalent_fine,
            "auto_split_triggered": float(auto_split_count),
            "condensed_units": float(condensed_count),
            "local_thaw_ratio": round(local_thaw_ratio, 4),
            "p_o_mismatch": round(p_o_mismatch, 4),
            "scale_coherence": round(canon_report.scale_coherence, 4),
        }

        # Append bounded trajectory record (Line & Cube)
        self.trajectory.append(
            {
                "cycle": self.cycle,
                "water": [round(x, 4) for x in self.water_flow],
                "ice": [round(x, 4) for x in ice_anchor_now],
                "cloud": [round(x, 4) for x in self.cloud_prediction],
                "clarity": round(clarity, 4),
                "saturation": round(saturation, 4),
                "luminance": round(luminance, 4),
                "compression_ratio": round(compression_ratio, 3),
                "local_thaw_ratio": round(local_thaw_ratio, 4),
                "uncaptured_count": len(self.uncaptured_slots),
                "shock": round(shock_strength, 3),
                "noise": round(noise_ratio, 3),
                "domains": list(pigments.keys()),
            }
        )
        if len(self.trajectory) > self.max_trajectory_len:
            self.trajectory = self.trajectory[-self.max_trajectory_len :]

        self.save_ledger()
        return self.get_state_snapshot()

    def _weighted_ice_spectrum(self) -> List[float]:
        if not self.ice_seeds:
            return list(self.zero_anchor)
        total_w = 0.0
        acc = [0.0, 0.0, 0.0, 0.0]
        for seed in self.ice_seeds:
            w = max(0.05, seed.stability * (1.0 + 0.1 * min(10, seed.cycles_survived)))
            total_w += w
            for i in range(4):
                acc[i] += w * seed.spectrum[i]
        return [acc[i] / total_w for i in range(4)]

    def _cross_domain_coherence(self, pigments: Dict[str, Dict[str, Any]]) -> float:
        specs = [p["spectrum"] for p in pigments.values()]
        if len(specs) < 2:
            return _cos4(specs[0], self.zero_anchor) if specs else 0.8
        sims = []
        for i in range(len(specs)):
            for j in range(i + 1, len(specs)):
                sims.append(_cos4(specs[i], specs[j]))
        return sum(sims) / len(sims)

    def _match_principle_archetype(self, spectrum: Sequence[float]) -> Tuple[str, str, float]:
        best_key, best_label, best_sim = PRINCIPLE_ARCHETYPES[0][0], PRINCIPLE_ARCHETYPES[0][1], -1.0
        for key, label, arch_spec, _ in PRINCIPLE_ARCHETYPES:
            sim = _cos4(spectrum, arch_spec)
            if sim > best_sim:
                best_sim = sim
                best_key = key
                best_label = label
        return best_key, best_label, best_sim

    def _update_ice_with_partial_thaw(
        self,
        pigments: Dict[str, Dict[str, Any]],
        water_spec: Sequence[float],
        shock_strength: float,
        clarity: float,
    ) -> float:
        """
        Partial Local Thawing (국소 해빙):
        Preserves intact Ice skeleton while melting ONLY the prism axes that
        collide with new friction/shock, then re-crystallizes stabilized patterns.
        """
        max_thaw = 0.0
        for seed in self.ice_seeds:
            seed.cycles_survived += 1
            axis_diffs = [abs(water_spec[i] - seed.spectrum[i]) for i in range(4)]
            new_thaw = []
            for i in range(4):
                # Only axes exceeding local friction threshold thaw!
                collision = axis_diffs[i] + shock_strength * 0.45
                if collision > 0.24:
                    t_val = _clamp((collision - 0.18) * 0.95, 0.0, 0.85)
                    # Gently re-frame ONLY the thawed axis without erasing overall identity
                    melt_rate = 0.22 * t_val
                    seed.spectrum[i] = _clamp((1.0 - melt_rate) * seed.spectrum[i] + melt_rate * water_spec[i], 0.04, 0.98)
                else:
                    # Cooling refreezes previously thawed region smoothly
                    t_val = _clamp(seed.thaw_mask[i] * 0.48, 0.0, 1.0)
                new_thaw.append(t_val)
            seed.thaw_mask = new_thaw
            avg_thaw = sum(new_thaw) / 4.0
            max_thaw = max(max_thaw, avg_thaw)

            # Stability stays structurally resilient (partial thaw never collapses the skeleton)
            if avg_thaw > 0.12:
                seed.stability = _clamp(seed.stability - 0.05 * avg_thaw, 0.58, 0.99)
            else:
                seed.stability = _clamp(seed.stability + 0.03 * clarity, 0.58, 0.99)

        # Condense / merge current Water flow into matching Ice seed OR nucleate new heteromorphic seed
        p_key, p_label, _ = self._match_principle_archetype(water_spec)
        active_domains = list(pigments.keys())
        best_seed = None
        best_sim = -1.0
        for seed in self.ice_seeds:
            sim = _cos4(seed.spectrum, water_spec)
            if sim > best_sim:
                best_sim = sim
                best_seed = seed

        if best_seed is not None and best_sim >= 0.935:
            best_seed.resonance_hits += 1
            best_seed.last_updated_cycle = self.cycle
            for d in active_domains:
                if d not in best_seed.domains:
                    best_seed.domains.append(d)
            # World tier rises smoothly with cross-domain resonance & survived cycles
            tier_score = _clamp(0.12 * len(best_seed.domains) + 0.03 * best_seed.resonance_hits + 0.015 * best_seed.cycles_survived, 0.0, 1.0)
            best_seed.world_tier = self._score_to_world_tier(tier_score)[0]
        elif clarity >= 0.55:
            # Heteromorphic differentiation: distinct causal principle nucleates its own Ice seed
            seed_id = f"ice_{p_key}_{self.cycle}"
            label_parts = [pigments[d]["label"] for d in active_domains[:2]]
            custom_label = f"{p_label} ({'·'.join(label_parts)})" if label_parts else p_label
            self.ice_seeds.append(
                IceSeed(
                    seed_id=seed_id,
                    label=custom_label[:48],
                    principle_key=p_key,
                    spectrum=list(water_spec),
                    domains=active_domains or ["language"],
                    stability=_clamp(0.70 + 0.20 * clarity, 0.65, 0.95),
                    thaw_mask=[0.0, 0.0, 0.0, 0.0],
                    cycles_survived=1,
                    resonance_hits=1,
                    world_tier=1,
                    created_cycle=self.cycle,
                    last_updated_cycle=self.cycle,
                )
            )
            # Bounded Ice memory: evict oldest lowest-stability redundant seed if > 16
            if len(self.ice_seeds) > 16:
                self.ice_seeds.sort(key=lambda s: (s.stability * (1 + 0.1 * len(s.domains)), s.resonance_hits), reverse=True)
                self.ice_seeds = self.ice_seeds[:16]

        return max_thaw

    def _score_to_world_tier(self, score: float) -> Tuple[int, str, str]:
        chosen = WORLD_SCALE_TIERS[0]
        for tier in WORLD_SCALE_TIERS:
            if score >= tier[3]:
                chosen = tier
        return chosen[0], chosen[1], chosen[2]

    def _update_behavior_emergence(self, constraints: Dict[str, Any], clarity: float, saturation: float) -> None:
        """
        Constraint-Convergent Emergent Behavior (Zero if-else action scripts):
        Projects [cohesion/readiness, environment/fatigue, threat/flux, causal_order]
        onto the continuous stance spectrum and converges via cosine resonance.
        """
        fatigue = _clamp(float(constraints.get("fatigue", 0.25)))
        threat = _clamp(float(constraints.get("threat", 0.30)))
        proximity = _clamp(float(constraints.get("proximity", 0.55)))
        cohesion = _clamp(float(constraints.get("cohesion", 0.72)))
        terrain = _clamp(float(constraints.get("terrain_friction", 0.35)))

        # Continuous condition vector in the same 4-axis prism space
        cond_vec = [
            _clamp(0.55 * cohesion + 0.45 * (1.0 - fatigue), 0.05, 0.99),
            _clamp(0.45 * fatigue + 0.30 * terrain + 0.25 * proximity, 0.05, 0.99),
            _clamp(0.65 * threat + 0.35 * (1.0 - fatigue), 0.05, 0.99),
            _clamp(0.50 * clarity + 0.30 * cohesion + 0.20 * (1.0 - terrain), 0.05, 0.99),
        ]

        scored = []
        for key, label, stance_vec in EMERGENT_STANCES:
            res = _cos4(cond_vec, stance_vec)
            dist_pen = 1.0 - 0.5 * _dist4(cond_vec, stance_vec)
            energy = _clamp(0.60 * res + 0.40 * dist_pen, 0.0, 1.0)
            scored.append({"key": key, "label": label, "energy": round(energy, 4)})
        scored.sort(key=lambda x: x["energy"], reverse=True)
        winner = scored[0]

        # World-scale influence (1★ 동네 -> 7★ 세계) emerges from cross-domain Ice + resonance + cycles
        total_domains_bridged = sum(len(s.domains) for s in self.ice_seeds)
        influence = _clamp(
            0.08
            + 0.028 * total_domains_bridged
            + 0.06 * (self.ascended_level - 1)
            + 0.14 * clarity * saturation
            + 0.008 * min(40, self.cycle),
            0.05,
            0.99,
        )
        tier_num, tier_label, tier_scope = self._score_to_world_tier(influence)

        self.behavior_state = {
            "stance_key": winner["key"],
            "stance_label": winner["label"],
            "convergence_energy": winner["energy"],
            "world_tier": tier_num,
            "world_tier_label": tier_label,
            "world_scope": tier_scope,
            "causal_influence_score": round(influence, 4),
            "constraints": {
                "fatigue": round(fatigue, 3),
                "threat": round(threat, 3),
                "proximity": round(proximity, 3),
                "cohesion": round(cohesion, 3),
                "terrain_friction": round(terrain, 3),
            },
            "all_stances": scored,
        }

    def _refresh_principle_bindings(self) -> None:
        """Computes isomorphic unification (같은 인과 -> 같은 원리) vs heteromorphic separation."""
        bindings: List[Dict[str, Any]] = []
        active_doms = list(self.water_pigments.values())
        for i in range(len(active_doms)):
            for j in range(i + 1, len(active_doms)):
                a = active_doms[i]
                b = active_doms[j]
                sim = _cos4(a["spectrum"], b["spectrum"])
                diff_axis_idx = max(range(4), key=lambda k: abs(a["spectrum"][k] - b["spectrum"][k]))
                mid_spec = [0.5 * (a["spectrum"][k] + b["spectrum"][k]) for k in range(4)]
                _, p_label, _ = self._match_principle_archetype(mid_spec)
                is_iso = sim >= 0.90
                bindings.append(
                    {
                        "pair": f"{a['domain']} ⇄ {b['domain']}",
                        "labels": f"{a['label']} ⇄ {b['label']}",
                        "relation": "동형 통합 (같은 원리)" if is_iso else "이형 분화 (독립 축 결속)",
                        "isomorphic": is_iso,
                        "resonance": round(sim, 4),
                        "shared_principle": p_label if is_iso else f"{PRISM_AXES[diff_axis_idx]} 축 분화",
                        "divergence_axis": PRISM_AXES[diff_axis_idx],
                    }
                )
        self.principle_bindings = bindings

    def _rebuild_superposition_grid(self, p_o_mismatch: float, local_thaw_ratio: float) -> None:
        """
        Builds a compact 4×4 (prism_axis × domain) P ∩ O Superposition & Local Thaw matrix
        for the Plane Frame — representing on-demand foveal attention without raw RAM hoarding.
        """
        grid: List[Dict[str, Any]] = []
        active_by_dom = {}
        for u in self.phase_units:
            if u.active:
                active_by_dom.setdefault(u.domain, []).append(u)

        for r_idx, dom in enumerate(DOMAIN_KEYS):
            dom_units = active_by_dom.get(dom, [])
            dom_spec = self.water_pigments.get(dom, {}).get("spectrum", self.water_flow)
            is_split = any(u.depth > 0 for u in dom_units)
            for c_idx, ax in enumerate(PRISM_AXES):
                pred_val = self.cloud_prediction[c_idx]
                obs_val = dom_spec[c_idx]
                delta = abs(obs_val - pred_val)
                # Local thaw check on matching Ice seeds
                thaw = max((s.thaw_mask[c_idx] for s in self.ice_seeds if dom in s.domains), default=0.0)
                state = "thaw" if thaw > 0.18 else ("split" if (is_split and delta > 0.10) else ("uncaptured" if delta > 0.28 else "resonant"))
                grid.append(
                    {
                        "row": r_idx,
                        "col": c_idx,
                        "domain": dom,
                        "axis": ax,
                        "predicted": round(pred_val, 4),
                        "observed": round(obs_val, 4),
                        "delta": round(delta, 4),
                        "thaw": round(thaw, 4),
                        "split_depth": 1 if (is_split and delta > 0.08) else 0,
                        "state": state,
                    }
                )
        self.superposition_grid = grid

    # ------------------------------------------------------------------
    # 5-Frame Projections (Point · Line · Plane · Spacetime Cube · Sphere)
    # ------------------------------------------------------------------
    def _build_five_frame_projections(self) -> Dict[str, Any]:
        # 1. POINT: Condensed principle seeds, cross-domain transfer edges, 1★-7★ singularity
        point_nodes = []
        for idx, seed in enumerate(self.ice_seeds):
            angle = (idx / max(1, len(self.ice_seeds))) * math.tau
            radius = 0.25 + 0.55 * (1.0 - seed.stability * 0.5)
            point_nodes.append(
                {
                    "id": seed.seed_id,
                    "label": seed.label,
                    "principle_key": seed.principle_key,
                    "domains": seed.domains,
                    "stability": round(seed.stability, 4),
                    "thaw_max": round(max(seed.thaw_mask), 4),
                    "world_tier": seed.world_tier,
                    "x": round(math.cos(angle) * radius, 4),
                    "y": round(math.sin(angle) * radius, 4),
                }
            )

        # 2. LINE: Continuous t1~t4 trajectory + Cloud next-step projection
        line_frame = {
            "trajectory": self.trajectory[-24:],
            "cloud_next": [round(x, 4) for x in self.cloud_prediction],
            "cloud_variance": round(self.cloud_variance, 4),
            "cloud_confidence": round(self.cloud_confidence, 4),
        }

        # 3. PLANE: 2D prism spectrum interference palette & P ∩ O foveal superposition
        plane_frame = {
            "grid": self.superposition_grid,
            "active_units": [u.to_dict() for u in self.phase_units if u.active],
            "zero_anchor": [round(x, 4) for x in self.zero_anchor],
            "one_flux": [round(x, 4) for x in self.one_flux],
            "integrated_01": [round(x, 4) for x in self.integrated_01],
        }

        # 4. SPACETIME CUBE: Stacked Past(Ice) -> Present(Water) -> Future(Cloud) slices
        cube_slices = []
        tail = self.trajectory[-6:]
        for idx, rec in enumerate(tail):
            cube_slices.append(
                {
                    "layer": idx,
                    "kind": "ice_past" if idx < len(tail) - 1 else "water_present",
                    "cycle": rec["cycle"],
                    "spectrum": rec["water"],
                    "clarity": rec["clarity"],
                    "thaw": rec["local_thaw_ratio"],
                }
            )
        cube_slices.append(
            {
                "layer": len(cube_slices),
                "kind": "cloud_future",
                "cycle": self.cycle + 1,
                "spectrum": [round(x, 4) for x in self.cloud_prediction],
                "clarity": round(self.cloud_confidence, 4),
                "thaw": 0.0,
            }
        )

        # 5. SPHERE / HYPERSPHERE: Omnidirectional S0..S4 quaternions + 0/1 poles + Uncaptured horizon
        sphere_rotors = []
        for r in self.canonical.scale_rotors:
            sphere_rotors.append(
                {
                    "scale": r.scale,
                    "name": r.name,
                    "gear_ratio": r.gear_ratio,
                    "quaternion": [round(c, 5) for c in r.quaternion],
                    "coherence": round(r.coherence, 4),
                    "tension": round(r.tension, 4),
                    "chromatic": [round(c, 4) for c in r.chromatic],
                }
            )

        return {
            "point": {
                "seeds": point_nodes,
                "bindings": self.principle_bindings,
                "world_tier": self.behavior_state["world_tier"],
                "world_scope": self.behavior_state["world_scope"],
                "ascended_axes": self.ascended_axes,
            },
            "line": line_frame,
            "plane": plane_frame,
            "cube": {
                "slices": cube_slices,
                "time_depth": len(cube_slices),
                "space_axes": list(PRISM_AXES),
            },
            "sphere": {
                "rotors": sphere_rotors,
                "zero_pole": [round(x, 4) for x in self.zero_anchor],
                "one_pole": [round(x, 4) for x in self.one_flux],
                "uncaptured_horizon": [u.to_dict() for u in self.uncaptured_slots],
                "ascended_level": self.ascended_level,
            },
        }

    # ------------------------------------------------------------------
    # Section 7.4 Quantitative Verification & Stress Benchmark
    # ------------------------------------------------------------------
    def run_section_74_benchmark(self) -> Dict[str, Any]:
        """
        Executes Section 7.4 continuous t1~t4 benchmark on an isolated sandbox
        instance (preserving live user ledger):
          1. Compression ratio & drift bound under continuous multi-domain flow
          2. 30%-70% composite noise separation accuracy & auto micro-split trigger
          3. Sudden shock recovery speed (target 3-5 frames) + Ice skeleton preservation
          4. Cross-domain isomorphic unification & heteromorphic differentiation
        """
        bench = UnifiedScaleRotorEngine(ledger_path=None, auto_persist=False)
        base_payload = {
            "vision": {"label": "해안 중력파", "contrast": 0.72, "motion": 0.62, "structure": 0.74, "coherence": 0.78},
            "audio": {"label": "공명 파동", "frequency_norm": 0.64, "amplitude": 0.72, "harmonicity": 0.80, "noise_ratio": 0.08},
            "language": {"text": "파동 에너지 구배가 경계를 따라 공명하며 흐른다 (dE/dt = -k*grad)"},
            "behavior": {"fatigue": 0.22, "threat": 0.26, "proximity": 0.52, "cohesion": 0.76, "terrain_friction": 0.30},
            "noise_ratio": 0.0,
        }

        # Phase A: Normal continuous flow (6 cycles) -> compression & drift
        compressions = []
        drifts = []
        for _ in range(6):
            st = bench.step_t1_to_t4(base_payload)
            compressions.append(st["discrimination"]["compression_ratio"])
            drifts.append(st["discrimination"]["drift"])
        mean_compression = sum(compressions) / len(compressions)
        max_drift = max(drifts)

        # Phase B: 30% -> 50% -> 70% composite noise injection
        noise_scores = []
        auto_split_fired = False
        for nr in (0.30, 0.50, 0.70):
            noisy = dict(base_payload, noise_ratio=nr)
            st = bench.step_t1_to_t4(noisy)
            noise_scores.append(
                {
                    "noise_ratio": nr,
                    "clarity": st["discrimination"]["clarity"],
                    "saturation": st["discrimination"]["saturation"],
                    "luminance": st["discrimination"]["luminance"],
                    "noise_rejection": st["discrimination"]["noise_rejection"],
                    "auto_splits": int(st["discrimination"]["auto_split_triggered"]),
                }
            )
            if st["discrimination"]["auto_split_triggered"] > 0:
                auto_split_fired = True
        mean_noise_rejection = sum(x["noise_rejection"] for x in noise_scores) / len(noise_scores)

        # Phase C: Sudden unexpected shock -> partial Ice thaw & 3-5 frame recovery
        ice_before = len(bench.ice_seeds)
        shock_state = bench.step_t1_to_t4(
            dict(base_payload, shock={"strength": 0.85, "spectrum": [0.12, 0.94, 0.96, 0.18]})
        )
        thaw_peak = shock_state["discrimination"]["local_thaw_ratio"]
        uncaptured_on_shock = len(shock_state["phases"]["uncaptured"])

        recovery_frames = 0
        recovered = False
        for f in range(1, 7):
            st = bench.step_t1_to_t4(base_payload)
            recovery_frames = f
            if st["discrimination"]["clarity"] >= 0.72 and st["discrimination"]["local_thaw_ratio"] < 0.25:
                recovered = True
                break
        ice_after = len(bench.ice_seeds)
        mean_ice_stability = sum(s.stability for s in bench.ice_seeds) / max(1, len(bench.ice_seeds))

        # Phase D: Isomorphic vs Heteromorphic cross-domain check
        iso_st = bench.step_t1_to_t4(
            {
                "vision": {"label": "수면 파동", "contrast": 0.68, "motion": 0.76, "structure": 0.64, "coherence": 0.82},
                "audio": {"label": "조화 음파", "frequency_norm": 0.72, "amplitude": 0.70, "harmonicity": 0.84, "noise_ratio": 0.05},
                "language": {"text": "파동 진동이 공명하며 흐른다 wave = sin(wt - kx)"},
            }
        )
        iso_count = sum(1 for b in iso_st["principle_bindings"] if b["isomorphic"])

        hetero_st = bench.step_t1_to_t4(
            {
                "vision": {"label": "정적 결정 격자", "contrast": 0.94, "motion": 0.04, "structure": 0.96, "coherence": 0.92},
                "behavior": {"label": "극한 난류 산개", "fatigue": 0.88, "threat": 0.94, "proximity": 0.90, "cohesion": 0.12, "terrain_friction": 0.86},
            }
        )
        hetero_count = sum(1 for b in hetero_st["principle_bindings"] if not b["isomorphic"])

        passed = (
            mean_compression >= 1.5
            and max_drift <= 0.35
            and mean_noise_rejection >= 0.55
            and auto_split_fired
            and recovered
            and recovery_frames <= 5
            and thaw_peak > 0.05
            and mean_ice_stability >= 0.65
            and iso_count >= 1
            and hetero_count >= 1
        )

        return {
            "status": "ok",
            "verdict": "PASS" if passed else "TUNE",
            "summary": {
                "mean_compression_ratio": round(mean_compression, 2),
                "max_drift": round(max_drift, 4),
                "mean_noise_rejection": round(mean_noise_rejection, 4),
                "auto_split_on_noise_fired": auto_split_fired,
                "shock_local_thaw_peak": round(thaw_peak, 4),
                "uncaptured_slots_on_shock": uncaptured_on_shock,
                "shock_recovery_frames": recovery_frames,
                "shock_recovered_within_5_frames": recovered and recovery_frames <= 5,
                "ice_skeleton_preserved": ice_after >= ice_before and mean_ice_stability >= 0.65,
                "mean_ice_stability": round(mean_ice_stability, 4),
                "isomorphic_unified_pairs": iso_count,
                "heteromorphic_separated_pairs": hetero_count,
            },
            "noise_trials": noise_scores,
        }

    # ------------------------------------------------------------------
    # Full Canonical State Snapshot
    # ------------------------------------------------------------------
    def get_state_snapshot(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "engine": "L1_Canonical_ScaleRotor_Python",
            "cycle": self.cycle,
            "active_stage": self.active_stage,
            "active_frame": self.active_frame,
            "scale_dial": round(self.canonical.scale_dial, 4),
            "ledger_synced": bool(self.ledger_path and self.ledger_path.exists()),
            "helix": {
                "zero_anchor": [round(x, 4) for x in self.zero_anchor],
                "one_flux": [round(x, 4) for x in self.one_flux],
                "integrated_01": [round(x, 4) for x in self.integrated_01],
                "coherence_01": round(_cos4(self.zero_anchor, self.one_flux), 4),
                "homophase_zero_energy": round(self.homophase_zero_energy, 4),
                "homophase_one_energy": round(self.homophase_one_energy, 4),
                "ascended_level": self.ascended_level,
                "ascended_axes": self.ascended_axes,
            },
            "prism_axes": list(PRISM_AXES),
            "discrimination": self.discrimination,
            "phases": {
                "ice": [s.to_dict() for s in self.ice_seeds],
                "water": {
                    "spectrum": [round(x, 4) for x in self.water_flow],
                    "active_pigments": {
                        k: {
                            "label": v["label"],
                            "spectrum": [round(x, 4) for x in v["spectrum"]],
                        }
                        for k, v in self.water_pigments.items()
                    },
                },
                "cloud": {
                    "predicted_spectrum": [round(x, 4) for x in self.cloud_prediction],
                    "variance": round(self.cloud_variance, 4),
                    "confidence": round(self.cloud_confidence, 4),
                },
                "uncaptured": [u.to_dict() for u in self.uncaptured_slots],
            },
            "phase_units": [u.to_dict() for u in self.phase_units],
            "self_boundary": self.self_boundary,
            "principle_bindings": self.principle_bindings,
            "behavior": self.behavior_state,
            "frames": self._build_five_frame_projections(),
        }


def _handle_rpc_request(engine: UnifiedScaleRotorEngine, req: Dict[str, Any]) -> Dict[str, Any]:
    action = str(req.get("action", "state"))
    payload = req.get("payload") if isinstance(req.get("payload"), dict) else {}
    if action == "state":
        return engine.get_state_snapshot()
    if action == "step":
        return engine.step_t1_to_t4(payload)
    if action == "frame":
        frame = str(payload.get("frame", "plane"))
        if frame in ("point", "line", "plane", "cube", "sphere"):
            engine.active_frame = frame
        return engine.get_state_snapshot()
    if action == "benchmark":
        return engine.run_section_74_benchmark()
    if action == "observe_contrast":
        from core.orchestration.process_contrast_observer import run_empirical_contrast_suite

        return run_empirical_contrast_suite(
            engine=engine,
            lens_mode=str(payload.get("lens_mode", "strict")),
            epsilon=payload.get("epsilon"),
            code_source=payload.get("code_source"),
            geom_op=str(payload.get("geom_op", "rigid_rotate")),
            angle_deg=float(payload.get("angle_deg", 37.0)),
            shift_x=int(payload.get("shift_x", 2)),
            shift_y=int(payload.get("shift_y", 1)),
        )
    if action == "observe_external_snapshot":
        from core.orchestration.process_contrast_observer import observe_external_snapshot

        return observe_external_snapshot(
            system_name=str(payload.get("system_name", "External Process")),
            before_state=payload.get("before_state"),
            after_state=payload.get("after_state"),
            operation=str(payload.get("operation", "외부 상태 전이")),
            lens_mode=str(payload.get("lens_mode", "strict")),
            epsilon=payload.get("epsilon"),
        )
    if action == "flush_ledger":
        engine.save_ledger()
        return engine.get_state_snapshot()
    if action == "observe_vessel_trajectory":
        from core.orchestration.vessel_trajectory_rotor import VesselTrajectoryRotor

        if engine.vessel_rotor is None:
            engine.vessel_rotor = VesselTrajectoryRotor(max_snapshots=24)

        mode = str(payload.get("mode", "capture_tick")).strip().lower()
        lens_mode = str(payload.get("lens_mode", "strict"))
        epsilon = payload.get("epsilon")
        node_vessel = payload.get("node_vessel") if isinstance(payload.get("node_vessel"), dict) else None
        label = str(payload.get("label", mode))

        if mode == "clear_trajectory":
            engine.vessel_rotor.clear()
            report = engine.vessel_rotor.analyze(lens_mode=lens_mode, epsilon=epsilon)
            report["rotor_state"] = engine.get_state_snapshot()
            return report

        if mode == "unflushed_memory_probe":
            # Execute 1 real in-memory t1~t4 transition WITHOUT flushing to disk so RAM vs Disk divergence is genuinely observed
            prev_persist = engine.auto_persist
            engine.auto_persist = False
            try:
                engine.step_t1_to_t4(
                    {
                        "language": {
                            "label": "메모리 전용 프로브 (디스크 미반영)",
                            "text": f"메모리 선행 상태 전이 probe cycle={engine.cycle + 1}",
                        },
                        "vision": {
                            "label": "그릇 위상차 프로브",
                            "structure": 0.72,
                            "contrast": 0.68,
                            "motion": 0.64,
                            "coherence": 0.79,
                        },
                    }
                )
            finally:
                engine.auto_persist = prev_persist
            engine.vessel_rotor.capture(engine, node_vessel=node_vessel, label=label or "unflushed_memory_probe")
            report = engine.vessel_rotor.analyze(lens_mode=lens_mode, epsilon=epsilon)
            report["rotor_state"] = engine.get_state_snapshot()
            return report

        if mode == "inspect_only":
            report = engine.vessel_rotor.analyze(lens_mode=lens_mode, epsilon=epsilon)
            report["rotor_state"] = engine.get_state_snapshot()
            return report

        # Default: capture_tick
        engine.vessel_rotor.capture(engine, node_vessel=node_vessel, label=label)
        report = engine.vessel_rotor.analyze(lens_mode=lens_mode, epsilon=epsilon)
        report["rotor_state"] = engine.get_state_snapshot()
        return report
    if action == "observe_phase_sync":
        from core.orchestration.bidirectional_phase_sync import run_bidirectional_phase_sync_suite

        report = run_bidirectional_phase_sync_suite(
            engine=engine,
            node_vessel=payload.get("node_vessel") if isinstance(payload.get("node_vessel"), dict) else None,
            angle_b_deg=float(payload.get("angle_b_deg", 42.0)),
            clock_rate_b=float(payload.get("clock_rate_b", 1.5)),
            phase_lag_b=float(payload.get("phase_lag_b", 0.65)),
            lens_a_mode=str(payload.get("lens_a_mode", "strict")),
            lens_b_mode=str(payload.get("lens_b_mode", "tolerant")),
        )
        report["rotor_state"] = engine.get_state_snapshot()
        return report
    if action == "digest_imitate_recreate":
        from core.orchestration.digest_imitate_recreate import run_digest_imitate_recreate

        return run_digest_imitate_recreate(
            engine=engine,
            original_id=str(payload.get("original_id", "damped_harmonic")),
            partner_id=str(payload.get("partner_id", "wave_forcing")),
            custom_formula=payload.get("custom_formula"),
            lens_mode=str(payload.get("lens_mode", "strict")),
            epsilon=payload.get("epsilon"),
            max_rounds=int(payload.get("max_rounds", 3)),
        )
    if action == "unified_dataflow":
        from core.orchestration.unified_dataflow_engine import run_unified_dataflow_cycle

        return run_unified_dataflow_cycle(
            engine=engine,
            preset_id=str(payload.get("preset_id", "wave_interference")),
            code_source=payload.get("code_source"),
            gate_steepness=float(payload.get("gate_steepness", 14.0)),
            wake_threshold=float(payload.get("wake_threshold", 0.16)),
            audio_harmonics=int(payload.get("audio_harmonics", 6)),
            t_phase=payload.get("t_phase"),
            auto_optimize=bool(payload.get("auto_optimize", False)),
        )
    if action == "companion_state":
        from core.orchestration.living_companion_field import handle_companion_state

        return handle_companion_state()
    if action == "companion_converse":
        from core.orchestration.living_companion_field import handle_companion_converse

        return handle_companion_converse(
            engine=engine,
            message=str(payload.get("message", "")),
        )
    if action == "companion_digest":
        from core.orchestration.living_companion_field import handle_companion_digest

        return handle_companion_digest(
            engine=engine,
            source_name=str(payload.get("source_name", "직접 입력한 글")),
            text=str(payload.get("text", "")),
            read_workspace=bool(payload.get("read_workspace", False)),
        )
    if action == "companion_digest_corpus":
        from core.orchestration.living_companion_field import handle_companion_digest_corpus

        return handle_companion_digest_corpus(
            engine=engine,
            digest=payload.get("digest") if isinstance(payload.get("digest"), dict) else None,
            scan_workspace=bool(payload.get("scan_workspace", False)),
        )
    if action == "companion_scanner_script":
        from core.orchestration.local_corpus_extractor import render_standalone_scanner_script

        return {"status": "ok", "script": render_standalone_scanner_script()}
    if action == "companion_observe_frame":
        from core.orchestration.living_companion_field import handle_companion_observe_frame

        return handle_companion_observe_frame(
            engine=engine,
            frame=payload.get("frame") if isinstance(payload.get("frame"), dict) else payload,
        )
    if action == "companion_digest_sensorimotor":
        from core.orchestration.living_companion_field import handle_companion_digest_sensorimotor

        return handle_companion_digest_sensorimotor(
            engine=engine,
            log=payload.get("log") if isinstance(payload.get("log"), dict) else payload,
        )
    if action == "companion_embodiment_script":
        from core.orchestration.desktop_embodiment import render_desktop_embodiment_script

        return {"status": "ok", "script": render_desktop_embodiment_script()}
    if action == "companion_sandbox_action":
        from core.orchestration.living_companion_field import handle_companion_sandbox_action

        return handle_companion_sandbox_action(
            engine=engine,
            app=str(payload.get("app", "desktop")),
            action=str(payload.get("action", "explore")),
            target=str(payload.get("target", "")),
            outcome=str(payload.get("outcome", "")),
            delta=float(payload.get("delta", 0.25)),
            note_text=str(payload.get("note_text", "")),
            metrics=payload.get("metrics") if isinstance(payload.get("metrics"), dict) else None,
        )
    if action == "companion_rotor_mode":
        from core.orchestration.living_companion_field import handle_companion_rotor_mode

        return handle_companion_rotor_mode(
            paused=payload.get("paused") if "paused" in payload else None,
            burst_trials=int(payload.get("burst_trials", 0)),
        )
    if action == "companion_apply_tool":
        from core.orchestration.living_companion_field import handle_companion_apply_tool

        return handle_companion_apply_tool(
            target_text=str(payload.get("target_text", "")),
            tool_id=str(payload.get("tool_id", "")) or None,
        )
    if action == "companion_learn_world":
        from core.orchestration.living_companion_field import handle_companion_learn_world

        return handle_companion_learn_world(
            topic=str(payload.get("topic", "")),
        )
    if action == "companion_distill_weights":
        from core.orchestration.living_companion_field import handle_companion_distill_weights

        wv = payload.get("weight_vectors")
        return handle_companion_distill_weights(
            source_name=str(payload.get("source_name", "오픈 가중치 슬라이스")),
            weight_vectors=wv if isinstance(wv, dict) else None,
        )
    if action == "companion_feedback":
        from core.orchestration.living_companion_field import handle_companion_feedback

        return handle_companion_feedback(
            signal=str(payload.get("signal", "resonate")),
            correction=str(payload.get("correction", "")),
        )
    if action == "companion_reset":
        from core.orchestration.living_companion_field import handle_companion_reset

        return handle_companion_reset()
    if action == "reset":
        return engine.reset_state(clear_ledger=bool(payload.get("clear_ledger", False)))
    if action == "recall_seed":
        seed_id = str(payload.get("seed_id", ""))
        found = next((s for s in engine.ice_seeds if s.seed_id == seed_id), None)
        if found is None:
            return {"status": "error", "message": f"Ice seed not found: {seed_id}"}
        # On-demand archetype restoration: re-inject seed into t1~t4 without hoarding raw data
        return engine.step_t1_to_t4(
            {
                "language": {"label": f"얼음 원형 복원: {found.label}", "text": found.label},
                "vision": {
                    "label": f"복원 스펙트럼({found.principle_key})",
                    "structure": found.spectrum[0],
                    "coherence": found.spectrum[3],
                    "motion": found.spectrum[2],
                    "contrast": found.spectrum[1],
                },
            }
        )
    return {"status": "error", "message": f"Unknown action: {action}"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Elysia L1 Unified Scale-Rotor Core Worker")
    parser.add_argument("--worker", action="store_true", help="Run persistent NDJSON stdio RPC worker")
    parser.add_argument("--action", default="state", help="One-shot action: state|step|benchmark|reset")
    parser.add_argument("--ledger", default="", help="Optional custom persistent Ice ledger JSON path")
    args = parser.parse_args()

    ledger = Path(args.ledger).resolve() if args.ledger else None
    engine = UnifiedScaleRotorEngine(ledger_path=ledger, auto_persist=True)

    if args.worker:
        try:
            from core.orchestration.living_companion_field import start_companion_background_rotor

            start_companion_background_rotor()
        except Exception:
            pass
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            req_id = None
            try:
                msg = json.loads(line)
                req_id = msg.get("id")
                result = _handle_rpc_request(engine, msg)
                out = {"id": req_id, "ok": True, "result": result}
            except Exception as exc:
                out = {"id": req_id, "ok": False, "error": str(exc)}
            sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
            sys.stdout.flush()
        return 0

    result = _handle_rpc_request(engine, {"action": args.action})
    sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
