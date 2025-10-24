# src/cli.py
from __future__ import annotations
import argparse
import sys
from typing import List, Optional, Tuple

from .io_utils import cargar_paises, guardar_paises, CSVInvalido
from .core import (
    agregar_pais, actualizar_pais,
    buscar_por_nombre, filtrar_por_continente,
    filtrar_por_rango_poblacion, filtrar_por_rango_superficie,
    ordenar, estadisticas, Pais
)


def imprimir_paises(paises: List[Pais], max_rows: int = 30) -> None:
    """Salida tabulada sencilla (sin libs externas)."""
    if not paises:
        print("No hay resultados.")
        return
    # Anchuras
    colw = {
        "nombre": max(6, max((len(p["nombre"]) for p in paises), default=6)),
        "poblacion": 10,
        "superficie": 10,
        "continente": max(10, max((len(p["continente"]) for p in paises), default=10)),
    }
    header = f"{'Nombre':<{colw['nombre']}}  {'Población':>{colw['poblacion']}}  {'Superficie':>{colw['superficie']}}  {'Continente':<{colw['continente']}}"
    print(header)
    print("-" * len(header))
    for i, p in enumerate(paises):
        if i >= max_rows:
            restantes = len(paises) - max_rows
            print(f"... ({restantes} más)")
            break
        print(
            f"{p['nombre']:<{colw['nombre']}}  "
            f"{p['poblacion']:>{colw['poblacion']},}  "
            f"{p['superficie']:>{colw['superficie']},}  "
            f"{p['continente']:<{colw['continente']}}"
        )


def _leer_entero(msg: str) -> Optional[int]:
    s = input(msg).strip()
    if s == "":
        return None
    try:
        return int(s)
    except ValueError:
        print("Ingresá un número entero válido.")
        return None


def _leer_rango_int(msg_min: str, msg_max: str) -> Tuple[Optional[int], Optional[int], bool]:
    """Devuelve (min, max, hubo_error). Enter para omitir un extremo."""
    min_s = input(msg_min).strip()
    max_s = input(msg_max).strip()
    try:
        min_v = int(min_s) if min_s else None
        max_v = int(max_s) if max_s else None
    except ValueError:
        print("Ingresá números enteros (o Enter para omitir).")
        return None, None, True
    if min_v is not None and max_v is not None and min_v > max_v:
        print("Rango inválido: el mínimo no puede ser mayor que el máximo.")
        return None, None, True
    return min_v, max_v, False


def menu(paises: List[Pais], ruta_csv: str) -> None:
    dirty = False  # hay cambios sin guardar

    while True:
        print("\n=== Menú ===")
        print("1) Agregar país")
        print("2) Actualizar país (población y/o superficie)")
        print("3) Buscar por nombre (parcial o exacto)")
        print("4) Filtrar por continente")
        print("5) Filtrar por rango de población")
        print("6) Filtrar por rango de superficie")
        print("7) Ordenar")
        print("8) Estadísticas")
        print("9) Guardar cambios")
        print("0) Salir")
        op = input("Opción: ").strip()

        try:
            if op == "0":
                if dirty:
                    resp = input("Hay cambios sin guardar. ¿Guardar ahora? [s/N]: ").strip().lower()
                    if resp == "s":
                        guardar_paises(ruta_csv, paises)
                        print(f"Cambios guardados en {ruta_csv}.")
                    else:
                        print("Saliendo sin guardar cambios…")
                print("Hasta luego.")
                break

            elif op == "9":
                guardar_paises(ruta_csv, paises)
                dirty = False
                print(f"Cambios guardados en {ruta_csv}.")

            elif op == "1":
                nombre = input("Nombre: ").strip()
                poblacion = _leer_entero("Población: ")
                superficie = _leer_entero("Superficie (km²): ")
                continente = input("Continente: ").strip()
                if poblacion is None or superficie is None:
                    print("Operación cancelada (valores inválidos).")
                    continue
                agregar_pais(paises, nombre, poblacion, superficie, continente)
                dirty = True
                print("País agregado con éxito.")

            elif op == "2":
                nombre = input("Nombre del país a actualizar: ").strip()
                p = input("Nueva población (Enter para omitir): ").strip()
                s = input("Nueva superficie (km², Enter para omitir): ").strip()
                nueva_p = int(p) if p else None
                nueva_s = int(s) if s else None
                res = actualizar_pais(paises, nombre, nueva_p, nueva_s)
                if res is None:
                    print("No se encontró un país con ese nombre (recordá que se ignoran tildes/mayúsculas).")
                else:
                    dirty = True
                    print("País actualizado con éxito.")

            elif op == "3":
                patron = input("Texto a buscar (se ignoran tildes y mayúsculas): ").strip()
                exacto = input("¿Búsqueda exacta? [s/N]: ").strip().lower() == "s"
                encontrados = buscar_por_nombre(paises, patron, exacto=exacto)
                imprimir_paises(encontrados)

            elif op == "4":
                cont = input("Continente: ").strip()
                imprimir_paises(filtrar_por_continente(paises, cont))

            elif op == "5":
                min_p, max_p, err = _leer_rango_int("Población mínima (Enter para omitir): ",
                                                    "Población máxima (Enter para omitir): ")
                if err: 
                    continue
                imprimir_paises(filtrar_por_rango_poblacion(paises, min_p, max_p))

            elif op == "6":
                min_s, max_s, err = _leer_rango_int("Superficie mínima (Enter para omitir): ",
                                                    "Superficie máxima (Enter para omitir): ")
                if err:
                    continue
                imprimir_paises(filtrar_por_rango_superficie(paises, min_s, max_s))

            elif op == "7":
                clave = input("Ordenar por (nombre | poblacion | superficie): ").strip().lower()
                desc = input("¿Descendente? [s/N]: ").strip().lower() == "s"
                imprimir_paises(ordenar(paises, clave, descendente=desc))

            elif op == "8":
                s = estadisticas(paises)
                print("\n> Estadísticas")
                if s["n"] == 0:
                    print("- Sin datos.")
                else:
                    may = s["mayor_poblacion"]; men = s["menor_poblacion"]
                    print(f"- Países considerados: {s['n']}")
                    print(f"- Mayor población: {may['nombre']} ({may['poblacion']:,})")
                    print(f"- Menor población: {men['nombre']} ({men['poblacion']:,})")
                    print(f"- Promedio de población: {int(s['prom_poblacion']):,}")
                    print(f"- Promedio de superficie: {int(s['prom_superficie']):,} km²")
                    print("- Cantidad por continente:")
                    for c, n in s['cant_por_continente'].items():
                        print(f"  * {c}: {n}")

            else:
                print("Opción inválida.")
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error inesperado: {e}", file=sys.stderr)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Gestión de países (CSV).")
    parser.add_argument("--dataset", "-d", required=True, help="Ruta al CSV")
    args = parser.parse_args(argv)

    try:
        paises = cargar_paises(args.dataset)
    except (FileNotFoundError, CSVInvalido) as e:
        print(f"Error al cargar el CSV: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Error inesperado: {e}", file=sys.stderr)
        return 3

    print(f"Cargados {len(paises)} países desde {args.dataset}")
    menu(paises, args.dataset)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
