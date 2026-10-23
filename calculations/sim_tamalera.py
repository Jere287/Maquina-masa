#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
 SIMULADOR DE LA PRUEBA EN TAMALERA  (bano maria, molde estatico)
 Porcelana fria · Quito · version corregida
=============================================================================

QUE CORRIGE RESPECTO A LA VERSION ANTERIOR

  La version anterior usaba CAPACITANCIA AGRUPADA (lumped capacitance), que
  supone la masa a una sola temperatura en todo momento. Eso solo vale si el
  numero de Biot < 0.1. En este molde estatico Biot vale 16 a 54: la masa NO
  se mezcla, y lo que manda es la CONDUCCION hacia el centro, no la pelicula
  de agua. La version anterior predecia coccion de 2-7 min; la realidad es de
  horas. Aqui se modela la conduccion real (termino dominante de la serie de
  Heisler para un cilindro corto calentado por el lado y el fondo).

QUE MIDE DE VERDAD ESTA PRUEBA

  La TEMPERATURA de cuaje (PRO-05), que es una propiedad del material y no
  depende de la agitacion. El TIEMPO que tarde este molde estatico NO se
  traslada a la maquina, porque la maquina mezcla. Por eso la instruccion de
  campo es: termometro de pincho EN EL CENTRO del molde, y anotar a que
  temperatura la masa cuaja a la vista. El tiempo solo sirve para saber
  cuanto hay que esperar.

  TODO valor de propiedad de la masa (k, rho, cp, T_cuaje) sigue siendo
  SUPUESTO. La prueba existe precisamente para medirlos.

Uso:  python3 calculations/sim_tamalera.py
=============================================================================
"""

import math

# ---------------- PARAMETROS (editar aqui) ----------------
D_olla    = 0.300    # m   diametro interior de la tamalera
D_molde   = 0.140    # m   diametro interior del molde de masa
H_masa    = 0.080    # m   altura de la capa de masa
prof_agua = 0.080    # m   profundidad de agua en la tamalera

T0        = 20.0     # C   temp inicial de masa y agua
T_agua    = 90.5     # C   hervor del agua en Quito (2850 m)  [CALCULADO]
T_cuaje   = 75.0     # C   fin de gelatinizacion            [SUPUESTO -> PRO-05]

P_nominal = 1200.0   # W   potencia que entregaria la hornilla sin perdidas
f_perdida = 1.38     # -   factor de perdidas (17 min real / 12.3 ideal, 3 L)

rho_masa  = 1150.0   # kg/m3   [SUPUESTO]
cp_masa   = 3000.0   # J/kgK   [SUPUESTO]
cp_agua   = 4186.0   # J/kgK
k_masa    = 0.45     # W/mK    [SUPUESTO] conductividad de la masa  <-- clave
# ----------------------------------------------------------


def precalentar_agua():
    A_olla  = math.pi * (D_olla / 2) ** 2
    A_molde = math.pi * (D_molde / 2) ** 2
    V_agua  = (A_olla - A_molde) * prof_agua
    m_agua  = V_agua * 1000.0                      # ~1 kg/L
    E_agua  = m_agua * cp_agua * (T_agua - T0)
    t_pre   = E_agua / P_nominal * f_perdida / 60.0
    return V_agua * 1000.0, t_pre


def masa_cargada():
    A_molde = math.pi * (D_molde / 2) ** 2
    return A_molde * H_masa * rho_masa


def biot():
    """Comprobacion que invalida la capacitancia agrupada."""
    A_molde = math.pi * (D_molde / 2) ** 2
    A_sum   = math.pi * D_molde * H_masa + A_molde      # lados + fondo
    V_masa  = A_molde * H_masa
    Lc      = V_masa / A_sum
    filas = []
    for h in (300, 600, 1000):
        Bi = h * Lc / k_masa
        filas.append((h, Bi, Bi < 0.1))
    return Lc, filas


def tiempo_conduccion(T_obj):
    """
    Tiempo para que el CENTRO llegue a T_obj, por conduccion (Bi grande).

    Solucion por producto de Heisler, primer termino:
       cilindro infinito (radio R)  x  placa (semiespesor L, calentada por el
       fondo con la cara superior ~adiabatica -> L = H completo).
    Es el modelo honesto para una masa quieta calentada por el lado y el
    fondo. Da el orden de magnitud correcto; para el numero fino hace falta
    medir, que es el proposito de la prueba.
    """
    alpha = k_masa / (rho_masa * cp_masa)
    theta = (T_obj - T_agua) / (T0 - T_agua)
    if theta <= 0:
        return None, theta, alpha           # no se alcanza nunca
    R = D_molde / 2.0
    L = H_masa                              # calienta el fondo, techo expuesto

    # cilindro infinito, Bi->inf: lambda1=2.4048, A1=1.6021
    lam_c, A_c = 2.4048, 1.6021
    # placa, Bi->inf: lambda1=pi/2, A1=1.2732
    lam_p, A_p = math.pi / 2.0, 1.2732

    # theta_total = theta_cil(Fo_r) * theta_placa(Fo_z)
    # Se resuelve el tiempo t tal que el producto = theta. Como Fo_r y Fo_z
    # comparten t, se itera.
    def theta_de_t(t):
        Fo_r = alpha * t / R**2
        Fo_z = alpha * t / L**2
        th_c = A_c * math.exp(-lam_c**2 * Fo_r)
        th_p = A_p * math.exp(-lam_p**2 * Fo_z)
        return min(1.0, th_c * th_p)

    # biseccion en t
    lo, hi = 1.0, 60000.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if theta_de_t(mid) > theta:
            lo = mid
        else:
            hi = mid
    return mid / 60.0, theta, alpha


def main():
    print("=" * 66)
    print(" PRUEBA EN TAMALERA - PREDICCION CORREGIDA")
    print("=" * 66)

    V_agua_L, t_pre = precalentar_agua()
    m_masa = masa_cargada()
    print(f"\n Masa cargada en el molde ... {m_masa:6.2f} kg")
    print(f" Agua en la tamalera ........ {V_agua_L:6.1f} L")
    print(f" Precalentar el agua ........ {t_pre:6.0f} min   (esto si es fiable)")

    Lc, filas = biot()
    print(f"\n POR QUE NO VALE 'MASA BIEN MEZCLADA' (capacitancia agrupada)")
    print(f"   Longitud caracteristica Lc = {Lc*1000:.1f} mm")
    print(f"   {'h (W/m2K)':>10} | {'Biot':>7} | capacitancia agrupada")
    print("   " + "-" * 44)
    for h, Bi, ok in filas:
        txt = "VALIDA" if ok else "INVALIDA (Bi >> 0.1)"
        print(f"   {h:>10} | {Bi:>7.1f} | {txt}")
    print("   La masa esta quieta: manda la conduccion al centro, no el agua.")

    print(f"\n TIEMPO REAL (conduccion al centro del molde)")
    print(f"   {'T objetivo':>11} | {'tiempo al centro':>18}")
    print("   " + "-" * 36)
    for T_obj in (62.0, 70.0, T_cuaje, 80.0, 85.0):
        t_coc, theta, alpha = tiempo_conduccion(T_obj)
        if t_coc is None:
            s = "NO se alcanza (> T agua)"
        else:
            s = f"{t_coc:5.0f} min  (total {t_pre + t_coc:4.0f} min)"
        marca = "  <- T_cuaje supuesto" if abs(T_obj - T_cuaje) < 1e-6 else ""
        print(f"   {T_obj:>9.0f} C | {s}{marca}")

    t_coc, theta, alpha = tiempo_conduccion(T_cuaje)
    print(f"\n   Difusividad usada alpha = {alpha:.3e} m2/s  [SUPUESTA]")

    print("\n" + "=" * 66)
    print(" LO QUE LA PRUEBA DEBE MEDIR (y como)")
    print("=" * 66)
    print("""
   1. TERMOMETRO DE PINCHO EN EL CENTRO del molde, no en el borde.
      El borde cuaja mucho antes; el centro es el que decide.

   2. Anotar la TEMPERATURA del centro cuando la masa cuaja a la vista
      (pasa de lechosa a translucida / gomosa). Ese numero es PRO-05,
      el dato mas importante del proyecto.

   3. El TIEMPO no se traslada a la maquina: este molde esta quieto y la
      maquina mezcla. Sirve solo para saber cuanto esperar en la prueba.

   4. Si el centro cuaja por encima de ~86 C, el bano de agua NO sirve en
      Quito (el agua no pasa de 90.5 C). Ahi habria que cambiar de fluido.

   5. Medir tambien el BORDE a la vez: la diferencia borde-centro es el
      'disparejo' que la agitacion viene a eliminar.
""")


if __name__ == "__main__":
    main()
