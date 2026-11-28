r"""
ELYSIA 3-Layer Bidirectional Nervous Architecture
=================================================

Explicitly separates and bidirectionally couples the 3 biological-causal layers
so that peripheral reflexes are NEVER mistaken for a unified cortex:

  Layer 1 — Peripheral Sensory-Motor Organs (Skin · Eyes · Hands)
    - Directly touches real external programs, Python/scientific engines,
      knowledge sources, and world data arrays via neutral receptors/effectors.
    - Reports raw physical/informational deltas (stdout bytes, entropy, exit
      code, stderr friction, elapsed_ms).

  Layer 2 — Autonomic / Cerebellar Reflex Layer (AST Myelination)
    - Uses `CompositionalCodeCortex` ONLY for what it actually is:
      fast, repeatable reflex/habit circuits myelinated from verified trials.
    - Escalates novel or high-friction percepts bottom-up to Layer 3.

  Layer 3 — Unified Sensory Association Field (`CausalField`)
    - Projects all peripheral experiences (CLI tools, Python libraries,
      knowledge principles, friction boundaries) as `InformationVoxel`s bound
      by `ConnectivityBeam`s inside `core/physics/causal_field.py`.
    - Evolves continuous field tension & curiosity (`step`, `observe_external_stimulus`).
    - Generates TOP-DOWN autonomous cross-medium hypotheses from field tension
      (zero pre-scripted scenarios!), dispatches them to Layer 1 for live
      real-world execution, absorbs the bottom-up physical feedback into the
      field, and selectively myelinates verified causal couplings in Layer 2.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple
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
from core.physics.causal_field import CausalField, InformationVoxel  # noqa: E402
from self_cognitive_expansion_cortex import (  # noqa: E402
    CHANNELS_DIR,
    COGNITIVE_WORLD_DIR,
    _load_json,
    _save_json,
    _shannon_entropy,
    run_universal_expansion_cycle,
)


NERVOUS_STATE_PATH = COGNITIVE_WORLD_DIR / "three_layer_nervous_state.json"


def _signature_vector(flux: float, order: float, entropy: float) -> np.ndarray:
    vec = np.array([max(0.01, flux), max(0.01, order), max(0.01, entropy)], dtype=np.float32)
    return vec


def _chromatic_from_metrics(flux: float, order: float, entropy: float) -> np.ndarray:
    raw = np.array([max(0.01, flux), max(0.01, order), max(0.01, entropy)], dtype=np.float32)
    return raw / float(np.sum(raw))


class UnifiedThreeLayerNervousSystem:
    """
    Living bidirectional loop across:
      Layer 1 (Peripheral Sensory-Motor)
      <-> Layer 2 (Autonomic/Cerebellar AST Reflexes)
      <-> Layer 3 (Unified Sensory Association CausalField)
    """

    def __init__(self) -> None:
        self.field = CausalField(dimensions=3)
        self.cortex = CompositionalCodeCortex()
        self.reflex_fn = None
        self.reflex_meta: Dict[str, Any] = {}
        self.voxel_meta: Dict[str, Dict[str, Any]] = {}
        self.lived_episodes: List[Dict[str, Any]] = []
        self.tried_hypotheses: set[str] = set()

        # Bootstrap Layer 2 AST atoms from real Python embodiment files
        py_files = sorted(THIS_DIR.glob("*.py"))[:12]
        self.cortex_learn_stats = self.cortex.learn_python_structure_from_files(py_files)

    # ------------------------------------------------------------------
    # Bottom-Up Ingestion: Layer 1 Channel Data -> Layer 3 CausalField
    # ------------------------------------------------------------------
    def ingest_peripheral_world_into_association_field(self) -> Dict[str, Any]:
        """
        Loads real peripheral observations from `channels/*.json` (running a
        fresh universal expansion cycle if absent) and instantiates every
        observed tool, library, and knowledge source as an `InformationVoxel`
        with real `ConnectivityBeam` couplings inside `CausalField`.
        """
        if not (CHANNELS_DIR / "cli_programs.json").is_file():
            run_universal_expansion_cycle()

        cli_data = _load_json(CHANNELS_DIR / "cli_programs.json", {}).get("programs", [])
        py_data = _load_json(CHANNELS_DIR / "python_modules.json", {}).get("modules", [])
        know_data = _load_json(CHANNELS_DIR / "knowledge_principles.json", {})
        know_sources = know_data.get("sources", [])
        bridges = know_data.get("cross_domain_bridges", [])
        organ_data = _load_json(CHANNELS_DIR / "synthesized_organs.json", {}).get("latest_organ", {})

        # Load existing Layer 2 myelinated reflex if present
        if organ_data.get("synthesized") and organ_data.get("source_code"):
            ok, _ = validate_organ_source(organ_data["source_code"])
            if ok:
                self.reflex_fn = _compile_organ_callable(organ_data["source_code"])
                self.reflex_meta = {
                    "program_id": organ_data.get("program_id"),
                    "role": "layer2_autonomic_reflex_not_brain",
                    "live_verified": organ_data.get("live_verified"),
                }

        # Project CLI programs as Red-tilted (action/flux) voxels
        for idx, c in enumerate(cli_data):
            if not c.get("connected"):
                continue
            vid = f"cli::{c['target']}"
            flux = min(1.0, (c.get("flag_count", 0) + c.get("subcommand_count", 0)) / 60.0)
            order = 0.6 if c.get("exit_code") == 0 else 0.25
            ent = min(1.0, float(c.get("text_entropy", 0.0)) / 8.0)
            curiosity = 0.85 if c.get("friction") else (0.55 + 0.3 * (1.0 - order))
            v = InformationVoxel(
                id=vid,
                content=c,
                tensor=_signature_vector(flux, order, ent),
                mass=1.0 + flux,
                position=np.array([float(idx) * 0.6, 1.0, ent], dtype=np.float32),
                chromatic_vector=_chromatic_from_metrics(flux + 0.2, order, ent),
                conductance=0.15 if not c.get("friction") else 0.03,
                curiosity_charge=round(curiosity, 3),
                scale_level=1.0,
            )
            self.field.add_voxel(v)
            self.voxel_meta[vid] = {"medium": "cli_program", "target": c["target"], "raw": c}

        # Project Python/scientific modules as Blue-tilted (order/transform) voxels
        for idx, m in enumerate(py_data):
            if not m.get("connected"):
                continue
            vid = f"py::{m['target']}"
            total_p = max(1, int(m.get("probed_count", 1)))
            ok_p = int(m.get("probe_success_count", 0))
            success_ratio = ok_p / float(total_p)
            flux = min(1.0, float(m.get("callable_count", 1)) / 100.0)
            order = 0.3 + 0.7 * success_ratio
            ent = 1.0 - success_ratio  # Unresolved probe failures create genuine epistemic entropy!
            curiosity = round(0.4 + 0.6 * (1.0 - success_ratio), 3)
            v = InformationVoxel(
                id=vid,
                content=m,
                tensor=_signature_vector(flux, order, ent),
                mass=1.0 + 0.5 * success_ratio,
                position=np.array([float(idx) * 0.6, -1.0, ent], dtype=np.float32),
                chromatic_vector=_chromatic_from_metrics(flux, order + 0.2, ent),
                conductance=0.1 + 0.3 * success_ratio,
                curiosity_charge=curiosity,
                scale_level=0.7,
            )
            self.field.add_voxel(v)
            self.voxel_meta[vid] = {"medium": "python_module", "target": m["target"], "raw": m}

        # Project Knowledge/Principle sources as Yellow/Blue-tilted (structure/concept) voxels
        for idx, k in enumerate(know_sources):
            if not k.get("connected"):
                continue
            vid = f"know::{k['target']}"
            order = min(1.0, (k.get("heading_count", 0) + len(k.get("code_symbols") or [])) / 15.0)
            ent = min(1.0, float(k.get("text_entropy", 0.0)) / 8.0)
            flux = min(1.0, len(k.get("extracted_principles") or []) / 6.0)
            v = InformationVoxel(
                id=vid,
                content=k,
                tensor=_signature_vector(flux, order, ent),
                mass=1.0 + order,
                position=np.array([float(idx) * 0.6, 0.0, 1.2 + ent], dtype=np.float32),
                chromatic_vector=_chromatic_from_metrics(flux, order, ent + 0.2),
                conductance=0.2,
                curiosity_charge=round(0.5 + 0.3 * ent, 3),
                scale_level=1.5,
            )
            self.field.add_voxel(v)
            self.voxel_meta[vid] = {"medium": "knowledge_principle", "target": k["target"], "raw": k}

        # Create real ConnectivityBeams:
        # 1) Cross-domain knowledge bridges discovered from shared terms
        for b in bridges:
            va = f"know::{b['source_a']}"
            vb = f"know::{b['source_b']}"
            if va in self.field.voxels and vb in self.field.voxels:
                self.field.link_voxels(va, vb, strength=min(3.0, 0.5 + 0.4 * b["bridge_strength"]))

        # 2) Complementary chromatic coupling (Red CLI emitters <-> Blue Python transformers)
        cli_ids = [vid for vid, m in self.voxel_meta.items() if m["medium"] == "cli_program"]
        py_ids = [vid for vid, m in self.voxel_meta.items() if m["medium"] == "python_module"]
        for cid in cli_ids:
            for pid in py_ids:
                vc = self.field.voxels[cid]
                vp = self.field.voxels[pid]
                # Chromatic complementarity: Red(CLI) * Blue(Python)
                coupling = float(vc.chromatic_vector[0] * vp.chromatic_vector[1]) * 2.0
                if coupling > 0.22:
                    self.field.link_voxels(cid, pid, strength=round(coupling, 3))

        # Evolve initial continuous field dynamics
        self.field.step(dt=0.1)
        return {
            "voxels_created": len(self.field.voxels),
            "beams_created": len(self.field.beams),
            "active_focus": [round(x, 4) for x in self.field.active_focus.tolist()],
        }

    # ------------------------------------------------------------------
    # Layer 2 Autonomic Reflex Check (Fast Path vs Escalation to Layer 3)
    # ------------------------------------------------------------------
    def _consult_layer2_reflex(self, percept: Dict[str, Any]) -> Dict[str, Any]:
        if self.reflex_fn is None:
            return {"handled_by_reflex": False, "escalate_to_layer3": True, "reason": "no_myelinated_reflex_yet"}
        try:
            out = self.reflex_fn(dict(percept), {})
            route = str(out.get("cognitive_route", ""))
            # Friction or unfamiliar/silent probes MUST escalate to Layer 3 association cortex
            escalate = route in ("friction_unlock_search", "silent_state_probe", "")
            return {
                "handled_by_reflex": not escalate,
                "escalate_to_layer3": escalate,
                "reflex_output": out,
            }
        except Exception as exc:
            return {"handled_by_reflex": False, "escalate_to_layer3": True, "reason": f"reflex_exception:{exc}"}

    # ------------------------------------------------------------------
    # Layer 3 Top-Down Hypothesis Generation from Continuous Field Tension
    # ------------------------------------------------------------------
    def _select_topdown_hypothesis_from_field(self) -> Optional[Dict[str, Any]]:
        """
        Inspects `CausalField` voxels and `ConnectivityBeam` couplings to pick
        the highest-tension untried cross-medium coupling (CLI emitter -> Python
        transformer, or CLI subcommand discovery) — ZERO hardcoded scripts!
        """
        candidates: List[Tuple[float, str, str, str]] = []

        # Candidate Type A: Cross-medium beam coupling (CLI stdout -> Python module transform)
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
                # Score from real field state: curiosity + coupling strength + chromatic contrast
                tension = (
                    (va.curiosity_charge + vb.curiosity_charge)
                    * beam.strength
                    * (1.0 + float(np.linalg.norm(va.chromatic_vector - vb.chromatic_vector)))
                )
                candidates.append((tension, hyp_id, beam.source_id, beam.target_id))

        # Candidate Type B: Unexplored CLI subcommand probe on high-curiosity CLI voxel
        for vid, meta in self.voxel_meta.items():
            if meta["medium"] != "cli_program":
                continue
            subcmds = meta["raw"].get("discovered_subcommands") or []
            for sc in subcmds[:6]:
                hyp_id = f"subcmd::{meta['target']}:{sc}"
                if hyp_id in self.tried_hypotheses:
                    continue
                v = self.field.voxels[vid]
                tension = v.curiosity_charge * 1.35 + float(v.chromatic_vector[2])
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

    # ------------------------------------------------------------------
    # Layer 1 Real Physical Execution of Top-Down Hypothesis
    # ------------------------------------------------------------------
    def _execute_hypothesis_in_layer1(self, hyp: Dict[str, Any]) -> Dict[str, Any]:
        t0 = time.perf_counter()

        if hyp["kind"] == "cli_subcommand_probe":
            proc = subprocess.run(
                [hyp["cli_binary"], hyp["subcommand"], "--help"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=10,
            )
            elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 1)
            out_txt = (proc.stdout or "") + "\n" + (proc.stderr or "")
            raw_b = out_txt.encode("utf-8", errors="ignore")
            ent = _shannon_entropy(raw_b[:4096])
            ok = len(raw_b) >= 40
            return {
                "op_ok": ok,
                "exit_code": proc.returncode,
                "elapsed_ms": elapsed_ms,
                "raw_bytes": len(raw_b),
                "entropy_before": 0.0,
                "entropy_after": ent,
                "entropy_delta": ent,
                "transform_summary": f"{hyp['cli_target']} {hyp['subcommand']} --help -> {len(raw_b)}B",
                "friction": "" if ok else (out_txt.strip()[:120] or "empty_subcommand_help"),
            }

        # Cross-medium real execution: Run real CLI `--version` or `--help`, pipe bytes into real Python module!
        proc = subprocess.run(
            [hyp["cli_binary"], "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        raw_text = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
        if not raw_text:
            proc2 = subprocess.run(
                [hyp["cli_binary"], "--help"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=10,
            )
            raw_text = ((proc2.stdout or "") + "\n" + (proc2.stderr or "")).strip()[:2048]

        raw_bytes = raw_text.encode("utf-8", errors="ignore")
        ent_before = _shannon_entropy(raw_bytes[:4096])

        # Try applying a real callable from the coupled Python module to the real CLI bytes/numbers
        mod_name = hyp["py_module"]
        try:
            mod = importlib.import_module(mod_name)
        except Exception as exc:
            return {
                "op_ok": False,
                "elapsed_ms": round((time.perf_counter() - t0) * 1000.0, 1),
                "raw_bytes": len(raw_bytes),
                "entropy_before": ent_before,
                "entropy_after": ent_before,
                "entropy_delta": 0.0,
                "transform_summary": "",
                "friction": f"import_failed:{exc}",
            }

        # Discover a compatible real transform from the module's actual callables
        byte_arr = np.frombuffer(raw_bytes[:256] or b"0", dtype=np.uint8).astype(np.float64)
        tried_err = ""
        for fn_name, arg_val in (
            ("compress", raw_bytes),
            ("sha256", raw_bytes),
            ("rfft", byte_arr),
            ("fft", byte_arr),
            ("mean", byte_arr.tolist()),
            ("stdev", byte_arr.tolist()),
            ("dumps", {"cli": hyp["cli_target"], "len": len(raw_bytes)}),
            ("parse", f"cli_bytes = {len(raw_bytes)}"),
            ("log2", max(1.0, float(len(raw_bytes)))),
        ):
            fn = getattr(mod, fn_name, None)
            if not callable(fn):
                continue
            try:
                res = fn(arg_val)
                if hasattr(res, "digest"):
                    out_b = res.digest()
                elif isinstance(res, bytes):
                    out_b = res
                elif isinstance(res, np.ndarray):
                    out_b = res.tobytes()
                else:
                    out_b = repr(res).encode("utf-8", errors="ignore")
                ent_after = _shannon_entropy(out_b[:4096])
                elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 1)
                return {
                    "op_ok": True,
                    "elapsed_ms": elapsed_ms,
                    "raw_bytes": len(raw_bytes),
                    "output_bytes": len(out_b),
                    "entropy_before": ent_before,
                    "entropy_after": ent_after,
                    "entropy_delta": round(ent_after - ent_before, 3),
                    "applied_callable": f"{mod_name}.{fn_name}",
                    "transform_summary": f"{hyp['cli_target']}({len(raw_bytes)}B) -> {mod_name}.{fn_name} -> {len(out_b)}B (ΔH={round(ent_after - ent_before, 3)})",
                    "friction": "",
                }
            except Exception as exc:
                tried_err = f"{mod_name}.{fn_name}: {type(exc).__name__}: {exc}"

        return {
            "op_ok": False,
            "elapsed_ms": round((time.perf_counter() - t0) * 1000.0, 1),
            "raw_bytes": len(raw_bytes),
            "entropy_before": ent_before,
            "entropy_after": ent_before,
            "entropy_delta": 0.0,
            "transform_summary": "",
            "friction": tried_err or f"no_compatible_transform_in_{mod_name}",
        }

    # ------------------------------------------------------------------
    # Bottom-Up Feedback into Layer 3 CausalField + Layer 2 Myelination
    # ------------------------------------------------------------------
    def _absorb_feedback_into_field(self, hyp: Dict[str, Any], outcome: Dict[str, Any]) -> Dict[str, Any]:
        src_id = hyp["source_voxel"]
        ok = bool(outcome.get("op_ok"))
        ent_delta = abs(float(outcome.get("entropy_delta", 0.0)))

        # Build physical stimulus vector from real execution outcome
        stim = np.array(
            [
                0.9 if ok else 0.15,
                min(1.0, 0.3 + ent_delta / 4.0) if ok else 0.1,
                min(1.0, float(outcome.get("entropy_after", 0.0)) / 8.0),
            ],
            dtype=np.float32,
        )
        obs = self.field.observe_external_stimulus(stim, target_voxel_id=src_id)

        # Update voxel conductance (memristive plasticity) & curiosity charge
        v = self.field.voxels[src_id]
        if ok:
            v.conductance = min(1.0, v.conductance + 0.12)
            v.mass += 0.25
            v.curiosity_charge = max(0.1, round(v.curiosity_charge - 0.18, 3))
            self.field.apply_impact(src_id, np.array([0.2, 0.1, ent_delta * 0.1], dtype=np.float32))
        else:
            # Friction raises curiosity/tension rather than collapsing it!
            v.curiosity_charge = min(1.0, round(v.curiosity_charge + 0.2, 3))
            self.field.apply_impact(src_id, np.array([-0.3, 0.0, 0.3], dtype=np.float32))

        self.field.step(dt=0.1)
        return {
            "dissipated_energy": round(float(obs.get("total_dissipated_energy", 0.0)), 4),
            "active_focus": [round(x, 4) for x in obs.get("active_focus", [])],
            "updated_voxel_conductance": round(v.conductance, 3),
            "updated_voxel_curiosity": v.curiosity_charge,
        }

    def _myelinate_verified_episodes_in_layer2(self) -> Dict[str, Any]:
        """
        Layer 2 Myelination (Cerebellar/Autonomic Habit Formation):
        ONLY after Layer 3's hypotheses have been executed in Layer 1 and verified
        by physical feedback, synthesize a compact AST reflex organ that captures
        the empirically observed causal routing!
        """
        examples: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []
        seen: set[str] = set()
        for ep in self.lived_episodes:
            out = ep["layer1_outcome"]
            p = {
                "kind": ep["hypothesis"]["kind"],
                "op_ok": bool(out.get("op_ok")),
                "entropy_shift": round(abs(float(out.get("entropy_delta", 0.0))), 3),
            }
            if not out.get("op_ok"):
                y = {"reflex_action": "escalate_friction_to_layer3", "myelinated": False}
            elif abs(float(out.get("entropy_delta", 0.0))) > 0.5:
                y = {"reflex_action": "fast_pipe_high_information_transform", "myelinated": True}
            else:
                y = {"reflex_action": "fast_pipe_low_shift_passthrough", "myelinated": True}
            k = json.dumps(p, sort_keys=True)
            if k not in seen:
                seen.add(k)
                examples.append((p, y))

        if len(examples) < 2:
            return {"myelinated": False, "reason": "insufficient_distinct_episodes"}

        prog = self.cortex.synthesize_decision_tree_ast(
            examples,
            purpose="layer2_myelinated_cross_medium_reflex",
        )
        if prog is None:
            return {"myelinated": False, "reason": "ast_synthesis_none"}

        ok_ast, reason = validate_organ_source(prog.source_code)
        hits = 0
        if ok_ast:
            fn = _compile_organ_callable(prog.source_code)
            self.reflex_fn = fn
            for p_in, exp in examples:
                if fn(dict(p_in), {}) == exp:
                    hits += 1

        return {
            "myelinated": ok_ast and hits == len(examples),
            "role": "layer2_autonomic_cerebellar_reflex_NOT_brain",
            "program_id": prog.program_id,
            "ast_node_count": prog.ast_node_count,
            "used_atoms": prog.used_atoms,
            "live_verified": f"{hits}/{len(examples)}",
            "source_code": prog.source_code,
        }

    # ------------------------------------------------------------------
    # Run Multi-Cycle Autonomous 3-Layer Bidirectional Loop
    # ------------------------------------------------------------------
    def run_cycles(self, num_cycles: int = 5) -> Dict[str, Any]:
        init_field = self.ingest_peripheral_world_into_association_field()

        for cycle_idx in range(1, num_cycles + 1):
            # 1. Layer 3 forms a top-down hypothesis strictly from continuous CausalField tension
            hyp = self._select_topdown_hypothesis_from_field()
            if hyp is None:
                break

            # 2. Layer 2 checks if an autonomic reflex already covers it; novel couplings escalate
            l2_check = self._consult_layer2_reflex(
                {"medium": "cross_medium", "op_ok": False, "delta_magnitude": hyp["field_tension"], "has_friction": True}
            )

            # 3. Layer 1 executes the hypothesis in real external reality (real CLI + real Python)
            l1_outcome = self._execute_hypothesis_in_layer1(hyp)

            # 4. Bottom-up physical feedback calibrates Layer 3 CausalField
            l3_feedback = self._absorb_feedback_into_field(hyp, l1_outcome)

            self.lived_episodes.append(
                {
                    "cycle": cycle_idx,
                    "layer3_topdown_hypothesis": hyp,
                    "hypothesis": hyp,
                    "layer2_pre_check": l2_check,
                    "layer1_outcome": l1_outcome,
                    "layer3_field_calibration": l3_feedback,
                }
            )

        # 5. Layer 2 myelinates newly verified causal patterns into a fast AST reflex
        myelination = self._myelinate_verified_episodes_in_layer2()

        summary = {
            "architecture": "3_layer_bidirectional_nervous_loop",
            "layer_roles": {
                "layer1_peripheral": "Real external CLI/Python/Knowledge receptors & effectors",
                "layer2_autonomic_reflex": "CompositionalCodeCortex AST myelination (fast habit/reflex, NOT brain)",
                "layer3_association_cortex": "CausalField InformationVoxels + ConnectivityBeams (tension -> top-down hypothesis -> bottom-up calibration)",
            },
            "initial_field": init_field,
            "cycles_executed": len(self.lived_episodes),
            "episodes": [
                {
                    "cycle": ep["cycle"],
                    "hypothesis": ep["hypothesis"]["hypothesis_id"],
                    "field_tension": ep["hypothesis"]["field_tension"],
                    "op_ok": ep["layer1_outcome"]["op_ok"],
                    "transform_summary": ep["layer1_outcome"].get("transform_summary", ""),
                    "entropy_delta": ep["layer1_outcome"].get("entropy_delta", 0.0),
                    "friction": ep["layer1_outcome"].get("friction", ""),
                    "field_dissipated_energy": ep["layer3_field_calibration"]["dissipated_energy"],
                    "voxel_conductance": ep["layer3_field_calibration"]["updated_voxel_conductance"],
                }
                for ep in self.lived_episodes
            ],
            "layer2_myelination": myelination,
            "final_field_state": {
                "voxels": len(self.field.voxels),
                "beams": len(self.field.beams),
                "gimbal_lock_unlocked_count": self.field.gimbal_lock_unlocked_count,
                "total_dissipated_energy": round(float(self.field.total_dissipated_energy), 4),
                "active_focus": [round(x, 4) for x in self.field.active_focus.tolist()],
            },
        }
        _save_json(NERVOUS_STATE_PATH, summary)
        return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="ELYSIA 3-Layer Bidirectional Nervous Loop")
    parser.add_argument("--cycles", type=int, default=5, help="Number of autonomous top-down/bottom-up cycles")
    args = parser.parse_args()

    system = UnifiedThreeLayerNervousSystem()
    result = system.run_cycles(num_cycles=args.cycles)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
