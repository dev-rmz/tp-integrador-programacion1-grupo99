from __future__ import annotations
from typing import List, Dict, Optional, TypedDict
class pais(TypedDict):
    nombre: str
    poblacion: int
    superficie: int
    continente: str
def buscar_pornombre(paises: List[Dict],query: str, exacto: bool = False) -> List[dict]:

 q=(query or "").strip().lower()
 if not q:
  return []
 if exacto:
    return [p for p in paises if p["nombre"].lower() == q]
    return [p for p in paises if q in p["nombre"].lower()]

def filtrarpor_continentes(continente paises: List[Pais], continente: str):
 

"""Busca un país por su nombre (case-insensitive, espacios ignorados).
Retorna el dict del país o None si no se encuentra.
    """
    nombre_normalizado = nombre.strip().lower()
    for pais in paises:
        if pais["nombre"].strip().lower() == nombre_normalizado:
            return pais
    return None
if __name__ == "__main__":

    from pathlib import Path
    from pprint import pprint

    # Calcula ruta al CSV desde este archivo
    raiz = Path(__file__).resolve().parents[1]
    ruta = raiz / "data" / "paises.csv"

    try:
        datos = cargar_paises_desde_csv(str(ruta))
        print(f"Países cargados: {len(datos)}")
        pprint(datos[:5])  # muestra los primeros 5
    except Exception as e:
        print("[ERROR]", e)