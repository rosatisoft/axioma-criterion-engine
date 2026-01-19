from __future__ import annotations

import json

# Ajusta imports según tu repo (siguen el patrón de tu v4_1_interview_demo.py)
from axioma_criterion_engine.v4_1.engine_v4_1 import evaluate_discernment
from axioma_criterion_engine.v4_1.interview_agent_v4_1 import InterviewAgentV41
from axioma_criterion_engine.v4_1.llm_adapter import LLMClientAdapter

# Si ya tienes un cliente OpenAI real en tu proyecto, puedes conectarlo aquí.
# Por ahora lo dejamos opcional para que corra igual que tu demo actual.


def _pretty(title: str, payload: object) -> None:
    print(f"\n--- {title} ---")
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def main() -> None:
    print("=== V4.1.1 Engine Demo (Interview + Scoring) ===\n")

    # 1) Cliente LLM (opcional)
    # Si tienes un cliente real, ponlo aquí:
    #   client = build_openai_client()   (si lo implementaste)
    # o
    #   client = OpenAI(api_key=...)
    #
    # Si lo dejas None, el InterviewAgent corre en modo interactivo (como tu screenshot).
    client = None

    llm = LLMClientAdapter(client) if client is not None else None

    # 2) Entrevista -> DiscernmentObject
    agent = InterviewAgentV41(llm=llm)

    statement = input("Describe brevemente la afirmación o decisión:\n> ").strip()
    obj = agent.run(statement)

    _pretty("DISCERNMENT OBJECT (V4.1)", obj)

    # 3) Evaluación por engine (scoring + confidence + penalties)
    evaluation = evaluate_discernment(obj)

    _pretty("ENGINE EVALUATION (V4.1)", evaluation)

    # 4) Resumen rápido (humano)
    print("\n=== RESUMEN ===")
    ws = evaluation.get("weighted_score")
    conf = evaluation.get("confidence")
    risk = evaluation.get("risk_index")
    penalties = evaluation.get("penalties") or []
    notes = evaluation.get("notes", "")

    print(f"- Weighted score: {ws}")
    print(f"- Confidence:     {conf}")
    print(f"- Risk index:     {risk}")
    print(f"- Penalties:      {', '.join(penalties) if penalties else 'none'}")
    print(f"- Notes:          {notes if notes else 'none'}")


if __name__ == "__main__":
    main()
