r"""
ELYSIA Stage 1 — Frameless 32-Tile Phase-Synchronized Streamer (Sender <-> Receiver)
====================================================================================

Proves real Phase-Synchronized Communication on live 1920x1080 desktop frames:
- Sender and Receiver share the 8x4 (32-tile) spatial rotor layout (Common Denominator 0).
- On each tick, Sender computes GPU/NumPy tile deltas against the synchronized carrier:
    - Unchanged 0000 tiles: 0 bytes transmitted!
    - Changed '1' tiles:    Only dirty tile JPEG slices + 64-bit dirty bitmask transmitted!
- Receiver reconstructs the full 1920x1080 canvas locally from the delta packet and
  measures REAL wire-bytes saved (%) and REAL reconstructed PSNR (dB) against ground truth.
"""

from __future__ import annotations

import json
import math
import time
from typing import Any, Dict, List, Tuple

import cv2  # type: ignore
import numpy as np

try:
    import mss  # type: ignore
except ImportError:
    mss = None


class PhaseSyncTileSender:
    def __init__(self, gx: int = 8, gy: int = 4, diff_thresh: float = 10.0, jpeg_quality: int = 80):
        self.gx = gx
        self.gy = gy
        self.diff_thresh = float(diff_thresh)
        self.jpeg_quality = int(jpeg_quality)
        self.carrier: np.ndarray | None = None

    def encode_delta_packet(self, frame_bgr: np.ndarray) -> Tuple[Dict[str, Any], int, int]:
        """Returns (packet, delta_wire_bytes, full_frame_jpeg_bytes)."""
        H, W = frame_bgr.shape[:2]
        tw, th = W // self.gx, H // self.gy

        # Reference: how big a standard full-frame JPEG packet would be
        _, full_buf = cv2.imencode(".jpg", frame_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality])
        full_bytes = int(full_buf.size)

        dirty_mask = 0
        tiles_payload: List[Tuple[int, bytes]] = []

        if self.carrier is None or self.carrier.shape != frame_bgr.shape:
            self.carrier = frame_bgr.copy()
            for ty in range(self.gy):
                y0, y1 = ty * th, (H if ty == self.gy - 1 else (ty + 1) * th)
                for tx in range(self.gx):
                    x0, x1 = tx * tw, (W if tx == self.gx - 1 else (tx + 1) * tw)
                    idx = ty * self.gx + tx
                    dirty_mask |= 1 << idx
                    _, tb = cv2.imencode(".jpg", frame_bgr[y0:y1, x0:x1], [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality])
                    tiles_payload.append((idx, tb.tobytes()))
        else:
            diff = np.abs(frame_bgr.astype(np.int16) - self.carrier.astype(np.int16)).max(axis=2)
            for ty in range(self.gy):
                y0, y1 = ty * th, (H if ty == self.gy - 1 else (ty + 1) * th)
                for tx in range(self.gx):
                    x0, x1 = tx * tw, (W if tx == self.gx - 1 else (tx + 1) * tw)
                    idx = ty * self.gx + tx
                    if float(diff[y0:y1, x0:x1].max()) > self.diff_thresh:
                        dirty_mask |= 1 << idx
                        roi = frame_bgr[y0:y1, x0:x1]
                        self.carrier[y0:y1, x0:x1] = roi
                        _, tb = cv2.imencode(".jpg", roi, [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality])
                        tiles_payload.append((idx, tb.tobytes()))

        # 8-byte dirty bitmask header + actual dirty tile bytes
        delta_bytes = 8 + sum(2 + len(b) for _, b in tiles_payload)
        packet = {
            "resolution": (W, H),
            "grid": (self.gx, self.gy),
            "dirty_mask_32bit": dirty_mask,
            "tiles": tiles_payload,
        }
        return packet, delta_bytes, full_bytes


class PhaseSyncTileReceiver:
    def __init__(self):
        self.canvas: np.ndarray | None = None

    def apply_delta_packet(self, packet: Dict[str, Any]) -> np.ndarray:
        W, H = packet["resolution"]
        gx, gy = packet["grid"]
        tw, th = W // gx, H // gy
        if self.canvas is None or self.canvas.shape[:2] != (H, W):
            self.canvas = np.zeros((H, W, 3), dtype=np.uint8)
        for idx, raw_jpg in packet["tiles"]:
            ty, tx = divmod(idx, gx)
            y0, y1 = ty * th, (H if ty == gy - 1 else (ty + 1) * th)
            x0, x1 = tx * tw, (W if tx == gx - 1 else (tx + 1) * tw)
            tile = cv2.imdecode(np.frombuffer(raw_jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            if tile is not None and tile.shape[:2] == (y1 - y0, x1 - x0):
                self.canvas[y0:y1, x0:x1] = tile
        return self.canvas


def run_stage1_stream_verification(frames: int = 8) -> Dict[str, Any]:
    if mss is None:
        return {"status": "error", "message": "mss not installed"}

    sender = PhaseSyncTileSender(gx=8, gy=4, diff_thresh=10.0, jpeg_quality=80)
    receiver = PhaseSyncTileReceiver()
    total_full_bytes = 0
    total_delta_bytes = 0
    psnr_list: List[float] = []
    dirty_counts: List[int] = []

    with mss.mss() as sct:
        mon = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
        for i in range(frames):
            shot = np.array(sct.grab(mon))
            bgr = cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR)
            pkt, d_bytes, f_bytes = sender.encode_delta_packet(bgr)
            reconstructed = receiver.apply_delta_packet(pkt)

            total_full_bytes += f_bytes
            total_delta_bytes += d_bytes
            dirty_counts.append(len(pkt["tiles"]))

            mse = float(np.mean((bgr.astype(np.float32) - reconstructed.astype(np.float32)) ** 2))
            psnr = 99.0 if mse < 1e-6 else min(99.0, 10.0 * math.log10((255.0 * 255.0) / mse))
            psnr_list.append(round(psnr, 2))
            if i + 1 < frames:
                time.sleep(0.12)

    saved_pct = round((1.0 - total_delta_bytes / max(1, total_full_bytes)) * 100.0, 2)
    return {
        "status": "ok",
        "stage": "Stage 1 — Frameless 32-Tile Phase-Sync Streaming",
        "frames_streamed": frames,
        "standard_full_stream_kb": round(total_full_bytes / 1024.0, 2),
        "phase_sync_delta_stream_kb": round(total_delta_bytes / 1024.0, 2),
        "bandwidth_saved_pct": saved_pct,
        "dirty_tiles_per_frame": dirty_counts,
        "mean_reconstructed_psnr_db": round(float(np.mean(psnr_list)), 2),
    }


if __name__ == "__main__":
    print(json.dumps(run_stage1_stream_verification(frames=8), ensure_ascii=False, indent=2))
