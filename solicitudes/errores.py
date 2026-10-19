"""Excepciones del dominio.

Reemplazan la mezcla de retornos True / False / "error" / None y los print()
dentro de la logica (CS-10). Quien llama decide como mostrar el error.
"""


class ErrorDeNegocio(Exception):
    """Base de los errores esperables que se informan al usuario."""


class DatosInvalidosError(ErrorDeNegocio):
    """Los datos ingresados no cumplen las reglas de validacion."""


class NoEncontradoError(ErrorDeNegocio):
    """No existe la entidad buscada."""


class OperacionNoPermitidaError(ErrorDeNegocio):
    """La operacion no es valida para el estado actual de la solicitud."""


class DatosDanadosError(Exception):
    """El archivo de datos existe pero no se puede interpretar.

    No hereda de ErrorDeNegocio porque no es un error del usuario: el sistema
    debe detenerse sin sobrescribir el archivo (defecto D1).
    """
