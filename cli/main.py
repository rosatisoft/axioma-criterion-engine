from engine.core import run_criterion_session
from engine.utils import normalize_level
from engine.states import Decision


def ask_yes_no(prompt: str) -> bool:
    while True:
        r = input(prompt + " (s/n): ").strip().lower()
        if r in ("s", "n"):
            return r == "s"
        print("Responde 's' o 'n' por favor.")


def ask_level(prompt: str) -> str:
    while True:
        r = input(prompt + " (bajo/medio/alto): ")
        nivel = normalize_level(r)
        if nivel in ("bajo", "medio", "alto"):
            return nivel
        print("Responde 'bajo', 'medio' o 'alto' por favor.")


def ask_text(prompt: str) -> str:
    return input(prompt + "\n> ")


def main():
    print("=== Motor de Criterio Básico (F–C–P / QUÉ–POR QUÉ–PARA QUÉ) ===\n")
    result = run_criterion_session(ask_yes_no, ask_level, ask_text)

    print("\n=== RESULTADO DEL CRITERIO ===")
    print("DECISIÓN:", result.decision.name)
    print("NOTA:", result.note)


if __name__ == "__main__":
    main()
