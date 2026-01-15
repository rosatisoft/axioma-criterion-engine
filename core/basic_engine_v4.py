# axioma_criterion_engine/core/basic_engine_v4.py

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, Literal, Optional


RiesgoNivel = Literal["bajo", "medio", "alto"]


RISK_MAP: Dict[RiesgoNivel, float] = {
    "bajo": 0.8,
    "medio": 0.5,
    "alto": 0.2,
}


@dataclass
class CriterionInputV4:
    """
    Entrada mínima para evaluar una afirmación con el Motor de Criterio V4.
    Puedes extenderla después según tu v3.
    """
    afirmacion: str
    ejemplos_reales: bool
    fuente_verificable: bool
    riesgo_tiempo: RiesgoNivel
    riesgo_dinero: RiesgoNivel
    riesgo_salud: RiesgoNivel
    razones: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class CriterionScoresV4:
    """
    Puntajes triaxiales simplificados.
    Ajusta la fórmula interna a tu método triaxial real.
    """
    fundamento: float
    contexto: float
    principio: float
    riesgo_global: float


@dataclass
class CriterionResultV4:
    """
    Resultado completo del Motor de Criterio V4.
    """
    input: CriterionInputV4
    scores: CriterionScoresV4
    notas: str = ""  # para textos breves o comentarios del motor

    def to_dict(self) -> Dict[str, Any]:
        return {
            "input": asdict(self.input),
            "scores": asdict(self.scores),
            "notas": self.notas,
        }


class CriterionEngineV4:
    """
    Motor de Criterio V4:
    - Tiene modo programático (evaluate_non_interactive).
    - Puede tener modo interactivo (CLI) si lo necesitas.
    """

    def __init__(self) -> None:
        # Aquí podrías cargar config, pesos, etc.
        pass

    # ---------- API PRINCIPAL (USO CON AGENTES IA) ----------

    def evaluate_non_interactive(
        self,
        afirmacion: str,
        ejemplos_reales: bool,
        fuente_verificable: bool,
        riesgo_tiempo: RiesgoNivel,
        riesgo_dinero: RiesgoNivel,
        riesgo_salud: RiesgoNivel,
        razones: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Evaluación programática: recibe parámetros simples, devuelve dict JSON-friendly.
        Esta es la firma que vamos a usar desde el IA Agent.
        """

        criterion_input = CriterionInputV4(
            afirmacion=afirmacion.strip(),
            ejemplos_reales=ejemplos_reales,
            fuente_verificable=fuente_verificable,
            riesgo_tiempo=riesgo_tiempo,
            riesgo_dinero=riesgo_dinero,
            riesgo_salud=riesgo_salud,
            razones=razones.strip(),
            metadata=metadata or {},
        )

        scores = self._calcular_scores(criterion_input)

        result = CriterionResultV4(
            input=criterion_input,
            scores=scores,
            notas="V4: evaluación básica generada por el Motor de Criterio.",
        )

        return result.to_dict()

    # ---------- LÓGICA INTERNA DEL MOTOR ----------

    def _calcular_scores(self, data: CriterionInputV4) -> CriterionScoresV4:
        """
        Aquí va la lógica interna del método triaxial.
        Por ahora implementamos una fórmula prudente y sencilla que luego puedes refinar.
        """

        # 1) Fundamento
        #    – ejemplos_reales y fuente_verificable incrementan el fundamento.
        fundamento_base = 0.4
        if data.ejemplos_reales:
            fundamento_base += 0.25
        if data.fuente_verificable:
            fundamento_base += 0.25

        fundamento = max(0.0, min(1.0, fundamento_base))

        # 2) Riesgos → riesgo_global
        r_t = RISK_MAP.get(data.riesgo_tiempo, 0.5)
        r_d = RISK_MAP.get(data.riesgo_dinero, 0.5)
        r_s = RISK_MAP.get(data.riesgo_salud, 0.5)
        riesgo_global = (r_t + r_d + r_s) / 3.0  # promedio

        # 3) Contexto (muy simple por ahora)
        #    – si el fundamento es alto pero el riesgo también, contexto baja un poco.
        if fundamento >= 0.7 and riesgo_global < 0.5:
            contexto = 0.8
        elif fundamento < 0.4 and riesgo_global < 0.5:
            contexto = 0.5
        else:
            contexto = 0.6

        # 4) Principio (para qué) – por ahora lo dejamos como armonización de ambos
        principio = (fundamento * 0.5) + (riesgo_global * 0.3) + (contexto * 0.2)

        return CriterionScoresV4(
            fundamento=round(fundamento, 3),
            contexto=round(contexto, 3),
            principio=round(principio, 3),
            riesgo_global=round(riesgo_global, 3),
        )

    # ---------- MODO INTERACTIVO OPCIONAL (CLI) ----------

    def evaluate_interactive(self) -> Dict[str, Any]:
        """
        Versión interactiva por consola, reusando la misma lógica interna.
        Puedes llamarla desde un CLI tipo `python -m cli.v4_main`.
        """
        print("=== Motor de Criterio V4 (Interactivo) ===\n")

        afirmacion = input("Escribe la afirmación o decisión que quieres evaluar:\n> ").strip()

        ejemplos_reales = self._ask_yes_no(
            "¿Puedes dar al menos un ejemplo real que respalde esta afirmación? (s/n): "
        )
        fuente_verificable = self._ask_yes_no(
            "¿Podrías verificarla en alguna fuente confiable (estudio, experto, dato)? (s/n): "
        )

        riesgo_tiempo = self._ask_riesgo("Si actúas como si esto fuera verdad, el riesgo/costo en TIEMPO es (bajo/medio/alto): ")
        riesgo_dinero = self._ask_riesgo("El riesgo/costo en DINERO es (bajo/medio/alto): ")
        riesgo_salud = self._ask_riesgo("El riesgo/costo en SALUD/PAZ/RELACIONES es (bajo/medio/alto): ")

        razones = input("Escribe brevemente por qué crees que esta afirmación es verdadera:\n> ").strip()

        return self.evaluate_non_interactive(
            afirmacion=afirmacion,
            ejemplos_reales=ejemplos_reales,
            fuente_verificable=fuente_verificable,
            riesgo_tiempo=riesgo_tiempo,
            riesgo_dinero=riesgo_dinero,
            riesgo_salud=riesgo_salud,
            razones=razones,
        )

    # ---------- HELPERS INTERACTIVOS ----------

    def _ask_yes_no(self, prompt: str) -> bool:
        while True:
            ans = input(prompt).strip().lower()
            if ans in ("s", "si", "sí", "y", "yes"):
                return True
            if ans in ("n", "no"):
                return False
            print("Por favor responde con 's' o 'n'.")

    def _ask_riesgo(self, prompt: str) -> RiesgoNivel:
        while True:
            ans = input(prompt).strip().lower()
            if ans in ("bajo", "medio", "alto"):
                return ans  # type: ignore[return-value]
            print("Por favor responde 'bajo', 'medio' o 'alto'.")
