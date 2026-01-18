from __future__ import annotations

import json

# Ajusta estos imports según tu repo
from axioma_criterion_engine.v4_1.interview_agent_v4_1 import InterviewAgentV41
from axioma_criterion_engine.v4_1.llm_adapter import LLMClientAdapter

# Importa tu LLMClient real (ajusta ruta/nombre)
# from axioma_criterion_engine.core.llm_client import LLMClient
# o donde lo tengas:
# from core.llm_client import LLMClient


def main() -> None:
    print("=== V4.1 Interview Demo (Discernment Builder) ===\n")

    # 1) Instancia tu cliente real (ajusta esto)
    # client = LLMClient(...)
    client = None  # <-- por ahora, para correr sin LLM

    llm = LLMClientAdapter(client) if client is not None else None

    agent = InterviewAgentV41(llm=llm)

    statement = input("Describe brevemente la afirmación o decisión:\n> ").strip()
    obj = agent.run(statement)

    print("\n--- DISCERNMENT OBJECT (V4.1) ---")
    print(json.dumps(obj, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
