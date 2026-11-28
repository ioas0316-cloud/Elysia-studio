"""
Dynamic Stream Prediction, Causal Reclassification & Intentional Recomposition Engine
=====================================================================================
Persistent, real-world dynamic learning & creative imagination loop obeying AGENTS.md
Section 7 (External Real-World Resource Ingestion + Dynamic-First Causal Reclassification):

  1. Persistent Disk Ledger (`L1_causal_field/data/dynamic_world_memory.json`):
     Survives restarts so Elysia accumulates real dynamic laws, harvested moving
     entities, and intentional creative recompositions across sessions.

  2. Dynamic Stream Learning (t-1 -> t -> Î(t+1) <-> I(t+1)):
     - Recalls prior matching motion/light laws on disk when a new video/game/camera
       stream begins (warm-start cross-session generalization).
     - Logs real measured pixel prediction RMSE improvement (initial -> adapted),
       motion segmentation ratios (static background / moving entity / specular slip),
       and inferred physical motion laws (static, fluid wave drift, gravity/accel,
       periodic stride, illumination shift).

  3. Human-Like Intentional Creative Recomposition (의도 기반 모방·변조·재창조):
     - Interprets natural Korean/English creative intents (e.g., "햇살이 어두우니
       밝혀보기", "나무가 허전하니 두 그루 넣기", "쓸쓸해 보이니 강아지나 고양이
       데려오기", "혼자라 외로우니 두 사람이 포옹하는 장면으로 바꾸기") OR
       proposes Elysia's own autonomous aesthetic/emotional intent directly from
       measured real-pixel luminance, warmth, and foreground emptiness!
     - Emits concrete causal rotor & entity composition operations that the browser
       executes directly on the live video / screen-capture / photo stream with
       matched S4 illumination, directional ground shadows, and motion coupling.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import math
from pathlib import Path
import time
from typing import Any, Dict, List, Optional


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


class DynamicStreamImaginationEngine:
    """
    Canonical persistent dynamic-stream learning & intentional recomposition core.
    """

    DEFAULT_ENTITIES: List[Dict[str, Any]] = [
        {
            "id": "entity::puppy",
            "name": "강아지",
            "role": "따뜻한 동반 생명 실체",
            "mood_tags": ["쓸쓸함 해소", "온기", "생명감", "동반"],
            "asset_url": "/static/assets/real_world/entity_puppy.jpg",
            "default_scale": 0.24,
            "default_y": 0.78,
            "key_mode": "white_matte",
            "origin": "real_photo_seed",
        },
        {
            "id": "entity::cat",
            "name": "고양이",
            "role": "고요한 동반 생명 실체",
            "mood_tags": ["쓸쓸함 해소", "평온", "귀여움", "동반"],
            "asset_url": "/static/assets/real_world/entity_cat.jpg",
            "default_scale": 0.21,
            "default_y": 0.79,
            "key_mode": "white_matte",
            "origin": "real_photo_seed",
        },
        {
            "id": "entity::pine_tree",
            "name": "삼나무",
            "role": "자연 경관·공간 균형 실체",
            "mood_tags": ["허전함 해소", "숲", "균형", "자연"],
            "asset_url": "/static/assets/real_world/entity_pine_tree.jpg",
            "default_scale": 0.44,
            "default_y": 0.68,
            "key_mode": "white_matte",
            "origin": "real_photo_seed",
        },
        {
            "id": "entity::embrace",
            "name": "포옹하는 두 사람",
            "role": "인간 관계·온기 결합 실체",
            "mood_tags": ["외로움 해소", "포옹", "관계", "사랑"],
            "asset_url": "/static/assets/real_world/entity_embrace.jpg",
            "default_scale": 0.42,
            "default_y": 0.74,
            "key_mode": "white_matte",
            "origin": "real_photo_seed",
        },
    ]

    DEFAULT_MOTION_DNAS: List[Dict[str, Any]] = [
        {
            "id": "dna::predator_prowl",
            "name": "고양이과·호랑이 저중심 보행 리듬",
            "source_name": "생체역학 기준 시드 (사족 저중심 보행)",
            "stream_kind": "biomechanical_seed",
            "origin": "biomechanical_seed",
            "gait_regime": "predator_prowl",
            "gait_label_ko": "저중심 포식자 어슬렁 보행",
            "dominant_freq_hz": 1.15,
            "stride_amp_x": 0.018,
            "stride_amp_y": 0.011,
            "lean_coupling": 0.14,
            "bounce_coupling": 0.045,
            "trajectory_samples": [
                [
                    round(0.016 * math.sin(2.0 * math.pi * k / 24.0), 5),
                    round(-0.010 * abs(math.sin(2.0 * math.pi * k / 24.0)), 5),
                    round(1.0 + 0.035 * math.cos(4.0 * math.pi * k / 24.0), 4),
                    round(0.07 * math.sin(2.0 * math.pi * k / 24.0), 4),
                ]
                for k in range(24)
            ],
            "extracted_at": "2026-01-01T00:00:00Z",
        },
        {
            "id": "dna::playful_bound",
            "name": "경쾌한 탄성 도약·탐색 리듬",
            "source_name": "생체역학 기준 시드 (소형 동물 탄성 도약)",
            "stream_kind": "biomechanical_seed",
            "origin": "biomechanical_seed",
            "gait_regime": "bounding_leap",
            "gait_label_ko": "탄성 도약·호기심 구보",
            "dominant_freq_hz": 2.10,
            "stride_amp_x": 0.024,
            "stride_amp_y": 0.026,
            "lean_coupling": 0.22,
            "bounce_coupling": 0.09,
            "trajectory_samples": [
                [
                    round(0.022 * math.sin(2.0 * math.pi * k / 24.0), 5),
                    round(-0.028 * (max(0.0, math.sin(2.0 * math.pi * k / 24.0)) ** 1.3), 5),
                    round(1.0 - 0.065 * math.sin(2.0 * math.pi * k / 24.0), 4),
                    round(0.11 * math.cos(2.0 * math.pi * k / 24.0), 4),
                ]
                for k in range(24)
            ],
            "extracted_at": "2026-01-01T00:00:00Z",
        },
    ]

    def __init__(self, ledger_path: Optional[Path] = None) -> None:
        if ledger_path is None:
            root = Path(__file__).resolve().parents[2]
            ledger_path = root / "data" / "dynamic_world_memory.json"
        self.ledger_path: Path = Path(ledger_path)
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)

        self.learned_laws: List[Dict[str, Any]] = []
        self.harvested_entities: List[Dict[str, Any]] = [dict(e) for e in self.DEFAULT_ENTITIES]
        self.intentional_creations: List[Dict[str, Any]] = []
        self.real_corpus_profiles: List[Dict[str, Any]] = []
        self.motion_dna_library: List[Dict[str, Any]] = [dict(d) for d in self.DEFAULT_MOTION_DNAS]
        self.cross_world_transplants: List[Dict[str, Any]] = []
        self.entity_relations: Dict[str, Dict[str, Any]] = {}
        self.epistemic_research_bridges: List[Dict[str, Any]] = []
        self.world_social_field: Dict[str, Any] = {
            "preset_id": "peaceful_sanctuary",
            "presence_preset_id": "balanced",
            "alignment_preset_id": "neutral_good",
            "realm_label_ko": "평온한 안식처 · 무명 여행자",
            "authority": 0.25,          # 0.0 .. 1.0 (지위·권위·위압)
            "reputation": 0.20,         # -1.0 .. +1.0 (명성·악명)
            "regional_tension": 0.14,   # 0.0 .. 1.0 (지역 긴장·전장)
            "faction_resonance": 0.20,  # -1.0 .. +1.0 (세력 우호·적대)
            "race_label_ko": "인간 방랑자",
            "trait_label_ko": "열린 호기심",
            "gender_presentation": "androgynous",  # feminine | masculine | androgynous
            "allure_gravity": 0.48,     # 0.0 .. 1.0 (매력·미모 시선 인력 로터)
            "charisma_rotor": 0.45,     # 0.0 .. 1.0 (카리스마·품격·예우 로터)
            "alignment_order": 0.20,    # -1.0(혼돈) .. +1.0(질서)
            "alignment_good": 0.35,     # -1.0(악)   .. +1.0(선)
            "alignment_label_ko": "중립 선",
            "spirit_affinity": 0.40,    # 0.0 .. 1.0 (정령·신수 친화력)
            "mana_affinity": 0.35,      # 0.0 .. 1.0 (마나·환경 공명도)
            "beast_mastery": 0.42,      # 0.0 .. 1.0 (야수·몬스터 교감 숙련도)
        }
        self.distilled_optical_priors: Dict[str, Any] = {
            "corpus_count": 0,
            "total_pixels_studied": 0,
            "sky_to_ground_ratio": 1.38,
            "horizon_mist_ratio": 0.24,
            "mean_specular_ratio": 0.08,
            "warm_specular_coupling": 0.0,
            "summary": "실세계 이미지·영상 코퍼스 학습 대기 중",
        }
        self.total_frames_observed: int = 0
        self.total_self_corrections: int = 0
        self.updated_at: str = _now_iso()

        self._load_ledger()

    # -------------------------------------------------------------------------
    # Persistent Disk Ledger (Survives Restarts)
    # -------------------------------------------------------------------------

    def _load_ledger(self) -> None:
        if not self.ledger_path.exists():
            self._save_ledger()
            return
        try:
            raw = json.loads(self.ledger_path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                self.learned_laws = list(raw.get("learned_laws") or [])[-32:]
                stored_ents = list(raw.get("harvested_entities") or [])
                by_id = {e["id"]: e for e in self.DEFAULT_ENTITIES}
                for se in stored_ents:
                    if isinstance(se, dict) and se.get("id"):
                        by_id[str(se["id"])] = se
                self.harvested_entities = list(by_id.values())[-24:]
                self.intentional_creations = list(raw.get("intentional_creations") or [])[-32:]
                self.real_corpus_profiles = list(raw.get("real_corpus_profiles") or [])[-80:]
                stored_dnas = list(raw.get("motion_dna_library") or [])
                dna_by_id = {d["id"]: dict(d) for d in self.DEFAULT_MOTION_DNAS}
                for sd in stored_dnas:
                    if isinstance(sd, dict) and sd.get("id"):
                        dna_by_id[str(sd["id"])] = sd
                self.motion_dna_library = list(dna_by_id.values())[-24:]
                self.cross_world_transplants = list(raw.get("cross_world_transplants") or [])[-32:]
                if isinstance(raw.get("entity_relations"), dict):
                    self.entity_relations = dict(raw["entity_relations"])
                self.epistemic_research_bridges = list(raw.get("epistemic_research_bridges") or [])[-24:]
                if isinstance(raw.get("world_social_field"), dict):
                    self.world_social_field.update(raw["world_social_field"])
                if isinstance(raw.get("distilled_optical_priors"), dict):
                    self.distilled_optical_priors.update(raw["distilled_optical_priors"])
                self.total_frames_observed = int(raw.get("total_frames_observed") or 0)
                self.total_self_corrections = int(raw.get("total_self_corrections") or 0)
                self.updated_at = str(raw.get("updated_at") or _now_iso())
        except Exception:
            # Never crash on corrupted file; preserve clean defaults
            self._save_ledger()

    def _save_ledger(self) -> None:
        payload = {
            "schema": "elysia.dynamic_world_memory.v1",
            "updated_at": self.updated_at,
            "total_frames_observed": self.total_frames_observed,
            "total_self_corrections": self.total_self_corrections,
            "learned_laws": self.learned_laws[-32:],
            "harvested_entities": self.harvested_entities[-24:],
            "intentional_creations": self.intentional_creations[-32:],
            "real_corpus_profiles": self.real_corpus_profiles[-80:],
            "motion_dna_library": self.motion_dna_library[-24:],
            "cross_world_transplants": self.cross_world_transplants[-32:],
            "entity_relations": self.entity_relations,
            "epistemic_research_bridges": self.epistemic_research_bridges[-24:],
            "world_social_field": self.world_social_field,
            "distilled_optical_priors": self.distilled_optical_priors,
        }
        try:
            self.ledger_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # 1. Dynamic Stream Observation, Law Extraction & Cross-Session Prior Recall
    # -------------------------------------------------------------------------

    def classify_motion_law(
        self,
        flow_x: float,
        flow_y: float,
        accel_x: float,
        accel_y: float,
        moving_ratio: float,
        specular_slip_ratio: float,
    ) -> Dict[str, Any]:
        speed = math.hypot(flow_x, flow_y)
        accel = math.hypot(accel_x, accel_y)
        if speed < 0.12 and moving_ratio < 0.04:
            return {
                "law_type": "static_equilibrium",
                "label_ko": "정적 평형 배경 (t=0 고정 기준축)",
                "causal_mechanism": "프레임 간 변위 ≈ 0 — 정적 구조 기억으로 즉시 압축 가능",
            }
        if accel_y > 0.25 and abs(accel_y) > abs(accel_x) * 1.35:
            return {
                "law_type": "gravity_acceleration",
                "label_ko": "중력·수직 가속 낙하 법칙 (물방울·낙하체)",
                "causal_mechanism": f"수직 가속도 a_y={accel_y:+.2f} 감지 — 위치 2차 미분 불변식으로 다음 궤적 예측",
            }
        if specular_slip_ratio > 0.09 and moving_ratio > 0.12:
            return {
                "law_type": "fluid_specular_drift",
                "label_ko": "유체 파동·경면 윤슬 분리 법칙 (바다·수면)",
                "causal_mechanism": (
                    f"유체 흐름 v=({flow_x:+.2f},{flow_y:+.2f})와 다른 속도로 미끄러지는 "
                    f"경면광({specular_slip_ratio*100:.1f}%)이 물성과 광원을 실시간 분리"
                ),
            }
        if accel > 0.18 and moving_ratio < 0.35:
            return {
                "law_type": "autonomous_entity_motion",
                "label_ko": "자율 개체 이동 법칙 (생명체·캐릭터·사물)",
                "causal_mechanism": (
                    f"배경과 분리된 응집 이동 실체({moving_ratio*100:.1f}%)가 "
                    f"속도({flow_x:+.2f},{flow_y:+.2f})·가속({accel_x:+.2f},{accel_y:+.2f})으로 자율 전개"
                ),
            }
        return {
            "law_type": "coherent_camera_or_scene_flow",
            "label_ko": "거시 시점·환경 연속 드리프트 법칙",
            "causal_mechanism": f"전역 S3 흐름 로터 v=({flow_x:+.2f},{flow_y:+.2f})로 전체 프레임 위상 예측",
        }

    def recall_prior_law(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recalls the closest previously learned dynamic law from persistent disk
        memory to warm-start prediction on a newly opened video / game stream.
        """
        source_name = str(params.get("source_name") or "").strip().lower()
        target_luma = float(params.get("mean_luma") or 0.5)
        target_speed = float(params.get("flow_speed") or 0.0)

        best: Optional[Dict[str, Any]] = None
        best_score = -1e9
        for law in self.learned_laws:
            score = 0.0
            lname = str(law.get("source_name") or "").lower()
            if source_name and (source_name in lname or lname in source_name):
                score += 2.5
            score -= abs(float(law.get("mean_luma", 0.5)) - target_luma) * 1.4
            lv = law.get("learned_flow_vec") or [0.0, 0.0]
            lspeed = math.hypot(float(lv[0]), float(lv[1]))
            score -= abs(lspeed - target_speed) * 0.35
            score += float(law.get("error_reduction_pct", 0.0)) * 0.01
            if score > best_score:
                best_score = score
                best = law

        return {
            "status": "ok",
            "matched": best is not None,
            "prior_law": best,
            "memory_summary": self.get_snapshot()["memory_summary"],
        }

    def record_stream_learning(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Records a real dynamic stream learning session where Elysia predicted
        Î(t+1), compared against real arriving I(t+1), self-corrected her rotors,
        and reduced pixel RMSE. Persists immediately to disk!
        """
        source_name = str(params.get("source_name") or "동적 실세계 스트림").strip()[:80]
        stream_kind = str(params.get("stream_kind") or "video").strip()[:24]
        frames_observed = max(1, int(params.get("frames_observed") or 30))
        rmse_initial = round(max(0.0001, float(params.get("rmse_initial") or 0.085)), 5)
        rmse_adapted = round(max(0.0001, float(params.get("rmse_adapted") or 0.032)), 5)
        psnr_adapted = round(_clamp(float(params.get("psnr_adapted") or 30.0), 8.0, 68.0), 2)
        flow_x = round(_clamp(float(params.get("flow_x") or 0.0), -25.0, 25.0), 4)
        flow_y = round(_clamp(float(params.get("flow_y") or 0.0), -25.0, 25.0), 4)
        accel_x = round(_clamp(float(params.get("accel_x") or 0.0), -20.0, 20.0), 4)
        accel_y = round(_clamp(float(params.get("accel_y") or 0.0), -20.0, 20.0), 4)
        moving_ratio = round(_clamp(float(params.get("moving_entity_ratio") or 0.18), 0.0, 1.0), 4)
        specular_ratio = round(_clamp(float(params.get("specular_slip_ratio") or 0.08), 0.0, 1.0), 4)
        mean_luma = round(_clamp(float(params.get("mean_luma") or 0.5), 0.0, 1.0), 4)
        color_temp_k = int(_clamp(float(params.get("color_temp_k") or 5600), 1800, 11000))

        reduction_pct = round(
            _clamp((1.0 - rmse_adapted / max(1e-6, rmse_initial)) * 100.0, -50.0, 99.5),
            1,
        )
        law_cls = self.classify_motion_law(
            flow_x=flow_x,
            flow_y=flow_y,
            accel_x=accel_x,
            accel_y=accel_y,
            moving_ratio=moving_ratio,
            specular_slip_ratio=specular_ratio,
        )

        law_id = f"law::{abs(hash(source_name + law_cls['law_type'])) % 100000:05d}"
        entry = {
            "id": law_id,
            "source_name": source_name,
            "stream_kind": stream_kind,
            "frames_observed": frames_observed,
            "law_type": law_cls["law_type"],
            "law_label_ko": law_cls["label_ko"],
            "causal_mechanism": law_cls["causal_mechanism"],
            "learned_flow_vec": [flow_x, flow_y],
            "learned_accel_vec": [accel_x, accel_y],
            "moving_entity_ratio": moving_ratio,
            "specular_slip_ratio": specular_ratio,
            "mean_luma": mean_luma,
            "color_temp_k": color_temp_k,
            "rmse_initial": rmse_initial,
            "rmse_adapted": rmse_adapted,
            "psnr_adapted": psnr_adapted,
            "error_reduction_pct": reduction_pct,
            "at": _now_iso(),
        }

        self.learned_laws = [x for x in self.learned_laws if x["id"] != law_id]
        self.learned_laws.append(entry)
        self.learned_laws = self.learned_laws[-32:]
        self.total_frames_observed += frames_observed
        self.total_self_corrections += 1
        self.updated_at = _now_iso()
        self._save_ledger()

        snap = self.get_snapshot()
        snap["recorded_law"] = entry
        return snap

    # -------------------------------------------------------------------------
    # 2. Harvest Real Moving Entity from Live Dynamic Video into Persistent Memory
    # -------------------------------------------------------------------------

    def harvest_moving_entity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Saves a real moving foreground entity automatically segmented from a live
        video/game/camera stream into Elysia's persistent Ice entity library so
        she can duplicate, re-place, or recombine it into future scenes!
        """
        name = str(params.get("name") or f"수확 실체 #{len(self.harvested_entities) + 1}").strip()[:40]
        source_name = str(params.get("source_name") or "동적 스트림").strip()[:60]
        data_url = str(params.get("data_url") or "")
        # Cap stored thumbnail data URL length to keep ledger fast & lightweight
        if len(data_url) > 220_000:
            data_url = ""
        bbox = params.get("bbox_norm") or [0.35, 0.35, 0.25, 0.25]
        eid = f"entity::harvest_{len(self.harvested_entities) + 1:03d}_{abs(hash(name + _now_iso())) % 9999:04d}"
        ent = {
            "id": eid,
            "name": name,
            "role": f"[{source_name}]의 움직임 경계에서 자동 분리·수확한 실체",
            "mood_tags": ["실세계 수확", "복제 가능", "동적 분리"],
            "asset_url": data_url,
            "default_scale": round(_clamp(float(bbox[2] if len(bbox) > 2 else 0.24), 0.14, 0.48), 3),
            "default_y": 0.72,
            "key_mode": "alpha_direct",
            "origin": "live_motion_harvest",
            "source_name": source_name,
            "at": _now_iso(),
        }
        self.harvested_entities.append(ent)
        self.harvested_entities = self.harvested_entities[-24:]
        self.updated_at = _now_iso()
        self._save_ledger()

        snap = self.get_snapshot()
        snap["harvested_entity"] = ent
        return snap

    # -------------------------------------------------------------------------
    # 3. Human-Like Intentional Creative Recomposition (의도적 변조·재창조)
    # -------------------------------------------------------------------------

    def plan_intentional_recomposition(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translates either:
          (a) User's natural Korean/English creative intent (e.g., "쓸쓸해 보이니까
              귀여운 강아지 넣고 햇살도 밝혀줘", "나무가 허전하니 두 그루 추가해줘",
              "혼자라 외로워 보이니 두 사람이 포옹하는 온기로 바꿔줘"), OR
          (b) Autonomous Elysia reflection directly from live measured scene state
              (mean_luma, color_temp_k, moving_entity_ratio, existing_entity_count)
        into concrete causal rotor modulations + real-entity compositions, and
        persists the intentional creation into Ice memory.
        """
        intent_text = str(params.get("intent_text") or "").strip()
        autonomous = bool(params.get("autonomous", False))
        scene_luma = _clamp(float(params.get("mean_luma") or 0.45), 0.0, 1.0)
        scene_kelvin = float(params.get("color_temp_k") or 5600)
        moving_ratio = _clamp(float(params.get("moving_entity_ratio") or 0.12), 0.0, 1.0)
        existing_count = max(0, int(params.get("existing_entity_count") or 0))
        source_name = str(params.get("source_name") or "현재 실세계 장면").strip()[:60]

        s4_brightness_delta = 0.0
        s4_warmth_delta = 0.0
        s2_relight_deg = 0.0
        s1_specular_boost = 0.0
        spawn_ops: List[Dict[str, Any]] = []
        rationale_parts: List[str] = []

        # Helper to count Korean/digit multiplicity locally around the target keyword ("나무 두 그루" vs "강아지")
        def _extract_count(text: str, keywords: tuple, default_n: int = 1) -> int:
            for kw in keywords:
                pos = text.find(kw)
                if pos != -1:
                    window = text[max(0, pos - 6):min(len(text), pos + len(kw) + 9)]
                    if any(k in window for k in ("세 ", "3마리", "3개", "3그루", "세그루", "세마리", "셋")):
                        return 3
                    if any(k in window for k in ("두 ", "둘", "2마리", "2개", "2그루", "두그루", "두마리", "쌍")):
                        return 2
            return default_n

        if autonomous or not intent_text:
            # Elysia reads the ACTUAL measured pixels of the live scene and chooses her own human-like creative intent!
            if scene_luma < 0.44:
                s4_brightness_delta = 0.28
                s4_warmth_delta = 0.24
                s1_specular_boost = 0.35
                rationale_parts.append(
                    f"실측 명도({scene_luma:.2f})가 어두워 S4 햇살 조광을 따뜻하게 밝히고 S1 윤슬 반사를 살렸습니다"
                )
            elif scene_kelvin > 6400:
                s4_warmth_delta = 0.32
                s2_relight_deg = 24.0
                rationale_parts.append(
                    f"색온도({int(scene_kelvin)}K)가 차가워 황금빛 노을 조광 로터를 더해 온기를 불어넣었습니다"
                )

            if existing_count == 0 and moving_ratio < 0.16:
                spawn_ops.append({"entity_id": "entity::puppy", "x": 0.64, "y": 0.79, "scale": 0.23, "reason": "쓸쓸함 해소·생명감"})
                spawn_ops.append({"entity_id": "entity::pine_tree", "x": 0.18, "y": 0.67, "scale": 0.44, "reason": "좌측 공간 균형"})
                rationale_parts.append(
                    "움직이는 생명이 적어 화면이 쓸쓸해 보이므로 기억 속 강아지와 삼나무 실체를 S4 조광에 맞춰 함께 배치했습니다"
                )
            elif existing_count == 1:
                spawn_ops.append({"entity_id": "entity::cat", "x": 0.36, "y": 0.80, "scale": 0.20, "reason": "동반자 추가"})
                rationale_parts.append("홀로 있던 실체 곁에 고양이 동반자를 더해 관계적 온기를 확장했습니다")
            else:
                spawn_ops.append({"entity_id": "entity::embrace", "x": 0.50, "y": 0.74, "scale": 0.42, "reason": "따뜻한 인간 포옹"})
                s4_warmth_delta = max(s4_warmth_delta, 0.26)
                rationale_parts.append("장면의 중심에 두 사람이 포옹하는 온기를 결합해 정서적 초점을 완성했습니다")

            intent_text = "엘리시아 자율 의도: " + " · ".join(rationale_parts)
        else:
            t = intent_text.lower()

            # 1. Sunlight / Brightness / Warmth / Mood illumination intents
            if any(k in t for k in ("밝", "햇살", "햇빛", "환하", "빛", "sun", "bright")):
                s4_brightness_delta = 0.30
                s4_warmth_delta = 0.22
                s1_specular_boost = 0.40
                rationale_parts.append("S4 조광 명도·햇살 온기 상승 + S1 윤슬 증폭")
            if any(k in t for k in ("어둡", "밤", "달빛", "차갑", "시원", "새벽", "푸른", "dark", "cool")):
                s4_brightness_delta = -0.22
                s4_warmth_delta = -0.28
                rationale_parts.append("S4 조광을 고요한 청색·저조도 위상으로 전환")
            if any(k in t for k in ("노을", "따뜻", "황혼", "온기", "포근", "warm", "sunset")):
                s4_warmth_delta = max(s4_warmth_delta, 0.36)
                s4_brightness_delta = max(s4_brightness_delta, 0.14)
                s2_relight_deg = 28.0
                rationale_parts.append("S4 노을 색온도 + S2 측면 재조명(+28°)")
            if any(k in t for k in ("왼쪽", "우측", "오른쪽", "각도", "회전", "재조명")):
                s2_relight_deg = -42.0 if "왼쪽" in t else 42.0
                rationale_parts.append(f"S2 표면 법선 재조명 회전({s2_relight_deg:+.0f}°)")

            # 2. Entity Creation / Duplication / Companion Intents
            if any(k in t for k in ("포옹", "안고", "두 사람", "두사람", "커플", "함께", "embrace", "hug")):
                spawn_ops.append({"entity_id": "entity::embrace", "x": 0.50, "y": 0.74, "scale": 0.43, "reason": "포옹·관계 결합"})
                s4_warmth_delta = max(s4_warmth_delta, 0.22)
                rationale_parts.append("포옹하는 두 사람 실체를 S4 조광·그림자와 결합")
            if any(k in t for k in ("나무", "숲", "그루", "tree")):
                n_trees = max(1, min(3, _extract_count(t, ("나무", "그루", "숲", "tree"), 1)))
                xs = [0.18, 0.82, 0.30]
                for ti in range(n_trees):
                    spawn_ops.append({
                        "entity_id": "entity::pine_tree",
                        "x": xs[ti % len(xs)],
                        "y": 0.67 + (ti % 2) * 0.03,
                        "scale": 0.44 - ti * 0.04,
                        "reason": "허전한 풍경 균형 확장",
                    })
                rationale_parts.append(f"삼나무 실체 {n_trees}그루 배치 (조광·그림자 동기화)")
            if any(k in t for k in ("강아지", "개", "멍멍", "puppy", "dog")):
                n_pup = max(1, min(2, _extract_count(t, ("강아지", "멍멍", "puppy", "dog"), 1)))
                for pi in range(n_pup):
                    spawn_ops.append({
                        "entity_id": "entity::puppy",
                        "x": 0.62 - pi * 0.22,
                        "y": 0.80,
                        "scale": 0.23,
                        "reason": "따뜻한 강아지 동반",
                    })
                rationale_parts.append(f"강아지 실체 {n_pup}마리 결합")
            if any(k in t for k in ("고양이", "야옹", "냥", "cat")):
                n_cat = max(1, min(2, _extract_count(t, ("고양이", "야옹", "냥", "cat"), 1)))
                for ci in range(n_cat):
                    spawn_ops.append({
                        "entity_id": "entity::cat",
                        "x": 0.37 + ci * 0.24,
                        "y": 0.80,
                        "scale": 0.21,
                        "reason": "귀여운 고양이 동반",
                    })
                rationale_parts.append(f"고양이 실체 {n_cat}마리 결합")
            if any(k in t for k in ("쓸쓸", "외로", "허전")) and not spawn_ops:
                spawn_ops.append({"entity_id": "entity::puppy", "x": 0.60, "y": 0.80, "scale": 0.23, "reason": "쓸쓸함 해소"})
                s4_warmth_delta = max(s4_warmth_delta, 0.24)
                s4_brightness_delta = max(s4_brightness_delta, 0.16)
                rationale_parts.append("정서적 쓸쓸함을 해소하기 위해 강아지 실체 + 따뜻한 S4 햇살 결합")

            # Check custom harvested entities by name
            for he in self.harvested_entities:
                if he.get("origin") == "live_motion_harvest" and he["name"].lower() in t:
                    spawn_ops.append({
                        "entity_id": he["id"],
                        "x": 0.56,
                        "y": 0.72,
                        "scale": float(he.get("default_scale", 0.24)),
                        "reason": f"수확 실체 [{he['name']}] 재조합",
                    })
                    rationale_parts.append(f"수확한 실체 [{he['name']}] 재투입")

            if not rationale_parts:
                # Default graceful enhancement: harmonize lighting & balance
                s4_brightness_delta = 0.18
                s4_warmth_delta = 0.15
                s1_specular_boost = 0.25
                rationale_parts.append("장면 S4 조광 균형과 S1 반사 선명도 보강")

        cid = f"create::{len(self.intentional_creations) + 1:03d}"
        creation = {
            "id": cid,
            "source_name": source_name,
            "intent": intent_text,
            "autonomous": autonomous,
            "causal_plan": {
                "s4_brightness_delta": round(s4_brightness_delta, 3),
                "s4_warmth_delta": round(s4_warmth_delta, 3),
                "s2_relight_deg": round(s2_relight_deg, 1),
                "s1_specular_boost": round(s1_specular_boost, 3),
                "spawn_entities": spawn_ops,
            },
            "rationale": " + ".join(rationale_parts),
            "at": _now_iso(),
        }

        self.intentional_creations.append(creation)
        self.intentional_creations = self.intentional_creations[-32:]
        self.updated_at = _now_iso()
        self._save_ledger()

        snap = self.get_snapshot()
        snap["creation_result"] = creation
        return snap

    # -------------------------------------------------------------------------
    # 4. Real-World Multi-Asset Corpus Batch Ingestion & Optical Prior Distillation
    # -------------------------------------------------------------------------

    def ingest_real_corpus_batch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ingests measured real-pixel optical profiles from a batch of actual
        photographs / videos, distills empirical cross-scene illumination &
        atmosphere laws (sky-to-ground ratio, mist contrast attenuation,
        warmth-specular coupling), and persists them to disk so Elysia's
        world-space relighting gets grounded directly in real-world data!
        """
        raw_items = params.get("items") or []
        if not isinstance(raw_items, list):
            raw_items = []

        by_name = {str(p.get("source_name") or ""): p for p in self.real_corpus_profiles}
        ingested_now = 0
        for it in raw_items:
            if not isinstance(it, dict):
                continue
            sname = str(it.get("source_name") or "").strip()[:90]
            if not sname:
                continue
            sky_rgb = [int(_clamp(float(c), 0, 255)) for c in (it.get("sky_rgb") or [120, 140, 170])[:3]]
            hor_rgb = [int(_clamp(float(c), 0, 255)) for c in (it.get("horizon_rgb") or [140, 148, 158])[:3]]
            gnd_rgb = [int(_clamp(float(c), 0, 255)) for c in (it.get("ground_rgb") or [70, 76, 82])[:3]]
            sky_l = (0.2126 * sky_rgb[0] + 0.7152 * sky_rgb[1] + 0.0722 * sky_rgb[2]) / 255.0
            hor_l = (0.2126 * hor_rgb[0] + 0.7152 * hor_rgb[1] + 0.0722 * hor_rgb[2]) / 255.0
            gnd_l = (0.2126 * gnd_rgb[0] + 0.7152 * gnd_rgb[1] + 0.0722 * gnd_rgb[2]) / 255.0
            profile = {
                "source_name": sname,
                "media_kind": str(it.get("media_kind") or "photo")[:20],
                "pixel_count": max(1, int(it.get("pixel_count") or 0)),
                "sky_rgb": sky_rgb,
                "horizon_rgb": hor_rgb,
                "ground_rgb": gnd_rgb,
                "sky_luma": round(sky_l, 4),
                "horizon_luma": round(hor_l, 4),
                "ground_luma": round(gnd_l, 4),
                "color_temp_k": int(_clamp(float(it.get("color_temp_k") or 5600), 1800, 11000)),
                "mean_luma": round(_clamp(float(it.get("mean_luma") or 0.5), 0.0, 1.0), 4),
                "specular_ratio": round(_clamp(float(it.get("specular_ratio") or 0.05), 0.0, 1.0), 4),
                "normal_energy": round(_clamp(float(it.get("normal_energy") or 0.12), 0.0, 1.0), 4),
                "at": _now_iso(),
            }
            by_name[sname] = profile
            ingested_now += 1

        self.real_corpus_profiles = list(by_name.values())[-80:]
        n = len(self.real_corpus_profiles)
        if n > 0:
            total_px = sum(int(p.get("pixel_count", 0)) for p in self.real_corpus_profiles)
            ratios = [
                _clamp(float(p["sky_luma"]) / max(0.06, float(p["ground_luma"])), 0.45, 3.2)
                for p in self.real_corpus_profiles
            ]
            sky_ground_ratio = round(sum(ratios) / float(n), 3)
            mist_vals = [
                _clamp(abs(float(p["horizon_luma"]) - float(p["ground_luma"])) * 0.85, 0.08, 0.48)
                for p in self.real_corpus_profiles
            ]
            mist_ratio = round(sum(mist_vals) / float(n), 3)
            mean_spec = round(sum(float(p["specular_ratio"]) for p in self.real_corpus_profiles) / float(n), 4)
            mean_norm = round(sum(float(p["normal_energy"]) for p in self.real_corpus_profiles) / float(n), 4)

            # Empirical warmth-vs-specular correlation across real ingested images
            warmths = [max(0.0, (7000.0 - float(p["color_temp_k"])) / 4500.0) for p in self.real_corpus_profiles]
            specs = [float(p["specular_ratio"]) for p in self.real_corpus_profiles]
            mw = sum(warmths) / float(n)
            ms = sum(specs) / float(n)
            cov = sum((w - mw) * (s - ms) for w, s in zip(warmths, specs))
            vw = math.sqrt(sum((w - mw) ** 2 for w in warmths))
            vs = math.sqrt(sum((s - ms) ** 2 for s in specs))
            corr = round(cov / max(1e-6, vw * vs), 3) if (vw > 1e-6 and vs > 1e-6) else 0.0

            self.distilled_optical_priors = {
                "corpus_count": n,
                "ingested_this_batch": ingested_now,
                "total_pixels_studied": total_px,
                "sky_to_ground_ratio": sky_ground_ratio,
                "horizon_mist_ratio": mist_ratio,
                "mean_specular_ratio": mean_spec,
                "mean_normal_energy": mean_norm,
                "warm_specular_coupling": corr,
                "summary": (
                    f"실세계 {n}개 자산({total_px:,}px) 직접 학습 완료 — "
                    f"하늘/지면 조도비 {sky_ground_ratio:.2f}:1 · 대기 안개 계수 {mist_ratio:.2f} · "
                    f"평균 경면윤슬 {mean_spec*100:.1f}% · 색온도-윤슬 상관 {corr:+.2f}"
                ),
            }

        self.total_frames_observed += ingested_now
        self.updated_at = _now_iso()
        self._save_ledger()

        snap = self.get_snapshot()
        snap["corpus_batch_result"] = self.distilled_optical_priors
        return snap

    # -------------------------------------------------------------------------
    # 5. Cross-Media Causal Motion DNA Extraction & Living Actor Transplant (A -> B)
    # -------------------------------------------------------------------------

    def extract_motion_dna(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts a reusable multi-scale causal motion & behavior rhythm (Motion DNA)
        directly from real recorded frame-series centroid/velocity samples of Source A
        (video, game capture, webcam, or dynamic stream) so it can be transplanted
        into any different World B!
        """
        source_name = str(params.get("source_name") or "실시간 영상 A").strip()[:80]
        stream_kind = str(params.get("stream_kind") or "video").strip()[:24]
        custom_name = str(params.get("dna_name") or "").strip()[:60]
        raw_samples = params.get("samples") or []
        if not isinstance(raw_samples, list):
            raw_samples = []

        cleaned: List[Dict[str, float]] = []
        for s in raw_samples[-96:]:
            if not isinstance(s, dict):
                continue
            cleaned.append(
                {
                    "vx": _clamp(float(s.get("vx", 0.0)), -15.0, 15.0),
                    "vy": _clamp(float(s.get("vy", 0.0)), -15.0, 15.0),
                    "cx": _clamp(float(s.get("cx", 0.5)), 0.0, 1.0),
                    "cy": _clamp(float(s.get("cy", 0.5)), 0.0, 1.0),
                    "area": _clamp(float(s.get("area", 0.15)), 0.01, 1.0),
                    "dt": _clamp(float(s.get("dt", 0.033)), 0.008, 0.25),
                }
            )

        if len(cleaned) < 6:
            # Guarantee safe minimum sample length if triggered immediately on frame 1
            for k in range(12):
                ang = 2.0 * math.pi * k / 12.0
                cleaned.append(
                    {
                        "vx": 0.6 * math.cos(ang),
                        "vy": 0.25 * math.sin(ang),
                        "cx": 0.5 + 0.03 * math.sin(ang),
                        "cy": 0.5 + 0.015 * math.cos(ang),
                        "area": 0.16,
                        "dt": 0.033,
                    }
                )

        n = len(cleaned)
        total_sec = max(0.25, sum(s["dt"] for s in cleaned))
        mean_cx = sum(s["cx"] for s in cleaned) / float(n)
        mean_cy = sum(s["cy"] for s in cleaned) / float(n)
        mean_area = sum(s["area"] for s in cleaned) / float(n)
        mean_vx = sum(s["vx"] for s in cleaned) / float(n)
        mean_vy = sum(s["vy"] for s in cleaned) / float(n)

        # Measure real cadence frequency via zero-crossings of detrended velocity/centroid energy
        sig = [
            (s["vx"] - mean_vx) * 0.65 + (s["vy"] - mean_vy) * 0.35 + (s["cx"] - mean_cx) * 6.0
            for s in cleaned
        ]
        crossings = 0
        for i in range(1, n):
            if (sig[i - 1] <= 0.0 < sig[i]) or (sig[i - 1] >= 0.0 > sig[i]):
                crossings += 1
        dominant_freq_hz = round(_clamp((crossings / 2.0) / total_sec, 0.55, 3.60), 2)

        dx_series = [s["cx"] - mean_cx for s in cleaned]
        dy_series = [s["cy"] - mean_cy for s in cleaned]
        rms_x = math.sqrt(sum(v * v for v in dx_series) / float(n))
        rms_y = math.sqrt(sum(v * v for v in dy_series) / float(n))
        mean_speed = sum(math.hypot(s["vx"], s["vy"]) for s in cleaned) / float(n)

        stride_amp_x = round(_clamp(rms_x * 0.85 + mean_speed * 0.008, 0.008, 0.048), 4)
        stride_amp_y = round(_clamp(rms_y * 0.95 + abs(mean_vy) * 0.006, 0.005, 0.044), 4)
        lean_coupling = round(_clamp(0.08 + mean_speed * 0.065, 0.06, 0.30), 3)
        bounce_coupling = round(_clamp(0.03 + rms_y * 1.4, 0.025, 0.14), 3)

        # Classify locomotive behavioral regime directly from real measured dynamics
        if stride_amp_y > stride_amp_x * 1.12 and dominant_freq_hz >= 1.5:
            gait_regime = "bounding_leap"
            gait_label_ko = "탄성 도약·경쾌 보행 리듬"
        elif mean_speed > 1.35 and dominant_freq_hz <= 1.55:
            gait_regime = "predator_prowl"
            gait_label_ko = "저중심 추적·유연 보행 리듬"
        elif rms_x > rms_y * 1.6:
            gait_regime = "fluid_sway"
            gait_label_ko = "수평 유체·바람 스웨이 리듬"
        else:
            gait_regime = "curious_wander"
            gait_label_ko = "자율 탐색·호흡 보행 리듬"

        # Resample real recorded motion into a compact 24-phase closed causal rotor loop
        # [dx_norm, dy_norm, squash_stretch, tilt_rad]
        max_dx = max(1e-4, max(abs(v) for v in dx_series))
        max_dy = max(1e-4, max(abs(v) for v in dy_series))
        max_vx = max(0.25, max(abs(s["vx"]) for s in cleaned))
        trajectory_samples: List[List[float]] = []
        for k in range(24):
            pos = (k / 24.0) * (n - 1)
            idx0 = int(math.floor(pos))
            idx1 = min(n - 1, idx0 + 1)
            frac = pos - idx0
            s0, s1 = cleaned[idx0], cleaned[idx1]
            # Window-blend edges slightly so loop closes smoothly with C1 continuity
            vx_k = s0["vx"] * (1.0 - frac) + s1["vx"] * frac
            dx_k = ((dx_series[idx0] * (1.0 - frac) + dx_series[idx1] * frac) / max_dx) * stride_amp_x
            raw_dy = ((dy_series[idx0] * (1.0 - frac) + dy_series[idx1] * frac) / max_dy) * stride_amp_y
            # Ensure ground contact stays non-sinking (lift upward <= 0 in canvas y)
            dy_k = -abs(raw_dy)
            area_k = (s0["area"] * (1.0 - frac) + s1["area"] * frac) / max(0.02, mean_area)
            squash_k = _clamp(1.0 + (area_k - 1.0) * 0.22 - abs(dy_k) * 1.35, 0.90, 1.10)
            tilt_k = _clamp((vx_k / max_vx) * lean_coupling, -0.22, 0.22)
            trajectory_samples.append(
                [round(dx_k, 5), round(dy_k, 5), round(squash_k, 4), round(tilt_k, 4)]
            )

        dna_id = f"dna::{int(time.time() * 1000) % 1000000}"
        short_src = source_name[:18]
        dna_entry = {
            "id": dna_id,
            "name": custom_name or f"{short_src} ({dominant_freq_hz:.1f}Hz)",
            "source_name": source_name,
            "stream_kind": stream_kind,
            "origin": "live_video_extraction",
            "gait_regime": gait_regime,
            "gait_label_ko": gait_label_ko,
            "dominant_freq_hz": dominant_freq_hz,
            "stride_amp_x": stride_amp_x,
            "stride_amp_y": stride_amp_y,
            "lean_coupling": lean_coupling,
            "bounce_coupling": bounce_coupling,
            "sample_frames_used": n,
            "trajectory_samples": trajectory_samples,
            "extracted_at": _now_iso(),
        }

        self.motion_dna_library.append(dna_entry)
        self.motion_dna_library = self.motion_dna_library[-24:]
        self.total_frames_observed += n
        self.updated_at = _now_iso()
        self._save_ledger()

        snap = self.get_snapshot()
        snap["extracted_motion_dna"] = dna_entry
        return snap

    def transplant_living_actor(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transplants a harvested Motion DNA from Source A onto a real entity inside
        Target World B, turning passive media into a live interactive actor!
        """
        motion_dna_id = str(params.get("motion_dna_id") or "").strip()
        entity_id = str(params.get("entity_id") or "entity::cat").strip()
        target_world = str(params.get("target_world_name") or "타겟 환경 B").strip()[:80]

        dna = next((d for d in self.motion_dna_library if d.get("id") == motion_dna_id), None)
        if dna is None and self.motion_dna_library:
            dna = self.motion_dna_library[-1]
        ent = next((e for e in self.harvested_entities if e.get("id") == entity_id), None)
        if ent is None and self.harvested_entities:
            ent = self.harvested_entities[0]

        record = {
            "id": f"transplant::{int(time.time() * 1000) % 1000000}",
            "source_dna_id": dna["id"] if dna else "dna::predator_prowl",
            "source_dna_name": dna["name"] if dna else "보행 리듬",
            "source_origin": dna["source_name"] if dna else "영상 A",
            "entity_id": ent["id"] if ent else entity_id,
            "entity_name": ent["name"] if ent else entity_id,
            "target_world_name": target_world,
            "gait_label_ko": dna["gait_label_ko"] if dna else "자율 보행",
            "dominant_freq_hz": float(dna.get("dominant_freq_hz", 1.2)) if dna else 1.2,
            "initial_behavior": "curious_patrol",
            "summary": (
                f"[{dna['source_name'] if dna else '영상 A'}]의 {dna['gait_label_ko'] if dna else '동작 리듬'}"
                f"({float(dna.get('dominant_freq_hz', 1.2)) if dna else 1.2:.1f}Hz)을 "
                f"[{target_world}] 속 [{ent['name'] if ent else entity_id}] 개체에 살아있는 행동 로터로 이식"
            ),
            "at": _now_iso(),
        }

        self.cross_world_transplants.append(record)
        self.cross_world_transplants = self.cross_world_transplants[-32:]
        self.updated_at = _now_iso()
        self._save_ledger()

        snap = self.get_snapshot()
        snap["transplant_result"] = record
        snap["motion_dna"] = dna
        snap["entity_meta"] = ent
        return snap

    def intervene_living_actor(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Real-time human intervention into the living world (click lure or Korean
        speech command): dissolves passive video vs. interactive NPC boundary!
        """
        cmd = str(params.get("command_text") or "").strip()
        click_intervention = bool(params.get("click_intervention"))
        tx = _clamp(float(params.get("target_x", 0.5)), 0.10, 0.90)
        ty = _clamp(float(params.get("target_y", 0.76)), 0.52, 0.88)
        target_world = str(params.get("target_world_name") or "현재 환경").strip()[:60]

        behavior = "curious_patrol"
        speed_mult = 1.0
        behavior_label_ko = "자율 탐색"
        reaction_ko = f"[{target_world}] 환경의 빛과 흐름을 읽으며 자율 보행을 이어갑니다."

        if click_intervention and not cmd:
            behavior = "approach_user"
            speed_mult = 1.38
            behavior_label_ko = "개입 지점 탐색·접근"
            reaction_ko = f"사용자가 짚은 공간 좌표({tx:.2f}, {ty:.2f})를 인지하고 이식된 보행 리듬으로 방향을 틀어 다가갑니다."
        elif any(k in cmd for k in ("피해", "도망", "놀라", "물러나", "저리")):
            behavior = "evade_retreat"
            speed_mult = 1.65
            behavior_label_ko = "경계 회피 이동"
            reaction_ko = "갑작스러운 개입 자극을 감지해 무게중심을 낮추고 반대편 안전 지대로 빠르게 물러납니다."
        elif any(k in cmd for k in ("쉬어", "멈춰", "앉아", "가만히", "휴식", "기다려")):
            behavior = "calm_rest"
            speed_mult = 0.25
            behavior_label_ko = "호흡 정지·휴식"
            reaction_ko = "이동 추력을 멈추고 현재 지면 위에 자리를 잡아 미세 호흡 리듬만 유지합니다."
        elif any(k in cmd for k in ("호랑이", "어슬렁", "사냥", "순찰", "포식", "느리게")):
            behavior = "predator_prowl"
            speed_mult = 0.88
            behavior_label_ko = "저중심 포식자 순찰"
            reaction_ko = "보폭 주기를 낮추고 무게중심을 지면 가까이 실어 주변을 경계하며 어슬렁거립니다."
        elif any(k in cmd for k in ("뛰어", "달려", "점프", "신나", "빨리", "쫓아")):
            behavior = "playful_chase"
            speed_mult = 1.75
            behavior_label_ko = "탄성 가속 질주"
            reaction_ko = "지면 반작용 탄성을 키워 빠른 보폭으로 목표 지점을 향해 뛰어갑니다."
        elif any(k in cmd for k in ("이리", "이쪽", "와봐", "다가", "불러", "같이", "따라")):
            behavior = "approach_user"
            speed_mult = 1.32
            behavior_label_ko = "사용자 호출 응답"
            reaction_ko = "사용자 호출 방향을 향해 시선과 몸체 방향을 전환하고 자연스럽게 다가옵니다."

        return {
            "status": "ok",
            "intervention": {
                "behavior": behavior,
                "behavior_label_ko": behavior_label_ko,
                "speed_mult": speed_mult,
                "target_x": round(tx, 3),
                "target_y": round(ty, 3),
                "reaction_ko": reaction_ko,
                "at": _now_iso(),
            },
            "memory_summary": self.get_snapshot()["memory_summary"],
        }

    # -------------------------------------------------------------------------
    # 6 & 7. Unified S4(Realm/Authority/Faction) -> S2(Archetypes) -> S0(Tactile) Field
    # -------------------------------------------------------------------------

    ARCHETYPE_SENSITIVITIES: Dict[str, Dict[str, Any]] = {
        "spirit_beast": {
            "label_ko": "영수·신수",
            "auth_sens": 0.92,
            "rep_sens": 0.95,
            "tens_sens": 0.55,
            "fac_sens": 0.45,
            "allure_sens": 0.42,
            "charisma_sens": 0.78,
            "order_pref": 0.35,
            "good_pref": 0.85,
            "bond_weight": 0.72,
            "pride": 0.78,
        },
        "companion_pet": {
            "label_ko": "반려동물",
            "auth_sens": 0.14,
            "rep_sens": 0.25,
            "tens_sens": 0.70,
            "fac_sens": 0.15,
            "allure_sens": 0.35,
            "charisma_sens": 0.42,
            "order_pref": 0.00,
            "good_pref": 0.72,
            "bond_weight": 1.15,
            "pride": 0.10,
        },
        "citizen_npc": {
            "label_ko": "마을 NPC",
            "auth_sens": 0.88,
            "rep_sens": 0.92,
            "tens_sens": 0.80,
            "fac_sens": 0.90,
            "allure_sens": 0.96,
            "charisma_sens": 0.90,
            "order_pref": 0.65,
            "good_pref": 0.60,
            "bond_weight": 0.78,
            "pride": 0.35,
        },
        "wild_monster": {
            "label_ko": "야생 몬스터",
            "auth_sens": 0.76,
            "rep_sens": 0.32,
            "tens_sens": 0.96,
            "fac_sens": 0.35,
            "allure_sens": 0.14,
            "charisma_sens": 0.48,
            "order_pref": -0.55,
            "good_pref": -0.15,
            "bond_weight": 0.48,
            "pride": 0.65,
        },
    }

    REALM_PRESETS: Dict[str, Dict[str, Any]] = {
        "peaceful_sanctuary": {
            "realm_label_ko": "평온한 안식처 · 무명 여행자",
            "authority": 0.25,
            "reputation": 0.20,
            "regional_tension": 0.14,
            "faction_resonance": 0.20,
        },
        "revered_sovereign": {
            "realm_label_ko": "경외받는 왕국 수호자 · 군주",
            "authority": 0.92,
            "reputation": 0.88,
            "regional_tension": 0.16,
            "faction_resonance": 0.85,
        },
        "feared_intruder": {
            "realm_label_ko": "적대 세력 · 악명 높은 침입자",
            "authority": 0.68,
            "reputation": -0.84,
            "regional_tension": 0.86,
            "faction_resonance": -0.82,
        },
        "warzone_frontier": {
            "realm_label_ko": "전장 경계선 · 극고긴장 영역",
            "authority": 0.54,
            "reputation": 0.10,
            "regional_tension": 0.94,
            "faction_resonance": -0.15,
        },
    }

    PRESENCE_ROTOR_PRESETS: Dict[str, Dict[str, Any]] = {
        "balanced": {
            "label_ko": "균형 매력·카리스마",
            "gender_presentation": "androgynous",
            "allure_gravity": 0.48,
            "charisma_rotor": 0.45,
        },
        "radiant_allure_f": {
            "label_ko": "치명적 미모·매혹 인력 (여성)",
            "gender_presentation": "feminine",
            "allure_gravity": 0.95,
            "charisma_rotor": 0.82,
        },
        "sovereign_charisma": {
            "label_ko": "압도적 제왕 카리스마",
            "gender_presentation": "masculine",
            "allure_gravity": 0.62,
            "charisma_rotor": 0.96,
        },
        "austere_loner": {
            "label_ko": "차가운 고독 · 무매력",
            "gender_presentation": "androgynous",
            "allure_gravity": 0.14,
            "charisma_rotor": 0.22,
        },
    }

    ALIGNMENT_PRESETS: Dict[str, Dict[str, Any]] = {
        "lawful_good": {"order": 0.85, "good": 0.85, "label_ko": "질서 선"},
        "neutral_good": {"order": 0.15, "good": 0.80, "label_ko": "중립 선"},
        "chaotic_good": {"order": -0.82, "good": 0.85, "label_ko": "혼돈 선"},
        "true_neutral": {"order": 0.00, "good": 0.00, "label_ko": "완전 중립"},
        "lawful_evil": {"order": 0.85, "good": -0.82, "label_ko": "질서 악"},
        "chaotic_evil": {"order": -0.85, "good": -0.88, "label_ko": "혼돈 악"},
    }

    @staticmethod
    def _alignment_label_ko(order_val: float, good_val: float) -> str:
        o_tag = "질서" if order_val >= 0.32 else ("혼돈" if order_val <= -0.32 else "중립")
        g_tag = "선" if good_val >= 0.32 else ("악" if good_val <= -0.32 else "중립")
        if o_tag == "중립" and g_tag == "중립":
            return "완전 중립"
        return f"{o_tag} {g_tag}"

    def compute_social_field_coupling(
        self,
        archetype: str,
        personal_trust: float = 0.32,
        personal_warmth: float = 0.28,
    ) -> Dict[str, Any]:
        """
        Single continuous S4->S3->S2->S0 field coupling equation:
        Stats are NOT inert numbers — Authority, Reputation, Allure Gravity,
        Charisma Rotor, and 2D DnD Alignment (Order/Chaos x Good/Evil) act as
        coupled physical potential fields bending gaze, courtesy restraint,
        stance, and touch receptivity across every archetype!
        """
        arch_key = archetype if archetype in self.ARCHETYPE_SENSITIVITIES else "companion_pet"
        s = self.ARCHETYPE_SENSITIVITIES[arch_key]
        wf = self.world_social_field
        auth = float(wf.get("authority", 0.25))
        rep = float(wf.get("reputation", 0.20))
        tens = float(wf.get("regional_tension", 0.14))
        fac = float(wf.get("faction_resonance", 0.20))
        spirit_aff = float(wf.get("spirit_affinity", 0.40))
        mana_aff = float(wf.get("mana_affinity", 0.35))
        beast_mas = float(wf.get("beast_mastery", 0.42))
        gender_pres = str(wf.get("gender_presentation", "androgynous"))
        allure = float(wf.get("allure_gravity", 0.48))
        charisma = float(wf.get("charisma_rotor", 0.45))
        order_val = float(wf.get("alignment_order", 0.20))
        good_val = float(wf.get("alignment_good", 0.35))

        # Character-lineage resonance term (same unified continuous field, zero species spaghetti!)
        if arch_key == "spirit_beast":
            lineage_bonus = spirit_aff * 0.48 + mana_aff * 0.24
        elif arch_key == "wild_monster":
            lineage_bonus = beast_mas * 0.52 + mana_aff * 0.14
        elif arch_key == "companion_pet":
            lineage_bonus = beast_mas * 0.36 + spirit_aff * 0.16
        else:
            lineage_bonus = mana_aff * 0.14 + charisma * 0.24 + max(0.0, rep) * 0.16

        # 2D Continuous DnD Value/Alignment Resonance Rotor (Order/Chaos x Good/Evil)
        alignment_resonance = _clamp(
            order_val * s["order_pref"] * 0.55 + good_val * s["good_pref"] * 0.65,
            -1.0,
            1.0,
        )
        alignment_dissonance = max(0.0, -alignment_resonance)

        # Allure & Charisma as Causal Gravity Wells (bends gaze & imposes chivalric courtesy even under hostility!)
        gender_gaze_boost = 1.18 if (gender_pres == "feminine" and arch_key == "citizen_npc") else 1.0
        captivation_pull = _clamp(
            (allure * s["allure_sens"] * gender_gaze_boost * 0.66 + charisma * s["charisma_sens"] * 0.40)
            * (1.0 - max(0.0, tens - 0.82) * 0.35),
            0.0,
            1.25,
        )
        courtesy_restraint = _clamp(
            captivation_pull * 0.56
            + charisma * s["charisma_sens"] * 0.44
            + max(0.0, order_val) * 0.14,
            0.0,
            1.25,
        )

        # Three primary emergent potentials coupled with Stat Rotors + Alignment
        deferential_awe = _clamp(
            auth * s["auth_sens"] * 0.50
            + charisma * s["charisma_sens"] * 0.22
            + max(0.0, rep) * s["rep_sens"] * 0.36
            + max(0.0, fac) * s["fac_sens"] * 0.18
            + max(0.0, alignment_resonance) * 0.26
            + (lineage_bonus * 0.42 if arch_key == "spirit_beast" else 0.0)
            - max(0.0, -rep) * 0.35
            - alignment_dissonance * 0.24,
            0.0,
            1.25,
        )
        threat_alarm = _clamp(
            tens * s["tens_sens"] * 0.64
            + max(0.0, -rep) * s["rep_sens"] * 0.60
            + max(0.0, -fac) * s["fac_sens"] * 0.42
            + alignment_dissonance * 0.34
            + s["pride"] * max(0.0, 0.35 - auth) * 0.24
            - personal_trust * s["bond_weight"] * 0.44
            - lineage_bonus * 0.34
            - max(0.0, alignment_resonance) * 0.14,
            0.0,
            1.35,
        )
        warm_affinity = _clamp(
            personal_warmth * s["bond_weight"] * 0.62
            + lineage_bonus * 0.48
            + captivation_pull * 0.28
            + max(0.0, alignment_resonance) * 0.24
            + max(0.0, rep) * 0.22
            + max(0.0, fac) * 0.14
            - tens * 0.28
            - alignment_dissonance * 0.26,
            0.0,
            1.25,
        )

        # Emergent behavioral stance derived continuously from the coupled potentials
        if threat_alarm >= 0.62:
            if arch_key == "citizen_npc" and courtesy_restraint >= 0.72:
                stance = "courteous_rivalry"
                stance_ko = "적대 속 매너·시선 이끌림"
                base_lean = 0.04
                speed_mult = 0.78
                prefer_dist = 0.24
            elif threat_alarm >= 0.68 and auth >= 0.72 and arch_key == "wild_monster":
                stance = "cower_retreat"
                stance_ko = "위압 굴복·후퇴"
                base_lean = -0.14
                speed_mult = 1.45
                prefer_dist = 0.36
            else:
                stance = "hostile_guard"
                stance_ko = "적대 경계·위협"
                base_lean = -0.11
                speed_mult = 1.32
                prefer_dist = 0.30
        elif captivation_pull >= 0.76 and arch_key == "citizen_npc":
            stance = "captivated_gaze"
            stance_ko = "매혹 인력·시선 고정"
            base_lean = 0.11
            speed_mult = 0.68
            prefer_dist = 0.16
        elif deferential_awe >= 0.68:
            stance = "reverent_bow"
            stance_ko = "경외·깊은 예우"
            base_lean = 0.15
            speed_mult = 0.72
            prefer_dist = 0.22
        elif warm_affinity >= 0.55:
            stance = "devoted_companion"
            stance_ko = "친화 동반·밀착"
            base_lean = 0.08
            speed_mult = 1.08
            prefer_dist = 0.11
        elif tens >= 0.70 and arch_key == "companion_pet":
            stance = "protective_huddle"
            stance_ko = "불안·곁으로 밀착"
            base_lean = 0.06
            speed_mult = 1.25
            prefer_dist = 0.09
        else:
            stance = "curious_observe"
            stance_ko = "자율 탐색·관찰"
            base_lean = 0.02
            speed_mult = 1.0
            prefer_dist = 0.20

        effective_receptivity = _clamp(
            personal_trust * s["bond_weight"] * 0.60
            + warm_affinity * 0.32
            + deferential_awe * 0.26
            + captivation_pull * 0.24
            - threat_alarm * 0.56
            - s["pride"] * 0.14,
            0.0,
            1.0,
        )

        return {
            "archetype": arch_key,
            "archetype_label_ko": s["label_ko"],
            "deferential_awe": round(deferential_awe, 3),
            "threat_alarm": round(threat_alarm, 3),
            "warm_affinity": round(warm_affinity, 3),
            "captivation_pull": round(captivation_pull, 3),
            "courtesy_restraint": round(courtesy_restraint, 3),
            "alignment_resonance": round(alignment_resonance, 3),
            "gaze_lock": bool(captivation_pull >= 0.62),
            "effective_receptivity": round(effective_receptivity, 3),
            "stance": stance,
            "stance_ko": stance_ko,
            "base_lean_rad": round(base_lean, 3),
            "speed_mult": round(speed_mult, 2),
            "prefer_dist": round(prefer_dist, 2),
        }

    def set_world_social_field(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates the S4-S3 Macro World Social Field (authority, reputation,
        regional_tension, faction_resonance) AND/OR Stat Scale-Rotors
        (Allure Gravity, Charisma Rotor, 2D DnD Alignment), immediately returning
        recomputed multi-archetype field couplings!
        """
        preset_id = str(params.get("preset_id") or "").strip()
        if preset_id in self.REALM_PRESETS:
            pr = self.REALM_PRESETS[preset_id]
            self.world_social_field.update(
                {
                    "preset_id": preset_id,
                    "realm_label_ko": pr["realm_label_ko"],
                    "authority": pr["authority"],
                    "reputation": pr["reputation"],
                    "regional_tension": pr["regional_tension"],
                    "faction_resonance": pr["faction_resonance"],
                }
            )
        else:
            realm_touched = False
            if "authority" in params:
                self.world_social_field["authority"] = round(_clamp(float(params["authority"]), 0.0, 1.0), 2)
                realm_touched = True
            if "reputation" in params:
                self.world_social_field["reputation"] = round(_clamp(float(params["reputation"]), -1.0, 1.0), 2)
                realm_touched = True
            if "regional_tension" in params:
                self.world_social_field["regional_tension"] = round(_clamp(float(params["regional_tension"]), 0.0, 1.0), 2)
                realm_touched = True
            if "faction_resonance" in params:
                self.world_social_field["faction_resonance"] = round(_clamp(float(params["faction_resonance"]), -1.0, 1.0), 2)
                realm_touched = True
            if realm_touched:
                self.world_social_field["preset_id"] = "custom"
                a = self.world_social_field["authority"]
                r = self.world_social_field["reputation"]
                t = self.world_social_field["regional_tension"]
                if r <= -0.45:
                    self.world_social_field["realm_label_ko"] = f"적대·악명 장력 (권위 {int(a*100)}% · 긴장 {int(t*100)}%)"
                elif a >= 0.72 and r >= 0.45:
                    self.world_social_field["realm_label_ko"] = f"경외받는 권위 장력 (권위 {int(a*100)}% · 명성 +{int(r*100)}%)"
                elif t >= 0.72:
                    self.world_social_field["realm_label_ko"] = f"고긴장 전장 장력 (긴장 {int(t*100)}%)"
                else:
                    self.world_social_field["realm_label_ko"] = f"사용자 조율 세계장 (권위 {int(a*100)}% · 명성 {int(r*100):+}%)"

        # Stat Scale-Rotor updates (Allure Gravity, Charisma, Gender Presentation)
        pres_id = str(params.get("presence_preset_id") or "").strip()
        if pres_id in self.PRESENCE_ROTOR_PRESETS:
            pp = self.PRESENCE_ROTOR_PRESETS[pres_id]
            self.world_social_field.update(
                {
                    "presence_preset_id": pres_id,
                    "gender_presentation": pp["gender_presentation"],
                    "allure_gravity": pp["allure_gravity"],
                    "charisma_rotor": pp["charisma_rotor"],
                }
            )
        else:
            if "gender_presentation" in params:
                gp = str(params["gender_presentation"]).strip().lower()
                if gp in ("feminine", "masculine", "androgynous"):
                    self.world_social_field["gender_presentation"] = gp
            if "allure_gravity" in params:
                self.world_social_field["allure_gravity"] = round(_clamp(float(params["allure_gravity"]), 0.0, 1.0), 2)
                self.world_social_field["presence_preset_id"] = "custom"
            if "charisma_rotor" in params:
                self.world_social_field["charisma_rotor"] = round(_clamp(float(params["charisma_rotor"]), 0.0, 1.0), 2)
                self.world_social_field["presence_preset_id"] = "custom"

        # 2D Continuous DnD Alignment / Value Axis updates
        align_id = str(params.get("alignment_preset_id") or "").strip()
        if align_id in self.ALIGNMENT_PRESETS:
            ap = self.ALIGNMENT_PRESETS[align_id]
            self.world_social_field.update(
                {
                    "alignment_preset_id": align_id,
                    "alignment_order": ap["order"],
                    "alignment_good": ap["good"],
                    "alignment_label_ko": ap["label_ko"],
                }
            )
        else:
            align_touched = False
            if "alignment_order" in params:
                self.world_social_field["alignment_order"] = round(_clamp(float(params["alignment_order"]), -1.0, 1.0), 2)
                align_touched = True
            if "alignment_good" in params:
                self.world_social_field["alignment_good"] = round(_clamp(float(params["alignment_good"]), -1.0, 1.0), 2)
                align_touched = True
            if align_touched:
                self.world_social_field["alignment_preset_id"] = "custom"
                self.world_social_field["alignment_label_ko"] = self._alignment_label_ko(
                    float(self.world_social_field["alignment_order"]),
                    float(self.world_social_field["alignment_good"]),
                )

        self.updated_at = _now_iso()
        self._save_ledger()
        snap = self.get_snapshot()
        snap["archetype_couplings"] = {
            k: self.compute_social_field_coupling(k)
            for k in self.ARCHETYPE_SENSITIVITIES
        }
        return snap

    def roll_character_profile(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rolls a complete living character scale-rotor profile:
        Race, Trait, Gender Presentation, Allure Gravity, Charisma Rotor,
        2D DnD Alignment (Order/Chaos x Good/Evil), and Spirit/Mana/Beast Affinities!
        """
        import random as _rnd

        # (name, spirit, mana, beast, auth, rep, allure, charisma, order, good)
        races = [
            ("달빛 하이엘프 여제", 0.90, 0.86, 0.54, 0.68, 0.62, 0.94, 0.86, 0.45, 0.72),
            ("고대 용혈 계승자", 0.72, 0.90, 0.62, 0.92, 0.35, 0.72, 0.90, 0.20, 0.15),
            ("야수 교감 수인족", 0.68, 0.45, 0.94, 0.38, 0.40, 0.66, 0.56, -0.58, 0.52),
            ("왕국 성기사단", 0.52, 0.60, 0.45, 0.84, 0.82, 0.64, 0.84, 0.88, 0.85),
            ("별빛 마나 방랑자", 0.78, 0.95, 0.50, 0.42, 0.28, 0.82, 0.74, -0.45, 0.60),
            ("경계선 암흑 추적자", 0.25, 0.70, 0.76, 0.66, -0.58, 0.78, 0.64, -0.62, -0.54),
        ]
        # (name, d_spirit, d_mana, d_beast, d_auth, d_rep, d_allure, d_charisma, d_order, d_good)
        traits = [
            ("천상의 매혹 오라", 0.08, 0.08, 0.02, 0.06, 0.10, 0.18, 0.14, 0.04, 0.08),
            ("정령의 축복", 0.16, 0.10, 0.04, 0.05, 0.12, 0.06, 0.06, 0.10, 0.16),
            ("고요한 야성 공명", 0.06, 0.02, 0.18, 0.04, 0.04, 0.02, 0.05, -0.18, 0.06),
            ("제왕의 카리스마", 0.05, 0.08, 0.02, 0.20, 0.10, 0.08, 0.20, 0.22, 0.04),
            ("금단의 치명적 매력", -0.08, 0.14, 0.08, 0.10, -0.22, 0.20, 0.12, -0.20, -0.24),
        ]
        seed_idx = params.get("seed")
        rng = _rnd.Random(seed_idx) if seed_idx is not None else _rnd.Random()
        race = rng.choice(races)
        trait = rng.choice(traits)
        gender_pres = "feminine" if "여제" in race[0] else rng.choice(["feminine", "masculine", "androgynous"])

        spirit_aff = round(_clamp(race[1] + trait[1] + rng.uniform(-0.06, 0.06), 0.05, 1.0), 2)
        mana_aff = round(_clamp(race[2] + trait[2] + rng.uniform(-0.06, 0.06), 0.05, 1.0), 2)
        beast_mas = round(_clamp(race[3] + trait[3] + rng.uniform(-0.06, 0.06), 0.05, 1.0), 2)
        authority = round(_clamp(race[4] + trait[4] + rng.uniform(-0.06, 0.06), 0.10, 1.0), 2)
        reputation = round(_clamp(race[5] + trait[5] + rng.uniform(-0.08, 0.08), -0.95, 0.95), 2)
        allure_grav = round(_clamp(race[6] + trait[6] + (0.06 if gender_pres == "feminine" else 0.0) + rng.uniform(-0.06, 0.06), 0.10, 1.0), 2)
        charisma_rot = round(_clamp(race[7] + trait[7] + rng.uniform(-0.06, 0.06), 0.10, 1.0), 2)
        align_order = round(_clamp(race[8] + trait[8] + rng.uniform(-0.14, 0.14), -1.0, 1.0), 2)
        align_good = round(_clamp(race[9] + trait[9] + rng.uniform(-0.14, 0.14), -1.0, 1.0), 2)
        align_ko = self._alignment_label_ko(align_order, align_good)
        tension = round(_clamp(0.22 + max(0.0, -reputation) * 0.65, 0.10, 0.90), 2)

        self.world_social_field.update(
            {
                "preset_id": "character_roll",
                "presence_preset_id": "custom",
                "alignment_preset_id": "custom",
                "race_label_ko": race[0],
                "trait_label_ko": trait[0],
                "gender_presentation": gender_pres,
                "allure_gravity": allure_grav,
                "charisma_rotor": charisma_rot,
                "alignment_order": align_order,
                "alignment_good": align_good,
                "alignment_label_ko": align_ko,
                "spirit_affinity": spirit_aff,
                "mana_affinity": mana_aff,
                "beast_mastery": beast_mas,
                "authority": authority,
                "reputation": reputation,
                "regional_tension": tension,
                "faction_resonance": round(_clamp(reputation * 0.85, -0.9, 0.9), 2),
                "realm_label_ko": (
                    f"{race[0]}[{trait[0]}] · {align_ko} · "
                    f"매력{int(allure_grav*100)}/카리스마{int(charisma_rot*100)} · "
                    f"정령{int(spirit_aff*100)}/마나{int(mana_aff*100)}"
                ),
            }
        )
        self.updated_at = _now_iso()
        self._save_ledger()
        snap = self.get_snapshot()
        snap["rolled_character"] = dict(self.world_social_field)
        return snap

    def _bond_stage_ko(self, trust: float, warmth: float) -> str:
        score = trust * 0.55 + warmth * 0.45
        if score >= 0.78:
            return "깊은 유대"
        if score >= 0.56:
            return "편안한 동반"
        if score >= 0.36:
            return "조심스러운 호감"
        return "낯선 탐색"

    def tactile_interaction(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes continuous organic tactile interaction coupled directly with the
        S4-S3 World Social Field (authority, reputation, tension, faction) and
        the entity's ecological archetype (spirit_beast / companion_pet / citizen_npc / wild_monster)!
        """
        entity_id = str(params.get("entity_id") or "entity::cat").strip()[:80]
        entity_name = str(params.get("entity_name") or entity_id).strip()[:40]
        archetype = str(params.get("archetype") or "").strip().lower()
        if archetype not in self.ARCHETYPE_SENSITIVITIES:
            if "embrace" in entity_id:
                archetype = "citizen_npc"
            elif "puppy" in entity_id:
                archetype = "companion_pet"
            else:
                archetype = "companion_pet"
        zone = str(params.get("zone") or "torso").strip().lower()
        gesture = str(params.get("gesture") or "stroke").strip().lower()
        duration_sec = _clamp(float(params.get("duration_sec", 0.5)), 0.05, 15.0)
        stroke_cycles = max(0, int(params.get("stroke_cycles", 1)))
        speed_norm = _clamp(float(params.get("speed_norm", 0.4)), 0.0, 3.0)

        zone_map = {
            "head": "머리",
            "shoulder": "어깨",
            "hand_paw": "손·발",
            "torso": "등·몸통",
        }
        gesture_map = {
            "stroke": "부드럽게 쓰다듬기",
            "hold": "지그시 잡기·감싸기",
            "poke": "툭 건드리기",
            "guide": "부드럽게 이끌기",
        }
        zone_ko = zone_map.get(zone, "몸통")
        gesture_ko = gesture_map.get(gesture, "닿기")

        rel = dict(
            self.entity_relations.get(entity_id)
            or {
                "entity_id": entity_id,
                "entity_name": entity_name,
                "archetype": archetype,
                "trust": 0.32,
                "warmth": 0.28,
                "arousal": 0.26,
                "comfort": 0.52,
                "touch_count": 0,
                "last_zone": zone,
                "last_gesture": gesture,
            }
        )
        trust = float(rel.get("trust", 0.32))
        warmth = float(rel.get("warmth", 0.28))
        arousal = float(rel.get("arousal", 0.26))
        comfort = float(rel.get("comfort", 0.52))

        # S4->S3->S2->S0 Unified Coupling: macro world field + Stat Scale-Rotors bend micro touch response!
        coupling = self.compute_social_field_coupling(archetype, trust, warmth)
        arch_ko = coupling["archetype_label_ko"]
        threat_alarm = coupling["threat_alarm"]
        deferential_awe = coupling["deferential_awe"]
        captivation_pull = coupling["captivation_pull"]
        courtesy_restraint = coupling["courtesy_restraint"]

        posture = "gentle_lean"
        lean_angle_rad = 0.08
        breath_rate_mult = 0.85
        warmth_glow = 0.45
        reaction_ko = f"[{entity_name}]의 {zone_ko}에 닿은 손길에 부드럽게 반응합니다."

        if entity_id == "entity::pine_tree":
            posture = "wind_rustle"
            lean_angle_rad = 0.06 if gesture != "poke" else 0.11
            breath_rate_mult = 1.15
            warmth_glow = 0.25
            reaction_ko = f"[{entity_name}] 줄기와 잎사귀가 손길의 결을 따라 잔잔하게 흔들리며 반응합니다."
            trust = _clamp(trust + 0.03, 0.0, 1.0)
            warmth = _clamp(warmth + 0.03, 0.0, 1.0)
        elif threat_alarm >= 0.64 and archetype == "citizen_npc" and courtesy_restraint >= 0.72 and gesture in ("stroke", "poke", "hold"):
            # Hostile S4 faction/reputation, YET Allure Gravity + Charisma Rotor enforces chivalric manners & gaze pull!
            posture = "courteous_restraint"
            lean_angle_rad = 0.04
            breath_rate_mult = 1.12
            warmth_glow = 0.58
            trust = _clamp(trust + 0.02, 0.0, 1.0)
            arousal = _clamp(arousal + 0.14, 0.15, 1.0)
            reaction_ko = (
                f"적대적 입장이지만 {arch_ko}[{entity_name}]가 압도적 매력과 카리스마 인력에 시선을 떼지 못한 채, "
                f"끝까지 매너를 지키며 정중하게 {zone_ko}의 거리를 조율합니다."
            )
        elif threat_alarm >= 0.64 and archetype in ("spirit_beast", "wild_monster", "citizen_npc") and gesture in ("stroke", "poke", "hold"):
            # Macro hostile reputation / extreme tension overrides casual touch!
            posture = "social_reject_recoil" if archetype != "wild_monster" else "hostile_bristle"
            lean_angle_rad = -0.17
            breath_rate_mult = 1.55
            warmth_glow = 0.12
            arousal = _clamp(arousal + 0.24, 0.15, 1.0)
            comfort = _clamp(comfort - 0.10, 0.05, 1.0)
            if archetype == "spirit_beast":
                reaction_ko = f"적대적 명성과 높은 긴장 장력을 꿰뚫어 본 {arch_ko}[{entity_name}]가 위엄 있게 물러서며 {zone_ko} 손길을 거부합니다."
            elif archetype == "wild_monster":
                reaction_ko = f"긴장된 영역에서 닿은 손길에 {arch_ko}[{entity_name}]가 털을 세우고 낮게 으르렁대며 반 발짝 물러납니다."
            else:
                reaction_ko = f"적대 세력의 압박을 의식한 {arch_ko}[{entity_name}]가 어깨를 굳히고 조심스럽게 거리를 둡니다."
        elif captivation_pull >= 0.76 and archetype == "citizen_npc" and gesture in ("stroke", "hold", "poke"):
            # High Allure Gravity + Charisma captivates NPC gaze and melts distance!
            posture = "captivated_blush"
            lean_angle_rad = 0.13
            breath_rate_mult = 1.16
            warmth_glow = 0.94
            trust = _clamp(trust + 0.08, 0.0, 1.0)
            warmth = _clamp(warmth + 0.11, 0.0, 1.0)
            arousal = _clamp(arousal + 0.12, 0.12, 1.0)
            reaction_ko = (
                f"매력 인력 로터에 눈길을 빼앗긴 {arch_ko}[{entity_name}]가 {zone_ko}에 닿은 손길에 "
                f"얼굴을 붉히며 자연스럽게 시선과 호흡을 맞춥니다."
            )
        elif deferential_awe >= 0.68 and archetype in ("spirit_beast", "citizen_npc") and gesture in ("stroke", "hold"):
            # Macro sovereign authority + high reputation bends posture into reverent yielding!
            posture = "reverent_yield"
            lean_angle_rad = 0.16
            breath_rate_mult = 0.68
            warmth_glow = 0.90
            trust = _clamp(trust + 0.09, 0.0, 1.0)
            warmth = _clamp(warmth + 0.09, 0.0, 1.0)
            arousal = _clamp(arousal - 0.10, 0.08, 1.0)
            if archetype == "spirit_beast":
                reaction_ko = f"높은 권위와 맑은 명성의 장력을 알아본 {arch_ko}[{entity_name}]가 고개를 깊이 숙여 {zone_ko}의 손길을 경외로 받아들입니다."
            else:
                reaction_ko = f"경외받는 존재의 따뜻한 {zone_ko} 손길에 {arch_ko}[{entity_name}]가 정중히 고개를 숙이며 깊은 신뢰를 보입니다."
        elif gesture == "stroke":
            gentleness = 1.0 - _clamp(speed_norm * 0.22, 0.0, 0.45)
            d_trust = (0.065 + 0.015 * min(4, stroke_cycles)) * gentleness
            d_warmth = (0.085 + 0.018 * min(4, stroke_cycles)) * gentleness
            if zone == "head":
                posture = "lean_into_stroke"
                lean_angle_rad = 0.11
                breath_rate_mult = 0.72
                warmth_glow = 0.82
                if trust < 0.42:
                    reaction_ko = f"[{entity_name}]가 처음엔 살짝 귀를 기울이다가, 천천히 쓰다듬는 리듬에 맞춰 조심스레 머리를 맡깁니다."
                else:
                    reaction_ko = f"[{entity_name}]가 머리를 쓰다듬는 손길 속도에 맞춰 고개를 기분 좋게 기대고 호흡을 깊게 늦춥니다."
            elif zone == "shoulder":
                posture = "soft_turn_in"
                lean_angle_rad = 0.09
                breath_rate_mult = 0.78
                warmth_glow = 0.72
                reaction_ko = f"[{entity_name}]가 어깨를 매만지는 따뜻한 손길에 긴장을 풀고 부드럽게 시선을 맞춥니다."
            else:
                posture = "gentle_lean"
                lean_angle_rad = 0.07
                breath_rate_mult = 0.80
                warmth_glow = 0.65
                reaction_ko = f"[{entity_name}]가 {zone_ko}을 따라 흐르는 손길에 편안하게 몸을 맡깁니다."
            trust = _clamp(trust + d_trust, 0.0, 1.0)
            warmth = _clamp(warmth + d_warmth, 0.0, 1.0)
            arousal = _clamp(arousal - 0.08, 0.08, 1.0)
            comfort = _clamp(comfort + 0.09, 0.0, 1.0)
        elif gesture == "hold":
            hold_bonus = _clamp(duration_sec / 2.2, 0.35, 1.25)
            if zone == "hand_paw":
                posture = "hand_hold_sync"
                lean_angle_rad = 0.06
                breath_rate_mult = 0.68
                warmth_glow = 0.92
                if trust < 0.38:
                    reaction_ko = f"[{entity_name}]가 조심스레 맞잡힌 손의 온기를 살피며 천천히 경계를 내려놓습니다."
                else:
                    reaction_ko = f"[{entity_name}]가 맞잡은 손의 온기에 화답하며 같은 박자로 고요하게 호흡을 맞춥니다."
            elif zone == "shoulder":
                posture = "shoulder_embrace"
                lean_angle_rad = 0.10
                breath_rate_mult = 0.70
                warmth_glow = 0.88
                reaction_ko = f"[{entity_name}]가 어깨를 지그시 감싸는 안정감에 몸을 살짝 기대며 깊은 안도감을 보입니다."
            else:
                posture = "warm_stillness"
                lean_angle_rad = 0.07
                breath_rate_mult = 0.74
                warmth_glow = 0.80
                reaction_ko = f"[{entity_name}]가 머무르는 따뜻한 손길을 느끼며 그 자리에서 고요히 마음을 엽니다."
            trust = _clamp(trust + 0.09 * hold_bonus, 0.0, 1.0)
            warmth = _clamp(warmth + 0.11 * hold_bonus, 0.0, 1.0)
            arousal = _clamp(arousal - 0.10, 0.08, 1.0)
            comfort = _clamp(comfort + 0.11 * hold_bonus, 0.0, 1.0)
        elif gesture == "poke":
            if trust < 0.48:
                posture = "startle_recoil"
                lean_angle_rad = -0.15
                breath_rate_mult = 1.48
                warmth_glow = 0.22
                trust = _clamp(trust - 0.03, 0.05, 1.0)
                arousal = _clamp(arousal + 0.22, 0.10, 1.0)
                comfort = _clamp(comfort - 0.07, 0.10, 1.0)
                reaction_ko = f"아직 낯선 사이에서 {zone_ko}을 툭 건드리자 [{entity_name}]가 깜짝 놀라 반 발짝 물러나며 경계합니다."
            else:
                posture = "playful_nudge_back"
                lean_angle_rad = 0.13
                breath_rate_mult = 1.28
                warmth_glow = 0.74
                trust = _clamp(trust + 0.035, 0.0, 1.0)
                warmth = _clamp(warmth + 0.05, 0.0, 1.0)
                arousal = _clamp(arousal + 0.14, 0.10, 1.0)
                reaction_ko = f"이미 친해진 [{entity_name}]가 {zone_ko}을 툭 건드리는 장난을 알아채고 반갑게 고개를 돌려 호응합니다."
        else:
            posture = "guided_step"
            lean_angle_rad = 0.08
            breath_rate_mult = 1.05
            warmth_glow = 0.62
            trust = _clamp(trust + 0.04, 0.0, 1.0)
            warmth = _clamp(warmth + 0.04, 0.0, 1.0)
            reaction_ko = f"[{entity_name}]가 {zone_ko}을 부드럽게 이끄는 방향을 따라 자연스럽게 발걸음을 옮깁니다."

        rel.update(
            {
                "entity_id": entity_id,
                "entity_name": entity_name,
                "archetype": archetype,
                "archetype_label_ko": arch_ko,
                "trust": round(trust, 3),
                "warmth": round(warmth, 3),
                "arousal": round(arousal, 3),
                "comfort": round(comfort, 3),
                "bond_stage_ko": self._bond_stage_ko(trust, warmth),
                "touch_count": int(rel.get("touch_count", 0)) + 1,
                "last_zone": zone,
                "last_zone_ko": zone_ko,
                "last_gesture": gesture,
                "last_gesture_ko": gesture_ko,
                "updated_at": _now_iso(),
            }
        )
        self.entity_relations[entity_id] = rel
        self.updated_at = _now_iso()
        self._save_ledger()

        snap = self.get_snapshot()
        snap["tactile_result"] = {
            "entity_id": entity_id,
            "entity_name": entity_name,
            "archetype": archetype,
            "archetype_label_ko": arch_ko,
            "zone": zone,
            "zone_ko": zone_ko,
            "gesture": gesture,
            "gesture_ko": gesture_ko,
            "posture": posture,
            "lean_angle_rad": round(lean_angle_rad, 3),
            "breath_rate_mult": round(breath_rate_mult, 2),
            "warmth_glow": round(warmth_glow, 2),
            "reaction_ko": reaction_ko,
            "social_coupling": coupling,
            "relation": rel,
        }
        return snap

    def compute_scale_joy_meaning_spectrum(self) -> Dict[str, Any]:
        """
        Multi-Scale Joy, Attention & Meaning Spectrum (점 -> 선 -> 면 -> 가정·조직 -> 나라·시대·세상):
        Derives sensory pleasure, fun/curiosity flow, relational stability, and
        macro meaning/enlightenment directly from the SAME continuous coupled field:
          Attention (선택과 집중) x Cross-Scale Resonance = Value & Meaning!
        """
        wf = self.world_social_field
        rels = list(self.entity_relations.values())
        avg_trust = sum(float(r.get("trust", 0.32)) for r in rels) / max(1, len(rels)) if rels else 0.32
        avg_warmth = sum(float(r.get("warmth", 0.28)) for r in rels) / max(1, len(rels)) if rels else 0.28
        avg_comfort = sum(float(r.get("comfort", 0.52)) for r in rels) / max(1, len(rels)) if rels else 0.52
        total_touches = sum(int(r.get("touch_count", 0)) for r in rels)

        couplings = {k: self.compute_social_field_coupling(k, avg_trust, avg_warmth) for k in self.ARCHETYPE_SENSITIVITIES}
        npc_c = couplings["citizen_npc"]
        sb_c = couplings["spirit_beast"]

        avg_err_drop = 0.0
        if self.learned_laws:
            avg_err_drop = sum(float(x.get("error_reduction_pct", 0.0)) for x in self.learned_laws) / (100.0 * len(self.learned_laws))

        tens = float(wf.get("regional_tension", 0.14))
        rep = float(wf.get("reputation", 0.20))
        fac = float(wf.get("faction_resonance", 0.20))
        good_val = float(wf.get("alignment_good", 0.35))
        allure = float(wf.get("allure_gravity", 0.48))
        charisma = float(wf.get("charisma_rotor", 0.45))

        # S0 Point Joy (점의 기쁨): tactile sensation, warmth, immediate sensory delight
        s0_point = _clamp(avg_warmth * 0.50 + avg_comfort * 0.35 + min(0.25, total_touches * 0.04), 0.0, 1.0)
        # S1 Line Joy (선의 기쁨): curiosity, rhythmic flow, fun of resolving unknown into motion DNA
        s1_line = _clamp(0.25 + avg_err_drop * 0.45 + min(0.22, len(self.motion_dna_library) * 0.06) + min(0.18, len(self.cross_world_transplants) * 0.06), 0.0, 1.0)
        # S2 Plane Joy (면의 기쁨): spatial harmony, magnetic allure, shared stability & abundance
        s2_plane = _clamp(
            npc_c["captivation_pull"] * 0.32
            + avg_trust * 0.34
            + (1.0 - tens) * 0.26
            + min(0.16, len(self.intentional_creations) * 0.04),
            0.0,
            1.0,
        )
        # S3 Relational/Household Joy (가정·조직의 기쁨): mutual trust, courtesy restraint, belonging
        s3_household = _clamp(
            avg_trust * 0.38
            + npc_c["courtesy_restraint"] * 0.26
            + max(0.0, fac) * 0.22
            + min(0.20, len(rels) * 0.07)
            - max(0.0, -fac) * 0.16,
            0.0,
            1.0,
        )
        # S4 Realm/Era Joy (나라·시대·세상의 기쁨): meaning, enlightenment, cross-scale value resonance
        s4_world = _clamp(
            max(0.0, rep) * 0.24
            + max(0.0, good_val) * 0.22
            + max(0.0, sb_c["alignment_resonance"]) * 0.20
            + (1.0 - tens) * 0.18
            + charisma * 0.14
            + min(0.22, (len(self.learned_laws) + int(self.distilled_optical_priors.get("corpus_count", 0) > 0)) * 0.06)
            - max(0.0, -rep) * 0.18,
            0.0,
            1.0,
        )

        # True Attention (선택과 집중) = Contrast between focused scale & surrounding scales + curiosity
        scales = [
            ("S0 점(감각·촉감)", s0_point),
            ("S1 선(흐름·재미)", s1_line),
            ("S2 면(공명·풍요)", s2_plane),
            ("S3 관계(가정·조직)", s3_household),
            ("S4 세상(시대·깨달음)", s4_world),
        ]
        dominant_label, dominant_val = max(scales, key=lambda kv: kv[1])
        mean_joy = sum(v for _, v in scales) / 5.0
        # Cross-scale coherence: enlightenment peaks when lower & higher scales harmonize without dissonance
        variance = sum((v - mean_joy) ** 2 for _, v in scales) / 5.0
        enlightenment_coherence = _clamp(mean_joy * (1.0 - math.sqrt(variance) * 0.45) + (allure * 0.04), 0.0, 1.0)

        return {
            "s0_point_joy": round(s0_point, 3),
            "s1_line_fun": round(s1_line, 3),
            "s2_plane_abundance": round(s2_plane, 3),
            "s3_household_trust": round(s3_household, 3),
            "s4_world_meaning": round(s4_world, 3),
            "dominant_attention_scale": dominant_label,
            "dominant_attention_score": round(dominant_val, 3),
            "enlightenment_coherence": round(enlightenment_coherence, 3),
            "summary_ko": (
                f"점{int(s0_point*100)}·선{int(s1_line*100)}·면{int(s2_plane*100)}·"
                f"관계{int(s3_household*100)}·세상{int(s4_world*100)} "
                f"(주의 초점: {dominant_label} · 깨달음 공명 {int(enlightenment_coherence*100)}%)"
            ),
        }

    def research_frontier_goal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Outward Epistemic Expansion & Grounding-as-Foothold Research Loop (AGENTS.md Sec 5 & 6):
        When Elysia attempts to invent or realize something beyond her current knowledge
        (e.g., an SF Starship, Aircraft, or Automobile), she NEVER hallucinates fake magic.
        Instead, she audits her ACTUALLY learned real-world causal laws as a foothold,
        explicitly maps the Reality Gap / Unknown Boundary vs. target physics, and
        formulates concrete real-world resources & experiments to ingest next!
        """
        goal_text = str(params.get("goal_text") or "SF 우주함선").strip()[:100]
        gl = goal_text.lower()

        learned_types = {str(x.get("law_type") or "") for x in self.learned_laws}
        has_fluid = "fluid_specular_drift" in learned_types
        has_gravity = "gravity_acceleration" in learned_types
        has_flow = ("coherent_camera_or_scene_flow" in learned_types) or ("autonomous_entity_motion" in learned_types)
        has_corpus = int(self.distilled_optical_priors.get("corpus_count", 0)) > 0
        has_dna = len(self.motion_dna_library) > 0
        has_social = bool(self.world_social_field)

        if any(k in gl for k in ("우주", "함선", "로켓", "sf", "starship", "space")):
            domain_id = "starship"
            domain_ko = "SF 우주함선"
            pillars = [
                {
                    "id": "inertial_flow",
                    "name_ko": "관성·연속 궤도 위상 흐름",
                    "status": "grounded" if (has_flow or has_dna) else "bridgeable",
                    "foothold": "실시간 스트림 예측·동작 DNA에서 확보한 속도·가속 연속 로터",
                    "reality_gap": "행성 중력권 탈출 궤도(케플러 2체·다체 역학)는 장기 궤적 실측 보강 필요",
                },
                {
                    "id": "vacuum_propulsion",
                    "name_ko": "진공 추진 (매질 부재 격차)",
                    "status": "unknown_boundary",
                    "foothold": (
                        "바다·유체에서 학습한 파동·유체 흐름 법칙(fluid_specular_drift)이 대조 발판으로 존재"
                        if has_fluid else "아직 유체·추진 실측 법칙 자체가 미확보"
                    ),
                    "reality_gap": "바다·공기와 달리 우주 진공에는 밀어낼 유체 매질이 없음 → 로켓·이온 분사(운동량 보존 반작용) 실세계 데이터 투입 필수",
                },
                {
                    "id": "radiative_thermal_hull",
                    "name_ko": "진공 복사 방열 · 기밀 압력선체",
                    "status": "unknown_boundary",
                    "foothold": "실세계 코퍼스 조광·복사 에너지 비율 학습" if has_corpus else "광학 복사 기준 미학습",
                    "reality_gap": "공기 대류가 없는 진공에서는 열을 식힐 매질이 없어 적외선 방열판·기압차 구조 강도 원리가 현재 미지 경계",
                },
                {
                    "id": "gravity_navigation",
                    "name_ko": "중력·가속장 평형 제어",
                    "status": "grounded" if has_gravity else "bridgeable",
                    "foothold": "낙하 수직 가속 법칙(gravity_acceleration) 확보" if has_gravity else "지면 기준 중력 감각만 보유",
                    "reality_gap": "무중력·원심 인공중력 전환 시 유체와 인체 균형이 완전히 달라짐",
                },
                {
                    "id": "crew_habitat_field",
                    "name_ko": "승무원 생태·권위·신뢰 거주장",
                    "status": "grounded" if has_social else "bridgeable",
                    "foothold": "통합 S4(지위·성향·긴장)↔S0(촉감·안정·기쁨) 관계 인과장 이미 확보",
                    "reality_gap": "장기 폐쇄 환경 스트레스에 따른 긴장도 누적 곡선 검증 가능",
                },
            ]
            next_experiments = [
                "로켓 연소·진공 플룸 분사 실사 영상 투입 → 매질 없는 운동량 보존 추진 법칙 추출",
                "열화상 복사 냉각·우주정거장 무중력 물방울 영상 투입 → 표면장력·복사 방열 로터 확장",
                "기존 항공기·잠수함 기밀 동체 설계 지식을 현실 발판으로 삼아 우주 압력선체 차이 대조",
            ]
        elif any(k in gl for k in ("비행기", "항공", "날개", "드론", "aircraft", "plane")):
            domain_id = "aircraft"
            domain_ko = "비행기 · 항공 역학"
            pillars = [
                {
                    "id": "fluid_lift",
                    "name_ko": "유체 흐름 → 날개 양력 전이",
                    "status": "grounded" if has_fluid else "bridgeable",
                    "foothold": "실측 유체 흐름 법칙(fluid_specular_drift)을 공기 유동장 발판으로 확장" if has_fluid else "기본 시점 흐름만 보유",
                    "reality_gap": "압력차(베르누이)와 받음각 실속(Stall) 임계점은 실제 풍동·비행 영상으로 정밀 교정 필요",
                },
                {
                    "id": "gravity_counter",
                    "name_ko": "중력 낙하 대항 평형",
                    "status": "grounded" if has_gravity else "unknown_boundary",
                    "foothold": "중력 수직 가속 법칙 확보" if has_gravity else "중력 낙하 실측 영상 미투입",
                    "reality_gap": "양력 < 중력 순간의 실속·활강 복원 궤적 학습 필요",
                },
                {
                    "id": "thrust_drag_envelope",
                    "name_ko": "추력·항력 비대칭 & 난류 경계",
                    "status": "unknown_boundary",
                    "foothold": "동작 DNA 주기 리듬을 프로펠러·날갯짓 주파수 유추에 활용 가능" if has_dna else "주기 추진 기준 미확보",
                    "reality_gap": "고속 공기 압축성과 항력 급증(음속 장벽)은 현재 미지 영역",
                },
                {
                    "id": "optical_horizon_nav",
                    "name_ko": "대기 산란·수평선 자세 인지",
                    "status": "grounded" if has_corpus else "bridgeable",
                    "foothold": "실세계 코퍼스 하늘/수평선/지면 3대역 조도·안개 계수 학습 완료" if has_corpus else "대기 코퍼스 미학습",
                    "reality_gap": "악천후·야간 계기비행 시 시각 외 관성센서 융합 필요",
                },
            ]
            next_experiments = [
                "새의 활강·풍동 연기 흐름 실사 영상 투입 → 받음각-양력-와류 분리 법칙 추출",
                "물체 자유낙하·글라이더 착륙 영상 투입 → 중력 대항 양력 균형 계수 실측",
            ]
        elif any(k in gl for k in ("자동차", "차량", "바퀴", "엔진", "car", "auto")):
            domain_id = "automobile"
            domain_ko = "자동차 · 지면 동역학"
            pillars = [
                {
                    "id": "ground_traction",
                    "name_ko": "지면 접촉·마찰 견인 & S3 좌표 고정",
                    "status": "grounded" if (has_flow or has_dna) else "bridgeable",
                    "foothold": "S3 월드 지면 좌표 고정 및 동작 DNA 지면 반작용 발판 확보",
                    "reality_gap": "노면(빗길·빙판·아스팔트)별 타이어 슬립률·마찰계수 차이 실측 필요",
                },
                {
                    "id": "powertrain_torque",
                    "name_ko": "동력 토크 전달 & 현가장치 감쇠",
                    "status": "unknown_boundary",
                    "foothold": "주기 보행 로터에서 회전·탄성 리듬 유추 가능" if has_dna else "회전 동력계 미학습",
                    "reality_gap": "내연/모터 토크 곡선, 기어비, 서스펜션 스프링-댐퍼 진동 억제는 미지 경계",
                },
                {
                    "id": "driver_optics",
                    "name_ko": "도로 조광·반사 시야 적응",
                    "status": "grounded" if has_corpus else "bridgeable",
                    "foothold": "실세계 코퍼스 경면 윤슬·조도비 학습을 빗길 헤드라이트 난반사 인지에 활용" if has_corpus else "실세계 코퍼스 학습 필요",
                    "reality_gap": "고속 주행 시 원근 광류 왜곡 및 제동거리 연동 필요",
                },
            ]
            next_experiments = [
                "도로 주행 블랙박스·타이어 슬립 실사 영상 투입 → 지면 마찰·제동 감속 로터 학습",
                "서스펜션 요철 통과 영상 투입 → 탄성 감쇠 계수 및 승차감 안정도 보정",
            ]
        elif any(k in gl for k in ("마나", "에테르", "마법", "연금", "워프", "반중력", "초광속", "mana", "aether", "magic", "warp")):
            domain_id = "axiom_world_seed"
            domain_ko = f"가정 공리 법칙화 씨앗 [{goal_text}]"
            pillars = [
                {
                    "id": "explicit_axiom",
                    "name_ko": "가정 공리 선언 (마나·에테르 매질 존재 가정)",
                    "status": "bridgeable",
                    "foothold": "현실 물리에는 없는 미지 매질임을 명확히 구분한 뒤, 연속 스칼라·벡터 장으로 공리화",
                    "reality_gap": "현실 세계에는 관측되지 않는 가정 공리 — 실세계 물리와의 경계를 항상 명시 유지",
                },
                {
                    "id": "fluid_wave_analogy",
                    "name_ko": "유체·파동 보존 법칙 전이 (현실 발판 → 마나 유동)",
                    "status": "grounded" if (has_fluid or has_flow) else "bridgeable",
                    "foothold": "실세계 유체·파동 법칙(fluid_specular_drift)을 마나 흐름·에테르 밀도 구배 법칙으로 투영",
                    "reality_gap": "마나 소모 시 대가(열·피로·엔트로피) 보존 규칙을 정해야 붕괴하지 않는 세계 법칙 완성",
                },
                {
                    "id": "affinity_resonance",
                    "name_ko": "생명·정령·마나 친화 공명 결합",
                    "status": "grounded" if has_social else "bridgeable",
                    "foothold": (
                        f"현재 캐릭터 마나친화도({int(float(self.world_social_field.get('mana_affinity', 0.35))*100)})·"
                        f"정령친화력({int(float(self.world_social_field.get('spirit_affinity', 0.40))*100)}) 로터를 직접 결합"
                    ),
                    "reality_gap": "공명 과부하(마나 폭주·역류) 임계 조건을 실험적으로 튜닝할 필요 있음",
                },
                {
                    "id": "observable_manifestation",
                    "name_ko": "광학·음향·촉각 발현 규칙 (S4→S0 일관성)",
                    "status": "unknown_boundary" if not has_corpus else "bridgeable",
                    "foothold": "실세계 광학 코퍼스의 조광·윤슬 산란 법칙을 마법 발광·왜곡 표현의 발판으로 활용",
                    "reality_gap": "가정된 마나 에너지가 현실 빛·열·운동량으로 변환되는 변환 효율 방정식 정립 필요",
                },
            ]
            next_experiments = [
                "현실 유체·오로라·플라즈마 방전 실사 영상을 투입해 '에테르/마나 흐름'의 시각·운동 불변식 추출",
                "마나 보존(입력=출력+엔트로피) 공리를 고정한 뒤 캐릭터 친화도와 환경 반응을 교차 검증",
            ]
        else:
            domain_id = "frontier_invention"
            domain_ko = f"미지 창조 과제 [{goal_text}]"
            pillars = [
                {
                    "id": "observed_dynamics",
                    "name_ko": "실세계 운동·흐름 발판",
                    "status": "grounded" if (has_fluid or has_flow or has_gravity) else "bridgeable",
                    "foothold": f"현재 원장에 축적된 실세계 동적 법칙 {len(self.learned_laws)}종 및 동작 DNA {len(self.motion_dna_library)}종",
                    "reality_gap": f"[{goal_text}] 고유의 물리 제약·에너지 보존 조건과 현재 자원 간 차이 비교 필요",
                },
                {
                    "id": "environmental_medium",
                    "name_ko": "환경 매질·에너지 격차 (Unknown Boundary)",
                    "status": "unknown_boundary",
                    "foothold": "실세계 광학 코퍼스" if has_corpus else "초기 관찰 상태",
                    "reality_gap": f"[{goal_text}]가 작동할 실제 매질·재료 강도·열/에너지 수지는 아직 미지 경계로, 실세계 영상·물리 데이터 투입이 필요함",
                },
                {
                    "id": "human_relational_fit",
                    "name_ko": "인간·생태계 공명 및 가치 적합성",
                    "status": "grounded" if has_social else "bridgeable",
                    "foothold": "S4(가치관·권위)↔S0(촉감·안전·기쁨) 통합 인과장 활용 가능",
                    "reality_gap": "실제 사용자 개입 피드백으로 기준을 지속 자가 보정해야 함",
                },
            ]
            next_experiments = [
                f"[{goal_text}]와 가장 가까운 현실 선행 기술·자연 현상 영상을 투입해 S3 흐름·S2 구조 법칙 먼저 추출",
                "현재 확보된 발판 원리와 목표 환경 간의 가장 큰 물리적 차이(매질·에너지·재료)부터 단계적 실험",
            ]

        grounded_cnt = sum(1 for p in pillars if p["status"] == "grounded")
        bridge_cnt = sum(1 for p in pillars if p["status"] == "bridgeable")
        unknown_cnt = sum(1 for p in pillars if p["status"] == "unknown_boundary")
        readiness_pct = round(((grounded_cnt + 0.45 * bridge_cnt) / max(1, len(pillars))) * 100.0, 1)

        grounded_names = [p["name_ko"] for p in pillars if p["status"] == "grounded"]
        unknown_names = [p["name_ko"] for p in pillars if p["status"] == "unknown_boundary"]

        record = {
            "id": f"research::{int(time.time() * 1000) % 1000000}",
            "goal_text": goal_text,
            "domain_id": domain_id,
            "domain_ko": domain_ko,
            "readiness_pct": readiness_pct,
            "grounded_count": grounded_cnt,
            "bridgeable_count": bridge_cnt,
            "unknown_count": unknown_cnt,
            "pillars": pillars,
            "grounded_footholds": grounded_names,
            "reality_gaps": [p["reality_gap"] for p in pillars if p["status"] != "grounded"],
            "next_experiments": next_experiments,
            "summary_ko": (
                f"[{domain_ko} 자가 원리 연구 · 준비도 {readiness_pct:.0f}%] "
                f"보유 발판({', '.join(grounded_names) if grounded_names else '기초 관찰'}) / "
                f"미지·현실 격차({', '.join(unknown_names) if unknown_names else '세부 교정'}) → "
                f"다음 실험: {next_experiments[0]}"
            ),
            "at": _now_iso(),
        }

        self.epistemic_research_bridges.append(record)
        self.epistemic_research_bridges = self.epistemic_research_bridges[-24:]
        self.updated_at = _now_iso()
        self._save_ledger()

        snap = self.get_snapshot()
        snap["research_bridge"] = record
        return snap

    # -------------------------------------------------------------------------
    # Public Action Router & Snapshot
    # -------------------------------------------------------------------------

    def apply_action(self, action: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        p = dict(params or {})
        act = (action or "state").strip()
        if act == "recall_prior":
            return self.recall_prior_law(p)
        if act == "record_stream_learning":
            return self.record_stream_learning(p)
        if act == "harvest_entity":
            return self.harvest_moving_entity(p)
        if act == "apply_intent":
            return self.plan_intentional_recomposition(p)
        if act == "ingest_real_corpus_batch":
            return self.ingest_real_corpus_batch(p)
        if act == "extract_motion_dna":
            return self.extract_motion_dna(p)
        if act == "transplant_living_actor":
            return self.transplant_living_actor(p)
        if act == "intervene_living_actor":
            return self.intervene_living_actor(p)
        if act == "tactile_interaction":
            return self.tactile_interaction(p)
        if act == "set_world_social_field":
            return self.set_world_social_field(p)
        if act == "roll_character_profile":
            return self.roll_character_profile(p)
        if act == "research_frontier_goal":
            return self.research_frontier_goal(p)
        return self.get_snapshot()

    def get_snapshot(self) -> Dict[str, Any]:
        avg_reduction = 0.0
        if self.learned_laws:
            avg_reduction = round(
                sum(float(x.get("error_reduction_pct", 0.0)) for x in self.learned_laws)
                / float(len(self.learned_laws)),
                1,
            )
        return {
            "status": "ok",
            "ledger_path": str(self.ledger_path.name),
            "memory_summary": {
                "learned_law_count": len(self.learned_laws),
                "harvested_entity_count": len(self.harvested_entities),
                "intentional_creation_count": len(self.intentional_creations),
                "real_corpus_count": len(self.real_corpus_profiles),
                "total_corpus_pixels": int(self.distilled_optical_priors.get("total_pixels_studied", 0)),
                "motion_dna_count": len(self.motion_dna_library),
                "transplant_count": len(self.cross_world_transplants),
                "bonded_entity_count": len(self.entity_relations),
                "research_bridge_count": len(self.epistemic_research_bridges),
                "total_frames_observed": self.total_frames_observed,
                "total_self_corrections": self.total_self_corrections,
                "mean_error_reduction_pct": avg_reduction,
            },
            "world_social_field": dict(self.world_social_field),
            "archetype_couplings": {
                k: self.compute_social_field_coupling(k)
                for k in self.ARCHETYPE_SENSITIVITIES
            },
            "scale_joy_meaning": self.compute_scale_joy_meaning_spectrum(),
            "distilled_optical_priors": self.distilled_optical_priors,
            "learned_laws": list(self.learned_laws[-8:][::-1]),
            "harvested_entities": list(self.harvested_entities),
            "intentional_creations": list(self.intentional_creations[-8:][::-1]),
            "motion_dna_library": list(self.motion_dna_library),
            "cross_world_transplants": list(self.cross_world_transplants[-8:][::-1]),
            "entity_relations": dict(self.entity_relations),
            "epistemic_research_bridges": list(self.epistemic_research_bridges[-8:][::-1]),
            "updated_at": self.updated_at,
        }
