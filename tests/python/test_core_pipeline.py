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
    print("ALL PYTHON CORE PIPELINE TESTS PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



