from __future__ import annotations

from enum import Enum


class SoftContradictionAction(str, Enum):
    NOTE_ONLY = "note_only"               # registrar y seguir
    REFRAME = "reframe"                   # reescribir la afirmación en forma coherente
    ASK_FOLLOWUP = "ask_followup"         # agregar 1-2 preguntas de precisión
    LOWER_CONFIDENCE = "lower_confidence" # reducir certeza del dictamen/eje
    STOP_AND_REFINE = "stop_and_refine"   # parar y pedir definición/ajuste antes de seguir
