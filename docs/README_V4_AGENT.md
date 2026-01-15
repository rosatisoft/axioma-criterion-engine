---

## 📄 Licencia
Este proyecto está licenciado bajo los términos de la **MIT License**.

Puedes usarlo, copiarlo, modificarlo y redistribuirlo, incluso con fines comerciales,
siempre que conserves el aviso de copyright:

**© 2026 Ernesto Rosati**

Para más detalles, consulta el archivo `LICENSE` incluido en este repositorio.
# Axioma-Criterion Engine V4 + IA Agent
Evaluación estructurada y narrativa de decisiones basada en el Método Triaxial de Discernimiento (Fundamento – Contexto – Principio)

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
- Analiza parámetros conocidos
- Estima puntajes F–C–P
- Calcula riesgo global
- No inventa información

### 2. Agente IA (conciencia narrativa)
- Reformula la afirmación del usuario
- Interpreta resultados estructurales
- Produce dictamen y siguiente paso
- Detecta matices prácticos y éticos

---

## 🚀 Cómo ejecutarlo

### Requisitos
- Python 3.10+
- `pip install openai`
- Variable de entorno:

setx OPENAI_API_KEY "tu_api_key"
  
### Ejecución
Desde la raíz del proyecto:

python examples\v4_ia_agent_demo.py


Escribe tu afirmación y recibe:
- JSON con puntajes
- Dictamen en lenguaje natural

---

## 🧪 Ejemplo rápido

**Afirmación:**
> Debo enfocarme en convertir el motor V4 en herramienta comercial usable

**Salida estructurada (resumen):**
fundamento: 0.65
contexto: 0.60
principio: 0.685
riesgo_global: 0.80

**Dictamen (resumen):**
- Conviene avanzar bajo condiciones razonables
- Riesgos bajos
- Plan sugerido: iterar y evaluar resultados

---

## 🎯 Propósito
El objetivo de esta herramienta es apoyar decisiones conscientes
mediante un análisis estructurado complementado por discernimiento contextual.

