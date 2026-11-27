r"""
Auto-grown Outward Organ: Real External Web Knowledge & Language Grounding
==========================================================================

Reaches OUTWARD to real public human knowledge (Korean/English Wikipedia REST API)
so Elysia can ground unknown words/concepts in real-world knowledge instead of
staying trapped inside internal memory (`BOUND_WORDS: 0`).
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any, Dict

ORGAN_DOMAIN = "external_web_knowledge"


def perceive_external_concept(concept: str, lang: str = "ko", timeout: float = 5.0) -> Dict[str, Any]:
    term = concept.strip()
    if not term:
        return {"ok": False, "error": "empty_concept"}
    encoded = urllib.parse.quote(term.replace(" ", "_"))
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{encoded}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "ElysiaScaleRotorOS/1.0 (OutwardEpistemicOrgan)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return {
            "ok": True,
            "domain": ORGAN_DOMAIN,
            "concept": term,
            "title": data.get("title"),
            "description": data.get("description"),
            "extract": (data.get("extract") or "")[:360],
            "source_url": (data.get("content_urls") or {}).get("desktop", {}).get("page", url),
        }
    except Exception as exc:
        return {"ok": False, "domain": ORGAN_DOMAIN, "concept": term, "error": str(exc)}


if __name__ == "__main__":
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "사과"
    print(json.dumps(perceive_external_concept(q), ensure_ascii=False, indent=2))
