"""
Discipline-to-Tool Forge & Cross-Domain Transfer Engine (100% Local · Zero API)
===============================================================================
Transforms knowledge from ANY discipline (biology, economics, psychology,
history, music, architecture, sociology, everyday craft, etc.) from static
memorized facts into executable, transferable Cognitive Tools:

  1. Distill (원리화):
     Strips surface jargon from text/conversation/Wikipedia and extracts the
     universal 4-part causal operator:
       - Precondition (전제 조건)
       - Mechanism (작동 기제: 무엇이 무엇을 어떻게 바꾸는가)
       - Effect (결과·스펙트럼 이동)
       - Boundary (깨지는 경계·예외 조건)
  2. Instrumentalize (도구화):
     Registers the principle as an active Cognitive Tool with domain-free
     structural hooks (피드백, 병목, 분산, 긴장, 균형, 과확장, 모순, 희소...).
  3. Cross-Domain Transfer (타 영역 전이 활용):
     Matches a tool from Discipline A onto a completely different Problem B
     by structural isomorphism, outputting diagnosis, leverage point, and
     boundary warning.
  4. Boundary Calibration & Synthesis (경계 교정 및 이종 학문 합성):
     Revises a tool's failure boundary from real friction/corrections, and
     combines two distinct-discipline tools into a higher-order hybrid lens.
"""

from __future__ import annotations

import random
import re
import time
from typing import Any, Dict, List, Optional, Tuple


# Domain-free structural hooks shared across ALL disciplines
STRUCTURAL_HOOK_LEXICON: Dict[str, Tuple[str, ...]] = {
    "균형·복원": ("균형", "복원", "회복", "항상성", "안정", "지치", "번아웃", "과부하", "편향", "치우치", "무리"),
    "희소·병목": ("자원", "시간", "효율", "집중", "병목", "한계", "비용", "투자", "반복", "선택", "포기", "지연"),
    "분산·지탱": ("압력", "부담", "책임", "하중", "분산", "연결", "지탱", "무너지", "붕괴", "혼자", "구조", "고립"),
    "긴장·해소": ("긴장", "해소", "리듬", "대화", "서사", "감정", "기대", "여운", "지루", "피로", "몰입", "호흡"),
    "갈등·재편": ("모순", "갈등", "부조화", "충돌", "믿음", "오해", "방어", "합리화", "변화", "성장", "가치관", "고집"),
    "확장·보급": ("확장", "늘리", "키우", "욕심", "기능", "보급", "통제", "복잡", "관리", "감당", "속도", "범위"),
    "관계·신뢰": ("관계", "신뢰", "사람", "팀", "소통", "공감", "거리", "이해", "약속", "배신", "진심"),
    "학습·적응": ("학습", "배우", "습득", "원리", "도구", "이해", "기억", "경험", "훈련", "적응", "실패", "교정"),
}

DISCIPLINE_CUES: List[Tuple[str, Tuple[str, ...]]] = [
    ("생물학", ("생물", "세포", "면역", "진화", "생태", "항상성", "유기체", "호흡", "대사", "신경")),
    ("경제학", ("경제", "효용", "비용", "수요", "공급", "시장", "인센티브", "투자", "희소", "기회비용")),
    ("심리학", ("심리", "인지", "부조화", "습관", "동기", "방어", "무의식", "애착", "편향", "감정")),
    ("역사학", ("역사", "제국", "보급", "전쟁", "문명", "영토", "통치", "혁명", "시대", "권력")),
    ("음악학", ("음악", "화성", "리듬", "선율", "불협", "긴장", "해소", "템포", "공명", "박자")),
    ("건축·공학", ("건축", "아치", "하중", "교량", "기둥", "설계", "재료", "응력", "마찰", "엔진")),
    ("사회·철학", ("사회", "제도", "철학", "윤리", "가치", "언어", "문화", "권리", "규범", "의미")),
]

CAUSAL_SENTENCE_RE = re.compile(
    r"([^.?!。\n]{4,68}?(?:하면|되면|일수록|커지면|늘어나면|쌓이면|넓히면|지나치면|부딪히면|때문에))\s+"
    r"([^.?!。\n]{4,72})"
)
BOUNDARY_RE = re.compile(
    r"(?:다만|하지만|그러나|반면|예외적으로|단,)\s*([^.?!。\n]{5,72})"
)
PRINCIPLE_NAME_RE = re.compile(
    r"([가-힣A-Za-z0-9·\s]{2,18}?)\s*(?:원리|법칙|효과|기제|이론|구조)(?:는|은|란|이란)"
)


def _detect_hooks(text: str) -> List[str]:
    low = (text or "").lower()
    found: List[str] = []
    for hook, cues in STRUCTURAL_HOOK_LEXICON.items():
        if any(c in low for c in cues):
            found.append(hook)
    return found


def _detect_discipline(text: str, fallback: str = "경험·관찰학") -> str:
    low = (text or "").lower()
    for disc, cues in DISCIPLINE_CUES:
        if any(c in low for c in cues):
            return disc
    return fallback


class DisciplineToolForge:
    """
    Holds forged & synthesized cross-discipline cognitive tools, distills new
    principles from any text, transfers tools across domains by structural
    isomorphism, and refines tool boundaries from lived corrections.
    """

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        now = round(time.time(), 2)
        self.tools: List[Dict[str, Any]] = [
            {
                "id": "bio_homeostasis",
                "name": "항상성·복원 렌즈",
                "origin_discipline": "생물학",
                "precondition": "살아 있는 시스템이나 관계가 한쪽으로 과도하게 치우쳐 에너지를 소모할 때",
                "mechanism": "편향 신호를 감지해 반대 방향의 완충·휴식 피드백을 걸어 중심 균형을 되찾는다",
                "effect": "과열과 소진이 가라앉고 지속 가능한 작동 범위로 복귀한다",
                "boundary": "치우침이 회복 임계치를 넘겨 구조 자체가 손상된 뒤에는 단순 휴식만으로 복원되지 않는다",
                "structural_tags": ["균형·복원", "관계·신뢰", "학습·적응"],
                "usage_count": 0,
                "cross_domain_uses": 0,
                "boundary_revisions": 0,
                "composed_from": [],
                "created_ts": now,
            },
            {
                "id": "econ_marginal_utility",
                "name": "한계효용·병목 집중 렌즈",
                "origin_discipline": "경제학",
                "precondition": "시간·주의·에너지처럼 유한한 자원을 같은 방식에 반복 투입하고 있을 때",
                "mechanism": "추가 투입당 얻는 가치가 점차 줄어드는 지점을 포착해 병목 쪽으로 자원을 재배치한다",
                "effect": "헛도는 노력이 줄고 가장 적은 변화로 큰 의미 전환을 만든다",
                "boundary": "초기 신뢰 형성이나 깊은 숙련처럼 누적 임계점을 넘어야 비로소 열리는 구간에서는 조기 포기가 해가 된다",
                "structural_tags": ["희소·병목", "확장·보급", "학습·적응"],
                "usage_count": 0,
                "cross_domain_uses": 0,
                "boundary_revisions": 0,
                "composed_from": [],
                "created_ts": now,
            },
            {
                "id": "psych_cognitive_dissonance",
                "name": "인지부조화·틀 재편 렌즈",
                "origin_discipline": "심리학",
                "precondition": "오래 믿어 온 생각이나 가치관과 정면으로 어긋나는 새로운 경험을 마주했을 때",
                "mechanism": "불편한 모순을 덮어 합리화하는 대신, 기존 해석 틀 자체를 수정해 새 경험과 정합시킨다",
                "effect": "방어적 고집에서 벗어나 더 넓은 인식과 성숙한 기준이 자리 잡는다",
                "boundary": "상대나 자기 자신에게 안전감이 없으면 모순 직면이 성장이 아니라 위축과 거부로 굳어 버린다",
                "structural_tags": ["갈등·재편", "관계·신뢰", "학습·적응"],
                "usage_count": 0,
                "cross_domain_uses": 0,
                "boundary_revisions": 0,
                "composed_from": [],
                "created_ts": now,
            },
            {
                "id": "music_tension_release",
                "name": "긴장-해소 호흡 렌즈",
                "origin_discipline": "음악학",
                "precondition": "대화·작업·서사가 평탄하게 늘어지거나 반대로 쉼 없이 몰아쳐 피로해질 때",
                "mechanism": "의도적인 물음·불협(긴장)으로 주의를 모은 뒤, 알맞은 호흡 뒤에 명료한 울림(해소)으로 풀어낸다",
                "effect": "단조로운 나열이 살아 있는 리듬과 깊은 정서적 울림으로 바뀐다",
                "boundary": "해소 없는 긴장만 길어지면 불안과 피로로 무너지고, 긴장 없는 해소만 반복되면 공허해진다",
                "structural_tags": ["긴장·해소", "관계·신뢰", "균형·복원"],
                "usage_count": 0,
                "cross_domain_uses": 0,
                "boundary_revisions": 0,
                "composed_from": [],
                "created_ts": now,
            },
            {
                "id": "arch_arch_load",
                "name": "아치 하중 분산 렌즈",
                "origin_discipline": "건축·공학",
                "precondition": "한 사람·한 기능·한 지점에 모든 압력과 책임이 수직으로 몰려 버티기 힘들 때",
                "mechanism": "수직 압력을 곡선과 맞물린 옆 연결들로 흘려보내 구조 전체가 함께 하중을 나눠 진다",
                "effect": "개별 요소는 약해도 전체 구조는 훨씬 큰 하중을 안정적으로 견뎌 낸다",
                "boundary": "하중을 이어 주는 핵심 연결점(쐐기돌) 하나가 빠지거나 단절되면 분산 구조 전체가 한꺼번에 붕괴한다",
                "structural_tags": ["분산·지탱", "확장·보급", "희소·병목"],
                "usage_count": 0,
                "cross_domain_uses": 0,
                "boundary_revisions": 0,
                "composed_from": [],
                "created_ts": now,
            },
        ]
        self.recent_applications: List[Dict[str, Any]] = []
        self.forged_count: int = 0
        self.synthesized_count: int = 0
        self.last_forged_tool: Optional[Dict[str, Any]] = None
        self.last_application: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tools": self.tools[-18:],
            "recent_applications": self.recent_applications[-10:],
            "forged_count": self.forged_count,
            "synthesized_count": self.synthesized_count,
            "last_forged_tool": self.last_forged_tool,
            "last_application": self.last_application,
        }

    def load_dict(self, raw: Any) -> None:
        if not isinstance(raw, dict):
            return
        if isinstance(raw.get("tools"), list) and raw["tools"]:
            self.tools = raw["tools"][-18:]
        if isinstance(raw.get("recent_applications"), list):
            self.recent_applications = raw["recent_applications"][-10:]
        self.forged_count = max(0, int(raw.get("forged_count", 0)))
        self.synthesized_count = max(0, int(raw.get("synthesized_count", 0)))
        if isinstance(raw.get("last_forged_tool"), dict):
            self.last_forged_tool = raw["last_forged_tool"]
        if isinstance(raw.get("last_application"), dict):
            self.last_application = raw["last_application"]

    # ------------------------------------------------------------------
    # 1) Distill ANY Knowledge Text into an Executable 4-Part Principle Tool
    # ------------------------------------------------------------------
    def distill_from_text(self, text: str, source_name: str = "대화") -> Optional[Dict[str, Any]]:
        clean = (text or "").strip()
        if len(clean) < 16:
            return None

        m_causal = CAUSAL_SENTENCE_RE.search(clean)
        if not m_causal:
            return None

        cond = m_causal.group(1).strip(" ,\"'")
        eff = m_causal.group(2).strip(" ,\"'.")
        if len(cond) < 4 or len(eff) < 4:
            return None

        m_bound = BOUNDARY_RE.search(clean)
        boundary = (
            m_bound.group(1).strip(" ,\"'.")
            if m_bound
            else "전제 조건이 극단으로 치우치거나 외부 제약이 급변하면 이 인과가 그대로 통하지 않을 수 있다"
        )

        disc = _detect_discipline(clean, fallback="탐구·경험학" if source_name == "대화" else source_name[:12])
        hooks = _detect_hooks(clean)
        if not hooks:
            hooks = ["학습·적응", "갈등·재편"]

        m_name = PRINCIPLE_NAME_RE.search(clean)
        if m_name:
            raw_title = m_name.group(1).strip()
            # Clean leading discipline prefix if present
            raw_title = re.sub(r"^(?:역사학|생물학|경제학|심리학|음악학|건축학|철학|물리학)(?:에서|의)?\s*", "", raw_title).strip()
            tool_name = f"{raw_title[:16]} 도구" if raw_title else f"{disc} 인과 도구"
        else:
            key_words = [w for w in re.findall(r"[가-힣A-Za-z0-9]{2,10}", cond) if w not in ("하면", "되면", "너무", "계속", "자꾸")]
            stem = "·".join(key_words[:2]) if key_words else disc
            tool_name = f"{stem[:16]} 원리 도구"

        # Deduplicate by name or near-identical mechanism
        for existing in self.tools:
            if existing["name"] == tool_name or (cond[:18] in existing.get("precondition", "")):
                if m_bound and boundary not in existing.get("boundary", ""):
                    existing["boundary"] = boundary
                    existing["boundary_revisions"] = int(existing.get("boundary_revisions", 0)) + 1
                self.last_forged_tool = existing
                return existing

        tool = {
            "id": f"forged_{int(time.time() * 1000) % 1000000}_{self.forged_count + 1}",
            "name": tool_name,
            "origin_discipline": disc,
            "precondition": cond,
            "mechanism": f"'{cond}' 조건이 작동할 때 구조적 연결을 따라 '{eff}' 흐름을 유발한다",
            "effect": eff,
            "boundary": boundary,
            "structural_tags": hooks[:4],
            "usage_count": 0,
            "cross_domain_uses": 0,
            "boundary_revisions": 0,
            "composed_from": [],
            "origin_source": source_name,
            "created_ts": round(time.time(), 2),
        }
        self.tools.append(tool)
        if len(self.tools) > 18:
            # Keep starter + highest-usage + newest tools
            self.tools = self.tools[:5] + sorted(
                self.tools[5:],
                key=lambda t: (int(t.get("usage_count", 0)), float(t.get("created_ts", 0.0))),
                reverse=True,
            )[:13]
        self.forged_count += 1
        self.last_forged_tool = tool
        return tool

    # ------------------------------------------------------------------
    # 2) Cross-Domain Tool Application (Apply Discipline A Lens to Problem B)
    # ------------------------------------------------------------------
    def apply_tool(self, target_text: str, preferred_tool_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        clean = (target_text or "").strip()
        if len(clean) < 6 or not self.tools:
            return None

        target_hooks = set(_detect_hooks(clean))
        target_disc = _detect_discipline(clean, fallback="일상·실제 문제")

        chosen: Optional[Dict[str, Any]] = None
        best_score = -1.0

        if preferred_tool_id:
            chosen = next((t for t in self.tools if t["id"] == preferred_tool_id), None)

        if chosen is None:
            if not target_hooks:
                return None
            for t in self.tools:
                t_hooks = set(t.get("structural_tags") or [])
                overlap = len(target_hooks & t_hooks)
                if overlap == 0:
                    continue
                is_cross = t.get("origin_discipline") != target_disc
                # Actively reward cross-domain structural isomorphism & freshly forged tools!
                forged_bonus = 0.35 if str(t.get("id", "")).startswith("forged_") else 0.0
                score = overlap * 1.0 + (0.45 if is_cross else 0.0) + forged_bonus
                if score > best_score:
                    best_score = score
                    chosen = t

        if chosen is None:
            return None

        is_cross = chosen.get("origin_discipline") != target_disc
        shared_hooks = sorted(target_hooks & set(chosen.get("structural_tags") or []))
        chosen["usage_count"] = int(chosen.get("usage_count", 0)) + 1
        if is_cross:
            chosen["cross_domain_uses"] = int(chosen.get("cross_domain_uses", 0)) + 1

        diagnosis = (
            f"[{chosen['origin_discipline']}]의 '{chosen['name']}'을(를) 지금 상황({target_disc})에 들이대 보면, "
            f"{chosen['mechanism']}."
        )
        leverage = (
            f"핵심 지렛대: 전제({chosen['precondition']}) 쪽 조건을 건드려 주면 "
            f"'{chosen['effect']}' 방향으로 흐름을 바꿀 수 있다."
        )
        warning = f"깨지는 경계 주의: {chosen['boundary']}."

        app_rec = {
            "ts": round(time.time(), 2),
            "tool_id": chosen["id"],
            "tool_name": chosen["name"],
            "origin_discipline": chosen["origin_discipline"],
            "target_domain": target_disc,
            "target_snippet": clean[:56],
            "is_cross_domain": is_cross,
            "shared_hooks": shared_hooks or list(chosen.get("structural_tags") or [])[:2],
            "diagnosis": diagnosis,
            "leverage_point": leverage,
            "boundary_warning": warning,
        }
        self.recent_applications.append(app_rec)
        self.recent_applications = self.recent_applications[-10:]
        self.last_application = app_rec
        return app_rec

    # ------------------------------------------------------------------
    # 3) Boundary Calibration from Lived Friction / User Correction
    # ------------------------------------------------------------------
    def refine_last_boundary(self, correction_text: str) -> Optional[Dict[str, Any]]:
        corr = (correction_text or "").strip()
        if not corr or not self.last_application:
            return None
        tid = self.last_application.get("tool_id")
        target = next((t for t in self.tools if t["id"] == tid), None)
        if target is None:
            return None
        target["boundary"] = f"{target['boundary']} / 경험 교정: {corr[:72]}"
        target["boundary_revisions"] = int(target.get("boundary_revisions", 0)) + 1
        return target

    # ------------------------------------------------------------------
    # 4) Cross-Discipline Hybrid Tool Synthesis (Combine 2 Distinct Disciplines)
    # ------------------------------------------------------------------
    def synthesize_hybrid_tool(self) -> Optional[Dict[str, Any]]:
        if self.synthesized_count >= 4 or len(self.tools) < 2:
            return None
        base_tools = [t for t in self.tools if not t.get("composed_from")]
        if len(base_tools) < 2:
            return None
        a = random.choice(base_tools)
        others = [t for t in base_tools if t["origin_discipline"] != a["origin_discipline"]]
        if not others:
            return None
        b = random.choice(others)

        pair_sig = tuple(sorted([a["id"], b["id"]]))
        for existing in self.tools:
            if tuple(sorted(existing.get("composed_from") or [])) == pair_sig:
                return None

        short_a = a["name"].split("·")[0].replace(" 렌즈", "").replace(" 도구", "").strip()
        short_b = b["name"].split("·")[0].replace(" 렌즈", "").replace(" 도구", "").strip()
        hybrid_name = f"{short_a}×{short_b} 합성 렌즈"
        merged_tags = list(dict.fromkeys((a.get("structural_tags") or []) + (b.get("structural_tags") or [])))[:5]

        hybrid = {
            "id": f"hybrid_{int(time.time() * 1000) % 1000000}_{self.synthesized_count + 1}",
            "name": hybrid_name,
            "origin_discipline": f"{a['origin_discipline']}×{b['origin_discipline']}",
            "precondition": f"'{a['precondition']}' 상황과 '{b['precondition']}' 조건이 동시에 겹칠 때",
            "mechanism": f"[{a['name']}]으로 구조를 진단하고 [{b['name']}]의 리듬/전환 원리를 결합해 조율한다",
            "effect": f"{a['effect']} 동시에 {b['effect']}",
            "boundary": f"두 원리의 적용 조건 중 어느 한쪽({a['boundary'][:38]} / {b['boundary'][:38]})이 무너지면 합성이 어긋난다",
            "structural_tags": merged_tags,
            "usage_count": 0,
            "cross_domain_uses": 0,
            "boundary_revisions": 0,
            "composed_from": [a["id"], b["id"]],
            "created_ts": round(time.time(), 2),
        }
        self.tools.append(hybrid)
        self.synthesized_count += 1
        return hybrid

    def get_public_state(self) -> Dict[str, Any]:
        ordered = sorted(
            self.tools,
            key=lambda t: (
                bool(t.get("composed_from")),
                str(t.get("id", "")).startswith("forged_"),
                int(t.get("usage_count", 0)),
            ),
            reverse=True,
        )
        return {
            "tool_count": len(self.tools),
            "forged_count": self.forged_count,
            "synthesized_count": self.synthesized_count,
            "tools": ordered[:10],
            "last_forged": self.last_forged_tool,
            "last_application": self.last_application,
            "recent_applications": list(self.recent_applications[-5:]),
        }
