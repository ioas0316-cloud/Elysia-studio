r"""
ELYSIA Unified Existing-Organ Wiring Bridge
===========================================

NO flat keyword shortcuts, NO disconnected toy scripts.
Directly wires Elysia's OWN existing production cognitive/linguistic/sensory
organs together into ONE continuous circulation connected to real external
media, 3D renders, audio prosody, and the living recursive Story World:

  1. `core.topology.unified_scale_rotor_hierarchy.ScaleRotorHierarchy`
     (Scale 0 Hangul Jamo / Visual Cells / Audio Impulses -> Scale 1 Syllables
      -> Scale 2 Word Stems & Operators -> Scale 3 Modal Configurations
      -> Scale 4 Lived Multimodal Episodes + Clifford Cl(3,0) Docking M_a*M_b~)
  2. `core.topology.hangul_topological_engine.HangulTopologicalEngine`
     (Articulatory Hangul jamo spin-matrix & vowel phase encoding)
  3. `core.orchestration.language_acquisition_engine.RealLanguageAcquisitionEngine`
     (Korean 받침 syntax walker + PPMI/SVD causal axes + semantic bridges)
  4. `core.embodiment.language_scale_rotor.LanguageScaleRotor`
     (Non-templated clause schema induction & novel utterance composition)
  5. `core.consciousness.conceptual_unit_system_engine.ConceptualUnitSystemEngine`
     (Existential intent extraction & unknown-concept sensory profile mapping)
  6. `story_scale_rotor_world_engine` + `multiverse_and_grounded_language_prism`
     (Live CoW parallel-universe counterfactual execution off Reference Rotor M_0)
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional

import cv2  # type: ignore
import numpy as np

THIS_DIR = Path(__file__).resolve().parent
L1_ROOT = THIS_DIR.parents[1]
WORKSPACE_ROOT = THIS_DIR.parents[2]
for _p in (str(THIS_DIR), str(L1_ROOT), str(WORKSPACE_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# --- ELYSIA'S OWN EXISTING CORE ORGANS ---
from core.consciousness.conceptual_unit_system_engine import ConceptualUnitSystemEngine  # noqa: E402
from core.embodiment.grown_organs.organ_voice_and_hearing import (  # noqa: E402
    synthesize_korean_wav_winrt,
    transcribe_wav_whisper,
)
from core.embodiment.language_scale_rotor import LanguageScaleRotor  # noqa: E402
from core.embodiment.world_expression_ingestor import (  # noqa: E402
    fetch_public_literature_from_web,
    ingest_youtube_multimodal_episode,
)
from core.memory.causal_concept_memory import (  # noqa: E402
    CausalConceptMemory,
    CausalObservation,
)
from core.memory.enactive_relational_memory import (  # noqa: E402
    EnactiveRelationalMemoryEngine,
    RelationalEdge,
    RelationalMesh,
    RelationalNode,
)
from core.orchestration.connected_media_causal_observer import (  # noqa: E402
    ConnectedMediaCausalObserver,
    TimeAlignedUtterance,
    encode_audio_to_scale_rotor,
    observe_audio_stream,
)
from core.orchestration.elysia_unified_living_cycle import (  # noqa: E402
    ElysiaUnifiedLivingCycle,
    LivingEncounter,
)
from core.orchestration.extended_cognitive_organism import ExtendedWorldState  # noqa: E402
from core.orchestration.language_acquisition_engine import RealLanguageAcquisitionEngine  # noqa: E402
from core.orchestration.multidimensional_lens_rotor import (  # noqa: E402
    CrossAxisPerspectiveRotorLens,
    CrossAxisPerspectiveSpec,
    MultiDimensionalLensRotorHub,
)
from core.orchestration.relational_perspective_rotor import (  # noqa: E402
    AgentCausalProfile,
    RelationalPerspectiveObserver,
)
from core.topology.hangul_topological_engine import HangulTopologicalEngine  # noqa: E402
from core.topology.korean_causal_linguistics import parse_korean_causal_frame  # noqa: E402
from core.topology.unified_scale_rotor_hierarchy import ScaleRotorHierarchy  # noqa: E402

# --- LIVE EXTERNAL WORLD / MULTIVERSE / SENSORY DATA ---
from multiverse_and_grounded_language_prism import _clone_world_from_reference_rotor  # noqa: E402
from self_cognitive_expansion_cortex import COGNITIVE_WORLD_DIR, _load_json, _save_json  # noqa: E402
from story_scale_rotor_world_engine import (  # noqa: E402
    DEFAULT_STORY_TEXT,
    STORY_STATE_PATH,
    STORY_WORLD_DIR,
    create_and_run_story_world,
)


CONNECTED_HIERARCHY_PATH = COGNITIVE_WORLD_DIR / "elysia_connected_hierarchy.json"
KOREAN_CORPUS_CACHE_PATH = COGNITIVE_WORLD_DIR / "elysia_korean_world_corpus.json"
YOUTUBE_MULTIMODAL_DIR = WORKSPACE_ROOT / "data" / "open_sandbox" / "youtube_multimodal"
YOUTUBE_MEMORY_PATH = COGNITIVE_WORLD_DIR / "elysia_youtube_multimodal_memory.json"
ENACTIVE_MEMORY_PATH = COGNITIVE_WORLD_DIR / "elysia_enactive_relational_memory.json"
CAUSAL_CONCEPT_MEMORY_PATH = COGNITIVE_WORLD_DIR / "elysia_causal_concept_memory.json"
LIVING_CYCLE_PROVENANCE_PATH = COGNITIVE_WORLD_DIR / "elysia_living_cycle_provenance.json"
UNIT_CORTEX_REPORT_PATH = STORY_WORLD_DIR / "unit_branch_language_report.json"

_INTERDISCIPLINARY_KO_TOPICS = [
    "빛", "광학", "시각", "안개", "등대", "시야", "소리", "리듬", "파동", "시간", "각도",
    "엔트로피", "신경계", "기억", "언어", "감정", "생태계", "물리학", "중력", "세포",
    "뇌", "우주", "바람", "바다", "태양", "소설", "대화", "인간", "의식", "역사", "철학", "음악",
]


def _triad_to_spec4(tri: Any) -> List[float]:
    if isinstance(tri, dict):
        vals = [float(tri.get(k, 0.33)) for k in ("red", "blue", "yellow")]
        if sum(vals) <= 1e-6:
            vals = [float(v) for v in list(tri.values())[:3]]
        while len(vals) < 3:
            vals.append(0.33)
        return [round(vals[0], 4), round(vals[1], 4), round(vals[2], 4), 0.15]
    if isinstance(tri, (list, tuple, np.ndarray)) and len(tri) >= 3:
        return [round(float(tri[0]), 4), round(float(tri[1]), 4), round(float(tri[2]), 4), 0.15]
    return [0.34, 0.33, 0.33, 0.15]


def _extract_visual_48_from_png(png_path: Path) -> Optional[Dict[str, Any]]:
    if not png_path.is_file():
        return None
    img = cv2.imread(str(png_path), cv2.IMREAD_COLOR)
    if img is None:
        return None
    small = cv2.resize(img, (4, 4), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    vec48 = small.reshape(-1).tolist()  # 4*4*3 = 48 continuous chroma cells
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    contrast_std = float(np.std(gray))
    b_mean, g_mean, r_mean = [float(np.mean(img[:, :, c])) / 255.0 for c in range(3)]
    warm_cool = round((r_mean + 0.5 * g_mean) / max(0.05, b_mean + 0.5 * g_mean), 3)
    return {
        "vec48": [round(x, 4) for x in vec48],
        "contrast_std": round(contrast_std, 4),
        "warm_cool": warm_cool,
        "spectrum": [round(r_mean, 4), round(b_mean, 4), round(g_mean, 4), round(contrast_std, 4)],
    }


def _split_korean_sentences(text: str, max_count: int = 25) -> List[str]:
    import re
    raw = re.split(r"(?<=[.!?다요죠])\s+|\n+", text or "")
    out: List[str] = []
    for s in raw:
        clean = re.sub(r"[#>*`\[\]]+", "", s).strip(" -•\t")
        if 10 <= len(clean) <= 130 and any(0xAC00 <= ord(ch) <= 0xD7A3 for ch in clean):
            out.append(clean)
            if len(out) >= max_count:
                break
    return out


def harvest_real_korean_world_corpus(rlae: RealLanguageAcquisitionEngine, force_refresh: bool = False) -> Dict[str, Any]:
    """
    Append-merges Elysia's EXISTING `RealLanguageAcquisitionEngine.fetch_korean_world_knowledge`
    + `world_expression_ingestor.fetch_public_literature_from_web` + local Korean docs
    into a persistent real-world Korean corpus (never wiping previously fetched topics!).
    """
    cached = _load_json(KOREAN_CORPUS_CACHE_PATH, {}) if KOREAN_CORPUS_CACHE_PATH.is_file() else {}
    if not force_refresh and cached.get("entries"):
        return cached

    # Start from existing cached entries & fetched topics (append-merge!)
    entries: List[Dict[str, str]] = list(cached.get("entries") or [])
    wiki_topics_fetched: List[str] = list(cached.get("wiki_topics_fetched") or [])
    lit_rotors_count = int(cached.get("public_literature_rotors") or 0)

    # 1. Live Korean Wikipedia / Wiktionary ONLY for topics not yet cached, with polite backoff
    unfetched = [t for t in _INTERDISCIPLINARY_KO_TOPICS if t not in wiki_topics_fetched]
    for topic in unfetched:
        try:
            wk = rlae.fetch_korean_world_knowledge(topic, timeout=5.0)
            if wk:
                txt = str(wk.get("extract") or wk.get("text") or wk.get("summary") or "")
                sents = _split_korean_sentences(txt, max_count=12)
                if sents:
                    wiki_topics_fetched.append(topic)
                    for s in sents:
                        entries.append({"sentence": s, "source": f"ko.wikipedia:{topic}", "topic": topic})
            time.sleep(0.35)
        except Exception:
            continue

    # 2. Live Public-Domain Korean Literature via Elysia's existing world_expression_ingestor!
    try:
        rotors = fetch_public_literature_from_web(lang="ko", max_works=5)
        if rotors:
            lit_rotors_count = max(lit_rotors_count, len(rotors))
        for r in rotors[:120]:
            utt = str(getattr(r, "expression_text", None) or getattr(r, "utterance", "") or "").strip()
            sit = str(getattr(r, "situation", "") or "문학")
            if 8 <= len(utt) <= 130 and any(0xAC00 <= ord(ch) <= 0xD7A3 for ch in utt):
                entries.append({"sentence": utt, "source": f"public_literature:{getattr(r, 'source_title', 'ko')}", "topic": sit[:30]})
    except Exception:
        pass

    # 3. Local Korean architectural/philosophical docs (`AGENTS.md` + `docs/*.md`)
    for doc_p in [WORKSPACE_ROOT / "AGENTS.md", *sorted((WORKSPACE_ROOT / "docs").glob("*.md"))[:5]]:
        if not doc_p.is_file():
            continue
        sents = _split_korean_sentences(doc_p.read_text(encoding="utf-8", errors="ignore"), max_count=24)
        for s in sents:
            entries.append({"sentence": s, "source": f"local_doc:{doc_p.name}", "topic": doc_p.stem})

    # Deduplicate cleanly preserving insertion order
    seen: set[str] = set()
    dedup: List[Dict[str, str]] = []
    for e in entries:
        if e["sentence"] not in seen:
            seen.add(e["sentence"])
            dedup.append(e)

    corpus_doc = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "wiki_topics_fetched": wiki_topics_fetched,
        "public_literature_rotors": lit_rotors_count,
        "total_sentences": len(dedup),
        "entries": dedup,
    }
    _save_json(KOREAN_CORPUS_CACHE_PATH, corpus_doc)
    return corpus_doc


def _extract_video_frame_48_at(mp4_path: Path, t_sec: float) -> Optional[Dict[str, Any]]:
    if not mp4_path.is_file():
        return None
    cap = cv2.VideoCapture(str(mp4_path))
    if not cap.isOpened():
        return None
    try:
        cap.set(cv2.CAP_PROP_POS_MSEC, max(0.0, float(t_sec) * 1000.0))
        ok, img = cap.read()
        if not ok or img is None:
            return None
        small = cv2.resize(img, (4, 4), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
        vec48 = small.reshape(-1).tolist()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        contrast_std = float(np.std(gray))
        b_mean, g_mean, r_mean = [float(np.mean(img[:, :, c])) / 255.0 for c in range(3)]
        warm_cool = round((r_mean + 0.5 * g_mean) / max(0.05, b_mean + 0.5 * g_mean), 3)
        return {
            "vec48": [round(x, 4) for x in vec48],
            "contrast_std": round(contrast_std, 4),
            "warm_cool": warm_cool,
            "spectrum": [round(r_mean, 4), round(b_mean, 4), round(g_mean, 4), round(contrast_std, 4)],
        }
    finally:
        cap.release()


def ingest_youtube_into_elysia(url_or_query: str, max_duration_s: int = 75) -> Dict[str, Any]:
    """
    Ingests a real YouTube video (Video + Voice Audio + Time-Aligned Korean Subtitles),
    observes cross-modal causality via Elysia's EXISTING `ConnectedMediaCausalObserver`,
    and persists all synchronized audiovisual-linguistic episodes to disk for warm-start grounding!
    """
    raw_ep = ingest_youtube_multimodal_episode(
        url_or_query=url_or_query,
        out_dir=YOUTUBE_MULTIMODAL_DIR,
        max_duration_s=max_duration_s,
        max_rotors=50,
        lang="ko",
    )
    if raw_ep.get("status") == "error":
        return raw_ep

    mp4_p = Path(raw_ep["mp4_path"]) if raw_ep.get("mp4_path") else None
    wav_p = Path(raw_ep["wav_path"]) if raw_ep.get("wav_path") else None
    utts_raw = raw_ep.get("utterances") or []
    time_utts = [
        TimeAlignedUtterance(
            t_start=float(u["t_start"]),
            t_end=float(u["t_end"]),
            speaker=str(u.get("speaker", "speaker")),
            text=str(u.get("text", "")),
        )
        for u in utts_raw
        if u.get("text")
    ]

    # Observe full synchronized triad with Elysia's EXISTING `ConnectedMediaCausalObserver`!
    observer = ConnectedMediaCausalObserver()
    obs_rep = observer.observe_episode(
        episode_id=f"yt_{raw_ep['video_id']}",
        description=raw_ep.get("title", ""),
        video_source=mp4_p if (mp4_p and mp4_p.is_file()) else None,
        audio_source=wav_p if (wav_p and wav_p.is_file()) else None,
        utterances=time_utts or None,
        max_frames=48,
        absorb_to_sphere=True,
    )

    # Pair sampled subtitle cues with actual 48-D video chroma vectors at their exact timestamp
    enriched_cues: List[Dict[str, Any]] = []
    for idx, u in enumerate(utts_raw):
        frame48 = _extract_video_frame_48_at(mp4_p, float(u["t_start"])) if (mp4_p and mp4_p.is_file() and idx < 24) else None
        enriched_cues.append({
            **u,
            "frame_visual_48": frame48,
        })

    links_summary = [
        {
            "cause": lk.cause_channel,
            "effect": lk.effect_channel,
            "lag_s": round(float(lk.lag_s), 3),
            "strength": round(float(lk.strength), 4),
            "direction": lk.direction,
        }
        for lk in (obs_rep.causal_links or [])[:8]
    ]
    ep_record = {
        "video_id": raw_ep["video_id"],
        "title": raw_ep["title"],
        "webpage_url": raw_ep["webpage_url"],
        "clip_duration_s": raw_ep["clip_duration_s"],
        "mp4_path": raw_ep["mp4_path"],
        "wav_path": raw_ep["wav_path"],
        "subtitle_path": raw_ep["subtitle_path"],
        "cues_count": len(enriched_cues),
        "present_modalities": list(obs_rep.present_modalities),
        "agency_mode": obs_rep.agency_mode.value if hasattr(obs_rep.agency_mode, "value") else str(obs_rep.agency_mode),
        "causality_mode": obs_rep.causality_mode.value if hasattr(obs_rep.causality_mode, "value") else str(obs_rep.causality_mode),
        "beats_count": len(obs_rep.beats or []),
        "continuity_bridges_count": len(obs_rep.continuity_bridges or []),
        "cross_modal_causal_links": links_summary,
        "observer_summary_ko": obs_rep.summary_ko,
        "cues": enriched_cues,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }

    mem_doc = _load_json(YOUTUBE_MEMORY_PATH, {"episodes": {}})
    episodes = dict(mem_doc.get("episodes") or {})
    episodes[raw_ep["video_id"]] = ep_record
    out_mem = {
        "schema": "elysia_youtube_multimodal_memory_v1",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "episodes_count": len(episodes),
        "total_aligned_cues": sum(int(e.get("cues_count", 0)) for e in episodes.values()),
        "episodes": episodes,
    }
    _save_json(YOUTUBE_MEMORY_PATH, out_mem)
    return ep_record


def _load_persistent_enactive_memory() -> EnactiveRelationalMemoryEngine:
    """Warm-starts Elysia's `EnactiveRelationalMemoryEngine` from disk so relational meshes accumulate across sessions."""
    engine = EnactiveRelationalMemoryEngine()
    raw = _load_json(ENACTIVE_MEMORY_PATH, {})
    for eid, mraw in (raw.get("consolidated_substrates") or {}).items():
        mesh = RelationalMesh(
            entity_id=str(mraw.get("entity_id", eid)),
            entity_name=str(mraw.get("entity_name", eid)),
            coherence_score=float(mraw.get("coherence_score", 1.0)),
            last_calibrated_time=float(mraw.get("last_calibrated_time", time.time())),
        )
        for nid, nraw in (mraw.get("nodes") or {}).items():
            mesh.add_node(
                RelationalNode(
                    node_id=str(nraw.get("node_id", nid)),
                    modal_type=str(nraw.get("modal_type", "LANGUAGE")),
                    label=str(nraw.get("label", "")),
                    attributes=dict(nraw.get("attributes") or {}),
                    grounded_context=str(nraw.get("grounded_context", "")),
                )
            )
        for eraw in mraw.get("edges") or []:
            mesh.add_edge(
                RelationalEdge(
                    source_id=str(eraw.get("source_id", "")),
                    target_id=str(eraw.get("target_id", "")),
                    relation_type=str(eraw.get("relation_type", "INTERWEAVES_WITH")),
                    tension=float(eraw.get("tension", 0.5)),
                    weight=float(eraw.get("weight", 1.0)),
                    contextual_glue=str(eraw.get("contextual_glue", "")),
                )
            )
        engine.active_meshes[mesh.entity_id] = mesh
        engine.consolidated_substrates[mesh.entity_id] = mesh
    return engine


def _save_persistent_enactive_memory(engine: EnactiveRelationalMemoryEngine) -> Dict[str, Any]:
    substrates_out: Dict[str, Any] = {}
    for eid, mesh in engine.consolidated_substrates.items():
        substrates_out[eid] = {
            "entity_id": mesh.entity_id,
            "entity_name": mesh.entity_name,
            "coherence_score": round(float(mesh.coherence_score), 4),
            "last_calibrated_time": float(mesh.last_calibrated_time),
            "nodes": {
                nid: {
                    "node_id": nd.node_id,
                    "modal_type": nd.modal_type,
                    "label": nd.label,
                    "attributes": nd.attributes,
                    "grounded_context": nd.grounded_context,
                }
                for nid, nd in mesh.nodes.items()
            },
            "edges": [
                {
                    "source_id": e.source_id,
                    "target_id": e.target_id,
                    "relation_type": e.relation_type,
                    "tension": round(float(e.tension), 4),
                    "weight": round(float(e.weight), 4),
                    "contextual_glue": e.contextual_glue,
                }
                for e in mesh.edges
            ],
        }
    doc = {
        "schema": "elysia_enactive_relational_memory_v1",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "consolidated_entities_count": len(substrates_out),
        "total_relational_nodes": sum(len(m["nodes"]) for m in substrates_out.values()),
        "total_relational_edges": sum(len(m["edges"]) for m in substrates_out.values()),
        "consolidated_substrates": substrates_out,
    }
    _save_json(ENACTIVE_MEMORY_PATH, doc)
    return doc


def _load_persistent_causal_concept_memory() -> CausalConceptMemory:
    """Warm-starts Elysia's `CausalConceptMemory` by replaying persisted real-world observations through `CausalJudgmentGear`."""
    mem = CausalConceptMemory(vector_dim=8)
    raw = _load_json(CAUSAL_CONCEPT_MEMORY_PATH, {})
    for obs_raw in (raw.get("observations") or [])[-120:]:
        try:
            obs = CausalObservation(
                observation_id=str(obs_raw.get("observation_id", "obs")),
                concept_id=str(obs_raw.get("concept_id", "world")),
                features=dict(obs_raw.get("features") or {}),
                process_context=dict(obs_raw.get("process_context") or {}),
                evidence_strength=float(obs_raw.get("evidence_strength", 1.0)),
                is_real_world=bool(obs_raw.get("is_real_world", True)),
            )
            mem.learn_observation(
                obs,
                label=str(obs_raw.get("label", obs.concept_id)),
                invariants=list(obs_raw.get("invariants") or []),
            )
        except Exception:
            continue
    return mem


def _save_persistent_causal_concept_memory(
    mem: CausalConceptMemory,
    new_obs_records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    prev = _load_json(CAUSAL_CONCEPT_MEMORY_PATH, {})
    obs_log = list(prev.get("observations") or [])
    existing_ids = {str(o.get("observation_id")) for o in obs_log}
    for rec in new_obs_records:
        if rec.get("observation_id") not in existing_ids:
            obs_log.append(rec)
            existing_ids.add(str(rec.get("observation_id")))
    obs_log = obs_log[-200:]
    concepts_summary = {
        cid: {
            "label": cdef.label,
            "invariants": list(cdef.invariants),
            "attractors_count": len(cdef.feature_attractors),
            "causal_traces_count": len(cdef.causal_history),
            "top_attractors": [
                {
                    "key": a.key,
                    "support_mass": round(float(a.support_mass), 4),
                    "imagination_mass": round(float(a.imagination_mass), 4),
                    "domain_layer": a.domain_layer,
                }
                for a in sorted(cdef.feature_attractors.values(), key=lambda x: -x.support_mass)[:6]
            ],
        }
        for cid, cdef in mem.concepts.items()
    }
    doc = {
        "schema": "elysia_causal_concept_memory_v1",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "concepts_count": len(concepts_summary),
        "observations_persisted": len(obs_log),
        "concepts": concepts_summary,
        "observations": obs_log,
    }
    _save_json(CAUSAL_CONCEPT_MEMORY_PATH, doc)
    return doc


def build_connected_elysia_organism(force_absorb_world: bool = False) -> Dict[str, Any]:
    """
    Instantiates Elysia's EXISTING core organs and feeds ALL real lived
    external sensory records (3D renders, audio prosody, story text, Korean
    principles) directly into `ScaleRotorHierarchy` + `RealLanguageAcquisitionEngine`
    + `LanguageScaleRotor` + `HangulTopologicalEngine` + `ConceptualUnitSystemEngine`
    + `EnactiveRelationalMemoryEngine` + `CausalConceptMemory` + `ElysiaUnifiedLivingCycle`.
    """
    srh = ScaleRotorHierarchy()
    hangul_engine = HangulTopologicalEngine()
    rlae = RealLanguageAcquisitionEngine()
    lsr = LanguageScaleRotor()
    cuse = ConceptualUnitSystemEngine()
    enactive_mem = _load_persistent_enactive_memory()
    causal_mem = _load_persistent_causal_concept_memory()
    living_cycle = ElysiaUnifiedLivingCycle(workspace_root=WORKSPACE_ROOT)

    ingested_visual_nodes: List[str] = []
    ingested_audio_nodes: List[str] = []
    ingested_text_nodes: List[str] = []

    # 1. Feed REAL rendered 3D / contrast visual frames into ScaleRotorHierarchy.differentiate_visual()
    visual_sources = [
        ("story_world_3d", STORY_WORLD_DIR / "story_world_embodied_3d.png", 0.35),
        ("woven_3d_pbr", WORKSPACE_ROOT / "data" / "open_sandbox" / "woven_world" / "elysia_woven_3d_keyframes.png", 0.65),
        ("prism_vision_3x3", WORKSPACE_ROOT / "data" / "open_sandbox" / "prism_vision" / "prism_vision_3x3_proof.png", 0.50),
        ("eternal_return_contrast", WORKSPACE_ROOT / "data" / "open_sandbox" / "contrast_verification" / "eternal_return_overlay_contrast_proof.png", 0.55),
    ]
    visual_obj_nodes = []
    for label, p, flux in visual_sources:
        vdata = _extract_visual_48_from_png(p)
        if vdata is None:
            continue
        vnode = srh.differentiate_visual(
            visual_vec_48=vdata["vec48"],
            motion_flux=flux,
            contrast_std=vdata["contrast_std"],
            warm_cool_ratio=vdata["warm_cool"],
            spectrum=vdata["spectrum"],
        )
        ingested_visual_nodes.append(vnode.node_id)
        visual_obj_nodes.append(vnode)

    # 2. Feed REAL synchronized audio-visual prosody into ScaleRotorHierarchy.differentiate_audio()
    av_doc = _load_json(COGNITIVE_WORLD_DIR / "control_weave_and_multimodal_prism.json", {})
    for tr in (av_doc.get("part2_synchronized_audiovisual_multimodal_prism") or [])[:4]:
        rms = float(tr.get("mean_audio_rms", 0.0))
        cent = float(tr.get("mean_audio_spectral_centroid_hz", 0.0))
        zcr = float(tr.get("mean_audio_zcr", 0.0))
        sil = float(tr.get("silence_ratio", 0.0))
        prosody = {
            "rms_energy": rms,
            "spectral_centroid_hz": cent,
            "zero_crossing_rate": zcr,
            "silence_ratio": sil,
            "av_corr": float(tr.get("visual_motion_vs_audio_rms_corr", 0.0)),
        }
        spec = [min(1.0, rms * 5.0), min(1.0, cent / 3000.0), sil, zcr]
        anode = srh.differentiate_audio(prosody=prosody, spectrum=spec)
        ingested_audio_nodes.append(anode.node_id)

    # 2.5 Feed ALL persisted REAL YouTube Multimodal Episodes (Synchronized Video + Voice Prosody + Korean Subtitles)!
    yt_mem = _load_json(YOUTUBE_MEMORY_PATH, {})
    yt_episodes = list((yt_mem.get("episodes") or {}).values())
    yt_triad_links_created = 0
    yt_cues_absorbed = 0
    for ep in yt_episodes:
        ep_title = str(ep.get("title", "youtube"))
        ep_vid = str(ep.get("video_id", "yt"))
        for cue in (ep.get("cues") or [])[:40]:
            txt = str(cue.get("text") or "").strip()
            if len(txt) < 4 or not any(0xAC00 <= ord(ch) <= 0xD7A3 for ch in txt):
                continue
            pros = cue.get("voice_prosody") or {}
            vmot = cue.get("visual_motion") or {}
            f48 = cue.get("frame_visual_48")
            chr_tri = cue.get("emotion_chroma") or [0.34, 0.33, 0.33]
            spec4 = [
                round(float(chr_tri[0]), 4),
                round(float(chr_tri[1]), 4),
                round(float(chr_tri[2]), 4),
                round(float(pros.get("rms_energy", 0.15)), 4),
            ]
            # Scale 3 spoken Korean utterance
            t_node = srh.differentiate_text(txt, spectrum=spec4, situation=ep_title[:40], cause=f"youtube:{ep_vid}")
            ingested_text_nodes.append(t_node.node_id)

            # Paired Scale 3 visual frame at exact timestamp t_start
            paired_sensory: List[Any] = []
            if isinstance(f48, dict) and f48.get("vec48"):
                v_node = srh.differentiate_visual(
                    visual_vec_48=f48["vec48"],
                    motion_flux=float(vmot.get("motion_flux", 0.15)),
                    contrast_std=float(f48.get("contrast_std", 0.2)),
                    warm_cool_ratio=float(f48.get("warm_cool", 1.0)),
                    spectrum=f48.get("spectrum", spec4),
                )
                ingested_visual_nodes.append(v_node.node_id)
                srh._add_or_reinforce_link(t_node.node_id, v_node.node_id, "resonates", weight=0.92)
                paired_sensory.append(v_node)
                yt_triad_links_created += 1

            # Paired Scale 3 vocal audio prosody at exact [t_start, t_end]
            if pros:
                a_node = srh.differentiate_audio(
                    prosody={
                        "rms_energy": float(pros.get("rms_energy", 0.0)),
                        "zero_crossing_rate": float(pros.get("zero_cross_rate", 0.0)),
                        "duration_s": float(pros.get("duration_s", 1.0)),
                        "motion_flux": float(vmot.get("motion_flux", 0.0)),
                    },
                    spectrum=[
                        min(1.0, float(pros.get("rms_energy", 0.0)) * 5.0),
                        min(1.0, float(pros.get("zero_cross_rate", 0.0)) * 3.0),
                        float(vmot.get("motion_flux", 0.1)),
                        float(vmot.get("contrast_std", 0.2)),
                    ],
                )
                ingested_audio_nodes.append(a_node.node_id)
                srh._add_or_reinforce_link(t_node.node_id, a_node.node_id, "resonates", weight=0.92)
                paired_sensory.append(a_node)
                yt_triad_links_created += 1

            if paired_sensory:
                srh.acquire_naming_links(t_node, paired_sensory)

            rlae.absorb_real_korean(txt, source=f"youtube_av:{ep_vid}", topic=ep_title[:30], rebuild_svd=False)
            yt_cues_absorbed += 1

    # 3. Feed REAL Korean Story World prose + lived encounters + AGENTS principles into
    #    ScaleRotorHierarchy.differentiate_text(), RealLanguageAcquisitionEngine, and LanguageScaleRotor!
    story_state = _load_json(STORY_STATE_PATH, {})
    if not story_state or not story_state.get("npcs"):
        story_state = create_and_run_story_world(DEFAULT_STORY_TEXT, generations=2, render_3d=False)

    korean_entries: List[Dict[str, str]] = []
    # Include all YouTube spoken subtitles in LSR induction too!
    for ep in yt_episodes:
        ep_title = str(ep.get("title", "youtube"))
        ep_vid = str(ep.get("video_id", "yt"))
        for cue in (ep.get("cues") or [])[:50]:
            txt = str(cue.get("text") or "").strip()
            if len(txt) >= 4 and any(0xAC00 <= ord(ch) <= 0xD7A3 for ch in txt):
                korean_entries.append({"sentence": txt, "source": f"youtube_av:{ep_vid}", "topic": ep_title[:30]})
    for ln in str(story_state.get("source_story", DEFAULT_STORY_TEXT)).splitlines():
        s = ln.strip().lstrip("-• ").strip()
        if len(s) >= 8:
            korean_entries.append({"sentence": s, "source": "story_world_corpus", "topic": "빛의_시계_계곡"})
    for ev in (story_state.get("recent_emergent_events") or [])[-6:]:
        gt = str(ev.get("grounded_trace", "")).strip()
        if gt:
            korean_entries.append({"sentence": gt, "source": "story_world_event", "topic": "NPC_상호작용"})

    # Harvest & feed real multi-domain Korean Wikipedia + Public Literature + Local Docs!
    world_corpus = harvest_real_korean_world_corpus(rlae, force_refresh=force_absorb_world)
    korean_entries.extend(world_corpus.get("entries") or [])

    lsr_samples: List[Dict[str, Any]] = []
    # Differentiate up to 340 diverse real Korean sentences across Scale 0..4 while absorbing full corpus into RLAE + LSR!
    for idx, entry in enumerate(korean_entries[:600]):
        sent = entry["sentence"]
        src = entry["source"]
        top = entry["topic"]
        if idx < 340 and not src.startswith("youtube_av:"):
            c_res = cuse.process_conceptual_unit(sent)
            spec = _triad_to_spec4(getattr(c_res, "chromatic_triad", None))
            tnode = srh.differentiate_text(sent, spectrum=spec, situation=top, cause=src)
            ingested_text_nodes.append(tnode.node_id)
            if visual_obj_nodes and idx < 24:
                srh.acquire_naming_links(tnode, visual_obj_nodes[:2])
        else:
            spec = [0.34, 0.33, 0.33, 0.15]
        rlae.absorb_real_korean(sent, source=src, topic=top, rebuild_svd=False)
        lsr_samples.append({"utterance": sent, "situation": top, "chroma": tuple(spec[:3])})

    # Rebuild PPMI/SVD causal axes once across the ENTIRE absorbed Korean corpus!
    if korean_entries:
        rlae.absorb_real_korean(korean_entries[0]["sentence"], source="corpus_finalize", topic="통합", rebuild_svd=True)
    lsr_induced = lsr.induce_from_utterances(lsr_samples)

    rlae_pub = rlae.get_public_state() if hasattr(rlae, "get_public_state") else {}

    return {
        "srh": srh,
        "hangul_engine": hangul_engine,
        "rlae": rlae,
        "lsr": lsr,
        "cuse": cuse,
        "enactive_mem": enactive_mem,
        "causal_mem": causal_mem,
        "living_cycle": living_cycle,
        "story_state": story_state,
        "ingested_counts": {
            "visual_nodes": len(ingested_visual_nodes),
            "audio_nodes": len(ingested_audio_nodes),
            "text_nodes_in_srh": len(ingested_text_nodes),
            "youtube_episodes_connected": len(yt_episodes),
            "youtube_aligned_cues_absorbed": yt_cues_absorbed,
            "youtube_av_text_triad_links": yt_triad_links_created,
            "total_korean_sentences_absorbed": len(lsr_samples),
            "wiki_topics_fetched": world_corpus.get("wiki_topics_fetched", []),
            "public_literature_rotors": world_corpus.get("public_literature_rotors", 0),
            "total_scale_rotor_nodes": len(srh.nodes),
            "total_scale_rotor_links": len(srh.links),
            "lsr_induced_schemas": lsr_induced,
            "rlae_public_state": {
                k: rlae_pub.get(k)
                for k in ("vocab_size", "walker_reliance", "read_count", "causal_edges_count", "clause_frames_count")
                if k in rlae_pub
            },
            "warm_started_enactive_entities": len(enactive_mem.consolidated_substrates),
            "warm_started_causal_concepts": len(causal_mem.concepts),
        },
        "visual_node_ids": ingested_visual_nodes,
        "audio_node_ids": ingested_audio_nodes,
    }


def process_through_connected_elysia(utterance: str, organism: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Runs a human Korean utterance through ALL of Elysia's real existing core
    organs in one continuous bottom-up + top-down living circulation:
      Scale 0 (Hangul Jamo articulatory spin) -> Scale 1 (Syllables)
      -> Scale 2 (Korean stems/particles/predicates + CausalPropositionFrame + ConceptualUnit)
      -> Scale 3 (Utterance/Visual/Audio) -> Clifford Cl(3,0) Docking
      -> PPMI/SVD Semantic Bridges -> ScaleRotorHierarchy + LanguageScaleRotor Composition
      -> EnactiveRelationalMemory Self-Calibration & Persistent Substrate Consolidation
      -> CausalConceptMemory Cause-Process-Result Learning & Counterfactual Assessment
      -> ElysiaUnifiedLivingCycle Breath + SHA-256 Provenance + CausalField 7-Organ Sync!
    """
    org = organism if organism is not None else build_connected_elysia_organism()
    srh: ScaleRotorHierarchy = org["srh"]
    hangul_engine: HangulTopologicalEngine = org["hangul_engine"]
    rlae: RealLanguageAcquisitionEngine = org["rlae"]
    lsr: LanguageScaleRotor = org["lsr"]
    cuse: ConceptualUnitSystemEngine = org["cuse"]
    enactive_mem: EnactiveRelationalMemoryEngine = org["enactive_mem"]
    causal_mem: CausalConceptMemory = org["causal_mem"]
    living_cycle: ElysiaUnifiedLivingCycle = org["living_cycle"]
    story_state: Dict[str, Any] = org["story_state"]

    q = (utterance or "").strip()

    # 0. Parse Korean Causal Semantic Roles via `core.topology.korean_causal_linguistics`
    parsed_input_frame = parse_korean_causal_frame(q)

    # 1. Scale 0-1: Real Hangul Articulatory Topology (Jamo Spin Matrices + Vowel Phase!)
    hangul_enc = hangul_engine.encode_text(q)
    if isinstance(hangul_enc, tuple) and len(hangul_enc) >= 2:
        spin_list, profile_list = hangul_enc[0], hangul_enc[1]
        hangul_summary = {
            "encoded_syllable_spins": len(spin_list),
            "syllable_count": len([ch for ch in q if 0xAC00 <= ord(ch) <= 0xD7A3]),
            "sample_syllable_profiles": profile_list[:3],
        }
    else:
        hangul_summary = {
            "syllable_count": len([ch for ch in q if 0xAC00 <= ord(ch) <= 0xD7A3]),
            "encoded_type": type(hangul_enc).__name__,
        }

    # 2. Conceptual Unit & Existential Intent (Elysia's existing ConceptualUnitSystemEngine!)
    c_res = cuse.process_conceptual_unit(q)
    spec = _triad_to_spec4(getattr(c_res, "chromatic_triad", None))
    intent_obj = getattr(c_res, "existential_intent", None)
    intent_summary = {
        "chromatic_triad": spec[:3],
        "existential_intent": str(getattr(intent_obj, "intent_type", intent_obj)) if intent_obj is not None else "open_inquiry",
        "sensory_profile": c_res.sensory_profile.to_dict() if hasattr(c_res, "sensory_profile") and hasattr(c_res.sensory_profile, "to_dict") else {},
    }

    # 3. Scale 0->1->2->3 Fractal Differentiation inside ScaleRotorHierarchy!
    u_node = srh.differentiate_text(q, spectrum=spec, situation="live_user_dialogue", cause="human_utterance")
    scale_dist: Dict[str, int] = {}
    for nd in srh.nodes.values():
        k = f"Scale_{nd.scale}"
        scale_dist[k] = scale_dist.get(k, 0) + 1

    # 4. Clifford Cl(3,0) Protein-Like Structural Docking (`M_a * M_b~`) across ALL modalities!
    dock_report = srh.dock_and_self_assemble(u_node.node_id, min_affinity=0.55, max_torque=0.65, max_partners=6)

    # 5. PPMI/SVD Semantic Bridges via RealLanguageAcquisitionEngine!
    rlae.absorb_real_korean(q, source="live_user_dialogue", topic="상호작용", rebuild_svd=True)
    words = [w.strip(".,?!\"'()") for w in q.split() if len(w.strip(".,?!\"'()")) >= 2]
    bridges = rlae.find_semantic_bridges(words[:6], limit=4)

    # 6. Compose Grounded Korean Utterance FROM Elysia's OWN ScaleRotorHierarchy (CausalPropositionFrame) + LanguageScaleRotor!
    cue_ids = [u_node.node_id, *org["visual_node_ids"][:2], *org["audio_node_ids"][:2]]
    srh_utterance, srh_meta = srh.compose_utterance_from_hierarchy(cue_ids, q, spec)
    lsr_utterance, lsr_meta = lsr.compose_novel_utterance(q, situation_text=story_state.get("world_title", ""), chroma=(spec[0], spec[1], spec[2]))

    # 7. EnactiveRelationalMemoryEngine: Cross-Modal Relational Mesh + Enactive Self-Calibration + Persistent Substrate!
    entity_key = parsed_input_frame.subject or (words[0] if words else "live_dialogue")
    entity_id = f"enactive::{entity_key}"
    docked_peers = dock_report.get("docked_peers") or []
    causal_events_list = [
        f"SRH_CausalFrame: {srh_utterance}" if srh_utterance else f"Utterance: {q}",
        f"LSR_Induced: {lsr_utterance}" if lsr_utterance else "LSR_idle",
        f"Clifford_Cl30_Docking: {len(docked_peers)} peers in {dock_report.get('cluster_id')}",
    ]
    if bridges:
        causal_events_list.append(f"PPMI_SVD_Bridge: {bridges[0]}")
    enactive_mem.create_cross_modal_mesh(
        entity_id=entity_id,
        entity_name=entity_key,
        linguistic_def=f"{q} => {srh_utterance or lsr_utterance}",
        visual_form_desc=f"ScaleRotorHierarchy visual_nodes={org['visual_node_ids'][:2]}",
        causal_events=causal_events_list,
        sensory_attributes={
            "audio_nodes": org["audio_node_ids"][:2],
            "touch_taste": f"chromatic_triad={spec[:3]}, intent={intent_summary['existential_intent']}",
        },
    )
    # Use REAL measured discrepancy from LanguageScaleRotor resonance & docking affinity (zero hardcoded fakes!)
    measured_res = float(lsr_meta.get("resonance_score", 0.6))
    measured_friction = max(0.02, min(0.95, 1.0 - measured_res))
    cal_res = enactive_mem.enact_self_calibration(
        entity_id,
        {
            "reality_coherence": measured_res,
            "world_friction": measured_friction,
            "mismatched_modal": "CAUSAL_EVENT" if measured_friction > 0.3 else "LANGUAGE",
        },
    )
    substrate_record = enactive_mem.consolidate_to_substrate(entity_id)
    enactive_persisted = _save_persistent_enactive_memory(enactive_mem)

    # 8. CausalConceptMemory: Cause-Process-Result Internalization & Counterfactual Variant Discernment!
    concept_id = f"concept::{entity_key}"
    obs_features = {
        k: v
        for k, v in {
            "subject": parsed_input_frame.subject,
            "object": parsed_input_frame.obj,
            "instrument": parsed_input_frame.instrument,
            "context": parsed_input_frame.context,
            "mechanism": parsed_input_frame.action_mechanism[:40],
        }.items()
        if v
    }
    if not obs_features:
        obs_features = {"utterance_head": entity_key}
    is_counterfactual = any(mk in q for mk in ("만약", "된다면", "없다면", "가린다면", "줄이고", "바뀐다면"))
    obs_id = f"obs_{int(time.time() * 1000)}_{len(causal_mem.concepts)}"
    new_obs_record = {
        "observation_id": obs_id,
        "concept_id": concept_id,
        "label": entity_key,
        "features": obs_features,
        "process_context": {
            "domain_layer": "multimodal_scale_rotor_layer",
            "causal_connector": parsed_input_frame.causal_connector or "direct",
            "srh_predicate": (srh_meta.get("used_predicates") or [""])[0],
        },
        "evidence_strength": round(max(0.25, measured_res), 4),
        "is_real_world": not is_counterfactual,
        "invariants": [f"scale_rotor_grounded:{entity_key}", f"cluster:{dock_report.get('cluster_id')}"],
    }
    cdef = causal_mem.learn_observation(
        CausalObservation(
            observation_id=obs_id,
            concept_id=concept_id,
            features=obs_features,
            process_context=new_obs_record["process_context"],
            evidence_strength=new_obs_record["evidence_strength"],
            is_real_world=new_obs_record["is_real_world"],
        ),
        label=entity_key,
        invariants=new_obs_record["invariants"],
    )
    variant_assessment = causal_mem.assess_variant(
        concept_id=concept_id,
        variant_name=f"live_variant::{entity_key}",
        proposed_features=obs_features,
        process_context={"variable_axes": list(obs_features.keys())},
    )
    causal_mem_persisted = _save_persistent_causal_concept_memory(causal_mem, [new_obs_record])

    # 9. ElysiaUnifiedLivingCycle: Living Breath + Real AST Organ Audit + SHA-256 Provenance + CausalField 7-Organ Sync!
    prev_prov = _load_json(LIVING_CYCLE_PROVENANCE_PATH, {})
    prev_breath_total = int(prev_prov.get("cumulative_breaths", 0))
    encounter = LivingEncounter(
        encounter_name=f"live_dialogue_{entity_key}",
        world=ExtendedWorldState(),
        text_document=f"{q}\n{srh_utterance}\n{lsr_utterance}".strip(),
    )
    cycle_res = living_cycle.breathe_and_understand(encounter)
    cf_sync = cycle_res.sync_to_causal_field()
    cf_obj = cf_sync["causal_field"]
    living_cycle_summary = {
        "cumulative_breaths": prev_breath_total + 1,
        "session_breath_index": cycle_res.breath_index,
        "encounter_name": cycle_res.encounter_name,
        "provenance_chain_valid": cycle_res.provenance_chain_valid,
        "provenance_hash": getattr(cycle_res.provenance_record, "state_hash", str(cycle_res.provenance_record))[:32],
        "provenance_tick": int(getattr(cycle_res.provenance_record, "tick", 0)),
        "hangul_wave_coherence": round(float(cycle_res.hangul_wave_coherence), 4),
        "ast_verified_organ_files": cycle_res.architectural_audit.total_organ_files,
        "ast_verified_organ_classes": cycle_res.architectural_audit.total_organ_classes,
        "ast_verified_organ_lines": cycle_res.architectural_audit.total_organ_lines,
        "causal_field_voxels_synced": len(cf_sync["voxels"]),
        "causal_field_beams_linked": int(cf_sync["beams_linked"]),
        "causal_field_total_voxels": len(getattr(cf_obj, "voxels", {})),
        "first_person_reflection_ko": cycle_res.divergence_reflection.first_person_reflection_ko,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    _save_json(LIVING_CYCLE_PROVENANCE_PATH, living_cycle_summary)

    # 10. Persist live ScaleRotorHierarchy snapshot (Scale 0..4 unified memory!)
    _save_json(
        CONNECTED_HIERARCHY_PATH,
        {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "scale_distribution": scale_dist,
            "total_nodes": len(srh.nodes),
            "total_links": len(srh.links),
            "grounded_names_count": srh.count_grounded_names(),
            "ingested_counts": org["ingested_counts"],
            "enactive_memory_entities": enactive_persisted["consolidated_entities_count"],
            "causal_concepts_persisted": causal_mem_persisted["concepts_count"],
            "living_cycle_cumulative_breaths": living_cycle_summary["cumulative_breaths"],
        },
    )

    unified_text = (
        f"[엘리시아 기존 10개 핵심 기관 통합 순환 응답]\n"
        f"• 입력 인과 역할 프레임 (CausalPropositionFrame): {parsed_input_frame.to_dict()}\n"
        f"• 계층 분화 (Scale 0 자모 → Scale 1 음절 → Scale 2 형태소/서술어 → Scale 3 발화/시각/음향): {scale_dist}\n"
        f"• Clifford Cl(3,0) 구조 도킹: 파트너 {len(docked_peers)}건 (클러스터={dock_report.get('cluster_id')}, 앵커={u_node.node_id})\n"
        f"• ScaleRotorHierarchy + CausalPropositionFrame 발화: {srh_utterance}\n"
        f"• LanguageScaleRotor 유도 발화: {lsr_utterance}\n"
        f"• RealLanguageAcquisitionEngine 의미 다리: {bridges[:3]}\n"
        f"• EnactiveRelationalMemory 영구 기억망: 엔티티 {enactive_persisted['consolidated_entities_count']}개 / 노드 {enactive_persisted['total_relational_nodes']} / 간선 {enactive_persisted['total_relational_edges']} (정합도={cal_res.calibrated_mesh.coherence_score:.3f}, 조율={cal_res.action_taken})\n"
        f"• CausalConceptMemory 인과 판별: 개념 '{cdef.label}' -> {variant_assessment.reality.value} (구조 타당도={variant_assessment.evidence['structural_validity']:.3f}, 누적 개념 {causal_mem_persisted['concepts_count']}개)\n"
        f"• ElysiaUnifiedLivingCycle & CausalField 동기화: 누적 호흡 #{living_cycle_summary['cumulative_breaths']} | SHA-256 Provenance={living_cycle_summary['provenance_chain_valid']} | AST 자가점검={living_cycle_summary['ast_verified_organ_files']}개 기관({living_cycle_summary['ast_verified_organ_classes']}클래스) | CausalField 복셀 {living_cycle_summary['causal_field_voxels_synced']}개·빔 {living_cycle_summary['causal_field_beams_linked']}개 연결"
    )

    return {
        "schema": "elysia_connected_existing_organs_v2",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "input_utterance": q,
        "parsed_causal_frame": parsed_input_frame.to_dict(),
        "connected_existing_organs": [
            "core.topology.unified_scale_rotor_hierarchy.ScaleRotorHierarchy",
            "core.topology.korean_causal_linguistics.CausalPropositionFrame",
            "core.topology.hangul_topological_engine.HangulTopologicalEngine",
            "core.orchestration.language_acquisition_engine.RealLanguageAcquisitionEngine",
            "core.embodiment.language_scale_rotor.LanguageScaleRotor",
            "core.consciousness.conceptual_unit_system_engine.ConceptualUnitSystemEngine",
            "core.memory.enactive_relational_memory.EnactiveRelationalMemoryEngine",
            "core.memory.causal_concept_memory.CausalConceptMemory",
            "core.orchestration.elysia_unified_living_cycle.ElysiaUnifiedLivingCycle",
            "core.physics.causal_field.CausalField",
        ],
        "hierarchy_scale_distribution": scale_dist,
        "hangul_topology_scale0_1": hangul_summary,
        "conceptual_unit_intent": intent_summary,
        "clifford_cl30_docking": dock_report,
        "ppmi_svd_semantic_bridges": bridges,
        "srh_composed_utterance": srh_utterance,
        "srh_composition_meta": srh_meta,
        "lsr_composed_utterance": lsr_utterance,
        "lsr_composition_meta": lsr_meta,
        "enactive_relational_memory": {
            "entity_id": entity_id,
            "calibration_discrepancy": round(float(cal_res.discrepancy_magnitude), 4),
            "coherence_score": round(float(cal_res.calibrated_mesh.coherence_score), 4),
            "action_taken": cal_res.action_taken,
            "persisted_entities_total": enactive_persisted["consolidated_entities_count"],
            "persisted_nodes_total": enactive_persisted["total_relational_nodes"],
            "persisted_edges_total": enactive_persisted["total_relational_edges"],
            "substrate_record": substrate_record,
        },
        "causal_concept_memory": {
            "concept_id": concept_id,
            "reality_assessment": variant_assessment.reality.value,
            "grounded_support": round(float(variant_assessment.grounded_support), 4),
            "imagination_support": round(float(variant_assessment.imagination_support), 4),
            "structural_validity": round(float(variant_assessment.evidence["structural_validity"]), 4),
            "persisted_concepts_total": causal_mem_persisted["concepts_count"],
            "persisted_observations_total": causal_mem_persisted["observations_persisted"],
        },
        "unified_living_cycle": living_cycle_summary,
        "unified_grounded_response": unified_text,
    }


def run_bidirectional_knob_recreation(
    utterance: str = "",
    *,
    youtube_url_or_query: str = "",
    tempo_knob: float = 1.0,
    pitch_knob: float = 1.0,
    warmth_knob: float = 0.0,
    tension_knob: float = 0.45,
    order_knob: float = 0.85,
    law_damping_knob: float = 0.0,
    run_whisper_stt: bool = True,
) -> Dict[str, Any]:
    """
    FULL BIDIRECTIONAL MULTIMODAL SCALE-ROTOR KNOB RECREATION & SELF-VERIFICATION LOOP:
      1. Audio -> Text (Blind Whisper STT on real YouTube `.wav`, no subtitle peeking)
      2. Law / Principle Knob (`law_damping_knob`: self-excitation < 0 | conservation == 0 | damping > 0)
         coupled with Language 4D Spectrum Knobs (`tension_knob`, `order_knob`) across
         `ScaleRotorHierarchy` (`CausalPropositionFrame`) + `LanguageScaleRotor`
      3. Text -> Voice (`Microsoft Heami ko-KR` offline WinRT `.wav`) -> `AcousticScaleRotorSpectrum`
         continuous knob modulation (`pitch_knob`, `order_knob`, `law_envelope`) ->
         Whisper + Blind Audio Observer self-hearing verification!
      4. Video + Voice + Law -> Real Playable Recreated `.mp4`:
         `ConnectedMediaCausalObserver.learn_recreate_and_self_improve` (Cycle 0->1->2) ->
         `SpatiotemporalScaleRotorSpectrum.recreate_with_knobs(...)` ->
         ffmpeg mux with modulated Korean voice -> Blind self-re-observation!
    """
    import shutil
    import subprocess
    from scipy.io import wavfile

    t0 = time.perf_counter()
    if youtube_url_or_query.strip():
        ingest_youtube_into_elysia(youtube_url_or_query.strip(), max_duration_s=60)

    org = build_connected_elysia_organism(force_absorb_world=False)
    srh: ScaleRotorHierarchy = org["srh"]
    lsr: LanguageScaleRotor = org["lsr"]

    # Pick latest observed YouTube episode from persistent multimodal memory
    yt_mem = _load_json(YOUTUBE_MEMORY_PATH, {})
    yt_eps = list((yt_mem.get("episodes") or {}).values())
    active_ep = yt_eps[-1] if yt_eps else None
    mp4_src = Path(active_ep["mp4_path"]) if (active_ep and active_ep.get("mp4_path")) else None
    wav_src = Path(active_ep["wav_path"]) if (active_ep and active_ep.get("wav_path")) else None

    # 1. AUDIO -> TEXT: Blind Whisper STT on real YouTube WAV (first 12s, zero .vtt peeking!)
    yt_whisper_stt: Dict[str, Any] = {"ok": False, "skipped": not run_whisper_stt}
    if run_whisper_stt and wav_src and wav_src.is_file():
        yt_whisper_stt = transcribe_wav_whisper(wav_src, language="ko", model_name="tiny", max_seconds=12.0)

    # 2. PHYSICAL PRINCIPLE KNOB (`law_damping_knob`) + LANGUAGE SPECTRUM KNOBS
    #    -0.6 (self-excitation) <-> 0.0 (harmonic conservation) <-> +0.8 (viscous damping)
    t_law = np.linspace(0.0, 2.0, 48)
    damping_val = max(-0.6, min(0.8, float(law_damping_knob)))
    tempo_val = max(0.4, min(2.2, float(tempo_knob)))
    raw_law = np.exp(-damping_val * t_law) * (0.55 + 0.45 * np.cos(2.0 * math.pi * tempo_val * t_law))
    law_env = (raw_law - float(np.min(raw_law))) / max(1e-6, float(np.max(raw_law) - np.min(raw_law)))
    law_regime = (
        "self_excitation_growth" if damping_val < -0.08
        else "harmonic_conservation" if abs(damping_val) <= 0.08
        else "damped_convergence"
    )

    q = (utterance or "").strip() or "파동이 굴절할 때 속력과 각도는 어떻게 변할까?"
    core_res = process_through_connected_elysia(q, organism=org)

    # Steer language spectrum directly with continuous knobs (`tension_knob`, `warmth_knob`, `order_knob`)
    knob_spec = [
        round(max(0.05, min(0.95, float(tension_knob))), 4),
        round(max(0.05, min(0.95, 1.0 - float(tension_knob))), 4),
        round(max(0.05, min(0.95, 0.5 + 0.45 * float(warmth_knob))), 4),
        round(max(0.15, min(0.98, float(order_knob))), 4),
    ]
    u_anchor = core_res["clifford_cl30_docking"]["anchor"]
    cue_ids = [u_anchor, *org["visual_node_ids"][:2], *org["audio_node_ids"][:2]]
    knob_srh_utt, knob_srh_meta = srh.compose_utterance_from_hierarchy(cue_ids, q, knob_spec)
    knob_lsr_utt, knob_lsr_meta = lsr.compose_novel_utterance(
        q,
        situation_text=f"{law_regime} tempo={tempo_val:.2f}",
        chroma=(knob_spec[0], knob_spec[3], knob_spec[2]),
    )
    spoken_ko = knob_srh_utt or knob_lsr_utt or core_res.get("srh_composed_utterance") or q

    # 3. TEXT -> VOICE (Microsoft Heami ko-KR offline .wav) -> AcousticScaleRotorSpectrum Knob Modulation -> Self-Hearing STT!
    out_dir = YOUTUBE_MULTIMODAL_DIR / "knob_recreation"
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_voice_wav = out_dir / "elysia_spoken_voice.wav"
    mod_voice_wav = out_dir / "elysia_rotor_modulated_voice.wav"

    tts_res = synthesize_korean_wav_winrt(
        text=spoken_ko,
        out_wav_path=raw_voice_wav,
        speaking_rate=max(0.65, min(1.75, tempo_val)),
        audio_pitch=max(0.7, min(1.45, float(pitch_knob))),
    )
    audio_rotor_report: Dict[str, Any] = {"ok": False}
    self_hearing_stt: Dict[str, Any] = {"ok": False}
    if tts_res.get("ok") and raw_voice_wav.is_file():
        sr_v, data_v = wavfile.read(str(raw_voice_wav))
        pcm_v = np.asarray(data_v, dtype=np.float64)
        if pcm_v.ndim > 1:
            pcm_v = pcm_v.mean(axis=1)
        if np.issubdtype(data_v.dtype, np.integer):
            pcm_v = pcm_v / float(max(abs(np.iinfo(data_v.dtype).min), np.iinfo(data_v.dtype).max))
        a_rotor = encode_audio_to_scale_rotor(pcm_v, sample_rate=int(sr_v), k_bins=48)
        mod_pcm = a_rotor.recreate_pcm_with_knobs(
            pitch_shift_knob=float(pitch_knob),
            harmonic_density_knob=float(order_knob),
            law_envelope=law_env,
        )
        wavfile.write(str(mod_voice_wav), int(sr_v), np.clip(mod_pcm * 32767.0, -32767, 32767).astype(np.int16))

        ref_at = observe_audio_stream((pcm_v, int(sr_v)), build_rotor=False)
        mod_at = observe_audio_stream((mod_pcm, int(sr_v)), build_rotor=False)
        audio_rotor_report = {
            "ok": True,
            "sample_rate": int(sr_v),
            "duration_s": round(len(mod_pcm) / float(sr_v), 3),
            "compression_ratio": round(float(a_rotor.compression_ratio), 2),
            "raw_mean_rms": round(float(np.mean(ref_at.rms_energy)), 4),
            "modulated_mean_rms": round(float(np.mean(mod_at.rms_energy)), 4),
            "raw_voice_url": "/data/open_sandbox/youtube_multimodal/knob_recreation/elysia_spoken_voice.wav",
            "modulated_voice_url": "/data/open_sandbox/youtube_multimodal/knob_recreation/elysia_rotor_modulated_voice.wav",
        }
        if run_whisper_stt:
            self_hearing_stt = transcribe_wav_whisper(raw_voice_wav, language="ko", model_name="tiny")

    # 4. VIDEO + VOICE + LAW -> Real Playable Recreated `.mp4` + Blind Self-Verification!
    recreated_mp4 = out_dir / "elysia_knob_recreated_world.mp4"
    video_recreation_report: Dict[str, Any] = {"ok": False}
    if mp4_src and mp4_src.is_file():
        observer = ConnectedMediaCausalObserver()
        si_rep = observer.learn_recreate_and_self_improve(
            episode_id=f"knob_learn_{active_ep['video_id']}",
            video_source=mp4_src,
            audio_source=wav_src if (wav_src and wav_src.is_file()) else None,
            max_frames=36,
            max_cycles=3,
        )
        v_rotor = si_rep.final_visual_rotor
        if v_rotor is not None:
            out_fps = 12.0
            voice_dur = float(audio_rotor_report.get("duration_s", 3.5)) if audio_rotor_report.get("ok") else 3.5
            n_out_frames = max(36, min(96, int(round(max(3.5, voice_dur + 0.5) * out_fps))))
            t_grid = np.linspace(0.0, float(v_rotor.duration_s), n_out_frames, endpoint=False)
            mod_frames = v_rotor.recreate_with_knobs(
                t_grid,
                tempo_knob=tempo_val,
                phase_knob=float(warmth_knob) * math.pi * 0.5,
                chroma_warmth_knob=float(warmth_knob),
                harmonic_order_knob=float(order_knob),
                law_envelope=law_env,
            )
            # Upscale cleanly for crisp web playback & write playable H.264 MP4 + Elysia's modulated Korean voice via ffmpeg
            raw_vid_tmp = out_dir / "elysia_knob_video_only.mp4"
            h_out, w_out = 224, 384
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            vw = cv2.VideoWriter(str(raw_vid_tmp), fourcc, out_fps, (w_out, h_out))
            for fr in mod_frames:
                bgr = cv2.cvtColor(cv2.resize(fr, (w_out, h_out), interpolation=cv2.INTER_CUBIC), cv2.COLOR_RGB2BGR)
                vw.write(bgr)
            vw.release()

            ffmpeg_bin = shutil.which("ffmpeg")
            muxed_ok = False
            if ffmpeg_bin and raw_vid_tmp.is_file():
                audio_in = mod_voice_wav if mod_voice_wav.is_file() else (raw_voice_wav if raw_voice_wav.is_file() else None)
                if audio_in is not None:
                    ff_cmd = [
                        ffmpeg_bin, "-y",
                        "-i", str(raw_vid_tmp),
                        "-i", str(audio_in),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                        "-c:a", "aac", "-b:a", "128k",
                        "-shortest",
                        str(recreated_mp4),
                    ]
                else:
                    ff_cmd = [
                        ffmpeg_bin, "-y",
                        "-i", str(raw_vid_tmp),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                        str(recreated_mp4),
                    ]
                ff_proc = subprocess.run(ff_cmd, capture_output=True, timeout=45)
                muxed_ok = ff_proc.returncode == 0 and recreated_mp4.is_file() and recreated_mp4.stat().st_size > 2048

            # Blind Self-Verification: Re-observe her OWN recreated video+voice+subtitle!
            self_obs = observer.observe_episode(
                episode_id="elysia_self_recreated_knob_world",
                description=f"Knob-recreated world: {spoken_ko}",
                video_source=mod_frames,
                video_fps=out_fps,
                audio_source=mod_voice_wav if mod_voice_wav.is_file() else None,
                utterances=[TimeAlignedUtterance(0.0, max(1.0, voice_dur), "Elysia", spoken_ko)],
                max_frames=len(mod_frames),
                absorb_to_sphere=False,
            )
            video_recreation_report = {
                "ok": bool(muxed_ok),
                "source_youtube_id": active_ep["video_id"],
                "source_youtube_title": active_ep["title"],
                "self_improvement_cycles": [
                    {
                        "cycle": c.cycle_index,
                        "visual_mse": round(float(c.visual_mse), 5),
                        "visual_fidelity": round(float(c.visual_fidelity), 4),
                        "visual_compression_ratio": round(float(c.visual_compression_ratio), 2),
                        "audio_mse": round(float(c.audio_mse), 5),
                        "audio_env_corr": round(float(c.audio_envelope_correlation), 4),
                    }
                    for c in si_rep.cycles
                ],
                "visual_mse_drop_pct": round(float(getattr(si_rep, "visual_error_drop_ratio", 0.0)) * 100.0, 2),
                "audio_mse_drop_pct": round(float(getattr(si_rep, "audio_error_drop_ratio", 0.0)) * 100.0, 2),
                "recreated_frames": len(mod_frames),
                "recreated_mp4_path": str(recreated_mp4) if muxed_ok else "",
                "recreated_mp4_url": "/data/open_sandbox/youtube_multimodal/knob_recreation/elysia_knob_recreated_world.mp4" if muxed_ok else "",
                "self_verified_modalities": list(self_obs.present_modalities),
                "self_verified_summary_ko": self_obs.summary_ko,
            }

    out_report = {
        "schema": "elysia_bidirectional_knob_recreation_v1",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "knobs": {
            "tempo_knob": tempo_val,
            "pitch_knob": float(pitch_knob),
            "warmth_knob": float(warmth_knob),
            "tension_knob": float(tension_knob),
            "order_knob": float(order_knob),
            "law_damping_knob": damping_val,
            "law_regime": law_regime,
            "language_target_spectrum": knob_spec,
        },
        "input_utterance": q,
        "youtube_blind_whisper_stt": yt_whisper_stt,
        "knob_modulated_language": {
            "srh_causal_frame_utterance": knob_srh_utt,
            "lsr_induced_utterance": knob_lsr_utt,
            "spoken_korean_chosen": spoken_ko,
            "srh_meta": knob_srh_meta,
            "lsr_meta": knob_lsr_meta,
        },
        "korean_tts_winrt": tts_res,
        "acoustic_scale_rotor_modulation": audio_rotor_report,
        "self_hearing_whisper_stt": self_hearing_stt,
        "video_av_knob_recreation": video_recreation_report,
        "connected_organs_telemetry": {
            "scale_distribution": core_res["hierarchy_scale_distribution"],
            "enactive_memory": {
                k: core_res["enactive_relational_memory"][k]
                for k in ("persisted_entities_total", "persisted_nodes_total", "persisted_edges_total", "coherence_score")
            },
            "causal_concept_memory": core_res["causal_concept_memory"],
            "unified_living_cycle": core_res["unified_living_cycle"],
        },
    }
    _save_json(COGNITIVE_WORLD_DIR / "elysia_knob_recreation_report.json", out_report)
    return out_report


def run_parallel_self_perspective_reintegration(
    utterance: str = "",
    *,
    custom_label: str = "남성적 저음 억양 × 부드러운 여성 어법",
    custom_vertical: float = 0.52,
    custom_horizontal: float = -0.35,
    custom_vocal_pitch: float = 0.74,
    custom_vocal_tempo: float = 0.92,
    custom_stance: float = 0.56,
    synthesize_voices: bool = True,
) -> Dict[str, Any]:
    """
    ELYSIA PARALLEL-UNIVERSE SELF-FORKING, CROSS-AXIS CHARACTER CREATION, & RE-INTEGRATION:
      Forks Elysia's LIVE cognitive state into orthogonal parallel perspectives inside
      `MultiDimensionalLensRotorHub`:
        1. `scientist_engineer_self` (Micro analytic Scale 0-2, controllable vs void audit,
           runs real `CodeArchitectureLens` on Elysia's own core organs)
        2. `artist_aesthetic_self` (Macro gestalt Scale 3-4, color/rhythm/character aesthetics)
        3. `recombined_character_self` (ANY user-selected cross-axis combination — e.g.
           deep masculine vocal pitch rotor `0.74x` × soft gentle feminine stance `0.56`!)
      Each parallel self observes the SAME world, speaks in its OWN orthogonal voice rotor
      (`.wav` via WinRT Heami + `AcousticScaleRotorSpectrum`), declares its controllable ground
      vs missing epistemic domain, and RE-INTEGRATES back into `ScaleRotorHierarchy`,
      `EnactiveRelationalMemoryEngine`, `RelationalPerspectiveObserver`, and `CausalField`!
    """
    from scipy.io import wavfile

    t0 = time.perf_counter()
    org = build_connected_elysia_organism(force_absorb_world=False)
    srh: ScaleRotorHierarchy = org["srh"]
    enactive_mem: EnactiveRelationalMemoryEngine = org["enactive_mem"]
    living_cycle: ElysiaUnifiedLivingCycle = org["living_cycle"]

    q = (utterance or "").strip() or "파동이 굴절할 때 속력과 각도는 어떻게 변할까?"
    core_res = process_through_connected_elysia(q, organism=org)
    base_utt = core_res.get("lsr_composed_utterance") or core_res.get("srh_composed_utterance") or q

    # Gather live measured telemetry from Elysia's own organs & YouTube memory
    prev_knob = _load_json(COGNITIVE_WORLD_DIR / "elysia_knob_recreation_report.json", {})
    yt_mem = _load_json(YOUTUBE_MEMORY_PATH, {})
    yt_eps = list((yt_mem.get("episodes") or {}).values())
    latest_yt = yt_eps[-1] if yt_eps else {}
    vis_mse = 0.00262
    si_cycles = (prev_knob.get("video_av_knob_recreation") or {}).get("self_improvement_cycles") or []
    if si_cycles:
        vis_mse = float(si_cycles[-1].get("visual_mse", vis_mse))

    shared_payload = {
        "base_utterance": base_utt,
        "visual_mse": vis_mse,
        "ast_organ_files": int((core_res.get("unified_living_cycle") or {}).get("ast_verified_organ_files", 20)),
        "sensory_voids": ["emission_wavelength_nm"],
        "srh_nodes": len(srh.nodes),
        "youtube_cues": int(yt_mem.get("total_aligned_cues", 0)),
        "narrative_arc": str(latest_yt.get("observer_summary_ko", "Blue → Red → Yellow → Yellow")),
    }

    # Define 3 parallel perspective forks on orthogonal continuous Scale-Rotor axes
    specs = [
        CrossAxisPerspectiveSpec(
            perspective_id="scientist_engineer_self",
            label_ko="과학자·엔지니어 평행자아 (미시 계측·코드·물리)",
            vertical_scale_axis=0.12,
            horizontal_relational_axis=0.0,
            vocal_pitch_rotor=0.94,
            vocal_tempo_rotor=1.08,
            linguistic_stance_axis=0.10,
            telos_gravity="physics_code_math_precision",
        ),
        CrossAxisPerspectiveSpec(
            perspective_id="artist_aesthetic_self",
            label_ko="예술가·극작가 평행자아 (거시 미학·조형·리듬)",
            vertical_scale_axis=0.90,
            horizontal_relational_axis=0.35,
            vocal_pitch_rotor=1.10,
            vocal_tempo_rotor=0.95,
            linguistic_stance_axis=0.80,
            telos_gravity="aesthetics_character_form_rhythm",
        ),
        CrossAxisPerspectiveSpec(
            perspective_id="recombined_character_self",
            label_ko=custom_label or "교차 축 재조합 캐릭터 자아",
            vertical_scale_axis=float(custom_vertical),
            horizontal_relational_axis=float(custom_horizontal),
            vocal_pitch_rotor=float(custom_vocal_pitch),
            vocal_tempo_rotor=float(custom_vocal_tempo),
            linguistic_stance_axis=float(custom_stance),
            telos_gravity="cross_axis_character_synthesis",
        ),
    ]

    # Run ALL parallel perspective lenses + real `CodeArchitectureLens` + `LinguisticCausalLens` inside `MultiDimensionalLensRotorHub`!
    hub = MultiDimensionalLensRotorHub(living_cycle=living_cycle)
    custom_inputs: Dict[str, Any] = {}
    for sp in specs:
        hub.register_lens(sp.perspective_id, CrossAxisPerspectiveRotorLens(sp))
        custom_inputs[sp.perspective_id] = shared_payload

    self_code_paths = [
        L1_ROOT / "core" / "topology" / "unified_scale_rotor_hierarchy.py",
        L1_ROOT / "core" / "orchestration" / "multidimensional_lens_rotor.py",
        L1_ROOT / "core" / "embodiment" / "language_scale_rotor.py",
    ]
    md_report = hub.observe_multidimensionally(
        utterances=[
            q,
            base_utt,
            "모든 감각과 관점은 단일 수치로만 환원될 수 없고 수직·수평 스케일 경계 안에서 공명한다.",
        ],
        code_paths=[p for p in self_code_paths if p.is_file()],
        custom_inputs=custom_inputs,
        witness_label="parallel_self_perspective_reintegration",
    )
    cf_sync = hub.sync_to_causal_field(md_report, prefix="parallel_self")

    # Relational Self-Other-Interspace check between Scientist Self and Recombined Character Self!
    rel_obs = RelationalPerspectiveObserver(
        AgentCausalProfile(name="ScientistSelf", resource_reserve=10.0, vulnerability_gain=0.8, boundary_tolerance=8.5)
    )
    other_char = AgentCausalProfile(
        name=specs[2].label_ko[:24],
        resource_reserve=max(2.0, 7.0 - 3.0 * abs(float(custom_horizontal))),
        vulnerability_gain=max(0.5, 1.4 - 0.8 * float(custom_horizontal)),
        boundary_tolerance=max(3.0, 6.0 + 2.0 * float(custom_horizontal)),
    )
    moments = [other_char.manifest_interaction(d, dem) for d, dem in ((0.8, 3.0), (1.8, 3.0), (3.0, 3.0))]
    rel_shift = rel_obs.shift_to_other_perspective(moments, test_hostile_stereotype=True)

    # Synthesize REAL distinct playable `.wav` voice for EACH parallel self branch using its exact vocal pitch/tempo rotor!
    voice_dir = YOUTUBE_MULTIMODAL_DIR / "parallel_self_voices"
    voice_dir.mkdir(parents=True, exist_ok=True)
    branches_out: List[Dict[str, Any]] = []
    unified_epistemic_demands: List[str] = []

    for sp in specs:
        lres = md_report.lens_results[sp.perspective_id]
        expr_ko = str(lres.scales.meso_process.get("expressed_utterance_ko", lres.native_outcome_ko))
        demands = list(lres.scales.macro_horizon.get("epistemic_demands") or [])
        for dm in demands:
            if dm not in unified_epistemic_demands:
                unified_epistemic_demands.append(dm)

        # Feed each parallel perspective's realized utterance BACK into `ScaleRotorHierarchy` (re-integration!)
        p_spec4 = [
            round(float(sp.vertical_scale_axis), 3),
            round(float(sp.linguistic_stance_axis), 3),
            round((float(sp.horizontal_relational_axis) + 1.0) * 0.5, 3),
            round(float(lres.native_tension), 3),
        ]
        srh.differentiate_text(expr_ko, spectrum=p_spec4, situation=sp.label_ko, cause=sp.perspective_id)

        voice_info: Dict[str, Any] = {"ok": False}
        if synthesize_voices:
            raw_p = voice_dir / f"{sp.perspective_id}_raw.wav"
            mod_p = voice_dir / f"{sp.perspective_id}_rotor.wav"
            tts = synthesize_korean_wav_winrt(
                text=expr_ko,
                out_wav_path=raw_p,
                speaking_rate=sp.vocal_tempo_rotor,
                audio_pitch=max(0.70, min(1.45, sp.vocal_pitch_rotor)),
            )
            if tts.get("ok") and raw_p.is_file():
                sr_v, data_v = wavfile.read(str(raw_p))
                pcm_v = np.asarray(data_v, dtype=np.float64)
                if pcm_v.ndim > 1:
                    pcm_v = pcm_v.mean(axis=1)
                if np.issubdtype(data_v.dtype, np.integer):
                    pcm_v = pcm_v / float(max(abs(np.iinfo(data_v.dtype).min), np.iinfo(data_v.dtype).max))
                a_rot = encode_audio_to_scale_rotor(pcm_v, sample_rate=int(sr_v), k_bins=48)
                # Apply exact orthogonal vocal pitch shift rotor (e.g. 0.74x deep masculine resonance on soft feminine wording!)
                mod_pcm = a_rot.recreate_pcm_with_knobs(
                    pitch_shift_knob=sp.vocal_pitch_rotor,
                    harmonic_density_knob=max(0.45, 1.0 - 0.35 * abs(sp.horizontal_relational_axis)),
                )
                wavfile.write(str(mod_p), int(sr_v), np.clip(mod_pcm * 32767.0, -32767, 32767).astype(np.int16))
                at_mod = observe_audio_stream((mod_pcm, int(sr_v)), build_rotor=False)
                voice_info = {
                    "ok": True,
                    "pitch_rotor": sp.vocal_pitch_rotor,
                    "tempo_rotor": sp.vocal_tempo_rotor,
                    "mean_rms": round(float(np.mean(at_mod.rms_energy)), 4),
                    "mean_pitch_hz": round(float(np.mean(at_mod.fundamental_pitch_hz[at_mod.fundamental_pitch_hz > 10])) if np.any(at_mod.fundamental_pitch_hz > 10) else 0.0, 2),
                    "wav_url": f"/data/open_sandbox/youtube_multimodal/parallel_self_voices/{sp.perspective_id}_rotor.wav",
                    "wav_path": str(mod_p),
                }

        branches_out.append({
            "perspective_id": sp.perspective_id,
            "label_ko": sp.label_ko,
            "axes": lres.scales.micro_cells,
            "verdict": lres.native_verdict,
            "tension": lres.native_tension,
            "blood_flow_pct": round(float(md_report.blood_pulse.blood_flow.get(sp.perspective_id, 0.0)) * 100.0, 1),
            "expressed_utterance_ko": expr_ko,
            "controllable_ground": lres.scales.meso_process.get("controllable_ground", []),
            "uncontrolled_gaps": lres.scales.meso_process.get("uncontrolled_gaps", []),
            "epistemic_demands": demands,
            "voice_rotor": voice_info,
        })

    # Re-integrate unified multi-perspective expansion horizon into persistent `EnactiveRelationalMemoryEngine`!
    reint_eid = "enactive::parallel_self_reintegration"
    enactive_mem.create_cross_modal_mesh(
        entity_id=reint_eid,
        entity_name="평행자아_다관점_통합",
        linguistic_def=md_report.overall_synthesis_ko,
        visual_form_desc=f"MultiDimensionalLensRotorHub active_lenses={list(md_report.lens_results.keys())}",
        causal_events=[
            f"{b['label_ko']}: {b['expressed_utterance_ko']}" for b in branches_out
        ] + [f"ExpansionDemand: {d}" for d in unified_epistemic_demands[:4]],
        sensory_attributes={
            "touch_taste": f"blood_dominant={md_report.blood_pulse.dominant_lens}, bridges={len(md_report.resonance_bridges)}, rel_empathy={rel_shift.empathic_resonance:.3f}",
        },
    )
    enactive_mem.enact_self_calibration(
        reint_eid,
        {
            "reality_coherence": round(float(rel_shift.empathic_resonance), 4),
            "world_friction": round(float(np.mean(list(md_report.blood_pulse.lens_tensions.values()))), 4),
            "mismatched_modal": "CAUSAL_EVENT",
        },
    )
    enactive_mem.consolidate_to_substrate(reint_eid)
    enactive_persisted = _save_persistent_enactive_memory(enactive_mem)

    # Persist recursive parallel-self lineage so each run builds hierarchically on prior runs!
    lineage_path = COGNITIVE_WORLD_DIR / "elysia_parallel_self_lineage.json"
    prev_lin = _load_json(lineage_path, {"generation": 0, "accumulated_epistemic_frontier": []})
    acc_frontier = list(dict.fromkeys([*(prev_lin.get("accumulated_epistemic_frontier") or []), *unified_epistemic_demands]))

    out_doc = {
        "schema": "elysia_parallel_self_reintegration_v1",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "generation": int(prev_lin.get("generation", 0)) + 1,
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "input_utterance": q,
        "blood_pulse": {
            "heartbeat": md_report.blood_pulse.heartbeat,
            "dominant_lens": md_report.blood_pulse.dominant_lens,
            "blood_flow_pct": {k: round(v * 100.0, 1) for k, v in md_report.blood_pulse.blood_flow.items()},
            "summary_ko": md_report.blood_pulse.summary_ko,
        },
        "parallel_self_branches": branches_out,
        "code_architecture_self_audit": (
            {
                "verdict": md_report.lens_results["code_architecture"].native_verdict,
                "tension": md_report.lens_results["code_architecture"].native_tension,
                "outcome_ko": md_report.lens_results["code_architecture"].native_outcome_ko,
            }
            if "code_architecture" in md_report.lens_results
            else {}
        ),
        "cross_lens_resonance_bridges": [
            {
                "lens_a": b.lens_a,
                "lens_b": b.lens_b,
                "shared_motifs": b.shared_motifs,
                "strength": round(float(b.resonance_strength), 3),
                "insight_ko": b.insight_ko,
            }
            for b in md_report.resonance_bridges
        ],
        "relational_perspective_shift": {
            "status": rel_shift.status.value,
            "egocentric_friction": round(float(rel_shift.egocentric_friction), 4),
            "ego_sacrifice_cost": round(float(rel_shift.ego_sacrifice_cost), 4),
            "empathic_resonance": round(float(rel_shift.empathic_resonance), 4),
            "sky_horizon_axes": list(rel_shift.horizon_boundary.sky_horizon_axes),
            "compassionate_distance": rel_shift.compassionate_distance_prescription,
        },
        "reintegrated_causal_field": {
            "voxels_synced": len(cf_sync["voxels"]),
            "beams_linked": int(cf_sync["beams_linked"]),
        },
        "reintegrated_srh_total_nodes": len(srh.nodes),
        "reintegrated_enactive_entities": enactive_persisted["consolidated_entities_count"],
        "unified_epistemic_expansion_demands": unified_epistemic_demands,
        "accumulated_epistemic_frontier": acc_frontier,
        "overall_synthesis_ko": md_report.overall_synthesis_ko,
    }
    _save_json(lineage_path, out_doc)
    return out_doc


def main() -> None:
    parser = argparse.ArgumentParser(description="ELYSIA Existing Core Spines Live Unified Runner")
    parser.add_argument("--utterance", type=str, default="", help="Korean/English utterance to run through Elysia's existing core organs")
    parser.add_argument("--absorb-world", action="store_true", help="Append-merge fresh Korean Wikipedia + Public Literature + Local Docs corpus")
    parser.add_argument("--youtube", type=str, default="", help="Real YouTube URL or Korean search query to ingest synchronized video + voice + subtitles")
    parser.add_argument("--yt-seconds", type=int, default=75, help="Max clip duration in seconds for YouTube multimodal ingestion")
    parser.add_argument("--knob-recreate", action="store_true", help="Run full bidirectional Audio<->Text<->Video<->Law Scale-Rotor knob recreation loop")
    parser.add_argument("--parallel-self", action="store_true", help="Fork Elysia into parallel vertical/horizontal/cross-axis perspectives and re-integrate")
    parser.add_argument("--persona-label", type=str, default="남성적 저음 억양 × 부드러운 여성 어법")
    parser.add_argument("--vertical-axis", type=float, default=0.52)
    parser.add_argument("--horizontal-axis", type=float, default=-0.35)
    parser.add_argument("--vocal-pitch", type=float, default=0.74)
    parser.add_argument("--vocal-tempo", type=float, default=0.92)
    parser.add_argument("--stance-axis", type=float, default=0.56)
    parser.add_argument("--tempo-knob", type=float, default=1.0)
    parser.add_argument("--pitch-knob", type=float, default=1.0)
    parser.add_argument("--warmth-knob", type=float, default=0.0)
    parser.add_argument("--tension-knob", type=float, default=0.45)
    parser.add_argument("--order-knob", type=float, default=0.85)
    parser.add_argument("--law-damping-knob", type=float, default=0.0)
    parser.add_argument("--skip-whisper", action="store_true")
    args = parser.parse_args()

    if args.parallel_self:
        rep = run_parallel_self_perspective_reintegration(
            utterance=args.utterance,
            custom_label=args.persona_label,
            custom_vertical=args.vertical_axis,
            custom_horizontal=args.horizontal_axis,
            custom_vocal_pitch=args.vocal_pitch,
            custom_vocal_tempo=args.vocal_tempo,
            custom_stance=args.stance_axis,
        )
        print(json.dumps(rep, ensure_ascii=False, indent=2, default=str))
        return

    if args.knob_recreate:
        rep = run_bidirectional_knob_recreation(
            utterance=args.utterance,
            youtube_url_or_query=args.youtube,
            tempo_knob=args.tempo_knob,
            pitch_knob=args.pitch_knob,
            warmth_knob=args.warmth_knob,
            tension_knob=args.tension_knob,
            order_knob=args.order_knob,
            law_damping_knob=args.law_damping_knob,
            run_whisper_stt=not args.skip_whisper,
        )
        print(json.dumps(rep, ensure_ascii=False, indent=2, default=str))
        return

    yt_result = None
    if args.youtube.strip():
        yt_result = ingest_youtube_into_elysia(args.youtube.strip(), max_duration_s=args.yt_seconds)

    org = build_connected_elysia_organism(force_absorb_world=args.absorb_world)
    if args.utterance.strip():
        out = process_through_connected_elysia(args.utterance.strip(), organism=org)
        if yt_result is not None:
            out["youtube_ingested_episode"] = {k: v for k, v in yt_result.items() if k != "cues"}
        print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
        return

    probes = [
        "만약 짙은 안개가 시야를 줄이고 등대를 가린다면 어떻게 될까?",
        "빛의 각도와 소리의 리듬이 하나의 스케일 계층으로 연결되면 무엇이 나타나는가?",
        "기억과 언어와 감정이 시간의 흐름 속에서 신경계로 이어지면 어떤 변화가 생길까?",
    ]
    results = [process_through_connected_elysia(p, organism=org) for p in probes]
    report = {
        "schema": "elysia_connected_existing_organs_suite_v1",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "youtube_ingested_episode": ({k: v for k, v in yt_result.items() if k != "cues"} if yt_result is not None else None),
        "ingested_counts": org["ingested_counts"],
        "results": results,
    }
    _save_json(UNIT_CORTEX_REPORT_PATH, report)
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
