"""Pruebas de la politica de prioridad (una regla por tipo)."""
import pytest

from modelos import DatosSolicitud, Prioridad, TipoSolicitud
from prioridad import PoliticaPrioridad


def datos(tipo, urgente=False, canal="web"):
    return DatosSolicitud("10001", tipo, "Descripcion de prueba", "Materia", urgente, canal)


@pytest.mark.parametrize("tipo, urgente, canal, esperada", [
    ("reclamo_nota", True, "web", Prioridad.ALTA),
    ("reclamo_nota", False, "web", Prioridad.MEDIA),
    ("equivalencia", True, "web", Prioridad.MEDIA),
    ("certificado", True, "web", Prioridad.MEDIA),
    ("certificado", False, "web", Prioridad.BAJA),
    ("baja_materia", False, "email", Prioridad.ALTA),
    ("cambio_comision", False, "presencial", Prioridad.MEDIA),
    ("cambio_comision", True, "web", Prioridad.BAJA),
])
def test_reglas_de_prioridad(tipo, urgente, canal, esperada):
    assert PoliticaPrioridad().calcular(datos(tipo, urgente, canal)) == esperada


def test_se_puede_cambiar_una_regla_sin_modificar_la_politica():
    """OCP: la politica se extiende/configura desde afuera."""
    politica = PoliticaPrioridad({TipoSolicitud.CERTIFICADO: lambda d: Prioridad.ALTA})
    assert politica.calcular(datos("certificado")) == Prioridad.ALTA
