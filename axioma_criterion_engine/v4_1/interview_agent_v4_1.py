"""
V4.1 Interview Agent (Skeleton)

Goal:
- Guided interview to build a DiscernmentObject incrementally.
- Theme selection -> axis questions -> stop criteria -> reorientation -> finalize object.

Design choices:
- Soft structure (TypedDict): supports dialectic freedom and partial completion.
- Hard vocabulary (Enums): stable reference for themes/axes/levels.
- Reorientation is evidence-driven (from early answers), controlled (no loops).
- Stop criteria prevents endless interviews and preserves user autonomy.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple

from .discernment_enums import (
    Axis,
    ClarityLevel,
    CompletenessLevel,
    ContradictionType,
    RiskLevel,
    Theme,
    TimeHorizon,
)
from .discernment_types import (
    ContextBlock,
    ContradictionItem,
    DeclaredRisks,
    DiscernmentObject,
    FoundationBlock,
    InterviewState,
    PrincipleBlock,
)
from .soft_contradiction_detector import detect_soft_contradictions

# -----------------------------
# Public hook interfaces
# -----------------------------


class LLMInterface:
    """
    Minimal interface for an LLM client.

    Implementations may wrap OpenAI, local models, etc.
    Kept intentionally small to avoid coupling.
    """

    def generate(self, prompt: str) -> str:
        raise NotImplementedError


UserInputFn = Callable[[str], str]


# -----------------------------
# Agent config
# -----------------------------


@dataclass
class InterviewConfigV41:
    max_turns: int = 12
    per_axis_max: int = 3
    allow_single_reorientation: bool = True
    stop_on_minimum_completeness: bool = True


# -----------------------------
# Question bank (MVP)
# -----------------------------

# NOTE: IDs matter only as stable references for logs.
# We keep the phrasing in Spanish for now.

QUESTION_BANK: Dict[Theme, List[Tuple[str, Axis, str]]] = {
    Theme.SURVIVAL_STABILITY: [
        ("SS_F_1", Axis.FOUNDATION, "¿Qué hecho concreto hace necesaria esta decisión ahora?"),
        ("SS_F_2", Axis.FOUNDATION, "¿Qué ocurriría realmente si no tomaras esta decisión?"),
        ("SS_F_3", Axis.FOUNDATION, "¿Esto es una necesidad comprobable o una percepción de urgencia?"),
        ("SS_C_1", Axis.CONTEXT, "¿Qué circunstancias actuales te colocan en esta situación?"),
        ("SS_C_2", Axis.CONTEXT, "¿Qué alternativas reales existen, aunque no sean ideales?"),
        ("SS_C_3", Axis.CONTEXT, "¿Esta decisión es temporal o te ata a largo plazo?"),
        ("SS_P_1", Axis.PRINCIPLE, "¿Qué estás preservando al tomar esta decisión?"),
        ("SS_P_2", Axis.PRINCIPLE, "¿Qué propósito explícito estás declarando con esta decisión?"),
        ("SS_P_3", Axis.PRINCIPLE, "¿Qué valor se dañaría si haces lo contrario?"),
    ],
    Theme.ETHICS_VALUES: [
        ("EV_F_1", Axis.FOUNDATION, "¿Qué hechos verificables sostienen tu afirmación (no interpretaciones)?"),
        ("EV_F_2", Axis.FOUNDATION, "¿Qué evidencia sólida podría contradecir tu postura?"),
        ("EV_F_3", Axis.FOUNDATION, "¿Qué tan claro es para ti qué está 'bien' o 'mal' aquí, y por qué?"),
        ("EV_C_1", Axis.CONTEXT, "¿Quiénes se verán afectados y de qué forma concreta?"),
        ("EV_C_2", Axis.CONTEXT, "¿Qué incentivos o presiones del entorno están influyendo?"),
        ("EV_C_3", Axis.CONTEXT, "¿Qué consecuencias a corto y largo plazo son plausibles?"),
        ("EV_P_1", Axis.PRINCIPLE, "¿Qué principio ético estás tratando de honrar (en una frase)?"),
        ("EV_P_2", Axis.PRINCIPLE, "¿Qué línea no cruzarías aunque te convenga?"),
        ("EV_P_3", Axis.PRINCIPLE, "¿Qué opción preserva mejor dignidad/verdad/justicia según tu criterio?"),
    ],
    Theme.EXTERNAL_PRESSURE: [
        ("EP_F_1", Axis.FOUNDATION, "¿Qué presión externa específica está ocurriendo (quién/qué)?"),
        ("EP_F_2", Axis.FOUNDATION, "¿Qué consecuencias reales existen si no cedes a la presión?"),
        ("EP_F_3", Axis.FOUNDATION, "¿Qué parte es un hecho y qué parte es interpretación o miedo?"),
        ("EP_C_1", Axis.CONTEXT, "¿Qué opciones reales tienes si pones límites?"),
        ("EP_C_2", Axis.CONTEXT, "¿Qué apoyos o recursos existen en tu entorno?"),
        ("EP_C_3", Axis.CONTEXT, "¿Qué tan temporal o permanente es esta presión?"),
        ("EP_P_1", Axis.PRINCIPLE, "¿Qué estás intentando evitar al decidir así?"),
        ("EP_P_2", Axis.PRINCIPLE, "¿Esta decisión protege algo valioso o solo evita conflicto?"),
        ("EP_P_3", Axis.PRINCIPLE, "¿Qué precedente establece esta decisión para ti?"),
    ],
}


# -----------------------------
# Interview Agent
# -----------------------------


class InterviewAgentV41:
    def __init__(
        self,
        llm: Optional[LLMInterface] = None,
        user_input: Optional[UserInputFn] = None,
        config: Optional[InterviewConfigV41] = None,
    ) -> None:
        self.llm = llm
        self.user_input = user_input or (lambda prompt: input(prompt))
        self.config = config or InterviewConfigV41()

    # -------------------------
    # Public API
    # -------------------------

    def run(self, statement: str) -> DiscernmentObject:
        """
        Run an interview for a given statement.

        Returns a DiscernmentObject:
        - original_statement
        - theme classification
        - axis blocks
        - contradictions (hard, optional)
        - soft_contradictions (V4.1.1, optional)
        """
        state: InterviewState = {
            "turns": 0,
            "asked": [],
            "reoriented": False,
            "stop_reason": "",
        }

        theme = self._classify_theme_initial(statement)

        obj: DiscernmentObject = {
            "original_statement": statement,
            "dominant_theme": theme,
            "secondary_themes": [],
            "contradictions": [],
            "completeness": CompletenessLevel.PARTIAL,
            "agent_notes": "",
            "foundation": self._empty_foundation(),
            "context": self._empty_context(),
            "principle": self._empty_principle(),
            "decision_object": "",
        }

        asked_per_axis = {Axis.FOUNDATION: 0, Axis.CONTEXT: 0, Axis.PRINCIPLE: 0}

        self._interview_loop(obj, state, asked_per_axis)

        self._finalize_discernment_object(obj, state)

        return obj

    # -------------------------
    # Interview loop
    # -------------------------

    def _interview_loop(
        self,
        obj: DiscernmentObject,
        state: InterviewState,
        asked_per_axis: Dict[Axis, int],
    ) -> None:
        theme = obj["dominant_theme"]
        questions = QUESTION_BANK.get(theme, QUESTION_BANK[Theme.SURVIVAL_STABILITY])

        for qid, axis, qtext in questions:
            if self._should_stop(obj, state, asked_per_axis):
                break

            if qid in state["asked"]:
                continue

            if asked_per_axis[axis] >= self.config.per_axis_max:
                continue

            answer = self._ask(qid, qtext, state)
            asked_per_axis[axis] += 1

            self._apply_answer(obj, axis, answer)

            # After early answers, detect signals and maybe reorient
            if self.config.allow_single_reorientation:
                prior_theme = obj["dominant_theme"]
                self._detect_signals_and_maybe_reorient(obj, state)

                # If reoriented, restart loop once with new theme
                if state.get("reoriented") and obj["dominant_theme"] != prior_theme:
                    self._append_note(obj, f"Reoriented theme: {prior_theme.value} -> {obj['dominant_theme'].value}")
                    self._interview_loop_restart(obj, state, asked_per_axis)
                    break

    def _interview_loop_restart(
        self,
        obj: DiscernmentObject,
        state: InterviewState,
        asked_per_axis: Dict[Axis, int],
    ) -> None:
        theme = obj["dominant_theme"]
        questions = QUESTION_BANK.get(theme, QUESTION_BANK[Theme.SURVIVAL_STABILITY])

        for qid, axis, qtext in questions:
            if self._should_stop(obj, state, asked_per_axis):
                break

            if qid in state["asked"]:
                continue

            if asked_per_axis[axis] >= self.config.per_axis_max:
                continue

            answer = self._ask(qid, qtext, state)
            asked_per_axis[axis] += 1
            self._apply_answer(obj, axis, answer)

    # -------------------------
    # Asking / applying answers
    # -------------------------

    def _ask(self, qid: str, question: str, state: InterviewState) -> str:
        state["turns"] = int(state.get("turns", 0)) + 1
        state["asked"].append(qid)
        prompt = f"\n[{qid}] {question}\n> "
        return (self.user_input(prompt) or "").strip()

    def _apply_answer(self, obj: DiscernmentObject, axis: Axis, answer: str) -> None:
        if axis == Axis.FOUNDATION:
            f = obj.get("foundation", self._empty_foundation())
            f["facts_key"] = self._append_line(f.get("facts_key", ""), answer)
            f["clarity"] = self._infer_clarity(f["facts_key"])
            obj["foundation"] = f

        elif axis == Axis.CONTEXT:
            c = obj.get("context", self._empty_context())
            c["current_situation"] = self._append_line(c.get("current_situation", ""), answer)
            c["time_horizon"] = self._infer_time_horizon(c["current_situation"])
            obj["context"] = c

        elif axis == Axis.PRINCIPLE:
            p = obj.get("principle", self._empty_principle())
            if not p.get("declared_purpose"):
                p["declared_purpose"] = answer
            else:
                # keep first as declared purpose; append further nuance into notes
                obj["agent_notes"] = self._append_line(obj.get("agent_notes", ""), f"Principle nuance: {answer}")
            p["alignment"] = self._infer_alignment(p.get("declared_purpose", ""))
            obj["principle"] = p

    # -------------------------
    # Stop criteria
    # -------------------------

    def _should_stop(
        self,
        obj: DiscernmentObject,
        state: InterviewState,
        asked_per_axis: Dict[Axis, int],
    ) -> bool:
        if int(state.get("turns", 0)) >= self.config.max_turns:
            state["stop_reason"] = "max_turns_reached"
            return True

        if self.config.stop_on_minimum_completeness and self._minimum_completeness_reached(obj):
            state["stop_reason"] = "minimum_completeness_reached"
            return True

        # If all axes hit max, stop
        if (
            asked_per_axis[Axis.FOUNDATION] >= self.config.per_axis_max
            and asked_per_axis[Axis.CONTEXT] >= self.config.per_axis_max
            and asked_per_axis[Axis.PRINCIPLE] >= self.config.per_axis_max
        ):
            state["stop_reason"] = "per_axis_max_reached"
            return True

        return False

    def _minimum_completeness_reached(self, obj: DiscernmentObject) -> bool:
        has_f = bool(obj.get("foundation", {}).get("facts_key"))
        has_c = bool(obj.get("context", {}).get("current_situation"))
        has_p = bool(obj.get("principle", {}).get("declared_purpose"))
        return has_f and has_c and has_p

    # -------------------------
    # Theme classification (initial)
    # -------------------------

    def _classify_theme_initial(self, statement: str) -> Theme:
        """
        Theme classification:
        - If LLM is available: ask it to classify into the 3 MVP themes.
        - Else: fallback to heuristic.
        """
        if self.llm is not None:
            try:
                prompt = (
                    "Clasifica el siguiente caso en UN SOLO tema dominante, eligiendo EXACTAMENTE uno:\n"
                    "- survival_stability\n"
                    "- ethics_values\n"
                    "- external_pressure\n\n"
                    "Responde SOLO con el identificador.\n\n"
                    f"Caso: {statement}\n"
                )
                out = (self.llm.generate(prompt) or "").strip().lower()

                mapping = {
                    "survival_stability": Theme.SURVIVAL_STABILITY,
                    "ethics_values": Theme.ETHICS_VALUES,
                    "external_pressure": Theme.EXTERNAL_PRESSURE,
                }
                if out in mapping:
                    return mapping[out]
            except Exception:
                pass

        s = statement.lower()
        ethics_markers = ["sé que está mal", "no es correcto", "ilegal", "fraude", "mentir", "corrup", "trampa", "ético"]
        pressure_markers = ["me obligan", "me piden", "presion", "ultimátum", "ultimatum", "amenaz", "si no", "exigen"]
        survival_markers = ["dinero", "trabajo", "renta", "deuda", "pagar", "urgente", "necesito", "ingresos", "estabilidad"]

        if any(m in s for m in ethics_markers):
            return Theme.ETHICS_VALUES
        if any(m in s for m in pressure_markers):
            return Theme.EXTERNAL_PRESSURE
        if any(m in s for m in survival_markers):
            return Theme.SURVIVAL_STABILITY

        return Theme.SURVIVAL_STABILITY

    # -------------------------
    # Signal detection + controlled reorientation
    # -------------------------

    def _detect_signals_and_maybe_reorient(self, obj: DiscernmentObject, state: InterviewState) -> None:
        """
        MVP signal detection from accumulated text.
        Controlled: can reorient only once.
        """
        if state.get("reoriented"):
            return

        text = self._all_text(obj).lower()

        # 1) Ethical conflict signals
        ethical_signals = ["sé que está mal", "no es correcto", "engaña", "fraude", "mentir", "corrup", "trampa"]
        if any(sig in text for sig in ethical_signals):
            if obj["dominant_theme"] != Theme.ETHICS_VALUES:
                obj["secondary_themes"] = self._merge_secondary(obj.get("secondary_themes", []), obj["dominant_theme"])
                obj["dominant_theme"] = Theme.ETHICS_VALUES
                state["reoriented"] = True
                return

        # 2) External pressure signals
        pressure_signals = ["me obligan", "me exigen", "amenaza", "ultimátum", "ultimatum", "si no", "me presionan"]
        if any(sig in text for sig in pressure_signals):
            if obj["dominant_theme"] != Theme.EXTERNAL_PRESSURE:
                obj["secondary_themes"] = self._merge_secondary(obj.get("secondary_themes", []), obj["dominant_theme"])
                obj["dominant_theme"] = Theme.EXTERNAL_PRESSURE
                state["reoriented"] = True
                return

    # -------------------------
    # Finalization
    # -------------------------

    def _finalize_discernment_object(self, obj: DiscernmentObject, state: InterviewState) -> None:
        """
        Sets decision_object and completeness based on collected blocks.
        In future: use LLM to compress and normalize.
        """
        if not obj.get("decision_object"):
            obj["decision_object"] = self._derive_decision_object(obj)

        has_f = bool(obj.get("foundation", {}).get("facts_key"))
        has_c = bool(obj.get("context", {}).get("current_situation"))
        has_p = bool(obj.get("principle", {}).get("declared_purpose"))

        if has_f and has_c and has_p:
            obj["completeness"] = CompletenessLevel.COMPLETE
        elif has_f or has_c or has_p:
            obj["completeness"] = CompletenessLevel.PARTIAL
        else:
            obj["completeness"] = CompletenessLevel.INCOMPLETE

        # Notes
        stop_reason = state.get("stop_reason") or ""
        if stop_reason:
            self._append_note(obj, f"Stop reason: {stop_reason}")
        self._append_note(obj, f"Turns: {state.get('turns', 0)}")

        # V4.1.1: soft contradiction detection (non-invasive)
        try:
            obj["soft_contradictions"] = detect_soft_contradictions(obj)
            if obj.get("soft_contradictions"):
                self._append_note(obj, f"Soft contradictions: {len(obj['soft_contradictions'])}")
        except Exception:
            # Never block finalization on soft contradiction detection
            obj["soft_contradictions"] = []

    def _derive_decision_object(self, obj: DiscernmentObject) -> str:
        """
        Derive a clear decision_object:
        - If LLM available: produce a single-sentence normalized decision.
        - Else: fallback to original statement + theme tag.
        """
        base = (obj.get("original_statement") or "").strip()
        theme = obj.get("dominant_theme", Theme.SURVIVAL_STABILITY).value

        if self.llm is not None:
            try:
                ftxt = obj.get("foundation", {}).get("facts_key", "")
                ctxt = obj.get("context", {}).get("current_situation", "")
                ptxt = obj.get("principle", {}).get("declared_purpose", "")

                prompt = (
                    "Reformula en UNA sola frase clara el objeto de la decisión (decision_object).\n"
                    "Debe describir QUÉ se decide y, si aplica, la tensión central.\n"
                    "No moralices. No aconsejes.\n\n"
                    f"Tema dominante: {theme}\n"
                    f"Afirmación original: {base}\n"
                    f"Fundamento (texto): {ftxt}\n"
                    f"Contexto (texto): {ctxt}\n"
                    f"Principio (texto): {ptxt}\n\n"
                    "Salida: una sola frase.\n"
                )
                out = (self.llm.generate(prompt) or "").strip()
                if out:
                    return out
            except Exception:
                pass

        return f"{base} (theme={theme})"

    # -------------------------
    # Blocks defaults + inference helpers
    # -------------------------

    def _empty_foundation(self) -> FoundationBlock:
        return {"facts_key": "", "clarity": ClarityLevel.MEDIUM, "source": "user"}

    def _empty_context(self) -> ContextBlock:
        return {"current_situation": "", "time_horizon": TimeHorizon.UNKNOWN, "source": "user"}

    def _empty_principle(self) -> PrincipleBlock:
        return {"declared_purpose": "", "alignment": ClarityLevel.MEDIUM, "source": "user"}

    def _infer_clarity(self, txt: str) -> ClarityLevel:
        t = (txt or "").strip()
        if len(t) >= 60:
            return ClarityLevel.HIGH
        if len(t) >= 20:
            return ClarityLevel.MEDIUM
        return ClarityLevel.LOW

    def _infer_alignment(self, purpose: str) -> ClarityLevel:
        p = (purpose or "").strip().lower()
        if not p or "no lo se" in p or "no sé" in p:
            return ClarityLevel.LOW
        if len(p) >= 20:
            return ClarityLevel.MEDIUM
        return ClarityLevel.MEDIUM

    def _infer_time_horizon(self, txt: str) -> TimeHorizon:
        t = (txt or "").lower()
        if any(x in t for x in ["temporal", "por ahora", "corto plazo", "solo un tiempo", "es temporal"]):
            return TimeHorizon.SHORT
        if any(x in t for x in ["largo plazo", "permanente", "para siempre", "a largo plazo"]):
            return TimeHorizon.LONG
        return TimeHorizon.UNKNOWN

    # -------------------------
    # Small utilities
    # -------------------------

    def _append_note(self, obj: DiscernmentObject, note: str) -> None:
        obj["agent_notes"] = self._append_line(obj.get("agent_notes", ""), note)

    def _append_line(self, base: str, line: str) -> str:
        line = (line or "").strip()
        if not line:
            return base
        if not base:
            return line
        return base + "\n" + line

    def _all_text(self, obj: DiscernmentObject) -> str:
        parts = [
            obj.get("original_statement", ""),
            obj.get("foundation", {}).get("facts_key", ""),
            obj.get("context", {}).get("current_situation", ""),
            obj.get("principle", {}).get("declared_purpose", ""),
        ]
        return "\n".join([p for p in parts if p])

    def _merge_secondary(self, existing: List[Theme], add: Theme) -> List[Theme]:
        if add in existing:
            return existing
        return existing + [add]

    # -------------------------
    # Hard contradiction placeholder (optional)
    # -------------------------

    def _add_contradiction(
        self,
        obj: DiscernmentObject,
        description: str,
        axes: List[Axis],
        ctype: ContradictionType,
    ) -> None:
        contradictions: List[ContradictionItem] = obj.get("contradictions", [])
        contradictions.append(
            {
                "description": description,
                "axes_affected": axes,
                "type": ctype,
            }
        )
        obj["contradictions"] = contradictions
