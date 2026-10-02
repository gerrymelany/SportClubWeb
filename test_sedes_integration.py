import pytest

from src.sedes import (
    BusquedaInvalidaError,
    Sede,
    SedesNoDisponibleError,
    SedesRepositoryApi,
    SedesService,
)

pytestmark = pytest.mark.integration

RESPUESTA_API = [
    # Datos simulados que representan la respuesta de la API de sedes
    {"id": 1, "nombre": "SportClub Palermo", "zona": "Palermo", "provincia": "CABA"},
    {"id": 2, "nombre": "SportClub Córdoba Centro", "zona": "Centro", "provincia": "Córdoba"},
    {"id": 3, "nombre": "SportClub Cerrada", "zona": "Palermo", "provincia": "CABA", "activa": False},
]


class ClienteApiFalso:
    """Simula el cliente HTTP. Puede devolver datos o fallar."""

    def __init__(self, datos=None, falla=False):
        # Dependencia simulada: cliente HTTP que interactúa con la API
        self._datos = datos or []
        self._falla = falla
        self.rutas_consultadas = []

    def get(self, ruta):
        # Simula una solicitud GET a la API
        self.rutas_consultadas.append(ruta)
        if self._falla:
            raise ConnectionError("API caída")
        return self._datos


def armar_servicio(cliente):
    # Componente de integración: combina el repositorio y el servicio
    return SedesService(SedesRepositoryApi(cliente))


def test_flujo_completo_busqueda_con_resultados():
    # Validación: búsqueda exitosa con resultados
    cliente = ClienteApiFalso(RESPUESTA_API)
    servicio = armar_servicio(cliente)

    resultado = servicio.buscar("  cordoba ")

    assert resultado == [Sede(2, "SportClub Córdoba Centro", "Centro", "Córdoba")]
    assert cliente.rutas_consultadas == ["/sedes"]


def test_flujo_excluye_sedes_inactivas_que_vienen_de_la_api():
    # Validación: las sedes inactivas no se incluyen en los resultados
    servicio = armar_servicio(ClienteApiFalso(RESPUESTA_API))

    ids = [s.id for s in servicio.buscar("Palermo")]

    assert ids == [1]


def test_flujo_sin_resultados():
    # Validación: búsqueda sin resultados
    servicio = armar_servicio(ClienteApiFalso(RESPUESTA_API))

    assert servicio.buscar("Ushuaia") == []


def test_flujo_con_busqueda_invalida_no_llega_a_la_api():
    # Validación: búsqueda inválida no realiza solicitudes a la API
    cliente = ClienteApiFalso(RESPUESTA_API)
    servicio = armar_servicio(cliente)

    with pytest.raises(BusquedaInvalidaError):
        servicio.buscar("<script>")

    assert cliente.rutas_consultadas == []


def test_flujo_cuando_la_api_falla_se_informa_error_de_negocio():
    # Validación: manejo de errores cuando la API falla
    servicio = armar_servicio(ClienteApiFalso(falla=True))

    with pytest.raises(SedesNoDisponibleError):
        servicio.buscar("Palermo")
