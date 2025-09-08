# src/io_utils.py
from __future__ import annotations
from typing import List, Dict
import csv
import os

class CSVFormatError(ValueError):
    """Error de formato/valores en el CSV."""

ENCABEZADOS_ESPERADOS = ["nombre", "poblacion", "superficie", "continente"]

def cargar_paises_desde_csv(ruta_csv: str) -> List[Dict]:
    """
    Lee un CSV con encabezados: nombre,poblacion,superficie,continente (UTF-8).
    Devuelve una lista de dicts tipados/validados. Si el archivo existe pero está vacío,
    retorna lista vacía. Lanza CSVFormatError con mensajes claros si hay problemas.

    Returns: List[{"nombre":str,"poblacion":int,"superficie":int,"continente":str}]
    """
    if not os.path.exists(ruta_csv):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_csv}")

    paises: List[Dict] = []
    with open(ruta_csv, "r", encoding="utf-8") as f:
        try:
            reader = csv.DictReader(f)
        except csv.Error as e:
            raise CSVFormatError(f"CSV ilegible: {e}")

        # Validación de encabezados (orden y nombres exactos)
        if reader.fieldnames is None:
            # archivo sin encabezado ni filas
            return []
        headers = [h.strip() for h in reader.fieldnames]
        if headers != ENCABEZADOS_ESPERADOS:
            raise CSVFormatError(
                f"Encabezados inválidos. Se esperan EXACTAMENTE: "
                f"{','.join(ENCABEZADOS_ESPERADOS)} (recibidos: {','.join(headers)})"
            )

        for num_linea, row in enumerate(reader, start=2):  # línea 2 = primera de datos
            try:
                nombre = (row["nombre"] or "").strip()
                continente = (row["continente"] or "").strip()

                if not nombre or not continente:
                    raise CSVFormatError("nombre/continente vacío")

                # ints (sin puntos, sin comas)
                poblacion = int(str(row["poblacion"]).strip())
                superficie = int(str(row["superficie"]).strip())

                if poblacion < 0:
                    raise CSVFormatError("población negativa")
                if superficie <= 0:
                    raise CSVFormatError("superficie debe ser > 0")

                paises.append({
                    "nombre": nombre,
                    "poblacion": poblacion,
                    "superficie": superficie,
                    "continente": continente
                })
            except ValueError:
                raise CSVFormatError(f"Error de tipo numérico en línea {num_linea}: "
                                     f"poblacion/superficie deben ser enteros")
            except CSVFormatError as e:
                raise CSVFormatError(f"Línea {num_linea}: {e}")

    return paises

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
