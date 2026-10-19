"""Punto de entrada: arma las dependencias y arranca la consola (composition root)."""
import sys

from consola import Consola
from errores import DatosDanadosError
from repositorio import RepositorioJSON
from servicio import ServicioSolicitudes


def main():
    try:
        repositorio = RepositorioJSON()
    except DatosDanadosError as error:
        print(f"Error: {error}")
        return 1
    Consola(ServicioSolicitudes(repositorio)).ejecutar()
    return 0


if __name__ == "__main__":
    sys.exit(main())
