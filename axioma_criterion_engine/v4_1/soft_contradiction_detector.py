from __future__ import annotations

from typing import List

from .discernment_types import DiscernmentObject
from .soft_contradictions import (
    SoftContradictionAction,
    SoftContradictionSeverity,
    SoftContradictionType,
    SOFT_CONTRADICTION_DEFAULT_ACTION,
)

# If you already defined a TypedDict like SoftContradictionItem in discernment_types.py,
# you can import it here. For now we keep it as dict to avoid breaking if it's not added yet.
SoftContradictionItem = dict


def detect_soft_contradictions(obj: DiscernmentObject) -> List[SoftContradictionItem]:
    """
    Detect soft contradictions in a DiscernmentObject (V4.1.1).

    Soft contradictions are tensions that reduce coherence but do not invalidate the claim.
    Output items should be serializable and deterministic.

    Returns a list of items like:
    {
      "type": SoftContradictionType,
      "severity": SoftContradictionSeverity,
      "affected_axes": ["F","C"],
      "note": str,
      "suggested_action": SoftContradictionAction
    }
    """
    findings: List[SoftContradictionItem] = []

    # MVP rules (start small, expand safely):
    _maybe_add_normative_vs_evidence(obj, findings)
    _maybe_add_action_vs_purpose_gap(obj, findings)

    return findings


# -----------------------------
# Rule helpers (MVP)
# -----------------------------

def _maybe_add_normative_vs_evidence(obj: DiscernmentObject, out: List[SoftContradictionItem]) -> None:
    """
    Detect: NORMATIVE_VS_EVIDENCE

    Trigger when the original statement uses strong normative language ("debo", "tengo que", "necesito")
    but evidence shows:
      - low/no urgency, and/or
      - the counterfactual ("if I don't do it") indicates stability/relief,
      - and no external pressure is present in context.

    This matches your example:
      "debo tener una novia mucho más joven"
      - "es una necesidad sin urgencia"
      - "si no... estaría más tranquilo"
    """
    stmt = (obj.get("original_statement") or "").strip().lower()
    ftxt = (obj.get("foundation", {}).get("facts_key") or "").strip().lower()
    ctxt = (obj.get("context", {}).get("current_situation") or "").strip().lower()

    if not stmt:
        return

    normative_markers = [
        "debo",
        "tengo que",
        "tengo que ",
        "necesito",
        "ocupo",
        "es necesario",
        "es una necesidad",
    ]
    has_normative = any(m in stmt for m in normative_markers)

    if not has_normative:
        return

    # Evidence markers: low urgency / no urgency
    low_urgency_markers = [
        "sin urgencia",
        "no es urgente",
        "no hay urgencia",
        "sin prisa",
        "no urge",
    ]
    has_low_urgency = any(m in ftxt for m in low_urgency_markers)

    # Counterfactual indicates relief/stability if not acted upon
    relief_markers = [
        "más tranquilo",
        "mas tranquilo",
        "mejor",
        "estaría mejor",
        "estaria mejor",
        "en paz",
        "más estable",
        "mas estable",
    ]
    counterfactual_relief = any(m in ftxt for m in relief_markers)

    # External pressure marker (context)
    pressure_markers = [
        "me obligan",
        "me presionan",
        "me exigen",
        "ultimátum",
        "ultimatum",
        "amenaza",
        "si no",
    ]
    has_pressure = any(m in ctxt for m in pressure_markers)

    # Decide
    if (has_low_urgency or counterfactual_relief) and not has_pressure:
        out.append(
            _mk_item(
                ctype=SoftContradictionType.NORMATIVE_VS_EVIDENCE,
                severity=_severity_low_med(has_low_urgency, counterfactual_relief),
                axes=["F", "C"],
                note=(
                    "La afirmación se formula como obligación ('debo/necesito'), "
                    "pero el fundamento sugiere baja urgencia y/o un contrafactual estable "
                    "(p.ej. 'más tranquilo') sin presión externa clara."
                ),
            )
        )


def _maybe_add_action_vs_purpose_gap(obj: DiscernmentObject, out: List[SoftContradictionItem]) -> None:
    """
    Detect: ACTION vs PURPOSE GAP (mapped to SEMANTIC_AMBIGUITY by default, or you can add
    a dedicated type later if you want)

    Trigger when:
      - the statement implies strong action/commitment, but
      - declared_purpose is empty or "no lo sé" (purpose gap)

    This matches your second example:
      "tengo que trabajar mucho..." + declared_purpose: "no lo se"
    """
    stmt = (obj.get("original_statement") or "").strip().lower()
    purpose = (obj.get("principle", {}).get("declared_purpose") or "").strip().lower()

    if not stmt:
        return

    strong_action_markers = [
        "tengo que",
        "debo",
        "necesito",
        "trabajar mucho",
        "hacer lo que sea",
        "cueste lo que cueste",
    ]
    implies_strong_action = any(m in stmt for m in strong_action_markers)

    purpose_gap = (purpose == "") or ("no lo se" in purpose) or ("no sé" in purpose)

    if implies_strong_action and purpose_gap:
        out.append(
            _mk_item(
                ctype=SoftContradictionType.SEMANTIC_AMBIGUITY,
                severity=SoftContradictionSeverity.MEDIUM,
                axes=["P"],
                note=(
                    "Se propone una acción fuerte ('tengo que/debo'), pero el propósito declarado "
                    "está ausente o es indeterminado ('no lo sé'). Esto reduce coherencia y certeza."
                ),
            )
        )


# -----------------------------
# Item construction
# -----------------------------

def _mk_item(
    ctype: SoftContradictionType,
    severity: SoftContradictionSeverity,
    axes: List[str],
    note: str,
) -> SoftContradictionItem:
    action = SOFT_CONTRADICTION_DEFAULT_ACTION.get(ctype, SoftContradictionAction.NOTE_ONLY)
    return {
        "type": ctype,
        "severity": severity,
        "affected_axes": axes,
        "note": note,
        "suggested_action": action,
    }


def _severity_low_med(has_low_urgency: bool, counterfactual_relief: bool) -> SoftContradictionSeverity:
    # If both signals are present, increase severity to MEDIUM.
    if has_low_urgency and counterfactual_relief:
        return SoftContradictionSeverity.MEDIUM
    return SoftContradictionSeverity.LOW
