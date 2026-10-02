import re
import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.e2e

BASE_URL = "https://www.sportclub.com.ar"
LINK_SEDES = "Conocé las sedes"
URL_SEDES = re.compile(r"sede", re.IGNORECASE)
PLACEHOLDER_BUSCADOR = re.compile(r"busc|zona|sede|ubicaci", re.IGNORECASE)
ZONA_A_BUSCAR = "Palermo"


def cerrar_banner_cookies_si_aparece(page: Page):
    # Componente auxiliar: cierra el banner de cookies si está visible
    boton = page.get_by_role("button", name=re.compile(r"aceptar|entendido|ok", re.IGNORECASE))
    if boton.count() and boton.first.is_visible():
        boton.first.click()


def test_buscar_sede_por_zona_desde_la_home(page: Page):
    # Validación: flujo completo de búsqueda de sedes desde la página principal
    page.goto(BASE_URL)
    cerrar_banner_cookies_si_aparece(page)

    # Interacción: clic en el enlace "Conocé las sedes"
    link_sedes = page.get_by_role("link", name=LINK_SEDES).first
    expect(link_sedes).to_be_visible()
    link_sedes.click()
    expect(page).to_have_url(URL_SEDES)

    # Interacción: uso del buscador para buscar una zona específica
    buscador = page.get_by_role("searchbox").or_(
        page.get_by_placeholder(PLACEHOLDER_BUSCADOR)
    ).first
    expect(buscador).to_be_visible()
    buscador.fill(ZONA_A_BUSCAR)
    buscador.press("Enter")

    # Validación: los resultados de la búsqueda son visibles
    resultados = page.get_by_text(re.compile(ZONA_A_BUSCAR, re.IGNORECASE))
    expect(resultados.first).to_be_visible()
