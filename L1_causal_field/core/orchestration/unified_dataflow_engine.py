"""
Elysia Unified Causal Dataflow Engine (통합 인과 데이터플로우 엔진)
====================================================================
Pure Python stdlib (zero third-party dependencies) implementation uniting
ALL THREE domains into ONE shared causal dataflow kernel:

1. Code -> Branchless Transistor / Sluice Circuit (if/else -> sigmoid gates):
   Safely parses real Python `if/elif/else` logic via a strict AST whitelist
   (zero eval/exec!) and compiles every discrete conditional branch into a
   continuous differentiable transistor gate:
       g = sigmoid(k * (lhs - rhs))
       y = g * true_branch + (1 - g) * false_branch
   Evaluates BOTH discrete branch execution and branchless gate execution
   simultaneously to prove exact equivalence at high k and smooth analog
   blending at low k.

2. Multi-Scale Gear-Ratio Compute Optimization (Macro -> Meso -> Micro):
   3-tier hierarchy (S0: 8x8 -> S1: 16x16 -> S2: 32x32 = 1024 fine cells).
   Only blocks where the coarse macro gear's spatial curvature or temporal
   delta exceeds the engagement threshold wake up fine meso/micro cells.
   Calm regions propagate analytically via bilinear gear interpolation at
   zero fine-grid cost — measuring exact cell savings and reconstruction
   fidelity against a naive 100% brute-force micro evaluation.

3. Signal / Audio Harmonic Condensation (Exact Radix-2 FFT Compression):
   Extracts a 256-sample continuous acoustic waveform directly from the same
   unified spatial field, runs an exact radix-2 Cooley-Tukey FFT, condenses
   it to K dominant harmonic seeds (freq, amp, phase), reconstructs via IFFT,
   and sends those exact harmonic seeds directly to the browser Web Audio synth.

4. Closed-Loop Perceptual Eye & Cross-Domain Integration:
   Inspects actual reconstruction error across space & signal, automatically
   tunes gate steepness & gear wake threshold when auto-eye is enabled,
   computes the real 3-domain cross-coupling matrix
   (Code Circuit <-> 3D Spatial Field <-> Acoustic Spectrum), and syncs back
   into the canonical L1 Scale-Rotor engine.
"""

from __future__ import annotations

import ast
import cmath
import math
import time
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Curated Multi-Domain Presets (Real Python if/else Rules)
# ---------------------------------------------------------------------------
DATAFLOW_PRESETS: Dict[str, Dict[str, Any]] = {
    "wave_interference": {
        "id": "wave_interference",
        "title": "파동·간섭 회로",
        "subtitle": "이중 파동 에너지 조건이 3D 빛 파동장과 배음 화음을 동시 구동",
        "base_freq_hz": 174.0,
        "code": (
            "# 공간 좌표 (x, y), 반경 r, 시간 위상 t 입력\n"
            "wave = sin(x * 2.6 + t) * cos(y * 2.4 - t * 0.7)\n"
            "ripple = sin(r * 4.2 - t * 1.4) * exp(-r * 0.45)\n"
            "if wave + ripple > 0.18:\n"
            "    field = 0.85 * wave + 0.95 * ripple + 0.25\n"
            "    temp = 0.82\n"
            "else:\n"
            "    field = 0.35 * wave - 0.55 * ripple - 0.15\n"
            "    temp = 0.22\n"
        ),
    },
    "thermal_bifurcation": {
        "id": "thermal_bifurcation",
        "title": "열·상전이 분기",
        "subtitle": "임계 온도 수문이 액체 흐름과 결정 경계를 동시에 가르고 저음 공명을 생성",
        "base_freq_hz": 130.81,
        "code": (
            "# 열 구배와 압력 경계에 따른 2상 분기 회로\n"
            "heat = exp(-r * r * 0.65) + 0.35 * sin(x * 2.0 + t * 0.9)\n"
            "if heat > 0.52:\n"
            "    field = heat * 1.15 + 0.28 * cos(y * 3.1 - t)\n"
            "    temp = 0.94\n"
            "else:\n"
            "    if r > 1.05:\n"
            "        field = -0.45 * tanh(r - 1.0) + 0.18 * sin(x * 3.0)\n"
            "        temp = 0.12\n"
            "    else:\n"
            "        field = 0.22 * cos(r * 3.5 + t * 0.6)\n"
            "        temp = 0.46\n"
        ),
    },
    "vortex_resonance": {
        "id": "vortex_resonance",
        "title": "소용돌이·공명장",
        "subtitle": "각운동량 조건이 3D 나선 은하 스플랫과 아르페지오 배음을 하나로 결속",
        "base_freq_hz": 220.0,
        "code": (
            "# 중심 소용돌이 공명 조건 회로\n"
            "spiral = sin(r * 3.6 - t * 1.2 + x * 1.1 - y * 1.1)\n"
            "core = exp(-r * 0.72)\n"
            "if core + 0.45 * spiral > 0.42:\n"
            "    field = (0.75 * spiral + 0.95 * core)\n"
            "    temp = 0.88\n"
            "else:\n"
            "    field = 0.30 * spiral * core - 0.28 * sin(r * 2.0)\n"
            "    temp = 0.18\n"
        ),
    },
}

MAX_CODE_CHARS = 2000
MAX_AST_NODES = 180
MAX_AST_DEPTH = 14


def _clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else (hi if v > hi else v)


def _safe_exp(v: float) -> float:
    return math.exp(_clamp(v, -12.0, 12.0))


def _safe_sqrt(v: float) -> float:
    return math.sqrt(v if v > 0.0 else 0.0)


def _safe_sigmoid(v: float) -> float:
    if v >= 40.0:
        return 1.0
    if v <= -40.0:
        return 0.0
    return 1.0 / (1.0 + math.exp(-v))


ALLOWED_FUNCS: Dict[str, Callable[[float], float]] = {
    "sin": math.sin,
    "cos": math.cos,
    "tanh": math.tanh,
    "abs": abs,
    "sqrt": _safe_sqrt,
    "exp": _safe_exp,
}


def _validate_ast_safety(tree: ast.AST) -> None:
    """Strict AST security whitelist: zero imports, attributes, subscripts, or arbitrary calls."""
    nodes = list(ast.walk(tree))
    if len(nodes) > MAX_AST_NODES:
        raise ValueError(f"코드 구조가 너무 큽니다 (최대 {MAX_AST_NODES} 노드).")

    allowed_node_types = (
        ast.Module,
        ast.Assign,
        ast.If,
        ast.Compare,
        ast.BinOp,
        ast.UnaryOp,
        ast.Name,
        ast.Load,
        ast.Store,
        ast.Constant,
        ast.Call,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.UAdd,
        ast.USub,
        ast.Gt,
        ast.GtE,
        ast.Lt,
        ast.LtE,
    )

    for node in nodes:
        if not isinstance(node, allowed_node_types):
            raise ValueError(f"허용되지 않은 파이썬 구문입니다: {type(node).__name__}")
        if isinstance(node, ast.Name):
            if node.id.startswith("_"):
                raise ValueError(f"내부 식별자는 사용할 수 없습니다: {node.id}")
        elif isinstance(node, ast.Constant):
            if not isinstance(node.value, (int, float)) or isinstance(node.value, bool):
                raise ValueError("숫자 상수(int/float)만 허용됩니다.")
        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in ALLOWED_FUNCS:
                fn = node.func.id if isinstance(node.func, ast.Name) else type(node.func).__name__
                raise ValueError(f"허용된 수학 함수(sin, cos, tanh, abs, sqrt, exp)만 사용 가능합니다: {fn}")
            if len(node.args) != 1 or node.keywords:
                raise ValueError("수학 함수는 단일 인자만 허용됩니다.")
        elif isinstance(node, ast.Assign):
            if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
                raise ValueError("단일 변수 대입만 허용됩니다.")
        elif isinstance(node, ast.Compare):
            if len(node.ops) != 1 or len(node.comparators) != 1:
                raise ValueError("단일 비교식(a > b, a < b 등)만 허용됩니다.")

    def _check_depth(n: ast.AST, depth: int = 0) -> None:
        if depth > MAX_AST_DEPTH:
            raise ValueError("식 중첩 깊이가 제한을 초과했습니다.")
        for child in ast.iter_child_nodes(n):
            _check_depth(child, depth + 1)

    _check_depth(tree)


def _eval_expr_scalar(node: ast.AST, env: Dict[str, float]) -> float:
    if isinstance(node, ast.Constant):
        return float(node.value)
    if isinstance(node, ast.Name):
        if node.id not in env:
            raise ValueError(f"정의되지 않은 변수입니다: {node.id}")
        return env[node.id]
    if isinstance(node, ast.UnaryOp):
        v = _eval_expr_scalar(node.operand, env)
        return -v if isinstance(node.op, ast.USub) else v
    if isinstance(node, ast.BinOp):
        left = _eval_expr_scalar(node.left, env)
        right = _eval_expr_scalar(node.right, env)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            denom = right if abs(right) >= 1e-6 else (1e-6 if right >= 0.0 else -1e-6)
            return _clamp(left / denom, -1e4, 1e4)
        if isinstance(node.op, ast.Pow):
            return math.pow(_clamp(abs(left), 0.0, 100.0), _clamp(right, -4.0, 4.0))
        raise ValueError(f"지원하지 않는 연산자: {type(node.op).__name__}")
    if isinstance(node, ast.Call):
        return ALLOWED_FUNCS[node.func.id](_eval_expr_scalar(node.args[0], env))
    raise ValueError(f"지원하지 않는 표현식: {type(node).__name__}")


def _exec_stmts_scalar(
    stmts: List[ast.stmt],
    env: Dict[str, float],
    steepness: float,
    discrete: bool,
    gate_stats: Optional[List[Dict[str, Any]]] = None,
    gate_cursor: Optional[List[int]] = None,
) -> Dict[str, float]:
    cur = dict(env)
    for stmt in stmts:
        if isinstance(stmt, ast.Assign):
            name = stmt.targets[0].id
            cur[name] = _clamp(_eval_expr_scalar(stmt.value, cur), -10.0, 10.0)
        elif isinstance(stmt, ast.If):
            if not isinstance(stmt.test, ast.Compare):
                raise ValueError("if 조건은 비교식(예: wave > 0.2)이어야 합니다.")
            lhs = _eval_expr_scalar(stmt.test.left, cur)
            rhs = _eval_expr_scalar(stmt.test.comparators[0], cur)
            op = stmt.test.ops[0]

            if isinstance(op, (ast.Gt, ast.GtE)):
                margin = lhs - rhs
                op_str = ">" if isinstance(op, ast.Gt) else ">="
            elif isinstance(op, (ast.Lt, ast.LtE)):
                margin = rhs - lhs
                op_str = "<" if isinstance(op, ast.Lt) else "<="
            else:
                raise ValueError(f"지원하지 않는 비교 연산자: {type(op).__name__}")

            if discrete:
                if isinstance(op, ast.Gt):
                    gate = 1.0 if lhs > rhs else 0.0
                elif isinstance(op, ast.GtE):
                    gate = 1.0 if lhs >= rhs else 0.0
                elif isinstance(op, ast.Lt):
                    gate = 1.0 if lhs < rhs else 0.0
                else:
                    gate = 1.0 if lhs <= rhs else 0.0
            else:
                gate = _safe_sigmoid(steepness * margin)
                if gate_stats is not None and gate_cursor is not None:
                    gid = gate_cursor[0]
                    gate_cursor[0] += 1
                    if gid >= len(gate_stats):
                        lhs_s = ast.unparse(stmt.test.left)
                        rhs_s = ast.unparse(stmt.test.comparators[0])
                        gate_stats.append(
                            {
                                "gate_id": f"G{gid + 1}",
                                "expr": f"{lhs_s} {op_str} {rhs_s}",
                                "compiled_formula": f"σ({steepness:.1f} · ({lhs_s} - {rhs_s}))",
                                "steepness": round(steepness, 2),
                                "sum_gate": 0.0,
                                "analog_hits": 0,
                                "count": 0,
                            }
                        )
                    st = gate_stats[gid]
                    st["sum_gate"] += gate
                    if 0.08 < gate < 0.92:
                        st["analog_hits"] += 1
                    st["count"] += 1

            env_true = _exec_stmts_scalar(stmt.body, cur, steepness, discrete, gate_stats, gate_cursor)
            env_false = (
                _exec_stmts_scalar(stmt.orelse, cur, steepness, discrete, gate_stats, gate_cursor)
                if stmt.orelse
                else dict(cur)
            )
            all_keys = set(cur.keys()) | set(env_true.keys()) | set(env_false.keys())
            inv_gate = 1.0 - gate
            merged: Dict[str, float] = {}
            for k in all_keys:
                vt = env_true.get(k, cur.get(k, 0.0))
                vf = env_false.get(k, cur.get(k, 0.0))
                merged[k] = gate * vt + inv_gate * vf
            cur = merged
    return cur


def _parse_safe_circuit(code_source: str) -> Tuple[ast.Module, int]:
    src = (code_source or "").strip()
    if not src:
        raise ValueError("실행할 코드가 비어 있습니다.")
    if len(src) > MAX_CODE_CHARS:
        raise ValueError(f"코드 길이는 최대 {MAX_CODE_CHARS}자까지 허용됩니다.")
    tree = ast.parse(src, mode="exec")
    _validate_ast_safety(tree)
    branch_count = sum(1 for n in ast.walk(tree) if isinstance(n, ast.If))
    return tree, branch_count


def _linspace(lo: float, hi: float, n: int) -> List[float]:
    if n <= 1:
        return [lo]
    step = (hi - lo) / (n - 1)
    return [lo + i * step for i in range(n)]


def _eval_point(
    tree: ast.Module,
    x: float,
    y: float,
    t_phase: float,
    steepness: float,
    discrete: bool,
    gate_stats: Optional[List[Dict[str, Any]]] = None,
) -> Tuple[float, float]:
    r = math.hypot(x, y)
    env = {"x": x, "y": y, "r": r, "t": t_phase, "field": 0.0, "temp": 0.5}
    cursor = [0] if gate_stats is not None else None
    out = _exec_stmts_scalar(tree.body, env, steepness, discrete, gate_stats, cursor)
    return _clamp(out.get("field", 0.0), -3.0, 3.0), _clamp(out.get("temp", 0.5), 0.0, 1.0)


def _eval_full_grid(
    tree: ast.Module,
    n: int,
    t_phase: float,
    steepness: float,
    discrete: bool = False,
    collect_gates: bool = False,
) -> Tuple[List[float], List[float], List[Dict[str, Any]]]:
    ax = _linspace(-2.0, 2.0, n)
    fields: List[float] = [0.0] * (n * n)
    temps: List[float] = [0.5] * (n * n)
    gate_stats: Optional[List[Dict[str, Any]]] = [] if collect_gates else None
    idx = 0
    for y in ax:
        for x in ax:
            f_val, t_val = _eval_point(tree, x, y, t_phase, steepness, discrete, gate_stats)
            fields[idx] = f_val
            temps[idx] = t_val
            idx += 1

    finalized_gates: List[Dict[str, Any]] = []
    if gate_stats:
        for st in gate_stats:
            cnt = max(1, st["count"])
            finalized_gates.append(
                {
                    "gate_id": st["gate_id"],
                    "expr": st["expr"],
                    "steepness": st["steepness"],
                    "open_ratio": round(st["sum_gate"] / cnt, 4),
                    "analog_band_ratio": round(st["analog_hits"] / cnt, 4),
                    "compiled_formula": st["compiled_formula"],
                }
            )
    return fields, temps, finalized_gates


def _upsample_2x_bilinear(coarse: Sequence[float], n: int) -> List[float]:
    m = n * 2
    out = [0.0] * (m * m)
    scale = (n - 1) / (m - 1) if m > 1 else 0.0
    for r in range(m):
        fy = r * scale
        y0 = int(fy)
        y1 = y0 + 1 if y0 + 1 < n else n - 1
        wy = fy - y0
        wy1 = 1.0 - wy
        row0 = y0 * n
        row1 = y1 * n
        out_row = r * m
        for c in range(m):
            fx = c * scale
            x0 = int(fx)
            x1 = x0 + 1 if x0 + 1 < n else n - 1
            wx = fx - x0
            top = coarse[row0 + x0] * (1.0 - wx) + coarse[row0 + x1] * wx
            bot = coarse[row1 + x0] * (1.0 - wx) + coarse[row1 + x1] * wx
            out[out_row + c] = top * wy1 + bot * wy
    return out


def _local_curvature(grid: Sequence[float], n: int) -> List[float]:
    out = [0.0] * (n * n)
    for r in range(n):
        ru = r - 1 if r > 0 else 0
        rd = r + 1 if r + 1 < n else n - 1
        for c in range(n):
            cl = c - 1 if c > 0 else 0
            cr = c + 1 if c + 1 < n else n - 1
            v = grid[r * n + c]
            up = grid[ru * n + c]
            dn = grid[rd * n + c]
            lt = grid[r * n + cl]
            rt = grid[r * n + cr]
            lap = abs(up + dn + lt + rt - 4.0 * v)
            gx = abs(rt - lt) * 0.5
            gy = abs(dn - up) * 0.5
            out[r * n + c] = 0.65 * lap + 0.35 * math.hypot(gx, gy)
    return out


def _fft_radix2(buf: List[complex], inverse: bool = False) -> List[complex]:
    """Exact iterative Cooley-Tukey radix-2 FFT/IFFT in pure Python (power-of-2 length)."""
    n = len(buf)
    a = list(buf)
    # Bit-reversal permutation
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            a[i], a[j] = a[j], a[i]

    length = 2
    sign = 1.0 if inverse else -1.0
    while length <= n:
        ang = sign * 2.0 * math.pi / length
        wlen = complex(math.cos(ang), math.sin(ang))
        half = length >> 1
        for i in range(0, n, length):
            w = 1.0 + 0.0j
            for k in range(half):
                u = a[i + k]
                v = a[i + k + half] * w
                a[i + k] = u + v
                a[i + k + half] = u - v
                w *= wlen
        length <<= 1

    if inverse:
        inv_n = 1.0 / n
        return [x * inv_n for x in a]
    return a


def _safe_corr(a: Sequence[float], b: Sequence[float]) -> float:
    n = min(len(a), len(b))
    if n < 2:
        return 0.0
    ma = sum(a[:n]) / n
    mb = sum(b[:n]) / n
    dot = 0.0
    na = 0.0
    nb = 0.0
    for i in range(n):
        da = a[i] - ma
        db = b[i] - mb
        dot += da * db
        na += da * da
        nb += db * db
    denom = math.sqrt(na * nb)
    if denom < 1e-9:
        return 0.0
    return _clamp(abs(dot / denom), 0.0, 1.0)


class UnifiedCausalDataflowEngine:
    """
    Stateful persistent engine maintaining previous macro-gear state so temporal
    deltas and closed-loop perceptual feedback evolve cleanly tick-to-tick.
    """

    def __init__(self) -> None:
        self.tick_count = 0
        self.prev_s0_field: Optional[List[float]] = None
        self.auto_wake_threshold = 0.16
        self.auto_steepness = 14.0

    def execute_cycle(
        self,
        *,
        preset_id: str = "wave_interference",
        code_source: Optional[str] = None,
        gate_steepness: float = 14.0,
        wake_threshold: float = 0.16,
        audio_harmonics: int = 6,
        t_phase: Optional[float] = None,
        auto_optimize: bool = False,
        rotor_engine: Any = None,
    ) -> Dict[str, Any]:
        t0_ns = time.perf_counter_ns()
        self.tick_count += 1

        preset = DATAFLOW_PRESETS.get(preset_id, DATAFLOW_PRESETS["wave_interference"])
        active_code = (code_source or "").strip() or preset["code"]

        k = _clamp(float(gate_steepness), 1.0, 60.0)
        thresh = _clamp(float(wake_threshold), 0.0, 0.65)
        n_harmonics = int(_clamp(float(audio_harmonics), 2.0, 16.0))
        phase = float(t_phase) if t_phase is not None else float(self.tick_count * 0.45)

        if auto_optimize:
            k = _clamp(self.auto_steepness, 2.0, 50.0)
            thresh = _clamp(self.auto_wake_threshold, 0.02, 0.50)

        # 1. Parse & validate Python if/else circuit safely (zero eval/exec!)
        tree, branch_count = _parse_safe_circuit(active_code)

        # 2. DOMAIN A — Branchless Transistor Circuit vs Discrete if/else Verification
        s2_discrete, _, _ = _eval_full_grid(tree, 32, phase, k, discrete=True, collect_gates=False)
        s2_branchless_full, _, gate_specs = _eval_full_grid(tree, 32, phase, k, discrete=False, collect_gates=True)

        diff_sq = sum((s2_discrete[i] - s2_branchless_full[i]) ** 2 for i in range(1024))
        circuit_diff_rmse = math.sqrt(diff_sq / 1024.0)
        mean_disc = sum(s2_discrete) / 1024.0
        s2_std = math.sqrt(sum((v - mean_disc) ** 2 for v in s2_discrete) / 1024.0) + 1e-6
        circuit_match_pct = _clamp((1.0 - circuit_diff_rmse / (s2_std * 2.5)) * 100.0, 0.0, 100.0)

        # 3. DOMAIN B — Multi-Scale Gear-Ratio Compute Optimization (S0 8x8 -> S1 16x16 -> S2 32x32)
        s0_field, s0_temp, _ = _eval_full_grid(tree, 8, phase, k, discrete=False, collect_gates=False)
        s0_curv = _local_curvature(s0_field, 8)
        max_s0_c = max(s0_curv) + 1e-6
        s0_curv_norm = [c / max_s0_c for c in s0_curv]

        if self.prev_s0_field is not None and len(self.prev_s0_field) == 64:
            tdeltas = [abs(s0_field[i] - self.prev_s0_field[i]) for i in range(64)]
            max_td = max(tdeltas) + 1e-6
            s0_activity = [0.72 * s0_curv_norm[i] + 0.28 * (tdeltas[i] / max_td) for i in range(64)]
        else:
            s0_activity = s0_curv_norm
        self.prev_s0_field = list(s0_field)

        # S1 Meso Gear (16x16): wake ONLY blocks whose S0 parent activity >= thresh * 0.75
        s1_field = _upsample_2x_bilinear(s0_field, 8)
        s1_temp = _upsample_2x_bilinear(s0_temp, 8)
        s1_wake_mask = [False] * 256
        s1_ax = _linspace(-2.0, 2.0, 16)
        s1_active_count = 0
        s1_thresh = thresh * 0.75
        for r in range(16):
            pr = r >> 1
            y = s1_ax[r]
            for c in range(16):
                pc = c >> 1
                idx = r * 16 + c
                if s0_activity[pr * 8 + pc] >= s1_thresh:
                    s1_wake_mask[idx] = True
                    s1_active_count += 1
                    f_val, t_val = _eval_point(tree, s1_ax[c], y, phase, k, discrete=False)
                    s1_field[idx] = f_val
                    s1_temp[idx] = t_val

        # S2 Micro Gear (32x32): wake ONLY fine cells whose S1 parent curvature >= thresh & awake
        s1_curv = _local_curvature(s1_field, 16)
        max_s1_c = max(s1_curv) + 1e-6
        s1_curv_norm = [c / max_s1_c for c in s1_curv]

        s2_optimized = _upsample_2x_bilinear(s1_field, 16)
        s2_temp_opt = _upsample_2x_bilinear(s1_temp, 16)
        s2_wake_mask = [0] * 1024
        s2_ax = _linspace(-2.0, 2.0, 32)
        s2_active_count = 0
        for r in range(32):
            pr = r >> 1
            y = s2_ax[r]
            for c in range(32):
                pc = c >> 1
                pidx = pr * 16 + pc
                idx = r * 32 + c
                if s1_wake_mask[pidx] and s1_curv_norm[pidx] >= thresh:
                    s2_wake_mask[idx] = 1
                    s2_active_count += 1
                    f_val, t_val = _eval_point(tree, s2_ax[c], y, phase, k, discrete=False)
                    s2_optimized[idx] = f_val
                    s2_temp_opt[idx] = t_val

        total_fine_cells = 1024
        total_evals_multiscale = 64 + s1_active_count + s2_active_count
        micro_skipped = total_fine_cells - s2_active_count
        weighted_cost = s2_active_count + 0.25 * s1_active_count + 0.0625 * 64.0
        compute_saved_pct = _clamp((1.0 - weighted_cost / total_fine_cells) * 100.0, 0.0, 96.0)
        effective_speedup = round(100.0 / max(4.0, 100.0 - compute_saved_pct), 2)

        spatial_err_map = [abs(s2_branchless_full[i] - s2_optimized[i]) for i in range(1024)]
        spatial_rmse = math.sqrt(sum(e * e for e in spatial_err_map) / 1024.0)
        field_range = (max(s2_branchless_full) - min(s2_branchless_full)) + 1e-6
        spatial_fidelity_pct = _clamp((1.0 - spatial_rmse / field_range) * 100.0, 0.0, 100.0)

        # 4. DOMAIN C — Real-Time Signal / Audio Harmonic Condensation (Exact Radix-2 FFT)
        n_samples = 256
        raw_wave: List[float] = []
        code_spiral: List[float] = []
        for i in range(n_samples):
            frac = i / n_samples
            theta = frac * 4.0 * math.pi
            rad = 0.18 + frac * 0.74
            rr = int(_clamp((0.5 + 0.45 * rad * math.sin(theta)) * 31.0, 0.0, 31.0))
            cc = int(_clamp((0.5 + 0.45 * rad * math.cos(theta)) * 31.0, 0.0, 31.0))
            idx = rr * 32 + cc
            raw_wave.append(s2_optimized[idx])
            code_spiral.append(s2_discrete[idx])

        mean_w = sum(raw_wave) / n_samples
        centered_w = [v - mean_w for v in raw_wave]
        max_w = max(abs(v) for v in centered_w) + 1e-6
        raw_wave_norm = [v / max_w for v in centered_w]

        fft_vals = _fft_radix2([complex(v, 0.0) for v in raw_wave_norm], inverse=False)
        half_n = n_samples // 2
        # Pick top-K positive-frequency bins (1..half_n-1)
        pos_bins = [(b, abs(fft_vals[b])) for b in range(1, half_n)]
        pos_bins.sort(key=lambda item: item[1], reverse=True)
        top_bins = sorted([b for b, _ in pos_bins[:n_harmonics]])

        sparse_fft = [0.0 + 0.0j] * n_samples
        for b in top_bins:
            sparse_fft[b] = fft_vals[b]
            sparse_fft[n_samples - b] = fft_vals[n_samples - b]
        reconstructed_c = _fft_radix2(sparse_fft, inverse=True)
        reconstructed_wave = [z.real for z in reconstructed_c]

        audio_rmse = math.sqrt(
            sum((raw_wave_norm[i] - reconstructed_wave[i]) ** 2 for i in range(n_samples)) / n_samples
        )
        audio_fidelity_pct = _clamp((1.0 - audio_rmse) * 100.0, 0.0, 100.0)
        audio_compression_ratio = round(float(n_samples) / float(n_harmonics * 2), 1)

        base_hz = float(preset.get("base_freq_hz", 174.0))
        max_bin_mag = max((abs(fft_vals[b]) for b in top_bins), default=1.0) + 1e-6
        harmonic_seeds: List[Dict[str, float]] = []
        for b in top_bins:
            amp = abs(fft_vals[b]) / max_bin_mag
            ph = cmath.phase(fft_vals[b])
            freq_hz = round(base_hz * (1.0 + 0.25 * min(b, 24)), 2)
            harmonic_seeds.append(
                {
                    "bin": b,
                    "freq_hz": freq_hz,
                    "amplitude": round(amp, 4),
                    "phase_rad": round(ph, 4),
                }
            )

        # 5. CLOSED-LOOP PERCEPTUAL EYE (Automatic Feedback Adjustment)
        eye_action = "균형 유지 (정밀도·절감률 최적 대역)"
        if auto_optimize:
            if spatial_fidelity_pct < 94.0:
                self.auto_wake_threshold = _clamp(self.auto_wake_threshold - 0.035, 0.04, 0.48)
                eye_action = "오차 증가 감지 → 기어 기상 임계값을 낮춰 미세 연산 자동 보강"
            elif compute_saved_pct < 62.0 and spatial_fidelity_pct > 97.5:
                self.auto_wake_threshold = _clamp(self.auto_wake_threshold + 0.03, 0.04, 0.48)
                eye_action = "여유 정밀도 확보 → 기어 임계값을 높여 불필요 연산 추가 절감"

            if circuit_match_pct < 92.0:
                self.auto_steepness = _clamp(self.auto_steepness + 4.0, 4.0, 48.0)
            elif circuit_match_pct > 98.8 and self.auto_steepness > 14.0:
                self.auto_steepness = _clamp(self.auto_steepness - 1.5, 8.0, 48.0)

        # 6. UNIFIED CROSS-DOMAIN COUPLING MATRIX (Code <-> 3D Space <-> Audio Signal)
        corr_code_space = _safe_corr(s2_discrete, s2_optimized)
        corr_space_audio = _safe_corr(raw_wave_norm, reconstructed_wave)
        corr_code_audio = _safe_corr(code_spiral, reconstructed_wave)
        unified_coherence = round((corr_code_space + corr_space_audio + corr_code_audio) / 3.0, 4)

        # 7. Sync compact summary back into canonical L1 Scale-Rotor Engine
        rotor_snapshot = None
        if rotor_engine is not None:
            try:
                rotor_snapshot = rotor_engine.step_t1_to_t4(
                    {
                        "vision": {
                            "label": f"통합필드:{preset['title']}",
                            "structure": round(_clamp(spatial_fidelity_pct / 100.0, 0.1, 0.99), 4),
                            "motion": round(_clamp(sum(s0_activity) / 64.0, 0.1, 0.99), 4),
                            "contrast": round(_clamp(field_range / 3.0, 0.1, 0.99), 4),
                            "coherence": unified_coherence,
                        },
                        "audio": {
                            "label": f"배음 {n_harmonics}씨앗 ({audio_compression_ratio}x)",
                            "frequency_norm": round(_clamp(base_hz / 440.0, 0.1, 0.95), 4),
                            "amplitude": round(_clamp(audio_fidelity_pct / 100.0, 0.1, 0.99), 4),
                            "harmonicity": round(corr_space_audio, 4),
                            "noise_ratio": round(_clamp(audio_rmse, 0.0, 0.6), 4),
                        },
                        "language": {
                            "label": f"분기 {branch_count}→0 트랜지스터 회로",
                            "text": f"브랜치 {branch_count}개를 연속 수문(k={k:.1f})과 다중스케일 기어({compute_saved_pct:.1f}% 절감)로 통합",
                        },
                    }
                )
            except Exception:
                rotor_snapshot = None

        elapsed_ms = round((time.perf_counter_ns() - t0_ns) / 1e6, 2)

        return {
            "status": "ok",
            "preset_id": preset["id"],
            "preset_title": preset["title"],
            "preset_subtitle": preset["subtitle"],
            "tick": self.tick_count,
            "t_phase": round(phase, 4),
            "elapsed_ms": elapsed_ms,
            "params": {
                "gate_steepness": round(k, 2),
                "wake_threshold": round(thresh, 4),
                "audio_harmonics": n_harmonics,
                "auto_optimize": bool(auto_optimize),
            },
            "code_circuit": {
                "source": active_code,
                "original_if_branches": branch_count,
                "compiled_runtime_branches": 0,
                "gate_steepness": round(k, 2),
                "discrete_vs_circuit_rmse": round(circuit_diff_rmse, 5),
                "discrete_equivalence_pct": round(circuit_match_pct, 2),
                "gates": gate_specs,
            },
            "multiscale_gear": {
                "s0_macro_cells": 64,
                "s1_meso_awake": s1_active_count,
                "s1_meso_total": 256,
                "s2_micro_awake": s2_active_count,
                "s2_micro_total": total_fine_cells,
                "s2_micro_skipped": micro_skipped,
                "total_multiscale_evals": total_evals_multiscale,
                "compute_saved_pct": round(compute_saved_pct, 2),
                "effective_speedup": effective_speedup,
                "spatial_rmse": round(spatial_rmse, 5),
                "spatial_fidelity_pct": round(spatial_fidelity_pct, 2),
            },
            "signal_audio": {
                "raw_samples": n_samples,
                "condensed_harmonics": n_harmonics,
                "compression_ratio": audio_compression_ratio,
                "waveform_fidelity_pct": round(audio_fidelity_pct, 2),
                "base_freq_hz": base_hz,
                "harmonics": harmonic_seeds,
                "waveform_preview": [round(raw_wave_norm[i], 4) for i in range(0, n_samples, 4)],
                "reconstructed_preview": [round(reconstructed_wave[i], 4) for i in range(0, n_samples, 4)],
            },
            "eye_feedback": {
                "auto_optimize": bool(auto_optimize),
                "recommended_wake_threshold": round(self.auto_wake_threshold, 4),
                "recommended_steepness": round(self.auto_steepness, 2),
                "action_note": eye_action,
            },
            "cross_domain_coupling": {
                "code_to_space": round(corr_code_space, 4),
                "space_to_audio": round(corr_space_audio, 4),
                "code_to_audio": round(corr_code_audio, 4),
                "unified_coherence": unified_coherence,
            },
            "spatial_field": {
                "grid_size": 32,
                "height": [round(v, 4) for v in s2_optimized],
                "temp": [round(v, 4) for v in s2_temp_opt],
                "active_mask": s2_wake_mask,
                "error_map": [round(v, 4) for v in spatial_err_map],
            },
            "presets": [
                {"id": p["id"], "title": p["title"], "subtitle": p["subtitle"], "code": p["code"]}
                for p in DATAFLOW_PRESETS.values()
            ],
            "rotor_state": rotor_snapshot,
        }


_DEFAULT_DATAFLOW_ENGINE = UnifiedCausalDataflowEngine()


def run_unified_dataflow_cycle(
    *,
    engine: Any = None,
    preset_id: str = "wave_interference",
    code_source: Optional[str] = None,
    gate_steepness: float = 14.0,
    wake_threshold: float = 0.16,
    audio_harmonics: int = 6,
    t_phase: Optional[float] = None,
    auto_optimize: bool = False,
) -> Dict[str, Any]:
    return _DEFAULT_DATAFLOW_ENGINE.execute_cycle(
        preset_id=preset_id,
        code_source=code_source,
        gate_steepness=gate_steepness,
        wake_threshold=wake_threshold,
        audio_harmonics=audio_harmonics,
        t_phase=t_phase,
        auto_optimize=auto_optimize,
        rotor_engine=engine,
    )
