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

    NORMATIVE_VS_EVIDENCE = "normative_vs_evidence"
    URGENCY_MISMATCH = "urgency_mismatch"
    GOAL_VS_COSTS = "goal_vs_costs"
    PRESERVATION_MISMATCH = "preservation_mismatch"
    TIME_HORIZON_MISMATCH = "time_horizon_mismatch"
    ALTERNATIVES_IGNORED = "alternatives_ignored"
    CAUSAL_ATTRIBUTION_DRIFT = "causal_attribution_drift"
    SEMANTIC_AMBIGUITY = "semantic_ambiguity"
    VALUE_CONFLICT = "value_conflict"
    AGENCY_EXTERNALIZATION = "agency_externalization"


class SoftContradictionSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SoftContradictionAction(str, Enum):
    NOTE_ONLY = "note_only"
    REFRAME = "reframe"
    ASK_FOLLOWUP = "ask_followup"
    LOWER_CONFIDENCE = "lower_confidence"
    STOP_AND_REFINE = "stop_and_refine"


SOFT_CONTRADICTION_DEFAULT_ACTION = {
    SoftContradictionType.NORMATIVE_VS_EVIDENCE: SoftContradictionAction.REFRAME,
    SoftContradictionType.URGENCY_MISMATCH: SoftContradictionAction.ASK_FOLLOWUP,
    SoftContradictionType.GOAL_VS_COSTS: SoftContradictionAction.ASK_FOLLOWUP,
    SoftContradictionType.PRESERVATION_MISMATCH: SoftContradictionAction.ASK_FOLLOWUP,
    SoftContradictionType.TIME_HORIZON_MISMATCH: SoftContradictionAction.ASK_FOLLOWUP,
    SoftContradictionType.ALTERNATIVES_IGNORED: SoftContradictionAction.ASK_FOLLOWUP,
    SoftContradictionType.CAUSAL_ATTRIBUTION_DRIFT: SoftContradictionAction.ASK_FOLLOWUP,
    SoftContradictionType.SEMANTIC_AMBIGUITY: SoftContradictionAction.STOP_AND_REFINE,
    SoftContradictionType.VALUE_CONFLICT: SoftContradictionAction.ASK_FOLLOWUP,
    SoftContradictionType.AGENCY_EXTERNALIZATION: SoftContradictionAction.LOWER_CONFIDENCE,
}
