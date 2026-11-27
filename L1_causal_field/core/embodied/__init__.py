"""
Elysia Embodied Cognition Package Initialization
"""

from .projector import SymbolPrototype, VQSensoryProjector
from .plasticity import DualPlasticityPipeline
from .emergence import OODLatentBuffer, AxiomInducer, ConsistencyFilter, CrossModalCausalFilter, ResidualCompressibilityFilter
from .embodied_sensorimotor_prediction_loop import (
    EmbodiedSensorimotorPredictionLoop,
    ProjectionWave,
    SensorimotorCollisionResult,
    RelationalRecalibrationOutput,
)

__all__ = [
    "SymbolPrototype",
    "VQSensoryProjector",
    "DualPlasticityPipeline",
    "OODLatentBuffer",
    "ConsistencyFilter",
    "CrossModalCausalFilter",
    "ResidualCompressibilityFilter",
    "AxiomInducer",
    "EmbodiedSensorimotorPredictionLoop",
    "ProjectionWave",
    "SensorimotorCollisionResult",
    "RelationalRecalibrationOutput",
]
