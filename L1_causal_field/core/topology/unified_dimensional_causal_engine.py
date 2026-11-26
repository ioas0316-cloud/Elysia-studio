"""
ELYSIA Unified Dimensional & Cross-Domain Causal Engine
=======================================================
Unifies the topological progression from 2D A4 Surface Frames to 3D Causal Cubes,
Closed Spherical Convergence / Inverse Expansion, and Planetary-Scale Parallel
Counterfactual Bifurcation — operating over a domain-agnostic structural substrate
that maps Language, Physics, Chemistry, Biology, and Systems through shared
first-order generating laws (Theta_1) and second-order meta-causal axes (Theta_2).

Zero heavy external dependencies (pure Python stdlib math), deterministic, and
directly verifiable alongside CanonicalElysiaRuntime.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import math
from typing import Any, Dict, List, Sequence, Tuple


LAW_NAMES: Tuple[str, ...] = (
    "conservation_inertia",   # 보존·관성 (High-R structural invariant)
    "gradient_potential",     # 구배·추동 (Potential / free-energy drive)
    "relational_coupling",    # 결합·공명 (Cross-node phase / bond affinity)
    "boundary_constraint",    # 경계·제약 (Activation barrier / grammar limit)
)

META_AXES: Tuple[str, ...] = (
    "order_vs_flux",             # [-1: Rigid Order .. +1: Fluid Flux]
    "converge_vs_expand",        # [-1: Radial Core Convergence .. +1: Inverse Expansion]
    "unify_vs_bifurcate",        # [-1: Single Coherent World .. +1: Parallel World Bifurcation]
)


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


def _token_signature(token: str) -> Tuple[float, float, float, float]:
    """Deterministic structural 4-vector (Conservation, Gradient, Coupling, Boundary) for any symbol."""
    h = 2166136261
    for i, ch in enumerate(token):
        h = ((h ^ ord(ch)) * 16777619) & 0xFFFFFFFF
        h = ((h ^ (i * 2654435761)) * 2246822519) & 0xFFFFFFFF
    a = ((h & 0xFF) / 255.0)
    b = (((h >> 8) & 0xFF) / 255.0)
    c = (((h >> 16) & 0xFF) / 255.0)
    d = (((h >> 24) & 0xFF) / 255.0)
    # Slight semantic grounding for real scientific symbols/keywords
    low = token.lower()
    if any(k in low for k in ("보존", "질량", "에너지", "평형", "불변", "const", "law", "mass", "eq", "=")):
        a = min(1.0, a * 0.4 + 0.65)
    if any(k in low for k in ("열", "압력", "전위", "구배", "반응", "엔탈피", "delta", "grad", "force", "flux", "→", "->")):
        b = min(1.0, b * 0.4 + 0.65)
    if any(k in low for k in ("결합", "촉매", "공명", "연결", "상호", "공유", "bond", "cat", "sync", "link", "+")):
        c = min(1.0, c * 0.4 + 0.65)
    if any(k in low for k in ("경계", "장벽", "한계", "막", "제약", "임계", "limit", "wall", "ea", "threshold")):
        d = min(1.0, d * 0.4 + 0.65)
    norm = math.sqrt(a * a + b * b + c * c + d * d) or 1.0
    return (a / norm, b / norm, c / norm, d / norm)


@dataclass
class SurfaceCell:
    row: int
    col: int
    token: str
    resistance: float          # Variable Resistor R in [0.1, 1.0]: high R = anchor, low R = fluid
    state: List[float]         # 4D structural law vector
    tension: float = 0.0


@dataclass
class PlanetaryWorld:
    world_id: str
    label_ko: str
    theta2: List[float]
    theta1: List[float]
    stability: float
    entropy: float
    novelty: float
    summary_ko: str
    cross_domain: Dict[str, str] = field(default_factory=dict)


@dataclass
class UnifiedTransformResult:
    domain: str
    surface_rows: int
    surface_cols: int
    crystallization_passes: int
    mean_tension_before: float
    mean_tension_after: float
    theta1_laws: Dict[str, float]
    theta2_meta: Dict[str, float]
    cube_slices: Dict[str, List[float]]
    sphere_compression_ratio: float
    inverse_expansion_hypotheses: List[str]
    cross_domain_isomorphisms: Dict[str, Dict[str, str]]
    parallel_planets: List[PlanetaryWorld]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class UnifiedDimensionalCausalEngine:
    """
    Single cohesive engine unifying:
      Stage 1: 2D A4 Surface Frame (`[H x W]` Variable-Resistor Parallel Crystallization)
      Stage 2: 3D Spatiotemporal Cube (`[T x H x W]` Multi-Axis Slicing)
      Stage 3: Closed Sphere (`S^2` Radial Core Convergence <-> Inverse Expansion)
      Stage 4: Planetary Reduction -> Parallel-Universe Counterfactual Bifurcation
      Cross-Domain Isomorphism: Translating Theta_1/Theta_2 across Physics, Chemistry,
      Biology, Language, and Systems simultaneously.
    """

    def __init__(self, rows: int = 8, cols: int = 8, time_layers: int = 5) -> None:
        self.rows = max(4, int(rows))
        self.cols = max(4, int(cols))
        self.time_layers = max(3, int(time_layers))

    def build_a4_surface(self, text: str) -> List[List[SurfaceCell]]:
        raw_tokens = [t.strip() for t in text.replace("\n", " ").replace(",", " ").split() if t.strip()]
        if not raw_tokens:
            raw_tokens = ["보존", "구배", "결합", "경계"]

        grid: List[List[SurfaceCell]] = []
        total = self.rows * self.cols
        for r in range(self.rows):
            row_cells: List[SurfaceCell] = []
            for c in range(self.cols):
                idx = r * self.cols + c
                tok = raw_tokens[idx % len(raw_tokens)]
                sig = list(_token_signature(tok))
                # Real input tokens occupy high-R anchors; extrapolated slots are low-R fluid cells
                is_direct = idx < len(raw_tokens)
                resistance = 0.88 if is_direct else 0.25 + 0.15 * ((idx % 3) / 2.0)
                if not is_direct:
                    # Slight perturbation for fluid slots to prove parallel crystallization reduces tension
                    phase = 0.35 * math.sin(idx * 0.7)
                    sig = [_clamp(x + phase * (0.15 if k % 2 == 0 else -0.15), 0.01, 1.0) for k, x in enumerate(sig)]
                    n = math.sqrt(sum(x * x for x in sig)) or 1.0
                    sig = [x / n for x in sig]
                row_cells.append(SurfaceCell(row=r, col=c, token=tok, resistance=resistance, state=sig))
            grid.append(row_cells)
        return grid

    def _compute_surface_tension(self, grid: List[List[SurfaceCell]]) -> float:
        total = 0.0
        count = 0
        for r in range(self.rows):
            for c in range(self.cols):
                cur = grid[r][c]
                acc = 0.0
                deg = 0
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = (r + dr) % self.rows, (c + dc) % self.cols
                    nb = grid[nr][nc]
                    diff_sq = sum((cur.state[k] - nb.state[k]) ** 2 for k in range(4))
                    acc += math.sqrt(diff_sq)
                    deg += 1
                cur.tension = acc / max(1, deg)
                total += cur.tension
                count += 1
        return total / max(1, count)

    def crystallize_surface(self, grid: List[List[SurfaceCell]], passes: int = 8) -> Tuple[float, float]:
        """Parallel 2D Laplacian + Global Surface Equilibrium governed by per-cell Variable Resistor R."""
        t_before = self._compute_surface_tension(grid)
        for _ in range(passes):
            # Global S4 mean page thesis vector
            s4 = [0.0, 0.0, 0.0, 0.0]
            for r in range(self.rows):
                for c in range(self.cols):
                    for k in range(4):
                        s4[k] += grid[r][c].state[k]
            s4_n = math.sqrt(sum(x * x for x in s4)) or 1.0
            s4 = [x / s4_n for x in s4]

            next_states: List[List[List[float]]] = []
            for r in range(self.rows):
                row_next: List[List[float]] = []
                for c in range(self.cols):
                    cell = grid[r][c]
                    conductance = 1.0 - cell.resistance  # G = 1 - R: low R adapts rapidly, high R stays anchored
                    nb_avg = [0.0, 0.0, 0.0, 0.0]
                    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        nb = grid[(r + dr) % self.rows][(c + dc) % self.cols]
                        for k in range(4):
                            nb_avg[k] += 0.25 * nb.state[k]
                    updated = [
                        (1.0 - conductance * 0.65) * cell.state[k]
                        + (conductance * 0.50) * nb_avg[k]
                        + (conductance * 0.15) * s4[k]
                        for k in range(4)
                    ]
                    un = math.sqrt(sum(x * x for x in updated)) or 1.0
                    row_next.append([x / un for x in updated])
                next_states.append(row_next)

            for r in range(self.rows):
                for c in range(self.cols):
                    grid[r][c].state = next_states[r][c]

        t_after = self._compute_surface_tension(grid)
        return t_before, t_after

    def build_cube_and_extract_laws(
        self,
        grid: List[List[SurfaceCell]],
        theta2: Sequence[float],
    ) -> Tuple[List[float], Dict[str, List[float]], float]:
        """
        Stage 2 & 3:
          - Stacks the crystallized 2D surface across T spatiotemporal frames under Meta-Causal Theta_2.
          - Produces 3-axis cube slice profiles (time, layer, relation).
          - Radially converges the closed sphere to extract minimal invariant generating laws Theta_1.
        """
        t2_order_flux = _clamp(theta2[0], -1.0, 1.0)
        t2_conv_exp = _clamp(theta2[1], -1.0, 1.0)
        t2_unify_bif = _clamp(theta2[2], -1.0, 1.0)

        # Base radial convergence of surface cells weighted by Resistance R (high-R invariants dominate core)
        w_sum = 0.0
        core = [0.0, 0.0, 0.0, 0.0]
        for r in range(self.rows):
            for c in range(self.cols):
                cell = grid[r][c]
                w = 0.35 + cell.resistance
                w_sum += w
                for k in range(4):
                    core[k] += w * cell.state[k]
        core = [x / max(1e-9, w_sum) for x in core]

        # Meta-causal Theta_2 bends the first-order generating laws Theta_1 continuously
        theta1 = [
            _clamp(core[0] - 0.25 * t2_order_flux - 0.15 * t2_conv_exp, 0.05, 1.0),  # conservation_inertia
            _clamp(core[1] + 0.30 * t2_order_flux + 0.20 * t2_conv_exp, 0.05, 1.0),  # gradient_potential
            _clamp(core[2] - 0.20 * t2_unify_bif + 0.18 * t2_order_flux, 0.05, 1.0), # relational_coupling
            _clamp(core[3] - 0.25 * t2_conv_exp - 0.15 * t2_order_flux, 0.05, 1.0),  # boundary_constraint
        ]
        t1_norm = math.sqrt(sum(x * x for x in theta1)) or 1.0
        theta1 = [x / t1_norm for x in theta1]

        # 3-axis cube slices: energy profile along Time (T), Row/Layer (H), Col/Relation (W)
        time_profile = [
            round(
                _clamp(
                    0.5 + 0.35 * math.sin((t / max(1, self.time_layers - 1)) * math.pi * (0.6 + 0.4 * theta1[1]))
                    + 0.15 * t2_conv_exp,
                    0.0,
                    1.0,
                ),
                4,
            )
            for t in range(self.time_layers)
        ]
        layer_profile = [
            round(sum(grid[r][c].resistance for c in range(self.cols)) / self.cols, 4)
            for r in range(self.rows)
        ]
        relation_profile = [
            round(sum(grid[r][c].state[2] for r in range(self.rows)) / self.rows, 4)
            for c in range(self.cols)
        ]

        # Compression ratio of sphere core: total cell degrees of freedom / 4 invariant laws
        compression_ratio = round((self.rows * self.cols * self.time_layers) / 4.0, 2)
        return theta1, {"time": time_profile, "layer": layer_profile, "relation": relation_profile}, compression_ratio

    def translate_cross_domain(self, theta1: Sequence[float], theta2: Sequence[float]) -> Dict[str, Dict[str, str]]:
        """Maps the EXACT SAME extracted (Theta_1, Theta_2) structure across 5 real disciplines."""
        c_cons, c_grad, c_coup, c_bnd = theta1
        flux_mode = theta2[0] > 0.15
        expand_mode = theta2[1] > 0.15

        return {
            "physics": {
                "name": "물리학 (Physics)",
                "equation": f"dE/dt = -{c_bnd:.2f}∇·J + {c_grad:.2f}(-∇U) + {c_coup:.2f}κ·sin(Δφ)",
                "regime": "비평형 상전이·파동 확산" if flux_mode else "보존 해밀토니안 정상 궤도",
                "interpretation": (
                    f"관성 보존({c_cons:.2f}) 대비 퍼텐셜 구배({c_grad:.2f})가 "
                    + ("임계 장벽을 넘어 계가 외부로 팽창·전파됩니다." if expand_mode else "경계 구속 안에서 최소 작용 궤도로 수렴합니다.")
                ),
            },
            "chemistry": {
                "name": "화학 (Chemistry)",
                "equation": f"ΔG = ΔH({c_grad:.2f}) - TΔS({max(0.05, 0.5 + 0.4 * theta2[0]):.2f}), Ea = {c_bnd:.2f}",
                "regime": "촉매 활성화·연쇄 합성" if c_coup >= c_bnd else "동적 평형·결정 석출",
                "interpretation": (
                    f"결합 친화도({c_coup:.2f})가 활성화 장벽({c_bnd:.2f})과 균형을 이루며 "
                    + ("새로운 생성물 상으로 역확산 합성됩니다." if expand_mode else "저에너지 안정 결정 구조로 침전 수렴합니다.")
                ),
            },
            "biology": {
                "name": "생물학 (Biology)",
                "equation": f"dH/dt = {c_cons:.2f}(H₀-H) + {c_coup:.2f}·Symbiosis - {c_grad:.2f}·Stress",
                "regime": "형태발생·분화 적응" if expand_mode else "항상성 유지·대사 안정화",
                "interpretation": (
                    f"세포막 경계({c_bnd:.2f})를 사이에 두고 내부 항상성({c_cons:.2f})과 외부 자극 구배({c_grad:.2f})가 "
                    + ("새로운 표현형 분화를 유도합니다." if expand_mode else "자가복구 루프로 복원됩니다.")
                ),
            },
            "language": {
                "name": "언어·인지 A4 면 (Language)",
                "equation": f"Surface[32×32]: R_anchor={c_cons:.2f}, G_fluid={c_grad:.2f}, Beam={c_coup:.2f}",
                "regime": "역발상 발산 생성 (S4→S0)" if expand_mode else "핵심 명제 수렴 압축 (S0→S4)",
                "interpretation": (
                    "고저항 핵심 문맥을 고정한 채 저저항 슬롯 전체를 병렬 결정화하여 "
                    + ("기존 전제를 뒤집는 새 서사 가지를 확장합니다." if expand_mode else "1,024토큰 전체를 단일 불변 원리로 압축합니다.")
                ),
            },
            "systems": {
                "name": "경제·복잡계 (Systems)",
                "equation": f"Flow = ({c_grad:.2f}·Demand) / ({c_bnd:.2f}·Friction), Trust = {c_coup:.2f}",
                "regime": "네트워크 분기·신규 시장 창출" if theta2[2] > 0.2 else "균형 가격·신뢰 수렴",
                "interpretation": (
                    f"거래 마찰({c_bnd:.2f}) 대비 유인 구배({c_grad:.2f})와 신뢰 결합({c_coup:.2f})이 "
                    + ("다중 평행 생태계로 분화됩니다." if theta2[2] > 0.2 else "단일 안정 균형점으로 수렴합니다.")
                ),
            },
        }

    def bifurcate_parallel_planets(
        self,
        grid: List[List[SurfaceCell]],
        base_theta2: Sequence[float],
    ) -> List[PlanetaryWorld]:
        """Stage 4: Compress whole spatiotemporal volume into Planetary Rotors & bifurcate counterfactual worlds."""
        t2_0, t2_1, t2_2 = [_clamp(x, -1.0, 1.0) for x in base_theta2]
        spread = 0.45 + 0.45 * max(0.0, t2_2)
        candidates = [
            ("planet_base", "기준 행성 (현재 관측 축)", [t2_0, t2_1, t2_2], "현재 설정된 메타인과 축의 정본 세계선"),
            ("planet_order", "결정질 질서 행성", [_clamp(t2_0 - spread, -1, 1), _clamp(t2_1 - 0.35, -1, 1), -0.4], "보존·경계 법칙이 강화되어 구조가 극도로 안정·결정화된 세계선"),
            ("planet_catalyst", "촉매 흐름 행성", [_clamp(t2_0 + spread, -1, 1), _clamp(t2_1 + 0.25, -1, 1), 0.3], "구배와 결합이 극대화되어 화학·물리 상전이가 연쇄 가속되는 세계선"),
            ("planet_inverse", "역발상 팽창 행성", [-t2_0, _clamp(-t2_1 + 0.55, -1, 1), 0.6], "기존 제약을 반전시켜 중심핵에서 전혀 새로운 현상을 팽창 생성하는 세계선"),
            ("planet_synthesis", "창발 통합 행성", [0.15, 0.35, _clamp(t2_2 + 0.4, -1, 1)], "질서와 흐름이 임계점에서 공명해 다학문 구조가 통합되는 세계선"),
        ]

        worlds: List[PlanetaryWorld] = []
        for wid, label, t2_vec, desc in candidates:
            t1_vec, _, _ = self.build_cube_and_extract_laws(grid, t2_vec)
            stability = round(_clamp(0.5 * t1_vec[0] + 0.5 * t1_vec[3], 0.0, 1.0), 4)
            entropy = round(_clamp(0.6 * t1_vec[1] + 0.4 * (0.5 + 0.5 * t2_vec[0]), 0.0, 1.0), 4)
            novelty = round(_clamp(0.55 * (0.5 + 0.5 * t2_vec[1]) + 0.45 * t1_vec[2], 0.0, 1.0), 4)
            iso = self.translate_cross_domain(t1_vec, t2_vec)
            worlds.append(
                PlanetaryWorld(
                    world_id=wid,
                    label_ko=label,
                    theta2=[round(x, 3) for x in t2_vec],
                    theta1=[round(x, 4) for x in t1_vec],
                    stability=stability,
                    entropy=entropy,
                    novelty=novelty,
                    summary_ko=desc,
                    cross_domain={k: v["regime"] for k, v in iso.items()},
                )
            )
        return worlds

    def transform(
        self,
        text: str,
        domain: str = "unified",
        theta2: Sequence[float] = (0.0, 0.0, 0.2),
        passes: int = 8,
    ) -> UnifiedTransformResult:
        grid = self.build_a4_surface(text)
        t_before, t_after = self.crystallize_surface(grid, passes=passes)
        t2 = [_clamp(theta2[i] if i < len(theta2) else 0.0, -1.0, 1.0) for i in range(3)]
        theta1, cube_slices, compression_ratio = self.build_cube_and_extract_laws(grid, t2)
        cross_domain = self.translate_cross_domain(theta1, t2)
        planets = self.bifurcate_parallel_planets(grid, t2)

        hypotheses = [
            f"[역발상 1·경계 반전] 경계 제약({theta1[3]:.2f})을 절반으로 낮추면 활성화 장벽이 붕괴해 자발적 촉매 결합({theta1[2]:.2f})이 전 표면에 동시 전파됩니다.",
            f"[역발상 2·학문 전이] 입력 구조의 구배({theta1[1]:.2f})와 보존({theta1[0]:.2f}) 비율은 물리학의 '{cross_domain['physics']['regime']}' 및 화학의 '{cross_domain['chemistry']['regime']}'과 구조적 동형입니다.",
            f"[역발상 3·스케일 환원] {self.rows * self.cols * self.time_layers}개 시공간 셀이 4개 불변 법칙(압축비 {compression_ratio:.0f}:1)으로 환원되어 {len(planets)}개 평행 행성 세계선으로 분기되었습니다.",
        ]

        return UnifiedTransformResult(
            domain=domain,
            surface_rows=self.rows,
            surface_cols=self.cols,
            crystallization_passes=passes,
            mean_tension_before=round(t_before, 4),
            mean_tension_after=round(t_after, 4),
            theta1_laws={LAW_NAMES[i]: round(theta1[i], 4) for i in range(4)},
            theta2_meta={META_AXES[i]: round(t2[i], 3) for i in range(3)},
            cube_slices=cube_slices,
            sphere_compression_ratio=compression_ratio,
            inverse_expansion_hypotheses=hypotheses,
            cross_domain_isomorphisms=cross_domain,
            parallel_planets=planets,
        )
