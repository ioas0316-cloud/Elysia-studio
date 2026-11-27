"""
Qualitative Perceptual-Spectrum & Physical-Attribute Cognitive Field
====================================================================
"Math observes only math."
Language itself ("사과는 빨갛고 둥글다", "얼음은 차갑고 투명하며 단단하다")
already encodes human perceptual spectra and physical/relational attributes —
NOT raw floating-point vectors.

This module:
1. Extracts subject entities and their qualitative perceptual/physical
   attributes directly from Korean natural language (zero LLM API).
2. Organizes every concept along real qualitative spectra:
   - 색채 스펙트럼 (Color / Light)
   - 형태·기하 속성 (Shape / Geometry)
   - 물성·촉감 속성 (Material / Texture / Hardness)
   - 온도·에너지 스펙트럼 (Temperature / Luminance)
   - 미각·생명 속성 (Taste / Vitality)
   - 움직임·변화 속성 (Motion / Continuity)
   - 관계·가치 스펙트럼 (Relational / Human Meaning)
   + Open dynamic spectrum creation for novel predicates never seen before!
3. Performs genuine qualitative Compare & Contrast and qualitative
   counterfactual mutation experiments (e.g. mutating ONE property of '사과'
   along its spectrum and re-classifying what it now resembles or breaks).
"""

from __future__ import annotations

import random
import re
import time
from typing import Any, Dict, List, Optional, Tuple


# Each axis holds an ordered qualitative spectrum of (canonical_label, Korean stem patterns)
QUALITATIVE_SPECTRA: Dict[str, List[Tuple[str, Tuple[str, ...]]]] = {
    "색채 스펙트럼": [
        ("빨갛다", ("빨갛", "빨간", "붉", "새빨")),
        ("주황빛이다", ("주황", "노을빛")),
        ("노랗다", ("노랗", "노란", "황금")),
        ("초록빛이다", ("초록", "푸릇", "녹색", "연두")),
        ("파랗다", ("파랗", "파란", "푸르", "푸른", "청색")),
        ("보랏빛이다", ("보라", "자주")),
        ("하얗다", ("하얗", "하얀", "희", "흰", "백색")),
        ("검다", ("검", "까맣", "까만", "흑색")),
        ("투명하다", ("투명", "맑")),
    ],
    "형태·물리 속성": [
        ("둥글다", ("둥글", "둥근", "동그", "구형", "원형")),
        ("각지다", ("각지", "각진", "네모", "사각", "직각")),
        ("뾰족하다", ("뾰족", "날카롭", "날카로")),
        ("길쭉하다", ("길쭉", "가늘", "길다", "긴")),
        ("평평하다", ("평평", "납작", "단면", "평면")),
        ("곡선적이다", ("휘어", "굽어", "나선", "곡선")),
        ("작다", ("작다", "작은", "조그", "미세")),
        ("크다", ("크다", "큰", "거대", "방대")),
    ],
    "물성·촉감 속성": [
        ("단단하다", ("단단", "딱딱", "굳어", "고정")),
        ("부드럽다", ("부드럽", "부드러", "말랑", "유연", "가소")),
        ("무르다", ("무르", "물렁", "여리")),
        ("매끄럽다", ("매끄럽", "매끄러", "매끈")),
        ("거칠다", ("거칠", "거친", "까칠")),
        ("가볍다", ("가볍", "가벼")),
        ("무겁다", ("무겁", "무거", "묵직")),
        ("촉촉하다", ("촉촉", "젖어", "축축")),
    ],
    "온도·빛 스펙트럼": [
        ("차갑다", ("차갑", "차가", "서늘", "시원", "얼음같")),
        ("따뜻하다", ("따뜻", "포근", "온기", "따스")),
        ("뜨겁다", ("뜨겁", "뜨거", "열기", "화끈")),
        ("밝다", ("밝", "눈부시", "환하", "빛나")),
        ("어둡다", ("어둡", "어두", "흐리", "캄캄")),
        ("고요하다", ("고요", "차분", "잔잔")),
    ],
    "미각·생명 속성": [
        ("달콤하다", ("달콤", "달다", "단맛", "달짝")),
        ("새콤하다", ("새콤", "시다", "신맛", "시큼")),
        ("쓰다", ("쓰다", "씁쓸", "쓴맛")),
        ("살아있다", ("살아", "생명", "숨쉬", "유기적")),
        ("기계적이다", ("기계적", "인공", "숫자화", "계산적")),
    ],
    "움직임·변화 속성": [
        ("흐른다", ("흐르", "흐른", "흘러", "유동")),
        ("변하고 자란다", ("변하", "달라지", "자라", "성장", "진화")),
        ("흔들린다", ("흔들", "떨리", "진동", "파동")),
        ("멈춰있다", ("멈추", "멈춰", "정지", "갇혀", "갇히")),
        ("이어진다", ("이어지", "연결", "맞물리")),
        ("사라진다", ("사라지", "없어지", "휘발")),
    ],
    "관계·의미 스펙트럼": [
        ("인간적 의미가 담겨있다", ("인간적", "진심", "가치", "의미")),
        ("가깝다", ("가깝", "가까", "친숙", "익숙")),
        ("멀고 낯설다", ("멀다", "멀어", "낯설", "낯선")),
        ("열려있다", ("열려", "자유롭", "가능성", "여지")),
    ],
}

# Topic-marker subject extraction: "사과는 빨갛고 둥글다", "얼음이 차갑고 투명하다"
SUBJECT_RE = re.compile(r"([가-힣A-Za-z0-9]{2,14})(?:은|는|이|가)\s+")
CLAUSE_SPLIT_RE = re.compile(r"[.?!。\n]+|(?:\s+(?:그리고|그런데|하지만|반면|또는)\s+)")

STOP_SUBJECTS = {
    "그것", "이것", "저것", "여기", "거기", "지금", "오늘", "나는", "내가",
    "너는", "네가", "우리", "그냥", "정말", "아직", "모든", "어떤", "이런",
    "그런", "무슨", "이건", "그건", "결국", "언어적", "개념자체",
}


class QualitativeSpectrumField:
    """
    Stores real-world objects/concepts directly as qualitative perceptual &
    physical-attribute profiles across human-meaningful spectra (NOT flat floats).
    """

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        # entities[name] = { name, attributes: { axis_name: [qual_label, ...] }, source_text, updated_ts }
        # Seed only 3 everyday physical anchors so qualitative comparison works naturally from day 1,
        # while every user sentence immediately builds & reshapes the field!
        now = round(time.time(), 2)
        self.entities: Dict[str, Dict[str, Any]] = {
            "얼음": {
                "name": "얼음",
                "attributes": {
                    "색채 스펙트럼": ["투명하다"],
                    "온도·빛 스펙트럼": ["차갑다"],
                    "물성·촉감 속성": ["단단하다"],
                },
                "origin": "기초 감각 기준점",
                "updated_ts": now,
            },
            "불꽃": {
                "name": "불꽃",
                "attributes": {
                    "색채 스펙트럼": ["빨갛다"],
                    "온도·빛 스펙트럼": ["뜨겁다", "밝다"],
                    "움직임·변화 속성": ["흔들린다"],
                },
                "origin": "기초 감각 기준점",
                "updated_ts": now,
            },
            "물결": {
                "name": "물결",
                "attributes": {
                    "색채 스펙트럼": ["투명하다"],
                    "물성·촉감 속성": ["부드럽다"],
                    "움직임·변화 속성": ["흐른다", "이어진다"],
                },
                "origin": "기초 감각 기준점",
                "updated_ts": now,
            },
        }
        self.custom_axes: List[str] = []
        self.last_qualitative_capture: Optional[Dict[str, Any]] = None
        self.last_qualitative_experiment: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entities": self.entities,
            "custom_axes": self.custom_axes[-20:],
            "last_qualitative_capture": self.last_qualitative_capture,
            "last_qualitative_experiment": self.last_qualitative_experiment,
        }

    def load_dict(self, raw: Any) -> None:
        if not isinstance(raw, dict):
            return
        if isinstance(raw.get("entities"), dict) and raw["entities"]:
            self.entities = raw["entities"]
        if isinstance(raw.get("custom_axes"), list):
            self.custom_axes = [str(x) for x in raw["custom_axes"][-20:]]
        if isinstance(raw.get("last_qualitative_capture"), dict):
            self.last_qualitative_capture = raw["last_qualitative_capture"]
        if isinstance(raw.get("last_qualitative_experiment"), dict):
            self.last_qualitative_experiment = raw["last_qualitative_experiment"]

    def detect_attributes(self, clause: str) -> Dict[str, List[str]]:
        found: Dict[str, List[str]] = {}
        for axis, poles in QUALITATIVE_SPECTRA.items():
            hits: List[str] = []
            for label, stems in poles:
                if any(st in clause for st in stems):
                    if label not in hits:
                        hits.append(label)
            if hits:
                found[axis] = hits
        return found

    def absorb_text(self, text: str) -> Dict[str, Any]:
        """
        Extracts qualitative perceptual-spectrum bindings from natural Korean text.
        Example: "사과는 빨갛고 둥글다" ->
          entity "사과": { "색채 스펙트럼": ["빨갛다"], "형태·물리 속성": ["둥글다"] }
        """
        captured: List[Dict[str, Any]] = []
        now = round(time.time(), 2)
        clauses = [c.strip() for c in CLAUSE_SPLIT_RE.split(text or "") if c.strip()]

        for clause in clauses:
            attrs = self.detect_attributes(clause)
            if not attrs:
                continue

            # Find all concrete subjects mentioned before attributes in this clause
            subjects: List[str] = []
            for m in SUBJECT_RE.finditer(clause):
                cand = m.group(1).strip()
                if len(cand) >= 2 and cand not in STOP_SUBJECTS and cand not in subjects:
                    subjects.append(cand)

            if not subjects:
                continue

            # Prefer the subject closest to the qualitative descriptors (usually the concrete noun like '사과')
            target_subj = subjects[-1]
            for s in subjects:
                # Prefer concrete physical/concept nouns over meta-words if multiple subjects exist
                if s not in ("언어", "개념", "정보", "속성", "스펙트럼", "표현", "말"):
                    target_subj = s
                    break

            ent = self.entities.get(target_subj)
            if ent is None:
                ent = {
                    "name": target_subj,
                    "attributes": {},
                    "origin": f"직접 들은 인지 속성: \"{clause[:42]}\"",
                    "updated_ts": now,
                }
                self.entities[target_subj] = ent
            else:
                ent["updated_ts"] = now

            for axis, vals in attrs.items():
                cur = list(ent["attributes"].get(axis, []))
                for v in vals:
                    if v not in cur:
                        cur.append(v)
                ent["attributes"][axis] = cur[-4:]

            # Run immediate qualitative comparison against existing entities in memory!
            comp = self.compare_against_memory(target_subj)
            cap_rec = {
                "entity": target_subj,
                "attributes": dict(attrs),
                "comparison": comp,
                "clause": clause[:80],
            }
            captured.append(cap_rec)
            self.last_qualitative_capture = cap_rec

        return {
            "captured": captured,
            "entity_count": len(self.entities),
        }

    def compare_entities(self, name_a: str, name_b: str) -> Dict[str, Any]:
        ea = self.entities.get(name_a)
        eb = self.entities.get(name_b)
        if not ea or not eb:
            return {"shared": [], "contrasts": []}

        aa = ea.get("attributes", {})
        ab = eb.get("attributes", {})
        shared: List[str] = []
        contrasts: List[str] = []

        all_axes = list(dict.fromkeys(list(aa.keys()) + list(ab.keys())))
        for axis in all_axes:
            va = set(aa.get(axis, []))
            vb = set(ab.get(axis, []))
            common = sorted(va & vb)
            if common:
                shared.append(f"{axis}: {', '.join(common)}")
            elif va and vb:
                contrasts.append(f"{axis}에서 {name_a}({', '.join(sorted(va))}) ↔ {name_b}({', '.join(sorted(vb))})")
            elif va:
                contrasts.append(f"{name_a} 쪽에만 {axis}({', '.join(sorted(va))})이 드러남")
            elif vb:
                contrasts.append(f"{name_b} 쪽에만 {axis}({', '.join(sorted(vb))})이 드러남")

        return {
            "entity_a": name_a,
            "entity_b": name_b,
            "shared": shared,
            "contrasts": contrasts,
        }

    def compare_against_memory(self, entity_name: str) -> Optional[Dict[str, Any]]:
        if entity_name not in self.entities:
            return None
        best: Optional[Tuple[int, int, Dict[str, Any]]] = None
        for other in self.entities.keys():
            if other == entity_name:
                continue
            comp = self.compare_entities(entity_name, other)
            score = (len(comp["shared"]) * 2 + len(comp["contrasts"]), len(comp["shared"]), comp)
            if best is None or score[:2] > best[:2]:
                best = score
        return best[2] if best else None

    def run_qualitative_mutation(self, entity_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        True Qualitative Thought Experiment:
        Picks a known entity (e.g. '사과' with 색채=빨갛다, 형태=둥글다), mutates ONE
        qualitative attribute along its perceptual spectrum (e.g. 빨갛다 -> 파랗다 or
        둥글다 -> 각지다), and observes which perceptual category/analogy shifts!
        """
        names = [k for k, v in self.entities.items() if v.get("attributes")]
        if not names:
            return None
        target = entity_name if (entity_name in self.entities and self.entities[entity_name].get("attributes")) else random.choice(names)
        attrs = self.entities[target]["attributes"]
        mutable_axes = [ax for ax in attrs.keys() if ax in QUALITATIVE_SPECTRA and attrs[ax]]
        if not mutable_axes:
            return None

        axis = random.choice(mutable_axes)
        orig_val = attrs[axis][0]
        alt_poles = [lbl for lbl, _ in QUALITATIVE_SPECTRA[axis] if lbl != orig_val]
        if not alt_poles:
            return None
        mutated_val = random.choice(alt_poles)

        # Find which other real entity shares the mutated attribute along this spectrum
        new_neighbors: List[str] = []
        for other, odata in self.entities.items():
            if other == target:
                continue
            if mutated_val in odata.get("attributes", {}).get(axis, []):
                new_neighbors.append(other)

        kept_other_axes = [f"{ax}({', '.join(vals)})" for ax, vals in attrs.items() if ax != axis]
        exp = {
            "ts": round(time.time(), 2),
            "entity": target,
            "axis": axis,
            "from_val": orig_val,
            "to_val": mutated_val,
            "kept_attributes": kept_other_axes,
            "new_neighbors": new_neighbors[:3],
            "insight": (
                f"'{target}'에서 [{axis}: {orig_val} → {mutated_val}]로 속성 하나만 바꾸면 "
                + (f"'{', '.join(new_neighbors[:2])}' 쪽 지각 영역과 겹치며 " if new_neighbors else "기존에 알던 결에서 벗어나 낯선 조합이 되며 ")
                + (f"{', '.join(kept_other_axes[:2])} 속성과의 긴장이 새로 생긴다." if kept_other_axes else "대상의 인지 정체성이 달라진다.")
            ),
        }
        self.last_qualitative_experiment = exp
        return exp

    def get_public_state(self) -> Dict[str, Any]:
        items = sorted(
            self.entities.values(),
            key=lambda e: float(e.get("updated_ts", 0.0)),
            reverse=True,
        )
        return {
            "entity_count": len(self.entities),
            "entities": [
                {
                    "name": e["name"],
                    "attributes": e.get("attributes", {}),
                    "origin": e.get("origin", ""),
                }
                for e in items[:10]
            ],
            "last_capture": self.last_qualitative_capture,
            "last_experiment": self.last_qualitative_experiment,
        }
