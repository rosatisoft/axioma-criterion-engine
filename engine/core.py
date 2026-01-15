from dataclasses import dataclass
from typing import Callable, Tuple

from .states import Decision


@dataclass
class EvaluationResult:
    decision: Decision
    note: str


# Tipos de funciones que harán las preguntas (inyectables)
YesNoPrompter = Callable[[str], bool]
LevelPrompter = Callable[[str], str]
TextPrompter = Callable[[str], str]


def run_criterion_session(
    ask_yes_no: YesNoPrompter,
    ask_level: LevelPrompter,
    ask_text: TextPrompter,
) -> EvaluationResult:
    """
    Ejecuta una sesión completa del motor de criterio usando funciones de entrada
    proporcionadas (para permitir CLI, web, tests, etc.).

    Las preguntas están escritas directamente aquí por simplicidad.
    Más adelante se pueden extraer a engine/questions.py.
    """

    # 1. QUÉ – Claridad
    statement = ask_text(
        "Escribe la afirmación o decisión que quieres evaluar:"
    ).strip()

    clara = ask_yes_no("¿La afirmación te resulta clara tal como la escribiste?")
    if not clara:
        statement = ask_text(
            "Reformula la afirmación para que sea más clara:"
        ).strip()
        clara_2 = ask_yes_no("¿Ahora sí está clara para ti?")
        if not clara_2:
            return EvaluationResult(
                Decision.NO,
                "La afirmación sigue sin ser clara. Reformúlala mejor antes de decidir.",
            )

    # 2. REALIDAD – Verificabilidad (F)
    ver_ejemplo = ask_yes_no(
        "¿Puedes dar al menos un ejemplo real que respalde esta afirmación?"
    )
    ver_fuente = ask_yes_no(
        "¿Podrías verificarla en alguna fuente confiable (estudio, experto, dato)?"
    )

    if not (ver_ejemplo or ver_fuente):
        return EvaluationResult(
            Decision.POSPONER,
            "Trata esta afirmación como hipótesis/opinión, no como verdad operativa. "
            "No hay verificabilidad suficiente por ahora.",
        )

    # 3. ENTROPÍA – Riesgos / Costos (C)
    r_tiempo = ask_level(
        "Si actúas como si esto fuera verdad, el riesgo/costo en TIEMPO es"
    )
    r_dinero = ask_level(
        "El riesgo/costo en DINERO es"
    )
    r_vida = ask_level(
        "El riesgo/costo en SALUD/PAZ/RELACIONES es"
    )

    precaucion = (r_tiempo == "alto" or r_dinero == "alto" or r_vida == "alto")

    # 4. POR QUÉ – Fundamento interno
    razones = ask_text(
        "Escribe brevemente por qué crees que esta afirmación es verdadera:"
    ).strip()
    if len(razones) < 5:
        return EvaluationResult(
            Decision.POSPONER,
            "Fundamento débil: no expresaste razones claras. "
            "No tomes decisiones fuertes basadas solo en esto.",
        )

    contradice = ask_yes_no(
        "¿Alguna de tus razones contradice hechos sólidos que ya conoces?"
    )
    if contradice:
        return EvaluationResult(
            Decision.NO,
            "Hay contradicciones entre tus razones y hechos que conoces. "
            "La afirmación requiere revisión o corrección.",
        )

    # 5. PARA QUÉ – Propósito (P)
    proposito = ask_text(
        "¿Para qué quieres aceptar esta afirmación o tomar esta decisión?"
    ).strip()

    alineado = ask_yes_no(
        "¿Este propósito se alinea con tus valores y con la persona que quieres ser?"
    )
    if not alineado:
        return EvaluationResult(
            Decision.NO,
            "El propósito no se alinea con tus valores o identidad. "
            "No procede por ahora o requiere cambiar el propósito.",
        )

    # 6. PAZ INTERIOR
    paz = ask_yes_no(
        "Viendo los riesgos y el propósito, ¿sientes paz interior con esta decisión?"
    )
    if not paz:
        return EvaluationResult(
            Decision.POSPONER,
            "No hay paz con esta decisión; conviene esperar, buscar consejo "
            "o conseguir más información.",
        )

    # 7. DECISIÓN FINAL
    if precaucion:
        return EvaluationResult(
            Decision.ADELANTE_GRADUAL,
            "La afirmación es razonable, pero hay riesgos altos. "
            "Sigue adelante de forma gradual, con límites claros y monitoreo.",
        )
    else:
        return EvaluationResult(
            Decision.ADELANTE,
            "La afirmación es razonable, verificada y alineada contigo. "
            "Puedes seguir adelante con tranquilidad.",
        )
