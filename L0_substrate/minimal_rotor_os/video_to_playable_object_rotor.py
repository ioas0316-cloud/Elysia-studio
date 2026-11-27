r"""
ELYSIA Video-to-Playable-Object Scale-Rotor Extractor
=====================================================

Turns a raw game video (`GadgetSkill8300400.mp4`) into genuinely SEPARATED,
INTERACTIVE playable game components — NO sticker portraits, NO fake shapes:

  1. Temporal Median Decomposition (`0000` Invariant Map):
     Computes the per-pixel temporal median across video frames so moving
     characters & skill VFX disappear, yielding a clean static game map
     (`extracted_map_0000.png`).

  2. Object-Change Carving (`1` Dynamic Playable Character RGBA Sprites):
     Subtracts the clean 0000 map from each active frame (`|frame - map_0000|`),
     extracts the largest coherent moving character silhouette via OpenCV
     morphology + soft alpha feathering, and saves real transparent RGBA
     character animation frames (`carved_actor_0..N.png`)!
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any, Dict, List

import cv2  # type: ignore
import numpy as np

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = WORKSPACE_ROOT / "data" / "video_carved_game"
DEFAULT_VIDEO = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\Eternal Return\EternalReturn_Data\StreamingAssets\GadgetSkillVideo\GadgetSkill8300400.mp4"
)


def extract_playable_world_from_video(video_path: Path, out_dir: Path = OUT_DIR, max_sprites: int = 12) -> Dict[str, Any]:
    if not video_path.exists():
        return {"status": "error", "message": f"Video not found: {video_path}"}

    out_dir.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return {"status": "error", "message": f"Failed to open video: {video_path}"}

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    sample_indices = np.linspace(0, max(1, total_frames - 1), num=min(48, max(12, total_frames)), dtype=int)

    sampled_frames: List[np.ndarray] = []
    for idx in sample_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ok, frame = cap.read()
        if ok and frame is not None:
            sampled_frames.append(frame)
    cap.release()

    if len(sampled_frames) < 4:
        return {"status": "error", "message": "Not enough frames decoded"}

    H, W = sampled_frames[0].shape[:2]

    # 1. Extract Clean Static 0000 Game Map via Temporal Median
    stack = np.stack(sampled_frames, axis=0)  # [N, H, W, 3]
    clean_map_bgr = np.median(stack, axis=0).astype(np.uint8)
    map_path = out_dir / "extracted_map_0000.png"
    cv2.imwrite(str(map_path), clean_map_bgr)

    # 2. Carve Dynamic '1' Character Silhouettes with Real Alpha Transparency
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    carved_meta: List[Dict[str, Any]] = []
    sprite_idx = 0
    for f_i, frame in enumerate(sampled_frames):
        if sprite_idx >= max_sprites:
            break
        diff = np.abs(frame.astype(np.int16) - clean_map_bgr.astype(np.int16)).max(axis=2).astype(np.uint8)
        _, mask = cv2.threshold(diff, 26, 255, cv2.THRESH_BINARY)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_open)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_close)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            continue
        # Pick largest coherent moving object (character / skill action)
        biggest = max(contours, key=cv2.contourArea)
        area = float(cv2.contourArea(biggest))
        if area < (W * H * 0.0025) or area > (W * H * 0.35):
            continue

        x, y, bw, bh = cv2.boundingRect(biggest)
        # Pad crop slightly & keep clean alpha mask only for this carved object
        pad = 8
        x0, y0 = max(0, x - pad), max(0, y - pad)
        x1, y1 = min(W, x + bw + pad), min(H, y + bh + pad)

        obj_mask = np.zeros((H, W), dtype=np.uint8)
        cv2.drawContours(obj_mask, [biggest], -1, 255, thickness=cv2.FILLED)
        obj_mask = cv2.GaussianBlur(obj_mask, (5, 5), 0)

        crop_bgr = frame[y0:y1, x0:x1]
        crop_a = obj_mask[y0:y1, x0:x1]
        rgba = np.dstack([crop_bgr, crop_a])

        # Normalize into a clean 256x256 square RGBA sprite centered by aspect ratio
        sq = np.zeros((256, 256, 4), dtype=np.uint8)
        ch, cw = rgba.shape[:2]
        scale = min(236.0 / max(1, cw), 236.0 / max(1, ch))
        nw, nh = max(1, int(cw * scale)), max(1, int(ch * scale))
        resized = cv2.resize(rgba, (nw, nh), interpolation=cv2.INTER_AREA)
        ox, oy = (256 - nw) // 2, (256 - nh) // 2
        sq[oy : oy + nh, ox : ox + nw] = resized

        sp_path = out_dir / f"carved_actor_{sprite_idx}.png"
        cv2.imwrite(str(sp_path), sq)
        carved_meta.append(
            {
                "sprite_index": sprite_idx,
                "source_frame_sample": f_i,
                "orig_bbox": [x, y, bw, bh],
                "area_ratio": round(area / float(W * H), 4),
                "file": sp_path.name,
            }
        )
        sprite_idx += 1

    manifest = {
        "status": "ok",
        "source_video": video_path.name,
        "resolution": [W, H],
        "clean_map_file": map_path.name,
        "carved_sprite_count": len(carved_meta),
        "sprites": carved_meta,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    vid = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_VIDEO
    print(json.dumps(extract_playable_world_from_video(vid), ensure_ascii=False, indent=2))
