# axioma-criterion-engine
El motor que enseña criterio al humano y a la IA

Es:
# Tri-Axial Discernment Engine v3

Motor de criterio basado en el Axioma del Absoluto y en el Método Triaxial de Discernimiento (F–C–P), diseñado para ayudar a humanos e IAs a tomar mejores decisiones.

> Este proyecto nace de una intuición simple:  
> la mayoría de nuestros errores no vienen de falta de información,  
> sino de falta de criterio para elegir bien.

---

## 🎯 Problema que intenta resolver

La educación moderna enseña datos, técnicas y procedimientos, pero casi nunca enseña **criterio**:

- Aceptamos argumentos sin verificar nada.
- Tomamos decisiones desde la emoción, la presión o el miedo.
- Nuestro diálogo interior está atrapado en nuestros propios límites.
- La IA, sin un marco de criterio, solo amplifica patrones y sesgos.

Resultado:  
**mucha capacidad, poca sabiduría**.

Este motor busca ofrecer una **herramienta práctica y universal** para:

- Evaluar afirmaciones y decisiones.
- Hacer las preguntas correctas antes de actuar.
- Recuperar una escala de valores explícita.
- Usar la IA como ampliador de conciencia, no como sustituto.

---

## 🧠 Idea central

El motor combina tres ejes:

1. **Fundamento (F)**  
   ¿Es real? ¿Es verificable? ¿Es coherente con los hechos?

2. **Contexto / Entropía (C)**  
   ¿Cuál es el costo, el riesgo, el desgaste?

3. **Principio / Propósito (P)**  
   ¿Para qué lo quiero? ¿Me construye? ¿Se alinea con mis valores?

Y los articula en un ciclo de preguntas:

- **QUÉ** estoy afirmando.
- **POR QUÉ** lo creo.
- **PARA QUÉ** lo quiero usar.

El motor **no decide por ti**.  
Te obliga a pensar de forma más clara y ordenada.

---

## ⚙️ Estado del proyecto

- Versión: **v3 (núcleo en construcción)**
- Enfoque actual:
  - Documentar la historia (v0–v3).
  - Definir la teoría mínima necesaria.
  - Fijar el diagrama de flujo.
  - Implementar un motor básico y una interfaz de línea de comandos.

Este repositorio está pensado **también con fines educativos**:  
para que cualquier persona pueda entender **cómo** se diseñó este motor y pueda mejorar o extender el camino.

---

## 📂 Estructura del repositorio

```text
axioma-criterion-engine-v3/
│
├─ README.md
│
├─ HISTORY/           # Historia de las versiones v0, v1, v2, v3
├─ THEORY/            # Documentos conceptuales (axioma, método, problema)
├─ FLOW/              # Diagramas de flujo y representaciones visuales
├─ engine/            # Núcleo del motor de criterio
├─ cli/               # Interfaz de línea de comandos (uso humano directo)
├─ tests/             # Pruebas básicas del motor
└─ roadmap.md         # Plan de evolución del proyecto

Estructura del nuevo repositorio
axioma-criterion-engine-v3/
│
├─ README.md
│
├─ HISTORY/
│   ├─ v0-notes.md
│   ├─ v1-first-filter.md
│   ├─ v2-dialogos-con-IA.md
│   └─ v3-nacimiento.md
│
├─ THEORY/
│   ├─ axioma-basico.md
│   ├─ metodo-triaxial.md
│   ├─ capas-que-por-que-para-que.md
│   └─ el-problema-que-resolvemos.md
│
├─ FLOW/
│   ├─ diagramas.md
│   └─ mermaid/
│       ├─ criterio-basico.md
│       └─ ciclo-evolutivo.md
│
├─ engine/
│   ├─ core.py
│   ├─ questions.py
│   ├─ states.py
│   └─ utils.py
│
├─ cli/
│   └─ main.py
│
├─ tests/
│   └─ test_core.py
│
└─ roadmap.md

🚀 Cómo probar el motor (versión CLI)

Requisitos:

Python 3.10 o superior

Pasos básicos:

git clone https://github.com/tu-usuario/axioma-criterion-engine-v3.git
cd axioma-criterion-engine-v3

# Ejecutar versión CLI
python -m cli.main

El programa te pedirá:

Una afirmación o decisión (ej: “Debo invertir en bolsa ahora”).

Ejemplos o fuentes para verificarla.

Riesgos y costos percibidos.

Razones por las que crees que es verdadera.

Propósito (para qué la quieres usar).

Si se alinea con tus valores.

Si sientes paz interior con la decisión.

Finalmente, devolverá una salida tipo:

NO

POSPONER

ADELANTE_GRADUAL

ADELANTE

junto con una nota explicativa.

🧭 Filosofía de diseño

Transparencia: el proceso debe ser entendible por cualquier persona.

Universalidad: que funcione en salud, finanzas, relaciones, proyectos, etc.

Humildad: el motor no reemplaza la conciencia, la acompaña.

Colaboración humano–IA: la IA se usa para ampliar el diálogo interior, no para imponerse a él.

🤝 Contribuciones

Este proyecto está pensado para crecer:

con nuevas interfaces (web, chat, móvil),

con adaptaciones por dominio (salud, finanzas, educación),

y con mejoras en el algoritmo.

Si quieres explorar o proponer cambios, lo ideal es:

Leer primero THEORY/el-problema-que-resolvemos.md

Revisar FLOW/diagramas.md

Mirar el código en engine/core.py

Abrir propuestas o ideas manteniendo el espíritu del proyecto:

ayudar a las personas a recuperar criterio y verdad en sus decisiones.

📜 Licencia

Licencia: @Ernesto Rosati Beristain CC BY-NC-SA para licenciamiento filosófico/teórico pertenece a documentos (papers, tablas, README).
Mientras tanto, considera este repositorio de uso educativo y experimental.

---

## 2️⃣ Carpeta `HISTORY/`

### `HISTORY/v0-notes.md`

```markdown
# Historia v0 – Intuiciones iniciales

La versión **v0** no era código, era conversación.

## 1. Intuición de fondo

- El problema real no es la falta de información.
- El problema es la **ausencia de criterio** al tomar decisiones.
- La mayoría de la gente acepta ideas, consejos o narrativas sin un filtro mínimo.
- Nuestro diálogo interior está limitado por nuestras propias heridas, sesgos y miedos.

De ahí surgió la pregunta:

> ¿Podemos crear un método simple y universal  
> para que cualquier persona pueda filtrar una idea antes de creerla o actuar?

## 2. Primeras chispas

En esta etapa aparecieron:

- La necesidad de un “**primer filtro**”: ¿es real?, ¿qué me cuesta?, ¿me construye?
- La idea de apoyarse en la IA como “espejo” del diálogo interior.
- El reconocimiento de que la educación nunca nos enseñó criterio explícito.

No había todavía:

- Diagrama de flujo.
- Algoritmo definido.
- Implementación formal.

Solo **principios** y **conversaciones**.

## 3. Valor educativo de v0

v0 es importante porque muestra:

- el origen humano del problema,
- la motivación espiritual y ética,
- y la convicción de que el criterio es enseñable.

Sin v0, el motor sería solo código;  
con v0, el motor tiene **alma y propósito**.
