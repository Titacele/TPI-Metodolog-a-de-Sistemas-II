"""Pruebas de la interfaz con entrada/salida inyectadas (sin subprocess)."""
from consola import Consola
from repositorio import RepositorioEnMemoria
from servicio import ServicioSolicitudes


def ejecutar_consola(entradas):
    pendientes = iter(entradas)
    salida = []
    servicio = ServicioSolicitudes(RepositorioEnMemoria(), reloj=lambda: "2026-10-20")
    Consola(servicio, leer=lambda _mensaje: next(pendientes), escribir=salida.append).ejecutar()
    return salida


def test_opcion_invalida_y_salida():
    salida = ejecutar_consola(["9", "0"])
    assert "Opcion invalida" in salida
    assert salida[-1] == "Hasta luego"


def test_errores_de_negocio_se_muestran_con_prefijo():
    salida = ejecutar_consola(["4", "abc", "6", "7", "0"])
    assert "Error: ID invalido" in salida
    assert "Error: no existe la solicitud #7" in salida
