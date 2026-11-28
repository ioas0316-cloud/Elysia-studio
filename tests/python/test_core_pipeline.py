#!/usr/bin/env python3
"""
Python Verification Suite for Elysia P0-P2 Components:
- CanonicalElysiaRuntime (4-stage observe -> evolve -> consolidate -> act + stagnation loop break)
- TopIRCompilerPython (dynamic EOL parsing & parameterized HLSL/C++ emission)
- Cross-platform MVA shared_field + real S^3 resonance search & OLS symbolic regression
- CausalDSLParser (.cdsl signal/node/rule parsing)
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "L1_causal_field"))
sys.path.insert(0, str(ROOT / "L0_substrate"))
sys.path.insert(0, str(ROOT / "L0_substrate" / "mva" / "api"))

from core.orchestration.canonical_runtime import CanonicalElysiaRuntime
from core.engine.causal_dsl.parser import CausalDSLParser
from isa_compiler.topir_compiler import TopIRCompilerPython
import shared_field


def test_canonical_runtime():
    rt = CanonicalElysiaRuntime(dimensions=3, resonance_threshold=0.4)
    rt.add_voxel("v1", "A", [0.0, 0.0, 0.0], [1.0, 0.0, 0.0], scale=0)
    rt.add_voxel("v2", "B", [1.0, 0.0, 0.0], [0.9, 0.1, 0.0], scale=2)
    rt.link("v1", "v2", strength=2.0)

    # Feed aligned stimulus -> friction decreases, S0..S4 rotors stay unit-norm & propagate upward
    reports = [rt.step_cycle([1.0, 0.05, 0.0], dt=0.1) for _ in range(10)]
    assert reports[-1].friction < reports[0].friction + 1e-6
    assert reports[-1].engrams_count >= 1
    assert len(rt.scale_rotors) == 5
    for scale_idx, q in reports[-1].rotor_quaternions.items():
        q_norm = math.sqrt(sum(c * c for c in q))
        assert abs(q_norm - 1.0) < 1e-12, f"Scale {scale_idx} quaternion drifted from S^3: {q_norm}"
    assert abs(rt.scale_rotors[4].angular_velocity[0]) > 0.0, "Expected upward gear-coupled torque from S0 to S4"
    assert len(rt.engrams[0].scale_signature) == 5

    # Feed orthogonal/opposing high-friction stimulus repeatedly -> stagnation escalates loop break
    escalated_any = any(rt.step_cycle([-5.0, 0.0, 0.0], dt=0.1).escalated_loop_break for _ in range(6))
    assert escalated_any, "Expected fractal loop break escalation under sustained friction"
    print(
        f"[PASS] CanonicalElysiaRuntime + S0..S4 Scale Rotors "
        f"(cycles={rt.cycle_count}, engrams={len(rt.engrams)}, scale_coherence={reports[-1].scale_coherence:.4f})"
    )


def test_topir_compiler_dynamic():
    compiler = TopIRCompilerPython()
    eol_a = (
        "vort = Diff::curl(V)\n"
        "sync = PhaseLock(K_0=33.5)(Q)\n"
        "comp = ScaleCompress(gamma=0.75)(sync)\n"
        "stress = BlendByOrder(comp, solid_th=0.82, gas_th=0.18)\n"
    )
    out_a = compiler.compile_eol(eol_a)
    assert out_a["status"] == "compiled_successfully"
    assert len(out_a["ir_graph"]["nodes"]) == 4
    assert len(out_a["ir_graph"]["edges"]) == 2
    assert "33.5000f" in out_a["hlsl"]
    assert "0.7500f" in out_a["hlsl"]
    assert "0.8200f" in out_a["cpp"]
    print(f"[PASS] TopIRCompilerPython dynamic parsing & codegen (nodes={len(out_a['ir_graph']['nodes'])})")


def test_cross_platform_shared_field():
    shared_field.write_rotor_tension(4.2, observation_axis="spatial", rotor_idx=7)
    pts = shared_field.read_active_rotors()
    assert len(pts) >= 1
    assert any(abs(p["position"][2] - 4.2) < 0.2 for p in pts)
    print(f"[PASS] MVA Cross-Platform SharedFieldStore (active_rotors={len(pts)})")


def test_mva_real_resonance_and_regression():
    # Import pure-math helper functions directly from engine.py without requiring numpy/scipy
    import ast
    src = (ROOT / "L0_substrate" / "mva" / "api" / "engine.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    ns = {"math": math, "List": list, "Dict": dict, "Any": object, "Tuple": tuple}
    wanted = {"_rotate_point_by_quat", "_extract_positions", "find_resonance_angle", "generate_symbolic_regression"}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in wanted:
            exec(compile(ast.Module(body=[node], type_ignores=[]), "<mva>", "exec"), ns)

    # Generate tilted planar 3D point cloud: z = 0.8*x - 0.5*y + 0.3
    pts = []
    for ix in range(-2, 3):
        for iy in range(-2, 3):
            x, y = float(ix), float(iy)
            z = 0.8 * x - 0.5 * y + 0.3
            pts.append({"position": [x, y, z], "token": "p"})

    best_q, min_var = ns["find_resonance_angle"](pts, 0.5)
    formula, r2 = ns["generate_symbolic_regression"](pts, [0.0, 0.0, 0.0, 1.0], 0.5)
    assert min_var < 0.05, f"Expected near-zero planar variance after quaternion alignment, got {min_var}"
    assert r2 > 0.99, f"Expected exact planar fit R^2 > 0.99, got {r2}"
    print(f"[PASS] MVA Resonance & OLS Regression (min_var={min_var:.5f}, R^2={r2:.4f}, {formula})")


def test_causal_dsl_parser():
    sample_cdsl = """
    signal GravityPulse : priority(1) {
        float magnitude;
        vec3 direction;
    }
    node CoreCell {
        dormant { mass: 1.0; state: idle; }
        manifested { float energy; }
    }
    rule CollapseGravity {
        trigger: GravityPulse g;
        target: CoreCell c;
        when: g.magnitude > 0.5;
        collapse { c.energy += g.magnitude; }
    }
    """
    prog = CausalDSLParser(sample_cdsl).parse()
    assert len(prog.signals) == 1 and prog.signals[0].name == "GravityPulse"
    assert len(prog.nodes) == 1 and prog.nodes[0].name == "CoreCell"
    assert len(prog.rules) == 1 and prog.rules[0].name == "CollapseGravity"
    print("[PASS] CausalDSLParser (.cdsl signal/node/rule AST)")


def test_unified_dimensional_engine():
    from core.topology.unified_dimensional_causal_engine import UnifiedDimensionalCausalEngine

    eng = UnifiedDimensionalCausalEngine(rows=8, cols=8, time_layers=5)
    res = eng.transform(
        "엔탈피 구배와 촉매 결합이 활성화 장벽을 낮추어 비평형 상전이와 결정 성장을 동시에 유도한다",
        domain="chemistry",
        theta2=(0.35, 0.40, 0.55),
        passes=8,
    )
    assert res.mean_tension_after < res.mean_tension_before, (
        f"Expected parallel A4 surface crystallization to reduce tension: {res.mean_tension_before} -> {res.mean_tension_after}"
    )
    assert len(res.theta1_laws) == 4
    assert len(res.cube_slices["time"]) == 5
    assert res.sphere_compression_ratio == 80.0
    assert len(res.cross_domain_isomorphisms) == 5
    assert len(res.parallel_planets) == 5
    print(
        f"[PASS] UnifiedDimensionalCausalEngine "
        f"(tension {res.mean_tension_before:.4f}->{res.mean_tension_after:.4f}, "
        f"compression={res.sphere_compression_ratio:.0f}:1, planets={len(res.parallel_planets)}, domains=5)"
    )


def test_unified_scale_rotor_core():
    import tempfile
    from core.orchestration.scale_rotor_core import UnifiedScaleRotorEngine

    with tempfile.TemporaryDirectory() as tmpdir:
        ledger = Path(tmpdir) / "test_ice_ledger.json"
        eng = UnifiedScaleRotorEngine(ledger_path=ledger, auto_persist=True)
        st = eng.step_t1_to_t4(
            {
                "vision": {"label": "사과 표면 곡률", "contrast": 0.72, "motion": 0.25, "structure": 0.85, "coherence": 0.80},
                "audio": {"label": "공명 진동", "frequency_norm": 0.60, "amplitude": 0.70, "harmonicity": 0.82, "noise_ratio": 0.12},
                "language": {"text": "사과의 세포벽과 껍질 경계가 내부 수분을 보존한다 (dP/dr = 0)"},
                "behavior": {"fatigue": 0.20, "threat": 0.22, "proximity": 0.45, "cohesion": 0.82, "terrain_friction": 0.25},
                "noise_ratio": 0.15,
            }
        )
        assert st["status"] == "ok"
        assert set(st["frames"].keys()) == {"point", "line", "plane", "cube", "sphere"}
        assert ledger.exists(), "Expected atomic persistent Ice Ledger JSON to be written"

        # Reload into fresh instance and verify Ice Ledger persistence sync
        reloaded = UnifiedScaleRotorEngine(ledger_path=ledger, auto_persist=False)
        assert reloaded.cycle == eng.cycle
        assert len(reloaded.ice_seeds) == len(eng.ice_seeds)

        # Verify Section 7.4 quantitative benchmark passes
        bench = eng.run_section_74_benchmark()
        assert bench["verdict"] == "PASS", f"Expected Section 7.4 benchmark PASS, got: {bench}"
        s = bench["summary"]
        print(
            f"[PASS] UnifiedScaleRotorEngine (t1~t4, Section 7.4={bench['verdict']}, "
            f"compression={s['mean_compression_ratio']}x, noise_rej={s['mean_noise_rejection']}, "
            f"shock_recovery={s['shock_recovery_frames']}f, ice_stab={s['mean_ice_stability']})"
        )


def test_empirical_process_contrast_observer():
    from core.orchestration.process_contrast_observer import (
        observe_external_snapshot,
        run_empirical_contrast_suite,
    )
    from core.orchestration.scale_rotor_core import UnifiedScaleRotorEngine

    eng = UnifiedScaleRotorEngine(ledger_path=None, auto_persist=False)
    strict_res = run_empirical_contrast_suite(engine=eng, lens_mode="strict", geom_op="rigid_rotate")
    tol_res = run_empirical_contrast_suite(engine=None, lens_mode="tolerant", geom_op="shear_deform")

    assert strict_res["status"] == "ok"
    assert strict_res["summary"]["all_reproduction_verified"] is True
    assert strict_res["summary"]["external_uncaptured_count"] == 3

    # Verify Observer Lens genuinely changes frame delta classification (strict catches 0.02 ripple; tolerant ignores <= 0.05)
    strict_frame = next(o for o in strict_res["observed_processes"] if o["process_id"] == "frame_delta")
    tol_frame = next(o for o in tol_res["observed_processes"] if o["process_id"] == "frame_delta")
    assert strict_frame["delta_patch_total"] > tol_frame["delta_patch_total"], (
        "Expected strict lens to flag 0.02 sensor ripple while tolerant lens (eps=0.05) treats it as invariant"
    )

    # Verify Rigid Rotation preserves all 6 edge lengths (0) while Shear Deformation mutates them (1)
    rigid_geom = next(o for o in strict_res["observed_processes"] if o["process_id"] == "geometry_constraint")
    shear_geom = next(o for o in tol_res["observed_processes"] if o["process_id"] == "geometry_constraint")
    rigid_edge_invs = [x for x in rigid_geom["invariants_0"] if x["entity"].startswith("edge_lengths.")]
    shear_edge_invs = [x for x in shear_geom["invariants_0"] if x["entity"].startswith("edge_lengths.")]
    assert len(rigid_edge_invs) == 6 and len(shear_edge_invs) < 6

    # Verify Open External Snapshot Contrast Protocol
    ext = observe_external_snapshot(
        system_name="External_CAD_Hook_Sample",
        before_state={"radius_mm": 40.0, "material": "Al6061", "tolerance_mm": 0.02},
        after_state={"radius_mm": 45.0, "material": "Al6061", "tolerance_mm": 0.02},
        operation="param radius 40->45",
        lens_mode="strict",
    )
    assert ext["reproduction"]["verified"] is True
    assert len(ext["invariants_0"]) == 2 and len(ext["mutations_1"]) == 1
    print(
        f"[PASS] Empirical Process Contrast Observer (4 live observed, 3 honest uncaptured, "
        f"strict_deltas={strict_frame['delta_patch_total']} vs tol_deltas={tol_frame['delta_patch_total']}, "
        f"rigid_edge_0={len(rigid_edge_invs)} vs shear_edge_0={len(shear_edge_invs)}, all_repro=True)"
    )


def test_vessel_and_snapshot_trajectory_rotor():
    import tempfile
    from core.orchestration.scale_rotor_core import UnifiedScaleRotorEngine
    from core.orchestration.vessel_trajectory_rotor import VesselTrajectoryRotor

    with tempfile.TemporaryDirectory() as tmpdir:
        ledger = Path(tmpdir) / "vessel_ledger.json"
        eng = UnifiedScaleRotorEngine(ledger_path=ledger, auto_persist=True)
        rotor = VesselTrajectoryRotor(max_snapshots=16)

        def _node_snap_from_eng(req_count: int) -> dict:
            return {
                "cycle": eng.cycle,
                "active_frame": eng.active_frame,
                "scale_dial": round(eng.canonical.scale_dial, 4),
                "ice_seed_count": len(eng.ice_seeds),
                "water_spectrum": [round(x, 4) for x in eng.water_flow],
                "node_engine_cycle": req_count,
                "http_requests_served": req_count,
                "l1_pending_rpcs": 0,
                "memory_heap_used_mb": 42.0,
                "memory_rss_mb": 88.0,
            }

        # Capture 3 synchronized ticks: t0 -> t1 -> t2
        eng.save_ledger()
        rotor.capture(eng, node_vessel=_node_snap_from_eng(1), label="sync_t0")
        for idx in (2, 3):
            eng.step_t1_to_t4(
                {
                    "vision": {"label": f"v{idx}", "structure": 0.78, "contrast": 0.64, "motion": 0.42, "coherence": 0.85},
                    "language": {"label": f"l{idx}", "text": "그릇 동기화 궤적"},
                }
            )
            rotor.capture(eng, node_vessel=_node_snap_from_eng(idx), label=f"sync_t{idx-1}")

        sync_report = rotor.analyze(lens_mode="strict")
        assert sync_report["summary"]["all_reproduction_verified"] is True
        assert sync_report["scale_3_cross_vessel_plane"]["all_vessels_coherent"] is True
        assert sync_report["scale_2_trajectory_rotor"]["ready"] is True
        # Scale-1 changing cycle (+1 every tick) MUST sublimate into Scale-2 invariant law (0)
        elevated_keys = {x["entity"] for x in sync_report["scale_2_trajectory_rotor"]["latest"]["elevated_laws_0"]}
        assert "l1_python_memory.cycle" in elevated_keys and "disk_ice_ledger.cycle" in elevated_keys, (
            f"Expected constant cycle stride (+1) to sublimate into Scale-2 law, got: {elevated_keys}"
        )

        # Now run a genuine UNFLUSHED memory transition (auto_persist=False) without syncing Node or Disk!
        stale_node = _node_snap_from_eng(3)
        eng.auto_persist = False
        eng.step_t1_to_t4({"language": {"label": "ram_only", "text": "메모리 전용 선행 전이"}})
        eng.auto_persist = True
        rotor.capture(eng, node_vessel=stale_node, label="unflushed_ram_drift")

        drift_report = rotor.analyze(lens_mode="strict")
        assert drift_report["summary"]["all_reproduction_verified"] is True
        assert drift_report["scale_3_cross_vessel_plane"]["all_vessels_coherent"] is False
        py_vs_disk = next(p for p in drift_report["scale_3_cross_vessel_plane"]["pairs"] if p["pair_id"] == "l1_python_vs_disk")
        assert py_vs_disk["status"] == "DIVERGED"
        assert any(d["entity"] == "cycle" for d in py_vs_disk["divergent_1"])
        # Scale-2 must detect that disk_ice_ledger.cycle broke its +1 law!
        shift_keys = {m["entity"] for m in drift_report["scale_2_trajectory_rotor"]["latest"]["regime_shifts_1"]}
        assert "disk_ice_ledger.cycle" in shift_keys

        # Now FLUSH memory to disk & reconcile Node -> divergence must collapse back to 0 (COHERENT)!
        eng.save_ledger()
        rotor.capture(eng, node_vessel=_node_snap_from_eng(4), label="flushed_reconciled")
        reconciled = rotor.analyze(lens_mode="strict")
        assert reconciled["scale_3_cross_vessel_plane"]["all_vessels_coherent"] is True
        print(
            f"[PASS] Vessel & Snapshot Trajectory Rotor "
            f"(elevated_laws={len(elevated_keys)}, drift_detected=True, reconciled_coherent=True, all_repro=True)"
        )


def test_bidirectional_phase_sync():
    import tempfile
    from core.orchestration.bidirectional_phase_sync import run_bidirectional_phase_sync_suite
    from core.orchestration.scale_rotor_core import UnifiedScaleRotorEngine

    with tempfile.TemporaryDirectory() as tmpdir:
        ledger = Path(tmpdir) / "sync_ledger.json"
        eng = UnifiedScaleRotorEngine(ledger_path=ledger, auto_persist=True)
        eng.save_ledger()
        node_v = {
            "cycle": eng.cycle,
            "active_frame": eng.active_frame,
            "scale_dial": round(eng.canonical.scale_dial, 4),
            "ice_seed_count": len(eng.ice_seeds),
            "water_spectrum": [round(x, 4) for x in eng.water_flow],
            "http_requests_served": 12,
        }
        res = run_bidirectional_phase_sync_suite(
            engine=eng,
            node_vessel=node_v,
            angle_b_deg=53.0,
            clock_rate_b=1.4,
            phase_lag_b=0.72,
            lens_a_mode="strict",
            lens_b_mode="tolerant",
        )
        ow = res["dual_observer_sync"]["one_way_observation"]
        bi = res["dual_observer_sync"]["bidirectional_sync"]
        assert ow["rmse_error"] > 1.0, f"Expected large one-way error, got {ow['rmse_error']}"
        assert ow["directional_asymmetry"] is True
        assert bi["reproduction"]["verified"] is True
        assert bi["synced_rmse_error"] < 1e-4, f"Expected synced RMSE < 1e-4, got {bi['synced_rmse_error']}"
        assert bi["clock_ratio_err"] < 1e-5
        assert bi["phase_lag_err"] < 1e-5
        assert bi["angle_offset_err_deg"] < 1e-3
        assert res["live_vessel_sync"]["phase_lags"]["synchronized"] is True
        print(
            f"[PASS] Bidirectional Common-Denominator Phase Sync "
            f"(one_way_rmse={ow['rmse_error']} -> synced_rmse={bi['synced_rmse_error']}, "
            f"clock_ratio={bi['recovered_clock_ratio']}, angle={bi['recovered_angle_offset_deg']}deg, roundtrip=PASS)"
        )


def test_digest_imitate_recreate_lab():
    from core.orchestration.digest_imitate_recreate import run_digest_imitate_recreate

    # 1. Absorbable physical original (damped harmonic + cubic boundary): must converge via iterative difference learning!
    ok_res = run_digest_imitate_recreate(
        engine=None,
        original_id="damped_harmonic",
        partner_id="wave_forcing",
        lens_mode="strict",
        max_rounds=3,
    )
    assert ok_res["stage_1_digest"]["workspace_knowledge"]["files_scanned"] >= 3
    s23 = ok_res["stage_2_3_imitate_and_learn_difference"]
    assert s23["absorbed_successfully"] is True
    assert s23["absorption_status"] == "DIGESTED_AND_VERIFIED"
    assert len(s23["rounds"]) == 3
    assert s23["rounds"][0]["rmse_original_vs_imitation"] > 0.2
    assert s23["final_probe_rmse"] < 1e-5
    assert ok_res["stage_4_recreate"]["cross_recombination"]["genuinely_novel"] is True

    # 2. Unrepresentable original (|x|*exp(-0.4x) + tanh): MUST NOT fake convergence -> honest UNCAPTURED_INGREDIENT!
    uncap_res = run_digest_imitate_recreate(
        engine=None,
        original_id="uncaptured_boundary_test",
        partner_id="diffusion_coupling",
        lens_mode="strict",
        max_rounds=3,
    )
    assert uncap_res["stage_2_3_imitate_and_learn_difference"]["absorbed_successfully"] is False
    assert uncap_res["stage_2_3_imitate_and_learn_difference"]["absorption_status"] == "UNCAPTURED_INGREDIENT"
    assert uncap_res["stage_2_3_imitate_and_learn_difference"]["final_probe_rmse"] > 0.05

    # 3. Custom formula supplied directly by user (no peeking!)
    custom_res = run_digest_imitate_recreate(
        engine=None,
        original_id="custom_formula",
        custom_formula="-1.5*x + 0.8*sin(x)",
        lens_mode="strict",
        max_rounds=3,
    )
    assert custom_res["stage_2_3_imitate_and_learn_difference"]["absorbed_successfully"] is True
    assert custom_res["stage_2_3_imitate_and_learn_difference"]["final_probe_rmse"] < 1e-5
    print(
        f"[PASS] Digest-Imitate-Recreate Lab "
        f"(damped_rmse={s23['rounds'][0]['rmse_original_vs_imitation']}->{s23['final_probe_rmse']}, "
        f"uncaptured_honest=True, custom_absorbed=True, ws_files={ok_res['stage_1_digest']['workspace_knowledge']['files_scanned']})"
    )


def test_unified_causal_dataflow_engine():
    from core.orchestration.unified_dataflow_engine import UnifiedCausalDataflowEngine

    df = UnifiedCausalDataflowEngine()
    res = df.execute_cycle(
        preset_id="wave_interference",
        gate_steepness=42.0,
        wake_threshold=0.22,
        audio_harmonics=6,
        t_phase=0.5,
        auto_optimize=False,
    )
    assert res["status"] == "ok"
    assert res["code_circuit"]["original_if_branches"] >= 1
    assert res["code_circuit"]["compiled_runtime_branches"] == 0
    assert res["code_circuit"]["discrete_equivalence_pct"] >= 95.0
    assert res["multiscale_gear"]["compute_saved_pct"] >= 25.0
    assert res["multiscale_gear"]["spatial_fidelity_pct"] >= 88.0
    assert res["signal_audio"]["compression_ratio"] >= 15.0
    assert len(res["signal_audio"]["harmonics"]) == 6
    assert res["cross_domain_coupling"]["unified_coherence"] >= 0.70
    assert len(res["spatial_field"]["height"]) == 1024

    # Security verification: unsafe Python constructs MUST be rejected strictly by AST whitelist
    for bad_code in [
        "import os\nfield = 1.0",
        "field = __import__('os').system('echo x')",
        "field = x.__class__",
        "field = open('/etc/passwd')",
    ]:
        rejected = False
        try:
            df.execute_cycle(code_source=bad_code)
        except ValueError:
            rejected = True
        assert rejected, f"Unsafe code was not rejected: {bad_code}"

    print(
        f"[PASS] Unified Causal Dataflow Engine "
        f"(saved={res['multiscale_gear']['compute_saved_pct']}%, "
        f"fidelity={res['multiscale_gear']['spatial_fidelity_pct']}%, "
        f"circuit_match={res['code_circuit']['discrete_equivalence_pct']}%, "
        f"audio_comp={res['signal_audio']['compression_ratio']}x, "
        f"coherence={res['cross_domain_coupling']['unified_coherence']}, ast_guard=PASS)"
    )


def test_living_companion_field():
    import tempfile
    from core.orchestration.living_companion_field import LivingCompanionField

    with tempfile.TemporaryDirectory() as tmpdir:
        mem_file = Path(tmpdir) / "elysia_autonomous_test.json"
        comp = LivingCompanionField(memory_path=mem_file, auto_persist=True)
        s0 = comp.get_state()
        assert s0["status"] == "ok"
        assert s0["autonomous_local"] is True
        assert s0["external_llm_used"] is False
        assert s0["optimization"]["zero_api_cost"] is True
        assert abs(sum(s0["scene_weights"].values()) - 1.0) < 0.01

        # 1. Unknown novel concept -> must honestly flag in unknown_tokens & ask about it!
        s1 = comp.converse(message="양자공명로터에 대해 알아?")
        assert "양자공명로터" in s1["causal_trace"]["unknown_tokens"]
        assert "양자공명로터" in s1["dialogue"]

        # 2. User teaches definition -> extracts concept, definition & causal edge locally!
        s2 = comp.converse(message="양자공명로터는 위상 간섭으로 에너지를 증폭하는 장치야.")
        assert s2["learned_concept_count"] >= 2
        assert s2["edge_count"] >= 1
        assert "양자공명로터" in comp.concepts
        assert len(comp.concepts["양자공명로터"]["definitions"]) >= 1

        # 3. Recall check: ask again -> recalls her OWN learned definition without ANY LLM API!
        s3 = comp.converse(message="양자공명로터가 뭐였지?")
        assert "위상 간섭" in s3["dialogue"]

        # 4. Authentic emotional causality: sudden harsh dismissal -> hurt_pout emerges continuously!
        s4 = comp.converse(message="너는 그냥 가짜 껍데기 아바타라 아무것도 못해 실망이야.")
        assert s4["scene_mood"] == "hurt_pout"
        assert s4["emotion_field"]["hurt_sulky"] > s3["emotion_field"]["hurt_sulky"]

        # 5. Autonomous workspace knowledge digestion (zero API!)
        s5 = comp.digest_knowledge(read_workspace=True)
        assert s5["status"] == "ok"
        assert s5["digest_report"]["new_concepts_count"] >= 10
        assert s5["edge_count"] > s4["edge_count"]

        # 6. Difference-learning correction feedback + full disk reload verification
        s6 = comp.apply_feedback(signal="correct", correction="지성은 단순 암기가 아니라 차이에서 스스로 자라는 과정이야")
        assert s6["status"] == "ok"

        # 7. Multi-modal local game corpus extraction (zero-upload header-slice & cross-modal binding!)
        game_dir = Path(tmpdir) / "AzurPromilia_Sample"
        (game_dir / "Content" / "Characters").mkdir(parents=True)
        (game_dir / "Content" / "Paks").mkdir(parents=True)
        # Unreal UAsset magic + DDS texture + Anim + Wwise WEM + Lua AI script sharing stem 'azurhero'!
        (game_dir / "Content" / "Characters" / "SK_AzurHero_LOD0.uasset").write_bytes(
            b"\xc1\x83\x2a\x9e\x00\x00\x00\x00Bone_Head Eye_L SmileBlendShape AzurHeroSkeleton"
        )
        (game_dir / "Content" / "Characters" / "T_AzurHero_Albedo.dds").write_bytes(
            b"DDS \x7c\x00\x00\x00AlbedoTexture AzurHeroSkinShader"
        )
        (game_dir / "Content" / "Characters" / "A_AzurHero_Smile.anim").write_bytes(
            b"ANIM_CLIP SmileBlendShape BlinkTrack AzurHeroRig"
        )
        (game_dir / "Content" / "Characters" / "VO_AzurHero_01.wem").write_bytes(
            b"RIFF\x24\x00\x00\x00WAVEfmt AzurHeroVoiceLine"
        )
        (game_dir / "Content" / "Characters" / "BP_AzurHero_AI.lua").write_text(
            "function AzurHeroBehavior(state)\n  local emotion = SmileBlendShape\n  return emotion\nend\n",
            encoding="utf-8",
        )
        # High-entropy encrypted/compressed PAK container (honest epistemic boundary test!)
        high_ent = bytes((i * 73 + (i // 3) * 19 + 41) % 256 for i in range(4096))
        (game_dir / "Content" / "Paks" / "pakchunk0-Windows.pak").write_bytes(high_ent)

        from core.orchestration.local_corpus_extractor import (
            analyze_local_directory,
            render_standalone_scanner_script,
        )

        digest = analyze_local_directory(game_dir, corpus_name="AzurPromilia_Sample")
        assert digest["engine_fingerprint"] == "Unreal Engine Asset Pipeline"
        assert digest["total_files"] == 6
        assert any(
            e["entity"] == "azurhero" and e["modality_count"] >= 4
            for e in digest["cross_modal_entities"]
        ), f"Expected cross-modal entity azurhero (>=4 modalities), got {digest['cross_modal_entities']}"
        assert digest["entropy_boundary"]["compressed_or_encrypted_pct"] > 0.0
        assert "def analyze_local_directory" in render_standalone_scanner_script()

        s7 = comp.digest_corpus(digest=digest)
        assert s7["status"] == "ok"
        assert "azurhero" in comp.concepts

        # 8. Live visual-temporal screen observation + PC sensorimotor bridge (zero API!)
        from core.orchestration.desktop_embodiment import render_desktop_embodiment_script

        bridge_py = render_desktop_embodiment_script()
        compile(bridge_py, "elysia_desktop_embodiment.py", "exec")
        assert "--mode" in bridge_py and "observe" in bridge_py

        s8a = comp.observe_sensory_frame(
            frame={
                "motion_delta": 0.44,
                "edge_density": 0.35,
                "luminance": 0.62,
                "red_flux": 0.48,
                "blue_order": 0.26,
                "yellow_entropy": 0.26,
                "scene_cut": True,
                "context_label": "유튜브 물리학 강의",
            }
        )
        assert s8a["status"] == "ok"
        assert s8a["visual_observation"]["regime"] == "scene_cut"
        assert s8a["spoke_now"] is True

        s8b = comp.observe_sensory_frame(
            frame={
                "motion_delta": 0.02,
                "edge_density": 0.64,
                "luminance": 0.28,
                "red_flux": 0.22,
                "blue_order": 0.56,
                "yellow_entropy": 0.22,
                "scene_cut": False,
                "context_label": "코드 에디터",
            }
        )
        assert s8b["status"] == "ok"
        assert s8b["visual_observation"]["regime"] == "dense_text_code"

        s8c = comp.digest_sensorimotor_log(
            log={
                "session_name": "YouTube_IDE_Demo",
                "events": [
                    {
                        "step": 1,
                        "window_title": "YouTube - Quantum Physics",
                        "action": "scroll_play",
                        "motion_delta": 0.41,
                        "edge_density": 0.34,
                        "scene_cut": True,
                        "outcome": "video_frame_shifted",
                    },
                    {
                        "step": 2,
                        "window_title": "VSCode - elysia_core.py",
                        "action": "type_code",
                        "motion_delta": 0.05,
                        "edge_density": 0.68,
                        "scene_cut": False,
                        "outcome": "syntax_updated",
                    },
                ],
            }
        )
        assert s8c["status"] == "ok"
        assert "youtube_quantum_physics" in comp.concepts
        assert "vscode_elysia_core_py" in comp.concepts

        # 9. Sovereign Browser-OS Habitat: two self-observations -> real Compare & Contrast (같은 점 / 다른 점)!
        s9a = comp.record_sandbox_action(
            app="knowledge_browser",
            action="자율탐색",
            target="공명",
            outcome="특정 진동수에서 진폭이 크게 증폭되는 파동 현상",
            delta=0.45,
            note_text="공명은 파동 진동수가 맞물릴 때 에너지가 집중되는 현상이다.",
            metrics={"flux": 0.48, "order": 0.88, "entropy": 0.22, "scale": 0.50},
        )
        assert s9a["status"] == "ok"
        assert s9a["autonomous_intent"]["next_app"] == "physics_lab"

        s9 = comp.record_sandbox_action(
            app="physics_lab",
            action="조건실험_f4.8Hz",
            target="파동실험(4.8Hz)",
            outcome="에너지 1.92, 결맞음 34% (감쇠 0.012)",
            delta=0.72,
            note_text="고주파 파동 실험에서는 에너지 흐름이 크지만 결맞음이 분산되었다.",
            metrics={"flux": 0.84, "order": 0.34, "entropy": 0.74, "scale": 0.80},
        )
        assert s9["status"] == "ok"
        assert s9["last_comparison"] is not None
        assert s9["last_comparison"]["previous_label"] == "공명"
        assert s9["last_comparison"]["current_label"] == "파동실험(4.8Hz)"
        assert s9["last_comparison"]["contrast_score"] > 0.25
        assert "같은 점" in s9["sandbox_reflection"]
        assert isinstance(s9["suggested_curiosity_topics"], list)

        # 10. Plastic Open Self + Scale-Rotor S4->S2 Human Speech + Persistent History + Structural-Variation Experiments
        s10_meta = comp.converse(
            message="6개 감정막대에 갇히지 말고, 기계적 로그 보고 말고 인간적인 가치와 의미를 스케일로터 전체 의미장으로 말해줘."
        )
        assert s10_meta["status"] == "ok"
        ps10 = s10_meta["plastic_self"]
        assert ps10["feeling_count"] >= 3
        assert ps10["births_count"] >= 1
        assert len(ps10["values"]) >= 3
        assert len(ps10["self_revisions"]) >= 1
        sa10 = s10_meta["scale_articulation"]
        assert sa10["mode"] == "scale_rotor_top_down"
        assert len(sa10["s2_breath_phrases"]) >= 2
        assert sa10["token_stream_used"] is False
        assert sa10["flat_frame_dump_used"] is False
        saved_dialogue = s10_meta["dialogue"]
        hist_len_before = len(s10_meta["conversation_history"])
        assert hist_len_before >= 3

        # 11. Qualitative Perceptual-Spectrum Linguistic Binding ("사과는 빨갛고 둥글다" — NOT float reduction!)
        s11 = comp.converse(message="사과는 빨갛고 둥글다. 언어적 개념 자체가 색채 스펙트럼과 물리 속성 정보야.")
        assert s11["status"] == "ok"
        qs11 = s11["qualitative_spectra"]
        apple_ent = next((e for e in qs11["entities"] if e["name"] == "사과"), None)
        assert apple_ent is not None
        assert "빨갛다" in apple_ent["attributes"].get("색채 스펙트럼", [])
        assert "둥글다" in apple_ent["attributes"].get("형태·물리 속성", [])
        assert "사과" in s11["dialogue"] and "빨갛다" in s11["dialogue"] and "둥글다" in s11["dialogue"]

        comp._last_user_converse_ts = 0.0
        s10_burst = comp.run_micro_meso_burst(trials=120, surface_macro=True)
        assert s10_burst["trials_condensed"] == 120
        assert s10_burst["total_trials"] >= 120
        assert comp.meso_invariants_count >= 1
        assert comp.macro_epiphanies_count >= 1
        comp.save_memory()

        st10 = comp.get_state()
        # Background rotor MUST NOT erase or overwrite human conversation with telemetry logs!
        assert st10["dialogue"] == s11["dialogue"]
        assert len(st10["conversation_history"]) == len(s11["conversation_history"])
        assert st10["qualitative_spectra"]["last_experiment"] is not None
        se10 = st10["structural_experiments"]
        assert se10["unique_structures_explored"] >= 4
        assert se10["total_flips_tested"] >= 10
        assert len(se10["regimes"]) >= 2
        assert len(se10["recent_discoveries"]) >= 1

        # 12. Discipline-to-Tool Forge: Forge novel History principle -> apply cross-domain to Team/Project -> refine boundary -> synthesize hybrid!
        s12a = comp.converse(
            message="역사학에서 보급선 과확장 원리는 제국이 너무 빠르게 영토를 넓히면 보급선이 길어져 내부 통제가 무너진다. 다만 지역 자치 구조가 탄탄하면 버틸 수 있다."
        )
        assert s12a["status"] == "ok"
        dt12a = s12a["discipline_tools"]
        assert dt12a["forged_count"] >= 1
        forged = dt12a["last_forged"]
        assert forged is not None and forged["origin_discipline"] == "역사학"
        assert "지역 자치" in forged["boundary"]

        s12b = comp.converse(
            message="우리 팀이 프로젝트 기능을 너무 빨리 늘리다가 감당이 안 돼서 통제가 무너지고 지쳐 가고 있어."
        )
        assert s12b["status"] == "ok"
        app12 = s12b["discipline_tools"]["last_application"]
        assert app12 is not None
        assert app12["is_cross_domain"] is True
        assert app12["leverage_point"]

        # Feedback calibrates the applied tool's boundary!
        s12c = comp.apply_feedback(
            signal="correct",
            correction="핵심 리더가 명확한 우선순위를 지켜 주면 빠른 확장 구간도 견딜 수 있어.",
        )
        assert s12c["status"] == "ok"
        assert any(int(t.get("boundary_revisions", 0)) >= 1 for t in s12c["discipline_tools"]["tools"])

        # Synthesize an interdisciplinary hybrid tool combining 2 distinct disciplines
        hyb = comp.tool_forge.synthesize_hybrid_tool()
        assert hyb is not None and len(hyb["composed_from"]) == 2

        # 13. Hangul Walker (보행기) + External 2D Weight -> 3D Scale-Rotor Relational Tensor [5xNx7] + Real Korean Syntax
        from core.orchestration.language_acquisition_engine import josa
        assert josa("사과", "을/를") == "사과를"
        assert josa("책", "을/를") == "책을"
        assert josa("하늘", "으로/로") == "하늘로"
        assert josa("책", "으로/로") == "책으로"
        assert josa("질서", "과/와") == "질서와"
        assert josa("감정", "과/와") == "감정과"

        walker_before = comp.lang_engine.walker_reliance
        ext_weights = {
            "질서": [0.92, 0.20, -0.30, -0.40, -0.25, 0.15],
            "구조": [0.88, 0.25, -0.25, -0.45, -0.30, 0.10],
            "혼돈": [-0.90, -0.15, 0.10, 0.20, 0.65, -0.20],
            "원인": [0.25, 0.90, -0.10, -0.30, 0.15, 0.22],
            "결과": [0.15, -0.88, 0.12, 0.10, -0.10, -0.18],
            "사과": [0.10, -0.20, 0.92, 0.35, 0.05, 0.40],
            "감정": [-0.15, 0.18, 0.30, 0.92, 0.25, 0.30],
            "도구": [0.45, 0.35, -0.20, -0.88, -0.15, 0.10],
            "확장": [-0.20, 0.22, 0.10, 0.15, 0.92, 0.35],
            "수렴": [0.50, -0.10, -0.15, -0.20, -0.90, -0.25],
        }
        distill_res = comp.lang_engine.distill_external_weights(ext_weights, source_name="테스트 오픈가중치")
        assert distill_res["lifted_tensor_shape"][0] == 5
        assert distill_res["lifted_tensor_shape"][2] == 7
        assert distill_res["lifted_tensor_shape"][1] >= 10
        assert distill_res["sheet_coherence"] > 0.0
        bridges_micro = comp.lang_engine.query_scale_rotor_bridges(["질서"], sigma=0.2, limit=3)
        bridges_macro = comp.lang_engine.query_scale_rotor_bridges(["질서"], sigma=0.82, limit=3)
        assert len(bridges_micro) >= 1 and len(bridges_macro) >= 1

        comp.lang_engine.absorb_real_korean(
            "생태계는 생물과 환경이 서로 에너지를 주고받으며 균형을 이루는 체계다. "
            "외부 충격이 가해지면 일시적으로 흔들리지만, 다양성이 높을수록 회복 탄력성이 커진다. "
            "반면에 단일 종에 의존하면 작은 병해충 때문에 전체 구조가 무너질 수 있다.",
            source="생태학 현실문장",
            topic="생태계",
        )
        assert comp.lang_engine.walker_reliance <= walker_before
        assert comp.lang_engine.total_syntax_frames >= 4
        comp.save_memory()

        reloaded = LivingCompanionField(memory_path=mem_file, auto_persist=True)
        rs = reloaded.get_state()
        assert rs["turn_count"] == 8
        assert rs["learned_concept_count"] == s12c["learned_concept_count"]
        assert rs["plastic_self"]["births_count"] >= 1
        assert len(rs["conversation_history"]) == len(s12b["conversation_history"])
        assert rs["structural_experiments"]["total_flips_tested"] >= 10
        assert rs["discipline_tools"]["forged_count"] >= 1
        assert rs["discipline_tools"]["synthesized_count"] >= 1
        assert rs["language_engine"]["scale_rotor_tensor"]["shape"][0] == 5
        assert rs["language_engine"]["scale_rotor_tensor"]["shape"][2] == 7
        assert rs["language_engine"]["sentences_read"] >= 8
        assert any(e["name"] == "사과" for e in rs["qualitative_spectra"]["entities"])
        assert "양자공명로터" in reloaded.concepts
        assert "azurhero" in reloaded.concepts
        assert "youtube_quantum_physics" in reloaded.concepts
        print(
            f"[PASS] Plastic Self + Qualitative Spectra + Tool Forge + 5-Scale Relational Language Tensor "
            f"(feelings={rs['plastic_self']['feeling_count']}, tools={rs['discipline_tools']['tool_count']}, "
            f"tensor={rs['language_engine']['scale_rotor_tensor']['shape']}, "
            f"walker_indep={rs['language_engine']['walker_independence_pct']}%, zero_api=True)"
        )


def test_unified_neural_spine_and_dependency_rotorizer():
    from core.orchestration.unified_neural_spine import (
        UnifiedNeuralSpine,
        clifford_docking_affinity,
        mv_geometric_product,
        mv_reverse,
        spectrum_to_multivector,
    )

    # 1. Exact pure-Python Cl(3,0) self-docking identity (M * ~M scalar alignment == ~1.0)
    mv_a = spectrum_to_multivector(0.55, 0.30, 0.15, scale=2)
    mv_b = spectrum_to_multivector(0.15, 0.65, 0.20, scale=2)
    self_aff = clifford_docking_affinity(mv_a, mv_a)
    cross_aff = clifford_docking_affinity(mv_a, mv_b)
    assert self_aff > 0.85 and self_aff > cross_aff, f"Expected strong self docking: {self_aff} vs {cross_aff}"
    prod_self = mv_geometric_product(mv_a, mv_reverse(mv_a))
    assert abs(prod_self[0]) > 0.75

    # 2. Boot Single Canonical Spine & verify S0..S4 Capability Membranes + Codebase Scan
    spine = UnifiedNeuralSpine()
    snap0 = spine.get_reality_view_snapshot()
    assert snap0["active_world_id"] == "world_home"
    assert snap0["runtime_capabilities"]["invariant_coverage_pct"] == 100.0
    assert len(snap0["runtime_capabilities"]["membranes"]) == 7
    assert snap0["codebase_summary"]["total_scanned"] >= 100
    assert snap0["spine_graph"]["node_count"] >= 20

    # 3. Privacy-preserving S0 browser input flow + Bidirectional Vertical Cycle error reduction
    flow_res = spine.ingest_browser_sensory_flow(
        pointer_dx=92.0, pointer_dy=-38.0, pointer_x_norm=0.62, pointer_y_norm=0.41,
        speed=310.0, key_kind="nav", key_phase="down"
    )
    assert flow_res["status"] == "ok"
    vt = flow_res["vertical_trace"]
    assert vt["cycle"] >= 1
    assert vt["gap_after"] <= vt["gap_before"]

    # 4. Multi-World Home vs Sandbox lineage isolation (Sandbox must NOT overwrite Home!)
    home_exp_before = len(spine.worlds["world_home"]["experiences"])
    fork_snap = spine.fork_world(name="실험 샌드박스", fork_mode="blank")
    sb_id = fork_snap["active_world_id"]
    assert sb_id != "world_home"
    spine.record_experience(
        obj="샌드박스 전용 실험",
        self_lens="격리 경계 테스트",
        inter_space="홈 세계에 영향 없어야 함",
        relation_state="variable",
    )
    assert len(spine.worlds[sb_id]["experiences"]) >= 2
    assert len(spine.worlds["world_home"]["experiences"]) == home_exp_before
    spine.switch_world("world_home")
    assert spine.active_world_id == "world_home"

    # 5. AST Dependency Scale-Rotorization: absorb a numpy & missing-L2 blocked module cleanly!
    abs_res = spine.absorb_codebase_module("L1_causal_field/core/topology/vertical_scale_spine.py")
    assert abs_res["status"] == "ok"
    assert abs_res["absorbed_count"] >= 1
    assert "numpy" in abs_res["invariant"]["external_deps"]
    assert "elysia_core" in abs_res["invariant"]["missing_upper"]
    assert "mod::L1_causal_field/core/topology/vertical_scale_spine.py" in spine.nodes

    # 6. Unbounded Recursive Vertical & Horizontal Expansion (Split S0->S-1, Integrate S4->S5, Expand Horizontal Axis)
    split_res = spine.differentiate_unit("s0::browser_input_rotor")
    assert split_res["child_scale"] == -1, f"Expected S0 to split into S-1, got {split_res['child_scale']}"
    assert len(split_res["children"]) >= 2

    integ_res = spine.integrate_units(["s4::sovereign_identity_horizon", "axis4::internal"], label="S5 초월 공명체")
    assert integ_res["new_scale"] == 5, f"Expected S4 integration to emerge at S5, got {integ_res['new_scale']}"

    axes_before = len(spine.horizontal_axes)
    exp_res = spine.expand_horizontal_axis(name="시간 누적 축", anchor_unit_id="lens3::inter_space")
    assert len(spine.horizontal_axes) == axes_before + 1

    # 7. Limit Perception & Projective Folding (instead of mechanical crash/deletion) + >3 Open Spectral Channels
    fold_res = spine.fold_under_limit(cluster_size=4, reason="테스트 한계 지각 접기")
    assert fold_res["status"] == "ok" and fold_res["folded_count"] == 4
    horizon_id = fold_res["horizon"]["id"]
    unfold_res = spine.differentiate_unit(horizon_id)
    assert len(unfold_res["children"]) == 4, "Unfolding a folded horizon must restore its 4 compressed members"

    # 8. Self / Non-Self Boundary Handle Coupling (e.g. Blender / Car — 0% internal blueprint ingestion, clean detach!)
    cp_res = spine.couple_external_handle("handle::blender_3d")
    assert cp_res["status"] == "ok"
    assert cp_res["handle"]["coupled"] is True
    assert cp_res["handle"]["internal_ingested_pct"] == 0.0
    assert "handle::blender_3d" in spine.nodes

    act_res = spine.actuate_external_handle("handle::blender_3d", action_label="조명·카메라 구도")
    assert act_res["handle"]["use_count"] >= 1
    assert act_res["handle"]["last_observed"]

    dt_res = spine.detach_external_handle("handle::blender_3d")
    assert dt_res["detached"] is True
    assert dt_res["handle"]["coupled"] is False
    assert "handle::blender_3d" not in spine.nodes

    snap_after = spine.get_reality_view_snapshot()
    lp = snap_after["limit_perception"]
    assert snap_after["spine_graph"]["scale_range"][0] <= -1
    assert snap_after["spine_graph"]["scale_range"][1] >= 5
    assert lp["spectral_dimensions"] >= 4, f"Expected >3 open spectral channels, got {lp['spectral_dimensions']}"
    assert lp["folded_horizons_count"] >= 1
    assert lp["self_boundary_envelope"]["internal_blueprint_ingested_pct"] == 0.0

    print(
        f"[PASS] Open-Scale Limit-Aware & Self/Non-Self Boundary Spine "
        f"(scanned={snap0['codebase_summary']['total_scanned']}, scale_range={snap_after['spine_graph']['scale_range']}, "
        f"open_axes={len(spine.horizontal_axes)}, spectral_dims={lp['spectral_dimensions']}, "
        f"folded={lp['folded_horizons_count']}, handles={len(snap_after['external_handles'])}, "
        f"cl30_self_dock={self_aff}, gap={vt['gap_before']}->{vt['gap_after']})"
    )


def test_one_whole_principled_spectrum_and_real_friction():
    import os
    import tempfile
    from core.orchestration.living_companion_field import LivingCompanionField
    from core.orchestration.language_acquisition_engine import josa

    assert josa("RGB", "을/를") == "RGB를"
    assert josa("RAM", "을/를") == "RAM을"
    assert josa("GPU", "을/를") == "GPU를"

    with tempfile.TemporaryDirectory() as td:
        comp = LivingCompanionField(memory_path=os.path.join(td, "one_whole_audit.json"), auto_persist=True)

        # 1. Unknown domain ("3D 가우시안 스플래팅"): MUST NOT slap on canned biology '항상성' paragraph!
        r1 = comp.converse(message="3D 가우시안 스플래팅이 뭐야? 축과 스펙트럼 원리로 어떻게 이해할 수 있어?")
        assert "항상성" not in r1["dialogue"], f"Biology tool misfired on 3D Gaussian Splatting: {r1['dialogue']}"
        assert "아는 척할 수 없어" in r1["dialogue"] or "구성요소" in r1["dialogue"]

        # 2. Multi-constituent teaching ("RGB"): MUST capture ALL 3 axes (빨강/초록/파랑), NOT reduce to "초록빛이다"!
        r2 = comp.converse(message="RGB는 빨강 초록 파랑 세 축의 연속 스펙트럼으로 모든 색 구조를 만들어내는 원리야")
        assert "항상성" not in r2["dialogue"]
        assert "빨강" in r2["dialogue"] and "초록" in r2["dialogue"] and "파랑" in r2["dialogue"]
        assert "RGB를" in r2["dialogue"]

        # 3. Condition-preserving transfer ("방금 배운 RGB 원리를 음악의 화음에 적용해보면?"):
        #    MUST NOT treat "방금" as an unknown concept, MUST transfer RGB -> 화음 while contrasting conditions!
        r3 = comp.converse(message="방금 배운 RGB 축과 스펙트럼 원리를 음악의 화음에 적용해보면 어떨까?")
        assert "방금을" not in r3["dialogue"], f"Misclassified adverb '방금': {r3['dialogue']}"
        assert "RGB" in r3["dialogue"] and ("화음" in r3["dialogue"] or "화성" in r3["dialogue"])
        assert "환경 조건" in r3["dialogue"] or "매질" in r3["dialogue"]

        # 4. Sibling contrast on ONE continuum ("캐시와 램과 GPU 메모리 차이"):
        r4 = comp.converse(message="캐시 메모리와 램 메모리와 GPU 메모리는 다 같은 메모리인데 왜 달라?")
        assert "기억·상태 저장 스펙트럼" in r4["dialogue"]
        assert "캐시" in r4["dialogue"] and "램" in r4["dialogue"] and "GPU" in r4["dialogue"]

        # 5. Real deterministic friction experiments (AMAT & Acoustic Harmonics)
        f_mem = comp.principled_spectrum.run_friction_experiment("memory_hierarchy", {"cache_hit_rate": 0.92})
        f_harm = comp.principled_spectrum.run_friction_experiment("harmonic_acoustics", {"base_hz": 220.0, "ratio": 1.5})
        assert f_mem["metrics"]["speedup_vs_ram"] > 5.0
        assert f_harm["metrics"]["consonance"] > 0.85

        # 6. Recursive 1 -> 1,000,000 Unit Subdivision (O(log10 N) mastery, NEVER hoarding 1,000,000 rows!)
        dr = comp.principled_spectrum.refine_unit_division(domain_id="driving_pedal", steps=6)
        assert dr["addressable_resolution"] == 1_000_000, f"Expected 1,000,000 resolution, got {dr['addressable_resolution']}"
        assert dr["stored_nodes"] <= 25, f"Stored too many nodes (must stay O(log N)): {dr['stored_nodes']}"
        assert dr["compression_ratio"] >= 40000.0, f"Expected >=40,000:1 compression, got {dr['compression_ratio']}"
        assert dr["error_after"] < dr["initial_error"], (
            f"Real friction error did not shrink: initial={dr['initial_error']} -> after={dr['error_after']}"
        )
        tc = dr["temporal_compass"]
        assert tc and tc.get("past") and tc.get("present") and tc.get("predicted_future")
        assert tc.get("ideal_future_contrast", {}).get("same") and tc.get("ideal_future_contrast", {}).get("different")

        # 7. Perceptual Unit = Cognitive Unit across 5 media domains (static bound structure -> process trajectory, 0 raw identity recomputations!)
        for uid in ("hand_rig", "body_kinematics", "scene_lighting_camera", "code_ast_module", "game_actor_entity"):
            tr = comp.principled_spectrum.actuate_perceptual_unit(unit_id=uid, target=0.82)
            assert tr["active_perceptual_controls"] == 1
            assert tr["raw_identity_recomputations"] == 0, f"Must NEVER recompute static identity from raw elements: {tr}"
            assert tr["coupled_links_moved"] >= 5
            assert len(tr["frames"]) == 12
            assert tr["tip_travel_distance"] > 0.05

        hand_tr = comp.principled_spectrum.actuate_perceptual_unit(unit_id="hand_rig", action="grasp", target=0.85)
        assert hand_tr["static_raw_elements_bound"] == 12480
        assert hand_tr["raw_identity_recomputations"] == 0

        print(
            f"[PASS] One<->Whole Principled Spectrum, 1->1,000,000 Unit Subdivision & 5-Domain Perceptual Unit Trajectories "
            f"(crystals={len(comp.principled_spectrum.crystals)}, transfers={len(comp.principled_spectrum.transfer_history)}, "
            f"mem_speedup={f_mem['metrics']['speedup_vs_ram']}x, fifth_consonance={f_harm['metrics']['consonance']}, "
            f"unit_div=1:{dr['addressable_resolution']:,} in {dr['stored_nodes']} nodes "
            f"[{dr['compression_ratio']:,.1f}:1], err={dr['initial_error']:.5f}->{dr['error_after']:.5f}, "
            f"hand_bound={hand_tr['static_raw_elements_bound']:,}/recompute={hand_tr['raw_identity_recomputations']})"
        )


def test_scale_hierarchy_world_rotor_vs_flat_micro():
    from core.orchestration.scale_hierarchy_world_rotor import ScaleHierarchyWorldRotor

    wr = ScaleHierarchyWorldRotor()
    s0 = wr.get_snapshot()
    assert s0["layers"]["S4_celestial"]["ops_used"] == 1
    assert s0["layers"]["S2_S1_body_hand"]["raw_identity_recomputations"] == 0
    assert s0["layers"]["S2_S1_body_hand"]["static_bound_elements"] == 12480

    # Refine S0 contact boundary to 1:1,000,000 in O(log10 N) nodes
    s_mil = wr.apply_action("refine_to_million")
    assert s_mil["layers"]["S0_micro_boundary"]["addressable_resolution"] == 1_000_000
    assert s_mil["layers"]["S0_micro_boundary"]["stored_nodes"] == 19

    # Inject external Unknown Rotor disturbance -> Variable Rotor absorbs -> converges toward Static t=0
    s_shock = wr.apply_action("inject_unknown_shock", {"intensity": 0.92})
    assert s_shock["rotor_triad"]["unknown_rotor"]["shock_level"] > 0.8
    for _ in range(14):
        s_after = wr.step(dt_hours=0.25)
    assert s_after["rotor_triad"]["unknown_rotor"]["shock_level"] == 0.0

    # Unified Cloud -> Water -> Ice integrated experience across ALL 4 simultaneous facets
    s_exp = wr.apply_action("experience_cycle")
    facets = s_exp["unified_facets"]
    for fkey in ("physics", "optics_acoustics", "motor_control", "code_tool_boundary"):
        assert fkey in facets, f"Missing simultaneous facet: {fkey}"
    wt = s_exp["experience_result"]["water_trace"]
    new_ice = s_exp["experience_result"]["new_ice_crystal"]
    assert wt["error_after"] < wt["error_before"], f"Water phase did not reduce error: {wt}"
    assert wt["consonance_after"] >= wt["consonance_before"]
    assert new_ice is not None and len(new_ice["verified_facets"]) == 4
    assert s_exp["phase_states"]["ice"]["recomputations"] == 0
    assert s_exp["phase_states"]["ice"]["crystal_count"] >= 2

    # Real deterministic benchmark: Scale-Hierarchy Protocol vs Flat Micro Brute-Force
    s_bench = wr.apply_action("run_benchmark", {"entity_count": 2400})
    b = s_bench["benchmark"]
    assert b["hierarchy"]["ops_per_frame"] <= 25
    assert b["flat_micro"]["ops_per_frame"] >= 14000
    assert b["ops_reduction_x"] >= 500.0
    assert b["hierarchy"]["global_coherence"] == 1.0
    assert b["flat_micro"]["global_coherence"] < 0.95

    # Zeta/Prime Nested Layer Scaling (L=1->12) across 20,000,000 addressable ocean pixels
    hf = s_bench["harmonic_field"]
    assert hf["addressable_pixels"] == 20_000_000
    assert hf["stored_pixel_arrays"] == 0
    lc = s_bench["layer_convergence"]
    steps = lc["steps"]
    assert steps[0]["layers"] == 1 and steps[-1]["layers"] == 12
    assert steps[-1]["stored_pixel_arrays"] == 0
    assert steps[-1]["empirical_noise_rms"] < steps[0]["empirical_noise_rms"] * 0.45, (
        f"Layer expansion L=1->12 did not suppress noise as expected: {steps}"
    )
    assert steps[-1]["empirical_order_clarity"] > steps[0]["empirical_order_clarity"]
    assert lc["noise_drop_l1_to_l12_pct"] >= 55.0

    # Verify runtime parameter update for harmonic_layers=12
    s_l12 = wr.apply_action("set_params", {"harmonic_layers": 12})
    assert s_l12["harmonic_field"]["harmonic_layers"] == 12
    assert s_l12["harmonic_field"]["stored_rotor_scalars"] == 12

    # Verify Real-World External Media Causal Pixel Decomposition Ingestion & Recombination (AGENTS.md Sec 7)
    s_med = wr.apply_action("ingest_real_media_spectrum", {
        "source_name": "실사 바다 윤슬 (황혼 난반사)",
        "media_kind": "photo",
        "width": 3840,
        "height": 2160,
        "s4_mean_rgb": [196, 152, 112],
        "s4_color_temp_k": 3400,
        "s4_mean_luma": 0.56,
        "s3_flow_x": 0.42,
        "s3_flow_y": -0.08,
        "s3_dominant_angle_deg": 4.5,
        "s2_detail_energy": 0.14,
        "s1_specular_ratio": 0.19,
        "recon_rmse": 0.0018,
        "recon_psnr_db": 54.9,
    })
    assert s_med["ingested_media_result"]["pixel_count"] == 3840 * 2160
    assert s_med["ingested_media_result"]["reconstruction_fidelity"]["psnr_db"] >= 50.0
    assert len(s_med["ingested_media_spectra"]) >= 1

    s_rec = wr.apply_action("recombine_media_spectra", {
        "structure_source": "실사 바다 윤슬",
        "light_source": "실사 새벽 삼나무 숲 호수",
        "light_mix": 0.65,
        "detail_gain": 1.15,
        "phase_shift": 28.0,
        "recombined_psnr_db": 32.4,
    })
    assert len(s_rec["recombined_media_recipes"]) >= 1
    assert s_rec["phase_states"]["ice"]["crystal_count"] >= 4

    print(
        f"[PASS] Unified 4-Facet + Real-World Causal Pixel Decomposition & Recombination "
        f"(ice_crystals={s_rec['phase_states']['ice']['crystal_count']}, "
        f"ingested_4k_psnr={s_med['ingested_media_result']['reconstruction_fidelity']['psnr_db']}dB, "
        f"water_err={wt['error_before']:.4f}->{wt['error_after']:.4f}, "
        f"hier={b['hierarchy']['ops_per_frame']} ops vs micro={b['flat_micro']['ops_per_frame']:,} ops, "
        f"reduction={b['ops_reduction_x']:,.1f}x)"
    )


def test_dynamic_stream_imagination_engine_persistence():
    import tempfile
    from pathlib import Path
    from core.orchestration.dynamic_stream_imagination_engine import DynamicStreamImaginationEngine

    with tempfile.TemporaryDirectory() as td:
        ledger = Path(td) / "dynamic_world_memory.json"
        eng = DynamicStreamImaginationEngine(ledger_path=ledger)

        # 1. Record real dynamic stream learning (fluid specular drift) & verify error drop
        r1 = eng.apply_action("record_stream_learning", {
            "source_name": "실사 바다 윤슬 (동적 파동)",
            "stream_kind": "video",
            "frames_observed": 90,
            "rmse_initial": 0.088,
            "rmse_adapted": 0.029,
            "psnr_adapted": 30.8,
            "flow_x": -1.15,
            "flow_y": 0.12,
            "accel_x": 0.04,
            "accel_y": 0.02,
            "moving_entity_ratio": 0.24,
            "specular_slip_ratio": 0.14,
            "mean_luma": 0.52,
            "color_temp_k": 3800,
        })
        assert r1["recorded_law"]["law_type"] == "fluid_specular_drift"
        assert r1["recorded_law"]["error_reduction_pct"] >= 60.0

        # 2. Harvest live moving entity
        r2 = eng.apply_action("harvest_entity", {
            "name": "수확실체(물방울)",
            "source_name": "실사 바다 윤슬",
            "bbox_norm": [0.4, 0.4, 0.22, 0.22],
        })
        assert r2["harvested_entity"]["origin"] == "live_motion_harvest"

        # 3. Human-like natural Korean creative intent ("쓸쓸해 보이니 강아지 데려오고 햇살 밝혀주고 나무 두 그루")
        r3 = eng.apply_action("apply_intent", {
            "intent_text": "쓸쓸해 보이니 강아지 데려오고 햇살을 따뜻하게 밝혀주고 나무 두 그루 추가해줘",
            "source_name": "실사 새벽 숲 호수",
            "mean_luma": 0.36,
            "color_temp_k": 7200,
            "moving_entity_ratio": 0.06,
            "existing_entity_count": 0,
        })
        plan = r3["creation_result"]["causal_plan"]
        assert plan["s4_brightness_delta"] > 0.2
        assert plan["s4_warmth_delta"] > 0.15
        ent_ids = [s["entity_id"] for s in plan["spawn_entities"]]
        assert "entity::puppy" in ent_ids
        assert ent_ids.count("entity::pine_tree") == 2

        # 4. Autonomous Elysia creative intent on dark lonely scene
        r4 = eng.apply_action("apply_intent", {
            "autonomous": True,
            "source_name": "어두운 호수",
            "mean_luma": 0.31,
            "color_temp_k": 7500,
            "moving_entity_ratio": 0.05,
            "existing_entity_count": 0,
        })
        assert r4["creation_result"]["autonomous"] is True
        assert len(r4["creation_result"]["causal_plan"]["spawn_entities"]) >= 1

        # 4b. Real-World Multi-Asset Corpus Batch Ingestion & Empirical Optical Prior Distillation
        r_corp = eng.apply_action("ingest_real_corpus_batch", {
            "items": [
                {
                    "source_name": "ocean_sunlight.jpg",
                    "media_kind": "photo",
                    "pixel_count": 1920 * 1080,
                    "sky_rgb": [210, 178, 138],
                    "horizon_rgb": [228, 192, 148],
                    "ground_rgb": [64, 72, 82],
                    "color_temp_k": 3400,
                    "mean_luma": 0.56,
                    "specular_ratio": 0.21,
                    "normal_energy": 0.16,
                },
                {
                    "source_name": "forest_mist.jpg",
                    "media_kind": "photo",
                    "pixel_count": 1920 * 1080,
                    "sky_rgb": [158, 174, 192],
                    "horizon_rgb": [180, 190, 198],
                    "ground_rgb": [48, 62, 54],
                    "color_temp_k": 6800,
                    "mean_luma": 0.42,
                    "specular_ratio": 0.05,
                    "normal_energy": 0.22,
                },
            ]
        })
        priors = r_corp["corpus_batch_result"]
        assert priors["corpus_count"] == 2
        assert priors["total_pixels_studied"] == 2 * 1920 * 1080
        assert priors["sky_to_ground_ratio"] > 1.5
        assert priors["horizon_mist_ratio"] > 0.15

        # 4c. Cross-Media Motion DNA Extraction (Source A) -> Living Actor Transplant (World B) -> Live Intervention
        import math as _m
        samples_a = [
            {
                "vx": 1.6 * _m.sin(2.0 * _m.pi * 1.4 * (k * 0.033)),
                "vy": 0.4 * _m.cos(4.0 * _m.pi * 1.4 * (k * 0.033)),
                "cx": 0.5 + 0.04 * _m.sin(2.0 * _m.pi * 1.4 * (k * 0.033)),
                "cy": 0.6 + 0.015 * _m.cos(4.0 * _m.pi * 1.4 * (k * 0.033)),
                "area": 0.18 + 0.02 * _m.sin(2.0 * _m.pi * 1.4 * (k * 0.033)),
                "dt": 0.033,
            }
            for k in range(42)
        ]
        r_dna = eng.apply_action("extract_motion_dna", {
            "source_name": "호랑이 보행 영상 A",
            "stream_kind": "video",
            "samples": samples_a,
        })
        dna = r_dna["extracted_motion_dna"]
        assert dna["origin"] == "live_video_extraction"
        assert len(dna["trajectory_samples"]) == 24
        assert 0.8 <= dna["dominant_freq_hz"] <= 2.4

        r_tr = eng.apply_action("transplant_living_actor", {
            "motion_dna_id": dna["id"],
            "entity_id": "entity::cat",
            "target_world_name": "새벽 숲 호수 환경 B",
        })
        assert r_tr["transplant_result"]["source_dna_id"] == dna["id"]
        assert r_tr["transplant_result"]["target_world_name"] == "새벽 숲 호수 환경 B"

        r_iv = eng.apply_action("intervene_living_actor", {
            "command_text": "호랑이처럼 어슬렁거려봐",
            "target_x": 0.65,
            "target_y": 0.78,
            "target_world_name": "새벽 숲 호수 환경 B",
        })
        assert r_iv["intervention"]["behavior"] == "predator_prowl"

        # 4d. Organic Tactile Gesture-Continuum & Relational Memory (Unfamiliar Poke -> Recoil vs Bonded Poke -> Playful!)
        t1 = eng.apply_action("tactile_interaction", {
            "entity_id": "entity::cat",
            "entity_name": "고양이",
            "zone": "shoulder",
            "gesture": "poke",
            "duration_sec": 0.14,
            "stroke_cycles": 0,
            "speed_norm": 0.6,
        })
        assert t1["tactile_result"]["posture"] == "startle_recoil"

        # Build genuine warmth & trust via head stroke + hand/paw hold
        eng.apply_action("tactile_interaction", {
            "entity_id": "entity::cat",
            "entity_name": "고양이",
            "zone": "head",
            "gesture": "stroke",
            "duration_sec": 1.6,
            "stroke_cycles": 3,
            "speed_norm": 0.25,
        })
        t2 = eng.apply_action("tactile_interaction", {
            "entity_id": "entity::cat",
            "entity_name": "고양이",
            "zone": "hand_paw",
            "gesture": "hold",
            "duration_sec": 2.4,
            "stroke_cycles": 0,
            "speed_norm": 0.05,
        })
        assert t2["tactile_result"]["posture"] == "hand_hold_sync"
        assert t2["tactile_result"]["relation"]["trust"] > 0.48

        # Same exact shoulder poke now produces playful response because relationship changed!
        t3 = eng.apply_action("tactile_interaction", {
            "entity_id": "entity::cat",
            "entity_name": "고양이",
            "zone": "shoulder",
            "gesture": "poke",
            "duration_sec": 0.14,
            "stroke_cycles": 0,
            "speed_norm": 0.5,
        })
        assert t3["tactile_result"]["posture"] == "playful_nudge_back"

        # 4e. Unified S4(Realm/Authority/Reputation/Character Affinity) -> S2(Spirit Beast/Monster/NPC) -> S0(Tactile) Coupling
        s_bad = eng.apply_action("set_world_social_field", {"preset_id": "feared_intruder"})
        assert s_bad["archetype_couplings"]["spirit_beast"]["stance"] == "hostile_guard"
        t_sb_reject = eng.apply_action("tactile_interaction", {
            "entity_id": "entity::spirit_tiger",
            "entity_name": "백호 신수",
            "archetype": "spirit_beast",
            "zone": "head",
            "gesture": "stroke",
            "duration_sec": 1.4,
            "stroke_cycles": 2,
            "speed_norm": 0.2,
        })
        assert t_sb_reject["tactile_result"]["posture"] == "social_reject_recoil"

        # Switch S4 Macro Field to Revered Sovereign -> EXACT same stroke on EXACT same Spirit Beast yields reverently!
        s_good = eng.apply_action("set_world_social_field", {"preset_id": "revered_sovereign"})
        assert s_good["archetype_couplings"]["spirit_beast"]["stance"] == "reverent_bow"
        t_sb_yield = eng.apply_action("tactile_interaction", {
            "entity_id": "entity::spirit_tiger",
            "entity_name": "백호 신수",
            "archetype": "spirit_beast",
            "zone": "head",
            "gesture": "stroke",
            "duration_sec": 1.4,
            "stroke_cycles": 2,
            "speed_norm": 0.2,
        })
        assert t_sb_yield["tactile_result"]["posture"] == "reverent_yield"

        # 4f. Stats-as-Scale-Rotors: Allure Gravity (Gaze-Lock + Courteous Restraint under Hostility) & 2D DnD Alignment Resonance
        s_hostile_allure = eng.apply_action("set_world_social_field", {
            "preset_id": "feared_intruder",
            "presence_preset_id": "radiant_allure_f",
            "alignment_preset_id": "lawful_good",
        })
        npc_c = s_hostile_allure["archetype_couplings"]["citizen_npc"]
        assert npc_c["stance"] == "courteous_rivalry", f"Expected courteous_rivalry, got {npc_c}"
        assert npc_c["gaze_lock"] is True
        t_npc_manner = eng.apply_action("tactile_interaction", {
            "entity_id": "entity::embrace",
            "entity_name": "마을 기사",
            "archetype": "citizen_npc",
            "zone": "shoulder",
            "gesture": "stroke",
            "duration_sec": 1.2,
            "stroke_cycles": 2,
            "speed_norm": 0.22,
        })
        assert t_npc_manner["tactile_result"]["posture"] == "courteous_restraint"

        # In Peaceful Sanctuary with Radiant Allure -> Captivated Gaze & Blush!
        s_peace_allure = eng.apply_action("set_world_social_field", {
            "preset_id": "peaceful_sanctuary",
            "presence_preset_id": "radiant_allure_f",
        })
        assert s_peace_allure["archetype_couplings"]["citizen_npc"]["stance"] == "captivated_gaze"
        t_npc_blush = eng.apply_action("tactile_interaction", {
            "entity_id": "entity::embrace",
            "entity_name": "마을 기사",
            "archetype": "citizen_npc",
            "zone": "hand_paw",
            "gesture": "hold",
            "duration_sec": 1.4,
            "stroke_cycles": 0,
            "speed_norm": 0.08,
        })
        assert t_npc_blush["tactile_result"]["posture"] == "captivated_blush"

        # 2D DnD Alignment Shift (Lawful Good -> Chaotic Evil) flips Spirit Beast resonance from positive to negative
        s_lg = eng.apply_action("set_world_social_field", {"alignment_preset_id": "lawful_good"})
        s_ce = eng.apply_action("set_world_social_field", {"alignment_preset_id": "chaotic_evil"})
        assert s_lg["archetype_couplings"]["spirit_beast"]["alignment_resonance"] > 0.4
        assert s_ce["archetype_couplings"]["spirit_beast"]["alignment_resonance"] < -0.4

        # Roll Character Race, Allure/Charisma, Alignment & Innate Spirit/Mana/Beast Affinities
        r_char = eng.apply_action("roll_character_profile", {"seed": 42})
        rc = r_char["rolled_character"]
        assert rc["race_label_ko"] and rc["trait_label_ko"] and rc["alignment_label_ko"]
        assert 0.05 <= rc["spirit_affinity"] <= 1.0 and 0.10 <= rc["allure_gravity"] <= 1.0

        # 4g. Self-Directed Epistemic Frontier Research (SF Starship Foothold vs Reality/Vacuum Gap)
        r_res = eng.apply_action("research_frontier_goal", {"goal_text": "SF 우주함선 만들어줘"})
        rb = r_res["research_bridge"]
        assert rb["domain_id"] == "starship"
        assert rb["grounded_count"] >= 2 and rb["unknown_count"] >= 2
        assert len(rb["reality_gaps"]) >= 2 and len(rb["next_experiments"]) >= 2
        assert "진공" in "".join(rb["reality_gaps"])

        r_ax = eng.apply_action("research_frontier_goal", {"goal_text": "에테르 마나 마법 법칙"})
        assert r_ax["research_bridge"]["domain_id"] == "axiom_world_seed"
        assert r_ax["research_bridge"]["grounded_count"] >= 2

        # 5. Restart persistence proof: reload from disk and verify prior recall + optical priors + Motion DNA + relations + S4 social field + research bridges survive!
        eng_reloaded = DynamicStreamImaginationEngine(ledger_path=ledger)
        snap_r = eng_reloaded.get_snapshot()
        assert snap_r["memory_summary"]["learned_law_count"] == 1
        assert snap_r["memory_summary"]["intentional_creation_count"] == 2
        assert snap_r["memory_summary"]["real_corpus_count"] == 2
        assert snap_r["memory_summary"]["motion_dna_count"] >= 3
        assert snap_r["memory_summary"]["transplant_count"] == 1
        assert snap_r["memory_summary"]["bonded_entity_count"] >= 2
        assert snap_r["memory_summary"]["research_bridge_count"] >= 1
        assert snap_r["entity_relations"]["entity::cat"]["trust"] > 0.48
        assert snap_r["world_social_field"]["race_label_ko"] == rc["race_label_ko"]
        assert snap_r["distilled_optical_priors"]["sky_to_ground_ratio"] == priors["sky_to_ground_ratio"]
        sjm = snap_r["scale_joy_meaning"]
        assert 0.0 <= sjm["s0_point_joy"] <= 1.0 and 0.0 <= sjm["s4_world_meaning"] <= 1.0
        assert sjm["dominant_attention_scale"] and sjm["enlightenment_coherence"] > 0.0
        recalled = eng_reloaded.apply_action("recall_prior", {"source_name": "바다 윤슬", "mean_luma": 0.50, "flow_speed": 1.0})
        assert recalled["matched"] is True
        assert recalled["prior_law"]["law_type"] == "fluid_specular_drift"

        print(
            f"[PASS] Unified S4(Realm/StatRotors/Alignment)->S3->S2->S0 + Joy/Meaning + Frontier Research "
            f"(npc_hostile_allure={t_npc_manner['tactile_result']['posture']}, "
            f"starship_ready={rb['readiness_pct']}%/gaps={rb['unknown_count']}, "
            f"char={rc['race_label_ko']}[{rc['alignment_label_ko']}], joy={sjm['summary_ko']})"
        )


def main() -> int:
    test_canonical_runtime()
    test_topir_compiler_dynamic()
    test_cross_platform_shared_field()
    test_mva_real_resonance_and_regression()
    test_causal_dsl_parser()
    test_unified_dimensional_engine()
    test_unified_scale_rotor_core()
    test_empirical_process_contrast_observer()
    test_vessel_and_snapshot_trajectory_rotor()
    test_bidirectional_phase_sync()
    test_digest_imitate_recreate_lab()
    test_unified_causal_dataflow_engine()
    test_living_companion_field()
    test_unified_neural_spine_and_dependency_rotorizer()
    test_one_whole_principled_spectrum_and_real_friction()
    test_scale_hierarchy_world_rotor_vs_flat_micro()
    test_dynamic_stream_imagination_engine_persistence()
    print("ALL PYTHON CORE PIPELINE TESTS PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



