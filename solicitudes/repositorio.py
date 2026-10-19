"""Persistencia de datos detras de una abstraccion (DIP).

El gestor ya no sabe que los datos estan en un archivo JSON: depende de
RepositorioSolicitudes. Esto elimina las variables globales ARCHIVO y contador
y concentra en un solo lugar la lectura y escritura (CS-05, CS-11).
"""
import json
import os
from abc import ABC, abstractmethod
from copy import deepcopy

RUTA_POR_DEFECTO = "datos/solicitudes.json"

RESPONSABLES_INICIALES = [
    {"id": 1, "nombre": "Laura Gomez", "area": "Alumnado"},
    {"id": 2, "nombre": "Martin Sosa", "area": "Coordinacion"},
    {"id": 3, "nombre": "Paula Diaz", "area": "Bedelia"},
]


class RepositorioSolicitudes(ABC):
    """Contrato que necesita la logica de negocio para acceder a los datos."""

    def __init__(self):
        self.estudiantes = []
        self.responsables = deepcopy(RESPONSABLES_INICIALES)
        self.solicitudes = []
        self.ultimo_id = 0

    def siguiente_id(self):
        self.ultimo_id += 1
        return self.ultimo_id

    def buscar_estudiante(self, legajo):
        return next((e for e in self.estudiantes if e["legajo"] == legajo), None)

    def buscar_solicitud(self, id_solicitud):
        return next((s for s in self.solicitudes if s["id"] == id_solicitud), None)

    def buscar_responsable(self, id_responsable):
        return next((r for r in self.responsables if r["id"] == id_responsable), None)

    @abstractmethod
    def guardar(self):
        """Persiste el estado actual."""


class RepositorioJSON(RepositorioSolicitudes):
    """Implementacion concreta sobre un archivo JSON (mismo formato que la version inicial)."""

    def __init__(self, ruta=None):
        super().__init__()
        self.ruta = ruta or os.environ.get("SOLICITUDES_DATA", RUTA_POR_DEFECTO)
        self._cargar()

    def _cargar(self):
        try:
            with open(self.ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
            self.estudiantes = datos["estudiantes"]
            self.responsables = datos["responsables"]
            self.solicitudes = datos["solicitudes"]
            self.ultimo_id = datos["contador"]
        except:  # noqa: E722  (se corrige en R6, defecto D1)
            pass

    def guardar(self):
        with open(self.ruta, "w", encoding="utf-8") as archivo:
            json.dump({"estudiantes": self.estudiantes, "responsables": self.responsables,
                       "solicitudes": self.solicitudes, "contador": self.ultimo_id},
                      archivo, indent=2, ensure_ascii=False)
