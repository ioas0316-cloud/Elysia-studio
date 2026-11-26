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


def main() -> int:
    test_canonical_runtime()
    test_topir_compiler_dynamic()
    test_cross_platform_shared_field()
    test_mva_real_resonance_and_regression()
    test_causal_dsl_parser()
    test_unified_dimensional_engine()
    print("ALL PYTHON CORE PIPELINE TESTS PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
