# Roadmap – Axioma Criterion Engine v3

Este documento es una guía de hacia dónde podría evolucionar el motor.

---

## Versión 3.x – Consolidar el núcleo

- [x] Crear repositorio dedicado.
- [x] Documentar la historia (v0–v3).
- [x] Redactar teoría mínima (Axioma, Método Triaxial, capas).
- [x] Definir diagrama de flujo en Mermaid.
- [x] Implementar núcleo en `engine/core.py`.
- [x] Crear interfaz CLI en `cli/main.py`.
- [x] Añadir pruebas básicas en `tests/`.
- [ ] Pulir textos de preguntas para distintos niveles de usuario (básico / avanzado).
- [ ] Escribir ejemplos de uso por dominio (salud, finanzas, proyectos personales).

---

## Versión 4 – Agente conversacional guiado

- [ ] Separar completamente textos de preguntas en `engine/questions.py`.
- [ ] Definir un protocolo de “prompter” para integrarse con modelos de lenguaje.
- [ ] Crear un agente que:
  - haga preguntas al usuario,
  - guarde las respuestas,
  - y aplique el motor de criterio al final.
- [ ] Documentar cómo integrar el agente con distintas IAs (locales o API).

---

## Versión 5 – Interfaz web mínima

- [ ] Crear una pequeña aplicación web (HTML/JS o framework ligero).
- [ ] Permitir al usuario contestar preguntas con formularios.
- [ ] Mostrar al final:
  - decisión,
  - nota explicativa,
  - y resumen visual del camino F–C–P.

---

## Versión 6 – Memoria de valores del usuario

- [ ] Permitir que el usuario registre explícitamente:
  - valores importantes,
  - límites innegociables,
  - objetivos de largo plazo.
- [ ] Hacer que el motor use esta información al evaluar el “PARA QUÉ”.

---

## Versión 7 – Adaptaciones por dominio

- [ ] Crear perfiles de preguntas para:
  - salud,
  - finanzas,
  - relaciones,
  - proyectos creativos,
  - decisiones éticas complejas.
- [ ] Documentar cómo extender el motor sin romper el núcleo.

---

## Versión 8 – Paquete educativo

- [ ] Preparar material para talleres:
  - PDFs,
  - presentaciones,
  - ejercicios guiados.
- [ ] Incluir ejemplos de casos reales (anonimizados).
- [ ] Publicar una guía de “Cómo enseñar criterio usando este motor”.

---

## Visión de largo plazo

- Integrar el motor en asistentes de IA para que:
  - hagan preguntas antes de responder,
  - revelen sesgos y contradicciones,
  - ayuden a las personas a recuperar su capacidad de elegir bien.
- Mantener el proyecto como un espacio donde:
  - la historia y el proceso sean tan importantes como el resultado,
  - otros puedan entender la ruta y crear nuevos caminos a partir de ella.
