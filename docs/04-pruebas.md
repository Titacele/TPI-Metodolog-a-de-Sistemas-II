# Etapa 6 — Pruebas y verificación del comportamiento

## Estrategia

| Nivel | Archivo | Qué verifica | Cuándo se escribió |
|---|---|---|---|
| **Caracterización (golden master)** | `tests/test_caracterizacion.py` | Ejecuta `main.py` real con entradas guionadas y compara la **salida por consola** y el **JSON guardado** contra la versión inicial. | Antes de refactorizar |
| Regresión de defectos | `tests/test_defectos_corregidos.py` | D1 (JSON dañado) y D2 (alta parcial). | Junto con cada corrección |
| Unitarias – dominio | `tests/test_modelos.py` | Transiciones, validaciones, asignación, serialización, filtro. | Después de R6 |
| Unitarias – reglas | `tests/test_prioridad.py` | Las 8 combinaciones de prioridad y la extensión por configuración (OCP). | Después de R6 |
| Unitarias – casos de uso | `tests/test_servicio.py` | Con repositorio en memoria, reloj fijo y un repositorio espía. | Después de R6 |
| Persistencia | `tests/test_repositorio.py` | Compatibilidad con el JSON inicial, archivo inexistente, archivos dañados, escritura atómica, LSP. | Después de R6 / code review |
| Interfaz | `tests/test_consola.py` | Entrada/salida inyectadas, prefijo `Error:`. | Después de R6 |

## Escenarios del golden master

| Escenario | Qué cubre |
|---|---|
| `flujo_completo` | Alta de 2 estudiantes y 1 implícito, 6 solicitudes (los 5 tipos, con/sin urgencia, 3 canales), 3 asignaciones, 2 cambios de estado, 5 búsquedas con filtros combinados, 2 detalles y el reporte. |
| `validaciones` | Más de 20 entradas inválidas: legajo, email, nombre, duplicado, tipo, descripción, materia, canal, ids no numéricos o inexistentes, transiciones inválidas, asignar a cerrada, prioridad inválida, opción inválida. |
| `persistencia` | Dos ejecuciones sobre el mismo archivo: la segunda recuerda estudiantes, solicitudes y el contador de ids. |
| `sistema_vacio` | Búsqueda y reporte sin datos (división por cero en el porcentaje). |

Las fechas se reemplazan por `<FECHA>` para que la comparación no dependa del día.

## Casos de prueba representativos

| ID | Caso | Entrada | Resultado esperado | Inicial | Refactorizada |
|---|---|---|---|---|---|
| CP-01 | Prioridad de reclamo urgente | `reclamo_nota`, urgente = s | `Solicitud #1 registrada con prioridad ALTA` | ✅ | ✅ |
| CP-02 | Cambio de comisión presencial | `cambio_comision`, canal presencial | prioridad MEDIA | ✅ | ✅ |
| CP-03 | Asignar responsable a pendiente | asignar #1 → responsable 2 | pasa a `en_proceso` y queda en el historial | ✅ | ✅ |
| CP-04 | Transición inválida | `pendiente → resuelta` | `Error: transicion invalida pendiente -> resuelta` | ✅ | ✅ |
| CP-05 | En proceso sin responsable | `pendiente → en_proceso` sin asignar | `Error: no se puede pasar a en_proceso sin responsable asignado` | ✅ | ✅ |
| CP-06 | Materia obligatoria | `equivalencia` sin materia | `Error: este tipo de solicitud requiere indicar la materia` | ✅ | ✅ |
| CP-07 | Búsqueda ordenada | sin filtros | ordenadas por prioridad desc. y luego id | ✅ | ✅ |
| CP-08 | Reporte | 6 solicitudes, 2 cerradas | `Porcentaje cerradas: 33.3%` | ✅ | ✅ |
| CP-09 | Persistencia del contador | 2.ª ejecución | la nueva solicitud es la #3 | ✅ | ✅ |
| CP-10 | **D2** – solicitud inválida de legajo nuevo | tipo `inscripcion` | No se da de alta al estudiante | ❌ | ✅ |
| CP-11 | **D1** – JSON dañado | archivo truncado | Mensaje de error, código 1, archivo intacto | ❌ | ✅ |
| CP-12 | Escritura atómica | falla durante `json.dump` | el archivo anterior queda intacto | — | ✅ |

## Resultados

| Indicador | Valor |
|---|---|
| Pruebas totales | **70**, todas en verde |
| Cobertura de ramas en `solicitudes/` | **99 %** (incluye las ejecuciones por subproceso del golden master) |
| Golden master en cada commit de refactoring | 8/8 en los 6 commits |
| Golden master sobre la versión inicial | 8/8 (la red describe el comportamiento original) |

Evidencias:
- [`evidencias/pruebas-resultado.txt`](evidencias/pruebas-resultado.txt) — salida de `pytest -v`
- [`evidencias/cobertura.txt`](evidencias/cobertura.txt)
- [`evidencias/antes-despues-pruebas.txt`](evidencias/antes-despues-pruebas.txt)
- [`evidencias/golden-por-commit.txt`](evidencias/golden-por-commit.txt)

Para reproducir todo: `bash scripts/verificar.sh`.
