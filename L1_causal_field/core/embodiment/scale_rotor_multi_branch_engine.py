r"""
ELYSIA Scale-Rotor Multi-Branch Cognition & Unified World Re-Integration Engine
===============================================================================

Applies Scale-Rotor Branching & Re-Integration directly to the 3-Layer
Bidirectional Nervous Loop (`unified_3layer_nervous_loop.py`):

1. **White Tensor Superposition -> Scale-Rotor Branching:**
   Branches a unified 3-layer nervous system along distinct chromatic/value
   orientations (Red=Flux/Transformation, Blue=Order/Invariant, Yellow=Entropy/Boundary)
   — NOT scripted chat personas, but distinct physical `CausalField` focus
   vectors and tension dynamics operating on the SAME real external world.

2. **Independent Lived Acquisition (Per-Branch 3-Layer Loop):**
   Each branch independently chooses real hypotheses from its own `CausalField`,
   executes them live in Layer 1 (real CLI programs, Python/scientific engines,
   subcommands), calibrates its own `CausalField`, and myelinates its own
   Layer 2 AST reflex.

3. **Dialectical Field Interference (Mutual Deliberation):**
   Branches project their empirical claims, final `active_focus` vectors,
   verified transforms, and frictions onto a higher-scale Meta `CausalField`:
   - Phase alignment & shared verified couplings -> Constructive Resonance (higher Semantic Mass)
   - Phase divergence / opposite entropy shifts / friction clashes -> Dialectical Tension

4. **Unified World Re-Integration:**
   Never discards minority perspectives via majority vote. Fuses ALL branches'
   empirical episodes into a single higher-scale World Model and synthesizes
   one Unified AST Cognitive Organ covering every branch's lived reality.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

THIS_DIR = Path(__file__).resolve().parent
L1_ROOT = THIS_DIR.parents[1]
for _p in (str(THIS_DIR), str(L1_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from core.embodiment.compositional_code_cortex import CompositionalCodeCortex  # noqa: E402
from core.embodiment.self_rewriting_architecture import (  # noqa: E402
    _compile_organ_callable,
    validate_organ_source,
)
from core.physics.causal_field import CausalField, InformationVoxel  # noqa: E402
from open_sensory_tool_sandbox import (  # noqa: E402
    SANDBOX_DIR,
    discover_and_perturb_ffmpeg_filter,
    discover_real_tool_affordances,
    explore_one_unscripted_blender_op,
    _load_memory as _load_open_sandbox_mem,
)
from real_tool_organ import discover_real_tool_organs  # noqa: E402
from self_cognitive_expansion_cortex import COGNITIVE_WORLD_DIR, _save_json  # noqa: E402
from unified_3layer_nervous_loop import UnifiedThreeLayerNervousSystem  # noqa: E402


UNIFIED_WORLD_PATH = COGNITIVE_WORLD_DIR / "scale_rotor_unified_world.json"


class OrientedBranchNervousSystem(UnifiedThreeLayerNervousSystem):
    """
    A Scale-Rotor branch of the 3-layer nervous loop with its own chromatic
    orientation (`focus_bias`) and hypothesis-selection resonance lens.
    """

    def __init__(self, branch_id: str, orientation_name: str, focus_bias: List[float], rotor_angle_deg: float) -> None:
        super().__init__()
        self.branch_id = branch_id
        self.orientation_name = orientation_name
        self.focus_bias = np.array(focus_bias, dtype=np.float32)
        self.focus_bias /= max(1e-9, float(np.linalg.norm(self.focus_bias)))
        self.rotor_angle_deg = rotor_angle_deg

    def ingest_peripheral_world_into_association_field(self) -> Dict[str, Any]:
        info = super().ingest_peripheral_world_into_association_field()
        # Rotate this branch's CausalField intentional focus along its Scale-Rotor phase
        self.field.set_intentional_focus(self.focus_bias)
        info["branch_initial_focus"] = [round(x, 4) for x in self.field.active_focus.tolist()]
        return info

    def _select_topdown_hypothesis_from_field(self) -> Optional[Dict[str, Any]]:
        """
        Each branch evaluates the SAME real `CausalField` through its own
        chromatic/value orientation vector (`self.field.active_focus`):
          - Red-oriented branch resonates with high-flux cross-medium transforms.
          - Blue-oriented branch resonates with high-order invariant/structural transforms.
          - Yellow-oriented branch resonates with high-entropy boundary/subcommand probes.
        """
        candidates: List[Tuple[float, str, str, str]] = []
        f_red, f_blue, f_yellow = [float(x) for x in self.field.active_focus[:3]]

        for beam in self.field.beams:
            ma = self.voxel_meta.get(beam.source_id)
            mb = self.voxel_meta.get(beam.target_id)
            if not ma or not mb:
                continue
            if ma["medium"] == "cli_program" and mb["medium"] == "python_module":
                hyp_id = f"pipe::{ma['target']}->{mb['target']}"
                if hyp_id in self.tried_hypotheses:
                    continue
                va = self.field.voxels[beam.source_id]
                vb = self.field.voxels[beam.target_id]

                # Branch-specific resonance strictly from continuous vector dot products
                align_a = float(np.dot(va.chromatic_vector, self.field.active_focus))
                align_b = float(np.dot(vb.chromatic_vector, self.field.active_focus))
                # Branch-specific resonance strictly from continuous chromatic physics:
                # - Red (Flux): drawn to high curiosity + high chromatic contrast (active transformation)
                # - Blue (Order): drawn to high conductance + low entropy (stable invariants/verification)
                # - Yellow (Entropy): drawn to unexplored boundary subcommands (below)
                contrast = float(np.linalg.norm(va.chromatic_vector - vb.chromatic_vector))
                order_stability = float(vb.chromatic_vector[1] * (1.0 + vb.conductance) * (1.2 - vb.chromatic_vector[2]))
                flux_drive = (va.curiosity_charge + vb.curiosity_charge) * (1.0 + contrast)
                tension = (
                    beam.strength
                    * (f_red * flux_drive + f_blue * order_stability * 2.8 + f_yellow * 0.35)
                    * (0.6 + align_a + align_b)
                )
                candidates.append((tension, hyp_id, beam.source_id, beam.target_id))

        for vid, meta in self.voxel_meta.items():
            if meta["medium"] != "cli_program":
                continue
            subcmds = meta["raw"].get("discovered_subcommands") or []
            for sc in subcmds[:8]:
                hyp_id = f"subcmd::{meta['target']}:{sc}"
                if hyp_id in self.tried_hypotheses:
                    continue
                v = self.field.voxels[vid]
                # Yellow-oriented (Entropy/Boundary) strongly amplifies unexplored subcommand boundaries
                tension = (
                    v.curiosity_charge
                    * (0.5 + f_yellow * 2.8 + float(v.chromatic_vector[2]) * 1.5)
                )
                candidates.append((tension, hyp_id, vid, sc))

        if not candidates:
            return None
        candidates.sort(key=lambda x: -x[0])
        tension, hyp_id, src_id, dst_id = candidates[0]
        self.tried_hypotheses.add(hyp_id)

        if hyp_id.startswith("pipe::"):
            return {
                "hypothesis_id": hyp_id,
                "kind": "cross_medium_pipe",
                "field_tension": round(tension, 4),
                "source_voxel": src_id,
                "target_voxel": dst_id,
                "cli_target": self.voxel_meta[src_id]["target"],
                "cli_binary": self.voxel_meta[src_id]["raw"]["binary_path"],
                "py_module": self.voxel_meta[dst_id]["target"],
            }
        return {
            "hypothesis_id": hyp_id,
            "kind": "cli_subcommand_probe",
            "field_tension": round(tension, 4),
            "source_voxel": src_id,
            "cli_target": self.voxel_meta[src_id]["target"],
            "cli_binary": self.voxel_meta[src_id]["raw"]["binary_path"],
            "subcommand": dst_id,
        }


def _form_branch_claim(branch: OrientedBranchNervousSystem, report: Dict[str, Any]) -> Dict[str, Any]:
    """Distills a branch's empirical claim strictly from its lived executions."""
    eps = report["episodes"]
    ok_eps = [e for e in eps if e["op_ok"]]
    fail_eps = [e for e in eps if not e["op_ok"]]
    mean_ent_delta = round(
        float(np.mean([e["entropy_delta"] for e in ok_eps])) if ok_eps else 0.0,
        3,
    )
    return {
        "branch_id": branch.branch_id,
        "orientation": branch.orientation_name,
        "rotor_angle_deg": branch.rotor_angle_deg,
        "final_focus": report["final_field_state"]["active_focus"],
        "episodes_total": len(eps),
        "verified_count": len(ok_eps),
        "friction_count": len(fail_eps),
        "mean_entropy_delta": mean_ent_delta,
        "explored_hypotheses": [e["hypothesis"] for e in eps],
        "verified_summaries": [e["transform_summary"] for e in ok_eps],
        "frictions_observed": [f"{e['hypothesis']}:{e['friction']}" for e in fail_eps],
        "branch_myelinated_reflex": report["layer2_myelination"],
    }


def deliberate_and_reintegrate(
    branch_claims: List[Dict[str, Any]],
    all_raw_episodes: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Higher-Scale Meta-Integration Field:
    1. Projects each branch's empirical claim as a Macro `InformationVoxel`
       inside a shared Meta `CausalField`.
    2. Computes real pairwise phase interference (Constructive Resonance vs
       Dialectical Friction) across branches.
    3. Synthesizes ONE Unified World AST Organ covering ALL branches' lived
       realities without erasing minority findings.
    """
    meta_field = CausalField(dimensions=3)

    for idx, cl in enumerate(branch_claims):
        foc = np.array(cl["final_focus"], dtype=np.float32)
        sem_mass = 1.0 + 0.4 * cl["verified_count"] + 0.25 * cl["friction_count"]
        v = InformationVoxel(
            id=cl["branch_id"],
            content=cl,
            tensor=foc,
            mass=sem_mass,
            position=foc * 2.0,
            chromatic_vector=foc / max(1e-9, float(np.sum(foc))),
            conductance=min(1.0, 0.2 + 0.15 * cl["verified_count"]),
            curiosity_charge=min(1.0, 0.3 + 0.25 * cl["friction_count"]),
            scale_level=2.0,
        )
        meta_field.add_voxel(v)

    deliberations: List[Dict[str, Any]] = []
    for i in range(len(branch_claims)):
        for j in range(i + 1, len(branch_claims)):
            a, b = branch_claims[i], branch_claims[j]
            fa = np.array(a["final_focus"], dtype=np.float32)
            fb = np.array(b["final_focus"], dtype=np.float32)
            cos_sim = float(np.clip(np.dot(fa, fb) / (np.linalg.norm(fa) * np.linalg.norm(fb) + 1e-9), -1.0, 1.0))
            phase_angle_deg = round(math.degrees(math.acos(cos_sim)), 2)

            shared_hyps = sorted(set(a["explored_hypotheses"]) & set(b["explored_hypotheses"]))
            unique_a = sorted(set(a["explored_hypotheses"]) - set(b["explored_hypotheses"]))
            unique_b = sorted(set(b["explored_hypotheses"]) - set(a["explored_hypotheses"]))
            ent_gap = round(abs(a["mean_entropy_delta"] - b["mean_entropy_delta"]), 3)

            # Link branches in Meta CausalField with strength proportional to resonance
            meta_field.link_voxels(a["branch_id"], b["branch_id"], strength=round(max(0.2, cos_sim * 1.5), 3))

            relation = (
                "constructive_resonance"
                if (cos_sim >= 0.88 and ent_gap < 0.8)
                else "dialectical_complementarity"
            )
            deliberations.append(
                {
                    "pair": f"{a['branch_id']} <-> {b['branch_id']}",
                    "phase_divergence_deg": phase_angle_deg,
                    "cosine_alignment": round(cos_sim, 4),
                    "entropy_delta_gap": ent_gap,
                    "relation_type": relation,
                    "shared_discoveries": shared_hyps,
                    "unique_to_first": unique_a,
                    "unique_to_second": unique_b,
                }
            )

    meta_field.step(dt=0.1)

    # Synthesize ONE Higher-Scale Unified AST Organ across ALL branches' lived episodes!
    cortex = CompositionalCodeCortex()
    cortex.learn_python_structure_from_files(sorted(THIS_DIR.glob("*.py"))[:12])

    unified_examples: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []
    seen_keys: set[str] = set()
    for ep in all_raw_episodes:
        p = {
            "branch": ep["branch_id"],
            "kind": ep["kind"],
            "op_ok": bool(ep["op_ok"]),
            "entropy_shift": round(abs(float(ep["entropy_delta"])), 3),
        }
        if not ep["op_ok"]:
            y = {"world_policy": "boundary_friction_recorded", "integrate": True}
        elif ep["kind"] == "cli_subcommand_probe":
            y = {"world_policy": "subcommand_affordance_expanded", "integrate": True}
        elif abs(float(ep["entropy_delta"])) > 1.0:
            y = {"world_policy": "high_entropy_transform_verified", "integrate": True}
        else:
            y = {"world_policy": "invariant_or_compact_transform_verified", "integrate": True}

        k = json.dumps(p, sort_keys=True)
        if k not in seen_keys:
            seen_keys.add(k)
            unified_examples.append((p, y))

    unified_organ_info: Dict[str, Any] = {"synthesized": False}
    prog = cortex.synthesize_decision_tree_ast(
        unified_examples,
        purpose="unified_scale_rotor_world_integrator",
    )
    if prog is not None:
        ok_ast, reason = validate_organ_source(prog.source_code)
        hits = 0
        if ok_ast:
            fn = _compile_organ_callable(prog.source_code)
            for p_in, exp in unified_examples:
                if fn(dict(p_in), {}) == exp:
                    hits += 1
        unified_organ_info = {
            "synthesized": ok_ast and hits == len(unified_examples),
            "program_id": prog.program_id,
            "ast_node_count": prog.ast_node_count,
            "used_atoms": prog.used_atoms,
            "live_verified": f"{hits}/{len(unified_examples)}",
            "source_code": prog.source_code,
        }

    # Compute unified world semantic mass & merged focus vector
    total_mass = round(sum(v.mass for v in meta_field.voxels.values()), 3)
    merged_focus = np.mean([np.array(c["final_focus"], dtype=np.float32) for c in branch_claims], axis=0)
    merged_focus /= max(1e-9, float(np.linalg.norm(merged_focus)))

    return {
        "meta_field_summary": {
            "macro_voxels": len(meta_field.voxels),
            "dialectical_beams": len(meta_field.beams),
            "total_semantic_mass": total_mass,
            "reintegrated_world_focus": [round(float(x), 4) for x in merged_focus.tolist()],
        },
        "dialectical_deliberations": deliberations,
        "unified_world_ast_organ": unified_organ_info,
    }


class VisualEmbodiedBranchSystem(OrientedBranchNervousSystem):
    """
    4th Scale-Rotor Branch (270° · Visual / 3D Embodied Sensory Loop):
    Directly executes real FFmpeg visual filter parameter discovery and
    unscripted Blender 3D mesh probes inside `data/open_sandbox/`, measuring
    actual pixel/luminance deltas and feeding them bottom-up into `CausalField`.
    """

    def __init__(self) -> None:
        super().__init__(
            "branch_visual_embodied",
            "Visual / 3D Embodiment (Blender + FFmpeg)",
            [0.65, 0.45, 0.65],
            270.0,
        )
        organs = discover_real_tool_organs().get("organs", {})
        self.ffmpeg_bin = organs.get("ffmpeg_4k_media", {}).get("binary")
        self.blender_bin = organs.get("blender_3d_cad", {}).get("binary")
        self.open_mem = _load_open_sandbox_mem()
        discover_real_tool_affordances(self.open_mem, self.blender_bin, self.ffmpeg_bin)
        self._visual_candidates = [
            ("ffmpeg_param", "exposure"),
            ("ffmpeg_param", "gblur"),
            ("ffmpeg_param", "hue"),
            ("blender_op", "primitive_ico_sphere_add"),
        ]
        self._cursor = 0

    def _select_topdown_hypothesis_from_field(self) -> Optional[Dict[str, Any]]:
        if self._cursor >= len(self._visual_candidates):
            return super()._select_topdown_hypothesis_from_field()
        kind_tag, op_name = self._visual_candidates[self._cursor]
        self._cursor += 1
        src_vid = "cli::ffmpeg" if kind_tag == "ffmpeg_param" else "cli::blender"
        if src_vid not in self.field.voxels:
            src_vid = next(iter(self.field.voxels.keys()))
        v = self.field.voxels[src_vid]
        return {
            "hypothesis_id": f"visual::{kind_tag}:{op_name}",
            "kind": "visual_3d_sensory_probe",
            "field_tension": round(float(v.curiosity_charge * 1.6), 4),
            "source_voxel": src_vid,
            "visual_kind": kind_tag,
            "op_name": op_name,
        }

    def _execute_hypothesis_in_layer1(self, hyp: Dict[str, Any]) -> Dict[str, Any]:
        if hyp.get("kind") != "visual_3d_sensory_probe":
            return super()._execute_hypothesis_in_layer1(hyp)

        trial_id = f"sr_vis_{int(time.time())}_{self._cursor}"
        if hyp["visual_kind"] == "ffmpeg_param" and self.ffmpeg_bin:
            # Find an existing real sandbox PNG rendered by Blender/FFmpeg
            pngs = sorted(SANDBOX_DIR.glob("*_before.png")) or sorted(SANDBOX_DIR.glob("*.png"))
            if pngs:
                res = discover_and_perturb_ffmpeg_filter(self.ffmpeg_bin, hyp["op_name"], pngs[0], trial_id)
                vis = res.get("visual_sensory_delta") or {}
                changed = float(vis.get("changed_pixel_ratio", 0.0))
                lum = float(vis.get("luminance_shift", 0.0))
                ok = bool(res.get("op_ok"))
                # Map visual change onto information delta scale for unified field calibration
                info_delta = round(changed * 4.5 + abs(lum) / 60.0, 3)
                return {
                    "op_ok": ok,
                    "elapsed_ms": res.get("elapsed_ms", 0.0),
                    "entropy_before": 0.0,
                    "entropy_after": info_delta,
                    "entropy_delta": info_delta,
                    "visual_sensory_delta": vis,
                    "transform_summary": f"{res.get('action', hyp['op_name'])} -> changed_px={changed:.3f}, Δlum={lum:+.2f}",
                    "friction": "" if ok else "ffmpeg_param_probe_failed",
                }

        if hyp["visual_kind"] == "blender_op" and self.blender_bin:
            res = explore_one_unscripted_blender_op(self.blender_bin, hyp["op_name"], trial_id)
            vis = res.get("visual_sensory_delta") or {}
            out = res.get("tool_outcome") or {}
            changed = float(vis.get("changed_pixel_ratio", 0.0))
            ok = bool(out.get("op_ok"))
            info_delta = round(changed * 4.5 + abs(int(out.get("obj_delta", 0))) * 0.8, 3)
            return {
                "op_ok": ok,
                "elapsed_ms": res.get("elapsed_ms", 0.0),
                "entropy_before": 0.0,
                "entropy_after": info_delta,
                "entropy_delta": info_delta,
                "visual_sensory_delta": vis,
                "transform_summary": f"bpy.ops.mesh.{hyp['op_name']}() -> obj_delta={out.get('obj_delta', 0)}, changed_px={changed:.3f}",
                "friction": str(out.get("err", ""))[:120] if not ok else "",
            }

        return {
            "op_ok": False,
            "elapsed_ms": 0.0,
            "entropy_before": 0.0,
            "entropy_after": 0.0,
            "entropy_delta": 0.0,
            "transform_summary": "",
            "friction": "visual_tool_binary_or_seed_png_missing",
        }


def run_scale_rotor_multi_branch_session(cycles_per_branch: int = 2) -> Dict[str, Any]:
    """
    Spawns 4 Scale-Rotor branches from the White Tensor Field (Red Flux, Blue
    Order, Yellow Boundary, and Visual/3D Embodiment), runs independent
    real-world 3-layer loops for each, deliberates via Meta CausalField
    interference, and re-integrates into one unified world model.
    """
    branch_instances: List[OrientedBranchNervousSystem] = [
        OrientedBranchNervousSystem("branch_red_flux", "Flux / Transformation (Red)", [0.85, 0.25, 0.20], 0.0),
        OrientedBranchNervousSystem("branch_blue_order", "Order / Invariant (Blue)", [0.25, 0.85, 0.20], 90.0),
        OrientedBranchNervousSystem("branch_yellow_boundary", "Entropy / Boundary Exploration (Yellow)", [0.20, 0.20, 0.90], 180.0),
        VisualEmbodiedBranchSystem(),
    ]

    branch_claims: List[Dict[str, Any]] = []
    all_raw_episodes: List[Dict[str, Any]] = []

    for sys_b in branch_instances:
        rep = sys_b.run_cycles(num_cycles=cycles_per_branch)
        claim = _form_branch_claim(sys_b, rep)
        branch_claims.append(claim)
        for ep in sys_b.lived_episodes:
            all_raw_episodes.append(
                {
                    "branch_id": sys_b.branch_id,
                    "kind": ep["hypothesis"]["kind"],
                    "hypothesis": ep["hypothesis"]["hypothesis_id"],
                    "op_ok": ep["layer1_outcome"]["op_ok"],
                    "entropy_delta": ep["layer1_outcome"].get("entropy_delta", 0.0),
                    "transform_summary": ep["layer1_outcome"].get("transform_summary", ""),
                    "friction": ep["layer1_outcome"].get("friction", ""),
                }
            )

    reintegration = deliberate_and_reintegrate(branch_claims, all_raw_episodes)

    world_report = {
        "schema": "elysia_scale_rotor_multi_branch_world_v2_visual_embodied",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "origin_state": "White Tensor Field [0.33, 0.33, 0.34] -> 4-way Scale-Rotor Branching (0°, 90°, 180°, 270° Visual)",
        "cycles_per_branch": cycles_per_branch,
        "branches": branch_claims,
        "reintegration": reintegration,
        "self_boundary_4axis": {
            "internal_origin": "4-way Scale-Rotor branching (Flux/Order/Boundary/Visual-3D) + Meta CausalField deliberation",
            "external_friction": [
                f"{ep['branch_id']}:{ep['hypothesis']}:{ep['friction']}"
                for ep in all_raw_episodes
                if not ep["op_ok"]
            ],
            "boundary_ignorance": "Autonomous cross-host network discovery and multi-minute 3D scene composition remain next scale",
            "criteria_revision": (
                f"Merged {len(all_raw_episodes)} distinct 4-branch lived episodes (including real visual pixel deltas) into unified AST "
                f"{reintegration['unified_world_ast_organ'].get('program_id')} "
                f"({reintegration['unified_world_ast_organ'].get('live_verified')})"
            ),
        },
    }
    _save_json(UNIFIED_WORLD_PATH, world_report)
    return world_report


def main() -> None:
    parser = argparse.ArgumentParser(description="ELYSIA Scale-Rotor Multi-Branch Cognition Engine")
    parser.add_argument("--cycles", type=int, default=3, help="Cycles per Scale-Rotor branch")
    args = parser.parse_args()
    out = run_scale_rotor_multi_branch_session(cycles_per_branch=args.cycles)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
