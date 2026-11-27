"""
Structural-Variation Thought Experiment Rotor & Spectrum Re-Classifier
======================================================================
Replaces repetitive fixed-formula random loops with genuine structural thought
experiments:
  1. Mutates 4 structural dimensions per experiment:
     - Structural Principle (구조원리): linear_harmonic, nonlinear_duffing,
       phase_kuramoto, delayed_feedback, antagonistic_inhibition
     - Connectivity Topology (연결성): ring_chain, hub_star,
       small_world_bridge, asymmetric_directed, severed_bottleneck
     - Environment & Constraints (환경·제약): quiet_vacuum, periodic_forcing,
       impulsive_shock, noisy_friction, bounded_scarcity
     - Parameters & Weights (매개변수·가중치): coupling strength, damping,
       nonlinearity/delay, drive amplitude
  2. Executes a real N-node coupled dynamical rollout under those exact
     structural constraints (100% local, zero external API).
  3. Re-observes 3 emergent spectrum coordinates directly from the trajectory:
     - order_chaos (질서 ↔ 혼돈 스펙트럼, 0..1)
     - resilience_drift (탄성회복 ↔ 비가역변형 스펙트럼, 0..1)
     - local_global (국소고립 ↔ 전역전파 스펙트럼, 0..1)
  4. Re-classifies outcomes onto named Spectrum Regimes & actively pairs
     counterfactual structural flips (changing ONE structural law/topology/
     constraint while holding others fixed) to extract real causal principles!
"""

from __future__ import annotations

import math
import random
import time
from typing import Any, Dict, List, Optional, Tuple


LAWS: List[Tuple[str, str]] = [
    ("linear_harmonic", "선형 복원 결합"),
    ("nonlinear_duffing", "비선형 쌍안정 포화"),
    ("phase_kuramoto", "위상 동기화 결합"),
    ("delayed_feedback", "지연 자기피드백"),
    ("antagonistic_inhibition", "상호 억제 경쟁"),
]

TOPOLOGIES: List[Tuple[str, str]] = [
    ("ring_chain", "국소 이웃 고리"),
    ("hub_star", "중심 허브 집중"),
    ("small_world_bridge", "원거리 교량 연결"),
    ("asymmetric_directed", "비대칭 단방향 사슬"),
    ("severed_bottleneck", "병목 단절 제약"),
]

ENVIRONMENTS: List[Tuple[str, str]] = [
    ("quiet_vacuum", "정적 평형 환경"),
    ("periodic_forcing", "주기 외력 구동"),
    ("impulsive_shock", "돌발 충격 환경"),
    ("noisy_friction", "확률 마찰 교란"),
    ("bounded_scarcity", "자원 상한 제약"),
]

LAW_KO = dict(LAWS)
TOPO_KO = dict(TOPOLOGIES)
ENV_KO = dict(ENVIRONMENTS)


def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(v)))


def _build_adjacency(topo_id: str, n: int, coupling: float) -> List[List[Tuple[int, float]]]:
    adj: List[List[Tuple[int, float]]] = [[] for _ in range(n)]
    if topo_id == "ring_chain":
        for i in range(n):
            adj[i].append(((i - 1) % n, coupling))
            adj[i].append(((i + 1) % n, coupling))
    elif topo_id == "hub_star":
        for i in range(1, n):
            adj[0].append((i, coupling * 0.7))
            adj[i].append((0, coupling * 1.25))
    elif topo_id == "small_world_bridge":
        for i in range(n):
            adj[i].append(((i - 1) % n, coupling * 0.85))
            adj[i].append(((i + 1) % n, coupling * 0.85))
        adj[0].append((n // 2, coupling * 1.15))
        adj[n // 2].append((0, coupling * 1.15))
        adj[1].append((n - 2, coupling * 1.0))
    elif topo_id == "asymmetric_directed":
        for i in range(n - 1):
            adj[i + 1].append((i, coupling * 1.25))  # downstream driven strictly by upstream
        adj[0].append((n - 1, coupling * 0.18))      # weak return feedback
    else:  # severed_bottleneck
        mid = n // 2
        for i in range(mid - 1):
            adj[i].append((i + 1, coupling))
            adj[i + 1].append((i, coupling))
        for i in range(mid, n - 1):
            adj[i].append((i + 1, coupling))
            adj[i + 1].append((i, coupling))
        # Narrow 1-way high-resistance bottleneck between clusters
        adj[mid].append((mid - 1, coupling * 0.22))
    return adj


def simulate_structural_config(
    *,
    law_id: str,
    topo_id: str,
    env_id: str,
    coupling: float,
    damping: float,
    nonlinearity: float,
    drive: float,
    seed: int = 0,
) -> Dict[str, Any]:
    """
    Runs a real 6-node coupled dynamical rollout under the specified structural
    law, connectivity topology, environmental constraints, and weights, then
    re-observes 3 emergent spectrum coordinates and classifies its phase regime.
    """
    rng = random.Random(seed if seed else None)
    n = 6
    steps = 16
    dt = 0.22
    adj = _build_adjacency(topo_id, n, coupling)

    # Initial asymmetric excitation concentrated on node 0 (to measure local->global propagation!)
    x = [0.85, 0.18, -0.10, 0.04, -0.05, 0.02]
    v = [0.0] * n
    history: List[List[float]] = [list(x)]

    for t in range(steps):
        prev_x = history[max(0, t - 2)]  # 2-step delay buffer for delayed_feedback
        new_x = [0.0] * n
        new_v = [0.0] * n

        for i in range(n):
            # 1) Connectivity interaction under the chosen Structural Law
            interact = 0.0
            for nb, w in adj[i]:
                diff = x[nb] - x[i]
                if law_id == "linear_harmonic":
                    interact += w * diff
                elif law_id == "nonlinear_duffing":
                    interact += w * diff - nonlinearity * (x[i] ** 3) * 0.55
                elif law_id == "phase_kuramoto":
                    interact += w * math.sin(diff * 2.2)
                elif law_id == "delayed_feedback":
                    interact += w * (prev_x[nb] - x[i]) - nonlinearity * prev_x[i] * 0.45
                else:  # antagonistic_inhibition
                    interact += -w * math.tanh(x[nb] * 1.4) + 0.18 * diff

            # 2) Environmental constraints & boundary conditions
            ext = 0.0
            if env_id == "periodic_forcing":
                ext = drive * math.sin(0.65 * t + (0.4 if i == 0 else 0.0)) * (1.0 if i < 2 else 0.25)
            elif env_id == "impulsive_shock":
                ext = (drive * 1.85) if (t == 4 and i in (0, 3)) else 0.0
            elif env_id == "noisy_friction":
                ext = rng.uniform(-drive, drive) * 0.85
            elif env_id == "bounded_scarcity":
                ext = drive * 0.45 if i == 0 else 0.0

            restore = -0.32 * x[i] if law_id != "nonlinear_duffing" else (0.38 * x[i] - nonlinearity * (x[i] ** 3))
            acc = restore + interact + ext - damping * v[i]
            nv = max(-4.5, min(4.5, v[i] + acc * dt))
            nx = max(-3.5, min(3.5, x[i] + nv * dt))

            if env_id == "bounded_scarcity":
                cap = max(0.35, 1.05 - 0.35 * nonlinearity)
                nx = max(-cap, min(cap, nx))

            new_x[i] = nx
            new_v[i] = nv

        x = new_x
        v = new_v
        history.append(list(x))

    # --- Re-Observe 3 Real Emergent Spectrum Axes from the simulated trajectory ---
    # Axis 1: Order <-> Chaos (spatial dispersion + late temporal jaggedness)
    final_mean = sum(x) / n
    spatial_std = math.sqrt(sum((xi - final_mean) ** 2 for xi in x) / n)
    late_deltas = [
        sum(abs(history[t][i] - history[t - 1][i]) for i in range(n)) / n
        for t in range(steps - 5, steps + 1)
    ]
    vel_mag = sum(late_deltas) / max(1, len(late_deltas))
    order_chaos = _clamp(0.48 * min(1.0, spatial_std / 1.15) + 0.52 * min(1.0, vel_mag / 0.58))

    # Axis 2: Elastic Resilience <-> Irreversible Drift (final displacement from rest & symmetry break)
    rms_final = math.sqrt(sum(xi * xi for xi in x) / n)
    mean_shift = abs(final_mean)
    resilience_drift = _clamp(0.55 * min(1.0, rms_final / 1.45) + 0.45 * min(1.0, mean_shift / 0.95))

    # Axis 3: Local Isolation <-> Global Propagation (how much excitation reached distant nodes 3..5)
    source_e = sum(abs(history[t][0]) for t in range(4, steps + 1)) / max(1, steps - 3)
    distant_e = sum(
        (abs(history[t][3]) + abs(history[t][4]) + abs(history[t][5])) / 3.0
        for t in range(4, steps + 1)
    ) / max(1, steps - 3)
    local_global = _clamp(distant_e / max(0.12, source_e + 0.12))

    # Re-classify into emergent Spectrum Regime
    if order_chaos < 0.28 and resilience_drift < 0.32:
        regime_id = "damped_equilibrium"
        regime_ko = "감쇠 안정 수렴"
    elif order_chaos < 0.36 and local_global >= 0.55:
        regime_id = "global_sync_crystal"
        regime_ko = "전역 동기화 공명"
    elif resilience_drift >= 0.58 and order_chaos < 0.52:
        regime_id = "bistable_phase_shift"
        regime_ko = "비가역 상전이 고착"
    elif order_chaos >= 0.62 and local_global >= 0.50:
        regime_id = "turbulent_cascade"
        regime_ko = "전역 혼돈 연쇄"
    elif local_global < 0.34 and resilience_drift >= 0.32:
        regime_id = "localized_bottleneck"
        regime_ko = "국소 병목 고립"
    else:
        regime_id = "critical_edge_oscillation"
        regime_ko = "임계 경계 진동"

    return {
        "law_id": law_id,
        "law_ko": LAW_KO[law_id],
        "topo_id": topo_id,
        "topo_ko": TOPO_KO[topo_id],
        "env_id": env_id,
        "env_ko": ENV_KO[env_id],
        "params": {
            "coupling": round(coupling, 3),
            "damping": round(damping, 3),
            "nonlinearity": round(nonlinearity, 3),
            "drive": round(drive, 3),
        },
        "spectrum": {
            "order_chaos": round(order_chaos, 3),
            "resilience_drift": round(resilience_drift, 3),
            "local_global": round(local_global, 3),
        },
        "regime_id": regime_id,
        "regime_ko": regime_ko,
    }


class StructuralExperimentRotor:
    """
    Maintains a non-repeating structural exploration space and a living
    3-Axis Spectrum Re-Classification Map.
    Each burst runs counterfactual structural flips (mutating one structural
    dimension at a time: Law, Topology, Environment, or Weights) to discover
    how structural constraints actually shift emergent outcomes across spectra.
    """

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.explored_signatures: List[str] = []
        self.regime_map: Dict[str, Dict[str, Any]] = {}
        self.structural_laws_discovered: List[Dict[str, Any]] = []
        self.total_flips_tested: int = 0
        self.regime_transitions_found: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "explored_signatures": self.explored_signatures[-240:],
            "regime_map": self.regime_map,
            "structural_laws_discovered": self.structural_laws_discovered[-12:],
            "total_flips_tested": self.total_flips_tested,
            "regime_transitions_found": self.regime_transitions_found,
        }

    def load_dict(self, raw: Any) -> None:
        if not isinstance(raw, dict):
            return
        if isinstance(raw.get("explored_signatures"), list):
            self.explored_signatures = [str(s) for s in raw["explored_signatures"][-240:]]
        if isinstance(raw.get("regime_map"), dict):
            self.regime_map = raw["regime_map"]
        if isinstance(raw.get("structural_laws_discovered"), list):
            self.structural_laws_discovered = raw["structural_laws_discovered"][-12:]
        self.total_flips_tested = max(0, int(raw.get("total_flips_tested", 0)))
        self.regime_transitions_found = max(0, int(raw.get("regime_transitions_found", 0)))

    def _record_spectrum_sample(self, res: Dict[str, Any]) -> None:
        sig = f"{res['law_id']}|{res['topo_id']}|{res['env_id']}"
        if sig not in self.explored_signatures:
            self.explored_signatures.append(sig)
            if len(self.explored_signatures) > 240:
                self.explored_signatures = self.explored_signatures[-240:]

        rid = res["regime_id"]
        sp = res["spectrum"]
        entry = self.regime_map.get(rid)
        if entry is None:
            self.regime_map[rid] = {
                "regime_id": rid,
                "regime_ko": res["regime_ko"],
                "count": 1,
                "avg_order_chaos": sp["order_chaos"],
                "avg_resilience_drift": sp["resilience_drift"],
                "avg_local_global": sp["local_global"],
                "exemplar": f"{res['law_ko']} × {res['topo_ko']} × {res['env_ko']}",
            }
        else:
            c = int(entry["count"]) + 1
            entry["count"] = c
            entry["avg_order_chaos"] = round((entry["avg_order_chaos"] * (c - 1) + sp["order_chaos"]) / c, 3)
            entry["avg_resilience_drift"] = round((entry["avg_resilience_drift"] * (c - 1) + sp["resilience_drift"]) / c, 3)
            entry["avg_local_global"] = round((entry["avg_local_global"] * (c - 1) + sp["local_global"]) / c, 3)
            entry["exemplar"] = f"{res['law_ko']} × {res['topo_ko']} × {res['env_ko']}"

    def run_structural_batch(self, pairs: int = 24) -> Dict[str, Any]:
        """
        Runs `pairs` real counterfactual structural-flip experiments (2 * pairs
        multi-node dynamical simulations), preferring unexplored structural
        combinations and extracting the highest-contrast regime transition!
        """
        n_pairs = max(6, min(96, int(pairs)))
        explored_set = set(self.explored_signatures)
        best_flip: Optional[Tuple[float, str, Dict[str, Any], Dict[str, Any]]] = None

        for _ in range(n_pairs):
            # Pick a baseline structural configuration (biasing toward unexplored triples!)
            law_a = random.choice(LAWS)[0]
            topo_a = random.choice(TOPOLOGIES)[0]
            env_a = random.choice(ENVIRONMENTS)[0]
            if f"{law_a}|{topo_a}|{env_a}" in explored_set:
                # Try one fresh jump to avoid looping over identical structures
                law_a = random.choice(LAWS)[0]
                topo_a = random.choice(TOPOLOGIES)[0]
                env_a = random.choice(ENVIRONMENTS)[0]

            coupling = random.uniform(0.18, 1.35)
            damping = random.uniform(0.06, 0.72)
            nonlin = random.uniform(0.15, 1.40)
            drive = random.uniform(0.20, 1.15)
            seed = random.randint(1, 999999)

            res_a = simulate_structural_config(
                law_id=law_a,
                topo_id=topo_a,
                env_id=env_a,
                coupling=coupling,
                damping=damping,
                nonlinearity=nonlin,
                drive=drive,
                seed=seed,
            )
            self._record_spectrum_sample(res_a)
            explored_set.add(f"{law_a}|{topo_a}|{env_a}")

            # Counterfactual single-factor structural mutation!
            flip_axis = random.choice(["law", "topology", "environment", "weights"])
            law_b, topo_b, env_b = law_a, topo_a, env_a
            c_b, d_b, nl_b, dr_b = coupling, damping, nonlin, drive

            if flip_axis == "law":
                law_b = random.choice([lid for lid, _ in LAWS if lid != law_a])
            elif flip_axis == "topology":
                topo_b = random.choice([tid for tid, _ in TOPOLOGIES if tid != topo_a])
            elif flip_axis == "environment":
                env_b = random.choice([eid for eid, _ in ENVIRONMENTS if eid != env_a])
            else:
                # Significant weight/constraint shift (invert damping/coupling regime)
                c_b = round(1.55 - coupling, 3) if coupling > 0.75 else round(coupling + 0.65, 3)
                d_b = round(0.80 - damping, 3)

            res_b = simulate_structural_config(
                law_id=law_b,
                topo_id=topo_b,
                env_id=env_b,
                coupling=c_b,
                damping=d_b,
                nonlinearity=nl_b,
                drive=dr_b,
                seed=seed,  # SAME noise seed so the difference is 100% causal from structural change!
            )
            self._record_spectrum_sample(res_b)
            explored_set.add(f"{law_b}|{topo_b}|{env_b}")

            self.total_flips_tested += 1
            sa, sb = res_a["spectrum"], res_b["spectrum"]
            spec_dist = math.sqrt(
                (sa["order_chaos"] - sb["order_chaos"]) ** 2
                + (sa["resilience_drift"] - sb["resilience_drift"]) ** 2
                + (sa["local_global"] - sb["local_global"]) ** 2
            ) / math.sqrt(3.0)
            regime_flipped = res_a["regime_id"] != res_b["regime_id"]
            if regime_flipped:
                self.regime_transitions_found += 1

            score = spec_dist + (0.35 if regime_flipped else 0.0)
            if best_flip is None or score > best_flip[0]:
                best_flip = (score, flip_axis, res_a, res_b)

        assert best_flip is not None
        score, flip_axis, ra, rb = best_flip
        axis_ko_map = {
            "law": "구조원리 변이",
            "topology": "연결성(토폴로지) 변이",
            "environment": "환경·제약 변이",
            "weights": "가중치·감쇠 변이",
        }
        if flip_axis == "law":
            change_desc = f"{ra['law_ko']} → {rb['law_ko']}"
            fixed_desc = f"연결({ra['topo_ko']})·환경({ra['env_ko']}) 동일"
        elif flip_axis == "topology":
            change_desc = f"{ra['topo_ko']} → {rb['topo_ko']}"
            fixed_desc = f"원리({ra['law_ko']})·환경({ra['env_ko']}) 동일"
        elif flip_axis == "environment":
            change_desc = f"{ra['env_ko']} → {rb['env_ko']}"
            fixed_desc = f"원리({ra['law_ko']})·연결({ra['topo_ko']}) 동일"
        else:
            change_desc = (
                f"결합({ra['params']['coupling']:.2f}→{rb['params']['coupling']:.2f})·"
                f"감쇠({ra['params']['damping']:.2f}→{rb['params']['damping']:.2f})"
            )
            fixed_desc = f"{ra['law_ko']} × {ra['topo_ko']} × {ra['env_ko']} 동일"

        sa, sb = ra["spectrum"], rb["spectrum"]
        outcome_shift = (
            f"[{ra['regime_ko']} → {rb['regime_ko']}] "
            f"(혼돈 {sa['order_chaos']:.2f}→{sb['order_chaos']:.2f}, "
            f"변형 {sa['resilience_drift']:.2f}→{sb['resilience_drift']:.2f}, "
            f"전파 {sa['local_global']:.2f}→{sb['local_global']:.2f})"
        )

        discovery = {
            "ts": round(time.time(), 2),
            "flip_axis": flip_axis,
            "flip_axis_ko": axis_ko_map[flip_axis],
            "change": change_desc,
            "held_constant": fixed_desc,
            "regime_from": ra["regime_ko"],
            "regime_to": rb["regime_ko"],
            "outcome_shift": outcome_shift,
            "contrast_score": round(_clamp(score, 0.05, 0.99), 3),
            "simulations_run": n_pairs * 2,
            "unique_structures_explored": len(self.explored_signatures),
        }
        self.structural_laws_discovered.append(discovery)
        self.structural_laws_discovered = self.structural_laws_discovered[-12:]
        return discovery

    def get_public_state(self) -> Dict[str, Any]:
        regimes = sorted(
            self.regime_map.values(),
            key=lambda r: int(r.get("count", 0)),
            reverse=True,
        )
        return {
            "unique_structures_explored": len(self.explored_signatures),
            "total_possible_structures": len(LAWS) * len(TOPOLOGIES) * len(ENVIRONMENTS),
            "total_flips_tested": self.total_flips_tested,
            "regime_transitions_found": self.regime_transitions_found,
            "regimes": regimes[:6],
            "recent_discoveries": list(self.structural_laws_discovered[-5:]),
        }
