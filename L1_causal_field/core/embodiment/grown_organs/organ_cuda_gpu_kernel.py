"""Auto-grown Outward Organ: Real CUDA `.cu` Kernel Structure Reader."""
from pathlib import Path
import re

ORGAN_DOMAIN = "cuda_gpu_kernel"

def perceive_external(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    globals_fn = re.findall(r"__global__\s+[\w\s\*&<>:]+\s+([A-Za-z_]\w*)\s*\(", text)
    devices_fn = re.findall(r"__device__\s+[\w\s\*&<>:]+\s+([A-Za-z_]\w*)\s*\(", text)
    includes = re.findall(r'^\s*#include\s+[<"]([^>"]+)[>"]', text, re.M)
    shared_mem = len(re.findall(r"\b__shared__\b", text))
    return {
        "ok": True,
        "domain": ORGAN_DOMAIN,
        "source": path.name,
        "global_kernels": globals_fn[:12],
        "device_helpers": devices_fn[:12],
        "includes": includes[:12],
        "shared_memory_decls": shared_mem,
        "line_count": len(text.splitlines()),
    }
