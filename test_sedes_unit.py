from unittest.mock import Mock

import pytest

from src.sedes import (
    BusquedaInvalidaError,
    Sede,
    SedesService,
    normalizar,
    validar_busqueda,
)

pytestmark = pytest.mark.unit

SEDES = [
    Sede(1, "SportClub Palermo", "Palermo", "CABA"),
    Sede(2, "SportClub Córdoba Centro", "Centro", "Córdoba"),
    Sede(3, "SportClub Belgrano", "Belgrano", "CABA"),
    Sede(4, "SportClub Cerrada", "Palermo", "CABA", activa=False),
]


@pytest.fixture
def service():
    repo = Mock()  # dependencia simulada
    repo.obtener_todas.return_value = SEDES
    return SedesService(repo)


# ---------- normalizar() ----------
@pytest.mark.parametrize(
    "entrada, esperado",
    [
        ("PALERMO", "palermo"),
        ("  Palermo  ", "palermo"),
        ("Córdoba", "cordoba"),
        ("san   isidro", "san isidro"),
    ],
)
def test_normalizar_deja_texto_comparable(entrada, esperado):
    assert normalizar(entrada) == esperado


# ---------- validar_busqueda() ----------
def test_validar_devuelve_texto_sin_espacios_extra():
    assert validar_busqueda("  Palermo ") == "Palermo"


@pytest.mark.parametrize("texto", [None, "", "   "])
def test_validar_rechaza_vacio(texto):
    with pytest.raises(BusquedaInvalidaError):
        validar_busqueda(texto)


def test_validar_rechaza_menos_del_minimo():
    with pytest.raises(BusquedaInvalidaError):
        validar_busqueda("a")


def test_validar_acepta_exactamente_el_minimo():
    assert validar_busqueda("ab") == "ab"


def test_validar_rechaza_mas_del_maximo():
    with pytest.raises(BusquedaInvalidaError):
        validar_busqueda("a" * 51)


@pytest.mark.parametrize("texto", ["<script>", "palermo; DROP", "pa$lermo"])
def test_validar_rechaza_caracteres_invalidos(texto):
    with pytest.raises(BusquedaInvalidaError):
        validar_busqueda(texto)


# ---------- SedesService.buscar() ----------
def test_buscar_por_zona(service):
    resultado = service.buscar("Belgrano")
    assert [s.id for s in resultado] == [3]


def test_buscar_ignora_mayusculas_y_tildes(service):
    assert [s.id for s in service.buscar("CORDOBA")] == [2]


def test_buscar_sin_resultados_devuelve_lista_vacia(service):
    assert service.buscar("Ushuaia") == []


def test_buscar_excluye_sedes_inactivas(service):
    ids = [s.id for s in service.buscar("Palermo")]
    assert ids == [1]


def test_buscar_con_texto_invalido_no_consulta_el_repositorio(service):
    with pytest.raises(BusquedaInvalidaError):
        service.buscar("")
    service._repository.obtener_todas.assert_not_called()


def test_buscar_ordena_alfabeticamente_por_nombre(service):
    nombres = [s.nombre for s in service.buscar("SportClub")]
    assert nombres == sorted(nombres)
