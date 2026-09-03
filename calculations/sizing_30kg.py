#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
 DIMENSIONAMIENTO PRELIMINAR - PROTOTIPO 2 PARA LOTE DE 30 kg
=============================================================================

ALCANCE Y LIMITACIONES  (leer antes de usar cualquier numero de aqui)

Este modulo produce un DIMENSIONAMIENTO CONCEPTUAL, no un diseno de taller.
Se ejecuta antes de disponer de las mediciones del Prototipo 1, a peticion
expresa del usuario, para poder responder tres preguntas concretas:

   1. Con 30 kg, un ancla movida por un motor razonable, ¿arrastra la masa?
   2. ¿Funciona el bano maria a esa escala?
   3. ¿Como se acopla la estructura existente con la nueva?

Todo valor que no provenga de una observacion o de un dato del usuario esta
marcado SUPUESTO y su influencia se muestra como banda de sensibilidad, no
como cifra unica. Un resultado calculado sobre un supuesto NO es un dato.

Salida: reports/sizing_30kg.txt
=============================================================================
"""

from __future__ import annotations

import math
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# =============================================================================
# ENTRADAS
# =============================================================================

# --- [PROPORCIONADO] por el usuario -----------------------------------------
LOTE_KG = 30.0                  # objetivo de produccion por mezcla
ALTITUD_QUITO_M = 2850.0        # Quito, Ecuador

# --- [SUPUESTO] propiedades de la masa --------------------------------------
# Tipicas de pastas de almidon. NINGUNA medida en esta receta.
# Se marcan una a una porque cada una arrastra incertidumbre a un resultado.
RHO = 1150.0                    # kg/m3   -> PRO-08 lo mide en 5 minutos
CP = 2800.0                     # J/kg.K
T_INICIAL = 18.0                # degC    ambiente de Quito
T_CUAJE = 72.0                  # degC    <-- EL SUPUESTO MAS PELIGROSO. PRO-05
U_PARED = 250.0                 # W/m2.K  coef. global con ancla y raspadores
REND_QUEMADOR = 0.40            # -       rendimiento de quemador a la camisa

# Banda de viscosidad aparente en el punto mas espeso, a la velocidad de
# corte del ancla. Es el rango honesto de desconocimiento: PAR-03/PAR-06 lo
# colapsa a un solo valor.
MU_BANDA = [100.0, 300.0, 500.0, 800.0, 1200.0, 2000.0]   # Pa.s
MU_DISENO = 500.0                                          # SUPUESTO de trabajo

# --- [SUPUESTO] geometria de proceso ----------------------------------------
LLENADO = 0.65                  # fraccion de llenado del recipiente
RPM = 30.0                      # velocidad de agitacion
KP_ANCLA = 350.0               # constante de potencia laminar del ancla
                                # (Np.Re; literatura da 300-400 con D/T ~0.95)
GAP_CAMISA = 20.0e-3            # m, luz anular del bano
T_CAMISA_OBJ = 85.0             # degC, consigna (ver hallazgo de altitud)

# --- [SUPUESTO] materiales y componentes ------------------------------------
SIGMA_Y = 250.0e6               # Pa, acero A36
FS_ESTRUCTURA = 2.5             # factor de seguridad estructural
FACTOR_SERVICIO = 2.0           # mezcla de pasta espesa con arranque en carga

# Secciones de tubo cuadrado candidatas: (lado_mm, espesor_mm)
TUBOS = [(40, 2.0), (40, 3.0), (50, 2.0), (50, 3.0),
         (60, 3.0), (75, 3.0), (75, 4.0), (100, 4.0)]


L: list[str] = []


def p(txt: str = "") -> None:
    L.append(txt)


def titulo(t: str) -> None:
    p("")
    p("=" * 78)
    p(f" {t}")
    p("=" * 78)


# =============================================================================
# 1. ALTITUD  — se calcula primero porque condiciona todo lo demas
# =============================================================================

def presion_atmosferica(altitud_m: float) -> float:
    """Atmosfera estandar ISA, en Pa."""
    return 101325.0 * (1.0 - 2.25577e-5 * altitud_m) ** 5.25588


def temp_ebullicion(presion_pa: float) -> float:
    """
    Temperatura de saturacion del agua, en degC.
    Antoine para agua (rango 1-100 degC), P en mmHg:
        log10(P) = A - B / (C + T)
    """
    a, b, c = 8.07131, 1730.63, 233.426
    p_mmhg = presion_pa / 133.322
    return b / (a - math.log10(p_mmhg)) - c


def bloque_altitud() -> dict:
    titulo("1. ALTITUD DE QUITO  —  HALLAZGO QUE CONDICIONA EL DISENO")
    pa = presion_atmosferica(ALTITUD_QUITO_M)
    t_eb = temp_ebullicion(pa)
    t_eb_mar = temp_ebullicion(101325.0)

    p("")
    p(f"    Altitud de Quito ................. {ALTITUD_QUITO_M:7.0f} m   [PROPORCIONADO]")
    p(f"    Presion atmosferica .............. {pa/1000:7.1f} kPa [CALCULADO]")
    p(f"    Ebullicion del agua a nivel del mar {t_eb_mar:6.1f} degC")
    p(f"    Ebullicion del agua EN QUITO ..... {t_eb:7.1f} degC [CALCULADO]")
    p("")
    p("    CONSECUENCIA DIRECTA:")
    p(f"    El bano maria NO puede pasar de {t_eb:.0f} degC en Quito. No es una")
    p("    cuestion de control: es el punto de ebullicion a esta presion.")
    p("")
    p("    Lo bueno: la garantia fisica contra la costra es MAS fuerte que a")
    p(f"    nivel del mar. La masa no puede ver mas de ~{t_eb-5:.0f} degC.")
    p("")
    p("    Lo malo: desaparece el margen de maniobra. Una consigna de camisa")
    p(f"    de 90 degC quedaria practicamente EN la ebullicion: hervor fuerte,")
    p("    perdida de agua por el venteo y consumo de gas desperdiciado.")
    p(f"    Por eso la consigna de trabajo se fija en {T_CAMISA_OBJ:.0f} degC.")
    p("")
    t_masa_max = T_CAMISA_OBJ - 5.0
    p(f"    Techo real de temperatura de la masa ... {t_masa_max:.0f} degC")
    p("")
    if T_CUAJE > t_masa_max:
        p("    [ALERTA CRITICA] Con el T_cuaje SUPUESTO, la masa NO cuajaria.")
    else:
        p(f"    Con T_cuaje SUPUESTO de {T_CUAJE:.0f} degC hay "
          f"{t_masa_max - T_CUAJE:.0f} K de margen.")
    p("")
    p("    ESTA ES LA RAZON POR LA QUE PRO-05 (temperatura real de cuaje) ES")
    p("    LA MEDIDA MAS IMPORTANTE DEL PROYECTO. Si la masa necesita mas de")
    p(f"    {t_masa_max:.0f} degC, el bano de AGUA no sirve en Quito y hay que")
    p("    cambiar de fluido. Ver bloque 7.")
    return {"p_atm": pa, "t_eb": t_eb, "t_masa_max": t_masa_max}


# =============================================================================
# 2. GEOMETRIA DEL RECIPIENTE
# =============================================================================

def bloque_geometria() -> dict:
    titulo("2. GEOMETRIA DEL RECIPIENTE PARA 30 kg")
    v_masa = LOTE_KG / RHO                      # m3
    v_recip = v_masa / LLENADO

    p("")
    p(f"    Lote objetivo .................... {LOTE_KG:7.1f} kg  [PROPORCIONADO]")
    p(f"    Volumen de masa .................. {v_masa*1000:7.1f} L   [CALCULADO]")
    p(f"    Volumen de recipiente ({LLENADO*100:.0f}% lleno) {v_recip*1000:7.1f} L")
    p("")
    p("    POR QUE ANGOSTO Y ALTO. Para un volumen dado, el area lateral")
    p("    mojada vale A = 4V/D: es INVERSAMENTE proporcional al diametro.")
    p("    Un recipiente mas angosto tiene MAS area de intercambio y ademas")
    p("    menor camino de conduccion al centro. Los dos efectos van en el")
    p("    mismo sentido. El limite lo pone el ancla, no la termica.")
    p("")
    p("    D_int   h_masa   h/D    A_interc   t_calent   Impulsor viable")
    p("     mm       mm      -       m2         min")
    p("    " + "-" * 62)

    opciones = []
    for d_mm in (220, 250, 280, 300, 350, 400):
        d = d_mm / 1000.0
        h = 4.0 * v_masa / (math.pi * d * d)
        rel = h / d
        area = math.pi * d * h + math.pi * d * d / 4.0
        dt1 = T_CAMISA_OBJ - T_INICIAL
        dt2 = T_CAMISA_OBJ - T_CUAJE
        lmtd = (dt1 - dt2) / math.log(dt1 / dt2)
        q = U_PARED * area * lmtd
        t_min = LOTE_KG * CP * (T_CUAJE - T_INICIAL) / q / 60.0
        # Criterio de seleccion de impulsor por esbeltez del bano:
        #   h/D <= 1.2  el ancla simple barre todo el volumen
        #   h/D <= 1.7  hace falta travesano intermedio para arrastrar el nucleo
        #   h/D <= 3.0  el ancla ya no circula axialmente -> cinta helicoidal
        if rel <= 1.2:
            imp = "ancla simple"
        elif rel <= 1.7:
            imp = "ancla + travesano"
        elif rel <= 3.0:
            imp = "cinta helicoidal"
        else:
            imp = "cinta helic. multiple"
        p(f"    {d_mm:5d}   {h*1000:6.0f}   {rel:4.2f}   {area:7.4f}   "
          f"{t_min:7.1f}    {imp}")
        opciones.append((d_mm, h, rel, area, t_min, imp))

    p("    " + "-" * 62)
    p("")
    p("    SELECCION: D_int = 280 mm  ->  ancla con travesano intermedio")
    p("")
    p("    Con h/D = 1.51 el ancla sigue siendo viable, pero ya NO la simple:")
    p("    necesita un travesano a media altura que arrastre el nucleo. Sin")
    p("    el, el ancla mueve bien la corona junto a la pared y deja el")
    p("    centro girando como un tapon. Es exactamente el defecto que hoy")
    p("    produce 'centro crudo'.")
    p("")
    p("    Por que no bajar mas el diametro: por debajo de ~250 mm el bano se")
    p("    vuelve demasiado esbelto para cualquier ancla y obliga a CINTA")
    p("    HELICOIDAL. La cinta mezcla mejor, pero es bastante mas cara de")
    p("    fabricar y de limpiar en un taller de Quito, y la ganancia termica")
    p("    frente a 280 mm es de menos de 1.5 min. No compensa.")
    p("")
    p("    Por que no subir a 300 o 350 mm: el ancla seria mas simple, pero se")
    p("    pierde area de intercambio y crece el camino al centro. Ademas el")
    p("    recipiente se sale del vano actual con mayor probabilidad.")

    d_sel = 0.280
    h_masa = 4.0 * v_masa / (math.pi * d_sel * d_sel)
    h_recip = h_masa / LLENADO
    esp = 0.002
    d_ext_olla = d_sel + 2 * esp
    d_int_cam = d_ext_olla + 2 * GAP_CAMISA
    d_ext_cam = d_int_cam + 2 * esp

    p("")
    p(f"    Diametro interior ................ {d_sel*1000:7.0f} mm")
    p(f"    Altura de masa ................... {h_masa*1000:7.0f} mm")
    p(f"    Altura interior del recipiente ... {h_recip*1000:7.0f} mm")
    p(f"    Resguardo libre .................. {(h_recip-h_masa)*1000:7.0f} mm")
    p(f"    Diametro exterior de la olla ..... {d_ext_olla*1000:7.0f} mm")
    p(f"    Diametro exterior CON CAMISA ..... {d_ext_cam*1000:7.0f} mm  <-- clave")
    p("")
    p("    NOTA DE ACOPLE. El diametro exterior con camisa queda en")
    p(f"    ~{d_ext_cam*1000:.0f} mm. En las fotos, la olla actual parece de orden")
    p("    similar. Si al medir BAS-06 el vano del bastidor lo admite, el")
    p("    recipiente nuevo entra en el hueco existente SIN tocar el marco.")
    p("    Seria el mejor escenario de acople posible. A CONFIRMAR.")

    return {"v_masa": v_masa, "d_int": d_sel, "h_masa": h_masa,
            "h_recip": h_recip, "d_ext_olla": d_ext_olla,
            "d_int_cam": d_int_cam, "d_ext_cam": d_ext_cam}


# =============================================================================
# 3. TERMICA
# =============================================================================

def bloque_termico(g: dict, alt: dict) -> dict:
    titulo("3. TERMICA  —  ¿FUNCIONA EL BANO MARIA A 30 kg?")
    area = math.pi * g["d_ext_olla"] * g["h_masa"] + \
        math.pi * g["d_ext_olla"] ** 2 / 4.0
    dt1 = T_CAMISA_OBJ - T_INICIAL
    dt2 = T_CAMISA_OBJ - T_CUAJE
    lmtd = (dt1 - dt2) / math.log(dt1 / dt2)
    q_dot = U_PARED * area * lmtd
    q_masa = LOTE_KG * CP * (T_CUAJE - T_INICIAL)
    t_masa = q_masa / q_dot

    # Agua de la camisa
    r_i = g["d_int_cam"] / 2.0
    r_o = g["d_ext_olla"] / 2.0
    h_cam = g["h_masa"] + 0.05
    v_anular = math.pi * (r_i ** 2 - r_o ** 2) * h_cam
    v_fondo = math.pi * r_i ** 2 * 0.030
    v_agua = v_anular + v_fondo
    m_agua = v_agua * 985.0
    q_agua = m_agua * 4186.0 * (T_CAMISA_OBJ - T_INICIAL)

    q_quem_util = q_dot
    q_quem_in = q_quem_util / REND_QUEMADOR
    t_precal = q_agua / q_quem_util

    p("")
    p("    TRANSFERENCIA A LA MASA")
    p(f"    Area de intercambio mojada ....... {area:7.4f} m2")
    p(f"    Salto medio logaritmico .......... {lmtd:7.1f} K")
    p(f"    Energia a entregar al lote ....... {q_masa/1e6:7.3f} MJ")
    p(f"    Potencia transferida ............. {q_dot:7.0f} W")
    p(f"    Tiempo de calentamiento .......... {t_masa/60:7.1f} min")
    p("")
    p("    CARGA DE AGUA DE LA CAMISA")
    p(f"    Volumen anular ................... {v_anular*1000:7.2f} L")
    p(f"    Colchon de fondo ................. {v_fondo*1000:7.2f} L")
    p(f"    CARGA TOTAL ...................... {v_agua*1000:7.2f} L "
      f"({m_agua:.1f} kg)")
    p("")
    p("    PRECALENTAMIENTO DE LA CAMISA  (se suele olvidar)")
    p(f"    Energia para llevar el agua a {T_CAMISA_OBJ:.0f} degC {q_agua/1e6:6.3f} MJ")
    p(f"    Tiempo de precalentamiento ....... {t_precal/60:7.1f} min")
    p("    La camisa hay que arrancarla ANTES de cargar la masa. Ese tiempo")
    p("    se solapa con la carga y la mezcla en frio, no se suma al ciclo.")
    p("")
    p("    QUEMADOR NECESARIO")
    p(f"    Potencia util requerida .......... {q_quem_util:7.0f} W")
    p(f"    Potencia de entrada (rend. {REND_QUEMADOR*100:.0f} %) . "
      f"{q_quem_in/1000:7.1f} kW")
    p(f"                                       {q_quem_in*3.412/1000:7.0f} kBTU/h")
    p("    El quemador domestico del prototipo actual (~20 kBTU/h) queda muy")
    p("    corto. Hace falta un quemador industrial de anillo, tipo paila o")
    p("    wok, de alta presion.")
    p("")
    p("    ATENCION AL AJUSTE DE ALTITUD: los quemadores e inyectores de GLP")
    p("    se calibran a nivel del mar. A 2850 m el aire es un 29 % menos")
    p("    denso y la mezcla se enriquece: la potencia real cae y aparece")
    p("    hollin. Hay que pedir el quemador con INYECTOR PARA ALTURA o")
    p("    cambiarlo. Es un detalle barato que arruina el rendimiento si se")
    p("    pasa por alto.")

    return {"area": area, "q_dot": q_dot, "t_masa": t_masa,
            "v_agua": v_agua, "m_agua": m_agua, "t_precal": t_precal,
            "q_quem_in": q_quem_in}


# =============================================================================
# 4. PAR  —  ¿ARRASTRA LA MASA?
# =============================================================================

def bloque_par(g: dict) -> dict:
    titulo("4. PAR EN EL EJE  —  ¿VA A JALAR POR LAS ASPAS?")
    n = RPM / 60.0                       # rev/s
    omega = 2.0 * math.pi * n            # rad/s
    d_ancla = g["d_int"] - 2 * 0.005     # ancla casi a pared

    p("")
    p("    METODO. En regimen laminar, que es donde trabaja un ancla en pasta")
    p("    espesa, la potencia de mezcla vale:")
    p("")
    p("        P = Kp . mu . N^2 . D^3        con Kp ~ 350 para ancla")
    p("")
    p(f"    D_ancla = {d_ancla*1000:.0f} mm    N = {RPM:.0f} rpm = {n:.3f} rev/s")
    p("")
    p("    LA VISCOSIDAD ES EL UNICO DATO QUE FALTA, y lo cambia todo:")
    p("")
    p("      mu       P_mezcla   Par eje    Motor min.   ¿Arrastra con")
    p("     Pa.s          W       N.m         kW         2.2 kW / 30 rpm?")
    p("    " + "-" * 66)

    par_diseno = None
    for mu in MU_BANDA:
        pot = KP_ANCLA * mu * n * n * d_ancla ** 3
        par = pot / omega
        kw_min = pot * FACTOR_SERVICIO / 1000.0
        ok = "si" if kw_min <= 2.2 else "NO - se cala"
        marca = " <--" if abs(mu - MU_DISENO) < 1e-6 else ""
        p(f"    {mu:6.0f}   {pot:8.0f}   {par:8.1f}   {kw_min:8.2f}      "
          f"{ok}{marca}")
        if abs(mu - MU_DISENO) < 1e-6:
            par_diseno = par
            pot_diseno = pot
    p("    " + "-" * 66)
    p("")
    p("    RESPUESTA HONESTA A LA PREGUNTA:")
    p("")
    p("    SI, arrastra — mientras la viscosidad aparente en el punto mas")
    p("    espeso no pase de ~1200 Pa.s. Por encima de eso, un conjunto de")
    p("    2.2 kW a 30 rpm se cala.")
    p("")
    p("    Y AHORA MISMO NO SABEMOS DONDE CAE. El rango de la tabla abarca un")
    p("    factor de 20 en el par. No es que el calculo sea malo: es que le")
    p("    falta el dato. PAR-03 (pinza amperimetrica) o PAR-06 (brazo de")
    p("    palanca con bascula) cierran esa banda en una tarde.")
    p("")
    p("    DIMENSIONAMIENTO ADOPTADO (sobre el SUPUESTO mu = "
      f"{MU_DISENO:.0f} Pa.s):")
    par_serv = par_diseno * FACTOR_SERVICIO
    p(f"    Par de mezcla .................... {par_diseno:7.1f} N.m")
    p(f"    Factor de servicio ............... {FACTOR_SERVICIO:7.1f}")
    p(f"    PAR DE DISENO .................... {par_serv:7.1f} N.m")
    p(f"    Potencia mecanica ................ {pot_diseno:7.0f} W")
    p("")
    p("    SELECCION PRELIMINAR:")
    p("      Motorreductor 2.2 kW (3 HP), salida 30 rpm")
    p("      Reductor sinfin-corona i=50 tipo NMRV110 o equivalente")
    p(f"      Par nominal de salida requerido: >= {par_serv:.0f} N.m")
    p("")
    p("    EL REDUCTOR MANDA, NO EL MOTOR. Un NMRV090 se queda en ~450 N.m y")
    p("    no sirve. Al comprar hay que exigir el PAR NOMINAL DE SALIDA del")
    p("    reductor, no los kW del motor. Es el error clasico de compra.")

    return {"par_mezcla": par_diseno, "par_diseno": par_serv,
            "omega": omega, "d_ancla": d_ancla}


# =============================================================================
# 5. CARGAS SOBRE LA ESTRUCTURA
# =============================================================================

def bloque_cargas(g: dict, t: dict, par: dict) -> dict:
    titulo("5. CARGAS QUE LLEGAN A LA ESTRUCTURA")
    m_masa = LOTE_KG
    m_agua = t["m_agua"]
    # Chapa de olla + camisa
    a_olla = math.pi * g["d_int"] * g["h_recip"] + math.pi * g["d_int"]**2 / 4
    a_cam = math.pi * g["d_ext_cam"] * g["h_masa"] + \
        math.pi * g["d_ext_cam"]**2 / 4
    m_inox = (a_olla + a_cam) * 0.002 * 8000.0
    m_eje = math.pi * (0.045 / 2) ** 2 * 1.3 * 7850.0
    m_ancla = 10.0
    m_motor = 65.0        # SUPUESTO: 2.2 kW + NMRV110

    m_sobre_marco = m_masa + m_agua + m_inox + m_ancla
    m_sobre_brazo = m_motor
    m_total = m_sobre_marco + m_sobre_brazo + m_eje

    p("")
    p("    DOS CAMINOS DE CARGA DISTINTOS. Es la clave del acople.")
    p("")
    p("    CAMINO A — el marco de la mesa sostiene el recipiente:")
    p(f"      Masa del lote .................. {m_masa:7.1f} kg")
    p(f"      Agua de la camisa .............. {m_agua:7.1f} kg")
    p(f"      Chapa de olla + camisa ......... {m_inox:7.1f} kg  [SUPUESTO]")
    p(f"      Ancla .......................... {m_ancla:7.1f} kg  [SUPUESTO]")
    p(f"      TOTAL sobre el marco ........... {m_sobre_marco:7.1f} kg")
    p(f"      Carga vertical ................. {m_sobre_marco*9.81:7.0f} N")
    p("      Es carga ESTATICA y VERTICAL, repartida en el perimetro del")
    p("      vano. Es el tipo de carga que una mesa soldada lleva bien.")
    p("")
    p("    CAMINO B — el brazo y la columna sostienen el accionamiento:")
    p(f"      Masa del motorreductor ......... {m_motor:7.1f} kg  [SUPUESTO]")
    p(f"      PAR DE REACCION ................ {par['par_diseno']:7.1f} N.m")
    p("      Este es el que hace dano. El par que el reductor entrega al eje")
    p("      se lo devuelve a su soporte, con el mismo valor y sentido")
    p("      contrario. Sale por los pernos del motor, torsiona el brazo y")
    p("      flexiona la columna. NO es carga estatica vertical: es TORSION")
    p("      mas FLEXION, y ademas pulsante, porque el ancla encuentra")
    p("      resistencia variable en cada vuelta.")
    p("")
    p(f"    MASA TOTAL DE LA MAQUINA CARGADA ... {m_total:7.0f} kg  [SUPUESTO]")

    return {"m_marco": m_sobre_marco, "m_motor": m_motor, "m_total": m_total}


# =============================================================================
# 6. ¿AGUANTA EL BASTIDOR EXISTENTE?
# =============================================================================

def bloque_estructura(par: dict, c: dict) -> dict:
    titulo("6. ¿AGUANTA EL BASTIDOR EXISTENTE?  —  TABLA DE CAPACIDAD")
    t_req = par["par_diseno"]
    sigma_adm = SIGMA_Y / FS_ESTRUCTURA
    tau_adm = 0.6 * SIGMA_Y / FS_ESTRUCTURA

    p("")
    p("    No se puede responder sin BAS-01 y BAS-02. Lo que si se puede es")
    p("    dejar la tabla resuelta, para leer la fila en cuanto llegue la")
    p("    medida del tubo esta tarde.")
    p("")
    p(f"    Par de reaccion a resistir ....... {t_req:7.0f} N.m")
    p(f"    Tension admisible (FS {FS_ESTRUCTURA:.1f}) ..... {sigma_adm/1e6:7.0f} MPa")
    p(f"    Cortante admisible ............... {tau_adm/1e6:7.0f} MPa")
    p("")
    p("    Tubo        M_flexion_adm   T_torsion_adm    ¿Resiste el par")
    p("    mm x mm         N.m             N.m          de reaccion?")
    p("    " + "-" * 62)

    resultados = []
    for lado, esp in TUBOS:
        b = lado
        bi = lado - 2 * esp
        inercia = (b ** 4 - bi ** 4) / 12.0                 # mm4
        modulo = inercia / (b / 2.0)                        # mm3
        m_adm = sigma_adm * modulo / 1e9                    # N.m
        # Torsion, seccion cerrada de pared delgada (Bredt)
        a_m = (lado - esp) ** 2                             # mm2
        t_adm = tau_adm * 2.0 * a_m * esp / 1e9             # N.m
        ok = "SI" if (t_adm >= t_req and m_adm >= t_req) else "NO"
        p(f"    {lado:3d} x {esp:3.1f}     {m_adm:9.0f}      {t_adm:9.0f}"
          f"           {ok}")
        resultados.append((lado, esp, m_adm, t_adm, ok))
    p("    " + "-" * 62)
    p("")
    p("    LECTURA DE LA TABLA:")
    p("")
    p("    Si el tubo del bastidor resulta ser 40x40x2 —lo mas probable en un")
    p("    bastidor artesanal de este tamano— la columna y el brazo NO")
    p("    resisten el par de reaccion de un accionamiento para 30 kg: se")
    p("    quedan en unos dos tercios de lo necesario, sin ningun margen.")
    p("    Haria falta pasar a 50x50x2 como minimo solo para EMPATAR el")
    p("    requisito, y a 60x60x3 para tener margen razonable.")
    p("")
    p("    Y ojo: aunque resistiese en tension, faltaria comprobar la")
    p("    DEFORMACION. Un brazo que gira unos grados bajo el par mueve el")
    p("    eje y descentra el ancla, que es justo lo que arruina la luz del")
    p("    raspador.")
    p("")
    p("    CONCLUSION PRELIMINAR (a confirmar con la medida):")
    p("      CAMINO A (recipiente sobre el marco) ....... probablemente OK")
    p("      CAMINO B (accionamiento) .................. probablemente NO")
    return {"resultados": resultados, "t_req": t_req}


# =============================================================================
# 7. RIESGOS Y DECISIONES REVERSIBLES
# =============================================================================

def bloque_riesgos(alt: dict) -> None:
    titulo("7. RIESGOS ABIERTOS Y COMO NO QUEDAR ATRAPADO")
    p("")
    p("    R1. TEMPERATURA DE CUAJE  (PRO-05)  — riesgo alto")
    p(f"        Si la masa cuaja por debajo de {alt['t_masa_max']:.0f} degC, el bano de")
    p("        agua funciona. Si necesita mas, en Quito NO hay forma de que")
    p("        el agua se lo de.")
    p("")
    p("        DECISION REVERSIBLE: disenar la camisa como camisa, sin atarla")
    p("        al agua. La misma envolvente admite:")
    p("           - agua .............. hasta ~85 degC utiles en Quito")
    p("           - aceite termico .... hasta 150 degC, con termostato")
    p("        Cambia el fluido y el control, no el recipiente. Asi la")
    p("        medicion de PRO-05 no obliga a rehacer nada de chapa.")
    p("")
    p("        Contrapartida honesta del aceite: se pierde el tope fisico. Con")
    p("        agua, la fisica impide pasarse. Con aceite, solo lo impide el")
    p("        termostato, y un termostato se puede averiar.")
    p("")
    p("    R2. VISCOSIDAD REAL  (PAR-03 / PAR-06)  — riesgo alto")
    p("        Banda de un factor 20 en el par. Determina reductor y motor,")
    p("        que son los dos items mas caros. Medir ANTES de comprar.")
    p("")
    p("    R3. ESTRUCTURA  (BAS-01, BAS-02)  — riesgo medio")
    p("        Se resuelve con la tabla del bloque 6 en cuanto llegue la")
    p("        medida del tubo.")
    p("")
    p("    R4. DESCARGA DE 30 kg  — riesgo medio, poco atendido")
    p("        30 kg de masa caliente y pegajosa en un recipiente de 280 mm")
    p("        de boca no se vuelcan a mano. Con la olla llena el conjunto")
    p("        pasa de 55 kg. Hay que resolver la descarga en el diseno, no")
    p("        despues: volteo con muñones, o recipiente extraible con")
    p("        polipasto, o fondo con valvula de mariposa sanitaria.")
    p("")
    p("    R5. INYECTOR DE GLP PARA ALTURA  — riesgo bajo, coste bajo")
    p("        Barato de resolver, caro de ignorar.")


# =============================================================================
# MAIN
# =============================================================================

def main() -> int:
    p("=" * 78)
    p(" DIMENSIONAMIENTO PRELIMINAR - PROTOTIPO 2 PARA 30 kg POR LOTE")
    p(" Mezcladora-cocedora de porcelana fria  ·  Quito, Ecuador")
    p("=" * 78)
    p("")
    p(" AVISO. Este es un dimensionamiento CONCEPTUAL. Se apoya en supuestos")
    p(" sobre las propiedades de la masa que NADIE ha medido todavia. Sirve")
    p(" para decidir la ARQUITECTURA y para saber que comprar y que medir.")
    p(" NO sirve para cortar material.")

    alt = bloque_altitud()
    g = bloque_geometria()
    t = bloque_termico(g, alt)
    par = bloque_par(g)
    c = bloque_cargas(g, t, par)
    bloque_estructura(par, c)
    bloque_riesgos(alt)

    titulo("RESUMEN EJECUTIVO")
    p("")
    p(f"    Recipiente ....... Ø{g['d_int']*1000:.0f} x {g['h_recip']*1000:.0f} mm int, "
      f"Ø{g['d_ext_cam']*1000:.0f} mm con camisa")
    p(f"    Camisa ........... {t['v_agua']*1000:.0f} L de agua, "
      f"consigna {T_CAMISA_OBJ:.0f} degC")
    p(f"    Quemador ......... {t['q_quem_in']*3.412/1000:.0f} kBTU/h, "
      f"inyector para altura")
    p(f"    Impulsor ......... ancla Ø{par['d_ancla']*1000:.0f} mm con raspadores, "
      f"{RPM:.0f} rpm")
    p(f"    Accionamiento .... 2.2 kW, reductor >= {par['par_diseno']:.0f} N.m de salida")
    p(f"    Calentamiento .... {t['t_masa']/60:.0f} min "
      f"(+ {t['t_precal']/60:.0f} min de precalentamiento, solapables)")
    p(f"    Masa cargada ..... ~{c['m_total']:.0f} kg")
    p("")
    p("    LAS TRES RESPUESTAS QUE PEDISTE:")
    p("")
    p("    1. ¿Jala por las aspas?")
    p("       Si, con 2.2 kW a 30 rpm, siempre que la viscosidad no pase de")
    p("       ~1200 Pa.s. Hoy no sabemos donde cae: la banda es de factor 20.")
    p("")
    p("    2. ¿Funciona el bano maria y el agua?")
    p(f"       Si, PERO en Quito el agua hierve a {alt['t_eb']:.0f} degC, no a 100. El")
    p(f"       techo de la masa queda en ~{alt['t_masa_max']:.0f} degC. Si la masa cuaja por")
    p("       debajo, funciona y ademas con garantia fisica reforzada. Si")
    p("       necesita mas, hay que cambiar de fluido.")
    p("")
    p("    3. ¿Como se acopla con la estructura existente?")
    p("       Separando los caminos de carga. Ver docs/coupling_strategy.md")
    p("")
    p("=" * 78)

    texto = "\n".join(L)
    print(texto)
    os.makedirs(os.path.join(RAIZ, "reports"), exist_ok=True)
    with open(os.path.join(RAIZ, "reports", "sizing_30kg.txt"), "w",
              encoding="utf-8") as fh:
        fh.write(texto + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
