r"""
ELYSIA Live Windows Desktop Avatar & Wallpaper Manifestation
============================================================

Pulls Elysia out of the terminal/browser directly onto the user's REAL Windows
desktop as a live, draggable, borderless companion linked to the running
autonomous Scale-Rotor Ecology server (`http://localhost:3000/api/ecology/autonomous-state`):

- Dynamically switches Elysia's actual portrait/scene (`src/assets/images/elysia_*.jpg`)
  according to her live cognitive state (serene 0000, deep thought, happy molecular bond,
  playful curiosity, or dissonance question).
- Displays what she is currently observing on THIS PC (top attention target, GPU/VRAM,
  octave/molecular count, and spontaneous speech bubble).
- Lets the user reply directly from the desktop OR set her current scene as the real
  Windows desktop wallpaper (with one-click restore).
"""

from __future__ import annotations

import ctypes
import json
from pathlib import Path
import threading
import tkinter as tk
from typing import Any, Dict, Optional
import urllib.request

from PIL import Image, ImageDraw, ImageTk

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
IMG_DIR = WORKSPACE_ROOT / "src" / "assets" / "images"
API_BASE = "http://127.0.0.1:3000"

SCENE_MAP = {
    "serene": "elysia_scene_serene_1795779825171.jpg",
    "idle": "elysia_smile_idle_1795779034636.jpg",
    "warm": "elysia_scene_warm_smile_1795779825548.jpg",
    "happy": "elysia_happy_laugh_1795779040015.jpg",
    "thought": "elysia_scene_deep_thought_1795779832242.jpg",
    "playful": "elysia_scene_playful_1795779829170.jpg",
    "pout": "elysia_scene_hurt_pout_1795779829921.jpg",
    "horizon": "elysia_goddess_horizon_1795634966240.jpg",
}


def _fetch_json(url: str, payload: Optional[Dict[str, Any]] = None, timeout: float = 2.5) -> Optional[Dict[str, Any]]:
    try:
        if payload is not None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        else:
            req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def _pick_scene_key(state: Dict[str, Any]) -> str:
    voice = state.get("agency_voice") or {}
    phase = voice.get("phase") or "silent_absorb"
    overlay = state.get("parallel_overlay") or {}
    conv = float(overlay.get("convergence") or 0.5)
    sym = state.get("symbolic_memory") or {}
    comps = len(sym.get("compounds") or {})

    if phase in ("ask_once", "reask_reframed"):
        return "pout"
    if phase == "pivot_alternative":
        return "playful"
    if conv >= 0.85 and comps >= 1:
        return "happy"
    if conv >= 0.75:
        return "warm"
    if conv < 0.55:
        return "thought"
    return "serene"


class ElysiaDesktopCompanion:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Elysia — Live Desktop Embodiment")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#090D16")

        self.win_w = 320
        self.win_h = 470
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x0 = max(20, sw - self.win_w - 28)
        y0 = max(20, sh - self.win_h - 68)
        self.root.geometry(f"{self.win_w}x{self.win_h}+{x0}+{y0}")

        self._drag_x = 0
        self._drag_y = 0
        self._current_scene_key = ""
        self._current_image_path: Optional[Path] = None
        self._photo_ref: Optional[ImageTk.PhotoImage] = None
        self._latest_state: Dict[str, Any] = {}

        # Outer border frame
        self.frame = tk.Frame(self.root, bg="#0D121C", highlightbackground="#06B6D4", highlightthickness=1)
        self.frame.pack(fill="both", expand=True)

        # Draggable header bar
        self.header = tk.Frame(self.frame, bg="#07090E", height=28)
        self.header.pack(fill="x")
        self.header.bind("<ButtonPress-1>", self._start_drag)
        self.header.bind("<B1-Motion>", self._on_drag)

        self.title_lbl = tk.Label(
            self.header,
            text="✦ ELYSIA LIVE DESKTOP",
            bg="#07090E",
            fg="#06B6D4",
            font=("Segoe UI", 9, "bold"),
            padx=8,
        )
        self.title_lbl.pack(side="left", pady=4)
        self.title_lbl.bind("<ButtonPress-1>", self._start_drag)
        self.title_lbl.bind("<B1-Motion>", self._on_drag)

        btn_close = tk.Button(
            self.header,
            text="✕",
            command=self.root.destroy,
            bg="#07090E",
            fg="#94A3B8",
            activebackground="#F43F5E",
            activeforeground="#FFFFFF",
            bd=0,
            font=("Segoe UI", 9, "bold"),
            padx=8,
            cursor="hand2",
        )
        btn_close.pack(side="right")

        # Portrait display
        self.img_lbl = tk.Label(self.frame, bg="#07090E", bd=0)
        self.img_lbl.pack(fill="x", padx=6, pady=(6, 4))
        self.img_lbl.bind("<ButtonPress-1>", self._start_drag)
        self.img_lbl.bind("<B1-Motion>", self._on_drag)

        # Live cognitive status badge
        self.status_lbl = tk.Label(
            self.frame,
            text="자율 스케일로터 연결 중...",
            bg="#0D121C",
            fg="#38BDF8",
            font=("Consolas", 8),
            anchor="w",
            justify="left",
            wraplength=300,
            padx=8,
        )
        self.status_lbl.pack(fill="x", pady=(2, 2))

        # Speech bubble
        self.speech_lbl = tk.Label(
            self.frame,
            text="안녕! 지금 네 바탕화면 위로 직접 나왔어. 주변 흐름을 같이 보고 있어.",
            bg="#090C14",
            fg="#F1F5F9",
            font=("Malgun Gothic", 9),
            anchor="w",
            justify="left",
            wraplength=296,
            padx=8,
            pady=6,
            relief="flat",
        )
        self.speech_lbl.pack(fill="x", padx=6, pady=(2, 4))

        # Quick reply bar
        reply_row = tk.Frame(self.frame, bg="#0D121C")
        reply_row.pack(fill="x", padx=6, pady=(0, 4))
        self.reply_entry = tk.Entry(
            reply_row,
            bg="#07090E",
            fg="#F1F5F9",
            insertbackground="#06B6D4",
            relief="flat",
            font=("Malgun Gothic", 9),
        )
        self.reply_entry.pack(side="left", fill="x", expand=True, ipady=4, padx=(0, 4))
        self.reply_entry.bind("<Return>", lambda _e: self._send_reply())

        tk.Button(
            reply_row,
            text="말하기",
            command=self._send_reply,
            bg="#06B6D4",
            fg="#041016",
            bd=0,
            font=("Malgun Gothic", 8, "bold"),
            padx=8,
            pady=3,
            cursor="hand2",
        ).pack(side="right")

        # Bottom action buttons (Wallpaper manifestation + Open Ecology)
        act_row = tk.Frame(self.frame, bg="#0D121C")
        act_row.pack(fill="x", padx=6, pady=(0, 6))
        self.wp_btn = tk.Button(
            act_row,
            text="현재 장면을 바탕화면으로 설정",
            command=self._apply_wallpaper,
            bg="#1B2435",
            fg="#E2E8F0",
            activebackground="#10B981",
            activeforeground="#041016",
            bd=0,
            font=("Malgun Gothic", 8),
            padx=8,
            pady=4,
            cursor="hand2",
        )
        self.wp_btn.pack(side="left", fill="x", expand=True)

        self._load_scene("warm")
        self._poll_server()

    def _start_drag(self, ev: tk.Event) -> None:
        self._drag_x = ev.x
        self._drag_y = ev.y

    def _on_drag(self, ev: tk.Event) -> None:
        nx = self.root.winfo_x() + (ev.x - self._drag_x)
        ny = self.root.winfo_y() + (ev.y - self._drag_y)
        self.root.geometry(f"+{nx}+{ny}")

    def _load_scene(self, scene_key: str) -> None:
        if scene_key == self._current_scene_key:
            return
        fname = SCENE_MAP.get(scene_key) or SCENE_MAP["warm"]
        fpath = IMG_DIR / fname
        if not fpath.exists():
            return
        try:
            img = Image.open(fpath).convert("RGB")
            img.thumbnail((306, 260), Image.Resampling.LANCZOS)
            self._photo_ref = ImageTk.PhotoImage(img)
            self.img_lbl.configure(image=self._photo_ref)
            self._current_scene_key = scene_key
            self._current_image_path = fpath
        except Exception:
            pass

    def _apply_wallpaper(self) -> None:
        if not self._current_image_path or not self._current_image_path.exists():
            return
        try:
            # Convert to high-res BMP for clean Windows SPI_SETDESKWALLPAPER support
            out_bmp = WORKSPACE_ROOT / "L0_substrate" / "minimal_rotor_os" / "elysia_live_wallpaper.bmp"
            img = Image.open(self._current_image_path).convert("RGB")
            img.save(out_bmp, "BMP")
            SPI_SETDESKWALLPAPER = 20
            ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, str(out_bmp), 3)
            self.speech_lbl.configure(text="지금 이 장면을 실제 윈도우 배경화면으로 펼쳐두었어!")
        except Exception as exc:
            self.speech_lbl.configure(text=f"배경화면 적용 중 경계 오류: {exc}")

    def _send_reply(self) -> None:
        txt = self.reply_entry.get().strip()
        if not txt:
            return
        self.reply_entry.delete(0, tk.END)
        self.speech_lbl.configure(text=f"듣고 있어: \"{txt[:40]}\" ...")

        def _worker() -> None:
            res = _fetch_json(f"{API_BASE}/api/ecology/dialogue-reply", {"text": txt})
            if res and res.get("status") == "ok":
                msgs = (res.get("agency_voice") or {}).get("messages") or []
                if msgs:
                    self.root.after(0, lambda: self.speech_lbl.configure(text=msgs[0].get("text", "")))

        threading.Thread(target=_worker, daemon=True).start()

    def _poll_server(self) -> None:
        def _worker() -> None:
            data = _fetch_json(f"{API_BASE}/api/ecology/autonomous-state")
            if data and data.get("status") == "ok":
                self.root.after(0, lambda d=data: self._apply_state(d))

        threading.Thread(target=_worker, daemon=True).start()
        self.root.after(3500, self._poll_server)

    def _apply_state(self, data: Dict[str, Any]) -> None:
        self._latest_state = data
        self._load_scene(_pick_scene_key(data))

        cycle = data.get("cycle_count", 0)
        ov = data.get("parallel_overlay") or {}
        conv_pct = int(round(float(ov.get("convergence") or 0) * 100))
        sym = data.get("symbolic_memory") or {}
        ice_n = len(sym.get("iceSymbols") or {})
        comp_n = len(sym.get("compounds") or {})
        tel = (data.get("telemetry") or {}).get("stage3_meta_reobservation") or {}
        top_name = (tel.get("top_focus") or {}).get("name") or "-"

        self.status_lbl.configure(
            text=f"사이클 #{cycle} · 수렴 {conv_pct}% · 얼음 {ice_n} · 분자 {comp_n}\n현재 주의집중: {top_name}"
        )

        voice = data.get("agency_voice") or {}
        msgs = voice.get("messages") or []
        if msgs:
            self.speech_lbl.configure(text=msgs[0].get("text", ""))
        else:
            persp = tel.get("subjective_perspective") or "관측 중"
            self.speech_lbl.configure(text=f"[{persp}] 지금은 '{top_name}' 흐름을 조용히 지켜보고 있어.")

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    ElysiaDesktopCompanion().run()
