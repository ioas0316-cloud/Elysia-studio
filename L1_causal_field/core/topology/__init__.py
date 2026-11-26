"""Topology module exports."""
from .unified_dimensional_causal_engine import (
    PlanetaryWorld,
    SurfaceCell,
    UnifiedDimensionalCausalEngine,
    UnifiedTransformResult,
)

__all__ = [
    "UnifiedDimensionalCausalEngine",
    "UnifiedTransformResult",
    "PlanetaryWorld",
    "SurfaceCell",
]

try:
    from .conceptual_phase_knob_engine import (  # type: ignore[import-not-found]
        CognitiveKnob,
        ConceptualDistanceResult,
        ConceptualEntity,
        ConceptualPhaseKnobEngine,
        ExtractedWorldMechanism,
    )
    __all__.extend([
        "ConceptualPhaseKnobEngine",
        "ConceptualEntity",
        "ConceptualDistanceResult",
        "ExtractedWorldMechanism",
        "CognitiveKnob",
    ])
except ImportError:
    pass
