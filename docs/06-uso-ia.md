# Declaración de uso de inteligencia artificial

Según el punto 7 de la consigna, se declara la herramienta, la finalidad, el grado de intervención
y el registro de las interacciones.

| Aspecto | Detalle |
|---|---|
| Herramienta | Claude (Anthropic), asistente conversacional con acceso a un entorno de ejecución de código |
| Fecha | Octubre de 2026 |
| Finalidad | Tutoría y apoyo para: armar un prototipo con problemas de diseño realistas, proponer el diagnóstico de code smells, sugerir y ejecutar refactorings paso a paso, escribir pruebas, medir métricas y redactar la documentación. |
| Grado de intervención | **Alto en la producción inicial** (código, pruebas y borradores de documentación fueron generados con asistencia de la IA). **El equipo** definió el alcance y las decisiones (caso, lenguaje, modalidad), revisó cada etapa, ejecutó las pruebas y es responsable de comprender y defender todo lo entregado. |
| Qué NO hizo la IA | No grabó ni narró el video (la defensa es con voz propia). No reemplaza la defensa individual. |
| Cómo se controló | Todo cambio quedó en un commit propio; cada refactoring se validó con el golden master; las métricas se obtuvieron con herramientas (radon, pylint, flake8, coverage), no con estimaciones de la IA. |
| Trazabilidad | Los commits generados con asistencia llevan la línea `Co-Authored-By: Claude`. |

## Registro de prompts

> Completar/ajustar con las interacciones posteriores que tenga el equipo (por ejemplo, consultas para estudiar la defensa). Adjuntar la exportación de la conversación en el anexo ZIP (`anexo/ia/`).

| # | Prompt / intercambio | Respuesta / resultado | Uso en el trabajo |
|---|---|---|---|
| 1 | Se adjuntó la consigna oficial (PDF), la descripción del aula virtual, la guía rápida y el modelo de presentación de la cátedra, con el pedido: *"¿me ayudás a hacer este TP?"* | La IA leyó el material y preguntó por: sistema base, lenguaje, modalidad y entregables a priorizar. | Definición del alcance. |
| 2 | Respuestas del equipo: *prototipo nuevo (Sistema de Gestión de Solicitudes Académicas), Python, grupal (Reinaudo – Rivas), armar código inicial + refactorizado, informe, guion del video y presentación.* | Plan de trabajo por etapas. | Organización del trabajo. |
| 3 | Construcción de la versión inicial con problemas de diseño detectables. | `solicitudes/gestor.py` y `main.py` (tag `estado-inicial`). | Etapa 1. |
| 4 | Diagnóstico de calidad y medición con radon, pylint y flake8. | `docs/01-diagnostico.md`, métricas iniciales, evidencia de los defectos D1 y D2. | Etapas 2 y 3. |
| 5 | Red de seguridad antes de refactorizar. | Tests de caracterización (golden master). | Etapa 6 (preparación). |
| 6 | Refactorings R1 a R6, uno por commit, ejecutando el golden master después de cada uno. | Commits `refactor(R1)` … `refactor(R6)`. | Etapas 4 y 5. |
| 7 | Pruebas unitarias, cobertura de ramas y evidencias antes/después. | `tests/`, `scripts/verificar.sh`, `docs/evidencias/`. | Etapa 6. |
| 8 | Aplicación del checklist de code review y corrección de observaciones. | `docs/05-code-review.md`, commit `review:`. | Etapa 7. |
| 9 | Redacción de documentación, informe, guion del video y presentación. | `docs/`, informe PDF, guion, diapositivas. | Etapa 8 y entregables. |

## Reflexión del equipo sobre el uso de IA

*(Completar con palabras propias: qué aprendieron, qué tuvieron que revisar o corregir, qué decisión tomarían distinto.)*
