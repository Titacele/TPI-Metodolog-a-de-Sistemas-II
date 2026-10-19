# Etapa 5 — Refactorings aplicados

Cada refactoring está en **su propio commit** y después de cada uno se ejecutó el golden master
(8/8 en todos los casos, ver [`evidencias/golden-por-commit.txt`](evidencias/golden-por-commit.txt)).
Para ver el antes/después exacto: `git show <commit>`.

| # | Técnica (catálogo de Fowler) | Commit | Smells que resuelve |
|---|---|---|---|
| R1 | **Extract Method** | `refactor(R1)` | CS-02, CS-04, CS-05, CS-06, CS-07, CS-12, CS-13, CS-15 |
| R2 | **Replace Magic Literal / Replace Type Code with Enum** | `refactor(R2)` | CS-07, CS-09 |
| R3 | **Move Method** (reubicación de responsabilidad) | `refactor(R3)` | CS-08, CS-01 |
| R4 | **Introduce Parameter Object** | `refactor(R4)` | CS-03 |
| R5 | **Extract Class** + inversión de dependencia | `refactor(R5)` | CS-05, CS-06, CS-11 |
| R6 | **Separate Query from Modifier**, **Replace Error Code with Exception**, Move Method a la entidad | `refactor(R6)` | CS-01, CS-10, CS-11, CS-16 |
| CR | Extract Method (sugerido por el code review) | `review:` | CR-02, CR-03 |

---

## R1 — Extract Method

**Antes** (`gestor.py`, 82 líneas, CC 28): validación, alta del estudiante, cálculo de prioridad, armado del diccionario, guardado e impresión en un solo método. El estudiante se agregaba **antes** de validar la solicitud (defecto D2).

```python
def registrar_solicitud(self, legajo, nombre, email, tipo, descripcion, materia, urgente, canal):
    global contador
    est = None
    for e in self.estudiantes:
        if e["legajo"] == legajo:
            est = e
    if est == None:
        if not legajo.isdigit() or len(legajo) != 5:     # duplicado de registrar_estudiante
            ...
        self.estudiantes.append(est)                       # <- efecto antes de validar (D2)
    if tipo not in [...]: ...
    p = 0
    if tipo == "reclamo_nota": ...                         # 20 líneas de if/elif
    f = open(ARCHIVO, "w", encoding="utf-8")               # copia 2 de 4
    json.dump({...}, f, indent=2, ensure_ascii=False)
    f.close()
    if p == 3: pr = "ALTA" ...                             # copia 1 de 4
```

**Después**: el método principal solo coordina pasos con nombre propio, y se valida todo antes de modificar datos.

```python
def registrar_solicitud(self, legajo, nombre, email, tipo, descripcion, materia, urgente, canal):
    estudiante = self.buscar_estudiante(legajo)
    error = None
    if estudiante is None:
        error = self._validar_datos_estudiante(legajo, nombre, email)
    if error is None:
        error = self._validar_solicitud(tipo, descripcion, materia, canal)
    if error is not None:
        print("Error: " + error)
        return False
    ...
    solicitud = self._crear_solicitud(contador, legajo, tipo, descripcion, materia, canal,
                                      self._calcular_prioridad(tipo, urgente, canal))
    self.solicitudes.append(solicitud)
    self._guardar()
```

Métodos extraídos: `_validar_datos_estudiante` (reutilizado por ambas altas), `_validar_solicitud`, `_calcular_prioridad`, `_crear_solicitud`, `_guardar` (con `with`), `_texto_prioridad`, `buscar_estudiante/solicitud/responsable`.
**Resultado:** CC promedio 11,3 → 5,7. Golden 8/8. Test nuevo `test_d2_...` en verde.

---

## R2 — Reemplazar literales mágicos por Enums

**Antes:** `"pendiente"`, `"en_proceso"`… como texto suelto; prioridades `1/2/3`; la lista de tipos copiada en `gestor.py` (dos veces) y en `main.py`.

**Después** (`modelos.py`):

```python
class Estado(str, Enum):
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    RESUELTA = "resuelta"
    RECHAZADA = "rechazada"

    @property
    def esta_abierta(self):
        return self in (Estado.PENDIENTE, Estado.EN_PROCESO)

class Prioridad(IntEnum):
    BAJA = 1
    MEDIA = 2
    ALTA = 3
```

Las condiciones `estado == "pendiente" or estado == "en_proceso"` (repetidas 4 veces) pasan a `Estado(...).esta_abierta`. Como los Enums heredan de `str`/`int`, el JSON no cambia.

---

## R3 — Move Method (reubicación de responsabilidad)

**Antes:** la regla de prioridad y la máquina de estados vivían en el gestor como condicionales.

```python
if ant == "pendiente":
    if nuevo == "en_proceso":
        ...
    elif nuevo == "rechazada":
        ok = True
elif ant == "en_proceso":
    if nuevo == "resuelta" or nuevo == "rechazada":
        ok = True
```

**Después:** cada regla se mueve a la clase que tiene los datos que usa.

```python
# modelos.py
_TRANSICIONES = {
    Estado.PENDIENTE: {Estado.EN_PROCESO, Estado.RECHAZADA},
    Estado.EN_PROCESO: {Estado.RESUELTA, Estado.RECHAZADA},
    Estado.RESUELTA: set(),
    Estado.RECHAZADA: set(),
}
def puede_pasar_a(self, nuevo):          # método de Estado
    return nuevo in _TRANSICIONES[self]

# prioridad.py
REGLAS_POR_DEFECTO = {
    TipoSolicitud.RECLAMO_NOTA: _segun_urgencia(Prioridad.ALTA, Prioridad.MEDIA),
    TipoSolicitud.EQUIVALENCIA: _fija(Prioridad.MEDIA),
    TipoSolicitud.CERTIFICADO: _segun_urgencia(Prioridad.MEDIA, Prioridad.BAJA),
    TipoSolicitud.BAJA_MATERIA: _fija(Prioridad.ALTA),
    TipoSolicitud.CAMBIO_COMISION: _segun_canal_presencial(Prioridad.MEDIA, Prioridad.BAJA),
}
```

En R6 se completa: `asignar_a()` y `cambiar_estado()` pasan a ser métodos de la entidad `Solicitud`.
**Principios:** SRP (el gestor deja de conocer reglas de negocio) y OCP (un tipo nuevo es una entrada nueva en el diccionario).

---

## R4 — Introduce Parameter Object

**Antes:** 8 parámetros posicionales, varios del mismo tipo (`str`), fáciles de invertir sin que nada falle.

```python
g.registrar_solicitud(legajo, nombre, email, tipo, descripcion, materia, urgente, canal)
```

**Después:**

```python
@dataclass(frozen=True)
class DatosSolicitud:
    legajo: str
    tipo: str
    descripcion: str
    materia: str = ""
    urgente: bool = False
    canal: str = Canal.WEB.value

    def validar(self): ...

g.registrar_solicitud(DatosSolicitud(legajo, tipo, descripcion, materia, urgente, canal),
                      DatosEstudiante(legajo, nombre, email))
```

Cada objeto valida sus propios datos (cohesión). En R6 se aplica la misma técnica a la búsqueda: `buscar(estado, tipo, legajo, prio_min)` → `buscar(FiltroSolicitudes(...))`.

---

## R5 — Extract Class (repositorio) + DIP

**Antes:** `open(ARCHIVO)` + `json.dump` en 5 métodos y dos variables globales (`ARCHIVO`, `contador`).

**Después:**

```python
class RepositorioSolicitudes(ABC):          # abstracción de la que depende la lógica
    @abstractmethod
    def obtener_solicitud(self, id_solicitud): ...
    @abstractmethod
    def guardar(self): ...
    ...

class RepositorioEnMemoria(RepositorioSolicitudes): ...    # para pruebas
class RepositorioJSON(RepositorioEnMemoria): ...           # mismo formato de archivo

class ServicioSolicitudes:
    def __init__(self, repositorio, politica_prioridad=None, reloj=fecha_de_hoy): ...
```

---

## R6 — Separar consulta de modificación y reemplazar códigos de error por excepciones

**Antes:** cada método del gestor imprimía y devolvía valores inconsistentes.

```python
def cambiar_estado(self, id_sol, nuevo):
    ...
    if sol == None:
        print("Error: no existe la solicitud #" + str(id_sol))
        return "error"            # en otros casos devuelve False o True
```

**Después:** el servicio lanza excepciones del dominio y la consola es la única que imprime.

```python
# servicio.py
def obtener_solicitud(self, id_solicitud):
    solicitud = self._repo.obtener_solicitud(id_solicitud)
    if solicitud is None:
        raise NoEncontradoError(f"no existe la solicitud #{id_solicitud}")
    return solicitud

# consola.py
try:
    accion()
except ErrorDeNegocio as error:
    self._escribir(f"Error: {error}")
```

También en este paso: `gestor.py` se elimina, `main.py` pasa a ser el composition root y se corrige D1 (`except:` genérico → `DatosDanadosError` sin sobrescribir el archivo).

---

## ¿Cómo sabemos que fueron refactorings *seguros*?

1. La red de seguridad (golden master) se escribió y se commiteó **antes** del primer cambio.
2. Se ejecutó después de **cada** commit de refactoring: 8/8 en todos.
3. La misma batería corrida sobre `estado-inicial` también da 8/8 → los tests describen el comportamiento original, no el nuevo.
4. Los únicos cambios de comportamiento (D1, D2) son intencionales, tienen su propio test y **fallan** en la versión inicial ([`evidencias/antes-despues-pruebas.txt`](evidencias/antes-despues-pruebas.txt)).
