import unittest

from engine.core import run_criterion_session
from engine.states import Decision


class TestCriterionEngine(unittest.TestCase):
    def test_decision_adelante(self):
        """
        Simula una sesión en la que todo está verificado, con riesgos moderados,
        buenas razones, propósito alineado y paz interior.
        Debería dar ADELANTE.
        """

        answers_yes_no = iter([
            # claridad
            True,  # afirmación clara
            # realidad
            True,   # ejemplo real
            False,  # fuente confiable (no necesaria si hay ejemplo)
            # contradicciones
            False,  # ¿contradice hechos? -> no
            # alineación de valores
            True,
            # paz interior
            True,
        ])

        answers_level = iter([
            "bajo",   # tiempo
            "medio",  # dinero
            "bajo",   # vida
        ])

        answers_text = iter([
            "Debo caminar 30 minutos diarios.",
            "Debo caminar 30 minutos diarios.",  # reformulación hipotética (no usada)
            "Porque es una recomendación médica y he visto mejoras en otros.",
            "Para mejorar mi salud y tener más energía.",
        ])

        def ask_yes_no(_prompt: str) -> bool:
            return next(answers_yes_no)

        def ask_level(_prompt: str) -> str:
            return next(answers_level)

        def ask_text(_prompt: str) -> str:
            return next(answers_text)

        result = run_criterion_session(ask_yes_no, ask_level, ask_text)
        self.assertEqual(result.decision, Decision.ADELANTE)

    def test_decision_posponer_por_falta_de_fundamento(self):
        """
        Simula una sesión donde hay cierta verificabilidad,
        pero el usuario no expresa razones claras.
        Debería dar POSPONER.
        """

        answers_yes_no = iter([
            True,   # claridad
            True,   # ejemplo real
            False,  # fuente confiable
        ])

        answers_level = iter([
            "bajo",   # tiempo
            "bajo",   # dinero
            "bajo",   # vida
        ])

        answers_text = iter([
            "Debo invertir todos mis ahorros en esta oportunidad.",
            "x",  # razones muy débiles
        ])

        def ask_yes_no(_prompt: str) -> bool:
            return next(answers_yes_no)

        def ask_level(_prompt: str) -> str:
            return next(answers_level)

        def ask_text(_prompt: str) -> str:
            return next(answers_text)

        result = run_criterion_session(ask_yes_no, ask_level, ask_text)
        self.assertEqual(result.decision, Decision.POSPONER)


if __name__ == "__main__":
    unittest.main()
