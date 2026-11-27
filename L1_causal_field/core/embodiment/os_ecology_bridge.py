r"""
ELYSIA Scale-Rotor OS Ecology Bridge
====================================

Bridges the browser multi-world ecology (`/ecology`) with the real host OS
protocol discovery (`os_protocol_discovery.py`) and converts arbitrary
principle structures or OS protocols into canonical Scale-Rotor descriptors
across the 5 Phase Frames:
    Point -> Line -> Plane -> Spacetime Cube -> Coupled Rotor Sphere

Maintains the 4 Continuities:
- Relationship: protocols and principles couple through typed ports and
  boundary membranes rather than hardcoded if/else chains.
- Connectivity: builds explicit port-to-port coupling edges between host
  OS protocols and browser-side world encounters.
- Mobility: computes continuous chromatic/momentum vectors (Red/Blue/Yellow)
  as an analogical lens for flux, order, and dispersion.
- Informational Continuity: preserves provenance, invariants (0), variables (1),
  and open/unobserved boundaries without collapsing unknowns into fake numbers.
"""

from __future__ import annotations

import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import sys
import time
import types
from typing import Any, Dict, List, Optional, Tuple

try:
    import psutil
except ImportError:
    psutil = None

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
L1_ROOT = WORKSPACE_ROOT / "L1_causal_field"
if str(L1_ROOT) not in sys.path:
    sys.path.insert(0, str(L1_ROOT))


def _load_os_protocol_discovery():
    """
    Loads `core.embodiment.os_protocol_discovery` directly without triggering
    unrelated eager imports in `core.embodiment.__init__` / `core.consciousness.__init__`.
    """
    try:
        from core.embodiment import os_protocol_discovery as mod
        return mod
    except ModuleNotFoundError:
        # Register minimal namespace packages for `core`, `core.embodiment`, `core.topology`
        for pkg_name, pkg_dir in [
            ("core", L1_ROOT / "core"),
            ("core.embodiment", L1_ROOT / "core" / "embodiment"),
            ("core.topology", L1_ROOT / "core" / "topology"),
        ]:
            if pkg_name not in sys.modules:
                pkg = types.ModuleType(pkg_name)
                pkg.__path__ = [str(pkg_dir)]
                sys.modules[pkg_name] = pkg
        spec = importlib.util.spec_from_file_location(
            "core.embodiment.os_protocol_discovery",
            L1_ROOT / "core" / "embodiment" / "os_protocol_discovery.py",
        )
        if spec is None or spec.loader is None:
            raise RuntimeError("Could not locate os_protocol_discovery.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        return mod


_os_proto_mod = _load_os_protocol_discovery()
capture_live_environment_seed = _os_proto_mod.capture_live_environment_seed
discover_real_os_protocols = _os_proto_mod.discover_real_os_protocols


# 10-Row OS Scale-Rotor Map metadata
OS_ROTOR_CATEGORY_MAP: Dict[str, Dict[str, Any]] = {
    "proto::os_file_read": {
        "rotor_category": "지속성 로터",
        "scale_band": "S1~S2",
        "invariants": ["파일 경로 주소 체계", "바이트 스트림 출처 보존"],
        "variables": ["파일 변경·삭제", "인코딩·권한 경계"],
        "chromatic": [0.22, 0.62, 0.16],
    },
    "proto::python_compile": {
        "rotor_category": "물리 제약 로터",
        "scale_band": "S0~S1",
        "invariants": ["문법·AST 수용/거부 불변성", "실행 구조 결정성"],
        "variables": ["런타임 버전", "외부 모듈 의존성"],
        "chromatic": [0.18, 0.72, 0.10],
    },
    "proto::os_dir_topology": {
        "rotor_category": "국소 생태계 로터",
        "scale_band": "S2",
        "invariants": ["디렉터리 계층·이웃 위상"],
        "variables": ["이웃 파일 증감", "작업 공간 분기"],
        "chromatic": [0.30, 0.48, 0.22],
    },
    "proto::tension_to_message": {
        "rotor_category": "성장 로터",
        "scale_band": "S3",
        "invariants": ["미해소 장력 -> 외부 확인 변환 경로"],
        "variables": ["표현 언어", "상대 응답 및 기준 수정"],
        "chromatic": [0.46, 0.24, 0.30],
    },
    "proto::win_foreground_window": {
        "rotor_category": "세계 접촉 로터",
        "scale_band": "S2~S3",
        "invariants": ["현재 활성 OS 창 포커스 출처"],
        "variables": ["사용자 창 전환", "다중 작업 문맥"],
        "chromatic": [0.42, 0.32, 0.26],
    },
    "proto::os_screen_retina": {
        "rotor_category": "입력 로터",
        "scale_band": "S1~S3",
        "invariants": ["디스플레이 광학 대비·운동 흐름"],
        "variables": ["해상도", "화면 갱신 리듬", "미해석 시각 패턴"],
        "chromatic": [0.48, 0.26, 0.26],
    },
    "proto::os_tkinter_dialog": {
        "rotor_category": "표현 로터",
        "scale_band": "S3",
        "invariants": ["양방향 인간 접촉 GUI 경계"],
        "variables": ["외부 권한 승인", "사용자 응답·거절"],
        "chromatic": [0.44, 0.28, 0.28],
    },
    "proto::os_powershell_voice": {
        "rotor_category": "표현 로터",
        "scale_band": "S3",
        "invariants": ["음성(SAPI) 감각 전달 경로"],
        "variables": ["오디오 장치 상태", "외부 권한 승인"],
        "chromatic": [0.52, 0.20, 0.28],
    },
    "proto::os_desktop_note": {
        "rotor_category": "지속성 로터",
        "scale_band": "S2~S3",
        "invariants": ["출처 보존 비동기 문서 전달"],
        "variables": ["열람 시점", "외부 권한 승인"],
        "chromatic": [0.28, 0.50, 0.22],
    },
}


def _structure_to_rotor_descriptor(struct: Any, idx: int) -> Dict[str, Any]:
    sid = str(getattr(struct, "structure_id", f"struct::{idx}"))
    meta = OS_ROTOR_CATEGORY_MAP.get(
        sid,
        {
            "rotor_category": "세계 접촉 로터" if sid.startswith("env::") else "지속성 로터",
            "scale_band": "S0~S2",
            "invariants": ["실제 호스트 관측 출처"],
            "variables": ["환경 변화", "미관측 경계"],
            "chromatic": [0.34, 0.38, 0.28],
        },
    )
    ports = [
        {
            "name": str(getattr(p, "name", "")),
            "direction": str(getattr(p, "direction", "")),
            "signal_type": str(getattr(p, "medium", "") or getattr(p, "signal_type", "")),
        }
        for p in getattr(struct, "ports", ())
    ]
    immutable = bool(getattr(struct, "immutable_external", False))
    requires_perm = bool(getattr(struct, "requires_outward_permission", False))
    relation_status = "invariant" if immutable else ("open" if requires_perm else "variable")
    angle = round((idx * 2.0 * math.pi) / 9.0, 4)
    return {
        "id": sid,
        "scale": int(getattr(struct, "scale", 1)),
        "scale_band": meta["scale_band"],
        "rotor_category": meta["rotor_category"],
        "description_ko": str(getattr(struct, "description_ko", sid)),
        "relation_status": relation_status,
        "immutable_external": immutable,
        "requires_outward_permission": requires_perm,
        "ports": ports,
        "invariants": meta["invariants"],
        "variables": meta["variables"],
        "chromatic_lens": {
            "flux_red": meta["chromatic"][0],
            "order_blue": meta["chromatic"][1],
            "entropy_yellow": meta["chromatic"][2],
        },
        "phase_angle_rad": angle,
        "signature": dict(getattr(struct, "signature", {}) or {}),
    }


def _build_port_couplings(rotors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Find natural port-to-port connectivity beams (out.signal_type == in.signal_type)."""
    edges: List[Dict[str, Any]] = []
    for src in rotors:
        out_ports = [p for p in src["ports"] if p["direction"] == "out"]
        for dst in rotors:
            if src["id"] == dst["id"]:
                continue
            in_ports = [p for p in dst["ports"] if p["direction"] == "in"]
            for op in out_ports:
                for ip in in_ports:
                    if op["signal_type"] and op["signal_type"] == ip["signal_type"]:
                        edges.append(
                            {
                                "from": src["id"],
                                "to": dst["id"],
                                "signal_type": op["signal_type"],
                                "coupling_strength": 0.85 if src["immutable_external"] else 0.65,
                            }
                        )
    return edges


def probe_host_boundary(file_limit: int = 6) -> Dict[str, Any]:
    protocols = discover_real_os_protocols(WORKSPACE_ROOT)
    seeds = capture_live_environment_seed(WORKSPACE_ROOT, file_limit=file_limit)

    proto_rotors = [_structure_to_rotor_descriptor(s, i) for i, s in enumerate(protocols)]
    seed_rotors = [_structure_to_rotor_descriptor(s, i + len(proto_rotors)) for i, s in enumerate(seeds)]
    all_rotors = proto_rotors + seed_rotors
    couplings = _build_port_couplings(all_rotors)

    return {
        "status": "ok",
        "observed_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "host": {
            "platform": sys.platform,
            "os_release": f"{platform.system()} {platform.release()}",
            "python_version": platform.python_version(),
            "workspace_root": str(WORKSPACE_ROOT),
        },
        "boundary_honesty": {
            "observable_here": [
                "실제 OS 파일·디렉터리 위상",
                "Python AST/컴파일 불변 문법 경계",
                "호스트 가용 프로토콜 목록 및 포트 결합성",
            ],
            "unobserved_or_gated": [
                "다른 브라우저 탭·임의 웹페이지 내용 (수집 안 함)",
                "외부 권한이 필요한 GUI/음성/문서 발신 (승인 전 차단)",
                "하드웨어 저수준 전원·클록·버스 레지스터 (가변/미관측 유지)",
            ],
        },
        "protocol_rotors": proto_rotors,
        "environment_seeds": seed_rotors,
        "coupling_beams": couplings,
    }


def _tokenize_korean_english(text: str) -> List[str]:
    cleaned = []
    cur = []
    for ch in text.lower():
        if ch.isalnum() or ("\uac00" <= ch <= "\ud7a3"):
            cur.append(ch)
        else:
            if cur:
                cleaned.append("".join(cur))
                cur = []
    if cur:
        cleaned.append("".join(cur))
    return [t for t in cleaned if len(t) >= 2]


def couple_principle_to_rotor(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts ANY user-described principle structure into a 5-frame Scale-Rotor
    representation (Point -> Line -> Plane -> Cube -> Coupled Sphere) and couples
    it against the live host OS protocol rotors without collapsing unknowns.
    """
    name = str(payload.get("name") or "이름 없는 원리 구조").strip()
    invariants_raw = str(payload.get("invariants") or "").strip()
    variables_raw = str(payload.get("variables") or "").strip()
    boundary_raw = str(payload.get("boundary") or "").strip()
    relation_raw = str(payload.get("relation") or "").strip()
    world_id = str(payload.get("world_id") or "home")
    input_flux = float(payload.get("input_flux", 0.0) or 0.0)

    inv_list = [x.strip() for x in invariants_raw.split(",") if x.strip()] or ["아직 명시되지 않은 불변 축 (관측 필요)"]
    var_list = [x.strip() for x in variables_raw.split(",") if x.strip()] or ["열려 있는 가변 조건"]

    # Derive analogical Red/Blue/Yellow tendencies from structural balance (never hardcoded dogma)
    inv_density = min(1.0, len(inv_list) / 4.0)
    var_density = min(1.0, len(var_list) / 4.0)
    rel_density = min(1.0, len(_tokenize_korean_english(relation_raw)) / 10.0)
    flux_red = round(min(0.95, 0.25 + 0.45 * rel_density + 0.25 * min(1.0, input_flux)), 3)
    order_blue = round(min(0.95, 0.25 + 0.55 * inv_density), 3)
    entropy_yellow = round(min(0.95, 0.20 + 0.55 * var_density), 3)
    total_c = max(1e-6, flux_red + order_blue + entropy_yellow)
    norm_chroma = {
        "flux_red": round(flux_red / total_c, 3),
        "order_blue": round(order_blue / total_c, 3),
        "entropy_yellow": round(entropy_yellow / total_c, 3),
    }

    # Find resonant host OS protocol rotors via token & chromatic affinity
    host_snapshot = probe_host_boundary(file_limit=4)
    query_tokens = set(_tokenize_korean_english(f"{name} {invariants_raw} {variables_raw} {boundary_raw} {relation_raw}"))
    resonant_host: List[Tuple[float, Dict[str, Any]]] = []
    for pr in host_snapshot["protocol_rotors"]:
        pr_tokens = set(
            _tokenize_korean_english(
                f"{pr['id']} {pr['rotor_category']} {pr['description_ko']} "
                f"{' '.join(pr['invariants'])} {' '.join(pr['variables'])}"
            )
        )
        overlap = len(query_tokens & pr_tokens)
        c = pr["chromatic_lens"]
        chroma_sim = 1.0 - (
            abs(norm_chroma["flux_red"] - c["flux_red"])
            + abs(norm_chroma["order_blue"] - c["order_blue"])
            + abs(norm_chroma["entropy_yellow"] - c["entropy_yellow"])
        ) / 2.0
        score = round(min(0.99, 0.45 * chroma_sim + 0.22 * min(3, overlap)), 3)
        resonant_host.append((score, pr))

    resonant_host.sort(key=lambda x: x[0], reverse=True)
    top_couplings = [
        {
            "protocol_id": pr["id"],
            "rotor_category": pr["rotor_category"],
            "resonance": score,
            "shared_boundary": pr["description_ko"],
        }
        for score, pr in resonant_host[:3]
    ]

    # 5-Frame Progression (escaping point-only cognition)
    phase_frames = {
        "point": {
            "label": "점 (단일 원리·씨앗)",
            "summary": f"'{name}' — 불변 {len(inv_list)}축 / 가변 {len(var_list)}축으로 응축된 씨앗",
        },
        "line": {
            "label": "선 (인과 궤적·운동성)",
            "summary": relation_raw or f"{inv_list[0]} 기준축을 따라 {var_list[0]} 변화가 이어지는 궤적",
        },
        "plane": {
            "label": "면 (불변 0 × 가변 1 간섭 단면)",
            "summary": f"불변({', '.join(inv_list[:2])}) × 가변({', '.join(var_list[:2])}) 경계막: {boundary_raw or '미지정(열린 경계)'}",
        },
        "cube": {
            "label": "시공간 큐브 (분기 세계 이력)",
            "summary": f"세계 '{world_id}'의 성장 나이테 위에서 분기 전후 보존/변화를 대조하는 입체 궤적",
        },
        "sphere": {
            "label": "구체 (전방위 결합 로터)",
            "summary": f"호스트 프로토콜 {top_couplings[0]['protocol_id']}({top_couplings[0]['rotor_category']}) 등과 공명({top_couplings[0]['resonance']})하며 회전하는 개방 로터"
            if top_couplings
            else "전방위 결합 대기 상태",
        },
    }

    return {
        "status": "ok",
        "converted_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "rotor": {
            "id": f"principle::{int(time.time() * 1000)}",
            "name": name,
            "world_id": world_id,
            "invariants": inv_list,
            "variables": var_list,
            "boundary_membrane": boundary_raw or "아직 경계가 명시되지 않음 (열린 경계 유지)",
            "relation_flow": relation_raw or "변화 관계 관측 대기",
            "chromatic_lens": norm_chroma,
            "phase_frames": phase_frames,
            "host_couplings": top_couplings,
        },
    }


_SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "archive", "build", "dist"}


def _scan_workspace_recency(limit: int = 10) -> Tuple[List[Dict[str, Any]], int]:
    """Scans real workspace file mtimes to separate recently changed vs invariant files."""
    now = time.time()
    entries: List[Tuple[float, str, float]] = []
    total_files = 0
    for root, dirs, files in os.walk(WORKSPACE_ROOT):
        dirs[:] = [d for d in dirs if d not in _SKIP_DIRS and not d.startswith(".")]
        for fname in files:
            if fname.startswith("."):
                continue
            fpath = Path(root) / fname
            try:
                st = fpath.stat()
                total_files += 1
                rel = str(fpath.relative_to(WORKSPACE_ROOT)).replace("\\", "/")
                entries.append((st.st_mtime, rel, st.st_size / 1024.0))
            except OSError:
                continue
            if total_files >= 450:
                break
        if total_files >= 450:
            break

    entries.sort(key=lambda x: x[0], reverse=True)
    top_files = []
    for mtime, rel, size_kb in entries[:limit]:
        age_sec = max(0.0, now - mtime)
        top_files.append(
            {
                "id": f"file::{rel}",
                "kind": "workspace_file",
                "name": rel,
                "mtime": round(mtime, 2),
                "age_sec": round(age_sec, 1),
                "size_kb": round(size_kb, 2),
                "recency_flux": round(math.exp(-age_sec / 180.0), 4),
            }
        )
    return top_files, total_files


def sense_live_os_telemetry(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    3-Stage Nested Scale-Observation Rotor on REAL live OS telemetry:
      Stage 1 (Observation): Live processes (RSS, CPU time) + workspace file recency + host RAM/CPU
      Stage 2 (Delta Observation): Compare prev_snapshot(t-1) vs now(t) -> Changed (1) vs Invariant (0)
      Stage 3 (Meta-Scale Re-Observation): Continuous Attention/Ascension ranking, Scale Horizon,
              Subjective Perspective, and adaptive cycle cadence.
    """
    prev = payload.get("prev_snapshot") or {}
    lens = payload.get("attention_lens") or {}
    w_change = float(lens.get("w_change", 0.45))
    w_rss = float(lens.get("w_rss", 0.38))
    w_novelty = float(lens.get("w_novelty", 0.17))
    w_sum = max(1e-6, w_change + w_rss + w_novelty)
    w_change, w_rss, w_novelty = w_change / w_sum, w_rss / w_sum, w_novelty / w_sum

    # --- Stage 1: Real Host Observation ---
    sys_mem = {"total_gb": 0.0, "used_gb": 0.0, "percent": 0.0}
    sys_cpu_pct = 0.0
    procs_raw: List[Dict[str, Any]] = []

    if psutil is not None:
        vm = psutil.virtual_memory()
        sys_mem = {
            "total_gb": round(vm.total / (1024 ** 3), 2),
            "used_gb": round(vm.used / (1024 ** 3), 2),
            "percent": round(float(vm.percent), 1),
        }
        sys_cpu_pct = round(float(psutil.cpu_percent(interval=0.04)), 1)
        for p in psutil.process_iter(["pid", "name", "memory_info", "cpu_times", "num_threads"]):
            try:
                info = p.info
                mi = info.get("memory_info")
                rss_mb = (mi.rss / (1024 * 1024)) if mi else 0.0
                if rss_mb < 15.0:
                    continue
                ct = info.get("cpu_times")
                cpu_s = float((ct.user + ct.system) if ct else 0.0)
                procs_raw.append(
                    {
                        "id": f"proc::{info['pid']}",
                        "kind": "os_process",
                        "pid": int(info["pid"]),
                        "name": str(info.get("name") or "unknown"),
                        "rss_mb": round(rss_mb, 1),
                        "cpu_s": round(cpu_s, 3),
                        "threads": int(info.get("num_threads") or 0),
                    }
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

    procs_raw.sort(key=lambda x: x["rss_mb"], reverse=True)
    top_procs = procs_raw[:12]
    top_files, total_files_scanned = _scan_workspace_recency(limit=10)

    # --- Stage 2: Delta Observation & Circuit Conservation (Order Rotor vs Error Rotor) ---
    prev_procs = {p["id"]: p for p in (prev.get("processes") or []) if "id" in p}
    prev_files = {f["id"]: f for f in (prev.get("files") or []) if "id" in f}
    prev_hist = prev.get("rss_history") or {}
    next_hist: Dict[str, List[float]] = {}

    max_rss = max([p["rss_mb"] for p in top_procs] + [1.0])
    max_file_kb = max([f["size_kb"] for f in top_files] + [1.0])

    attention_targets: List[Dict[str, Any]] = []
    changed_items: List[Dict[str, Any]] = []
    invariant_items: List[Dict[str, Any]] = []
    error_rotors: List[Dict[str, Any]] = []

    for p in top_procs:
        old = prev_procs.get(p["id"])
        is_new = old is None and bool(prev_procs)
        delta_rss = round(p["rss_mb"] - old["rss_mb"], 2) if old else 0.0
        delta_cpu = round(max(0.0, p["cpu_s"] - old["cpu_s"]), 3) if old else 0.0

        # Track short circulation history (tensor-like flow over time, not a single point!)
        hist = list(prev_hist.get(p["id"], []))[-4:]
        hist.append(p["rss_mb"])
        next_hist[p["id"]] = hist

        # Circuit Conservation Check (Order Rotor vs Chaos/Leak Error Rotor):
        # Monotonic RSS expansion across >=3 ticks without return flow violates closed circulation
        diffs = [round(hist[i + 1] - hist[i], 2) for i in range(len(hist) - 1)]
        monotonic_inflation = len(diffs) >= 2 and all(d > 1.2 for d in diffs)
        if monotonic_inflation:
            circuit_role = "error_rotor_leak"
            circuit_label_ko = "오류 로터 (순환 이탈 · 단조 팽창)"
        elif is_new or abs(delta_rss) >= 1.5 or delta_cpu >= 0.03:
            circuit_role = "active_circulation"
            circuit_label_ko = "질서 로터 (활성 순환 흐름)"
        else:
            circuit_role = "order_invariant"
            circuit_label_ko = "질서 로터 (안정 상주 0000)"

        change_flux = min(1.0, abs(delta_rss) / 25.0 + delta_cpu / 0.35)
        resident_mass = min(1.0, math.log1p(p["rss_mb"]) / math.log1p(max_rss))
        novelty_open = 1.0 if (is_new or monotonic_inflation) else min(1.0, abs(delta_rss) / 50.0)
        attention = round(w_change * change_flux + w_rss * resident_mass + w_novelty * novelty_open, 4)

        status = "changed" if circuit_role != "order_invariant" else "invariant"
        item = {
            **p,
            "delta_rss_mb": delta_rss,
            "delta_cpu_s": delta_cpu,
            "rss_diffs": diffs,
            "circuit_role": circuit_role,
            "circuit_label_ko": circuit_label_ko,
            "change_flux": round(change_flux, 3),
            "resident_mass": round(resident_mass, 3),
            "novelty_open": round(novelty_open, 3),
            "attention_score": attention,
            "state_class": status,
        }
        attention_targets.append(item)
        (changed_items if status == "changed" else invariant_items).append(item)
        if monotonic_inflation:
            error_rotors.append(item)

    for f in top_files:
        old = prev_files.get(f["id"])
        is_new = old is None and bool(prev_files)
        mtime_changed = (old is not None) and (abs(f["mtime"] - old["mtime"]) > 0.05)
        change_flux = 1.0 if mtime_changed else f["recency_flux"]
        resident_mass = min(1.0, math.log1p(f["size_kb"]) / math.log1p(max_file_kb)) * 0.55
        novelty_open = 1.0 if (is_new or mtime_changed) else (0.45 if f["age_sec"] < 90.0 else 0.08)
        attention = round(w_change * change_flux + w_rss * resident_mass + w_novelty * novelty_open, 4)

        status = "changed" if (mtime_changed or is_new or f["age_sec"] < 120.0) else "invariant"
        circuit_role = "active_circulation" if status == "changed" else "order_invariant"
        circuit_label_ko = "변화 감지 1 (최근 파일 흐름)" if status == "changed" else "질서 로터 (불변 파일 0000)"
        item = {
            **f,
            "mtime_changed": mtime_changed,
            "circuit_role": circuit_role,
            "circuit_label_ko": circuit_label_ko,
            "change_flux": round(change_flux, 3),
            "resident_mass": round(resident_mass, 3),
            "novelty_open": round(novelty_open, 3),
            "attention_score": attention,
            "state_class": status,
        }
        attention_targets.append(item)
        (changed_items if status == "changed" else invariant_items).append(item)

    attention_targets.sort(key=lambda x: x["attention_score"], reverse=True)

    # --- Stage 3: Meta-Scale Re-Observation (Scale Horizon, Perspective, Adaptive Cadence) ---
    total_obs = max(1, len(attention_targets))
    changed_ratio = round(len(changed_items) / total_obs, 3)
    invariant_ratio = round(1.0 - changed_ratio, 3)
    mean_flux = round(sum(x["change_flux"] for x in attention_targets) / total_obs, 3)
    mean_mass = round(sum(x["resident_mass"] for x in attention_targets) / total_obs, 3)
    mean_novelty = round(sum(x["novelty_open"] for x in attention_targets) / total_obs, 3)

    # Continuous Scale Horizon sigma in [0.12, 0.92]:
    # High recent change flux -> pulls sigma toward Micro (0.15~0.35) for sharp focus
    # High invariant mass -> pulls sigma toward Macro (0.65~0.88) for wide structural view
    scale_horizon = round(max(0.12, min(0.92, 0.52 + 0.36 * (invariant_ratio - changed_ratio) - 0.18 * mean_flux)), 3)

    if mean_flux >= 0.38 or changed_ratio >= 0.5:
        perspective = "최근 변화 추적 시야 (미시 집중 · 어센션)"
        recommended_frame = "line" if mean_novelty < 0.35 else "plane"
    elif mean_novelty >= 0.32:
        perspective = "미지 경계 탐색 시야 (발산 · 분기)"
        recommended_frame = "cube"
    elif mean_mass >= 0.55 and invariant_ratio >= 0.6:
        perspective = "상주 질량·불변 구조 조망 시야 (거시 재관측)"
        recommended_frame = "sphere"
    else:
        perspective = "변화×상주 균형 시야 (중시 결합)"
        recommended_frame = "plane"

    # Real adaptive resource allocation: fast cadence under real flux, calm under invariance
    recommended_cadence_ms = int(round(12000 - min(1.0, mean_flux * 1.4 + changed_ratio * 0.4) * 7500))
    recommended_cadence_ms = max(3500, min(12000, recommended_cadence_ms))

    top_focus = attention_targets[0] if attention_targets else None

    return {
        "status": "ok",
        "sensed_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "system": {
            "memory": sys_mem,
            "cpu_percent": sys_cpu_pct,
            "total_files_scanned": total_files_scanned,
            "psutil_active": psutil is not None,
        },
        "stage1_observation": {
            "processes": top_procs,
            "files": top_files,
            "rss_history": next_hist,
        },
        "stage2_delta": {
            "changed_count": len(changed_items),
            "invariant_count": len(invariant_items),
            "error_rotor_count": len(error_rotors),
            "changed_ratio": changed_ratio,
            "invariant_ratio": invariant_ratio,
            "changed_preview": [
                {"id": x["id"], "name": x["name"], "kind": x["kind"], "change_flux": x["change_flux"]}
                for x in changed_items[:5]
            ],
            "invariant_preview": [
                {"id": x["id"], "name": x["name"], "kind": x["kind"], "resident_mass": x["resident_mass"]}
                for x in invariant_items[:5]
            ],
        },
        "stage3_meta_reobservation": {
            "scale_horizon": scale_horizon,
            "subjective_perspective": perspective,
            "recommended_frame": recommended_frame,
            "recommended_cadence_ms": recommended_cadence_ms,
            "attention_lens": {
                "w_change": round(w_change, 3),
                "w_rss": round(w_rss, 3),
                "w_novelty": round(w_novelty, 3),
            },
            "chromatic_field": {
                "flux_red": mean_flux,
                "order_blue": mean_mass,
                "entropy_yellow": mean_novelty,
            },
            "top_focus": top_focus,
            "attention_ranking": attention_targets[:10],
        },
    }


def main() -> None:
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "Usage: os_ecology_bridge.py <probe|couple|sense>"}, ensure_ascii=False))
        sys.exit(1)

    cmd = sys.argv[1].strip().lower()
    if cmd == "probe":
        out = probe_host_boundary()
        print(json.dumps(out, ensure_ascii=False))
        return

    if cmd == "couple":
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        out = couple_principle_to_rotor(payload)
        print(json.dumps(out, ensure_ascii=False))
        return

    if cmd == "sense":
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        out = sense_live_os_telemetry(payload)
        print(json.dumps(out, ensure_ascii=False))
        return

    print(json.dumps({"status": "error", "message": f"Unknown command: {cmd}"}, ensure_ascii=False))
    sys.exit(1)


if __name__ == "__main__":
    main()
