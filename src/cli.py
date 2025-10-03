# src/cli.py
from __future__ import annotations
import argparse, sys
from typing import List, Optional
from .io_utils import cargar_paises
from .core import (
    buscar_por_nombre, filtrar_por_continente,
    filtrar_por_rango_poblacion, filtrar_por_rango_superficie,
    ordenar, estadisticas, Pais
)

def imprimir_paises(paises: List[Pais], max_rows: int = 20) -> None:
    if not paises:
        print("No hay resultados.")
        return
    print(f"{'Nombre':30} {'Población':>12} {'Superficie':>12} {'Continente':>12}")
    print("-"*72)
    for p in paises[:max_rows]:
        print(f"{p['nombre'][:30]:30} {p['poblacion']:>12,d} {p['superficie']:>12,d} {p['continente'][:12]:>12}")
    if len(paises) > max_rows:
        print(f"... ({len(paises)-max_rows} más)")

def pedir_int_opcional(msg: str) -> Optional[int]:
    s = input(msg).strip()
    if s == "" or s.lower() == "none":
        return None
    try:
        return int(s)
    except ValueError:
        print("Valor inválido; se ignora.")
        return None

def menu(paises: List[Pais]) -> None:
    while True:
        print("\n=== Gestión de Datos de Países ===")
        print("1) Buscar por nombre")
        print("2) Filtrar por continente")
        print("3) Filtrar por rango de población")
        print("4) Filtrar por rango de superficie")
        print("5) Ordenar")
        print("6) Estadísticas")
        print("0) Salir")
        op = input("Opción: ").strip()
        if op == "0":
            return
        elif op == "1":
            q = input("Texto a buscar: ")
            exacto = input("¿Exacto? (s/n): ").strip().lower().startswith("s")
            res = buscar_por_nombre(paises, q, exacto=exacto)
            imprimir_paises(res)
        elif op == "2":
            c = input("Continente: ")
            res = filtrar_por_continente(paises, c)
            imprimir_paises(res)
        elif op == "3":
            min_p = pedir_int_opcional("Mínimo (enter para omitir): ")
            max_p = pedir_int_opcional("Máximo (enter para omitir): ")
            res = filtrar_por_rango_poblacion(paises, min_p, max_p)
            imprimir_paises(res)
        elif op == "4":
            min_s = pedir_int_opcional("Mínimo km² (enter para omitir): ")
            max_s = pedir_int_opcional("Máximo km² (enter para omitir): ")
            res = filtrar_por_rango_superficie(paises, min_s, max_s)
            imprimir_paises(res)
        elif op == "5":
            clave = input("Clave (nombre|poblacion|superficie): ").strip().lower()
            asc = not input("¿Descendente? (s/n): ").strip().lower().startswith("s")
            try:
                res = ordenar(paises, clave, asc=asc)
                imprimir_paises(res)
            except ValueError as e:
                print(e)
        elif op == "6":
            stats = estadisticas(paises)
            print("\n> Estadísticas")
            for k, v in stats.items():
                print(f"- {k}: {v}")
        else:
            print("Opción inválida.")

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="TP Integrador - Gestión de Países")
    parser.add_argument("--dataset", default="data/paises.csv", help="Ruta al CSV de países")
    args = parser.parse_args(argv)

    try:
        paises = cargar_paises(args.dataset)
    except Exception as e:
        print(f"Error al cargar el CSV: {e}", file=sys.stderr)
        return 2

    print(f"Cargados {len(paises)} países desde {args.dataset}")
    menu(paises)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
