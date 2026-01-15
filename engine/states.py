from enum import Enum, auto


class Decision(Enum):
    """
    Estados de salida del motor de criterio.

    NO               -> La afirmación/decisión no debe usarse como base operativa.
    POSPONER         -> Aún no hay fundamento suficiente; conviene esperar.
    ADELANTE_GRADUAL -> Se puede avanzar, pero con cautela y pasos pequeños.
    ADELANTE         -> Adelante con tranquilidad; la decisión es razonable.
    """
    NO = auto()
    POSPONER = auto()
    ADELANTE_GRADUAL = auto()
    ADELANTE = auto()
