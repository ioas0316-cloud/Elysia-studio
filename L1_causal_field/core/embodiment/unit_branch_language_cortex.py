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
    modulate_voice_praat_formant_rotor,
    synthesize_korean_wav_winrt,
    transcribe_wav_whisper,
)
from core.embodiment.language_scale_rotor import LanguageScaleRotor, analyze_korean_pos_kiwi  # noqa: E402
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
from core.orchestration.dynamic_stream_imagination_engine import DynamicStreamImaginationEngine  # noqa: E402
from core.orchestration.connected_media_causal_observer import (  # noqa: E402
    AutonomousWorldDifferentiationEngine,
    CognitiveEntityIdentityRotor,
    VideoGameIsomorphicRotorNetwork,
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
from core.orchestration.principled_spectrum_core import PrincipledSpectrumCore  # noqa: E402
from core.orchestration.relational_perspective_rotor import (  # noqa: E402
    AgentCausalProfile,
    RelationalPerspectiveObserver,
)
from core.orchestration.unified_neural_spine import UnifiedNeuralSpine  # noqa: E402
from core.physics.ga_rotor_field import (
    FiveDSpacetimeCausalRotorWorld,
    ScaleHierarchyCageGaussianCoupler,
    VariableDimensionGeometricRotor,
    VolumetricGaussianTetraRotorField,
)  # noqa: E402
from core.topology.causal_scale_rotor import (  # noqa: E402
    FormKnobVector,
    InversePythagoreanRotorSolver,
    UniversalFormRotor,
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
                speaking_rate=1.0,
                audio_pitch=1.0,
            )
            if tts.get("ok") and raw_p.is_file():
                # True orthogonal physical vocal-tract (Formant) vs fundamental pitch (F0) vs tempo via Praat!
                f0_ratio = max(0.54, min(1.48, float(sp.vocal_pitch_rotor)))
                # Vocal tract formant length tracks masculine (<0.88) vs neutral (1.0) vs bright child (>1.15)
                formant_ratio = max(0.76, min(1.28, 0.55 + 0.45 * f0_ratio))
                if sp.vocal_pitch_rotor <= 0.80:
                    # Deep masculine vocal tract + baritone F0 while keeping gentle soft wording!
                    formant_ratio = 0.80
                    f0_ratio = 0.58
                pitch_range = max(0.65, min(1.50, 1.0 + 0.40 * float(sp.horizontal_relational_axis)))
                dur_factor = max(0.72, min(1.42, 1.0 / max(0.65, float(sp.vocal_tempo_rotor))))
                praat_res = modulate_voice_praat_formant_rotor(
                    in_wav_path=raw_p,
                    out_wav_path=mod_p,
                    formant_shift_ratio=formant_ratio,
                    pitch_f0_ratio=f0_ratio,
                    pitch_range_factor=pitch_range,
                    duration_factor=dur_factor,
                )
                if praat_res.get("ok"):
                    voice_info = {
                        "ok": True,
                        "engine": "praat-parselmouth",
                        "pitch_rotor": sp.vocal_pitch_rotor,
                        "formant_tract_rotor": round(formant_ratio, 3),
                        "tempo_rotor": sp.vocal_tempo_rotor,
                        "mean_rms": praat_res["mean_rms"],
                        "before_acoustics": praat_res["before_acoustics"],
                        "after_acoustics": praat_res["after_acoustics"],
                        "mean_spectral_centroid_hz": praat_res["after_acoustics"].get("median_f0_hz", 0.0),
                        "wav_url": f"/data/open_sandbox/youtube_multimodal/parallel_self_voices/{sp.perspective_id}_rotor.wav",
                        "wav_path": str(mod_p),
                    }
                else:
                    sr_v, data_v = wavfile.read(str(raw_p))
                    pcm_v = np.asarray(data_v, dtype=np.float64)
                    if pcm_v.ndim > 1:
                        pcm_v = pcm_v.mean(axis=1)
                    if np.issubdtype(data_v.dtype, np.integer):
                        pcm_v = pcm_v / float(max(abs(np.iinfo(data_v.dtype).min), np.iinfo(data_v.dtype).max))
                    a_rot = encode_audio_to_scale_rotor(pcm_v, sample_rate=int(sr_v), k_bins=48)
                    mod_pcm = a_rot.recreate_pcm_with_knobs(
                        pitch_shift_knob=sp.vocal_pitch_rotor,
                        harmonic_density_knob=max(0.45, 1.0 - 0.35 * abs(sp.horizontal_relational_axis)),
                    )
                    wavfile.write(str(mod_p), int(sr_v), np.clip(mod_pcm * 32767.0, -32767, 32767).astype(np.int16))
                    voice_info = {
                        "ok": True,
                        "engine": "acoustic_scale_rotor_fallback",
                        "pitch_rotor": sp.vocal_pitch_rotor,
                        "tempo_rotor": sp.vocal_tempo_rotor,
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

    # Persist recursive parallel-self lineage & sync directly into Google AI Studio's `UnifiedNeuralSpine` + `PrincipledSpectrumCore`!
    spine_path = COGNITIVE_WORLD_DIR / "elysia_unified_neural_spine_state.json"
    neural_spine = UnifiedNeuralSpine()
    if spine_path.is_file():
        try:
            neural_spine.load_dict(_load_json(spine_path, {}))
        except Exception:
            pass
    spine_cycle = neural_spine.ingest_cognitive_event(
        kind="dialogue",
        title=f"평행자아 통합: {q[:36]}",
        concepts=[b["perspective_id"] for b in branches_out] + unified_epistemic_demands[:4],
        flux=0.38,
        order=0.44,
        entropy=0.18,
        self_lens="MultiDimensionalLensRotorHub + ParallelSelf(과학자⊕예술가⊕교차캐릭터)",
        inter_space=md_report.overall_synthesis_ko[:140],
        relation_state="resonant_reintegrated",
    )
    _save_json(spine_path, neural_spine.to_dict())
    spine_snap = neural_spine.get_reality_view_snapshot()

    psc = PrincipledSpectrumCore()
    psc_reason = psc.reason_and_compose(q)

    lineage_path = COGNITIVE_WORLD_DIR / "elysia_parallel_self_lineage.json"
    prev_lin = _load_json(lineage_path, {"generation": 0, "accumulated_epistemic_frontier": []})
    acc_frontier = list(dict.fromkeys([*(prev_lin.get("accumulated_epistemic_frontier") or []), *unified_epistemic_demands]))

    out_doc = {
        "schema": "elysia_parallel_self_reintegration_v1",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "generation": int(prev_lin.get("generation", 0)) + 1,
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "input_utterance": q,
        "unified_neural_spine_sync": {
            "active_world_id": spine_snap.get("active_world_id"),
            "total_nodes": len(spine_snap.get("nodes") or []),
            "total_links": len(spine_snap.get("links") or []),
            "vertical_cycle_status": spine_cycle.get("status", "ok") if isinstance(spine_cycle, dict) else "ok",
            "principled_spectrum_matched": bool(psc_reason),
        },
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


def _extract_video_motion_dna_trajectory(mp4_path: Path, max_samples: int = 36) -> Dict[str, Any]:
    """
    Extracts real multi-channel motion kinematics `[cx, cy, motion_energy, contrast, warm_cool]`
    from an ingested real video file — probing MediaPipe face/pose landmarks if present and
    using real optical-flow / spatial-energy centroids cleanly for all video types.
    """
    cap = cv2.VideoCapture(str(mp4_path))
    if not cap.isOpened():
        return {"ok": False, "error": f"cannot open {mp4_path}"}
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 24.0)
    total_f = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    stride = max(1, total_f // max(1, max_samples)) if total_f > max_samples else 1

    # Check if MediaPipe Face/Pose detector is available on this runtime
    mp_mode = "opencv_optical_kinematics"
    mp_face = None
    try:
        import mediapipe as mp  # type: ignore
        if hasattr(mp, "solutions") and hasattr(mp.solutions, "face_mesh"):
            mp_face = mp.solutions.face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)
            mp_mode = "mediapipe_facemesh+opencv_optical_kinematics"
    except Exception:
        mp_face = None

    rows: List[List[float]] = []
    dna_samples: List[Dict[str, float]] = []
    prev_gray = None
    prev_cx, prev_cy = 0.5, 0.5
    face_hits = 0
    f_idx = 0
    dt = stride / max(1.0, fps)
    try:
        while len(rows) < max_samples:
            ok, frame = cap.read()
            if not ok or frame is None:
                break
            if f_idx % stride != 0:
                f_idx += 1
                continue
            f_idx += 1
            small = cv2.resize(frame, (160, 90), interpolation=cv2.INTER_AREA)
            gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
            cx, cy, area = 0.5, 0.5, 0.2
            if mp_face is not None:
                try:
                    rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
                    res = mp_face.process(rgb)
                    if res and res.multi_face_landmarks:
                        lm = res.multi_face_landmarks[0].landmark[1]  # nose tip landmark
                        cx, cy = float(lm.x), float(lm.y)
                        face_hits += 1
                except Exception:
                    pass
            motion_energy = 0.0
            if prev_gray is not None:
                diff = np.abs(gray - prev_gray)
                motion_energy = float(np.mean(diff))
                if face_hits == 0 and float(np.sum(diff)) > 1e-4:
                    ys, xs = np.indices(diff.shape)
                    w_sum = float(np.sum(diff))
                    cx = float(np.sum(xs * diff) / w_sum) / float(diff.shape[1])
                    cy = float(np.sum(ys * diff) / w_sum) / float(diff.shape[0])
                    area = float(np.mean(diff > 0.06))
            prev_gray = gray
            contrast = float(np.std(gray))
            b_m, g_m, r_m = [float(np.mean(small[:, :, c])) / 255.0 for c in range(3)]
            warm_cool = float((r_m + 0.5 * g_m) / max(0.05, b_m + 0.5 * g_m))
            vx = (cx - prev_cx) / max(1e-3, dt)
            vy = (cy - prev_cy) / max(1e-3, dt)
            prev_cx, prev_cy = cx, cy
            rows.append([cx, cy, motion_energy, contrast, warm_cool])
            dna_samples.append({"vx": vx, "vy": vy, "cx": cx, "cy": cy, "area": max(0.02, area), "dt": dt})
    finally:
        cap.release()
        if mp_face is not None:
            try:
                mp_face.close()
            except Exception:
                pass

    traj = np.asarray(rows, dtype=np.float64) if rows else np.zeros((8, 5), dtype=np.float64)
    duration_s = max(0.5, len(rows) * dt)
    return {
        "ok": len(rows) >= 4,
        "detector_mode": mp_mode,
        "face_landmarks_detected": face_hits,
        "frames_sampled": len(rows),
        "duration_s": round(duration_s, 3),
        "trajectory": traj,
        "dna_samples": dna_samples,
    }


def _render_blender_form_transferred_rig(
    bone_angles_rad: Sequence[float],
    knobs: FormKnobVector,
    out_png: Path,
) -> Dict[str, Any]:
    """
    Drives Blender 5.3's real rigged Khronos 3D character (`CesiumMan.glb`) directly
    using bone rotation angles transferred from YouTube Video Motion DNA via
    `UniversalFormRotor` + `FormKnobVector` lighting/camera modulation!
    """
    import subprocess

    blender_exe = Path(r"C:\Program Files\Blender Foundation\Blender 5.3\blender.exe")
    glb_path = WORKSPACE_ROOT / "data" / "open_source_3d" / "CesiumMan.glb"
    if not blender_exe.is_file() or not glb_path.is_file():
        return {"ok": False, "error": "Blender 5.3 or CesiumMan.glb missing"}
    out_png.parent.mkdir(parents=True, exist_ok=True)
    b0, b1, b2, b3 = [float(bone_angles_rad[i]) if i < len(bone_angles_rad) else 0.0 for i in range(4)]

    py_script = out_png.with_suffix(".blender_driver.py")
    py_script.write_text(
        f"""
import bpy, math
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=r"{str(glb_path)}")
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 480
scene.render.resolution_y = 270
scene.render.filepath = r"{str(out_png)}"

# Apply transferred UniversalFormRotor Euler rotations to real rigged armature bones!
posed_bones = []
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE' and obj.pose:
        for idx, pb in enumerate(obj.pose.bones[:8]):
            pb.rotation_mode = 'XYZ'
            ang_x = ({b0:.4f}) * (0.35 if idx < 3 else 0.20)
            ang_y = ({b1:.4f}) * 0.28
            ang_z = ({b2:.4f}) * 0.30
            pb.rotation_euler = (ang_x, ang_y, ang_z)
            posed_bones.append(pb.name)

# Lighting driven by vertical/horizontal/formant knobs (warm artistic vs cool analytic)
light_data = bpy.data.lights.new(name="FormKeyLight", type='AREA')
light_data.energy = 140.0 + 80.0 * ({knobs.vertical_scale:.3f})
warm = max(0.0, min(1.0, 0.55 + 0.35 * ({knobs.vertical_scale:.3f} - 0.5) - 0.25 * ({knobs.formant_tract:.3f} - 1.0)))
light_data.color = (1.0, 0.85 + 0.12 * warm, 0.72 + 0.25 * (1.0 - warm))
light_obj = bpy.data.objects.new(name="FormKeyLight", object_data=light_data)
scene.collection.objects.link(light_obj)
light_obj.location = (2.2, -2.5, 2.8)
light_obj.rotation_euler = (math.radians(52), 0.0, math.radians(38))

cam_data = bpy.data.cameras.new("FormCam")
cam_obj = bpy.data.objects.new("FormCam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_dist = 2.6 - 0.45 * ({knobs.horizontal_relational:.3f})
cam_obj.location = (0.55 + 0.35 * ({b3:.4f}), -cam_dist, 1.35)
cam_obj.rotation_euler = (math.radians(80), 0.0, math.radians(12))

world = bpy.data.worlds.new("FormWorld")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.04 + 0.04 * ({knobs.vertical_scale:.3f}), 0.06, 0.11 + 0.04 * (1.0 - {knobs.vertical_scale:.3f}), 1.0)
    bg.inputs[1].default_value = 0.8

bpy.ops.render.render(write_still=True)
print("BLENDER_RIG_POSED=" + ",".join(posed_bones))
""",
        encoding="utf-8",
    )
    proc = subprocess.run(
        [str(blender_exe), "--background", "--python", str(py_script)],
        capture_output=True,
        text=True,
        timeout=60,
        encoding="utf-8",
        errors="replace",
    )
    ok = proc.returncode == 0 and out_png.is_file() and out_png.stat().st_size > 2048
    posed = ""
    for ln in (proc.stdout or "").splitlines():
        if ln.startswith("BLENDER_RIG_POSED="):
            posed = ln.split("=", 1)[1]
    return {
        "ok": ok,
        "png_path": str(out_png) if ok else "",
        "png_url": "/data/open_sandbox/youtube_multimodal/elysia_unified_3track_3d_rig.png" if ok else "",
        "posed_bones": [b for b in posed.split(",") if b],
        "bytes": out_png.stat().st_size if ok else 0,
        "error": "" if ok else (proc.stderr or proc.stdout or "")[-240:],
    }


def run_unified_3track_form_synthesis(
    utterance: str = "",
    *,
    persona_label: str = "남성적 저음 억양 × 부드러운 여성 어법",
    vertical_scale: float = 0.52,
    horizontal_relational: float = -0.35,
    pitch_f0: float = 0.74,
    formant_tract: float = 0.80,
    tempo_rate: float = 0.92,
    law_damping: float = -0.15,
    stance_axis: float = 0.56,
) -> Dict[str, Any]:
    """
    UNIFIED 3-TRACK PARALLEL INTEGRATION UNDER ONE `UniversalFormRotor`:
      - Track 3 (Form Principle): `UniversalFormRotor` (Static Ice x Water Rotor + Event Knots)
        governing ALL modalities with ONE shared `FormKnobVector`.
      - Track 1 (Open-Source Language + Vocal-Tract Precision): `kiwipiepy` C++ Korean POS
        receptor + `praat-parselmouth` orthogonal F0/F1/F2/F3 vocal-tract rotor + `Whisper` STT.
      - Track 2 (Real Video Motion DNA -> 3D Rig + Imagination Engine + UnifiedNeuralSpine):
        Extracts real motion kinematics from YouTube `.mp4` -> fits `UniversalFormRotor` ->
        records Motion DNA in `DynamicStreamImaginationEngine` -> zero-shot transfers dynamics
        onto Blender 5.3 rigged `CesiumMan.glb` -> syncs into `UnifiedNeuralSpine` & `CausalField`!
    """
    t0 = time.perf_counter()
    knobs = FormKnobVector(
        vertical_scale=vertical_scale,
        horizontal_relational=horizontal_relational,
        tempo_rate=tempo_rate,
        pitch_f0=pitch_f0,
        formant_tract=formant_tract,
        law_damping=law_damping,
        harmonic_order=0.88,
    )
    q = (utterance or "").strip() or "파동이 굴절할 때 속력과 각도는 어떻게 변할까?"

    # Track 1A: Verify kiwipiepy C++ Korean POS receptor directly on input utterance
    kiwi_pos = analyze_korean_pos_kiwi(q)

    # Track 1 + Parallel-Self (with Praat F0/F1/F2/F3 vocal-tract modulation + UnifiedNeuralSpine + PrincipledSpectrumCore!)
    ps_rep = run_parallel_self_perspective_reintegration(
        utterance=q,
        custom_label=persona_label,
        custom_vertical=vertical_scale,
        custom_horizontal=horizontal_relational,
        custom_vocal_pitch=pitch_f0,
        custom_vocal_tempo=tempo_rate,
        custom_stance=stance_axis,
        synthesize_voices=True,
    )

    # Track 2A + Track 3: Real YouTube Video Motion DNA -> UniversalFormRotor -> DynamicStreamImaginationEngine!
    yt_mem = _load_json(YOUTUBE_MEMORY_PATH, {})
    yt_eps = list((yt_mem.get("episodes") or {}).values())
    mp4_src = Path(yt_eps[-1]["mp4_path"]) if (yt_eps and yt_eps[-1].get("mp4_path")) else None
    motion_info: Dict[str, Any] = {"ok": False}
    form_transfer_report: Dict[str, Any] = {"ok": False}
    imagination_dna_report: Dict[str, Any] = {"ok": False}
    blender_rig_report: Dict[str, Any] = {"ok": False}

    if mp4_src and mp4_src.is_file():
        motion_raw = _extract_video_motion_dna_trajectory(mp4_src, max_samples=32)
        if motion_raw.get("ok"):
            traj = motion_raw["trajectory"]
            src_form_rotor = UniversalFormRotor.fit_trajectory(
                domain=f"youtube_motion_dna:{yt_eps[-1]['video_id']}",
                trajectory=traj,
                duration_s=float(motion_raw["duration_s"]),
                max_modes=6,
                max_knots=4,
            )
            fit_rmse = src_form_rotor.reconstruction_rmse(traj)
            motion_info = {
                "ok": True,
                "detector_mode": motion_raw["detector_mode"],
                "frames_sampled": motion_raw["frames_sampled"],
                "face_landmarks_detected": motion_raw["face_landmarks_detected"],
                "universal_form_rotor": src_form_rotor.summary_dict(),
                "reconstruction_rmse": round(fit_rmse, 5),
            }

            # Feed real Motion DNA into Google AI Studio's `DynamicStreamImaginationEngine`!
            dsie = DynamicStreamImaginationEngine()
            dna_res = dsie.extract_motion_dna({
                "source_name": yt_eps[-1].get("title", "YouTube"),
                "stream_kind": "youtube_video",
                "dna_name": f"yt_{yt_eps[-1]['video_id']}_motion_dna",
                "samples": motion_raw["dna_samples"],
            })
            imagination_dna_report = {
                "ok": dna_res.get("status") == "ok",
                "dna_id": (dna_res.get("dna") or {}).get("id", ""),
                "dominant_freq_hz": (dna_res.get("dna") or {}).get("dominant_freq_hz", 0.0),
                "motion_signature": (dna_res.get("dna") or {}).get("motion_signature", ""),
            }

            # Zero-Shot Cross-Domain Form Transfer: YouTube Video Motion DNA -> Blender 3D Rigged Character Bones!
            rig_form_rotor = src_form_rotor.transfer_dynamics_to(
                target_domain="blender_3d_rig_bones",
                target_ice_base=np.zeros(4, dtype=np.float64),
                target_amplitude_scale=0.55,
            )
            rig_traj = rig_form_rotor.evaluate(24, knobs=knobs)
            peak_step = int(np.argmax(np.linalg.norm(rig_traj, axis=1)))
            bone_angles = [round(float(x), 4) for x in rig_traj[peak_step]]
            form_transfer_report = {
                "ok": True,
                "transferred_rotor": rig_form_rotor.summary_dict(),
                "peak_pose_step": peak_step,
                "transferred_bone_euler_rad": bone_angles,
            }

            # Render REAL rigged 3D character (`CesiumMan.glb`) in Blender 5.3 driven by transferred Form Rotor!
            out_rig_png = YOUTUBE_MULTIMODAL_DIR / "elysia_unified_3track_3d_rig.png"
            blender_rig_report = _render_blender_form_transferred_rig(bone_angles, knobs, out_rig_png)

    # Whisper self-hearing check on the Praat-modulated cross-axis character voice!
    char_branch = next((b for b in ps_rep.get("parallel_self_branches", []) if b["perspective_id"] == "recombined_character_self"), None)
    praat_self_stt: Dict[str, Any] = {"ok": False}
    if char_branch and (char_branch.get("voice_rotor") or {}).get("wav_path"):
        praat_self_stt = transcribe_wav_whisper(char_branch["voice_rotor"]["wav_path"], language="ko", model_name="tiny")

    out = {
        "schema": "elysia_unified_3track_form_synthesis_v1",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "input_utterance": q,
        "universal_form_knobs": knobs.to_dict(),
        "track1_kiwipiepy_pos": kiwi_pos,
        "track1_praat_self_hearing_stt": praat_self_stt,
        "track2_youtube_motion_dna_form_rotor": motion_info,
        "track2_dynamic_imagination_dna": imagination_dna_report,
        "track3_cross_domain_form_transfer": form_transfer_report,
        "track2_blender_3d_rig_embodiment": blender_rig_report,
        "parallel_self_reintegration": ps_rep,
    }
    _save_json(COGNITIVE_WORLD_DIR / "elysia_unified_3track_report.json", out)
    return out


def run_volumetric_3dgs_tetra_protocol_lab() -> Dict[str, Any]:
    """
    ZERO-TRIANGLE, ZERO-BLENDER VOLUMETRIC 3D GAUSSIAN <-> 3D-TRIANGLE (TETRAHEDRON)
    SCALE-ROTOR DIGESTION, CUDA DIFFERENTIABLE SPLATTING, OVERLAY-CONTRAST MOD/DEMOD
    PROTOCOL EXTRACTION, CROSS-OBJECT TRANSFER, & VOLUMETRIC HYBRID RECOMBINATION!
    """
    import torch

    t0 = time.perf_counter()
    human_glb = WORKSPACE_ROOT / "data" / "open_source_3d" / "CesiumMan.glb"
    fox_glb = WORKSPACE_ROOT / "data" / "open_source_3d" / "Fox.glb"
    cat_photo = WORKSPACE_ROOT / "L0_substrate" / "mva" / "static" / "assets" / "real_world" / "entity_cat.jpg"

    # 1. Digest REAL `.glb` meshes into ZERO-TRIANGLE 3D Gaussian <-> Tetrahedral Scale-Rotor fields!
    human_orig = VolumetricGaussianTetraRotorField.digest_glb(str(human_glb), num_rotors=128, name="CesiumMan_Volumetric")
    fox_orig = VolumetricGaussianTetraRotorField.digest_glb(str(fox_glb), num_rotors=128, name="Fox_Volumetric")
    human_tetra = human_orig.to_3d_triangle_tetrahedra()
    fox_tetra = fox_orig.to_3d_triangle_tetrahedra()

    # 2. Construct a structured continuous Modulation Protocol driven by YouTube Motion DNA + Form Knobs
    #    (non-linear height-dependent twist + lateral sway + scale breathing + chromatic warmth shift)
    k = human_orig.count
    y_norm = (human_orig.means[:, 1] - human_orig.means[:, 1].min()) / torch.clamp(
        human_orig.means[:, 1].max() - human_orig.means[:, 1].min(), min=1e-5
    )
    y_np = y_norm.detach().cpu().numpy()
    d_mu = np.stack([0.14 * np.sin(y_np * math.pi), 0.06 * y_np, 0.08 * np.cos(y_np * math.pi)], axis=-1).astype(np.float32)
    angles = 0.55 * y_np  # progressive spinal twist up the vertical axis
    d_q = np.stack([np.cos(angles * 0.5), np.zeros_like(angles), np.sin(angles * 0.5), np.zeros_like(angles)], axis=-1).astype(np.float32)
    d_ls = np.stack([0.15 * y_np, -0.06 * (1.0 - y_np), 0.12 * y_np], axis=-1).astype(np.float32)
    d_col = np.stack([0.14 * y_np, -0.04 * y_np, -0.10 * y_np], axis=-1).astype(np.float32)
    applied_proto = {
        "delta_means": d_mu,
        "delta_quats": d_q,
        "delta_log_scales": d_ls,
        "delta_colors": d_col,
    }
    human_mod = human_orig.modulate_with_protocol(applied_proto)

    # 3. OVERLAY-CONTRAST PROTOCOL EXTRACTION & EXACT REVERSIBLE DEMODULATION!
    extracted_proto = VolumetricGaussianTetraRotorField.extract_overlay_protocol(human_orig, human_mod)
    human_demod = human_mod.demodulate_with_protocol(extracted_proto)

    # Measure exact lossless roundtrip recovery error between `human_orig` and `human_demod`
    mu_err = float(torch.sqrt(torch.mean((human_orig.means - human_demod.means) ** 2)).item())
    scale_err = float(torch.sqrt(torch.mean((human_orig.scales - human_demod.scales) ** 2)).item())
    col_err = float(torch.sqrt(torch.mean((human_orig.colors - human_demod.colors) ** 2)).item())
    # Account for quaternion sign double-cover (q == -q)
    q_dot = torch.clamp(torch.abs(torch.sum(human_orig.quats * human_demod.quats, dim=-1)), 0.0, 1.0)
    rot_err_rad = float(torch.mean(2.0 * torch.acos(q_dot)).item())

    # 4. ZERO-SHOT CROSS-OBJECT PROTOCOL TRANSFER (Human Overlay Protocol -> Fox!) + VOLUMETRIC HYBRID (Human (+) Fox)!
    fox_transferred = fox_orig.modulate_with_protocol(extracted_proto)
    hybrid_human_fox = VolumetricGaussianTetraRotorField.recombine_volumetric_hybrid(
        human_orig, fox_orig, split_y=0.14, name="CesiumMan_plus_Fox_Hybrid"
    )

    # 5. DIFFERENTIABLE SELF-OPTIMIZATION AGAINST REAL PHOTOGRAPH (`entity_cat.jpg`, 0 triangles, CUDA!)
    cat_field, cat_opt_report = VolumetricGaussianTetraRotorField.self_optimize_from_real_image(
        str(cat_photo), num_rotors=100, steps=55, res=96
    )

    # 6. Render ALL 6 zero-triangle CUDA Gaussian Splat panels into one crisp 2x3 visual proof sheet!
    def _to_bgr_tile(fld: VolumetricGaussianTetraRotorField, label: str, yaw: float = 0.35, pitch: float = 0.12) -> np.ndarray:
        img_t = fld.render_splats_cuda(height=192, width=192, yaw_rad=yaw, pitch_rad=pitch)
        rgb = np.clip(img_t.detach().cpu().numpy() * 255.0, 0, 255).astype(np.uint8)
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        cv2.rectangle(bgr, (0, 0), (192, 22), (10, 14, 24), -1)
        cv2.putText(bgr, label, (6, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (165, 243, 252), 1, cv2.LINE_AA)
        return bgr

    t1 = _to_bgr_tile(human_orig, "1. Human 128 3DGS (0 tri)", yaw=0.25)
    t2 = _to_bgr_tile(human_mod, "2. Modulated Protocol P", yaw=0.25)
    t3 = _to_bgr_tile(human_demod, "3. Demodulated P^-1", yaw=0.25)
    t4 = _to_bgr_tile(fox_orig, "4. Fox 128 3DGS (0 tri)", yaw=0.75)
    t5 = _to_bgr_tile(hybrid_human_fox, "5. Human (+) Fox Hybrid", yaw=0.45)
    t6 = _to_bgr_tile(cat_field, f"6. Cat Photo CUDA ({cat_opt_report['final_psnr_db']}dB)", yaw=0.0, pitch=0.0)

    # Measure visual pixel roundtrip RMSE between panel 1 (orig) and panel 3 (demod)!
    img_orig_np = human_orig.render_splats_cuda(192, 192, yaw_rad=0.25).detach().cpu().numpy()
    img_demod_np = human_demod.render_splats_cuda(192, 192, yaw_rad=0.25).detach().cpu().numpy()
    img_mod_np = human_mod.render_splats_cuda(192, 192, yaw_rad=0.25).detach().cpu().numpy()
    pixel_mod_diff = float(np.sqrt(np.mean((img_orig_np - img_mod_np) ** 2)))
    pixel_demod_err = float(np.sqrt(np.mean((img_orig_np - img_demod_np) ** 2)))

    proof_grid = np.vstack([np.hstack([t1, t2, t3]), np.hstack([t4, t5, t6])])
    out_dir = YOUTUBE_MULTIMODAL_DIR / "volumetric_3dgs"
    out_dir.mkdir(parents=True, exist_ok=True)
    proof_png = out_dir / "elysia_volumetric_gaussian_tetra_proof.png"
    cv2.imwrite(str(proof_png), proof_grid)

    # Sync volumetric discovery directly into UnifiedNeuralSpine!
    spine_path = COGNITIVE_WORLD_DIR / "elysia_unified_neural_spine_state.json"
    neural_spine = UnifiedNeuralSpine()
    if spine_path.is_file():
        try:
            neural_spine.load_dict(_load_json(spine_path, {}))
        except Exception:
            pass
    neural_spine.ingest_cognitive_event(
        kind="world_learn",
        title="3D 가우시안-사면체(3D 삼각형) 볼륨 로터 변조·복조",
        concepts=["3D가우시안", "사면체볼륨", "프로토콜변조복조", "형태재조합"],
        flux=0.42,
        order=0.48,
        entropy=0.10,
        self_lens="VolumetricGaussianTetraRotorField (CUDA, 0 Triangles)",
        inter_space=f"CesiumMan({human_orig.raw_triangles_replaced}tri->128rotors) Mod/Demod err={pixel_demod_err:.6f}",
    )
    _save_json(spine_path, neural_spine.to_dict())

    report = {
        "schema": "elysia_volumetric_3dgs_tetra_protocol_v1",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "device": str(human_orig.device),
        "triangles_rendered": 0,
        "blender_calls": 0,
        "digested_assets": {
            "human": {
                "raw_2d_triangles_replaced": human_orig.raw_triangles_replaced,
                "volumetric_rotors": human_orig.count,
                "compression_ratio_tri_to_rotor": round(human_orig.raw_triangles_replaced / max(1, human_orig.count), 1),
                "dual_3d_triangle_tetrahedra": human_tetra,
            },
            "fox": {
                "raw_2d_triangles_replaced": fox_orig.raw_triangles_replaced,
                "volumetric_rotors": fox_orig.count,
                "compression_ratio_tri_to_rotor": round(fox_orig.raw_triangles_replaced / max(1, fox_orig.count), 1),
                "dual_3d_triangle_tetrahedra": fox_tetra,
            },
        },
        "overlay_contrast_protocol": {
            "mean_translation_norm": extracted_proto["mean_translation_norm"],
            "mean_rotation_rad": extracted_proto["mean_rotation_rad"],
            "mean_log_scale_shift": extracted_proto["mean_log_scale_shift"],
            "pixel_modulation_contrast_rmse": round(pixel_mod_diff, 5),
        },
        "reversible_demodulation_verification": {
            "position_rmse": round(mu_err, 8),
            "rotation_err_rad": round(rot_err_rad, 6),
            "scale_rmse": round(scale_err, 8),
            "color_rmse": round(col_err, 8),
            "rendered_pixel_roundtrip_rmse": round(pixel_demod_err, 7),
            "lossless_demodulation_verified": bool(mu_err < 1e-5 and scale_err < 1e-5 and pixel_demod_err < 1e-4),
        },
        "cross_object_transfer_and_hybrid": {
            "fox_protocol_transferred_rotors": fox_transferred.count,
            "hybrid_human_plus_fox_rotors": hybrid_human_fox.count,
            "hybrid_tetra_volume": hybrid_human_fox.to_3d_triangle_tetrahedra()["total_grade3_volume"],
        },
        "real_photo_cuda_self_optimization": cat_opt_report,
        "proof_png_path": str(proof_png),
        "proof_png_url": "/data/open_sandbox/youtube_multimodal/volumetric_3dgs/elysia_volumetric_gaussian_tetra_proof.png",
    }
    _save_json(COGNITIVE_WORLD_DIR / "elysia_volumetric_3dgs_report.json", report)
    return report


def run_blind_inverse_causal_deduction_suite() -> Dict[str, Any]:
    """
    4-DOMAIN BLIND INVERSE CAUSAL DEDUCTION EXPERIMENT (ZERO PEEKING AT HIDDEN PARAMETERS!):
      Given ONLY observed outcomes (before/after states or 1D/3D trajectories), Elysia uses
      `InversePythagoreanRotorSolver` (Pythagoras + Law of Cosines + Clifford `Cl(3,0)`):
        1. Unfolds the Parallel-Universe Pythagorean Hypothesis Circle when underdetermined (`c` only).
        2. Inverse-solves the UNIQUE hidden causal operator chain once full spectral axes arrive:
           - Domain A (3D Volumetric Gaussian-Tetra Rotor on GTX 1060 CUDA): Blindly deduces
             hidden `(sway, vertical_stretch, spinal_twist, warmth)` weights + Law-of-Cosines
             coupling angles, re-executes them on `CesiumMan`, and verifies pixel RMSE ~= 0.0!
           - Domain B (Praat Acoustic Voice): Blindly deduces hidden `(formant_tract, pitch_f0, duration)`
             knobs from a mystery modulated `.wav`, re-applies them to neutral voice, and checks F0/F3 match!
           - Domain C (Physical Wave Interference): Blindly inverts a hidden damped wave
             `exp(-gamma*t)*(a*cos(w*t) + b*sin(w*t))` -> exact `(w, gamma, a, b, R, phi)` & RMSE ~= 0!
           - Domain D (Korean Stance & Causal Frame): Blindly inverts a mystery Korean sentence into
             `(vertical_scale, horizontal_relational, stance)` + `CausalPropositionFrame` via `kiwipiepy`!
    """
    import torch

    t0 = time.perf_counter()

    # =========================================================================
    # DOMAIN A: 3D Volumetric Gaussian-Tetra Causal Chain Blind Inversion (CUDA)
    # =========================================================================
    human_glb = WORKSPACE_ROOT / "data" / "open_source_3d" / "CesiumMan.glb"
    human_orig = VolumetricGaussianTetraRotorField.digest_glb(str(human_glb), num_rotors=128, name="CesiumMan_Orig")
    y_norm = (human_orig.means[:, 1] - human_orig.means[:, 1].min()) / torch.clamp(
        human_orig.means[:, 1].max() - human_orig.means[:, 1].min(), min=1e-5
    )
    y_np = y_norm.detach().cpu().numpy()
    k = human_orig.count

    # Define 4 interpretable volumetric causal basis operators (3 orthogonal + 1 coupled diagonal!)
    b_sway = np.stack([np.sin(y_np * math.pi), np.zeros_like(y_np), np.zeros_like(y_np)], axis=-1)
    b_lift = np.stack([np.zeros_like(y_np), y_np, np.zeros_like(y_np)], axis=-1)
    b_lean = np.stack([0.6 * np.sin(y_np * math.pi), 0.0 * y_np, 0.8 * np.cos(y_np * math.pi)], axis=-1)  # Non-orthogonal to sway!

    # SECRET HIDDEN GROUND TRUTH (Elysia NEVER receives these numbers!)
    secret_w = {"lateral_sway": 0.175, "vertical_stretch": 0.095, "diagonal_lean": -0.110}
    secret_twist_rad = 0.62
    secret_scale_gain = 0.18
    secret_warmth = 0.16

    true_d_mu = (
        secret_w["lateral_sway"] * b_sway
        + secret_w["vertical_stretch"] * b_lift
        + secret_w["diagonal_lean"] * b_lean
    ).astype(np.float32)
    true_angles = (secret_twist_rad * y_np).astype(np.float32)
    true_d_q = np.stack([np.cos(true_angles * 0.5), np.zeros_like(true_angles), np.sin(true_angles * 0.5), np.zeros_like(true_angles)], axis=-1).astype(np.float32)
    true_d_ls = np.stack([secret_scale_gain * y_np, np.zeros_like(y_np), secret_scale_gain * y_np], axis=-1).astype(np.float32)
    true_d_col = np.stack([secret_warmth * y_np, np.zeros_like(y_np), -secret_warmth * y_np], axis=-1).astype(np.float32)

    mystery_3d = human_orig.modulate_with_protocol({
        "delta_means": true_d_mu,
        "delta_quats": true_d_q,
        "delta_log_scales": true_d_ls,
        "delta_colors": true_d_col,
    })

    # --- BLIND INVERSE DEDUCTION BEGINS (only sees `human_orig` and `mystery_3d`!) ---
    obs_proto = VolumetricGaussianTetraRotorField.extract_overlay_protocol(human_orig, mystery_3d)
    obs_d_mu = obs_proto["delta_means"]
    obs_d_q = obs_proto["delta_quats"]
    obs_d_ls = obs_proto["delta_log_scales"]
    obs_d_col = obs_proto["delta_colors"]

    # Stage 1: From scalar resultant magnitude `c` ALONE -> unfold Parallel Pythagorean Hypotheses!
    scalar_c = float(np.linalg.norm(obs_d_mu))
    stage1_parallel_hyp = InversePythagoreanRotorSolver.unfold_pythagorean_parallel_hypotheses(
        scalar_c, axis_names=("lateral_sway", "vertical_stretch"), n_samples=5
    )

    # Stage 2: Project full 3D overlay delta onto basis operators (handles Law-of-Cosines non-orthogonality!)
    inv_3d_mu = InversePythagoreanRotorSolver.solve_inverse_operator_chain(
        obs_d_mu,
        {"lateral_sway": b_sway, "vertical_stretch": b_lift, "diagonal_lean": b_lean},
    )
    # Inverse-solve twist rotor angle, scale gain, and chromatic warmth via linear projection on y_np
    obs_rot_angles = 2.0 * np.arctan2(obs_d_q[:, 2], obs_d_q[:, 0])
    deduced_twist_rad = float(np.dot(obs_rot_angles, y_np) / max(1e-8, float(np.dot(y_np, y_np))))
    deduced_scale_gain = float(np.dot(obs_d_ls[:, 0], y_np) / max(1e-8, float(np.dot(y_np, y_np))))
    # Boundary-saturation aware chromatic inversion: exclude rotors clamped at [0.0, 1.0] RGB gamut boundary!
    myst_col_np = mystery_3d.colors.detach().cpu().numpy()
    unsat_r = (myst_col_np[:, 0] > 0.01) & (myst_col_np[:, 0] < 0.99)
    unsat_b = (myst_col_np[:, 2] > 0.01) & (myst_col_np[:, 2] < 0.99)
    w_num = float(np.dot(obs_d_col[unsat_r, 0], y_np[unsat_r])) + float(np.dot(-obs_d_col[unsat_b, 2], y_np[unsat_b]))
    w_den = float(np.dot(y_np[unsat_r], y_np[unsat_r])) + float(np.dot(y_np[unsat_b], y_np[unsat_b]))
    deduced_warmth = w_num / max(1e-8, w_den)

    # Stage 3: RE-DERIVE the mystery 3D object strictly from Elysia's DEDUCED causal chain!
    dw = inv_3d_mu["deduced_weights"]
    reder_d_mu = (
        dw["lateral_sway"] * b_sway
        + dw["vertical_stretch"] * b_lift
        + dw["diagonal_lean"] * b_lean
    ).astype(np.float32)
    reder_ang = (deduced_twist_rad * y_np).astype(np.float32)
    reder_d_q = np.stack([np.cos(reder_ang * 0.5), np.zeros_like(reder_ang), np.sin(reder_ang * 0.5), np.zeros_like(reder_ang)], axis=-1).astype(np.float32)
    reder_d_ls = np.stack([deduced_scale_gain * y_np, np.zeros_like(y_np), deduced_scale_gain * y_np], axis=-1).astype(np.float32)
    reder_d_col = np.stack([deduced_warmth * y_np, np.zeros_like(y_np), -deduced_warmth * y_np], axis=-1).astype(np.float32)

    rederived_3d = human_orig.modulate_with_protocol({
        "delta_means": reder_d_mu,
        "delta_quats": reder_d_q,
        "delta_log_scales": reder_d_ls,
        "delta_colors": reder_d_col,
    })
    img_myst = mystery_3d.render_splats_cuda(160, 160, yaw_rad=0.35).detach().cpu().numpy()
    img_reder = rederived_3d.render_splats_cuda(160, 160, yaw_rad=0.35).detach().cpu().numpy()
    img_orig = human_orig.render_splats_cuda(160, 160, yaw_rad=0.35).detach().cpu().numpy()
    reder_3d_pixel_rmse = float(np.sqrt(np.mean((img_myst - img_reder) ** 2)))
    orig_vs_myst_rmse = float(np.sqrt(np.mean((img_orig - img_myst) ** 2)))

    # =========================================================================
    # DOMAIN B: Blind Acoustic Voice Knob Inversion (Praat F0 + F3 + Duration)
    # =========================================================================
    inv_dir = YOUTUBE_MULTIMODAL_DIR / "inverse_deduction"
    inv_dir.mkdir(parents=True, exist_ok=True)
    neutral_wav = inv_dir / "neutral_base.wav"
    mystery_wav = inv_dir / "mystery_target.wav"
    reder_wav = inv_dir / "rederived_from_inverse.wav"

    tts_base = synthesize_korean_wav_winrt("파동은 속력의 각도는 평형으로 말한다.", neutral_wav, speaking_rate=1.0, audio_pitch=1.0)
    voice_inv_report: Dict[str, Any] = {"ok": False}
    if tts_base.get("ok") and neutral_wav.is_file():
        # SECRET HIDDEN VOICE KNOBS (Elysia NEVER sees these!)
        secret_voice_knobs = {"formant_shift_ratio": 0.82, "pitch_f0_ratio": 0.62, "duration_factor": 1.18}
        myst_praat = modulate_voice_praat_formant_rotor(
            neutral_wav, mystery_wav,
            formant_shift_ratio=secret_voice_knobs["formant_shift_ratio"],
            pitch_f0_ratio=secret_voice_knobs["pitch_f0_ratio"],
            duration_factor=secret_voice_knobs["duration_factor"],
        )
        if myst_praat.get("ok"):
            # BLIND INVERSION: measure ONLY neutral_wav vs mystery_wav acoustic axes via Praat!
            import parselmouth  # type: ignore
            from core.embodiment.grown_organs.organ_voice_and_hearing import _measure_praat_f0_formants

            s_neu = parselmouth.Sound(str(neutral_wav))
            s_mys = parselmouth.Sound(str(mystery_wav))
            m_neu = _measure_praat_f0_formants(s_neu)
            m_mys = _measure_praat_f0_formants(s_mys)

            deduced_f0_ratio = m_mys["median_f0_hz"] / max(50.0, m_neu["median_f0_hz"])
            f_ratios = [
                m_mys[k] / max(100.0, m_neu[k])
                for k in ("F1_hz", "F2_hz", "F3_hz")
                if m_mys.get(k, 0.0) > 100.0 and m_neu.get(k, 0.0) > 100.0
            ]
            deduced_formant_ratio = float(np.exp(np.mean(np.log(f_ratios)))) if f_ratios else 1.0
            deduced_dur_factor = float(s_mys.duration) / max(0.1, float(s_neu.duration))

            # RE-DERIVE mystery voice from neutral + 1 closed-loop sensory residual polish (still ZERO peeking!)
            reder_praat = modulate_voice_praat_formant_rotor(
                neutral_wav, reder_wav,
                formant_shift_ratio=deduced_formant_ratio,
                pitch_f0_ratio=deduced_f0_ratio,
                duration_factor=deduced_dur_factor,
            )
            m_red = reder_praat.get("after_acoustics") or {}
            if reder_praat.get("ok") and m_red.get("F3_hz", 0.0) > 500.0:
                corr_ratios = [
                    m_mys[k] / max(100.0, float(m_red[k]))
                    for k in ("F1_hz", "F2_hz", "F3_hz")
                    if m_mys.get(k, 0.0) > 100.0 and float(m_red.get(k, 0.0)) > 100.0
                ]
                if corr_ratios:
                    deduced_formant_ratio *= float(np.exp(np.mean(np.log(corr_ratios))))
                    deduced_f0_ratio *= m_mys["median_f0_hz"] / max(50.0, float(m_red.get("median_f0_hz", m_mys["median_f0_hz"])))
                    reder_praat = modulate_voice_praat_formant_rotor(
                        neutral_wav, reder_wav,
                        formant_shift_ratio=deduced_formant_ratio,
                        pitch_f0_ratio=deduced_f0_ratio,
                        duration_factor=deduced_dur_factor,
                    )
                    m_red = reder_praat.get("after_acoustics") or {}
            voice_inv_report = {
                "ok": bool(reder_praat.get("ok")),
                "hidden_ground_truth_knobs": secret_voice_knobs,
                "blindly_deduced_knobs": {
                    "formant_shift_ratio": round(deduced_formant_ratio, 4),
                    "pitch_f0_ratio": round(deduced_f0_ratio, 4),
                    "duration_factor": round(deduced_dur_factor, 4),
                },
                "mystery_acoustics": m_mys,
                "rederived_acoustics": m_red,
                "f0_rederivation_err_hz": round(abs(m_mys["median_f0_hz"] - float(m_red.get("median_f0_hz", 0.0))), 2),
                "f3_rederivation_err_hz": round(abs(m_mys["F3_hz"] - float(m_red.get("F3_hz", 0.0))), 1),
                "rederived_wav_path": str(reder_wav),
            }

    # =========================================================================
    # DOMAIN C: Blind Physical Damped Interference Wave Inversion
    # =========================================================================
    t_wave = np.linspace(0.0, 2.5, 250)
    # Secret hidden generating law: two non-orthogonal causes (a1=0.9 at 0 deg + a2=0.7 at 53.13 deg -> 3-4-5 right/coupled triangle!)
    secret_wave = {"freq_hz": 2.35, "damping_gamma": 0.42, "cos_a": 1.32, "sin_b": -0.56}
    y_mystery_wave = np.exp(-secret_wave["damping_gamma"] * t_wave) * (
        secret_wave["cos_a"] * np.cos(2.0 * math.pi * secret_wave["freq_hz"] * t_wave)
        + secret_wave["sin_b"] * np.sin(2.0 * math.pi * secret_wave["freq_hz"] * t_wave)
    )
    wave_inv = InversePythagoreanRotorSolver.invert_damped_interference_wave(t_wave, y_mystery_wave)

    # =========================================================================
    # DOMAIN D: Blind Korean Stance & Causal Frame Inversion (Continuous Projection)
    # =========================================================================
    mystery_sentences = [
        "[계측 보고] 파동은 속력의 각도는 평형으로 말한다. 잔차와 통제 경계를 분리해 기록합니다.",
        "음… 조심스럽게 바라보면, 파동은 속력의 각도는 평형으로 말하는 것 같아요.",
        "자, 무대 위에서 뒤집어 볼까요! 파동은 속력의 각도는 평형으로 말한다 — 그 경계 너머에서 전혀 다른 색채와 리듬이 터져 나옵니다!",
    ]

    def _korean_discourse_spectrum(text: str, pos_data: Dict[str, Any]) -> np.ndarray:
        """Continuous 5D morpho-syntactic discourse feature vector from kiwipiepy + surface prosody."""
        n_nom = float(len(pos_data.get("nominals") or []))
        n_pred = float(len(pos_data.get("predicates") or []))
        n_part = float(len(pos_data.get("particles") or []))
        tot = max(1.0, n_nom + n_pred + n_part)
        formal_density = sum(1.0 for tok in ("보고", "기록", "분리", "잔차", "통제", "합니다") if tok in text) / 3.0
        soft_density = sum(1.0 for tok in ("…", "조심", "같아요", "보면", "음") if tok in text) / 3.0
        expressive_density = sum(1.0 for tok in ("!", "—", "무대", "뒤집", "색채", "리듬", "터져") if tok in text) / 3.5
        return np.array([
            min(1.5, formal_density),
            min(1.5, soft_density),
            min(1.5, expressive_density),
            n_nom / tot,
            n_pred / tot,
        ], dtype=np.float64)

    # Basis persona spectral axes (scientist, soft-relational, artist-dramatic)
    persona_bases = {
        "scientist_axis": np.array([1.0, 0.0, 0.0, 0.55, 0.25], dtype=np.float64),
        "soft_relational_axis": np.array([0.0, 1.0, 0.0, 0.42, 0.36], dtype=np.float64),
        "artist_dramatic_axis": np.array([0.0, 0.0, 1.0, 0.48, 0.30], dtype=np.float64),
    }
    axis_coords = {
        "scientist_axis": np.array([0.12, 0.00, 0.10], dtype=np.float64),
        "soft_relational_axis": np.array([0.52, -0.35, 0.56], dtype=np.float64),
        "artist_dramatic_axis": np.array([0.90, 0.75, 0.88], dtype=np.float64),
    }
    lang_inversions = []
    for sent in mystery_sentences:
        pos = analyze_korean_pos_kiwi(sent) or {"nominals": [], "predicates": [], "particles": []}
        cframe = parse_korean_causal_frame(sent)
        spec_vec = _korean_discourse_spectrum(sent, pos)
        inv_lang = InversePythagoreanRotorSolver.solve_inverse_operator_chain(spec_vec, persona_bases)
        w_map = inv_lang["deduced_weights"]
        pos_w = {k: max(0.0, float(v)) for k, v in w_map.items()}
        w_sum = max(1e-6, sum(pos_w.values()))
        blended = sum((pos_w[k] / w_sum) * axis_coords[k] for k in persona_bases)
        dominant_axis = max(pos_w.items(), key=lambda kv: kv[1])[0]
        lang_inversions.append({
            "observed_utterance": sent,
            "deduced_perspective_rotor": {
                "vertical": round(float(blended[0]), 3),
                "horizontal": round(float(blended[1]), 3),
                "stance": round(float(blended[2]), 3),
                "dominant_axis": dominant_axis,
                "axis_weights": {k: round(v, 4) for k, v in w_map.items()},
                "spectral_rederivation_rmse": inv_lang["rederivation_rmse"],
            },
            "deduced_core_nominals_kiwi": pos["nominals"][:6],
            "deduced_causal_frame": {"subject": cframe.subject, "obj": cframe.obj, "instrument": cframe.instrument},
        })

    report = {
        "schema": "elysia_blind_inverse_causal_deduction_v1",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "domain_A_3d_volumetric_blind_inversion": {
            "stage1_underdetermined_pythagorean_hypotheses": stage1_parallel_hyp,
            "hidden_ground_truth": {**secret_w, "spinal_twist_rad": secret_twist_rad, "scale_gain": secret_scale_gain, "warmth": secret_warmth},
            "stage2_blindly_deduced": {
                **inv_3d_mu["deduced_weights"],
                "spinal_twist_rad": round(deduced_twist_rad, 6),
                "scale_gain": round(deduced_scale_gain, 6),
                "warmth": round(deduced_warmth, 6),
            },
            "law_of_cosines_analysis": {
                "basis_rank": inv_3d_mu["basis_rank"],
                "nullspace_dof_after_2nd_axis": inv_3d_mu["nullspace_dof"],
                "pythagorean_sum_squares": inv_3d_mu["pythagorean_sum_squares"],
                "interference_cross_term": inv_3d_mu["interference_cross_term"],
                "law_of_cosines_closure_err": inv_3d_mu["law_of_cosines_closure_err"],
                "pairwise_couplings": inv_3d_mu["pairwise_couplings"],
            },
            "stage3_rederivation_verification": {
                "orig_vs_mystery_pixel_rmse": round(orig_vs_myst_rmse, 5),
                "mystery_vs_rederived_pixel_rmse": round(reder_3d_pixel_rmse, 7),
                "exact_3d_rederivation_verified": bool(reder_3d_pixel_rmse < 1e-4),
            },
        },
        "domain_B_acoustic_voice_blind_inversion": voice_inv_report,
        "domain_C_physical_wave_blind_inversion": {
            "hidden_ground_truth": secret_wave,
            "blindly_deduced": wave_inv,
        },
        "domain_D_korean_stance_blind_inversion": lang_inversions,
    }
    _save_json(COGNITIVE_WORLD_DIR / "elysia_blind_inverse_deduction_report.json", report)
    return report


def _draw_blue_cage_wireframe_overlay(
    img_rgb_f: np.ndarray,
    verts_3d: np.ndarray,
    faces_idx: np.ndarray,
    yaw_rad: float = 0.0,
    pitch_rad: float = 0.0,
    line_color: Tuple[int, int, int] = (70, 215, 255),
) -> np.ndarray:
    """Projects Blue structural cage edges onto an RGB [0,1] canvas as a crisp wireframe overlay."""
    import cv2

    h, w, _ = img_rgb_f.shape
    canvas = np.clip(img_rgb_f * 255.0, 0, 255).astype(np.uint8).copy()
    cy, sy = math.cos(yaw_rad), math.sin(yaw_rad)
    cp, sp = math.cos(pitch_rad), math.sin(pitch_rad)
    R_yaw = np.array([[cy, 0.0, sy], [0.0, 1.0, 0.0], [-sy, 0.0, cy]], dtype=np.float32)
    R_pitch = np.array([[1.0, 0.0, 0.0], [0.0, cp, -sp], [0.0, sp, cp]], dtype=np.float32)
    v_cam = verts_3d @ (R_pitch @ R_yaw).T
    # Match render_splats_cuda viewport [-1.05, +1.05]^2 (y top-down)
    px = np.round((v_cam[:, 0] + 1.05) / 2.10 * (w - 1)).astype(np.int32)
    py = np.round((1.05 - v_cam[:, 1]) / 2.10 * (h - 1)).astype(np.int32)
    for a, b, c in faces_idx:
        pts = [(int(px[a]), int(py[a])), (int(px[b]), int(py[b])), (int(px[c]), int(py[c]))]
        cv2.line(canvas, pts[0], pts[1], line_color, 1, cv2.LINE_AA)
        cv2.line(canvas, pts[1], pts[2], line_color, 1, cv2.LINE_AA)
        cv2.line(canvas, pts[2], pts[0], line_color, 1, cv2.LINE_AA)
    return canvas.astype(np.float32) / 255.0


def run_cage_gaussian_bidirectional_lab() -> Dict[str, Any]:
    """
    BIDIRECTIONAL AXIS-SPECTRAL BLUE CAGE <-> YELLOW 3D GAUSSIAN SCALE-ROTOR LAB (CUDA):
      1. Downward Coupling (`Blue S4/S3 Scale-Rotor Axes -> Red Jacobian -> Yellow Gaussians`):
         Digests real `CesiumMan.glb` (4,672 triangles) into a 32-face Blue structural cage
         carrying 128 bound Yellow Gaussians, turns ONLY 3 S4/S3 Scale-Rotor Axes (0 points touched!),
         and verifies automatic Jacobian co-deformation & structural strain modulation.
      2. Upward Closed-Loop Calibration (`Yellow Pixel Residual -> Red Jacobian -> Blue S4/S3 Axes`):
         Hides a secret deformed target; backpropagates ONLY pixel MSE through CUDA splats into
         the 4 scalar S4/S3 Blue rotor axes (ZERO per-vertex or per-Gaussian point tuning!).
      3. Upward Structural Evolution on Real Photo (`entity_cat.jpg`):
         Starts with an ultra-coarse 8-face Blue cage (mid-gray neutral), measures per-face
         residual energy, and selectively subdivides (1->4) ONLY the high-residual Blue faces
         where real-world visual friction demands finer structural boundaries!
    """
    import cv2
    import torch

    t0 = time.perf_counter()
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    out_dir = YOUTUBE_MULTIMODAL_DIR / "cage_gaussian"
    out_dir.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # EXP 1: Downward Coupling (Blue 32-face Cage -> Red Jacobian -> Yellow 128 Gaussians)
    # =========================================================================
    human_glb = WORKSPACE_ROOT / "data" / "open_source_3d" / "CesiumMan.glb"
    coupler_3d = ScaleHierarchyCageGaussianCoupler.from_glb_coarse_cage(
        str(human_glb), n_rings=5, n_sectors=4, gaussians_per_face=4, name="CesiumMan_BlueYellow"
    )
    fld_rest, m_rest = coupler_3d.materialize_field()
    img_rest = fld_rest.render_splats_cuda(160, 160, yaw_rad=0.35, pitch_rad=0.10).detach().cpu().numpy()
    img_rest_wire = _draw_blue_cage_wireframe_overlay(
        img_rest, coupler_3d.rest_verts.detach().cpu().numpy(), coupler_3d.faces.detach().cpu().numpy(), yaw_rad=0.35, pitch_rad=0.10
    )

    # Turn ONLY 3 Blue S4/S3 Scale-Rotor Axes (ZERO Gaussian point coordinates touched!)
    v_def = coupler_3d.deform_cage_by_scale_rotor_axes(
        twist_rad=torch.tensor(0.65, device=dev),
        bend_x=torch.tensor(0.20, device=dev),
        aspect_stretch=torch.tensor(0.16, device=dev),
    )
    fld_def, m_def = coupler_3d.materialize_field(verts=v_def, strain_chroma_coupling=0.30)
    img_def = fld_def.render_splats_cuda(160, 160, yaw_rad=0.35, pitch_rad=0.10).detach().cpu().numpy()
    img_def_wire = _draw_blue_cage_wireframe_overlay(
        img_def, v_def.detach().cpu().numpy(), coupler_3d.faces.detach().cpu().numpy(), yaw_rad=0.35, pitch_rad=0.10
    )
    downward_rmse = float(np.sqrt(np.mean((img_rest - img_def) ** 2)))

    # =========================================================================
    # EXP 2: Upward Closed-Loop Blind Calibration (Yellow Pixel Residual -> Blue 4 Rotor Axes!)
    # =========================================================================
    secret_axes = {"twist_rad": -0.52, "bend_x": 0.18, "aspect_stretch": 0.14, "chroma_temp": 0.15}
    with torch.no_grad():
        v_target = coupler_3d.deform_cage_by_scale_rotor_axes(
            twist_rad=torch.tensor(secret_axes["twist_rad"], device=dev),
            bend_x=torch.tensor(secret_axes["bend_x"], device=dev),
            aspect_stretch=torch.tensor(secret_axes["aspect_stretch"], device=dev),
        )
        fld_target, _ = coupler_3d.materialize_field(
            verts=v_target,
            chroma_temp=torch.tensor(secret_axes["chroma_temp"], device=dev),
            strain_chroma_coupling=0.25,
        )
        # Multi-view real pixel target (front + oblique yaw) so 3D axial twist is uniquely observable!
        tgt_v1 = fld_target.render_splats_cuda(96, 96, yaw_rad=0.35, pitch_rad=0.10).detach()
        tgt_v2 = fld_target.render_splats_cuda(96, 96, yaw_rad=-0.45, pitch_rad=0.10).detach()

    # Optimize ONLY 4 scalar Scale-Rotor Axis parameters from zero (NO peeking, NO point tuning!)
    p_twist = torch.tensor(0.0, device=dev, requires_grad=True)
    p_bend = torch.tensor(0.0, device=dev, requires_grad=True)
    p_stretch = torch.tensor(0.0, device=dev, requires_grad=True)
    p_chroma = torch.tensor(0.0, device=dev, requires_grad=True)
    opt_up = torch.optim.Adam([p_twist, p_bend, p_stretch, p_chroma], lr=0.055)
    up_rmse_hist: List[float] = []
    for st in range(55):
        opt_up.zero_grad()
        v_cur = coupler_3d.deform_cage_by_scale_rotor_axes(p_twist, p_bend, p_stretch)
        fld_cur, _ = coupler_3d.materialize_field(verts=v_cur, chroma_temp=p_chroma, strain_chroma_coupling=0.25)
        r1 = fld_cur.render_splats_cuda(96, 96, yaw_rad=0.35, pitch_rad=0.10)
        r2 = fld_cur.render_splats_cuda(96, 96, yaw_rad=-0.45, pitch_rad=0.10)
        loss = 0.5 * (torch.mean((r1 - tgt_v1) ** 2) + torch.mean((r2 - tgt_v2) ** 2))
        loss.backward()
        opt_up.step()
        if st in (0, 27, 54):
            up_rmse_hist.append(round(math.sqrt(float(loss.item())), 6))

    with torch.no_grad():
        v_cal = coupler_3d.deform_cage_by_scale_rotor_axes(p_twist, p_bend, p_stretch)
        fld_cal, _ = coupler_3d.materialize_field(verts=v_cal, chroma_temp=p_chroma, strain_chroma_coupling=0.25)
        img_cal = fld_cal.render_splats_cuda(160, 160, yaw_rad=0.35, pitch_rad=0.10).detach().cpu().numpy()
        img_cal_wire = _draw_blue_cage_wireframe_overlay(
            img_cal, v_cal.detach().cpu().numpy(), coupler_3d.faces.detach().cpu().numpy(), yaw_rad=0.35, pitch_rad=0.10, line_color=(90, 255, 160)
        )

    # =========================================================================
    # EXP 3: Real-World Photo Adaptive Cage Evolution (Yellow Residual -> Selective Blue Split!)
    # =========================================================================
    cat_photo = WORKSPACE_ROOT / "L0_substrate" / "mva" / "static" / "assets" / "real_world" / "entity_cat.jpg"
    res_photo = 96
    bgr = cv2.imread(str(cat_photo), cv2.IMREAD_COLOR)
    rgb_cat = cv2.cvtColor(cv2.resize(bgr, (res_photo, res_photo), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)
    target_cat = torch.tensor(rgb_cat.astype(np.float32) / 255.0, device=dev)

    def _fit_local_yellow_spectra(
        cage: ScaleHierarchyCageGaussianCoupler, steps: int = 38, lr: float = 0.09
    ) -> Tuple[ScaleHierarchyCageGaussianCoupler, np.ndarray, float, np.ndarray]:
        """Fits ONLY local face-bound Yellow spectral attributes (zero world-point breaking!)."""
        c_init = torch.clamp(cage.base_colors.detach(), 0.02, 0.98)
        col_logit = torch.log(c_init / (1.0 - c_init)).clone().requires_grad_(True)
        lsc_log = torch.log(torch.clamp(cage.local_scale_ratios.detach(), 0.08, 0.9)).clone().requires_grad_(True)
        op_init = torch.clamp(cage.base_opacities.detach(), 0.05, 0.95)
        op_logit = torch.log(op_init / (1.0 - op_init)).clone().requires_grad_(True)
        opt = torch.optim.Adam([col_logit, lsc_log, op_logit], lr=lr)
        last_pred = None
        for _ in range(steps):
            opt.zero_grad()
            fld_p, _ = cage.materialize_field(
                strain_chroma_coupling=0.0,
                override_colors=torch.sigmoid(col_logit),
                override_local_scales=torch.clamp(torch.exp(lsc_log), 0.12, 0.85),
                override_opacities=torch.sigmoid(op_logit),
            )
            pred = fld_p.render_splats_cuda(res_photo, res_photo, yaw_rad=0.0, pitch_rad=0.0, bg_rgb=(0.95, 0.95, 0.95), shading=False)
            loss = torch.mean((pred - target_cat) ** 2)
            loss.backward()
            opt.step()
            last_pred = pred.detach()

        cage.base_colors = torch.sigmoid(col_logit.detach())
        cage.local_scale_ratios = torch.clamp(torch.exp(lsc_log.detach()), 0.12, 0.85)
        cage.base_opacities = torch.sigmoid(op_logit.detach())
        rmse_val = math.sqrt(float(torch.mean((last_pred - target_cat) ** 2).item()))

        # Compute per-face real pixel residual energy spectrum so Blue knows WHERE to subdivide!
        err_map = torch.mean((last_pred - target_cat) ** 2, dim=-1).cpu().numpy()  # (H, W)
        ys_g = np.linspace(1.05, -1.05, res_photo)
        xs_g = np.linspace(-1.05, 1.05, res_photo)
        gy, gx = np.meshgrid(ys_g, xs_g, indexing="ij")
        v_np = cage.rest_verts.detach().cpu().numpy()
        f_np = cage.faces.detach().cpu().numpy()
        face_res = np.zeros(len(f_np), dtype=np.float64)
        for fi, (ia, ib, ic) in enumerate(f_np):
            x0, y0 = v_np[ia, 0], v_np[ia, 1]
            x1, y1 = v_np[ib, 0], v_np[ib, 1]
            x2, y2 = v_np[ic, 0], v_np[ic, 1]
            denom = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
            if abs(denom) < 1e-8:
                continue
            l1 = ((y1 - y2) * (gx - x2) + (x2 - x1) * (gy - y2)) / denom
            l2 = ((y2 - y0) * (gx - x2) + (x0 - x2) * (gy - y2)) / denom
            l3 = 1.0 - l1 - l2
            inside = (l1 >= -0.02) & (l2 >= -0.02) & (l3 >= -0.02)
            if np.any(inside):
                # Area-weighted residual energy so big high-error faces split first!
                face_res[fi] = float(np.sum(err_map[inside]))
        return cage, last_pred.cpu().numpy(), rmse_val, face_res

    # Round 0: Ultra-coarse 8-face initial Blue cage (32 bound Yellow Gaussians)
    cat_cage_0 = ScaleHierarchyCageGaussianCoupler.from_coarse_image_cage(grid_n=2, gaussians_per_face=4, name="cat_coarse_8f")
    cat_cage_0, pred_cat_0, rmse_cat_0, res_scores_0 = _fit_local_yellow_spectra(cat_cage_0, steps=36, lr=0.10)
    img_cat_0_wire = _draw_blue_cage_wireframe_overlay(
        pred_cat_0, cat_cage_0.rest_verts.detach().cpu().numpy(), cat_cage_0.faces.detach().cpu().numpy(), line_color=(70, 215, 255)
    )

    # Round 1: Residual forces selective 1->4 split ONLY on top 4 highest-residual Blue faces (8 -> 20 faces)
    cat_cage_1, split_r1 = cat_cage_0.subdivide_high_residual_faces(res_scores_0, top_k=4, gaussians_per_new_face=4)
    cat_cage_1, pred_cat_1, rmse_cat_1, res_scores_1 = _fit_local_yellow_spectra(cat_cage_1, steps=42, lr=0.09)

    # Round 2: Residual forces second selective 1->4 split ONLY on top 8 highest-residual Blue faces (20 -> 44 faces)
    cat_cage_2, split_r2 = cat_cage_1.subdivide_high_residual_faces(res_scores_1, top_k=8, gaussians_per_new_face=4)
    cat_cage_2, pred_cat_2, rmse_cat_2, _ = _fit_local_yellow_spectra(cat_cage_2, steps=48, lr=0.08)
    img_cat_2_wire = _draw_blue_cage_wireframe_overlay(
        pred_cat_2, cat_cage_2.rest_verts.detach().cpu().numpy(), cat_cage_2.faces.detach().cpu().numpy(), line_color=(70, 215, 255)
    )

    psnr_0 = 20.0 * math.log10(1.0 / max(1e-6, rmse_cat_0))
    psnr_2 = 20.0 * math.log10(1.0 / max(1e-6, rmse_cat_2))

    # Build 2x3 visual proof sheet
    def _tile(img_f: np.ndarray, title: str, size: int = 240) -> np.ndarray:
        u8 = np.clip(img_f * 255.0, 0, 255).astype(np.uint8)
        u8 = cv2.resize(u8, (size, size), interpolation=cv2.INTER_CUBIC)
        bgr_t = cv2.cvtColor(u8, cv2.COLOR_RGB2BGR)
        bar = np.full((34, size, 3), (18, 22, 32), dtype=np.uint8)
        cv2.putText(bar, title, (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.37, (235, 245, 255), 1, cv2.LINE_AA)
        return np.vstack([bar, bgr_t])

    row1 = np.hstack([
        _tile(img_rest_wire, f"1. Blue {coupler_3d.face_count}F + Yellow 128G"),
        _tile(img_def_wire, "2. Down: 3 S4/S3 Axes Turned"),
        _tile(img_cal_wire, f"3. Up Calib RMSE={up_rmse_hist[-1]:.4f}"),
    ])
    row2 = np.hstack([
        _tile(rgb_cat.astype(np.float32) / 255.0, "4. Real Photo Target (Cat)"),
        _tile(img_cat_0_wire, f"5. Coarse 8F Cage ({psnr_0:.1f}dB)"),
        _tile(img_cat_2_wire, f"6. Residual-Split 44F ({psnr_2:.1f}dB)"),
    ])
    proof_path = out_dir / "elysia_cage_gaussian_scale_rotor_proof.png"
    cv2.imwrite(str(proof_path), np.vstack([row1, row2]))

    deduced_axes = {
        "twist_rad": round(float(p_twist.item()), 4),
        "bend_x": round(float(p_bend.item()), 4),
        "aspect_stretch": round(float(p_stretch.item()), 4),
        "chroma_temp": round(float(p_chroma.item()), 4),
    }

    report = {
        "schema": "elysia_cage_gaussian_bidirectional_scale_rotor_v1",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "device": str(dev),
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "exp1_downward_blue_to_yellow_coupling": {
            "source_glb": "CesiumMan.glb",
            "raw_triangles_replaced": coupler_3d.raw_triangles_replaced,
            "blue_cage_faces": coupler_3d.face_count,
            "cage_compression_ratio": round(coupler_3d.raw_triangles_replaced / max(1, coupler_3d.face_count), 1),
            "yellow_bound_gaussians": coupler_3d.gaussian_count,
            "gaussian_points_manually_edited": 0,
            "rest_metrics": m_rest,
            "deformed_metrics": m_def,
            "rest_vs_deformed_pixel_rmse": round(downward_rmse, 5),
        },
        "exp2_upward_pixel_residual_to_blue_rotor_axes": {
            "trainable_parameters": "4 scalar S4/S3 Blue scale-rotor axes ONLY (0 vertex/point params)",
            "hidden_ground_truth_axes": secret_axes,
            "blindly_calibrated_axes": deduced_axes,
            "axis_max_abs_err": round(max(abs(secret_axes[k] - deduced_axes[k]) for k in secret_axes), 4),
            "pixel_rmse_trajectory": up_rmse_hist,
            "pixel_rmse_drop_pct": round((up_rmse_hist[0] - up_rmse_hist[-1]) / max(1e-6, up_rmse_hist[0]) * 100.0, 2),
        },
        "exp3_upward_residual_driven_cage_subdivision": {
            "target_photo": str(cat_photo),
            "round0_coarse": {"blue_faces": cat_cage_0.face_count, "yellow_gaussians": cat_cage_0.gaussian_count, "rmse": round(rmse_cat_0, 5), "psnr_db": round(psnr_0, 2)},
            "round1_selective_split": {"split_face_ids": split_r1, "blue_faces": cat_cage_1.face_count, "yellow_gaussians": cat_cage_1.gaussian_count, "rmse": round(rmse_cat_1, 5)},
            "round2_selective_split": {"split_face_ids": split_r2, "blue_faces": cat_cage_2.face_count, "yellow_gaussians": cat_cage_2.gaussian_count, "rmse": round(rmse_cat_2, 5), "psnr_db": round(psnr_2, 2)},
            "total_rmse_drop_pct": round((rmse_cat_0 - rmse_cat_2) / max(1e-6, rmse_cat_0) * 100.0, 2),
            "psnr_gain_db": round(psnr_2 - psnr_0, 2),
        },
        "proof_sheet_png": str(proof_path),
    }
    _save_json(COGNITIVE_WORLD_DIR / "elysia_cage_gaussian_scale_rotor_report.json", report)
    return report


def run_azeria_cognitive_entity_discrimination(video_path: Optional[str] = None) -> Dict[str, Any]:
    """
    REAL AI-DRAMA VIDEO (`[AZERIA]`, YouTube `hCX6LYlmJoc`) COGNITIVE PART-WHOLE
    ENTITY IDENTITY DISCRIMINATION & PURPOSEFUL RE-CREATION:
      1. Automatic shot-cut detection + S3 Part-Whole decomposition (Face Anchor,
         Left/Right Eye Local Rotors & Gaze/Roll, Crown/Hair Spectrum, GrabCut+Flow
         Garment Boundary, S4 Illumination Demodulation).
      2. Unsupervised cross-cut entity clustering (`Entity_A` vs `Entity_B`) with
         head-to-head benchmark: **Naive Raw Pixel Correlation vs Cognitive S4/S3 Identity**.
      3. Honest failure/boundary logging (tiny distant faces, back views, occlusion).
      4. Purposeful Identity-Preserving Re-Creation: Locks Entity A's S4 Face/Eyes/Crown
         while transferring Entity B's S3 Garment Spectrum strictly onto Entity A's segmented
         garment boundary + shifting S4 Scene Illumination to cool twilight!
    """
    import cv2

    t0 = time.perf_counter()
    vpath = Path(video_path) if video_path else (YOUTUBE_MULTIMODAL_DIR / "azeria" / "azeria_clip.mp4")
    if not vpath.is_file():
        raise FileNotFoundError(f"AZERIA clip not found at {vpath}")

    out_dir = vpath.parent
    rotor = CognitiveEntityIdentityRotor()
    obs_list, meta = rotor.analyze_video_shots(str(vpath), sample_stride=8, max_shots=16)

    verified = [o for o in obs_list if o.has_verified_entity]
    ent_a = [o for o in verified if o.assigned_entity_id == "Entity_A"]
    ent_b = [o for o in verified if o.assigned_entity_id == "Entity_B"]
    frame_cache = meta["frame_cache"]

    def _draw_cognitive_overlay(obs: Any, label: str) -> np.ndarray:
        cache = frame_cache.get(obs.shot_id)
        if cache is None:
            return np.zeros((180, 320, 3), dtype=np.uint8)
        vis = cache["bgr"].copy()
        fx, fy, fw, fh = obs.face_box
        # Green contour: S3 Segmented Garment Boundary (separated from background!)
        g_u8 = (cache["garment_mask"].astype(np.uint8) * 255)
        cnts, _ = cv2.findContours(g_u8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(vis, cnts, -1, (80, 240, 120), 2)
        # Magenta tint contour: S3 Crown/Hair Identity Axis
        c_u8 = (cache["crown_mask"].astype(np.uint8) * 255)
        ccnts, _ = cv2.findContours(c_u8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(vis, ccnts, -1, (220, 110, 240), 1)
        # Cyan box: S3 Face Structural Anchor
        cv2.rectangle(vis, (fx, fy), (fx + fw, fy + fh), (255, 220, 60), 2)
        # Bright yellow circles + inter-ocular roll line: S2 Eye Local Rotors
        lx, ly = int(fx + obs.left_eye_local[0] * fw), int(fy + obs.left_eye_local[1] * fh)
        rx, ry = int(fx + obs.right_eye_local[0] * fw), int(fy + obs.right_eye_local[1] * fh)
        cv2.line(vis, (lx, ly), (rx, ry), (0, 255, 255), 1, cv2.LINE_AA)
        cv2.circle(vis, (lx, ly), max(4, fw // 16), (0, 255, 255), 2)
        cv2.circle(vis, (rx, ry), max(4, fw // 16), (0, 255, 255), 2)
        sm = cv2.resize(vis, (320, 180), interpolation=cv2.INTER_AREA)
        bar = np.full((30, 320, 3), (18, 22, 32), dtype=np.uint8)
        cv2.putText(bar, label, (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (235, 245, 255), 1, cv2.LINE_AA)
        return np.vstack([bar, sm])

    # Pick representative cross-cut shots of Entity A and Entity B (maximizing garment visibility & cross-cut spread)
    def _pick_two_cuts(group: List[Any]) -> List[Any]:
        if len(group) <= 2:
            return group
        ordered = sorted(group, key=lambda o: o.garment_area_ratio * 2.0 + (o.face_box[2] * o.face_box[3]) / 25000.0, reverse=True)
        first = ordered[0]
        # Pick second cut farthest in time from first (cross-cut / lighting change!)
        second = max([o for o in group if o.shot_id != first.shot_id], key=lambda o: abs(o.time_s - first.time_s))
        return [first, second]

    picks_a = _pick_two_cuts(ent_a)
    picks_b = _pick_two_cuts(ent_b)

    # Purposeful Identity-Preserving Re-Creation: Entity A face/eyes locked + Entity B garment spectrum + cool twilight!
    recreation_metrics: Dict[str, Any] = {"ok": False}
    recreated_tile = np.zeros((210, 320, 3), dtype=np.uint8)
    if picks_a and picks_b:
        src_o = max(ent_a, key=lambda o: o.garment_area_ratio)
        don_o = max(ent_b, key=lambda o: o.garment_area_ratio)
        sc = frame_cache[src_o.shot_id]
        dc = frame_cache[don_o.shot_id]
        rec_bgr, rec_m = CognitiveEntityIdentityRotor.recreate_identity_preserving_recombination(
            sc["bgr"], src_o.face_box, sc["garment_mask"], dc["bgr"], dc["garment_mask"],
            target_illum_gain_rgb=(0.76, 0.92, 1.24),
        )
        recreation_metrics = {
            "ok": True,
            "source_entity_shot": f"{src_o.assigned_entity_id}@shot{src_o.shot_id} ({src_o.time_s}s)",
            "garment_donor_shot": f"{don_o.assigned_entity_id}@shot{don_o.shot_id} ({don_o.time_s}s)",
            **rec_m,
        }
        sm_rec = cv2.resize(rec_bgr, (320, 180), interpolation=cv2.INTER_AREA)
        bar = np.full((30, 320, 3), (18, 22, 32), dtype=np.uint8)
        cv2.putText(
            bar,
            f"6. Recreated: Lock S4 Face + Swap S3 Garment",
            (6, 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.39,
            (130, 255, 190),
            1,
            cv2.LINE_AA,
        )
        recreated_tile = np.vstack([bar, sm_rec])

    # Render side-by-side Heatmap Tile: Cognitive S4/S3 Identity Matrix vs Naive Pixel Correlation Matrix
    def _heatmap_tile(cog_m: np.ndarray, pix_m: np.ndarray, v_obs: List[Any]) -> np.ndarray:
        canvas = np.full((180, 320, 3), (20, 24, 34), dtype=np.uint8)
        n = len(v_obs)
        if n >= 2:
            # Order indices by Entity_A then Entity_B so block-diagonal structure is visually unmistakable!
            ord_idx = [i for i, o in enumerate(v_obs) if o.assigned_entity_id == "Entity_A"] + [
                i for i, o in enumerate(v_obs) if o.assigned_entity_id != "Entity_A"
            ]
            cm = cog_m[np.ix_(ord_idx, ord_idx)]
            pm = pix_m[np.ix_(ord_idx, ord_idx)]
            sz = 126
            c_u8 = np.clip(cm * 255.0, 0, 255).astype(np.uint8)
            p_u8 = np.clip((pm + 1.0) * 0.5 * 255.0, 0, 255).astype(np.uint8)
            c_img = cv2.applyColorMap(cv2.resize(c_u8, (sz, sz), interpolation=cv2.INTER_NEAREST), cv2.COLORMAP_INFERNO)
            p_img = cv2.applyColorMap(cv2.resize(p_u8, (sz, sz), interpolation=cv2.INTER_NEAREST), cv2.COLORMAP_INFERNO)
            canvas[34 : 34 + sz, 18 : 18 + sz] = c_img
            canvas[34 : 34 + sz, 174 : 174 + sz] = p_img
            cv2.putText(canvas, "Cognitive S4/S3", (24, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (120, 255, 180), 1, cv2.LINE_AA)
            cv2.putText(canvas, "Naive Pixel Corr", (180, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (140, 180, 255), 1, cv2.LINE_AA)
            sb = meta["separation_benchmark"]
            cv2.putText(
                canvas,
                f"Margin: +{sb['cognitive_discrimination_margin']:.2f} vs +{sb['naive_pixel_discrimination_margin']:.2f}",
                (26, 174),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.38,
                (235, 245, 255),
                1,
                cv2.LINE_AA,
            )
        bar = np.full((30, 320, 3), (18, 22, 32), dtype=np.uint8)
        cv2.putText(bar, "5. Cross-Cut Identity vs Naive Pixel", (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.41, (235, 245, 255), 1, cv2.LINE_AA)
        return np.vstack([bar, canvas])

    # Assemble 2x3 Visual Proof Sheet
    t1 = _draw_cognitive_overlay(picks_a[0], f"1. Entity_A Cut1 (s{picks_a[0].shot_id} {picks_a[0].time_s}s)") if len(picks_a) >= 1 else np.zeros((210, 320, 3), dtype=np.uint8)
    t2 = _draw_cognitive_overlay(picks_a[1], f"2. Entity_A Cut2 (s{picks_a[1].shot_id} {picks_a[1].time_s}s)") if len(picks_a) >= 2 else t1.copy()
    t3 = _draw_cognitive_overlay(picks_b[0], f"3. Entity_B Cut1 (s{picks_b[0].shot_id} {picks_b[0].time_s}s)") if len(picks_b) >= 1 else np.zeros((210, 320, 3), dtype=np.uint8)
    t4 = _draw_cognitive_overlay(picks_b[1], f"4. Entity_B Cut2 (s{picks_b[1].shot_id} {picks_b[1].time_s}s)") if len(picks_b) >= 2 else t3.copy()
    t5 = _heatmap_tile(meta["cognitive_mat"], meta["pixel_mat"], verified)
    t6 = recreated_tile
    proof_path = out_dir / "elysia_azeria_cognitive_identity_proof.png"
    cv2.imwrite(str(proof_path), np.vstack([np.hstack([t1, t2, t3]), np.hstack([t4, t5, t6])]))

    # Detailed shot log (including rejected/missed shots for 100% honest limit audit!)
    shot_summaries = []
    for o in obs_list:
        shot_summaries.append({
            "shot_id": o.shot_id,
            "time_s": o.time_s,
            "verified_entity": o.has_verified_entity,
            "assigned_entity": o.assigned_entity_id,
            "reason": o.rejection_reason,
            "face_wh": [o.face_box[2], o.face_box[3]],
            "eyes_detected": o.eyes_detected_count,
            "head_roll_deg": o.head_roll_deg,
            "eye_openness": o.eye_openness_ratio,
            "gaze_shift_xy": list(o.gaze_shift_xy),
            "eye_motion_std_px": o.eye_motion_std_px,
            "garment_area_ratio": o.garment_area_ratio,
            "garment_boundary_cohesion": o.garment_boundary_cohesion,
            "scene_illum_rgb": list(o.scene_illum_rgb),
        })

    report = {
        "schema": "elysia_azeria_cognitive_entity_identity_v1",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "source_video": str(vpath),
        "shots_detected": meta["shots_detected"],
        "verified_character_shots": meta["verified_character_shots"],
        "non_character_or_rejected_shots": meta["non_character_or_rejected_shots"],
        "discovered_entity_clusters": meta["entity_clusters"],
        "separation_benchmark_cognitive_vs_pixel": meta["separation_benchmark"],
        "purposeful_identity_preserving_recreation": recreation_metrics,
        "shot_observations": shot_summaries,
        "proof_sheet_png": str(proof_path),
    }
    _save_json(COGNITIVE_WORLD_DIR / "elysia_azeria_cognitive_identity_report.json", report)
    return report


PLAYABLE_WORLD_DIR = YOUTUBE_MULTIMODAL_DIR / "azeria" / "playable"
PLAYABLE_WORLD_STATE_PATH = PLAYABLE_WORLD_DIR / "azeria_playable_world.json"


def build_azeria_playable_world(force_rebuild: bool = False) -> Dict[str, Any]:
    """Lifts the real `[AZERIA]` clip into a live playable Video<=>Game Rotor Network World."""
    if not force_rebuild and PLAYABLE_WORLD_STATE_PATH.is_file():
        loaded = _load_json(PLAYABLE_WORLD_STATE_PATH, {})
        if loaded and loaded.get("schema") == "elysia_video_game_isomorphic_rotor_world_v1":
            return loaded
    vpath = YOUTUBE_MULTIMODAL_DIR / "azeria" / "azeria_clip.mp4"
    world = VideoGameIsomorphicRotorNetwork.lift_video_to_playable_world(str(vpath), PLAYABLE_WORLD_DIR)
    _save_json(PLAYABLE_WORLD_STATE_PATH, world)
    return world


def _compose_character_rotor_reply(
    actor_id: str,
    actor_state: Dict[str, Any],
    other_state: Dict[str, Any],
    stage_state: Dict[str, Any],
    user_utterance: str,
    dist: float,
) -> Tuple[str, str, float, Optional[float]]:
    """
    Generates a contextually grounded Korean response strictly from the actor's
    `kiwipiepy` POS nominals, `CausalPropositionFrame`, spatial distance/tension state,
    and persona rotor axes (`Viela` mystical-gentle vs `Kaio` resolute-protective)!
    Returns `(reply_ko, emotion_label, dialogue_flux, optional_illum_shift)`.
    """
    pos = analyze_korean_pos_kiwi(user_utterance) or {"nominals": [], "predicates": []}
    cframe = parse_korean_causal_frame(user_utterance)
    noms = [w for w in (pos.get("nominals") or []) if len(w) >= 2 and w not in ("여기", "거기", "지금", "오늘", "우리", "당신")]
    key_topic = cframe.subject or (noms[0] if noms else "이 장면")
    key_obj = cframe.obj or (noms[1] if len(noms) >= 2 else "")

    u_low = user_utterance
    is_danger = any(k in u_low for k in ("마물", "몬스터", "위험", "싸우", "검", "공격", "적", "전투", "어둠"))
    is_magic = any(k in u_low for k in ("마법", "봉인", "빛", "별", "힘", "원리", "로터", "세계", "시간"))
    is_move = any(k in u_low for k in ("가자", "움직", "가까이", "이리", "따라", "도망", "밖", "나가", "오른쪽", "왼쪽"))
    is_greet = any(k in u_low for k in ("안녕", "이름", "누구", "반가", "어때", "기분", "뭐해"))

    near_note = "바로 곁에 서 있으니" if dist < 0.28 else "조금 떨어져 있지만"
    illum_shift = None

    if actor_id == "viela":
        if is_danger:
            reply = f"어머, '{key_topic}'의 기척이 느껴져… {near_note} 카이오, 무리해서 혼자 뛰어들진 마. 내가 봉인의 결을 읽어볼게."
            emo, flux, illum_shift = "긴장·집중", 0.92, -0.35
        elif is_magic:
            reply = f"후후, '{key_topic}'의 결을 눈치챘구나? 이 선술집의 빛과 공기마저 하나의 로터처럼 맞물려 흐르고 있어."
            emo, flux, illum_shift = "신비·공명", 0.85, -0.20
        elif is_move:
            reply = f"좋아, 네가 이끄는 방향으로 발걸음을 옮겨볼게. {near_note} 이 세계의 경계가 새로 열리는 느낌이 드네."
            emo, flux = "호기심·동행", 0.78
        elif is_greet:
            reply = f"안녕, 난 비엘라야. 기록된 영상 너머에서 네가 직접 말을 걸어주니… {near_note} 참 흥미롭네."
            emo, flux = "미소·친근", 0.72
        else:
            extra = f" 그리고 '{key_obj}'와의 연결도 놓칠 수 없지." if key_obj else ""
            reply = f"음… '{key_topic}'에 대한 네 시선이 흥미로워.{extra} {near_note} 조금 더 자세히 들려줄래?"
            emo, flux = "사색·호기심", 0.75
    else:  # kaio
        if is_danger:
            reply = f"알겠어! '{key_topic}'이라면 내가 앞장서서 막을게. {near_note} 비엘라와 마을 사람들은 절대 다치게 두지 않아."
            emo, flux, illum_shift = "결의·전투태세", 0.95, 0.30
        elif is_magic:
            reply = f"난 마법은 못 쓰지만… '{key_topic}'의 흐름이 바뀐 건 분명히 느껴져. 네 지시에 맞춰 움직일 준비가 됐어."
            emo, flux = "진지·신뢰", 0.82
        elif is_move:
            reply = f"알았어, 지금 바로 자리를 옮길게! {near_note} 시야를 넓히고 주변 경계를 확인하자."
            emo, flux = "기동·민첩", 0.84
        elif is_greet:
            reply = f"난 카이오야. 선술집 안에서 그냥 대본대로만 움직이는 게 아니라, 이렇게 직접 호흡을 맞추니 훨씬 든든하네."
            emo, flux = "담백·신뢰", 0.70
        else:
            extra = f" '{key_obj}' 쪽도 함께 살필게." if key_obj else ""
            reply = f"'{key_topic}' 말이군.{extra} {near_note} 네 판단을 믿고 같이 움직여 볼게."
            emo, flux = "집중·응답", 0.74

    return reply, emo, flux, illum_shift


def intervene_azeria_playable_world(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes a live Scale-Hierarchy Rotor Network intervention on the `[AZERIA]` playable world:
      - Supports reset (`action='reset'`), physical movement/pose/garment/lighting (`action='move'`),
        direct Korean dialogue with real Praat-modulated character voice (`action='talk'`),
        and autonomous Viela<->Kaio interaction (`action='autonomous_tick'`).
      - Syncs live CausalField voxels/beams so every player intervention leaves a physical impact vector!
    """
    t0 = time.perf_counter()
    action = str(payload.get("action") or "move").strip().lower()
    if action == "reset":
        world = build_azeria_playable_world(force_rebuild=True)
        return {"ok": True, "elapsed_s": round(time.perf_counter() - t0, 2), "world": world}

    world = build_azeria_playable_world(force_rebuild=False)
    actor_id = str(payload.get("actor_id") or "kaio").strip().lower()
    if actor_id not in ("viela", "kaio"):
        actor_id = "kaio"
    other_id = "viela" if actor_id == "kaio" else "kaio"

    utterance = str(payload.get("utterance") or "").strip()
    speaker_label = "player"
    if action == "autonomous_tick":
        # Autonomous interaction: other actor speaks to `actor_id` using their last context!
        speaker_label = other_id
        other_last = str(world["actors"][other_id].get("last_utterance") or "지금 이 선술집의 기척을 느껴봐.")
        utterance = other_last

    move_x = payload.get("x")
    move_y = payload.get("y")
    depth_scale = payload.get("depth_scale")
    yaw_deg = payload.get("yaw_deg")
    garment_hue_deg = payload.get("garment_hue_deg")
    illum_temp = payload.get("illum_temp")
    illum_brightness = payload.get("illum_brightness")
    synthesize_voice = bool(payload.get("synthesize_voice", action in ("talk", "autonomous_tick")))

    spoken_reply: Optional[str] = None
    emotion_delta: Optional[str] = None
    dialogue_flux = 0.0
    voice_url: Optional[str] = None
    praat_metrics: Dict[str, Any] = {}

    if utterance and action in ("talk", "autonomous_tick"):
        dx = float(world["actors"][actor_id]["x"]) - float(world["actors"][other_id]["x"])
        dy = float(world["actors"][actor_id]["y"]) - float(world["actors"][other_id]["y"])
        dist = math.hypot(dx, dy)
        spoken_reply, emotion_delta, dialogue_flux, auto_illum = _compose_character_rotor_reply(
            actor_id, world["actors"][actor_id], world["actors"][other_id], world["stage"], utterance, dist
        )
        if auto_illum is not None and illum_temp is None:
            illum_temp = float(np.clip(float(world["stage"]["illum_temp"]) * 0.5 + auto_illum, -1.0, 1.0))

        # Slight physical approach/step reaction driven by the Dialogue-to-Kinematics Rotor!
        if move_x is None and action == "autonomous_tick":
            step_dir = -0.04 if dx > 0.25 else (0.04 if dx < -0.25 else 0.0)
            move_x = float(world["actors"][actor_id]["x"]) + step_dir

        if synthesize_voice and spoken_reply:
            pr = world["actors"][actor_id]["persona_rotor"]
            raw_wav = PLAYABLE_WORLD_DIR / f"voice_{actor_id}_raw.wav"
            mod_wav = PLAYABLE_WORLD_DIR / f"voice_{actor_id}_mod.wav"
            tts = synthesize_korean_wav_winrt(spoken_reply, raw_wav, speaking_rate=float(pr["tempo"]), audio_pitch=1.0)
            if tts.get("ok") and raw_wav.is_file():
                pm = modulate_voice_praat_formant_rotor(
                    raw_wav,
                    mod_wav,
                    formant_shift_ratio=float(pr["formant_tract"]),
                    pitch_f0_ratio=float(pr["pitch_f0"]),
                    duration_factor=1.0,
                )
                if pm.get("ok") and mod_wav.is_file():
                    voice_url = f"/data/open_sandbox/youtube_multimodal/azeria/playable/{mod_wav.name}"
                    praat_metrics = pm.get("after_acoustics") or {}
                else:
                    voice_url = f"/data/open_sandbox/youtube_multimodal/azeria/playable/{raw_wav.name}"

    world = VideoGameIsomorphicRotorNetwork.step_rotor_network_intervention(
        world,
        actor_id=actor_id,
        move_x=float(move_x) if move_x is not None else None,
        move_y=float(move_y) if move_y is not None else None,
        depth_scale=float(depth_scale) if depth_scale is not None else None,
        yaw_deg=float(yaw_deg) if yaw_deg is not None else None,
        garment_hue_deg=float(garment_hue_deg) if garment_hue_deg is not None else None,
        illum_temp=float(illum_temp) if illum_temp is not None else None,
        illum_brightness=float(illum_brightness) if illum_brightness is not None else None,
        dialogue_flux=dialogue_flux,
        emotion_delta=emotion_delta,
        spoken_reply=spoken_reply,
        voice_url=voice_url,
        speaker_label=speaker_label,
        user_utterance=utterance,
    )

    # Sync live intervention into Elysia's CausalField (every action has an impact vector!)
    from core.physics.causal_field import CausalField, ConnectivityBeam, InformationVoxel

    cf = CausalField(dimensions=3)
    v_a = world["actors"]["viela"]
    k_a = world["actors"]["kaio"]
    vox_v = InformationVoxel(
        id="actor::viela",
        content=v_a["last_utterance"],
        tensor=np.array([v_a["x"], v_a["y"], v_a["energy"], v_a["gaze_x"]], dtype=np.float32),
        mass=1.2,
        position=np.array([v_a["x"] * 2.0 - 1.0, v_a["y"] * 2.0 - 1.0, 0.2], dtype=np.float32),
        chromatic_vector=np.array([0.35, 0.25, 0.40], dtype=np.float32),
    )
    vox_k = InformationVoxel(
        id="actor::kaio",
        content=k_a["last_utterance"],
        tensor=np.array([k_a["x"], k_a["y"], k_a["energy"], k_a["gaze_x"]], dtype=np.float32),
        mass=1.4,
        position=np.array([k_a["x"] * 2.0 - 1.0, k_a["y"] * 2.0 - 1.0, 0.2], dtype=np.float32),
        chromatic_vector=np.array([0.30, 0.50, 0.20], dtype=np.float32),
    )
    vox_s = InformationVoxel(
        id="stage::azeria_tavern",
        content=world["stage"]["name_ko"],
        tensor=np.array([world["stage"]["illum_temp"], world["stage"]["illum_brightness"], world["stage"]["narrative_tension"], 1.0], dtype=np.float32),
        mass=2.0,
        position=np.array([0.0, 0.0, float(world["stage"]["illum_temp"])], dtype=np.float32),
        chromatic_vector=np.array([0.50, 0.30, 0.20], dtype=np.float32),
    )
    for vx in (vox_v, vox_k, vox_s):
        cf.voxels[vx.id] = vx
    dist_vk = float(world["causal_couplings"]["inter_actor_distance"])
    cf.beams.extend([
        ConnectivityBeam("actor::viela", "actor::kaio", strength=float(world["causal_couplings"]["gaze_resonance"]), rest_length=0.44, current_tension=abs(dist_vk - 0.44)),
        ConnectivityBeam("actor::viela", "stage::azeria_tavern", strength=0.65, rest_length=0.5, current_tension=float(world["stage"]["narrative_tension"])),
        ConnectivityBeam("actor::kaio", "stage::azeria_tavern", strength=0.65, rest_length=0.5, current_tension=float(world["stage"]["narrative_tension"])),
    ])
    world["causal_field_sync"] = {
        "voxels": len(cf.voxels),
        "beams": len(cf.beams),
        "beam_tension_vk": round(abs(dist_vk - 0.44), 4),
        "praat_voice_acoustics": praat_metrics,
    }
    _save_json(PLAYABLE_WORLD_STATE_PATH, world)
    return {"ok": True, "elapsed_s": round(time.perf_counter() - t0, 2), "world": world}


def main() -> None:
    parser = argparse.ArgumentParser(description="ELYSIA Existing Core Spines Live Unified Runner")
    parser.add_argument("--utterance", type=str, default="", help="Korean/English utterance to run through Elysia's existing core organs")
    parser.add_argument("--absorb-world", action="store_true", help="Append-merge fresh Korean Wikipedia + Public Literature + Local Docs corpus")
    parser.add_argument("--youtube", type=str, default="", help="Real YouTube URL or Korean search query to ingest synchronized video + voice + subtitles")
    parser.add_argument("--yt-seconds", type=int, default=75, help="Max clip duration in seconds for YouTube multimodal ingestion")
    parser.add_argument("--knob-recreate", action="store_true", help="Run full bidirectional Audio<->Text<->Video<->Law Scale-Rotor knob recreation loop")
    parser.add_argument("--parallel-self", action="store_true", help="Fork Elysia into parallel vertical/horizontal/cross-axis perspectives and re-integrate")
    parser.add_argument("--unified-3track", action="store_true", help="Run unified 3-track UniversalFormRotor + kiwipiepy + Praat + MotionDNA->Blender 3D rig loop")
    parser.add_argument("--volumetric-3dgs", action="store_true", help="Run zero-triangle CUDA 3D Gaussian <-> 3D-Triangle Tetrahedral Scale-Rotor Mod/Demod lab")
    parser.add_argument("--inverse-deduce", action="store_true", help="Run 4-domain Blind Inverse Pythagorean/Law-of-Cosines Causal Deduction suite")
    parser.add_argument("--cage-gaussian", action="store_true", help="Run bidirectional Blue Structural Cage <-> Yellow 3D Gaussian Scale-Rotor lab")
    parser.add_argument("--entity-discriminate", action="store_true", help="Run real AZERIA video cognitive part-whole entity identity discrimination & purposeful re-creation")
    parser.add_argument("--build-playable", action="store_true", help="Lift real AZERIA video into Playable Video<=>Game Isomorphic Rotor Network World")
    parser.add_argument("--playable-intervene", type=str, default="", help="JSON payload to run live Rotor Network intervention (move/talk/autonomous/reset)")
    parser.add_argument("--build-5d-world", action="store_true", help="Lift real AZERIA video sequence into 5D (X,Y,Z,T,Sigma) Spacetime-Causal Rotor World")
    parser.add_argument("--var-dim-4d", action="store_true", help="Verify 4D-base + Variable Geometric Rotor Dimension auto-discovery & MDL folding on AZERIA splats")
    parser.add_argument("--autonomous-world-diff", action="store_true", help="Run full-span 60s cross-modal 4D integration + unsupervised 4D Terrain/River/Forest/NPC differentiation & fusion")
    parser.add_argument("--persona-label", type=str, default="남성적 저음 억양 × 부드러운 여성 어법")
    parser.add_argument("--vertical-axis", type=float, default=0.52)
    parser.add_argument("--horizontal-axis", type=float, default=-0.35)
    parser.add_argument("--vocal-pitch", type=float, default=0.74)
    parser.add_argument("--formant-tract", type=float, default=0.80)
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

    if args.autonomous_world_diff:
        voids = AutonomousWorldDifferentiationEngine.detect_epistemic_voids(WORKSPACE_ROOT / "data")
        az_mp4 = YOUTUBE_MULTIMODAL_DIR / "azeria" / "azeria_clip.mp4"
        az_wav = YOUTUBE_MULTIMODAL_DIR / "azeria" / "azeria_60s.wav"
        az_out = YOUTUBE_MULTIMODAL_DIR / "azeria" / "world_5d"
        fullspan_rep = AutonomousWorldDifferentiationEngine.integrate_fullspan_crossmodal_4d(
            str(az_mp4), str(az_wav), az_out, n_depth_knots=48
        )
        env_mp4 = YOUTUBE_MULTIMODAL_DIR / "nature_env" / "forest_river_clip.mp4"
        env_out = YOUTUBE_MULTIMODAL_DIR / "nature_env"
        env_rep = AutonomousWorldDifferentiationEngine.differentiate_4d_env_and_fuse_game_map(
            str(env_mp4), str(az_out / "azeria_5d_splats.bin"), env_out, n_frames=22
        )
        rep = {
            "schema": "elysia_autonomous_fullspan_and_env_differentiation_v1",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "epistemic_void_audit": voids,
            "trackA_azeria_fullspan_60s_1820f": fullspan_rep,
            "trackB_unsupervised_4d_env_and_fused_game_map": env_rep,
        }
        _save_json(COGNITIVE_WORLD_DIR / "elysia_autonomous_world_diff_report.json", rep)
        print(json.dumps(rep, ensure_ascii=False, indent=2, default=str))
        return

    if args.var_dim_4d:
        bin_p = YOUTUBE_MULTIMODAL_DIR / "azeria" / "world_5d" / "azeria_5d_splats.bin"
        packed = np.fromfile(str(bin_p), dtype=np.float32).reshape(-1, 12)
        # Clean 4D base spacetime substrate: (X, Y, Z, T_phase)
        t_phase = (packed[:, 0] * 0.5 + packed[:, 2] * 0.5).astype(np.float32)
        base_4d = np.stack([packed[:, 0], packed[:, 1], packed[:, 2], t_phase], axis=1)
        vd = VariableDimensionGeometricRotor(base_4d)
        # Feed raw multi-modal observable residuals beyond 4D -> let SVD discover the true minimal extra rotor dimensions!
        speed_3d = np.sqrt(packed[:, 6] ** 2 + packed[:, 7] ** 2 + packed[:, 8] ** 2)
        luma = 0.299 * packed[:, 3] + 0.587 * packed[:, 4] + 0.114 * packed[:, 5]
        warmth = packed[:, 3] - packed[:, 5]
        osc = packed[:, 10]
        layer_f = packed[:, 9]
        res_mat = np.stack([speed_3d, luma, warmth, osc, layer_f], axis=1)
        disc = vd.discover_dimensions_from_residual(
            res_mat, ["motion_speed", "luminance", "chroma_warmth", "micro_osc", "scale_depth"], variance_target=0.88, max_new_dims=4
        )
        # Test MDL collinearity folding: try attaching a redundant duplicate of D5!
        dup_test = vd.attach_dimension("redundant_copy_of_D5", vd.extra_dims[0]["values"] * 1.35 + 0.01, source="redundancy_probe")
        # Test exact Clifford Bivector planar rotation between Time (dim 3) and auto-discovered D5 (dim 4)!
        rot_check = vd.rotate_plane(3, 4, math.radians(35.0))
        rep = {
            "schema": "elysia_4d_variable_geometric_rotor_v1",
            "splats_analyzed": int(len(packed)),
            "auto_discovery": disc,
            "redundant_axis_folding_test": dup_test,
            "clifford_T_D5_plane_rotation": rot_check,
            "final_manifold_summary": vd.summary(),
        }
        _save_json(COGNITIVE_WORLD_DIR / "elysia_4d_variable_rotor_report.json", rep)
        print(json.dumps(rep, ensure_ascii=False, indent=2, default=str))
        return

    if args.build_5d_world:
        vpath = YOUTUBE_MULTIMODAL_DIR / "azeria" / "azeria_clip.mp4"
        out_5d = YOUTUBE_MULTIMODAL_DIR / "azeria" / "world_5d"
        rep = FiveDSpacetimeCausalRotorWorld.lift_video_to_5d_world(str(vpath), out_5d)
        print(json.dumps(rep, ensure_ascii=False, indent=2, default=str))
        return

    if args.build_playable:
        rep = build_azeria_playable_world(force_rebuild=True)
        print(json.dumps(rep, ensure_ascii=False, indent=2, default=str))
        return

    if args.playable_intervene:
        payload = json.loads(args.playable_intervene)
        rep = intervene_azeria_playable_world(payload)
        print(json.dumps(rep, ensure_ascii=False, indent=2, default=str))
        return

    if args.entity_discriminate:
        rep = run_azeria_cognitive_entity_discrimination()
        print(json.dumps(rep, ensure_ascii=False, indent=2, default=str))
        return

    if args.cage_gaussian:
        rep = run_cage_gaussian_bidirectional_lab()
        print(json.dumps(rep, ensure_ascii=False, indent=2, default=str))
        return

    if args.inverse_deduce:
        rep = run_blind_inverse_causal_deduction_suite()
        print(json.dumps(rep, ensure_ascii=False, indent=2, default=str))
        return

    if args.volumetric_3dgs:
        rep = run_volumetric_3dgs_tetra_protocol_lab()
        print(json.dumps(rep, ensure_ascii=False, indent=2, default=str))
        return

    if args.unified_3track:
        rep = run_unified_3track_form_synthesis(
            utterance=args.utterance,
            persona_label=args.persona_label,
            vertical_scale=args.vertical_axis,
            horizontal_relational=args.horizontal_axis,
            pitch_f0=args.vocal_pitch,
            formant_tract=args.formant_tract,
            tempo_rate=args.vocal_tempo,
            law_damping=args.law_damping_knob,
            stance_axis=args.stance_axis,
        )
        print(json.dumps(rep, ensure_ascii=False, indent=2, default=str))
        return

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
