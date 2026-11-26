#!/usr/bin/env python3
"""
Static AST & Internal Import Integrity Auditor for Elysia.
Checks syntax validity, internal dependency graph, orphan count, and broken imports.
"""
from __future__ import annotations

import ast
import collections
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {".git", ".eggs", "__pycache__", "build", "build_native_tests", "node_modules"}


def audit(root: Path = ROOT, include_archive: bool = False) -> dict:
    py_files: dict[str, str] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d for d in dirnames
            if d not in EXCLUDE_DIRS and not d.startswith(".")
            and (include_archive or d != "archive")
        ]
        for fname in filenames:
            if fname.endswith(".py"):
                fpath = Path(dirpath) / fname
                rel = str(fpath.relative_to(root))
                py_files[rel] = fpath.read_text(encoding="utf-8", errors="ignore")

    mod_to_file: dict[str, str] = {}
    pkg_dirs: set[str] = set()
    for rel in py_files:
        p = Path(rel)
        if p.name == "__init__.py":
            mod = str(p.parent).replace(os.sep, ".")
        else:
            mod = rel[:-3].replace(os.sep, ".")
        mod_to_file[mod] = rel
        for prefix in ("L1_causal_field.", "L0_substrate."):
            if mod.startswith(prefix):
                mod_to_file[mod[len(prefix):]] = rel
        # Track parent packages
        parts = mod.split(".")
        for i in range(1, len(parts)):
            sub = ".".join(parts[:i])
            pkg_dirs.add(sub)
            for prefix in ("L1_causal_field.", "L0_substrate."):
                if sub.startswith(prefix):
                    pkg_dirs.add(sub[len(prefix):])

    syntax_errors = []
    in_deg: collections.Counter[str] = collections.Counter()
    out_deg: collections.Counter[str] = collections.Counter()
    broken_imports: list[dict] = []

    for rel, src in sorted(py_files.items()):
        try:
            tree = ast.parse(src, filename=rel)
        except SyntaxError as exc:
            syntax_errors.append({"file": rel, "error": str(exc)})
            continue

        for node in ast.walk(tree):
            mods = []
            if isinstance(node, ast.Import):
                mods = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                mods = [node.module]
            for m in mods:
                top = m.split(".")[0]
                if m in mod_to_file:
                    target = mod_to_file[m]
                    if target != rel:
                        in_deg[target] += 1
                        out_deg[rel] += 1
                elif m in pkg_dirs:
                    out_deg[rel] += 1
                elif top in ("core", "modules", "L1_causal_field", "L0_substrate", "isa_compiler", "spinoffs"):
                    broken_imports.append({"file": rel, "import": m, "line": getattr(node, "lineno", 0)})

    orphans = sorted(
        r for r in py_files
        if not r.endswith("__init__.py")
        and in_deg[r] == 0 and out_deg[r] == 0
        and r.startswith("L1_causal_field/core/")
    )

    return {
        "total_py_files": len(py_files),
        "syntax_errors": syntax_errors,
        "broken_imports": broken_imports,
        "core_orphans_count": len(orphans),
        "core_orphans": orphans,
        "top_hubs": in_deg.most_common(10),
    }


def main() -> int:
    include_archive = "--include-archive" in sys.argv
    as_json = "--json" in sys.argv
    report = audit(ROOT, include_archive=include_archive)
    if as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Total active .py files : {report['total_py_files']}")
        print(f"Syntax errors          : {len(report['syntax_errors'])}")
        print(f"Broken internal imports: {len(report['broken_imports'])}")
        print(f"Core isolated orphans  : {report['core_orphans_count']}")
        if report["broken_imports"]:
            print("\nBroken internal imports:")
            for b in report["broken_imports"]:
                print(f"  - {b['file']}:{b['line']} -> {b['import']}")
    if report["syntax_errors"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
