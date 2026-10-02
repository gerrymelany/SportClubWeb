import re
import unicodedata
from dataclasses import dataclass

MIN_CARACTERES = 2
MAX_CARACTERES = 50


# ---------- Errores de negocio ----------
class BusquedaInvalidaError(ValueError):
    """El texto de búsqueda no cumple las reglas."""


class SedesNoDisponibleError(Exception):
    """No se pudo obtener el listado de sedes."""


# ---------- Modelo ----------
@dataclass(frozen=True)
class Sede:
    id: int
    nombre: str
    zona: str
    provincia: str
    activa: bool = True


# ---------- Funciones puras ----------
def normalizar(texto: str) -> str:
    sin_tildes = unicodedata.normalize("NFD", texto)
    sin_tildes = "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn")
    return " ".join(sin_tildes.lower().split())


def validar_busqueda(texto) -> str:
    if texto is None or not texto.strip():
        raise BusquedaInvalidaError("La búsqueda no puede estar vacía")
    limpio = texto.strip()
    if len(limpio) < MIN_CARACTERES:
        raise BusquedaInvalidaError(f"Mínimo {MIN_CARACTERES} caracteres")
    if len(limpio) > MAX_CARACTERES:
        raise BusquedaInvalidaError(f"Máximo {MAX_CARACTERES} caracteres")
    if not re.fullmatch(r"[\w\s\-\.]+", limpio):
        raise BusquedaInvalidaError("La búsqueda contiene caracteres inválidos")
    return limpio


# ---------- Acceso a datos ----------
class SedesRepositoryApi:

    def __init__(self, cliente):
        self._cliente = cliente

    def obtener_todas(self) -> list[Sede]:
        try:
            datos = self._cliente.get("/sedes")
        except Exception as error:
            raise SedesNoDisponibleError("No se pudo obtener las sedes") from error
        return [
            Sede(
                id=d["id"],
                nombre=d["nombre"],
                zona=d["zona"],
                provincia=d["provincia"],
                activa=d.get("activa", True),
            )
            for d in datos
        ]


class SedesService:

    def __init__(self, repository):
        self._repository = repository

    def buscar(self, texto) -> list[Sede]:
        termino = normalizar(validar_busqueda(texto))
        activas = [s for s in self._repository.obtener_todas() if s.activa]
        coincidencias = [
            s
            for s in activas
            if termino in normalizar(s.nombre)
            or termino in normalizar(s.zona)
            or termino in normalizar(s.provincia)
        ]
        return sorted(coincidencias, key=lambda s: normalizar(s.nombre))
