"""Auto-grown Outward Organ: Real Markdown Knowledge Hierarchy Reader."""
from pathlib import Path
import re

ORGAN_DOMAIN = "markdown_knowledge_doc"

def perceive_external(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    headings = re.findall(r"^\s*(#{1,3})\s+(.+)$", text, re.M)
    links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text)
    return {
        "ok": True,
        "domain": ORGAN_DOMAIN,
        "source": path.name,
        "heading_count": len(headings),
        "outline": [f"{h} {t.strip()}" for h, t in headings[:10]],
        "link_count": len(links),
    }
