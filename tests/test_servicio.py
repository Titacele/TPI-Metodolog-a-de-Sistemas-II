"""Pruebas de los casos de uso con repositorio en memoria y reloj fijo (sin archivos ni consola)."""
import pytest

from errores import DatosInvalidosError, NoEncontradoError, OperacionNoPermitidaError
from modelos import DatosEstudiante, DatosSolicitud, Estado, FiltroSolicitudes, Prioridad
from repositorio import RepositorioEnMemoria
from servicio import ServicioSolicitudes

HOY = "2026-10-20"


class RepositorioEspia(RepositorioEnMemoria):
    """Doble de prueba: cuenta cuantas veces se guardo."""

    def __init__(self):
        super().__init__()
        self.guardados = 0

    def guardar(self):
        self.guardados += 1


@pytest.fixture
def repo():
    return RepositorioEspia()


@pytest.fixture
def servicio(repo):
    return ServicioSolicitudes(repo, reloj=lambda: HOY)


def registrar(servicio, legajo="10001", tipo="certificado", **extra):
    datos = DatosSolicitud(legajo, tipo, "Descripcion suficientemente larga", **extra)
    return servicio.registrar_solicitud(datos, DatosEstudiante(legajo, "Ana Perez", "ana@mail.com"))


def test_registrar_solicitud_para_estudiante_nuevo(servicio, repo):
    resultado = registrar(servicio)
    assert resultado.estudiante_dado_de_alta
    assert resultado.solicitud.id == 1
    assert resultado.solicitud.fecha == HOY
    assert resultado.solicitud.prioridad == Prioridad.BAJA
    assert repo.obtener_estudiante("10001").nombre == "Ana Perez"
    assert repo.guardados == 1


def test_segunda_solicitud_reutiliza_estudiante_e_incrementa_id(servicio):
    registrar(servicio)
    resultado = registrar(servicio)
    assert not resultado.estudiante_dado_de_alta
    assert resultado.solicitud.id == 2


def test_solicitud_invalida_no_modifica_nada(servicio, repo):
    with pytest.raises(DatosInvalidosError, match="tipo de solicitud invalido"):
        registrar(servicio, tipo="inscripcion")
    assert repo.obtener_estudiante("10001") is None
    assert repo.listar_solicitudes() == []
    assert repo.guardados == 0


def test_registrar_estudiante_duplicado(servicio):
    servicio.registrar_estudiante(DatosEstudiante("10001", "Ana", "ana@mail.com"))
    with pytest.raises(DatosInvalidosError, match="ya existe"):
        servicio.registrar_estudiante(DatosEstudiante("10001", "Otra", "otra@mail.com"))


def test_asignar_responsable(servicio):
    registrar(servicio)
    solicitud, responsable = servicio.asignar_responsable(1, 2)
    assert responsable.nombre == "Martin Sosa"
    assert solicitud.estado == Estado.EN_PROCESO


@pytest.mark.parametrize("id_solicitud, id_responsable, mensaje", [
    (99, 1, "no existe la solicitud #99"),
    (1, 9, "no existe el responsable 9"),
])
def test_asignar_con_ids_inexistentes(servicio, id_solicitud, id_responsable, mensaje):
    registrar(servicio)
    with pytest.raises(NoEncontradoError, match=mensaje):
        servicio.asignar_responsable(id_solicitud, id_responsable)


def test_cambiar_estado_devuelve_estado_anterior(servicio):
    registrar(servicio)
    servicio.asignar_responsable(1, 1)
    assert servicio.cambiar_estado(1, "resuelta") == Estado.EN_PROCESO


def test_cambiar_a_estado_inexistente(servicio):
    registrar(servicio)
    with pytest.raises(OperacionNoPermitidaError, match="pendiente -> cerrada"):
        servicio.cambiar_estado(1, "cerrada")


def test_buscar_ordena_por_prioridad_y_id(servicio):
    registrar(servicio, tipo="certificado")                         # 1 BAJA
    registrar(servicio, tipo="baja_materia", materia="Legislacion")  # 2 ALTA
    registrar(servicio, tipo="certificado", urgente=True)           # 3 MEDIA
    ids = [s.id for s in servicio.buscar(FiltroSolicitudes())]
    assert ids == [2, 3, 1]


def test_reporte(servicio):
    registrar(servicio)
    registrar(servicio, tipo="baja_materia", materia="Legislacion")
    servicio.asignar_responsable(2, 3)
    servicio.cambiar_estado(1, "rechazada")
    reporte = servicio.generar_reporte()
    assert reporte.total == 2
    assert reporte.por_estado[Estado.RECHAZADA] == 1
    assert reporte.abiertas_por_prioridad[Prioridad.ALTA] == 1
    assert [c for _, c in reporte.carga_por_responsable] == [0, 0, 1]
    assert reporte.porcentaje_cerradas == 50.0


def test_reporte_vacio(servicio):
    assert servicio.generar_reporte().porcentaje_cerradas is None
