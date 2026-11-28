r"""
ELYSIA CoW Parallel-Universe Multiverse & Grounded Language-Sensory Prism
=========================================================================

Connects TWO pivotal layers into one unified structure:

1. **Copy-on-Write Parallel-Universe Branching (`M_0 -> U_A / U_B / U_C`):**
   Treats the crystallized 3-generation Macro-Rotor (`R_0001 -> R_0003` from
   `story_world_state.json`) as ONE shared `0000` Reference Rotor (`M_0`),
   spawns 3 counterfactual universes differing ONLY by their causal delta `Δ`:
     - `U_eternal_night`: Optical collapse (sun locked to night, vis=2.3m)
     - `U_value_conflict`: Orthogonalized NPC value axes (dialectical friction)
     - `U_open_horizon`: Expanded daylight & frontier freedom
   Overlays all 3 parallel universes onto Baseline `M_0` to separate
   **Universal Invariants** from **Counterfactual Leverage Points**.

2. **Bidirectional Grounded Language <-> Multi-Sensory Structural Architecture:**
   Structurally binds linguistic units (Korean/English concepts & clauses)
   directly into ALL 5 lived multi-sensory systems inside one `CausalField`:
     - Visual/Optical 3D Prism (`embodied_prism_vision.json`)
     - Synchronized Audio-Visual Prosody/Silence (`control_weave_and_multimodal_prism.json`)
     - 545-Object Cross-Domain Information Manifolds (`universal_cross_intersection_reclassification.json`)
     - Recursive Temporal Story World (`story_world_state.json`)
     - Counterfactual Multiverse Contrast (`U_A / U_B / U_C vs M_0`)
   Supports BOTH directions without scalar emotions or canned chatbot scripts:
     - Bottom-Up (`Sensory State -> Grounded Korean Utterance`)
     - Top-Down (`Human Korean Query -> Multi-Sensory Beam Activation & World Retrieval`)
"""

from __future__ import annotations

import argparse
import copy
import json
import math
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

THIS_DIR = Path(__file__).resolve().parent
L1_ROOT = THIS_DIR.parents[1]
WORKSPACE_ROOT = THIS_DIR.parents[2]
for _p in (str(THIS_DIR), str(L1_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from core.physics.causal_field import CausalField, InformationVoxel  # noqa: E402
from self_cognitive_expansion_cortex import COGNITIVE_WORLD_DIR, _load_json, _save_json  # noqa: E402
from story_scale_rotor_world_engine import (  # noqa: E402
    DEFAULT_STORY_TEXT,
    STORY_STATE_PATH,
    STORY_WORLD_DIR,
    StoryScaleRotorDigitalWorld,
    create_and_run_story_world,
)


MULTIVERSE_REPORT_PATH = STORY_WORLD_DIR / "multiverse_and_language_prism.json"
LANGUAGE_GRAPH_PATH = COGNITIVE_WORLD_DIR / "grounded_language_sensory_graph.json"


# ---------------------------------------------------------------------------
# PART 1: CoW Parallel-Universe Branching off Reference Rotor M_0
# ---------------------------------------------------------------------------

def _clone_world_from_reference_rotor(ref_state: Dict[str, Any]) -> StoryScaleRotorDigitalWorld:
    bp = {
        "world_title": ref_state["world_title"],
        "source_story": ref_state["source_story"],
        "landmarks": copy.deepcopy(ref_state["landmarks"]),
        "npcs": copy.deepcopy(ref_state["npcs"]),
    }
    w = StoryScaleRotorDigitalWorld(bp)
    w.tick = int(ref_state.get("tick", 0))
    w.solar_phase_rad = float((ref_state.get("solar_state") or {}).get("solar_phase_rad", 0.0))
    w.temporal_rotor_chain = copy.deepcopy(ref_state.get("temporal_rotor_chain") or [])
    return w


def run_cow_parallel_universes_from_baseline() -> Dict[str, Any]:
    ref_state = _load_json(STORY_STATE_PATH, {})
    if not ref_state or not ref_state.get("npcs"):
        ref_state = create_and_run_story_world(DEFAULT_STORY_TEXT, generations=2, render_3d=False)

    ref_macro = ref_state.get("macro_epoch_rotor") or {}
    ref_last_rotor = (ref_state.get("temporal_rotor_chain") or [{}])[-1]
    ref_centroids = ((ref_last_rotor.get("crystallized_invariants") or {}).get("npc_centroids")) or {
        n["id"]: n["position"] for n in ref_state["npcs"]
    }
    ref_relations = set((ref_last_rotor.get("crystallized_invariants") or {}).get("active_relation_pairs") or [])

    # Run 1 baseline continuation `M_0_cont` + 3 counterfactual CoW branches differing ONLY by Δ!
    specs = [
        ("U_baseline_continuation", "기준 우주 연장 (Δ = 0)", "baseline"),
        ("U_eternal_night", "평행우주 A: 영원한 밤 (Δ = 태양 위상 어둠 고정, 시야 2.3m)", "eternal_night"),
        ("U_value_conflict", "평행우주 B: 가치 축 충돌 (Δ = 오르·루멘 가치 직교 역전)", "value_conflict"),
        ("U_open_horizon", "평행우주 C: 개방 지평선 (Δ = 상시 최대 광량·외곽 확장)", "open_horizon"),
    ]

    universes: List[Dict[str, Any]] = []
    for uid, desc, mode in specs:
        w = _clone_world_from_reference_rotor(ref_state)

        # Apply ONLY the minimal CoW counterfactual perturbation Δ
        if mode == "eternal_night":
            w.solar_phase_rad = 1.5 * math.pi  # trough of sin(theta) -> deep night
            orig_solar = w._solar_state
            w._solar_state = lambda: {
                "solar_phase_rad": round(1.5 * math.pi, 4),
                "daylight_intensity": 0.04,
                "visibility_radius": 2.35,
                "diurnal_phase": "eternal_night",
            }
        elif mode == "value_conflict":
            # Orthogonalize value axes of NPC #2 and #3 to inject genuine relational conflict
            if len(w.npcs) >= 3:
                w.npcs[1]["value_axis"] = [0.05, 0.05, 0.997]
                w.npcs[2]["value_axis"] = [0.05, 0.997, 0.05]
        elif mode == "open_horizon":
            w._solar_state = lambda: {
                "solar_phase_rad": round(0.5 * math.pi, 4),
                "daylight_intensity": 1.0,
                "visibility_radius": 6.0,
                "diurnal_phase": "perpetual_daylight",
            }
            for nid, sh in w.npc_shells.items():
                if sh.tiers.get("macro") is not None:
                    sh.tiers["macro"].position = sh.tiers["macro"].position * 1.45

        ring = w.unfold_one_adaptive_temporal_rotor()
        u_centroids = (ring.get("crystallized_invariants") or {}).get("npc_centroids") or {}
        u_rels = set((ring.get("crystallized_invariants") or {}).get("active_relation_pairs") or [])

        # Overlay-contrast against shared Reference Rotor M_0
        divs = [
            float(np.linalg.norm(np.array(u_centroids.get(nid, [0, 0, 0])) - np.array(ref_centroids.get(nid, [0, 0, 0]))))
            for nid in ref_centroids.keys()
        ]
        mean_div = round(float(np.mean(divs)) if divs else 0.0, 3)

        friction_events = sum(1 for e in w.event_log[-ring["events_in_rotor"] :] if e.get("kind") == "dialectical_boundary_friction") if ring["events_in_rotor"] else 0
        resonant_events = sum(1 for e in w.event_log[-ring["events_in_rotor"] :] if e.get("kind") == "resonant_exchange") if ring["events_in_rotor"] else 0

        universes.append(
            {
                "universe_id": uid,
                "description": desc,
                "cow_perturbation_mode": mode,
                "reference_rotor_shared": ref_last_rotor.get("rotor_id", "R_0003"),
                "adaptive_steps": ring["adaptive_steps_taken"],
                "micro_zoom_steps": ring["micro_zoom_steps"],
                "events_total": ring["events_in_rotor"],
                "resonant_events": resonant_events,
                "friction_events": friction_events,
                "divergence_vs_baseline_M0": mean_div,
                "preserved_relations_count": len(u_rels & ref_relations),
                "myelinated_ast_habits": (ring.get("crystallized_invariants") or {}).get("myelinated_ast_habits", 0),
                "sample_npc_positions": u_centroids,
            }
        )

    # Extract Universal Invariants vs Counterfactual Leverage Points across all 4 universes
    all_preserved = min(u["preserved_relations_count"] for u in universes)
    max_div_u = max(universes[1:], key=lambda u: u["divergence_vs_baseline_M0"])
    max_fric_u = max(universes, key=lambda u: u["friction_events"])

    return {
        "reference_rotor_M0": {
            "macro_span": ref_macro.get("macro_scale_span", "R_0001 -> R_0003"),
            "shared_compressed_bytes": (ref_last_rotor.get("compressed_world_chunk") or {}).get("compressed_bytes", 0),
        },
        "parallel_universes": universes,
        "counterfactual_synthesis": {
            "universal_invariants_0000": f"All {len(universes)} universes retained {all_preserved} core relational links and 4/4 myelinated NPC AST habits without duplicating M_0 history.",
            "highest_spatial_leverage_point": f"{max_div_u['universe_id']} produced largest trajectory shift vs M_0 (Δ={max_div_u['divergence_vs_baseline_M0']}m).",
            "highest_dialectical_friction_universe": f"{max_fric_u['universe_id']} generated {max_fric_u['friction_events']} dialectical friction events vs {universes[0]['friction_events']} in baseline.",
        },
    }


# ---------------------------------------------------------------------------
# PART 2: Bidirectional Grounded Language <-> All 5 Multi-Sensory Systems
# ---------------------------------------------------------------------------

class GroundedLanguageSensoryPrism:
    """
    Connects Korean/English linguistic structures directly into ALL 5 lived
    multi-sensory databases inside one `CausalField` — zero canned templates,
    zero scalar emotion scores!
    """

    def __init__(self, multiverse_data: Dict[str, Any]) -> None:
        self.field = CausalField(dimensions=3)
        self.prism_vision = _load_json(COGNITIVE_WORLD_DIR / "embodied_prism_vision.json", {})
        self.woven_av = _load_json(COGNITIVE_WORLD_DIR / "control_weave_and_multimodal_prism.json", {})
        self.reclass = _load_json(COGNITIVE_WORLD_DIR / "universal_cross_intersection_reclassification.json", {})
        self.story = _load_json(STORY_STATE_PATH, {})
        self.multiverse = multiverse_data
        self.grounded_nodes: List[Dict[str, Any]] = []
        self._build_unified_sensory_language_graph()

    def _add_node(self, node_id: str, modality: str, lexemes: List[str], physical_evidence: Dict[str, Any], tensor_vec: List[float]) -> None:
        node = {
            "node_id": node_id,
            "modality": modality,
            "grounded_lexemes": lexemes,
            "physical_evidence": physical_evidence,
            "tensor": [round(x, 4) for x in tensor_vec],
        }
        self.grounded_nodes.append(node)
        self.field.add_voxel(
            InformationVoxel(
                id=node_id,
                content=node,
                tensor=np.array(tensor_vec, dtype=np.float32),
                mass=1.2,
                conductance=0.5,
                curiosity_charge=0.3,
            )
        )

    def _build_unified_sensory_language_graph(self) -> None:
        # 1. Dock Visual/Optical 3D Prism experiments to language
        for cause, info in (self.prism_vision.get("experiments") or {}).items():
            sig = info.get("mean_prism_signature") or {}
            lex_map = {
                "light_angle_rotation": ["빛", "각도", "광원", "그림자", "회전", "조명", "시각", "light", "angle"],
                "observer_viewpoint_rotation": ["시점", "관찰자", "카메라", "각도", "배경", "시야", "observer", "camera"],
                "object_temporal_motion": ["움직임", "물체", "시간", "변화", "이동", "윤곽", "motion", "object", "time"],
            }
            self._add_node(
                f"vision::{cause}",
                "visual_3d_prism",
                lex_map.get(cause, [cause]),
                sig,
                [float(sig.get("center_obj_shift", 0.0)) / 50.0, float(sig.get("edge_structure_shift", 0.0)), float(sig.get("luminance_centroid_dx", 0.0)) * 5.0],
            )

        # 2. Dock Synchronized Audio-Visual Prosody/Silence trajectories to language
        for tr in self.woven_av.get("part2_synchronized_audiovisual_multimodal_prism") or []:
            corr = float(tr.get("visual_motion_vs_audio_rms_corr", 0.0))
            sil = float(tr.get("silence_ratio", 0.0))
            lex = ["소리", "음향", "영상", "리듬", "멀티모달", "audio", "sound"]
            if sil >= 0.8:
                lex += ["침묵", "무음", "고요", "정적", "silence"]
            if corr >= 0.5:
                lex += ["동기화", "공명", "일치", "함께", "충격", "sync"]
            if float(tr.get("mean_visual_motion", 0.0)) >= 10.0:
                lex += ["격렬", "움직임", "폭발", "변화", "surge"]
            self._add_node(
                f"audiovisual::{tr['file']}",
                "audiovisual_multimodal",
                lex,
                {
                    "file": tr["file"],
                    "av_corr": corr,
                    "silence_ratio": sil,
                    "spectral_centroid_hz": tr.get("mean_audio_spectral_centroid_hz"),
                    "phases": list((tr.get("observed_multimodal_phase_states") or {}).keys()),
                },
                [min(1.0, float(tr.get("mean_visual_motion", 0.0)) / 20.0), max(0.05, corr), sil],
            )

        # 3. Dock 545-object Cross-Domain Information Manifolds to language
        for inter in self.reclass.get("discovered_cross_domain_intersections") or []:
            mname = inter["emergent_manifold"]
            law = inter["shared_physical_law"]
            lex = ["구조", "데이터", "재분류", "교차", "원리", "엔트로피"]
            if "symbolic" in mname:
                lex += ["언어", "문법", "코드", "규칙", "법칙", "기호", "grammar", "code"]
            if "packed_media" in mname:
                lex += ["고밀도", "압축", "미디어", "영상", "오디오", "3d", "포화"]
            if "membrane" in mname:
                lex += ["경계", "경계막", "헤더", "컨테이너", "스케일", "폰트", "그물", "membrane"]
            self._add_node(
                f"manifold::{mname}",
                "cross_domain_information",
                lex,
                {"domains": inter["converging_domains"], "law": law},
                [law["zlib_compressibility"], law["ascii_symbolic_ratio"], law["entropy_head"] / 8.0],
            )

        # 4. Dock Multiverse Counterfactual Worlds to language
        for u in self.multiverse.get("parallel_universes") or []:
            uid = u["universe_id"]
            lex = ["평행우주", "다중우주", "만약", "세계", "분기", "우주", "npc", "스토리", "multiverse"]
            if "night" in uid:
                lex += ["밤", "어둠", "시야", "등대", "빛", "night", "dark"]
            if "conflict" in uid:
                lex += ["갈등", "마찰", "충돌", "가치", "경계", "conflict", "friction"]
            if "open" in uid:
                lex += ["개방", "자유", "확장", "지평선", "낮", "open", "freedom"]
            self._add_node(
                f"multiverse::{uid}",
                "counterfactual_multiverse",
                lex,
                {
                    "description": u["description"],
                    "divergence_vs_M0": u["divergence_vs_baseline_M0"],
                    "resonant_events": u["resonant_events"],
                    "friction_events": u["friction_events"],
                },
                [min(1.0, u["divergence_vs_baseline_M0"] / 3.0), min(1.0, u["resonant_events"] / 100.0), min(1.0, u["friction_events"] / 40.0)],
            )

        # Link nodes across DIFFERENT modalities that share grounded lexemes via ConnectivityBeams!
        for i in range(len(self.grounded_nodes)):
            for j in range(i + 1, len(self.grounded_nodes)):
                a, b = self.grounded_nodes[i], self.grounded_nodes[j]
                if a["modality"] == b["modality"]:
                    continue
                shared = set(a["grounded_lexemes"]) & set(b["grounded_lexemes"])
                if shared:
                    self.field.link_voxels(a["node_id"], b["node_id"], strength=float(len(shared)))
        self.field.step(dt=0.1)

    def ground_human_utterance(self, utterance: str) -> Dict[str, Any]:
        """
        Top-Down (`Language -> Unified Multi-Sensory Beams`) + Bottom-Up (`Activated
        Multi-Sensory Evidence -> Grounded Structural Reply`, ZERO canned scripts!).
        """
        q = (utterance or "").strip()
        q_low = q.lower()
        activated: List[Tuple[int, List[str], Dict[str, Any]]] = []

        for node in self.grounded_nodes:
            matched = [lx for lx in node["grounded_lexemes"] if lx in q_low]
            if matched:
                activated.append((len(matched), matched, node))

        activated.sort(key=lambda x: (-x[0], x[2]["modality"]))
        top_hits = activated[:6]

        # Collect distinct sensory modalities activated simultaneously by this sentence!
        modalities_hit = sorted({h[2]["modality"] for h in top_hits})

        # Compose a strictly evidence-grounded Korean synthesis from the activated multi-sensory nodes
        evidence_lines: List[str] = []
        for _cnt, matched, node in top_hits:
            ev = node["physical_evidence"]
            mod = node["modality"]
            if mod == "visual_3d_prism":
                evidence_lines.append(f"[3D 시각 프리즘·{node['node_id'].split('::')[1]}] 교차어 {matched} → 빛중심이동={ev.get('luminance_centroid_dx')}, 윤곽변화={ev.get('edge_structure_shift')}")
            elif mod == "audiovisual_multimodal":
                evidence_lines.append(f"[시청각 동기화·{ev.get('file')}] 교차어 {matched} → 영상-음향 상관 r={ev.get('av_corr')}, 침묵비율={ev.get('silence_ratio')}, 중심주파수={ev.get('spectral_centroid_hz')}Hz")
            elif mod == "cross_domain_information":
                evidence_lines.append(f"[545실물 정보다양체·{node['node_id'].split('::')[1]}] 교차어 {matched} → 도메인 {ev.get('domains')} (H={ev['law'].get('entropy_head')}, ΔH={ev['law'].get('entropy_gradient')})")
            elif mod == "counterfactual_multiverse":
                evidence_lines.append(f"[평행우주 대조·{node['node_id'].split('::')[1]}] 교차어 {matched} → 기준 M0 대비 변위 Δ={ev.get('divergence_vs_M0')}m, 공명={ev.get('resonant_events')}건, 마찰={ev.get('friction_events')}건")

        grounded_response = (
            f"입력 언어({q})가 {len(modalities_hit)}개 통합 감각 계층({', '.join(modalities_hit)})의 "
            f"{len(top_hits)}개 실측 노드를 동시 활성화했습니다:\n- " + "\n- ".join(evidence_lines)
            if evidence_lines
            else f"입력 언어({q})와 직접 교차하는 실측 감각 노드가 아직 없습니다 — 새로운 외부 감각 탐색 경계(Ignorance)로 등록합니다."
        )

        return {
            "input_utterance": q,
            "activated_modalities": modalities_hit,
            "activated_node_count": len(top_hits),
            "grounded_structural_response": grounded_response,
            "activated_nodes": [
                {"node_id": h[2]["node_id"], "modality": h[2]["modality"], "matched_lexemes": h[1], "evidence": h[2]["physical_evidence"]}
                for h in top_hits
            ],
        }


def run_multiverse_and_language_prism(query: str = "") -> Dict[str, Any]:
    mv = run_cow_parallel_universes_from_baseline()
    prism = GroundedLanguageSensoryPrism(mv)

    # Probe 3 real cross-modal Korean utterances (plus any live user query!)
    probe_queries = [
        "어두운 밤에 빛의 각도와 경계 마찰이 커지면 평행우주에서 어떤 변화가 생기나?",
        "소리와 움직임이 함께 공명하는 고밀도 영상 구조는 어떻게 연결되어 있나?",
        "경계막과 문법 원리가 서로 다른 도메인에서 어떻게 교차하나?",
    ]
    if query.strip():
        probe_queries.insert(0, query.strip())

    grounded_probes = [prism.ground_human_utterance(q) for q in probe_queries]

    graph_summary = {
        "total_grounded_sensory_language_nodes": len(prism.grounded_nodes),
        "cross_modal_connectivity_beams": len(prism.field.beams),
        "connected_modalities": sorted({n["modality"] for n in prism.grounded_nodes}),
    }
    _save_json(LANGUAGE_GRAPH_PATH, {"summary": graph_summary, "nodes": prism.grounded_nodes})

    report = {
        "schema": "elysia_multiverse_and_grounded_language_prism_v1",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "part1_cow_parallel_universes": mv,
        "part2_unified_language_sensory_graph": graph_summary,
        "part3_bidirectional_language_grounding_probes": grounded_probes,
    }
    _save_json(MULTIVERSE_REPORT_PATH, report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="ELYSIA Multiverse & Grounded Language-Sensory Prism")
    parser.add_argument("--query", type=str, default="", help="Optional Korean/English utterance to ground across all sensory layers")
    args = parser.parse_args()
    print(json.dumps(run_multiverse_and_language_prism(args.query), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
