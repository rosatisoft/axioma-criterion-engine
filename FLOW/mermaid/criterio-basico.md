# Diagrama de flujo – Criterio básico F–C–P

```mermaid
flowchart TD
  A["Inicio: Afirmación / Decisión"] --> B["QUÉ<br/>¿Qué se está afirmando exactamente?"]

  B -->|"No está claro"| B1["Reformular: definir términos<br/>y/o dividir en partes"] --> B
  B -->|"Está claro"| C["REALIDAD (F):<br/>¿Puedo verificarlo en hechos / ejemplos / fuentes?"]

  C -->|"No"| C1["No verificable por ahora<br/>Tratar como hipótesis / opinión,<br/>no como verdad operativa"] --> FIN
  C -->|"Sí"| D["ENTROPÍA RÁPIDA (C):<br/>¿Hay riesgos o costos grandes evidentes?"]

  D -->|"Sí"| D1["Marcar como 'Precaución'<br/>Anotar qué puede salir mal"] --> E
  D -->|"No"| E["POR QUÉ (Fundamento interno):<br/>¿Por qué digo / creo / afirmo esto?"]

  E --> F["¿Tengo razones y/o evidencia concretas?"]

  F -->|"No"| F1["Fundamento débil<br/>Evitar decisiones fuertes basadas en esto"] --> FIN
  F -->|"Sí"| G["¿Las razones son coherentes<br/>y no contradicen hechos sólidos?"]

  G -->|"No"| G1["Inconsistencia detectada<br/>Ajustar la afirmación o descartarla"] --> FIN
  G -->|"Sí"| H["PARA QUÉ (Propósito):<br/>¿Para qué quiero usar / aceptar esta afirmación?"]

  H --> I["¿Se alinea con mis valores<br/>y con quién quiero ser?"]

  I -->|"No"| I1["No procede por ahora<br/>o requiere cambiar el propósito"] --> FIN
  I -->|"Sí"| J["¿Tengo paz interior<br/>al decidir con base en esto?"]

  J -->|"No"| J1["Posponer<br/>Buscar consejo / más información"] --> FIN
  J -->|"Sí"| K["DECISIÓN BASE: Adelante"]

  FIN["Fin del proceso"]
