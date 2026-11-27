#!/usr/bin/env python3
"""
Vessel & Continuous Snapshot Trajectory Scale Rotor
(저장·실행 그릇 간 위상 대조 및 연속 스냅샷 궤적 스케일 로터)
====================================================================
Treats the actual execution & storage vessels themselves —
  1. Node.js Runtime Vessel       (linear execution & event-loop state)
  2. L1 Python Memory Vessel      (in-memory causal rotor plane)
  3. Persistent Disk Ledger Vessel (on-disk JSON structural array)
as first-class observable state planes on the exact same contrast axis, AND
recursively elevates the continuous trajectory of snapshots
  S(t0) -> S(t1) -> S(t2) -> ... -> S(tk)
into a multi-scale rotor:
  - Scale 1 (Δ):  S(t_{k-1}) <-> S(t_k)  -> immediate invariants(0) & mutations(1)
  - Scale 2 (Δ²): Δ_{k-1}    <-> Δ_k     -> 1st-order changes that recur stably
                                            sublimate into 2nd-order invariant laws(0),
                                            while broken change-laws emerge as regime shifts(1)
  - Scale 3 (Cross-Vessel Plane): Node.js <-> L1 Python Memory <-> Disk Ledger
                                  coherence(0) vs real runtime/storage drift(1)

Zero fake ratios. Zero simulated vessels. Every number and entity comes from
live process/memory/filesystem inspection governed by the explicit Observer Lens.
"""
from __future__ import annotations

import copy
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.orchestration.process_contrast_observer import (
    _values_equal,
    build_observer_lens,
    diff_states_by_lens,
)


def _apply_path(obj: Dict[str, Any], dotted: str, kind: str, val: Any) -> None:
    parts = dotted.split(".")
    cur = obj
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    if kind == "removed":
        cur.pop(parts[-1], None)
    else:
        cur[parts[-1]] = copy.deepcopy(val)


def _reconstruct_from_mutations(origin: Dict[str, Any], mutations: List[Dict[str, Any]]) -> Dict[str, Any]:
    reconstructed = copy.deepcopy(origin)
    for m in mutations:
        _apply_path(reconstructed, m["entity"], m["kind"], m.get("after"))
    return reconstructed


def _reconstruct_flat_signature(origin: Dict[str, Any], mutations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Reconstructs a flat signature dict whose keys themselves contain dotted entity paths."""
    reconstructed = copy.deepcopy(origin)
    for m in mutations:
        key = str(m["entity"])
        if m["kind"] == "removed":
            reconstructed.pop(key, None)
        else:
            reconstructed[key] = copy.deepcopy(m.get("after"))
    return reconstructed


def _mutation_signature(mutations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Re-frames a 1st-order mutation list (Δ_k) into a state dictionary so the
    exact same contrast engine can observe Δ_{k-1} <-> Δ_k at Scale 2!
    Numeric changes carry their exact delta; structural changes carry kind+after.
    """
    sig: Dict[str, Any] = {}
    for m in mutations:
        ent = str(m.get("entity", ""))
        if not ent:
            continue
        delta = m.get("delta")
        if isinstance(delta, (int, float)) and not isinstance(delta, bool):
            sig[ent] = round(float(delta), 6)
        else:
            sig[ent] = f"{m.get('kind', 'mutated')}:{m.get('after')}"
    return sig


def capture_l1_python_vessel(engine: Any) -> Dict[str, Any]:
    """Direct live inspection of the in-memory L1 Python UnifiedScaleRotorEngine."""
    return {
        "vessel": "l1_python_memory",
        "cycle": int(engine.cycle),
        "active_frame": str(engine.active_frame),
        "active_stage": str(engine.active_stage),
        "scale_dial": round(float(engine.canonical.scale_dial), 4),
        "ice_seed_count": len(engine.ice_seeds),
        "ice_seed_ids": [str(s.seed_id) for s in engine.ice_seeds],
        "water_spectrum": [round(float(x), 4) for x in engine.water_flow],
        "cloud_confidence": round(float(engine.cloud_confidence), 4),
        "uncaptured_count": len(engine.uncaptured_slots),
        "ascended_level": int(engine.ascended_level),
        "trajectory_depth": len(engine.trajectory),
    }


def capture_disk_ledger_vessel(ledger_path: Optional[Path]) -> Dict[str, Any]:
    """Direct live filesystem inspection of the actual on-disk Ice Ledger JSON file."""
    if ledger_path is None:
        return {
            "vessel": "disk_ice_ledger",
            "ledger_exists": False,
            "file_size_bytes": 0,
            "cycle": None,
            "active_frame": None,
            "ice_seed_count": 0,
            "ice_seed_ids": [],
            "water_spectrum": [],
            "ascended_level": None,
        }
    p = Path(ledger_path)
    if not p.exists():
        return {
            "vessel": "disk_ice_ledger",
            "ledger_exists": False,
            "file_size_bytes": 0,
            "cycle": None,
            "active_frame": None,
            "ice_seed_count": 0,
            "ice_seed_ids": [],
            "water_spectrum": [],
            "ascended_level": None,
        }
    stat = os.stat(p)
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        raw = {}
    ice_seeds = raw.get("ice_seeds") if isinstance(raw.get("ice_seeds"), list) else []
    water_flow = raw.get("water_flow") if isinstance(raw.get("water_flow"), list) else []
    return {
        "vessel": "disk_ice_ledger",
        "ledger_exists": True,
        "file_size_bytes": int(stat.st_size),
        "cycle": int(raw.get("cycle", 0)) if raw.get("cycle") is not None else None,
        "active_frame": str(raw.get("active_frame", "plane")) if raw.get("active_frame") is not None else None,
        "ice_seed_count": len(ice_seeds),
        "ice_seed_ids": [str(s.get("seed_id", "")) for s in ice_seeds if isinstance(s, dict)],
        "water_spectrum": [round(float(x), 4) for x in water_flow[:4]],
        "ascended_level": int(raw.get("ascended_level", 1)) if raw.get("ascended_level") is not None else None,
    }


def normalize_node_vessel(node_vessel: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Normalizes the live Node.js runtime state passed by server.js (never fabricated)."""
    if not isinstance(node_vessel, dict) or not node_vessel:
        return {
            "vessel": "node_runtime",
            "attached": False,
            "cycle": None,
            "active_frame": None,
            "scale_dial": None,
            "ice_seed_count": None,
            "water_spectrum": [],
            "http_requests_served": None,
            "memory_heap_used_mb": None,
        }
    ws = node_vessel.get("water_spectrum")
    clean_ws = [round(float(x), 4) for x in ws[:4]] if isinstance(ws, list) else []
    return {
        "vessel": "node_runtime",
        "attached": True,
        "cycle": int(node_vessel["cycle"]) if node_vessel.get("cycle") is not None else None,
        "active_frame": str(node_vessel["active_frame"]) if node_vessel.get("active_frame") is not None else None,
        "scale_dial": round(float(node_vessel["scale_dial"]), 4) if node_vessel.get("scale_dial") is not None else None,
        "ice_seed_count": int(node_vessel["ice_seed_count"]) if node_vessel.get("ice_seed_count") is not None else None,
        "water_spectrum": clean_ws,
        "node_engine_cycle": int(node_vessel.get("node_engine_cycle", 0)),
        "http_requests_served": int(node_vessel.get("http_requests_served", 0)),
        "l1_pending_rpcs": int(node_vessel.get("l1_pending_rpcs", 0)),
        "memory_heap_used_mb": round(float(node_vessel.get("memory_heap_used_mb", 0.0)), 2),
        "memory_rss_mb": round(float(node_vessel.get("memory_rss_mb", 0.0)), 2),
    }


def _shared_plane_projection(vessel_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Projects any runtime/storage vessel onto the shared canonical comparison plane
    so heterogeneous vessels (Node.js runtime, L1 Python RAM, Disk JSON file)
    can be directly contrasted on identical structural axes.
    """
    return {
        "cycle": vessel_state.get("cycle"),
        "active_frame": vessel_state.get("active_frame"),
        "ice_seed_count": vessel_state.get("ice_seed_count"),
        "water_spectrum": vessel_state.get("water_spectrum", []),
    }


def _diagnose_pair(pair_name: str, invariants_0: List[Dict[str, Any]], mutations_1: List[Dict[str, Any]]) -> str:
    if not mutations_1:
        return f"{pair_name}: 공통 축 {len(invariants_0)}건 완전 정합 (위상차 0)"
    mut_keys = ", ".join(m["entity"] for m in mutations_1[:4])
    return f"{pair_name}: 정합 {len(invariants_0)}건 · 어긋남 {len(mutations_1)}건 [{mut_keys}]"


class VesselTrajectoryRotor:
    """
    Maintains a bounded continuous trajectory of multi-vessel snapshots and
    recursively computes Scale-1 (Δ), Scale-2 (Δ² law sublimation), and
    Scale-3 (Cross-Vessel Plane) comparative contrast under an explicit Observer Lens.
    """

    def __init__(self, max_snapshots: int = 24) -> None:
        self.max_snapshots = max(4, int(max_snapshots))
        self.snapshots: List[Dict[str, Any]] = []
        self.tick_seq: int = 0

    def clear(self) -> None:
        self.snapshots = []
        self.tick_seq = 0

    def capture(
        self,
        engine: Any,
        node_vessel: Optional[Dict[str, Any]] = None,
        label: str = "live_tick",
    ) -> Dict[str, Any]:
        self.tick_seq += 1
        snap = {
            "tick": self.tick_seq,
            "ts_ms": int(time.time() * 1000),
            "label": str(label),
            "vessels": {
                "node_runtime": normalize_node_vessel(node_vessel),
                "l1_python_memory": capture_l1_python_vessel(engine),
                "disk_ice_ledger": capture_disk_ledger_vessel(getattr(engine, "ledger_path", None)),
            },
        }
        self.snapshots.append(snap)
        if len(self.snapshots) > self.max_snapshots:
            self.snapshots = self.snapshots[-self.max_snapshots :]
        return snap

    def analyze(self, lens_mode: str = "strict", epsilon: Optional[float] = None) -> Dict[str, Any]:
        lens = build_observer_lens(lens_mode, epsilon)
        eps = float(lens["epsilon"])
        n = len(self.snapshots)
        latest = self.snapshots[-1] if n > 0 else None

        # =====================================================================
        # SCALE 1: 1st-Order Trajectory Transitions S(t_{k-1}) <-> S(t_k) (Δ_k)
        # =====================================================================
        transitions_1st: List[Dict[str, Any]] = []
        all_repro_1st = True
        for i in range(1, n):
            prev_s = self.snapshots[i - 1]
            curr_s = self.snapshots[i]
            # Exclude noisy timestamp/tick metadata; contrast actual vessel structures
            b_state = prev_s["vessels"]
            a_state = curr_s["vessels"]
            inv_0, mut_1 = diff_states_by_lens(b_state, a_state, lens)
            reconstructed = _reconstruct_from_mutations(b_state, mut_1)
            repro_ok = _values_equal(reconstructed, a_state, eps)
            if not repro_ok:
                all_repro_1st = False
            transitions_1st.append(
                {
                    "from_tick": prev_s["tick"],
                    "to_tick": curr_s["tick"],
                    "label": f"t{prev_s['tick']}({prev_s['label']}) → t{curr_s['tick']}({curr_s['label']})",
                    "invariants_0_count": len(inv_0),
                    "mutations_1_count": len(mut_1),
                    "invariants_0_preview": inv_0[:6],
                    "mutations_1": mut_1,
                    "signature": _mutation_signature(mut_1),
                    "reproduction": {
                        "verified": repro_ok,
                        "residual_error": 0.0 if repro_ok else 1.0,
                    },
                }
            )

        # =====================================================================
        # SCALE 2: 2nd-Order Trajectory Rotor Δ_{k-1} <-> Δ_k (Δ²_k)
        #   Changes that keep recurring with identical delta SUBLIMATE from
        #   Scale-1 mutation (1) into Scale-2 invariant law (0)!
        # =====================================================================
        transitions_2nd: List[Dict[str, Any]] = []
        for i in range(1, len(transitions_1st)):
            prev_tr = transitions_1st[i - 1]
            curr_tr = transitions_1st[i]
            sig_prev = prev_tr["signature"]
            sig_curr = curr_tr["signature"]
            elevated_laws_0, regime_shifts_1 = diff_states_by_lens(sig_prev, sig_curr, lens)
            # Reconstruct curr_tr signature from prev_tr signature + regime_shifts_1 (flat dotted-key dict)
            reconstructed_sig = _reconstruct_flat_signature(sig_prev, regime_shifts_1)
            repro_2nd = _values_equal(reconstructed_sig, sig_curr, eps)
            transitions_2nd.append(
                {
                    "span": f"Δ({prev_tr['from_tick']}→{prev_tr['to_tick']}) ↔ Δ({curr_tr['from_tick']}→{curr_tr['to_tick']})",
                    "elevated_laws_0": elevated_laws_0,
                    "regime_shifts_1": regime_shifts_1,
                    "reproduction": {
                        "verified": repro_2nd,
                        "method": "이전 변화 서명 Δ_{k-1}(0) + 2차 규칙 이탈 Δ²_k(1) == 현재 변화 서명 Δ_k",
                        "residual_error": 0.0 if repro_2nd else 1.0,
                    },
                }
            )

        # =====================================================================
        # SCALE 3: Cross-Vessel Structural Plane Contrast (Node ↔ Python ↔ Disk)
        # =====================================================================
        cross_vessel_pairs: List[Dict[str, Any]] = []
        if latest is not None:
            v_node = latest["vessels"]["node_runtime"]
            v_py = latest["vessels"]["l1_python_memory"]
            v_disk = latest["vessels"]["disk_ice_ledger"]

            p_node = _shared_plane_projection(v_node)
            p_py = _shared_plane_projection(v_py)
            p_disk = _shared_plane_projection(v_disk)

            pair_specs: List[Tuple[str, str, Dict[str, Any], Dict[str, Any], bool]] = [
                ("l1_python_vs_disk", "L1 Python 메모리 ↔ 디스크 영속 원장", p_py, p_disk, bool(v_disk.get("ledger_exists"))),
                ("node_vs_l1_python", "Node.js 런타임 ↔ L1 Python 메모리", p_node, p_py, bool(v_node.get("attached"))),
                ("node_vs_disk", "Node.js 런타임 ↔ 디스크 영속 원장", p_node, p_disk, bool(v_node.get("attached") and v_disk.get("ledger_exists"))),
            ]
            for pid, title, left_plane, right_plane, both_attached in pair_specs:
                if not both_attached:
                    cross_vessel_pairs.append(
                        {
                            "pair_id": pid,
                            "title": title,
                            "status": "PARTIAL_UNCAPTURED",
                            "coherent_0": [],
                            "divergent_1": [],
                            "diagnosis": f"{title}: 한쪽 그릇 스냅샷이 미연결(미포집) 상태입니다.",
                        }
                    )
                    continue
                coh_0, div_1 = diff_states_by_lens(left_plane, right_plane, lens)
                cross_vessel_pairs.append(
                    {
                        "pair_id": pid,
                        "title": title,
                        "status": "COHERENT" if not div_1 else "DIVERGED",
                        "coherent_0": coh_0,
                        "divergent_1": div_1,
                        "diagnosis": _diagnose_pair(title, coh_0, div_1),
                    }
                )

        latest_2nd = transitions_2nd[-1] if transitions_2nd else None
        all_2nd_repro = all(t["reproduction"]["verified"] for t in transitions_2nd) if transitions_2nd else True
        diverged_pairs = [p for p in cross_vessel_pairs if p["status"] == "DIVERGED"]

        return {
            "status": "ok",
            "experiment": "vessel_and_snapshot_trajectory_rotor",
            "observer_lens": lens,
            "trajectory_length": n,
            "latest_snapshot": latest,
            "scale_1_transitions": [
                {
                    "from_tick": t["from_tick"],
                    "to_tick": t["to_tick"],
                    "label": t["label"],
                    "invariants_0_count": t["invariants_0_count"],
                    "mutations_1_count": t["mutations_1_count"],
                    "mutations_1": t["mutations_1"][:10],
                    "reproduction": t["reproduction"],
                }
                for t in transitions_1st[-6:]
            ],
            "scale_2_trajectory_rotor": {
                "ready": len(transitions_2nd) > 0,
                "transitions_count": len(transitions_2nd),
                "latest": latest_2nd,
                "history": transitions_2nd[-4:],
                "explanation": (
                    "1차 스냅샷 대조에서 매 틱 변하던 항목(1)이라도 변화율(Δ)이 연속 구간에서 동일하게 유지되면 "
                    "2차 궤적 로터에서는 불변 변화법칙(0)으로 승화하고, 그 규칙이 깨진 지점만 2차 변화(1)로 포착됩니다."
                ),
            },
            "scale_3_cross_vessel_plane": {
                "pairs": cross_vessel_pairs,
                "diverged_pair_count": len(diverged_pairs),
                "all_vessels_coherent": len(diverged_pairs) == 0 and any(p["status"] == "COHERENT" for p in cross_vessel_pairs),
            },
            "summary": {
                "snapshots_captured": n,
                "scale1_transitions": len(transitions_1st),
                "scale2_transitions": len(transitions_2nd),
                "elevated_laws_count": len(latest_2nd["elevated_laws_0"]) if latest_2nd else 0,
                "regime_shifts_count": len(latest_2nd["regime_shifts_1"]) if latest_2nd else 0,
                "diverged_vessel_pairs": len(diverged_pairs),
                "all_reproduction_verified": bool(all_repro_1st and all_2nd_repro),
                "principle_note": (
                    "Node.js 런타임·L1 Python 메모리·디스크 영속 원장 3개 그릇 자체를 실제 상태 배열로 포집해 "
                    "그릇 간 면 대조(Scale 3)와 연속 스냅샷 궤적의 1차(Δ)→2차(Δ²) 로터 승화를 실측했습니다."
                ),
            },
            "uncaptured": [
                "스냅샷 포집 시각 t_{k-1}과 t_k 사이의 비관측 공백(중간에 변했다 되돌아온 과도 상태)은 이벤트 훅 없이는 미포집",
                "OS 커널 페이지 캐시·물리 디스크 섹터 fsync 완료 및 V8/CPython 내부 GC 메모리 이동 계층은 현재 관측 범위 밖(미포집)",
                "이 호스트에 연결되지 않은 외부 DB(PostgreSQL/MySQL 등)나 외부 프로그램은 미포집(외부 스냅샷 프로토콜로만 편입)",
            ],
        }
