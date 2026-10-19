"""Politica de prioridad de las solicitudes.

Antes vivia como una cadena if/elif dentro del gestor (CS-08). Ahora cada tipo
tiene su propia regla registrada en un diccionario: agregar un tipo nuevo es
agregar una entrada, sin modificar la logica existente (OCP).
"""
from modelos import Canal, Prioridad, TipoSolicitud


def _segun_urgencia(si_urgente, si_no_urgente):
    return lambda datos: si_urgente if datos.urgente else si_no_urgente


def _fija(prioridad):
    return lambda datos: prioridad


def _segun_canal_presencial(si_presencial, si_no):
    return lambda datos: si_presencial if datos.canal == Canal.PRESENCIAL else si_no


REGLAS_POR_DEFECTO = {
    TipoSolicitud.RECLAMO_NOTA: _segun_urgencia(Prioridad.ALTA, Prioridad.MEDIA),
    TipoSolicitud.EQUIVALENCIA: _fija(Prioridad.MEDIA),
    TipoSolicitud.CERTIFICADO: _segun_urgencia(Prioridad.MEDIA, Prioridad.BAJA),
    TipoSolicitud.BAJA_MATERIA: _fija(Prioridad.ALTA),
    TipoSolicitud.CAMBIO_COMISION: _segun_canal_presencial(Prioridad.MEDIA, Prioridad.BAJA),
}


class PoliticaPrioridad:
    """Calcula la prioridad de una solicitud a partir de sus datos."""

    def __init__(self, reglas=None):
        self._reglas = dict(reglas or REGLAS_POR_DEFECTO)

    def calcular(self, datos):
        """'datos' debe exponer .tipo (TipoSolicitud), .urgente (bool) y .canal (Canal)."""
        return self._reglas[datos.tipo](datos)
