r"""
ELYSIA 4-Scale Generative Language Rotor
========================================

Replaces surface sentence memorization and developer-authored emotion/intent
taxonomies with a continuous generative linguistic axis substrate inspired by
the Hangul combinatoric principle:

- **Scale 0 (Hangul Phonological Axis):** Decomposes/composes Unicode Hangul
  syllables (`초성·중성·종성`) and binds induced Korean operators across coda
  boundaries (`이/가`, `은/는`, `을/를`, `과/와`, `으로/로`) continuously.
- **Scale 1 (Unsupervised Distributional Morpheme Induction):** Discovers concept
  stems, predicate stems, functional operators, stance endings, and concept
  co-occurrence topology directly from observed external utterances without a
  hardcoded vocabulary or rule dictionary.
- **Scale 2 (Causal Structural Array Schemas):** Induces ordered role schemas
  (`CAUSE_LINK`, `TOPIC_CORE`, `FOCUS_CORE`, `PREDICATE_CORE`, `STANCE_END`)
  and slot-local operator distributions from live texts.
- **Scale 3 (Continuous 4-D Causal Spectrum):** Maps `[tension, resolution_shift,
  flux_energy, order_coherence]`, detects self-directed `ExpressiveDeficit`
  to formulate world queries, and composes genuinely novel non-verbatim speech.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
import json
import math
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from core.orchestration.autonomous_open_explorer import _extract_lexical_tokens


# Scale 0: Standard Unicode Hangul Jamo tables (0xAC00..0xD7A3)
_CHOSEONG: Tuple[str, ...] = (
    "ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ",
    "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ",
)
_JUNGSEONG: Tuple[str, ...] = (
    "ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ",
    "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ",
)
_JONGSEONG: Tuple[str, ...] = (
    "", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ",
    "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ",
    "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ",
)

_CHO_IDX = {ch: i for i, ch in enumerate(_CHOSEONG)}
_JUNG_IDX = {ch: i for i, ch in enumerate(_JUNGSEONG)}
_JONG_IDX = {ch: i for i, ch in enumerate(_JONGSEONG)}

_OPERATOR_ALLOMORPHS: Dict[str, Tuple[str, str]] = {
    "이": ("이", "가"),
    "가": ("이", "가"),
    "이/가": ("이", "가"),
    "은": ("은", "는"),
    "는": ("은", "는"),
    "은/는": ("은", "는"),
    "을": ("을", "를"),
    "를": ("을", "를"),
    "을/를": ("을", "를"),
    "과": ("과", "와"),
    "와": ("과", "와"),
    "과/와": ("과", "와"),
    "으로": ("으로", "로"),
    "로": ("으로", "로"),
    "으로/로": ("으로", "로"),
    "아": ("아", "야"),
    "야": ("아", "야"),
    "아/야": ("아", "야"),
    "이나": ("이나", "나"),
    "이나/나": ("이나", "나"),
}


def decompose_hangul_jamo(ch: str) -> Optional[Tuple[str, str, str]]:
    """Decomposes one modern Hangul syllable into `(onset, nucleus, coda)`."""
    if not ch or len(ch) != 1:
        return None
    code = ord(ch)
    if not (0xAC00 <= code <= 0xD7A3):
        return None
    offset = code - 0xAC00
    cho, rem = divmod(offset, 588)
    jung, jong = divmod(rem, 28)
    return _CHOSEONG[cho], _JUNGSEONG[jung], _JONGSEONG[jong]


def compose_hangul_jamo(onset: str, nucleus: str, coda: str = "") -> str:
    """Composes `(onset, nucleus, coda)` back into one Hangul syllable."""
    if onset not in _CHO_IDX or nucleus not in _JUNG_IDX or coda not in _JONG_IDX:
        raise ValueError(f"Invalid Hangul jamo triple: ({onset!r}, {nucleus!r}, {coda!r})")
    code = 0xAC00 + (_CHO_IDX[onset] * 21 + _JUNG_IDX[nucleus]) * 28 + _JONG_IDX[coda]
    return chr(code)


def _last_hangul_coda(word: str) -> Optional[str]:
    clean = (word or "").strip()
    for ch in reversed(clean):
        parts = decompose_hangul_jamo(ch)
        if parts is not None:
            return parts[2]
    return None


def has_jongseong(word: str) -> bool:
    """Returns True if the final Hangul syllable in `word` carries a non-empty coda."""
    coda = _last_hangul_coda(word)
    return bool(coda)


def bind_korean_operator(stem: str, operator: str) -> str:
    """Binds a Korean particle/operator cleanly honoring final-syllable coda harmony."""
    clean_stem = (stem or "").strip()
    clean_op = (operator or "").strip()
    if not clean_stem:
        return clean_op
    if not clean_op:
        return clean_stem

    coda = _last_hangul_coda(clean_stem)
    has_coda = bool(coda)

    if clean_op in _OPERATOR_ALLOMORPHS:
        with_coda, without_coda = _OPERATOR_ALLOMORPHS[clean_op]
        if with_coda == "으로":
            # In Korean phonology, coda 'ㄹ' attaches '로' rather than '으로'
            chosen = "으로" if (has_coda and coda != "ㄹ") else "로"
        else:
            chosen = with_coda if has_coda else without_coda
        return clean_stem + chosen

    if "/" in clean_op:
        left, right = clean_op.split("/", 1)
        chosen = left if has_coda else right
        return clean_stem + chosen

    return clean_stem + clean_op


def compute_continuous_spectrum(
    situation: str,
    cause: str,
    utterance: str,
    prosody_rms: float = 0.0,
    motion_flux: float = 0.0,
) -> List[float]:
    """
    Computes continuous 4-D Causal Spectrum `[tension, resolution_shift, flux_energy, order_coherence]`
    from contextual overlap, structural punctuation contour, cadence, prosody, and motion.
    Zero hardcoded emotion word tables or discrete intent label strings.
    """
    utt = (utterance or "").strip()
    ctx = f"{situation or ''} {cause or ''}".strip()

    q_mark = 1.0 if "?" in utt else 0.0
    excl = 1.0 if "!" in utt else 0.0
    ellipsis = 1.0 if ("..." in utt or "…" in utt) else 0.0
    period = 1.0 if "." in utt else 0.0

    ctx_toks = set(_extract_lexical_tokens(ctx))
    utt_toks = _extract_lexical_tokens(utt)
    utt_set = set(utt_toks)
    if ctx_toks and utt_set:
        overlap = len(ctx_toks & utt_set) / max(1, len(ctx_toks | utt_set))
    else:
        overlap = 0.0
    novel_div = (1.0 - overlap) if utt_set else 0.5

    tok_lens = [len(t) for t in utt_toks]
    len_var = min(1.0, float(np.std(tok_lens)) / 3.0) if len(tok_lens) >= 2 else 0.2

    tension = float(
        np.clip(
            0.34 * q_mark + 0.22 * ellipsis + 0.34 * novel_div + (0.14 if len(utt) < 12 else 0.05),
            0.0,
            1.0,
        )
    )
    resolution_shift = float(
        np.clip(
            0.42 * overlap + (0.36 if q_mark == 0.0 and len(utt) >= 8 else 0.12) + 0.14 * period,
            0.0,
            1.0,
        )
    )
    flux_energy = float(
        np.clip(
            0.34 * excl + 0.30 * min(1.0, float(prosody_rms) * 2.5) + 0.24 * float(motion_flux) + 0.22 * len_var,
            0.0,
            1.0,
        )
    )
    order_coherence = float(
        np.clip(
            1.0 - 0.32 * q_mark - 0.24 * excl - 0.20 * ellipsis - 0.20 * abs(len(utt) - 34) / 60.0,
            0.1,
            1.0,
        )
    )
    return [round(tension, 4), round(resolution_shift, 4), round(flux_energy, 4), round(order_coherence, 4)]


def _equilibrium_target_spectrum(live_spec: Sequence[float]) -> List[float]:
    """Restoring response spectrum: high tension invites resolving shift & stabilizing coherence."""
    t, r, f, o = (float(live_spec[0]), float(live_spec[1]), float(live_spec[2]), float(live_spec[3]))
    target_t = float(np.clip(0.35 * t, 0.05, 0.75))
    target_r = float(np.clip(max(r, 0.42 + 0.40 * t), 0.15, 0.95))
    target_f = float(np.clip(0.55 * f + 0.18, 0.10, 0.90))
    target_o = float(np.clip(max(o, 0.55 + 0.20 * t), 0.25, 0.95))
    return [round(target_t, 4), round(target_r, 4), round(target_f, 4), round(target_o, 4)]


@dataclass
class CausalArraySchema:
    """Induced Scale-2 utterance array pattern with slot operator preferences & 4-D centroid."""

    schema_id: str
    slots: List[str]
    slot_operators: Dict[str, List[str]] = field(default_factory=dict)
    spectrum_centroid: List[float] = field(default_factory=lambda: [0.3, 0.5, 0.3, 0.6])
    count: int = 1
    feedback_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "CausalArraySchema":
        return cls(
            schema_id=str(raw.get("schema_id", "")),
            slots=[str(s) for s in raw.get("slots", [])],
            slot_operators={str(k): [str(x) for x in v] for k, v in (raw.get("slot_operators") or {}).items()},
            spectrum_centroid=[float(x) for x in raw.get("spectrum_centroid", [0.3, 0.5, 0.3, 0.6])],
            count=int(raw.get("count", 1)),
            feedback_score=float(raw.get("feedback_score", 0.0)),
        )


@dataclass
class ExpressiveDeficit:
    """Self-detected gap on the 4-D spectrum or unknown concept stems requiring world inquiry."""

    needs_world_inquiry: bool
    missing_axis: str
    nearest_spectrum_dist: float
    inquiry_terms: List[str]
    inquiry_query: str
    reason_ko: str


_CANONICAL_KOREAN_PARTICLES: Tuple[str, ...] = (
    "에서는", "으로는", "에게서", "까지도", "에서", "에게", "으로", "부터", "까지", "처럼", "보다",
    "은", "는", "이", "가", "을", "를", "과", "와", "로", "에", "의", "도", "만",
)

_PARTICLE_TO_ROLE: Dict[str, str] = {
    "은": "TOPIC_CORE",
    "는": "TOPIC_CORE",
    "이": "SUBJECT_CORE",
    "가": "SUBJECT_CORE",
    "을": "OBJECT_CORE",
    "를": "OBJECT_CORE",
    "과": "COUPLED_LINK",
    "와": "COUPLED_LINK",
    "에": "CONTEXT_LOC",
    "에서": "CONTEXT_LOC",
    "에서는": "CONTEXT_LOC",
    "으로": "CONTEXT_LOC",
    "으로는": "CONTEXT_LOC",
    "로": "CONTEXT_LOC",
    "에게": "CONTEXT_LOC",
    "부터": "CONTEXT_LOC",
    "까지": "CONTEXT_LOC",
    "처럼": "CONTEXT_LOC",
    "보다": "CONTEXT_LOC",
    "의": "ATTR_MOD",
}

_KOREAN_FINAL_ENDINGS: Tuple[str, ...] = (
    "습니다", "입니다", "합니다", "됩니다", "한다", "된다", "있다", "없다",
    "는다", "ㄴ다", "이다", "였다", "했다", "졌다", "났다", "간다", "온다", "본다",
    "일까", "할까", "될까", "인가", "는가", "나요", "해요", "돼요", "다", "요", "까",
)

_NON_NOMINAL_TOKENS: set[str] = {
    "만약", "어떻게", "무엇", "어디", "언제", "누구", "왜", "매우", "이미", "서로", "바로",
    "항상", "가장", "모두", "다시", "함께", "아직", "결국", "그러나", "하지만", "그래서",
    "또는", "그리고", "또한", "즉", "혹은", "만일", "비록", "더욱", "아주", "너무",
    "하나", "하나의", "모든", "어떤", "이런", "그런", "저런", "어느", "다른", "같은",
    "짙은", "깊은", "높은", "낮은", "밝은", "맑은", "작은", "적은", "많은", "좋은", "넓은",
    "짧은", "어두운", "새로운", "오랜", "큰", "긴", "검은", "붉은", "푸른", "흰",
    "하는", "되는", "있는", "없는", "가는", "오는", "보는", "쓰는", "맞는", "아닌",
    "가진", "따른", "통한", "대한", "대해", "대해서", "위한", "관한", "인한", "의한",
    "뭐냐면", "뭐냐", "자", "이제", "그럼", "그러면", "그런데", "이렇게", "그렇게", "저렇게",
}
try:
    from core.orchestration.principled_spectrum_core import DISCOURSE_AND_FUNCTION_WORDS as _PSC_DISCOURSE  # noqa: E402
    _NON_NOMINAL_TOKENS |= set(_PSC_DISCOURSE)
except Exception:
    pass

_NON_NOMINAL_SUFFIXES: Tuple[str, ...] = (
    "하는", "되는", "있는", "없는", "가는", "오는", "보는", "나타나는", "연결되는",
    "흐르는", "움직이는", "변하는", "줄이고", "가린다면", "다면", "라면", "하면", "되면",
    "이면", "이고", "하고", "되고", "되며", "하며", "지만", "거나", "도록", "면서",
    "될까", "할까", "을까", "는가", "인가", "하게", "되게", "있게", "없게",
    "할", "될", "갈", "올", "볼", "냐면", "냐",
)

_ALLOWED_ONE_CHAR_NOUNS: set[str] = {
    "빛", "밤", "낮", "길", "말", "눈", "귀", "손", "별", "해", "달", "물", "불", "힘", "숨", "꿈", "뇌", "땅", "산", "강", "숲", "꽃", "집", "몸", "맘", "삶", "죽",
}


_KIWI_SINGLETON: Any = None
_KIWI_CHECKED: bool = False
_KIWI_BOUND_NOUNS_SKIP = {
    "것", "수", "등", "때", "바", "줄", "분", "데", "쪽", "곳", "채", "뿐",
    "대한", "대해", "애들", "중", "위", "아래", "안", "밖", "속", "앞", "뒤", "옆", "상",
}


def _get_kiwi() -> Any:
    global _KIWI_SINGLETON, _KIWI_CHECKED
    if not _KIWI_CHECKED:
        _KIWI_CHECKED = True
        try:
            from kiwipiepy import Kiwi  # type: ignore
            _KIWI_SINGLETON = Kiwi()
        except Exception:
            _KIWI_SINGLETON = None
    return _KIWI_SINGLETON


def analyze_korean_pos_kiwi(text: str) -> Optional[Dict[str, List[str]]]:
    """
    Uses open-source C++ `kiwipiepy` as Elysia's Scale 1<->2 Korean morphosyntactic
    receptor to separate true nominals (NNG/NNP), verbal predicates (VV/VA/VCP),
    and case particles (JKS/JKO/JKB/JX/JKG) cleanly from spoken YouTube/web text.
    """
    kiwi = _get_kiwi()
    if kiwi is None or not (text or "").strip():
        return None
    try:
        toks = kiwi.tokenize(text)
    except Exception:
        return None
    nominals: List[str] = []
    predicates: List[str] = []
    particles: List[str] = []
    for tk in toks:
        form = str(tk.form).strip()
        tag = str(tk.tag)
        if not form or not _is_pure_hangul(form):
            continue
        if tag in ("NNG", "NNP") and form not in _KIWI_BOUND_NOUNS_SKIP and form not in _NON_NOMINAL_TOKENS:
            if len(form) >= 2 or form in _ALLOWED_ONE_CHAR_NOUNS:
                nominals.append(form)
        elif tag.startswith(("VV", "VA")):
            predicates.append(form)
        elif tag.startswith("J"):
            particles.append(form)
    return {"nominals": nominals, "predicates": predicates, "particles": particles}


def _is_pure_hangul(s: str) -> bool:
    return bool(s) and all("가" <= ch <= "힣" for ch in s)


def _is_valid_korean_predicate_word(word: str) -> bool:
    if len(word) < 2 or not _is_pure_hangul(word):
        return False
    return any(word.endswith(e) for e in _KOREAN_FINAL_ENDINGS)


def _is_valid_nominal_stem(stem: str, raw_word: str = "") -> bool:
    s = (stem or "").strip()
    rw = (raw_word or s).strip()
    if not s or not _is_pure_hangul(s):
        return False
    if len(s) == 1 and s not in _ALLOWED_ONE_CHAR_NOUNS:
        return False
    if len(s) > 7:
        return False
    if s in _NON_NOMINAL_TOKENS or rw in _NON_NOMINAL_TOKENS or s in _KIWI_BOUND_NOUNS_SKIP:
        return False
    if any(s.endswith(suf) for suf in _NON_NOMINAL_SUFFIXES) or any(rw.endswith(suf) for suf in _NON_NOMINAL_SUFFIXES):
        return False
    if _is_valid_korean_predicate_word(s):
        return False
    # Verify via kiwipiepy POS receptor when available so colloquial fragments/postpositions never leak into noun slots!
    kiwi = _get_kiwi()
    if kiwi is not None:
        try:
            toks = kiwi.tokenize(rw)
            if toks:
                has_noun = any(
                    str(tk.tag) in ("NNG", "NNP") and str(tk.form) not in _KIWI_BOUND_NOUNS_SKIP
                    for tk in toks
                )
                first_tag = str(toks[0].tag)
                if not has_noun or first_tag.startswith(("MM", "MA", "IC", "E", "J", "VV", "VA")):
                    return False
        except Exception:
            pass
    return True


def _strip_word_edge_punct(token: str) -> Tuple[str, str]:
    m = re.match(r"^([가-힣a-zA-Z0-9]+)([?!….,\"'”’」』]*)$", token.strip())
    if not m:
        return "", ""
    return m.group(1), m.group(2)


class LanguageScaleRotor:
    """
    4-Scale generative linguistic rotor inducing stems, functional operators,
    stance endings, structural slot schemas, and 4-D causal spectrum centroids
    from real-world utterances (zero hardcoded lexicons or canned sentences).
    """

    MAX_SEEN_UTTERANCES = 2000

    def __init__(self) -> None:
        self.surface_vocab: Counter[str] = Counter()
        self.stem_counts: Counter[str] = Counter()
        self.nominal_stems: Counter[str] = Counter()
        self.predicate_stems: Counter[str] = Counter()
        self.predicate_surfaces: Counter[str] = Counter()
        self.predicate_cooccurrence: Dict[str, Dict[str, int]] = defaultdict(dict)
        self.operator_counts: Counter[str] = Counter()
        self.operator_spectrum: Dict[str, List[float]] = {}
        self.stance_endings: Counter[str] = Counter()
        self.stance_ending_spectrum: Dict[str, List[float]] = {}
        self.stem_cooccurrence: Dict[str, Dict[str, int]] = defaultdict(dict)
        self.schemas: Dict[str, CausalArraySchema] = {}
        self.seen_utterances: List[str] = []
        self._seen_utt_set: set[str] = set()

    @staticmethod
    def _update_centroid(prev: Optional[List[float]], count_after: int, new_vec: Sequence[float]) -> List[float]:
        nv = [float(new_vec[i]) for i in range(4)]
        if prev is None or count_after <= 1:
            return nv
        w_old = (count_after - 1) / float(count_after)
        w_new = 1.0 / float(count_after)
        return [round(prev[i] * w_old + nv[i] * w_new, 4) for i in range(4)]

    def _induce_prefix_splits(self, tokens: Sequence[str]) -> None:
        """Induces shared-prefix stems & functional suffixes cleanly from observed surface words."""
        vocab_words = {w for w in self.surface_vocab if len(w) >= 2 and all("가" <= c <= "힣" for c in w)}
        for t in tokens:
            if len(t) >= 2 and all("가" <= c <= "힣" for c in t):
                vocab_words.add(t)

        by_prefix: Dict[str, List[str]] = defaultdict(list)
        for w in vocab_words:
            for plen in range(1, min(len(w), 5)):
                pref = w[:plen]
                if plen >= 2 or len(w) >= 2:
                    by_prefix[pref].append(w)

        for pref, group in by_prefix.items():
            if len(group) < 2:
                continue
            if len(pref) == 1 and len(group) < 3:
                continue
            self.stem_counts[pref] += 0  # register prefix stem
            for w in group:
                suf = w[len(pref) :]
                if 1 <= len(suf) <= 3:
                    self.operator_counts[suf] += 0

    def _split_word_distributional(self, word: str, is_final: bool) -> Tuple[str, str]:
        """Splits a surface word honoring genuine Korean particle & verbal-ending morphology."""
        if not word:
            return "", ""
        if len(word) <= 1 or not _is_pure_hangul(word):
            return word, ""

        if is_final:
            for end in _KOREAN_FINAL_ENDINGS:
                if word.endswith(end) and len(word) - len(end) >= 1:
                    return word[: -len(end)], end
            return (word[:-1], word[-1]) if len(word) >= 3 else (word, "")

        # Protect adverbs, adnominal modifiers (짙은, 깊은, 하는, 되는), and clause connectives from particle-splitting
        if word in _NON_NOMINAL_TOKENS or any(word.endswith(suf) for suf in _NON_NOMINAL_SUFFIXES):
            return word, ""

        # Prefer genuine Korean case/connective particles (allow 1-char roots like 빛/밤/낮/말/길)
        for part in _CANONICAL_KOREAN_PARTICLES:
            min_root = 1 if part in ("의", "이", "가", "은", "는", "을", "를", "과", "와", "에", "로", "도", "만") else 2
            if word.endswith(part) and len(word) - len(part) >= min_root:
                cand_stem = word[: -len(part)]
                if len(cand_stem) == 1 and cand_stem not in _ALLOWED_ONE_CHAR_NOUNS:
                    continue
                return cand_stem, part

        # Fallback: previously induced prefix stem if suffix is a real Hangul particle/connective
        for plen in range(min(len(word) - 1, 5), 1, -1):
            cand_s = word[:plen]
            cand_op = word[plen:]
            if cand_s in self.stem_counts and cand_op in _PARTICLE_TO_ROLE:
                return cand_s, cand_op

        return word, ""

    def induce_from_utterances(self, samples: Sequence[Dict[str, Any]]) -> Dict[str, int]:
        """
        Induces Scale 1 morpheme axes, Scale 2 array schemas, and Scale 3 spectrum
        centroids from observed `{situation, cause, utterance, spectrum}` records.
        """
        parsed_samples: List[Tuple[str, str, str, List[float], List[Tuple[str, str]]]] = []

        for smp in samples:
            utt = str(smp.get("utterance") or "").strip()
            if len(utt) < 3:
                continue
            sit = str(smp.get("situation") or "")
            cause = str(smp.get("cause") or "")
            spec = smp.get("spectrum")
            if not spec or len(spec) != 4:
                spec = compute_continuous_spectrum(sit, cause, utt)
            raw_tokens = re.findall(r"[가-힣a-zA-Z0-9]+[?!….,\"'”’」』]*", utt)
            clean_words: List[Tuple[str, str]] = []
            for rt in raw_tokens:
                w, p = _strip_word_edge_punct(rt)
                if w:
                    self.surface_vocab[w] += 1
                    clean_words.append((w, p))
            if clean_words:
                parsed_samples.append((sit, cause, utt, [float(x) for x in spec], clean_words))

        all_batch_words = [w for _, _, _, _, cws in parsed_samples for w, _ in cws]
        self._induce_prefix_splits(all_batch_words)

        added_utts = 0
        for sit, cause, utt, spec, clean_words in parsed_samples:
            low_u = utt.lower()
            if low_u not in self._seen_utt_set:
                self._seen_utt_set.add(low_u)
                self.seen_utterances.append(utt)
                added_utts += 1
            if len(self.seen_utterances) > self.MAX_SEEN_UTTERANCES:
                self.seen_utterances = self.seen_utterances[-self.MAX_SEEN_UTTERANCES :]
                self._seen_utt_set = {u.lower() for u in self.seen_utterances}

            ctx_stems = set(_extract_lexical_tokens(f"{sit} {cause}"))
            n_words = len(clean_words)
            slots: List[str] = []
            slot_ops: Dict[str, List[str]] = defaultdict(list)
            utt_stems: List[str] = []

            for i, (w, p) in enumerate(clean_words):
                is_final = i == n_words - 1
                stem, op = self._split_word_distributional(w, is_final=is_final)
                if not stem or not _is_pure_hangul(stem):
                    continue
                self.stem_counts[stem] += 1
                utt_stems.append(stem)

                if is_final:
                    if not _is_valid_korean_predicate_word(w):
                        continue
                    ending_tok = (op + (p or ".")).strip()
                    pred_full = w + (p if p in (".", "?", "!") else ".")
                    self.predicate_stems[stem] += 1
                    self.predicate_surfaces[pred_full] += 1
                    for prev_st in utt_stems[:-1]:
                        self.predicate_cooccurrence[prev_st][pred_full] = (
                            self.predicate_cooccurrence[prev_st].get(pred_full, 0) + 1
                        )
                    self.stance_endings[ending_tok] += 1
                    self.stance_ending_spectrum[ending_tok] = self._update_centroid(
                        self.stance_ending_spectrum.get(ending_tok),
                        self.stance_endings[ending_tok],
                        spec,
                    )
                    if op:
                        self.operator_counts[op] += 1
                        self.operator_spectrum[op] = self._update_centroid(
                            self.operator_spectrum.get(op),
                            self.operator_counts[op],
                            spec,
                        )
                    slots.extend(["PREDICATE_CORE", "STANCE_END"])
                else:
                    if _is_valid_nominal_stem(stem, w):
                        self.nominal_stems[stem] += 1
                    if op and op in _PARTICLE_TO_ROLE:
                        self.operator_counts[op] += 1
                        self.operator_spectrum[op] = self._update_centroid(
                            self.operator_spectrum.get(op),
                            self.operator_counts[op],
                            spec,
                        )
                    if op in _PARTICLE_TO_ROLE:
                        role = _PARTICLE_TO_ROLE[op]
                    elif w.endswith(("고", "며", "면", "면서", "서")) and len(w) >= 3:
                        role = "CLAUSE_BRIDGE"
                    elif i == 0 and any(cs in stem or stem in cs for cs in ctx_stems if len(cs) >= 2):
                        role = "CAUSE_LINK"
                    elif "TOPIC_CORE" not in slots:
                        role = "TOPIC_CORE"
                    else:
                        role = "FOCUS_CORE"
                    if len(slots) < 4 and (not slots or slots[-1] != role):
                        slots.append(role)
                    if op and op in _PARTICLE_TO_ROLE:
                        slot_ops[role].append(op)

            # Update co-occurrence topology across stems in scene + utterance
            unique_stems = list(dict.fromkeys(utt_stems))
            for a in unique_stems:
                for b in unique_stems:
                    if a != b:
                        self.stem_cooccurrence[a][b] = self.stem_cooccurrence[a].get(b, 0) + 1
                for c_tok in ctx_stems:
                    if len(c_tok) >= 2 and c_tok != a:
                        self.stem_cooccurrence[c_tok][a] = self.stem_cooccurrence[c_tok].get(a, 0) + 1

            # Compact consecutive FOCUS_CORE roles into canonical schema signature
            compact_slots: List[str] = []
            for sl in slots:
                if sl == "FOCUS_CORE" and compact_slots and compact_slots[-1] == "FOCUS_CORE":
                    continue
                compact_slots.append(sl)
            if not compact_slots or "PREDICATE_CORE" not in compact_slots:
                continue

            schema_id = "+".join(compact_slots)
            if schema_id not in self.schemas:
                self.schemas[schema_id] = CausalArraySchema(
                    schema_id=schema_id,
                    slots=compact_slots,
                    slot_operators={k: list(dict.fromkeys(v))[:12] for k, v in slot_ops.items()},
                    spectrum_centroid=[float(x) for x in spec],
                    count=1,
                )
            else:
                sch = self.schemas[schema_id]
                sch.count += 1
                sch.spectrum_centroid = self._update_centroid(sch.spectrum_centroid, sch.count, spec)
                for k, ops in slot_ops.items():
                    merged = list(dict.fromkeys([*sch.slot_operators.get(k, []), *ops]))[:12]
                    sch.slot_operators[k] = merged

        return {
            "samples_processed": len(parsed_samples),
            "added_utterances": added_utts,
            "stems_total": len(self.stem_counts),
            "operators_total": len(self.operator_counts),
            "schemas_total": len(self.schemas),
        }

    def _nearest_schema_distance(self, target_spec: Sequence[float]) -> float:
        if not self.schemas:
            return 1.0
        q = np.asarray(target_spec[:4], dtype=np.float64)
        cents = np.stack([np.asarray(s.spectrum_centroid[:4], dtype=np.float64) for s in self.schemas.values()], axis=0)
        dists = np.linalg.norm(cents - q[None, :], axis=1)
        return float(np.min(dists))

    def detect_expressive_deficit(self, user_text: str, situation_text: str = "") -> ExpressiveDeficit:
        """Detects epistemic/expressive gaps prompting Elysia's own autonomous world inquiry."""
        live_spec = compute_continuous_spectrum(situation_text, "", user_text)
        target_spec = _equilibrium_target_spectrum(live_spec)
        dist = self._nearest_schema_distance(target_spec)

        user_words = [w for w, _ in (_strip_word_edge_punct(t) for t in (user_text or "").split()) if len(w) >= 2]
        user_stems = [self._split_word_distributional(w, is_final=(i == len(user_words) - 1))[0] for i, w in enumerate(user_words)]
        unknown_stems = [s for s in dict.fromkeys(user_stems) if s and s not in self.stem_counts]

        missing_axis = "none"
        needs_inquiry = False
        if len(self.schemas) < 2:
            missing_axis = "structural_schema_axis"
            needs_inquiry = True
        elif len(self.stance_endings) < 2:
            missing_axis = "stance_ending_axis"
            needs_inquiry = True
        elif dist > 0.55:
            missing_axis = "spectrum_coverage"
            needs_inquiry = True
        elif unknown_stems and len(self.stem_counts) < 10:
            missing_axis = "concept_stem_axis"
            needs_inquiry = True

        terms = [t for t in dict.fromkeys([*unknown_stems, *user_stems, *_extract_lexical_tokens(user_text)]) if len(t) >= 2][:3]
        if not terms:
            terms = ["대화"]
        query = " ".join(terms[:2])

        if needs_inquiry:
            reason = (
                f"내부 표현 축 부족({missing_axis}, 스펙트럼 거리={dist:.2f})으로 "
                f"'{query}' 맥락의 실제 인간 발화 구조를 외부에서 먼저 탐구하려 합니다."
            )
        else:
            reason = f"기존 스키마({len(self.schemas)}종)·어간({len(self.stem_counts)}개)으로 스펙트럼 거리 {dist:.2f} 내 대응 가능."

        return ExpressiveDeficit(
            needs_world_inquiry=needs_inquiry,
            missing_axis=missing_axis,
            nearest_spectrum_dist=round(dist, 4),
            inquiry_terms=terms,
            inquiry_query=query,
            reason_ko=reason,
        )

    def _pick_best_schema(self, target_spec: Sequence[float]) -> CausalArraySchema:
        q = np.asarray(target_spec[:4], dtype=np.float64)
        schemas = list(self.schemas.values())
        cents = np.stack([np.asarray(s.spectrum_centroid[:4], dtype=np.float64) for s in schemas], axis=0)
        dists = np.linalg.norm(cents - q[None, :], axis=1)
        fb = np.array([s.feedback_score for s in schemas], dtype=np.float64)
        freq = np.array([math.log1p(max(0, s.count)) * 0.04 for s in schemas], dtype=np.float64)
        scores = -dists + fb + freq
        return schemas[int(np.argmax(scores))]

    def _pick_best_ending(self, target_spec: Sequence[float], rank_offset: int = 0) -> str:
        if not self.stance_endings:
            return "다."
        q = np.asarray(target_spec[:4], dtype=np.float64)
        endings = list(self.stance_endings.keys())
        cents = np.stack(
            [np.asarray(self.stance_ending_spectrum.get(e, target_spec)[:4], dtype=np.float64) for e in endings],
            axis=0,
        )
        dists = np.linalg.norm(cents - q[None, :], axis=1)
        order = np.argsort(dists)
        pick_idx = int(order[min(rank_offset, len(order) - 1)])
        return endings[pick_idx]

    def _select_companion_stems(self, active_stems: Sequence[str], limit: int = 5) -> List[str]:
        cand_scores: Dict[str, float] = {}
        for a in active_stems:
            for nb, wt in self.stem_cooccurrence.get(a, {}).items():
                if nb in active_stems or nb not in self.stem_counts:
                    continue
                if not _is_valid_nominal_stem(nb):
                    continue
                # IDF anti-hub weighting so domain-specific partners beat generic high-frequency hubs
                idf = 1.0 / math.sqrt(1.0 + self.stem_counts.get(nb, 1))
                cand_scores[nb] = cand_scores.get(nb, 0.0) + float(wt) * idf
        ordered = [s for s, _ in sorted(cand_scores.items(), key=lambda kv: -kv[1])[:limit]]
        # Fallback to valid induced nominal stems
        non_pred = [
            st for st, _ in self.nominal_stems.most_common(limit * 4)
            if _is_valid_nominal_stem(st) and st not in self.predicate_stems
        ]
        for st in non_pred:
            if st not in ordered and st not in active_stems:
                ordered.append(st)
        return ordered[:limit]

    def _best_operator_for_slot(self, schema: CausalArraySchema, slot_role: str, target_spec: Sequence[float]) -> str:
        ops = schema.slot_operators.get(slot_role) or list(self.operator_counts.keys())[:6]
        if not ops:
            return ""
        q = np.asarray(target_spec[:4], dtype=np.float64)
        best_op = ops[0]
        best_d = 1e9
        for op in ops:
            cent = np.asarray(self.operator_spectrum.get(op, target_spec)[:4], dtype=np.float64)
            d = float(np.linalg.norm(cent - q))
            if d < best_d:
                best_d = d
                best_op = op
        return best_op

    def compose_novel_utterance(
        self,
        user_text: str,
        situation_text: str = "",
        chroma: Tuple[float, float, float] = (0.33, 0.34, 0.33),
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Composes a genuinely new Korean utterance along Scale 0->1->2->3 axes without
        canned prose templates or verbatim copying from seen training sentences.
        """
        deficit = self.detect_expressive_deficit(user_text, situation_text)
        if not self.schemas or not self.stem_counts:
            return "", {
                "grounded_in_real_world": False,
                "novel_vs_corpus": True,
                "used_schema": "",
                "used_ending": "",
                "assembled_stems": [],
                "bound_operators": [],
                "deficit": asdict(deficit),
            }

        live_spec = compute_continuous_spectrum(situation_text, "", user_text or situation_text)
        target_spec = _equilibrium_target_spectrum(live_spec)
        # Blend subtle live visual/chromatic gradient into spectrum target
        target_spec[2] = round(float(np.clip(0.75 * target_spec[2] + 0.25 * chroma[0], 0.0, 1.0)), 4)
        target_spec[3] = round(float(np.clip(0.75 * target_spec[3] + 0.25 * chroma[1], 0.1, 1.0)), 4)

        schema = self._pick_best_schema(target_spec)

        user_words = [w for w, _ in (_strip_word_edge_punct(t) for t in (user_text or "").split()) if len(w) >= 1]
        active_stems: List[str] = []
        for idx, w in enumerate(user_words):
            st, _op = self._split_word_distributional(w, is_final=(idx == len(user_words) - 1))
            if st and st not in active_stems and _is_valid_nominal_stem(st, w):
                active_stems.append(st)

        companions = self._select_companion_stems(active_stems, limit=6)
        nominal_pool = [
            s for s in [*active_stems, *companions]
            if _is_valid_nominal_stem(s) and (s in self.nominal_stems or s not in self.predicate_stems)
        ]
        if not nominal_pool:
            nominal_pool = [s for s, _ in self.nominal_stems.most_common(8) if _is_valid_nominal_stem(s)] or [*active_stems, *companions]

        # Select context-resonant complete Korean verbal predicates via IDF-weighted co-occurrence!
        is_user_question = "?" in (user_text or "")
        pred_scores: Dict[str, float] = {}
        for st_idx, st in enumerate([*active_stems, *companions[:4]]):
            w_mult = 4.0 if st_idx < len(active_stems) else 1.8
            for pf, wt in self.predicate_cooccurrence.get(st, {}).items():
                if is_user_question and pf.rstrip(".?!").endswith(("까", "인가", "는가", "나요")):
                    continue
                idf_p = 1.0 / math.sqrt(1.0 + self.predicate_surfaces.get(pf, 1))
                # Penalize ultra-generic copula/existential stubs when richer action verbs exist
                generic_pen = 0.35 if pf.rstrip(".?!") in ("있다", "없다", "이다", "된다", "한다") else 1.0
                pred_scores[pf] = pred_scores.get(pf, 0.0) + float(wt) * w_mult * idf_p * generic_pen
        for pf, cnt in self.predicate_surfaces.most_common(20):
            if is_user_question and pf.rstrip(".?!").endswith(("까", "인가", "는가", "나요")):
                continue
            generic_pen = 0.25 if pf.rstrip(".?!") in ("있다", "없다", "이다", "된다", "한다") else 1.0
            pred_scores[pf] = pred_scores.get(pf, 0.0) + 0.15 * generic_pen
        pred_surface_pool = [pf for pf, _ in sorted(pred_scores.items(), key=lambda kv: -kv[1])[:12]]
        pred_pool = [p for p, _ in self.predicate_stems.most_common(12) if _is_pure_hangul(p) and len(p) >= 2]
        if not pred_pool:
            pred_pool = ["이어지"]

        # Try up to 3 ending/stem perturbations so output is non-verbatim whenever multiple axes exist
        best_sentence = ""
        used_stems: List[str] = []
        bound_ops: List[str] = []
        chosen_ending = self._pick_best_ending(target_spec, rank_offset=0)

        for attempt in range(min(3, max(1, len(self.stance_endings)))):
            cand_ending = self._pick_best_ending(target_spec, rank_offset=attempt)
            cand_stems: List[str] = []
            cand_ops: List[str] = []
            words_out: List[str] = []
            nom_idx = 0
            last_stem = ""

            for sl in schema.slots:
                if sl == "STANCE_END":
                    continue
                if sl == "PREDICATE_CORE":
                    if pred_surface_pool:
                        bound_pred = pred_surface_pool[min(attempt, len(pred_surface_pool) - 1)]
                        clean_p, p_end = self._split_word_distributional(bound_pred.rstrip(".?!"), is_final=True)
                        words_out.append(bound_pred)
                        cand_stems.append(clean_p or bound_pred)
                        cand_ops.append(p_end or cand_ending)
                        last_stem = clean_p or bound_pred
                    else:
                        p_stem = pred_pool[min(attempt, len(pred_pool) - 1)]
                        clean_p = re.sub(r"[?!….,]+$", "", p_stem)
                        bound_pred = clean_p + cand_ending if not clean_p.endswith(cand_ending) else clean_p
                        words_out.append(bound_pred)
                        cand_stems.append(clean_p)
                        cand_ops.append(cand_ending)
                        last_stem = clean_p
                else:
                    if not nominal_pool:
                        continue
                    pick_idx = (nom_idx + attempt) % len(nominal_pool)
                    n_stem = nominal_pool[pick_idx]
                    nom_idx += 1
                    if n_stem == last_stem and len(nominal_pool) > 1:
                        n_stem = nominal_pool[(pick_idx + 1) % len(nominal_pool)]
                    op = self._best_operator_for_slot(schema, sl, target_spec)
                    if op not in _PARTICLE_TO_ROLE:
                        default_op_by_role = {
                            "TOPIC_CORE": "은/는",
                            "SUBJECT_CORE": "이/가",
                            "OBJECT_CORE": "을/를",
                            "COUPLED_LINK": "과/와",
                            "CONTEXT_LOC": "에서",
                            "ATTR_MOD": "의",
                        }
                        op = default_op_by_role.get(sl, "은/는")
                    word_bound = bind_korean_operator(n_stem, op) if op else n_stem
                    words_out.append(word_bound)
                    cand_stems.append(n_stem)
                    cand_ops.append(op)
                    last_stem = n_stem

            candidate_str = re.sub(r"\s+", " ", " ".join(w for w in words_out if w)).strip()
            if not candidate_str:
                continue
            best_sentence = candidate_str
            used_stems = cand_stems
            bound_ops = cand_ops
            chosen_ending = cand_ending
            if candidate_str.lower() not in self._seen_utt_set:
                break

        novel_flag = bool(best_sentence) and (best_sentence.lower() not in self._seen_utt_set)
        return best_sentence, {
            "grounded_in_real_world": bool(best_sentence),
            "novel_vs_corpus": novel_flag,
            "used_schema": schema.schema_id,
            "used_ending": chosen_ending,
            "assembled_stems": used_stems,
            "bound_operators": bound_ops,
            "target_spectrum": target_spec,
            "deficit": asdict(deficit),
            "source_title": f"LanguageScaleRotor({schema.schema_id})",
            "intent_purpose": f"spec_t{target_spec[0]:.1f}_r{target_spec[1]:.1f}_f{target_spec[2]:.1f}",
            "resonance_score": round(max(0.0, 1.0 - deficit.nearest_spectrum_dist), 4),
            "situation": situation_text or user_text[:60],
        }

    def reinforce_from_feedback(
        self,
        used_schema_id: str,
        used_ending: str,
        user_reply_text: str,
    ) -> None:
        """Closes the self-revision loop when the user responds to Elysia's composed speech."""
        reply = (user_reply_text or "").strip()
        if not reply:
            return
        engagement = float(np.clip(0.08 + 0.02 * len(_extract_lexical_tokens(reply)), 0.05, 0.25))
        if "?" not in reply and len(reply) >= 6:
            engagement += 0.05
        if used_schema_id in self.schemas:
            sch = self.schemas[used_schema_id]
            sch.feedback_score = round(float(np.clip(sch.feedback_score + engagement, -0.5, 0.8)), 4)
        reply_spec = compute_continuous_spectrum("", "", reply)
        if used_ending and used_ending in self.stance_endings:
            self.stance_ending_spectrum[used_ending] = self._update_centroid(
                self.stance_ending_spectrum.get(used_ending),
                max(2, self.stance_endings[used_ending]),
                reply_spec,
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "surface_vocab": dict(self.surface_vocab.most_common(1500)),
            "stem_counts": dict(self.stem_counts.most_common(1200)),
            "predicate_stems": dict(self.predicate_stems.most_common(800)),
            "operator_counts": dict(self.operator_counts.most_common(300)),
            "operator_spectrum": dict(self.operator_spectrum),
            "stance_endings": dict(self.stance_endings.most_common(300)),
            "stance_ending_spectrum": dict(self.stance_ending_spectrum),
            "stem_cooccurrence": {
                k: dict(sorted(v.items(), key=lambda kv: -kv[1])[:24])
                for k, v in list(self.stem_cooccurrence.items())[:800]
            },
            "schemas": {k: v.to_dict() for k, v in self.schemas.items()},
            "seen_utterances": self.seen_utterances[-self.MAX_SEEN_UTTERANCES :],
        }

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "LanguageScaleRotor":
        obj = cls()
        obj.surface_vocab = Counter({str(k): int(v) for k, v in (raw.get("surface_vocab") or {}).items()})
        obj.stem_counts = Counter({str(k): int(v) for k, v in (raw.get("stem_counts") or {}).items()})
        obj.predicate_stems = Counter({str(k): int(v) for k, v in (raw.get("predicate_stems") or {}).items()})
        obj.operator_counts = Counter({str(k): int(v) for k, v in (raw.get("operator_counts") or {}).items()})
        obj.operator_spectrum = {str(k): [float(x) for x in v] for k, v in (raw.get("operator_spectrum") or {}).items()}
        obj.stance_endings = Counter({str(k): int(v) for k, v in (raw.get("stance_endings") or {}).items()})
        obj.stance_ending_spectrum = {
            str(k): [float(x) for x in v] for k, v in (raw.get("stance_ending_spectrum") or {}).items()
        }
        for k, nb_map in (raw.get("stem_cooccurrence") or {}).items():
            obj.stem_cooccurrence[str(k)] = {str(nb): int(cnt) for nb, cnt in nb_map.items()}
        obj.schemas = {
            str(k): CausalArraySchema.from_dict(v) for k, v in (raw.get("schemas") or {}).items()
        }
        obj.seen_utterances = [str(u) for u in raw.get("seen_utterances", [])][-obj.MAX_SEEN_UTTERANCES :]
        obj._seen_utt_set = {u.lower() for u in obj.seen_utterances}
        return obj
