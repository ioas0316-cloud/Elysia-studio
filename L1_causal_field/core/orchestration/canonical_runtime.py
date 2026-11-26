"""
Canonical Elysia Runtime (단일 정본 오케스트레이터)
==================================================
Unifies the core 4-stage continuous causal lifecycle:
    1. Observe  : Ingest raw external stimulus & measure phase friction against active focus.
    2. Evolve   : Advance continuous causal field potentials, beam tensions, and chromatic flow.
    3. Consolidate: Crystallize low-tension resonant states into persistent engram attractors.
    4. Act      : Emit continuous motor/focus directive & escalate fractal resistance if stuck.

Works with NumPy when installed and falls back cleanly to pure-Python stdlib math so
the canonical lifecycle can be verified in minimal environments without heavy dependencies.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple


def _vec_norm(v: Sequence[float]) -> float:
    return math.sqrt(sum(x * x for x in v))


def _vec_normalize(v: Sequence[float]) -> List[float]:
    n = _vec_norm(v)
    if n < 1e-12:
        return [0.0 for _ in v]
    return [x / n for x in v]


def _q_normalize(q: Sequence[float]) -> List[float]:
    n = math.sqrt(sum(x * x for x in q))
    if n < 1e-12:
        return [0.0, 0.0, 0.0, 1.0]
    return [x / n for x in q]


def _q_mul(a: Sequence[float], b: Sequence[float]) -> List[float]:
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return _q_normalize([
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
        aw * bw - ax * bx - ay * by - az * bz,
    ])


def _q_from_axis_angle(axis: Sequence[float], angle: float) -> List[float]:
    n = _vec_norm(axis)
    if n < 1e-12 or abs(angle) < 1e-12:
        return [0.0, 0.0, 0.0, 1.0]
    half = 0.5 * angle
    s = math.sin(half) / n
    return _q_normalize([axis[0] * s, axis[1] * s, axis[2] * s, math.cos(half)])


def _q_geodesic_dist(a: Sequence[float], b: Sequence[float]) -> float:
    dot = abs(sum(x * y for x, y in zip(a, b)))
    return 2.0 * math.acos(max(0.0, min(1.0, dot)))


@dataclass
class ScaleRotorLevel:
    """Single scale stratum (S0..S4) in the bidirectional Fractal Scale-Rotor Hierarchy."""

    scale: int
    name: str
    gear_ratio: float
    damping: float
    quaternion: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 1.0])
    angular_velocity: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    semantic_mass: float = 1.0
    coherence: float = 1.0
    tension: float = 0.0
    chromatic: List[float] = field(default_factory=lambda: [0.33, 0.34, 0.33])


@dataclass
class CanonicalVoxel:
    voxel_id: str
    content: str
    position: List[float]
    velocity: List[float]
    tensor: List[float]
    chromatic: List[float] = field(default_factory=lambda: [0.33, 0.34, 0.33])  # [Red, Blue, Yellow]
    mass: float = 1.0
    potential: float = 0.0
    scale: int = 0


@dataclass
class CanonicalBeam:
    source_id: str
    target_id: str
    strength: float = 1.0
    rest_length: float = 1.0
    break_threshold: float = 5.0
    current_tension: float = 0.0
    is_broken: bool = False


@dataclass
class EngramMemory:
    engram_id: str
    signature: List[float]
    resonance_score: float
    cycle_created: int
    scale_signature: List[float] = field(default_factory=list)


@dataclass
class CycleReport:
    cycle: int
    friction: float
    mean_tension: float
    mean_potential: float
    active_beams: int
    broken_beams: int
    engrams_count: int
    escalated_loop_break: bool
    action_vector: List[float]
    scale_coherence: float = 1.0
    scale_dial: float = 0.5
    rotor_quaternions: Dict[int, List[float]] = field(default_factory=dict)


class CanonicalElysiaRuntime:
    """
    Single canonical entry point consolidating Elysia's living causal cycle
    with the 5-Scale Fractal Rotor Hierarchy (S0 Atomic <-> S4 Episode Attractor).
    """

    _DEFAULT_SCALES: Tuple[Tuple[int, str, float, float], ...] = (
        (0, "S0_Atomic_Impulse", 1.000, 0.04),
        (1, "S1_Micro_Composite", 0.618, 0.06),
        (2, "S2_Functional_Unit", 0.382, 0.08),
        (3, "S3_Modal_Config", 0.236, 0.10),
        (4, "S4_Episode_Attractor", 0.146, 0.12),
    )

    def __init__(self, dimensions: int = 3, resonance_threshold: float = 0.35, scale_dial: float = 0.5):
        self.dimensions = dimensions
        self.resonance_threshold = resonance_threshold
        self.scale_dial = max(0.0, min(1.0, float(scale_dial)))
        self.cycle_count = 0
        self.active_focus = _vec_normalize([1.0] * dimensions)
        self.voxels: Dict[str, CanonicalVoxel] = {}
        self.beams: List[CanonicalBeam] = []
        self.engrams: List[EngramMemory] = []
        self._stagnation_accumulator = 0.0
        self.scale_rotors: List[ScaleRotorLevel] = [
            ScaleRotorLevel(
                scale=s,
                name=name,
                gear_ratio=gamma,
                damping=damp,
                semantic_mass=1.0 + 0.85 * s,
            )
            for s, name, gamma, damp in self._DEFAULT_SCALES
        ]

    def set_scale_dial(self, sigma: float) -> float:
        """Continuously zoom focus between S0 micro-flux (0.0) and S4 macro-order (1.0)."""
        self.scale_dial = max(0.0, min(1.0, float(sigma)))
        return self.scale_dial

    def add_voxel(
        self,
        voxel_id: str,
        content: str,
        position: Sequence[float],
        tensor: Sequence[float],
        mass: float = 1.0,
        scale: int = 0,
    ) -> CanonicalVoxel:
        pos = self._fit_dim(position)
        ten = self._fit_dim(tensor)
        v = CanonicalVoxel(
            voxel_id=voxel_id,
            content=content,
            position=pos,
            velocity=[0.0] * self.dimensions,
            tensor=ten,
            mass=max(1e-3, float(mass)),
            scale=max(0, min(4, int(scale))),
        )
        self.voxels[voxel_id] = v
        return v

    def link(self, id_a: str, id_b: str, strength: float = 1.0, break_threshold: float = 5.0) -> Optional[CanonicalBeam]:
        if id_a not in self.voxels or id_b not in self.voxels:
            return None
        pa, pb = self.voxels[id_a].position, self.voxels[id_b].position
        dist = _vec_norm([b - a for a, b in zip(pa, pb)])
        beam = CanonicalBeam(
            source_id=id_a,
            target_id=id_b,
            strength=strength,
            rest_length=dist,
            break_threshold=break_threshold,
        )
        self.beams.append(beam)
        return beam

    def _fit_dim(self, vec: Sequence[float]) -> List[float]:
        arr = [float(x) for x in vec]
        if len(arr) < self.dimensions:
            arr.extend([0.0] * (self.dimensions - len(arr)))
        return arr[: self.dimensions]

    def _to_vec3(self, vec: Sequence[float]) -> List[float]:
        out = [float(vec[i]) if i < len(vec) else 0.0 for i in range(3)]
        return out

    def evolve_scale_rotors(self, stimulus: Sequence[float], friction: float, dt: float = 0.1) -> float:
        """
        Bidirectional Fractal Scale-Rotor Dynamics:
          - Upward Ascent (S0 -> S4): inject atomic torque at S0 and couple upward by gear ratio Gamma_ij.
          - Downward Plasticity (S4 -> S0): macro attractor phase coherence stabilizes lower scales
            weighted by the continuous scale_dial (sigma).
          - Exact S^3 Exponential Map Integration: guarantees ||q|| == 1.0 at every scale.
        """
        stim3 = self._to_vec3(stimulus)
        s0 = self.scale_rotors[0]
        impulse_gain = 0.25 + 0.5 * min(2.0, friction)
        for k in range(3):
            s0.angular_velocity[k] += (stim3[k] * impulse_gain / s0.semantic_mass) * dt

        # 1. Upward Dimensional Rotor Ascent (S0 -> S4)
        for i in range(len(self.scale_rotors) - 1):
            child = self.scale_rotors[i]
            parent = self.scale_rotors[i + 1]
            gamma = parent.gear_ratio / max(1e-6, child.gear_ratio)
            upward_gain = 0.40 * (0.6 + 0.4 * (1.0 - self.scale_dial))
            for k in range(3):
                torque = upward_gain * (child.angular_velocity[k] * gamma - parent.angular_velocity[k])
                parent.angular_velocity[k] += (torque / parent.semantic_mass) * dt

        # 2. Downward Differentiation / Plastic Feedback (S4 -> S0)
        for i in range(len(self.scale_rotors) - 2, -1, -1):
            cur = self.scale_rotors[i]
            above = self.scale_rotors[i + 1]
            dist = _q_geodesic_dist(cur.quaternion, above.quaternion)
            cur.coherence = max(0.0, min(1.0, math.cos(0.5 * dist)))
            cur.tension = min(2.0, dist / math.pi)
            downward_gain = 0.30 * (0.5 + 0.5 * self.scale_dial)
            for k in range(3):
                cur.angular_velocity[k] = (
                    cur.angular_velocity[k] * (1.0 - cur.damping * dt)
                    + downward_gain * (above.angular_velocity[k] - cur.angular_velocity[k]) * dt
                )
            speed = _vec_norm(cur.angular_velocity)
            r_c = min(0.85, 0.2 + 0.35 * speed)
            b_c = min(0.85, 0.2 + 0.6 * cur.coherence)
            y_c = max(0.05, 0.5 * cur.tension)
            tot = r_c + b_c + y_c
            cur.chromatic = [r_c / tot, b_c / tot, y_c / tot]

        # 3. Exact S^3 Exponential Map Quaternion Integration
        for rotor in self.scale_rotors:
            w_mag = _vec_norm(rotor.angular_velocity)
            if w_mag > 1e-12:
                dq = _q_from_axis_angle(rotor.angular_velocity, w_mag * dt)
                rotor.quaternion = _q_mul(dq, rotor.quaternion)

        lower_coh = sum(r.coherence for r in self.scale_rotors[:-1]) / max(1, len(self.scale_rotors) - 1)
        self.scale_rotors[-1].coherence = lower_coh
        self.scale_rotors[-1].tension = max(0.0, 1.0 - lower_coh)
        return sum(r.coherence for r in self.scale_rotors) / len(self.scale_rotors)

    def observe(self, stimulus: Sequence[float], target_id: Optional[str] = None) -> float:
        """Stage 1: Project intentional focus onto external stimulus and compute causal friction."""
        raw = self._fit_dim(stimulus)
        raw_unit = _vec_normalize(raw)
        if not self.voxels:
            self.add_voxel("core_0", "origin", [0.0] * self.dimensions, self.active_focus, scale=0)

        targets = [self.voxels[target_id]] if target_id and target_id in self.voxels else list(self.voxels.values())
        total_friction = 0.0
        for v in targets:
            v_unit = _vec_normalize(v.tensor)
            dot = max(-1.0, min(1.0, sum(a * b for a, b in zip(v_unit, raw_unit))))
            phase_div = math.acos(dot)
            friction = phase_div * (1.0 + abs(_vec_norm(v.tensor) - _vec_norm(raw)))
            total_friction += friction

            if friction > 0.25:
                rate = min(0.5, friction * 0.25)
                v.tensor = [(1.0 - rate) * a + rate * b for a, b in zip(v.tensor, raw)]
                for i in range(self.dimensions):
                    v.velocity[i] += ((raw_unit[i] - v_unit[i]) * friction) / v.mass
                # Chromatic calibration (Red -> Blue stabilization)
                v.chromatic[0] = max(0.0, v.chromatic[0] - 0.1 * rate)
                v.chromatic[1] = min(1.0, v.chromatic[1] + 0.15 * rate)
                s = sum(v.chromatic)
                if s > 0:
                    v.chromatic = [c / s for c in v.chromatic]

        self.active_focus = _vec_normalize([0.8 * a + 0.2 * b for a, b in zip(self.active_focus, raw_unit)])
        return total_friction / max(1, len(targets))

    def evolve_field(self, dt: float = 0.1) -> Tuple[float, float]:
        """Stage 2: Update beam tensions, Hooke's law forces, potential flow, and damped mobility."""
        tensions: List[float] = []
        for beam in self.beams:
            if beam.is_broken:
                continue
            va = self.voxels.get(beam.source_id)
            vb = self.voxels.get(beam.target_id)
            if va is None or vb is None:
                continue
            diff = [b - a for a, b in zip(va.position, vb.position)]
            dist = _vec_norm(diff)
            ext = dist - beam.rest_length
            beam.current_tension = beam.strength * abs(ext)
            tensions.append(beam.current_tension)
            if beam.current_tension > beam.break_threshold:
                beam.is_broken = True
                continue
            scale = (beam.strength * ext) / (dist + 1e-9)
            for i in range(self.dimensions):
                f_i = scale * diff[i]
                va.velocity[i] += (f_i / va.mass) * dt
                vb.velocity[i] -= (f_i / vb.mass) * dt

            # Potential flow along active beam
            delta_p = (va.potential - vb.potential) * 0.1 * dt
            va.potential -= delta_p
            vb.potential += delta_p

        potentials: List[float] = []
        for v in self.voxels.values():
            r, b, _ = v.chromatic
            scale_rotor = self.scale_rotors[v.scale]
            flux_boost = (1.0 + r) * (0.7 + 0.3 * scale_rotor.gear_ratio)
            damping = 0.95 * (1.0 - 0.2 * b) * (1.0 - 0.05 * scale_rotor.tension)
            for i in range(self.dimensions):
                v.position[i] += v.velocity[i] * flux_boost * dt
                v.velocity[i] *= damping
            speed = _vec_norm(v.velocity)
            v.potential = 0.9 * v.potential + 0.1 * speed
            potentials.append(v.potential)

        mean_tension = sum(tensions) / len(tensions) if tensions else 0.0
        mean_potential = sum(potentials) / len(potentials) if potentials else 0.0
        return mean_tension, mean_potential

    def consolidate_memory(self, friction: float) -> bool:
        """Stage 3: Crystallize stable low-friction resonant state with S0..S4 signature into EngramMemory."""
        if friction <= self.resonance_threshold:
            self.engrams.append(
                EngramMemory(
                    engram_id=f"engram_{self.cycle_count}",
                    signature=list(self.active_focus),
                    resonance_score=max(0.0, 1.0 - friction),
                    cycle_created=self.cycle_count,
                    scale_signature=[round(r.coherence, 4) for r in self.scale_rotors],
                )
            )
            return True
        return False

    def act(self, friction: float) -> Tuple[List[float], bool]:
        """Stage 4: Emit continuous focus action vector and break local minima if stagnated."""
        escalated = False
        if friction > 0.8:
            self._stagnation_accumulator += friction
        else:
            self._stagnation_accumulator = max(0.0, self._stagnation_accumulator - 0.5)

        action = list(self.active_focus)
        if self._stagnation_accumulator >= 2.5:
            # Orthogonal nudge + scale-rotor S4->S0 phase twist to break closed-loop fixation
            self._stagnation_accumulator = 0.0
            escalated = True
            if self.dimensions >= 2:
                action[0], action[1] = -action[1], action[0]
            self.active_focus = _vec_normalize(action)
            self.scale_rotors[-1].angular_velocity[1] += 0.75
        return action, escalated

    def step_cycle(self, stimulus: Sequence[float], dt: float = 0.1) -> CycleReport:
        self.cycle_count += 1
        friction = self.observe(stimulus)
        scale_coherence = self.evolve_scale_rotors(stimulus, friction, dt=dt)
        mean_tension, mean_potential = self.evolve_field(dt=dt)
        self.consolidate_memory(friction)
        action, escalated = self.act(friction)
        active_beams = sum(1 for b in self.beams if not b.is_broken)
        broken_beams = sum(1 for b in self.beams if b.is_broken)
        return CycleReport(
            cycle=self.cycle_count,
            friction=friction,
            mean_tension=mean_tension,
            mean_potential=mean_potential,
            active_beams=active_beams,
            broken_beams=broken_beams,
            engrams_count=len(self.engrams),
            escalated_loop_break=escalated,
            action_vector=action,
            scale_coherence=scale_coherence,
            scale_dial=self.scale_dial,
            rotor_quaternions={r.scale: list(r.quaternion) for r in self.scale_rotors},
        )

