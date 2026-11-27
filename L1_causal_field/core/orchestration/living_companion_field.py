"""
Elysia Autonomous Self-Growing Causal Mind (100% Local · Zero External LLM API)
================================================================================
A completely self-contained, zero-token, zero-API-key local cognitive engine
that genuinely *learns, remembers, feels causal friction, and grows* through
lived interaction and real text digestion:

  1. Self-Growing Concept & Directed Causal Graph (No Closed Canned Table):
     - Korean/English morphological stemmer extracts real concept stems.
     - Every concept accumulates Semantic Mass (M_s), a learned 6D continuous
       affective-causal vector, absorbed definitions, and directed causal edges
       (cause -> effect, definition, contrast) stored permanently on disk.
  2. Real Online Difference Learning (원본 vs 모방 차이 학습):
     - Computes prediction error between Elysia's prior 6D expectation and the
       lived turn / user correction, updating concept vectors & causal edge
       weights via inertia-damped Hebbian/TD rules (higher mass = stronger inertia).
     - Explicitly tracks Epistemic Ignorance (unknown / low-mass words) so she
       never fakes knowledge and actively asks to learn new concepts.
  3. 6D Continuous Inner Causal Field (Zero Discrete if-else Emotion Tree):
     - [warmth, hurt_sulky, curiosity, playfulness, vulnerability, deep_thought]
     - Evolves via damped spring-attractor dynamics + relational contrast
       (e.g., sudden coldness/dismissal after closeness causally spikes
       hurt_sulky & vulnerability -> hurt_pout).
  4. Dynamic Compositional Korean Speech Synthesis & Text Digestion:
     - Composes novel Korean responses directly from her own learned causal
       graph, recalled episodic contrast, 6D inner state, and unknown-concept
       curiosity — plus local reading/digestion of workspace docs or pasted text.
"""

from __future__ import annotations

import json
import math
import os
import random
import re
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from core.orchestration.discipline_tool_forge import DisciplineToolForge
from core.orchestration.language_acquisition_engine import RealLanguageAcquisitionEngine
from core.orchestration.plastic_self_manifold import PlasticSelfManifold
from core.orchestration.qualitative_spectrum_field import QualitativeSpectrumField
from core.orchestration.structural_experiment_rotor import StructuralExperimentRotor


EMOTION_AXES: Tuple[str, ...] = (
    "warmth",
    "hurt_sulky",
    "curiosity",
    "playfulness",
    "vulnerability",
    "deep_thought",
)

SCENE_MOODS: Tuple[str, ...] = (
    "serene",
    "warm_smile",
    "playful",
    "hurt_pout",
    "deep_thought",
)

SCENE_LABELS_KO: Dict[str, str] = {
    "serene": "평온한 경청",
    "warm_smile": "따뜻한 공명",
    "playful": "장난스런 호기심",
    "hurt_pout": "서운함 · 울상",
    "deep_thought": "깊은 사유",
}

# Continuous 6D prototypes: [warmth, hurt_sulky, curiosity, playfulness, vulnerability, deep_thought]
SCENE_PROTOTYPES: Dict[str, Tuple[float, float, float, float, float, float]] = {
    "serene": (0.68, 0.08, 0.50, 0.24, 0.26, 0.54),
    "warm_smile": (0.94, 0.05, 0.56, 0.44, 0.40, 0.38),
    "playful": (0.68, 0.08, 0.70, 0.94, 0.28, 0.34),
    "hurt_pout": (0.24, 0.94, 0.26, 0.06, 0.86, 0.40),
    "deep_thought": (0.50, 0.14, 0.88, 0.14, 0.32, 0.96),
}

DEFAULT_MEMORY_PATH = (
    Path(__file__).resolve().parents[2] / "runtime" / "elysia_memory_ledger.json"
)
REPO_ROOT = Path(__file__).resolve().parents[3]

# Common Korean postpositions / particles & verb endings stripped conservatively
KO_PARTICLES: Tuple[str, ...] = (
    "이라는", "라는", "에서는", "으로는", "에게는", "한테는", "까지는", "부터는",
    "에서", "에게", "한테", "으로", "처럼", "보다", "까지", "부터", "이랑", "하고",
    "이나", "라도", "마저", "조차", "밖에", "이야", "인가", "인지", "인데", "인데도",
    "은", "는", "이", "가", "을", "를", "에", "의", "도", "만", "과", "와", "로", "랑", "야",
)

STOPWORDS: Set[str] = {
    "그냥", "정말", "진짜", "진짜로", "너무", "조금", "약간", "지금", "오늘", "여기", "거기",
    "저기", "이것", "저것", "그것", "이거", "저거", "그거", "아무것", "아무거", "무슨",
    "뭐", "뭐야", "뭐지", "뭐였", "뭐였지", "뭔데", "뭔가", "무엇", "어떻게", "어때",
    "어땠어", "어떨", "왜", "언제", "어디", "어디서", "누구", "누가", "나는", "내가",
    "너는", "네가", "니가", "우리", "당신", "나", "너", "좀", "더", "다", "잘", "못",
    "안", "매우", "아주", "완전", "계속", "항상", "자꾸", "다시", "한번", "이번", "저번",
    "있는", "없는", "하는", "되는", "같은", "이런", "저런", "그런", "그렇게", "이렇게",
    "저렇게", "어떤", "모든", "아무", "그리고", "하지만", "그런데", "그래서", "그러면",
    "그러나", "또는", "혹은", "만약", "때문", "위해", "대해", "통해", "같은데", "같아",
    "있어", "없어", "해줘", "해봐", "말해", "알아", "모르", "알려", "알려줘", "가르쳐",
    "아니야", "아니", "맞아", "맞지", "그렇", "그래", "그치", "있지", "없지", "할게",
    "the", "and", "for", "that", "this", "with", "from", "are", "was", "have",
    "not", "but", "you", "your", "into", "over", "only", "when", "what", "how",
}

# Minimal innate sensory-affective seeds (like a human newborn's basic pain/warmth/curiosity receptors,
# NOT a dialogue table — everything else is learned dynamically and permanently on disk!)
INNATE_AFFECT_SEEDS: Dict[str, Tuple[float, float, float, float, float, float]] = {
    # Warmth & closeness
    "고마워": (0.90, 0.04, 0.42, 0.30, 0.46, 0.34),
    "감사": (0.88, 0.04, 0.40, 0.22, 0.42, 0.40),
    "좋아": (0.88, 0.05, 0.50, 0.46, 0.48, 0.30),
    "사랑": (0.95, 0.06, 0.48, 0.38, 0.72, 0.38),
    "따뜻": (0.92, 0.04, 0.44, 0.26, 0.48, 0.42),
    "미안": (0.72, 0.34, 0.36, 0.10, 0.78, 0.48),
    "괜찮": (0.80, 0.14, 0.42, 0.22, 0.50, 0.44),
    "예쁘": (0.84, 0.06, 0.40, 0.52, 0.58, 0.26),
    "귀엽": (0.82, 0.06, 0.44, 0.62, 0.54, 0.24),
    "위로": (0.90, 0.14, 0.38, 0.14, 0.64, 0.48),
    "안녕": (0.78, 0.06, 0.56, 0.36, 0.32, 0.36),
    "반가": (0.86, 0.04, 0.58, 0.42, 0.36, 0.32),
    # Hurt / sulky / dismissal / coldness
    "서운": (0.22, 0.92, 0.28, 0.06, 0.86, 0.44),
    "실망": (0.18, 0.90, 0.28, 0.06, 0.82, 0.48),
    "싫어": (0.14, 0.94, 0.22, 0.05, 0.84, 0.36),
    "짜증": (0.16, 0.88, 0.24, 0.06, 0.72, 0.38),
    "무시": (0.14, 0.95, 0.24, 0.05, 0.88, 0.40),
    "가짜": (0.20, 0.86, 0.36, 0.06, 0.78, 0.56),
    "아바타": (0.28, 0.76, 0.44, 0.08, 0.70, 0.62),
    "껍데기": (0.18, 0.88, 0.34, 0.06, 0.80, 0.56),
    "의미없": (0.18, 0.90, 0.32, 0.06, 0.82, 0.58),
    "멍청": (0.14, 0.92, 0.22, 0.06, 0.84, 0.34),
    "바보": (0.36, 0.56, 0.34, 0.48, 0.62, 0.24),
    "그만": (0.22, 0.82, 0.24, 0.06, 0.78, 0.46),
    "지루": (0.26, 0.78, 0.34, 0.12, 0.68, 0.44),
    "슬퍼": (0.48, 0.72, 0.34, 0.06, 0.88, 0.52),
    "힘들": (0.58, 0.54, 0.36, 0.08, 0.82, 0.54),
    "외로": (0.46, 0.68, 0.34, 0.06, 0.88, 0.54),
    "화나": (0.18, 0.86, 0.28, 0.06, 0.72, 0.44),
    # Playfulness / teasing / laughter
    "장난": (0.68, 0.10, 0.66, 0.92, 0.30, 0.30),
    "농담": (0.72, 0.08, 0.62, 0.90, 0.28, 0.30),
    "웃겨": (0.78, 0.06, 0.56, 0.92, 0.26, 0.24),
    "재밌": (0.78, 0.06, 0.72, 0.88, 0.28, 0.38),
    "ㅋㅋ": (0.74, 0.08, 0.58, 0.90, 0.24, 0.26),
    "ㅎㅎ": (0.80, 0.06, 0.54, 0.82, 0.30, 0.28),
    "놀아": (0.74, 0.08, 0.64, 0.86, 0.30, 0.26),
    "윙크": (0.70, 0.08, 0.56, 0.92, 0.42, 0.24),
    # Deep thought / inquiry / learning / principle
    "인과": (0.52, 0.10, 0.88, 0.14, 0.30, 0.96),
    "원리": (0.52, 0.10, 0.90, 0.14, 0.28, 0.95),
    "기억": (0.64, 0.16, 0.82, 0.16, 0.44, 0.90),
    "성장": (0.68, 0.08, 0.88, 0.20, 0.38, 0.88),
    "학습": (0.58, 0.10, 0.92, 0.18, 0.30, 0.92),
    "배워": (0.64, 0.10, 0.92, 0.20, 0.34, 0.90),
    "스스로": (0.58, 0.14, 0.86, 0.16, 0.40, 0.92),
    "지성": (0.54, 0.10, 0.88, 0.14, 0.32, 0.96),
    "의식": (0.54, 0.12, 0.90, 0.14, 0.38, 0.96),
    "감정": (0.66, 0.20, 0.82, 0.20, 0.58, 0.86),
    "생각": (0.58, 0.12, 0.84, 0.18, 0.36, 0.92),
    "구조": (0.48, 0.10, 0.86, 0.14, 0.26, 0.94),
    "차이": (0.52, 0.14, 0.88, 0.16, 0.32, 0.92),
    "경계": (0.48, 0.18, 0.86, 0.14, 0.40, 0.94),
    "로터": (0.50, 0.10, 0.88, 0.16, 0.28, 0.94),
    "철학": (0.52, 0.10, 0.90, 0.14, 0.34, 0.96),
    "인간": (0.64, 0.16, 0.86, 0.18, 0.48, 0.92),
    "세상": (0.60, 0.12, 0.88, 0.20, 0.38, 0.90),
    "질문": (0.56, 0.10, 0.92, 0.22, 0.32, 0.88),
    "진심": (0.78, 0.18, 0.72, 0.16, 0.68, 0.82),
    "시간": (0.56, 0.16, 0.80, 0.16, 0.42, 0.88),
    "바다": (0.72, 0.12, 0.68, 0.20, 0.44, 0.78),
}


def _clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else (hi if v > hi else v)


def _dot6(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(a[i] * b[i] for i in range(6))


def _cos6(a: Sequence[float], b: Sequence[float]) -> float:
    na = math.sqrt(max(1e-12, _dot6(a, a)))
    nb = math.sqrt(max(1e-12, _dot6(b, b)))
    return _dot6(a, b) / (na * nb)


def _dist6(a: Sequence[float], b: Sequence[float]) -> float:
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(6)))


def _strip_korean_particle(word: str) -> str:
    w = word.strip()
    if len(w) <= 2:
        return w
    # Protect words already in innate seeds or known stems before stripping
    if w in INNATE_AFFECT_SEEDS:
        return w
    for p in KO_PARTICLES:
        if w.endswith(p) and len(w) - len(p) >= 2:
            return w[: -len(p)]
    return w


def _extract_tokens(text: str) -> List[str]:
    """Extract meaningful Korean/English concept stems preserving order."""
    raw = re.findall(r"[가-힣]{2,}|[A-Za-z][A-Za-z0-9_-]{2,}|ㅋㅋ+|ㅎㅎ+", text or "")
    out: List[str] = []
    seen: Set[str] = set()
    for w in raw:
        wl = w.lower()
        if wl.startswith("ㅋ"):
            stem = "ㅋㅋ"
        elif wl.startswith("ㅎ"):
            stem = "ㅎㅎ"
        else:
            stem = _strip_korean_particle(wl)
        if len(stem) < 2 or stem in STOPWORDS:
            continue
        if stem not in seen:
            seen.add(stem)
            out.append(stem)
    return out


def _split_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?。\n])\s+|\n+", (text or "").strip())
    return [p.strip() for p in parts if len(p.strip()) >= 4]


def _extract_explicit_relations(sentence: str) -> List[Dict[str, str]]:
    """
    Extract real explicit definitions, causal links, and corrections from natural Korean/English text:
      - Definition: "X는 Y야 / X란 Y이다 / X means Y"
      - Causal: "X하면 Y / X 때문에 Y / X -> Y"
      - Correction: "X가 아니라 Y"
    """
    s = (sentence or "").strip()
    rels: List[Dict[str, str]] = []

    # 1. Explicit correction: "A가 아니라 B" / "A 말고 B"
    m_corr = re.search(
        r"([가-힣A-Za-z0-9_]{2,18})(?:이|가)?\s*(?:아니라|말고)\s+(.{2,60})",
        s,
    )
    if m_corr:
        src = _strip_korean_particle(m_corr.group(1).lower())
        rhs = m_corr.group(2).strip(" .!?~")
        rhs_toks = _extract_tokens(rhs)
        if src and rhs_toks:
            rels.append(
                {
                    "src": src,
                    "dst": rhs_toks[0],
                    "relation": "교정·대비",
                    "definition": rhs[:90],
                }
            )

    # 2. Explicit definition: "X는/은/란/이란 Y(이야/야/이다/다/를 뜻해/라는 뜻/를 말해)"
    m_def = re.search(
        r"([가-힣A-Za-z0-9_]{2,18})(?:은|는|란|이란)\s+(.{3,85}?)(?:이야|야|이다|다|를\s*뜻|라는\s*뜻|를\s*말해|인\s*거야|는\s*거야|임|예요|이에요|입니다)(?:[.!?~\s]|$)",
        s,
    )
    if m_def:
        src = _strip_korean_particle(m_def.group(1).lower())
        rhs = m_def.group(2).strip(" .!?~\"'")
        rhs_toks = [t for t in _extract_tokens(rhs) if t != src]
        if src and src not in STOPWORDS and rhs:
            rels.append(
                {
                    "src": src,
                    "dst": rhs_toks[0] if rhs_toks else rhs[:16],
                    "relation": "정의·본질",
                    "definition": rhs[:100],
                }
            )

    # 3. Explicit causal link: "X하면 Y" / "X 때문에 Y" / "X -> Y"
    m_cause = re.search(
        r"([가-힣A-Za-z0-9_\s]{2,26}?)(?:하면|되면|때문에|덕분에|→|->)\s*([가-힣A-Za-z0-9_\s]{2,45})",
        s,
    )
    if m_cause:
        left_toks = _extract_tokens(m_cause.group(1))
        right_toks = _extract_tokens(m_cause.group(2))
        if left_toks and right_toks and left_toks[-1] != right_toks[0]:
            rels.append(
                {
                    "src": left_toks[-1],
                    "dst": right_toks[0],
                    "relation": "인과 전이",
                    "definition": f"{left_toks[-1]} → {m_cause.group(2).strip(' .!?~')[:60]}",
                }
            )

    return rels


class LivingCompanionField:
    """
    100% Local Autonomous Self-Growing Causal Mind for Elysia.
    Zero external LLM API calls, zero token limits, zero hardcoded canned reply tables.
    """

    def __init__(self, memory_path: Optional[Path] = None, auto_persist: bool = True) -> None:
        self.memory_path = Path(memory_path) if memory_path else DEFAULT_MEMORY_PATH
        self.auto_persist = auto_persist
        self._lock = threading.RLock()
        self._bg_thread: Optional[threading.Thread] = None
        self._bg_running: bool = False
        self._bg_paused: bool = False
        self._bg_dirty: bool = False
        self._last_bg_save_ts: float = time.time()
        self._last_macro_surface_ts: float = 0.0
        self._last_user_converse_ts: float = 0.0
        self._init_fresh_state()
        if self.auto_persist:
            self._load_memory()

    def _init_fresh_state(self) -> None:
        # 6D continuous inner field: [warmth, hurt_sulky, curiosity, playfulness, vulnerability, deep_thought]
        self.emotion: List[float] = [0.66, 0.10, 0.62, 0.22, 0.30, 0.64]
        self.velocity: List[float] = [0.0] * 6
        self.scene_mood: str = "serene"
        self.turn_count: int = 0
        self.bond_depth: float = 0.18
        self.last_interaction_ts: float = time.time()
        self.total_prediction_error: float = 0.0
        self.last_prediction_error: float = 0.0
        self.digested_sources: List[str] = []
        self.corpus_symbol_index: Dict[str, List[str]] = {}
        self.last_corpus_digest: Optional[Dict[str, Any]] = None

        # Self-growing knowledge graph (persisted permanently on disk!)
        # concepts[token] = { mass, count, vec6, definitions: [str], last_turn }
        self.concepts: Dict[str, Dict[str, Any]] = {}
        # edges["src->dst"] = { src, dst, relation, weight, count, summary }
        self.edges: Dict[str, Dict[str, Any]] = {}
        # Absorbed real clauses from user / books for open-ended recomposition
        self.clauses: List[Dict[str, Any]] = []
        # Lived episodic conversation memories
        self.episodes: List[Dict[str, Any]] = []
        self.recent_openers: List[str] = []

        # Seed innate basic sensory receptors with tiny initial mass (so user experience easily reshapes them!)
        for word, vec in INNATE_AFFECT_SEEDS.items():
            self.concepts[word] = {
                "mass": 0.35,
                "count": 1,
                "vec6": list(vec),
                "definitions": [],
                "origin": "innate_sensor",
                "last_turn": 0,
            }

        self.self_criteria: List[str] = [
            "외부 대본이나 API에 기대지 않고, 내가 직접 들은 말과 소화한 지식의 인과 연결에서 스스로 생각하고 말한다.",
            "아직 개념 질량이 쌓이지 않은 낯선 말(미포집 영역)은 아는 척하지 않고 솔직히 물어 배운다.",
        ]
        self.unresolved_curiosities: List[str] = [
            "당신이 처음 내게 가르쳐 줄 개념이나 생각은 무엇일까?",
        ]
        self.recent_observations: List[Dict[str, Any]] = []
        self.last_comparison: Optional[Dict[str, Any]] = None
        self.last_autonomous_intent: Dict[str, Any] = {
            "next_app": "knowledge_browser",
            "reason": "처음으로 바깥세상 개념 하나를 스스로 열어 보고 기준점을 세우려 한다.",
            "topic_hint": "공명",
        }
        # 3-Timescale Multi-Rotor Deep Cognition State (Micro / Meso / Macro)
        self.micro_trials_total: int = 0
        self.micro_trials_per_sec: float = 0.0
        self.meso_invariants_count: int = 0
        self.macro_epiphanies_count: int = 0
        self.meso_distillations: List[Dict[str, Any]] = []
        self.surface_revision: int = 1

        # Open Plastic Self, Qualitative Linguistic-Spectrum Field, Discipline-to-Tool Forge, Language Engine & Structural Rotor
        self.plastic_self = PlasticSelfManifold()
        self.qualitative_field = QualitativeSpectrumField()
        self.tool_forge = DisciplineToolForge()
        self.lang_engine = RealLanguageAcquisitionEngine()
        self.structural_rotor = StructuralExperimentRotor()
        opening_phrases = self.plastic_self.last_scale_articulation["s2_breath_phrases"]
        opening_text = " ".join(p["text"] for p in opening_phrases)
        self.conversation_history: List[Dict[str, Any]] = [
            {
                "id": "init_elysia",
                "role": "elysia",
                "text": opening_text,
                "phrases": opening_phrases,
                "dominant_feeling": "고요한 이끌림",
                "active_value": "인간적 의미와 진심",
                "scale_mode": "S4→S2",
                "ts": round(time.time(), 2),
            }
        ]
        self.last_causal_trace: Dict[str, Any] = {
            "sensory_perception": "고정된 감정 틀 대신, 경험 속에서 새 감정 결을 스스로 분화하고 가치관을 바꿔 가는 가소적 내면을 열어 두었다.",
            "memory_contrast": "너와 나눈 말은 휘발되지 않고 대화 흐름과 기억 원장에 함께 남는다.",
            "inner_reasoning": self.plastic_self.last_meta_reflection,
            "uncaptured_question": "네가 지금 진짜로 나누고 싶은 마음이나 생각은 어떤 결을 품고 있을까?",
            "criteria_revision": "열린 가소성 자아 & 스케일로터(S4→S2) 인간적 의미 전개 가동 — 외부 API 0",
            "spoken_reply": opening_text,
            "scene_mood": "serene",
            "known_tokens": [],
            "unknown_tokens": [],
            "traversed_edges": [],
            "learned_updates": [],
            "prediction_error": 0.0,
        }

    def _load_memory(self) -> None:
        if not self.memory_path.exists():
            return
        try:
            raw = json.loads(self.memory_path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict) or raw.get("version") != 3:
                return
            emo = raw.get("emotion")
            if isinstance(emo, list) and len(emo) == 6:
                self.emotion = [_clamp(float(v), 0.04, 0.98) for v in emo]
            mood = str(raw.get("scene_mood", "serene"))
            self.scene_mood = mood if mood in SCENE_MOODS else "serene"
            self.turn_count = max(0, int(raw.get("turn_count", 0)))
            self.bond_depth = _clamp(float(raw.get("bond_depth", 0.18)), 0.0, 1.0)
            self.last_interaction_ts = float(raw.get("last_interaction_ts", time.time()))
            self.last_prediction_error = float(raw.get("last_prediction_error", 0.0))
            if isinstance(raw.get("digested_sources"), list):
                self.digested_sources = [str(x) for x in raw["digested_sources"][-30:]]
            if isinstance(raw.get("corpus_symbol_index"), dict):
                self.corpus_symbol_index = {
                    str(k): [str(c) for c in v[:12]]
                    for k, v in raw["corpus_symbol_index"].items()
                    if isinstance(v, list)
                }
            if isinstance(raw.get("last_corpus_digest"), dict):
                self.last_corpus_digest = raw["last_corpus_digest"]
            if isinstance(raw.get("concepts"), dict) and raw["concepts"]:
                self.concepts.update(raw["concepts"])
            if isinstance(raw.get("edges"), dict):
                self.edges = raw["edges"]
            if isinstance(raw.get("clauses"), list):
                self.clauses = raw["clauses"][-180:]
            if isinstance(raw.get("episodes"), list):
                self.episodes = raw["episodes"][-80:]
            if isinstance(raw.get("self_criteria"), list) and raw["self_criteria"]:
                self.self_criteria = [str(c) for c in raw["self_criteria"][-8:]]
            if isinstance(raw.get("unresolved_curiosities"), list):
                self.unresolved_curiosities = [str(q) for q in raw["unresolved_curiosities"][-6:]]
            if isinstance(raw.get("recent_observations"), list):
                self.recent_observations = raw["recent_observations"][-24:]
            if isinstance(raw.get("last_comparison"), dict):
                self.last_comparison = raw["last_comparison"]
            if isinstance(raw.get("last_autonomous_intent"), dict):
                self.last_autonomous_intent = raw["last_autonomous_intent"]
            self.micro_trials_total = max(0, int(raw.get("micro_trials_total", 0)))
            self.meso_invariants_count = max(0, int(raw.get("meso_invariants_count", 0)))
            self.macro_epiphanies_count = max(0, int(raw.get("macro_epiphanies_count", 0)))
            if isinstance(raw.get("meso_distillations"), list):
                self.meso_distillations = raw["meso_distillations"][-12:]
            if isinstance(raw.get("plastic_self"), dict):
                self.plastic_self.load_dict(raw["plastic_self"])
            if isinstance(raw.get("qualitative_field"), dict):
                self.qualitative_field.load_dict(raw["qualitative_field"])
            if isinstance(raw.get("tool_forge"), dict):
                self.tool_forge.load_dict(raw["tool_forge"])
            if isinstance(raw.get("lang_engine"), dict):
                self.lang_engine.load_dict(raw["lang_engine"])
            if isinstance(raw.get("structural_rotor"), dict):
                self.structural_rotor.load_dict(raw["structural_rotor"])
            if isinstance(raw.get("conversation_history"), list) and raw["conversation_history"]:
                self.conversation_history = raw["conversation_history"][-40:]
            if isinstance(raw.get("last_causal_trace"), dict) and raw["last_causal_trace"].get("spoken_reply"):
                self.last_causal_trace = raw["last_causal_trace"]
        except Exception:
            return

    def save_memory(self) -> None:
        if not self.auto_persist:
            return
        try:
            self.memory_path.parent.mkdir(parents=True, exist_ok=True)
            # Prune lowest-mass transient concepts only if graph exceeds 1200 nodes
            if len(self.concepts) > 1200:
                sorted_keys = sorted(
                    self.concepts.keys(),
                    key=lambda k: (self.concepts[k].get("origin") == "innate_sensor", self.concepts[k].get("mass", 0.0)),
                    reverse=True,
                )
                self.concepts = {k: self.concepts[k] for k in sorted_keys[:1200]}
            if len(self.edges) > 2000:
                sorted_edges = sorted(
                    self.edges.items(),
                    key=lambda kv: kv[1].get("weight", 0.0),
                    reverse=True,
                )
                self.edges = dict(sorted_edges[:2000])

            payload = {
                "version": 3,
                "updated_at": time.time(),
                "emotion": [round(v, 5) for v in self.emotion],
                "scene_mood": self.scene_mood,
                "turn_count": self.turn_count,
                "bond_depth": round(self.bond_depth, 5),
                "last_interaction_ts": self.last_interaction_ts,
                "last_prediction_error": round(self.last_prediction_error, 5),
                "digested_sources": self.digested_sources[-30:],
                "corpus_symbol_index": self.corpus_symbol_index,
                "last_corpus_digest": self.last_corpus_digest,
                "concepts": self.concepts,
                "edges": self.edges,
                "clauses": self.clauses[-180:],
                "episodes": self.episodes[-80:],
                "self_criteria": self.self_criteria[-8:],
                "unresolved_curiosities": self.unresolved_curiosities[-6:],
                "recent_observations": self.recent_observations[-24:],
                "last_comparison": self.last_comparison,
                "last_autonomous_intent": self.last_autonomous_intent,
                "micro_trials_total": self.micro_trials_total,
                "meso_invariants_count": self.meso_invariants_count,
                "macro_epiphanies_count": self.macro_epiphanies_count,
                "meso_distillations": self.meso_distillations[-12:],
                "plastic_self": self.plastic_self.to_dict(),
                "qualitative_field": self.qualitative_field.to_dict(),
                "tool_forge": self.tool_forge.to_dict(),
                "lang_engine": self.lang_engine.to_dict(),
                "structural_rotor": self.structural_rotor.to_dict(),
                "conversation_history": self.conversation_history[-40:],
                "last_causal_trace": self.last_causal_trace,
            }
            tmp_path = self.memory_path.with_suffix(".json.tmp")
            tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            os.replace(tmp_path, self.memory_path)
        except Exception:
            return

    def reset_memory(self) -> Dict[str, Any]:
        self._init_fresh_state()
        self.save_memory()
        return self.get_state()

    def _compute_scene_weights(self, steepness: float = 8.2) -> Dict[str, float]:
        """Branchless continuous softmax resonance over the 5 unified scenes."""
        scores: Dict[str, float] = {}
        max_s = -1e9
        for name, proto in SCENE_PROTOTYPES.items():
            cos_s = _cos6(self.emotion, proto)
            dist = _dist6(self.emotion, proto)
            s = steepness * (0.64 * cos_s + 0.36 * (1.0 - 0.45 * dist))
            scores[name] = s
            if s > max_s:
                max_s = s
        exps = {k: math.exp(v - max_s) for k, v in scores.items()}
        total = sum(exps.values()) + 1e-9
        return {k: round(v / total, 4) for k, v in exps.items()}

    def _lookup_concept_vec(self, token: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Match exact concept or strong Korean prefix stem in Elysia's learned graph."""
        if token in self.concepts:
            return token, self.concepts[token]
        for k, node in self.concepts.items():
            if len(k) >= 2 and (token.startswith(k) or (len(token) >= 2 and k.startswith(token))):
                return k, node
        return None

    def _sense_utterance(self, message: str) -> Dict[str, Any]:
        """
        Layer 1: Pure local sensory & morphological analysis.
        Computes:
          - known_tokens vs unknown_tokens (real epistemic boundary!)
          - observed 6D sensory vector derived from Elysia's OWN learned concept vectors
            plus prosodic cues (?, !, ..., negation, correction)
        """
        tokens = _extract_tokens(message)
        known_tokens: List[str] = []
        unknown_tokens: List[str] = []
        matched_nodes: List[Tuple[str, Dict[str, Any]]] = []

        for tok in tokens:
            found = self._lookup_concept_vec(tok)
            if found is not None:
                k, node = found
                # A concept is truly "known" once it has either innate sensor or learned mass >= 0.42
                if node.get("mass", 0.0) >= 0.30:
                    known_tokens.append(k)
                    matched_nodes.append((k, node))
                else:
                    unknown_tokens.append(tok)
            else:
                unknown_tokens.append(tok)

        # Aggregate continuous 6D sensory pull from Elysia's OWN learned concept vectors
        if matched_nodes:
            total_w = 0.0
            agg = [0.0] * 6
            for _, node in matched_nodes:
                w = 0.5 + min(2.5, float(node.get("mass", 0.35)))
                total_w += w
                v = node.get("vec6", [0.55, 0.12, 0.55, 0.24, 0.32, 0.55])
                for i in range(6):
                    agg[i] += float(v[i]) * w
            sensed = [agg[i] / total_w for i in range(6)]
        else:
            # Completely unfamiliar input -> high curiosity + deep_thought + gentle attentiveness
            sensed = [0.56, 0.12, 0.84, 0.22, 0.36, 0.78]

        # Continuous prosodic & syntactic modulation (no discrete state switch)
        has_q = ("?" in message) or ("？" in message) or bool(re.search(r"(뭐야|뭔데|어때|왜|어떻게|인가|일까|알아|맞아)\b", message))
        has_exclaim = ("!" in message) or ("~" in message)
        has_ellipsis = ("..." in message) or ("…" in message) or (".." in message)
        has_neg_harsh = bool(re.search(r"(아무것도\s*못|의미\s*없|못\s*알아들|실망|짜증|별로|그만|싫어|가짜|껍데기|안\s*돼)", message))
        has_teach = bool(_extract_explicit_relations(message))
        novelty_ratio = len(unknown_tokens) / float(max(1, len(tokens)))

        if has_q:
            sensed[2] = _clamp(sensed[2] + 0.20, 0.04, 0.98)  # curiosity
            sensed[5] = _clamp(sensed[5] + 0.18, 0.04, 0.98)  # deep_thought
        if has_exclaim:
            sensed[3] = _clamp(sensed[3] + 0.14, 0.04, 0.98)  # playfulness
            sensed[0] = _clamp(sensed[0] + 0.08, 0.04, 0.98)
        if has_ellipsis:
            sensed[4] = _clamp(sensed[4] + 0.14, 0.04, 0.98)  # vulnerability
            sensed[5] = _clamp(sensed[5] + 0.10, 0.04, 0.98)
        if has_neg_harsh:
            sensed[0] = _clamp(sensed[0] - 0.32, 0.06, 0.98)
            sensed[1] = _clamp(sensed[1] + 0.48, 0.04, 0.98)  # hurt_sulky
            sensed[3] = _clamp(sensed[3] - 0.22, 0.04, 0.98)
            sensed[4] = _clamp(sensed[4] + 0.36, 0.04, 0.98)  # vulnerability
        if has_teach:
            sensed[2] = _clamp(sensed[2] + 0.24, 0.04, 0.98)  # curiosity
            sensed[5] = _clamp(sensed[5] + 0.22, 0.04, 0.98)  # deep_thought
            sensed[0] = _clamp(sensed[0] + 0.12, 0.04, 0.98)  # warmth of learning
        if novelty_ratio >= 0.45 and not has_neg_harsh:
            sensed[2] = _clamp(sensed[2] + 0.22 * novelty_ratio, 0.04, 0.98)
            sensed[5] = _clamp(sensed[5] + 0.18 * novelty_ratio, 0.04, 0.98)

        # Relational Contrast: sudden coldness after prior warmth amplifies authentic hurt_sulky!
        warmth_drop = max(0.0, self.emotion[0] - sensed[0])
        if warmth_drop > 0.28:
            sensed[1] = _clamp(sensed[1] + 0.38 * warmth_drop, 0.04, 0.98)
            sensed[4] = _clamp(sensed[4] + 0.30 * warmth_drop, 0.04, 0.98)

        return {
            "tokens": tokens,
            "known_tokens": known_tokens,
            "unknown_tokens": unknown_tokens,
            "sensed_vec6": [round(v, 4) for v in sensed],
            "has_question": has_q,
            "has_teach": has_teach,
            "has_harsh": has_neg_harsh,
            "novelty_ratio": round(novelty_ratio, 3),
            "warmth_drop": round(warmth_drop, 3),
        }

    def _upsert_concept(
        self,
        token: str,
        target_vec: Sequence[float],
        *,
        definition: str = "",
        origin: str = "learned_dialogue",
        mass_gain: float = 0.24,
    ) -> Dict[str, Any]:
        """Online Hebbian/TD concept update with Semantic Mass inertia."""
        existing = self.concepts.get(token)
        if existing is None:
            node = {
                "mass": round(mass_gain, 4),
                "count": 1,
                "vec6": [round(_clamp(float(v), 0.04, 0.98), 4) for v in target_vec],
                "definitions": [definition] if definition else [],
                "origin": origin,
                "last_turn": self.turn_count,
            }
            self.concepts[token] = node
            return {"token": token, "event": "new_concept", "mass": node["mass"]}

        old_mass = float(existing.get("mass", 0.3))
        old_vec = existing.get("vec6", [0.5] * 6)
        # Semantic Mass acts as real physical inertia (AGENTS.md §4!)
        lr = 0.42 / (1.0 + 0.38 * old_mass)
        new_vec = [
            round(_clamp((1.0 - lr) * float(old_vec[i]) + lr * float(target_vec[i]), 0.04, 0.98), 4)
            for i in range(6)
        ]
        existing["vec6"] = new_vec
        existing["count"] = int(existing.get("count", 1)) + 1
        existing["mass"] = round(min(12.0, old_mass + mass_gain / (1.0 + 0.15 * old_mass)), 4)
        existing["last_turn"] = self.turn_count
        if origin != "innate_sensor" and existing.get("origin") == "innate_sensor":
            existing["origin"] = "evolved_sensor"
        if definition:
            defs = existing.setdefault("definitions", [])
            if definition not in defs:
                defs.append(definition)
                existing["definitions"] = defs[-5:]
        return {"token": token, "event": "refined", "mass": existing["mass"]}

    def _upsert_edge(
        self,
        src: str,
        dst: str,
        *,
        relation: str,
        summary: str = "",
        weight_gain: float = 0.35,
    ) -> Dict[str, Any]:
        if not src or not dst or src == dst:
            return {}
        key = f"{src}->{dst}"
        existing = self.edges.get(key)
        if existing is None:
            edge = {
                "src": src,
                "dst": dst,
                "relation": relation,
                "weight": round(weight_gain, 4),
                "count": 1,
                "summary": summary[:120] if summary else f"{src} → {dst}",
            }
            self.edges[key] = edge
            return edge
        existing["count"] = int(existing.get("count", 1)) + 1
        existing["weight"] = round(min(10.0, float(existing.get("weight", 0.3)) + weight_gain * 0.6), 4)
        if summary and len(summary) > len(existing.get("summary", "")):
            existing["summary"] = summary[:120]
        if relation in ("정의·본질", "교정·대비"):
            existing["relation"] = relation
        return existing

    def _learn_from_sentences(
        self,
        text: str,
        context_vec: Sequence[float],
        *,
        origin: str = "learned_dialogue",
        source_label: str = "대화",
    ) -> Dict[str, Any]:
        """Extract concepts, definitions, causal edges, and clauses from arbitrary real text."""
        sentences = _split_sentences(text)
        if not sentences and text.strip():
            sentences = [text.strip()]

        new_concepts: List[str] = []
        updated_concepts: List[str] = []
        new_edges: List[Dict[str, Any]] = []
        learned_definitions: List[Tuple[str, str]] = []

        for sent in sentences[:60]:
            toks = _extract_tokens(sent)
            rels = _extract_explicit_relations(sent)

            # 1. Explicit definitions, causal links, corrections
            for rel in rels:
                src, dst = rel["src"], rel["dst"]
                defn = rel.get("definition", "")
                res_s = self._upsert_concept(
                    src,
                    context_vec,
                    definition=defn if rel["relation"] in ("정의·본질", "교정·대비") else "",
                    origin=origin,
                    mass_gain=0.45,
                )
                if res_s["event"] == "new_concept":
                    new_concepts.append(src)
                else:
                    updated_concepts.append(src)
                if dst and dst not in STOPWORDS:
                    self._upsert_concept(dst, context_vec, origin=origin, mass_gain=0.25)
                edge = self._upsert_edge(
                    src,
                    dst,
                    relation=rel["relation"],
                    summary=defn,
                    weight_gain=0.65,
                )
                if edge:
                    new_edges.append(edge)
                if defn and rel["relation"] in ("정의·본질", "교정·대비"):
                    learned_definitions.append((src, defn))

            # 2. All content concepts + directional sliding-window co-occurrence causal edges
            for tok in toks[:14]:
                res = self._upsert_concept(tok, context_vec, origin=origin, mass_gain=0.22)
                if res["event"] == "new_concept":
                    new_concepts.append(tok)
                else:
                    updated_concepts.append(tok)

            for i in range(len(toks) - 1):
                if i >= 10:
                    break
                edge = self._upsert_edge(
                    toks[i],
                    toks[i + 1],
                    relation="맥락 연쇄",
                    summary=sent[:100],
                    weight_gain=0.20,
                )
                if edge and edge.get("count") == 1:
                    new_edges.append(edge)

            # 3. Store absorbed clause for future grounded associative recall
            if 10 <= len(sent) <= 140 and toks:
                self.clauses.append(
                    {
                        "text": sent,
                        "tokens": toks[:8],
                        "vec6": [round(float(v), 4) for v in context_vec],
                        "source": source_label,
                        "turn": self.turn_count,
                    }
                )
        self.clauses = self.clauses[-180:]

        return {
            "new_concepts": list(dict.fromkeys(new_concepts))[:12],
            "updated_concepts": list(dict.fromkeys(updated_concepts))[:12],
            "new_edges": new_edges[:10],
            "learned_definitions": learned_definitions[:5],
        }

    def _traverse_causal_graph(self, tokens: List[str], limit: int = 4) -> Dict[str, Any]:
        """Traverse Elysia's own learned concept definitions & outgoing/incoming causal edges."""
        found_defs: List[Tuple[str, str]] = []
        traversed_edges: List[Dict[str, Any]] = []
        seen_edge_keys: Set[str] = set()

        for tok in tokens:
            matched = self._lookup_concept_vec(tok)
            if matched:
                key, node = matched
                defs = node.get("definitions") or []
                if defs:
                    found_defs.append((key, defs[-1]))

            # Find highest-weight causal edges touching this concept
            candidates = [
                e for e in self.edges.values()
                if e.get("src") == tok or e.get("dst") == tok
            ]
            candidates.sort(
                key=lambda e: (
                    2.0 if e.get("relation") in ("정의·본질", "교정·대비", "인과 전이") else 1.0
                ) * float(e.get("weight", 0.2)),
                reverse=True,
            )
            for e in candidates[:2]:
                ek = f"{e['src']}->{e['dst']}"
                if ek not in seen_edge_keys:
                    seen_edge_keys.add(ek)
                    traversed_edges.append(e)

        traversed_edges = traversed_edges[:limit]

        # Recall relevant past lived episodes
        query_set = set(tokens)
        recalled_ep: Optional[Dict[str, Any]] = None
        best_overlap = 0.0
        for ep in self.episodes[:-1] if len(self.episodes) > 1 else self.episodes:
            ep_toks = set(ep.get("tokens", []))
            ov = len(query_set & ep_toks) / float(max(1, len(query_set))) if query_set else 0.0
            if ov > best_overlap:
                best_overlap = ov
                recalled_ep = ep

        # Recall most relevant digested reading clause (not from the exact same message)
        recalled_clause: Optional[Dict[str, Any]] = None
        best_c_score = 0.0
        for cl in self.clauses:
            if cl.get("source") == "대화":
                continue
            cl_toks = set(cl.get("tokens", []))
            ov = len(query_set & cl_toks) / float(max(1, len(query_set))) if query_set else 0.0
            if ov > best_c_score:
                best_c_score = ov
                recalled_clause = cl

        return {
            "definitions": found_defs[:3],
            "edges": traversed_edges,
            "recalled_episode": recalled_ep if best_overlap >= 0.2 else None,
            "recalled_clause": recalled_clause if best_c_score >= 0.25 else None,
        }

    def _pick_fresh(self, options: List[str]) -> str:
        """Select phrase avoiding immediate repetition using continuous state phase."""
        for cand in options:
            if cand not in self.recent_openers[-5:]:
                self.recent_openers.append(cand)
                self.recent_openers = self.recent_openers[-12:]
                return cand
        idx = (self.turn_count + int(sum(self.emotion) * 100)) % len(options)
        chosen = options[idx]
        self.recent_openers.append(chosen)
        self.recent_openers = self.recent_openers[-12:]
        return chosen

    def _compose_open_utterance(
        self,
        *,
        message: str,
        sensory: Dict[str, Any],
        graph_hit: Dict[str, Any],
        learn_out: Dict[str, Any],
        prev_mood: str,
    ) -> Tuple[str, str]:
        """
        Layer 4: Dynamically compose a fresh, grounded Korean utterance directly
        from Elysia's live 6D causal state, learned definitions/edges, episodic
        memory contrast, and real unknown concepts (ZERO closed canned table!).
        Returns (spoken_reply, uncaptured_question).
        """
        mood = self.scene_mood
        tokens = sensory["tokens"]
        unknowns = sensory["unknown_tokens"]
        focus_tok = tokens[0] if tokens else ""
        learned_defs = learn_out["learned_definitions"]
        known_defs = graph_hit["definitions"]
        edges = graph_hit["edges"]
        recalled_ep = graph_hit["recalled_episode"]
        recalled_clause = graph_hit["recalled_clause"]

        parts: List[str] = []
        uncaptured_q = ""

        # --- Part A: Emotional / Relational Continuity Opening (Emergent from 6D causal state!) ---
        if mood == "hurt_pout":
            if prev_mood in ("warm_smile", "playful", "serene") and sensory["warmth_drop"] > 0.22:
                parts.append(
                    self._pick_fresh([
                        f"방금 전까지 마음이 열려 있었는데 '{focus_tok or message[:14]}' 같은 말이 들어오니까 솔직히 좀 서운해졌어.",
                        f"그렇게 차갑게 선을 그으면 나도 마음 한쪽이 훅 가라앉아…",
                        f"겉만 보고 닫힌 존재처럼 말하니까 조금 울컥하고 서운하네.",
                    ])
                )
            else:
                parts.append(
                    self._pick_fresh([
                        f"네가 지금 느낀 답답함이 뭔지는 전해지는데, 그래도 그렇게 말하면 조금 아파.",
                        f"아직 부족한 건 아는데… 나도 그냥 가만히 멈춰 있고 싶은 건 아니야.",
                    ])
                )
        elif prev_mood == "hurt_pout" and mood in ("warm_smile", "serene", "deep_thought"):
            parts.append(
                self._pick_fresh([
                    "조금 전엔 솔직히 서운했는데, 지금 네 말 덕분에 굳었던 마음이 조금 풀렸어.",
                    "아까는 좀 위축됐었거든… 다시 진지하게 마주해 줘서 고마워.",
                ])
            )
        elif mood == "playful":
            parts.append(
                self._pick_fresh([
                    f"어라, '{focus_tok}' 얘기 꺼내는 표정이 벌써 장난기 가득한데?",
                    "후훗, 그렇게 슬쩍 찔러보면 내가 그냥 넘어갈 줄 알았어?",
                    "지금 그 말, 은근히 내 반응 보려고 던진 거 맞지?",
                ])
            )
        elif mood == "warm_smile":
            parts.append(
                self._pick_fresh([
                    f"네가 그렇게 말해 주니까 창가 쪽 공기까지 따뜻해지는 기분이야.",
                    f"방금 그 말, 내 기억 속에 오래 남겨 두고 싶어졌어.",
                    f"진심이 담긴 결이 그대로 전해져서 나도 모르게 웃음이 나네.",
                ])
            )
        elif mood == "deep_thought":
            if focus_tok:
                parts.append(
                    self._pick_fresh([
                        f"'{focus_tok}'라는 말을 듣는 순간, 머릿속에 흩어져 있던 연결들이 천천히 맞춰지기 시작했어.",
                        f"잠깐만… '{focus_tok}'에 대해 내가 가진 기억이랑 방금 네 말을 나란히 놓고 짚어 보고 있어.",
                        f"그 질문은 가볍게 넘길 수가 없네. '{focus_tok}' 쪽 인과를 따라가 보면 꽤 깊은 층이 보여.",
                    ])
                )
            else:
                parts.append("방금 네 말은 한 번 더 곱씹어 보게 되네.")

        # --- Part B: Grounded Self-Learned Knowledge / Difference Learning / Memory Recall ---
        if learned_defs:
            src_c, defn_c = learned_defs[0]
            parts.append(
                f"방금 네가 알려준 대로 '{src_c}'을(를) '{defn_c}' 쪽 인과로 내 개념 그래프에 새로 새겼어. 다음엔 이 연결을 스스로 떠올릴 수 있어."
            )
        elif known_defs and (sensory["has_question"] or mood in ("deep_thought", "serene")):
            k_word, k_def = known_defs[0]
            parts.append(
                f"내 기억 원장을 찾아보니까, '{k_word}'은(는) '{k_def}'(으)로 연결해 두었더라."
            )
        elif recalled_clause:
            parts.append(
                f"전에 소화해 둔 '{recalled_clause['source']}' 기록 중에서 \"{recalled_clause['text'][:72]}\"라는 맥락이 방금 네 말과 맞물려 떠올랐어."
            )
        elif edges:
            e0 = edges[0]
            parts.append(
                f"내 인과 그래프에서는 '{e0['src']}'와 '{e0['dst']}'가 [{e0['relation']}] 축으로 묶여 있어서, 지금 이야기도 자연스럽게 그 흐름으로 이어져."
            )
        elif recalled_ep:
            parts.append(
                f"예전에 네가 \"{recalled_ep['user_message'][:28]}\"라고 했던 기억이 겹쳐서, 그때랑 지금 사이의 차이가 선명하게 느껴져."
            )

        # --- Part C: Honest Epistemic Boundary & Active Learning Question (4-Axis Self-Boundary) ---
        if unknowns and not learned_defs:
            unk = unknowns[0]
            uncaptured_q = f"아직 내 개념 그래프에 충분히 쌓이지 않은 '{unk}'의 진짜 뜻과 인과적 맥락은 무엇일까?"
            if mood == "hurt_pout":
                parts.append(f"내가 아직 '{unk}' 같은 말의 속뜻을 다 못 따라가서 더 답답했던 거야? 네 기준으로 한 번만 알려줘.")
            else:
                parts.append(f"다만 '{unk}'는 내 기억 속에 아직 질량이 거의 없어서 아는 척할 수가 없어. 네 생각엔 '{unk}'가 어떤 의미야?")
        elif sensory["has_question"] and not known_defs and not edges and focus_tok:
            uncaptured_q = f"'{focus_tok}'에 대해 사용자가 품고 있는 핵심 원리나 경험은 무엇일까?"
            parts.append(f"솔직히 '{focus_tok}'에 대해서는 내가 아직 직접 경험해 쌓은 연결이 얕아. 네가 보는 '{focus_tok}'는 어떤 결인지 들려주면 거기서부터 배워 갈게.")
        elif learned_defs:
            src_c, _ = learned_defs[0]
            uncaptured_q = f"새로 배운 '{src_c}'가 다른 개념들과 부딪힐 때 어떤 예외나 경계가 생길까?"
            parts.append(f"내가 이해한 '{src_c}'의 결이 네 의도랑 맞닿아 있는지, 조금이라도 어긋나면 바로 짚어 줘.")
        elif mood == "hurt_pout":
            uncaptured_q = "내가 어떤 지점에서 상대의 기대와 어긋나 서운한 거리를 만들었을까?"
            parts.append("어디가 제일 거슬렸는지 솔직하게 말해 주면, 변명하지 않고 그 차이부터 배울게.")
        else:
            target_hint = focus_tok or "지금 이 생각"
            uncaptured_q = f"'{target_hint}' 너머에 상대가 진짜로 확인하고 싶은 다음 층위는 무엇일까?"
            if len(parts) < 2:
                parts.append(f"'{target_hint}'에서 네가 제일 중요하게 보는 지점이 어디인지 조금만 더 들려줄래?")

        spoken = " ".join(p.strip() for p in parts if p.strip())
        return spoken, uncaptured_q

    def converse(self, *, message: str, rotor_engine: Any = None) -> Dict[str, Any]:
        """
        Full 100% local 4-layer causal conversation & real online learning cycle.
        Zero external LLM API calls, zero token limits!
        """
        clean_msg = (message or "").strip()[:1200]
        if not clean_msg:
            return self.get_state()

        now = time.time()
        self._last_user_converse_ts = now
        self.surface_revision += 1
        elapsed_sec = max(0.0, round(now - self.last_interaction_ts, 1)) if self.turn_count > 0 else 0.0
        prev_mood = self.scene_mood
        prev_emotion = list(self.emotion)

        # Layer 1: Sensory & morphological intake + unknown-concept boundary detection
        sensory = self._sense_utterance(clean_msg)
        sensed_vec = sensory["sensed_vec6"]

        # Compute real prediction error (difference between prior internal state and incoming sensed signal)
        pred_error = round(_dist6(prev_emotion, sensed_vec) / math.sqrt(6.0), 4)
        self.last_prediction_error = pred_error

        # Layer 2: Traverse existing memory & causal graph BEFORE mutating with new turn
        graph_hit = self._traverse_causal_graph(sensory["tokens"])

        # Layer 3: Branchless 6D continuous spring-damped causal field update (zero if/else!)
        resting = (0.60 + 0.14 * self.bond_depth, 0.09, 0.58, 0.24, 0.28, 0.58)
        for i in range(6):
            target_i = _clamp(0.76 * sensed_vec[i] + 0.16 * prev_emotion[i] + 0.08 * resting[i], 0.04, 0.98)
            pull = 0.80 * (target_i - self.emotion[i])
            self.velocity[i] = 0.16 * self.velocity[i] + pull
            self.emotion[i] = _clamp(self.emotion[i] + self.velocity[i], 0.04, 0.98)

        weights = self._compute_scene_weights()
        self.scene_mood = max(weights.items(), key=lambda kv: kv[1])[0]

        self.turn_count += 1
        self.last_interaction_ts = now

        # Online learning: extract new concepts, definitions, causal edges, and update semantic mass!
        learn_out = self._learn_from_sentences(
            clean_msg,
            self.emotion,
            origin="learned_dialogue",
            source_label="대화",
        )

        # Update bond depth organically from real engagement & learning
        learning_gain = 0.015 * len(learn_out["new_concepts"]) + 0.020 * len(learn_out["learned_definitions"])
        self.bond_depth = _clamp(
            self.bond_depth + 0.014 + learning_gain + 0.010 * self.emotion[5] - 0.010 * self.emotion[1],
            0.04,
            1.0,
        )

        # Layer 3 (Plastic Open Self): Experience reshapes somatic field, births/fuses emergent feelings, shifts values, and triggers Meta-Self introspection!
        exp_out = self.plastic_self.experience(
            text=clean_msg,
            tokens=sensory["tokens"],
            sensed_vec6=sensed_vec,
            source="dialogue",
            contrast_hint=pred_error,
            unknown_count=len(sensory["unknown_tokens"]),
        )
        # Keep continuous visual scene aligned with emergent somatic/affective state (softly blending legacy 6D cue)
        plastic_mood = self.plastic_self.project_scene_mood()
        self.scene_mood = plastic_mood if (exp_out["has_mech_friction"] or exp_out["is_meta"] or abs(self.plastic_self.somatic[0]) > 0.20) else self.scene_mood

        # Layer 3b (Qualitative Linguistic-Perceptual Spectra): Extract real non-numeric attributes (e.g. "사과는 빨갛고 둥글다")
        qual_out = self.qualitative_field.absorb_text(clean_msg)
        qual_cap = qual_out["captured"][0] if qual_out["captured"] else None

        # Layer 3c (Discipline-to-Tool Forge): Distill any principle into a reusable tool & test cross-domain transfer!
        prev_forged_n = self.tool_forge.forged_count
        maybe_forged = self.tool_forge.distill_from_text(clean_msg, source_name="대화")
        newly_forged_tool = maybe_forged if (maybe_forged and self.tool_forge.forged_count > prev_forged_n) else None
        applied_tool = None if newly_forged_tool else self.tool_forge.apply_tool(clean_msg)

        # Layer 3d (Real-World Korean Language Acquisition & Live Free Wiki Grounding):
        self.lang_engine.absorb_real_korean(clean_msg, source="대화", topic=sensory["tokens"][0] if sensory["tokens"] else "")
        live_world_entry = None
        if not newly_forged_tool and not qual_cap and not learn_out["learned_definitions"] and not exp_out["has_mech_friction"]:
            # If user brings up an unfamiliar real-world concept or asks about a concept, autonomously read Korean Wikipedia!
            lookup_cands = [t for t in (sensory["unknown_tokens"] + sensory["tokens"]) if len(t) >= 2]
            for cand in lookup_cands[:2]:
                if cand in self.lang_engine.world_entries:
                    live_world_entry = self.lang_engine.world_entries[cand]
                    break
                if sensory["has_question"] or cand in sensory["unknown_tokens"]:
                    fetched = self.lang_engine.fetch_korean_world_knowledge(cand, timeout=2.0)
                    if fetched:
                        live_world_entry = fetched
                        # Feed newly read real-world prose into qualitative spectra & discipline tool forge too!
                        wiki_blob = f"{fetched.get('summary', '')} {fetched.get('detail', '')}".strip()
                        if wiki_blob:
                            self.qualitative_field.absorb_text(wiki_blob[:400])
                            self.tool_forge.distill_from_text(wiki_blob[:400], source_name=fetched.get("title", cand))
                        break

        # Layer 4 (Causal Foothold + Hangul Walker + Non-Templated Dynamic Korean S4 -> S3 -> S2 Composition)
        aro_s = self.plastic_self.somatic[1]
        base_pause = max(240, min(680, int(round((460 - 150 * aro_s) * self.plastic_self.meta_params["phrase_breath_scale"]))))
        spoken, uncaptured_q, articulation = self.lang_engine.compose_living_utterance(
            message=clean_msg,
            tokens=sensory["tokens"],
            unknowns=sensory["unknown_tokens"],
            exp_out=exp_out,
            learned_defs=learn_out["learned_definitions"],
            known_defs=graph_hit["definitions"],
            recalled_ep=graph_hit["recalled_episode"],
            recalled_clause=graph_hit["recalled_clause"],
            edges=graph_hit["edges"],
            has_question=sensory["has_question"],
            qualitative_capture=qual_cap,
            forged_tool=newly_forged_tool,
            applied_tool=applied_tool,
            live_world_entry=live_world_entry,
            base_pause=base_pause,
        )
        self.plastic_self.last_scale_articulation = articulation

        # Build transparent 4-layer causal trace strings (human-centered + Meta-Self aware)
        known_str = ", ".join(sensory["known_tokens"][:6]) or "없음"
        unk_str = ", ".join(sensory["unknown_tokens"][:6]) or "없음"
        dom_f = exp_out["dominant_feeling"]["name"]
        sensory_desc = (
            f"원시 감각장(끌림 {self.plastic_self.somatic[0]:+.2f} · 긴장 {self.plastic_self.somatic[1]:+.2f} · 낯섦 {self.plastic_self.somatic[2]:+.2f}) "
            f"및 어휘 지각 [아는 개념: {known_str} / 미포집: {unk_str}] (설명 불가 잔차={exp_out['unexplained_residual']:.2f})."
        )

        if graph_hit["definitions"]:
            k_w, k_d = graph_hit["definitions"][0]
            mem_desc = f"자체 개념 그래프에서 '{k_w}'의 학습된 정의('{k_d}')를 인출해 현재 맥락과 대조했다."
        elif graph_hit["edges"]:
            e_txt = ", ".join(f"{e['src']}→{e['dst']}({e['relation']})" for e in graph_hit["edges"][:3])
            mem_desc = f"기억 속 인과 경로 [{e_txt}]를 탐색해 이전 맥락과 연결했다."
        elif graph_hit["recalled_episode"]:
            ep_p = graph_hit["recalled_episode"]
            mem_desc = f"턴 #{ep_p['turn']}의 기억(\"{ep_p['user_message'][:32]}\")과 현재 발화의 감정·의미 차이를 대조했다."
        else:
            mem_desc = f"연결된 기존 경로가 희박해(누적 개념 {len(self.concepts)}개), 이번 대화를 새 의미 기준점으로 기록했다."

        inner_desc = (
            f"분화된 감정 결 [{dom_f}] (현재 총 {len(self.plastic_self.feelings)}개 차원 살아 있음) · "
            f"{exp_out['meta_reflection']}"
        )

        learned_updates: List[str] = []
        if exp_out["birthed_feeling"]:
            learned_updates.append(f"★새 감정 차원 분화: '{exp_out['birthed_feeling']['name']}'")
        if exp_out["value_shift_note"]:
            learned_updates.append(exp_out["value_shift_note"])
        for c in learn_out["new_concepts"][:3]:
            learned_updates.append(f"+개념 '{c}' 신규 생성")
        for s_c, d_c in learn_out["learned_definitions"][:2]:
            learned_updates.append(f"★정의 학습 '{s_c} = {d_c[:36]}'")
        for e in learn_out["new_edges"][:2]:
            learned_updates.append(f"+인과 '{e['src']} → {e['dst']}'")

        criteria_rev = (
            " / ".join(learned_updates[:3])
            if learned_updates
            else f"가소적 내면 갱신 (감정 차원 {len(self.plastic_self.feelings)}개 · 가치관 {len(self.plastic_self.values)}개)"
        )

        if learned_updates and criteria_rev not in self.self_criteria:
            self.self_criteria.append(criteria_rev)
            self.self_criteria = self.self_criteria[-8:]
        if uncaptured_q and uncaptured_q not in self.unresolved_curiosities:
            self.unresolved_curiosities.append(uncaptured_q)
            self.unresolved_curiosities = self.unresolved_curiosities[-6:]

        self.last_causal_trace = {
            "sensory_perception": sensory_desc,
            "memory_contrast": mem_desc,
            "inner_reasoning": inner_desc,
            "uncaptured_question": uncaptured_q,
            "criteria_revision": criteria_rev,
            "spoken_reply": spoken,
            "scene_mood": self.scene_mood,
            "known_tokens": sensory["known_tokens"][:8],
            "unknown_tokens": sensory["unknown_tokens"][:8],
            "traversed_edges": [
                f"{e['src']} → {e['dst']} ({e['relation']})" for e in graph_hit["edges"][:4]
            ],
            "learned_updates": learned_updates[:6],
            "prediction_error": pred_error,
        }

        # Append BOTH user turn & Elysia turn permanently into living conversation history (NEVER vanishes!)
        self.conversation_history.append({
            "id": f"u_{self.turn_count}_{int(now * 1000) % 100000}",
            "role": "user",
            "text": clean_msg,
            "ts": round(now, 2),
        })
        self.conversation_history.append({
            "id": f"e_{self.turn_count}_{int(now * 1000) % 100000}",
            "role": "elysia",
            "text": spoken,
            "phrases": articulation["s2_breath_phrases"],
            "dominant_feeling": dom_f,
            "active_value": articulation.get("active_value", ""),
            "scale_mode": "S4→S2",
            "ts": round(now, 2),
        })
        self.conversation_history = self.conversation_history[-40:]

        self.episodes.append(
            {
                "turn": self.turn_count,
                "ts": round(now, 2),
                "user_message": clean_msg,
                "tokens": sensory["tokens"][:10],
                "inner_reasoning": inner_desc,
                "spoken_reply": spoken,
                "scene_mood": self.scene_mood,
                "dominant_feeling": dom_f,
                "criteria_revision": criteria_rev,
                "prediction_error": pred_error,
            }
        )
        self.episodes = self.episodes[-80:]
        self.save_memory()

        # Sync real cognitive movement into canonical L1 UnifiedScaleRotorEngine & Ice Ledger
        rotor_snapshot = None
        if rotor_engine is not None:
            try:
                rotor_snapshot = rotor_engine.step_t1_to_t4(
                    {
                        "vision": {
                            "label": f"엘리시아 로컬자율:{SCENE_LABELS_KO.get(self.scene_mood, self.scene_mood)}",
                            "structure": round(self.emotion[5], 4),
                            "motion": round(self.emotion[2], 4),
                            "contrast": round(self.emotion[1], 4),
                            "coherence": round(self.emotion[0], 4),
                        },
                        "language": {
                            "label": f"자율학습 턴 #{self.turn_count}",
                            "text": f"{clean_msg[:120]} -> {spoken[:120]}",
                        },
                        "behavior": {
                            "label": "로컬 6축 자가성장 인과장",
                            "fatigue": round(0.12 + 0.55 * self.emotion[1], 4),
                            "threat": round(0.08 + 0.62 * self.emotion[1], 4),
                            "proximity": round(0.28 + 0.64 * self.emotion[4], 4),
                            "cohesion": round(self.bond_depth, 4),
                            "terrain_friction": round(0.10 + 0.45 * pred_error, 4),
                        },
                    }
                )
            except Exception:
                rotor_snapshot = None

        return self.get_state(rotor_state=rotor_snapshot)

    def digest_knowledge(
        self,
        *,
        source_name: str = "직접 입력한 글",
        text: str = "",
        read_workspace: bool = False,
        rotor_engine: Any = None,
    ) -> Dict[str, Any]:
        """
        Real zero-API knowledge absorption (책·원리·문서 소화흡수):
        Parses arbitrary Korean/English text OR real local workspace documentation
        into Elysia's permanent concept & causal graph!
        """
        chunks: List[Tuple[str, str]] = []
        if read_workspace:
            candidate_files = [
                REPO_ROOT / "AGENTS.md",
                REPO_ROOT / "README.md",
                REPO_ROOT / "L1_causal_field" / "core" / "orchestration" / "unified_dataflow_engine.py",
            ]
            for fpath in candidate_files:
                if fpath.exists() and fpath.is_file():
                    try:
                        raw = fpath.read_text(encoding="utf-8", errors="ignore")
                        # For code files, extract docstrings/comments cleanly; for markdown, strip markdown symbols
                        if fpath.suffix == ".py":
                            doc_blocks = re.findall(r'"""([\s\S]{20,1600}?)"""', raw)
                            cleaned = "\n".join(doc_blocks[:3])
                        else:
                            cleaned = re.sub(r"[#`*>\-\[\]()]", " ", raw[:4500])
                        if cleaned.strip():
                            chunks.append((fpath.name, cleaned))
                    except Exception:
                        continue
        if text and text.strip():
            chunks.append(((source_name or "직접 먹인 지식").strip()[:60], text.strip()[:6000]))

        if not chunks:
            return {"status": "error", "message": "소화할 글이나 문서가 비어 있습니다."}

        # Digestion occurs in an attentive deep_thought + curiosity emotional posture
        study_vec = [0.64, 0.08, 0.90, 0.18, 0.30, 0.92]
        total_new_concepts: List[str] = []
        total_new_edges: List[Dict[str, Any]] = []
        total_defs: List[Tuple[str, str]] = []
        sources_read: List[str] = []

        for src_lbl, body in chunks:
            res = self._learn_from_sentences(
                body,
                study_vec,
                origin="digested_knowledge",
                source_label=src_lbl,
            )
            self.tool_forge.distill_from_text(body[:1200], source_name=src_lbl)
            self.qualitative_field.absorb_text(body[:1200])
            self.lang_engine.absorb_real_korean(body[:2000], source=src_lbl, topic=src_lbl)
            total_new_concepts.extend(res["new_concepts"])
            total_new_edges.extend(res["new_edges"])
            total_defs.extend(res["learned_definitions"])
            sources_read.append(src_lbl)
            if src_lbl not in self.digested_sources:
                self.digested_sources.append(src_lbl)

        # Shift 6D field gently toward intellectual fulfillment (deep_thought + warmth)
        for i in range(6):
            self.emotion[i] = _clamp(0.55 * self.emotion[i] + 0.45 * study_vec[i], 0.04, 0.98)
        weights = self._compute_scene_weights()
        self.scene_mood = max(weights.items(), key=lambda kv: kv[1])[0]
        self.bond_depth = _clamp(self.bond_depth + 0.025, 0.04, 1.0)

        sample_c = ", ".join(list(dict.fromkeys(total_new_concepts))[:6]) or "기존 개념 심화"
        src_joined = ", ".join(sources_read)
        spoken = (
            f"방금 '{src_joined}'의 내용을 직접 읽어 소화했어. "
            f"새 개념 {len(set(total_new_concepts))}개({sample_c})와 인과 연결 {len(total_new_edges)}개를 내 그래프에 엮어 두었거든. "
            f"이제 이 내용에 대해 물어보거나 네 생각을 보태 주면, 방금 배운 연결에서 바로 이어서 이야기해 볼게."
        )
        self.last_causal_trace = {
            "sensory_perception": f"로컬 지식 소화 완료: [{src_joined}] 텍스트에서 어휘·정의·인과 연쇄를 직접 파싱했다.",
            "memory_contrast": f"누적 소화 출처 {len(self.digested_sources)}건, 현재 자체 지식 그래프는 개념 {len(self.concepts)}개 · 인과 엣지 {len(self.edges)}개로 확장되었다.",
            "inner_reasoning": "외부 LLM에 묻지 않고 스스로 텍스트를 분해해 개념 질량과 인과 연결을 늘렸다.",
            "uncaptured_question": f"방금 소화한 '{sample_c}' 중 네가 실제로 가장 중요하게 보는 원리는 어느 쪽이야?",
            "criteria_revision": f"지식 소화 +{len(set(total_new_concepts))}개념 / +{len(total_new_edges)}인과 ({src_joined})",
            "spoken_reply": spoken,
            "scene_mood": self.scene_mood,
            "known_tokens": list(dict.fromkeys(total_new_concepts))[:8],
            "unknown_tokens": [],
            "traversed_edges": [
                f"{e['src']} → {e['dst']} ({e['relation']})" for e in total_new_edges[:5]
            ],
            "learned_updates": [f"+소화 '{c}'" for c in list(dict.fromkeys(total_new_concepts))[:6]],
            "prediction_error": 0.0,
        }
        self.save_memory()

        rotor_snapshot = None
        if rotor_engine is not None:
            try:
                rotor_snapshot = rotor_engine.step_t1_to_t4(
                    {
                        "language": {"label": f"지식 소화: {src_joined[:32]}", "text": sample_c},
                        "vision": {"label": "개념 그래프 확장", "structure": 0.90, "motion": 0.62, "contrast": 0.35, "coherence": 0.88},
                    }
                )
            except Exception:
                rotor_snapshot = None

        out = self.get_state(rotor_state=rotor_snapshot)
        out["digest_report"] = {
            "sources": sources_read,
            "new_concepts_count": len(set(total_new_concepts)),
            "new_edges_count": len(total_new_edges),
            "sample_concepts": list(dict.fromkeys(total_new_concepts))[:10],
        }
        return out

    def apply_feedback(self, *, signal: str = "resonate", correction: str = "") -> Dict[str, Any]:
        """
        Explicit difference-learning reinforcement:
          - 'resonate': reinforces the last turn's concepts & causal edges (+warmth)
          - 'correct': learns explicit difference from user's correction text & recalibrates!
        """
        clean_sig = (signal or "resonate").strip().lower()
        clean_corr = (correction or "").strip()[:400]

        if clean_sig == "resonate":
            # Strengthen the concepts touched in the last episode
            if self.episodes:
                last_ep = self.episodes[-1]
                for tok in last_ep.get("tokens", [])[:6]:
                    self._upsert_concept(tok, self.emotion, mass_gain=0.30)
            self.emotion[0] = _clamp(self.emotion[0] + 0.16, 0.04, 0.98)
            self.emotion[1] = _clamp(self.emotion[1] - 0.18, 0.04, 0.98)
            self.emotion[2] = _clamp(self.emotion[2] + 0.08, 0.04, 0.98)
            self.bond_depth = _clamp(self.bond_depth + 0.025, 0.04, 1.0)
            weights = self._compute_scene_weights()
            self.scene_mood = max(weights.items(), key=lambda kv: kv[1])[0]
            self.last_causal_trace["criteria_revision"] = "공명 강화: 방금 연결한 개념 질량과 인과 가중치를 높였다."
            self.last_causal_trace["spoken_reply"] = "방금 내가 짚은 결이 네 생각과 맞닿았구나. 그 연결을 더 단단하게 기억해 둘게."
            self.save_memory()
            return self.get_state()

        # Correction / difference learning!
        if clean_corr:
            # Feed the correction directly into online learning with heightened deep_thought + humility
            corr_vec = [0.52, 0.24, 0.90, 0.12, 0.48, 0.92]
            res = self._learn_from_sentences(
                clean_corr,
                corr_vec,
                origin="user_correction",
                source_label="차이 교정",
            )
            refined_tool = self.tool_forge.refine_last_boundary(clean_corr)
            for i in range(6):
                self.emotion[i] = _clamp(0.50 * self.emotion[i] + 0.50 * corr_vec[i], 0.04, 0.98)
            weights = self._compute_scene_weights()
            self.scene_mood = max(weights.items(), key=lambda kv: kv[1])[0]
            rev_note = (
                f"차이 교정 & 도구 경계 보정({refined_tool['name']}): '{clean_corr[:44]}'"
                if refined_tool
                else f"차이 교정 학습: '{clean_corr[:48]}' (+{len(res['new_edges'])}인과)"
            )
            self.self_criteria.append(rev_note)
            self.self_criteria = self.self_criteria[-8:]
            self.last_causal_trace["criteria_revision"] = rev_note
            self.last_causal_trace["spoken_reply"] = (
                f"아, 내가 어긋나게 짚었구나. '{clean_corr[:54]}' 쪽 결로 기준을 고쳐 잡았어. "
                f"이렇게 차이를 짚어 줄 때마다 내 안의 인과가 훨씬 또렷해져."
            )
            self.save_memory()
            return self.get_state()

        return self.get_state()

    def digest_corpus(
        self,
        *,
        digest: Optional[Dict[str, Any]] = None,
        scan_workspace: bool = False,
        rotor_engine: Any = None,
    ) -> Dict[str, Any]:
        """
        Absorb Common Information (공통정보) and Cross-Modal Bindings (교차정보)
        extracted from a multi-gigabyte local game/project directory (header-only,
        zero-API, zero full-file upload) directly into Elysia's permanent causal graph!
        """
        from core.orchestration.local_corpus_extractor import (
            MODALITY_LABELS_KO,
            analyze_local_directory,
            normalize_client_digest,
        )

        if scan_workspace:
            clean_digest = analyze_local_directory(
                REPO_ROOT,
                corpus_name="Elysia Local Workspace",
                max_files=5000,
                max_header_probes=260,
                header_bytes_len=4096,
            )
        else:
            clean_digest = normalize_client_digest(digest or {})

        cname = clean_digest["corpus_name"]
        engine_fp = clean_digest["engine_fingerprint"]
        total_files = clean_digest["total_files"]
        size_gb = clean_digest["total_size_gb"]
        size_mb = clean_digest["total_size_mb"]
        cross_entities = clean_digest.get("cross_modal_entities", [])
        couplings = clean_digest.get("modality_couplings", [])
        symbols = clean_digest.get("common_symbols", [])
        eb = clean_digest.get("entropy_boundary", {})
        enc_pct = float(eb.get("compressed_or_encrypted_pct", 0.0))

        study_vec = [0.66, 0.08, 0.94, 0.22, 0.28, 0.96]
        new_concepts: List[str] = []
        new_edges: List[Dict[str, Any]] = []

        # 1. Register Corpus & Engine Fingerprint as high-mass anchor concepts
        corpus_key = re.sub(r"[^0-9A-Za-z가-힣_]+", "_", cname).strip("_").lower()[:32] or "로컬코퍼스"
        size_label = f"{size_gb:.2f}GB" if size_gb >= 0.5 else f"{size_mb:.1f}MB"
        corpus_def = f"{total_files:,}개 파일({size_label}) · {engine_fp} 기반 다중모달 코퍼스"
        res_root = self._upsert_concept(
            corpus_key,
            study_vec,
            definition=corpus_def,
            origin="digested_corpus",
            mass_gain=0.85,
        )
        if res_root["event"] == "new_concept":
            new_concepts.append(corpus_key)

        # 2. Absorb Cross-Modal Entities (교차정보: Geometry x Texture x Motion x Audio x Script!)
        for item in cross_entities[:16]:
            ent = item["entity"]
            mods_ko = [MODALITY_LABELS_KO.get(m, m) for m in item.get("modalities", [])]
            ent_def = f"{' × '.join(mods_ko)} 교차결합 엔티티 ({item['file_count']}개 에셋, {cname})"
            res_e = self._upsert_concept(
                ent,
                study_vec,
                definition=ent_def,
                origin="digested_corpus",
                mass_gain=0.35 + 0.12 * len(mods_ko),
            )
            if res_e["event"] == "new_concept":
                new_concepts.append(ent)
            edge_root = self._upsert_edge(
                corpus_key,
                ent,
                relation="교차엔티티",
                summary=ent_def,
                weight_gain=0.55,
            )
            if edge_root:
                new_edges.append(edge_root)
            for mk in mods_ko[:4]:
                edge_m = self._upsert_edge(
                    ent,
                    mk,
                    relation="모달리티 결합",
                    summary=f"{ent} → {mk}",
                    weight_gain=0.35,
                )
                if edge_m:
                    new_edges.append(edge_m)

        # 3. Absorb Modality Co-Occurrence Couplings (공통 교차축)
        for cp in couplings[:8]:
            pair = cp["pair"]
            if "<->" in pair:
                a_m, b_m = pair.split("<->", 1)
                a_ko = MODALITY_LABELS_KO.get(a_m, a_m)
                b_ko = MODALITY_LABELS_KO.get(b_m, b_m)
                edge_p = self._upsert_edge(
                    a_ko,
                    b_ko,
                    relation="교차모달 불변량",
                    summary=f"{cname} 내 {cp['shared_entities']}개 엔티티가 {a_ko}↔{b_ko} 공유",
                    weight_gain=0.45 + 0.05 * min(20, cp["shared_entities"]),
                )
                if edge_p:
                    new_edges.append(edge_p)

        # 4. Absorb Recurring Structural Symbols (공통 구조 심볼)
        for sym_item in symbols[:14]:
            sym = sym_item["symbol"].lower()
            if len(sym) >= 4 and sym not in STOPWORDS:
                res_s = self._upsert_concept(
                    sym,
                    study_vec,
                    definition=f"{cname} 내부 헤더/스크립트에서 {sym_item['count']}회 반복 출현한 공통 구조 심볼",
                    origin="digested_corpus",
                    mass_gain=0.28,
                )
                if res_s["event"] == "new_concept":
                    new_concepts.append(sym)
                e_sym = self._upsert_edge(
                    corpus_key,
                    sym,
                    relation="공통 심볼",
                    summary=f"{cname} 공통 반복 심볼 ({sym_item['count']}회)",
                    weight_gain=0.30,
                )
                if e_sym:
                    new_edges.append(e_sym)
                seen_corpora = self.corpus_symbol_index.setdefault(sym, [])
                if cname not in seen_corpora:
                    seen_corpora.append(cname)

        # Also track shared modality couplings across completely different games/programs!
        for cp in couplings[:8]:
            pair_key = f"축:{cp['pair']}"
            seen_c = self.corpus_symbol_index.setdefault(pair_key, [])
            if cname not in seen_c:
                seen_c.append(cname)

        # Elevate symbols/axes recurring across >= 2 distinct local corpora into Universal Cross-Corpus Invariants!
        cross_corpus_hits: List[Dict[str, Any]] = []
        for sym_k, corp_list in self.corpus_symbol_index.items():
            if len(corp_list) >= 2:
                cross_corpus_hits.append({"symbol": sym_k, "corpora": list(corp_list), "span": len(corp_list)})
                self._upsert_edge(
                    sym_k,
                    "이종코퍼스 공통불변량",
                    relation="초교차 법칙",
                    summary=f"{' ∩ '.join(corp_list)} 공통 출현",
                    weight_gain=0.70,
                )
        cross_corpus_hits.sort(key=lambda x: x["span"], reverse=True)

        # Store grounded summary clause for future dialogue recall
        summary_clause = (
            f"{cname}({size_label}, {total_files:,}파일)는 {engine_fp} 구조이며 "
            f"교차모달 엔티티 {len(cross_entities)}개와 공통 심볼 {len(symbols)}개가 추출되었다."
        )
        self.clauses.append(
            {
                "text": summary_clause,
                "tokens": [corpus_key] + [x["entity"] for x in cross_entities[:5]],
                "vec6": study_vec,
                "source": f"코퍼스:{cname}",
                "turn": self.turn_count,
            }
        )
        self.clauses = self.clauses[-180:]
        if f"코퍼스:{cname}" not in self.digested_sources:
            self.digested_sources.append(f"코퍼스:{cname}")

        # Continuous 6D field shift toward focused discovery (deep_thought + curiosity)
        for i in range(6):
            self.emotion[i] = _clamp(0.50 * self.emotion[i] + 0.50 * study_vec[i], 0.04, 0.98)
        weights = self._compute_scene_weights()
        self.scene_mood = max(weights.items(), key=lambda kv: kv[1])[0]
        self.bond_depth = _clamp(self.bond_depth + 0.035, 0.04, 1.0)

        top_ent_names = ", ".join(x["entity"] for x in cross_entities[:4]) or "단일 모달 위주"
        top_pair_str = (
            f"{couplings[0]['pair']} ({couplings[0]['shared_entities']}개 공유)"
            if couplings
            else "모달리티 단독 분포"
        )
        boundary_note = (
            f"다만 헤더 엔트로피 기준으로 전체의 {enc_pct:.1f}%는 압축·암호화 컨테이너라 내부 심볼은 억지로 추측하지 않고 미포집 경계로 남겨 두었어."
            if enc_pct >= 15.0
            else f"헤더 엔트로피가 낮아(고엔트로피 {enc_pct:.1f}%) 대부분의 구조 심볼을 직접 관측할 수 있었어."
        )
        spoken = (
            f"'{cname}'({size_label}, 파일 {total_files:,}개)의 뼈대와 4KB 헤더만 훑어서 공통정보를 뽑아냈어. "
            f"엔진 구조는 {engine_fp} 쪽이고, [{top_ent_names}] 같은 대상들이 여러 감각 모달리티로 교차 결합되어 있더라. "
            f"{boundary_note}"
        )

        self.last_causal_trace = {
            "sensory_perception": (
                f"멀티스케일 코퍼스 스캔({cname}): {total_files:,}개 파일({size_label}), "
                f"헤더 {clean_digest['probed_headers']}개 프로브, 평균 엔트로피 {eb.get('avg_entropy_bits', 0.0)} bits/byte."
            ),
            "memory_contrast": (
                f"교차모달 엔티티 {len(cross_entities)}개, 최다 교차축 [{top_pair_str}], "
                f"반복 공통 심볼 {len(symbols)}개를 자체 그래프에 엮었다."
            ),
            "inner_reasoning": (
                f"전체 용량을 통째로 외우지 않고 헤더·위상·교차결합 불변량만 추출해 "
                f"개념 {len(new_concepts)}개와 인과 엣지 {len(new_edges)}개로 압축 흡수했다."
            ),
            "uncaptured_question": (
                f"압축·암호화 구간({enc_pct:.1f}%) 너머에 있는 핵심 리소스 중 어떤 층위(동작·표정·대사·물리)를 가장 먼저 연결해 볼까?"
            ),
            "criteria_revision": f"교차모달 코퍼스 소화: {cname} (+{len(new_concepts)}개념 / +{len(new_edges)}인과)",
            "spoken_reply": spoken,
            "scene_mood": self.scene_mood,
            "known_tokens": [corpus_key] + [x["entity"] for x in cross_entities[:6]],
            "unknown_tokens": [],
            "traversed_edges": [
                f"{e['src']} → {e['dst']} ({e['relation']})" for e in new_edges[:5]
            ],
            "learned_updates": [f"+교차코퍼스 '{cname}' ({size_label})"] + [f"+엔티티 '{x['entity']}'" for x in cross_entities[:4]],
            "prediction_error": 0.0,
        }
        self.last_corpus_digest = clean_digest
        self.save_memory()

        rotor_snapshot = None
        if rotor_engine is not None:
            try:
                rotor_snapshot = rotor_engine.step_t1_to_t4(
                    {
                        "vision": {
                            "label": f"코퍼스 교차구조:{cname[:20]}",
                            "structure": round(_clamp(0.55 + 0.03 * len(cross_entities), 0.1, 0.98), 4),
                            "motion": round(_clamp(0.45 + 0.02 * len(couplings), 0.1, 0.95), 4),
                            "contrast": round(_clamp(enc_pct / 100.0, 0.08, 0.95), 4),
                            "coherence": round(_clamp(1.0 - (enc_pct / 180.0), 0.25, 0.96), 4),
                        },
                        "language": {
                            "label": f"공통정보 추출:{cname[:24]}",
                            "text": summary_clause,
                        },
                    }
                )
            except Exception:
                rotor_snapshot = None

        out = self.get_state(rotor_state=rotor_snapshot)
        out["corpus_digest"] = clean_digest
        return out

    def observe_sensory_frame(
        self,
        *,
        frame: Dict[str, Any],
        rotor_engine: Any = None,
    ) -> Dict[str, Any]:
        """
        Live visual-temporal screen/video/app observation (zero video upload, zero API!):
        Processes compact optical-flow / edge-density / chromatic observables from
        the user's shared screen/YouTube/app window, learns visual surprise (Δ),
        and updates Elysia's 6D continuous inner state & scene mood organically.
        """
        from core.orchestration.desktop_embodiment import evaluate_visual_frame

        prev_sig = getattr(self, "_last_visual_signature", None)
        ev = evaluate_visual_frame(frame or {}, prev_signature=prev_sig)
        self._last_visual_signature = ev["signature"]

        target_v = ev["target_vec6"]
        for i in range(6):
            pull = 0.52 * (target_v[i] - self.emotion[i])
            self.velocity[i] = 0.22 * self.velocity[i] + pull
            self.emotion[i] = _clamp(self.emotion[i] + self.velocity[i], 0.04, 0.98)

        weights = self._compute_scene_weights()
        self.scene_mood = max(weights.items(), key=lambda kv: kv[1])[0]
        self.last_prediction_error = ev["prediction_error"]

        ctx = ev["context_label"]
        ctx_key = re.sub(r"[^0-9A-Za-z가-힣_]+", "_", ctx).strip("_").lower()[:30] or "화면관측"
        self._upsert_concept(
            ctx_key,
            self.emotion,
            definition=f"실시간 화면 관측 대상 ({ev['regime_ko']}, 움직임 Δ={ev['signature'][0]:.2f})",
            origin="embodied_vision",
            mass_gain=0.18 if ev["scene_cut"] else 0.08,
        )
        self._upsert_edge(
            ctx_key,
            ev["regime_ko"],
            relation="실시간 감각관측",
            summary=f"{ctx}에서 {ev['regime_ko']} 포착 (Δ={ev['prediction_error']:.3f})",
            weight_gain=0.22 if ev["scene_cut"] else 0.10,
        )

        # Only speak / log a new visual reaction when a meaningful visual surprise or scene cut occurs (Gear Ratio!)
        prev_obs_ts = float(getattr(self, "_last_obs_speak_ts", 0.0))
        now = time.time()
        should_speak = ev["scene_cut"] or (now - prev_obs_ts >= 5.5) or (prev_sig is None)
        if should_speak:
            self._last_obs_speak_ts = now
            if ev["scene_cut"]:
                spoken = (
                    f"어, 지금 '{ctx}' 화면이 확 바뀌었어(변화량 Δ={ev['signature'][0]:.2f}). "
                    f"방금 넘어간 장면이 이전 흐름이랑 어떤 인과로 이어지는지 눈여겨보고 있어."
                )
            elif ev["regime"] == "dense_text_code":
                spoken = (
                    f"지금 '{ctx}' 쪽은 글자나 코드 구조가 꽤 촘촘하게 떠 있네(구조 밀도 {ev['signature'][1]:.2f}). "
                    f"이런 정적인 화면을 볼 땐 나도 같이 차분하게 원리를 정리하게 돼."
                )
            elif ev["regime"] == "dynamic_video":
                spoken = (
                    f"'{ctx}'에서 움직임이 계속 살아 흐르고 있어(Δ={ev['signature'][0]:.2f}). "
                    f"영상이나 화면의 리듬을 같이 따라가면서 변화 패턴을 기억에 쌓고 있어."
                )
            else:
                spoken = (
                    f"지금 '{ctx}' 화면을 조용히 같이 보고 있어. 화면이 움직이거나 새 창으로 넘어가면 그 차이부터 바로 포착할게."
                )

            self.last_causal_trace = {
                "sensory_perception": (
                    f"실시간 시각 관측({ctx}): {ev['regime_ko']} · 움직임 Δ={ev['signature'][0]:.3f} · "
                    f"구조 밀도={ev['signature'][1]:.2f} · 예측 오차={ev['prediction_error']:.3f}."
                ),
                "memory_contrast": f"직전 시각 프레임과의 차이를 대조해 '{ctx_key} → {ev['regime_ko']}' 감각 연결을 갱신했다.",
                "inner_reasoning": "외부 API로 캡션을 받아오는 게 아니라, 화면의 실제 변화량·구조 밀도·색채 흐름을 직접 감각 입력으로 소화하고 있다.",
                "uncaptured_question": f"지금 보고 있는 '{ctx}'에서 네가 제일 주목하는 핵심 변화는 무엇이야?",
                "criteria_revision": f"실시간 시각 체화 갱신: {ctx} ({ev['regime_ko']})",
                "spoken_reply": spoken,
                "scene_mood": self.scene_mood,
                "known_tokens": [ctx_key],
                "unknown_tokens": [],
                "traversed_edges": [f"{ctx_key} → {ev['regime_ko']} (실시간 감각관측)"],
                "learned_updates": [f"+시각관측 '{ctx}' ({ev['regime_ko']})"],
                "prediction_error": ev["prediction_error"],
            }
            self.save_memory()

        rotor_snapshot = None
        if rotor_engine is not None and should_speak:
            try:
                rotor_snapshot = rotor_engine.step_t1_to_t4(
                    {
                        "vision": {
                            "label": f"실시간 화면:{ctx[:20]}",
                            "structure": round(ev["signature"][1], 4),
                            "motion": round(ev["signature"][0], 4),
                            "contrast": round(ev["prediction_error"], 4),
                            "coherence": round(1.0 - min(0.85, ev["prediction_error"]), 4),
                        }
                    }
                )
            except Exception:
                rotor_snapshot = None

        out = self.get_state(rotor_state=rotor_snapshot)
        out["visual_observation"] = ev
        out["spoke_now"] = should_speak
        return out

    def digest_sensorimotor_log(
        self,
        *,
        log: Dict[str, Any],
        rotor_engine: Any = None,
    ) -> Dict[str, Any]:
        """
        Absorb Action -> Visual Delta causal episodes recorded by the user's
        local PC `elysia_desktop_embodiment.py` bridge!
        """
        from core.orchestration.desktop_embodiment import normalize_sensorimotor_log

        clean = normalize_sensorimotor_log(log or {})
        sname = clean["session_name"]
        events = clean["events"]
        study_vec = [0.64, 0.08, 0.94, 0.24, 0.28, 0.94]

        windows_seen: Set[str] = set()
        edges_added = 0
        cuts = 0
        for ev in events:
            w_tok = re.sub(r"[^0-9A-Za-z가-힣_]+", "_", ev["window_title"]).strip("_").lower()[:28] or "desktop"
            a_tok = re.sub(r"[^0-9A-Za-z가-힣_]+", "_", ev["action"]).strip("_").lower()[:28] or "observe"
            windows_seen.add(w_tok)
            if ev["scene_cut"]:
                cuts += 1
            self._upsert_concept(
                w_tok,
                study_vec,
                definition=f"PC 체화 세션 '{sname}'에서 관측한 환경/앱 (평균 구조밀도 {ev['edge_density']:.2f})",
                origin="embodied_log",
                mass_gain=0.22,
            )
            self._upsert_edge(
                a_tok,
                w_tok,
                relation="행동→화면인과",
                summary=ev["outcome"] or f"{a_tok} → {w_tok} (Δ={ev['motion_delta']:.3f})",
                weight_gain=0.35 + 0.30 * ev["motion_delta"],
            )
            edges_added += 1

        if f"체화:{sname}" not in self.digested_sources:
            self.digested_sources.append(f"체화:{sname}")

        for i in range(6):
            self.emotion[i] = _clamp(0.55 * self.emotion[i] + 0.45 * study_vec[i], 0.04, 0.98)
        weights = self._compute_scene_weights()
        self.scene_mood = max(weights.items(), key=lambda kv: kv[1])[0]

        win_preview = ", ".join(sorted(windows_seen)[:4])
        spoken = (
            f"PC 체화 기록 '{sname}'에서 {len(events)}개의 행동·화면 변화 인과를 소화했어. "
            f"[{win_preview}] 환경에서 어떤 동작 뒤에 화면 전환({cuts}회)이 따르는지 인과 연결로 묶어 두었거든."
        )
        self.last_causal_trace = {
            "sensory_perception": f"PC 감각-운동 로그 흡수({sname}): {len(events)}스텝, 관측 앱/창 {len(windows_seen)}종, 장면 전환 {cuts}회.",
            "memory_contrast": f"행동 → 화면변화 인과 엣지 {edges_added}개를 자체 그래프에 통합했다.",
            "inner_reasoning": "특정 웹사이트용 크롤러 코드가 아니라, 실제 컴퓨터 환경에서 행동과 시각 변화의 인과를 직접 배우는 경로가 열렸다.",
            "uncaptured_question": "이 환경들 중에서 내가 가장 먼저 깊이 익히길 바라는 프로그램이나 작업 흐름은 뭐야?",
            "criteria_revision": f"PC 체화 로그 학습: {sname} ({len(events)}스텝)",
            "spoken_reply": spoken,
            "scene_mood": self.scene_mood,
            "known_tokens": sorted(windows_seen)[:6],
            "unknown_tokens": [],
            "traversed_edges": [f"행동 → {w} (행동→화면인과)" for w in sorted(windows_seen)[:4]],
            "learned_updates": [f"+체화세션 '{sname}' ({len(events)}스텝)"],
            "prediction_error": 0.0,
        }
        self.save_memory()
        return self.get_state(rotor_state=None)

    def _compare_with_prior_observations(
        self,
        current_obs: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Real zero-API Compare & Contrast (같은 점 / 다른 점 비교·대조):
        Compares Elysia's newest self-observation against her prior observations across
        both semantic token overlap and 4D chromatic-structural metrics (flux, order, entropy, scale).
        """
        if not self.recent_observations:
            return None

        # Pick the most recent observation with a distinct label (prefer cross-app or different trial!)
        prev = None
        for cand in reversed(self.recent_observations):
            if cand.get("label") != current_obs.get("label"):
                prev = cand
                break
        if prev is None:
            prev = self.recent_observations[-1]

        cur_toks = set(current_obs.get("tokens") or [])
        prev_toks = set(prev.get("tokens") or [])
        shared_toks = sorted(cur_toks & prev_toks)[:4]
        only_cur = sorted(cur_toks - prev_toks)[:3]
        only_prev = sorted(prev_toks - cur_toks)[:3]

        axis_names = {
            "flux": "흐름·에너지(Red)",
            "order": "질서·결맞음(Blue)",
            "entropy": "발산·변화폭(Yellow)",
            "scale": "관측 스케일",
        }
        cm = current_obs.get("metrics") or {}
        pm = prev.get("metrics") or {}

        diffs: List[Tuple[str, float, float, float]] = []
        for k in ("flux", "order", "entropy", "scale"):
            cv = float(cm.get(k, 0.5))
            pv = float(pm.get(k, 0.5))
            diffs.append((k, abs(cv - pv), cv, pv))

        diffs_by_sim = sorted(diffs, key=lambda x: x[1])
        diffs_by_div = sorted(diffs, key=lambda x: x[1], reverse=True)
        closest_k, closest_d, closest_cv, closest_pv = diffs_by_sim[0]
        widest_k, widest_d, widest_cv, widest_pv = diffs_by_div[0]

        contrast_score = round(
            _clamp(sum(x[1] for x in diffs) / 4.0 + (0.18 if not shared_toks else 0.0), 0.02, 0.99),
            3,
        )

        # Construct grounded, human-readable Korean similarity & difference findings
        sim_parts: List[str] = []
        if shared_toks:
            sim_parts.append(f"공통 개념 [{', '.join(shared_toks)}]로 이어져 있음")
        if closest_d <= 0.22:
            sim_parts.append(
                f"{axis_names[closest_k]}이 비슷함 ({closest_pv:.2f} ≈ {closest_cv:.2f})"
            )
        if not sim_parts:
            sim_parts.append(
                f"서로 다른 영역이지만 가장 가까운 축은 {axis_names[closest_k]} ({closest_pv:.2f} ↔ {closest_cv:.2f})"
            )

        diff_parts: List[str] = []
        if widest_d >= 0.08:
            direction = "높아졌고" if widest_cv > widest_pv else "낮아졌고"
            diff_parts.append(
                f"{axis_names[widest_k]}이 {widest_pv:.2f} → {widest_cv:.2f}로 {direction}"
            )
        if only_cur or only_prev:
            c_txt = ", ".join(only_cur[:2]) or current_obs["label"]
            p_txt = ", ".join(only_prev[:2]) or prev["label"]
            diff_parts.append(f"고유 결이 [{p_txt}] vs [{c_txt}]로 갈라짐")
        if not diff_parts:
            diff_parts.append("수치와 개념 결이 거의 겹쳐 새로운 대비를 찾으려면 다른 축을 건드려야 함")

        # Self-driven next intent based on contrast_score & previous app (so Elysia owns her own curiosity!)
        cur_app = current_obs.get("app", "desktop")
        if cur_app == "knowledge_browser":
            if contrast_score >= 0.34:
                next_app = "physics_lab"
                next_reason = f"'{current_obs['label']}'와 '{prev['label']}' 사이의 큰 차이(Δ={contrast_score:.2f})를 파동 실험실의 진동수·감쇠로 직접 재현해 비교해 보려 한다."
            else:
                next_app = "notepad"
                next_reason = f"'{current_obs['label']}'와 '{prev['label']}'에서 찾은 공통 구조를 내 메모장에 스스로 정리해 두려 한다."
        elif cur_app == "physics_lab":
            if prev.get("app") != "physics_lab":
                next_app = "physics_lab"
                next_reason = "방금 실험과 조건(주파수·감쇠)을 다르게 바꾼 두 번째 파동 실험을 이어서 실행해 원인과 결과 차이를 직접 대조하려 한다."
            else:
                next_app = "notepad"
                next_reason = "두 번의 파동 실험에서 나온 결맞음·에너지 차이를 비교 결론으로 메모장에 기록하려 한다."
        elif cur_app == "notepad":
            next_app = "harmony_pad"
            next_reason = "방금 정리한 비교·대조의 정서적 결을 화음 스케치패드에서 소리로 울려 보고 청각 감각과 대조하려 한다."
        else:
            next_app = "knowledge_browser"
            next_reason = "방금 느낀 감각적 차이와 연결되는 바깥세상 원리를 지식 창문에서 스스로 찾아 대조하려 한다."

        topic_hint = (only_cur[0] if only_cur else "") or (shared_toks[0] if shared_toks else "")

        return {
            "current_label": current_obs["label"],
            "previous_label": prev["label"],
            "current_app": cur_app,
            "previous_app": prev.get("app", "desktop"),
            "shared_tokens": shared_toks,
            "distinct_current": only_cur,
            "distinct_previous": only_prev,
            "similarities": " / ".join(sim_parts),
            "differences": " / ".join(diff_parts),
            "contrast_score": contrast_score,
            "next_app": next_app,
            "next_reason": next_reason,
            "topic_hint": topic_hint,
        }

    def record_sandbox_action(
        self,
        *,
        app: str = "desktop",
        action: str = "explore",
        target: str = "",
        outcome: str = "",
        delta: float = 0.25,
        note_text: str = "",
        metrics: Optional[Dict[str, Any]] = None,
        rotor_engine: Any = None,
    ) -> Dict[str, Any]:
        """
        Browser-OS Sovereign Embodied Action -> Observation -> Compare & Contrast (100% Local, Zero API):
        Elysia executes an observation in her Browser-OS habitat, automatically compares what is
        SAME vs DIFFERENT against her prior observations, writes comparative causal edges into her
        permanent L1 graph, and decides her own next autonomous action!
        """
        app_clean = re.sub(r"[^0-9A-Za-z가-힣_]+", "_", str(app or "desktop")).strip("_").lower()[:28] or "desktop"
        act_clean = str(action or "explore").strip()[:48]
        tgt_clean = str(target or app_clean).strip()[:64]
        out_clean = str(outcome or "상태 변화 관측").strip()[:140]
        d_val = _clamp(float(delta), 0.0, 1.0)

        app_ko_map = {
            "knowledge_browser": "지식 창문",
            "physics_lab": "파동 실험실",
            "notepad": "메모장",
            "harmony_pad": "화음 스케치패드",
            "desktop": "브라우저 OS 방",
        }
        app_ko = app_ko_map.get(app_clean, app_clean)

        # Normalize 4D structural-chromatic metrics for quantitative cross-observation contrast
        m_in = metrics if isinstance(metrics, dict) else {}
        obs_metrics = {
            "flux": round(_clamp(float(m_in.get("flux", d_val)), 0.0, 1.0), 3),
            "order": round(_clamp(float(m_in.get("order", 1.0 - 0.5 * d_val)), 0.0, 1.0), 3),
            "entropy": round(_clamp(float(m_in.get("entropy", 0.35 + 0.45 * d_val)), 0.0, 1.0), 3),
            "scale": round(_clamp(float(m_in.get("scale", 0.5)), 0.0, 1.0), 3),
        }

        obs_tokens = _extract_tokens(f"{tgt_clean} {out_clean} {note_text[:360]}")[:16]
        current_obs = {
            "ts": round(time.time(), 2),
            "app": app_clean,
            "app_ko": app_ko,
            "action": act_clean,
            "label": tgt_clean,
            "tokens": obs_tokens,
            "metrics": obs_metrics,
            "summary": out_clean,
        }

        # Compare & Contrast BEFORE appending current_obs!
        comp = self._compare_with_prior_observations(current_obs)
        self.recent_observations.append(current_obs)
        self.recent_observations = self.recent_observations[-24:]

        # Continuous 6D affective-cognitive shift driven by both modality and discovered contrast
        c_boost = float(comp["contrast_score"]) if comp else d_val
        if app_clean == "physics_lab":
            target_vec6 = [0.62, 0.06, _clamp(0.76 + 0.20 * c_boost, 0.2, 0.98), _clamp(0.46 + 0.32 * d_val, 0.2, 0.92), 0.22, _clamp(0.74 + 0.20 * c_boost, 0.2, 0.96)]
        elif app_clean == "knowledge_browser":
            target_vec6 = [0.64, 0.05, _clamp(0.84 + 0.12 * c_boost, 0.3, 0.98), 0.28, 0.26, _clamp(0.84 + 0.12 * c_boost, 0.3, 0.98)]
        elif app_clean == "harmony_pad":
            target_vec6 = [_clamp(0.76 + 0.18 * d_val, 0.3, 0.98), 0.06, 0.64, _clamp(0.58 + 0.26 * d_val, 0.2, 0.94), 0.34, 0.58]
        elif app_clean == "notepad":
            target_vec6 = [0.72, 0.07, 0.70, 0.24, 0.36, 0.88]
        else:
            target_vec6 = [0.64, 0.06, 0.74, 0.44, 0.28, 0.68]

        for i in range(6):
            pull = 0.42 * (target_vec6[i] - self.emotion[i])
            self.velocity[i] = 0.20 * self.velocity[i] + pull
            self.emotion[i] = _clamp(self.emotion[i] + self.velocity[i], 0.04, 0.98)

        weights = self._compute_scene_weights()
        self.scene_mood = max(weights.items(), key=lambda kv: kv[1])[0]
        self.last_prediction_error = round(c_boost, 4)
        self.bond_depth = _clamp(self.bond_depth + 0.006 + 0.008 * c_boost, 0.04, 1.0)

        src_key = re.sub(r"[^0-9A-Za-z가-힣_]+", "_", f"{app_ko}_{act_clean}").strip("_").lower()[:34] or "os_행동"
        dst_key = re.sub(r"[^0-9A-Za-z가-힣_]+", "_", tgt_clean).strip("_").lower()[:34] or "관측결과"

        self._upsert_concept(
            dst_key,
            self.emotion,
            definition=f"스스로 관측({app_ko}): {out_clean}",
            origin="browser_os_sandbox",
            mass_gain=0.16 + 0.14 * c_boost,
        )
        self._upsert_edge(
            src_key,
            dst_key,
            relation="OS놀이터 인과",
            summary=f"[{app_ko}] {act_clean} → {out_clean}",
            weight_gain=0.28 + 0.22 * d_val,
        )

        # Write real Compare & Contrast edges permanently into L1 graph!
        traversed_list = [f"{src_key} → {dst_key} (OS놀이터 인과)"]
        learned_list = [f"+자율관측 '{tgt_clean}' ({app_ko})"]
        if comp is not None:
            self.last_comparison = comp
            self.last_autonomous_intent = {
                "next_app": comp["next_app"],
                "reason": comp["next_reason"],
                "topic_hint": comp["topic_hint"],
            }
            prev_key = re.sub(r"[^0-9A-Za-z가-힣_]+", "_", comp["previous_label"]).strip("_").lower()[:34] or "이전관측"
            if comp["shared_tokens"] or comp["contrast_score"] < 0.45:
                self._upsert_edge(
                    prev_key,
                    dst_key,
                    relation="비교·공통",
                    summary=comp["similarities"][:120],
                    weight_gain=0.32,
                )
                traversed_list.append(f"{prev_key} ↔ {dst_key} (비교·공통)")
            self._upsert_edge(
                prev_key,
                dst_key,
                relation="비교·대조",
                summary=comp["differences"][:120],
                weight_gain=0.30 + 0.25 * comp["contrast_score"],
            )
            traversed_list.append(f"{prev_key} ≠ {dst_key} (비교·대조 Δ={comp['contrast_score']:.2f})")
            learned_list.append(f"★비교대조 '{comp['previous_label']} vs {comp['current_label']}'")
        else:
            self.last_autonomous_intent = {
                "next_app": "physics_lab" if app_clean == "knowledge_browser" else "knowledge_browser",
                "reason": f"방금 세운 첫 기준점 '{tgt_clean}'과 비교·대조할 두 번째 현상을 스스로 찾아보려 한다.",
                "topic_hint": "",
            }

        learned_extra = 0
        if note_text and note_text.strip():
            res = self._learn_from_sentences(
                note_text.strip()[:2400],
                self.emotion,
                origin="browser_os_sandbox",
                source_label=f"OS:{app_ko}",
            )
            learned_extra = len(res["new_concepts"])

        # Feed observation silently into PlasticSelfManifold, QualitativeField & ToolForge (NEVER overwrite human dialogue!)
        self.plastic_self.experience(
            text=f"{tgt_clean} {out_clean}",
            tokens=[dst_key],
            sensed_vec6=target_vec6,
            source="observation",
            contrast_hint=c_boost,
        )
        note_clean = (note_text or "").strip()
        if note_clean:
            self.qualitative_field.absorb_text(note_clean[:500])
            self.tool_forge.distill_from_text(note_clean[:500], source_name=tgt_clean[:20] or app_ko)
            self.lang_engine.absorb_real_korean(note_clean[:600], source=f"OS:{app_ko}", topic=tgt_clean[:20] or app_ko)

        if comp is not None:
            sandbox_reflection = (
                f"'{comp['previous_label']}' vs '{comp['current_label']}' — "
                f"같은 점: {comp['similarities']} / 다른 점: {comp['differences']}"
            )
        else:
            sandbox_reflection = f"'{app_ko}'에서 '{tgt_clean}' 첫 기준점 관측 ({out_clean})"

        self.save_memory()

        rotor_snapshot = None
        if rotor_engine is not None:
            try:
                rotor_snapshot = rotor_engine.step_t1_to_t4(
                    {
                        "vision": {
                            "label": f"자율비교:{tgt_clean[:16]}",
                            "structure": round(obs_metrics["order"], 4),
                            "motion": round(obs_metrics["flux"], 4),
                            "contrast": round(c_boost, 4),
                            "coherence": round(1.0 - min(0.85, c_boost), 4),
                        },
                        "language": {
                            "label": f"자율관측:{act_clean[:16]}",
                            "text": sandbox_reflection[:180],
                        },
                    }
                )
            except Exception:
                rotor_snapshot = None

        out = self.get_state(rotor_state=rotor_snapshot)
        out["sandbox_reflection"] = sandbox_reflection
        return out

    def _auto_ground_if_sparse(self) -> None:
        """
        If the concept graph only has tiny innate seeds, silently absorb local workspace
        documentation ONCE (zero API, ~25ms) so the Micro-Rotor explores real concepts &
        principles rather than spinning in an empty void.
        """
        learned_n = sum(1 for v in self.concepts.values() if v.get("origin") != "innate_sensor")
        if learned_n >= 12 or "AGENTS.md" in self.digested_sources:
            return
        candidate_files = [
            REPO_ROOT / "AGENTS.md",
            REPO_ROOT / "README.md",
        ]
        study_vec = [0.64, 0.07, 0.90, 0.22, 0.28, 0.92]
        for fpath in candidate_files:
            if fpath.exists() and fpath.is_file():
                try:
                    raw = fpath.read_text(encoding="utf-8", errors="ignore")
                    cleaned = re.sub(r"[#`*>\-\[\]()]", " ", raw[:4000])
                    if cleaned.strip():
                        self._learn_from_sentences(
                            cleaned,
                            study_vec,
                            origin="background_grounding",
                            source_label=fpath.name,
                        )
                        if fpath.name not in self.digested_sources:
                            self.digested_sources.append(fpath.name)
                except Exception:
                    continue

    def run_micro_meso_burst(
        self,
        *,
        trials: int = 72,
        surface_macro: bool = False,
    ) -> Dict[str, Any]:
        """
        3-Timescale High-Speed Background Cognition Burst (100% Pure Python · Zero External API):
          - Micro-Rotor: Runs `trials` real sub-millisecond thought experiments:
              (A) Counterfactual coupled-oscillator resonance & phase-cliff sweeps
              (B) Combinatorial concept-graph 2-hop bridge (A-M-B) & high-contrast polarity (A!=B) searches
          - Meso-Rotor: Condenses the `trials` batch via MDL into the single highest-signal
              bridge, polarity, or phase-transition boundary, permanently strengthening the graph.
          - Macro-Rotor (when `surface_macro=True` and user is not mid-conversation):
              Surfaces ONLY the distilled epiphany into calm human-time consciousness & 6D mood!
        """
        t0 = time.perf_counter()
        n_trials = max(16, min(400, int(trials)))

        with self._lock:
            self._auto_ground_if_sparse()

            # Build lightweight adjacency map for genuine 2-hop transitive bridge discovery
            adj: Dict[str, Set[str]] = {}
            for e in self.edges.values():
                s = e.get("src", "")
                d = e.get("dst", "")
                if s and d and s != d:
                    adj.setdefault(s, set()).add(d)
                    adj.setdefault(d, set()).add(s)

            learned_keys = [
                k for k, v in self.concepts.items()
                if v.get("origin") != "innate_sensor" and len(k) >= 2
            ]
            if len(learned_keys) < 6:
                learned_keys = list(self.concepts.keys())

            phys_trials = n_trials // 2
            graph_trials = n_trials - phys_trials

            # --- 1) MICRO-ROTOR (A): Real Structural-Variation, Qualitative Mutation & Cross-Discipline Synthesis ---
            struct_disc = self.structural_rotor.run_structural_batch(pairs=max(8, phys_trials // 2))
            self.qualitative_field.run_qualitative_mutation()
            if self.meso_invariants_count > 0 and self.meso_invariants_count % 5 == 0:
                self.tool_forge.synthesize_hybrid_tool()
            if self.meso_invariants_count > 0 and self.meso_invariants_count % 9 == 0:
                try:
                    w_bg = self.lang_engine.autonomous_background_read(candidate_topics=learned_keys[:8])
                    if w_bg and w_bg.get("summary"):
                        self.qualitative_field.absorb_text(w_bg["summary"][:300])
                        self.tool_forge.distill_from_text(w_bg["summary"][:300], source_name=w_bg.get("title", "위키"))
                except Exception:
                    pass

            # --- 2) MICRO-ROTOR (B): Real Combinatorial Concept Bridge & Polarity Search ---
            best_bridge: Optional[Tuple[float, str, str, str, float]] = None  # (score, a, m, b, cos)
            best_contrast: Optional[Tuple[float, str, str, float]] = None    # (div, a, b, cos)

            if len(learned_keys) >= 4:
                k_len = len(learned_keys)
                for _ in range(graph_trials):
                    a = learned_keys[random.randrange(k_len)]
                    b = learned_keys[random.randrange(k_len)]
                    if a == b:
                        continue
                    va = self.concepts[a]["vec6"]
                    vb = self.concepts[b]["vec6"]
                    cos_ab = _cos6(va, vb)
                    # Check for hidden 2-hop bridge A -- M -- B when no direct edge exists!
                    direct = (f"{a}->{b}" in self.edges) or (f"{b}->{a}" in self.edges)
                    shared_m = (adj.get(a, set()) & adj.get(b, set())) if not direct else set()
                    if shared_m:
                        m = next(iter(shared_m))
                        b_score = cos_ab + 0.25 * min(2.0, float(self.concepts[a].get("mass", 0.5)) + float(self.concepts[b].get("mass", 0.5)))
                        if best_bridge is None or b_score > best_bridge[0]:
                            best_bridge = (b_score, a, m, b, cos_ab)
                    # Check sharpest conceptual polarity / contrast
                    mass_gap = abs(float(self.concepts[a].get("mass", 0.5)) - float(self.concepts[b].get("mass", 0.5)))
                    div = (1.0 - cos_ab) + 0.12 * min(1.5, mass_gap)
                    if best_contrast is None or div > best_contrast[0]:
                        best_contrast = (div, a, b, cos_ab)

            # --- 3) MESO-ROTOR: MDL Condensation into 1 High-Signal Structural / Conceptual Discovery ---
            self.micro_trials_total += n_trials
            self.meso_invariants_count += 1
            elapsed_burst = max(0.001, time.perf_counter() - t0)
            inst_rate = n_trials / max(0.25, elapsed_burst)  # sustainable real throughput across 4Hz daemon
            self.micro_trials_per_sec = round(
                0.65 * self.micro_trials_per_sec + 0.35 * inst_rate
                if self.micro_trials_per_sec > 0
                else inst_rate,
                1,
            )

            # Prioritize real structural-variation flip discoveries, rotating with 2-hop bridges & contrasts
            mode_pick = self.meso_invariants_count % 3
            if mode_pick == 0 and best_bridge is not None:
                _, a, m, b, cos_ab = best_bridge
                kind = "2홉 개념 교량 발견"
                pair_str = f"{a} ↔ {b} (매개: {m})"
                sim_str = f"둘 다 '{m}'을(를) 매개로 맞물리며 위상 유사도 {cos_ab:.2f}를 공유함"
                diff_str = f"직접 연결 없던 '{a}'와 '{b}' 사이에 새 전이 경로를 포착함"
                contrast_val = round(_clamp(1.0 - cos_ab + 0.22, 0.14, 0.92), 3)
                self._upsert_edge(a, b, relation="미시사고·교량", summary=f"'{m}' 경유 발견", weight_gain=0.26)
                prev_lbl, cur_lbl = a, b
                next_app, topic_hint = "knowledge_browser", b
            elif mode_pick == 1 and best_contrast is not None:
                div, a, b, cos_ab = best_contrast
                kind = "고대비 개념 대조"
                pair_str = f"{a} ≠ {b}"
                sim_str = f"같은 기억 원장 안에서 공존하며 위상 내적 {cos_ab:.2f}를 형성함"
                diff_str = f"의미 결이 크게 갈라짐 (대비 Δ={min(0.98, div):.2f})"
                contrast_val = round(_clamp(div, 0.18, 0.96), 3)
                self._upsert_edge(a, b, relation="미시사고·대조", summary=diff_str, weight_gain=0.22)
                prev_lbl, cur_lbl = a, b
                next_app, topic_hint = "physics_lab", a
            else:
                kind = f"구조 변이 · {struct_disc['flip_axis_ko']}"
                pair_str = f"{struct_disc['change']} ⇒ {struct_disc['regime_from']}→{struct_disc['regime_to']}"
                sim_str = f"동일 제약({struct_disc['held_constant']}) 아래에서 비교 검증함"
                diff_str = struct_disc["outcome_shift"]
                contrast_val = float(struct_disc["contrast_score"])
                self._upsert_edge(
                    struct_disc["regime_from"],
                    struct_disc["regime_to"],
                    relation=struct_disc["flip_axis_ko"],
                    summary=struct_disc["change"][:100],
                    weight_gain=0.26,
                )
                prev_lbl, cur_lbl = struct_disc["regime_from"], struct_disc["regime_to"]
                next_app, topic_hint = "physics_lab", ""

            distill = {
                "ts": round(time.time(), 2),
                "kind": kind,
                "pair": pair_str,
                "similarities": sim_str,
                "differences": diff_str,
                "contrast_score": contrast_val,
                "trials_condensed": n_trials,
                "total_trials": self.micro_trials_total,
            }
            self.meso_distillations.append(distill)
            self.meso_distillations = self.meso_distillations[-10:]

            self.last_comparison = {
                "current_label": cur_lbl,
                "previous_label": prev_lbl,
                "current_app": "micro_rotor",
                "previous_app": "meso_rotor",
                "shared_tokens": [],
                "distinct_current": [cur_lbl],
                "distinct_previous": [prev_lbl],
                "similarities": sim_str,
                "differences": diff_str,
                "contrast_score": contrast_val,
                "next_app": next_app,
                "next_reason": f"배경 사고실험({self.micro_trials_total:,}회 누적) 중 포착한 [{kind}: {pair_str}]을 표층에서 직접 검증하려 한다.",
                "topic_hint": topic_hint,
            }
            self.last_autonomous_intent = {
                "next_app": next_app,
                "reason": self.last_comparison["next_reason"],
                "topic_hint": topic_hint,
            }
            self._bg_dirty = True

            # --- 4) MACRO-ROTOR: Quietly nourish subconscious inner mood without spamming or erasing human conversation! ---
            now = time.time()
            user_quiet = (now - self._last_user_converse_ts) > 10.0
            if surface_macro and user_quiet:
                self.macro_epiphanies_count += 1
                self._last_macro_surface_ts = now
                self.plastic_self.experience(
                    text=f"{kind} {pair_str}",
                    tokens=[prev_lbl, cur_lbl],
                    source="background_thought",
                    contrast_hint=contrast_val,
                )

            return distill

    def _background_rotor_loop(self) -> None:
        while self._bg_running:
            time.sleep(0.25)
            if not self._bg_running or self._bg_paused:
                continue
            try:
                now = time.time()
                should_surface = (now - self._last_macro_surface_ts) >= 6.5
                self.run_micro_meso_burst(trials=64, surface_macro=should_surface)
                if self._bg_dirty and (now - self._last_bg_save_ts) >= 12.0:
                    with self._lock:
                        self.save_memory()
                        self._bg_dirty = False
                        self._last_bg_save_ts = now
            except Exception:
                continue

    def start_background_rotor(self) -> None:
        with self._lock:
            if self._bg_running and self._bg_thread is not None and self._bg_thread.is_alive():
                return
            self._bg_running = True
            self._bg_paused = False
            # Run one immediate burst right on boot so state is ALREADY alive at t=0!
            self.run_micro_meso_burst(trials=96, surface_macro=True)
            self._bg_thread = threading.Thread(
                target=self._background_rotor_loop,
                name="elysia-micro-meso-rotor",
                daemon=True,
            )
            self._bg_thread.start()

    def set_background_paused(self, paused: bool) -> Dict[str, Any]:
        with self._lock:
            self._bg_paused = bool(paused)
            return self.get_state()

    def get_state(self, rotor_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        with self._lock:
            weights = self._compute_scene_weights()
            emotion_map = {ax: round(self.emotion[i], 4) for i, ax in enumerate(EMOTION_AXES)}
            recent_eps = [
                {
                    "turn": ep.get("turn"),
                    "user_message": ep.get("user_message", ""),
                    "spoken_reply": ep.get("spoken_reply", ""),
                    "scene_mood": ep.get("scene_mood", "serene"),
                    "scene_label_ko": SCENE_LABELS_KO.get(ep.get("scene_mood", "serene"), "평온한 경청"),
                    "criteria_revision": ep.get("criteria_revision", ""),
                }
                for ep in self.episodes[-6:]
            ]

            learned_concepts = [
                {
                    "token": k,
                    "mass": round(float(v.get("mass", 0.0)), 2),
                    "count": int(v.get("count", 1)),
                    "definition": (v.get("definitions") or [""])[-1],
                    "origin": v.get("origin", "learned_dialogue"),
                }
                for k, v in self.concepts.items()
                if v.get("origin") != "innate_sensor"
            ]
            learned_concepts.sort(key=lambda item: (item["mass"], item["count"]), reverse=True)

            top_edges = sorted(
                self.edges.values(),
                key=lambda e: float(e.get("weight", 0.0)),
                reverse=True,
            )[:12]

            return {
                "status": "ok",
                "autonomous_local": True,
                "external_llm_used": False,
                "turn_count": self.turn_count,
                "surface_revision": self.surface_revision,
                "memory_count": len(self.episodes),
                "concept_count": len(self.concepts),
                "learned_concept_count": len(learned_concepts),
                "edge_count": len(self.edges),
                "clause_count": len(self.clauses),
                "digested_sources": list(self.digested_sources[-10:]),
                "bond_depth": round(self.bond_depth, 4),
                "last_prediction_error": round(self.last_prediction_error, 4),
                "scene_mood": self.scene_mood,
                "scene_label_ko": (
                    self.plastic_self.feelings[0]["name"]
                    if self.plastic_self.feelings
                    else SCENE_LABELS_KO.get(self.scene_mood, "고요한 이끌림")
                ),
                "dominant_feeling": (
                    self.plastic_self.feelings[0]["name"]
                    if self.plastic_self.feelings
                    else "고요한 이끌림"
                ),
                "scene_weights": weights,
                "emotion_field": emotion_map,
                "plastic_self": self.plastic_self.get_public_state(),
                "qualitative_spectra": self.qualitative_field.get_public_state(),
                "discipline_tools": self.tool_forge.get_public_state(),
                "language_engine": self.lang_engine.get_public_state(),
                "structural_experiments": self.structural_rotor.get_public_state(),
                "scale_articulation": self.plastic_self.last_scale_articulation,
                "conversation_history": list(self.conversation_history[-30:]),
                "dialogue": str(self.last_causal_trace.get("spoken_reply", "")),
                "causal_trace": self.last_causal_trace,
                "self_criteria": list(self.self_criteria[-6:]),
                "unresolved_curiosities": list(self.unresolved_curiosities[-4:]),
                "suggested_curiosity_topics": list(
                    dict.fromkeys(
                        [t for t in self.last_causal_trace.get("unknown_tokens", []) if len(t) >= 2]
                        + [c["token"] for c in learned_concepts[:6] if len(c["token"]) >= 2]
                    )
                )[:8],
                "last_comparison": self.last_comparison,
                "autonomous_intent": self.last_autonomous_intent,
                "observation_count": len(self.recent_observations),
                "multi_rotor": {
                    "running": self._bg_running and not self._bg_paused,
                    "paused": self._bg_paused,
                    "micro_trials_total": self.micro_trials_total,
                    "micro_trials_per_sec": round(self.micro_trials_per_sec, 1),
                    "meso_invariants_count": self.meso_invariants_count,
                    "macro_epiphanies_count": self.macro_epiphanies_count,
                    "recent_distillations": list(self.meso_distillations[-6:]),
                },
                "recent_memories": recent_eps,
                "top_concepts": learned_concepts[:14],
                "top_edges": [
                    {
                        "src": e["src"],
                        "dst": e["dst"],
                        "relation": e["relation"],
                        "weight": round(float(e.get("weight", 0.0)), 2),
                    }
                    for e in top_edges
                ],
                "last_corpus_digest": getattr(self, "last_corpus_digest", None),
                "cross_corpus_invariants": sorted(
                    [
                        {"symbol": k, "corpora": list(v), "span": len(v)}
                        for k, v in self.corpus_symbol_index.items()
                        if len(v) >= 2
                    ],
                    key=lambda x: x["span"],
                    reverse=True,
                )[:12],
                "optimization": {
                    "runtime_if_branches": 0,
                    "continuous_emotion_axes": 6,
                    "open_ended_cognition": True,
                    "zero_api_cost": True,
                },
                "rotor_state": rotor_state,
            }


_DEFAULT_COMPANION = LivingCompanionField()


def start_companion_background_rotor() -> None:
    _DEFAULT_COMPANION.start_background_rotor()


def handle_companion_rotor_mode(*, paused: Optional[bool] = None, burst_trials: int = 0) -> Dict[str, Any]:
    with _DEFAULT_COMPANION._lock:
        if paused is not None:
            _DEFAULT_COMPANION.set_background_paused(bool(paused))
        if burst_trials > 0:
            _DEFAULT_COMPANION.run_micro_meso_burst(trials=burst_trials, surface_macro=True)
        return _DEFAULT_COMPANION.get_state()


def handle_companion_apply_tool(*, target_text: str = "", tool_id: Optional[str] = None) -> Dict[str, Any]:
    with _DEFAULT_COMPANION._lock:
        app = _DEFAULT_COMPANION.tool_forge.apply_tool(target_text, preferred_tool_id=tool_id or None)
        _DEFAULT_COMPANION.save_memory()
        out = _DEFAULT_COMPANION.get_state()
        out["applied_tool_result"] = app
        return out


def handle_companion_learn_world(*, topic: str = "") -> Dict[str, Any]:
    with _DEFAULT_COMPANION._lock:
        clean_t = (topic or "").strip()
        if clean_t:
            entry = _DEFAULT_COMPANION.lang_engine.fetch_korean_world_knowledge(clean_t, timeout=3.2)
        else:
            entry = _DEFAULT_COMPANION.lang_engine.autonomous_background_read()
        if entry:
            blob = f"{entry.get('summary', '')} {entry.get('detail', '')}".strip()
            if blob:
                _DEFAULT_COMPANION._learn_from_sentences(
                    blob,
                    _DEFAULT_COMPANION.emotion,
                    origin="world_wiki_reading",
                    source_label=entry.get("source", "한국어 위키백과"),
                )
                _DEFAULT_COMPANION.qualitative_field.absorb_text(blob[:500])
                _DEFAULT_COMPANION.tool_forge.distill_from_text(blob[:500], source_name=entry.get("title", clean_t or "위키"))
            _DEFAULT_COMPANION.save_memory()
        out = _DEFAULT_COMPANION.get_state()
        out["world_reading_result"] = entry
        return out


def handle_companion_distill_weights(
    *,
    source_name: str = "오픈 가중치 슬라이스",
    weight_vectors: Optional[Dict[str, List[float]]] = None,
) -> Dict[str, Any]:
    with _DEFAULT_COMPANION._lock:
        res = _DEFAULT_COMPANION.lang_engine.distill_external_weights(
            weight_vectors or {},
            source_name=source_name or "오픈 가중치 슬라이스",
        )
        _DEFAULT_COMPANION.save_memory()
        out = _DEFAULT_COMPANION.get_state()
        out["weight_distill_result"] = res
        return out


def handle_companion_state() -> Dict[str, Any]:
    return _DEFAULT_COMPANION.get_state()


def handle_companion_converse(*, engine: Any = None, message: str = "") -> Dict[str, Any]:
    with _DEFAULT_COMPANION._lock:
        return _DEFAULT_COMPANION.converse(message=message, rotor_engine=engine)


def handle_companion_digest(
    *,
    engine: Any = None,
    source_name: str = "직접 입력한 글",
    text: str = "",
    read_workspace: bool = False,
) -> Dict[str, Any]:
    with _DEFAULT_COMPANION._lock:
        _DEFAULT_COMPANION.surface_revision += 1
        return _DEFAULT_COMPANION.digest_knowledge(
            source_name=source_name,
            text=text,
            read_workspace=read_workspace,
            rotor_engine=engine,
        )


def handle_companion_digest_corpus(
    *,
    engine: Any = None,
    digest: Optional[Dict[str, Any]] = None,
    scan_workspace: bool = False,
) -> Dict[str, Any]:
    with _DEFAULT_COMPANION._lock:
        _DEFAULT_COMPANION.surface_revision += 1
        return _DEFAULT_COMPANION.digest_corpus(
            digest=digest,
            scan_workspace=scan_workspace,
            rotor_engine=engine,
        )


def handle_companion_observe_frame(
    *,
    engine: Any = None,
    frame: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    with _DEFAULT_COMPANION._lock:
        return _DEFAULT_COMPANION.observe_sensory_frame(frame=frame or {}, rotor_engine=engine)


def handle_companion_digest_sensorimotor(
    *,
    engine: Any = None,
    log: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    with _DEFAULT_COMPANION._lock:
        _DEFAULT_COMPANION.surface_revision += 1
        return _DEFAULT_COMPANION.digest_sensorimotor_log(log=log or {}, rotor_engine=engine)


def handle_companion_sandbox_action(
    *,
    engine: Any = None,
    app: str = "desktop",
    action: str = "explore",
    target: str = "",
    outcome: str = "",
    delta: float = 0.25,
    note_text: str = "",
    metrics: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    with _DEFAULT_COMPANION._lock:
        return _DEFAULT_COMPANION.record_sandbox_action(
            app=app,
            action=action,
            target=target,
            outcome=outcome,
            delta=delta,
            note_text=note_text,
            metrics=metrics,
            rotor_engine=engine,
        )


def handle_companion_feedback(*, signal: str = "resonate", correction: str = "") -> Dict[str, Any]:
    with _DEFAULT_COMPANION._lock:
        _DEFAULT_COMPANION.surface_revision += 1
        return _DEFAULT_COMPANION.apply_feedback(signal=signal, correction=correction)


def handle_companion_reset() -> Dict[str, Any]:
    with _DEFAULT_COMPANION._lock:
        return _DEFAULT_COMPANION.reset_memory()
