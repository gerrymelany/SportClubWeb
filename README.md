# Challenge QA Semi Senior – Testing Web (2.2, 2.3 y 2.4)

**Sección seleccionada:** "Conocé las sedes" (filtrar sedes por nombre, zona o provincia) – landing sportclub.com.ar
**Herramientas:** Python + `pytest` (unit e integration, con `unittest.mock`) y `pytest-playwright` (E2E).

## Por qué esta sección
Es la pregunta previa a asociarse ("¿tengo una sede cerca?"), tiene reglas claras y observables, y se puede
probar sin pagos ni acciones irreversibles. Permite cubrir las tres consignas con un solo flujo funcional.

## 2.2 Unit Testing
**Comportamiento representado** (`src/sedes.py`):
- `normalizar()`: texto en minúsculas, sin tildes y sin espacios sobrantes.
- `validar_busqueda()`: no vacía, entre 2 y 50 caracteres, sin caracteres especiales.
- `SedesService.buscar()`: filtra por nombre, zona o provincia; solo sedes activas; orden alfabético.

**Supuestos:** el sitio busca sin distinguir mayúsculas ni tildes; las sedes inactivas no se muestran; los límites
de 2 y 50 caracteres son definidos por mí (no se pudieron confirmar en el sitio real).

**Casos unitarios** (`tests/unit/test_sedes_unit.py`, el repositorio se simula con `Mock`):
normalización (4 variantes) · validación: vacío/None/espacios, mínimo, justo el mínimo, máximo, caracteres inválidos ·
búsqueda: por zona, sin importar mayúsculas/tildes, sin resultados, excluye inactivas, texto inválido no consulta
el repositorio, orden alfabético.

## 2.3 Integration Testing
**Componentes que participan (reales):** `SedesService` + `validar_busqueda`/`normalizar` + `SedesRepositoryApi`.
**Dependencia simulada:** el cliente HTTP (`ClienteApiFalso`), sin llamadas de red.
**Comportamiento validado** (`tests/integration/test_sedes_integration.py`): el JSON de la API se convierte en
`Sede`, se filtra con las reglas de negocio y se devuelve; las sedes inactivas se excluyen; una búsqueda inválida
no llega a la API; si la API falla, se informa un error de negocio (`SedesNoDisponibleError`).

## 2.4 E2E
**Flujo:** Home → "Conocé las sedes" → buscar "Palermo" → verificar que aparece al menos una sede coincidente.
**Rutas:** `https://www.sportclub.com.ar` y la ruta de sedes (validada con regex `/sede/`).
**Selectores:** `get_by_role` y `get_by_placeholder` primero, `get_by_text` para validar. Todo está concentrado
al inicio de `tests/e2e/test_sedes_e2e.py`.
**Validaciones:** menú visible, URL de sedes, buscador visible, resultado coincidente visible.
**Por qué este flujo:** es de alto valor para el negocio, no destructivo y usa solo funcionalidades públicas.
**Limitaciones:** [completar con lo que encuentres: falta de `data-testid`, textos que cambian, etc.].

## Cómo ejecutar
```bash
python -m venv .venv && source .venv/bin/activate      # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install                                      # descarga los navegadores (solo la primera vez)

pytest -m unit              # solo unitarias
pytest -m integration       # solo integración
pytest -m e2e --headed      # solo E2E, viendo el navegador
pytest                      # las tres
pytest --html=reporte.html --self-contained-html   # genera un reporte para la entrega
```
