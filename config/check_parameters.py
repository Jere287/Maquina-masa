#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificador de la base de datos de parametros.

No calcula nada de ingenieria: audita el estado de los DATOS. Responde a
"que sabemos, que falta, y podemos empezar a calcular".

Uso:
    python3 config/check_parameters.py
    python3 config/check_parameters.py --faltantes    # solo lo que falta
"""

from __future__ import annotations

import os
import sys

try:
    import yaml
except ImportError:
    sys.exit("Falta PyYAML.  Instalar con:  pip3 install pyyaml")

RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "design_parameters.yaml")

# Procedencias validas, de mas a menos firme.
FIRMEZA = {
    "MEDIDO": 5,
    "OBSERVADO": 4,
    "PROPORCIONADO": 4,
    "CALCULADO": 3,
    "SUPUESTO": 2,
    "PENDIENTE": 0,
}

# Los 12 parametros minimos para arrancar FASE 4 (ver measurement_plan.md).
MINIMOS_FASE_4 = [
    ("bastidor", "perfil_lado"),
    ("bastidor", "perfil_espesor"),
    ("bastidor", "altura_mesa"),
    ("bastidor", "voladizo_brazo"),
    ("recipiente", "diametro_interior"),
    ("recipiente", "capacidad"),
    ("recipiente", "altura_llenado_lote"),
    ("eje", "diametro"),
    ("eje", "longitud_libre"),
    ("motor", "rpm_placa"),
    ("cargas", "corriente_maxima"),
    ("producto", "temperatura_cuaje"),
]


def es_parametro(v) -> bool:
    """Un parametro es un dict con clave 'value'."""
    return isinstance(v, dict) and "value" in v


def recorrer(datos: dict):
    """Devuelve (seccion, nombre, parametro) para cada parametro del arbol."""
    for seccion, contenido in datos.items():
        if not isinstance(contenido, dict):
            continue
        for nombre, valor in contenido.items():
            if es_parametro(valor):
                yield seccion, nombre, valor


def conocido(par: dict) -> bool:
    """True si el parametro tiene un valor utilizable."""
    v = par.get("value")
    if v is None:
        return False
    if isinstance(v, str) and v.strip().upper() == "UNKNOWN":
        return False
    return par.get("source") not in (None, "PENDIENTE")


def main() -> int:
    solo_faltantes = "--faltantes" in sys.argv
    datos = yaml.safe_load(open(RUTA, encoding="utf-8"))

    parametros = list(recorrer(datos))
    total = len(parametros)

    # --- validacion del esquema ---
    errores = []
    for seccion, nombre, par in parametros:
        src = par.get("source")
        if src not in FIRMEZA:
            errores.append(f"{seccion}.{nombre}: source invalido -> {src!r}")
        if "unit" not in par:
            errores.append(f"{seccion}.{nombre}: falta 'unit'")

    print("=" * 74)
    print(" AUDITORIA DE PARAMETROS DE DISENO")
    print("=" * 74)
    print(f" Archivo : {os.path.relpath(RUTA)}")
    print(f" Fase    : {datos.get('meta', {}).get('fase_actual', '?')}")
    print()

    if errores:
        print(" ERRORES DE ESQUEMA:")
        for e in errores:
            print(f"   - {e}")
        print()
    else:
        print(" Esquema correcto: todos los parametros tienen 'value', 'unit'")
        print(" y un 'source' valido.")
        print()

    # --- recuento por procedencia ---
    por_fuente: dict[str, int] = {}
    for _, _, par in parametros:
        por_fuente[par.get("source", "?")] = por_fuente.get(
            par.get("source", "?"), 0) + 1

    print(" ESTADO DE LOS DATOS")
    print(" " + "-" * 50)
    for fuente in sorted(por_fuente, key=lambda f: -FIRMEZA.get(f, -1)):
        n = por_fuente[fuente]
        barra = "#" * int(40 * n / total)
        print(f"   {fuente:<15}{n:>4}  {barra}")
    print(" " + "-" * 50)

    n_conocidos = sum(1 for _, _, p in parametros if conocido(p))
    pct = 100.0 * n_conocidos / total
    print(f"   {'CONOCIDOS':<15}{n_conocidos:>4} de {total}  ({pct:.0f} %)")
    print()

    # --- puerta de entrada a FASE 4 ---
    print(" REQUISITOS MINIMOS PARA ARRANCAR FASE 4 (calculos)")
    print(" " + "-" * 50)
    faltan = []
    for seccion, nombre in MINIMOS_FASE_4:
        par = datos.get(seccion, {}).get(nombre)
        if par is None:
            estado, ref = "NO EXISTE", "-"
        elif conocido(par):
            estado, ref = "ok", str(par.get("value"))
        else:
            estado, ref = "FALTA", par.get("ref", "-")
            faltan.append((seccion, nombre, par.get("ref", "-")))
        marca = " " if estado == "ok" else ">"
        print(f" {marca} {seccion + '.' + nombre:<38}{estado:<10}{ref}")
    print(" " + "-" * 50)

    if faltan:
        print(f"   FALTAN {len(faltan)} de {len(MINIMOS_FASE_4)}."
              f"  NO se puede arrancar FASE 4.")
    else:
        print("   Completos. FASE 4 puede arrancar.")
    print()

    # --- supuestos activos ---
    supuestos = [(s, n, p) for s, n, p in parametros
                 if p.get("source") == "SUPUESTO"]
    if supuestos:
        print(" SUPUESTOS ACTIVOS (arrastran incertidumbre a los calculos)")
        print(" " + "-" * 50)
        for s, n, p in supuestos:
            print(f"   {s}.{n} = {p['value']} {p['unit']}")
            if p.get("notes"):
                print(f"      {p['notes']}")
        print()

    # --- listado de pendientes ---
    if solo_faltantes:
        print(" TODOS LOS PARAMETROS PENDIENTES")
        print(" " + "-" * 50)
        for s, n, p in parametros:
            if not conocido(p):
                print(f"   {s}.{n:<32}ref: {p.get('ref', '-')}")
        print()

    print("=" * 74)
    print(" Consultar docs/measurement_plan.md para obtener los datos que faltan.")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
