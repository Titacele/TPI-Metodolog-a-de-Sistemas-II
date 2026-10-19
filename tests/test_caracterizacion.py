"""Tests de caracterizacion (golden master).

Fijan el comportamiento externo de la version inicial: lo que se ve por consola y
lo que queda guardado en el archivo JSON. Se generaron ANTES de refactorizar
(ver tests/generar_golden.py) y deben seguir pasando despues de cada refactoring.
"""
import pytest

from escenarios import ESCENARIOS
from utils import GOLDEN, ejecutar_escenario


@pytest.mark.parametrize("nombre", sorted(ESCENARIOS))
def test_salida_por_consola_igual_a_version_inicial(nombre, tmp_path):
    salida, _ = ejecutar_escenario(ESCENARIOS[nombre], tmp_path / "datos.json")
    esperado = (GOLDEN / f"{nombre}.salida.txt").read_text(encoding="utf-8")
    assert salida == esperado


@pytest.mark.parametrize("nombre", sorted(ESCENARIOS))
def test_datos_persistidos_iguales_a_version_inicial(nombre, tmp_path):
    _, datos = ejecutar_escenario(ESCENARIOS[nombre], tmp_path / "datos.json")
    esperado = (GOLDEN / f"{nombre}.datos.json").read_text(encoding="utf-8")
    assert datos == esperado
