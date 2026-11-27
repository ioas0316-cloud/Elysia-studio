"""
Elysia Core Consciousness Modules
==================================
Houses phase dynamics, scar tensor engine, existential meta-cognition,
phenomenological growth tracker, subjective agency, meta subjectivity, and
the meta-causal epistemic mirror.
"""

from .human_cognitive_phase_dynamics import (
    MultiScalePhaseCouplingEngine,
    HebbianPhasePlasticity,
    MetaCognitiveCriticalityGovernor,
    HierarchicalAttractorNetwork,
)

from .scar_tensor_engine import (
    ScarRecord,
    ScarTensorEngine,
)

from .existential_growth_engine import (
    ExistentialGrowthEngine,
)

from .causal_reverse_engineering_engine import (
    CausalReverseEngineeringEngine,
)

try:
    from .meta_causal_epistemic_mirror import (
        MetaCausalTrajectoryTensor,
        SynestheticTranslationEngine,
        IsomorphicMirrorLayer,
        MetaCausalEpistemicMirror,
    )
except ImportError:
    pass

__all__ = [
    "MultiScalePhaseCouplingEngine",
    "HebbianPhasePlasticity",
    "MetaCognitiveCriticalityGovernor",
    "HierarchicalAttractorNetwork",
    "ScarRecord",
    "ScarTensorEngine",
    "ExistentialGrowthEngine",
    "CausalReverseEngineeringEngine",
    "MetaCausalTrajectoryTensor",
    "SynestheticTranslationEngine",
    "IsomorphicMirrorLayer",
    "MetaCausalEpistemicMirror",
]
