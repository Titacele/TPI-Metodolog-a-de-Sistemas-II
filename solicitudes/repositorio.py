"""Persistencia de datos detras de una abstraccion (DIP).

La logica de negocio depende de RepositorioSolicitudes. Hay dos implementaciones
intercambiables (LSP): RepositorioEnMemoria, usada en las pruebas unitarias, y
RepositorioJSON, que guarda en el mismo formato de archivo que la version inicial.
"""
import json
import os
from abc import ABC, abstractmethod

from errores import DatosDanadosError
from modelos import Estudiante, Responsable, Solicitud

RUTA_POR_DEFECTO = "datos/solicitudes.json"

RESPONSABLES_INICIALES = (
    Responsable(1, "Laura Gomez", "Alumnado"),
    Responsable(2, "Martin Sosa", "Coordinacion"),
    Responsable(3, "Paula Diaz", "Bedelia"),
)


class RepositorioSolicitudes(ABC):
    """Contrato que necesita la logica de negocio para acceder a los datos."""

    @abstractmethod
    def obtener_estudiante(self, legajo):
        """Devuelve el Estudiante o None."""

    @abstractmethod
    def agregar_estudiante(self, estudiante):
        """Agrega un estudiante nuevo."""

    @abstractmethod
    def obtener_responsable(self, id_responsable):
        """Devuelve el Responsable o None."""

    @abstractmethod
    def listar_responsables(self):
        """Devuelve todos los responsables."""

    @abstractmethod
    def obtener_solicitud(self, id_solicitud):
        """Devuelve la Solicitud o None."""

    @abstractmethod
    def listar_solicitudes(self):
        """Devuelve todas las solicitudes."""

    @abstractmethod
    def agregar_solicitud(self, solicitud):
        """Agrega una solicitud nueva."""

    @abstractmethod
    def siguiente_id(self):
        """Reserva y devuelve el proximo id de solicitud."""

    @abstractmethod
    def guardar(self):
        """Persiste los cambios realizados."""


class RepositorioEnMemoria(RepositorioSolicitudes):
    """Implementacion en memoria. No persiste nada: ideal para pruebas."""

    def __init__(self, responsables=RESPONSABLES_INICIALES):
        self._estudiantes = {}
        self._responsables = {r.id: r for r in responsables}
        self._solicitudes = {}
        self._ultimo_id = 0

    def obtener_estudiante(self, legajo):
        return self._estudiantes.get(legajo)

    def agregar_estudiante(self, estudiante):
        self._estudiantes[estudiante.legajo] = estudiante

    def obtener_responsable(self, id_responsable):
        return self._responsables.get(id_responsable)

    def listar_responsables(self):
        return list(self._responsables.values())

    def obtener_solicitud(self, id_solicitud):
        return self._solicitudes.get(id_solicitud)

    def listar_solicitudes(self):
        return list(self._solicitudes.values())

    def agregar_solicitud(self, solicitud):
        self._solicitudes[solicitud.id] = solicitud

    def siguiente_id(self):
        self._ultimo_id += 1
        return self._ultimo_id

    def guardar(self):
        """En memoria no hay nada que guardar."""


class RepositorioJSON(RepositorioEnMemoria):
    """Guarda los datos en un archivo JSON compatible con la version inicial."""

    def __init__(self, ruta=None):
        super().__init__()
        self.ruta = ruta or os.environ.get("SOLICITUDES_DATA", RUTA_POR_DEFECTO)
        self._cargar()

    def _cargar(self):
        if not os.path.exists(self.ruta):
            return  # primera ejecucion: se arranca con los responsables iniciales
        try:
            with open(self.ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
            self._estudiantes = {e["legajo"]: Estudiante.from_dict(e) for e in datos["estudiantes"]}
            self._responsables = {r["id"]: Responsable.from_dict(r) for r in datos["responsables"]}
            self._solicitudes = {s["id"]: Solicitud.from_dict(s) for s in datos["solicitudes"]}
            self._ultimo_id = datos["contador"]
        except (OSError, ValueError, KeyError, TypeError) as error:
            # Antes: 'except:' que reiniciaba los datos y luego los sobrescribia (defecto D1).
            raise DatosDanadosError(
                f"no se pudo leer el archivo de datos '{self.ruta}' ({error.__class__.__name__}). "
                "No se modifico el archivo: reparelo o restaure una copia de seguridad."
            ) from error

    def guardar(self):
        datos = {
            "estudiantes": [e.to_dict() for e in self._estudiantes.values()],
            "responsables": [r.to_dict() for r in self._responsables.values()],
            "solicitudes": [s.to_dict() for s in self._solicitudes.values()],
            "contador": self._ultimo_id,
        }
        # Escritura atomica: si el programa se corta a mitad de camino, el archivo
        # anterior queda intacto (observacion CR-04 del code review).
        temporal = f"{self.ruta}.tmp"
        with open(temporal, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=2, ensure_ascii=False)
        os.replace(temporal, self.ruta)
