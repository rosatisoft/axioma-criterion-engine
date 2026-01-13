# Historia v3 – Nacimiento del motor estructurado

La **v3** marca el nacimiento del motor como **proyecto formal**.

## 1. Qué cambia en v3

- Se crea un repositorio dedicado.
- Se documenta la historia (v0, v1, v2).
- Se fijan documentos teóricos mínimos.
- Se define un **diagrama de flujo** claro.
- Se escribe el **algoritmo en pseudocódigo**.
- Se implementa una primera versión en Python (CLI).

## 2. Elementos clave de v3

- El motor tiene ahora:
  - estados de salida (`NO`, `POSPONER`, `ADELANTE_GRADUAL`, `ADELANTE`),
  - pasos bien definidos,
  - conexión explícita con:
    - Fundamento (F),
    - Contexto/Entropía (C),
    - Principio/Propósito (P),
    - y las capas QUÉ–POR QUÉ–PARA QUÉ.

- Se separa la lógica (en `engine/core.py`)  
  de la interfaz humana (en `cli/main.py`).

## 3. Objetivo educativo

v3 no es solo una mejora técnica.

El objetivo es que:

- cualquier persona pueda ver **cómo se llegó aquí**,
- entender el **por qué de cada decisión de diseño**,
- y tener la libertad de:
  - adaptar el motor a otros contextos,
  - o construir caminos nuevos a partir de este.

v3 es la versión en la que el motor empieza a ser **heredable**.
