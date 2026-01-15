flowchart LR
  N["Niño sin criterio propio"] --> A["Adulto sin formación en criterio"]
  A --> E["Errores repetidos en decisiones"]
  E --> M["Busca ayuda externa (autoridades, gurús, sistemas)"]
  M --> IA_S["IA sin criterio<br/>(modelo estadístico)"]
  IA_S --> R["Respuestas rápidas pero superficiales"]

  R --> T["Tomar decisiones sin filtro<br/>ni escala de valores"]
  T --> C["Consecuencias negativas<br/>(entropía alta)"]
  C --> Q["Pregunta existencial:<br/>¿Cómo decido bien?"]

  Q --> K["Motor de Criterio<br/>F–C–P + QUÉ/POR QUÉ/PARA QUÉ"]
  K --> IA_C["IA con criterio guiado<br/>(hace preguntas antes de responder)"]
  IA_C --> H["Humano con diálogo interior ampliado"]
  H --> B["Mejor toma de decisiones<br/>con responsabilidad y verdad"]

  B --> N2["Adulto que transmite criterio<br/>a nuevas generaciones"]

  K --> L{"¿Se marcó 'Precaución'<br/>por riesgo/costo alto?"}
  L -->|"Sí"| L1["Adelante PERO<br/>de forma gradual, con límites<br/>y monitoreo consciente"] --> FIN
  L -->|"No"| FIN["Fin"]
