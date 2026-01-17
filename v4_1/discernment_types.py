"""
V4.1 Discernment Types (TypedDict-based)

Design intent:
- Flexible, dialogue-friendly structures: partial/incremental construction is allowed.
- Validation is intentionally soft here (no hard exceptions) to preserve dialectic freedom.
- Strong validation (pydantic/dataclasses) is reserved for institutional / IA–IA criterion layers.

Note:
- Use `total=False` on TypedDict to allow incremental builds.
- Enums provide the stable vocabulary; text fields remain free-form.
"""

from __future__ import annotations

from typing import List, Optional, TypedDict

from .discernment_enums import (
    AnswerSource,
    Axis,
    ClarityLevel,
    CompletenessLevel,
    ContradictionType,
    RiskLevel,
    Theme,
    TimeHorizon,
)


class FoundationBlock(TypedDict, total=False):
    """
    FUNDAMENTO (F / QUÉ)
    Captures reality-anchored information vs assumptions.
    """

    facts_key: str  # key facts supporting the decision
    examples_real: bool  # at least one concrete real example exists
    assumptions_detected: str  # brief description of assumptions/suspicions
    clarity: ClarityLevel
    source: AnswerSource  # provenance of the block (optional)


class ContextBlock(TypedDict, total=False):
    """
    CONTEXTO (C / POR QUÉ)
    Captures situational constraints, alternatives, and timing.
    """

    current_situation: str
    constraints: str
    alternatives_identified: str
    time_horizon: TimeHorizon
    source: AnswerSource


class PrincipleBlock(TypedDict, total=False):
    """
    PRINCIPIO (P / PARA QUÉ)
    Captures purpose, values, long-term direction and alignment.
    """

    declared_purpose: str
    values_compromised: str
    long_term_impact: str
    alignment: ClarityLevel
    source: AnswerSource


class ContradictionItem(TypedDict, total=False):
    """
    Contradiction record:
    - Do not attempt to 'solve' contradictions; make them explicit.
    - Used for warnings and potential score penalties.
    """

    description: str
    axes_affected: List[Axis]
    type: ContradictionType


class DeclaredRisks(TypedDict, total=False):
    """User-declared (or explicitly inferred) risk levels."""

    time: RiskLevel
    money: RiskLevel
    health_relationships: RiskLevel
    source: AnswerSource


class DiscernmentObject(TypedDict, total=False):
    """
    The standard Discernment Object for V4.1.

    This is the formalized, structured representation of a decision after guided interview.
    It is the internal 'contract' shared by: interview agent, heuristic reorientation, engine scoring, and dictamen.
    """

    # Traceability
    original_statement: str  # user raw input, preserved as-is

    # Theme routing
    dominant_theme: Theme
    secondary_themes: List[Theme]

    # The actual decision object (agent-clarified)
    decision_object: str  # the concrete decision as structured sentence

    # Tri-axial blocks
    foundation: FoundationBlock
    context: ContextBlock
    principle: PrincipleBlock

    # Signals
    contradictions: List[ContradictionItem]
    declared_risks: DeclaredRisks

    # Meta
    completeness: CompletenessLevel
    agent_notes: str  # brief notes: reorientation, stop reason, etc.


# Optional: a minimal "build state" for interview flow (useful but not required).
class InterviewState(TypedDict, total=False):
    """
    Runtime state for the interactive interview loop.
    Keeps track of asked questions and current hypotheses.
    """

    turns: int
    current_theme: Theme
    asked: List[str]  # store question IDs or raw question text
    stop_reason: Optional[str]
    reoriented: bool
