r"""
ELYSIA Story-to-Scale-Rotor Living Digital World Engine
=======================================================

Transforms ANY story / novel text into a living, interactive 3D digital world
where every NPC is an independent 3-layer Scale-Rotor agent (Peripheral Senses
<-> AST Myelinated Habits <-> Personal `CausalField` + `FractalEngramShell`),
grounded in interdisciplinary real-world principles:

  - Optics & Diurnal Physics: Closed `0 -> 2π` solar angle orbit directly
    modulates visibility range and scene lighting (from our Blender Prism).
  - Cognitive Neuroscience (Zero Scalar Emotions): Each NPC holds real
    non-scalar episodic memory traces, relational beams, and friction trails.
  - Information Theory: Low-entropy world manifest + separated channels +
    high-entropy compressed `.zchunk` world history (from our 3-game audit).
  - Scale-Boundary Unfolding: Coarse world simulation runs in milliseconds;
    focused world snapshots unfold into full PBR/rigged 3D via Blender 5.3.0
    using real `.glb` assets (`CesiumMan`, `Fox`, `DamagedHelmet`, `Lantern`).
  - Universal HAVE <-> ACQUIRE Bridge: Explicitly maps what disciplines,
    tools, and capabilities are currently fused vs what external capabilities
    the world needs to acquire next.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple
import zlib

import numpy as np

THIS_DIR = Path(__file__).resolve().parent
L1_ROOT = THIS_DIR.parents[1]
WORKSPACE_ROOT = THIS_DIR.parents[2]
for _p in (str(THIS_DIR), str(L1_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from core.embodiment.compositional_code_cortex import CompositionalCodeCortex  # noqa: E402
from core.embodiment.self_rewriting_architecture import (  # noqa: E402
    _compile_organ_callable,
    validate_organ_source,
)
from core.physics.causal_field import (  # noqa: E402
    CausalField,
    EngramAttractor,
    FractalEngramShell,
    InformationVoxel,
)
from real_tool_organ import discover_real_tool_organs  # noqa: E402
from self_cognitive_expansion_cortex import _load_json, _save_json, _shannon_entropy  # noqa: E402


STORY_WORLD_DIR = WORKSPACE_ROOT / "data" / "open_sandbox" / "story_world"
STORY_STATE_PATH = STORY_WORLD_DIR / "story_world_state.json"
STORY_CHUNKS_DIR = STORY_WORLD_DIR / "chunks"
OSS_3D_DIR = WORKSPACE_ROOT / "data" / "open_source_3d"

DEFAULT_STORY_TEXT = """
[세계관: 빛의 시계 계곡 (Valley of the Light-Clock)]
태양이 완벽한 2π 주기로 기울어지며 낮과 어둠이 교차하는 계곡 중심에는 오래된 등대(Lantern Spire)가 서 있다.
- 아리아(Aria): 계곡의 기록자이자 탐구자. 어둠 속에서도 등대 주변의 빛의 각도와 구조적 법칙을 지키려 하며, 새로운 타인을 경계하기보다 관찰하고 연결하려 한다. (아바타: cesium_man)
- 루멘(Lumen): 경계선을 달리는 야생 여우 정령. 고정된 울타리를 싫어하고 늘 미지의 외곽 지형을 정찰하며, 위험이나 낯선 움직임이 감지되면 빠르게 거리를 벌린다. (아바타: fox)
- 오르(Or): 잊힌 시대의 철투구 수호자. 등대와 옛 유적의 질서를 지키려 하며, 경계 없이 접근하는 존재와는 마찰을 일으키지만 검증된 약속에는 강한 유대를 형성한다. (아바타: helmet)
- 소라(Sora): 등불의 맥박을 조율하는 장인. 낮에는 외곽 자원을 모아 밤이 오기 전에 등대 중심으로 돌아와 공동의 빛을 유지하려 한다. (아바타: lantern)
""".strip()


# ---------------------------------------------------------------------------
# 1. Story / Novel -> World Causal Graph Parser (Zero Hardcoded Scripts!)
# ---------------------------------------------------------------------------

_AVATAR_POOL = ("cesium_man", "fox", "helmet", "lantern")
_AVATAR_FILES = {
    "cesium_man": "CesiumMan.glb",
    "fox": "Fox.glb",
    "helmet": "DamagedHelmet.glb",
    "lantern": "Lantern.glb",
}


def parse_story_into_world_blueprint(story_text: str) -> Dict[str, Any]:
    """
    Parses ANY user-provided story or novel excerpt into:
      - World title & environmental conditions
      - Autonomous NPC agents with distinct teleological axes & initial 3D coordinates
      - Environmental landmarks
      - Initial narrative relational beams
    """
    text = (story_text or "").strip() or DEFAULT_STORY_TEXT
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    title = "Story Scale-Rotor World"
    for ln in lines:
        if ln.startswith("[") and "]" in ln:
            title = ln.strip("[]").strip()
            break

    # Extract character definitions from bullet/colon lines OR fallback noun extraction
    npcs: List[Dict[str, Any]] = []
    for ln in lines:
        m = re.match(r"^[-*•]?\s*([가-힣A-Za-z0-9_]+)(?:\(([A-Za-z0-9_ -]+)\))?\s*[:：]\s*(.+)$", ln)
        if not m:
            continue
        name, eng_alias, desc = m.group(1), m.group(2) or "", m.group(3)
        if name in ("세계관", "배경", "장소", "World", "Setting"):
            title = desc[:60]
            continue

        # Infer teleological orientation vector [Red=Exploration/Flux, Blue=Order/Protection, Yellow=Boundary/Autonomy]
        # strictly from story description semantics (NOT scalar emotions — value orientation axes!)
        d_low = desc.lower()
        flux_w = 0.35 + 0.45 * int(any(k in d_low for k in ("탐구", "개척", "모아", "조율", "연결", "흐름", "창조", "explore", "create", "gather")))
        order_w = 0.35 + 0.45 * int(any(k in d_low for k in ("지키", "질서", "기록", "수호", "유지", "약속", "guard", "order", "keep", "law")))
        bound_w = 0.35 + 0.45 * int(any(k in d_low for k in ("경계", "외곽", "야생", "자유", "마찰", "정찰", "울타리", "boundary", "wild", "scout")))
        vec = np.array([flux_w, order_w, bound_w], dtype=np.float32)
        vec /= max(1e-9, float(np.linalg.norm(vec)))

        # Detect preferred 3D avatar if mentioned, else assign round-robin from real .glb pool
        av = _AVATAR_POOL[len(npcs) % len(_AVATAR_POOL)]
        for k in _AVATAR_POOL:
            if k in d_low:
                av = k
                break

        idx = len(npcs)
        ang = 2.0 * math.pi * (idx / 4.0)
        radius = 3.2 if bound_w > order_w else 1.8
        npcs.append(
            {
                "id": f"npc_{idx + 1}_{re.sub(r'[^a-zA-Z0-9가-힣]', '', name)}",
                "name": f"{name}({eng_alias})" if eng_alias else name,
                "story_role": desc[:160],
                "avatar_glb": av,
                "value_axis": [round(float(x), 4) for x in vec.tolist()],
                "position": [round(radius * math.cos(ang), 3), round(radius * math.sin(ang), 3), 0.0],
                "velocity": [0.0, 0.0, 0.0],
                "facing_rad": round(ang + math.pi, 3),
                "lived_traces": [],
                "myelinated_habit_ast": None,
                "relational_memory": {},
            }
        )

    # If free-form story prose had no bullet list, extract recurring character names automatically
    if len(npcs) < 2:
        tokens = re.findall(r"[가-힣]{2,4}(?=[은는이가의를])|\b[A-Z][a-z]{2,10}\b", text)
        stop = {"세계", "이야기", "시간", "사람", "등대", "계곡", "태양", "어둠", "마음", "기억"}
        uniq = [t for t in dict.fromkeys(tokens) if t not in stop][:4]
        while len(uniq) < 3:
            uniq.append(f"주체{len(uniq) + 1}")
        for idx, nm in enumerate(uniq):
            ang = 2.0 * math.pi * (idx / float(len(uniq)))
            bias = [[0.8, 0.4, 0.4], [0.4, 0.8, 0.4], [0.4, 0.4, 0.8], [0.6, 0.6, 0.5]][idx % 4]
            vec = np.array(bias, dtype=np.float32)
            vec /= float(np.linalg.norm(vec))
            npcs.append(
                {
                    "id": f"npc_{idx + 1}_{nm}",
                    "name": nm,
                    "story_role": f"Extracted from story narrative ({text[:80]}...)",
                    "avatar_glb": _AVATAR_POOL[idx % len(_AVATAR_POOL)],
                    "value_axis": [round(float(x), 4) for x in vec.tolist()],
                    "position": [round(2.5 * math.cos(ang), 3), round(2.5 * math.sin(ang), 3), 0.0],
                    "velocity": [0.0, 0.0, 0.0],
                    "facing_rad": round(ang + math.pi, 3),
                    "lived_traces": [],
                    "myelinated_habit_ast": None,
                    "relational_memory": {},
                }
            )

    landmarks = [
        {"id": "lm_lantern_core", "name": "등대 중심(Light Core)", "position": [0.0, 0.0, 0.0], "role": "diurnal_energy_anchor"},
        {"id": "lm_north_ruin", "name": "북쪽 유적(Order Ruin)", "position": [0.0, 4.2, 0.0], "role": "memory_archive"},
        {"id": "lm_east_frontier", "name": "동쪽 경계(Wild Frontier)", "position": [4.5, -1.2, 0.0], "role": "novelty_resource"},
        {"id": "lm_west_grove", "name": "서쪽 협곡(Echo Grove)", "position": [-4.2, -1.5, 0.0], "role": "acoustic_shelter"},
    ]

    return {
        "world_title": title,
        "source_story": text,
        "landmarks": landmarks,
        "npcs": npcs,
    }


# ---------------------------------------------------------------------------
# 2. Living 3-Layer Scale-Rotor Digital World Simulation
# ---------------------------------------------------------------------------

class StoryScaleRotorDigitalWorld:
    """
    Runs an autonomous 3D living society where each NPC has its own 3-layer
    `CausalField` + `FractalEngramShell` + `CompositionalCodeCortex` AST habits,
    evolving under a closed `0 -> 2π` diurnal solar cycle.
    """

    def __init__(self, blueprint: Dict[str, Any]) -> None:
        self.world_title: str = blueprint["world_title"]
        self.source_story: str = blueprint["source_story"]
        self.landmarks: List[Dict[str, Any]] = blueprint["landmarks"]
        self.npcs: List[Dict[str, Any]] = blueprint["npcs"]
        self.tick: int = 0
        self.solar_phase_rad: float = 0.0  # Closed 0 -> 2π diurnal cycle
        self.event_log: List[Dict[str, Any]] = []
        self.user_interventions: List[Dict[str, Any]] = []
        self.temporal_rotor_chain: List[Dict[str, Any]] = []  # Recursive R_1 -> R_2 -> R_3 ... history
        self.macro_epoch_rotor: Dict[str, Any] = {}

        # Each NPC owns an independent Layer 3 CausalField & FractalEngramShell!
        self.npc_fields: Dict[str, CausalField] = {}
        self.npc_shells: Dict[str, FractalEngramShell] = {}
        self.cortex = CompositionalCodeCortex()
        self.cortex.learn_python_structure_from_files(sorted(THIS_DIR.glob("*.py"))[:12])

        for npc in self.npcs:
            f = CausalField(dimensions=3)
            axis = np.array(npc["value_axis"], dtype=np.float32)
            f.set_intentional_focus(axis)
            f.add_voxel(
                InformationVoxel(
                    id="self_core",
                    content=npc["story_role"],
                    tensor=axis,
                    mass=1.5,
                    position=np.array(npc["position"], dtype=np.float32),
                    chromatic_vector=axis / max(1e-9, float(np.sum(axis))),
                )
            )
            # Register teleological engram from the NPC's story value axis
            # Order-oriented gravitates toward Light Core/Ruin; Boundary-oriented explores Wild Frontier
            if axis[2] >= axis[1] and axis[2] >= axis[0]:
                home_target = np.array([4.0, -1.0, 0.0], dtype=np.float32)
                intent_txt = "Scout outer frontier and preserve autonomous space"
            elif axis[1] >= axis[0]:
                home_target = np.array([0.0, 2.2, 0.0], dtype=np.float32)
                intent_txt = "Preserve structural order between Light Core and Ruin"
            else:
                home_target = np.array([0.0, 0.0, 0.0], dtype=np.float32)
                intent_txt = "Observe, connect, and harmonize light and encounters"

            shell = FractalEngramShell(
                shell_id=f"shell_{npc['id']}",
                macro=EngramAttractor(
                    id=f"macro_{npc['id']}",
                    name=f"{npc['name']} Teleology",
                    position=home_target,
                    intensity=4.5,
                    sigma=3.5,
                    tier="macro",
                    symbolic_intent=intent_txt,
                ),
            )
            f.register_engram(shell.tiers["macro"])
            self.npc_fields[npc["id"]] = f
            self.npc_shells[npc["id"]] = shell

    def _solar_state(self) -> Dict[str, Any]:
        # Closed 2π diurnal cycle: elevation = sin(theta), visibility scales physically with sunlight!
        elev = math.sin(self.solar_phase_rad)
        daylight = 0.5 * (1.0 + elev)  # [0, 1] continuous
        vis_radius = round(2.2 + 3.8 * daylight, 2)
        phase_name = "dawn" if (0.0 <= self.solar_phase_rad < 1.0) else (
            "daylight" if (1.0 <= self.solar_phase_rad < 2.6) else (
                "dusk" if (2.6 <= self.solar_phase_rad < 3.6) else "night"
            )
        )
        return {
            "solar_phase_rad": round(self.solar_phase_rad, 4),
            "daylight_intensity": round(daylight, 3),
            "visibility_radius": vis_radius,
            "diurnal_phase": phase_name,
        }

    def step_world(self, dt_phase: float = math.pi / 12.0) -> Dict[str, Any]:
        """Advances 1 living tick of physics, diurnal optics, multi-NPC perception, and emergent encounters."""
        self.tick += 1
        self.solar_phase_rad = (self.solar_phase_rad + dt_phase) % (2.0 * math.pi)
        sun = self._solar_state()
        vis_r = sun["visibility_radius"]

        tick_events: List[Dict[str, Any]] = []

        for npc in self.npcs:
            nid = npc["id"]
            f = self.npc_fields[nid]
            pos = np.array(npc["position"], dtype=np.float32)
            vel = np.array(npc["velocity"], dtype=np.float32)
            axis = np.array(npc["value_axis"], dtype=np.float32)

            # 1. Top-Down Teleological Gradient from personal CausalField Engram
            grad_engram = f.calculate_engram_gradient(pos)
            # Nighttime optical pull toward Light Core for non-wild NPCs
            light_pull = -pos * (0.28 * (1.0 - sun["daylight_intensity"])) * (0.4 + axis[1])

            # 2. Layer 1 Peripheral Perception of OTHER NPCs within optical visibility radius!
            social_force = np.zeros(3, dtype=np.float32)
            perceived_others: List[str] = []

            for other in self.npcs:
                if other["id"] == nid:
                    continue
                opos = np.array(other["position"], dtype=np.float32)
                diff = opos - pos
                dist = float(np.linalg.norm(diff))
                if dist <= vis_r and dist > 1e-4:
                    perceived_others.append(other["name"])
                    o_axis = np.array(other["value_axis"], dtype=np.float32)
                    # Real physical value-axis alignment (cosine similarity)
                    align = float(np.dot(axis, o_axis) / (np.linalg.norm(axis) * np.linalg.norm(o_axis) + 1e-9))

                    # Update personal CausalField with observed encounter
                    obs_vec = np.array([align, sun["daylight_intensity"], min(1.0, dist / 6.0)], dtype=np.float32)
                    f.observe_external_stimulus(obs_vec, target_voxel_id="self_core")

                    # Relational mechanics: resonant actors draw closer to exchange; divergent boundary actors keep margin
                    if dist < 1.35:
                        # Close personal boundary -> physical spacing + direct social interaction!
                        social_force -= (diff / dist) * 0.45
                        rel = npc["relational_memory"].setdefault(
                            other["id"], {"partner": other["name"], "encounters": 0, "phase_alignment": round(align, 3), "outcomes": []}
                        )
                        rel["encounters"] += 1
                        rel["phase_alignment"] = round(align, 3)

                        if align >= 0.85:
                            interaction_kind = "resonant_exchange"
                            utterance = f"{npc['name']} ↔ {other['name']}: {sun['diurnal_phase']} 빛 아래 공통 축(정렬 {align:.2f})을 확인하고 궤도를 맞춥니다."
                        else:
                            interaction_kind = "dialectical_boundary_friction"
                            utterance = f"{npc['name']} ↔ {other['name']}: 서로 다른 가치 축(정렬 {align:.2f})이 근접 마찰을 일으켜 각자의 경계를 재조정합니다."
                            self.npc_shells[nid].report_resistance("macro", 0.5)

                        rel["outcomes"].append(interaction_kind)
                        rel["outcomes"] = rel["outcomes"][-6:]
                        if nid < other["id"]:  # log each pair encounter once per tick
                            ev = {
                                "tick": self.tick,
                                "diurnal_phase": sun["diurnal_phase"],
                                "kind": interaction_kind,
                                "actors": [npc["name"], other["name"]],
                                "distance": round(dist, 2),
                                "value_alignment": round(align, 3),
                                "grounded_trace": utterance,
                            }
                            tick_events.append(ev)
                            self.event_log.append(ev)
                    elif align >= 0.82:
                        social_force += (diff / dist) * 0.22
                    else:
                        # Divergent value axis -> tangential orbit rather than flat repulsion
                        tangent = np.array([-diff[1], diff[0], 0.0], dtype=np.float32) / dist
                        social_force += tangent * 0.25

            # Continuous momentum update (Mobility + damping, bounded to valley radius 5.5)
            accel = grad_engram * 0.16 + light_pull + social_force
            # Subtle diurnal exploration wave so NPCs never freeze in dead equilibrium
            wave_ang = self.solar_phase_rad + hash(nid) % 7
            accel += np.array([0.14 * math.cos(wave_ang), 0.14 * math.sin(wave_ang), 0.0], dtype=np.float32)

            vel = 0.72 * vel + 0.28 * accel
            speed = float(np.linalg.norm(vel))
            if speed > 0.65:
                vel = vel * (0.65 / speed)
            pos = pos + vel
            pos[2] = 0.0
            r_now = float(np.linalg.norm(pos))
            if r_now > 5.4:
                pos = pos * (5.4 / r_now)

            npc["position"] = [round(float(pos[0]), 3), round(float(pos[1]), 3), 0.0]
            npc["velocity"] = [round(float(vel[0]), 3), round(float(vel[1]), 3), 0.0]
            if speed > 0.02:
                npc["facing_rad"] = round(math.atan2(float(vel[1]), float(vel[0])), 3)

            # Record non-scalar lived trace for Layer 2 AST habit myelination!
            dist_core = float(np.linalg.norm(pos))
            npc["lived_traces"].append(
                {
                    "tick": self.tick,
                    "daylight": sun["daylight_intensity"],
                    "perceived_count": len(perceived_others),
                    "dist_to_core": round(dist_core, 2),
                    "speed": round(speed, 3),
                    "behavior_mode": (
                        "close_social_interaction" if (len(perceived_others) > 0 and speed < 0.28)
                        else ("night_light_seeking" if (sun["daylight_intensity"] < 0.35 and dist_core < 2.8)
                        else "autonomous_frontier_roaming")
                    ),
                }
            )
            npc["lived_traces"] = npc["lived_traces"][-24:]
            f.step(dt=0.1)

        self.event_log = self.event_log[-40:]
        return {"tick": self.tick, "solar": sun, "events_this_tick": tick_events}

    def myelinate_npc_habits_and_reclassify_world(self) -> Dict[str, Any]:
        """
        Re-encodes lived NPC trajectories back into Layer 2 AST habits (per NPC!)
        and compresses world history into a high-entropy `.zchunk` block.
        """
        myelinated_count = 0
        for npc in self.npcs:
            traces = npc.get("lived_traces") or []
            if len(traces) < 4:
                continue
            examples = [
                (
                    {
                        "daylight": tr["daylight"],
                        "perceived_count": tr["perceived_count"],
                        "dist_to_core": tr["dist_to_core"],
                    },
                    {"habit_mode": tr["behavior_mode"]},
                )
                for tr in traces
            ]
            prog = self.cortex.synthesize_decision_tree_ast(
                examples,
                purpose=f"npc_habit_{npc['id']}",
                min_accuracy=0.80,
                max_depth=3,
            )
            if prog is not None:
                myelinated_count += 1
                npc["myelinated_habit_ast"] = {
                    "program_id": prog.program_id,
                    "examples_passed": f"{prog.examples_passed}/{prog.examples_total}",
                    "source_code": prog.source_code,
                }

        # Scale-separated compressed episodic world chunk (AAA game memory law!)
        STORY_CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
        raw = json.dumps({"tick": self.tick, "events": self.event_log, "npcs": self.npcs}, ensure_ascii=False).encode("utf-8")
        comp = zlib.compress(raw, level=6)
        chunk_file = STORY_CHUNKS_DIR / f"world_epoch_{self.tick:04d}.zchunk"
        chunk_file.write_bytes(comp)

        return {
            "npcs_with_myelinated_ast_habits": myelinated_count,
            "compressed_world_chunk": {
                "file": chunk_file.name,
                "raw_bytes": len(raw),
                "compressed_bytes": len(comp),
                "ratio": round(len(comp) / max(1, len(raw)), 3),
                "entropy_compressed": _shannon_entropy(comp[:4096]),
            },
        }

    def render_live_3d_blender_snapshot(self) -> Dict[str, Any]:
        """
        Scale-Boundary Unfolding: Unfolds the current live NPC coordinates and
        diurnal solar angle into a real Blender 5.3.0 PBR/rigged 3D snapshot!
        """
        blender_bin = discover_real_tool_organs().get("organs", {}).get("blender_3d_cad", {}).get("binary")
        if not blender_bin:
            return {"status": "skipped", "reason": "blender_missing"}

        STORY_WORLD_DIR.mkdir(parents=True, exist_ok=True)
        out_png = STORY_WORLD_DIR / "story_world_embodied_3d.png"
        out_blend = STORY_WORLD_DIR / "story_world_embodied_3d.blend"
        scene_json = STORY_WORLD_DIR / "story_scene_input.json"
        harness_py = STORY_WORLD_DIR / "story_blender_harness.py"

        sun = self._solar_state()
        scene_payload = {
            "solar_phase_rad": sun["solar_phase_rad"],
            "daylight_intensity": sun["daylight_intensity"],
            "npcs": [
                {
                    "name": n["name"],
                    "position": n["position"],
                    "facing_rad": n["facing_rad"],
                    "glb_path": str(OSS_3D_DIR / _AVATAR_FILES.get(n["avatar_glb"], "CesiumMan.glb")),
                    "avatar_key": n["avatar_glb"],
                }
                for n in self.npcs
            ],
        }
        scene_json.write_text(json.dumps(scene_payload, ensure_ascii=False, indent=2), encoding="utf-8")

        harness_py.write_text(
            "import bpy, json, math, os\n"
            "from mathutils import Vector\n"
            "def look_at(obj, target):\n"
            "    d = Vector(target) - obj.location\n"
            "    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()\n"
            f"data = json.loads(open(r'{scene_json}', encoding='utf-8').read())\n"
            "bpy.ops.wm.read_factory_settings(use_empty=True)\n"
            "s = bpy.context.scene\n"
            "s.render.engine = 'BLENDER_EEVEE'\n"
            "s.render.resolution_x = 640\n"
            "s.render.resolution_y = 360\n"
            "day = float(data['daylight_intensity'])\n"
            "w = bpy.data.worlds.new('StoryWorld'); s.world = w; w.use_nodes = False\n"
            "w.color = (0.04 + 0.14 * day, 0.06 + 0.18 * day, 0.12 + 0.24 * day)\n"
            "# Valley terrain floor\n"
            "bpy.ops.mesh.primitive_plane_add(size=24.0, location=(0.0, 0.0, 0.0))\n"
            "fl = bpy.context.active_object\n"
            "fm = bpy.data.materials.new('ValleyGround'); fm.use_nodes = True\n"
            "bsdf = fm.node_tree.nodes.get('Principled BSDF')\n"
            "if bsdf:\n"
            "    bsdf.inputs['Base Color'].default_value = (0.12, 0.16, 0.18, 1.0)\n"
            "    bsdf.inputs['Roughness'].default_value = 0.65\n"
            "fl.data.materials.append(fm)\n"
            "# Central Light-Clock Spire\n"
            "bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.35, depth=2.6, location=(0.0, 0.0, 1.3))\n"
            "beacon_d = bpy.data.lights.new('CoreBeacon', type='POINT'); beacon_d.energy = 600.0; beacon_d.color = (1.0, 0.85, 0.55)\n"
            "beacon = bpy.data.objects.new('CoreBeacon', beacon_d); s.collection.objects.link(beacon); beacon.location = (0.0, 0.0, 2.9)\n"
            "# Diurnal Sun Light positioned by exact 2pi solar phase\n"
            "theta = float(data['solar_phase_rad'])\n"
            "sun_d = bpy.data.lights.new('SolarLight', type='POINT'); sun_d.energy = 300.0 + 1800.0 * day; sun_d.color = (1.0, 0.94, 0.84)\n"
            "sun_o = bpy.data.objects.new('SolarLight', sun_d); s.collection.objects.link(sun_o)\n"
            "sun_o.location = (7.0 * math.cos(theta), -5.0, 2.5 + 5.5 * day)\n"
            "# Import REAL PBR/rigged .glb avatars at the EXACT simulated NPC coordinates!\n"
            "scale_map = {'cesium_man': 1.0, 'fox': 0.016, 'helmet': 0.72, 'lantern': 0.055}\n"
            "z_map = {'cesium_man': 0.0, 'fox': 0.0, 'helmet': 1.15, 'lantern': 0.0}\n"
            "for npc in data['npcs']:\n"
            "    p = npc['glb_path']\n"
            "    if not os.path.isfile(p): continue\n"
            "    before = set(bpy.data.objects)\n"
            "    bpy.ops.import_scene.gltf(filepath=p)\n"
            "    added = [o for o in bpy.data.objects if o not in before]\n"
            "    sc = scale_map.get(npc['avatar_key'], 1.0)\n"
            "    px, py, _ = npc['position']\n"
            "    pz = z_map.get(npc['avatar_key'], 0.0)\n"
            "    for r in [o for o in added if o.parent is None]:\n"
            "        r.location = (px, py, pz)\n"
            "        r.scale = (sc, sc, sc)\n"
            "        r.rotation_euler = (r.rotation_euler[0], r.rotation_euler[1], float(npc['facing_rad']))\n"
            "cd = bpy.data.cameras.new('WorldCam'); cam = bpy.data.objects.new('WorldCam', cd); s.collection.objects.link(cam); s.camera = cam\n"
            "cam.location = (7.8, -8.2, 5.4)\n"
            "look_at(cam, (0.0, 0.0, 0.9))\n"
            f"bpy.ops.wm.save_as_mainfile(filepath=r'{out_blend}')\n"
            f"s.render.filepath = r'{out_png}'\n"
            "bpy.ops.render.render(write_still=True)\n"
            "print('STORY_3D_DONE:' + str(sum(len(o.data.vertices) for o in bpy.data.objects if o.type == 'MESH')))\n",
            encoding="utf-8",
        )

        t0 = time.perf_counter()
        proc = subprocess.run([blender_bin, "--background", "--python", str(harness_py)], capture_output=True, text=True, timeout=90)
        elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 1)
        try:
            harness_py.unlink(missing_ok=True)
        except OSError:
            pass

        verts = 0
        for ln in proc.stdout.splitlines():
            if ln.startswith("STORY_3D_DONE:"):
                verts = int(ln.split(":")[1].strip())
                break
        return {
            "status": "ok" if (proc.returncode == 0 and out_png.is_file()) else "error",
            "elapsed_ms": elapsed_ms,
            "total_vertices": verts,
            "render_png": str(out_png) if out_png.is_file() else None,
            "blend_file": str(out_blend) if out_blend.is_file() else None,
        }

    def _min_pairwise_npc_distance(self) -> float:
        best = 99.0
        for i in range(len(self.npcs)):
            pa = np.array(self.npcs[i]["position"], dtype=np.float32)
            for j in range(i + 1, len(self.npcs)):
                pb = np.array(self.npcs[j]["position"], dtype=np.float32)
                d = float(np.linalg.norm(pa - pb))
                if d < best:
                    best = d
        return best

    def unfold_one_adaptive_temporal_rotor(self) -> Dict[str, Any]:
        """
        Unfolds ONE complete closed `0 -> 2π` Temporal Scale-Rotor (`R_k`)
        WITHOUT any hardcoded fixed tick count:
          - Calm invariant flow (`min_dist > 2.2m`) -> coarse macro phase leap (`dθ = π/6`)
          - Active proximity / encounter (`min_dist <= 1.6m`) -> fine micro zoom-in (`dθ = π/20`)
        Connects `Past Rotor R_{k-1} ⊗ Present Rotor R_k` by inheriting crystallized
        relational/habit invariants and computing the exact Temporal Overlay-Contrast
        Residual (`Predicted from Past` vs `Actual Lived Present`)!
        """
        rotor_idx = len(self.temporal_rotor_chain) + 1
        rotor_id = f"R_{rotor_idx:04d}"
        past_rotor = self.temporal_rotor_chain[-1] if self.temporal_rotor_chain else None

        # 1. Past -> Present Recursive Inheritance & Prediction
        predicted_positions: Dict[str, List[float]] = {}
        past_relations: set[str] = set()
        if past_rotor is not None:
            inv_past = past_rotor.get("crystallized_invariants") or {}
            past_relations = set(inv_past.get("active_relation_pairs") or [])
            # Predict present centroids linearly from past crystallized centroids + drift
            for npc in self.npcs:
                p_rec = (inv_past.get("npc_centroids") or {}).get(npc["id"])
                if p_rec:
                    predicted_positions[npc["id"]] = p_rec
                else:
                    predicted_positions[npc["id"]] = list(npc["position"])
            # Recursive Causal Coupling: Past Rotor's friction/resonance reshapes Present Engram Shells!
            for npc in self.npcs:
                nid = npc["id"]
                rel_mem = npc.get("relational_memory") or {}
                total_enc = sum(int(r.get("encounters", 0)) for r in rel_mem.values())
                if total_enc > 0 and nid in self.npc_shells:
                    # Subtle recursive phase evolution of macro engram from lived past history
                    engram = self.npc_shells[nid].tiers.get("macro")
                    if engram is not None:
                        rot_ang = 0.22 * rotor_idx
                        px, py = float(engram.position[0]), float(engram.position[1])
                        engram.position[0] = px * math.cos(rot_ang) - py * math.sin(rot_ang)
                        engram.position[1] = px * math.sin(rot_ang) + py * math.cos(rot_ang)
        else:
            for npc in self.npcs:
                predicted_positions[npc["id"]] = list(npc["position"])

        # 2. Adaptive `0 -> 2π` Continuous Phase Unfolding (NO hardcoded 20 ticks!)
        phase_accum = 0.0
        target_phase = 2.0 * math.pi
        adaptive_steps = 0
        micro_zoom_steps = 0
        macro_leap_steps = 0
        rotor_events: List[Dict[str, Any]] = []
        pos_samples: Dict[str, List[np.ndarray]] = {n["id"]: [] for n in self.npcs}

        while phase_accum < target_phase - 1e-6 and adaptive_steps < 48:
            min_d = self._min_pairwise_npc_distance()
            if min_d <= 1.6:
                d_theta = math.pi / 20.0  # Fine Micro Time Zoom-In on active encounter!
                micro_zoom_steps += 1
            elif min_d <= 2.3:
                d_theta = math.pi / 10.0  # Meso Time Scale
            else:
                d_theta = math.pi / 6.0   # Coarse Macro Leap on calm invariant flow!
                macro_leap_steps += 1

            step_dt = min(d_theta, target_phase - phase_accum)
            tick_out = self.step_world(dt_phase=step_dt)
            phase_accum += step_dt
            adaptive_steps += 1
            rotor_events.extend(tick_out.get("events_this_tick") or [])
            for npc in self.npcs:
                pos_samples[npc["id"]].append(np.array(npc["position"], dtype=np.float32))

        # 3. Crystallize Present Span into ONE Unified Temporal Rotor Ring `R_k`
        reclass = self.myelinate_npc_habits_and_reclassify_world()
        npc_centroids: Dict[str, List[float]] = {}
        for nid, pts in pos_samples.items():
            mean_p = np.mean(pts, axis=0) if pts else np.zeros(3, dtype=np.float32)
            npc_centroids[nid] = [round(float(x), 3) for x in mean_p.tolist()]

        curr_relations: set[str] = set()
        for npc in self.npcs:
            for pid in (npc.get("relational_memory") or {}).keys():
                pair_key = " <-> ".join(sorted([npc["id"], pid]))
                curr_relations.add(pair_key)

        # 4. Temporal Overlay-Contrast Residual: Predict(R_{k-1}) vs Actual(R_k)
        pos_residuals: List[float] = []
        for nid, c_pos in npc_centroids.items():
            p_pos = predicted_positions.get(nid, c_pos)
            pos_residuals.append(float(np.linalg.norm(np.array(c_pos) - np.array(p_pos))))
        mean_temporal_residual = round(float(np.mean(pos_residuals)) if pos_residuals else 0.0, 3)
        newly_emerged_relations = sorted(curr_relations - past_relations)
        preserved_relations = sorted(curr_relations & past_relations)
        continuity_ratio = round(1.0 / (1.0 + mean_temporal_residual), 3)

        rotor_ring = {
            "rotor_id": rotor_id,
            "parent_past_rotor": past_rotor["rotor_id"] if past_rotor else "ORIGIN_POINT_0",
            "phase_span_rad": round(phase_accum, 4),
            "adaptive_steps_taken": adaptive_steps,
            "micro_zoom_steps": micro_zoom_steps,
            "macro_leap_steps": macro_leap_steps,
            "events_in_rotor": len(rotor_events),
            "crystallized_invariants": {
                "npc_centroids": npc_centroids,
                "active_relation_pairs": sorted(curr_relations),
                "myelinated_ast_habits": reclass["npcs_with_myelinated_ast_habits"],
            },
            "temporal_overlay_contrast": {
                "mean_spatial_residual_vs_past": mean_temporal_residual,
                "invariant_continuity_0000": continuity_ratio,
                "newly_emerged_relations_1": newly_emerged_relations,
                "preserved_past_relations": preserved_relations,
            },
            "compressed_world_chunk": reclass["compressed_world_chunk"],
        }
        self.temporal_rotor_chain.append(rotor_ring)

        # 5. Fold ALL Rotor Rings [R_1 .. R_k] into Higher-Scale Macro-Epoch Rotor!
        total_steps = sum(r["adaptive_steps_taken"] for r in self.temporal_rotor_chain)
        total_events = sum(r["events_in_rotor"] for r in self.temporal_rotor_chain)
        self.macro_epoch_rotor = {
            "macro_scale_span": f"{self.temporal_rotor_chain[0]['rotor_id']} -> {rotor_id}",
            "generations_folded": len(self.temporal_rotor_chain),
            "total_adaptive_steps": total_steps,
            "total_micro_zoom_steps": sum(r["micro_zoom_steps"] for r in self.temporal_rotor_chain),
            "total_macro_leap_steps": sum(r["macro_leap_steps"] for r in self.temporal_rotor_chain),
            "total_emergent_events": total_events,
            "latest_temporal_residual": mean_temporal_residual,
            "latest_continuity_ratio": continuity_ratio,
        }
        return rotor_ring

    def export_state(self, reclass_meta: Dict[str, Any], render_meta: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "schema": "elysia_story_scale_rotor_digital_world_v2_recursive_time",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "world_title": self.world_title,
            "source_story": self.source_story,
            "tick": self.tick,
            "solar_state": self._solar_state(),
            "landmarks": self.landmarks,
            "npcs": self.npcs,
            "recent_emergent_events": self.event_log[-20:],
            "temporal_rotor_chain": self.temporal_rotor_chain,
            "macro_epoch_rotor": self.macro_epoch_rotor,
            "world_reintegration": reclass_meta,
            "blender_3d_embodiment": render_meta,
            "have_vs_acquire_interdisciplinary_bridge": {
                "fused_now_HAVE": [
                    "Recursive Adaptive Time Scale-Rotor (Point -> 2π Ring R_1 -> Past⊗Present R_2 -> Macro-History Folding)",
                    "Temporal Overlay-Contrast Residual (Predict(R_past) vs Actual(R_present) separating 0000 continuity vs 1 emergent history)",
                    "Optics & 2π Diurnal Solar Visibility Physics",
                    "Per-NPC 3-Layer CausalField + FractalEngramShell + Template-Free AST Habits (Zero Scalar Emotions)",
                    "On-Demand Scale-Boundary 3D PBR/Rigged Unfolding (Blender 5.3 + Khronos .glb)",
                ],
                "next_expansion_ACQUIRE": [
                    "Grounded Local/API Language Voice per NPC (driving natural Korean speech strictly from each NPC's lived relational traces)",
                    "Procedural Geometry & MaterialX GLSL Shader Synthesis (unfolding micro-surface detail inside active gaze cone beyond 3GB VRAM)",
                    "External Multi-Modal Open Knowledge Intake (physics/biology/history/literature datasets auto-mapped into world laws)",
                    "Real-Time Multi-User WebSocket Sync & Live Microphone Voice Intervention",
                ],
            },
        }


def create_and_run_story_world(story_text: str = DEFAULT_STORY_TEXT, generations: int = 3, render_3d: bool = True) -> Dict[str, Any]:
    bp = parse_story_into_world_blueprint(story_text)
    world = StoryScaleRotorDigitalWorld(bp)
    last_ring: Dict[str, Any] = {}
    for _ in range(max(1, generations)):
        last_ring = world.unfold_one_adaptive_temporal_rotor()
    reclass = {
        "npcs_with_myelinated_ast_habits": (last_ring.get("crystallized_invariants") or {}).get("myelinated_ast_habits", 0),
        "compressed_world_chunk": last_ring.get("compressed_world_chunk", {}),
    }
    render_meta = world.render_live_3d_blender_snapshot() if render_3d else {"status": "deferred"}
    state = world.export_state(reclass, render_meta)
    _save_json(STORY_STATE_PATH, state)
    return state


def advance_existing_story_world_by_one_rotor(render_3d: bool = True) -> Dict[str, Any]:
    """
    Loads the existing living world, preserves ALL past crystallized Rotor Rings
    as `R_1 .. R_k` (Past), and recursively derives `R_{k+1}` (Present) connected to them!
    """
    saved = _load_json(STORY_STATE_PATH, {})
    if not saved or not saved.get("npcs"):
        return create_and_run_story_world(DEFAULT_STORY_TEXT, generations=2, render_3d=render_3d)

    bp = {
        "world_title": saved["world_title"],
        "source_story": saved["source_story"],
        "landmarks": saved["landmarks"],
        "npcs": saved["npcs"],
    }
    world = StoryScaleRotorDigitalWorld(bp)
    world.tick = int(saved.get("tick", 0))
    world.solar_phase_rad = float((saved.get("solar_state") or {}).get("solar_phase_rad", 0.0))
    world.event_log = list(saved.get("recent_emergent_events") or [])
    world.temporal_rotor_chain = list(saved.get("temporal_rotor_chain") or [])

    new_ring = world.unfold_one_adaptive_temporal_rotor()
    reclass = {
        "npcs_with_myelinated_ast_habits": (new_ring.get("crystallized_invariants") or {}).get("myelinated_ast_habits", 0),
        "compressed_world_chunk": new_ring.get("compressed_world_chunk", {}),
    }
    render_meta = world.render_live_3d_blender_snapshot() if render_3d else (saved.get("blender_3d_embodiment") or {"status": "kept"})
    state = world.export_state(reclass, render_meta)
    _save_json(STORY_STATE_PATH, state)
    return state


def main() -> None:
    parser = argparse.ArgumentParser(description="ELYSIA Recursive Temporal Scale-Rotor Digital World Engine")
    parser.add_argument("--story-file", type=str, default="", help="Optional path to custom story text file")
    parser.add_argument("--generations", type=int, default=3, help="Number of recursive 2π temporal rotors (R1->R2->R3)")
    parser.add_argument("--advance", action="store_true", help="Recursively derive the next temporal rotor R_{k+1} from saved Past Rotor R_k")
    parser.add_argument("--no-render", action="store_true", help="Skip Blender 3D render snapshot")
    args = parser.parse_args()

    if args.advance:
        out = advance_existing_story_world_by_one_rotor(render_3d=not args.no_render)
    else:
        story_txt = DEFAULT_STORY_TEXT
        if args.story_file and Path(args.story_file).is_file():
            story_txt = Path(args.story_file).read_text(encoding="utf-8")
        out = create_and_run_story_world(story_txt, generations=args.generations, render_3d=not args.no_render)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
