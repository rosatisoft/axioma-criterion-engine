# Axioma-Criterion Engine V4 + IA Agent
Evaluación estructurada y narrativa de decisiones basada en el Método Triaxial de Discernimiento (Fundamento – Contexto – Principio)

## 📄 Licencia
Este proyecto está licenciado bajo los términos de la **MIT License**.

Puedes usarlo, copiarlo, modificarlo y redistribuirlo, incluso con fines comerciales,
siempre que conserves el aviso de copyright:

**© 2026 Ernesto Rosati**

Para más detalles, consulta el archivo `LICENSE` incluido en este repositorio.

---

## 🌟 Introducción
El Axioma-Criterion Engine V4 es un evaluador estructural de decisiones que aplica el Método Triaxial de Discernimiento.

Su función es calcular una evaluación racional basada en tres ejes:

- **Fundamento** — ¿Está bien fundamentada la afirmación?
- **Contexto** — ¿Encaja razonablemente en la situación actual?
- **Principio** — ¿La acción está alineada con el propósito o convicciones?

El **IA Agent** complementa al motor generando:

- Una clarificación de la afirmación original
- Una narrativa prudente e interpretativa
- Una recomendación práctica basada en los resultados

De esta forma, el usuario recibe:

- Datos estructurados (JSON)
- Un dictamen legible y útil (texto)

---

## ⚙️ Arquitectura de dos capas

### 1. Motor V4 (núcleo lógico)
- Analiza parámetros básicos declarados
- Estima puntajes F–C–P
- Calcula un riesgo global
- No inventa información; solo combina parámetros de entrada

### 2. Agente IA (conciencia narrativa)
- Reformula la afirmación del usuario
- Interpreta los resultados estructurales del motor
- Produce un dictamen prudente
- Explica riesgos y sugiere un siguiente paso concreto

---

## 🚀 Cómo ejecutarlo

### Requisitos
- Python 3.10 o superior
- Paquete `openai` instalado
- Variable de entorno configurada:
  ```bash
  OPENAI_API_KEY="tu_api_key_aquí"

  
### Ejecución
Desde la raíz del proyecto:

python examples\v4_ia_agent_demo.py


El programa pedirá una afirmación o decisión a evaluar y devolverá:

Un JSON con la evaluación estructural (salida del motor V4)

Un dictamen narrativo (salida del IA Agent)

---

## 🧪 Ejemplo rápido

**Afirmación:**
> Debo enfocarme en convertir el motor V4 en herramienta comercial usable

**Salida estructurada (resumen):**
{
  "scores": {
    "fundamento": 0.65,
    "contexto": 0.6,
    "principio": 0.685,
    "riesgo_global": 0.8
  }
}


**Dictamen (resumen):**
Conviene avanzar con el desarrollo del motor V4.

Los riesgos individuales (tiempo, dinero, salud/relaciones) se consideran bajos.

Se sugiere definir objetivos claros y puntos de revisión periódicos.

---

## 🎯 Propósito
El objetivo de esta herramienta es apoyar decisiones conscientes mediante:

Un análisis estructurado (Fundamento–Contexto–Principio)

Una interpretación narrativa que incorpore prudencia, propósito y ética

El código se ofrece bajo MIT para facilitar su adopción, estudio y mejora,
en coherencia con la intención de difundir un criterio operativo basado en la verdad.

4. Abajo escribe un mensaje de commit, por ejemplo: `Add clean README_V4_AGENT`
5. Guarda el archivo.

Cuando regreses a verlo, ya no debe aparecer ningún error YAML ni 503.

---

Si al abrirlo de nuevo GitHub vuelve a mostrar algo raro, me dices exactamente qué ves y lo pulimos, pero con este contenido limpio debería quedar perfecto.

Cuando lo tengas listo, el siguiente paso es:  
- revisar rápido `v4_behavior_examples.md` y `v4_limitations_and_next_steps.md`  
y luego sí, pensar en **V4.1 o el paper para Zenodo**.
::contentReference[oaicite:0]{index=0}
