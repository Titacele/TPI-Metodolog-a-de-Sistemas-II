"""Tipos del dominio. Reemplazan los strings y numeros 'magicos' de la version inicial."""
from enum import Enum, IntEnum


class Estado(str, Enum):
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    RESUELTA = "resuelta"
    RECHAZADA = "rechazada"

    @property
    def esta_abierta(self):
        return self in (Estado.PENDIENTE, Estado.EN_PROCESO)

    def puede_pasar_a(self, nuevo):
        return nuevo in _TRANSICIONES[self]


# Maquina de estados: antes eran if anidados dentro de cambiar_estado (CS-08).
_TRANSICIONES = {
    Estado.PENDIENTE: {Estado.EN_PROCESO, Estado.RECHAZADA},
    Estado.EN_PROCESO: {Estado.RESUELTA, Estado.RECHAZADA},
    Estado.RESUELTA: set(),
    Estado.RECHAZADA: set(),
}


class TipoSolicitud(str, Enum):
    CERTIFICADO = "certificado"
    EQUIVALENCIA = "equivalencia"
    CAMBIO_COMISION = "cambio_comision"
    RECLAMO_NOTA = "reclamo_nota"
    BAJA_MATERIA = "baja_materia"

    @property
    def requiere_materia(self):
        return self in (TipoSolicitud.EQUIVALENCIA, TipoSolicitud.RECLAMO_NOTA,
                        TipoSolicitud.BAJA_MATERIA)

    @classmethod
    def valores(cls):
        return [tipo.value for tipo in cls]


class Canal(str, Enum):
    WEB = "web"
    PRESENCIAL = "presencial"
    EMAIL = "email"


class Prioridad(IntEnum):
    BAJA = 1
    MEDIA = 2
    ALTA = 3

    @property
    def etiqueta(self):
        return self.name


def es_valor_de(enum_cls, valor):
    """Indica si 'valor' es uno de los valores validos del Enum."""
    return valor in {miembro.value for miembro in enum_cls}
