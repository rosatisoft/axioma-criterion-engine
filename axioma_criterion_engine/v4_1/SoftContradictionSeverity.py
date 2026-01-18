from __future__ import annotations

from enum import Enum


class SoftContradictionSeverity(str, Enum):
    LOW = "low"         # leve: solo baja certeza
    MEDIUM = "medium"   # requiere reframe o 1 pregunta extra
    HIGH = "high"       # reframe + preguntas adicionales o detener por incoherencia
