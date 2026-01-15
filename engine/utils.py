"""
Funciones auxiliares para el motor de criterio.
Por ahora se mantiene mínimo.
"""


def normalize_level(value: str) -> str:
    """
    Normaliza una entrada de nivel de riesgo/costo a 'bajo', 'medio' o 'alto'.

    Ejemplos de entrada aceptada:
    - 'b', 'B', 'bajo', 'BAJO'
    - 'm', 'medio', 'M'
    - 'a', 'alto', 'ALTO'

    Si no se reconoce, se devuelve la cadena en minúsculas tal cual.
    """
    v = value.strip().lower()
    if v in ("b", "ba", "bajo"):
        return "bajo"
    if v in ("m", "me", "medio"):
        return "medio"
    if v in ("a", "al", "alto"):
        return "alto"
    return v
