"""
ELYSIA Core Package: Scale Principle Hierarchy Architecture

Exposes scale principle layers (Layer 0 Substrate, Layer 1 Constraint, Layer 2 Resonant,
Layer 3 Macro, and Orchestration) along with backward compatibility facades for existing modules.
"""

from .orchestration.canonical_runtime import CanonicalElysiaRuntime

try:
    from .layer_1_constraint.sensory_prismatic_gate import SensoryPrismaticGate, ContinuousWaveformLens
    from .layer_2_resonant.surface_tension_attractor import SurfaceTensionAttractor, PhaseRelaxationEngine
except ImportError:
    SensoryPrismaticGate = None
    ContinuousWaveformLens = None
    SurfaceTensionAttractor = None
    PhaseRelaxationEngine = None

__all__ = [
    "CanonicalElysiaRuntime",
    "SensoryPrismaticGate",
    "ContinuousWaveformLens",
    "SurfaceTensionAttractor",
    "PhaseRelaxationEngine",
]
