# axioma_criterion_engine/v4_1/risk_patterns_v4_1.py
from __future__ import annotations

from typing import Dict, List, Literal, TypedDict

RiskLevelStr = Literal["low", "medium", "high"]
DomainStr = Literal["relationships", "money_work", "health_care"]

class RiskPattern(TypedDict, total=False):
    id: str
    domain: DomainStr
    title: str

    # Frases gatillo (matching simple, sin LLM)
    trigger_phrases: List[str]

    # Lo que el motor reporta (sin juicio)
    observed_risks: List[str]

    # Variables ocultas (lo que baja confianza si falta)
    missing_critical_data: List[str]

    # Preguntas sugeridas (sin empujar una respuesta)
    followup_questions: List[str]

    # Severidad base del patrón (no “veredicto”, solo riesgo agregado)
    severity: RiskLevelStr


RISK_PATTERNS_V41: List[RiskPattern] = [
    # -----------------------------
    # RELATIONSHIPS / FAMILY
    # -----------------------------
    {
        "id": "REL_AGE_GAP",
        "domain": "relationships",
        "title": "Diferencia de edad significativa (pareja)",
        "trigger_phrases": [
            "novia mucho mas joven",
            "pareja mucho mas joven",
            "una novia mas joven",
            "una pareja mas joven",
            "pareja mucho menor",
            "la edad es solo un numero",
        ],
        "observed_risks": [
            "Posible asimetría de poder (económica, emocional o social) si existen dependencias.",
            "Mayor probabilidad de incompatibilidad por etapas de vida (proyectos, energía, fertilidad, retiro).",
            "Riesgo de aislamiento social si los círculos de pares no se integran.",
        ],
        "missing_critical_data": [
            "Edades específicas (no es igual 18–35 que 40–57).",
            "Nivel de independencia financiera de ambas partes.",
            "Calidad de consentimiento mutuo y expectativas explícitas.",
            "Patrones previos de relación de la parte mayor/menor.",
            "Contexto cultural y red de apoyo.",
        ],
        "followup_questions": [
            "¿Qué edades tienen ambos (aprox.)?",
            "¿Hay dependencia económica o de vivienda entre ustedes?",
            "¿Qué esperan ambos en 6–12 meses (exclusividad, convivencia, hijos, etc.)?",
            "¿Cómo reaccionan ambos ante límites y autonomía?",
        ],
        "severity": "medium",
    },

    {
        "id": "REL_BABY_SAVE_REL",
        "domain": "relationships",
        "title": "“Un bebé salvará la relación”",
        "trigger_phrases": [
            "un bebe salvara nuestra relacion",
            "tener un bebe para arreglar la relacion",
            "un hijo nos unira",
        ],
        "observed_risks": [
            "Incremento drástico del estrés y carga logística en el primer año.",
            "Disminución de satisfacción marital reportada con frecuencia en transición a paternidad.",
            "Riesgo de conflicto posparto por distribución de tareas y expectativas.",
        ],
        "missing_critical_data": [
            "Calidad actual de comunicación y resolución de conflictos.",
            "Distribución realista de tareas y apoyo familiar.",
            "Estado financiero y estabilidad laboral.",
            "Salud mental/posparto y red de apoyo.",
        ],
        "followup_questions": [
            "¿Cómo resuelven hoy los conflictos (ejemplos reales)?",
            "¿Cómo se repartirían tareas y noches sin dormir?",
            "¿Con qué apoyo real cuentan (familia/recursos)?",
            "¿La relación es estable antes del embarazo?",
        ],
        "severity": "high",
    },

    {
        "id": "REL_JEALOUS_LOVE",
        "domain": "relationships",
        "title": "“Es celoso/a porque me quiere”",
        "trigger_phrases": [
            "es celoso porque me quiere",
            "es celosa porque me quiere",
            "me cela porque me ama",
        ],
        "observed_risks": [
            "Escalada hacia control coercitivo e invasión de privacidad.",
            "Aislamiento social progresivo.",
            "Mayor riesgo de violencia psicológica o física si hay patrones de control.",
        ],
        "missing_critical_data": [
            "Frecuencia e intensidad de episodios.",
            "Reacción ante límites/autonomía.",
            "Antecedentes de violencia o control.",
            "Red de apoyo y seguridad personal.",
        ],
        "followup_questions": [
            "¿Qué conductas específicas ocurren (revisar teléfono, impedir salidas, amenazas)?",
            "¿Cómo responde cuando pones límites claros?",
            "¿Ha habido agresión verbal o física?",
        ],
        "severity": "high",
    },

    # -----------------------------
    # MONEY / WORK
    # -----------------------------
    {
        "id": "MNY_MLM",
        "domain": "money_work",
        "title": "Entrar a redes de mercadeo (MLM) como independencia financiera",
        "trigger_phrases": [
            "redes de mercadeo",
            "mlm",
            "marketing multinivel",
            "ser mi propio jefe en redes",
        ],
        "observed_risks": [
            "Pérdida financiera frecuente por estructura de incentivos.",
            "Conflicto/alienación de círculo social por venta agresiva.",
            "Sesgo de supervivencia: casos visibles no representan el promedio.",
        ],
        "missing_critical_data": [
            "Estructura real de ingresos (venta vs reclutamiento).",
            "Costos fijos (kits, eventos, inventario).",
            "Saturación del mercado local y tasa de rotación.",
            "Políticas de devolución y transparencia contractual.",
        ],
        "followup_questions": [
            "¿De dónde viene el ingreso principal (producto o reclutamiento)?",
            "¿Cuánto debes invertir mensual obligatoriamente?",
            "¿Cuántos vendedores ya existen en tu zona?",
            "¿Hay contrato y políticas de devolución claras?",
        ],
        "severity": "high",
    },

    {
        "id": "MNY_QUIT_NO_PLAN",
        "domain": "money_work",
        "title": "Renunciar sin empleo/plan firmado",
        "trigger_phrases": [
            "renunciar sin tener otro empleo",
            "voy a renunciar mañana",
            "dejo el trabajo sin plan",
            "sin plan b",
        ],
        "observed_risks": [
            "Desempleo prolongado y presión financiera.",
            "Aceptar ofertas inferiores por urgencia.",
            "Decisiones subóptimas por estrés (valle de la muerte personal).",
        ],
        "missing_critical_data": [
            "Meses de ahorros líquidos (runway).",
            "Demanda real del sector y tiempos promedio de contratación.",
            "Red de contactos y plan de búsqueda.",
            "Gastos fijos mensuales no negociables.",
        ],
        "followup_questions": [
            "¿Cuántos meses puedes cubrir tus gastos sin ingresos?",
            "¿Cuál es tu plan de búsqueda (fechas, contactos, portafolio)?",
            "¿Qué gastos fijos no puedes reducir?",
        ],
        "severity": "medium",
    },

    {
        "id": "MNY_FOMO_INVEST",
        "domain": "money_work",
        "title": "Invertir por tendencia viral (FOMO) en cripto/acciones",
        "trigger_phrases": [
            "invertir por tendencia",
            "porque esta subiendo",
            "me voy a meter a cripto",
            "por tiktok",
            "por viral",
        ],
        "observed_risks": [
            "Compra en máximos históricos por FOMO y venta en pánico.",
            "Volatilidad alta y pérdida rápida de capital.",
            "Riesgo de fraude si la fuente no es verificable.",
        ],
        "missing_critical_data": [
            "Horizonte temporal real (días/meses/años).",
            "Tolerancia al riesgo y tamaño de posición.",
            "Diversificación y plan de salida.",
            "Conocimiento del activo y fuente de información.",
        ],
        "followup_questions": [
            "¿Cuánto capital es (porcentaje de tus ahorros)?",
            "¿Cuál es tu horizonte (3 meses vs 3 años)?",
            "¿Cuál es tu plan de salida si baja 20–40%?",
        ],
        "severity": "high",
    },

    # -----------------------------
    # HEALTH / CARE
    # -----------------------------
    {
        "id": "HLT_SLEEP_4H",
        "domain": "health_care",
        "title": "“Dormir 4 horas es suficiente”",
        "trigger_phrases": [
            "dormir 4 horas",
            "duermo 4 horas",
            "con 4 horas tengo",
        ],
        "observed_risks": [
            "Deterioro cognitivo acumulativo y reducción de rendimiento.",
            "Desregulación emocional e inmunológica.",
            "Riesgo cardiovascular aumentado en déficit crónico de sueño.",
        ],
        "missing_critical_data": [
            "Edad y demandas diarias (trabajo, conducción, etc.).",
            "Calidad del sueño (interrupciones, REM/profundo).",
            "Microsueños diurnos o somnolencia.",
            "Uso de estimulantes (café, energizantes, fármacos).",
        ],
        "followup_questions": [
            "¿Cuántos días a la semana duermes 4 horas?",
            "¿Te quedas dormido/a de día o al manejar?",
            "¿Te despiertas descansado/a o cansado/a?",
        ],
        "severity": "high",
    },

    {
        "id": "HLT_ALCOHOL_SLEEP",
        "domain": "health_care",
        "title": "Alcohol para dormir mejor",
        "trigger_phrases": [
            "tomo alcohol para dormir",
            "una copa para dormir",
            "me ayuda a dormir el alcohol",
        ],
        "observed_risks": [
            "Fragmentación del sueño y reducción de sueño reparador.",
            "Tolerancia progresiva y riesgo de dependencia.",
            "Aumento de ansiedad basal a mediano plazo.",
        ],
        "missing_critical_data": [
            "Cantidad y frecuencia semanal.",
            "Ansiedad o insomnio subyacente.",
            "Calidad del descanso (objetiva vs subjetiva).",
            "Interacciones con medicamentos.",
        ],
        "followup_questions": [
            "¿Cuántos días por semana lo haces y cuánto tomas?",
            "¿Qué pasa si no bebes (te cuesta conciliar, despiertas)?",
            "¿Hay ansiedad o estrés sostenido detrás?",
        ],
        "severity": "high",
    },

    {
        "id": "HLT_IGNORE_PAIN",
        "domain": "health_care",
        "title": "Ignorar dolor crónico (“ya se pasará”)",
        "trigger_phrases": [
            "ya se pasara",
            "ignorar el dolor",
            "dolor persistente normal",
        ],
        "observed_risks": [
            "Cronificación de lesiones y compensaciones biomecánicas.",
            "Riesgo de discapacidad futura por retraso de diagnóstico.",
        ],
        "missing_critical_data": [
            "Duración del dolor (semanas/meses).",
            "Intensidad y progresión.",
            "Síntomas asociados (fiebre, debilidad, pérdida de peso, hormigueo).",
            "Historia clínica y factores de riesgo.",
        ],
        "followup_questions": [
            "¿Desde cuándo empezó y ha ido empeorando?",
            "¿Dónde duele exactamente y qué lo dispara/mejora?",
            "¿Hay síntomas asociados (fiebre, adormecimiento, debilidad)?",
        ],
        "severity": "medium",
    },
]
