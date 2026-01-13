# Diagrama de flujo – Criterio básico F–C–P

```mermaid
flowchart TD
  A[Inicio: Afirmación / Decisión] --> B[QUÉ<br/>¿Qué se está afirmando exactamente?]

  B -->|No está claro| B1[Reformular: definir términos<br/>y/o dividir en partes] --> B
  B -->|Está claro| C[REALIDAD (F):<br/>¿Puedo verificarlo en hechos / ejemplos / fuentes?]

  C -->|No| C1[No verificable por ahora<br/>Tratar como hipótesis / opinión,<br/>no como verdad operativa] --> FIN
  C -->|Sí| D[ENTROPÍA RÁPIDA (C):<br/>¿Hay riesgos o costos grandes evidentes?]

  D -->|Sí| D1[Marcar como 'Precaución'<br/>Anotar qué puede salir mal] --> E
  D -->|No| E[POR QUÉ (Fundamento interno):<br/>¿Por qué digo / creo / afirmo esto?]

  E --> F[¿Tengo razones y/o evidencia concretas?]

  F -->|No| F1[Fundamento débil<br/>Evitar decisiones fuertes basadas en esto] --> FIN
  F -->|Sí| G[¿Las razones son coherentes<br/>y no contradicen hechos sólidos?]

  G -->|No| G1[Inconsistencia detectada<br/>Ajustar la afirmación o descartarla] --> FIN
  G -->|Sí| H[PARA QUÉ (Propósito):<br/>¿Para qué quiero usar / aceptar esta afirmación?]

  H --> I[¿Se alinea con mis valores<br/>y con quién quiero ser?]

  I -->|No| I1[No procede por ahora<br/>o requiere cambiar el propósito] --> FIN
  I -->|Sí| J[¿Tengo paz interior<br/>al decidir con base en esto?]

  J -->|No| J1[Posponer<br/>Buscar consejo / más información] --> FIN
  J -->|Sí| K[DECISIÓN BASE: Adelante]


*(nota: cuando lo uses, asegúrate de que el bloque ```mermaid esté bien cerrado en tu editor)*

---

### `FLOW/mermaid/ciclo-evolutivo.md`

```markdown
# Diagrama – Ciclo evolutivo humano–IA–criterio

```mermaid
flowchart LR
  N[Niño sin criterio propio] --> A[Adulto sin formación en criterio]
  A --> E[Errores repetidos en decisiones]
  E --> M[Busca ayuda externa (autoridades, gurús, sistemas)]
  M --> IA_S[IA sin criterio<br/>(modelo estadístico)]
  IA_S --> R[Respuestas rápidas pero superficiales]

  R --> T[Tomar decisiones sin filtro<br/>ni escala de valores]
  T --> C[Consecuencias negativas<br/>(entropía alta)]
  C --> Q[Pregunta existencial:<br/>¿Cómo decido bien?]

  Q --> K[Motor de Criterio<br/>F–C–P + QUÉ/POR QUÉ/PARA QUÉ]
  K --> IA_C[IA con criterio guiado<br/>(hace preguntas antes de responder)]
  IA_C --> H[Humano con diálogo interior ampliado]
  H --> B[Mejor toma de decisiones<br/>con responsabilidad y verdad]

  B --> N2[Adulto que transmite criterio<br/>a nuevas generaciones]

  K --> L{¿Se marcó 'Precaución'<br/>por riesgo/costo alto?}
  L -->|Sí| L1[Adelante PERO<br/>de forma gradual, con límites<br/>y monitoreo consciente] --> FIN
  L -->|No| FIN[Fin]


---

## 5️⃣ Carpeta `engine/`

### `engine/states.py`

```python
from enum import Enum, auto


class Decision(Enum):
    """
    Estados de salida del motor de criterio.

    NO               -> La afirmación/decisión no debe usarse como base operativa.
    POSPONER         -> Aún no hay fundamento suficiente; conviene esperar.
    ADELANTE_GRADUAL -> Se puede avanzar, pero con cautela y pasos pequeños.
    ADELANTE         -> Adelante con tranquilidad; la decisión es razonable.
    """
    NO = auto()
    POSPONER = auto()
    ADELANTE_GRADUAL = auto()
    ADELANTE = auto()
