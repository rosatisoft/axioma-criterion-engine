from __future__ import annotations

from enum import Enum


class SoftContradictionType(str, Enum):
    """
    Soft contradictions are *tensions* inside the user's formulation that do not
    strictly invalidate the statement, but reduce coherence or certainty and
    often require reframing or follow-up.

    These contradictions are not "hard" logical contradictions; they are
    structural, motivational, temporal, or semantic misalignments.
    """

    # 1) Forma normativa vs evidencia (tu ejemplo: "debo" sin urgencia/presión)
    NORMATIVE_VS_EVIDENCE = "normative_vs_evidence"

    # 2) Urgencia declarada vs urgencia real (dice "es urgente" pero no hay presión real)
    URGENCY_MISMATCH = "urgency_mismatch"

    # 3) Objetivo declarado vs costos/impactos aceptados (quiere X, pero acepta daños incompatibles)
    GOAL_VS_COSTS = "goal_vs_costs"

    # 4) Preservación vs acción (dice que preserva Y, pero la acción lo erosiona)
    PRESERVATION_MISMATCH = "preservation_mismatch"

    # 5) Temporalidad inconsistente (lo describe como temporal, pero amarra a largo plazo)
    TIME_HORIZON_MISMATCH = "time_horizon_mismatch"

    # 6) Alternativas existen pero se niegan/ignoran ("no hay opción" pero sí la hay)
    ALTERNATIVES_IGNORED = "alternatives_ignored"

    # 7) Causa atribuida vs causa plausible (atribuye a X, pero lo que describe apunta a Y)
    CAUSAL_ATTRIBUTION_DRIFT = "causal_attribution_drift"

    # 8) Confusión semántica / término borroso (usa palabras sin definición operativa)
    SEMANTIC_AMBIGUITY = "semantic_ambiguity"

    # 9) Conflicto de valores (dos valores/propósitos chocan sin jerarquía)
    VALUE_CONFLICT = "value_conflict"

    # 10) Externalización de agencia (responsabilidad puesta afuera sin evidencia suficiente)
    AGENCY_EXTERNALIZATION = "agency_externalization"
  
from __future__ import annotations

from enum import Enum


class SoftContradictionSeverity(str, Enum):
    LOW = "low"         # leve: solo baja certeza
    MEDIUM = "medium"   # requiere reframe o 1 pregunta extra
    HIGH = "high"       # reframe + preguntas adicionales o detener por incoherencia

from __future__ import annotations

from enum import Enum


class SoftContradictionAction(str, Enum):
    NOTE_ONLY = "note_only"               # registrar y seguir
    REFRAME = "reframe"                   # reescribir la afirmación en forma coherente
    ASK_FOLLOWUP = "ask_followup"         # agregar 1-2 preguntas de precisión
    LOWER_CONFIDENCE = "lower_confidence" # reducir certeza del dictamen/eje
    STOP_AND_REFINE = "stop_and_refine"   # parar y pedir definición/ajuste antes de seguir

SOFT_CONTRADICTION_DEFAULT_ACTION = {
    "normative_vs_evidence": "reframe",
    "urgency_mismatch": "ask_followup",
    "goal_vs_costs": "ask_followup",
    "preservation_mismatch": "ask_followup",
    "time_horizon_mismatch": "ask_followup",
    "alternatives_ignored": "ask_followup",
    "causal_attribution_drift": "ask_followup",
    "semantic_ambiguity": "stop_and_refine",
    "value_conflict": "ask_followup",
    "agency_externalization": "lower_confidence",
}
