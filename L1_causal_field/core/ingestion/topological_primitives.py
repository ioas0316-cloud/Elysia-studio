"""
Canonical lightweight topological ingestion primitives (TensionVector, CausalTrajectory,
TopologicalCorpusParser, TopologicalCompiler) restored for compatibility with
magnetic_gear and mva_ingester.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class TensionVector:
    math: float = 0.0
    lang: float = 0.0
    spatial: float = 0.0
    temporal: float = 0.0
    light_mass: float = 0.0


@dataclass
class CausalTrajectory:
    source_id: str
    tokens: List[str] = field(default_factory=list)
    tension_trace: List[TensionVector] = field(default_factory=list)


class TopologicalCorpusParser:
    """Splits raw text streams into lightweight CausalTrajectory objects."""

    def parse(self, text: str, source_id: str = "stream") -> List[CausalTrajectory]:
        chunks = [line.strip() for line in text.splitlines() if line.strip()]
        trajectories: List[CausalTrajectory] = []
        for idx, chunk in enumerate(chunks):
            tokens = chunk.split()
            trajectories.append(CausalTrajectory(source_id=f"{source_id}_{idx}", tokens=tokens))
        return trajectories


class TopologicalCompiler:
    """Compiles CausalTrajectory streams into 5-axis TensionVectors."""

    def compile(self, trajectories: List[CausalTrajectory]) -> List[Tuple[CausalTrajectory, TensionVector]]:
        compiled: List[Tuple[CausalTrajectory, TensionVector]] = []
        for traj in trajectories:
            joined = " ".join(traj.tokens)
            n_chars = max(1, len(joined))
            digits = sum(ch.isdigit() for ch in joined)
            alpha = sum(ch.isalpha() for ch in joined)
            spaces = sum(ch.isspace() for ch in joined)
            tv = TensionVector(
                math=min(1.0, digits / n_chars),
                lang=min(1.0, alpha / n_chars),
                spatial=min(1.0, spaces / n_chars),
                temporal=min(1.0, len(traj.tokens) / 64.0),
                light_mass=min(1.0, n_chars / 256.0),
            )
            traj.tension_trace.append(tv)
            compiled.append((traj, tv))
        return compiled
