# src/io_utils.py
from __future__ import annotations
from typing import List, Dict, Any, Tuple
import csv
import os
import sys

# Estructura de salida esperada por core.py
Pais = Dict[str, Any]  # keys: nombre(str), poblacion(int), superficie(int), continente(str)
CAMPOS_REQUERIDOS = ("nombre", "poblacion", "superficie", "continente")


class CSVInvalido(Exception):
    """Error de formato/validación del CSV."""


def _mapear_headers(headers: List[str]) -> Dict[str, str]:
    """
    Mapea headers del CSV a los nombres canónicos requeridos.
    Acepta variantes como 'Población', 'superficie km2', etc.
    """
    mapa: Dict[str, str] = {}
    for h in headers:
        base = (h or "").strip().lower()
        if base == "":
            continue
        if "nombre" in base:
            mapa[h] = "nombre"
        elif "pobl" in base:  # poblacion / población
            mapa[h] = "poblacion"
        elif "superf" in base:  # superficie / superficie km2
            mapa[h] = "superficie"
        elif "continent" in base:  # continente
            mapa[h] = "continente"
    faltantes = [c for c in CAMPOS_REQUERIDOS if c not in mapa.values()]
    if faltantes:
        raise CSVInvalido(
            f"Faltan columnas requeridas: {', '.join(faltantes)}. "
            f"Encontradas: {headers}"
        )
    return mapa


def _to_int(value: Any, campo: str, fila_nro: int) -> int:
    s = str(value).strip()
    if s == "":
        raise CSVInvalido(f"Fila {fila_nro}: campo '{campo}' vacío.")
    # Permitir '1.234.567' o '1,234,567'
    s_limpio = "".join(ch for ch in s if ch.isdigit())
    if s_limpio == "":
        raise CSVInvalido(f"Fila {fila_nro}: campo '{campo}' no es numérico: {value!r}")
    return int(s_limpio)


def cargar_paises(ruta_csv: str) -> List[Pais]:
    """
    Lee el CSV, valida y convierte tipos.
    Devuelve una lista de dicts con keys: nombre(str), poblacion(int), superficie(int), continente(str).
    Puede imprimir advertencias por filas inválidas y las salta.
    """
    if not os.path.exists(ruta_csv):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_csv}")

    paises: List[Pais] = []
    errores: List[str] = []

    with open(ruta_csv, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise CSVInvalido("El CSV no tiene encabezados.")

        mapa_headers = _mapear_headers(reader.fieldnames)

        for idx, row in enumerate(reader, start=2):  # empieza en 2 por el header
            try:
                nombre = (row.get(next(k for k, v in mapa_headers.items() if v == "nombre"), "") or "").strip()
                continente = (row.get(next(k for k, v in mapa_headers.items() if v == "continente"), "") or "").strip()

                if not nombre or not continente:
                    raise CSVInvalido(f"Fila {idx}: nombre/continente vacío.")

                poblacion_raw = row.get(next(k for k, v in mapa_headers.items() if v == "poblacion"))
                superficie_raw = row.get(next(k for k, v in mapa_headers.items() if v == "superficie"))

                poblacion = _to_int(poblacion_raw, "poblacion", idx)
                superficie = _to_int(superficie_raw, "superficie", idx)

                paises.append({
                    "nombre": nombre,
                    "poblacion": poblacion,
                    "superficie": superficie,
                    "continente": continente
                })
            except Exception as e:
                errores.append(str(e))
                # seguimos con la próxima fila

    if errores:
        print(f"[io_utils] Advertencias: se omitieron {len(errores)} filas inválidas.", file=sys.stderr)
        for msg in errores[:5]:
            print("  - " + msg, file=sys.stderr)
        if len(errores) > 5:
            print(f"  ... y {len(errores)-5} más.", file=sys.stderr)

    return paises


# Alias por si en algún lado quedó otro nombre escrito
def carga_paises(ruta_csv: str) -> List[Pais]:
    return cargar_paises(ruta_csv)


__all__ = ["cargar_paises", "carga_paises", "CSVInvalido"]
