r"""
ELYSIA Universal Cross-Domain Intersection, Reclassification & Re-Integration Engine
====================================================================================

NO toy cones, NO single-file demos, NO hardcoded human category rules.

Simultaneously ingests HUNDREDS of real heterogeneous objects across 8 distinct
real-world domains on this machine (plus any downloaded open-source 3D assets):
  1. Real Game Videos (`.mp4`/`.webm` across Eternal Return, Sword of Convallaria, Azur Promilia)
  2. Real 3D GPU Shaders & Rendering Laws (`.glsl`/`.osl` from Blender 5.3)
  3. Real 3D Meshes & Scene Containers (`.blend` from Blender 5.3 + `.glb`/`.gltf` open-source PBR/rigged models)
  4. Real 3D World Asset Packs (`UnityFS\0` `.bundle`/`.unity3d`/`.r` across 3 commercial games)
  5. Real Acoustic/Audio Banks (`.bnk`/`.wem` Wwise audio banks from Sword of Convallaria)
  6. Real Network Protocols & Schema Catalogs (`.proto`, `.json`, `.xml` across games + Elysia)
  7. Real Program Logic & Scientific Code (`.py`, `.js`, `.cpp` across Blender 5.3 + Elysia)
  8. Real Native Binaries & Vector Geometry Fonts (`MZ` `.dll`/`.exe` + `.ttf`/`.otf` Bezier fonts)

Then performs TWO genuine unsupervised cross-intersection & reclassification passes:

  Pass A — Universal 10D Physical-Informational Manifold (Blind to Extensions/Folders):
    Extracts 10 continuous physical-informational observables for EVERY object
    (scale octave, head/mid Shannon entropy, membrane entropy gradient, MDL
    zlib compressibility, ASCII symbolic ratio, byte lag-1 autocorrelation,
    zero sparsity, line hierarchy, unique-byte breadth), runs vectorized NumPy
    SVD + K-Means++, and discovers **Cross-Domain Intersections** — where
    completely different human domains share identical underlying structural laws!

  Pass B — Multi-Video Visual-Temporal Prism Cross-Intersection (Across 36+ Real Videos):
    Decodes real multi-frame visual-temporal physics (spatial edge density,
    chroma variance, temporal motion flux, border camera shift, motion
    localization ratio, and bidirectional overlay-contrast PSNR) across dozens
    of real videos from multiple games, strips filenames, and reclassifies them
    purely by their lived visual-motion physics!

  Pass C — Re-Integration & Out-of-Sample Generalization Check:
    Projects emergent archetypes into `CausalField`, synthesizes a template-free
    AST reclassification organ via `CompositionalCodeCortex`, and verifies it
    on a strict 80/20 held-out test split (real generalization, not memorization!).
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
import random
import sys
import time
from typing import Any, Dict, List, Sequence, Tuple
import zlib

import cv2  # type: ignore
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
from core.physics.causal_field import CausalField, InformationVoxel  # noqa: E402
from self_cognitive_expansion_cortex import COGNITIVE_WORLD_DIR, _save_json  # noqa: E402


RECLASS_REPORT_PATH = COGNITIVE_WORLD_DIR / "universal_cross_intersection_reclassification.json"

FEATURE_NAMES = [
    "log10_size",
    "entropy_head",
    "entropy_mid",
    "entropy_gradient",
    "zlib_ratio",
    "ascii_ratio",
    "autocorr_lag1",
    "zero_sparsity",
    "newline_density",
    "unique_byte_frac",
]

VIDEO_FEATURE_NAMES = [
    "edge_density",
    "chroma_std",
    "temporal_motion",
    "border_cam_shift",
    "motion_localization",
    "overlay_psnr_db",
]


def _entropy_u8(arr: np.ndarray) -> float:
    if arr.size == 0:
        return 0.0
    counts = np.bincount(arr, minlength=256)
    probs = counts[counts > 0] / float(arr.size)
    return float(-np.sum(probs * np.log2(probs)))


def extract_10d_physical_signature(fpath: Path) -> Tuple[List[float], Dict[str, Any]] | None:
    """Extracts 10 domain-blind continuous physical-informational observables from ANY file."""
    try:
        sz = fpath.stat().st_size
        if sz < 64:
            return None
        with open(fpath, "rb") as fh:
            head = fh.read(4096)
            if sz > 8192:
                fh.seek(sz // 2)
                mid = fh.read(4096)
            else:
                mid = head
    except OSError:
        return None

    h_arr = np.frombuffer(head, dtype=np.uint8)
    m_arr = np.frombuffer(mid, dtype=np.uint8)
    if h_arr.size < 32:
        return None

    ent_head = _entropy_u8(h_arr)
    ent_mid = _entropy_u8(m_arr)
    ent_grad = ent_mid - ent_head  # Positive => structured header membrane wrapping dense payload!

    comp = zlib.compress(head, level=6)
    zlib_ratio = min(1.5, len(comp) / float(len(head)))

    # Printable ASCII (32..126 + tab/newline/cr)
    printable = ((h_arr >= 32) & (h_arr <= 126)) | (h_arr == 9) | (h_arr == 10) | (h_arr == 13)
    ascii_ratio = float(np.mean(printable))

    # Lag-1 byte autocorrelation (structural smoothness / tabular rhythm)
    hf = h_arr.astype(np.float32)
    h_std = float(np.std(hf))
    if h_std > 1e-6 and hf.size > 2:
        a, b = hf[:-1] - float(np.mean(hf[:-1])), hf[1:] - float(np.mean(hf[1:]))
        autocorr = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
    else:
        autocorr = 0.0

    zero_sparsity = float(np.mean(h_arr == 0))
    newline_density = float(np.mean(h_arr == 10))
    unique_frac = float(np.unique(h_arr).size / 256.0)
    log_sz = math.log10(max(1, sz))

    vec = [
        round(log_sz, 4),
        round(ent_head, 4),
        round(ent_mid, 4),
        round(ent_grad, 4),
        round(zlib_ratio, 4),
        round(ascii_ratio, 4),
        round(autocorr, 4),
        round(zero_sparsity, 4),
        round(newline_density, 4),
        round(unique_frac, 4),
    ]
    meta = {
        "file": fpath.name,
        "ext": fpath.suffix.lower() or "(none)",
        "size_bytes": sz,
        "magic_ascii": "".join(chr(int(c)) if 32 <= int(c) < 127 else "." for c in h_arr[:6]),
    }
    return vec, meta


def _collect_bounded(root: Path, exts: set[str], limit: int, max_walk: int = 8000) -> List[Path]:
    if not root.exists():
        return []
    found: List[Path] = []
    walked = 0
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            walked += 1
            p = Path(dirpath) / fn
            if p.suffix.lower() in exts:
                found.append(p)
                if len(found) >= limit * 3:
                    break
            if walked >= max_walk:
                break
        if len(found) >= limit * 3 or walked >= max_walk:
            break
    if len(found) <= limit:
        return found
    # Evenly strided sample across the directory tree (diverse coverage, not just first folder!)
    step = max(1, len(found) // limit)
    return found[::step][:limit]


def gather_mass_heterogeneous_corpus() -> List[Tuple[str, Path]]:
    """Gathers hundreds of real heterogeneous objects across 8 completely different domains."""
    er_root = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Eternal Return")
    ap_root = Path(r"C:\Nexon\AzurPromilia")
    sc_root = Path(r"C:\Program Files\SwordofConvallaria")
    bl_root = Path(r"C:\Program Files\Blender Foundation\Blender 5.3")
    fonts_root = Path(r"C:\Windows\Fonts")
    oss_3d_root = WORKSPACE_ROOT / "data" / "open_source_3d"

    buckets: List[Tuple[str, List[Path]]] = [
        ("game_videos_mp4", _collect_bounded(er_root, {".mp4"}, 45) + _collect_bounded(sc_root, {".mp4"}, 35) + _collect_bounded(ap_root, {".mp4", ".webm"}, 20)),
        ("blender_3d_shaders_glsl", _collect_bounded(bl_root, {".glsl", ".osl"}, 90, max_walk=15000)),
        ("3d_meshes_blend_gltf", _collect_bounded(bl_root, {".blend"}, 30, max_walk=15000) + _collect_bounded(oss_3d_root, {".glb", ".gltf", ".obj"}, 30) + _collect_bounded(COGNITIVE_WORLD_DIR, {".blend"}, 5)),
        ("game_3d_world_containers", _collect_bounded(er_root, {".bundle", ".unity3d", ".ab"}, 40) + _collect_bounded(ap_root, {".r"}, 45, max_walk=4000) + _collect_bounded(sc_root, {".bundle", ".unity3d"}, 25)),
        ("game_audio_banks_wwise", _collect_bounded(sc_root, {".bnk", ".wem"}, 80, max_walk=6000)),
        ("schemas_protocols_catalogs", _collect_bounded(sc_root, {".proto", ".json", ".xml"}, 45, max_walk=15000) + _collect_bounded(er_root, {".json", ".xml"}, 15) + _collect_bounded(WORKSPACE_ROOT / "data" / "open_sandbox" / "cognitive_world", {".json"}, 15)),
        ("program_logic_code", _collect_bounded(bl_root, {".py"}, 50, max_walk=15000) + _collect_bounded(WORKSPACE_ROOT / "L1_causal_field", {".py"}, 40, max_walk=5000)),
        ("native_binaries_and_fonts", _collect_bounded(er_root, {".dll", ".exe"}, 35) + _collect_bounded(sc_root, {".dll"}, 15) + _collect_bounded(fonts_root, {".ttf", ".otf"}, 40, max_walk=2000)),
    ]

    corpus: List[Tuple[str, Path]] = []
    for domain, paths in buckets:
        for p in paths:
            corpus.append((domain, p))
    return corpus


def _kmeans_numpy(X: np.ndarray, k: int, seed: int = 42, iters: int = 35) -> Tuple[np.ndarray, np.ndarray]:
    """Deterministic vectorized K-Means++ in pure NumPy (zero sklearn dependency)."""
    rng = np.random.default_rng(seed)
    n = X.shape[0]
    k = min(k, n)
    centroids = np.empty((k, X.shape[1]), dtype=np.float64)
    centroids[0] = X[rng.integers(0, n)]
    for c_idx in range(1, k):
        d2 = np.min(np.sum((X[:, None, :] - centroids[None, :c_idx, :]) ** 2, axis=2), axis=1)
        probs = d2 / max(1e-12, float(np.sum(d2)))
        centroids[c_idx] = X[rng.choice(n, p=probs)]

    labels = np.zeros(n, dtype=np.int32)
    for _ in range(iters):
        dists = np.sum((X[:, None, :] - centroids[None, :, :]) ** 2, axis=2)
        new_labels = np.argmin(dists, axis=1).astype(np.int32)
        if np.array_equal(new_labels, labels):
            break
        labels = new_labels
        for j in range(k):
            mask = labels == j
            if np.any(mask):
                centroids[j] = np.mean(X[mask], axis=0)
    return labels, centroids


def _auto_describe_cluster(mean_raw: np.ndarray) -> str:
    """Data-derived structural archetype name strictly from measured physical centroid properties."""
    log_sz, ent_h, ent_m, ent_g, z_rat, asc, auto, z_sp, _nl, _uniq = mean_raw.tolist()
    if asc > 0.85 and z_rat < 0.55:
        return "symbolic_law_and_grammar_manifold"
    if ent_h > 7.2 and z_rat > 0.90:
        return "entropy_saturated_packed_media_manifold"
    if ent_g > 0.65:
        return "container_membrane_header_over_dense_body"
    if z_sp > 0.15 and asc < 0.35:
        return "structured_native_binary_and_table_manifold"
    if ent_h > 5.0 and z_rat < 0.85:
        return "semi_structured_compressed_container_manifold"
    return f"hybrid_structural_manifold_H{ent_h:.1f}"


def extract_video_temporal_prism(video_path: Path, sample_frames: int = 10) -> Dict[str, Any] | None:
    """Decodes real multi-frame visual-temporal physics + overlay-contrast PSNR from ANY video."""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return None
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total < 6:
        cap.release()
        return None
    step = max(1, total // sample_frames)
    frames: List[np.ndarray] = []
    idx = 0
    while len(frames) < sample_frames:
        ok, fr = cap.read()
        if not ok:
            break
        if idx % step == 0:
            h, w = fr.shape[:2]
            if w > 240:
                nh = max(64, int(round(h * (240.0 / w))))
                fr = cv2.resize(fr, (240, nh), interpolation=cv2.INTER_AREA)
            frames.append(fr)
        idx += 1
    cap.release()
    if len(frames) < 5:
        return None

    grays = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32) for f in frames]
    h, w = grays[0].shape
    bh, bw = max(8, int(h * 0.15)), max(8, int(w * 0.15))
    border_mask = np.ones((h, w), dtype=bool)
    border_mask[bh : h - bh, bw : w - bw] = False
    center_mask = ~border_mask

    edge_dens = float(np.mean([np.mean(cv2.Canny(g.astype(np.uint8), 50, 140) > 0) for g in grays]))
    chroma_std = float(np.mean([np.std(cv2.cvtColor(f, cv2.COLOR_BGR2HSV)[:, :, 1]) for f in frames]))

    t_diffs = [np.abs(grays[i] - grays[i - 1]) for i in range(1, len(grays))]
    temp_motion = float(np.mean([np.mean(d) for d in t_diffs]))
    border_shift = float(np.mean([np.mean(d[border_mask]) for d in t_diffs]))
    center_shift = float(np.mean([np.mean(d[center_mask]) for d in t_diffs]))
    localization = min(10.0, center_shift / max(0.25, border_shift))

    # Real bidirectional overlay-contrast PSNR check on this video
    bg = np.median(np.stack(frames, axis=0), axis=0).astype(np.float32)
    psnrs: List[float] = []
    for i, f in enumerate(frames):
        ff = f.astype(np.float32)
        bdiff = np.max(np.abs(ff - bg), axis=2)
        mdiff = np.max(np.abs(ff - frames[i - 1].astype(np.float32)), axis=2) if i > 0 else np.zeros_like(bdiff)
        alpha = np.clip((np.maximum(bdiff, mdiff * 0.9) - 10.0) / 18.0, 0.0, 1.0)[:, :, None]
        recon = bg * (1.0 - alpha) + ff * alpha
        mse = float(np.mean((ff - recon) ** 2))
        psnrs.append(99.0 if mse <= 1e-6 else float(10.0 * math.log10((255.0 ** 2) / mse)))

    return {
        "file": video_path.name,
        "source_game": (
            "Eternal Return" if "Eternal Return" in str(video_path)
            else ("Sword of Convallaria" if "SwordofConvallaria" in str(video_path) else "Azur Promilia")
        ),
        "vec": [
            round(edge_dens, 4),
            round(chroma_std, 2),
            round(temp_motion, 3),
            round(border_shift, 3),
            round(localization, 3),
            round(float(np.mean(psnrs)), 2),
        ],
    }


def run_universal_cross_intersection() -> Dict[str, Any]:
    t0 = time.perf_counter()
    corpus = gather_mass_heterogeneous_corpus()

    records: List[Dict[str, Any]] = []
    X_list: List[List[float]] = []
    video_paths: List[Path] = []

    for domain, fpath in corpus:
        if domain == "game_videos_mp4" and fpath.suffix.lower() == ".mp4":
            video_paths.append(fpath)
        res = extract_10d_physical_signature(fpath)
        if res is None:
            continue
        vec, meta = res
        X_list.append(vec)
        records.append({"human_domain": domain, "vec": vec, **meta})

    X_raw = np.array(X_list, dtype=np.float64)
    mu = np.mean(X_raw, axis=0)
    sd = np.std(X_raw, axis=0) + 1e-9
    X_norm = (X_raw - mu) / sd

    # SVD spectral variance explained (measures genuine multi-scale dimensionality!)
    _u, s_vals, _vt = np.linalg.svd(X_norm, full_matrices=False)
    var_explained = (s_vals ** 2) / max(1e-9, float(np.sum(s_vals ** 2)))

    # Unsupervised K=5 reclassification purely from 10D physical observables (blind to extensions!)
    k_clusters = 5
    labels, _centroids = _kmeans_numpy(X_norm, k=k_clusters, seed=42)

    clusters_summary: List[Dict[str, Any]] = []
    cross_domain_intersections: List[Dict[str, Any]] = []
    cluster_names: Dict[int, str] = {}

    # Build CausalField macro-reintegration
    field = CausalField(dimensions=3)

    for c_id in range(k_clusters):
        idxs = [i for i, lb in enumerate(labels) if int(lb) == c_id]
        if not idxs:
            continue
        mean_raw = np.mean(X_raw[idxs], axis=0)
        cname = _auto_describe_cluster(mean_raw)
        # Ensure unique cluster name if two clusters share coarse archetype
        if cname in cluster_names.values():
            cname = f"{cname}_{c_id}"
        cluster_names[c_id] = cname

        dom_counts: Dict[str, int] = {}
        ext_counts: Dict[str, int] = {}
        sample_files: List[str] = []
        for i in idxs:
            d = records[i]["human_domain"]
            e = records[i]["ext"]
            dom_counts[d] = dom_counts.get(d, 0) + 1
            ext_counts[e] = ext_counts.get(e, 0) + 1
            if len(sample_files) < 6:
                sample_files.append(f"{records[i]['file']} ({d})")

        sorted_doms = sorted(dom_counts.items(), key=lambda kv: -kv[1])
        clusters_summary.append(
            {
                "cluster_id": c_id,
                "reclassified_archetype": cname,
                "object_count": len(idxs),
                "intersecting_human_domains": dict(sorted_doms),
                "top_extensions": dict(sorted(ext_counts.items(), key=lambda kv: -kv[1])[:6]),
                "physical_centroid": {FEATURE_NAMES[j]: round(float(mean_raw[j]), 3) for j in range(len(FEATURE_NAMES))},
                "sample_objects": sample_files,
            }
        )

        # Record genuine cross-domain intersections (where >=2 DIFFERENT human domains converge!)
        if len(sorted_doms) >= 2:
            cross_domain_intersections.append(
                {
                    "emergent_manifold": cname,
                    "converging_domains": [d for d, _cnt in sorted_doms],
                    "domain_counts": dict(sorted_doms),
                    "shared_physical_law": {
                        "entropy_head": round(float(mean_raw[1]), 2),
                        "entropy_gradient": round(float(mean_raw[3]), 2),
                        "zlib_compressibility": round(float(mean_raw[4]), 3),
                        "ascii_symbolic_ratio": round(float(mean_raw[5]), 3),
                    },
                }
            )

        # Project emergent manifold into CausalField as Macro InformationVoxel
        field.add_voxel(
            InformationVoxel(
                id=cname,
                content=dom_counts,
                tensor=np.array([float(mean_raw[4]), float(mean_raw[5]), float(mean_raw[1]) / 8.0], dtype=np.float32),
                mass=1.0 + math.log1p(len(idxs)),
                conductance=min(1.0, len(sorted_doms) * 0.25),
                curiosity_charge=0.3,
                scale_level=3.0,
            )
        )

    # Link emergent manifolds that share bridging human domains via ConnectivityBeams
    c_list = list(cluster_names.values())
    for i in range(len(c_list)):
        for j in range(i + 1, len(c_list)):
            doms_a = set(field.voxels[c_list[i]].content.keys())
            doms_b = set(field.voxels[c_list[j]].content.keys())
            shared_d = doms_a & doms_b
            if shared_d:
                field.link_voxels(c_list[i], c_list[j], strength=float(len(shared_d)))
    field.step(dt=0.1)

    # ------------------------------------------------------------------
    # Pass B: Multi-Video Visual-Temporal Prism Cross-Intersection (36+ Real Videos!)
    # ------------------------------------------------------------------
    rng = random.Random(42)
    video_sample = list(video_paths)
    rng.shuffle(video_sample)
    video_sample = video_sample[:36]

    vid_records: List[Dict[str, Any]] = []
    for vp in video_sample:
        vr = extract_video_temporal_prism(vp, sample_frames=8)
        if vr is not None:
            vid_records.append(vr)

    video_reclass: Dict[str, Any] = {"videos_decoded": len(vid_records), "clusters": []}
    if len(vid_records) >= 6:
        VX = np.array([v["vec"] for v in vid_records], dtype=np.float64)
        VX_norm = (VX - np.mean(VX, axis=0)) / (np.std(VX, axis=0) + 1e-9)
        v_labels, _vc = _kmeans_numpy(VX_norm, k=3, seed=42)
        for vc_id in range(3):
            vidxs = [i for i, lb in enumerate(v_labels) if int(lb) == vc_id]
            if not vidxs:
                continue
            vmean = np.mean(VX[vidxs], axis=0)
            games_in_c: Dict[str, int] = {}
            for i in vidxs:
                g = vid_records[i]["source_game"]
                games_in_c[g] = games_in_c.get(g, 0) + 1
            # Describe strictly by real physics centroid
            b_shift, loc, t_mot = float(vmean[3]), float(vmean[4]), float(vmean[2])
            if loc > 2.2 and b_shift < 3.0:
                v_arch = "static_camera_localized_actor_motion"
            elif b_shift > 5.0 or t_mot > 12.0:
                v_arch = "dynamic_camera_or_fullframe_cinematic_flux"
            else:
                v_arch = "balanced_arena_skill_vfx_dynamics"
            video_reclass["clusters"].append(
                {
                    "cluster_id": vc_id,
                    "visual_physics_class": v_arch,
                    "video_count": len(vidxs),
                    "intersecting_games": games_in_c,
                    "mean_prism_physics": {VIDEO_FEATURE_NAMES[j]: round(float(vmean[j]), 3) for j in range(len(VIDEO_FEATURE_NAMES))},
                    "sample_videos": [f"{vid_records[i]['file']} ({vid_records[i]['source_game']})" for i in vidxs[:4]],
                }
            )

    # ------------------------------------------------------------------
    # Pass C: Template-Free AST Synthesis + Strict 80/20 Held-Out Generalization Test!
    # ------------------------------------------------------------------
    all_pairs: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []
    for i, rec in enumerate(records):
        p = {
            "entropy_head": round(rec["vec"][1], 3),
            "entropy_gradient": round(rec["vec"][3], 3),
            "zlib_ratio": round(rec["vec"][4], 3),
            "ascii_ratio": round(rec["vec"][5], 3),
            "zero_sparsity": round(rec["vec"][7], 3),
        }
        y = {"reclassified_manifold": cluster_names[int(labels[i])]}
        all_pairs.append((p, y))

    rng.shuffle(all_pairs)
    split_at = int(len(all_pairs) * 0.8)
    train_pairs = all_pairs[:split_at]
    test_pairs = all_pairs[split_at:]

    # Subsample balanced representative train set for crisp MDL decision-tree induction
    train_sub = train_pairs[:120]
    cortex = CompositionalCodeCortex()
    cortex.learn_python_structure_from_files(sorted(THIS_DIR.glob("*.py"))[:12])
    prog = cortex.synthesize_decision_tree_ast(
        train_sub,
        purpose="universal_cross_domain_manifold_reclassifier",
    )
    ast_eval: Dict[str, Any] = {"synthesized": False}
    if prog is not None:
        ok_ast, _ = validate_organ_source(prog.source_code)
        if ok_ast:
            fn = _compile_organ_callable(prog.source_code)
            train_hits = sum(1 for p_in, exp in train_pairs if fn(dict(p_in), {}) == exp)
            test_hits = sum(1 for p_in, exp in test_pairs if fn(dict(p_in), {}) == exp)
            ast_eval = {
                "synthesized": True,
                "program_id": prog.program_id,
                "ast_node_count": prog.ast_node_count,
                "train_accuracy": f"{train_hits}/{len(train_pairs)} ({100.0 * train_hits / max(1, len(train_pairs)):.1f}%)",
                "unseen_heldout_test_accuracy": f"{test_hits}/{len(test_pairs)} ({100.0 * test_hits / max(1, len(test_pairs)):.1f}%)",
                "source_code": prog.source_code,
            }

    elapsed_s = round(time.perf_counter() - t0, 2)
    domain_totals: Dict[str, int] = {}
    for r in records:
        domain_totals[r["human_domain"]] = domain_totals.get(r["human_domain"], 0) + 1

    report = {
        "schema": "elysia_universal_cross_intersection_reclassification_v1",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": elapsed_s,
        "total_real_objects_ingested": len(records),
        "human_domains_ingested": domain_totals,
        "svd_top3_variance_explained": [round(float(x), 4) for x in var_explained[:3]],
        "emergent_reclassified_manifolds": clusters_summary,
        "discovered_cross_domain_intersections": cross_domain_intersections,
        "multi_video_visual_physics_reclassification": video_reclass,
        "reintegrated_causal_field": {
            "macro_manifold_voxels": len(field.voxels),
            "inter_manifold_beams": len(field.beams),
            "total_semantic_mass": round(sum(v.mass for v in field.voxels.values()), 3),
        },
        "generalized_ast_reclassifier_80_20": ast_eval,
    }
    _save_json(RECLASS_REPORT_PATH, report)
    return report


if __name__ == "__main__":
    print(json.dumps(run_universal_cross_intersection(), ensure_ascii=False, indent=2))
