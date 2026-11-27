r"""
ELYSIA Phase 1 — Real 4K / Live Screen CUDA Visual Object-Carving Rotor
=======================================================================

Zero toy code, zero arbitrary scalar collapse:
- Uses REAL NVIDIA CUDA (PyTorch GPU tensors) + REAL OpenCV (`cv2`) + REAL `mss` screen capture
  or REAL 4K video files (`cv2.VideoCapture`).
- Maintains a `0000` static background carrier on the GPU so unchanged background pixels are
  skipped, while ONLY `1` (object-level change / contrast heterogeneity) is carved into
  higher-order Multi-Sensory Visual Object Units:
    Form (shape, contour vertices, compactness, aspect)
    + Chroma & Heterogeneity (dominant hue/saturation, edge texture)
    + Spatial Relation (position, relative scale)
    + Temporal Trajectory (velocity, appearing / moving / stationary_0000)

This carved object structure itself is the higher-order "word / cognitive unit"
— not raw pixels and not a 1D float score.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import cv2  # type: ignore
import numpy as np

try:
    import torch  # type: ignore
except ImportError:
    torch = None

try:
    import mss  # type: ignore
except ImportError:
    mss = None


@dataclass
class CarvedVisualObject:
    """Higher-order perceptual object carved from visual reality (not raw pixels)."""

    object_id: str
    form_class: str  # e.g. "둥근/유기적 형태", "사각/구조적 형태", "선형/가늘고 긴 형태"
    vertex_count: int
    compactness: float
    aspect_ratio: float
    area_ratio: float
    bbox_norm: Tuple[float, float, float, float]  # (x, y, w, h) in [0, 1]
    center_norm: Tuple[float, float]
    dominant_hue_label: str
    saturation_level: str
    brightness_level: str
    texture_heterogeneity: str  # "매끄러움(저질감)" | "중간 결" | "거침/고이질성"
    motion_vector_norm: Tuple[float, float]
    temporal_state: str  # "출현(1)" | "이동 중(1)" | "정지 경계(0)"


def _hue_to_korean_spectrum(h: float, s: float, v: float) -> str:
    if v < 45:
        return "어두운 무채(흑)"
    if s < 35:
        return "밝은 무채(백/회)" if v > 175 else "중간 무채(회)"
    if h < 12 or h >= 168:
        return "적색 스펙트럼"
    if h < 28:
        return "주황/황토 스펙트럼"
    if h < 42:
        return "황색 스펙트럼"
    if h < 85:
        return "녹색 스펙트럼"
    if h < 128:
        return "청/시안 스펙트럼"
    return "자색/보라 스펙트럼"


def _classify_form(contour: np.ndarray, w: int, h: int, area: float) -> Tuple[str, int, float]:
    peri = float(cv2.arcLength(contour, True))
    approx = cv2.approxPolyDP(contour, 0.03 * peri, True)
    verts = int(len(approx))
    compactness = float((4.0 * math.pi * area) / max(1e-5, peri * peri))
    aspect = float(w) / float(max(1, h))
    if aspect > 3.2 or aspect < 0.31:
        return "선형/가늘고 긴 형태", verts, round(compactness, 3)
    if verts == 4 and compactness > 0.65:
        return "사각/구조적 프레임 형태", verts, round(compactness, 3)
    if compactness > 0.72:
        return "둥근/응집 객체 형태", verts, round(compactness, 3)
    return "복합/유기적 윤곽 형태", verts, round(compactness, 3)


class CudaVisualObjectRotor:
    """
    GPU-accelerated 0000-carrier visual rotor that carves real objects from
    live desktop frames (`mss`) or real 4K videos (`cv2.VideoCapture`).
    """

    def __init__(self, diff_threshold: float = 18.0, min_area_ratio: float = 0.0015):
        self.diff_threshold = float(diff_threshold)
        self.min_area_ratio = float(min_area_ratio)
        self.use_cuda = bool(torch is not None and torch.cuda.is_available())
        self.device = torch.device("cuda") if self.use_cuda else (torch.device("cpu") if torch is not None else None)
        self.carrier_gpu = None  # 0000 static background tensor on GPU
        self.carrier_cpu: Optional[np.ndarray] = None
        self.prev_objects: List[CarvedVisualObject] = []
        self.frame_index = 0

    def _compute_change_mask(self, frame_bgr: np.ndarray) -> Tuple[np.ndarray, float]:
        """Computes 0000 (unchanged) vs 1 (changed) mask on CUDA GPU if available."""
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        if self.use_cuda and torch is not None:
            t = torch.from_numpy(gray).to(self.device, dtype=torch.float16)
            if self.carrier_gpu is None or self.carrier_gpu.shape != t.shape:
                self.carrier_gpu = t.clone()
                # First frame: carve salient contrast boundaries instead of empty zero diff
                edges = cv2.Canny(gray, 55, 145)
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
                mask = cv2.dilate(edges, kernel, iterations=2)
                skipped_ratio = float(1.0 - np.count_nonzero(mask) / max(1, mask.size))
                return mask, round(skipped_ratio, 4)

            diff = torch.abs(t - self.carrier_gpu)
            changed_bool = diff > self.diff_threshold
            # Slowly adapt 0000 carrier toward invariant background
            self.carrier_gpu = self.carrier_gpu * 0.92 + t * 0.08
            changed_px = int(changed_bool.sum().item())
            total_px = int(t.numel())
            skipped_ratio = float(1.0 - changed_px / max(1, total_px))
            mask = (changed_bool.to(torch.uint8) * 255).cpu().numpy()
            return mask, round(skipped_ratio, 4)

        # CPU fallback using NumPy
        g_f = gray.astype(np.float32)
        if self.carrier_cpu is None or self.carrier_cpu.shape != g_f.shape:
            self.carrier_cpu = g_f.copy()
            edges = cv2.Canny(gray, 55, 145)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
            mask = cv2.dilate(edges, kernel, iterations=2)
            return mask, round(float(1.0 - np.count_nonzero(mask) / max(1, mask.size)), 4)

        diff = np.abs(g_f - self.carrier_cpu)
        changed = diff > self.diff_threshold
        self.carrier_cpu = self.carrier_cpu * 0.92 + g_f * 0.08
        skipped_ratio = float(1.0 - np.count_nonzero(changed) / max(1, changed.size))
        return (changed.astype(np.uint8) * 255), round(skipped_ratio, 4)

    def process_frame(self, frame_bgr: np.ndarray, max_objects: int = 8) -> Dict[str, Any]:
        t0 = time.perf_counter()
        self.frame_index += 1
        H, W = frame_bgr.shape[:2]
        total_area = float(max(1, H * W))

        mask, skipped_0000_ratio = self._compute_change_mask(frame_bgr)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        clean_mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(clean_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

        # Sort by contour area descending and carve structured perceptual objects
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        carved: List[CarvedVisualObject] = []

        for idx, cnt in enumerate(contours):
            if len(carved) >= max_objects:
                break
            area = float(cv2.contourArea(cnt))
            area_ratio = area / total_area
            if area_ratio < self.min_area_ratio:
                continue

            x, y, bw, bh = cv2.boundingRect(cnt)
            form_class, verts, compactness = _classify_form(cnt, bw, bh, area)

            roi_hsv = hsv[y : y + bh, x : x + bw]
            roi_gray = gray[y : y + bh, x : x + bw]
            mean_h = float(np.mean(roi_hsv[:, :, 0])) if roi_hsv.size else 0.0
            mean_s = float(np.mean(roi_hsv[:, :, 1])) if roi_hsv.size else 0.0
            mean_v = float(np.mean(roi_hsv[:, :, 2])) if roi_hsv.size else 0.0
            lap_var = float(cv2.Laplacian(roi_gray, cv2.CV_64F).var()) if roi_gray.size else 0.0

            hue_label = _hue_to_korean_spectrum(mean_h, mean_s, mean_v)
            sat_label = "고채도(선명)" if mean_s >= 120 else ("중채도" if mean_s >= 45 else "저채도(무채)")
            bri_label = "밝음" if mean_v >= 165 else ("중간 명도" if mean_v >= 75 else "어두움")
            tex_label = "거침/고이질성" if lap_var >= 350 else ("중간 결" if lap_var >= 80 else "매끄러움(저질감)")

            cx = round((x + bw * 0.5) / W, 4)
            cy = round((y + bh * 0.5) / H, 4)

            # Match against previous frame carved objects for temporal trajectory
            dx, dy = 0.0, 0.0
            t_state = "출현(1)"
            if self.prev_objects:
                best_prev = min(
                    self.prev_objects,
                    key=lambda po: math.hypot(po.center_norm[0] - cx, po.center_norm[1] - cy),
                )
                dist = math.hypot(best_prev.center_norm[0] - cx, best_prev.center_norm[1] - cy)
                if dist < 0.18:
                    dx = round(cx - best_prev.center_norm[0], 4)
                    dy = round(cy - best_prev.center_norm[1], 4)
                    t_state = "이동 중(1)" if dist > 0.008 else "정지 경계(0)"

            carved.append(
                CarvedVisualObject(
                    object_id=f"vis_obj_{self.frame_index}_{idx}",
                    form_class=form_class,
                    vertex_count=verts,
                    compactness=compactness,
                    aspect_ratio=round(bw / float(max(1, bh)), 3),
                    area_ratio=round(area_ratio, 4),
                    bbox_norm=(round(x / W, 4), round(y / H, 4), round(bw / W, 4), round(bh / H, 4)),
                    center_norm=(cx, cy),
                    dominant_hue_label=hue_label,
                    saturation_level=sat_label,
                    brightness_level=bri_label,
                    texture_heterogeneity=tex_label,
                    motion_vector_norm=(dx, dy),
                    temporal_state=t_state,
                )
            )

        self.prev_objects = carved
        elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 2)

        return {
            "status": "ok",
            "frame_index": self.frame_index,
            "resolution": [W, H],
            "cuda_used": self.use_cuda,
            "gpu_name": str(torch.cuda.get_device_name(0)) if (self.use_cuda and torch is not None) else "CPU",
            "elapsed_ms": elapsed_ms,
            "carrier_0000_skipped_ratio": skipped_0000_ratio,
            "carved_object_count": len(carved),
            "carved_objects": [asdict(o) for o in carved],
        }


def run_live_screen_carve(frames: int = 2, interval_s: float = 0.25) -> Dict[str, Any]:
    """Captures REAL live OS desktop frames via `mss` and carves objects on CUDA GPU."""
    if mss is None:
        return {"status": "error", "message": "mss not installed"}
    rotor = CudaVisualObjectRotor()
    results = []
    with mss.mss() as sct:
        mon = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
        for i in range(max(1, frames)):
            shot = np.array(sct.grab(mon))
            bgr = cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR)
            results.append(rotor.process_frame(bgr))
            if i + 1 < frames:
                time.sleep(interval_s)
    return {
        "status": "ok",
        "source": "live_desktop_mss",
        "frames_processed": len(results),
        "latest": results[-1],
        "history": results,
    }


def run_video_file_carve(video_path: str, max_frames: int = 6) -> Dict[str, Any]:
    """Processes a REAL video file (including 4K MP4/MKV) via OpenCV + CUDA."""
    p = Path(video_path)
    if not p.exists():
        return {"status": "error", "message": f"Video not found: {video_path}"}
    cap = cv2.VideoCapture(str(p))
    if not cap.isOpened():
        return {"status": "error", "message": f"Could not open video: {video_path}"}
    rotor = CudaVisualObjectRotor()
    results = []
    try:
        for _ in range(max(1, max_frames)):
            ok, frame = cap.read()
            if not ok or frame is None:
                break
            results.append(rotor.process_frame(frame))
    finally:
        cap.release()
    if not results:
        return {"status": "error", "message": "No frames decoded from video"}
    return {
        "status": "ok",
        "source": str(p),
        "frames_processed": len(results),
        "latest": results[-1],
    }


def main() -> None:
    mode = sys.argv[1].strip().lower() if len(sys.argv) > 1 else "screen"
    if mode == "screen":
        out = run_live_screen_carve(frames=2, interval_s=0.2)
    elif mode == "video" and len(sys.argv) > 2:
        out = run_video_file_carve(sys.argv[2], max_frames=5)
    elif mode == "image" and len(sys.argv) > 2:
        img = cv2.imread(sys.argv[2])
        if img is None:
            out = {"status": "error", "message": f"Could not read image: {sys.argv[2]}"}
        else:
            rotor = CudaVisualObjectRotor()
            out = {"status": "ok", "source": sys.argv[2], "latest": rotor.process_frame(img)}
    else:
        out = {"status": "error", "message": "Usage: cuda_visual_object_rotor.py <screen|video <path>|image <path>>"}
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
