# src/core.py
from __future__ import annotations
from typing import List, Dict, Optional, TypedDict

# Tipado más estricto 
class Pais(TypedDict):
    nombre: str
    poblacion: int
    superficie: int
    continente: str

# ---------- BÚSQUEDAS ----------
def buscar_por_nombre(paises: List[Pais], query: str, exacto: bool = False) -> List[Pais]:
    """
    Busca países por nombre.
    - exacto=True: igualdad exacta (ignora mayúsculas/minúsculas).
    - exacto=False: coincidencia parcial (subcadena).
    Complejidad: O(n)
    """
    q = (query or "").strip().lower()
    if not q:
        return []
    if exacto:
        return [p for p in paises if p["nombre"].lower() == q]
    return [p for p in paises if q in p["nombre"].lower()]

# ---------- FILTROS ----------
def filtrar_por_continente(paises: List[Pais], continente: str) -> List[Pais]:
    """
    Filtra por continente (case-insensitive).
    Complejidad: O(n)
    """
    c = (continente or "").strip().lower()
    if not c:
        return []
    return [p for p in paises if p["continente"].lower() == c]

def filtrar_por_rango_poblacion(
    paises: List[Pais],
    min_p: Optional[int] = None,
    max_p: Optional[int] = None,
) -> List[Pais]:
    """
    Filtra por rango de población. Si min_p o max_p son None, ese extremo no se aplica.
    Complejidad: O(n)
    """
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
    """
    Filtra por rango de superficie. Si min_s o max_s son None, ese extremo no se aplica.
    Complejidad: O(n)
    """
    return [
        p for p in paises
        if (min_s is None or p["superficie"] >= min_s)
        and (max_s is None or p["superficie"] <= max_s)
    ]

# ---------- ORDEN ----------
def ordenar(paises: List[Pais], clave: str, asc: bool = True) -> List[Pais]:
    """
    Ordena por 'nombre' | 'poblacion' | 'superficie'.
    Usa Timsort (sorted), estable: O(n log n)
    """
    clave = (clave or "").strip().lower()
    if clave not in {"nombre", "poblacion", "superficie"}:
        raise ValueError("Clave de orden inválida. Use: nombre | poblacion | superficie")
    return sorted(paises, key=lambda p: p[clave], reverse=not asc)

# ---------- ESTADÍSTICAS ----------
def estadisticas(paises: List[Pais]) -> Dict[str, object]:
    """
    Calcula estadísticas básicas del conjunto.
    Devuelve un dict con:
      - mayor_poblacion: dict (país) o None
      - menor_poblacion: dict (país) o None
      - prom_poblacion: float o None
      - prom_superficie: float o None
      - cant_por_continente: dict[str, int]
    Complejidad: O(n)
    """
    if not paises:
        return {
            "mayor_poblacion": None,
            "menor_poblacion": None,
            "prom_poblacion": None,
            "prom_superficie": None,
            "cant_por_continente": {}
        }

    # mayor/menor por población
    mayor = max(paises, key=lambda p: p["poblacion"])
    menor = min(paises, key=lambda p: p["poblacion"])

    n = len(paises)
    prom_p = sum(p["poblacion"] for p in paises) / n
    prom_s = sum(p["superficie"] for p in paises) / n

    # conteo por continente
    conteo: Dict[str, int] = {}
    for p in paises:
        cont = p["continente"]
        conteo[cont] = conteo.get(cont, 0) + 1

    return {
        "mayor_poblacion": mayor,
            "menor_poblacion": menor,
            "prom_poblacion": prom_p,
            "prom_superficie": prom_s,
            "cant_por_continente": conteo
    }
