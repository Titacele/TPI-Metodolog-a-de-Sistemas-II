# Etapas 2 y 3 — Diagnóstico de calidad, deuda técnica y code smells

Versión analizada: tag `estado-inicial`. Las líneas se refieren a `solicitudes/gestor.py`
salvo que se indique `main.py`. Las métricas completas están en
[`evidencias/metricas-inicial.txt`](evidencias/metricas-inicial.txt).

## 1. Calidad externa vs. calidad interna

| Mirada | Qué observamos |
|---|---|
| **Externa (usuario)** | Las 7 operaciones del menú funcionan: alta de estudiantes, registro de solicitudes con prioridad automática, asignación de responsable, cambio de estado, búsqueda con filtros, detalle con historial y reporte. Los mensajes de error son claros y los datos persisten entre ejecuciones. |
| **Interna (equipo)** | Toda la lógica vive en una sola clase de 325 líneas que mezcla persistencia, validación, reglas de negocio e impresión por pantalla. Hay 4 copias del código de guardado, 2 copias de la validación de estudiantes, 4 copias de la conversión prioridad→texto y los estados/tipos son strings repetidos en varios archivos. No hay pruebas automatizadas. |

**Indicadores de la versión inicial**

| Métrica | Valor | Lectura |
|---|---|---|
| Complejidad ciclomática promedio (radon) | **11,3 (C)** | Por encima de 10 se considera difícil de probar. |
| `registrar_solicitud` | **CC 28 (D)**, 57 sentencias, 8 parámetros | Método más riesgoso del sistema. |
| `reporte` | **CC 24 (D)** | Cinco bucles casi idénticos. |
| Índice de mantenibilidad `gestor.py` | **16,5 (B)** | Bajo: el archivo es grande y muy ramificado. |
| pylint | **8,66/10** | 37 avisos (bare-except, global, too-many-*). |
| flake8 | **17 avisos** | 6 `except:` sin tipo, 7 comparaciones `== None`. |
| Pruebas automatizadas | **0** | Cualquier cambio se verifica a mano. |

**Conclusión:** el sistema *funciona*, pero el costo del cambio es alto. Ejemplos concretos:

- Agregar un tipo de solicitud nuevo obliga a tocar **4 lugares** (lista en `gestor.py:82`, lista en `gestor.py:282`, lista en `main.py:3` y la cadena `if/elif` de prioridad).
- Cambiar el formato del archivo (por ejemplo, pasar a SQLite) obliga a modificar **5 métodos** que abren el archivo directamente.
- No se puede probar una regla de negocio sin pasar por la consola, porque los métodos imprimen en lugar de devolver resultados.

Además, durante el diagnóstico encontramos **dos defectos latentes** que el usuario todavía no vio,
pero que son consecuencia directa de la mala estructura interna:

- **D1 – Pérdida silenciosa de datos:** si el JSON está dañado, el `except:` genérico reinicia todo y la siguiente operación sobrescribe el archivo. Evidencia: [`defecto-D1-json-danado.txt`](evidencias/defecto-D1-json-danado.txt).
- **D2 – Alta parcial:** al registrar una solicitud para un legajo nuevo, el estudiante se da de alta *antes* de validar la solicitud; si la solicitud es inválida, el estudiante queda creado igual. Evidencia: [`defecto-D2-alta-parcial.txt`](evidencias/defecto-D2-alta-parcial.txt).

## 2. Deuda técnica y code smells

Prioridad = impacto en mantenimiento × probabilidad de que esa zona cambie.
**Alta** = se corrige en este TPI primero; **Media** = se corrige en este TPI; **Baja** = se corrige si el refactoring lo deja servido.

| ID | Smell / debilidad | Ubicación | Evidencia | Impacto | Riesgo de mantenimiento | Prioridad |
|---|---|---|---|---|---|---|
| CS-01 | **God Class** (Large Class) | `GestorSolicitudes` (9–325) | Una clase con persistencia, validación, reglas de negocio, formateo e impresión. Viola SRP. | Todo cambio toca el mismo archivo; conflictos de merge en equipo. | Alto | **Alta** |
| CS-02 | **Long Method** | `registrar_solicitud` (61–142) | 82 líneas, CC 28, 57 sentencias, 8 `return`. | Difícil de entender y probar; origen del defecto D2. | Alto | **Alta** |
| CS-03 | **Long Parameter List** | `registrar_solicitud` (61) | 8 parámetros posicionales: `legajo, nombre, email, tipo, descripcion, materia, urgente, canal`. | Fácil invertir argumentos del mismo tipo (`str`) sin que nada falle. | Medio | **Media** |
| CS-04 | **Duplicated Code** – validación de estudiante | 39–48 y 69–77 | Mismas tres validaciones copiadas. | Cambiar la regla de legajo exige recordar dos lugares. | Alto | **Alta** |
| CS-05 | **Duplicated Code** – guardado en JSON | 54–57, 131–134, 168–171, 202–205 | Cuatro bloques `open/json.dump/close` idénticos. | Cambiar el formato o la ruta implica 4 ediciones; sin `with`, un error deja el archivo abierto. | Alto | **Alta** |
| CS-06 | **Duplicated Code** – búsqueda por id | 145–148, 152–155, 176–179, 244–247, 251–254 | Mismo bucle `for x in ...: if x["id"] == ...` cinco veces. | Ruido y posibilidad de inconsistencias. | Medio | **Media** |
| CS-07 | **Magic Numbers** + duplicación prioridad→texto | 135–140, 228–233, 260–265, 295–300 | Prioridades `1/2/3` sin nombre; traducción a `ALTA/MEDIA/BAJA` repetida 4 veces. | Agregar un nivel (p. ej. `URGENTE`) obliga a tocar 4 bloques. | Medio | **Media** |
| CS-08 | **Switch Statements** (condicionales por tipo y por estado) | prioridad 92–111; transiciones 184–195 | Cadena `if/elif` por tipo de solicitud y `if` anidados para las transiciones de estado. Viola OCP. | Cada tipo o estado nuevo modifica código existente. | Alto | **Alta** |
| CS-09 | **Primitive Obsession** | todo el sistema; listas de tipos en 82, 282 y `main.py:3` | Estados, tipos y canales como `str`; solicitudes como `dict`. | Un error de tipeo (`"en proceso"`) no se detecta hasta producción. | Alto | **Alta** |
| CS-10 | **Manejo de errores deficiente** | `except:` en 26; retornos en 175–206 | `except:` genérico que oculta cualquier error (defecto D1). `cambiar_estado` devuelve `True`, `False` o `"error"` según el caso. | Pérdida de datos; quien llama no puede distinguir errores. | Muy alto | **Alta** |
| CS-11 | **Acoplamiento a infraestructura y UI** (viola DIP) | `print` en todos los métodos; `open(ARCHIVO)`; `global contador` (6, 17, 62) | La lógica depende de la consola y del archivo concreto; estado global mutable. | No se puede reutilizar la lógica en una web/API ni probarla aislada. | Alto | **Alta** |
| CS-12 | **Efecto colateral antes de validar** (acoplamiento temporal) | 78–80 | El estudiante se agrega a la lista antes de validar tipo, descripción, canal y materia (defecto D2). | Datos inconsistentes. | Alto | **Alta** |
| CS-13 | **Feature Envy / límites rotos** en la UI | `main.py:33–36` | `main` recorre `g.estudiantes` para saber si un legajo existe: la UI conoce la estructura interna del gestor. | Cambiar la representación interna rompe la UI. | Medio | **Media** |
| CS-14 | **Nombres poco expresivos** | `p`, `pr`, `l`, `x`, `d`, `f`, `c`, `ant`, `g`, `u` | Variables de una letra sin significado de dominio. | Lectura lenta; errores al modificar. | Bajo | **Baja** |
| CS-15 | **Código muerto** | 318–321 | Método viejo comentado `calcular_prioridad_vieja`. | Confunde sobre cuál es la regla vigente. | Bajo | **Baja** |
| CS-16 | **Script con efectos al importar** | `main.py:102` | `main()` se ejecuta al importar el módulo (sin `if __name__ == "__main__"`). | Impide importar y probar el módulo. | Bajo | **Baja** |

**Total: 16 code smells/debilidades + 2 defectos latentes (D1, D2).**

## 3. Plan de corrección (trazabilidad smell → acción)

| Smell | Principio | Refactoring / acción | Commit |
|---|---|---|---|
| CS-02, CS-12 | SRP, Clean Code | **R1 – Extract Method**: separar validación, cálculo de prioridad y creación | ver `docs/03-refactorings.md` |
| CS-07, CS-08, CS-09 | OCP | **R2 – Replace Magic Literal / Replace Type Code with Enum** | |
| CS-08, CS-01 | SRP, OCP | **R3 – Move Method**: prioridad → `PoliticaPrioridad`; transiciones → `Estado` | |
| CS-03, CS-13 | Clean Code | **R4 – Introduce Parameter Object**: `DatosSolicitud` / `DatosEstudiante` | |
| CS-05, CS-06, CS-11 | DIP, SRP | **R5 – Extract Class**: `RepositorioJSON` detrás de una interfaz | |
| CS-10, CS-11, CS-01 | SRP, Clean Code | **R6 – Separar UI de la lógica** y reemplazar códigos de retorno por excepciones | |
| CS-04, CS-14, CS-15, CS-16 | Clean Code | Se resuelven dentro de R1–R6 | |
