from __future__ import annotations

# V4.1 Interview Agent (V4.1.1 patched)
#
# Goal:
# - Guided interview to build a DiscernmentObject incrementally.
# - Theme selection -> axis questions -> stop criteria -> reorientation -> finalize object.
#
# Design choices:
# - Soft structure (TypedDict): supports dialectic freedom and partial completion.
# - Hard vocabulary (Enums): stable reference for themes/axes/levels.
# - Reorientation is evidence-driven (from early answers), controlled (no loops).
# - Stop criteria prevents endless interviews and preserves user autonomy.

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

from .discernment_enums import (
    Axis,
    ClarityLevel,
    CompletenessLevel,
    ContradictionType,
    Theme,
    TimeHorizon,
)
from .discernment_types import (
    ContextBlock,
    ContradictionItem,
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

Question = Tuple[str, Axis, str]  # (question_id, axis, question_text)

QUESTION_BANK: Dict[Theme, List[Question]] = {
    Theme.SURVIVAL_STABILITY: [
        ("SS_F_1", Axis.FOUNDATION, "¿Qué hecho concreto hace necesaria esta decisión ahora?"),
        ("SS_F_2", Axis.FOUNDATION, "¿Qué ocurriría realmente si no tomaras esta decisión?"),
        ("SS_F_3", Axis.FOUNDATION, "¿Esto es una necesidad comprobable o una percepción de urgencia?"),
        ("SS_F_4", Axis.FOUNDATION, "¿Qué lograrías realmente si tomas esta secisión?"),
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
        ("EV_F_3", Axis.FOUNDATION, "¿Qué parte exacta te hace dudar o te incomoda?"),
        ("EV_C_1", Axis.CONTEXT, "¿A quién afecta esta decisión y cómo (tú/otros)?"),
        ("EV_C_2", Axis.CONTEXT, "¿Qué alternativa ética existe, aunque sea menos cómoda?"),
        ("EV_C_3", Axis.CONTEXT, "¿Este contexto justifica la acción o solo la explica?"),
        ("EV_P_1", Axis.PRINCIPLE, "¿Qué valor se vería comprometido si actúas así?"),
        ("EV_P_2", Axis.PRINCIPLE, "¿Aceptarías esta decisión como regla general?"),
        ("EV_P_3", Axis.PRINCIPLE, "¿Cómo te explicarías esta decisión dentro de un año?"),
    ],
    Theme.EXTERNAL_PRESSURE: [
        ("EP_F_1", Axis.FOUNDATION, "¿Quién o qué está impulsando esta decisión?"),
        ("EP_F_2", Axis.FOUNDATION, "¿Qué ocurriría si decidieras no responder ahora?"),
        ("EP_F_3", Axis.FOUNDATION, "¿Esta decisión nace de ti o de una expectativa externa?"),
        ("EP_C_1", Axis.CONTEXT, "¿Qué tipo de presión estás experimentando (tiempo, miedo, aprobación)?"),
        ("EP_C_2", Axis.CONTEXT, "¿Esta presión es explícita o implícita?"),
        ("EP_C_3", Axis.CONTEXT, "¿Qué perderías realmente si no cumples esa expectativa?"),
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
        Run an interview for a given statement and return a DiscernmentObject.
        """
        state: InterviewState = {
            "turns": 0,
            "asked": [],
            "reoriented": False,
            "stop_reason": "",
        }

        statement = (statement or "").strip()
        if not statement:
            raise ValueError("statement must be non-empty")

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

        asked_per_axis: Dict[Axis, int] = {
            Axis.FOUNDATION: 0,
            Axis.CONTEXT: 0,
            Axis.PRINCIPLE: 0,
        }

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

            if self.config.allow_single_reorientation:
                prior_theme = obj["dominant_theme"]
                self._detect_signals_and_maybe_reorient(obj, state)

                if state.get("reoriented") and obj["dominant_theme"] != prior_theme:
                    self._append_note(
                        obj,
                        f"Reoriented theme: {prior_theme.value} -> {obj['dominant_theme'].value}",
                    )
                    # restart once with new theme
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
    # Asking + applying answers
    # -------------------------

    def _ask(self, qid: str, qtext: str, state: InterviewState) -> str:
        prompt = f"\n[{qid}] {qtext}\n> "
        ans = (self.user_input(prompt) or "").strip()
        state["asked"].append(qid)
        state["turns"] = int(state.get("turns", 0)) + 1
        return ans

    def _apply_answer(self, obj: DiscernmentObject, axis: Axis, answer: str) -> None:
        answer = (answer or "").strip()
        if not answer:
            return

        if axis == Axis.FOUNDATION:
            blk = obj.get("foundation", self._empty_foundation())
            blk["facts_key"] = (blk.get("facts_key", "") + "\n" if blk.get("facts_key") else "") + answer
            blk["clarity"] = self._infer_clarity(blk.get("facts_key", ""))
            obj["foundation"] = blk

        elif axis == Axis.CONTEXT:
            blk = obj.get("context", self._empty_context())
            blk["current_situation"] = (blk.get("current_situation", "") + "\n" if blk.get("current_situation") else "") + answer
            blk["time_horizon"] = self._infer_time_horizon(blk.get("current_situation", ""))
            obj["context"] = blk

        elif axis == Axis.PRINCIPLE:
            blk = obj.get("principle", self._empty_principle())
            blk["declared_purpose"] = (blk.get("declared_purpose", "") + "\n" if blk.get("declared_purpose") else "") + answer
            blk["alignment"] = self._infer_alignment(blk.get("declared_purpose", ""))
            obj["principle"] = blk

    # -------------------------
    # Stop criteria
    # -------------------------

    def _should_stop(self, obj: DiscernmentObject, state: InterviewState, asked_per_axis: Dict[Axis, int]) -> bool:
        if state.get("turns", 0) >= self.config.max_turns:
            state["stop_reason"] = "max_turns_reached"
            return True

        if self.config.stop_on_minimum_completeness:
            has_f = bool(obj.get("foundation", {}).get("facts_key"))
            has_c = bool(obj.get("context", {}).get("current_situation"))
            has_p = bool(obj.get("principle", {}).get("declared_purpose"))
            if has_f and has_c and has_p:
                state["stop_reason"] = "minimum_completeness_reached"
                return True

        return False

    # -------------------------
    # Theme detection + controlled reorientation
    # -------------------------

    def _classify_theme_initial(self, statement: str) -> Theme:
        s = (statement or "").lower()

        ethics_markers = ["está mal", "no es correcto", "engaña", "fraude", "mentir", "corrup", "trampa", "ilegal"]
        pressure_markers = ["me obligan", "me exigen", "amenaza", "ultimátum", "ultimatum", "me presionan"]
        survival_markers = ["dinero", "trabajo", "renta", "deuda", "pagar", "urgente", "necesito", "ingresos", "estabilidad"]

        if any(m in s for m in ethics_markers):
            return Theme.ETHICS_VALUES
        if any(m in s for m in pressure_markers):
            return Theme.EXTERNAL_PRESSURE
        if any(m in s for m in survival_markers):
            return Theme.SURVIVAL_STABILITY

        return Theme.SURVIVAL_STABILITY

    def _detect_signals_and_maybe_reorient(self, obj: DiscernmentObject, state: InterviewState) -> None:
        if state.get("reoriented"):
            return

        text = self._all_text(obj).lower()

        ethical_signals = ["sé que está mal", "no es correcto", "engaña", "fraude", "mentir", "corrup", "trampa"]
        if any(sig in text for sig in ethical_signals):
            if obj["dominant_theme"] != Theme.ETHICS_VALUES:
                obj["secondary_themes"] = self._merge_secondary(obj.get("secondary_themes", []), obj["dominant_theme"])
                obj["dominant_theme"] = Theme.ETHICS_VALUES
                state["reoriented"] = True
                return

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
            obj["completeness"] = CompletenessLevel.INSUFFICIENTE

        stop_reason = state.get("stop_reason") or ""
        if stop_reason:
            self._append_note(obj, f"Stop reason: {stop_reason}")
        self._append_note(obj, f"Turns: {state.get('turns', 0)}")

        # V4.1.1: soft contradiction detection (LLM + fallback)
        try:
            soft = detect_soft_contradictions(obj, llm=self.llm)
            obj["soft_contradictions"] = soft  # opcional: campo extra
            if soft:
                obj["contradictions"] = (obj.get("contradictions") or []) + soft
                self._append_note(obj, f"Soft contradictions: {len(soft)}")
        except Exception:
            # Never block finalization on soft contradiction detection
            obj["soft_contradictions"] = []

        # V4.1.2: risk pattern detection (determinista)
        try:
            from .risk_pattern_detector import detect_risk_patterns
            risk_pack = detect_risk_patterns(obj)
            obj["risk_signals"] = risk_pack.get("signals", [])
            obj["risk_delta"] = risk_pack.get("risk_delta", 0.0)
            obj["missing_context_count"] = risk_pack.get("missing_context_count", 0)
            if obj["risk_signals"]:
                self._append_note(obj, f"Risk signals: {len(obj['risk_signals'])}")
        except Exception:
            obj["risk_signals"] = []
            obj["risk_delta"] = 0.0
            obj["missing_context_count"] = 0

    def _derive_decision_object(self, obj: DiscernmentObject) -> str:
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
    # Utilities
    # -------------------------

    def _append_note(self, obj: DiscernmentObject, note: str) -> None:
        prior = obj.get("agent_notes", "")
        obj["agent_notes"] = (prior + "\n" if prior else "") + note

    def _all_text(self, obj: DiscernmentObject) -> str:
        parts: List[str] = []
        parts.append(obj.get("original_statement", ""))

        f = obj.get("foundation", {})
        c = obj.get("context", {})
        p = obj.get("principle", {})

        parts.append(f.get("facts_key", ""))
        parts.append(c.get("current_situation", ""))
        parts.append(p.get("declared_purpose", ""))

        return "\n".join([x for x in parts if x])

    def _merge_secondary(self, existing: List[Theme], add: Theme) -> List[Theme]:
        if add in existing:
            return existing
        return existing + [add]

    def _add_contradiction(self, obj: DiscernmentObject, description: str, axes: List[Axis], ctype: ContradictionType) -> None:
        contradictions: List[ContradictionItem] = obj.get("contradictions", [])
        contradictions.append(
            {
                "description": description,
                "axes_affected": axes,
                "type": ctype,
            }
        )
        obj["contradictions"] = contradictions

    # -------------------------
    # Blocks defaults + inference helpers
    # -------------------------

    def _empty_foundation(self) -> FoundationBlock:
        return {"facts_key": "", "clarity": ClarityLevel.MEDIUM, "source": "user"}

    def _empty_context(self) -> ContextBlock:
        # IMPORTANT: TimeHorizon has only SHORT/MEDIUM/LONG (no UNKNOWN)
        return {"current_situation": "", "time_horizon": TimeHorizon.MEDIUM, "source": "user"}

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
        return TimeHorizon.MEDIUM



