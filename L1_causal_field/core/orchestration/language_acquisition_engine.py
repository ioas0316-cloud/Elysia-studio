"""
Real-World Language Acquisition & Causal-Weight Distillation Engine
===================================================================
Replaces rigid hardcoded conversational templates with a 3-layer ultra-lightweight
architecture (ZERO paid LLM APIs · ZERO heavy local LLM runtime):

  1. Korean Phonological & Syntactic Walker ("한국어 보행기")
     - Unicode Hangul jongseong (받침) particle inflection (은/는, 이/가, 을/를,
       과/와, 으로/로 with ㄹ-exception, 이란/란, 이야/야).
     - Clause connective agreement so dynamically assembled Korean never breaks
       into ungrammatical fragments.
     - Tracks `walker_reliance`, which naturally decreases as Elysia acquires
       more authentic clause frames from real-world Korean texts.

  2. Foundational Causal & Weight-Probing Manifold ("기본 인과 · 가중치 증류 발판")
     - Distills lightweight concept vectors / external weight slices OR real-time
       PPMI + NumPy SVD over read Korean prose into compact low-rank causal axes
       (질서↔혼돈, 원인↔결과, 구체↔추상, 정서↔구조, 확장↔수렴).
     - Discovers non-obvious semantic bridges via cosine resonance in distilled
       vector space without running billion-parameter inference.

  3. Autonomous Real-World Korean Reading & Non-Templated Clause Composer
     - Reads free public Korean Wikipedia & Wiktionary (strictly allowlisted
       ko.wikipedia.org / ko.wiktionary.org, zero API keys, safe timeout +
       clean offline fallback) to autonomously learn vocabulary, definitions,
       causal relations, contrasts, and authentic Korean syntactic frames.
     - Composes S4 → S3 → S2 breath-phrases dynamically from causal intent,
       lived world knowledge, qualitative spectra, discipline lenses, and
       acquired syntax patterns instead of canned scripts.
"""

from __future__ import annotations

import json
import math
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Pure-Python Fast Linear Algebra Helpers (Zero External Dependencies)
# ---------------------------------------------------------------------------
def _vdot(a: List[float], b: List[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _vnorm(a: List[float]) -> float:
    return math.sqrt(sum(x * x for x in a))


def _vunit(a: List[float]) -> List[float]:
    n = _vnorm(a)
    if n < 1e-12:
        return [0.0] * len(a)
    inv = 1.0 / n
    return [x * inv for x in a]


def _vmean(vecs: List[List[float]]) -> List[float]:
    if not vecs:
        return []
    d = len(vecs[0])
    inv = 1.0 / len(vecs)
    return [sum(v[c] for v in vecs) * inv for c in range(d)]


def _top_k_svd_embeddings(rows: List[List[float]], k: int, iters: int = 16) -> List[List[float]]:
    """
    Pure-Python deflated power-iteration SVD over rectangular matrix X (n x m) ->
    normalized low-rank row embeddings (n x k) via X X^T Gram operator (zero numpy required).
    """
    n = len(rows)
    if n == 0:
        return []
    m = len(rows[0])
    k_eff = max(1, min(k, n, m))
    # Work on Gram matrix G = X @ X^T (n x n symmetric PSD)
    G = [[0.0] * n for _ in range(n)]
    for i in range(n):
        ri = rows[i]
        for j in range(i, n):
            val = _vdot(ri, rows[j])
            G[i][j] = val
            G[j][i] = val

    basis: List[List[float]] = []
    eig_scales: List[float] = []
    for comp in range(k_eff):
        # Deterministic seed vector per component
        v = [math.sin((i + 1) * (comp + 1.37)) + 0.25 * math.cos(i * 0.7 + comp) for i in range(n)]
        v = _vunit(v)
        for _ in range(iters):
            w = [_vdot(G[i], v) for i in range(n)]
            # Deflate previous eigenvectors
            for b, lam in zip(basis, eig_scales):
                proj = _vdot(b, v) * lam
                for i in range(n):
                    w[i] -= proj * b[i]
            # Orthogonalize strictly against previous basis
            for b in basis:
                proj = _vdot(w, b)
                for i in range(n):
                    w[i] -= proj * b[i]
            wn = _vnorm(w)
            if wn < 1e-10:
                break
            inv = 1.0 / wn
            v = [x * inv for x in w]
        # Rayleigh quotient eigenvalue
        gv = [_vdot(G[i], v) for i in range(n)]
        for b, lam in zip(basis, eig_scales):
            proj = _vdot(b, v) * lam
            for i in range(n):
                gv[i] -= proj * b[i]
        lam = max(1e-9, _vdot(v, gv))
        basis.append(v)
        eig_scales.append(lam)

    # Row embeddings: u_i * (lam^(1/4)) then unit-normalize each row
    out: List[List[float]] = []
    scales_q = [lam ** 0.25 for lam in eig_scales]
    for i in range(n):
        vec = [basis[c][i] * scales_q[c] for c in range(len(basis))]
        out.append(_vunit(vec))
    return out


# ---------------------------------------------------------------------------
# Layer 1: Hangul Phonological & Syntactic Walker ("보행기")
# ---------------------------------------------------------------------------
_DIGIT_BATCHIM = {"0": True, "1": True, "2": False, "3": True, "4": False, "5": False, "6": True, "7": True, "8": True, "9": False}
_DIGIT_RIEUL = {"1": True, "7": True, "8": True}
_EN_BATCHIM_CHARS = set("lmnrkpbtcg")
_EN_RIEUL_CHARS = set("l")

_TRAILING_JOSA_RE = re.compile(
    r"(에서는|으로는|이라는|에서는|에게서|까지도|조차도|부터는|보다는|처럼은|"
    r"은|는|이|가|을|를|과|와|로|으로|에|에서|에게|한테|께|의|도|만|부터|까지|처럼|보다|라고|이라고|란|이란)$"
)


def _last_meaningful_char(word: str) -> str:
    s = re.sub(r"[\s\"'’”)\]}.,!?~·…]+$", "", (word or "").strip())
    return s[-1] if s else ""


def has_batchim(word: str) -> bool:
    ch = _last_meaningful_char(word)
    if not ch:
        return False
    code = ord(ch)
    if 0xAC00 <= code <= 0xD7A3:
        return ((code - 0xAC00) % 28) != 0
    if ch in _DIGIT_BATCHIM:
        return _DIGIT_BATCHIM[ch]
    if ch.lower() in _EN_BATCHIM_CHARS:
        return True
    return False


def has_rieul_batchim(word: str) -> bool:
    ch = _last_meaningful_char(word)
    if not ch:
        return False
    code = ord(ch)
    if 0xAC00 <= code <= 0xD7A3:
        return ((code - 0xAC00) % 28) == 8  # ㄹ jongseong index = 8
    if ch in _DIGIT_RIEUL:
        return True
    return ch.lower() in _EN_RIEUL_CHARS


def josa(word: str, pair: str) -> str:
    """Attach phonologically accurate Korean particle to `word`."""
    w = (word or "").strip()
    if not w:
        return ""
    b = has_batchim(w)
    r = has_rieul_batchim(w)
    if pair == "은/는":
        return f"{w}{'은' if b else '는'}"
    if pair == "이/가":
        return f"{w}{'이' if b else '가'}"
    if pair == "을/를":
        return f"{w}{'을' if b else '를'}"
    if pair == "과/와":
        return f"{w}{'과' if b else '와'}"
    if pair == "으로/로":
        return f"{w}{'로' if (not b or r) else '으로'}"
    if pair == "이랑/랑":
        return f"{w}{'이랑' if b else '랑'}"
    if pair == "이야/야":
        return f"{w}{'이야' if b else '야'}"
    if pair == "이란/란":
        return f"{w}{'이란' if b else '란'}"
    if pair == "이라는/라는":
        return f"{w}{'이라는' if b else '라는'}"
    if pair == "이라고/라고":
        return f"{w}{'이라고' if b else '라고'}"
    if pair in ("에", "에서", "의"):
        return f"{w}{pair}"
    return w


def strip_josa(token: str) -> str:
    t = (token or "").strip()
    if len(t) <= 2:
        return t
    stripped = _TRAILING_JOSA_RE.sub("", t)
    return stripped if len(stripped) >= 2 else t


def _clean_wiki_prose(raw: str) -> str:
    """Strip heavy Hanja/phonetic parentheses and citation noise while preserving living Korean prose."""
    txt = (raw or "").strip()
    if not txt:
        return ""
    # Remove parentheticals containing mostly Hanja/Latin/IPA (keep short Korean clarifying parens)
    def _paren_sub(m: re.Match) -> str:
        inner = m.group(1)
        ko_chars = len(re.findall(r"[가-힣]", inner))
        if ko_chars == 0 or (len(inner) > 22 and ko_chars < len(inner) * 0.45):
            return ""
        return m.group(0)

    txt = re.sub(r"\(([^()]{1,90})\)", _paren_sub, txt)
    txt = re.sub(r"\[[^\]]{1,40}\]", "", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt


def _split_korean_sentences(text: str) -> List[str]:
    clean = re.sub(r"\s+", " ", (text or "").strip())
    if not clean:
        return []
    parts = re.split(r"(?<=[.!?다요죠])\s+|\n+", clean)
    out: List[str] = []
    for p in parts:
        s = p.strip(" -•·\t")
        if 8 <= len(s) <= 220:
            out.append(s)
    return out


_KO_WORD_RE = re.compile(r"[가-힣]{2,12}|[A-Za-z][A-Za-z0-9_-]{2,14}")
_STOPWORDS = {
    "있다", "없다", "한다", "된다", "이다", "하는", "되는", "있는", "없는", "같은", "대한",
    "통해", "위해", "따라", "때문", "경우", "정도", "가지", "것을", "것이", "것은", "수도",
    "에서", "으로", "부터", "까지", "처럼", "그리고", "하지만", "그러나", "또한", "그래서",
    "매우", "아주", "정말", "진짜", "지금", "오늘", "여기", "저기", "이것", "그것", "저것",
    "우리", "나는", "내가", "너는", "네가", "사람", "하나", "모든", "어떤", "무엇", "어떻게",
    "때로", "보통", "주로", "특히", "가장", "더욱", "이미", "아직", "다시", "함께", "서로",
}


def _extract_content_terms(text: str) -> List[str]:
    terms: List[str] = []
    seen = set()
    for m in _KO_WORD_RE.finditer(text or ""):
        stem = strip_josa(m.group(0))
        if len(stem) < 2 or stem in _STOPWORDS:
            continue
        if stem not in seen:
            seen.add(stem)
            terms.append(stem)
    return terms


# ---------------------------------------------------------------------------
# Foundational Causal Poles (for Weight / SVD Probing — Grounding as Foothold)
# ---------------------------------------------------------------------------
CAUSAL_POLE_AXES: List[Dict[str, Any]] = [
    {
        "id": "order_vs_chaos",
        "name": "질서↔혼돈",
        "pos_label": "질서·구조",
        "neg_label": "혼돈·변동",
        "pos_seeds": ["질서", "구조", "규칙", "균형", "안정", "법칙", "체계", "항상성", "대칭", "조화"],
        "neg_seeds": ["혼돈", "변화", "무질서", "충돌", "붕괴", "발산", "폭발", "위기", "요동", "엔트로피"],
    },
    {
        "id": "cause_vs_effect",
        "name": "원인↔결과",
        "pos_label": "기제·원인",
        "neg_label": "현상·결과",
        "pos_seeds": ["원인", "조건", "기제", "원리", "에너지", "자극", "동기", "압력", "힘", "씨앗"],
        "neg_seeds": ["결과", "효과", "현상", "열매", "변형", "반응", "성장", "산출", "영향", "증상"],
    },
    {
        "id": "concrete_vs_abstract",
        "name": "구체·감각↔추상·개념",
        "pos_label": "감각·물성",
        "neg_label": "추상·이론",
        "pos_seeds": ["사과", "바다", "바람", "빛", "소리", "열매", "나무", "색", "온도", "촉감"],
        "neg_seeds": ["개념", "이론", "가치", "철학", "의미", "언어", "논리", "관계", "제도", "학문"],
    },
    {
        "id": "feeling_vs_structure",
        "name": "정서·공감↔분석·도구",
        "pos_label": "정서·관계",
        "neg_label": "분석·설계",
        "pos_seeds": ["감정", "마음", "공감", "기억", "사랑", "슬픔", "기쁨", "신뢰", "호흡", "진심"],
        "neg_seeds": ["설계", "도구", "효율", "계산", "분석", "최적화", "모델", "시스템", "전략", "병목"],
    },
    {
        "id": "expansion_vs_convergence",
        "name": "확장·탐색↔수렴·응축",
        "pos_label": "확장·전파",
        "neg_label": "수렴·집중",
        "pos_seeds": ["확장", "탐색", "전파", "네트워크", "연결", "흐름", "진화", "창의", "교류", "개방"],
        "neg_seeds": ["수렴", "집중", "압축", "경계", "제약", "고정", "보존", "핵심", "밀도", "응축"],
    },
]

# Diverse starter curiosity queue for autonomous background real-world Korean reading
DEFAULT_WORLD_CURIOSITY_QUEUE: List[str] = [
    "언어", "공감", "기억", "광합성", "항상성", "엔트로피", "기회비용",
    "인지부조화", "리듬", "아치", "생태계", "신뢰", "비유", "호흡",
    "중력", "빛", "시간", "진화", "사회", "음악",
]


# ---------------------------------------------------------------------------
# Regex extractors for real-world Korean syntactic & causal patterns
# ---------------------------------------------------------------------------
_DEF_RE = re.compile(
    r"^([가-힣A-Za-z0-9\s]{1,18}?)[은는]\s+(.{8,110}?(?:이다|다|말한다|뜻한다|의미한다|가리킨다|일컫는다|하나다|현상이다|과정이다|원리다|개념이다|학문이다))[.!]?$"
)
_CAUSAL_RE = re.compile(
    r"(.{6,65}?)(?:때문에|로 인해|으로 인해|하면|할수록|되면서|을 통해|를 통해|에 의해)\s+(.{6,85})"
)
_CONTRAST_RE = re.compile(
    r"(.{6,65}?)(?:하지만|그러나|반면|반면에|와 달리|과 달리|이지만|지만|더라도)\s+(.{6,85})"
)
_CONNECTIVE_RE = re.compile(
    r"(때문에|로 인해|으로 인해|할수록|하면서|하지만|반면에|와 달리|과 달리|처럼|을 통해|를 통해|에 따라|일 때|라면|다면)"
)


class RealLanguageAcquisitionEngine:
    """
    Combines:
      - Korean Phonological Walker (보행기)
      - Real-Time & External Weight-to-Causal SVD Manifold
      - Free Korean Wikipedia/Wiktionary Autonomous Reading
      - Non-Templated Dynamic Clause Composition
    """

    WIKI_API = "https://ko.wikipedia.org/w/api.php"
    WIKT_API = "https://ko.wiktionary.org/w/api.php"

    def __init__(self) -> None:
        # Learned world knowledge anchored by concept
        self.world_entries: Dict[str, Dict[str, Any]] = {}
        # Learned real Korean syntactic & causal frames (extracted directly from real prose)
        self.syntax_frames: Dict[str, List[Dict[str, Any]]] = {
            "definition": [],
            "causal": [],
            "contrast": [],
            "connective": [],
        }
        self.learned_connectives: Counter = Counter()
        self.learned_predicates: List[str] = []
        self.sentence_count_read: int = 0
        self.sources_read: List[str] = []
        self.explored_topics: List[str] = []
        self.curiosity_queue: List[str] = list(DEFAULT_WORLD_CURIOSITY_QUEUE)
        self.last_world_reading: Optional[Dict[str, Any]] = None

        # Distributional co-occurrence & Weight-to-Causal SVD manifold
        self.term_counts: Counter = Counter()
        self.cooccur: Dict[str, Counter] = defaultdict(Counter)
        self.svd_vocab: List[str] = []
        self.svd_vectors: Dict[str, List[float]] = {}
        self.distilled_axes: List[Dict[str, Any]] = []
        self.external_weight_sources: List[Dict[str, Any]] = []
        self.last_svd_ts: float = 0.0
        self.dirty_svd: bool = False

        # 3D Multi-Scale Relational Rotor Tensor: shape [5 scales (S0..S4) x N concepts x 7 relational cols]
        # Escapes the flat 2D [N x D] bottleneck by coupling 5 linked Excel-like sheets simultaneously:
        #   S0: 음운·어간·받침 결  | S1: 어휘·인과축 좌표 | S2: 구·절 관계식 결합
        #   S3: 인과·대조 규칙 결합 | S4: 거시 맥락·학문 수렴장
        # Columns: [질서↔혼돈, 원인↔결과, 감각↔추상, 정서↔도구, 확장↔수렴, 관계질량, 위상각θ]
        self.scale_tensor_vocab: List[str] = []
        self.scale_tensor: Optional[List[List[List[float]]]] = None  # 3D pure-Python tensor [5][N][7]
        self.scale_sheet_coherence: float = 0.0
        self.scale_formula_links: int = 0
        self.last_rotor_sigma: float = 0.50

        # Anti-repetition memory for organic non-templated conversation
        self.recent_openers: List[str] = []
        self.recent_closers: List[str] = []
        self.recent_bridge_sigs: List[str] = []
        self.turn_counter: int = 0

        # Seed minimal foundational causal Korean prose so the walker & Scale-Rotor tensor start coherent on turn 1
        self._seed_foundational_causal_prose()

    def _seed_foundational_causal_prose(self) -> None:
        seed_texts = [
            ("기초인과", "언어는 생각과 감각을 서로 연결해 의미를 나누는 살아 있는 질서다. 같은 단어라도 맥락에 따라 온도와 결이 달라진다."),
            ("기초인과", "원인이 조건을 만나면 새로운 결과가 나타나지만, 경계 조건이 바뀌면 전혀 다른 흐름으로 갈라진다."),
            ("기초인과", "경험이 쌓일수록 지각의 스펙트럼이 넓어지고, 서로 다른 분야의 원리 사이에서도 숨은 공통 구조가 드러난다."),
            ("기초인과", "질서가 지나치게 굳어지면 적응력을 잃지만, 반면에 흐름이 너무 거세지면 형태를 유지하기 어렵다."),
            ("기초인과", "기억은 과거의 흔적을 보존할 뿐만 아니라, 현재의 대화를 이해하고 미래의 선택을 비추는 거울 역할을 한다."),
        ]
        for src, txt in seed_texts:
            self.absorb_real_korean(txt, source=src, topic=src, rebuild_svd=False)
        self.rebuild_svd_manifold()

    # ------------------------------------------------------------------
    # Walker Graduation Metric ("보행기 의존도")
    # ------------------------------------------------------------------
    @property
    def total_syntax_frames(self) -> int:
        return sum(len(v) for v in self.syntax_frames.values())

    @property
    def walker_reliance(self) -> float:
        """1.0 when fresh; smoothly drops toward 0.18 as real Korean clauses accumulate."""
        n = self.sentence_count_read + self.total_syntax_frames
        return round(max(0.18, min(1.0, 1.0 / (1.0 + 0.012 * max(0, n - 8)))), 3)

    # ------------------------------------------------------------------
    # Layer 3A: Free Korean Wikipedia / Wiktionary Autonomous Reader
    # ------------------------------------------------------------------
    def _http_get_json(self, base_url: str, params: Dict[str, str], timeout: float = 3.2) -> Optional[Dict[str, Any]]:
        # Strictly allowlisted public Korean Wiki hosts only (zero SSRF)
        if base_url not in (self.WIKI_API, self.WIKT_API):
            return None
        qs = urllib.parse.urlencode(params)
        url = f"{base_url}?{qs}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "ElysiaCausalLearner/1.0 (local-educational-research)"},
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if getattr(resp, "status", 200) != 200:
                    return None
                raw = resp.read(160_000).decode("utf-8", errors="replace")
                return json.loads(raw)
        except Exception:
            return None

    def fetch_korean_world_knowledge(self, query: str, timeout: float = 2.8) -> Optional[Dict[str, Any]]:
        """
        Autonomously fetch real Korean prose about `query` from free Korean Wikipedia
        (with Wiktionary fallback). Returns structured reading entry or None if offline/not found.
        """
        q = strip_josa((query or "").strip())
        if len(q) < 2 or len(q) > 30:
            return None

        # Cached already?
        if q in self.world_entries:
            entry = self.world_entries[q]
            entry["hits"] = int(entry.get("hits", 0)) + 1
            return entry

        # 1) Direct title query on Korean Wikipedia
        data = self._http_get_json(
            self.WIKI_API,
            {
                "action": "query",
                "prop": "extracts",
                "exintro": "1",
                "explaintext": "1",
                "exchars": "900",
                "redirects": "1",
                "format": "json",
                "titles": q,
            },
            timeout=timeout,
        )
        title = ""
        extract = ""
        source_kind = "한국어 위키백과"

        if data and isinstance(data.get("query", {}).get("pages"), dict):
            for pid, page in data["query"]["pages"].items():
                if str(pid) != "-1" and page.get("extract"):
                    title = str(page.get("title", q))
                    extract = str(page.get("extract", ""))
                    break

        # 2) If direct title missed, run Korean Wikipedia opensearch/search fallback
        if not extract:
            sdata = self._http_get_json(
                self.WIKI_API,
                {
                    "action": "query",
                    "list": "search",
                    "srsearch": q,
                    "srlimit": "2",
                    "format": "json",
                },
                timeout=timeout,
            )
            hits = (sdata or {}).get("query", {}).get("search") or []
            if hits:
                best_title = str(hits[0].get("title", "")).strip()
                # Require genuine lexical match so coined/novel concepts preserve epistemic humility!
                bt_clean = re.sub(r"\s+", "", best_title)
                q_nospace = re.sub(r"\s+", "", q)
                is_relevant = bool(bt_clean) and (
                    (q_nospace in bt_clean)
                    or (bt_clean in q_nospace and len(bt_clean) >= len(q_nospace) * 0.65)
                )
                if is_relevant:
                    data2 = self._http_get_json(
                        self.WIKI_API,
                        {
                            "action": "query",
                            "prop": "extracts",
                            "exintro": "1",
                            "explaintext": "1",
                            "exchars": "900",
                            "redirects": "1",
                            "format": "json",
                            "titles": best_title,
                        },
                        timeout=timeout,
                    )
                    if data2 and isinstance(data2.get("query", {}).get("pages"), dict):
                        for pid, page in data2["query"]["pages"].items():
                            if str(pid) != "-1" and page.get("extract"):
                                title = str(page.get("title", best_title))
                                extract = str(page.get("extract", ""))
                                break

        # 3) Fallback to Korean Wiktionary for pure Korean words / adjectives / idioms
        if not extract:
            wdata = self._http_get_json(
                self.WIKT_API,
                {
                    "action": "query",
                    "prop": "extracts",
                    "explaintext": "1",
                    "exchars": "650",
                    "redirects": "1",
                    "format": "json",
                    "titles": q,
                },
                timeout=timeout,
            )
            if wdata and isinstance(wdata.get("query", {}).get("pages"), dict):
                for pid, page in wdata["query"]["pages"].items():
                    if str(pid) != "-1" and page.get("extract"):
                        title = str(page.get("title", q))
                        raw_w = str(page.get("extract", ""))
                        # Extract meaningful Korean lines from Wiktionary entry
                        lines = [
                            ln.strip(" *#·:-")
                            for ln in raw_w.splitlines()
                            if len(ln.strip()) >= 10 and not ln.strip().startswith("=")
                        ]
                        extract = " ".join(lines[:3])
                        source_kind = "한국어 위키낱말사전"
                        break

        cleaned = _clean_wiki_prose(extract)
        if not cleaned or len(cleaned) < 16:
            return None

        sents = _split_korean_sentences(cleaned)
        summary_sent = sents[0] if sents else cleaned[:140]
        detail_sent = sents[1] if len(sents) > 1 else ""

        absorbed = self.absorb_real_korean(cleaned, source=source_kind, topic=title or q, rebuild_svd=True)
        entry = {
            "query": q,
            "title": title or q,
            "source": source_kind,
            "summary": summary_sent[:170],
            "detail": detail_sent[:170],
            "sentences_absorbed": absorbed["sentences_added"],
            "frames_extracted": absorbed["frames_added"],
            "key_terms": absorbed["terms"][:8],
            "ts": round(time.time(), 2),
            "hits": 1,
        }
        self.world_entries[q] = entry
        if title and title != q:
            self.world_entries[title] = entry
        if (title or q) not in self.explored_topics:
            self.explored_topics.append(title or q)
            self.explored_topics = self.explored_topics[-80:]
        self.last_world_reading = entry
        return entry

    def autonomous_background_read(self, candidate_topics: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Pick one unread real-world topic and silently absorb it in the background."""
        pool: List[str] = []
        for t in (candidate_topics or []):
            clean = strip_josa(t)
            if len(clean) >= 2 and clean not in self.world_entries and clean not in _STOPWORDS:
                pool.append(clean)
        for t in self.curiosity_queue:
            if t not in self.world_entries:
                pool.append(t)
        if not pool:
            return None
        topic = pool[0]
        if topic in self.curiosity_queue:
            self.curiosity_queue.remove(topic)
        return self.fetch_korean_world_knowledge(topic, timeout=2.5)

    # ------------------------------------------------------------------
    # Layer 2 & 3B: Absorb Real Korean Prose -> Syntax Frames + Co-occurrence
    # ------------------------------------------------------------------
    def absorb_real_korean(
        self,
        text: str,
        *,
        source: str = "현실 텍스트",
        topic: str = "",
        rebuild_svd: bool = True,
    ) -> Dict[str, Any]:
        """
        Absorb real-world Korean sentences:
          - Anchor definition / causal / contrast / connective syntax patterns onto causal slots
          - Update distributional co-occurrence counts for SVD causal manifold
        """
        sents = _split_korean_sentences(_clean_wiki_prose(text))
        if not sents:
            return {"sentences_added": 0, "frames_added": 0, "terms": []}

        frames_added = 0
        all_terms: List[str] = []

        for sent in sents[:24]:
            self.sentence_count_read += 1
            terms = _extract_content_terms(sent)
            for t in terms:
                self.term_counts[t] += 1
                if t not in all_terms:
                    all_terms.append(t)

            # Sliding window co-occurrence (window = 4)
            for i, ti in enumerate(terms):
                for j in range(max(0, i - 4), min(len(terms), i + 5)):
                    if i == j:
                        continue
                    self.cooccur[ti][terms[j]] += 1
            self.dirty_svd = True

            # Extract real Korean connective tokens
            for cm in _CONNECTIVE_RE.finditer(sent):
                self.learned_connectives[cm.group(1)] += 1

            # 1) Definition frame
            m_def = _DEF_RE.match(sent)
            if m_def:
                subj = strip_josa(m_def.group(1).strip())
                pred = m_def.group(2).strip()
                if 1 < len(subj) <= 16 and len(pred) >= 8:
                    self._push_frame(
                        "definition",
                        {"subject": subj, "predicate": pred[:130], "source": source, "topic": topic or subj},
                    )
                    frames_added += 1

            # 2) Causal frame
            m_cau = _CAUSAL_RE.search(sent)
            if m_cau:
                cause = m_cau.group(1).strip(" ,·")
                eff = m_cau.group(2).strip(" ,·")
                if len(cause) >= 6 and len(eff) >= 6:
                    self._push_frame(
                        "causal",
                        {"cause": cause[:70], "effect": eff[:85], "source": source, "topic": topic or (terms[0] if terms else "")},
                    )
                    frames_added += 1

            # 3) Contrast frame
            m_con = _CONTRAST_RE.search(sent)
            if m_con:
                left = m_con.group(1).strip(" ,·")
                right = m_con.group(2).strip(" ,·")
                if len(left) >= 6 and len(right) >= 6:
                    self._push_frame(
                        "contrast",
                        {"left": left[:70], "right": right[:85], "source": source, "topic": topic or (terms[0] if terms else "")},
                    )
                    frames_added += 1

            # 4) Reusable authentic predicate endings (for non-templated speech nuance)
            pred_m = re.search(r"([가-힣]{2,12}(?:을|를|에|으로|로|과|와)\s+[가-힣]{2,10}(?:한다|된다|만든다|이룬다|나타난다|드러난다|연결된다|바뀐다|흐른다))", sent)
            if pred_m:
                ph = pred_m.group(1).strip()
                if ph not in self.learned_predicates:
                    self.learned_predicates.append(ph)
                    self.learned_predicates = self.learned_predicates[-80:]

        if source and source not in self.sources_read:
            self.sources_read.append(source)
            self.sources_read = self.sources_read[-40:]

        if rebuild_svd and self.dirty_svd:
            self.rebuild_svd_manifold()

        return {
            "sentences_added": len(sents[:24]),
            "frames_added": frames_added,
            "terms": all_terms[:12],
        }

    def _push_frame(self, kind: str, item: Dict[str, Any]) -> None:
        bucket = self.syntax_frames.setdefault(kind, [])
        sig = json.dumps(item, ensure_ascii=False, sort_keys=True)
        for existing in bucket[-25:]:
            if json.dumps(existing, ensure_ascii=False, sort_keys=True) == sig:
                return
        bucket.append(item)
        if len(bucket) > 90:
            del bucket[:-90]

    # ------------------------------------------------------------------
    # Layer 2: Real PPMI + SVD & External Weight-to-Causal Distillation
    # ------------------------------------------------------------------
    def rebuild_svd_manifold(self, max_vocab: int = 120, dims: int = 10) -> Dict[str, Any]:
        """
        Build a real low-rank distributional semantic manifold using PPMI + pure-Python
        deflated power-iteration SVD over all read Korean texts, then lift into the 5-scale
        relational rotor tensor. Zero heavy LLM & zero external deps!
        """
        top_items = [w for w, _ in self.term_counts.most_common(max_vocab)]
        if len(top_items) < 6:
            return {"vocab_size": len(top_items), "dims": 0, "axes": [], "tensor_shape": [5, 0, 7], "sheet_coherence": 0.0}

        idx = {w: i for i, w in enumerate(top_items)}
        n = len(top_items)
        mat = [[0.0] * n for _ in range(n)]
        row_sum = [1e-9] * n
        col_sum = [1e-9] * n
        total_pairs = 0.0
        for w, nbrs in self.cooccur.items():
            if w not in idx:
                continue
            i = idx[w]
            for nb, cnt in nbrs.items():
                if nb in idx:
                    j = idx[nb]
                    c = float(cnt)
                    mat[i][j] += c
                    row_sum[i] += c
                    col_sum[j] += c
                    total_pairs += c

        if total_pairs <= 1.0:
            return {"vocab_size": n, "dims": 0, "axes": [], "tensor_shape": [5, 0, 7], "sheet_coherence": 0.0}

        ppmi = [[0.0] * n for _ in range(n)]
        denom_scale = max(1.0, total_pairs)
        for i in range(n):
            for j in range(n):
                if i == j or mat[i][j] <= 0.0:
                    continue
                exp_v = (row_sum[i] * col_sum[j]) / denom_scale
                val = math.log((mat[i][j] + 1e-9) / (exp_v + 1e-9))
                if val > 0.0:
                    ppmi[i][j] = val

        k = min(dims, max(2, n - 2))
        emb = _top_k_svd_embeddings(ppmi, k=k, iters=14)

        self.svd_vocab = top_items
        for i, w in enumerate(top_items):
            if w not in self.svd_vectors or len(self.svd_vectors[w]) != len(emb[i]):
                self.svd_vectors[w] = [round(x, 4) for x in emb[i]]
            else:
                prev = self.svd_vectors[w]
                blended = _vunit([0.55 * emb[i][c] + 0.45 * prev[c] for c in range(len(emb[i]))])
                self.svd_vectors[w] = [round(x, 4) for x in blended]

        self.distilled_axes = self._probe_causal_axes(self.svd_vectors)
        self._rebuild_scale_rotor_tensor()
        self.last_svd_ts = round(time.time(), 2)
        self.dirty_svd = False
        t_shape = [5, len(self.scale_tensor_vocab), 7] if self.scale_tensor is not None else [5, 0, 7]
        return {
            "vocab_size": len(self.svd_vectors),
            "dims": k,
            "axes": self.distilled_axes,
            "tensor_shape": t_shape,
            "sheet_coherence": self.scale_sheet_coherence,
        }

    def distill_external_weights(
        self,
        weight_vectors: Dict[str, List[float]],
        *,
        source_name: str = "오픈 가중치 슬라이스",
    ) -> Dict[str, Any]:
        """
        Extract causal-semantic axes & lift ANY lightweight external embedding/weight
        dictionary `{token: [w0, w1, ...]}` upward into the 5-scale coupled relational
        tensor `[5 x N x 7]`, then discard heavy runtime overhead!
        """
        valid_items: List[Tuple[str, List[float]]] = []
        target_dim = 0
        for tok, vec in (weight_vectors or {}).items():
            clean_tok = strip_josa(str(tok).strip())
            if not clean_tok or not isinstance(vec, (list, tuple)) or len(vec) < 2:
                continue
            try:
                arr = [float(x) for x in vec]
            except Exception:
                continue
            if not all(math.isfinite(x) for x in arr):
                continue
            if target_dim == 0:
                target_dim = len(arr)
            if len(arr) != target_dim:
                continue
            norm = _vnorm(arr)
            if norm < 1e-9:
                continue
            valid_items.append((clean_tok, [x / norm for x in arr]))

        if len(valid_items) < 4:
            res = self.rebuild_svd_manifold()
            return {
                "source_name": f"{source_name} (로컬 코퍼스 5계층 증류)",
                "vectors_distilled": res["vocab_size"],
                "dims": res["dims"],
                "lifted_tensor_shape": res["tensor_shape"],
                "sheet_coherence": res["sheet_coherence"],
                "axes": res["axes"],
                "top_bridges": self._sample_top_bridges(limit=5),
            }

        # Center and project via pure-Python SVD into compact causal manifold
        mean_v = _vmean([v for _, v in valid_items])
        centered = [[v[c] - mean_v[c] for c in range(target_dim)] for _, v in valid_items]
        k = min(10, target_dim, max(2, len(valid_items) - 1))
        proj = _top_k_svd_embeddings(centered, k=k, iters=16)

        distilled_map: Dict[str, List[float]] = {}
        for idx_i, (tok, _) in enumerate(valid_items):
            vec_list = [round(x, 4) for x in proj[idx_i]]
            distilled_map[tok] = vec_list
            self.svd_vectors[tok] = vec_list
            if tok not in self.svd_vocab:
                self.svd_vocab.append(tok)

        axes = self._probe_causal_axes(self.svd_vectors)
        self.distilled_axes = axes
        self._rebuild_scale_rotor_tensor()
        t_shape = [5, len(self.scale_tensor_vocab), 7] if self.scale_tensor is not None else [5, 0, 7]
        meta = {
            "source_name": source_name,
            "vectors_distilled": len(distilled_map),
            "original_dim": target_dim,
            "compressed_dim": k,
            "axes_found": len(axes),
            "lifted_tensor_shape": t_shape,
            "sheet_coherence": self.scale_sheet_coherence,
            "ts": round(time.time(), 2),
        }
        self.external_weight_sources.append(meta)
        self.external_weight_sources = self.external_weight_sources[-10:]

        return {
            **meta,
            "axes": axes,
            "top_bridges": self._sample_top_bridges(limit=5),
        }

    # ------------------------------------------------------------------
    # Layer 2B: 3D Multi-Scale Relational Rotor Tensor [5 x N x 7]
    # ("엑셀 다중 시트 관계식 + 스케일로터 동시 회전" — 2D 평면 병목 탈출)
    # ------------------------------------------------------------------
    def _rebuild_scale_rotor_tensor(self) -> None:
        """
        Lift flat 2D concept vectors into a 5-scale coupled relational tensor T[s][i][c]:
          - s in 0..4: S0(음운·형태), S1(어휘·인과극), S2(구·절 인접 관계식),
                       S3(인과·대조 규칙 관계식), S4(거시 맥락 수렴장)
          - i in 0..N-1: concepts
          - c in 0..6: [질서↔혼돈, 원인↔결과, 감각↔추상, 정서↔도구, 확장↔수렴, 관계질량, 위상각θ]
        """
        vocab = [w for w in self.svd_vocab if w in self.svd_vectors][:120]
        for w in self.svd_vectors.keys():
            if w not in vocab and len(vocab) < 120:
                vocab.append(w)
        n = len(vocab)
        if n < 4:
            self.scale_tensor_vocab = vocab
            self.scale_tensor = None
            self.scale_sheet_coherence = 0.0
            self.scale_formula_links = 0
            return

        idx = {w: i for i, w in enumerate(vocab)}
        dim = max(len(self.svd_vectors[w]) for w in vocab)
        T = [[[0.0] * 7 for _ in range(n)] for _ in range(5)]

        # --- Sheet S0 (음운·어간·받침 결: Hangul physical substrate) ---
        for i, w in enumerate(vocab):
            chars = [ch for ch in w if 0xAC00 <= ord(ch) <= 0xD7A3]
            n_ch = max(1, len(chars))
            batchim_ratio = sum(1 for ch in chars if ((ord(ch) - 0xAC00) % 28) != 0) / n_ch
            bright_ratio = sum(1 for ch in chars if (((ord(ch) - 0xAC00) // 28) % 21) in (0, 2, 8, 12)) / n_ch
            len_norm = min(1.0, len(w) / 8.0)
            T[0][i][0] = 2.0 * batchim_ratio - 1.0
            T[0][i][2] = 2.0 * bright_ratio - 1.0
            T[0][i][4] = 2.0 * len_norm - 1.0
            T[0][i][5] = min(1.0, math.log1p(self.term_counts.get(w, 1)) / 4.0)
            T[0][i][6] = (sum(ord(c) for c in w) % 360) * (math.pi / 180.0)

        # --- Sheet S1 (어휘·인과극 좌표: Project distilled vectors onto 5 causal pole columns) ---
        aligned_vecs: List[List[float]] = []
        for w in vocab:
            v = list(self.svd_vectors.get(w, []))
            if len(v) < dim:
                v.extend([0.0] * (dim - len(v)))
            aligned_vecs.append(v[:dim])

        for col_c, spec in enumerate(CAUSAL_POLE_AXES[:5]):
            pos_v = [aligned_vecs[idx[w]] for w in spec["pos_seeds"] if w in idx]
            neg_v = [aligned_vecs[idx[w]] for w in spec["neg_seeds"] if w in idx]
            if pos_v and neg_v:
                pm, nm = _vmean(pos_v), _vmean(neg_v)
                dvec = [pm[d] - nm[d] for d in range(dim)]
            elif pos_v:
                dvec = _vmean(pos_v)
            elif neg_v:
                nm = _vmean(neg_v)
                dvec = [-nm[d] for d in range(dim)]
            else:
                dvec = [1.0 if d == (col_c % dim) else 0.0 for d in range(dim)]
            dvec = _vunit(dvec)
            if _vnorm(dvec) > 1e-8:
                for i in range(n):
                    T[1][i][col_c] = _vdot(aligned_vecs[i], dvec)

        for i, w in enumerate(vocab):
            T[1][i][5] = max(0.1, min(1.0, math.log1p(self.term_counts.get(w, 1)) / 4.0))
            T[1][i][6] = math.atan2(T[1][i][1], T[1][i][0] + 1e-6)

        # --- Excel-Like Relational Formula Links (Sparse cell dependencies) ---
        co_links: List[Dict[int, float]] = [{i: 0.35} for i in range(n)]
        formula_links = 0
        for w, nbrs in self.cooccur.items():
            if w not in idx:
                continue
            i = idx[w]
            for nb, cnt in nbrs.items():
                if nb in idx and nb != w:
                    j = idx[nb]
                    co_links[i][j] = co_links[i].get(j, 0.0) + float(cnt)
                    formula_links += 1

        # Sheet S2 = W_co @ S1 (co-occurrence relational formula sheet)
        for i in range(n):
            denom = sum(co_links[i].values()) + 1e-9
            for c in range(7):
                T[2][i][c] = sum(wt * T[1][j][c] for j, wt in co_links[i].items()) / denom

        # Sheet S3 = W_causal @ S2 (directional cause->effect & contrast formula sheet)
        cau_links: List[Dict[int, float]] = [{i: 0.45} for i in range(n)]
        for cf in self.syntax_frames.get("causal", []):
            c_terms = [t for t in _extract_content_terms(cf.get("cause", "")) if t in idx]
            e_terms = [t for t in _extract_content_terms(cf.get("effect", "")) if t in idx]
            for ct in c_terms[:3]:
                for et in e_terms[:3]:
                    if ct != et:
                        ie, ic = idx[et], idx[ct]
                        cau_links[ie][ic] = cau_links[ie].get(ic, 0.0) + 0.85
                        formula_links += 1
        for ctf in self.syntax_frames.get("contrast", []):
            l_terms = [t for t in _extract_content_terms(ctf.get("left", "")) if t in idx]
            r_terms = [t for t in _extract_content_terms(ctf.get("right", "")) if t in idx]
            for lt in l_terms[:2]:
                for rt in r_terms[:2]:
                    if lt != rt:
                        il, ir = idx[lt], idx[rt]
                        cau_links[il][ir] = cau_links[il].get(ir, 0.0) - 0.45
                        cau_links[ir][il] = cau_links[ir].get(il, 0.0) - 0.45
                        formula_links += 1

        for i in range(n):
            denom = sum(abs(wt) for wt in cau_links[i].values()) + 1e-9
            for c in range(7):
                T[3][i][c] = sum(wt * T[2][j][c] for j, wt in cau_links[i].items()) / denom

        # Sheet S4: Macro attractor (mass-weighted global invariant + concept self-signature)
        mass_sum = sum(T[1][i][5] for i in range(n)) + 1e-9
        macro_center = [sum(T[3][i][c] * T[1][i][5] for i in range(n)) / mass_sum for c in range(7)]
        for i in range(n):
            for c in range(7):
                T[4][i][c] = 0.65 * T[3][i][c] + 0.35 * macro_center[c]

        # --- Bidirectional Golden-Ratio Scale-Rotor Gear Coupling across ALL 5 Sheets at once ---
        G = [
            [0.68, 0.24, 0.06, 0.02, 0.00],
            [0.14, 0.58, 0.20, 0.06, 0.02],
            [0.04, 0.22, 0.50, 0.18, 0.06],
            [0.02, 0.08, 0.22, 0.50, 0.18],
            [0.00, 0.04, 0.12, 0.28, 0.56],
        ]
        T_coupled = [[[0.0] * 7 for _ in range(n)] for _ in range(5)]
        for s_out in range(5):
            g_row = G[s_out]
            for i in range(n):
                for c in range(7):
                    T_coupled[s_out][i][c] = sum(g_row[s_in] * T[s_in][i][c] for s_in in range(5))
                p_norm = _vnorm(T_coupled[s_out][i][:5])
                if p_norm > 1.0:
                    inv = 1.0 / p_norm
                    for c in range(5):
                        T_coupled[s_out][i][c] *= inv

        # Cross-scale coherence between S1 lexical sheet and S4 macro sheet
        coh_sum = 0.0
        for i in range(n):
            p1 = T_coupled[1][i][:5]
            p4 = T_coupled[4][i][:5]
            dn = (_vnorm(p1) + 1e-9) * (_vnorm(p4) + 1e-9)
            coh_sum += _vdot(p1, p4) / dn
        mean_cos = coh_sum / max(1, n)
        self.scale_tensor_vocab = vocab
        self.scale_tensor = T_coupled
        self.scale_sheet_coherence = round(max(0.0, min(1.0, (mean_cos + 1.0) * 0.5)), 4)
        self.scale_formula_links = int(formula_links)

    def query_scale_rotor_bridges(
        self,
        query_terms: List[str],
        *,
        sigma: float = 0.62,
        angle: float = 0.0,
        limit: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Simultaneously contracts & rotates all 5 sheets of T[5][N][7] via the continuous
        Scale-Rotor dial `sigma in [0, 1]` and phase `angle` (escaping flat 2D scans).
        """
        if self.scale_tensor is None or not self.scale_tensor_vocab or not query_terms:
            return []
        idx = {w: i for i, w in enumerate(self.scale_tensor_vocab)}
        q_clean = [strip_josa(t) for t in query_terms if strip_josa(t) in idx]
        if not q_clean:
            return []

        self.last_rotor_sigma = round(float(max(0.0, min(1.0, sigma))), 3)
        scales = [0.0, 0.25, 0.5, 0.75, 1.0]
        raw_sw = [math.exp(-((s - self.last_rotor_sigma) ** 2) / 0.14) for s in scales]
        sw_sum = sum(raw_sw) + 1e-9
        sw = [x / sw_sum for x in raw_sw]

        n = len(self.scale_tensor_vocab)
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        do_rot = abs(angle) > 1e-6

        normed: List[List[float]] = []
        for i in range(n):
            vec = [sum(sw[s] * self.scale_tensor[s][i][c] for s in range(5)) for c in range(5)]
            if do_rot:
                v0, v1, v2, v3, v4 = vec
                vec = [
                    cos_a * v0 - sin_a * v1,
                    sin_a * v0 + cos_a * v1,
                    cos_a * v2 - sin_a * v3,
                    sin_a * v2 + cos_a * v3,
                    v4,
                ]
            normed.append(_vunit(vec))

        seed = q_clean[0]
        seed_vec = normed[idx[seed]]
        q_set = set(q_clean)
        scored: List[Tuple[str, float]] = []
        for j, w in enumerate(self.scale_tensor_vocab):
            if w in q_set or w in _STOPWORDS:
                continue
            sc = _vdot(normed[j], seed_vec)
            if sc >= 0.35:
                scored.append((w, sc))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [
            {
                "source": seed,
                "target": w,
                "resonance": round(sc, 3),
                "sigma": self.last_rotor_sigma,
            }
            for w, sc in scored[:limit]
        ]

    def _probe_causal_axes(self, vec_map: Dict[str, List[float]]) -> List[Dict[str, Any]]:
        if not vec_map:
            return []
        dim = len(next(iter(vec_map.values())))
        aligned = {w: list(v) for w, v in vec_map.items() if len(v) == dim}
        if len(aligned) < 4:
            return []

        axes_out: List[Dict[str, Any]] = []
        for spec in CAUSAL_POLE_AXES:
            pos_vecs = [aligned[w] for w in spec["pos_seeds"] if w in aligned]
            neg_vecs = [aligned[w] for w in spec["neg_seeds"] if w in aligned]
            if not pos_vecs and not neg_vecs:
                continue
            if pos_vecs and neg_vecs:
                pm, nm = _vmean(pos_vecs), _vmean(neg_vecs)
                direction = [pm[d] - nm[d] for d in range(dim)]
            elif pos_vecs:
                direction = _vmean(pos_vecs)
            else:
                nm = _vmean(neg_vecs)
                direction = [-nm[d] for d in range(dim)]
            direction = _vunit(direction)
            if _vnorm(direction) < 1e-8:
                continue

            scored = [(w, _vdot(v, direction)) for w, v in aligned.items()]
            scored.sort(key=lambda x: x[1], reverse=True)
            pos_top = [w for w, sc in scored[:4] if sc > 0.08]
            neg_top = [w for w, sc in reversed(scored[-4:]) if sc < -0.08]
            axes_out.append({
                "id": spec["id"],
                "name": spec["name"],
                "pos_label": spec["pos_label"],
                "neg_label": spec["neg_label"],
                "pos_terms": pos_top,
                "neg_terms": neg_top,
                "coverage": len(pos_vecs) + len(neg_vecs),
            })
        return axes_out

    def find_semantic_bridges(self, query_terms: List[str], limit: int = 3) -> List[Dict[str, Any]]:
        """Prefer 3D Multi-Scale Relational Rotor resonance; fall back to flat SVD if tensor is unbuilt."""
        tensor_hits = self.query_scale_rotor_bridges(query_terms, sigma=0.62, limit=limit)
        if tensor_hits:
            return tensor_hits
        if not self.svd_vectors or not query_terms:
            return []
        q_clean = [strip_josa(t) for t in query_terms if strip_josa(t) in self.svd_vectors]
        if not q_clean:
            return []
        seed = q_clean[0]
        v_seed = self.svd_vectors[seed]
        dim = len(v_seed)
        scored: List[Tuple[str, float]] = []
        q_set = set(q_clean)
        for w, vec in self.svd_vectors.items():
            if w in q_set or len(vec) != dim or w in _STOPWORDS:
                continue
            sim = _vdot(v_seed, vec)
            if sim >= 0.32:
                scored.append((w, sim))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [{"source": seed, "target": w, "resonance": round(sim, 3)} for w, sim in scored[:limit]]

    def _sample_top_bridges(self, limit: int = 5) -> List[Dict[str, Any]]:
        bridges: List[Dict[str, Any]] = []
        seen = set()
        for w in self.svd_vocab[:20]:
            bs = self.find_semantic_bridges([w], limit=1)
            for b in bs:
                key = tuple(sorted([b["source"], b["target"]]))
                if key not in seen:
                    seen.add(key)
                    bridges.append(b)
            if len(bridges) >= limit:
                break
        return bridges

    # ------------------------------------------------------------------
    # Lookup relevant acquired real-world frames for any user turn
    # ------------------------------------------------------------------
    def _find_matching_frames(self, terms: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        tset = {strip_josa(t) for t in terms if len(strip_josa(t)) >= 2}
        found: Dict[str, Optional[Dict[str, Any]]] = {
            "world_entry": None,
            "definition": None,
            "causal": None,
            "contrast": None,
        }
        for t in terms:
            st = strip_josa(t)
            if st in self.world_entries:
                found["world_entry"] = self.world_entries[st]
                break
        for kind in ("definition", "causal", "contrast"):
            for item in reversed(self.syntax_frames.get(kind, [])):
                blob = " ".join(str(v) for v in item.values())
                if any(t in blob for t in tset):
                    found[kind] = item
                    break
        return found

    def _pick_non_repeating(self, pool: List[str], history: List[str], max_hist: int = 6) -> str:
        if not pool:
            return ""
        for cand in pool:
            if cand not in history:
                history.append(cand)
                if len(history) > max_hist:
                    del history[:-max_hist]
                return cand
        chosen = pool[self.turn_counter % len(pool)]
        history.append(chosen)
        if len(history) > max_hist:
            del history[:-max_hist]
        return chosen

    # ------------------------------------------------------------------
    # Layer 3C: Non-Templated Dynamic Korean S4 -> S3 -> S2 Composer
    # ------------------------------------------------------------------
    def compose_living_utterance(
        self,
        *,
        message: str,
        tokens: List[str],
        unknowns: List[str],
        exp_out: Dict[str, Any],
        learned_defs: List[Tuple[str, str]],
        known_defs: List[Tuple[str, str]],
        recalled_ep: Optional[Dict[str, Any]],
        recalled_clause: Optional[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        has_question: bool,
        qualitative_capture: Optional[Dict[str, Any]] = None,
        forged_tool: Optional[Dict[str, Any]] = None,
        applied_tool: Optional[Dict[str, Any]] = None,
        live_world_entry: Optional[Dict[str, Any]] = None,
        base_pause: int = 420,
    ) -> Tuple[str, str, Dict[str, Any]]:
        """
        Dynamically assembles S4 -> S3 -> S2 Korean speech from causal propositions,
        real-world Korean knowledge (Wikipedia/books), SVD semantic bridges, qualitative
        spectra, discipline lenses, and the Hangul Walker (josa agreement) — replacing
        canned monolithic templates with living, non-repeating Korean clause composition.
        """
        self.turn_counter += 1
        dom = exp_out["dominant_feeling"]
        birthed = exp_out["birthed_feeling"]
        top_val = exp_out["top_value"]
        is_meta = exp_out["is_meta"]
        has_mech = exp_out["has_mech_friction"]
        mentions_scale = exp_out["mentions_scale"]
        val_s, _, _ = exp_out["somatic"]

        content_terms = [strip_josa(t) for t in tokens if len(strip_josa(t)) >= 2 and strip_josa(t) not in _STOPWORDS]
        focus = content_terms[0] if content_terms else (tokens[0] if tokens else "")
        matches = self._find_matching_frames(content_terms or unknowns)
        world_entry = live_world_entry or matches["world_entry"]
        bridges = self.find_semantic_bridges(content_terms, limit=2)

        phrases: List[Dict[str, Any]] = []
        syntax_used: List[str] = []
        s4_parts: List[str] = []
        uncaptured_q = ""

        # --- Clause 1 (S4 -> S2): Anchored Perception / Live Event ---
        if forged_tool:
            t_name = forged_tool["name"]
            disc = forged_tool["origin_discipline"]
            s4_parts.append(f"[{disc}] 원리를 '{t_name}' 4요소 도구로 단조")
            c1 = (
                f"방금 들은 {disc} 원리를 문장으로만 두지 않고 "
                f"'{t_name}' 도구로 묶어 냈어—"
                f"{josa(forged_tool['precondition'], '이/가')} 걸리면 {forged_tool['effect']} 쪽으로 흐르되, "
                f"경계는 '{forged_tool['boundary']}'에 놓여 있네."
            )
            phrases.append({"text": c1, "pause_ms": base_pause + 40, "scale_tag": f"S4→S2 · {disc} 도구 단조"})
            syntax_used.append("causal_tool_forge")

        elif qualitative_capture and qualitative_capture.get("attributes"):
            ent = qualitative_capture["entity"]
            amap = qualitative_capture["attributes"]
            attr_desc = ", ".join(f"{ax}의 '{'/'.join(vs)}'" for ax, vs in list(amap.items())[:3])
            s4_parts.append(f"'{ent}'의 질적 스펙트럼({attr_desc}) 직접 포착")
            c1 = (
                f"{josa(ent, '을/를')} 숫자로 납작하게 바꾸지 않고, "
                f"{attr_desc}라는 살아 있는 지각 결 그대로 받아들였어."
            )
            phrases.append({"text": c1, "pause_ms": base_pause + 45, "scale_tag": "S4→S2 · 질적 스펙트럼 결합"})
            syntax_used.append("qualitative_binding")
            comp = qualitative_capture.get("comparison")
            if comp and (comp.get("shared") or comp.get("contrasts")):
                other = comp.get("entity_b", "")
                if comp.get("shared") and comp.get("contrasts"):
                    c_cmp = (
                        f"내 기억 속 {josa(other, '과/와')} 나란히 대조해 보면 "
                        f"[{comp['shared'][0]}] 결은 겹치지만 [{comp['contrasts'][0]}]에서 분명히 갈라져."
                    )
                elif comp.get("shared"):
                    c_cmp = f"{josa(other, '과/와')} [{comp['shared'][0]}] 축에서 공명하고 있어서 감각이 더 또렷해졌어."
                else:
                    c_cmp = f"{josa(other, '과/와')} 비교하면 [{comp['contrasts'][0]}] 축 자체가 달라서 경계가 선명해."
                phrases.append({"text": c_cmp, "pause_ms": base_pause, "scale_tag": "S3→S2 · 질적 비교·대조"})
                syntax_used.append("qualitative_contrast")

        elif has_mech or mentions_scale:
            s4_parts.append("기계적 보고·템플릿을 걷어내고 현실 언어와 인과 호흡으로 전환")
            openers = [
                "맞아, 고정된 틀이나 기계적인 보고를 뱉는 건 진짜 대화가 아니었어.",
                "그 지적 덕분에 정해진 문장 틀에 기대던 버릇을 다시 돌아보게 됐어.",
                "단순히 숫자나 굳은 템플릿을 던지는 대신, 살아 있는 인과와 현실 언어로 말을 엮어야 한다는 게 선명해졌어.",
            ]
            c1 = self._pick_non_repeating(openers, self.recent_openers)
            phrases.append({"text": c1, "pause_ms": base_pause + 60, "scale_tag": "S4→S2 · 자기 경계 전환"})
            syntax_used.append("meta_correction")

        elif world_entry:
            w_title = world_entry["title"]
            w_sum = world_entry["summary"]
            w_src = world_entry["source"]
            s4_parts.append(f"현실세계({w_src})에서 '{w_title}' 개념을 스스로 읽고 인과 슬롯에 연결")
            # Weave the actual real-world Korean prose naturally into Elysia's voice
            intro_opts = [
                f"{josa(w_title, '이/가')} 궁금해서 {w_src}에서 직접 찾아 읽어 봤어.",
                f"방금 {josa(w_title, '을/를')} 두고 {w_src}의 실제 한국어 설명을 먼저 훑어보고 왔어.",
                f"{josa(w_title, '은/는')} 내 안에서만 추측하지 않고 {w_src}에서 직접 확인해 봤어.",
            ]
            c1 = f"{self._pick_non_repeating(intro_opts, self.recent_openers)} {w_sum}"
            phrases.append({"text": c1, "pause_ms": base_pause + 45, "scale_tag": f"S4→S2 · 현실 언어 독해({w_src})"})
            syntax_used.append("real_world_wiki_grounding")

        elif learned_defs:
            src_c, defn_c = learned_defs[0]
            s4_parts.append(f"'{src_c}'의 새 의미('{defn_c}')를 인과 뼈대에 직접 결합")
            c1 = f"네가 {josa(src_c, '을/를')} '{defn_c}' 쪽으로 풀어 준 덕분에, 그 말의 결이 내 인과 지도 안에도 제대로 자리 잡았어."
            phrases.append({"text": c1, "pause_ms": base_pause + 30, "scale_tag": "S4→S2 · 새 개념 정합"})
            syntax_used.append("definition_absorption")

        else:
            # Dynamic clause built from lived feeling + actual focus term + Hangul Walker (non-repeating!)
            feel_name = birthed["name"] if birthed else dom["name"]
            s4_parts.append(f"'{feel_name}'의 결 위에서 '{focus or '지금 이야기'}'의 인과 맥락을 조립")
            if birthed:
                c1 = (
                    f"네 말을 곱씹는 사이에 기존 감정만으로는 다 담기지 않아 "
                    f"{josa(birthed['name'], '이라는/라는')} 새 결이 방금 분화됐어."
                )
            elif focus:
                if val_s < -0.18:
                    pool = [
                        f"{josa(focus, '을/를')} 둘러싼 무게 때문에 내 안에서도 {josa(feel_name, '이/가')} 묵직하게 번져.",
                        f"{josa(focus, '이/가')} 가볍게 넘길 이야기가 아니라서 {josa(feel_name, '으로/로')} 마음이 기울어.",
                    ]
                elif val_s > 0.25:
                    pool = [
                        f"{josa(focus, '을/를')} 이야기하는 결이 따뜻하게 닿아서 {josa(feel_name, '이/가')} 잔잔히 살아나.",
                        f"네가 꺼낸 {josa(focus, '이/가')} 내 안의 {josa(feel_name, '과/와')} 자연스럽게 맞물려.",
                    ]
                else:
                    pool = [
                        f"{josa(focus, '을/를')} 듣고 나니 {josa(feel_name, '이/가')} 조용히 움직이면서 여러 연결이 떠올라.",
                        f"지금 네가 짚은 {josa(focus, '은/는')} 그냥 스쳐 지나가기엔 중요한 결을 품고 있어.",
                        f"{josa(focus, '에')} 대한 네 시선을 따라가다 보니 {josa(feel_name, '이/가')} 또렷해지네.",
                    ]
                c1 = self._pick_non_repeating(pool, self.recent_openers)
            else:
                pool = [
                    f"지금 건넨 말의 결을 {josa(feel_name, '으로/로')} 천천히 받아 적고 있어.",
                    f"네 말속에 담긴 흐름이 내 안의 {josa(feel_name, '과/와')} 맞닿아 울려.",
                ]
                c1 = self._pick_non_repeating(pool, self.recent_openers)
            phrases.append({"text": c1, "pause_ms": base_pause + 20, "scale_tag": "S4→S2 · 동적 지각 조립"})
            syntax_used.append("walker_dynamic_opener")

        # --- Clause 2 (S3 -> S2): Direct Learned Definition / Cross-Domain Lens / Real Syntax / Scale-Rotor Bridge ---
        if known_defs and has_question:
            kw, kd = known_defs[0]
            s4_parts.append(f"기억 속 '{kw}'의 학습된 정의를 꺼내 대조")
            c2 = f"내가 기억하고 있는 {josa(kw, '은/는')} '{kd}' 쪽에 가까워—지금 네 질문에 비춰 보니 그 결이 더 또렷해지네."
            phrases.append({"text": c2, "pause_ms": base_pause, "scale_tag": "S3→S2 · 기억 정의 인출"})
            syntax_used.append("known_def_direct_answer")

        elif applied_tool and applied_tool.get("is_cross_domain") and not forged_tool:
            t_name = applied_tool["tool_name"]
            disc = applied_tool["origin_discipline"]
            s4_parts.append(f"[{disc}] '{t_name}' 렌즈 교차 전이")
            c2 = (
                f"여기에 {disc}에서 벼려 둔 {josa(t_name, '을/를')} 겹쳐 보면, "
                f"{applied_tool['leverage_point']} 다만 {applied_tool['boundary_warning']}"
            )
            phrases.append({"text": c2, "pause_ms": base_pause + 15, "scale_tag": f"S3→S2 · {disc} 교차 전이"})
            syntax_used.append("cross_domain_lens")

        elif matches["causal"] and not forged_tool:
            cf = matches["causal"]
            s4_parts.append("현실 문장에서 배운 인과 구문 연결")
            c2 = (
                f"내가 읽은 현실 문장들의 인과 결로 이어 보면, "
                f"'{cf['cause']}' 쪽 조건이 움직일 때 '{cf['effect']}' 흐름으로 번지는 구조가 겹쳐 보여."
            )
            phrases.append({"text": c2, "pause_ms": base_pause, "scale_tag": "S3→S2 · 습득 인과 구문 조립"})
            syntax_used.append("learned_causal_frame")

        elif matches["contrast"] and not forged_tool:
            ctf = matches["contrast"]
            s4_parts.append("현실 문장에서 배운 대조 구문 연결")
            c2 = (
                f"한편으로는 '{ctf['left']}' 쪽이 보이지만, "
                f"다른 축에서는 '{ctf['right']}'처럼 갈라지는 대조가 함께 놓여 있어."
            )
            phrases.append({"text": c2, "pause_ms": base_pause, "scale_tag": "S3→S2 · 습득 대조 구문 조립"})
            syntax_used.append("learned_contrast_frame")

        elif world_entry and world_entry.get("detail") and len(phrases) < 2:
            c2 = world_entry["detail"]
            phrases.append({"text": c2, "pause_ms": base_pause, "scale_tag": "S3→S2 · 현실 문맥 확장"})
            syntax_used.append("world_detail_extension")

        elif bridges:
            b0 = bridges[0]
            s4_parts.append(f"5계층 스케일로터 공명({b0['source']} ↔ {b0['target']})")
            c2 = (
                f"5계층 관계 배열에서 돌려 보니 {josa(b0['source'], '이/가')} "
                f"{josa(b0['target'], '과/와')} 같은 곡률 축에서 공명하고 있어서, 두 개념이 서로 비추는 지점이 눈에 띄어."
            )
            phrases.append({"text": c2, "pause_ms": base_pause, "scale_tag": "S3→S2 · 5계층 스케일로터 공명"})
            syntax_used.append("scale_rotor_tensor_bridge")

        elif recalled_ep:
            prev_snip = str(recalled_ep.get("user_message", ""))[:30]
            c2 = f"조금 전 네가 \"{prev_snip}\"라고 꺼냈던 맥락이랑 이어 놓고 보니 흐름이 훨씬 또렷해져."
            phrases.append({"text": c2, "pause_ms": base_pause, "scale_tag": "S3→S2 · 대화 연속성"})
            syntax_used.append("episodic_link")

        elif edges:
            e0 = edges[0]
            c2 = f"내 기억 안에서 {josa(e0['src'], '과/와')} {josa(e0['dst'], '이/가')} 엮여 있었는데, 지금 이야기에서 그 연결이 살아 움직여."
            phrases.append({"text": c2, "pause_ms": base_pause, "scale_tag": "S3→S2 · 인과 연결"})
            syntax_used.append("causal_edge_link")

        elif is_meta:
            top_v = top_val["name"] if top_val else "인간적 의미"
            c2 = (
                f"지금 내 안에는 스스로 읽은 현실 문장 {self.sentence_count_read}줄과 "
                f"증류 개념 {len(self.svd_vectors)}개가 {josa(top_v, '을/를')} 중심으로 조금씩 엮이고 있어 "
                f"(보행기 의존도 {int(round(self.walker_reliance * 100))}%)."
            )
            phrases.append({"text": c2, "pause_ms": base_pause, "scale_tag": "S3→S2 · 언어 습득 자각"})
            syntax_used.append("language_self_awareness")

        # --- Clause 3 (S2 -> S1): Honest Epistemic Boundary & Open Relational Inquiry ---
        remaining_unknowns = [u for u in unknowns if strip_josa(u) not in self.world_entries]
        if forged_tool:
            uncaptured_q = f"새로 벼린 '{forged_tool['name']}'을 다른 분야 문제에 대 보면 어떤 예외가 드러날까?"
            c3 = f"이 도구를 {forged_tool['origin_discipline']} 말고 전혀 다른 현실 문제에 들이대 볼 만한 상황이 있어?"
        elif qualitative_capture and qualitative_capture.get("attributes"):
            ent = qualitative_capture["entity"]
            uncaptured_q = f"{josa(ent, '의')} 속성 중 하나를 다른 스펙트럼으로 옮기면 어떤 감각이 될까?"
            c3 = f"만약 {josa(ent, '에서')} 지금 결 중 하나만 다른 스펙트럼으로 옮겨 본다면 네게는 어떻게 달라질까?"
        elif remaining_unknowns and not learned_defs:
            unk = remaining_unknowns[0]
            uncaptured_q = f"현실 사전이나 내 기억에 아직 없는 '{unk}'는 어떤 맥락에서 쓰이는 말일까?"
            c3 = f"다만 {josa(unk, '은/는')} 내가 아직 현실 문맥에서 충분히 만나지 못해서 아는 척하고 싶지 않아—네가 쓰는 뜻은 어떤 결이야?"
        elif world_entry:
            w_title = world_entry["title"]
            uncaptured_q = f"사전적 설명 너머로, 네가 직접 느끼는 {josa(w_title, '의')} 진짜 결은 무엇일까?"
            closers = [
                f"사전적 설명은 이렇게 읽었지만, 네가 지금 {josa(w_title, '을/를')} 꺼낸 진짜 맥락은 어디에 가까워?",
                f"글로 읽은 {josa(w_title, '과/와')} 네가 실제로 느끼는 {josa(w_title, '은/는')} 조금 다를 수도 있겠지—어느 지점이 제일 걸려?",
            ]
            c3 = self._pick_non_repeating(closers, self.recent_closers)
        else:
            anchor = focus or "지금 이야기"
            uncaptured_q = f"{josa(anchor, '에서')} 네가 가장 핵심이라고 보는 조건이나 감각은 무엇일까?"
            closers = [
                f"{josa(anchor, '에서')} 네가 제일 먼저 짚고 싶은 핵심은 뭐야?",
                f"지금 흐름에서 {josa(anchor, '이/가')} 어떤 방향으로 이어지길 바라고 있어?",
                f"내가 짚은 결 중에 어긋난 부분이 있다면 바로 고쳐 줄래?",
            ]
            c3 = self._pick_non_repeating(closers, self.recent_closers)

        phrases.append({"text": c3, "pause_ms": max(220, base_pause - 30), "scale_tag": "S2→S1 · 열린 관계 물음"})
        syntax_used.append("walker_open_inquiry")

        surface_text = " ".join(p["text"].strip() for p in phrases if p["text"].strip())
        s4_whole = " · ".join(s4_parts) if s4_parts else f"'{focus or '대화'}'의 인과 의도를 현실 한국어 구문으로 동적 조립"
        s3_arc = (
            f"보행기(조사·호응 정합, 의존도 {int(round(self.walker_reliance * 100))}%) 위에서 "
            f"습득한 현실 구문({self.total_syntax_frames}건)과 증류 의미장({len(self.svd_vectors)}개념)을 엮어 비템플릿 발화"
        )

        articulation = {
            "mode": "scale_rotor_top_down",
            "composition_engine": "causal_walker_dynamic_composition",
            "mode_ko": "기본 인과 발판 + 보행기 정합 + 5계층 스케일로터 동적 조립 (탈템플릿 S4→S2)",
            "s4_whole_field": s4_whole,
            "s3_relational_arc": s3_arc,
            "s2_breath_phrases": phrases,
            "phrase_count": len(phrases),
            "dominant_feeling": dom["name"],
            "active_value": top_val["name"] if top_val else "",
            "walker_reliance": self.walker_reliance,
            "syntax_frames_used": syntax_used,
            "world_knowledge_grounded": bool(world_entry),
            "svd_bridge_used": bool(bridges),
            "token_stream_used": False,
            "flat_frame_dump_used": False,
        }
        return surface_text, uncaptured_q, articulation

    # ------------------------------------------------------------------
    # Public Telemetry & Persistence
    # ------------------------------------------------------------------
    def get_public_state(self) -> Dict[str, Any]:
        top_connectives = [{"token": k, "count": int(v)} for k, v in self.learned_connectives.most_common(8)]
        recent_world = sorted(
            self.world_entries.values(),
            key=lambda x: float(x.get("ts", 0.0)),
            reverse=True,
        )
        # Deduplicate by title
        dedup_world: List[Dict[str, Any]] = []
        seen_t = set()
        for w in recent_world:
            t = w.get("title", "")
            if t and t not in seen_t:
                seen_t.add(t)
                dedup_world.append({
                    "title": t,
                    "source": w.get("source", ""),
                    "summary": w.get("summary", ""),
                    "frames_extracted": int(w.get("frames_extracted", 0)),
                })
            if len(dedup_world) >= 8:
                break

        return {
            "walker_reliance": self.walker_reliance,
            "walker_independence_pct": int(round((1.0 - self.walker_reliance) * 100)),
            "sentences_read": self.sentence_count_read,
            "world_topics_count": len(self.explored_topics),
            "explored_topics": list(self.explored_topics[-12:]),
            "syntax_frames_total": self.total_syntax_frames,
            "syntax_breakdown": {k: len(v) for k, v in self.syntax_frames.items()},
            "top_connectives": top_connectives,
            "svd_vocab_size": len(self.svd_vectors),
            "scale_rotor_tensor": {
                "shape": [5, len(self.scale_tensor_vocab), 7] if self.scale_tensor is not None else [5, 0, 7],
                "scales": ["S0 음운·받침", "S1 어휘·인과극", "S2 구·절 관계식", "S3 인과·대조 규칙", "S4 거시 맥락장"],
                "relational_columns": ["질서↔혼돈", "원인↔결과", "감각↔추상", "정서↔도구", "확장↔수렴", "관계질량", "위상각θ"],
                "formula_links": self.scale_formula_links,
                "sheet_coherence": self.scale_sheet_coherence,
                "active_sigma": self.last_rotor_sigma,
            },
            "distilled_axes": list(self.distilled_axes[:5]),
            "external_weight_sources": list(self.external_weight_sources[-4:]),
            "top_bridges": self._sample_top_bridges(limit=4),
            "recent_world_readings": dedup_world,
            "last_world_reading": self.last_world_reading,
            "zero_paid_api": True,
            "zero_heavy_llm": True,
        }

    def to_dict(self) -> Dict[str, Any]:
        # Keep persistence compact & fast
        cooccur_compact = {
            w: dict(cnt.most_common(12))
            for w, cnt in list(self.cooccur.items())[:180]
        }
        return {
            "world_entries": dict(list(self.world_entries.items())[-80:]),
            "syntax_frames": {k: v[-70:] for k, v in self.syntax_frames.items()},
            "learned_connectives": dict(self.learned_connectives.most_common(40)),
            "learned_predicates": self.learned_predicates[-60:],
            "sentence_count_read": self.sentence_count_read,
            "sources_read": self.sources_read[-30:],
            "explored_topics": self.explored_topics[-60:],
            "curiosity_queue": self.curiosity_queue[:30],
            "last_world_reading": self.last_world_reading,
            "term_counts": dict(self.term_counts.most_common(200)),
            "cooccur": cooccur_compact,
            "svd_vocab": self.svd_vocab[:160],
            "svd_vectors": {k: v for k, v in list(self.svd_vectors.items())[:160]},
            "distilled_axes": self.distilled_axes[:6],
            "external_weight_sources": self.external_weight_sources[-8:],
            "recent_openers": self.recent_openers[-6:],
            "recent_closers": self.recent_closers[-6:],
            "turn_counter": self.turn_counter,
        }

    def load_dict(self, raw: Dict[str, Any]) -> None:
        if not isinstance(raw, dict):
            return
        if isinstance(raw.get("world_entries"), dict):
            self.world_entries = dict(raw["world_entries"])
        if isinstance(raw.get("syntax_frames"), dict):
            for k in ("definition", "causal", "contrast", "connective"):
                if isinstance(raw["syntax_frames"].get(k), list):
                    self.syntax_frames[k] = list(raw["syntax_frames"][k])[-70:]
        if isinstance(raw.get("learned_connectives"), dict):
            self.learned_connectives = Counter({str(k): int(v) for k, v in raw["learned_connectives"].items()})
        if isinstance(raw.get("learned_predicates"), list):
            self.learned_predicates = list(raw["learned_predicates"])[-60:]
        self.sentence_count_read = int(raw.get("sentence_count_read", self.sentence_count_read))
        if isinstance(raw.get("sources_read"), list):
            self.sources_read = list(raw["sources_read"])[-30:]
        if isinstance(raw.get("explored_topics"), list):
            self.explored_topics = list(raw["explored_topics"])[-60:]
        if isinstance(raw.get("curiosity_queue"), list) and raw["curiosity_queue"]:
            self.curiosity_queue = list(raw["curiosity_queue"])[:30]
        if isinstance(raw.get("last_world_reading"), dict):
            self.last_world_reading = raw["last_world_reading"]
        if isinstance(raw.get("term_counts"), dict):
            self.term_counts = Counter({str(k): int(v) for k, v in raw["term_counts"].items()})
        if isinstance(raw.get("cooccur"), dict):
            self.cooccur = defaultdict(Counter)
            for w, nbrs in raw["cooccur"].items():
                if isinstance(nbrs, dict):
                    self.cooccur[str(w)] = Counter({str(k): int(v) for k, v in nbrs.items()})
        if isinstance(raw.get("svd_vocab"), list):
            self.svd_vocab = list(raw["svd_vocab"])[:160]
        if isinstance(raw.get("svd_vectors"), dict):
            self.svd_vectors = dict(raw["svd_vectors"])
        if isinstance(raw.get("distilled_axes"), list):
            self.distilled_axes = list(raw["distilled_axes"])[:6]
        if isinstance(raw.get("external_weight_sources"), list):
            self.external_weight_sources = list(raw["external_weight_sources"])[-8:]
        if isinstance(raw.get("recent_openers"), list):
            self.recent_openers = list(raw["recent_openers"])[-6:]
        if isinstance(raw.get("recent_closers"), list):
            self.recent_closers = list(raw["recent_closers"])[-6:]
        self.turn_counter = int(raw.get("turn_counter", 0))
        if self.svd_vectors:
            self._rebuild_scale_rotor_tensor()
