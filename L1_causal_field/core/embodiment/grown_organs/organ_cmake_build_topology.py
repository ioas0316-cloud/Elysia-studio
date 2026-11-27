"""Auto-grown Outward Organ: Real CMake Build Topology Reader."""
from pathlib import Path
import re

ORGAN_DOMAIN = "cmake_build_topology"

def perceive_external(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    projects = re.findall(r"project\s*\(\s*([A-Za-z0-9_\-]+)", text, re.I)
    libs = re.findall(r"add_library\s*\(\s*([A-Za-z0-9_\-]+)", text, re.I)
    exes = re.findall(r"add_executable\s*\(\s*([A-Za-z0-9_\-]+)", text, re.I)
    pkgs = re.findall(r"find_package\s*\(\s*([A-Za-z0-9_\-]+)", text, re.I)
    return {
        "ok": True,
        "domain": ORGAN_DOMAIN,
        "source": path.name,
        "projects": projects[:8],
        "libraries": libs[:12],
        "executables": exes[:12],
        "external_packages": pkgs[:12],
    }
