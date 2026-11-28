"""Hierarchical, reversible motion field for scale-coupled world objects.

This prototype stores a world's *generating rules* (rotors and parent links),
then derives positions at a requested time.  It is intended for macro motion
such as orbits, rotation, and slowly changing illumination, not pixel rendering.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional, Tuple

import numpy as np


Vector = Tuple[float, float, float]


def _unit(vector: Vector) -> np.ndarray:
    value = np.asarray(vector, dtype=np.float64)
    norm = float(np.linalg.norm(value))
    if norm <= 1e-12:
        raise ValueError("rotor axis must have non-zero length")
    return value / norm


@dataclass(frozen=True)
class ScaleRotor:
    """A continuous generator: axis, angular rate, phase, radius, and scale."""

    axis: Vector = (0.0, 0.0, 1.0)
    angular_rate: float = 1.0
    phase: float = 0.0
    radius: float = 1.0
    scale: float = 1.0

    def angle_at(self, time: float) -> float:
        return self.phase + self.angular_rate * time

    def offset_at(self, time: float) -> np.ndarray:
        """Position in the rotor plane at arbitrary time, including rewind."""
        axis = _unit(self.axis)
        # Pick a stable in-plane basis; the second vector completes the plane.
        reference = np.array([1.0, 0.0, 0.0])
        if abs(float(np.dot(axis, reference))) > 0.9:
            reference = np.array([0.0, 1.0, 0.0])
        u = np.cross(axis, reference)
        u /= np.linalg.norm(u)
        v = np.cross(axis, u)
        angle = self.angle_at(time)
        return self.radius * self.scale * (np.cos(angle) * u + np.sin(angle) * v)


@dataclass
class RotorNode:
    """A causal object whose local motion is defined relative to a parent."""

    node_id: str
    rotor: ScaleRotor
    parent_id: Optional[str] = None
    local_origin: Vector = (0.0, 0.0, 0.0)
    # Optional spectral bands represent motion at different temporal scales.
    bands: Tuple[ScaleRotor, ...] = field(default_factory=tuple)


class CausalScaleRotorField:
    """Evaluate nested rotors as a worldline, forward or backward in time.

    Nodes retain their causal parent links and motion generators.  Querying a
    time slice composes only the requested node's ancestry; no frame history or
    full scene tensor is required.  `advance` uses exact analytic phase deltas
    for any requested time and returns changed positions for consumers.
    """

    def __init__(self, nodes: Iterable[RotorNode] = (), causal_field=None) -> None:
        self.nodes: Dict[str, RotorNode] = {}
        self._last_positions: Dict[str, np.ndarray] = {}
        self._time: Optional[float] = None
        self.causal_field = causal_field
        for node in nodes:
            self.add(node)

    def add(self, node: RotorNode) -> None:
        if node.node_id in self.nodes:
            raise ValueError(f"duplicate rotor node: {node.node_id}")
        if node.parent_id is not None and node.parent_id not in self.nodes:
            raise ValueError(f"parent must be registered first: {node.parent_id}")
        self.nodes[node.node_id] = node
        if self.causal_field is not None:
            # Bind the generator to Elysia's shared causal substrate.  The
            # rotor remains the authoritative rule; the voxel carries its
            # current observable state and causal signature.
            from core.physics.causal_field import InformationVoxel

            self.causal_field.add_voxel(
                InformationVoxel(
                    id=node.node_id,
                    content={"rotor": node.rotor, "parent_id": node.parent_id},
                    tensor=np.asarray(
                        [node.rotor.angular_rate, node.rotor.phase, node.rotor.radius, node.rotor.scale],
                        dtype=np.float32,
                    ),
                    mass=max(abs(node.rotor.scale), 1e-6),
                    position=np.asarray(node.local_origin, dtype=np.float32),
                    velocity=np.zeros(3, dtype=np.float32),
                    phase_angle=node.rotor.phase,
                    scale_level=abs(node.rotor.scale),
                )
            )

    def position_at(self, node_id: str, time: float) -> np.ndarray:
        """Resolve a causal world position at any time, including the past."""
        node = self.nodes[node_id]
        local = np.asarray(node.local_origin, dtype=np.float64) + node.rotor.offset_at(time)
        for band in node.bands:
            local += band.offset_at(time)
        if node.parent_id is None:
            return local
        return self.position_at(node.parent_id, time) + local

    def slice_at(self, time: float, node_ids: Optional[Iterable[str]] = None) -> Dict[str, np.ndarray]:
        """Extract a spatial cross-section of the worldline at arbitrary time."""
        selected = self.nodes.keys() if node_ids is None else node_ids
        return {node_id: self.position_at(node_id, time) for node_id in selected}

    def advance(self, time: float) -> Dict[str, np.ndarray]:
        """Return per-node displacement from the previous slice (causal delta)."""
        current = self.slice_at(time)
        previous_positions = self._last_positions
        previous_time = self._time
        if self._time is None:
            changes = {key: value.copy() for key, value in current.items()}
        else:
            changes = {
                key: value - self._last_positions[key]
                for key, value in current.items()
                if not np.allclose(value, self._last_positions[key], rtol=0.0, atol=1e-12)
            }
        if self.causal_field is not None:
            for node_id, position in current.items():
                voxel = self.causal_field.voxels[node_id]
                voxel.position = position.astype(np.float32)
                if node_id in previous_positions and previous_time is not None:
                    voxel.velocity = (
                        (position - previous_positions[node_id])
                        / ((time - previous_time) if time != previous_time else 1e-12)
                    ).astype(np.float32)
                voxel.phase_angle = self.nodes[node_id].rotor.angle_at(time) % (2.0 * np.pi)
        self._last_positions = current
        self._time = time
        return changes


def sample_solar_system(time: float) -> Dict[str, np.ndarray]:
    """Small demonstration: star, planet orbit, moon orbit, and axial spin."""
    field = CausalScaleRotorField(
        [
            RotorNode("star", ScaleRotor(radius=0.0)),
            RotorNode("planet", ScaleRotor(angular_rate=0.2, radius=10.0), "star"),
            RotorNode(
                "moon",
                ScaleRotor(angular_rate=1.4, radius=2.0),
                "planet",
                bands=(ScaleRotor(angular_rate=0.8, radius=0.25),),
            ),
        ]
    )
    return field.slice_at(time)


# ---------------------------------------------------------------------------
# Universal Scale-Rotor Form Principle: Static Ice (x) Water Rotor (+) Knots
# ---------------------------------------------------------------------------


@dataclass
class FormKnobVector:
    """Unified orthogonal knob coordinates shared across language, voice, vision, 3D rig, and law."""

    vertical_scale: float = 0.5        # 0.0 (micro analytic) .. 1.0 (macro aesthetic)
    horizontal_relational: float = 0.0  # -1.0 (shy/soft) .. +1.0 (theatrical/jester)
    tempo_rate: float = 1.0            # temporal angular frequency multiplier
    pitch_f0: float = 1.0              # fundamental frequency / vocal fold axis
    formant_tract: float = 1.0         # vocal-tract / resonance chamber length axis (<1 masculine, >1 bright)
    law_damping: float = 0.0           # <0 self-excitation, 0 conservation, >0 damping
    harmonic_order: float = 0.85       # high-frequency detail retention [0.15..1.0]

    def to_dict(self) -> Dict[str, float]:
        return {
            "vertical_scale": round(float(self.vertical_scale), 4),
            "horizontal_relational": round(float(self.horizontal_relational), 4),
            "tempo_rate": round(float(self.tempo_rate), 4),
            "pitch_f0": round(float(self.pitch_f0), 4),
            "formant_tract": round(float(self.formant_tract), 4),
            "law_damping": round(float(self.law_damping), 4),
            "harmonic_order": round(float(self.harmonic_order), 4),
        }


@dataclass
class UniversalFormRotor:
    """
    Domain-agnostic Scale-Rotor Form representation:
        Phi(t; u) = IceBase (x) WaterRotor(t; u) (+) sum_k Knot_k * G_sigma(t - t_k)
    Allows extracting a dynamic form signature from ANY modality (e.g. YouTube video
    face/body motion DNA or speech prosody) and zero-shot transferring it to ANY other
    modality (e.g. Blender 3D rig bones, vocal formant envelope, or narrative pacing).
    """

    domain: str
    ice_base: np.ndarray           # (D,) static t=0 invariant centroid / rest pose
    mode_freqs_hz: np.ndarray      # (K,) dominant temporal frequencies
    mode_coeffs: np.ndarray        # (K, D) complex Fourier rotor amplitudes
    knot_times: np.ndarray         # (M,) sparse boundary event timestamps in [0, 1]
    knot_impulses: np.ndarray      # (M, D) sparse residual impulse vectors
    duration_s: float = 1.0

    @classmethod
    def fit_trajectory(
        cls,
        domain: str,
        trajectory: np.ndarray,
        duration_s: float = 1.0,
        max_modes: int = 6,
        max_knots: int = 4,
    ) -> "UniversalFormRotor":
        arr = np.asarray(trajectory, dtype=np.float64)
        if arr.ndim == 1:
            arr = arr[:, None]
        n, d = arr.shape
        ice_base = np.mean(arr, axis=0)
        centered = arr - ice_base[None, :]

        # Extract dominant Fourier Water-Rotor modes via rFFT
        spec = np.fft.rfft(centered, axis=0) / max(1, n)
        freqs = np.fft.rfftfreq(n, d=max(1e-4, duration_s / max(1, n)))
        power = np.sum(np.abs(spec) ** 2, axis=1)
        if len(power) > 1:
            power[0] = 0.0  # DC already stored in ice_base
        k_keep = min(max_modes, max(1, len(power) - 1))
        top_idx = np.argsort(-power)[:k_keep]
        mode_freqs = freqs[top_idx]
        # Double non-DC non-Nyquist complex amplitudes for one-sided reconstruction
        mode_coeffs = spec[top_idx] * 2.0

        # Reconstruct continuous Water trajectory and harvest Sparse Event Knots from residual
        t_norm = np.linspace(0.0, 1.0, n, endpoint=False)
        t_sec = t_norm * duration_s
        phases = 2.0 * np.pi * np.outer(t_sec, mode_freqs)
        water = np.real(np.exp(1j * phases) @ mode_coeffs)
        residual = centered - water
        res_energy = np.linalg.norm(residual, axis=1)

        knot_t_list = []
        knot_imp_list = []
        if n >= 4 and float(np.max(res_energy)) > 1e-6:
            peak_order = np.argsort(-res_energy)
            for idx in peak_order:
                tn = float(t_norm[int(idx)])
                if all(abs(tn - prev) > 0.08 for prev in knot_t_list):
                    knot_t_list.append(tn)
                    knot_imp_list.append(residual[int(idx)].copy())
                if len(knot_t_list) >= max_knots:
                    break

        knot_times = np.asarray(knot_t_list, dtype=np.float64) if knot_t_list else np.zeros(0, dtype=np.float64)
        knot_impulses = np.stack(knot_imp_list, axis=0) if knot_imp_list else np.zeros((0, d), dtype=np.float64)
        return cls(
            domain=domain,
            ice_base=ice_base,
            mode_freqs_hz=mode_freqs,
            mode_coeffs=mode_coeffs,
            knot_times=knot_times,
            knot_impulses=knot_impulses,
            duration_s=float(duration_s),
        )

    def evaluate(self, n_steps: int, knobs: Optional[FormKnobVector] = None) -> np.ndarray:
        """Evaluates Phi(t; u) under any continuous `FormKnobVector` modulation."""
        u = knobs if knobs is not None else FormKnobVector()
        n = max(2, int(n_steps))
        t_norm = np.linspace(0.0, 1.0, n, endpoint=False)
        t_sec = t_norm * self.duration_s

        tempo = max(0.3, min(2.5, float(u.tempo_rate)))
        damping = max(-0.6, min(0.8, float(u.law_damping)))
        h_order = max(0.15, min(1.0, float(u.harmonic_order)))
        amp_scale = max(0.35, min(1.85, 1.0 + 0.45 * float(u.horizontal_relational)))

        # Mode weights attenuate upper harmonics continuously by `harmonic_order`
        k = len(self.mode_freqs_hz)
        m_weights = np.linspace(1.0, h_order, k)[:, None] if k > 0 else np.zeros((0, 1))
        phase_shift = float(u.vertical_scale - 0.5) * np.pi
        phases = 2.0 * np.pi * np.outer(t_sec, self.mode_freqs_hz * tempo) + phase_shift
        env = np.exp(-damping * t_norm * 2.0)[:, None]
        water = np.real(np.exp(1j * phases) @ (self.mode_coeffs * m_weights)) * env * amp_scale

        out = self.ice_base[None, :] + water
        if len(self.knot_times) > 0:
            sigma = 0.055
            for kt, kimp in zip(self.knot_times, self.knot_impulses):
                kt_scaled = (kt / tempo) % 1.0
                g = np.exp(-0.5 * ((t_norm - kt_scaled) / sigma) ** 2)[:, None]
                out += g * kimp[None, :] * h_order * amp_scale
        return out

    def transfer_dynamics_to(
        self,
        target_domain: str,
        target_ice_base: np.ndarray,
        target_amplitude_scale: float = 1.0,
    ) -> "UniversalFormRotor":
        """
        Zero-shot cross-domain form transfer: preserves this rotor's learned temporal
        frequencies, normalized phase dynamics, and sparse event-knot timings while
        re-grounding them onto `target_domain`'s Static Ice Base!
        """
        t_ice = np.asarray(target_ice_base, dtype=np.float64).ravel()
        d_src = self.mode_coeffs.shape[1]
        d_dst = len(t_ice)
        src_norm = float(np.max(np.abs(self.mode_coeffs))) + 1e-8
        norm_coeffs = self.mode_coeffs / src_norm * float(target_amplitude_scale)
        # Project/tile cleanly across channel count mismatch
        dst_coeffs = np.zeros((len(self.mode_freqs_hz), d_dst), dtype=np.complex128)
        for j in range(d_dst):
            dst_coeffs[:, j] = norm_coeffs[:, j % d_src]

        dst_knots = np.zeros((len(self.knot_times), d_dst), dtype=np.float64)
        if len(self.knot_times) > 0:
            k_norm = float(np.max(np.abs(self.knot_impulses))) + 1e-8
            for j in range(d_dst):
                dst_knots[:, j] = (self.knot_impulses[:, j % d_src] / k_norm) * float(target_amplitude_scale) * 0.45

        return UniversalFormRotor(
            domain=f"{self.domain}->{target_domain}",
            ice_base=t_ice,
            mode_freqs_hz=self.mode_freqs_hz.copy(),
            mode_coeffs=dst_coeffs,
            knot_times=self.knot_times.copy(),
            knot_impulses=dst_knots,
            duration_s=self.duration_s,
        )

    def reconstruction_rmse(self, reference: np.ndarray) -> float:
        ref = np.asarray(reference, dtype=np.float64)
        if ref.ndim == 1:
            ref = ref[:, None]
        rec = self.evaluate(len(ref), FormKnobVector())
        return float(np.sqrt(np.mean((ref - rec) ** 2)))

    def summary_dict(self) -> Dict[str, object]:
        return {
            "domain": self.domain,
            "dims": int(len(self.ice_base)),
            "modes_count": int(len(self.mode_freqs_hz)),
            "dominant_freqs_hz": [round(float(f), 3) for f in self.mode_freqs_hz[:4]],
            "event_knots_count": int(len(self.knot_times)),
            "event_knot_times_norm": [round(float(t), 3) for t in self.knot_times],
            "duration_s": round(float(self.duration_s), 3),
        }


# ---------------------------------------------------------------------------
# Inverse Pythagorean / Law-of-Cosines / De Gua Causal Deduction Solver
# ---------------------------------------------------------------------------


class InversePythagoreanRotorSolver:
    """
    Inverse Causal Deduction Engine grounded in Pythagorean / Law-of-Cosines /
    Clifford `Cl(3,0)` metric closure:
      - Stage 1 (Underdetermined Observation): Given ONLY a scalar resultant magnitude `c`,
        NEVER guesses a single fake cause; explicitly unfolds the Parallel-Universe
        Pythagorean Hypothesis Manifold (`a^2 + b^2 = c^2` / `a^2 + b^2 - 2ab cos(theta) = c^2`)
        along with `nullspace_dof`.
      - Stage 2 (Multi-Axis Spectral Projection): Once full vector/overlay/spectral axes
        arrive, inverse-solves exact orthogonal operator weights `w_hat` via Gram/QR
        projection, detects non-orthogonal Law-of-Cosines interference angles `theta_ij`,
        and verifies re-derivation residual (`RMSE ~ 0.0`) without peeking at hidden truths.
    """

    @staticmethod
    def unfold_pythagorean_parallel_hypotheses(
        resultant_magnitude: float,
        axis_names: Tuple[str, str] = ("Axis_A", "Axis_B"),
        n_samples: int = 5,
    ) -> Dict[str, object]:
        """Unfolds the infinite `a^2 + b^2 = c^2` causal hypothesis circle when only `c` is observed."""
        c = max(0.0, float(resultant_magnitude))
        angles = np.linspace(0.0, 0.5 * np.pi, max(3, int(n_samples)))
        hypotheses = []
        for idx, ang in enumerate(angles):
            a = c * math.cos(float(ang))
            b = c * math.sin(float(ang))
            hypotheses.append({
                "hypothesis_id": f"H{idx + 1}",
                "angle_deg": round(math.degrees(float(ang)), 1),
                axis_names[0]: round(a, 5),
                axis_names[1]: round(b, 5),
                "pythagorean_check_c": round(math.hypot(a, b), 5),
            })
        # Also compute a non-orthogonal Law-of-Cosines interference example (theta = 60 deg constructive)
        # If a = b and angle between vectors is 60 deg: c^2 = a^2 + b^2 + 2ab cos(60) = 3 a^2 -> a = c / sqrt(3)
        eq_interf = c / math.sqrt(3.0)
        return {
            "observed_resultant_c": round(c, 5),
            "nullspace_dof": 1,
            "is_uniquely_determined": False,
            "orthogonal_circle_hypotheses": hypotheses,
            "law_of_cosines_interference_example": {
                "coupling_angle_deg": 60.0,
                axis_names[0]: round(eq_interf, 5),
                axis_names[1]: round(eq_interf, 5),
                "constructive_interference_term": round(2.0 * eq_interf * eq_interf * math.cos(math.radians(60.0)), 6),
                "resultant_check_c": round(math.sqrt(2.0 * eq_interf**2 + 2.0 * eq_interf**2 * 0.5), 5),
            },
        }

    @staticmethod
    def solve_inverse_operator_chain(
        observed_delta: np.ndarray,
        basis_operators: Dict[str, np.ndarray],
    ) -> Dict[str, object]:
        """
        Given an observed result delta vector `y` and a dictionary of candidate basis
        causal operator signatures `{name: b_i}`, inverse-solves the exact weights `w_hat`
        (`sum_i w_i * b_i ~= y`), computes pairwise Law-of-Cosines coupling angles between
        active operators, and measures exact re-derivation RMSE!
        """
        y = np.asarray(observed_delta, dtype=np.float64).ravel()
        names = list(basis_operators.keys())
        cols = [np.asarray(basis_operators[nm], dtype=np.float64).ravel() for nm in names]
        B = np.stack(cols, axis=1)  # (N, M)

        # Solve least-squares inverse projection B @ w = y via SVD (exact for orthogonal & coupled bases!)
        w_hat, _res, rank, svals = np.linalg.lstsq(B, y, rcond=None)
        y_rederived = B @ w_hat
        rmse = float(np.sqrt(np.mean((y - y_rederived) ** 2)))
        y_norm = float(np.linalg.norm(y))
        rel_err = rmse / max(1e-9, float(np.sqrt(np.mean(y ** 2))))

        # Measure Law-of-Cosines pairwise coupling angles between weighted causal components
        couplings = []
        active_components = []
        for i, nm in enumerate(names):
            comp = w_hat[i] * cols[i]
            comp_norm = float(np.linalg.norm(comp))
            active_components.append((nm, comp, comp_norm))
        for i in range(len(active_components)):
            for j in range(i + 1, len(active_components)):
                na, ca, ma = active_components[i]
                nb, cb, mb = active_components[j]
                if ma < 1e-7 or mb < 1e-7:
                    continue
                cos_th = float(np.clip(np.dot(ca, cb) / (ma * mb), -1.0, 1.0))
                ang_deg = math.degrees(math.acos(cos_th))
                kind = (
                    "orthogonal_independent" if abs(cos_th) < 0.08
                    else "constructive_resonance" if cos_th > 0.0
                    else "destructive_friction"
                )
                couplings.append({
                    "pair": f"{na} <-> {nb}",
                    "angle_deg": round(ang_deg, 2),
                    "cos_theta": round(cos_th, 4),
                    "coupling_kind": kind,
                })

        # Verify De Gua / generalized Pythagorean energy identity: ||y||^2 = sum ||c_i||^2 + 2 sum_{i<j} <c_i, c_j>
        sum_sq = sum(m * m for _, _, m in active_components)
        cross_term = 0.0
        for i in range(len(active_components)):
            for j in range(i + 1, len(active_components)):
                cross_term += 2.0 * float(np.dot(active_components[i][1], active_components[j][1]))
        law_of_cosines_lhs = float(np.dot(y_rederived, y_rederived))
        law_of_cosines_rhs = sum_sq + cross_term

        return {
            "deduced_weights": {names[i]: round(float(w_hat[i]), 6) for i in range(len(names))},
            "basis_rank": int(rank),
            "nullspace_dof": int(len(names) - rank),
            "observed_norm_c": round(y_norm, 6),
            "rederivation_rmse": round(rmse, 8),
            "relative_error": round(rel_err, 8),
            "pythagorean_sum_squares": round(sum_sq, 6),
            "interference_cross_term": round(cross_term, 6),
            "law_of_cosines_closure_err": round(abs(law_of_cosines_lhs - law_of_cosines_rhs), 10),
            "pairwise_couplings": couplings,
        }

    @staticmethod
    def invert_damped_interference_wave(
        times: np.ndarray,
        signal: np.ndarray,
    ) -> Dict[str, object]:
        """
        Blindly inverts an observed 1D physical damped wave `y(t) = exp(-gamma*t) * (a*cos(w*t) + b*sin(w*t))`
        strictly from `(times, signal)` — recovering frequency `w`, damping `gamma`, orthogonal
        quadrature amplitudes `(a, b)`, resultant phasor `R = sqrt(a^2 + b^2)`, and phase `phi = atan2(-b, a)`!
        """
        t = np.asarray(times, dtype=np.float64).ravel()
        y = np.asarray(signal, dtype=np.float64).ravel()
        dt = float(t[1] - t[0]) if len(t) > 1 else 0.01

        # 1. Estimate dominant angular frequency via fine zero-padded rFFT
        n_pad = max(2048, len(y) * 16)
        spec = np.abs(np.fft.rfft(y * np.hanning(len(y)), n=n_pad))
        freqs = np.fft.rfftfreq(n_pad, d=dt)
        peak_idx = int(np.argmax(spec[1:])) + 1
        f_est = float(freqs[peak_idx])
        w_est = 2.0 * math.pi * f_est

        # 2. Estimate exponential damping rate gamma via analytic Hilbert envelope (FFT)
        Y_full = np.fft.fft(y)
        h_mask = np.zeros(len(y))
        h_mask[0] = 1.0
        if len(y) % 2 == 0:
            h_mask[1 : len(y) // 2] = 2.0
            h_mask[len(y) // 2] = 1.0
        else:
            h_mask[1 : (len(y) + 1) // 2] = 2.0
        analytic = np.fft.ifft(Y_full * h_mask)
        env = np.abs(analytic)
        # Fit log(env) = c0 - gamma * t on interior region (avoiding FFT edge taper)
        m0, m1 = max(2, len(y) // 10), min(len(y) - 2, (9 * len(y)) // 10)
        valid = env[m0:m1] > max(1e-6, 0.05 * float(np.max(env)))
        if int(np.sum(valid)) >= 4:
            t_in = t[m0:m1][valid]
            log_e = np.log(env[m0:m1][valid])
            slope, _intercept = np.polyfit(t_in, log_e, 1)
            gamma_est = float(-slope)
        else:
            gamma_est = 0.0

        # 3. Refine (w_est, gamma_est) via lightweight coordinate polish around FFT/Hilbert foothold
        def _fit_ab(w_val: float, g_val: float) -> Tuple[float, float, float]:
            e = np.exp(-g_val * t)
            B = np.stack([e * np.cos(w_val * t), e * np.sin(w_val * t)], axis=1)
            ab, _, _, _ = np.linalg.lstsq(B, y, rcond=None)
            pred = B @ ab
            return float(ab[0]), float(ab[1]), float(np.sqrt(np.mean((y - pred) ** 2)))

        best_w, best_g = w_est, gamma_est
        best_a, best_b, best_rmse = _fit_ab(best_w, best_g)
        for step_w, step_g in ((0.20, 0.12), (0.05, 0.03), (0.01, 0.006), (0.002, 0.0012), (0.0003, 0.0002), (0.00005, 0.00003)):
            for _ in range(8):
                improved = False
                for dw in (-step_w, 0.0, step_w):
                    for dg in (-step_g, 0.0, step_g):
                        if dw == 0.0 and dg == 0.0:
                            continue
                        a_c, b_c, r_c = _fit_ab(best_w + dw, best_g + dg)
                        if r_c < best_rmse:
                            best_w, best_g, best_a, best_b, best_rmse = best_w + dw, best_g + dg, a_c, b_c, r_c
                            improved = True
                if not improved:
                    break

        R_phasor = math.hypot(best_a, best_b)
        phi_rad = math.atan2(-best_b, best_a)
        return {
            "deduced_freq_hz": round(best_w / (2.0 * math.pi), 5),
            "deduced_omega_rad_s": round(best_w, 5),
            "deduced_damping_gamma": round(best_g, 5),
            "orthogonal_cos_amp_a": round(best_a, 5),
            "orthogonal_sin_amp_b": round(best_b, 5),
            "pythagorean_resultant_R": round(R_phasor, 5),
            "phase_rad": round(phi_rad, 5),
            "phase_deg": round(math.degrees(phi_rad), 2),
            "rederivation_rmse": round(best_rmse, 7),
        }
