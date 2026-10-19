# Etapa 7 — Code review profesional

**Alcance revisado:** diferencias entre `etapa-pruebas` y la versión inicial (`git diff estado-inicial..etapa-pruebas -- solicitudes/`), es decir, todo el código refactorizado.
**Modalidad:** revisión cruzada. Quien no escribió un módulo lo revisa con el checklist; las observaciones se discuten y se registran acá. Las correcciones aceptadas están en el commit `review: ...` (ver `git log`).
**Herramientas de apoyo:** pylint, flake8, radon (complejidad y mantenibilidad) y la batería de pruebas (`bash scripts/verificar.sh`).

## 1. Checklist técnico

Escala: ✅ cumple · ⚠️ cumple con observaciones · ❌ no cumple (bloquea el merge).

| # | Criterio | Cómo se verifica | Resultado | Obs. |
|---|---|---|---|---|
| **A** | **Comportamiento** | | | |
| A1 | El golden master pasa (no se alteró el comportamiento externo) | `pytest tests/test_caracterizacion.py` | ✅ 8/8 | |
| A2 | Los defectos del diagnóstico tienen test de regresión | `tests/test_defectos_corregidos.py` | ✅ D1 y D2 | |
| A3 | Los datos guardados por la versión inicial se siguen leyendo | `test_lee_y_reescribe_archivo_de_la_version_inicial_sin_cambios` | ✅ | |
| A4 | Ante un corte durante el guardado no se pierden datos | Lectura de `RepositorioJSON.guardar` | ⚠️ | CR-04 |
| **B** | **Diseño (SOLID)** | | | |
| B1 | Cada módulo/clase tiene una única razón de cambio (SRP) | Revisión de responsabilidades por módulo | ✅ | |
| B2 | Agregar un tipo de solicitud no modifica lógica existente (OCP) | Se agrega un tipo de prueba: enum + 1 regla | ✅ | |
| B3 | Las implementaciones de repositorio son intercambiables (LSP) | `test_implementaciones_intercambiables` | ✅ | |
| B4 | Ningún cliente depende de métodos que no usa (ISP) | La consola solo conoce `ServicioSolicitudes`; el reporte recibe listas, no el repositorio | ✅ | |
| B5 | La lógica depende de abstracciones, no de detalles (DIP) | `ServicioSolicitudes` recibe repositorio, política y reloj por constructor | ✅ | |
| B6 | No hay estado global mutable | Búsqueda de `global` | ✅ | |
| **C** | **Clean Code** | | | |
| C1 | Nombres expresivos, sin abreviaturas de una letra | Lectura | ✅ | |
| C2 | Funciones cortas, complejidad ciclomática ≤ 10 | `radon cc -n C` | ⚠️ | CR-02 |
| C3 | Cada función hace una sola cosa (un nivel de abstracción) | Lectura | ⚠️ | CR-03 |
| C4 | Sin código muerto ni comentarios que repiten el código | Lectura | ✅ | |
| C5 | Sin literales mágicos | Búsqueda de strings de estado/tipo fuera de `modelos.py` | ✅ | |
| C6 | Estilo uniforme (PEP 8, líneas ≤ 110) | `flake8`, `pylint` | ⚠️ | CR-01 |
| **D** | **Manejo de errores** | | | |
| D1 | Sin `except:` genéricos | `flake8` E722 | ✅ | |
| D2 | Los errores se informan con excepciones del dominio, no con códigos de retorno | Lectura de `servicio.py` | ✅ | |
| D3 | Los mensajes al usuario son claros | Golden master `validaciones` | ⚠️ | CR-07 |
| **E** | **Pruebas** | | | |
| E1 | Cobertura de ramas ≥ 90 % en `solicitudes/` | `scripts/verificar.sh` | ✅ 99 % | |
| E2 | Pruebas unitarias independientes de archivos y de la fecha real | Repositorio en memoria + reloj inyectado | ✅ | |
| E3 | Las pruebas siguen el patrón AAA y tienen nombres descriptivos | Lectura | ✅ | |
| **F** | **Repositorio y documentación** | | | |
| F1 | Commits pequeños, con mensaje que explica el *por qué* | `git log` | ✅ | |
| F2 | Tags de estado y de etapa presentes | `git tag` | ✅ | |
| F3 | README con instalación, uso, funcionalidades y tecnologías | Lectura | ⚠️ | CR-06 |
| F4 | Decisiones técnicas documentadas | `docs/` | ✅ | |

## 2. Observaciones y feedback

Formato: **qué** se observó, **por qué** importa (criterio objetivo), **propuesta** y **decisión**.

| ID | Archivo / zona | Observación | Por qué importa | Propuesta | Severidad | Decisión |
|---|---|---|---|---|---|---|
| CR-01 | `consola.py` (6 líneas), `servicio.py:78` | Líneas de más de 100 caracteres (pylint C0301). | Legibilidad en revisiones lado a lado; regla de estilo del equipo. | Partir las líneas largas; fijar 110 como máximo en `.pylintrc`. | Baja | ✅ **Corregido** |
| CR-02 | `reportes.py` – `generar_reporte` | Complejidad ciclomática 13 (radon C) por las comprensiones con condiciones. | Supera el umbral de 10 acordado en C2. | Extract Method: `_contar_por`, `_sin_ceros`, `_carga_por_responsable`, `_porcentaje`. | Media | ✅ **Corregido** → CC 1 |
| CR-03 | `consola.py` – `_registrar_solicitud` | Mezcla tres niveles de abstracción: decidir si el estudiante es nuevo, leer 6 campos y mostrar el resultado. | Clean Code: una función, un nivel de abstracción. | Extract Method: `_leer_datos_estudiante_si_es_nuevo` y `_leer_datos_solicitud`. | Media | ✅ **Corregido** |
| CR-04 | `repositorio.py` – `guardar` | Se escribe directamente sobre el archivo; si el proceso se corta a mitad de la escritura, el JSON queda truncado. | Es el mismo tipo de riesgo que motivó la corrección de D1 (pérdida de datos). | Escritura atómica: escribir en `.tmp` y reemplazar con `os.replace`. Agregar test. | Alta | ✅ **Corregido** + `test_guardar_es_atomico_y_no_deja_temporales` |
| CR-05 | `consola.py`, `prioridad.py` | pylint R0903 *too-few-public-methods*. | — | Es un falso positivo: son clases con un único punto de entrada por diseño. | Info | ➖ **Aceptado sin cambios**; se desactiva R0903 con justificación en `.pylintrc` |
| CR-06 | `README.md` | Describe solo la versión inicial; no explica tests, tags ni estructura. | F3; quien corrige tiene que poder ejecutar todo. | Reescribir README. | Media | ✅ **Corregido** en el commit de documentación |
| CR-07 | Mensajes de la consola | Los textos no tienen tildes ("Opcion", "invalido"). | Calidad externa percibida. | Agregar tildes. | Baja | ⏭️ **Pospuesto**: cambia la salida y obligaría a regenerar el golden master. Se registra como mejora futura con criterio: hacerlo en un cambio separado, aprobado y con golden nuevo. |
| CR-08 | `modelos.py` – `validar()` | Las validaciones devuelven `str | None` y el servicio las convierte en excepción. | Podría lanzar directamente. | Lanzar `DatosInvalidosError` desde `validar()`. | Baja | ➖ **Aceptado sin cambios**: devolver el mensaje mantiene los objetos de datos sin dependencia de las excepciones y facilita probarlos. |
| CR-09 | `servicio.py` – `fecha_de_hoy` | Usa la fecha local del equipo. | Si se despliega en un servidor en otra zona horaria, las fechas podrían diferir. | Inyectar un reloj con zona horaria. | Baja | ⏭️ **Mejora futura**: el reloj ya es inyectable, el cambio queda acotado a `main.py`. |

**Resumen:** 9 observaciones · 5 corregidas · 2 aceptadas con justificación · 2 pospuestas como mejora futura · 0 bloqueantes pendientes.

## 3. Criterios de aceptación técnica

El cambio se acepta (merge a `main` y tag `estado-refactorizado`) solo si se cumplen **todos**:

| # | Criterio | Umbral | Resultado final |
|---|---|---|---|
| AC-1 | Golden master | 8/8 tests en verde | ✅ 8/8 |
| AC-2 | Batería completa | 100 % de tests en verde | ✅ 70/70 |
| AC-3 | Cobertura de ramas en `solicitudes/` | ≥ 90 % | ✅ 99 % |
| AC-4 | Complejidad ciclomática máxima por función | ≤ 10 (radon A/B) | ✅ máx. 7 |
| AC-5 | Análisis estático | pylint ≥ 9,5 y flake8 sin avisos | ✅ 10,00 y 0 |
| AC-6 | Compatibilidad de datos | El JSON de la versión inicial se lee sin cambios | ✅ |
| AC-7 | Observaciones de severidad Alta o Media | Todas corregidas | ✅ CR-02, CR-03, CR-04, CR-06 |
| AC-8 | Trazabilidad | Cada refactoring en su propio commit con referencia al smell | ✅ R1–R6 |

Evidencias: [`evidencias/pruebas-resultado.txt`](evidencias/pruebas-resultado.txt), [`evidencias/cobertura.txt`](evidencias/cobertura.txt), [`evidencias/metricas-final.txt`](evidencias/metricas-final.txt).
