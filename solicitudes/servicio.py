"""Casos de uso del sistema.

Orquesta el dominio y el repositorio. No imprime ni lee de la consola (CS-11):
devuelve resultados o lanza excepciones de errores.py (CS-10).
"""
from dataclasses import dataclass
from datetime import date

from errores import DatosInvalidosError, NoEncontradoError, OperacionNoPermitidaError
from modelos import DatosEstudiante, Estado, Estudiante, Solicitud, es_valor_de
from prioridad import PoliticaPrioridad
from reportes import generar_reporte


def fecha_de_hoy():
    return date.today().isoformat()


@dataclass(frozen=True)
class ResultadoRegistro:
    solicitud: Solicitud
    estudiante_dado_de_alta: bool


class ServicioSolicitudes:
    def __init__(self, repositorio, politica_prioridad=None, reloj=fecha_de_hoy):
        self._repo = repositorio
        self._politica = politica_prioridad or PoliticaPrioridad()
        self._hoy = reloj

    # ---------------------------------------------------------- estudiantes
    def existe_estudiante(self, legajo):
        return self._repo.obtener_estudiante(legajo) is not None

    def registrar_estudiante(self, datos):
        self._validar(datos)
        if self.existe_estudiante(datos.legajo):
            raise DatosInvalidosError("ya existe un estudiante con ese legajo")
        estudiante = Estudiante.desde(datos)
        self._repo.agregar_estudiante(estudiante)
        self._repo.guardar()
        return estudiante

    # ---------------------------------------------------------- solicitudes
    def registrar_solicitud(self, datos, datos_estudiante=None):
        """Registra una solicitud. 'datos_estudiante' solo se usa si el legajo no existe.

        Se valida todo antes de modificar datos (corrige el defecto D2).
        """
        es_nuevo = not self.existe_estudiante(datos.legajo)
        if es_nuevo:
            datos_estudiante = datos_estudiante or DatosEstudiante(datos.legajo, "", "")
            self._validar(datos_estudiante)
        self._validar(datos)

        if es_nuevo:
            self._repo.agregar_estudiante(Estudiante.desde(datos_estudiante))
        solicitud = Solicitud.crear(self._repo.siguiente_id(), datos,
                                    self._politica.calcular(datos), self._hoy())
        self._repo.agregar_solicitud(solicitud)
        self._repo.guardar()
        return ResultadoRegistro(solicitud, es_nuevo)

    def asignar_responsable(self, id_solicitud, id_responsable):
        solicitud = self.obtener_solicitud(id_solicitud)
        responsable = self._repo.obtener_responsable(id_responsable)
        if responsable is None:
            raise NoEncontradoError(f"no existe el responsable {id_responsable}")
        solicitud.asignar_a(responsable, self._hoy())
        self._repo.guardar()
        return solicitud, responsable

    def cambiar_estado(self, id_solicitud, nuevo_estado):
        """Devuelve el estado anterior para que la interfaz pueda informarlo."""
        solicitud = self.obtener_solicitud(id_solicitud)
        anterior = solicitud.estado
        if not es_valor_de(Estado, nuevo_estado):
            raise OperacionNoPermitidaError(
                f"transicion invalida {anterior.value} -> {nuevo_estado}")
        solicitud.cambiar_estado(Estado(nuevo_estado), self._hoy())
        self._repo.guardar()
        return anterior

    # -------------------------------------------------------------- consultas
    def obtener_solicitud(self, id_solicitud):
        solicitud = self._repo.obtener_solicitud(id_solicitud)
        if solicitud is None:
            raise NoEncontradoError(f"no existe la solicitud #{id_solicitud}")
        return solicitud

    def obtener_detalle(self, id_solicitud):
        solicitud = self.obtener_solicitud(id_solicitud)
        return solicitud, self._repo.obtener_estudiante(solicitud.legajo)

    def buscar(self, filtro):
        """Solicitudes que cumplen el filtro, ordenadas por prioridad (desc) e id."""
        encontradas = [s for s in self._repo.listar_solicitudes() if filtro.acepta(s)]
        return sorted(encontradas, key=lambda s: (-s.prioridad, s.id))

    def listar_responsables(self):
        return self._repo.listar_responsables()

    def obtener_responsable(self, id_responsable):
        return self._repo.obtener_responsable(id_responsable)

    def generar_reporte(self):
        return generar_reporte(self._repo.listar_solicitudes(), self._repo.listar_responsables())

    # --------------------------------------------------------------- privados
    @staticmethod
    def _validar(datos):
        error = datos.validar()
        if error is not None:
            raise DatosInvalidosError(error)
