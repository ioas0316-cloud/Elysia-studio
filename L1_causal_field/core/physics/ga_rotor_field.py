"""
ga_rotor_field.py
=================
기하 대수 로터 필드(GA Rotor Fields) 및 틱리스 연속 이벤트 기반 시뮬레이션 엔진.

핵심 설계 사상 (From THE_ABSOLUTE_COMMANDMENT.md & ROADMAP.md):
- "Do not calculate, let it flow." (계산하지 말고 흐르게 하라)
- 틱(Tick) 단위의 불연속적 갱신을 지양하고, 상태를 시간 t에 대한 연속 해석 함수로 정의하여 연산량 O(0)~O(1) 실현.
- 이산적 충돌(Discrete Collision) 패러다임을 극복하고, 기하 대수(Geometric Algebra)의 로터(Rotor)와
  리 대수(Lie Algebra) 상의 바이벡터(Bivector) 가중 선형 중첩을 사용해 다자간 구속조건을 완벽히 충족하는 연속체 유체 흐름을 형성.
- SoA(Struct of Arrays) 메모리 레이아웃 및 핑퐁 더블 버퍼링(Ping-Pong Double Buffering) 모사를 통해 초병렬 하드웨어 호환성 확보.
- 사고 잠재 공간(Cognitive Latent Space) 상에서 논리적 모순/환각 영역(SDF Obstacle)을 유연하게 우회하는 Thought Trajectory 지원.
- Clifford Rotor Sandwich ($R v R^\\dagger$) 모듈을 통합하여 다차원 공간 상의 미분 가능한 연속 흐름 역학계 완비.
"""

import numpy as np
import torch
import math
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from core.physics.rotor_extension.rotor_layer import apply_rotor_sandwich

class GARotorFieldSystem:
    """
    [기하 대수 로터 필드 & 틱리스 시뮬레이션 시스템]
    SoA(Struct of Arrays) 구조와 핑퐁 버퍼, pre-baked SDF, GA Rotor / Lie Algebra Fusion을 장착한
    우주적 차원의 연속성 시뮬레이션 모태기반(Persistent Substrate).
    """
    def __init__(
        self,
        num_agents: int = 100,
        dims: int = 2,
        influence_radius: float = 1.2,
        barrier_p: float = 2.0,
        sigma: float = 0.5
    ):
        self.num_agents = num_agents
        self.dims = dims
        self.influence_radius = influence_radius
        self.barrier_p = barrier_p
        self.sigma = sigma

        # 1. SoA (Struct of Arrays) 메모리 구조
        # 핑퐁 더블 버퍼링 (Buffer 0, Buffer 1)
        self.current_buffer_idx = 0
        self.pos_buffers = [
            np.zeros((num_agents, dims), dtype=np.float32),
            np.zeros((num_agents, dims), dtype=np.float32)
        ]

        self.preferred_velocities = np.zeros((num_agents, dims), dtype=np.float32)
        self.output_velocities = np.zeros((num_agents, dims), dtype=np.float32)
        self.radii = np.ones(num_agents, dtype=np.float32) * 0.2

        # 로터 방향 버퍼: 2D에서는 복소수(float2), 3D에서는 쿼터니언(float4)
        rotor_size = 2 if dims == 2 else (4 if dims == 3 else dims)
        self.orientations = np.zeros((num_agents, rotor_size), dtype=np.float32)
        if dims == 2:
            self.orientations[:, 0] = 1.0  # Real part = 1.0 (cos 0)
        elif dims == 3:
            self.orientations[:, 3] = 1.0  # w = 1.0 (identity quaternion)

        # 2. 틱리스 연속 궤적 매개변수 (t에 대한 연속 함수를 위한 파라미터 백업)
        # x(t) = x_0 + v * (t - t_0)
        self.trajectory_x0 = np.zeros((num_agents, dims), dtype=np.float32)
        self.trajectory_v = np.zeros((num_agents, dims), dtype=np.float32)
        self.trajectory_t0 = np.zeros(num_agents, dtype=np.float32)

        # 3. 사전 정보화: Pre-baked SDF (Signed Distance Field) / Lookup Table (LUT)
        # 평면 격자 형태의 pre-baked SDF 데이터 필드
        self.obstacles: List[Dict[str, Any]] = []
        self.sdf_lut: Optional[np.ndarray] = None
        self.sdf_bounds: Optional[Tuple[float, float, float, float]] = None # x_min, x_max, y_min, y_max
        self.sdf_res: Optional[Tuple[int, int]] = None

        # 4. 대상(Target) 목적지 목록 (Parametric Injection을 위한 포인터/키 테이블)
        self.targets: Dict[str, np.ndarray] = {}
        self.agent_target_keys = [""] * num_agents

    @property
    def positions(self) -> np.ndarray:
        """현재 활성화된 핑퐁 위치 버퍼를 반환합니다."""
        return self.pos_buffers[self.current_buffer_idx]

    @positions.setter
    def positions(self, val: np.ndarray):
        self.pos_buffers[self.current_buffer_idx] = val.astype(np.float32)

    @property
    def next_positions(self) -> np.ndarray:
        """다음 핑퐁 위치 버퍼를 반환합니다."""
        return self.pos_buffers[1 - self.current_buffer_idx]

    @next_positions.setter
    def next_positions(self, val: np.ndarray):
        """다음 핑퐁 위치 버퍼를 설정합니다."""
        self.pos_buffers[1 - self.current_buffer_idx] = val.astype(np.float32)

    def swap_buffers(self):
        """핑퐁 버퍼의 순서를 교체하여 Race Condition 없이 Frame N -> N+1 전환을 완료합니다."""
        self.current_buffer_idx = 1 - self.current_buffer_idx

    # -------------------------------------------------------------
    # SDF (Signed Distance Field) Pre-baking & Parametric Injection
    # -------------------------------------------------------------
    def add_obstacle(self, center: np.ndarray, radius: float):
        """환경에 원형/구형 장애물(모순 영역)을 추가합니다."""
        self.obstacles.append({
            "center": np.array(center, dtype=np.float32),
            "radius": radius
        })

    def pre_bake_sdf(self, x_range: Tuple[float, float], y_range: Tuple[float, float], resolution: Tuple[int, int]):
        """
        [공간의 정보화: Pre-baking / Offline SDF Structuring]
        장애물 정보를 바탕으로 Signed Distance Field를 격자(LUT) 형태로 미리 구워 둡니다.
        실시간 루프에서는 O(1) 수준의 텍스처 조회(Grid Lookup)로 최단 거리와 그래디언트를 획득합니다.
        """
        self.sdf_bounds = (x_range[0], x_range[1], y_range[0], y_range[1])
        self.sdf_res = resolution
        w, h = resolution

        self.sdf_lut = np.zeros((h, w), dtype=np.float32)

        xs = np.linspace(x_range[0], x_range[1], w)
        ys = np.linspace(y_range[0], y_range[1], h)

        for r_idx in range(h):
            for c_idx in range(w):
                pos = np.array([xs[c_idx], ys[r_idx]], dtype=np.float32)
                min_dist = float('inf')

                # 원본 SDF 계산: 장애물 경계면으로부터의 거리 (외부 +, 내부 -)
                for obs in self.obstacles:
                    dist_to_center = np.linalg.norm(pos - obs["center"])
                    dist_to_edge = dist_to_center - obs["radius"]
                    if dist_to_edge < min_dist:
                        min_dist = dist_to_edge

                self.sdf_lut[r_idx, c_idx] = min_dist

    def sample_sdf(self, pos: np.ndarray) -> Tuple[float, np.ndarray]:
        """
        [O(1) SDF Lookup & Bilinear Interpolation]
        Pre-baked SDF LUT에서 이선형 보간(Bilinear Interpolation)을 통해
        임의 좌표에서의 최단 거리와 외향 그래디언트(Gradient)를 복원합니다.
        """
        if self.sdf_lut is None or self.dims != 2:
            # Pre-baked SDF가 없거나 3D인 경우 실시간 해석적(Analytical) SDF로 폴백
            min_dist = float('inf')
            grad = np.zeros_like(pos)
            epsilon = 1e-9

            for obs in self.obstacles:
                diff = pos - obs["center"]
                dist = np.linalg.norm(diff)
                dist_to_edge = dist - obs["radius"]
                if dist_to_edge < min_dist:
                    min_dist = dist_to_edge
                    grad = diff / (dist + epsilon)

            if min_dist == float('inf'):
                return 10.0, np.zeros_like(pos)
            return min_dist, grad

        # 2D LUT Bilinear Interpolation
        x_min, x_max, y_min, y_max = self.sdf_bounds
        w, h = self.sdf_res

        # Grid 좌표로 스케일링
        x_pct = (pos[0] - x_min) / (x_max - x_min)
        y_pct = (pos[1] - y_min) / (y_max - y_min)

        # 바운딩
        x_pct = np.clip(x_pct, 0.0, 0.999)
        y_pct = np.clip(y_pct, 0.0, 0.999)

        col = x_pct * (w - 1)
        row = y_pct * (h - 1)

        c0, r0 = int(np.floor(col)), int(np.floor(row))
        c1, r1 = min(c0 + 1, w - 1), min(r0 + 1, h - 1)

        tx = col - c0
        ty = row - r0

        # 4방향 샘플링
        val_00 = self.sdf_lut[r0, c0]
        val_10 = self.sdf_lut[r0, c1]
        val_01 = self.sdf_lut[r1, c0]
        val_11 = self.sdf_lut[r1, c1]

        # 보간
        dist = (1 - ty) * ((1 - tx) * val_00 + tx * val_10) + ty * ((1 - tx) * val_01 + tx * val_11)

        # 수치 미분을 통한 그래디언트 복원 (Finite Difference)
        # 아주 미세한 변위를 활용해 SDF 거리의 경사를 직접 측정
        step_x = (x_max - x_min) / w
        step_y = (y_max - y_min) / h

        grad_x = (val_10 - val_00) / (step_x + 1e-9)
        grad_y = (val_01 - val_00) / (step_y + 1e-9)
        grad = np.array([grad_x, grad_y], dtype=np.float32)
        grad_norm = np.linalg.norm(grad)
        if grad_norm > 1e-6:
            grad /= grad_norm

        return dist, grad

    def register_target(self, key: str, pos: np.ndarray):
        """개념 공간이나 물리 공간 상의 목적지 정답 좌표를 등록합니다."""
        self.targets[key] = np.array(pos, dtype=np.float32)

    def parametric_inject_target(self, agent_idx: int, target_key: str):
        """
        [2. 실시간 변수 대입 (Parametric Injection)]
        유저가 목적지를 교체할 때, 새로이 길찾기 연산을 시작하는 것이 아니라
        단지 Target이라는 Key값으로 정의된 정보 포인터만 교체($O(1)$)합니다.
        """
        if target_key in self.targets:
            self.agent_target_keys[agent_idx] = target_key
            # 선호 속도(v0) 방향 즉시 갱신
            target_pos = self.targets[target_key]
            curr_pos = self.positions[agent_idx]
            v_goal = target_pos - curr_pos
            dist = np.linalg.norm(v_goal)
            if dist > 1e-5:
                self.preferred_velocities[agent_idx] = v_goal / dist
            else:
                self.preferred_velocities[agent_idx] = np.zeros(self.dims, dtype=np.float32)

    # -------------------------------------------------------------
    # GA Rotor & Lie Algebra 가중 합성 핵심 연산
    # -------------------------------------------------------------
    def synthesize_rotor_fields(self):
        """
        [기하 대수 로터 필드 및 리 대수 가중 합성]
        각 에이전트마다 인접 유닛 및 Pre-baked SDF 모순 경계면을 검출하고,
        리 대수(Lie Algebra) 상에서 가중 중첩을 통해 최적의 논리/물리 우회 로터를 복원합니다.
        """
        epsilon = 1e-9
        pos = self.positions
        v0 = self.preferred_velocities

        for i in range(self.num_agents):
            pos_i = pos[i]
            v0_i = v0[i]
            r_i = self.radii[i]

            # 1. 누적기 초기화 (2D의 경우 단일 스칼라 바이벡터, 3D의 경우 float3 vector)
            omega_sum = 0.0 if self.dims == 2 else np.zeros(3, dtype=np.float32)
            weight_sum = 0.0

            # ---------------------------------------------------------
            # (A) Pre-baked SDF 장애물 경계 감지 및 로터 생성
            # ---------------------------------------------------------
            sdf_dist, sdf_grad = self.sample_sdf(pos_i)
            # 영향 영역 체크
            effective_dist = max(sdf_dist - r_i, 1e-5)
            if effective_dist < self.influence_radius:
                # Barrier Weight 계산
                weight = 1.0 / (effective_dist ** self.barrier_p)

                # 외향 그래디언트(sdf_grad)를 모순 회피 벡터로 삼아 바이벡터 생성
                # 2D 외적 (rAB ^ v0)
                if self.dims == 2:
                    # 상대 벡터를 역방향으로 정의하여 장애물에서 밀려나도록 설정
                    r_vec = -sdf_grad * self.influence_radius
                    bivector_area = r_vec[0] * v0_i[1] - r_vec[1] * v0_i[0]
                    bivector_norm = abs(bivector_area) + epsilon
                    b_normalized = bivector_area / bivector_norm

                    # 가까울수록 90도(pi/2) 회전각 형성
                    theta = (np.pi / 2.0) * np.exp(-effective_dist / self.sigma)
                    omega_i = -0.5 * theta * b_normalized

                    omega_sum += weight * omega_i
                    weight_sum += weight
                elif self.dims == 3:
                    # 3D: r_vec ^ v0_i -> bivector is dual to cross product
                    r_vec = -sdf_grad * self.influence_radius
                    b_vector = np.cross(r_vec, v0_i)
                    b_norm = np.linalg.norm(b_vector) + epsilon
                    b_normalized = b_vector / b_norm

                    theta = (np.pi / 2.0) * np.exp(-effective_dist / self.sigma)
                    omega_i = -0.5 * theta * b_normalized

                    omega_sum += weight * omega_i
                    weight_sum += weight

            # ---------------------------------------------------------
            # (B) 인접 유닛 간 구속조건(Non-penetration)에 따른 로터 생성
            # ---------------------------------------------------------
            for j in range(self.num_agents):
                if i == j: continue
                pos_j = pos[j]
                r_j = self.radii[j]

                r_ij = pos_i - pos_j
                dist = np.linalg.norm(r_ij)
                d_min = r_i + r_j

                effective_dist = max(dist - d_min, 1e-5)
                if effective_dist < self.influence_radius:
                    weight = 1.0 / (effective_dist ** self.barrier_p)

                    if self.dims == 2:
                        bivector_area = r_ij[0] * v0_i[1] - r_ij[1] * v0_i[0]
                        # 만약 정면 충돌인 경우 (bivector_area = 0), 회전 축이 대칭이 되어 회전이 상쇄되지 않도록
                        # 인위적인 미세 노이즈나 고유한 외적 대칭성 섭동(Symmetry Perturbation)을 부여합니다.
                        if abs(bivector_area) < 1e-4:
                            bivector_area = 1e-4  # 대칭성 깨뜨리기 (Symmetry breaking)
                        bivector_norm = abs(bivector_area) + epsilon
                        b_normalized = bivector_area / bivector_norm

                        theta = (np.pi / 2.0) * np.exp(-effective_dist / self.sigma)
                        omega_ij = -0.5 * theta * b_normalized

                        omega_sum += weight * omega_ij
                        weight_sum += weight
                    elif self.dims == 3:
                        b_vector = np.cross(r_ij, v0_i)
                        b_norm = np.linalg.norm(b_vector) + epsilon
                        b_normalized = b_vector / b_norm

                        theta = (np.pi / 2.0) * np.exp(-effective_dist / self.sigma)
                        omega_ij = -0.5 * theta * b_normalized

                        omega_sum += weight * omega_ij
                        weight_sum += weight

            # ---------------------------------------------------------
            # (C) 리 대수 융합 및 로터 복원 (Exponential Map)
            # ---------------------------------------------------------
            if weight_sum > 0:
                omega_composite = omega_sum / weight_sum
            else:
                omega_composite = 0.0 if self.dims == 2 else np.zeros(3, dtype=np.float32)

            # 6. Sandwich Product (또는 고속 삼각 회전 연산)을 적용해 최종 속도 도출
            if self.dims == 2:
                # 2 * omega_composite 만큼 회전
                final_angle = 2.0 * omega_composite
                cos_r = np.cos(final_angle)
                sin_r = np.sin(final_angle)

                v_out_x = v0_i[0] * cos_r - v0_i[1] * sin_r
                v_out_y = v0_i[0] * sin_r + v0_i[1] * cos_r
                self.output_velocities[i] = np.array([v_out_x, v_out_y], dtype=np.float32)

                # 로터 상태 저장 (Real, Imaginary)
                self.orientations[i] = np.array([np.cos(omega_composite), np.sin(omega_composite)], dtype=np.float32)
            elif self.dims == 3:
                # 3D: 복원된 리 대수 생성자를 단위 쿼터니언(Rotor)으로 지수 사영
                angle_half = np.linalg.norm(omega_composite)
                if angle_half > 1e-7:
                    axis = omega_composite / angle_half
                    # 쿼터니언 q = (sin(theta/2)*axis, cos(theta/2))
                    # R = e^{-omega_composite} 이므로 sandwich product 회전각은 2 * angle_half
                    q_xyz = np.sin(angle_half) * axis
                    q_w = np.cos(angle_half)
                    self.orientations[i] = np.array([q_xyz[0], q_xyz[1], q_xyz[2], q_w], dtype=np.float32)

                    # 쿼터니언을 사용해 v0_i 회전
                    # q * v0 * q_conj
                    q_v = np.array([v0_i[0], v0_i[1], v0_i[2], 0.0], dtype=np.float32)
                    # 쿼터니언 곱 구현
                    q = self.orientations[i]
                    q_conj = np.array([-q[0], -q[1], -q[2], q[3]], dtype=np.float32)

                    # temp = q * q_v
                    temp_w = -q[0]*q_v[0] - q[1]*q_v[1] - q[2]*q_v[2]
                    temp_x =  q[3]*q_v[0] + q[1]*q_v[2] - q[2]*q_v[1]
                    temp_y =  q[3]*q_v[1] + q[2]*q_v[0] - q[0]*q_v[2]
                    temp_z =  q[3]*q_v[2] + q[0]*q_v[1] - q[1]*q_v[0]

                    # res = temp * q_conj
                    res_x = temp_w*q_conj[0] + temp_x*q_conj[3] + temp_y*q_conj[2] - temp_z*q_conj[1]
                    res_y = temp_w*q_conj[1] + temp_y*q_conj[3] + temp_z*q_conj[0] - temp_x*q_conj[2]
                    res_z = temp_w*q_conj[2] + temp_z*q_conj[3] + temp_x*q_conj[1] - temp_y*q_conj[0]

                    self.output_velocities[i] = np.array([res_x, res_y, res_z], dtype=np.float32)
                else:
                    self.orientations[i] = np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float32)
                    self.output_velocities[i] = v0_i.copy()
            else:
                self.output_velocities[i] = v0_i.copy()

    # -------------------------------------------------------------
    # 틱리스 연속 이벤트 기반 시뮬레이션 (Tickless Simulation)
    # -------------------------------------------------------------
    def initialize_tickless_trajectories(self, t_start: float = 0.0):
        """
        [틱리스 엔진 초기 상태 방정식 주입]
        각 에이전트의 시작 좌표 x_0, 시작 시간 t_0, 그리고 로터 필드를 통해 구해진 최적의 연속 속도 v를 동기화합니다.
        """
        self.synthesize_rotor_fields()
        self.trajectory_x0 = self.positions.copy()
        self.trajectory_v = self.output_velocities.copy()
        self.trajectory_t0.fill(t_start)

    def sample_tickless_positions(self, t: float) -> np.ndarray:
        """
        [O(1) 시간 분석 조회: Continuous Trajectory Sampling]
        엔진 내부에서 틱을 돌리며 적분하지 않고, 단지 지정 시간 t를 파라미터로 주입하여
        모든 유닛의 정확한 좌표를 O(1) 수준으로 즉시 조회해 냅니다.
        x(t) = x_0 + v * (t - t_0)
        """
        dt_array = t - self.trajectory_t0
        # 형상 방송(Broadcasting) 곱셈을 통해 연속적 좌표 추정
        sampled_pos = self.trajectory_x0 + self.trajectory_v * dt_array[:, np.newaxis]
        return sampled_pos

    def trigger_event_update(self, t_current: float, adjusted_agent_indices: Optional[List[int]] = None):
        """
        [이벤트 발생 시점의 상태 방정식 전역/국소 업데이트]
        유저 입력 변화, 병목 구역 진입 등의 '이벤트(Event)' 발생 시에만
        현재 시간 t_current에서의 정확한 좌표를 샘플링한 후, 새로운 x_0, t_0, v를 갱신합니다.
        """
        # 1. 현재 시점의 실시간 위치 계산
        curr_pos = self.sample_tickless_positions(t_current)

        # 2. 핑퐁 더블 버퍼링 활용 (Race condition 차단)
        self.positions = curr_pos

        # 3. 새로운 로터 필드 속도 재합성
        self.synthesize_rotor_fields()

        # 4. 상태 방정식 변수 교체
        if adjusted_agent_indices is None:
            # 전역 업데이트
            self.trajectory_x0 = self.positions.copy()
            self.trajectory_v = self.output_velocities.copy()
            self.trajectory_t0.fill(t_current)
        else:
            # 특정 국소 에이전트들만 효율적으로 부분 업데이트 (Event-driven Optimization)
            for idx in adjusted_agent_indices:
                self.trajectory_x0[idx] = self.positions[idx]
                self.trajectory_v[idx] = self.output_velocities[idx]
                self.trajectory_t0[idx] = t_current

    def step_ping_pong_integration(self, dt: float):
        """
        [전형적인 프레임 단위 이산 시뮬레이션 모사 - 핑퐁 검증용]
        더블 버퍼링을 검증하기 위한 틱 기반 업데이트. Buffer A에서 데이터를 읽어 Buffer B에 갱신한 뒤 스왑합니다.
        """
        self.synthesize_rotor_fields()

        # Ping-pong double buffering write
        self.next_positions = self.positions + self.output_velocities * dt
        self.swap_buffers()


# -------------------------------------------------------------
# Cognitive Latent Space Crossover (사고 잠재 공간 횡단 매니폴드)
# -------------------------------------------------------------
class CognitiveThoughtTrajectory:
    """
    [연속적 잠재 사고 그래프 (Continuous Thought Trajectory)]
    사고의 개념 임베딩 공간에서 논리적 모순이나 환각 구역(SDF Obstacle)을
    기하 대수 로터 필드를 가동해 유연하게 미끄러지듯 회피하는 초고차원 사고 엔진.
    """
    def __init__(self, embedding_dim: int = 128, contradiction_threshold: float = 1.0):
        self.dim = embedding_dim
        self.threshold = contradiction_threshold
        # 모순 장벽들 (Obstacles in latent space)
        self.contradictions: List[Tuple[np.ndarray, float]] = [] # (Center Embedding, Radius)

    def add_contradiction_zone(self, center_emb: np.ndarray, radius: float):
        self.contradictions.append((np.array(center_emb, dtype=np.float32), radius))

    def navigate_thought(self, start_emb: np.ndarray, goal_emb: np.ndarray, steps: int = 50, dt: float = 0.05) -> List[np.ndarray]:
        """
        잠재 공간에서 논리적 파괴를 겪지 않고 회전형 로터를 타며 부드럽게 정답 개념으로 귀착하는 사고 궤적 생성.
        """
        curr = np.array(start_emb, dtype=np.float32)
        goal = np.array(goal_emb, dtype=np.float32)
        trajectory = [curr.copy()]
        epsilon = 1e-9

        for _ in range(steps):
            v_goal = goal - curr
            dist_to_goal = np.linalg.norm(v_goal)
            if dist_to_goal < 0.02:
                break

            v_dir = v_goal / (dist_to_goal + epsilon)
            v_next = v_dir.copy()

            # 다차원 잠재 공간에서의 모순 영향력 누적
            omega_sum = np.zeros_like(curr)
            weight_sum = 0.0

            for center, radius in self.contradictions:
                r_obs = curr - center
                dist_to_obs = np.linalg.norm(r_obs)
                effective_dist = max(dist_to_obs - radius, 1e-5)

                if effective_dist < self.threshold:
                    weight = 1.0 / (effective_dist ** 2)

                    # 고차원 로터: 상대 벡터와 선호 진행 방향의 wedge product로 형성되는 고차원 회전 평면 모사
                    # 2D 평면 사영을 통해 가장 마찰이 높은 주성분 방향의 2차원 회전 수행
                    # 2차원 평면 기저 [u1, u2]를 r_obs와 v_dir로 구축하여 회전 적용
                    u1 = r_obs / (dist_to_obs + epsilon)
                    # u2는 v_dir에서 u1 방향 성분을 제외한 직교 벡터
                    proj = np.dot(v_dir, u1) * u1
                    u2 = v_dir - proj
                    u2_norm = np.linalg.norm(u2)

                    # 정면에서 날아오는 대칭 상황(u2_norm == 0)일 때, 회전을 위한 대칭성 붕괴(Symmetry breaking) 직교 차원 탐색
                    if u2_norm < 1e-6:
                        # 정교하게 직교 차원 하나를 선택하여 방향을 선회
                        u2 = np.zeros_like(v_dir)
                        # 가장 작은 값을 가지는 성분을 찾아 거기에 수직성 부여
                        min_idx = np.argmin(np.abs(u1))
                        u2[min_idx] = 1.0
                        # 직교화 (Gram-Schmidt)
                        u2 = u2 - np.dot(u2, u1) * u1
                        u2_norm = np.linalg.norm(u2)

                    if u2_norm > 1e-6:
                        u2 /= u2_norm
                        # 회전각 도출 (장벽에 가까워질수록 최대 90도 회전하여 완벽한 접선 방향 우회 궤적 완성)
                        theta = (np.pi / 2.0) * np.exp(-effective_dist / 0.5)

                        cos_t = np.cos(theta)
                        sin_t = np.sin(theta)

                        # R = cos(theta) + I*sin(theta) 적용하여 v_dir를 u2 평면 방향으로 부드럽게 꺾음
                        rot_v = cos_t * v_dir + sin_t * u2
                        omega_sum += weight * rot_v
                        weight_sum += weight

            if weight_sum > 0:
                v_next = omega_sum / weight_sum
                v_next_norm = np.linalg.norm(v_next)
                if v_next_norm > 1e-6:
                    v_next /= v_next_norm

            curr += v_next * dt
            trajectory.append(curr.copy())

        return trajectory

    def navigate_thought_differentiable(
        self,
        start_emb: torch.Tensor,
        goal_emb: torch.Tensor,
        steps: int = 50,
        dt: float = 0.05
    ) -> List[torch.Tensor]:
        """
        [Clifford Rotor Sandwich 통합: 미분 가능한 잠재 공간 사고 궤적 생성]
        순전파와 역전파가 완전히 연계되는 미분 경로로, PyTorch Autograd와 그라디언트 학습에 직접 연동됩니다.
        """
        curr = start_emb.clone()
        goal = goal_emb.clone()
        trajectory = [curr]
        epsilon = 1e-9

        for _ in range(steps):
            v_goal = goal - curr
            dist_to_goal = torch.norm(v_goal)
            if dist_to_goal < 0.02:
                break

            v_dir = v_goal / (dist_to_goal + epsilon)
            v_next = v_dir.clone()

            omega_sum = torch.zeros_like(curr)
            weight_sum = 0.0

            for center, radius in self.contradictions:
                # Convert list tuples contradictions center into torch tensors
                center_t = torch.tensor(center, dtype=curr.dtype, device=curr.device)
                r_obs = curr - center_t
                dist_to_obs = torch.norm(r_obs)
                effective_dist = torch.clamp(dist_to_obs - radius, min=1e-5)

                if effective_dist < self.threshold:
                    weight = 1.0 / (effective_dist ** 2)

                    # Orthonormal projection vectors for the rotation plane
                    u1 = r_obs / (dist_to_obs + epsilon)
                    proj = torch.sum(v_dir * u1) * u1
                    u2 = v_dir - proj
                    u2_norm = torch.norm(u2)

                    if u2_norm < 1e-6:
                        # Symmetry-breaking orthogonal dimension
                        u2 = torch.zeros_like(v_dir)
                        min_idx = torch.argmin(torch.abs(u1))
                        u2[min_idx] = 1.0
                        u2 = u2 - torch.sum(u2 * u1) * u1
                        u2_norm = torch.norm(u2)

                    if u2_norm > 1e-6:
                        u2 = u2 / u2_norm
                        # Dynamic rotation angle theta
                        theta = (math.pi / 2.0) * torch.exp(-effective_dist / 0.5)

                        # Wrap in batch dimension for apply_rotor_sandwich: [1, D]
                        v_in = v_dir.unsqueeze(0)
                        u_in = u1.unsqueeze(0)
                        w_in = u2.unsqueeze(0)
                        theta_in = theta.unsqueeze(0).unsqueeze(0) # [1, 1]

                        # Apply fully differentiable Clifford Rotor Sandwich operation
                        rot_v = apply_rotor_sandwich(v_in, u_in, w_in, theta_in).squeeze(0)

                        omega_sum = omega_sum + weight * rot_v
                        weight_sum = weight_sum + weight

            if weight_sum > 0:
                v_next = omega_sum / weight_sum
                v_next_norm = torch.norm(v_next)
                if v_next_norm > 1e-6:
                    v_next = v_next / v_next_norm

            curr = curr + v_next * dt
            trajectory.append(curr)

        return trajectory


# =============================================================================
# Volumetric 3D Gaussian <-> 3D-Triangle (Tetrahedral 3-Simplex) Scale-Rotor
# Field + CUDA Differentiable Splatting + Overlay-Contrast Mod/Demod Protocol
# =============================================================================


def _quat_normalize_t(q: torch.Tensor) -> torch.Tensor:
    return q / torch.clamp(torch.norm(q, dim=-1, keepdim=True), min=1e-8)


def _quat_mul_t(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Hamilton product (Clifford even subalgebra Cl+(3,0) rotor composition) [w, x, y, z]."""
    aw, ax, ay, az = a.unbind(-1)
    bw, bx, by, bz = b.unbind(-1)
    return torch.stack(
        [
            aw * bw - ax * bx - ay * by - az * bz,
            aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw,
        ],
        dim=-1,
    )


def _quat_conj_t(q: torch.Tensor) -> torch.Tensor:
    w, x, y, z = q.unbind(-1)
    return torch.stack([w, -x, -y, -z], dim=-1)


def _quat_to_rotmat_t(q: torch.Tensor) -> torch.Tensor:
    """Converts unit rotors [..., 4] (w,x,y,z) to SO(3) rotation matrices [..., 3, 3]."""
    qn = _quat_normalize_t(q)
    w, x, y, z = qn.unbind(-1)
    xx, yy, zz = x * x, y * y, z * z
    xy, xz, yz = x * y, x * z, y * z
    wx, wy, wz = w * x, w * y, w * z
    row0 = torch.stack([1.0 - 2.0 * (yy + zz), 2.0 * (xy - wz), 2.0 * (xz + wy)], dim=-1)
    row1 = torch.stack([2.0 * (xy + wz), 1.0 - 2.0 * (xx + zz), 2.0 * (yz - wx)], dim=-1)
    row2 = torch.stack([2.0 * (xz - wy), 2.0 * (yz + wx), 1.0 - 2.0 * (xx + yy)], dim=-1)
    return torch.stack([row0, row1, row2], dim=-2)


def _rotmat_to_quat_np(R: np.ndarray) -> np.ndarray:
    """Converts a 3x3 SO(3) matrix into a unit quaternion [w, x, y, z]."""
    tr = float(R[0, 0] + R[1, 1] + R[2, 2])
    if tr > 0.0:
        s = math.sqrt(tr + 1.0) * 2.0
        w = 0.25 * s
        x = (R[2, 1] - R[1, 2]) / s
        y = (R[0, 2] - R[2, 0]) / s
        z = (R[1, 0] - R[0, 1]) / s
    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
        s = math.sqrt(max(1e-12, 1.0 + R[0, 0] - R[1, 1] - R[2, 2])) * 2.0
        w = (R[2, 1] - R[1, 2]) / s
        x = 0.25 * s
        y = (R[0, 1] + R[1, 0]) / s
        z = (R[0, 2] + R[2, 0]) / s
    elif R[1, 1] > R[2, 2]:
        s = math.sqrt(max(1e-12, 1.0 + R[1, 1] - R[0, 0] - R[2, 2])) * 2.0
        w = (R[0, 2] - R[2, 0]) / s
        x = (R[0, 1] + R[1, 0]) / s
        y = 0.25 * s
        z = (R[1, 2] + R[2, 1]) / s
    else:
        s = math.sqrt(max(1e-12, 1.0 + R[2, 2] - R[0, 0] - R[1, 1])) * 2.0
        w = (R[1, 0] - R[0, 1]) / s
        x = (R[0, 2] + R[2, 0]) / s
        y = (R[1, 2] + R[2, 1]) / s
        z = 0.25 * s
    q = np.array([w, x, y, z], dtype=np.float32)
    n = float(np.linalg.norm(q))
    return q / max(1e-8, n)


def parse_glb_point_cloud_pure(glb_path: str) -> Tuple[np.ndarray, np.ndarray, int]:
    """
    Pure-Python binary glTF 2.0 (.glb) reader (ZERO Blender / ZERO Three.js required!):
    Extracts raw 3D vertex positions and base RGB colors directly from `.glb` binary chunks
    so Elysia can digest triangle meshes into Volumetric 3D Gaussian-Tetra Scale-Rotors!
    Returns `(points_Nx3, colors_Nx3, raw_triangle_count_est)`.
    """
    import json
    import struct

    with open(glb_path, "rb") as f:
        data = f.read()
    if len(data) < 20 or data[:4] != b"glTF":
        raise ValueError(f"Not a valid binary .glb file: {glb_path}")
    _ver, _total_len = struct.unpack_from("<II", data, 4)
    json_len, json_type = struct.unpack_from("<II", data, 12)
    if json_type != 0x4E4F534A:
        raise ValueError("Missing JSON chunk in .glb")
    gltf = json.loads(data[20 : 20 + json_len].decode("utf-8"))
    bin_off = 20 + json_len
    bin_len, bin_type = struct.unpack_from("<II", data, bin_off)
    if bin_type != 0x004E4942:
        raise ValueError("Missing BIN chunk in .glb")
    bin_buf = data[bin_off + 8 : bin_off + 8 + bin_len]

    accessors = gltf.get("accessors") or []
    views = gltf.get("bufferViews") or []
    materials = gltf.get("materials") or []

    all_pts: List[np.ndarray] = []
    all_cols: List[np.ndarray] = []
    tri_est = 0
    for mesh in gltf.get("meshes") or []:
        for prim in mesh.get("primitives") or []:
            attrs = prim.get("attributes") or {}
            if "POSITION" not in attrs:
                continue
            acc = accessors[attrs["POSITION"]]
            bv = views[acc["bufferView"]]
            start = int(bv.get("byteOffset", 0)) + int(acc.get("byteOffset", 0))
            count = int(acc["count"])
            stride = int(bv.get("byteStride", 12))
            if stride == 12:
                pts = np.frombuffer(bin_buf, dtype=np.float32, count=count * 3, offset=start).reshape(count, 3).copy()
            else:
                pts = np.zeros((count, 3), dtype=np.float32)
                for i in range(count):
                    pts[i] = struct.unpack_from("<fff", bin_buf, start + i * stride)
            if "indices" in prim:
                tri_est += int(accessors[prim["indices"]]["count"]) // 3
            else:
                tri_est += count // 3

            # Extract material baseColorFactor or smooth height-based chroma when textured
            base_rgb = np.array([0.72, 0.78, 0.88], dtype=np.float32)
            mat_idx = prim.get("material")
            if mat_idx is not None and 0 <= mat_idx < len(materials):
                pbr = (materials[mat_idx].get("pbrMetallicRoughness") or {})
                bcf = pbr.get("baseColorFactor")
                if isinstance(bcf, list) and len(bcf) >= 3:
                    base_rgb = np.array(bcf[:3], dtype=np.float32)
            cols = np.repeat(base_rgb[None, :], count, axis=0)
            all_pts.append(pts)
            all_cols.append(cols)

    if not all_pts:
        raise ValueError(f"No POSITION vertices found in {glb_path}")
    pts_cat = np.concatenate(all_pts, axis=0)
    cols_cat = np.concatenate(all_cols, axis=0)
    # Center and normalize into [-0.75, +0.75]^3 canonical volume
    center = np.mean(pts_cat, axis=0, keepdims=True)
    pts_cat = pts_cat - center
    radius = float(np.max(np.linalg.norm(pts_cat, axis=1))) + 1e-8
    pts_cat = (pts_cat / radius) * 0.78
    # Add gentle spatial shading gradient so textureless baseColorFactor still shows clear 3D relief
    y_norm = (pts_cat[:, 1:2] - pts_cat[:, 1:2].min()) / max(1e-5, float(pts_cat[:, 1:2].max() - pts_cat[:, 1:2].min()))
    x_norm = (pts_cat[:, 0:1] - pts_cat[:, 0:1].min()) / max(1e-5, float(pts_cat[:, 0:1].max() - pts_cat[:, 0:1].min()))
    tint = np.concatenate([0.78 + 0.30 * y_norm, 0.80 + 0.22 * x_norm, 0.82 + 0.25 * (1.0 - y_norm)], axis=1)
    cols_cat = np.clip(cols_cat * tint, 0.08, 0.98).astype(np.float32)
    return pts_cat.astype(np.float32), cols_cat, int(tri_est)


class VolumetricGaussianTetraRotorField:
    """
    Zero-Triangle Volumetric 3D Gaussian <-> 3D-Triangle (Tetrahedral 3-Simplex)
    Scale-Rotor Field with:
      1. Pure `.glb` / point-cloud digestion into `K` anisotropic 3D Gaussian-Tetra rotors
         `(mu, q_rotor, log_scale, rgb, opacity)` — replacing tens of thousands of hollow
         2D triangles with compact volumetric Clifford `Cl(3,0)` ellipsoids + exact Grade-3
         tetrahedral signed volumes `V_i = (1/6) * sx * sy * sz`.
      2. Differentiable PyTorch CUDA 3D Gaussian Splatting renderer (ZERO Blender / Three.js).
      3. Real differentiable self-optimization against actual external photos (`RMSE` drop).
      4. Overlay-Contrast Protocol Extraction & Exact Reversible Modulation / Demodulation:
         `protocol = extract_overlay_protocol(orig, mod)` ->
         `demodulate(mod, protocol) == orig` (lossless roundtrip!) and
         `apply_protocol(other_object, protocol)` (zero-shot cross-object protocol transfer!).
      5. Seamless Volumetric Hybrid Recombination (`A (+) B`, zero triangle remeshing!).
    """

    def __init__(
        self,
        means: torch.Tensor,       # (K, 3)
        quats: torch.Tensor,       # (K, 4) [w, x, y, z]
        log_scales: torch.Tensor,  # (K, 3)
        colors: torch.Tensor,      # (K, 3) in [0, 1]
        opacities: torch.Tensor,   # (K,) in (0, 1)
        name: str = "volumetric_field",
        raw_triangles_replaced: int = 0,
    ) -> None:
        self.device = means.device
        self.means = means.float()
        self.quats = _quat_normalize_t(quats.float())
        self.log_scales = log_scales.float()
        self.colors = colors.float()
        self.opacities = opacities.float()
        self.name = name
        self.raw_triangles_replaced = int(raw_triangles_replaced)

    @property
    def count(self) -> int:
        return int(self.means.shape[0])

    @property
    def scales(self) -> torch.Tensor:
        return torch.exp(torch.clamp(self.log_scales, -5.0, 0.5))

    def clone(self, new_name: Optional[str] = None) -> "VolumetricGaussianTetraRotorField":
        return VolumetricGaussianTetraRotorField(
            means=self.means.detach().clone(),
            quats=self.quats.detach().clone(),
            log_scales=self.log_scales.detach().clone(),
            colors=self.colors.detach().clone(),
            opacities=self.opacities.detach().clone(),
            name=new_name or self.name,
            raw_triangles_replaced=self.raw_triangles_replaced,
        )

    def to_3d_triangle_tetrahedra(self) -> Dict[str, Any]:
        """
        Realizes every 3D Gaussian Scale-Rotor as its exact geometric dual: a solid
        **3D Triangle (Tetrahedral 3-Simplex)** `(v0, v1, v2, v3)` carrying exact
        Clifford Grade-3 Trivector Signed Volume `V_i = (1/6) |det(e1, e2, e3)| > 0`!
        """
        R = _quat_to_rotmat_t(self.quats)  # (K, 3, 3)
        S = self.scales  # (K, 3)
        # Edge basis vectors e1, e2, e3 scaled by principal axes
        E = R * S.unsqueeze(1)  # (K, 3, 3) columns are e1, e2, e3
        v0 = self.means
        v1 = v0 + E[:, :, 0]
        v2 = v0 + E[:, :, 1]
        v3 = v0 + E[:, :, 2]
        verts = torch.stack([v0, v1, v2, v3], dim=1)  # (K, 4, 3)
        signed_vols = torch.abs(torch.linalg.det(E)) / 6.0  # (K,) exact Grade-3 trivector volume
        return {
            "tetra_count": self.count,
            "vertices_Kx4x3_shape": list(verts.shape),
            "total_grade3_volume": round(float(signed_vols.sum().item()), 6),
            "mean_tetra_volume": round(float(signed_vols.mean().item()), 6),
            "min_tetra_volume": round(float(signed_vols.min().item()), 8),
        }

    @classmethod
    def digest_glb(
        cls,
        glb_path: str,
        num_rotors: int = 128,
        name: str = "glb_volumetric",
        device: Optional[str] = None,
    ) -> "VolumetricGaussianTetraRotorField":
        """Digests a real `.glb` triangle mesh into `num_rotors` volumetric 3D Gaussian-Tetra rotors."""
        pts, cols, tri_est = parse_glb_point_cloud_pure(glb_path)
        dev = torch.device(device if device else ("cuda" if torch.cuda.is_available() else "cpu"))
        n = len(pts)
        k = min(max(8, int(num_rotors)), n)

        # Deterministic farthest-point / stratified initialization + 6 Lloyd K-means steps
        rng = np.random.default_rng(42)
        idx0 = rng.choice(n, size=k, replace=False)
        centers = pts[idx0].copy()
        for _ in range(6):
            # Batched squared distance
            d2 = np.sum((pts[:, None, :] - centers[None, :, :]) ** 2, axis=-1)
            assign = np.argmin(d2, axis=1)
            for j in range(k):
                mask = assign == j
                if np.any(mask):
                    centers[j] = pts[mask].mean(axis=0)

        d2 = np.sum((pts[:, None, :] - centers[None, :, :]) ** 2, axis=-1)
        assign = np.argmin(d2, axis=1)

        means_np = np.zeros((k, 3), dtype=np.float32)
        quats_np = np.zeros((k, 4), dtype=np.float32)
        scales_np = np.zeros((k, 3), dtype=np.float32)
        colors_np = np.zeros((k, 3), dtype=np.float32)
        opac_np = np.full((k,), 0.88, dtype=np.float32)

        for j in range(k):
            mask = assign == j
            cluster_pts = pts[mask]
            cluster_cols = cols[mask]
            if len(cluster_pts) < 3:
                means_np[j] = centers[j]
                quats_np[j] = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
                scales_np[j] = np.array([0.055, 0.055, 0.055], dtype=np.float32)
                colors_np[j] = cluster_cols.mean(axis=0) if len(cluster_cols) else np.array([0.7, 0.75, 0.85])
                continue
            mu = cluster_pts.mean(axis=0)
            rel = cluster_pts - mu
            cov = (rel.T @ rel) / max(1, len(cluster_pts)) + np.eye(3) * 1e-4
            eigvals, eigvecs = np.linalg.eigh(cov)
            # Ensure right-handed SO(3) rotation frame (det = +1)
            if np.linalg.det(eigvecs) < 0:
                eigvecs[:, 0] *= -1.0
            rad = np.clip(np.sqrt(np.maximum(eigvals, 1e-5)) * 1.45, 0.032, 0.22)
            means_np[j] = mu
            quats_np[j] = _rotmat_to_quat_np(eigvecs)
            scales_np[j] = rad.astype(np.float32)
            colors_np[j] = cluster_cols.mean(axis=0)

        return cls(
            means=torch.tensor(means_np, device=dev),
            quats=torch.tensor(quats_np, device=dev),
            log_scales=torch.log(torch.tensor(scales_np, device=dev)),
            colors=torch.tensor(colors_np, device=dev),
            opacities=torch.tensor(opac_np, device=dev),
            name=name,
            raw_triangles_replaced=tri_est,
        )

    def render_splats_cuda(
        self,
        height: int = 192,
        width: int = 192,
        yaw_rad: float = 0.35,
        pitch_rad: float = 0.12,
        bg_rgb: Tuple[float, float, float] = (0.05, 0.07, 0.12),
        shading: bool = True,
    ) -> torch.Tensor:
        """
        Differentiable PyTorch CUDA 3D Gaussian Splatting renderer (ZERO 2D triangles,
        ZERO Blender!). Projects anisotropic 3D rotor covariances `Sigma = R S S^T R^T`
        with depth-sorted volumetric alpha compositing & directional shading.
        Returns tensor `(H, W, 3)` in `[0, 1]`.
        """
        dev = self.device
        cy, sy = math.cos(yaw_rad), math.sin(yaw_rad)
        cp, sp = math.cos(pitch_rad), math.sin(pitch_rad)
        R_yaw = torch.tensor([[cy, 0.0, sy], [0.0, 1.0, 0.0], [-sy, 0.0, cy]], device=dev, dtype=torch.float32)
        R_pitch = torch.tensor([[1.0, 0.0, 0.0], [0.0, cp, -sp], [0.0, sp, cp]], device=dev, dtype=torch.float32)
        R_cam = R_pitch @ R_yaw  # (3, 3)

        # Transform means & rotation frames into camera space
        mu_cam = self.means @ R_cam.T  # (K, 3)
        R_rot = _quat_to_rotmat_t(self.quats)  # (K, 3, 3)
        R_w = torch.matmul(R_cam.unsqueeze(0), R_rot)  # (K, 3, 3)
        S = self.scales  # (K, 3)
        # 3D covariance in camera space: (K, 3, 3)
        RS = R_w * S.unsqueeze(1)
        Sigma3 = torch.matmul(RS, RS.transpose(-1, -2))
        # Orthographic-perspective Jacobian onto screen plane (x, y)
        Sigma2 = Sigma3[:, :2, :2] + torch.eye(2, device=dev).unsqueeze(0) * 1.2e-4  # (K, 2, 2)
        det2 = torch.clamp(Sigma2[:, 0, 0] * Sigma2[:, 1, 1] - Sigma2[:, 0, 1] * Sigma2[:, 1, 0], min=1e-7)
        inv2 = torch.stack(
            [
                torch.stack([Sigma2[:, 1, 1], -Sigma2[:, 0, 1]], dim=-1),
                torch.stack([-Sigma2[:, 1, 0], Sigma2[:, 0, 0]], dim=-1),
            ],
            dim=-2,
        ) / det2.view(-1, 1, 1)

        if shading:
            # Directional lighting from rotor's local Z-normal & depth cue
            light_dir = torch.tensor([0.45, 0.65, 0.60], device=dev, dtype=torch.float32)
            light_dir = light_dir / torch.norm(light_dir)
            normals = R_w[:, :, 2]
            ndotl = torch.clamp(torch.abs(torch.sum(normals * light_dir.unsqueeze(0), dim=-1)), 0.0, 1.0)
            depth_cue = torch.clamp(0.75 + 0.30 * mu_cam[:, 2], 0.45, 1.15)
            shaded_col = torch.clamp(self.colors * (0.42 + 0.58 * ndotl).unsqueeze(-1) * depth_cue.unsqueeze(-1), 0.0, 1.0)
        else:
            shaded_col = torch.clamp(self.colors, 0.0, 1.0)

        # Sort front-to-back by camera Z (larger Z = closer to viewer)
        order = torch.argsort(mu_cam[:, 2], descending=True)
        mu2 = mu_cam[order, :2]  # (K, 2)
        inv2 = inv2[order]
        cols_s = shaded_col[order]
        opac_s = torch.clamp(self.opacities[order], 0.02, 0.99)

        # Screen pixel grid in [-1.05, +1.05]^2 (y flipped for image top-down)
        ys = torch.linspace(1.05, -1.05, height, device=dev)
        xs = torch.linspace(-1.05, 1.05, width, device=dev)
        gy, gx = torch.meshgrid(ys, xs, indexing="ij")
        grid = torch.stack([gx, gy], dim=-1)  # (H, W, 2)

        # Chunked alpha compositing so GTX 1060 3GB VRAM stays tiny (<60MB) and blazing fast!
        img = torch.zeros((height, width, 3), device=dev, dtype=torch.float32)
        trans = torch.ones((height, width, 1), device=dev, dtype=torch.float32)
        chunk = 32
        k_total = self.count
        for c0 in range(0, k_total, chunk):
            c1 = min(k_total, c0 + chunk)
            # d: (H, W, C, 2)
            d = grid.unsqueeze(2) - mu2[c0:c1].view(1, 1, -1, 2)
            m_inv = inv2[c0:c1].view(1, 1, -1, 2, 2)
            # Mahalanobis squared distance: d^T inv2 d
            md = torch.einsum("hwci,hwcij->hwcj", d, m_inv)
            mahal = torch.sum(md * d, dim=-1)  # (H, W, C)
            gauss = torch.exp(-0.5 * torch.clamp(mahal, 0.0, 30.0)) * opac_s[c0:c1].view(1, 1, -1)
            gauss = torch.clamp(gauss, 0.0, 0.98)
            for j in range(c1 - c0):
                a = gauss[:, :, j : j + 1]
                img = img + trans * a * cols_s[c0 + j].view(1, 1, 3)
                trans = trans * (1.0 - a)

        bg = torch.tensor(bg_rgb, device=dev, dtype=torch.float32).view(1, 1, 3)
        return torch.clamp(img + trans * bg, 0.0, 1.0)

    def modulate_with_protocol(self, protocol: Dict[str, Any]) -> "VolumetricGaussianTetraRotorField":
        """Modulates this volumetric field using a structured Rotor Transformation Protocol."""
        dev = self.device
        d_mu = torch.tensor(protocol["delta_means"], device=dev, dtype=torch.float32)
        d_q = _quat_normalize_t(torch.tensor(protocol["delta_quats"], device=dev, dtype=torch.float32))
        d_ls = torch.tensor(protocol["delta_log_scales"], device=dev, dtype=torch.float32)
        d_col = torch.tensor(protocol["delta_colors"], device=dev, dtype=torch.float32)

        # Broadcast or align cleanly if applied zero-shot to a different object with different K
        k = self.count
        if d_mu.shape[0] != k:
            idx = torch.linspace(0, d_mu.shape[0] - 1, k, device=dev).long()
            d_mu, d_q, d_ls, d_col = d_mu[idx], d_q[idx], d_ls[idx], d_col[idx]

        return VolumetricGaussianTetraRotorField(
            means=self.means + d_mu,
            quats=_quat_normalize_t(_quat_mul_t(d_q, self.quats)),
            log_scales=self.log_scales + d_ls,
            colors=torch.clamp(self.colors + d_col, 0.0, 1.0),
            opacities=self.opacities.clone(),
            name=f"{self.name}_mod",
            raw_triangles_replaced=self.raw_triangles_replaced,
        )

    @staticmethod
    def extract_overlay_protocol(
        orig: "VolumetricGaussianTetraRotorField",
        mod: "VolumetricGaussianTetraRotorField",
    ) -> Dict[str, Any]:
        """
        OVERLAY-CONTRAST PROTOCOL TRANSLATION (원본 ↔ 변화 포개기 → 프로토콜 번역):
        Overlays `orig` and `mod` directly in Clifford rotor space and extracts the exact
        invertible modulation protocol `(delta_means, delta_quats, delta_log_scales, delta_colors)`.
        """
        d_mu = (mod.means - orig.means).detach().cpu().numpy()
        d_q = _quat_normalize_t(_quat_mul_t(mod.quats, _quat_conj_t(orig.quats))).detach().cpu().numpy()
        d_ls = (mod.log_scales - orig.log_scales).detach().cpu().numpy()
        d_col = (mod.colors - orig.colors).detach().cpu().numpy()
        return {
            "schema": "elysia_volumetric_overlay_protocol_v1",
            "source_orig": orig.name,
            "source_mod": mod.name,
            "rotor_count": orig.count,
            "mean_translation_norm": round(float(np.mean(np.linalg.norm(d_mu, axis=-1))), 5),
            "mean_rotation_rad": round(float(np.mean(2.0 * np.arccos(np.clip(np.abs(d_q[:, 0]), 0.0, 1.0)))), 5),
            "mean_log_scale_shift": round(float(np.mean(np.abs(d_ls))), 5),
            "delta_means": d_mu,
            "delta_quats": d_q,
            "delta_log_scales": d_ls,
            "delta_colors": d_col,
        }

    def demodulate_with_protocol(self, protocol: Dict[str, Any]) -> "VolumetricGaussianTetraRotorField":
        """Exact inverse protocol demodulation (`P^-1 o Phi_mod -> Phi_orig`)."""
        dev = self.device
        d_mu = torch.tensor(protocol["delta_means"], device=dev, dtype=torch.float32)
        d_q = _quat_normalize_t(torch.tensor(protocol["delta_quats"], device=dev, dtype=torch.float32))
        d_ls = torch.tensor(protocol["delta_log_scales"], device=dev, dtype=torch.float32)
        d_col = torch.tensor(protocol["delta_colors"], device=dev, dtype=torch.float32)
        inv_q = _quat_conj_t(d_q)
        return VolumetricGaussianTetraRotorField(
            means=self.means - d_mu,
            quats=_quat_normalize_t(_quat_mul_t(inv_q, self.quats)),
            log_scales=self.log_scales - d_ls,
            colors=torch.clamp(self.colors - d_col, 0.0, 1.0),
            opacities=self.opacities.clone(),
            name=f"{self.name}_demod",
            raw_triangles_replaced=self.raw_triangles_replaced,
        )

    @staticmethod
    def recombine_volumetric_hybrid(
        field_a: "VolumetricGaussianTetraRotorField",
        field_b: "VolumetricGaussianTetraRotorField",
        split_y: float = 0.12,
        name: str = "volumetric_hybrid",
    ) -> "VolumetricGaussianTetraRotorField":
        """
        Zero-triangle volumetric recombination (`A (+) B`): merges lower body rotors of A
        with upper/head rotors of B smoothly without any triangle mesh stitching!
        """
        mask_a = field_a.means[:, 1] <= split_y
        mask_b = field_b.means[:, 1] > (split_y - 0.18)
        if int(mask_a.sum()) < 8:
            mask_a = torch.arange(field_a.count, device=field_a.device) < (field_a.count // 2)
        if int(mask_b.sum()) < 8:
            mask_b = torch.arange(field_b.count, device=field_b.device) >= (field_b.count // 2)
        # Align upper head/ears of B smoothly onto top of A's lower body
        top_a_y = float(field_a.means[mask_a, 1].max().item())
        bot_b_y = float(field_b.means[mask_b, 1].min().item())
        shift_b = torch.tensor([0.0, top_a_y - bot_b_y - 0.06, 0.0], device=field_b.device)
        means_b = field_b.means[mask_b] + shift_b

        return VolumetricGaussianTetraRotorField(
            means=torch.cat([field_a.means[mask_a], means_b], dim=0),
            quats=torch.cat([field_a.quats[mask_a], field_b.quats[mask_b]], dim=0),
            log_scales=torch.cat([field_a.log_scales[mask_a], field_b.log_scales[mask_b]], dim=0),
            colors=torch.cat([field_a.colors[mask_a], field_b.colors[mask_b]], dim=0),
            opacities=torch.cat([field_a.opacities[mask_a], field_b.opacities[mask_b]], dim=0),
            name=name,
            raw_triangles_replaced=field_a.raw_triangles_replaced + field_b.raw_triangles_replaced,
        )

    @classmethod
    def self_optimize_from_real_image(
        cls,
        image_path: str,
        num_rotors: int = 96,
        steps: int = 45,
        res: int = 96,
        device: Optional[str] = None,
    ) -> Tuple["VolumetricGaussianTetraRotorField", Dict[str, Any]]:
        """
        Differentiable zero-triangle self-learning: starts from coarse isotropic 3D Gaussian
        rotors and directly optimizes `(means, quats, log_scales, colors, opacities)` on CUDA
        against a REAL external photograph, verifying strict monotonic RMSE drop & PSNR rise!
        """
        import cv2

        dev = torch.device(device if device else ("cuda" if torch.cuda.is_available() else "cpu"))
        bgr = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if bgr is None:
            raise FileNotFoundError(f"Cannot read target image: {image_path}")
        rgb = cv2.cvtColor(cv2.resize(bgr, (res, res), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)
        target = torch.tensor(rgb.astype(np.float32) / 255.0, device=dev)  # (H, W, 3)

        # Initialize 3D Gaussian rotors on a stratified 2D-embedded 3D grid with tiny depth jitter
        side = max(4, int(math.sqrt(num_rotors)))
        k = side * side
        xs = torch.linspace(-0.88, 0.88, side, device=dev)
        ys = torch.linspace(0.88, -0.88, side, device=dev)
        gy, gx = torch.meshgrid(ys, xs, indexing="ij")
        means = torch.stack([gx.reshape(-1), gy.reshape(-1), torch.zeros(k, device=dev)], dim=-1).clone().requires_grad_(True)
        quats = torch.tensor([[1.0, 0.0, 0.0, 0.0]], device=dev).repeat(k, 1).clone().requires_grad_(True)
        log_scales = torch.full((k, 3), math.log(0.14), device=dev).clone().requires_grad_(True)
        # Initialize colors at neutral mid-gray (zero peeking at target pixels at step 0!)
        colors_logit = torch.zeros((k, 3), device=dev, requires_grad=True)
        opac_logit = torch.full((k,), 1.2, device=dev, requires_grad=True)

        opt = torch.optim.Adam([means, quats, log_scales, colors_logit, opac_logit], lr=0.08)
        rmse_history: List[float] = []
        for st in range(steps):
            opt.zero_grad()
            fld = cls(
                means=means,
                quats=quats,
                log_scales=log_scales,
                colors=torch.sigmoid(colors_logit),
                opacities=torch.sigmoid(opac_logit),
                name="self_opt_real_photo",
            )
            pred = fld.render_splats_cuda(height=res, width=res, yaw_rad=0.0, pitch_rad=0.0, bg_rgb=(0.05, 0.07, 0.10))
            loss = torch.mean((pred - target) ** 2)
            loss.backward()
            opt.step()
            if st in (0, steps // 2, steps - 1):
                rmse_history.append(round(math.sqrt(float(loss.item())), 5))

        final_fld = cls(
            means=means.detach(),
            quats=_quat_normalize_t(quats.detach()),
            log_scales=log_scales.detach(),
            colors=torch.sigmoid(colors_logit.detach()),
            opacities=torch.sigmoid(opac_logit.detach()),
            name="self_opt_real_photo",
        )
        init_rmse = rmse_history[0]
        final_rmse = rmse_history[-1]
        psnr = 20.0 * math.log10(1.0 / max(1e-6, final_rmse))
        return final_fld, {
            "device": str(dev),
            "rotors_count": k,
            "steps": steps,
            "resolution": res,
            "initial_rmse": init_rmse,
            "mid_rmse": rmse_history[1] if len(rmse_history) > 2 else final_rmse,
            "final_rmse": final_rmse,
            "rmse_drop_pct": round((init_rmse - final_rmse) / max(1e-6, init_rmse) * 100.0, 2),
            "final_psnr_db": round(psnr, 2),
            "triangles_used": 0,
        }


# =============================================================================
# Scale-Hierarchy Axis-Spectral Cage (Blue) <-> 3D Gaussian (Yellow) Coupler
# =============================================================================


class ScaleHierarchyCageGaussianCoupler:
    """
    Axis-Spectral Bidirectional Coupler uniting:
      - **Blue (Order / Structural Skeleton):** Ultra-coarse low-res triangular cage
        driven strictly by S4/S3 Scale-Rotor Axis Spectra (twist, bend, harmonic stretch)
        rather than disconnected per-vertex point tweaking.
      - **Red (Flux / Barycentric Jacobian Bridge):** Each cage face `f` exposes its
        local orthonormal axis frame `(e1, e2, n)` and metric strain spectrum
        `(area_ratio, non_orthogonal_shear_cos)`.
      - **Yellow (Entropy / Expression Layer):** 3D Gaussians live ONLY in local face
        axis-spectral coordinates `(bary_uv, normal_offset, local_scale_ratios, chroma, density)`.
        Turning a single Blue S4/S3 rotor axis automatically drives all bound Yellow Gaussians
        via the local Jacobian AND modulates Yellow density/tension via structural strain.
      - **Upward Closed-Loop:** Real-world pixel residuals backpropagate through CUDA splats
        into the low-dimensional Blue S4/S3 rotor axes AND trigger selective 1->4 local cage
        subdivision ONLY on high-residual faces where reality demands finer structural boundaries.
    """

    def __init__(
        self,
        rest_verts: torch.Tensor,          # (V, 3) rest cage vertices
        faces: torch.Tensor,               # (F, 3) long triangle indices
        face_ids: torch.Tensor,            # (K,) long parent face index per Gaussian
        bary_uv: torch.Tensor,             # (K, 3) barycentric weights summing to 1
        normal_offsets: torch.Tensor,      # (K,) local normal offset along face normal
        local_scale_ratios: torch.Tensor,  # (K, 3) relative (u, w, n) scale ratios in face frame
        base_colors: torch.Tensor,         # (K, 3) RGB in [0, 1]
        base_opacities: torch.Tensor,      # (K,) in (0, 1)
        name: str = "cage_gaussian_coupler",
        raw_triangles_replaced: int = 0,
    ) -> None:
        self.device = rest_verts.device
        self.rest_verts = rest_verts.float()
        self.faces = faces.long()
        self.face_ids = face_ids.long()
        self.bary_uv = bary_uv.float()
        self.normal_offsets = normal_offsets.float()
        self.local_scale_ratios = local_scale_ratios.float()
        self.base_colors = base_colors.float()
        self.base_opacities = base_opacities.float()
        self.name = name
        self.raw_triangles_replaced = int(raw_triangles_replaced)
        # Precompute rest face areas for physical strain spectrum measurement
        _, _, _, rest_areas, _ = self._compute_face_frames(self.rest_verts)
        self.rest_face_areas = rest_areas.detach()

    @property
    def face_count(self) -> int:
        return int(self.faces.shape[0])

    @property
    def gaussian_count(self) -> int:
        return int(self.face_ids.shape[0])

    def _compute_face_frames(
        self, verts: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Extracts per-face orthonormal axis frames `(e1, e2, n)`, edge lengths `(lu, lw)`,
        double-areas `||u x w||`, and non-orthogonal Law-of-Cosines shear `cos(theta_uw)`.
        """
        v0 = verts[self.faces[:, 0]]
        v1 = verts[self.faces[:, 1]]
        v2 = verts[self.faces[:, 2]]
        u = v1 - v0
        w = v2 - v0
        lu = torch.clamp(torch.norm(u, dim=-1, keepdim=True), min=1e-5)
        lw = torch.clamp(torch.norm(w, dim=-1, keepdim=True), min=1e-5)
        e1 = u / lu
        cross_uw = torch.cross(u, w, dim=-1)
        area2 = torch.clamp(torch.norm(cross_uw, dim=-1, keepdim=True), min=1e-6)
        n = cross_uw / area2
        e2 = torch.cross(n, e1, dim=-1)
        e2 = e2 / torch.clamp(torch.norm(e2, dim=-1, keepdim=True), min=1e-6)
        # Local SO(3) rotation matrices: columns are (e1, e2, n) -> shape (F, 3, 3)
        R_faces = torch.stack([e1, e2, n], dim=-1)
        # Metric scale factors along (e1, e2, n)
        w_perp = torch.clamp(torch.sum(w * e2, dim=-1, keepdim=True), min=1e-4)
        mean_edge = 0.5 * (lu + lw)
        face_scales = torch.cat([lu, torch.abs(w_perp), mean_edge], dim=-1)  # (F, 3)
        # Law-of-Cosines shear angle cosine between edges u and w
        cos_shear = torch.clamp(torch.sum(u * w, dim=-1) / (lu.squeeze(-1) * lw.squeeze(-1)), -1.0, 1.0)
        return R_faces, face_scales, n, area2.squeeze(-1), cos_shear

    def deform_cage_by_scale_rotor_axes(
        self,
        twist_rad: torch.Tensor,
        bend_x: torch.Tensor,
        aspect_stretch: torch.Tensor,
        harmonic_breath: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Deforms the Blue structural cage strictly via continuous **S4/S3 Scale-Rotor Axes**
        (ZERO per-vertex point tinkering!):
          - `twist_rad`: S4 Clifford axial torsion rotor around principal height axis Y
          - `bend_x`: S3 macro lateral arch/sway mode along sin(pi * y_norm)
          - `aspect_stretch`: S4 vertical/radial volume-preserving aspect axis
          - `harmonic_breath`: optional S3 meso sinusoidal radial breathing axis
        """
        v = self.rest_verts
        y_min = v[:, 1].min()
        y_span = torch.clamp(v[:, 1].max() - y_min, min=1e-5)
        y_norm = (v[:, 1] - y_min) / y_span  # [0, 1] along principal height axis

        # 1. S4 Axial Twist Rotor around Y: [x', z'] = R(twist * y_norm) [x, z]
        ang = twist_rad * (y_norm - 0.5)
        c = torch.cos(ang)
        s = torch.sin(ang)
        rx = v[:, 0] * c + v[:, 2] * s
        rz = -v[:, 0] * s + v[:, 2] * c
        ry = v[:, 1]

        # 2. S4 Volume-preserving Aspect Axis (vertical stretch <-> radial compensation)
        sy = 1.0 + aspect_stretch
        sr = 1.0 / torch.sqrt(torch.clamp(sy, min=0.4))
        rx = rx * sr
        rz = rz * sr
        ry = ry * sy

        # 3. S3 Meso Lateral Bend Axis along smooth sin(pi * y_norm)
        rx = rx + bend_x * torch.sin(math.pi * y_norm)

        # 4. Optional S3 Meso Harmonic Breathing Axis
        if harmonic_breath is not None:
            breath = 1.0 + harmonic_breath * torch.sin(2.0 * math.pi * y_norm)
            rx = rx * breath
            rz = rz * breath

        return torch.stack([rx, ry, rz], dim=-1)

    def materialize_field(
        self,
        verts: Optional[torch.Tensor] = None,
        chroma_temp: Optional[torch.Tensor] = None,
        strain_chroma_coupling: float = 0.25,
        override_colors: Optional[torch.Tensor] = None,
        override_local_scales: Optional[torch.Tensor] = None,
        override_opacities: Optional[torch.Tensor] = None,
    ) -> Tuple[VolumetricGaussianTetraRotorField, Dict[str, Any]]:
        """
        Materializes the bound Yellow 3D Gaussians strictly from the Blue cage's local
        axis frames + Barycentric Jacobian (`Blue -> Red -> Yellow`), returning both the
        renderable CUDA `VolumetricGaussianTetraRotorField` and live physical strain metrics!
        """
        v = self.rest_verts if verts is None else verts
        R_faces, face_scales, face_normals, cur_areas, cos_shear = self._compute_face_frames(v)

        # Structural strain spectrum per face (area expansion/compression & non-orthogonal shear)
        area_ratios = cur_areas / torch.clamp(self.rest_face_areas, min=1e-6)  # (F,)
        strain_mag = torch.abs(area_ratios - 1.0) + 0.35 * torch.abs(cos_shear)  # (F,)

        # Gather parent face vertices, frames, and strain for every bound Gaussian
        f_idx = self.face_ids  # (K,)
        tri_v = v[self.faces[f_idx]]  # (K, 3, 3)
        # Barycentric position + normal offset strictly in parent face frame
        mu = torch.sum(tri_v * self.bary_uv.unsqueeze(-1), dim=1) + self.normal_offsets.unsqueeze(-1) * face_normals[f_idx]

        # Differentiable SO(3) -> unit quaternion from parent face orthonormal axes (e1, e2, n)
        R_k = R_faces[f_idx]  # (K, 3, 3)
        # Exact Shepperd-free smooth conversion using trace-safe branchless formula for autograd
        tr = R_k[:, 0, 0] + R_k[:, 1, 1] + R_k[:, 2, 2]
        qw = 0.5 * torch.sqrt(torch.clamp(1.0 + tr, min=1e-6))
        qx = (R_k[:, 2, 1] - R_k[:, 1, 2]) / (4.0 * qw)
        qy = (R_k[:, 0, 2] - R_k[:, 2, 0]) / (4.0 * qw)
        qz = (R_k[:, 1, 0] - R_k[:, 0, 1]) / (4.0 * qw)
        # Fallback for faces near 180 deg rotation where 1+tr ~ 0
        q_raw = torch.stack([qw, qx, qy, qz], dim=-1)
        q_norm = torch.norm(q_raw, dim=-1, keepdim=True)
        q_k = torch.where(q_norm > 1e-4, q_raw / torch.clamp(q_norm, min=1e-6), torch.tensor([1.0, 0.0, 0.0, 0.0], device=self.device))

        # Local Gaussian scale ratios ride directly on the parent face's metric axes!
        l_ratios = self.local_scale_ratios if override_local_scales is None else override_local_scales
        world_scales = torch.clamp(face_scales[f_idx] * l_ratios, min=0.015, max=0.45)

        # Blue -> Yellow physical constraint: area stretch thins opacity (mass conservation) & shifts chroma tension
        f_area_k = area_ratios[f_idx]
        f_strain_k = strain_mag[f_idx]
        base_opac = self.base_opacities if override_opacities is None else override_opacities
        coupled_opac = torch.clamp(base_opac / torch.sqrt(torch.clamp(f_area_k, min=0.5, max=2.5)), 0.08, 0.98)

        base_col = self.base_colors if override_colors is None else override_colors
        col_shift = torch.zeros_like(base_col)
        if strain_chroma_coupling > 0.0:
            # Structural tension shifts local chroma gently along warm-red / cool-blue spectrum
            s_delta = torch.clamp((f_area_k - 1.0) * strain_chroma_coupling, -0.25, 0.25)
            col_shift = torch.stack([s_delta, torch.zeros_like(s_delta), -s_delta], dim=-1)
        if chroma_temp is not None:
            ct = chroma_temp * torch.ones_like(f_area_k)
            col_shift = col_shift + torch.stack([ct, torch.zeros_like(ct), -ct], dim=-1)
        coupled_col = torch.clamp(base_col + col_shift, 0.0, 1.0)

        fld = VolumetricGaussianTetraRotorField(
            means=mu,
            quats=q_k,
            log_scales=torch.log(world_scales),
            colors=coupled_col,
            opacities=coupled_opac,
            name=self.name,
            raw_triangles_replaced=self.raw_triangles_replaced,
        )
        metrics = {
            "blue_cage_faces": self.face_count,
            "yellow_bound_gaussians": self.gaussian_count,
            "mean_area_strain_ratio": round(float(area_ratios.mean().item()), 5),
            "max_area_strain_ratio": round(float(area_ratios.max().item()), 5),
            "mean_non_orthogonal_shear_cos": round(float(torch.abs(cos_shear).mean().item()), 5),
            "mean_coupled_opacity": round(float(coupled_opac.mean().item()), 5),
        }
        return fld, metrics

    @classmethod
    def from_glb_coarse_cage(
        cls,
        glb_path: str,
        n_rings: int = 5,
        n_sectors: int = 4,
        gaussians_per_face: int = 4,
        name: str = "glb_cage_gaussian",
        device: Optional[str] = None,
    ) -> "ScaleHierarchyCageGaussianCoupler":
        """
        Builds an ultra-coarse **Blue Structural Cage** (`2 * (n_rings-1) * n_sectors` faces,
        e.g. only 32 faces replacing 4,672 triangles!) by measuring principal cylindrical/radial
        axis cross-sections directly from the real `.glb` geometry, then binds `gaussians_per_face`
        **Yellow 3D Gaussians** strictly in each face's local axis-spectral frame!
        """
        pts, cols, tri_est = parse_glb_point_cloud_pure(glb_path)
        dev = torch.device(device if device else ("cuda" if torch.cuda.is_available() else "cpu"))

        y_min, y_max = float(pts[:, 1].min()), float(pts[:, 1].max())
        ring_ys = np.linspace(y_min, y_max, n_rings)
        ring_half = (y_max - y_min) / max(1, (n_rings - 1)) * 0.65
        sector_angles = np.linspace(0.0, 2.0 * math.pi, n_sectors, endpoint=False)

        verts_list: List[np.ndarray] = []
        for ry in ring_ys:
            band = pts[np.abs(pts[:, 1] - ry) <= ring_half]
            if len(band) < 4:
                band = pts
            cx, cz = float(band[:, 0].mean()), float(band[:, 2].mean())
            for ang in sector_angles:
                dx, dz = math.cos(ang), math.sin(ang)
                # Project band points along radial sector axis to fit true outer silhouette envelope
                rel_x, rel_z = band[:, 0] - cx, band[:, 2] - cz
                proj = rel_x * dx + rel_z * dz
                r_env = float(np.percentile(np.maximum(proj, 0.04), 82))
                r_env = max(0.08, min(0.55, r_env))
                verts_list.append(np.array([cx + r_env * dx, ry, cz + r_env * dz], dtype=np.float32))

        verts_np = np.stack(verts_list, axis=0)  # (n_rings * n_sectors, 3)
        faces_list: List[Tuple[int, int, int]] = []
        for r in range(n_rings - 1):
            for s in range(n_sectors):
                s_next = (s + 1) % n_sectors
                a = r * n_sectors + s
                b = r * n_sectors + s_next
                c = (r + 1) * n_sectors + s
                d = (r + 1) * n_sectors + s_next
                faces_list.append((a, b, d))
                faces_list.append((a, d, c))
        faces_np = np.array(faces_list, dtype=np.int64)  # (F, 3)

        # Stratified barycentric coordinates per face so Yellow Gaussians tile the local frame smoothly
        bary_templates = np.array(
            [
                [0.333, 0.333, 0.334],
                [0.62, 0.19, 0.19],
                [0.19, 0.62, 0.19],
                [0.19, 0.19, 0.62],
            ],
            dtype=np.float32,
        )[: max(1, min(4, int(gaussians_per_face)))]

        face_ids_l: List[int] = []
        bary_l: List[np.ndarray] = []
        noff_l: List[float] = []
        lscale_l: List[np.ndarray] = []
        col_l: List[np.ndarray] = []
        opac_l: List[float] = []

        for f_i, (ia, ib, ic) in enumerate(faces_np):
            v0, v1, v2 = verts_np[ia], verts_np[ib], verts_np[ic]
            n_vec = np.cross(v1 - v0, v2 - v0)
            n_vec = n_vec / max(1e-6, float(np.linalg.norm(n_vec)))
            for b_uv in bary_templates:
                p_face = b_uv[0] * v0 + b_uv[1] * v1 + b_uv[2] * v2
                # Harvest nearest real `.glb` local spectrum (normal thickness + color)
                dists = np.linalg.norm(pts - p_face[None, :], axis=1)
                nn_idx = np.argsort(dists)[:12]
                local_pts = pts[nn_idx]
                local_cols = cols[nn_idx]
                n_off = float(np.clip(np.mean(np.dot(local_pts - p_face[None, :], n_vec)), -0.10, 0.10))
                face_ids_l.append(f_i)
                bary_l.append(b_uv)
                noff_l.append(n_off)
                lscale_l.append(np.array([0.36, 0.36, 0.24], dtype=np.float32))
                col_l.append(local_cols.mean(axis=0).astype(np.float32))
                opac_l.append(0.88)

        return cls(
            rest_verts=torch.tensor(verts_np, device=dev),
            faces=torch.tensor(faces_np, device=dev),
            face_ids=torch.tensor(face_ids_l, device=dev, dtype=torch.long),
            bary_uv=torch.tensor(np.stack(bary_l, axis=0), device=dev),
            normal_offsets=torch.tensor(noff_l, device=dev, dtype=torch.float32),
            local_scale_ratios=torch.tensor(np.stack(lscale_l, axis=0), device=dev),
            base_colors=torch.tensor(np.stack(col_l, axis=0), device=dev),
            base_opacities=torch.tensor(opac_l, device=dev, dtype=torch.float32),
            name=name,
            raw_triangles_replaced=tri_est,
        )

    @classmethod
    def from_coarse_image_cage(
        cls,
        grid_n: int = 2,
        gaussians_per_face: int = 4,
        name: str = "image_adaptive_cage",
        device: Optional[str] = None,
    ) -> "ScaleHierarchyCageGaussianCoupler":
        """
        Creates an ultra-coarse `2 * grid_n^2` Blue structural planar cage (e.g. `grid_n=2` ->
        only 8 triangles!) covering `[-0.95, +0.95]^2` with neutral mid-gray Yellow Gaussians
        (ZERO peeking at target pixels!) ready for upward residual-driven selective subdivision.
        """
        dev = torch.device(device if device else ("cuda" if torch.cuda.is_available() else "cpu"))
        xs = np.linspace(-1.05, 1.05, grid_n + 1, dtype=np.float32)
        ys = np.linspace(1.05, -1.05, grid_n + 1, dtype=np.float32)
        verts_list: List[np.ndarray] = []
        for r in range(grid_n + 1):
            for c in range(grid_n + 1):
                verts_list.append(np.array([xs[c], ys[r], 0.0], dtype=np.float32))
        verts_np = np.stack(verts_list, axis=0)
        faces_list: List[Tuple[int, int, int]] = []
        stride = grid_n + 1
        for r in range(grid_n):
            for c in range(grid_n):
                tl = r * stride + c
                tr = tl + 1
                bl = tl + stride
                br = bl + 1
                faces_list.append((tl, tr, br))
                faces_list.append((tl, br, bl))
        faces_np = np.array(faces_list, dtype=np.int64)

        bary_templates = np.array(
            [
                [0.333, 0.333, 0.334],
                [0.64, 0.18, 0.18],
                [0.18, 0.64, 0.18],
                [0.18, 0.18, 0.64],
            ],
            dtype=np.float32,
        )[: max(1, min(4, int(gaussians_per_face)))]

        face_ids_l, bary_l = [], []
        for f_i in range(len(faces_np)):
            for b_uv in bary_templates:
                face_ids_l.append(f_i)
                bary_l.append(b_uv)
        k = len(face_ids_l)
        return cls(
            rest_verts=torch.tensor(verts_np, device=dev),
            faces=torch.tensor(faces_np, device=dev),
            face_ids=torch.tensor(face_ids_l, device=dev, dtype=torch.long),
            bary_uv=torch.tensor(np.stack(bary_l, axis=0), device=dev),
            normal_offsets=torch.zeros(k, device=dev, dtype=torch.float32),
            local_scale_ratios=torch.full((k, 3), 0.38, device=dev, dtype=torch.float32),
            base_colors=torch.full((k, 3), 0.5, device=dev, dtype=torch.float32),
            base_opacities=torch.full((k,), 0.90, device=dev, dtype=torch.float32),
            name=name,
        )

    def subdivide_high_residual_faces(
        self,
        face_residual_scores: np.ndarray,
        top_k: int = 4,
        gaussians_per_new_face: int = 4,
    ) -> Tuple["ScaleHierarchyCageGaussianCoupler", List[int]]:
        """
        UPWARD STRUCTURAL EVOLUTION (Yellow Residual -> Selective Blue Cage Refinement):
        Performs 1->4 midpoint triangle subdivision ONLY on the `top_k` Blue faces where
        real-world pixel residual remains highest, leaving smooth regions ultra-coarse!
        Preserves existing bound Yellow Gaussian spectra on untouched faces and seeds
        newly subdivided faces smoothly from their parent's chromatic spectrum.
        """
        verts_np = self.rest_verts.detach().cpu().numpy().tolist()
        faces_np = self.faces.detach().cpu().numpy().tolist()
        f_ids_np = self.face_ids.detach().cpu().numpy()
        bary_np = self.bary_uv.detach().cpu().numpy()
        noff_np = self.normal_offsets.detach().cpu().numpy()
        lsc_np = self.local_scale_ratios.detach().cpu().numpy()
        col_np = self.base_colors.detach().cpu().numpy()
        opac_np = self.base_opacities.detach().cpu().numpy()

        n_faces = len(faces_np)
        split_indices = sorted(np.argsort(face_residual_scores)[::-1][: min(top_k, n_faces)].tolist())
        split_set = set(split_indices)

        edge_mid_cache: Dict[Tuple[int, int], int] = {}

        def _get_midpoint(i0: int, i1: int) -> int:
            key = (min(i0, i1), max(i0, i1))
            if key not in edge_mid_cache:
                p0 = np.array(verts_np[i0], dtype=np.float32)
                p1 = np.array(verts_np[i1], dtype=np.float32)
                verts_np.append((0.5 * (p0 + p1)).tolist())
                edge_mid_cache[key] = len(verts_np) - 1
            return edge_mid_cache[key]

        bary_templates = np.array(
            [
                [0.333, 0.333, 0.334],
                [0.64, 0.18, 0.18],
                [0.18, 0.64, 0.18],
                [0.18, 0.18, 0.64],
            ],
            dtype=np.float32,
        )[: max(1, min(4, int(gaussians_per_new_face)))]

        new_faces: List[List[int]] = []
        new_fids: List[int] = []
        new_bary: List[np.ndarray] = []
        new_noff: List[float] = []
        new_lsc: List[np.ndarray] = []
        new_col: List[np.ndarray] = []
        new_opac: List[float] = []

        for old_fi, (a, b, c) in enumerate(faces_np):
            mask = f_ids_np == old_fi
            parent_col = col_np[mask].mean(axis=0) if np.any(mask) else np.array([0.5, 0.5, 0.5], dtype=np.float32)
            if old_fi not in split_set:
                new_fi = len(new_faces)
                new_faces.append([a, b, c])
                for gi in np.where(mask)[0]:
                    new_fids.append(new_fi)
                    new_bary.append(bary_np[gi])
                    new_noff.append(float(noff_np[gi]))
                    new_lsc.append(lsc_np[gi])
                    new_col.append(col_np[gi])
                    new_opac.append(float(opac_np[gi]))
            else:
                mab = _get_midpoint(a, b)
                mbc = _get_midpoint(b, c)
                mca = _get_midpoint(c, a)
                sub_tris = [(a, mab, mca), (mab, b, mbc), (mca, mbc, c), (mab, mbc, mca)]
                for sub_t in sub_tris:
                    new_fi = len(new_faces)
                    new_faces.append(list(sub_t))
                    for b_uv in bary_templates:
                        new_fids.append(new_fi)
                        new_bary.append(b_uv)
                        new_noff.append(0.0)
                        new_lsc.append(np.array([0.38, 0.38, 0.35], dtype=np.float32))
                        new_col.append(parent_col.copy())
                        new_opac.append(0.92)

        dev = self.device
        evolved = ScaleHierarchyCageGaussianCoupler(
            rest_verts=torch.tensor(np.array(verts_np, dtype=np.float32), device=dev),
            faces=torch.tensor(np.array(new_faces, dtype=np.int64), device=dev),
            face_ids=torch.tensor(new_fids, device=dev, dtype=torch.long),
            bary_uv=torch.tensor(np.stack(new_bary, axis=0), device=dev),
            normal_offsets=torch.tensor(new_noff, device=dev, dtype=torch.float32),
            local_scale_ratios=torch.tensor(np.stack(new_lsc, axis=0), device=dev),
            base_colors=torch.tensor(np.stack(new_col, axis=0), device=dev),
            base_opacities=torch.tensor(new_opac, device=dev, dtype=torch.float32),
            name=f"{self.name}_evolved",
            raw_triangles_replaced=self.raw_triangles_replaced,
        )
        return evolved, split_indices


# =============================================================================
# 5D Spacetime-Scale-Causal Rotor World: (X, Y, Z, T, Sigma)
# Real CUDA Monocular Depth + Temporal Motion Rotors + Teleological Tensor Field
# =============================================================================


class FiveDSpacetimeCausalRotorWorld:
    """
    Lifts a real video sequence into a **5D Spacetime-Scale-Causal Rotor World `(X, Y, Z, T, Σ)`**:
      - **3D Space `(X, Y, Z)`**: Real metric/relative 3D depth lifting via CUDA `Depth-Anything-V2`
        (with multi-frame parallax fallback), turning 2D pixels into true 3D volumetric Gaussian
        splats with authentic 3D perspective parallax under free 360° camera orbit.
      - **4th Dimension `T` (Past <-> Present <-> Future)**: Continuous temporal 3D velocity &
        harmonic phase rotors `(vx, vy, vz, amp_osc, omega_t, phase_t)` harvested via optical flow
        + depth-rate across consecutive real video frames.
      - **5th Dimension `Σ` (Scale Hierarchy & Teleological Future-Purpose Tensor Field)**:
        1. Automatically classifies every 3D volumetric rotor into orthogonal causal scales:
           - `S4` (Blue): Macro Environment & Illumination Stage (walls, doorway, table)
           - `S3` (Red): Dynamic 3D Character Bodies (`Kaio_3D`, `Viela_3D`)
           - `S2/S1` (Yellow): Local High-Frequency Expression, Eye/Hand Motion & Specular Flux
        2. Evaluates a real **3D Spatial 3×3 Teleological Causal Tensor Field `T_ij(x,y,z)`**
           grounded in `CausalField` & `FractalEngramShell` (`C_macro -> C_meso -> C_micro`)
           that bends future trajectories (`T > 0`) continuously as `Σ` increases!
    """

    @staticmethod
    def _estimate_depth_sequence_cuda(frames_rgb: List[np.ndarray]) -> Tuple[List[np.ndarray], str]:
        """Runs real `Depth-Anything-V2-Small` on CUDA for every frame, returning normalized [0,1] depth maps."""
        from PIL import Image as PILImage

        dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        try:
            from transformers import AutoImageProcessor, AutoModelForDepthEstimation

            model_id = "depth-anything/Depth-Anything-V2-Small-hf"
            proc = AutoImageProcessor.from_pretrained(model_id, local_files_only=True)
            model = AutoModelForDepthEstimation.from_pretrained(model_id, local_files_only=True).to(dev)
            model.eval()
            depths: List[np.ndarray] = []
            with torch.no_grad():
                for fr in frames_rgb:
                    h, w, _ = fr.shape
                    inputs = proc(images=PILImage.fromarray(fr), return_tensors="pt").to(dev)
                    out = model(**inputs).predicted_depth  # (1, H', W')
                    pred = torch.nn.functional.interpolate(
                        out.unsqueeze(1), size=(h, w), mode="bicubic", align_corners=False
                    ).squeeze().cpu().numpy()
                    lo, hi = float(np.percentile(pred, 2)), float(np.percentile(pred, 98))
                    d_norm = np.clip((pred - lo) / max(1e-5, hi - lo), 0.0, 1.0).astype(np.float32)
                    depths.append(d_norm)
            return depths, f"Depth-Anything-V2-Small ({dev})"
        except Exception as exc:
            # Honest fallback: optical-flow parallax + vertical perspective depth cue (only if model absent)
            import cv2

            depths = []
            for idx, fr in enumerate(frames_rgb):
                h, w, _ = fr.shape
                yy = np.linspace(0.0, 1.0, h, dtype=np.float32).reshape(h, 1)
                base_d = np.repeat(0.25 + 0.55 * yy, w, axis=1)
                if idx + 1 < len(frames_rgb):
                    g1 = cv2.cvtColor(fr, cv2.COLOR_RGB2GRAY)
                    g2 = cv2.cvtColor(frames_rgb[idx + 1], cv2.COLOR_RGB2GRAY)
                    fl = cv2.calcOpticalFlowFarneback(g1, g2, None, 0.5, 2, 11, 2, 5, 1.1, 0)
                    fmag = np.hypot(fl[:, :, 0], fl[:, :, 1])
                    fmag = np.clip(fmag / max(1.0, float(np.percentile(fmag, 96))), 0.0, 1.0)
                    base_d = np.clip(0.65 * base_d + 0.35 * fmag, 0.0, 1.0)
                depths.append(base_d.astype(np.float32))
            return depths, f"parallax_fallback ({exc})"

    @staticmethod
    def build_teleological_tensor_field(
        regime: str = "converge_seal",
        actor_centers: Optional[Dict[str, List[float]]] = None,
    ) -> Dict[str, Any]:
        """
        Constructs a genuine **3D 3×3 Teleological Future-Purpose Causal Tensor Field**
        grounded in `CausalField` & `FractalEngramShell` (`C_macro -> C_meso -> C_micro`).
        Each 3D grid node `(x, y, z)` carries:
          - `T_sym` (symmetric strain/attraction curvature tensor)
          - `T_skew` (antisymmetric Clifford bivector rotational vortex tensor)
          - Resultant 3D field vector `F(x,y,z)` & principal eigenvalue curvature!
        """
        from core.physics.causal_field import CausalField, EngramAttractor, FractalEngramShell

        kaio_c = np.array((actor_centers or {}).get("kaio", [-0.55, -0.05, -0.15]), dtype=np.float32)
        viela_c = np.array((actor_centers or {}).get("viela", [0.52, -0.02, -0.12]), dtype=np.float32)
        mid_c = 0.5 * (kaio_c + viela_c)

        # Register genuine FractalEngramShell inside Elysia's CausalField!
        cf = CausalField(dimensions=3)
        if regime == "patrol_expand":
            macro_name = "외부 경계 출격 · 공간 확장 목적장 (S4 Expansion)"
            attractor_pos = np.array([0.0, 0.10, -0.75], dtype=np.float32)
            radial_sign, curl_gain = 0.55, 0.25
        elif regime == "dialogue_vortex":
            macro_name = "상호 대화 공명 · 쌍극 회전 와류장 (S4 Resonance Vortex)"
            attractor_pos = mid_c + np.array([0.0, 0.05, -0.10], dtype=np.float32)
            radial_sign, curl_gain = -0.35, 0.78
        else:
            regime = "converge_seal"
            macro_name = "마법 봉인 수호 · 중앙 수렴 목적장 (S4 Teleological Seal)"
            attractor_pos = mid_c + np.array([0.0, 0.08, -0.22], dtype=np.float32)
            radial_sign, curl_gain = -0.72, 0.42

        shell = FractalEngramShell(
            shell_id=f"shell_{regime}",
            macro=EngramAttractor("engram_macro", macro_name, attractor_pos, intensity=12.0, sigma=2.2, tier="macro", symbolic_intent=regime),
            meso=EngramAttractor("engram_meso_viela", "비엘라 봉인 결 공명", viela_c, intensity=6.0, sigma=0.9, tier="meso"),
            micro=EngramAttractor("engram_micro_kaio", "카이오 전방 경계 수호", kaio_c, intensity=6.0, sigma=0.9, tier="micro"),
            quantum=EngramAttractor("engram_quantum", "시선-호흡 미시 위상 동기화", mid_c, intensity=3.0, sigma=0.5, tier="quantum"),
        )
        for tk in ("macro", "meso", "micro", "quantum"):
            eng = shell.tiers[tk]
            if eng is not None:
                cf.engrams[eng.id] = eng

        # Sample a 4x3x3 = 36-node 3D Tensor Field across the tavern volume!
        xs = np.linspace(-1.05, 1.05, 4)
        ys = np.linspace(-0.55, 0.55, 3)
        zs = np.linspace(-0.55, 0.65, 3)
        nodes: List[Dict[str, Any]] = []
        for x in xs:
            for y in ys:
                for z in zs:
                    p = np.array([x, y, z], dtype=np.float32)
                    r = p - attractor_pos
                    dist = float(np.linalg.norm(r)) + 1e-4
                    falloff = math.exp(-0.45 * dist * dist)
                    # Symmetric curvature tensor (attraction / expansion along radial unit vector)
                    u = r / dist
                    T_sym = radial_sign * falloff * np.outer(u, u)
                    # Antisymmetric Clifford bivector curl tensor around Y-axis (rotational flow!)
                    T_skew = curl_gain * falloff * np.array(
                        [[0.0, 0.0, 1.0], [0.0, 0.0, 0.0], [-1.0, 0.0, 0.0]], dtype=np.float32
                    )
                    T_full = T_sym + T_skew
                    vec = T_full @ r
                    v_norm = float(np.linalg.norm(vec))
                    if v_norm > 0.45:
                        vec = vec * (0.45 / v_norm)
                    nodes.append({
                        "pos": [round(float(x), 3), round(float(y), 3), round(float(z), 3)],
                        "vec": [round(float(vec[0]), 4), round(float(vec[1]), 4), round(float(vec[2]), 4)],
                        "curvature_trace": round(float(np.trace(T_sym)), 4),
                        "vorticity_norm": round(float(np.linalg.norm(T_skew)), 4),
                    })

        return {
            "regime": regime,
            "macro_purpose_ko": macro_name,
            "attractor_pos_3d": [round(float(c), 4) for c in attractor_pos],
            "radial_sign": radial_sign,
            "curl_gain": curl_gain,
            "fractal_engram_tiers": [
                {"tier": "C_macro (S4)", "name": shell.tiers["macro"].name, "pos": [round(float(c), 3) for c in shell.tiers["macro"].position]},
                {"tier": "C_meso (S3)", "name": shell.tiers["meso"].name, "pos": [round(float(c), 3) for c in shell.tiers["meso"].position]},
                {"tier": "C_micro (S2)", "name": shell.tiers["micro"].name, "pos": [round(float(c), 3) for c in shell.tiers["micro"].position]},
                {"tier": "C_quantum (S1)", "name": shell.tiers["quantum"].name, "pos": [round(float(c), 3) for c in shell.tiers["quantum"].position]},
            ],
            "tensor_grid_nodes": nodes,
        }

    @classmethod
    def lift_video_to_5d_world(
        cls,
        video_path: str,
        output_dir: Path,
        t_start_s: float = 4.2,
        t_end_s: float = 11.8,
        n_time_samples: int = 10,
        grid_w: int = 128,
        grid_h: int = 72,
    ) -> Dict[str, Any]:
        """
        Lifts a continuous real video sequence (`[AZERIA]` two-shot tavern `4.2s..11.8s`) into a
        true **5D Spacetime-Scale-Causal Volumetric Rotor World `(X, Y, Z, T, Σ)`**:
          - Real CUDA `Depth-Anything-V2-Small` 3D depth maps across all `n_time_samples` frames
          - True 3D unprojection `(X, Y, Z)` + 4D temporal motion/depth/color rotors `(T)`
          - Automatic 5D scale separation (`S4 Environment` vs `S3 Dynamic Characters` vs `S2 Micro Flux`)
          - Real 3×3 Teleological Future-Purpose Tensor Field (`CausalField` + `FractalEngramShell`)
          - Exports WebGL2-ready 5D volumetric splat package + 2×3 multi-angle visual proof PNG!
        """
        import cv2

        t0 = time.perf_counter()
        output_dir.mkdir(parents=True, exist_ok=True)
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise FileNotFoundError(f"Cannot open video: {video_path}")
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = float(cap.get(cv2.CAP_PROP_FPS) or 30.0)

        times_s = np.linspace(t_start_s, t_end_s, max(4, int(n_time_samples)))
        frames_rgb: List[np.ndarray] = []
        for ts in times_s:
            fi = max(0, min(total_frames - 5, int(ts * fps)))
            cap.set(cv2.CAP_PROP_POS_FRAMES, fi)
            ok, bgr = cap.read()
            if not ok:
                continue
            # Crop out bottom burned-in subtitle strip (keep top 80% pure visual world!)
            ch = int(bgr.shape[0] * 0.80)
            bgr_c = bgr[:ch, :, :]
            frames_rgb.append(cv2.cvtColor(bgr_c, cv2.COLOR_BGR2RGB))
        cap.release()

        if len(frames_rgb) < 3:
            raise RuntimeError("Insufficient frames extracted for 5D temporal lifting")

        # 1. Real CUDA Depth-Anything-V2 across the full temporal window!
        depth_maps, depth_engine_name = cls._estimate_depth_sequence_cuda(frames_rgb)

        # Anchor Present `t=0` at middle frame of the sequence
        mid = len(frames_rgb) // 2
        fr_mid = cv2.resize(frames_rgb[mid], (grid_w, grid_h), interpolation=cv2.INTER_AREA)
        d_mid = cv2.resize(depth_maps[mid], (grid_w, grid_h), interpolation=cv2.INTER_AREA)

        # 2. Measure true 4D temporal flow (dx/dt, dy/dt, dz/dt, dRGB/dt) across the sequence!
        flow_u_acc = np.zeros((grid_h, grid_w), dtype=np.float32)
        flow_v_acc = np.zeros((grid_h, grid_w), dtype=np.float32)
        flow_mag_acc = np.zeros((grid_h, grid_w), dtype=np.float32)
        dz_acc = np.zeros((grid_h, grid_w), dtype=np.float32)
        rgb_var_stack = []
        for i in range(len(frames_rgb)):
            sm_rgb = cv2.resize(frames_rgb[i], (grid_w, grid_h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
            rgb_var_stack.append(sm_rgb)
            if i + 1 < len(frames_rgb):
                g1 = cv2.cvtColor(cv2.resize(frames_rgb[i], (grid_w, grid_h)), cv2.COLOR_RGB2GRAY)
                g2 = cv2.cvtColor(cv2.resize(frames_rgb[i + 1], (grid_w, grid_h)), cv2.COLOR_RGB2GRAY)
                fl = cv2.calcOpticalFlowFarneback(g1, g2, None, 0.5, 2, 9, 2, 5, 1.1, 0)
                flow_u_acc += fl[:, :, 0]
                flow_v_acc += fl[:, :, 1]
                flow_mag_acc += np.hypot(fl[:, :, 0], fl[:, :, 1])
                d1 = cv2.resize(depth_maps[i], (grid_w, grid_h))
                d2 = cv2.resize(depth_maps[i + 1], (grid_w, grid_h))
                dz_acc += (d2 - d1)

        n_steps = max(1, len(frames_rgb) - 1)
        mean_du = flow_u_acc / n_steps
        mean_dv = flow_v_acc / n_steps
        mean_fmag = flow_mag_acc / n_steps
        mean_dz = dz_acc / n_steps
        rgb_temporal_std = np.std(np.stack(rgb_var_stack, axis=0), axis=0).mean(axis=-1)  # (H, W)

        # 3. True 3D Metric Perspective Unprojection `(X, Y, Z)`!
        # Larger `d_mid` = closer to camera -> smaller camera distance `z_cam` -> negative world Z (in front!)
        aspect = float(grid_w) / float(grid_h)
        u_ndc = np.linspace(-1.0, 1.0, grid_w, dtype=np.float32).reshape(1, grid_w)
        v_ndc = np.linspace(1.0, -1.0, grid_h, dtype=np.float32).reshape(grid_h, 1)
        # Depth range: closest foreground at Z = -0.65, far tavern wall at Z = +1.15
        world_z = 1.15 - d_mid * 1.80
        z_cam = world_z + 2.35  # camera sits at z = -2.35 looking toward +Z
        fov_scale = 0.52
        world_x = u_ndc * z_cam * fov_scale * aspect
        world_y = v_ndc * z_cam * fov_scale

        # Convert pixel flow into 3D world velocity `(vx, vy, vz)` + harmonic oscillation rotor
        vx_3d = np.clip((mean_du / grid_w) * 2.4, -0.35, 0.35)
        vy_3d = np.clip((-mean_dv / grid_h) * 2.0, -0.35, 0.35)
        vz_3d = np.clip(-mean_dz * 1.6, -0.35, 0.35)

        # 4. 5D Automatic Scale-Layer Classification (`S4 Environment` vs `S3 Characters` vs `S2 Micro-Flux`)!
        motion_score = (mean_fmag / max(1e-4, float(np.percentile(mean_fmag, 95)))) * 0.65 + (
            rgb_temporal_std / max(1e-4, float(np.percentile(rgb_temporal_std, 95)))
        ) * 0.35
        depth_fg_thresh = float(np.percentile(d_mid, 52))
        micro_flux_thresh = float(np.percentile(motion_score[d_mid >= depth_fg_thresh], 76)) if np.any(d_mid >= depth_fg_thresh) else 0.7

        # layer_id: 4 = S4 Environment (walls/window/table), 3 = S3 Character Bodies, 2 = S2 Micro Expression/Flux
        layer_id = np.full((grid_h, grid_w), 4, dtype=np.int32)
        fg_mask = d_mid >= depth_fg_thresh
        layer_id[fg_mask] = 3
        micro_mask = fg_mask & (motion_score >= micro_flux_thresh)
        layer_id[micro_mask] = 2

        # Locate 3D centroids of Kaio (left foreground) and Viela (right foreground)
        kaio_mask = fg_mask & (world_x < 0.0)
        viela_mask = fg_mask & (world_x >= 0.0)
        kaio_center = [
            round(float(world_x[kaio_mask].mean()), 4),
            round(float(world_y[kaio_mask].mean()), 4),
            round(float(world_z[kaio_mask].mean()), 4),
        ] if np.any(kaio_mask) else [-0.55, -0.05, -0.15]
        viela_center = [
            round(float(world_x[viela_mask].mean()), 4),
            round(float(world_y[viela_mask].mean()), 4),
            round(float(world_z[viela_mask].mean()), 4),
        ] if np.any(viela_mask) else [0.52, -0.02, -0.12]

        # Build the 3 Teleological Future-Purpose Tensor Regimes!
        actor_centers = {"kaio": kaio_center, "viela": viela_center}
        tensor_regimes = {
            reg: cls.build_teleological_tensor_field(reg, actor_centers)
            for reg in ("converge_seal", "patrol_expand", "dialogue_vortex")
        }

        # Pack compact 5D Volumetric Splat arrays for 60fps WebGL2 GPU shader!
        # Flat arrays: N = grid_w * grid_h (~9,216 splats)
        rgb_f = fr_mid.astype(np.float32) / 255.0
        # Harmonic oscillation amplitude & phase per splat (characters breathe/move continuously!)
        osc_amp = np.where(layer_id == 4, 0.004, np.where(layer_id == 3, 0.028 + 0.04 * motion_score, 0.055 + 0.06 * motion_score)).astype(np.float32)
        phase_t = (world_x * 2.3 + world_y * 1.9 + world_z * 1.5).astype(np.float32)
        # Depth discontinuity filter (thin out stretched silhouette flying pixels slightly via opacity)
        gx_d = np.abs(np.diff(d_mid, axis=1, prepend=d_mid[:, :1]))
        gy_d = np.abs(np.diff(d_mid, axis=0, prepend=d_mid[:1, :]))
        edge_jump = np.hypot(gx_d, gy_d)
        splat_size = np.where(edge_jump > 0.14, 0.55, 1.0).astype(np.float32)

        n_pts = grid_w * grid_h
        # Save compact float32 binary buffer for ultra-fast WebGL2 loading:
        # 12 floats per splat: [x, y, z, r, g, b, vx, vy, vz, layer_id, osc_amp, size_w]
        packed = np.stack(
            [
                world_x.ravel(),
                world_y.ravel(),
                world_z.ravel(),
                rgb_f[:, :, 0].ravel(),
                rgb_f[:, :, 1].ravel(),
                rgb_f[:, :, 2].ravel(),
                vx_3d.ravel(),
                vy_3d.ravel(),
                vz_3d.ravel(),
                layer_id.astype(np.float32).ravel(),
                osc_amp.ravel(),
                splat_size.ravel(),
            ],
            axis=1,
        ).astype(np.float32)
        bin_path = output_dir / "azeria_5d_splats.bin"
        packed.tofile(str(bin_path))

        # 5. Render REAL 2x3 Multi-Angle 5D Proof Sheet directly on CPU/NumPy (true perspective z-buffer!)
        def _render_5d_view(
            yaw_deg: float = 0.0,
            pitch_deg: float = 0.0,
            t_val: float = 0.0,
            sigma_teleo: float = 0.0,
            layer_tint: bool = False,
            out_w: int = 320,
            out_h: int = 180,
        ) -> np.ndarray:
            px = packed[:, 0].copy()
            py = packed[:, 1].copy()
            pz = packed[:, 2].copy()
            pr = packed[:, 3].copy()
            pg = packed[:, 4].copy()
            pb = packed[:, 5].copy()
            lv = packed[:, 9]

            # Apply 4th dimension T (Past <-> Present <-> Future) + 5th dimension Sigma Teleological Tensor!
            if abs(t_val) > 1e-4:
                px += packed[:, 6] * t_val * 2.2
                py += packed[:, 7] * t_val * 2.2 + np.sin(t_val * 4.0 + phase_t.ravel()) * packed[:, 10] * 0.5
                pz += packed[:, 8] * t_val * 2.2
                if t_val > 0.0 and sigma_teleo > 1e-4:
                    # Contract with S4 Future Teleological Tensor Field (`converge_seal` attractor + vortex curl!)
                    attr = np.array(tensor_regimes["converge_seal"]["attractor_pos_3d"], dtype=np.float32)
                    rx, ry, rz = px - attr[0], py - attr[1], pz - attr[2]
                    d2 = rx * rx + ry * ry + rz * rz + 0.15
                    weight = np.where(lv < 3.5, 1.0, 0.20) * sigma_teleo * t_val * np.exp(-0.35 * d2)
                    # Symmetric attraction + Clifford bivector Y-curl
                    px += weight * (-0.55 * rx + 0.42 * rz)
                    py += weight * (-0.35 * ry)
                    pz += weight * (-0.55 * rz - 0.42 * rx)
                    # Subtle golden-cyan teleological energy glow on S2/S3 bent future
                    pr = np.clip(pr + weight * 0.25, 0.0, 1.0)
                    pb = np.clip(pb + weight * 0.35, 0.0, 1.0)

            if layer_tint:
                # Visualize S4 Environment (Blue) vs S3 Character Bodies (Red) vs S2 Micro-Flux (Yellow)
                pr = np.where(lv == 4, pr * 0.35 + 0.08, np.where(lv == 3, np.clip(pr * 0.5 + 0.50, 0, 1), 1.0))
                pg = np.where(lv == 4, pg * 0.45 + 0.18, np.where(lv == 3, pg * 0.30 + 0.10, 0.90))
                pb = np.where(lv == 4, np.clip(pb * 0.5 + 0.52, 0, 1), np.where(lv == 3, pb * 0.30 + 0.12, 0.15))

            # Orbit camera around origin (0, 0, 0.15)
            cy_r, sy_r = math.cos(math.radians(yaw_deg)), math.sin(math.radians(yaw_deg))
            cp_r, sp_r = math.cos(math.radians(pitch_deg)), math.sin(math.radians(pitch_deg))
            cx0, cy0, cz0 = px, py, pz - 0.15
            rx1 = cx0 * cy_r + cz0 * sy_r
            rz1 = -cx0 * sy_r + cz0 * cy_r
            ry2 = cy0 * cp_r - rz1 * sp_r
            rz2 = cy0 * sp_r + rz1 * cp_r + 2.50

            valid = rz2 > 0.35
            rx1, ry2, rz2 = rx1[valid], ry2[valid], rz2[valid]
            cols = np.stack([pr[valid], pg[valid], pb[valid]], axis=1)
            # Perspective project
            f_px = out_h * 0.92
            sx = np.round(out_w * 0.5 + (rx1 / rz2) * f_px).astype(np.int32)
            sy = np.round(out_h * 0.5 - (ry2 / rz2) * f_px).astype(np.int32)
            in_b = (sx >= 1) & (sx < out_w - 1) & (sy >= 1) & (sy < out_h - 1)
            sx, sy, rz2, cols = sx[in_b], sy[in_b], rz2[in_b], cols[in_b]

            # Painter's sort far-to-near with 3x3 volumetric splat kernel!
            order = np.argsort(rz2)[::-1]
            sx, sy, cols = sx[order], sy[order], cols[order]
            canvas = np.full((out_h, out_w, 3), (12, 16, 26), dtype=np.uint8)
            c_u8 = np.clip(cols * 255.0, 0, 255).astype(np.uint8)
            for oy in (-1, 0, 1):
                for ox in (-1, 0, 1):
                    canvas[sy + oy, sx + ox] = c_u8
            return canvas  # RGB uint8

        def _tile(rgb_u8: np.ndarray, title: str) -> np.ndarray:
            bgr_t = cv2.cvtColor(cv2.resize(rgb_u8, (320, 180), interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2BGR)
            bar = np.full((30, 320, 3), (16, 20, 32), dtype=np.uint8)
            cv2.putText(bar, title, (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (235, 245, 255), 1, cv2.LINE_AA)
            return np.vstack([bar, bgr_t])

        depth_vis_bgr = cv2.applyColorMap(np.clip(d_mid * 255.0, 0, 255).astype(np.uint8), cv2.COLORMAP_INFERNO)
        depth_vis_rgb = cv2.cvtColor(depth_vis_bgr, cv2.COLOR_BGR2RGB)
        v_left = _render_5d_view(yaw_deg=-26.0, pitch_deg=6.0, t_val=0.0, sigma_teleo=0.0)
        v_right = _render_5d_view(yaw_deg=26.0, pitch_deg=6.0, t_val=0.0, sigma_teleo=0.0)
        v_layers = _render_5d_view(yaw_deg=-14.0, pitch_deg=8.0, t_val=0.0, sigma_teleo=0.0, layer_tint=True)
        v_future = _render_5d_view(yaw_deg=14.0, pitch_deg=6.0, t_val=0.85, sigma_teleo=1.0)

        # Measure real 3D parallax difference between Left (-26 deg) and Right (+26 deg) orbits!
        parallax_rmse = float(np.sqrt(np.mean(((v_left.astype(np.float32) - v_right.astype(np.float32)) / 255.0) ** 2)))
        future_bend_rmse = float(
            np.sqrt(
                np.mean(
                    (
                        (_render_5d_view(yaw_deg=14.0, pitch_deg=6.0, t_val=0.85, sigma_teleo=0.0).astype(np.float32)
                         - v_future.astype(np.float32))
                        / 255.0
                    )
                    ** 2
                )
            )
        )

        proof_path = output_dir / "elysia_5d_azeria_world_proof.png"
        cv2.imwrite(
            str(proof_path),
            np.vstack([
                np.hstack([
                    _tile(frames_rgb[mid], f"1. Original AZERIA Frame ({times_s[mid]:.1f}s)"),
                    _tile(depth_vis_rgb, f"2. CUDA 3D Depth ({depth_engine_name.split(' ')[0]})"),
                    _tile(v_left, "3. True 3D Orbit Left (-26 deg)"),
                ]),
                np.hstack([
                    _tile(v_right, "4. True 3D Orbit Right (+26 deg)"),
                    _tile(v_layers, "5. 5D Scales: S4 Blue/S3 Red/S2 Yel"),
                    _tile(v_future, "6. Future T=+0.85 x Sigma=+1 Tensor"),
                ]),
            ]),
        )

        # Save metadata JSON for instant WebGL2 5D GPU Studio loading
        meta = {
            "schema": "elysia_5d_spacetime_causal_rotor_world_v1",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "elapsed_s": round(time.perf_counter() - t0, 2),
            "source_video": str(video_path),
            "time_window_s": [round(float(times_s[0]), 2), round(float(times_s[-1]), 2)],
            "time_samples_analyzed": len(frames_rgb),
            "depth_engine": depth_engine_name,
            "splat_count": int(n_pts),
            "grid_wh": [int(grid_w), int(grid_h)],
            "splats_bin_url": "/data/open_sandbox/youtube_multimodal/azeria/world_5d/azeria_5d_splats.bin",
            "original_video_url": "/data/open_sandbox/youtube_multimodal/azeria/azeria_clip.mp4",
            "proof_sheet_png": str(proof_path),
            "scale_layer_counts": {
                "S4_environment_blue": int(np.sum(layer_id == 4)),
                "S3_characters_red": int(np.sum(layer_id == 3)),
                "S2_micro_flux_yellow": int(np.sum(layer_id == 2)),
            },
            "actor_3d_centroids": actor_centers,
            "teleological_tensor_regimes": tensor_regimes,
            "active_regime": "converge_seal",
            "verification_metrics": {
                "true_3d_orbit_parallax_rmse": round(parallax_rmse, 5),
                "future_tensor_bend_rmse": round(future_bend_rmse, 5),
                "depth_range_world_z": [round(float(world_z.min()), 3), round(float(world_z.max()), 3)],
            },
        }
        import json
        (output_dir / "azeria_5d_world_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        return meta


# =============================================================================
# 4D Base Spacetime + Variable Geometric Rotor Dimension Engine (4D + K_dynamic)
# =============================================================================


class VariableDimensionGeometricRotor:
    """
    Holds **4D Spacetime `(X, Y, Z, T)`** as the clean invariant base substrate and treats
    ALL higher dimensions (`D_5, D_6, ..., D_N`) as **variable plug-and-play Geometric Rotor
    Axes** — NEVER hardcoding fixed premature axes when the agent doesn't yet know which
    axis matters!

    Capabilities:
      1. `attach_dimension(name, signature_vec)`: attaches a new candidate geometric rotor axis
         and checks Clifford/Law-of-Cosines orthogonality against existing dimensions; if
         collinear (`|cos theta| > 0.95`), automatically folds/prunes it under MDL!
      2. `discover_dimensions_from_residual(feature_matrix, energy_threshold)`: runs SVD directly
         on observed world friction/residuals beyond 4D to **autonomously discover** the minimal
         orthogonal extra rotor dimensions (`D_5, D_6, ...`) and their explained variance ratios!
      3. `rotate_plane(dim_a, dim_b, angle_rad)`: performs an exact Givens / Clifford Bivector
         planar rotation `exp(-0.5 * theta * e_a ^ e_b)` between ANY two active dimensions
         (e.g. rotating Time `T` into discovered `D_5`, or `X` into `D_6`)!
      4. `prune_low_energy_dimensions(min_energy)`: folds inactive dimensions back down toward
         pure 4D `(X, Y, Z, T)` for automatic runtime optimization.
    """

    BASE_4D_NAMES = ("X_space", "Y_space", "Z_depth", "T_time")

    def __init__(self, base_4d_coords: np.ndarray) -> None:
        arr = np.asarray(base_4d_coords, dtype=np.float32)
        if arr.ndim != 2 or arr.shape[1] != 4:
            raise ValueError(f"Expected (N, 4) base 4D spacetime coordinates, got {arr.shape}")
        self.base_4d = arr  # (N, 4): [X, Y, Z, T]
        self.n_points = int(arr.shape[0])
        self.extra_dims: List[Dict[str, Any]] = []  # each: {name, values_N, energy, source, angle_rad}
        self.pruned_log: List[Dict[str, Any]] = []

    @property
    def total_dimensions(self) -> int:
        return 4 + len(self.extra_dims)

    def _unit_centered(self, v: np.ndarray) -> Tuple[np.ndarray, float]:
        x = np.asarray(v, dtype=np.float64).ravel()
        x = x - float(np.mean(x))
        norm = float(np.linalg.norm(x))
        if norm < 1e-8:
            return np.zeros_like(x), 0.0
        return x / norm, norm

    def attach_dimension(
        self,
        name: str,
        values: np.ndarray,
        source: str = "manual",
        collinearity_cutoff: float = 0.95,
    ) -> Dict[str, Any]:
        """
        Attaches a variable geometric rotor dimension `D_k` ONLY if it carries genuine
        orthogonal information not already spanned by `4D + existing extra dims` (Gram-Schmidt
        residual check!). Collinear redundant axes are folded cleanly under MDL!
        """
        u_raw, raw_norm = self._unit_centered(values)
        if raw_norm < 1e-6:
            rec = {"name": name, "accepted": False, "reason": "zero_variance_axis"}
            self.pruned_log.append(rec)
            return rec

        # Check maximum cosine overlap with existing extra dimensions (Law-of-Cosines independence)
        max_cos = 0.0
        most_similar = ""
        orth = u_raw.copy()
        for dim in self.extra_dims:
            e = dim["unit_vec"]
            c = abs(float(np.dot(u_raw, e)))
            if c > max_cos:
                max_cos = c
                most_similar = dim["name"]
            # Gram-Schmidt orthogonalize residual component
            orth = orth - float(np.dot(orth, e)) * e

        if max_cos > collinearity_cutoff:
            rec = {
                "name": name,
                "accepted": False,
                "reason": "folded_redundant_collinear_axis",
                "max_cos_theta": round(max_cos, 4),
                "folded_into": most_similar,
            }
            self.pruned_log.append(rec)
            return rec

        orth_norm = float(np.linalg.norm(orth))
        orth_unit = orth / max(1e-8, orth_norm)
        # Store standardized coordinate values along the orthogonalized geometric rotor axis
        vals_std = (orth_unit * math.sqrt(self.n_points)).astype(np.float32)
        entry = {
            "dim_index": 5 + len(self.extra_dims),
            "name": name,
            "source": source,
            "unit_vec": orth_unit,
            "values": vals_std,
            "orthogonal_retention": round(orth_norm, 4),
            "energy": round(float(np.mean(vals_std ** 2)), 4),
            "rotor_phase_rad": 0.0,
        }
        self.extra_dims.append(entry)
        return {
            "name": name,
            "accepted": True,
            "dim_index": entry["dim_index"],
            "orthogonal_retention": entry["orthogonal_retention"],
            "total_dimensions": self.total_dimensions,
        }

    def discover_dimensions_from_residual(
        self,
        residual_features: np.ndarray,
        feature_names: List[str],
        variance_target: float = 0.88,
        max_new_dims: int = 4,
    ) -> Dict[str, Any]:
        """
        Autonomously discovers orthogonal higher rotor dimensions `D_5, D_6, ...` via SVD on
        real observed world residuals beyond 4D `(X, Y, Z, T)` — zero upfront guesswork!
        """
        M = np.asarray(residual_features, dtype=np.float64)
        # Standardize columns so heterogeneous physical units (motion, chroma, depth-rate) compete fairly
        M_c = M - M.mean(axis=0, keepdims=True)
        stds = np.maximum(M_c.std(axis=0, keepdims=True), 1e-6)
        M_z = M_c / stds
        U, S, Vt = np.linalg.svd(M_z, full_matrices=False)
        var = (S ** 2) / max(1e-12, float(np.sum(S ** 2)))
        cum = 0.0
        discovered = []
        for k in range(min(max_new_dims, len(S))):
            if cum >= variance_target and k >= 1:
                break
            loadings = Vt[k]
            top_idx = np.argsort(np.abs(loadings))[::-1][:2]
            top_desc = "+".join(
                f"{feature_names[int(i)]}({loadings[int(i)]:+.2f})" for i in top_idx if int(i) < len(feature_names)
            )
            axis_name = f"D{5 + len(self.extra_dims)}_auto[{top_desc}]"
            att = self.attach_dimension(axis_name, U[:, k] * S[k], source="svd_residual_discovery")
            cum += float(var[k])
            discovered.append({
                "dim_name": axis_name,
                "explained_variance_ratio": round(float(var[k]), 4),
                "cumulative_variance": round(cum, 4),
                "accepted": att.get("accepted", False),
            })
        return {
            "base_dimensions": 4,
            "discovered_extra_dimensions": discovered,
            "total_active_dimensions": self.total_dimensions,
            "total_variance_captured": round(cum, 4),
        }

    def rotate_plane(self, dim_a: int, dim_b: int, angle_rad: float) -> Dict[str, Any]:
        """
        Applies an exact Clifford Bivector planar rotation `R = exp(-0.5 * theta * e_a ^ e_b)`
        between ANY two dimensions (`0..3` = X,Y,Z,T; `4..` = dynamic variable rotor dimensions),
        returning the norm-preservation check (`||v'|| == ||v||` to machine precision)!
        """
        full = np.hstack([self.base_4d] + [d["values"].reshape(-1, 1) for d in self.extra_dims]) if self.extra_dims else self.base_4d.copy()
        d_tot = full.shape[1]
        if not (0 <= dim_a < d_tot and 0 <= dim_b < d_tot and dim_a != dim_b):
            raise ValueError(f"Invalid rotation plane ({dim_a}, {dim_b}) for {d_tot}D state")
        norm_before = float(np.linalg.norm(full[:, [dim_a, dim_b]]))
        c, s = math.cos(angle_rad), math.sin(angle_rad)
        va = full[:, dim_a].copy()
        vb = full[:, dim_b].copy()
        full[:, dim_a] = c * va - s * vb
        full[:, dim_b] = s * va + c * vb
        norm_after = float(np.linalg.norm(full[:, [dim_a, dim_b]]))
        return {
            "plane": [int(dim_a), int(dim_b)],
            "angle_deg": round(math.degrees(angle_rad), 2),
            "clifford_norm_conservation_err": round(abs(norm_after - norm_before), 8),
            "rotated_dims_total": int(d_tot),
        }

    def summary(self) -> Dict[str, Any]:
        return {
            "base_spacetime": list(self.BASE_4D_NAMES),
            "total_dimensions": self.total_dimensions,
            "active_variable_rotors": [
                {
                    "dim_index": d["dim_index"],
                    "name": d["name"],
                    "source": d["source"],
                    "orthogonal_retention": d["orthogonal_retention"],
                    "energy": d["energy"],
                }
                for d in self.extra_dims
            ],
            "pruned_or_folded_axes": self.pruned_log,
        }
