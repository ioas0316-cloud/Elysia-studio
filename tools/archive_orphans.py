#!/usr/bin/env python3
"""
Lossless Archive Migrator for Elysia Phase 1 (P1).
Moves strictly verified zero-reference isolated orphan modules and dead duplicate
organism orchestrators into archive/ while generating archive/ARCHIVE_INDEX.md.
"""
from __future__ import annotations

import shutil
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from audit_python_integrity import audit  # noqa: E402

PROTECTED_EXACT = {
    "L1_causal_field/core/elysia_hangul_kronecker_tokenizer.py",
    "L1_causal_field/core/physics/causal_field.py",
    "L1_causal_field/core/orchestration/canonical_runtime.py",
    "L1_causal_field/core/ingestion/topological_primitives.py",
}

PROTECTED_PREFIXES = (
    "L1_causal_field/core/physics/rotor_extension/",
    "L1_causal_field/core/engine/causal_dsl/",
)

DEAD_DUPLICATE_ORCHESTRATORS = {
    "L1_causal_field/core/topology/unified_elysia_organism.py",
    "L1_causal_field/core/physics/elysia_unified_organism.py",
    "L1_causal_field/core/sensory/elysia_unified_mind_organism.py",
}


def is_protected(rel: str) -> bool:
    if rel in PROTECTED_EXACT:
        return True
    return any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES)


def main() -> int:
    report = audit(ROOT, include_archive=False)
    candidates: list[tuple[str, str]] = []

    for rel in report["core_orphans"]:
        if not is_protected(rel):
            candidates.append((rel, "isolated_orphan (in_deg=0, out_deg=0)"))

    for rel in sorted(DEAD_DUPLICATE_ORCHESTRATORS):
        if (ROOT / rel).exists() and all(c[0] != rel for c in candidates):
            candidates.append((rel, "duplicate_unreferenced_orchestrator (in_deg=0)"))

    archive_root = ROOT / "archive"
    archive_root.mkdir(parents=True, exist_ok=True)

    moved: list[tuple[str, int, str]] = []
    for rel, reason in sorted(candidates):
        src = ROOT / rel
        if not src.exists():
            continue
        loc = len(src.read_text(encoding="utf-8", errors="ignore").splitlines())
        dst = archive_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        moved.append((rel, loc, reason))

    total_loc = sum(item[1] for item in moved)
    index_lines = [
        "# Elysia Experimental Archive Index (Zero-Delete Isolation)",
        "",
        f"- **Archived Modules:** {len(moved)} files",
        f"- **Archived Lines of Code:** {total_loc:,} LOC",
        "- **Policy:** Strictly zero-reference isolated prototypes and unreferenced duplicate orchestrators were moved here without deletion. Any module can be restored by moving it back to its original relative path.",
        "",
        "| Original Path | LOC | Reason |",
        "| :--- | ---: | :--- |",
    ]
    for rel, loc, reason in moved:
        index_lines.append(f"| `{rel}` | {loc} | {reason} |")

    (archive_root / "ARCHIVE_INDEX.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    print(f"Archived {len(moved)} modules ({total_loc:,} LOC) -> archive/ARCHIVE_INDEX.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
