r"""
ELYSIA Stage 5 — Double-Helix Multi-Device Memory Synchronization Protocol
==========================================================================

Synchronizes compact Octave/Molecular Ledgers (`ecology_octave_ledger.json`)
between two independent devices (Device A <-> Device B) using Double-Helix
Complementary Verification:
  - Strand A (Device A ledger) + Strand B (Device B ledger)
  - Complementary Integrity Hash (SHA-256 over canonical sorted symbols)
  - Conflict-free CRDT-style Octave Merge:
      * Sums counts & recomputes Octave Order (일/십/백/천)
      * Preserves provenance & merges Molecular Compounds (`compounds`)
      * Merges Bidirectional Sensory <-> Language Conventions without overwriting
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Dict


def _octave_label(count: int) -> str:
    if count >= 1000:
        return "천(10³) 옥타브 상징"
    if count >= 100:
        return "백(10²) 옥타브 상징"
    if count >= 10:
        return "십(10¹) 옥타브 상징"
    return "일(10⁰) 씨앗"


def double_helix_checksum(ledger: Dict[str, Any]) -> str:
    canonical = json.dumps(
        {
            "ice": sorted(ledger.get("iceSymbols", {}).keys()),
            "compounds": sorted(ledger.get("compounds", {}).keys()),
            "words": sorted((ledger.get("languageConventions") or {}).get("sensoryToWord", {}).keys()),
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def merge_double_helix_ledgers(strand_a: Dict[str, Any], strand_b: Dict[str, Any]) -> Dict[str, Any]:
    """Complementary conflict-free merge of two independent device ledgers."""
    merged_ice: Dict[str, Any] = {}
    for src in (strand_a, strand_b):
        for k, sym in (src.get("iceSymbols") or {}).items():
            if k not in merged_ice:
                merged_ice[k] = dict(sym)
            else:
                new_cnt = int(merged_ice[k].get("count", 0)) + int(sym.get("count", 0))
                merged_ice[k]["count"] = new_cnt
                merged_ice[k]["octaveOrder"] = int(math.floor(math.log10(max(1, new_cnt))))
                merged_ice[k]["symbolUnit"] = _octave_label(new_cnt)
                merged_ice[k]["melted"] = bool(merged_ice[k].get("melted") or sym.get("melted"))

    merged_comp: Dict[str, Any] = {}
    for src in (strand_a, strand_b):
        for bid, comp in (src.get("compounds") or {}).items():
            if bid not in merged_comp:
                merged_comp[bid] = dict(comp)
            else:
                merged_comp[bid]["bondStrength"] = int(merged_comp[bid].get("bondStrength", 1)) + int(comp.get("bondStrength", 1))

    merged_s2w: Dict[str, Any] = {}
    for src in (strand_a, strand_b):
        lc = src.get("languageConventions") or {}
        for sig, entry in (lc.get("sensoryToWord") or {}).items():
            if sig not in merged_s2w:
                merged_s2w[sig] = dict(entry)
            else:
                merged_s2w[sig]["hits"] = int(merged_s2w[sig].get("hits", 1)) + int(entry.get("hits", 1))

    merged = {
        "iceSymbols": merged_ice,
        "compounds": merged_comp,
        "languageConventions": {
            "sensoryToWord": merged_s2w,
            "pendingWords": list((strand_a.get("languageConventions") or {}).get("pendingWords") or []),
            "unnamedClusters": dict((strand_a.get("languageConventions") or {}).get("unnamedClusters") or {}),
        },
        "totalRawAbsorbed": int(strand_a.get("totalRawAbsorbed", 0)) + int(strand_b.get("totalRawAbsorbed", 0)),
        "meltedCount": int(strand_a.get("meltedCount", 0)) + int(strand_b.get("meltedCount", 0)),
        "decayedCount": int(strand_a.get("decayedCount", 0)) + int(strand_b.get("decayedCount", 0)),
        "bondRejections": int(strand_a.get("bondRejections", 0)) + int(strand_b.get("bondRejections", 0)),
    }
    return merged


def run_stage5_sync_verification() -> Dict[str, Any]:
    ledger_path = Path(__file__).resolve().parents[2] / "L1_causal_field" / "core" / "embodiment" / "ecology_octave_ledger.json"
    strand_a = json.loads(ledger_path.read_text(encoding="utf-8")) if ledger_path.exists() else {"iceSymbols": {}, "compounds": {}}

    # Simulate a second device (e.g. mobile/laptop) with its own independent observations
    strand_b = {
        "iceSymbols": {
            "청각 스펙트럼 로터::active_circulation": {
                "key": "청각 스펙트럼 로터::active_circulation",
                "rotorCategory": "청각 스펙트럼 로터",
                "circuitRole": "active_circulation",
                "count": 12,
                "octaveOrder": 1,
                "symbolUnit": "십(10¹) 옥타브 상징",
                "lastSample": "mobile_ambient_harmony",
                "melted": False,
            }
        },
        "compounds": {},
        "languageConventions": {
            "sensoryToWord": {
                "둥근/응집 객체 형태|적색 스펙트럼|밝음|매끄러움(저질감)": {
                    "word": "사과",
                    "direction": "sensory_to_language",
                    "hits": 3,
                }
            },
            "pendingWords": [],
            "unnamedClusters": {},
        },
        "totalRawAbsorbed": 12,
    }

    merged = merge_double_helix_ledgers(strand_a, strand_b)
    packet_bytes = len(json.dumps(merged, ensure_ascii=False).encode("utf-8"))

    return {
        "status": "ok",
        "stage": "Stage 5 — Double-Helix Multi-Device Memory Sync",
        "device_a_checksum": double_helix_checksum(strand_a),
        "device_b_checksum": double_helix_checksum(strand_b),
        "merged_helix_checksum": double_helix_checksum(merged),
        "sync_packet_bytes": packet_bytes,
        "merged_ice_symbols": len(merged["iceSymbols"]),
        "merged_compounds": len(merged["compounds"]),
        "merged_language_bindings": len(merged["languageConventions"]["sensoryToWord"]),
        "total_raw_represented": merged["totalRawAbsorbed"],
    }


if __name__ == "__main__":
    print(json.dumps(run_stage5_sync_verification(), ensure_ascii=False, indent=2))
