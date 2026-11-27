"""Auto-grown Outward Organ: Real TOML Manifest & Dependency Reader."""
from pathlib import Path
import tomllib

ORGAN_DOMAIN = "toml_project_manifest"

def perceive_external(path: Path) -> dict:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    top_sections = list(data.keys())
    proj = data.get("project") if isinstance(data.get("project"), dict) else {}
    deps = proj.get("dependencies") if isinstance(proj.get("dependencies"), list) else []
    return {
        "ok": True,
        "domain": ORGAN_DOMAIN,
        "source": path.name,
        "top_sections": top_sections[:12],
        "project_name": proj.get("name"),
        "dependency_count": len(deps),
        "dependencies_preview": deps[:10],
    }
