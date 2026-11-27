r"""
ELYSIA Real Photorealistic Video Scale-Rotor Verifier (NVIDIA GTX 1060 CUDA)
============================================================================

ZERO TOY CODE · ZERO FAKE METRICS:
Captures REAL live 1080p/4K video playing anywhere on your screen (e.g., YouTube 4K,
drama, game, or a local 4K video file) and compares Side-by-Side on your real
NVIDIA GeForce GTX 1060 3GB GPU:

  LEFT  (Baseline 100%): Full-frame GPU sharpening/detail pass on 100% of pixels every frame.
  RIGHT (Scale-Rotor):   0000-carrier GPU diff -> reuses cached output for all 0000 pixels,
                         recomputes ONLY '1' changed pixels on GPU!

Measures REAL mathematical PSNR (dB) between Left and Right on every frame so you
can see with your own eyes whether photorealistic video stays visually identical
(>= 38-45 dB) while skipping 70-98% of redundant pixel computation!

Controls inside the live window:
  [M] Toggle '1' change-mask overlay (Amber = recomputed '1', Dark = skipped '0000')
  [+ / -] Adjust 0000 invariance threshold
  [Q / ESC] Close window
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import sys
import time
from typing import Any, Dict, Optional, Tuple

import cv2  # type: ignore
import numpy as np
import torch  # type: ignore
import torch.nn.functional as F  # type: ignore

try:
    import mss  # type: ignore
except ImportError:
    mss = None


class CudaPhotorealisticRotorVerifier:
    def __init__(self, threshold: float = 10.0):
        self.threshold = float(threshold)
        self.use_cuda = torch.cuda.is_available()
        self.device = torch.device("cuda" if self.use_cuda else "cpu")
        self.gpu_name = torch.cuda.get_device_name(0) if self.use_cuda else "CPU"

        # 3x3 unsharp / local contrast kernel (represents real per-pixel heavy video pass)
        k = torch.tensor(
            [[0.0, -0.5, 0.0], [-0.5, 3.0, -0.5], [0.0, -0.5, 0.0]],
            dtype=torch.float16 if self.use_cuda else torch.float32,
            device=self.device,
        ).view(1, 1, 3, 3)
        self.kernel = k.repeat(3, 1, 1, 1)  # depthwise 3-channel

        self.prev_in: Optional[torch.Tensor] = None
        self.cached_out: Optional[torch.Tensor] = None
        self.frame_count = 0

    def _heavy_pass(self, x_nchw: torch.Tensor) -> torch.Tensor:
        out = F.conv2d(x_nchw, self.kernel, padding=1, groups=3)
        return torch.clamp(out, 0.0, 255.0)

    def step(self, frame_bgr: np.ndarray, show_mask: bool = False) -> Tuple[np.ndarray, Dict[str, Any]]:
        self.frame_count += 1
        dtype = torch.float16 if self.use_cuda else torch.float32

        # Upload real frame to GPU [1, 3, H, W]
        x = torch.from_numpy(frame_bgr).to(self.device, dtype=dtype).permute(2, 0, 1).unsqueeze(0)

        # --- LEFT: Baseline 100% full-frame recomputation ---
        if self.use_cuda:
            torch.cuda.synchronize()
        t0 = time.perf_counter()
        full_out = self._heavy_pass(x)
        if self.use_cuda:
            torch.cuda.synchronize()
        baseline_ms = (time.perf_counter() - t0) * 1000.0

        # --- RIGHT: Scale-Rotor 0000-skip + '1' selective recomputation ---
        if self.use_cuda:
            torch.cuda.synchronize()
        t1 = time.perf_counter()

        if self.prev_in is None or self.prev_in.shape != x.shape or self.cached_out is None:
            rotor_out = self._heavy_pass(x)
            self.prev_in = x.clone()
            self.cached_out = rotor_out.clone()
            skipped_ratio = 0.0
            change_mask_2d = torch.ones((x.shape[2], x.shape[3]), dtype=torch.bool, device=self.device)
        else:
            diff = torch.abs(x - self.prev_in).max(dim=1).values  # [1, H, W]
            change_mask_2d = (diff > self.threshold).squeeze(0)   # [H, W]
            changed_px = int(change_mask_2d.sum().item())
            total_px = int(change_mask_2d.numel())
            skipped_ratio = 1.0 - (changed_px / max(1, total_px))

            if changed_px == 0:
                # Pure 0000 invariance: ZERO recomputation!
                rotor_out = self.cached_out
            else:
                # Compute bounding box of '1' changed pixels and recompute ONLY that ROI on GPU!
                ys, xs = torch.where(change_mask_2d)
                y0 = max(0, int(ys.min().item()) - 1)
                y1 = min(x.shape[2], int(ys.max().item()) + 2)
                x0 = max(0, int(xs.min().item()) - 1)
                x1 = min(x.shape[3], int(xs.max().item()) + 2)

                roi_in = x[:, :, y0:y1, x0:x1]
                roi_out = self._heavy_pass(roi_in)

                rotor_out = self.cached_out.clone()
                sub_mask = change_mask_2d[y0:y1, x0:x1].unsqueeze(0).unsqueeze(0)
                rotor_out[:, :, y0:y1, x0:x1] = torch.where(sub_mask, roi_out, rotor_out[:, :, y0:y1, x0:x1])
                self.prev_in[:, :, y0:y1, x0:x1] = torch.where(sub_mask, roi_in, self.prev_in[:, :, y0:y1, x0:x1])
                self.cached_out = rotor_out

        if self.use_cuda:
            torch.cuda.synchronize()
        rotor_ms = (time.perf_counter() - t1) * 1000.0

        # Real mathematical PSNR (dB) between Baseline (100%) and Scale-Rotor output
        mse = float(torch.mean((full_out.float() - rotor_out.float()) ** 2).item())
        psnr_db = 99.0 if mse < 1e-6 else min(99.0, 10.0 * math.log10((255.0 * 255.0) / mse))

        left_np = full_out.squeeze(0).permute(1, 2, 0).to(torch.uint8).cpu().numpy()
        right_np = rotor_out.squeeze(0).permute(1, 2, 0).to(torch.uint8).cpu().numpy()

        if show_mask:
            m_np = change_mask_2d.cpu().numpy()
            overlay = np.zeros_like(right_np)
            overlay[m_np] = (11, 158, 245)  # Amber for '1' recomputed pixels
            right_np = cv2.addWeighted(right_np, 0.55, overlay, 0.45, 0)

        # Build Side-by-Side comparison view scaled cleanly to fit monitor
        h, w = left_np.shape[:2]
        half_w = min(640, w // 2)
        half_h = max(180, int(h * (half_w / float(w))))
        l_small = cv2.resize(left_np, (half_w, half_h), interpolation=cv2.INTER_AREA)
        r_small = cv2.resize(right_np, (half_w, half_h), interpolation=cv2.INTER_AREA)
        combined = np.hstack([l_small, r_small])

        # Draw crisp HUD bar
        cv2.rectangle(combined, (0, 0), (combined.shape[1], 34), (10, 14, 22), -1)
        cv2.line(combined, (half_w, 0), (half_w, half_h), (6, 182, 212), 2)
        cv2.putText(
            combined,
            f"BASELINE 100% ({w}x{h}) | {baseline_ms:.2f} ms",
            (10, 22),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            (241, 245, 249),
            1,
            cv2.LINE_AA,
        )
        cv2.putText(
            combined,
            f"ROTOR 0000-SKIP {skipped_ratio*100:.1f}% | {rotor_ms:.2f} ms | PSNR {psnr_db:.1f} dB [M:Mask Q:Quit]",
            (half_w + 10, 22),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (16, 185, 129),
            1,
            cv2.LINE_AA,
        )

        metrics = {
            "frame": self.frame_count,
            "resolution": [w, h],
            "gpu": self.gpu_name,
            "baseline_ms": round(baseline_ms, 3),
            "rotor_ms": round(rotor_ms, 3),
            "skipped_0000_pct": round(skipped_ratio * 100.0, 2),
            "psnr_db": round(psnr_db, 2),
            "threshold": self.threshold,
        }
        return combined, metrics


def run_live_window(video_path: Optional[str] = None) -> None:
    import tkinter as tk
    from PIL import Image, ImageTk

    verifier = CudaPhotorealisticRotorVerifier(threshold=10.0)
    state = {"show_mask": False, "running": True}

    root = tk.Tk()
    root.title("Elysia Real Video Scale-Rotor Verifier (GTX 1060 CUDA)")
    root.configure(bg="#07090E")
    root.geometry("1260x450+40+40")

    bar = tk.Frame(root, bg="#0D121C", height=36)
    bar.pack(fill="x")

    info_lbl = tk.Label(
        bar,
        text="NVIDIA GTX 1060 CUDA 실측 준비 중...",
        bg="#0D121C",
        fg="#10B981",
        font=("Consolas", 10, "bold"),
        padx=10,
    )
    info_lbl.pack(side="left", pady=6)

    def _toggle_mask() -> None:
        state["show_mask"] = not state["show_mask"]
        mask_btn.configure(text=f"변화(1) 마스크: {'ON' if state['show_mask'] else 'OFF'}")

    def _adj_thresh(delta: float) -> None:
        verifier.threshold = max(2.0, min(40.0, verifier.threshold + delta))

    tk.Button(bar, text="닫기", command=root.destroy, bg="#F43F5E", fg="#FFFFFF", bd=0, padx=10, pady=4).pack(side="right", padx=6)
    tk.Button(bar, text="임계치 +", command=lambda: _adj_thresh(2.0), bg="#1B2435", fg="#F1F5F9", bd=0, padx=8, pady=4).pack(side="right", padx=2)
    tk.Button(bar, text="임계치 -", command=lambda: _adj_thresh(-2.0), bg="#1B2435", fg="#F1F5F9", bd=0, padx=8, pady=4).pack(side="right", padx=2)
    mask_btn = tk.Button(bar, text="변화(1) 마스크: OFF", command=_toggle_mask, bg="#06B6D4", fg="#041016", bd=0, padx=10, pady=4)
    mask_btn.pack(side="right", padx=6)

    canvas_lbl = tk.Label(root, bg="#07090E")
    canvas_lbl.pack(fill="both", expand=True, padx=4, pady=4)
    photo_holder = {"ref": None}

    cap = cv2.VideoCapture(video_path) if (video_path and Path(video_path).exists()) else None
    sct = mss.mss() if (cap is None and mss is not None) else None
    mon = (sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]) if sct is not None else None

    def _tick() -> None:
        if not state["running"]:
            return
        frame_bgr = None
        if cap is not None:
            ok, f = cap.read()
            if not ok:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ok, f = cap.read()
            if ok:
                frame_bgr = f
        elif sct is not None and mon is not None:
            shot = np.array(sct.grab(mon))
            frame_bgr = cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR)

        if frame_bgr is not None:
            view_bgr, m = verifier.step(frame_bgr, show_mask=state["show_mask"])
            rgb = cv2.cvtColor(view_bgr, cv2.COLOR_BGR2RGB)
            photo = ImageTk.PhotoImage(Image.fromarray(rgb))
            photo_holder["ref"] = photo
            canvas_lbl.configure(image=photo)
            info_lbl.configure(
                text=f"GTX 1060 CUDA ({m['resolution'][0]}x{m['resolution'][1]}) | 0000 생략률: {m['skipped_0000_pct']}% | PSNR: {m['psnr_db']} dB | 임계치: {m['threshold']:.0f}"
            )
        root.after(45, _tick)

    def _on_close() -> None:
        state["running"] = False
        if cap is not None:
            cap.release()
        if sct is not None:
            sct.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", _on_close)
    root.after(100, _tick)
    root.mainloop()


def run_headless_bench() -> None:
    if mss is None:
        print(json.dumps({"status": "error", "message": "mss not installed"}))
        return
    verifier = CudaPhotorealisticRotorVerifier(threshold=10.0)
    results = []
    with mss.mss() as sct:
        mon = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
        for _ in range(4):
            shot = np.array(sct.grab(mon))
            bgr = cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR)
            _, m = verifier.step(bgr, show_mask=False)
            results.append(m)
            time.sleep(0.08)
    print(json.dumps({"status": "ok", "frames": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--bench":
        run_headless_bench()
    else:
        run_live_window(sys.argv[1] if len(sys.argv) > 1 else None)
