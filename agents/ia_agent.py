from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from core.basic_engine_v4 import CriterionEngineV4
from llm_client import LLMClient


@dataclass
class CriterionAgentResult:
    raw_engine_output: Dict[str, Any]
    narrative: str


class CriterionAgent:
    """
    Agente IA que integra:
    - Motor de Criterio V4 (estructura, F–C–P, riesgo…)
    - LLMClient (narrativa y recomendación en lenguaje natural)
    """

    def __init__(self, engine: CriterionEngineV4, llm_client: LLMClient) -> None:
        self.engine = engine
        self.llm = llm_client

    # ---------- Paso 1: aclarar afirmación ----------

    def _clarify_statement(self, statement: str) -> str:
        system = (
            "Eres un asistente que ayuda a clarificar decisiones para ser evaluadas "
            "con el Método Triaxial de Discernimiento (Fundamento–Contexto–Principio)."
        )

        prompt = f"""
Reformula la siguiente decisión en una frase clara, específica y neutra,
sin cambiar su sentido de fondo. Sólo devuelve UNA frase.

Decisión original:
\"\"\"{statement}\"\"\"
"""
        return self.llm.complete(prompt=prompt, system=system).strip()

    # ---------- Paso 2: construir entrada para el motor ----------

    def _build_engine_input(self, clarified_statement: str) -> Dict[str, Any]:
        return {
            "afirmacion": clarified_statement,
            "ejemplos_reales": True,
            "fuente_verificable": False,
            "riesgo_tiempo": "bajo",
            "riesgo_dinero": "bajo",
            "riesgo_salud": "bajo",
            "razones": "El usuario considera seriamente esta decisión en su contexto actual.",
            "metadata": {},
        }

    # ---------- Paso 3: generar narrativa con IA ----------

    def _narrate_result(self, statement: str, engine_output: Dict[str, Any]) -> str:
        system = (
            "Eres un agente de discernimiento basado en el Axioma del Absoluto "
            "y en el Método Triaxial de Discernimiento (Fundamento–Contexto–Principio). "
            "Tu objetivo es ser claro, honesto y prudente."
        )

        prompt = f"""
Afirmación evaluada:
\"\"\"{statement}\"\"\"

Resultado estructurado del Motor de Criterio (JSON):
```json
{engine_output}
