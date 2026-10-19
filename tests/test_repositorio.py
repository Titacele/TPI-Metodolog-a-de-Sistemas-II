"""Pruebas de persistencia: compatibilidad de formato y manejo de archivos danados."""
import json
import shutil
from pathlib import Path

import pytest

from errores import DatosDanadosError
from repositorio import RepositorioEnMemoria, RepositorioJSON, RepositorioSolicitudes

DATOS_EJEMPLO = Path(__file__).resolve().parent.parent / "datos" / "solicitudes.json"


def test_lee_y_reescribe_archivo_de_la_version_inicial_sin_cambios(tmp_path):
    copia = tmp_path / "datos.json"
    shutil.copy(DATOS_EJEMPLO, copia)
    original = json.loads(copia.read_text(encoding="utf-8"))

    repo = RepositorioJSON(str(copia))
    repo.guardar()

    assert json.loads(copia.read_text(encoding="utf-8")) == original
    assert len(repo.listar_solicitudes()) == 6


def test_archivo_inexistente_arranca_con_responsables_iniciales(tmp_path):
    repo = RepositorioJSON(str(tmp_path / "nuevo.json"))
    assert [r.nombre for r in repo.listar_responsables()] == ["Laura Gomez", "Martin Sosa", "Paula Diaz"]
    assert repo.siguiente_id() == 1


@pytest.mark.parametrize("contenido", ["{ esto no es json", '{"estudiantes": []}', "[]"])
def test_archivo_danado_lanza_error_y_no_se_modifica(tmp_path, contenido):
    archivo = tmp_path / "datos.json"
    archivo.write_text(contenido, encoding="utf-8")
    with pytest.raises(DatosDanadosError):
        RepositorioJSON(str(archivo))
    assert archivo.read_text(encoding="utf-8") == contenido


@pytest.mark.parametrize("clase", [RepositorioEnMemoria, RepositorioJSON])
def test_implementaciones_intercambiables(clase, tmp_path):
    """LSP: ambas implementaciones cumplen el mismo contrato."""
    repo = clase(str(tmp_path / "d.json")) if clase is RepositorioJSON else clase()
    assert isinstance(repo, RepositorioSolicitudes)
    assert repo.obtener_solicitud(1) is None
    assert repo.siguiente_id() == 1
    repo.guardar()
