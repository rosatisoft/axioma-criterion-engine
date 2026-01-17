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
from typing import Callable, Dict, List, Optional, Tuple

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
from .discernment_types import (
    ContextBlock,
    ContradictionItem,
    DeclaredRisks,
    DiscernmentObject,
    FoundationBlock,
    InterviewState,
    PrincipleBlock,
)


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
# Configuration
# -----------------------------

@dataclass(frozen=True)
class InterviewConfig:
    """
    Safety/usability constraints.
    - max_total_questions: hard cap for the interview.
    - max_questions_per_axis: hard cap per axis.
    - allow_single_reorientation: if True, can reorient once based on signals.
    """

    max_total_questions: int = 9
    max_questions_per_axis: int = 3
    allow_single_reorientation: bool = True


# -----------------------------
# Question bank (base)
# -----------------------------

Question = Tuple[str, Axis, str]  # (question_id, axis, question_text)


QUESTION_BANK: Dict[Theme, List[Question]] = {
    Theme.SURVIVAL_STABILITY: [
        ("SS_F_1", Axis.FOUNDATION, "¿Qué hecho concreto hace necesaria esta decisión ahora?"),
        ("SS_F_2", Axis.FOUNDATION, "¿Qué ocurriría realmente si no tomaras esta decisión?"),
        ("SS_F_3", Axis.FOUNDATION, "¿Esto es una necesidad comprobable o una percepción de urgencia?"),

        ("SS_C_1", Axis.CONTEXT, "¿Qué circunstancias actuales te colocan en esta situación?"),
        ("SS_C_2", Axis.CONTEXT, "¿Qué alternativas reales existen, aunque no sean ideales?"),
        ("SS_C_3", Axis.CONTEXT, "¿Esta decisión es temporal o te ata a largo plazo?"),

        ("SS_P_1", Axis.PRINCIPLE, "¿Qué estás preservando al tomar esta decisión?"),
        ("SS_P_2", Axis.PRINCIPLE, "¿Qué estarías sacrificando si la aceptas?"),
        ("SS_P_3", Axis.PRINCIPLE, "¿Esta decisión te acerca o te aleja de la persona que quieres ser?"),
    ],
    Theme.ETHICS_VALUES: [
        ("EV_F_1", Axis.FOUNDATION, "¿Qué parte de esta decisión consideras problemática?"),
        ("EV_F_2", Axis.FOUNDATION, "¿Qué hecho concreto te hace dudar de su corrección?"),
        ("EV_F_3", Axis.FOUNDATION, "¿Qué estás asumiendo como “normal” sin cuestionarlo?"),

        ("EV_C_1", Axis.CONTEXT, "¿Qué presión o beneficio hace atractiva esta opción?"),
        ("EV_C_2", Axis.CONTEXT, "¿Quiénes se verían afectados por esta decisión?"),
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
        config: Optional[InterviewConfig] = None,
    ) -> None:
        self.llm = llm
        self.user_input = user_input or (lambda prompt: input(prompt))
        self.config = config or InterviewConfig()

    # -------------------------
    # Entry point
    # -------------------------

    def run(self, original_statement: str) -> DiscernmentObject:
        """
        Run the guided interview and produce a DiscernmentObject.
        """
        original_statement = (original_statement or "").strip()
        if not original_statement:
            raise ValueError("original_statement must be non-empty")

        state: InterviewState = {
            "turns": 0,
            "asked": [],
            "reoriented": False,
        }

        # 1) Initial theme hypothesis (simple heuristic; can be replaced by LLM classification)
        theme = self._classify_theme_initial(original_statement)
        state["current_theme"] = theme

        # 2) Initialize a partial DiscernmentObject (incremental build)
        obj: DiscernmentObject = {
            "original_statement": original_statement,
            "dominant_theme": theme,
            "secondary_themes": [],
            "contradictions": [],
            "completeness": CompletenessLevel.PARTIAL,
            "agent_notes": "",
        }

        # 3) Ask questions, collect answers, possibly reorient once
        self._interview_loop(obj, state)

        # 4) Finalize derived fields (decision_object, completeness, notes)
        self._finalize_discernment_object(obj, state)

        return obj

    # -------------------------
    # Interview loop
    # -------------------------

    def _interview_loop(self, obj: DiscernmentObject, state: InterviewState) -> None:
        theme: Theme = obj["dominant_theme"]

        asked_per_axis: Dict[Axis, int] = {
            Axis.FOUNDATION: 0,
            Axis.CONTEXT: 0,
            Axis.PRINCIPLE: 0,
        }

        questions = QUESTION_BANK[theme]

        for qid, axis, qtext in questions:
            if self._should_stop(state, asked_per_axis):
                break

            if asked_per_axis[axis] >= self.config.max_questions_per_axis:
                continue

            # Ask the question
            answer = self._ask(qid, qtext, state)
            asked_per_axis[axis] += 1

            # Update DiscernmentObject with the new answer (axis-specific)
            self._apply_answer(obj, axis, answer)

            # After early answers, check signals (reorientation / contradictions)
            if self.config.allow_single_reorientation:
                self._detect_signals_and_maybe_reorient(obj, state)

                # If reoriented, restart question flow with the new theme (once)
                if state.get("reoriented") and obj["dominant_theme"] != theme:
                    self._append_note(obj, f"Reoriented theme: {theme.value} -> {obj['dominant_theme'].value}")
                    # Restart loop with new theme, preserving asked history
                    self._interview_loop_restart(obj, state, asked_per_axis)
                    return  # important: stop current loop after restart

        # Stop reason note
        if state.get("stop_reason"):
            self._append_note(obj, f"Stop reason: {state['stop_reason']}")

    def _interview_loop_restart(
        self,
        obj: DiscernmentObject,
        state: InterviewState,
        asked_per_axis: Dict[Axis, int],
    ) -> None:
        """
        Called once after reorientation. Adds at most one extra question per relevant axis.
        Uses the same stop criteria.
        """
        new_theme = obj["dominant_theme"]
        questions = QUESTION_BANK[new_theme]

        # Allow a small extension after reorientation: max +1 per axis (controlled)
        extra_cap_per_axis = 1
        used_extra: Dict[Axis, int] = {Axis.FOUNDATION: 0, Axis.CONTEXT: 0, Axis.PRINCIPLE: 0}

        for qid, axis, qtext in questions:
            if self._should_stop(state, asked_per_axis):
                break

            if used_extra[axis] >= extra_cap_per_axis:
                continue

            # Ask and apply
            answer = self._ask(qid, qtext, state)
            asked_per_axis[axis] += 1
            used_extra[axis] += 1
            self._apply_answer(obj, axis, answer)

        if state.get("stop_reason"):
            self._append_note(obj, f"Stop reason: {state['stop_reason']}")

    # -------------------------
    # Stop criteria
    # -------------------------

    def _should_stop(self, state: InterviewState, asked_per_axis: Dict[Axis, int]) -> bool:
        # Hard caps
        if state["turns"] >= self.config.max_total_questions:
            state["stop_reason"] = "max_total_questions"
            return True

        # If we already have at least 1 question per axis, we can stop (minimum completeness)
        if all(asked_per_axis[a] >= 1 for a in (Axis.FOUNDATION, Axis.CONTEXT, Axis.PRINCIPLE)):
            # We still allow continuing until caps, but can stop early if user indicates.
            # In skeleton: we stop at minimum completeness to keep MVP tight.
            state["stop_reason"] = "minimum_completeness_reached"
            return True

        return False

    # -------------------------
    # Asking / applying answers
    # -------------------------

    def _ask(self, qid: str, qtext: str, state: InterviewState) -> str:
        state["turns"] += 1
        state["asked"].append(qid)

        prompt = f"\n[{qid}] {qtext}\n> "
        answer = self.user_input(prompt).strip()
        return answer

    def _apply_answer(self, obj: DiscernmentObject, axis: Axis, answer: str) -> None:
        """
        MVP: Store raw answers into axis blocks as text.
        Later: LLM-assisted extraction to structured fields.
        """
        if not answer:
            # Keep silence as signal; do not force content.
            return

        if axis == Axis.FOUNDATION:
            block: FoundationBlock = obj.get("foundation", {})
            # For MVP we aggregate into facts_key; later can split.
            prior = block.get("facts_key", "")
            block["facts_key"] = (prior + "\n" if prior else "") + answer
            block.setdefault("clarity", ClarityLevel.MEDIUM)
            block.setdefault("source", AnswerSource.USER)
            obj["foundation"] = block

        elif axis == Axis.CONTEXT:
            block2: ContextBlock = obj.get("context", {})
            prior2 = block2.get("current_situation", "")
            block2["current_situation"] = (prior2 + "\n" if prior2 else "") + answer
            block2.setdefault("time_horizon", TimeHorizon.SHORT)
            block2.setdefault("source", AnswerSource.USER)
            obj["context"] = block2

        elif axis == Axis.PRINCIPLE:
            block3: PrincipleBlock = obj.get("principle", {})
            prior3 = block3.get("declared_purpose", "")
            block3["declared_purpose"] = (prior3 + "\n" if prior3 else "") + answer
            block3.setdefault("alignment", ClarityLevel.MEDIUM)
            block3.setdefault("source", AnswerSource.USER)
            obj["principle"] = block3

    # -------------------------
    # Theme classification (initial)
    # -------------------------

    def _classify_theme_initial(self, statement: str) -> Theme:
        """
        MVP heuristic classifier (replaceable by LLM classification).
        """
        s = statement.lower()

        ethics_markers = ["sé que está mal", "engaña", "ilegal", "fraude", "mentir", "corrup", "trampa", "ético"]
        pressure_markers = ["me obligan", "me piden", "presion", "ultimátum", "si no", "amenaz", "esperan que"]
        survival_markers = ["dinero", "trabajo", "renta", "deuda", "pagar", "urgente", "necesito", "ingresos"]

        if any(m in s for m in ethics_markers):
            return Theme.ETHICS_VALUES
        if any(m in s for m in pressure_markers):
            return Theme.EXTERNAL_PRESSURE
        if any(m in s for m in survival_markers):
            return Theme.SURVIVAL_STABILITY

        # Default: survival as most common base layer
        return Theme.SURVIVAL_STABILITY

    # -------------------------
    # Signal detection & reorientation (MVP)
    # -------------------------

    def _detect_signals_and_maybe_reorient(self, obj: DiscernmentObject, state: InterviewState) -> None:
        """
        MVP signal detection from accumulated text.
        In future: can use LLM to detect contradictions and thematic dominance.
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
        pressure_signals = ["me obligan", "me piden", "no quiero problemas", "si no hago", "esperan que", "amenaz"]
        if any(sig in text for sig in pressure_signals):
            if obj["dominant_theme"] != Theme.EXTERNAL_PRESSURE:
                obj["secondary_themes"] = self._merge_secondary(obj.get("secondary_themes", []), obj["dominant_theme"])
                obj["dominant_theme"] = Theme.EXTERNAL_PRESSURE
                state["reoriented"] = True
                return

        # 3) Contradiction placeholder (very simple)
        # Example: "no me afecta" and later "me preocupa" -> coherence contradiction
        if "no me afecta" in text and "me preocupa" in text:
            self._add_contradiction(
                obj,
                description="Possible internal inconsistency: 'no me afecta' vs 'me preocupa'.",
                axes=[Axis.CONTEXT, Axis.PRINCIPLE],
                ctype=ContradictionType.COHERENCE,
            )

    # -------------------------
    # Finalization
    # -------------------------

    def _finalize_discernment_object(self, obj: DiscernmentObject, state: InterviewState) -> None:
        """
        Sets decision_object and completeness based on collected blocks.
        In future: use LLM to compress and normalize.
        """
        # Decision object (MVP): derive from original statement + theme
        if not obj.get("decision_object"):
            obj["decision_object"] = self._derive_decision_object(obj)

        # Completeness: if we have at least some content per axis
        has_f = bool(obj.get("foundation", {}).get("facts_key"))
        has_c = bool(obj.get("context", {}).get("current_situation"))
        has_p = bool(obj.get("principle", {}).get("declared_purpose"))

        if has_f and has_c and has_p:
            obj["completeness"] = CompletenessLevel.COMPLETE
        elif has_f or has_c or has_p:
            obj["completeness"] = CompletenessLevel.PARTIAL
        else:
            obj["completeness"] = CompletenessLevel.INSUFFICIENT

        # Keep final note about turns
        self._append_note(obj, f"Turns: {state.get('turns', 0)}")

    def _derive_decision_object(self, obj: DiscernmentObject) -> str:
        base = obj.get("original_statement", "").strip()
        theme = obj.get("dominant_theme", Theme.SURVIVAL_STABILITY).value
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
