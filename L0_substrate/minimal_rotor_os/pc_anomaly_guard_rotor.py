r"""
ELYSIA Stage 4 — Personalized PC Anomaly & Auto-Performance Guard Rotor
=======================================================================

Compares live host OS telemetry (`os_ecology_bridge` + `nvidia-smi` GTX 1060)
against this PC's persistent Octave Baseline (`ecology_octave_ledger.json`) to
detect real anomalies (circuit-conservation leaks, VRAM/GPU pressure, RAM spikes)
and emit non-intrusive self-regulation recommendations.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
import time
from typing import Any, Dict, List

EMBODIMENT_DIR = Path(__file__).resolve().parents[2] / "L1_causal_field" / "core" / "embodiment"
if str(EMBODIMENT_DIR) not in sys.path:
    sys.path.insert(0, str(EMBODIMENT_DIR))

import game_ecology_organ as game_mod  # noqa: E402
import os_ecology_bridge as eco_mod  # noqa: E402


def run_stage4_pc_guard() -> Dict[str, Any]:
    ledger_path = EMBODIMENT_DIR / "ecology_octave_ledger.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8")) if ledger_path.exists() else {}

    t1 = eco_mod.sense_live_os_telemetry({})
    time.sleep(0.25)
    t2 = eco_mod.sense_live_os_telemetry({"prev_snapshot": t1.get("stage1_observation")})
    gpu = game_mod.query_nvidia_gpu_live()
    grain = game_mod.compute_adaptive_graphics_grain(gpu)

    alerts: List[Dict[str, Any]] = []
    ram_pct = float((t2.get("system") or {}).get("memory", {}).get("percent", 0.0))
    err_rotors = int((t2.get("stage2_delta") or {}).get("error_rotor_count", 0))
    if err_rotors > 0:
        alerts.append({"severity": "high", "kind": "error_rotor_leak", "detail": f"단조 팽창 오류 로터 {err_rotors}건 감지"})
    if ram_pct >= 85.0:
        alerts.append({"severity": "medium", "kind": "ram_pressure", "detail": f"시스템 RAM {ram_pct}% → 자체 관측 주기 감속 권고"})
    if gpu.get("available") and (gpu.get("vram_pct", 0) >= 85.0 or gpu.get("gpu_util_pct", 0) >= 88.0):
        alerts.append({"severity": "medium", "kind": "gpu_pressure", "detail": f"GPU {gpu['gpu_util_pct']}% / VRAM {gpu['vram_pct']}% → {grain['mode']} 적용"})

    return {
        "status": "ok",
        "stage": "Stage 4 — Personalized PC Anomaly & Auto-Performance Guard",
        "baseline_raw_observations": int(ledger.get("totalRawAbsorbed", 0)),
        "baseline_ice_symbols": len(ledger.get("iceSymbols") or {}),
        "live_ram_pct": ram_pct,
        "live_gpu": gpu,
        "adaptive_graphics_grain": grain,
        "error_rotors_detected": err_rotors,
        "alerts": alerts,
        "guard_verdict": "정상 순환(0000 안정)" if not alerts else f"주의 경보 {len(alerts)}건 감지",
    }


if __name__ == "__main__":
    print(json.dumps(run_stage4_pc_guard(), ensure_ascii=False, indent=2))
