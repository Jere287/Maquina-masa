#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
 MEZCLADO DE PASTA PEGAJOSA  -  las cuatro objeciones al ancla
=============================================================================

Responde con numeros, no con opinion, a cuatro preguntas concretas:

  Q1  Se cargan liquidos y DESPUES la maicena en polvo.
      ¿Como se que el polvo no se apelmaza en las aspas?
  Q2  ¿Como se que las aspas barren TODO el volumen?
  Q3  ¿Como se que la masa no se empaqueta dentro de la cuadricula que gira?
  Q4  Es super pegajosa. ¿Como se que no se queda adherida?

Y de paso audita dos cosas que estaban MAL en el dimensionamiento anterior
(calculations/sizing_30kg.py), encontradas al revisar los archivos.

TODO valor de propiedad de la masa sigue siendo SUPUESTO. Lo que hace util
este modulo no son las cifras absolutas, sino los UMBRALES: dicen a partir de
que valor medido el diseno deja de funcionar. Eso convierte la medicion de
campo en una decision de si/no, no en un numero suelto.

Salida: reports/mezclado.txt
=============================================================================
"""

from __future__ import annotations

import math
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L: list[str] = []


def p(t: str = "") -> None:
    L.append(t)


def titulo(t: str) -> None:
    p("")
    p("=" * 78)
    p(f" {t}")
    p("=" * 78)


# =============================================================================
# ENTRADAS
# =============================================================================

# --- [PROPORCIONADO] ---------------------------------------------------------
PRODUCTO_KG = 30.0              # masa terminada objetivo por lote
ALTITUD = 2850.0                # m

# --- [SUPUESTO] receta, escalada de la formula base --------------------------
# Formula base: 3 tazas goma + 6 tazas maicena + 2 cda glicerina
#               + 1 cda vaselina + 1 cdta vinagre + 3x2.5 ml benzoato
TAZA_ML = 240.0
RHO_GOMA = 1.10                 # g/ml, cola vinilica (emulsion PVA)
MAICENA_G_TAZA = 128.0          # g por taza, almidon de maiz sin compactar
AGUA_EN_GOMA = 0.50             # fraccion masica de agua en la cola vinilica

# --- [SUPUESTO] propiedades de la masa --------------------------------------
RHO = 1150.0                    # kg/m3
CP = 2800.0                     # J/kg.K
T_INI = 18.0                    # degC
T_CAMISA = 85.0                 # degC
U_PARED = 250.0                 # W/m2.K
T_GELAT = 62.0                  # degC, INICIO de gelatinizacion del almidon
                                #       de maiz. Dato de bibliografia, no de
                                #       esta receta.

# Banda de esfuerzo de fluencia (yield stress) de la masa al cuajar.
# Es la propiedad que decide TODO en este modulo y no esta medida.
TAU_Y_BANDA = [500.0, 1000.0, 2000.0, 5000.0, 10000.0, 20000.0]   # Pa

# --- [DISENIO] geometria y accionamiento -------------------------------------
D_INT = 0.280                   # m, diametro interior del recipiente
LLENADO = 0.65
RPM = 30.0
PAR_MEZCLA = 274.0              # N.m, del sizing anterior (mu=500 Pa.s)
PAR_DISENO = 548.0              # N.m, con factor de servicio 2.0

# Factores de velocidad de corte (Metzner-Otto). Bibliografia.
KS_ANCLA = 11.0
KS_CINTA = 30.0

# Numeros de circulacion axial. Bibliografia.
NC_ANCLA = 0.05
NC_CINTA = 0.60


# =============================================================================
# 0. AUDITORIA DEL DIMENSIONAMIENTO ANTERIOR
# =============================================================================

def bloque_auditoria() -> dict:
    titulo("0. AUDITORIA  —  DOS ERRORES EN EL DIMENSIONAMIENTO ANTERIOR")

    # --- carga real, escalando la receta ---
    goma = 3 * TAZA_ML * RHO_GOMA
    maicena = 6 * MAICENA_G_TAZA
    glicerina = 2 * 15.0 * 1.26
    vaselina = 1 * 15.0 * 0.87
    vinagre = 5.0 * 1.01
    benzoato = 7.5 * 1.05
    carga_base = goma + maicena + glicerina + vaselina + vinagre + benzoato
    agua_base = goma * AGUA_EN_GOMA

    p("")
    p("  ERROR 1 — SE DIMENSIONO SOBRE LA MASA DE PRODUCTO, NO DE CARGA")
    p("")
    p(f"    Receta base, carga total ......... {carga_base:7.0f} g")
    p(f"      de la cual, agua en la cola .... {agua_base:7.0f} g "
      f"({100*agua_base/carga_base:.0f} %)")
    p("")
    p("    Durante la coccion se pierde agua. La masa que sale del equipo")
    p("    pesa MENOS que la que entra. El calculo anterior tomo los 30 kg")
    p("    como si fueran la carga, y son el producto.")
    p("")
    p("    perdida    carga a cargar   volumen de carga")
    p("      %             kg               L")
    p("    " + "-" * 46)
    cargas = {}
    for perd in (0.0, 0.05, 0.10, 0.15):
        carga = PRODUCTO_KG / (1.0 - perd)
        cargas[perd] = carga
        p(f"    {perd*100:5.0f}      {carga:9.1f}        {carga/RHO*1000:8.1f}")
    p("    " + "-" * 46)
    p("")
    p("    El recipiente hay que dimensionarlo para la CARGA. PRO-01 y PRO-02")
    p("    lo resuelven pesando entrada y salida de un lote: dos pesadas.")

    # --- error 2: calor latente ---
    perd_sup = 0.12
    carga_sup = PRODUCTO_KG / (1.0 - perd_sup)
    agua_evap = carga_sup - PRODUCTO_KG
    h_fg = 2308e3                       # J/kg a ~80 degC
    q_sens = carga_sup * CP * (T_GELAT + 10 - T_INI)
    q_lat = agua_evap * h_fg

    p("")
    p("  ERROR 2 — SE IGNORO EL CALOR LATENTE DE EVAPORACION")
    p("")
    p(f"    Con {perd_sup*100:.0f} % de perdida, agua evaporada .. "
      f"{agua_evap:7.2f} kg")
    p(f"    Calor sensible (calentar la carga) . {q_sens/1e6:7.2f} MJ")
    p(f"    Calor LATENTE (evaporar esa agua) .. {q_lat/1e6:7.2f} MJ")
    p(f"    Total .............................. {(q_sens+q_lat)/1e6:7.2f} MJ")
    p(f"    Relacion latente/sensible .......... {q_lat/q_sens:7.2f} x")
    p("")
    p("    El calculo anterior solo conto el sensible. Si la perdida real es")
    p(f"    del {perd_sup*100:.0f} %, el quemador esta infradimensionado por un factor de")
    p(f"    {(q_sens+q_lat)/q_sens:.1f}, y el tiempo de ciclo tambien.")
    p("")
    p("    MATIZ IMPORTANTE, y va a favor: a 80 degC de masa tapada, la")
    p("    evaporacion es MUCHO mas lenta que en el microondas, donde la masa")
    p("    hierve por puntos. Es probable que el bano maria pierda bastante")
    p("    menos agua. Pero eso tiene su propia consecuencia:")
    p("")
    p("    >> El producto puede salir MAS HUMEDO y MAS PEGAJOSO que el que")
    p("       hacen hoy en el microondas, aunque el almidon haya cuajado.")
    p("       No es un fallo del equipo: es que el proceso ya no es el mismo.")
    p("       Puede hacer falta una fase final de secado con la tapa abierta.")
    p("")
    p("    Las dos pesadas de PRO-01 y PRO-02 cierran esto tambien.")

    return {"carga": carga_sup, "perdida": perd_sup, "q_lat": q_lat,
            "q_sens": q_sens}


# =============================================================================
# 1. GEOMETRIA RECALCULADA SOBRE LA CARGA
# =============================================================================

def bloque_geometria(aud: dict) -> dict:
    titulo("1. GEOMETRIA RECALCULADA  (sobre la carga, no sobre el producto)")
    carga = aud["carga"]
    v_carga = carga / RHO
    r = D_INT / 2.0
    h_masa = v_carga / (math.pi * r * r)
    v_recip = v_carga / LLENADO
    h_recip = v_recip / (math.pi * r * r)
    rel = h_masa / D_INT

    p("")
    p(f"    Carga a procesar ................. {carga:7.1f} kg")
    p(f"    Volumen de carga ................. {v_carga*1000:7.1f} L")
    p(f"    Diametro interior ................ {D_INT*1000:7.0f} mm")
    p(f"    Altura de masa ................... {h_masa*1000:7.0f} mm")
    p(f"    Altura interior del recipiente ... {h_recip*1000:7.0f} mm")
    p(f"    Esbeltez h/D de la masa .......... {rel:7.2f}")
    p("")
    if rel > 1.7:
        p("    h/D > 1.7. El ancla queda descartada por geometria, incluso")
        p("    antes de entrar en los problemas de pegajosidad. A esta")
        p("    esbeltez un ancla no circula el volumen: solo remueve una")
        p("    corona junto a la pared.")
    return {"carga": carga, "v": v_carga, "h_masa": h_masa,
            "h_recip": h_recip, "rel": rel}


# =============================================================================
# Q1. INCORPORACION DE LA MAICENA
# =============================================================================

def bloque_q1(g: dict) -> None:
    titulo("Q1. LA MAICENA  —  ¿por que no se apelmaza en las aspas?")

    n = RPM / 60.0
    gamma_ancla = KS_ANCLA * n
    gamma_cinta = KS_CINTA * n
    gamma_grumo = 1000.0        # s^-1, orden de magnitud para romper grumos

    p("")
    p("  1a) EL IMPULSOR NO PUEDE DESHACER GRUMOS. NINGUNO.")
    p("")
    p("    Velocidad de corte disponible (Metzner-Otto, gamma = ks . N):")
    p(f"      ancla   ks={KS_ANCLA:.0f} .... {gamma_ancla:7.2f} 1/s")
    p(f"      cinta   ks={KS_CINTA:.0f} .... {gamma_cinta:7.2f} 1/s")
    p(f"    Necesaria para romper un grumo ya formado .. ~{gamma_grumo:.0f} 1/s")
    p(f"    Deficit ................................... "
      f"{gamma_grumo/gamma_cinta:7.0f} veces")
    p("")
    p("    Estamos DOS ORDENES DE MAGNITUD por debajo. Da igual el impulsor")
    p("    y da igual el motor: a 30 rpm no se rompe un grumo de almidon.")
    p("    Un grumo con la piel ya gelatinizada solo se deshace con corte")
    p("    alto (rotor-estator, 3000 rpm) o a mano.")
    p("")
    p("    CONCLUSION: no se pueden deshacer. Hay que EVITAR que se formen.")

    p("")
    p("  1b) LA VENTANA: EL ALMIDON NO GELATINIZA EN FRIO")
    p("")
    p(f"    Inicio de gelatinizacion del almidon de maiz .. {T_GELAT:.0f} degC")
    p("")
    p("    Por debajo de esa temperatura el almidon es polvo inerte en")
    p("    suspension: la mezcla es fluida y el polvo se incorpora sin")
    p("    dificultad. Por encima, cada particula se hincha y se pega a sus")
    p("    vecinas: ahi nacen los grumos, y ya no hay vuelta atras.")
    p("")
    p("    Si se enciende el quemador con maicena sin dispersar, hay tiempo")
    p("    limitado. Cuanto:")
    p("")
    ua = U_PARED * (math.pi * D_INT * g["h_masa"] + math.pi * D_INT**2 / 4)
    mc = g["carga"] * CP
    tau = mc / ua
    t_gel = tau * math.log((T_CAMISA - T_INI) / (T_CAMISA - T_GELAT))
    p(f"    Constante de tiempo termica ...... {tau/60:7.1f} min")
    p(f"    Tiempo de {T_INI:.0f} a {T_GELAT:.0f} degC ............. "
      f"{t_gel/60:7.1f} min")
    p("")
    p("    Son los minutos que hay para meter TODA la maicena una vez")
    p("    encendido el fuego. Es poco margen para 15 kg de polvo.")
    p("")
    p("  1c) LA REGLA DE OPERACION QUE RESUELVE Q1")
    p("")
    p("    No es un problema de maquina: es de SECUENCIA. Tres reglas:")
    p("")
    p("    R1. TODA la maicena entra EN FRIO, con el quemador APAGADO.")
    p("        La ventana deja de existir. Es gratis.")
    p("")
    p("    R2. La maicena NO se vuelca encima. Se tamiza y se deja caer")
    p("        despacio sobre la superficie en movimiento, o mejor, se")
    p("        introduce POR DEBAJO del nivel de liquido con un conducto.")
    p("        Volcada de golpe forma una capa seca en la superficie que")
    p("        el impulsor dobla hacia dentro sin mojar: eso es un grumo")
    p("        gigante, y es exactamente lo que pasa hoy.")
    p("")
    p("    R3. Antes de encender, se confirma que no hay grumos. Una vez")
    p("        encendido, ya no se corrige.")
    p("")
    p("    Y RESPONDE A TU PREGUNTA LITERAL: el polvo no se apelmaza en las")
    p("    aspas porque cuando entra, las aspas estan sumergidas en liquido")
    p("    frio y fluido. El polvo nunca toca una pala pegajosa. La pala se")
    p("    vuelve pegajosa despues, cuando ya no hay polvo suelto.")
    p("")
    p("    ESTO CAMBIA LA MAQUINA: hace falta una BOCA DE CARGA DE SOLIDOS")
    p("    con tamiz, no un agujero en la tapa.")


# =============================================================================
# Q3. PUENTEO  -  la cuadricula giratoria   (va antes que Q2 porque decide)
# =============================================================================

def bloque_q3(g: dict) -> None:
    titulo("Q3. LA CUADRICULA GIRATORIA  —  ¿se empaqueta la masa dentro?")

    p("")
    p("  RESPUESTA CORTA: SI. Y no se arregla cambiando el tamano de los")
    p("  huecos. Se arregla quitando los huecos.")
    p("")
    p("  CRITERIO DE ARCO (Jenike). Un material cohesivo forma un puente")
    p("  estable sobre una abertura si esta es menor que:")
    p("")
    p("        B = (1 + m) . sigma_c / (rho . g)      m=0 ranura, m=1 circular")
    p("")
    p("  donde sigma_c es la resistencia a compresion sin confinar, que para")
    p("  una pasta plastica vale del orden de 2 . tau_y.")
    p("")
    p("    tau_y     sigma_c    B ranura    B circular   ¿puentea en una")
    p("     Pa         Pa          mm          mm        olla de 280 mm?")
    p("  " + "-" * 68)
    for ty in TAU_Y_BANDA:
        sc = 2.0 * ty
        b_ranura = sc / (RHO * 9.81)
        b_circ = 2.0 * sc / (RHO * 9.81)
        puentea = "SI" if b_ranura * 1000 > D_INT * 1000 else "no"
        p(f"  {ty:7.0f}   {sc:8.0f}   {b_ranura*1000:9.0f}   "
          f"{b_circ*1000:10.0f}        {puentea}")
    p("  " + "-" * 68)
    p("")
    p("  LECTURA. Con un esfuerzo de fluencia de apenas 2000 Pa —una pasta")
    p("  blanda, mucho menos que porcelana fria cuajada— el arco estable")
    p("  mide ya 355 mm. La olla entera mide 280 mm de diametro.")
    p("")
    p("  Es decir: ESTA MASA PUENTEA CUALQUIER ABERTURA QUE QUEPA EN ESTA")
    p("  OLLA. No hay tamano de hueco que la deje pasar por gravedad.")
    p("")
    p("  CONSECUENCIAS DE DISENO, y son duras:")
    p("")
    p("   1. Cualquier estructura del impulsor que forme un lazo cerrado o")
    p("      semicerrado —el travesano intermedio que yo propuse, un aro,")
    p("      una cuadricula, dos brazos con barra— se llena de masa y a")
    p("      partir de ahi GIRA COMO UN SOLIDO. Deja de mezclar. Es")
    p("      exactamente lo que intuiste.")
    p("")
    p("   2. El ancla con travesano intermedio que propuse en")
    p("      calculations/sizing_30kg.py ES ESA CUADRICULA. Estaba mal.")
    p("      Lo puse para arrastrar el nucleo y lo que hace es fabricarlo.")
    p("")
    p("   3. No sirve descargar por gravedad por un fondo con valvula: la")
    p("      masa hace arco sobre la boca y no baja. La descarga tiene que")
    p("      ser por desplazamiento positivo o por volteo.")
    p("")
    p("  LO QUE SI FUNCIONA: DESPLAZAMIENTO POSITIVO.")
    p("  Que ningun elemento espere a que la masa fluya hacia el. Cada")
    p("  elemento tiene que EMPUJAR masa a un sitio distinto, continuamente,")
    p("  y no dejar ningun volumen sin barrer entre pasada y pasada.")
    p("")
    p("  Eso es una CINTA HELICOIDAL: una helice abierta, sin travesanos,")
    p("  sin lazos cerrados y sin superficies horizontales. Bombea como un")
    p("  tornillo: sube masa por la pared y la deja caer por el centro, o al")
    p("  reves. No hay volumen que pueda quedarse quieto.")


# =============================================================================
# Q2. BARRIDO DEL VOLUMEN
# =============================================================================

def bloque_q2(g: dict) -> dict:
    titulo("Q2. BARRIDO  —  ¿las aspas alcanzan todo el volumen?")

    r_olla = D_INT / 2.0
    h = g["h_masa"]

    p("")
    p("  2a) ZONA MUERTA JUNTO A LA PARED  (modelo de caverna)")
    p("")
    p("    En un fluido con esfuerzo de fluencia, el impulsor solo mueve una")
    p("    'caverna' a su alrededor. Mas alla, el material esta QUIETO. El")
    p("    radio de esa caverna sale de un balance de par: en su frontera, el")
    p("    esfuerzo cortante iguala al de fluencia.")
    p("")
    p("        T = 2 . pi . tau_y . H . Rc^2   ->   Rc = raiz(T / (2 pi tau_y H))")
    p("")
    p(f"    Con H = {h*1000:.0f} mm de masa y radio de olla {r_olla*1000:.0f} mm:")
    p("")
    p("     tau_y    Rc con 274 N.m   Rc con 548 N.m   ¿barre hasta")
    p("      Pa            mm               mm          la pared?")
    p("    " + "-" * 60)
    tau_lim = None
    for ty in TAU_Y_BANDA:
        rc1 = math.sqrt(PAR_MEZCLA / (2 * math.pi * ty * h))
        rc2 = math.sqrt(PAR_DISENO / (2 * math.pi * ty * h))
        ok = "SI" if rc2 >= r_olla else "NO - zona muerta"
        p(f"    {ty:6.0f}      {rc1*1000:9.0f}        {rc2*1000:9.0f}"
          f"        {ok}")
    tau_lim = PAR_DISENO / (2 * math.pi * r_olla**2 * h)
    p("    " + "-" * 60)
    p("")
    p(f"    UMBRAL: con el par de diseno de {PAR_DISENO:.0f} N.m, el limite esta en")
    p(f"    tau_y = {tau_lim:.0f} Pa.")
    p("")
    p("    >> Si la masa al cuajar supera ese esfuerzo de fluencia, queda un")
    p("       anillo muerto pegado a la pared, por mucho par que se ponga en")
    p("       el eje: el par se gasta en la caverna interior.")
    p("")
    p("    ESTA ES LA CIFRA DE GO / NO-GO DE TODA LA MAQUINA, y se mide con")
    p("    PAR-06 (brazo de palanca) en una tarde.")
    p("")
    p("    MATIZ: los raspadores cambian el problema en la pared. Un raspador")
    p("    no espera a que la masa fluya: la arranca por interferencia")
    p("    mecanica. Con raspadores, la pared se renueva aunque haya zona")
    p("    muerta. Pero entonces el problema se muda al NUCLEO, que es 2b.")

    p("")
    p("  2b) RECIRCULACION AXIAL  —  el problema de verdad")
    p("")
    n = RPM / 60.0
    d_imp = D_INT - 2 * 0.010
    v = g["v"]

    # Ancla: bombeo axial incidental
    q_ancla = NC_ANCLA * n * d_imp ** 3
    t_ancla = v / q_ancla

    # Cinta: dos estimaciones, porque discrepan y conviene ver la banda.
    #  (a) correlacion de bibliografia, Nc = Q/(N.D^3) ~ 0.5-0.9 para cinta
    #  (b) desplazamiento geometrico de la banda de la cinta, deliberadamente
    #      conservador: solo cuenta el area barrida por el fleje.
    q_cinta_corr = NC_CINTA * n * d_imp ** 3
    t_cinta_corr = v / q_cinta_corr

    paso = d_imp                       # p/D = 1, valor tipico
    ancho_cinta = 0.10 * d_imp
    r_o = d_imp / 2.0
    r_i = r_o - ancho_cinta
    area_banda = math.pi * (r_o**2 - r_i**2)
    rend = 0.50                        # rendimiento volumetrico
    q_cinta_geo = paso * area_banda * n * rend
    t_cinta_geo = v / q_cinta_geo

    q_cinta, t_cinta = q_cinta_geo, t_cinta_geo   # el caso desfavorable

    p("    Un ancla mueve la masa EN CIRCULOS. Su bombeo de arriba a abajo es")
    p("    incidental. Una cinta helicoidal bombea por desplazamiento")
    p("    positivo, como un tornillo: es geometria, no conveccion.")
    p("")
    p(f"    Volumen a renovar ................ {v*1000:7.1f} L")
    p("")
    p(f"    ANCLA   caudal axial ............. {q_ancla*1000:7.2f} L/s")
    p(f"            tiempo de renovacion ..... {t_ancla:7.0f} s")
    p("")
    p("    CINTA   dos estimaciones, porque no coinciden:")
    p(f"      (a) correlacion Nc={NC_CINTA:.1f} ..... {q_cinta_corr*1000:7.2f} L/s"
      f"  ->  {t_cinta_corr:5.0f} s")
    p(f"      (b) geometrica, paso {paso*1000:.0f} mm ... "
      f"{q_cinta_geo*1000:7.2f} L/s  ->  {t_cinta_geo:5.0f} s")
    p("      (b) es deliberadamente pesimista: solo cuenta el area barrida")
    p("      por el fleje, no el volumen arrastrado entre fleje y eje. El")
    p("      valor real cae entre las dos.")
    p("")
    p(f"    VENTAJA DE LA CINTA .............. de {t_ancla/t_cinta_geo:.1f} a "
      f"{t_ancla/t_cinta_corr:.0f} veces")
    p("")
    p("    Y el numero del ancla es OPTIMISTA: supone que la masa circula.")
    p("    Con una pasta que puentea (Q3), el bombeo incidental del ancla")
    p("    tiende a cero, porque lo que gira es un tapon solido. El de la")
    p("    cinta no: es desplazamiento geometrico y no depende de que la")
    p("    masa 'quiera' fluir.")
    return {"t_cinta": t_cinta, "tau_lim": tau_lim, "d_imp": d_imp}


# =============================================================================
# Q4. ADHERENCIA
# =============================================================================

def bloque_q4(g: dict, q2: dict) -> None:
    titulo("Q4. PEGAJOSIDAD  —  ¿que se queda adherido y como se evita?")

    p("")
    p("  AVISO DE HONESTIDAD: la adherencia NO se puede calcular de primeros")
    p("  principios. Depende de la energia superficial de la masa contra cada")
    p("  material, y eso se mide, no se deduce. Lo que si se puede hacer es")
    p("  separar lo que la geometria decide de lo que hay que ensayar.")
    p("")
    p("  4a) LO QUE SI DECIDE LA GEOMETRIA")
    p("")
    p("    Una pasta pegajosa se queda donde puede APOYARSE. Por eso:")
    p("")
    p("    - Ninguna superficie plana mirando hacia ARRIBA en la zona mojada.")
    p("      Una pletina plana horizontal es una repisa: acumula hasta que el")
    p("      monton gira con ella. Barra redonda o pletina a 45 grados o mas.")
    p("    - Ningun rincon interior en angulo vivo. Todo radio >= 6 mm.")
    p("    - Ningun lazo cerrado (ver Q3).")
    p("    - Nada de tornillos, tuercas ni cabezas expuestas en la zona")
    p("      mojada: cada hueco de una llave es un nido de masa que no se")
    p("      limpia y termina en el producto.")
    p("    - Acabado pulido, Ra <= 0.8 micras. La adherencia de pastas cae")
    p("      mucho al pasar de laminado a pulido. No es cosmetica.")
    p("")
    p("  4b) LA CAPA DE PARED SI SE RESUELVE, Y ES LO IMPORTANTE")
    p("")
    p("    La masa adherida a la PARED es la que se quema, porque es la que")
    p("    esta contra la fuente de calor y no se renueva. Con raspadores:")
    v_rasp = 2 * math.pi * (q2["d_imp"] / 2.0) * (RPM / 60.0)
    p(f"      velocidad del raspador en la pared .. {v_rasp:7.2f} m/s")
    p(f"      la pelicula se renueva cada ......... {60.0/RPM:7.1f} s")
    p("")
    p("    Ese es el mecanismo que hoy no existe y que resuelve la costra y")
    p("    el desperdicio. Es independiente de la pegajosidad: el raspador")
    p("    no espera a que la masa se despegue, la arranca.")
    p("")
    p("  4c) LO QUE SE QUEDA EN EL IMPULSOR Y NO TIENE ARREGLO")
    p("")
    p("    Sobre la propia cinta SIEMPRE va a quedar masa adherida. Eso no")
    p("    es un fallo: es normal en cualquier mezclador de pasta. Lo que")
    p("    importa es que sea una pelicula fina y uniforme, no un monton")
    p("    creciente. La diferencia entre las dos cosas la marcan las reglas")
    p("    de 4a.")
    p("")
    p("    Consecuencia de operacion: la cinta hay que poder EXTRAERLA para")
    p("    limpiarla. Cubo desmontable en el eje, sin herramienta especial.")
    p("")
    p("  4d) EL ENSAYO QUE CIERRA ESTO  —  15 minutos, sin instrumentos")
    p("")
    p("    Preparar 3 probetas de ~100 cm2: inox laminado, inox pulido y")
    p("    PTFE. Pesarlas. Sumergirlas en la masa recien cuajada, sacarlas,")
    p("    dejarlas escurrir 60 s en vertical y volver a pesarlas.")
    p("")
    p("    La diferencia, en g/m2, dice cual material usar y cuanto producto")
    p("    se va a quedar pegado por lote. Es el unico dato que convierte")
    p("    'es super pegajosa' en una cifra de diseno.")


# =============================================================================
# ESTRUCTURA: EL LAZO DE PAR  (por que sobran las columnas grandes)
# =============================================================================

def bloque_estructura(g: dict) -> None:
    titulo("EXTRA. LAS COLUMNAS AZULES  —  por que sobran casi enteras")

    p("")
    p("  La pregunta era: ¿que hacen ahi esas columnas tan grandes?")
    p("  Respuesta honesta: estaban resolviendo mal un problema real.")
    p("")
    p("  SIGAMOS EL PAR. El par no desaparece, circula:")
    p("")
    p("     motor -> eje -> cinta -> MASA -> pared de la olla -> cuna ->")
    p("     -> soporte del motor -> motor")
    p("")
    p("  Es un LAZO CERRADO. El par que el reductor mete en el eje vuelve por")
    p("  la masa y la olla hasta el propio soporte del motor. Si el soporte")
    p("  del motor y la cuna de la olla son la MISMA pieza rigida, el par se")
    p("  queda dentro de ese conjunto y no sale de el.")
    p("")
    p("  Yo lo monte al reves: puse el motor arriba de una torre de 1.75 m y")
    p("  la olla colgando de esa misma torre. Asi el lazo tiene que recorrer")
    p("  toda la torre, y por eso salia una estructura enorme: estaba")
    p("  dimensionada para transmitir 548 N.m a lo largo de metro y medio.")
    p("")
    p("  LO CORRECTO: cerrar el lazo cerca de donde nace.")
    p("")
    p("    - Un BASTIDOR DE PAR compacto une el soporte del motor con la cuna")
    p("      de la olla. Recorrido corto, seccion modesta.")
    p("    - La olla se KIVETEA a la cuna con topes antigiro. Hoy solo se")
    p("      apoya por gravedad: eso ya estaba senalado como pendiente R-05")
    p("      en el inventario de componentes, y con este par es critico. Una")
    p("      olla que gira con la masa es un accidente.")
    p("    - La estructura de abajo pasa a llevar SOLO PESO.")
    p("")
    peso = g["carga"] + 12.0 + 20.0 + 25.0 + 70.0
    p("  ¿Y aguanta tu bastidor actual solo el peso?")
    p("")
    p(f"    Carga ({g['carga']:.0f}) + agua (12) + inox (20) + eje/cinta (25)")
    p(f"    + accionamiento (70) ............. {peso:7.0f} kg  [SUPUESTO]")
    p("")
    tramo = 0.41
    p_viga = peso * 9.81 / 4.0
    m_viga = p_viga * tramo / 4.0
    m_adm_40 = 367.0
    p(f"    Reparto por viga del marco ....... {p_viga:7.0f} N")
    p(f"    Momento flector en viga .......... {m_viga:7.1f} N.m")
    p(f"    Capacidad de 40x40x2 ............. {m_adm_40:7.0f} N.m")
    p(f"    Factor de seguridad .............. {m_adm_40/m_viga:7.1f}")
    p("")
    p("    >> SI. Con un factor amplio. El bastidor nunca tuvo problema con")
    p("       el PESO: lo tenia con el PAR. Si el par ya no pasa por el, el")
    p("       bastidor se conserva casi tal cual y las columnas grandes")
    p("       desaparecen.")
    p("")
    p("  LO QUE SI SIGUE HACIENDO FALTA, y no es negociable:")
    p("")
    p("    - ANCLAJE AL PISO. Con la olla llena y alta, el centro de gravedad")
    p("      sube mucho. En arranque, el par no esta equilibrado todavia")
    p("      —la masa aun no reacciona— y ahi si sale par al exterior.")
    p("    - TOPES ANTIGIRO en la olla.")
    p("    - Rigidez del bastidor de par: si flecta, el eje se descentra y se")
    p("      pierde la luz del raspador.")


# =============================================================================
# CONCLUSION
# =============================================================================

def bloque_conclusion(g: dict, q2: dict) -> None:
    titulo("CONCLUSION  —  que cambia en el diseno")

    p("")
    p("  LAS CUATRO RESPUESTAS:")
    p("")
    p("  Q1  La maicena no se apelmaza en las aspas porque entra EN FRIO,")
    p("      tamizada y bajo el nivel de liquido, con el fuego apagado. No es")
    p("      un problema de maquina sino de secuencia. Pero obliga a una boca")
    p("      de carga de solidos con tamiz. A 30 rpm NINGUN impulsor puede")
    p("      deshacer un grumo ya formado: estamos 60 veces por debajo del")
    p("      corte necesario.")
    p("")
    p(f"  Q2  Barre todo mientras el esfuerzo de fluencia no pase de")
    p(f"      ~{q2['tau_lim']:.0f} Pa. Por encima queda anillo muerto en la pared. Los")
    p("      raspadores cubren la pared por interferencia mecanica; el")
    p("      nucleo lo cubre la cinta, no el ancla.")
    p("")
    p("  Q3  SI se empaqueta, y tenias razon. Esta masa puentea cualquier")
    p("      abertura que quepa en la olla. La solucion no es agrandar")
    p("      huecos: es que no haya huecos ni lazos. El travesano que")
    p("      propuse era el error.")
    p("")
    p("  Q4  Algo siempre se queda pegado. Lo que decide si es una pelicula")
    p("      o un monton es la geometria: nada horizontal hacia arriba, nada")
    p("      de lazos, radios generosos, pulido. Y un ensayo de 15 minutos.")
    p("")
    p("  CAMBIOS EN EL DISENO:")
    p("")
    p("   1. FUERA el ancla con travesano.  ENTRA cinta helicoidal con")
    p("      raspadores, sin travesanos ni lazos cerrados.")
    p("   2. FUERA la torre grande.  ENTRA bastidor de par compacto que cierra")
    p("      el lazo motor-cuna, sobre el bastidor actual, que solo lleva peso.")
    p("   3. NUEVO: topes antigiro en la olla. Obligatorio.")
    p("   4. NUEVO: boca de carga de solidos con tamiz.")
    p("   5. RECALCULAR sobre la CARGA, no sobre el producto, y meter el")
    p("      calor latente de evaporacion en el balance del quemador.")
    p("   6. La descarga no puede ser por gravedad: la masa hace arco.")
    p("      Volteo o extraccion de la olla.")
    p("")
    p("  LO QUE BLOQUEA EL SIGUIENTE PASO:")
    p("")
    p("    PAR-06   esfuerzo de fluencia al cuajar  -> Q2, motor, reductor")
    p("    PRO-01   masa cargada                    -> geometria del recipiente")
    p("    PRO-02   masa de producto                -> perdida por evaporacion")
    p("    PRO-05   temperatura de cuaje            -> viabilidad del bano")
    p("    ensayo de adherencia 4d                  -> material del impulsor")


def main() -> int:
    p("=" * 78)
    p(" MEZCLADO DE PASTA PEGAJOSA - REVISION DEL IMPULSOR")
    p(" Mezcladora de porcelana fria  ·  Quito")
    p("=" * 78)
    aud = bloque_auditoria()
    g = bloque_geometria(aud)
    bloque_q1(g)
    bloque_q3(g)
    q2 = bloque_q2(g)
    bloque_q4(g, q2)
    bloque_estructura(g)
    bloque_conclusion(g, q2)

    texto = "\n".join(L)
    print(texto)
    os.makedirs(os.path.join(RAIZ, "reports"), exist_ok=True)
    with open(os.path.join(RAIZ, "reports", "mezclado.txt"), "w",
              encoding="utf-8") as fh:
        fh.write(texto + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
