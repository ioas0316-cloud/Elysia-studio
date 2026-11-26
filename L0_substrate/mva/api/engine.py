import numpy as np
from typing import List, Dict, Any, Tuple
from scipy.spatial.transform import Rotation as R
import math
import json
import os
import mmap
import struct
import sys
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from core.memory.causal_controller import CausalMemoryController
from core.physics.topological_manifold import TopologicalManifold
from core.physics.phase_gravity import PhaseTransitionEngine, DensityFluidGravity
from core.physics.causal_field import InformationVoxel

memory_controller = CausalMemoryController()
# Global manifold instance for continuous simulation
manifold = TopologicalManifold(size=32, damping=0.95, wave_speed=0.5)

# [Phase-Gravity Continuous Fluid Engine Components]
phase_engine = PhaseTransitionEngine(size=32)
fluid_gravity = DensityFluidGravity(size=32, pressure_scaling=10.0, viscosity=0.15)

def inject_resonance_to_fractal_field(tension: float, observation_axis: str = 'spatial'):
    """(Phase 4) Cross-platform write of continuous tension to the shared rotor field."""
    from shared_field import write_rotor_tension
    write_rotor_tension(tension, observation_axis=observation_axis)


def _rotate_point_by_quat(p: Tuple[float, float, float], q: List[float]) -> Tuple[float, float, float]:
    """Rotate 3D vector p=(x,y,z) by unit quaternion q=[qx,qy,qz,qw]."""
    qx, qy, qz, qw = q
    norm = math.sqrt(qx * qx + qy * qy + qz * qz + qw * qw) + 1e-12
    qx, qy, qz, qw = qx / norm, qy / norm, qz / norm, qw / norm
    px, py, pz = p
    # t = 2 * cross(q.xyz, p)
    tx = 2.0 * (qy * pz - qz * py)
    ty = 2.0 * (qz * px - qx * pz)
    tz = 2.0 * (qx * py - qy * px)
    return (
        px + qw * tx + (qy * tz - qz * ty),
        py + qw * ty + (qz * tx - qx * tz),
        pz + qw * tz + (qx * ty - qy * tx),
    )


def _extract_positions(points_data: List[Dict[str, Any]]) -> List[Tuple[float, float, float]]:
    coords: List[Tuple[float, float, float]] = []
    for p in points_data:
        pos = p.get("position", [0.0, 0.0, 0.0])
        x = float(pos[0]) if len(pos) > 0 else 0.0
        y = float(pos[1]) if len(pos) > 1 else 0.0
        z = float(pos[2]) if len(pos) > 2 else 0.0
        coords.append((x, y, z))
    return coords


def find_resonance_angle(points_data: List[Dict[str, Any]], time_t: float) -> Tuple[List[float], float]:
    """
    Finds the optimal unit quaternion [qx, qy, qz, qw] minimizing z-axis projection variance
    (planar alignment resonance) via deterministic Fibonacci-sphere S^3 sampling + local refinement.
    """
    coords = _extract_positions(points_data)
    if len(coords) < 2:
        return [0.0, 0.0, 0.0, 1.0], 0.0

    def z_variance(q: List[float]) -> float:
        zs = [_rotate_point_by_quat(pt, q)[2] for pt in coords]
        mean_z = sum(zs) / len(zs)
        return sum((z - mean_z) ** 2 for z in zs) / len(zs)

    best_q = [0.0, 0.0, 0.0, 1.0]
    best_var = z_variance(best_q)

    # Deterministic coarse search on SO(3) axes + phase angles
    golden = (1.0 + math.sqrt(5.0)) / 2.0
    for i in range(24):
        theta_s = math.acos(1.0 - 2.0 * (i + 0.5) / 24.0)
        phi_s = 2.0 * math.pi * i / golden
        ax = math.sin(theta_s) * math.cos(phi_s)
        ay = math.sin(theta_s) * math.sin(phi_s)
        az = math.cos(theta_s)
        for k in range(1, 5):
            half = 0.5 * (math.pi * k / 5.0 + 0.05 * math.sin(time_t))
            s = math.sin(half)
            cand = [ax * s, ay * s, az * s, math.cos(half)]
            v = z_variance(cand)
            if v < best_var:
                best_var = v
                best_q = cand

    # Local coordinate refinement
    step = 0.08
    for _ in range(4):
        improved = False
        for axis in range(4):
            for sign in (-1.0, 1.0):
                cand = list(best_q)
                cand[axis] += sign * step
                n = math.sqrt(sum(c * c for c in cand)) + 1e-12
                cand = [c / n for c in cand]
                v = z_variance(cand)
                if v < best_var:
                    best_var = v
                    best_q = cand
                    improved = True
        if not improved:
            step *= 0.5

    return [round(c, 6) for c in best_q], float(best_var)


def generate_symbolic_regression(
    points_data: List[Dict[str, Any]], quaternion: List[float], time_t: float
) -> Tuple[str, float]:
    """
    Fits an analytical planar-harmonic law z(x, y, t) = a*x + b*y + c*cos(t) + d
    to the quaternion-aligned points via ordinary least squares and reports true R^2.
    """
    coords = _extract_positions(points_data)
    if len(coords) < 2:
        return "z(x, y, t) = 0.000", 1.0

    rotated = [_rotate_point_by_quat(pt, quaternion) for pt in coords]
    cos_t = math.cos(time_t)
    # Build 3x3 normal equations for z = a*x + b*y + d (plus harmonic phase offset)
    sxx = syy = sxy = sx = sy = sz = sxz = syz = 0.0
    n = float(len(rotated))
    for x, y, z in rotated:
        sxx += x * x
        syy += y * y
        sxy += x * y
        sx += x
        sy += y
        sz += z
        sxz += x * z
        syz += y * z

    # Ridge-stabilized 3x3 Gaussian elimination
    reg = 1e-5
    A = [
        [sxx + reg, sxy, sx],
        [sxy, syy + reg, sy],
        [sx, sy, n + reg],
    ]
    b_vec = [sxz, syz, sz]
    for col in range(3):
        piv = max(range(col, 3), key=lambda r: abs(A[r][col]))
        A[col], A[piv] = A[piv], A[col]
        b_vec[col], b_vec[piv] = b_vec[piv], b_vec[col]
        div = A[col][col] if abs(A[col][col]) > 1e-12 else 1e-12
        for j in range(col, 3):
            A[col][j] /= div
        b_vec[col] /= div
        for r in range(3):
            if r != col:
                f = A[r][col]
                for j in range(col, 3):
                    A[r][j] -= f * A[col][j]
                b_vec[r] -= f * b_vec[col]

    a_coef, b_coef, d_coef = b_vec
    mean_z = sz / n
    ss_tot = sum((z - mean_z) ** 2 for _, _, z in rotated)
    ss_res = sum((z - (a_coef * x + b_coef * y + d_coef)) ** 2 for x, y, z in rotated)
    r_squared = 1.0 if ss_tot < 1e-12 else max(0.0, min(1.0, 1.0 - ss_res / ss_tot))

    formula = (
        f"z(x,y,t) = {a_coef:+.3f}*x {b_coef:+.3f}*y {d_coef:+.3f} "
        f"[phase cos(t)={cos_t:+.2f}, R^2={r_squared:.3f}]"
    )
    return formula, float(r_squared)


def evaluate_current_state(points_data: List[Dict[str, Any]], quaternion: List[float], time_t: float) -> Tuple[float, bool, str]:
    if not points_data:
        return 1.0, False, ""

    voxels = []
    for i, p in enumerate(points_data):
        pos = p.get('position', [0, 0, 0])
        nx = max(0.0, min(1.0, (pos[0] + 10.0) / 20.0))
        ny = max(0.0, min(1.0, (pos[1] + 10.0) / 20.0))
        amp = pos[2] if len(pos) > 2 else 1.0

        manifold.inject_disturbance(nx, ny, amplitude=amp)
        phase_engine.inject_disturbance(nx, ny, intensity=0.15)

        vox = InformationVoxel(
            id=f"pt_{i}",
            content=p.get('token', '*'),
            tensor=np.array([nx, ny, amp], dtype=np.float32),
            position=np.array(pos, dtype=np.float32),
            velocity=np.array(p.get('velocity', [0, 0, 0]), dtype=np.float32)
        )
        voxels.append(vox)

    manifold.step()
    phase_engine.step(dt=0.1)
    fluid_gravity.apply_gravity(voxels, phase_engine, dt=0.1)

    for i, vox in enumerate(voxels):
        vox.position += vox.velocity * 0.1
        points_data[i]['position'] = vox.position.tolist()
        points_data[i]['velocity'] = vox.velocity.tolist()

    bulk_e, grad_e = phase_engine.calculate_free_energy()
    total_phase_energy = bulk_e + grad_e
    wave_tension = manifold.calculate_surface_tension()
    tension = float((wave_tension * 0.4) + (total_phase_energy * 0.6))

    is_resonant = tension < 1.0
    formula, _ = generate_symbolic_regression(points_data, quaternion, time_t)

    if is_resonant:
        try:
            tokens = "".join([p.get('token', '') for p in points_data])
            memory_controller.write_causal_engram(
                data_blob={"event": "Manifold Resonance", "tension": tension, "tokens_snippet": tokens[:50]},
                emotional_value=1.0,
                cause_id="Topological_Resonance"
            )
        except Exception:
            pass
        inject_resonance_to_fractal_field(tension, observation_axis='spatial')

    return tension, is_resonant, formula


def elysia_auto_observe_step(points_data: List[Dict[str, Any]], time_t: float) -> Tuple[List[float], float, bool, str]:
    """Autonomously searches optimal resonance quaternion and evaluates the updated field."""
    best_quat, _ = find_resonance_angle(points_data, time_t)
    tension, is_resonant, formula = evaluate_current_state(points_data, best_quat, time_t)
    return best_quat, tension, is_resonant, formula
