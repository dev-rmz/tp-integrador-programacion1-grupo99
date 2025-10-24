# src/io_utils.py
from __future__ import annotations
from typing import List, Dict, Any, Tuple
import csv
import os
import sys

# Estructura compatible con core.Pais
Pais = Dict[str, Any]
CAMPOS_REQUERIDOS = ("nombre", "poblacion", "superficie", "continente")


class CSVInvalido(Exception):
    """Error de formato/validación del CSV."""


def _mapear_headers(headers: List[str]) -> Dict[str, str]:
    """
    Permite headers flexibles. Devuelve un mapa header_origen -> header_canonico.
    """
    canonicos = {
        "nombre": {"nombre", "pais", "country"},
        "poblacion": {"poblacion", "población", "population", "hab", "habitantes"},
        "superficie": {"superficie", "area", "área", "km2", "km^2"},
        "continente": {"continente", "region", "región", "continent"},
    }
    mapa: Dict[str, str] = {}
    for h in headers:
        h_low = h.strip().lower()
        asignado = False
        for canon, variantes in canonicos.items():
            if h_low in variantes:
                mapa[h] = canon
                asignado = True
                break
        if not asignado:
            # Mantener header original por si coincide exacto con canon
            if h_low in canonicos:
                mapa[h] = h_low
    return mapa


def _to_int(value: Any, campo: str, fila_nro: int) -> int:
    s = str(value).strip()
    if s == "":
        raise CSVInvalido(f"Fila {fila_nro}: campo '{campo}' vacío.")
    # Eliminar separadores de miles comunes
    s_limpio = "".join(ch for ch in s if ch.isdigit())
    if s_limpio == "":
        raise CSVInvalido(f"Fila {fila_nro}: campo '{campo}' no es numérico: {value!r}")
    return int(s_limpio)


def cargar_paises(ruta_csv: str) -> List[Pais]:
    """
    Lee el CSV, valida y convierte tipos. Tolera filas con errores (avisa por stderr).
    """
    if not os.path.exists(ruta_csv):
        raise FileNotFoundError(ruta_csv)

    with open(ruta_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise CSVInvalido("El CSV no tiene encabezados.")
        mapa = _mapear_headers(reader.fieldnames)
        faltantes = set(CAMPOS_REQUERIDOS) - set(mapa.values())
        if faltantes:
            raise CSVInvalido(f"Headers faltantes: {', '.join(sorted(faltantes))}")

        out: List[Pais] = []
        for i, row in enumerate(reader, start=2):  # datos arrancan en fila 2 (tras encabezados)
            try:
                nombre = str(row.get(next(k for k, v in mapa.items() if v == 'nombre'), "")).strip()
                continente = str(row.get(next(k for k, v in mapa.items() if v == 'continente'), "")).strip()
                poblacion_raw = row.get(next(k for k, v in mapa.items() if v == 'poblacion'), "")
                superficie_raw = row.get(next(k for k, v in mapa.items() if v == 'superficie'), "")

                if not nombre or not continente:
                    raise CSVInvalido(f"Fila {i}: nombre/continente vacío.")

                poblacion = _to_int(poblacion_raw, "poblacion", i)
                superficie = _to_int(superficie_raw, "superficie", i)

                out.append({
                    "nombre": nombre,
                    "poblacion": poblacion,
                    "superficie": superficie,
                    "continente": continente,
                })
            except Exception as e:
                print(f"[Advertencia] {e}", file=sys.stderr)
                continue

    return out


def guardar_paises(ruta_csv: str, paises: List[Pais]) -> None:
    tmp = ruta_csv + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(CAMPOS_REQUERIDOS))
        writer.writeheader()
        for p in paises:
            writer.writerow({
                "nombre": p["nombre"],
                "poblacion": int(p["poblacion"]),
                "superficie": int(p["superficie"]),
                "continente": p["continente"],
            })
    os.replace(tmp, ruta_csv)


# Alias por si quedó otro nombre escrito en algún lado
def carga_paises(ruta_csv: str) -> List[Pais]:
    return cargar_paises(ruta_csv)


__all__ = ["cargar_paises", "carga_paises", "guardar_paises", "CSVInvalido"]
