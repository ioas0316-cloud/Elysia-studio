#!/usr/bin/env python3
"""
Digest -> Imitate -> Learn Difference -> Re-Create Environment
(기존 재료 소화·흡수 → 재조합 모방 → 원본·모방 차이 학습 → 차이 기반 재창조 환경)
==============================================================================
Implements the real 4-stage epistemic growth loop without faking outputs:
  1. DIGEST (소화·흡수):
     - Inspects real existing workspace Python files via AST to catalog actual
       reusable pure laws vs stateful/external uncaptured structures.
     - Observes a real executable Original (physical law, wave interference,
       field diffusion, unrepresentable test law, or user-supplied formula)
       strictly through its concrete input -> output trajectory (no peeking at
       hidden coefficients).
  2. IMITATE BY RECOMBINING EXISTING INGREDIENTS (기존 재료 재조합 모방):
     - Builds Imitation Round 1 -> Round 2 -> Round 3 by selecting and solving
       combinations of already-absorbed primitive ingredients using exact
       ordinary least squares (pure-Python Gaussian elimination).
  3. CONTRAST ORIGINAL <-> IMITATION & LEARN DIFFERENCE (원본·모방 차이 학습):
     - Computes exact Residual = Original - Imitation at every round under the
       explicit Observer Lens.
     - Uses the exact residual difference to discover which missing ingredient
       explains the gap next.
     - If even combining all available ingredients leaves residual > epsilon,
       HONESTLY reports UNCAPTURED_INGREDIENT (미포집 재료 발견) instead of
       faking convergence.
  4. RE-CREATE USING LEARNED DIFFERENCE (차이를 이용한 재창조):
     - (a) Difference Modulation: intentionally modulates or inverts the exact
           difference term learned between rounds (e.g. damping -> conservation
           or self-excitation) and executes the new law.
     - (b) Cross-Original Recombination (A ⊕ B): combines the digested
           generating ingredients of Original A and Original B to synthesize a
           genuinely new executable phenomenon (e.g. Forced Resonant Oscillator),
           contrasting what was inherited (0) vs what newly emerged (1).
"""
from __future__ import annotations

import ast
import math
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from core.orchestration.process_contrast_observer import build_observer_lens

_REPO_ROOT = Path(__file__).resolve().parents[3]


# ============================================================================
# Pure-Python Linear Solver (Gaussian Elimination with Partial Pivoting)
# ============================================================================
def _solve_linear_system(a_mat: List[List[float]], b_vec: List[float]) -> Optional[List[float]]:
    n = len(b_vec)
    if n == 0:
        return []
    aug = [list(map(float, a_mat[i])) + [float(b_vec[i])] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-12:
            return None
        aug[col], aug[pivot] = aug[pivot], aug[col]
        div = aug[col][col]
        for j in range(col, n + 1):
            aug[col][j] /= div
        for r in range(n):
            if r == col:
                continue
            factor = aug[r][col]
            if abs(factor) > 1e-15:
                for j in range(col, n + 1):
                    aug[r][j] -= factor * aug[col][j]
    return [aug[i][n] for i in range(n)]


def _fit_ols_weights(cols: List[List[float]], target: List[float]) -> Optional[List[float]]:
    """Solves min_w || sum_j w_j * cols[j] - target ||_2 exactly via normal equations."""
    k = len(cols)
    m = len(target)
    if k == 0 or m == 0:
        return []
    ata = [[0.0] * k for _ in range(k)]
    atb = [0.0] * k
    for i in range(k):
        ci = cols[i]
        atb[i] = sum(ci[r] * target[r] for r in range(m))
        for j in range(i, k):
            cj = cols[j]
            val = sum(ci[r] * cj[r] for r in range(m))
            ata[i][j] = val
            ata[j][i] = val
    # Tiny Tikhonov guard only if nearly singular
    sol = _solve_linear_system(ata, atb)
    if sol is None:
        for i in range(k):
            ata[i][i] += 1e-9
        sol = _solve_linear_system(ata, atb)
    return sol


def _vec_rmse(a: Sequence[float], b: Sequence[float]) -> float:
    if not a:
        return 0.0
    return math.sqrt(sum((float(x) - float(y)) ** 2 for x, y in zip(a, b)) / len(a))


def _vec_max_err(a: Sequence[float], b: Sequence[float]) -> float:
    if not a:
        return 0.0
    return max(abs(float(x) - float(y)) for x, y in zip(a, b))


def _corr_abs(col: Sequence[float], residual: Sequence[float]) -> float:
    n_c = math.sqrt(sum(c * c for c in col))
    n_r = math.sqrt(sum(r * r for r in residual))
    if n_c < 1e-12 or n_r < 1e-12:
        return 0.0
    return abs(sum(c * r for c, r in zip(col, residual)) / (n_c * n_r))


# ============================================================================
# Safe Custom Formula Evaluator (AST Allowlisted — Zero exec/eval risk)
# ============================================================================
_SAFE_EXPR_NODES = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.Call,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Pow,
    ast.USub,
    ast.UAdd,
)

_SAFE_MATH_FUNCS: Dict[str, Callable[[float], float]] = {
    "sin": math.sin,
    "cos": math.cos,
    "abs": abs,
    "exp": lambda v: math.exp(max(-20.0, min(20.0, float(v)))),
    "tanh": math.tanh,
}


def _compile_safe_formula(expr_text: str) -> Callable[[float, float, float], float]:
    cleaned = (expr_text or "").strip()
    if not cleaned or len(cleaned) > 220:
        raise ValueError("수식은 1~220자 이내로 입력해 주세요. (허용 변수: x, v, u_lap)")
    tree = ast.parse(cleaned, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, _SAFE_EXPR_NODES):
            raise ValueError(f"허용되지 않는 수식 구문입니다: {type(node).__name__}")
        if isinstance(node, ast.Name):
            if node.id not in ("x", "v", "u_lap") and node.id not in _SAFE_MATH_FUNCS:
                raise ValueError(f"허용되지 않는 식별자 '{node.id}' (허용: x, v, u_lap, sin, cos, abs, exp, tanh)")
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in _SAFE_MATH_FUNCS or len(node.args) != 1:
                raise ValueError("함수는 sin, cos, abs, exp, tanh (인자 1개)만 사용할 수 있습니다.")

    def _eval_node(node: ast.AST, env: Dict[str, float]) -> float:
        if isinstance(node, ast.Expression):
            return _eval_node(node.body, env)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.Name):
            return float(env[node.id])
        if isinstance(node, ast.UnaryOp):
            val = _eval_node(node.operand, env)
            return -val if isinstance(node.op, ast.USub) else val
        if isinstance(node, ast.BinOp):
            left = _eval_node(node.left, env)
            right = _eval_node(node.right, env)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / (right if abs(right) > 1e-9 else 1e-9)
            if isinstance(node.op, ast.Pow):
                exp_v = max(-4.0, min(4.0, right))
                return math.copysign(abs(left) ** exp_v, left) if left < 0 and int(exp_v) != exp_v else (left ** exp_v)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            arg_v = _eval_node(node.args[0], env)
            return float(_SAFE_MATH_FUNCS[node.func.id](arg_v))
        raise ValueError("수식 평가 불가")

    def _fn(x: float, v: float, u_lap: float) -> float:
        return _eval_node(tree, {"x": x, "v": v, "u_lap": u_lap})

    return _fn


# ============================================================================
# Stage 1A: Real Workspace Knowledge Digester (Reads actual repo .py files)
# ============================================================================
_WORKSPACE_KNOWLEDGE_FILES = [
    "L1_causal_field/core/physics/causal_field.py",
    "L1_causal_field/core/orchestration/scale_rotor_core.py",
    "L1_causal_field/core/orchestration/bidirectional_phase_sync.py",
]


def digest_workspace_existing_knowledge() -> Dict[str, Any]:
    """
    Directly parses real existing Python files inside this repository via AST
    to inventory already-present structural classes, pure functions, and
    external/stateful boundaries (honestly distinguishing directly runnable
    pure ingredients vs stateful uncaptured methods).
    """
    digested_files: List[Dict[str, Any]] = []
    total_funcs = 0
    total_classes = 0
    pure_reusable_count = 0

    for rel in _WORKSPACE_KNOWLEDGE_FILES:
        fpath = (_REPO_ROOT / rel).resolve()
        # Strict containment check inside repo root
        if _REPO_ROOT not in fpath.parents or not fpath.exists():
            continue
        src = fpath.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(src)
        classes: List[str] = []
        pure_funcs: List[str] = []
        stateful_methods: List[str] = []
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
                for sub in node.body:
                    if isinstance(sub, ast.FunctionDef) and not sub.name.startswith("__"):
                        stateful_methods.append(f"{node.name}.{sub.name}")
            elif isinstance(node, ast.FunctionDef):
                if not node.name.startswith("__"):
                    pure_funcs.append(node.name)

        total_classes += len(classes)
        total_funcs += len(pure_funcs) + len(stateful_methods)
        pure_reusable_count += len(pure_funcs)
        digested_files.append(
            {
                "file": rel,
                "lines": len(src.splitlines()),
                "classes": classes[:6],
                "pure_reusable_ingredients": pure_funcs[:8],
                "stateful_coupled_methods_count": len(stateful_methods),
            }
        )

    return {
        "files_scanned": len(digested_files),
        "total_classes": total_classes,
        "total_functions": total_funcs,
        "pure_reusable_count": pure_reusable_count,
        "files": digested_files,
        "note": (
            f"실제 워크스페이스 파일 {len(digested_files)}건(클래스 {total_classes}·함수 {total_funcs}개)을 AST로 직접 소화했습니다. "
            f"순수 함수 {pure_reusable_count}건은 즉시 재조합 재료로 편입 가능하며, 내부 상태 결합 메서드는 컨텍스트 없이는 미포집 경계로 구분했습니다."
        ),
    }


# ============================================================================
# Primitive Absorbed Ingredient Palette (이미 흡수된 기본 재료 팔레트)
# ============================================================================
def _build_ingredient_palette() -> List[Dict[str, Any]]:
    return [
        {"id": "const_1", "label": "상수 기준(1)", "symbol": "1", "fn": lambda x, v, u: 1.0},
        {"id": "linear_x", "label": "선형 복원·비례(x)", "symbol": "x", "fn": lambda x, v, u: x},
        {"id": "linear_v", "label": "속도·감쇠 저항(v)", "symbol": "v", "fn": lambda x, v, u: v},
        {"id": "laplacian_u", "label": "이웃 구배·확산(Δ²u)", "symbol": "u_lap", "fn": lambda x, v, u: u},
        {"id": "cubic_x", "label": "비선형 3차 경계(x³)", "symbol": "x³", "fn": lambda x, v, u: x * x * x},
        {"id": "sin_x", "label": "주기 사인 파동(sin x)", "symbol": "sin(x)", "fn": lambda x, v, u: math.sin(x)},
        {"id": "cos_2x", "label": "2배조 코사인 파동(cos 2x)", "symbol": "cos(2x)", "fn": lambda x, v, u: math.cos(2.0 * x)},
        {"id": "quad_xv", "label": "비선형 교차항(x·v)", "symbol": "x·v", "fn": lambda x, v, u: x * v},
    ]


# ============================================================================
# Real Executable Originals (기존에 존재하는 실제 원리 원본들)
# ============================================================================
def _get_original_spec(original_id: str, custom_formula: Optional[str] = None) -> Dict[str, Any]:
    oid = (original_id or "damped_harmonic").strip().lower()
    if oid == "custom_formula" and custom_formula and custom_formula.strip():
        fn = _compile_safe_formula(custom_formula)
        return {
            "id": "custom_formula",
            "title": f"사용자 투입 미지 원본: f(x, v, u_lap) = {custom_formula.strip()}",
            "domain": "사용자 직접 투입 수식",
            "fn": fn,
            "description": "시스템이 수식 내부를 엿보지 않고 오직 입출력 궤적만 관측해 기존 재료 재조합으로 모방·차이 학습을 시도합니다.",
        }
    if oid == "wave_interference":
        return {
            "id": "wave_interference",
            "title": "원본: 이중 파동 간섭 법칙 (음향·광학 중첩)",
            "domain": "파동·음향·광학",
            "fn": lambda x, v, u: 1.40 * math.sin(x) + 0.65 * math.cos(2.0 * x) - 0.25 * x,
            "description": "기본파와 2배조 파동, 배경 경사가 중첩된 실제 간섭 파형",
        }
    if oid == "thermal_diffusion":
        return {
            "id": "thermal_diffusion",
            "title": "원본: 1D 열·인과장 확산 법칙 (라플라시안 + 감쇠)",
            "domain": "열역학·장방정식",
            "fn": lambda x, v, u: 0.42 * u - 0.18 * v + 0.12 * x,
            "description": "이웃 노드 구배(Δ²u)에 의한 확산과 국소 마찰 감쇠가 맞물린 장 전이 원리",
        }
    if oid == "uncaptured_boundary_test":
        return {
            "id": "uncaptured_boundary_test",
            "title": "원본: 미지 비선형 경계 법칙 (|x|·exp(-0.4x) — 미포집 정직성 테스트)",
            "domain": "현재 팔레트 외곽 미지 원리",
            "fn": lambda x, v, u: abs(x) * math.exp(-0.4 * x) + 0.5 * math.tanh(2.5 * v),
            "description": "현재 보유한 기본 재료 팔레트에 없는 절대값·지수·포화 함수가 섞인 원본 — 억지 끼워맞춤 없이 미포집 판정이 나와야 정상",
        }
    # Default: damped_harmonic
    return {
        "id": "damped_harmonic",
        "title": "원본: 감쇠 조화 진동 법칙 (Hooke 복원력 + 점성 감쇠 + 비선형 경계)",
        "domain": "고전 역학·인과 복원",
        "fn": lambda x, v, u: -2.20 * x - 0.45 * v - 0.15 * (x * x * x),
        "description": "복원력(-k·x), 점성 감쇠(-c·v), 3차 비선형 경계(-β·x³)가 결합된 실제 물리 가속도 법칙",
    }


def _get_partner_spec(partner_id: str) -> Dict[str, Any]:
    pid = (partner_id or "wave_forcing").strip().lower()
    if pid == "diffusion_coupling":
        return {
            "id": "diffusion_coupling",
            "title": "교차 재료 B: 공간 이웃 확산 결합 (+0.45·u_lap)",
            "terms": [("laplacian_u", 0.45)],
            "emergent_label": "파동-확산 결합장 (Reaction-Diffusion Coupling)",
        }
    if pid == "nonlinear_boundary":
        return {
            "id": "nonlinear_boundary",
            "title": "교차 재료 B: 교차 마찰 비선형 결합 (+0.35·x·v)",
            "terms": [("quad_xv", 0.35), ("const_1", 0.15)],
            "emergent_label": "비대칭 자기-제동 진동체 (Asymmetric Self-Braking Oscillator)",
        }
    return {
        "id": "wave_forcing",
        "title": "교차 재료 B: 주기 공명 외력 (+0.95·sin(x) + 0.35·cos(2x))",
        "terms": [("sin_x", 0.95), ("cos_2x", 0.35)],
        "emergent_label": "강제 공명 진동자 (Forced Resonant Oscillator — 맥놀이·공명 창발)",
    }


def _format_recombined_formula(selected_ids: List[str], weights: List[float], palette_map: Dict[str, Dict[str, Any]]) -> str:
    parts: List[str] = []
    for iid, w in zip(selected_ids, weights):
        if abs(w) < 1e-6:
            continue
        sym = palette_map[iid]["symbol"]
        sign = "+" if w >= 0 else "-"
        coeff = f"{abs(w):.4f}"
        term = coeff if sym == "1" else f"{coeff}*{sym}"
        parts.append(f"{sign} {term}" if parts else (f"-{term}" if w < 0 else term))
    return " ".join(parts) if parts else "0.0"


def _evaluate_linear_combo(
    selected_ids: List[str],
    weights: List[float],
    palette_map: Dict[str, Dict[str, Any]],
    x: float,
    v: float,
    u_lap: float,
) -> float:
    return sum(w * palette_map[iid]["fn"](x, v, u_lap) for iid, w in zip(selected_ids, weights))


def _simulate_dynamical_trajectory(
    accel_fn: Callable[[float, float, float], float],
    steps: int = 24,
    dt: float = 0.14,
) -> Dict[str, Any]:
    """Runs an actual forward Euler-Cromer trajectory so re-created laws are empirically executed."""
    x = 1.35
    v = 0.25
    xs: List[float] = []
    vs: List[float] = []
    energies: List[float] = []
    for k in range(steps):
        # Deterministic spatial neighbor Laplacian proxy u_lap(x, k)
        u_lap = math.sin(0.35 * k) - x
        a = max(-30.0, min(30.0, float(accel_fn(x, v, u_lap))))
        v = max(-20.0, min(20.0, v + a * dt))
        x = max(-20.0, min(20.0, x + v * dt))
        xs.append(round(x, 5))
        vs.append(round(v, 5))
        energies.append(round(0.5 * v * v + 0.5 * x * x, 5))
    peak_amp = round(max(abs(val) for val in xs), 5)
    final_energy = energies[-1]
    initial_energy = energies[0]
    energy_trend = "감쇠 수렴" if final_energy < initial_energy * 0.78 else ("증폭·공명 발산" if final_energy > initial_energy * 1.25 else "지속 진동 유지")
    return {
        "steps": steps,
        "x_tail": xs[-6:],
        "peak_amplitude": peak_amp,
        "initial_energy": initial_energy,
        "final_energy": final_energy,
        "energy_trend": energy_trend,
        "xs": xs,
    }


def run_digest_imitate_recreate(
    engine: Any = None,
    original_id: str = "damped_harmonic",
    partner_id: str = "wave_forcing",
    custom_formula: Optional[str] = None,
    lens_mode: str = "strict",
    epsilon: Optional[float] = None,
    max_rounds: int = 3,
) -> Dict[str, Any]:
    """
    Executes the complete genuine 4-stage loop:
      1. Digest existing workspace files + observe real Original trajectory
      2. Progressive Recombination Imitation (Round 1 -> Round 2 -> Round 3)
      3. Contrast Original <-> Imitation -> Learn exact Residual Difference (or honestly flag UNCAPTURED)
      4. Re-Create via (a) Learned-Difference Modulation & (b) Cross-Original Recombination (A ⊕ B)
    """
    lens = build_observer_lens(lens_mode, epsilon)
    # Practical convergence threshold linked to observer lens
    tol = max(1e-4, float(lens["epsilon"]) * (1.0 if lens["mode"] == "tolerant" else 50.0))

    workspace_digest = digest_workspace_existing_knowledge()
    original = _get_original_spec(original_id, custom_formula=custom_formula)
    partner = _get_partner_spec(partner_id)
    palette = _build_ingredient_palette()
    palette_map = {item["id"]: item for item in palette}

    # Build rich deterministic probe set covering independent (x, v, u_lap) space (36 real states)
    probes: List[Tuple[float, float, float]] = []
    for i in range(36):
        t = (i - 18) * 0.17
        x = round(math.sin(t * 1.3) * 1.65 + 0.25 * math.cos(t * 0.7), 6)
        v = round(math.cos(t * 1.9) * 1.45 - 0.30 * math.sin(t * 0.5), 6)
        u_lap = round(math.sin(t * 2.3 + 0.6) * 1.25 - 0.4 * x, 6)
        probes.append((x, v, u_lap))

    # Stage 1: Observe real Original outputs on probes (NO peeking at hidden formula!)
    y_orig = [float(original["fn"](x, v, u)) for (x, v, u) in probes]
    basis_matrix: Dict[str, List[float]] = {
        item["id"]: [float(item["fn"](x, v, u)) for (x, v, u) in probes] for item in palette
    }

    # Stage 2 & 3: Iterative Imitation -> Original vs Imitation Contrast -> Difference Learning
    selected_ids: List[str] = []
    weights: List[float] = []
    residual = list(y_orig)
    rounds: List[Dict[str, Any]] = []
    absorbed_successfully = False
    rounds_limit = max(1, min(5, int(max_rounds)))

    for r_idx in range(1, rounds_limit + 1):
        # Evaluate each remaining existing ingredient by actual OLS residual reduction (true difference minimization)
        candidates = [item["id"] for item in palette if item["id"] not in selected_ids]
        if not candidates:
            break
        best_id = None
        best_weights = None
        best_rmse = float("inf")
        best_y_imit: List[float] = []
        for cand_id in candidates:
            trial_ids = selected_ids + [cand_id]
            trial_cols = [basis_matrix[iid] for iid in trial_ids]
            trial_w = _fit_ols_weights(trial_cols, y_orig)
            if trial_w is None:
                continue
            trial_y = [
                sum(trial_w[j] * basis_matrix[trial_ids[j]][idx] for j in range(len(trial_ids)))
                for idx in range(len(probes))
            ]
            trial_rmse = _vec_rmse(y_orig, trial_y)
            if trial_rmse < best_rmse - 1e-12:
                best_rmse = trial_rmse
                best_id = cand_id
                best_weights = trial_w
                best_y_imit = trial_y

        if best_id is None or best_weights is None:
            break
        best_corr = _corr_abs(basis_matrix[best_id], residual)
        selected_ids.append(best_id)
        weights = best_weights
        y_imit = best_y_imit
        new_residual = [y_orig[idx] - y_imit[idx] for idx in range(len(probes))]
        rmse = best_rmse
        max_err = _vec_max_err(y_orig, y_imit)
        matched_0 = sum(1 for err in new_residual if abs(err) <= tol)
        mismatched_1 = len(new_residual) - matched_0
        formula_str = _format_recombined_formula(selected_ids, weights, palette_map)

        # Identify what the remaining gap looks like (if not yet converged)
        next_hint = "원본과 모방의 잔차(차이)가 관측 임계치 이하로 소멸 — 원리 소화 완료"
        if rmse > tol:
            rem_cands = [item["id"] for item in palette if item["id"] not in selected_ids]
            if rem_cands:
                nxt = max(rem_cands, key=lambda iid: _corr_abs(basis_matrix[iid], new_residual))
                nxt_corr = _corr_abs(basis_matrix[nxt], new_residual)
                if nxt_corr > 0.35:
                    next_hint = f"남은 차이(잔차 RMSE={rmse:.4f})가 기존 재료 '{palette_map[nxt]['label']}'와 상관계수 {nxt_corr:.2f}로 공명 → 다음 라운드 재조합 후보"
                else:
                    next_hint = f"남은 차이(RMSE={rmse:.4f})가 보유 재료들과 낮은 상관({nxt_corr:.2f}) — 미포집 비선형 원리 가능성"

        rounds.append(
            {
                "round": r_idx,
                "added_ingredient_id": best_id,
                "added_ingredient_label": palette_map[best_id]["label"],
                "residual_correlation": round(best_corr, 4),
                "imitation_formula": formula_str,
                "rmse_original_vs_imitation": round(rmse, 6),
                "max_error": round(max_err, 6),
                "matched_0_probes": matched_0,
                "mismatched_1_probes": mismatched_1,
                "learned_difference_note": next_hint,
            }
        )
        residual = new_residual
        if rmse <= tol:
            absorbed_successfully = True
            break

    final_rmse = rounds[-1]["rmse_original_vs_imitation"] if rounds else 1.0
    final_formula = rounds[-1]["imitation_formula"] if rounds else "0.0"

    # Honest Epistemic Classification: Digested vs UNCAPTURED_INGREDIENT
    absorption_status = "DIGESTED_AND_VERIFIED" if absorbed_successfully else "UNCAPTURED_INGREDIENT"

    # Stage 4: REAL Re-Creation Using the Learned Difference & Cross-Original Recombination
    # (a) Original trajectory execution
    orig_traj = _simulate_dynamical_trajectory(original["fn"])
    imit_fn = lambda x, v, u: _evaluate_linear_combo(selected_ids, weights, palette_map, x, v, u)
    imit_traj = _simulate_dynamical_trajectory(imit_fn)
    traj_orig_vs_imit_rmse = round(_vec_rmse(orig_traj["xs"], imit_traj["xs"]), 6)

    # (b) Difference-Modulated Re-Creation:
    # Take the exact ingredient discovered from the Round 1 -> Round 2 residual difference (or last learned term)
    # and invert/modulate ONLY that learned difference while keeping the Round-1 base invariant (0)!
    diff_term_idx = 1 if len(selected_ids) >= 2 else 0
    diff_term_id = selected_ids[diff_term_idx] if selected_ids else "linear_x"
    diff_term_w = weights[diff_term_idx] if weights else 0.0
    mod_weights = list(weights)
    if mod_weights:
        # Invert the learned difference term's sign (e.g., damping -0.45*v -> self-driving +0.35*v, or phase flip)
        mod_weights[diff_term_idx] = -0.65 * diff_term_w
    mod_formula = _format_recombined_formula(selected_ids, mod_weights, palette_map)
    mod_fn = lambda x, v, u: _evaluate_linear_combo(selected_ids, mod_weights, palette_map, x, v, u)
    mod_traj = _simulate_dynamical_trajectory(mod_fn)
    mod_divergence = round(_vec_rmse(orig_traj["xs"], mod_traj["xs"]), 5)

    # (c) Cross-Original Recombination (A ⊕ B):
    # Combine absorbed Original A weights + Partner B ingredients -> execute genuinely new hybrid system!
    combo_map: Dict[str, float] = {}
    for iid, w in zip(selected_ids, weights):
        combo_map[iid] = combo_map.get(iid, 0.0) + w
    for iid, w in partner["terms"]:
        combo_map[iid] = combo_map.get(iid, 0.0) + w
    combo_ids = list(combo_map.keys())
    combo_ws = [combo_map[k] for k in combo_ids]
    combo_formula = _format_recombined_formula(combo_ids, combo_ws, palette_map)
    combo_fn = lambda x, v, u: _evaluate_linear_combo(combo_ids, combo_ws, palette_map, x, v, u)
    combo_traj = _simulate_dynamical_trajectory(combo_fn)
    partner_only_fn = lambda x, v, u: _evaluate_linear_combo(
        [t[0] for t in partner["terms"]],
        [t[1] for t in partner["terms"]],
        palette_map,
        x,
        v,
        u,
    )
    partner_traj = _simulate_dynamical_trajectory(partner_only_fn)

    combo_diff_from_a = round(_vec_rmse(orig_traj["xs"], combo_traj["xs"]), 5)
    combo_diff_from_b = round(_vec_rmse(partner_traj["xs"], combo_traj["xs"]), 5)

    # Sync newly digested empirical evidence into live L1 ScaleRotorEngine (if provided)
    rotor_state = None
    if engine is not None:
        fidelity = max(0.05, min(0.99, 1.0 / (1.0 + final_rmse)))
        novelty = max(0.05, min(0.99, combo_diff_from_a / (1.0 + combo_diff_from_a)))
        rotor_state = engine.step_t1_to_t4(
            {
                "vision": {
                    "label": f"소화·모방·재창조 ({original['id']})",
                    "structure": round(fidelity, 4),
                    "contrast": round(novelty, 4),
                    "motion": round(min(0.95, 0.25 + 0.2 * len(rounds)), 4),
                    "coherence": round(fidelity, 4),
                },
                "language": {
                    "label": f"소화 원리: {original['id']}",
                    "text": (
                        f"원본({original['id']}) 모방식={final_formula} (RMSE={final_rmse:.5f}, {absorption_status}) "
                        f"→ 교차 재창조({partner['emergent_label']}): {combo_formula}"
                    ),
                },
                "behavior": {
                    "label": "차이 학습 기반 재창조",
                    "fatigue": round(1.0 - fidelity, 4),
                    "threat": 0.12 if absorbed_successfully else 0.68,
                    "proximity": 0.55,
                    "cohesion": round(fidelity, 4),
                    "terrain_friction": round(novelty, 4),
                },
                "noise_ratio": 0.0 if absorbed_successfully else min(0.55, final_rmse),
            }
        )

    uncaptured_notes: List[str] = []
    if not absorbed_successfully:
        uncaptured_notes.append(
            f"[미포집 재료 감지] 현재 보유한 8종 기본 재료({', '.join(p['symbol'] for p in palette)})의 재조합만으로는 "
            f"원본 '{original['title']}'의 잔차(RMSE={final_rmse:.4f} > 허용 {tol:.4f})를 설명할 수 없습니다. "
            "억지 근사로 통과시키지 않고 미포집으로 남겨 새로운 기본 원리 흡수를 대기합니다."
        )
    uncaptured_notes.append(
        "외부 세계의 아직 관측되지 않은 물리 변수·비선형 불연속 경계(충돌, 상전이 임계점 등)는 실제 프로브 궤적이 유입되기 전까지 미포집입니다."
    )

    return {
        "status": "ok",
        "experiment": "digest_imitate_learn_difference_recreate",
        "observer_lens": lens,
        "convergence_threshold": round(tol, 6),
        "stage_1_digest": {
            "workspace_knowledge": workspace_digest,
            "original": {
                "id": original["id"],
                "title": original["title"],
                "domain": original["domain"],
                "description": original["description"],
                "probes_observed": len(probes),
                "trajectory_summary": {
                    "peak_amplitude": orig_traj["peak_amplitude"],
                    "energy_trend": orig_traj["energy_trend"],
                },
            },
            "available_ingredients": [{"id": p["id"], "label": p["label"], "symbol": p["symbol"]} for p in palette],
        },
        "stage_2_3_imitate_and_learn_difference": {
            "absorption_status": absorption_status,
            "absorbed_successfully": absorbed_successfully,
            "rounds": rounds,
            "final_imitation_formula": final_formula,
            "final_probe_rmse": final_rmse,
            "forward_trajectory_rmse_orig_vs_imit": traj_orig_vs_imit_rmse,
            "learned_ingredients": [
                {
                    "id": iid,
                    "label": palette_map[iid]["label"],
                    "symbol": palette_map[iid]["symbol"],
                    "weight": round(w, 5),
                }
                for iid, w in zip(selected_ids, weights)
            ],
        },
        "stage_4_recreate": {
            "difference_modulation": {
                "title": f"4-A. 학습된 차이 변조 재창조 ('{palette_map[diff_term_id]['label']}' 계수 반전)",
                "pivoted_difference": f"{palette_map[diff_term_id]['symbol']}: {diff_term_w:+.4f} → {-0.65 * diff_term_w:+.4f}",
                "recreated_formula": mod_formula,
                "original_trend": orig_traj["energy_trend"],
                "recreated_trend": mod_traj["energy_trend"],
                "peak_amplitude_before": orig_traj["peak_amplitude"],
                "peak_amplitude_after": mod_traj["peak_amplitude"],
                "trajectory_divergence_from_original": mod_divergence,
            },
            "cross_recombination": {
                "title": f"4-B. 이종 원리 교차 재조합 재창조 (소화 원본 A ⊕ {partner['title']})",
                "emergent_name": partner["emergent_label"],
                "recreated_formula": combo_formula,
                "inherited_0_from_a": [palette_map[iid]["symbol"] for iid in selected_ids],
                "added_1_from_b": [palette_map[iid]["symbol"] for iid, _ in partner["terms"]],
                "recreated_trend": combo_traj["energy_trend"],
                "recreated_peak_amplitude": combo_traj["peak_amplitude"],
                "divergence_from_original_a": combo_diff_from_a,
                "divergence_from_partner_b": combo_diff_from_b,
                "genuinely_novel": bool(combo_diff_from_a > 0.05 and combo_diff_from_b > 0.05),
            },
        },
        "summary": {
            "absorption_status": absorption_status,
            "rounds_taken": len(rounds),
            "initial_round_rmse": rounds[0]["rmse_original_vs_imitation"] if rounds else 1.0,
            "final_round_rmse": final_rmse,
            "recreation_novelty_from_a": combo_diff_from_a,
            "recreation_novelty_from_b": combo_diff_from_b,
            "principle_note": (
                f"이미 존재하는 재료 팔레트에서 {len(rounds)}라운드 재조합 모방을 거쳐 "
                + (
                    f"원본↔모방 오차를 {rounds[0]['rmse_original_vs_imitation']:.4f} → {final_rmse:.6f}로 수렴시켜 원리를 소화한 뒤, "
                    "학습된 차이를 변조·교차 재조합해 실제로 실행되는 새로운 거동을 재창조했습니다."
                    if absorbed_successfully
                    else f"원본↔모방 잔차(RMSE={final_rmse:.4f})가 임계치({tol:.4f})를 초과함을 실측하여 "
                    "가짜 수렴 없이 '미포집 재료 발견'으로 정직하게 분류했습니다."
                )
            ),
        },
        "uncaptured": uncaptured_notes,
        "rotor_state": rotor_state,
    }
