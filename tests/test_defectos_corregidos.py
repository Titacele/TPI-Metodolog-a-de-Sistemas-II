"""Tests de regresion de los defectos encontrados en el diagnostico.

Estos casos NO estan en el golden master porque la version inicial se comportaba mal:
son mejoras de comportamiento documentadas (docs/01-diagnostico.md, D1 y D2).
"""
from utils import ejecutar


def test_d2_solicitud_invalida_no_da_de_alta_al_estudiante(tmp_path):
    datos = tmp_path / "datos.json"
    entradas = [
        "2", "40001", "Luis Vega", "luis@mail.com", "inscripcion",
        "Quiero inscribirme a una materia", "", "n", "web",
        "1", "40001", "Luis Vega", "luis@mail.com",
        "0",
    ]
    _, salida, _ = ejecutar(entradas, datos)
    assert "Error: tipo de solicitud invalido" in salida
    assert "Se dio de alta" not in salida
    assert "Estudiante registrado: 40001 - Luis Vega" in salida


def test_d1_json_danado_no_se_sobrescribe(tmp_path):
    datos = tmp_path / "datos.json"
    contenido_original = '{"estudiantes": [{"legajo": "10001", "nombre": "Ana", "email": "a@b.com"}]'
    datos.write_text(contenido_original, encoding="utf-8")
    codigo, salida, _ = ejecutar(["1", "10009", "Zoe Paz", "zoe@mail.com", "0"], datos)
    assert codigo == 1
    assert "Error: no se pudo leer el archivo de datos" in salida
    assert "Estudiante registrado" not in salida
    assert datos.read_text(encoding="utf-8") == contenido_original
