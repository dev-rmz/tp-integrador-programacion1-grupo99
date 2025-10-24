# src/core.py
from __future__ import annotations
from typing import List, Dict, Optional, TypedDict
from unicodedata import normalize as _u_norm, combining

# ---------------- Tipos ----------------
class Pais(TypedDict):
    nombre: str
    poblacion: int
    superficie: int
    continente: str

# ---------------- Normalización (sin tildes, case-insensitive) ----------------
def _norm(s: str) -> str:
    """
    Normaliza texto para comparar sin tildes y en minúsculas.
    """
    s = _u_norm("NFKD", s)
    s = "".join(ch for ch in s if not combining(ch))
    return s.lower().strip()


# ---------------- Validaciones básicas ----------------
def _validar_no_vacio(s: str, campo: str) -> str:
    if not s or not s.strip():
        raise ValueError(f"{campo} no puede estar vacío.")
    return s.strip()


def _validar_entero_positivo(n: int, campo: str) -> int:
    try:
        n = int(n)
    except Exception:
        raise ValueError(f"{campo} debe ser un entero.")
    if n < 0:
        raise ValueError(f"{campo} debe ser un entero positivo.")
    return n


# ---------------- Operaciones ----------------
def agregar_pais(paises: List[Pais], nombre: str, poblacion: int, superficie: int, continente: str) -> Pais:
    nombre = _validar_no_vacio(nombre, "Nombre")
    continente = _validar_no_vacio(continente, "Continente")
    poblacion = _validar_entero_positivo(poblacion, "Población")
    superficie = _validar_entero_positivo(superficie, "Superficie")

    # Si ya existe, actualizamos (criterio simple).
    target = _norm(nombre)
    for p in paises:
        if _norm(p["nombre"]) == target:
            p["poblacion"] = poblacion
            p["superficie"] = superficie
            p["continente"] = continente
            return p
    nuevo = {"nombre": nombre, "poblacion": poblacion, "superficie": superficie, "continente": continente}
    paises.append(nuevo)
    return nuevo


def actualizar_pais(
    paises: List[Pais],
    nombre: str,
    nueva_poblacion: Optional[int] = None,
    nueva_superficie: Optional[int] = None,
) -> Optional[Pais]:
    """
    Actualiza población y/o superficie del país cuyo nombre matchee normalizado.
    Devuelve el país actualizado o None si no existe.
    """
    nombre = _validar_no_vacio(nombre, "Nombre")
    if nueva_poblacion is None and nueva_superficie is None:
        raise ValueError("Debe indicar al menos un valor a actualizar (población/superficie).")

    target = _norm(nombre)
    for p in paises:
        if _norm(p["nombre"]) == target:
            if nueva_poblacion is not None:
                p["poblacion"] = _validar_entero_positivo(nueva_poblacion, "Población")
            if nueva_superficie is not None:
                p["superficie"] = _validar_entero_positivo(nueva_superficie, "Superficie")
            return p
    return None


def buscar_por_nombre(paises: List[Pais], patron: str, exacto: bool = False) -> List[Pais]:
    patron_n = _norm(_validar_no_vacio(patron, "Patrón de búsqueda"))
    if exacto:
        return [p for p in paises if _norm(p["nombre"]) == patron_n]
    return [p for p in paises if patron_n in _norm(p["nombre"])]


def filtrar_por_continente(paises: List[Pais], continente: str) -> List[Pais]:
    c = _norm(_validar_no_vacio(continente, "Continente"))
    return [p for p in paises if _norm(p["continente"]) == c]


def filtrar_por_rango_poblacion(
    paises: List[Pais],
    min_p: Optional[int] = None,
    max_p: Optional[int] = None,
) -> List[Pais]:
    return [
        p for p in paises
        if (min_p is None or p["poblacion"] >= min_p)
        and (max_p is None or p["poblacion"] <= max_p)
    ]


def filtrar_por_rango_superficie(
    paises: List[Pais],
    min_s: Optional[int] = None,
    max_s: Optional[int] = None,
) -> List[Pais]:
    return [
        p for p in paises
        if (min_s is None or p["superficie"] >= min_s)
        and (max_s is None or p["superficie"] <= max_s)
    ]


def ordenar(paises: List[Pais], clave: str, descendente: bool = False) -> List[Pais]:
    clave = clave.lower().strip()
    if clave not in {"nombre", "poblacion", "superficie"}:
        raise ValueError("Clave inválida. Use: nombre | poblacion | superficie")
    if clave == "nombre":
        return sorted(paises, key=lambda p: _norm(p["nombre"]), reverse=descendente)
    return sorted(paises, key=lambda p: p[clave], reverse=descendente)


def estadisticas(paises: List[Pais]) -> Dict[str, object]:
    n = len(paises)
    if n == 0:
        return {
            "n": 0,
            "mayor_poblacion": {"nombre": "", "poblacion": 0},
            "menor_poblacion": {"nombre": "", "poblacion": 0},
            "prom_poblacion": 0.0,
            "prom_superficie": 0.0,
            "cant_por_continente": {},
        }
    mayor = max(paises, key=lambda p: p["poblacion"])
    menor = min(paises, key=lambda p: p["poblacion"])
    prom_p = sum(p["poblacion"] for p in paises) / n
    prom_s = sum(p["superficie"] for p in paises) / n
    por_cont = {}
    for p in paises:
        por_cont[p["continente"]] = por_cont.get(p["continente"], 0) + 1

    return {
        "n": n,
        "mayor_poblacion": {"nombre": mayor["nombre"], "poblacion": mayor["poblacion"]},
        "menor_poblacion": {"nombre": menor["nombre"], "poblacion": menor["poblacion"]},
        "prom_poblacion": prom_p,
        "prom_superficie": prom_s,
        "cant_por_continente": por_cont,
    }
