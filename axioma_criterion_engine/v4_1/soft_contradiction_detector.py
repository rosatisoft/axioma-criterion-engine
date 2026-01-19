from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .discernment_enums import Axis, ContradictionType
from .discernment_types import DiscernmentObject, ContradictionItem  # TypedDicts/aliases en tu repo

# Usa TUS enums ya creados
from .soft_contradictions import (
    SoftContradictionType,
    SoftContradictionSeverity,
    SoftContradictionAction,
    SOFT_CONTRADICTION_DEFAULT_ACTION,
)

# Si tu llm_adapter define otra interfaz, solo ajusta este import.
# La idea: un objeto con método generate(prompt:str)->str
try:
    from .llm_adapter import LLMAdapter  # type: ignore
except Exception:  # pragma: no cover
    LLMAdapter = Any  # fallback


# -----------------------------
# Utilidades
# -----------------------------

_SOFT_TO_CONTRADICTION_TYPE: Dict[SoftContradictionType, ContradictionType] = {
    SoftContradictionType.NORMATIVE_VS_EVIDENCE: ContradictionType.COHERENCE,
    SoftContradictionType.URGENCY_MISMATCH: ContradictionType.COHERENCE,
    SoftContradictionType.GOAL_VS_COSTS: ContradictionType.COHERENCE,
    SoftContradictionType.PRESERVATION_MISMATCH: ContradictionType.COHERENCE,
    SoftContradictionType.TIME_HORIZON_MISMATCH: ContradictionType.COHERENCE,
    SoftContradictionType.ALTERNATIVES_IGNORED: ContradictionType.COHERENCE,
    SoftContradictionType.CAUSAL_ATTRIBUTION_DRIFT: ContradictionType.COHERENCE,
    SoftContradictionType.SEMANTIC_AMBIGUITY: ContradictionType.COHERENCE,
    SoftContradictionType.VALUE_CONFLICT: ContradictionType.ETHICAL,
    SoftContradictionType.AGENCY_EXTERNALIZATION: ContradictionType.AGENCY,
}

# Mapeo “soft contradiction → ejes afectados” (base)
_SOFT_TO_AXES: Dict[SoftContradictionType, List[Axis]] = {
    SoftContradictionType.NORMATIVE_VS_EVIDENCE: [Axis.FOUNDATION, Axis.CONTEXT],
    SoftContradictionType.URGENCY_MISMATCH: [Axis.FOUNDATION, Axis.CONTEXT],
    SoftContradictionType.GOAL_VS_COSTS: [Axis.PRINCIPLE, Axis.CONTEXT],
    SoftContradictionType.PRESERVATION_MISMATCH: [Axis.PRINCIPLE],
    SoftContradictionType.TIME_HORIZON_MISMATCH: [Axis.CONTEXT],
    SoftContradictionType.ALTERNATIVES_IGNORED: [Axis.CONTEXT],
    SoftContradictionType.CAUSAL_ATTRIBUTION_DRIFT: [Axis.FOUNDATION],
    SoftContradictionType.SEMANTIC_AMBIGUITY: [Axis.FOUNDATION, Axis.PRINCIPLE],
    SoftContradictionType.VALUE_CONFLICT: [Axis.PRINCIPLE, Axis.CONTEXT],
    SoftContradictionType.AGENCY_EXTERNALIZATION: [Axis.CONTEXT, Axis.PRINCIPLE],
}


def _all_text(obj: DiscernmentObject) -> str:
    parts: List[str] = []
    parts.append(str(obj.get("original_statement", "")))
    f = obj.get("foundation", {}) or {}
    c = obj.get("context", {}) or {}
    p = obj.get("principle", {}) or {}
    parts.append(str(f.get("facts_key", "")))
    parts.append(str(c.get("current_situation", "")))
    parts.append(str(p.get("declared_purpose", "")))
    return "\n".join([x for x in parts if x]).strip()


def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip()).lower()


def _default_action_for(t: SoftContradictionType) -> SoftContradictionAction:
    key = t.value
    act = SOFT_CONTRADICTION_DEFAULT_ACTION.get(key, "note_only")
    try:
        return SoftContradictionAction(act)
    except Exception:
        return SoftContradictionAction.NOTE_ONLY


def _soft_to_contradiction_item(
    t: SoftContradictionType,
    description: str,
    severity: SoftContradictionSeverity = SoftContradictionSeverity.MEDIUM,
    action: Optional[SoftContradictionAction] = None,
    evidence: Optional[List[str]] = None,
) -> ContradictionItem:
    axes = _SOFT_TO_AXES.get(t, [Axis.CONTEXT])
    ctype = _SOFT_TO_CONTRADICTION_TYPE.get(t, ContradictionType.COHERENCE)
    action = action or _default_action_for(t)

    # ContradictionItem en tu repo probablemente tiene:
    # - type (ContradictionType)
    # - description (str)
    # - axes (List[Axis])
    # Si tu TypedDict tiene campos extra, puedes agregar.
    item: Dict[str, Any] = {
        "type": ctype,
        "description": f"[{t.value} | {severity.value} | {action.value}] {description}",
        "axes_affected": axes,
    }
    if evidence:
        item["evidence"] = evidence
    return item  # type: ignore[return-value]


# -----------------------------
# Heurísticas mínimas (fallback)
# -----------------------------

def _heuristic_detect(obj: DiscernmentObject) -> List[ContradictionItem]:
    """
    Detecta solo lo obvio si no hay LLM o si el JSON del LLM falla.
    """
    out: List[ContradictionItem] = []
    statement = _normalize(str(obj.get("original_statement", "")))

    ftxt = _normalize(str((obj.get("foundation", {}) or {}).get("facts_key", "")))
    ctxt = _normalize(str((obj.get("context", {}) or {}).get("current_situation", "")))
    ptxt = _normalize(str((obj.get("principle", {}) or {}).get("declared_purpose", "")))
    alltxt = " ".join([statement, ftxt, ctxt, ptxt]).strip()

    # 1) "debo/tengo que" + "sin urgencia / no es urgente" → NORMATIVE_VS_EVIDENCE
    if ("debo" in statement or "tengo que" in statement) and ("sin urgencia" in alltxt or "no es urgente" in alltxt):
        out.append(
            _soft_to_contradiction_item(
                SoftContradictionType.NORMATIVE_VS_EVIDENCE,
                "La formulación es normativa ('debo') pero tú mismo indicas que no hay urgencia/presión real.",
                severity=SoftContradictionSeverity.MEDIUM,
                action=SoftContradictionAction.REFRAME,
                evidence=["debo/tengo que", "sin urgencia/no es urgente"],
            )
        )

    # 2) Temporalidad: "temporal" + señales de amarre largo plazo
    if "temporal" in alltxt and ("para siempre" in alltxt or "de por vida" in alltxt or "largo plazo" in alltxt):
        out.append(
            _soft_to_contradiction_item(
                SoftContradictionType.TIME_HORIZON_MISMATCH,
                "Se declara como temporal pero aparecen señales de compromiso de largo plazo.",
                severity=SoftContradictionSeverity.MEDIUM,
                action=SoftContradictionAction.ASK_FOLLOWUP,
            )
        )

    # 3) Ambigüedad semántica: palabras borrosas sin operacionalizar
    ambiguous_markers = ["mejor", "mucho", "real", "verdad", "éxito", "feliz", "propósito", "simulación"]
    if any(w in statement for w in ambiguous_markers) and len(statement.split()) < 12:
        out.append(
            _soft_to_contradiction_item(
                SoftContradictionType.SEMANTIC_AMBIGUITY,
                "La afirmación usa términos que requieren definición operativa para evaluar con certeza.",
                severity=SoftContradictionSeverity.LOW,
                action=SoftContradictionAction.ASK_FOLLOWUP,
            )
        )

    return out


# -----------------------------
# LLM detector (lingüística)
# -----------------------------

_LLM_SYSTEM_INSTRUCTIONS = """Eres un detector de contradicción suave para un motor de discernimiento F-C-P.
Tu tarea:
1) Identificar tensiones internas en el lenguaje del usuario.
2) NO moralices. NO aconsejes. NO reescribas el caso (solo detecta).
3) Devuelve SOLO JSON válido.

Lista de tipos permitidos (SoftContradictionType):
- normative_vs_evidence
- urgency_mismatch
- goal_vs_costs
- preservation_mismatch
- time_horizon_mismatch
- alternatives_ignored
- causal_attribution_drift
- semantic_ambiguity
- value_conflict
- agency_externalization

Severidad permitida:
- low, medium, high

Acción sugerida permitida:
- note_only, reframe, ask_followup, lower_confidence, stop_and_refine

Formato de salida:
{
  "items": [
    {
      "type": "<uno de los tipos>",
      "severity": "<low|medium|high>",
      "action": "<note_only|reframe|ask_followup|lower_confidence|stop_and_refine>",
      "description": "<breve descripción>",
      "evidence": ["<fragmento 1>", "<fragmento 2>"]
    }
  ]
}
Si no detectas representativamente nada, regresa {"items": []}.
"""


def _llm_detect(obj: DiscernmentObject, llm: Any) -> List[ContradictionItem]:
    text = _all_text(obj)
    if not text:
        return []

    prompt = (
        _LLM_SYSTEM_INSTRUCTIONS
        + "\n\n"
        + "CASO (texto del usuario):\n"
        + text
        + "\n\n"
        + "Responde SOLO JSON.\n"
    )

    raw = (llm.generate(prompt) or "").strip()
    if not raw:
        return []

    try:
        data = json.loads(raw)
        items = data.get("items", [])
        out: List[ContradictionItem] = []

        for it in items:
            t = SoftContradictionType(it["type"])
            sev = SoftContradictionSeverity(it.get("severity", "medium"))
            act = SoftContradictionAction(it.get("action", _default_action_for(t).value))
            desc = str(it.get("description", "")).strip() or "Soft contradiction detected."
            ev = it.get("evidence", None)
            if isinstance(ev, list):
                ev = [str(x) for x in ev][:3]
            else:
                ev = None

            out.append(_soft_to_contradiction_item(t, desc, sev, act, evidence=ev))

        return out
    except Exception:
        # Si el JSON falla, no tiramos el motor: caemos a heurística
        return []


# -----------------------------
# API principal
# -----------------------------

def detect_soft_contradictions(
    obj: DiscernmentObject,
    llm: Optional[Any] = None,
    *,
    fallback_to_heuristics: bool = True,
) -> List[ContradictionItem]:
    """
    Devuelve una lista de ContradictionItem (compatibles con tu DiscernmentObject)
    usando:
    - LLM (si existe) para contradicciones basadas en lenguaje
    - Heurística mínima como respaldo

    Nota:
    - Este detector NO decide el dictamen final.
    - Solo agrega señales/contradicciones suaves.
    """
    found: List[ContradictionItem] = []

    if llm is not None:
        found.extend(_llm_detect(obj, llm))

    if fallback_to_heuristics:
        found.extend(_heuristic_detect(obj))

    # Deduplicación simple por description
    seen = set()
    unique: List[ContradictionItem] = []
    for c in found:
        d = str(c.get("description", "")).strip()
        if not d or d in seen:
            continue
        seen.add(d)
        unique.append(c)

    return unique

