from __future__ import annotations

import os
import sys

# Añadimos la carpeta padre (axioma-criterion-engine) al sys.path
CURRENT_DIR = os.path.dirname(__file__)
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from core.basic_engine_v4 import CriterionEngineV4
from llm_client import LLMClient
from agents.ia_agent import CriterionAgent


def main() -> None:
    print("=== Agente de Discernimiento V4 (Axioma-Criterion-Engine IA) ===\n")

    try:
        afirmacion = input(
            "Describe brevemente la afirmación o decisión que quieres evaluar:\n> "
        )
    except EOFError:
        print("Entrada cancelada.")
        return

    afirmacion = afirmacion.strip()
    if not afirmacion:
        print("No se recibió ninguna afirmación. Saliendo.")
        return

    engine = CriterionEngineV4()
    llm = LLMClient()  # usa OPENAI_API_KEY del entorno
    agent = CriterionAgent(engine=engine, llm_client=llm)

    result = agent.evaluate(afirmacion)

    print("\n--- RESULTADO DEL MOTOR (estructura) ---")
    print(result.raw_engine_output)

    print("\n--- DICTAMEN DEL AGENTE (narrativa) ---\n")
    print(result.narrative)


if __name__ == "__main__":
    main()

# axioma_criterion_engine/examples/v4_ia_agent_demo.py

from __future__ import annotations

from core.basic_engine_v4 import CriterionEngineV4
from llm_client import LLMClient
from agents.ia_agent import CriterionAgent


def main() -> None:
    print("=== Agente de Discernimiento V4 (Axioma-Criterion-Engine IA) ===\n")

    afirmacion = input("Describe brevemente la afirmación o decisión que quieres evaluar:\n> ").strip()
    if not afirmacion:
        print("No se recibió ninguna afirmación. Saliendo.")
        return

    engine = CriterionEngineV4()
    llm = LLMClient()  # usa OPENAI_API_KEY del entorno
    agent = CriterionAgent(engine=engine, llm_client=llm)

    result = agent.evaluate(afirmacion)

    print("\n--- RESULTADO DEL MOTOR (estructura) ---")
    print(result.raw_engine_output)

    print("\n--- DICTAMEN DEL AGENTE (narrativa) ---\n")
    print(result.narrative)


if __name__ == "__main__":
    main()
