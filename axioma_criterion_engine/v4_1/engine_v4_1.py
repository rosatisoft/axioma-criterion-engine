"""
V4.1 Criterion Engine (Scoring)

Responsibilities:
- Consume a DiscernmentObject (TypedDict).
- Compute dynamic F–C–P scores.
- Apply penalties for contradictions and incompleteness.
- Produce a transparent evaluation payload for dictamen generation.

Design:
- Deterministic, explainable scoring.
- Conservative by default (no overconfidence).
- Extensible for institutional matrices later.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from .discernment_enums import (
    Axis,
    ClarityLevel,
    CompletenessLevel,
    ContradictionType,
    RiskLevel,
)
from .discernment_types import DiscernmentObject


# -----------------------------
# Scoring configuration (MVP)
# -----------------------------

# Base axis weights (can be tuned later or overridden by institutional matrices)
AXIS_WEIGHTS: Dict[Axis, float] = {
    Axis.FOUNDATION: 0.34,
    Axis.CONTEXT: 0.33,
    Axis.PRINCIPLE: 0.33,
}

# Clarity / alignment numeric mapping
CLARITY_SCORE = {
    ClarityLevel.LOW: 0.3,
    ClarityLevel.MEDIUM: 0.6,
    ClarityLevel.HIGH: 0.9,
}

# Completeness confidence multiplier
COMPLETENESS_CONFIDENCE = {
    CompletenessLevel.COMPLETE: 1.0,
    CompletenessLevel.PARTIAL: 0.75,
    CompletenessLevel.INSUFFICIENT: 0.5,
}

# Penalties by contradiction type (subtractive)
CONTRADICTION_PENALTY = {
    ContradictionType.ETHICAL: 0.20,
    ContradictionType.COHERENCE: 0.15,
    ContradictionType.AGENCY: 0.15,
}

# Risk impact (additive to risk index)
RISK_IMPACT = {
    RiskLevel.LOW: 0.10,
    RiskLevel.MEDIUM: 0.20,
    RiskLevel.HIGH: 0.35,
}


# -----------------------------
# Public API
# -----------------------------

def evaluate_discernment(obj: DiscernmentObject) -> Dict:
    """
    Evaluate a DiscernmentObject and return a structured evaluation payload.

    Returns:
    {
      "scores": { "foundation": float, "context": float, "principle": float },
      "weighted_score": float,
      "risk_index": float,
      "confidence": float,
      "penalties": [...],
      "notes": str
    }
    """
    scores = {
        Axis.FOUNDATION.value: _score_foundation(obj),
        Axis.CONTEXT.value: _score_context(obj),
        Axis.PRINCIPLE.value: _score_principle(obj),
    }

    weighted = _weighted_score(scores)
    penalties, penalty_value = _apply_contradictions(obj)

    weighted_after_penalty = max(0.0, weighted - penalty_value)

    risk_index = _compute_risk_index(obj)
    confidence = _compute_confidence(obj)

    notes = _build_notes(obj, penalties)

    return {
        "scores": scores,
        "weighted_score": round(weighted_after_penalty, 3),
        "risk_index": round(risk_index, 3),
        "confidence": round(confidence, 3),
        "penalties": penalties,
        "notes": notes,
    }


# -----------------------------
# Axis scoring
# -----------------------------

def _score_foundation(obj: DiscernmentObject) -> float:
    block = obj.get("foundation", {})
    clarity = block.get("clarity", ClarityLevel.MEDIUM)

    has_facts = bool(block.get("facts_key"))
    examples_real = bool(block.get("examples_real", False))

    base = CLARITY_SCORE.get(clarity, 0.6)
    if has_facts:
        base += 0.05
    if examples_real:
        base += 0.05

    return min(base, 1.0)


def _score_context(obj: DiscernmentObject) -> float:
    block = obj.get("context", {})
    clarity = ClarityLevel.MEDIUM  # Context clarity inferred conservatively

    has_situation = bool(block.get("current_situation"))
    has_alternatives = bool(block.get("alternatives_identified"))

    base = CLARITY_SCORE.get(clarity, 0.6)
    if has_situation:
        base += 0.05
    if has_alternatives:
        base += 0.05

    return min(base, 1.0)


def _score_principle(obj: DiscernmentObject) -> float:
    block = obj.get("principle", {})
    alignment = block.get("alignment", ClarityLevel.MEDIUM)

    has_purpose = bool(block.get("declared_purpose"))
    has_values = bool(block.get("values_compromised"))

    base = CLARITY_SCORE.get(alignment, 0.6)
    if has_purpose:
        base += 0.05
    if has_values:
        base -= 0.05  # values compromised reduces score

    return max(min(base, 1.0), 0.0)


# -----------------------------
# Aggregation & penalties
# -----------------------------

def _weighted_score(scores: Dict[str, float]) -> float:
    total = 0.0
    for axis, weight in AXIS_WEIGHTS.items():
        total += scores.get(axis.value, 0.0) * weight
    return total


def _apply_contradictions(obj: DiscernmentObject) -> Tuple[List[str], float]:
    penalties: List[str] = []
    penalty_value = 0.0

    for c in obj.get("contradictions", []):
        ctype = c.get("type")
        penalty = CONTRADICTION_PENALTY.get(ctype, 0.0)
        if penalty > 0:
            penalty_value += penalty
            penalties.append(
                f"{ctype.value} contradiction (-{penalty:.2f})"
            )

    return penalties, penalty_value


# -----------------------------
# Risk & confidence
# -----------------------------

def _compute_risk_index(obj: DiscernmentObject) -> float:
    risks = obj.get("declared_risks", {})
    risk_value = 0.0

    for _, level in risks.items():
        if isinstance(level, RiskLevel):
            risk_value += RISK_IMPACT.get(level, 0.0)

    # Normalize to [0,1]
    return min(risk_value, 1.0)


def _compute_confidence(obj: DiscernmentObject) -> float:
    completeness = obj.get("completeness", CompletenessLevel.PARTIAL)
    base = COMPLETENESS_CONFIDENCE.get(completeness, 0.75)

    # Confidence reduction if contradictions exist
    contradictions = len(obj.get("contradictions", []))
    if contradictions:
        base -= min(0.1 * contradictions, 0.3)

    return max(base, 0.3)


# -----------------------------
# Notes
# -----------------------------

def _build_notes(obj: DiscernmentObject, penalties: List[str]) -> str:
    parts: List[str] = []

    if penalties:
        parts.append("Penalties applied: " + "; ".join(penalties))

    completeness = obj.get("completeness")
    if completeness != CompletenessLevel.COMPLETE:
        parts.append(f"Completeness level: {completeness.value}")

    agent_notes = obj.get("agent_notes")
    if agent_notes:
        parts.append(f"Agent notes: {agent_notes}")

    return " | ".join(parts)
