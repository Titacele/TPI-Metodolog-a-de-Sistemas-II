"""Tipos del dominio. Reemplazan los strings y numeros 'magicos' de la version inicial."""
from dataclasses import dataclass
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


@dataclass(frozen=True)
class DatosEstudiante:
    """Parameter Object con los datos ingresados para dar de alta un estudiante."""
    legajo: str
    nombre: str
    email: str

    def validar(self):
        """Devuelve el mensaje del primer error encontrado o None si los datos son validos."""
        if not self.legajo.isdigit() or len(self.legajo) != 5:
            return "el legajo debe tener 5 digitos"
        if "@" not in self.email or "." not in self.email.split("@")[-1]:
            return "email invalido"
        if self.nombre.strip() == "":
            return "el nombre no puede estar vacio"
        return None


LONGITUD_MINIMA_DESCRIPCION = 10


@dataclass(frozen=True)
class DatosSolicitud:
    """Parameter Object que reemplaza los 8 parametros de registrar_solicitud (CS-03).

    'tipo' y 'canal' llegan como texto ingresado por el usuario; como Estado,
    TipoSolicitud y Canal heredan de str, se comparan directamente con esos textos.
    """
    legajo: str
    tipo: str
    descripcion: str
    materia: str = ""
    urgente: bool = False
    canal: str = Canal.WEB.value

    def validar(self):
        """Devuelve el mensaje del primer error encontrado o None si los datos son validos."""
        if not es_valor_de(TipoSolicitud, self.tipo):
            return "tipo de solicitud invalido"
        if len(self.descripcion.strip()) < LONGITUD_MINIMA_DESCRIPCION:
            return "la descripcion debe tener al menos 10 caracteres"
        if not es_valor_de(Canal, self.canal):
            return "canal invalido"
        if self.materia.strip() == "" and TipoSolicitud(self.tipo).requiere_materia:
            return "este tipo de solicitud requiere indicar la materia"
        return None
