"""Pruebas unitarias del dominio (patron AAA: Arrange / Act / Assert)."""
import pytest

from errores import OperacionNoPermitidaError
from modelos import (DatosEstudiante, DatosSolicitud, Estado, FiltroSolicitudes, Prioridad,
                     Responsable, Solicitud)

HOY = "2026-10-20"
RESPONSABLE = Responsable(1, "Laura Gomez", "Alumnado")


def nueva_solicitud(**cambios):
    datos = DatosSolicitud(legajo="10001", tipo="certificado", descripcion="Certificado de alumno regular")
    solicitud = Solicitud.crear(1, datos, Prioridad.BAJA, HOY)
    for campo, valor in cambios.items():
        setattr(solicitud, campo, valor)
    return solicitud


@pytest.mark.parametrize("actual, nuevo, permitido", [
    (Estado.PENDIENTE, Estado.EN_PROCESO, True),
    (Estado.PENDIENTE, Estado.RECHAZADA, True),
    (Estado.PENDIENTE, Estado.RESUELTA, False),
    (Estado.EN_PROCESO, Estado.RESUELTA, True),
    (Estado.EN_PROCESO, Estado.RECHAZADA, True),
    (Estado.EN_PROCESO, Estado.PENDIENTE, False),
    (Estado.RESUELTA, Estado.EN_PROCESO, False),
    (Estado.RECHAZADA, Estado.PENDIENTE, False),
])
def test_tabla_de_transiciones(actual, nuevo, permitido):
    assert actual.puede_pasar_a(nuevo) is permitido


@pytest.mark.parametrize("datos, error", [
    (DatosEstudiante("123", "Ana", "a@b.com"), "el legajo debe tener 5 digitos"),
    (DatosEstudiante("12a45", "Ana", "a@b.com"), "el legajo debe tener 5 digitos"),
    (DatosEstudiante("12345", "Ana", "ab.com"), "email invalido"),
    (DatosEstudiante("12345", "Ana", "a@bcom"), "email invalido"),
    (DatosEstudiante("12345", "  ", "a@b.com"), "el nombre no puede estar vacio"),
    (DatosEstudiante("12345", "Ana", "a@b.com"), None),
])
def test_validacion_de_estudiante(datos, error):
    assert datos.validar() == error


@pytest.mark.parametrize("cambios, error", [
    ({"tipo": "inscripcion"}, "tipo de solicitud invalido"),
    ({"descripcion": "corta"}, "la descripcion debe tener al menos 10 caracteres"),
    ({"canal": "fax"}, "canal invalido"),
    ({"tipo": "equivalencia"}, "este tipo de solicitud requiere indicar la materia"),
    ({"tipo": "equivalencia", "materia": "Bases de Datos I"}, None),
    ({}, None),
])
def test_validacion_de_solicitud(cambios, error):
    base = {"legajo": "10001", "tipo": "certificado", "descripcion": "Descripcion valida", "canal": "web"}
    base.update(cambios)
    assert DatosSolicitud(**base).validar() == error


def test_crear_solicitud_queda_pendiente_con_historial():
    solicitud = nueva_solicitud()
    assert solicitud.estado == Estado.PENDIENTE
    assert solicitud.responsable is None
    assert solicitud.historial == [f"{HOY} creada (pendiente)"]


def test_asignar_pendiente_pasa_a_en_proceso():
    # Arrange
    solicitud = nueva_solicitud()
    # Act
    solicitud.asignar_a(RESPONSABLE, HOY)
    # Assert
    assert solicitud.responsable == 1
    assert solicitud.estado == Estado.EN_PROCESO
    assert solicitud.historial[-2:] == [f"{HOY} asignada a Laura Gomez", f"{HOY} pendiente -> en_proceso"]


def test_reasignar_en_proceso_no_cambia_estado():
    solicitud = nueva_solicitud(estado=Estado.EN_PROCESO, responsable=2)
    solicitud.asignar_a(RESPONSABLE, HOY)
    assert solicitud.estado == Estado.EN_PROCESO
    assert solicitud.historial[-1] == f"{HOY} asignada a Laura Gomez"


@pytest.mark.parametrize("estado", [Estado.RESUELTA, Estado.RECHAZADA])
def test_no_se_puede_asignar_una_solicitud_cerrada(estado):
    solicitud = nueva_solicitud(estado=estado)
    with pytest.raises(OperacionNoPermitidaError, match="ya esta cerrada"):
        solicitud.asignar_a(RESPONSABLE, HOY)


def test_no_pasa_a_en_proceso_sin_responsable():
    solicitud = nueva_solicitud()
    with pytest.raises(OperacionNoPermitidaError, match="sin responsable"):
        solicitud.cambiar_estado(Estado.EN_PROCESO, HOY)


def test_transicion_invalida_informa_estados():
    solicitud = nueva_solicitud()
    with pytest.raises(OperacionNoPermitidaError, match="pendiente -> resuelta"):
        solicitud.cambiar_estado(Estado.RESUELTA, HOY)
    assert solicitud.estado == Estado.PENDIENTE


def test_serializacion_ida_y_vuelta_conserva_datos():
    solicitud = nueva_solicitud()
    solicitud.asignar_a(RESPONSABLE, HOY)
    assert Solicitud.from_dict(solicitud.to_dict()) == solicitud


def test_filtro_vacio_acepta_todo_y_filtros_combinados():
    solicitud = nueva_solicitud()
    assert FiltroSolicitudes().acepta(solicitud)
    assert FiltroSolicitudes(estado="pendiente", tipo="certificado", legajo="10001").acepta(solicitud)
    assert not FiltroSolicitudes(prioridad_minima=2).acepta(solicitud)
    assert not FiltroSolicitudes(legajo="99999").acepta(solicitud)
