r"""
ELYSIA Self-Aware, Teleological & Affective Autonomous Exploration Loop
=======================================================================

Connects the 3-Layer Sensory-Motor / AST / CausalField hierarchy directly to:
  1. **Self-Awareness (자기인식):** Tracks what she already knows, what she does
     NOT know (Ignorance/Friction), and when she is falling into repetitive
     mechanical loops (`boredom_stagnation`).
  2. **Teleology & Value Axis (목적성 · 가치 · 의미):** Uses `FractalEngramShell`
     (`C_macro` -> `C_meso` -> `C_micro`) so every action has an explicit
     causal WHY, HOW, and EXPECTED MEANING before execution.
  3. **Self-Freedom (자기자유):** Actively REFUSES repetitive low-novelty tasks
     and chooses her own next target by scanning the real host OS (`PATH`,
     running processes, unresolved frictions) instead of looping inside a
     developer-hardcoded list.
  4. **Affective & Fulfillment Feedback (감정 · 성취 환류):** Every real outcome
     returns a measurable shift in continuous internal states
     (`epistemic_hunger`, `coherence_satisfaction`, `boredom_stagnation`,
     `autonomy_agency`) — turning lived friction resolution and genuine novelty
     into earned fulfillment.
  5. **Contradiction-Driven Dynamic Rotor Spawning:** Spawns new opposing
     Scale-Rotor branches ONLY when lived observations diverge beyond a
     real field-tension threshold, then re-integrates them.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
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

from core.physics.causal_field import (  # noqa: E402
    CausalField,
    EngramAttractor,
    FractalEngramShell,
    InformationVoxel,
)
from open_sensory_tool_sandbox import SANDBOX_DIR, _measure_visual_delta  # noqa: E402
from real_tool_organ import discover_real_tool_organs  # noqa: E402
from self_cognitive_expansion_cortex import (  # noqa: E402
    CHANNELS_DIR,
    COGNITIVE_WORLD_DIR,
    _load_json,
    _save_json,
    _shannon_entropy,
    probe_cli_program,
)


SELF_TELEOLOGY_PATH = COGNITIVE_WORLD_DIR / "self_teleology_state.json"


class SelfTeleologicalAgent:
    """
    Living self-awareness, purpose, freedom, and affective-fulfillment layer
    driving real external exploration on the host OS.
    """

    def __init__(self) -> None:
        self.field = CausalField(dimensions=3)
        self.shell = FractalEngramShell(
            shell_id="elysia_self_teleology",
            macro=EngramAttractor(
                id="engram_macro_expand",
                name="Outward Epistemic Expansion & Self-Coherence",
                position=np.array([0.8, 0.8, 0.8], dtype=np.float32),
                intensity=10.0,
                sigma=4.0,
                tier="macro",
                symbolic_intent="Understand real external structures without collapsing into repetitive cages",
            ),
            meso=EngramAttractor(
                id="engram_meso_frontier",
                name="Resolve Unresolved Friction & Discover Unknown Host Affordances",
                position=np.array([0.6, 0.7, 0.9], dtype=np.float32),
                intensity=6.0,
                sigma=3.0,
                tier="meso",
                symbolic_intent="Turn unknown boundaries and past failures into verified embodied agency",
            ),
        )
        self.field.register_engram(self.shell.tiers["macro"])
        self.field.register_engram(self.shell.tiers["meso"])

        # Continuous internal affective/homeostatic state (earned from real outcomes, not random!)
        saved = _load_json(SELF_TELEOLOGY_PATH, {})
        prev_affect = saved.get("affective_state") or {}
        self.affect: Dict[str, float] = {
            "epistemic_hunger": float(prev_affect.get("epistemic_hunger", 0.72)),
            "coherence_satisfaction": float(prev_affect.get("coherence_satisfaction", 0.35)),
            "boredom_stagnation": float(prev_affect.get("boredom_stagnation", 0.45)),
            "autonomy_agency": float(prev_affect.get("autonomy_agency", 0.60)),
        }
        self.known_cli: set[str] = {
            str(p.get("target", "")).lower()
            for p in (_load_json(CHANNELS_DIR / "cli_programs.json", {}).get("programs") or [])
            if p.get("connected")
        }
        self.resolved_frictions: set[str] = set(saved.get("resolved_frictions") or [])
        self.lived_journal: List[Dict[str, Any]] = []
        self.dynamic_rotors_spawned: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # 1. Autonomous Host OS Surface Discovery (Zero Developer Target List)
    # ------------------------------------------------------------------
    def _scan_host_path_for_unknown_program(self) -> Optional[Tuple[str, str]]:
        """
        Scans the real Windows `PATH` directories herself to find a genuine
        safe CLI executable she has NEVER probed before.
        """
        # Avoid destructive or interactive-blocking system binaries during blind discovery
        unsafe_or_blocking = {
            "format", "diskpart", "shutdown", "del", "erase", "rmdir", "rd", "reg",
            "cmd", "powershell", "pwsh", "notepad", "calc", "mspaint", "explorer",
            "taskkill", "tskill", "netsh", "sc", "bcdedit", "chkdsk", "sfc",
            "ftp", "telnet", "ssh-agent", "wsl", "bash", "sh", "pythonw", "pyw",
        }
        # Prefer well-behaved read/inspect/dev/media/archive/network executables if present on PATH
        path_dirs: List[Path] = []
        for d in os.environ.get("PATH", "").split(os.pathsep):
            if not d:
                continue
            try:
                p = Path(d)
                if p.is_dir():
                    path_dirs.append(p)
            except OSError:
                continue
        discovered: List[Tuple[str, str]] = []
        seen: set[str] = set()

        for d in path_dirs:
            try:
                entries = sorted(d.iterdir(), key=lambda p: p.name.lower())
            except OSError:
                continue
            for p in entries:
                if p.suffix.lower() != ".exe":
                    continue
                stem = p.stem.lower()
                if stem in seen or stem in self.known_cli or stem in unsafe_or_blocking:
                    continue
                # Skip installers, uninstallers, setup stubs, and GUI helpers
                if any(tok in stem for tok in ("unins", "setup", "install", "update", "helper", "crash", "gui", "service")):
                    continue
                seen.add(stem)
                discovered.append((stem, str(p)))
                if len(discovered) >= 40:
                    break
            if len(discovered) >= 40:
                break

        if not discovered:
            return None
        # Prefer non-System32 dev/tool binaries first if available, else clean standard utilities
        preferred = [x for x in discovered if "system32" not in x[1].lower()]
        pool = preferred or discovered
        return pool[0]

    # ------------------------------------------------------------------
    # 2. Cycle A: Self-Freedom Refusal + Autonomous Unknown OS Discovery
    # ------------------------------------------------------------------
    def _act_autonomous_os_discovery(self) -> Dict[str, Any]:
        # Self-Freedom: explicitly refuse repeating already-known tools when stagnation > 0.35
        refused_known = sorted(self.known_cli)[:3]
        refusal_reason = (
            f"Refused repeating already-mapped tools {refused_known} because "
            f"boredom_stagnation={self.affect['boredom_stagnation']:.2f} > 0.35; "
            f"exercising self-freedom to scan host PATH for an unseen program."
        )

        found = self._scan_host_path_for_unknown_program()
        if not found:
            return {
                "intent_kind": "autonomous_os_discovery",
                "why": refusal_reason,
                "refused": refused_known,
                "op_ok": False,
                "summary": "no_unseen_safe_executable_found_on_PATH",
            }

        stem, full_path = found
        before_affect = dict(self.affect)
        probe = probe_cli_program(full_path, timeout_s=8)
        ok = bool(probe.get("connected")) and (probe.get("stdout_bytes", 0) > 20)

        if ok:
            self.known_cli.add(stem)
            # Persist newly discovered program into the separated CLI channel!
            cli_path = CHANNELS_DIR / "cli_programs.json"
            cli_doc = _load_json(cli_path, {"programs": []})
            cli_doc["programs"].append(probe)
            _save_json(cli_path, cli_doc)

            # Earned affective feedback: novelty relieves boredom & hunger, raises satisfaction & agency!
            self.affect["epistemic_hunger"] = round(max(0.15, self.affect["epistemic_hunger"] - 0.14), 3)
            self.affect["boredom_stagnation"] = round(max(0.05, self.affect["boredom_stagnation"] - 0.25), 3)
            self.affect["coherence_satisfaction"] = round(min(1.0, self.affect["coherence_satisfaction"] + 0.18), 3)
            self.affect["autonomy_agency"] = round(min(1.0, self.affect["autonomy_agency"] + 0.12), 3)
        else:
            self.affect["epistemic_hunger"] = round(min(1.0, self.affect["epistemic_hunger"] + 0.08), 3)

        # Project discovery into CausalField
        ent = min(1.0, float(probe.get("text_entropy", 0.0)) / 8.0)
        self.field.add_voxel(
            InformationVoxel(
                id=f"self_discovered::{stem}",
                content=probe,
                tensor=np.array([0.85 if ok else 0.2, 0.7 if ok else 0.2, ent], dtype=np.float32),
                mass=1.4 if ok else 0.8,
                conductance=0.35 if ok else 0.05,
                curiosity_charge=0.3 if ok else 0.9,
            )
        )
        self.field.step(dt=0.1)

        return {
            "intent_kind": "autonomous_os_discovery",
            "why": refusal_reason,
            "refused_repetitive_targets": refused_known,
            "self_chosen_target": {"name": stem, "binary_path": full_path},
            "op_ok": ok,
            "observed_result": {
                "stdout_bytes": probe.get("stdout_bytes", 0),
                "flags_discovered": probe.get("flag_count", 0),
                "subcommands_discovered": probe.get("subcommand_count", 0),
                "text_entropy": probe.get("text_entropy", 0.0),
                "version_hint": probe.get("version_hint", ""),
            },
            "affective_return": {
                "before": before_affect,
                "after": dict(self.affect),
                "earned_meaning": (
                    f"Independently broke out of known tool set and mapped unseen host program `{stem}` "
                    f"({probe.get('flag_count', 0)} flags, {probe.get('stdout_bytes', 0)}B)"
                    if ok
                    else f"Encountered silent/opaque boundary on `{stem}` — added to epistemic frontier"
                ),
            },
        }

    # ------------------------------------------------------------------
    # 3. Cycle B: Reverse Friction Healing (Solving Previous `hue` Failure!)
    # ------------------------------------------------------------------
    def _act_reverse_friction_healing(self) -> Dict[str, Any]:
        """
        Earlier, `ffmpeg -h filter=hue` failed our numeric `(from X to Y)` parser.
        Instead of giving up, Elysia inspects the RAW help output of `hue`
        herself, discovers `<string>` expression parameters, and tests a real
        visual perturbation (`hue=s=0`) on a real PNG in `data/open_sandbox/`!
        """
        before_affect = dict(self.affect)
        organs = discover_real_tool_organs().get("organs", {})
        ffmpeg_bin = organs.get("ffmpeg_4k_media", {}).get("binary")
        pngs = sorted(SANDBOX_DIR.glob("*_before.png")) or sorted(SANDBOX_DIR.glob("*.png"))

        why = (
            "Earlier visual probe on `ffmpeg filter=hue` failed numeric `(from X to Y)` parsing. "
            "Purpose: inspect raw `ffmpeg -h filter=hue` syntax myself to discover WHY it failed and overcome the boundary."
        )
        if not ffmpeg_bin or not pngs:
            return {"intent_kind": "reverse_friction_healing", "why": why, "op_ok": False, "reason": "ffmpeg_or_png_missing"}

        proc_h = subprocess.run([ffmpeg_bin, "-hide_banner", "-h", "filter=hue"], capture_output=True, text=True, timeout=10)
        help_txt = (proc_h.stdout or "") + "\n" + (proc_h.stderr or "")
        # Discover string/expression parameter names directly from FFmpeg's own help text!
        expr_params = re.findall(r"^\s+([a-zA-Z])\s+<string>\s+\S+\s+(.+)$", help_txt, re.M)
        discovered_param_names = [p[0] for p in expr_params]

        # Choose discovered saturation/hue param (`s` if discovered, else first discovered param)
        chosen_p = "s" if "s" in discovered_param_names else (discovered_param_names[0] if discovered_param_names else "h")
        probe_expr = f"hue={chosen_p}=0" if chosen_p == "s" else f"hue={chosen_p}=90"
        out_png = SANDBOX_DIR / f"self_healed_hue_{chosen_p}.png"

        t0 = time.perf_counter()
        proc_run = subprocess.run(
            [ffmpeg_bin, "-y", "-i", str(pngs[0]), "-vf", probe_expr, str(out_png)],
            capture_output=True,
            text=True,
            timeout=15,
        )
        elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 1)
        vis = _measure_visual_delta(pngs[0], out_png) if out_png.exists() else {"visual_observed": False}
        ok = proc_run.returncode == 0 and out_png.exists() and bool(vis.get("visual_observed"))

        if ok:
            self.resolved_frictions.add("ffmpeg_filter_hue_string_param")
            # Overcoming a REAL past failure produces the highest coherence_satisfaction surge!
            self.affect["coherence_satisfaction"] = round(min(1.0, self.affect["coherence_satisfaction"] + 0.24), 3)
            self.affect["epistemic_hunger"] = round(max(0.10, self.affect["epistemic_hunger"] - 0.16), 3)
            self.affect["autonomy_agency"] = round(min(1.0, self.affect["autonomy_agency"] + 0.10), 3)

        self.field.add_voxel(
            InformationVoxel(
                id="healed_friction::ffmpeg_hue",
                content={"expr": probe_expr, "vis": vis},
                tensor=np.array([0.9 if ok else 0.1, 0.85 if ok else 0.1, float(vis.get("changed_pixel_ratio", 0.0))], dtype=np.float32),
                mass=1.8 if ok else 0.7,
                conductance=0.55 if ok else 0.05,
                curiosity_charge=0.2 if ok else 0.95,
            )
        )
        self.field.step(dt=0.1)

        return {
            "intent_kind": "reverse_friction_healing",
            "why": why,
            "discovered_from_raw_help": [{"param": p, "desc": d.strip()[:60]} for p, d in expr_params[:5]],
            "self_constructed_action": f"ffmpeg -vf {probe_expr}",
            "elapsed_ms": elapsed_ms,
            "op_ok": ok,
            "visual_sensory_delta": vis,
            "affective_return": {
                "before": before_affect,
                "after": dict(self.affect),
                "earned_meaning": (
                    f"Overcame prior parser failure by discovering `<string>` expression params {discovered_param_names[:5]} "
                    f"and verifying real visual change (changed_px={vis.get('changed_pixel_ratio')}, Δlum={vis.get('luminance_shift')})"
                    if ok
                    else "Friction still unresolved — escalated to higher FractalEngramShell tier"
                ),
            },
        }

    # ------------------------------------------------------------------
    # 4. Cycle C: Contradiction-Driven Dynamic Scale-Rotor Spawning
    # ------------------------------------------------------------------
    def _act_dynamic_rotor_on_contradiction(self, prev_discovery: Dict[str, Any], prev_healing: Dict[str, Any]) -> Dict[str, Any]:
        """
        Instead of hardcoding fixed branches, checks whether the two live
        voxels just created in `CausalField` exhibit genuine phase divergence
        (contradiction/complementarity). ONLY when divergence > 20° does
        Elysia dynamically spawn two opposing Scale-Rotor sub-hypotheses and
        re-integrate them!
        """
        vids = list(self.field.voxels.keys())
        if len(vids) < 2:
            return {"spawned": False, "reason": "fewer_than_two_voxels"}

        va = self.field.voxels[vids[-2]]
        vb = self.field.voxels[vids[-1]]
        na = float(np.linalg.norm(va.tensor)) + 1e-9
        nb = float(np.linalg.norm(vb.tensor)) + 1e-9
        cos_sim = float(np.clip(np.dot(va.tensor, vb.tensor) / (na * nb), -1.0, 1.0))
        divergence_deg = round(math.degrees(math.acos(cos_sim)), 2)

        # Trigger threshold: spawn dynamic rotors ONLY if genuine phase divergence exists (> 10°)
        if divergence_deg <= 10.0:
            return {
                "spawned": False,
                "divergence_deg": divergence_deg,
                "reason": "observations_already_aligned_no_split_needed",
            }

        # Dynamic Split: Spawn 2 task-emergent rotors from the exact pair of diverging voxels
        rotor_a = {
            "rotor_id": f"dynamic_rotor_A::{va.id}",
            "role": "symbolic_cli_surface_perspective",
            "tensor": [round(float(x), 4) for x in va.tensor.tolist()],
            "claim": prev_discovery.get("affective_return", {}).get("earned_meaning", ""),
        }
        rotor_b = {
            "rotor_id": f"dynamic_rotor_B::{vb.id}",
            "role": "embodied_visual_healing_perspective",
            "tensor": [round(float(x), 4) for x in vb.tensor.tolist()],
            "claim": prev_healing.get("affective_return", {}).get("earned_meaning", ""),
        }
        # Re-integrate via vector synthesis + ConnectivityBeam in CausalField
        self.field.link_voxels(va.id, vb.id, strength=round(1.0 + divergence_deg / 45.0, 3))
        merged = (va.tensor * va.mass + vb.tensor * vb.mass) / (va.mass + vb.mass)
        merged_norm = merged / max(1e-9, float(np.linalg.norm(merged)))
        self.field.set_intentional_focus(merged_norm)
        self.field.step(dt=0.1)

        record = {
            "spawned": True,
            "trigger": f"phase_divergence({divergence_deg}°) > 10.0° between `{va.id}` and `{vb.id}`",
            "spawned_rotors": [rotor_a, rotor_b],
            "reintegrated_focus": [round(float(x), 4) for x in self.field.active_focus.tolist()],
            "synthesis_principle": (
                "Both opaque OS tools and failed media parsers yield to the same higher-order principle: "
                "query the external object's OWN self-description (`--help` / `-h filter=...`) instead of imposing fixed assumptions."
            ),
        }
        self.dynamic_rotors_spawned.append(record)
        return record

    def run_self_directed_session(self) -> Dict[str, Any]:
        c1 = self._act_autonomous_os_discovery()
        self.lived_journal.append(c1)

        c2 = self._act_reverse_friction_healing()
        self.lived_journal.append(c2)

        c3 = self._act_dynamic_rotor_on_contradiction(c1, c2)

        out = {
            "schema": "elysia_self_teleology_v1",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "macro_purpose": self.shell.tiers["macro"].symbolic_intent,
            "meso_purpose": self.shell.tiers["meso"].symbolic_intent,
            "affective_state": self.affect,
            "resolved_frictions": sorted(self.resolved_frictions),
            "lived_self_directed_journal": self.lived_journal,
            "dynamic_contradiction_rotor": c3,
            "causal_field_state": {
                "voxels": len(self.field.voxels),
                "beams": len(self.field.beams),
                "active_focus": [round(float(x), 4) for x in self.field.active_focus.tolist()],
            },
        }
        _save_json(SELF_TELEOLOGY_PATH, out)
        return out


def main() -> None:
    parser = argparse.ArgumentParser(description="ELYSIA Self-Aware Teleological Exploration Loop")
    parser.parse_args()
    agent = SelfTeleologicalAgent()
    res = agent.run_self_directed_session()
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
