"""
V4.1 Discernment Enums

Design intent:
- Enums define the stable vocabulary of the system (theme, axis, risk, etc.).
- Values are str-based for easy JSON serialization and logging.
- Enums may be extended in future versions without breaking backwards compatibility.
"""

from __future__ import annotations

from enum import Enum


class Theme(str, Enum):
    """Dominant thematic lens used to select interview questions (MVP)."""

    SURVIVAL_STABILITY = "survival_stability"
    ETHICS_VALUES = "ethics_values"
    EXTERNAL_PRESSURE = "external_pressure"


class Axis(str, Enum):
    """Tri-axial method axes (F–C–P)."""

    FOUNDATION = "foundation"  # Fundamento (QUÉ)
    CONTEXT = "context"        # Contexto (POR QUÉ)
    PRINCIPLE = "principle"    # Principio (PARA QUÉ)


class CompletenessLevel(str, Enum):
    """How complete the discernment object is after the interview."""

    COMPLETE = "complete"
    PARTIAL = "partial"
    INSUFFICIENT = "insufficient"


class RiskLevel(str, Enum):
    """User-declared or explicitly inferred risk levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TimeHorizon(str, Enum):
    """Time horizon primarily used in Context axis."""

    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class ClarityLevel(str, Enum):
    """General-purpose 3-level scale for clarity/alignment in MVP."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ContradictionType(str, Enum):
    """Contradiction categories used for signals, reorientation, and penalties."""

    ETHICAL = "ethical"
    COHERENCE = "coherence"
    AGENCY = "agency"


class AnswerSource(str, Enum):
    """
    Provenance of a field:
    - USER: directly stated by the user
    - INFERRED: explicitly inferred by the agent
    - MIXED: a blend of user text + agent inference/reformulation
    """

    USER = "user"
    INFERRED = "inferred"
    MIXED = "mixed"
