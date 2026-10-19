"""Modelo del dominio: tipos, entidades y objetos de datos.

Reemplaza los strings y numeros 'magicos' (CS-07, CS-09) y los diccionarios
sueltos de la version inicial. Cada entidad conoce sus propias reglas.
"""
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import List, Optional

from errores import OperacionNoPermitidaError


# --------------------------------------------------------------------- tipos
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


# ------------------------------------------------- objetos de datos (entrada)
LONGITUD_LEGAJO = 5
LONGITUD_MINIMA_DESCRIPCION = 10


@dataclass(frozen=True)
class DatosEstudiante:
    """Parameter Object con los datos ingresados para dar de alta un estudiante."""
    legajo: str
    nombre: str
    email: str

    def validar(self):
        """Devuelve el mensaje del primer error encontrado o None si los datos son validos."""
        if not self.legajo.isdigit() or len(self.legajo) != LONGITUD_LEGAJO:
            return "el legajo debe tener 5 digitos"
        if "@" not in self.email or "." not in self.email.split("@")[-1]:
            return "email invalido"
        if self.nombre.strip() == "":
            return "el nombre no puede estar vacio"
        return None


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


@dataclass(frozen=True)
class FiltroSolicitudes:
    """Parameter Object para la busqueda (antes: buscar(estado, tipo, legajo, prio_min)).

    Un campo vacio (o prioridad_minima = 0) significa 'sin filtro'.
    """
    estado: str = ""
    tipo: str = ""
    legajo: str = ""
    prioridad_minima: int = 0

    def acepta(self, solicitud):
        return ((not self.estado or solicitud.estado == self.estado)
                and (not self.tipo or solicitud.tipo == self.tipo)
                and (not self.legajo or solicitud.legajo == self.legajo)
                and solicitud.prioridad >= self.prioridad_minima)


# ------------------------------------------------------------------ entidades
@dataclass
class Estudiante:
    legajo: str
    nombre: str
    email: str

    @classmethod
    def desde(cls, datos):
        return cls(datos.legajo, datos.nombre.strip(), datos.email)

    def to_dict(self):
        return {"legajo": self.legajo, "nombre": self.nombre, "email": self.email}

    @classmethod
    def from_dict(cls, datos):
        return cls(datos["legajo"], datos["nombre"], datos["email"])


@dataclass(frozen=True)
class Responsable:
    id: int
    nombre: str
    area: str

    def to_dict(self):
        return {"id": self.id, "nombre": self.nombre, "area": self.area}

    @classmethod
    def from_dict(cls, datos):
        return cls(datos["id"], datos["nombre"], datos["area"])


@dataclass
class Solicitud:  # pylint: disable=too-many-instance-attributes
    id: int
    legajo: str
    tipo: TipoSolicitud
    descripcion: str
    materia: str
    canal: Canal
    prioridad: Prioridad
    fecha: str
    estado: Estado = Estado.PENDIENTE
    responsable: Optional[int] = None
    historial: List[str] = field(default_factory=list)

    @classmethod
    def crear(cls, id_solicitud, datos, prioridad, hoy):
        solicitud = cls(
            id=id_solicitud,
            legajo=datos.legajo,
            tipo=TipoSolicitud(datos.tipo),
            descripcion=datos.descripcion.strip(),
            materia=datos.materia.strip(),
            canal=Canal(datos.canal),
            prioridad=prioridad,
            fecha=hoy,
        )
        solicitud.historial.append(f"{hoy} creada (pendiente)")
        return solicitud

    # Move Method: estas reglas estaban en GestorSolicitudes (CS-01, CS-08).
    def asignar_a(self, responsable, hoy):
        if not self.estado.esta_abierta:
            raise OperacionNoPermitidaError("la solicitud ya esta cerrada")
        self.responsable = responsable.id
        self.historial.append(f"{hoy} asignada a {responsable.nombre}")
        if self.estado == Estado.PENDIENTE:
            self._pasar_a(Estado.EN_PROCESO, hoy)

    def cambiar_estado(self, nuevo, hoy):
        if not self.estado.puede_pasar_a(nuevo):
            raise OperacionNoPermitidaError(
                f"transicion invalida {self.estado.value} -> {nuevo.value}")
        if nuevo == Estado.EN_PROCESO and self.responsable is None:
            raise OperacionNoPermitidaError(
                "no se puede pasar a en_proceso sin responsable asignado")
        self._pasar_a(nuevo, hoy)

    def _pasar_a(self, nuevo, hoy):
        self.historial.append(f"{hoy} {self.estado.value} -> {nuevo.value}")
        self.estado = nuevo

    def to_dict(self):
        return {
            "id": self.id,
            "legajo": self.legajo,
            "tipo": self.tipo.value,
            "descripcion": self.descripcion,
            "materia": self.materia,
            "canal": self.canal.value,
            "prioridad": int(self.prioridad),
            "estado": self.estado.value,
            "responsable": self.responsable,
            "fecha": self.fecha,
            "historial": list(self.historial),
        }

    @classmethod
    def from_dict(cls, datos):
        return cls(
            id=datos["id"],
            legajo=datos["legajo"],
            tipo=TipoSolicitud(datos["tipo"]),
            descripcion=datos["descripcion"],
            materia=datos["materia"],
            canal=Canal(datos["canal"]),
            prioridad=Prioridad(datos["prioridad"]),
            fecha=datos["fecha"],
            estado=Estado(datos["estado"]),
            responsable=datos["responsable"],
            historial=list(datos["historial"]),
        )
