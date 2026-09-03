#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
 REDISENO EVOLUTIVO - Maquina mezcladora-cocedora de porcelana fria
 Emprendimiento en Quito, Ecuador
=============================================================================

QUE ES ESTE ARCHIVO
-------------------
Modelo CAD parametrico del prototipo EXISTENTE mas las modificaciones del
redisenio. NO se parte de cero: el bastidor de tubo negro, el brazo superior,
la repisa de la olla y el quemador GLP se CONSERVAN y se reutilizan tal cual.
Lo que cambia se marca como pieza NUEVA y se une con tornilleria a lo que ya
existe, para que el taller solo fabrique lo nuevo.

DE DONDE SALE EL "ESTADO ACTUAL"
--------------------------------
De las fotos del prototipo fisico (Drive del proyecto). Lo observado:
  - Bastidor tipo portico de tubo cuadrado negro, mesa con vano central.
  - Olla de acero INOX de pared SIMPLE, tipo tamalera (ancha, relacion ~1:1).
  - Quemador GLP DIRECTO bajo el fondo de la olla (manguera amarilla visible).
  - Impulsor = BATIDOR GLOBO de alambre.
  - Motor Hubbell Special Products, placa: HP .125 (1/8 HP = 93 W), 115 V.

Es decir: el equipo fisico todavia NO tiene camisa de agua, NO tiene ancla y
NO tiene el motorreductor. Las 3 fallas del proceso (costra, motor que no
mueve, coccion despareja) son consecuencia directa de esas 3 ausencias.

LOS 3 CAMBIOS DE ESTE REDISENIO
-------------------------------
  1) MOTOR   : motorreductor sinfin-corona sobre PLACA ADAPTADORA atornillada
               al brazo superior existente. No se corta ni se suelda el
               bastidor. Se agrega soporte de rodamiento para carga radial.
  2) ALTURA  : EMPALMES ATORNILLADOS con el mismo perfil de tubo 40x40, para
               alojar la olla angosta y alta. La altura se gana ABAJO
               (+250 mm en las 4 patas), porque la olla cuelga de la mesa;
               mas +120 mm de columna solo como holgura de montaje del eje.
  3) UNIONES : cuna de olla, bandeja de quemador y placa de motor pasan a ser
               uniones ATORNILLADAS de desmontaje rapido (limpieza entre lotes).

  + Los dos cambios de fisica que hacen que el redisenio tenga sentido:
       - CAMISA DE AGUA (bano maria) alrededor de la olla -> tope fisico 100 C.
       - IMPULSOR TIPO ANCLA con raspadores de PTFE -> reemplaza el batidor.

CONVENCIONES
------------
  - Unidades: milimetros (mm), grados, kg, W, N.m, C.
  - Origen (0,0,0): piso, sobre el EJE de la olla.
  - Eje Z: vertical hacia arriba.
  - Cada parametro lleva etiqueta de procedencia:
       [MEDIDO]   valor tomado del equipo real
       [FOTO]     estimado a escala desde las fotos - CONFIRMAR CON FLEXOMETRO
       [DISENIO]  valor decidido en este redisenio
       [NORMA]    valor de catalogo / practica estandar

  Los parametros [FOTO] son los unicos que pueden mover cotas de interfaz.
  Corregirlos aqui arriba y volver a correr el script reajusta todo el modelo.

SALIDAS
-------
  output/maquina_completa.step   ensamble completo (STEP AP214, para taller/CAM)
  output/maquina_completa.stl    malla del ensamble (visualizacion / impresion)
  output/piezas/<pieza>.step     cada pieza suelta
  output/piezas/<pieza>.stl      cada pieza suelta
  output/vistas/*.svg            proyecciones ortogonales rapidas

USO
---
  python3 rediseno_prototipo.py
=============================================================================
"""

from __future__ import annotations

import math
import os
import sys
import time
from dataclasses import dataclass, field

try:
    import cadquery as cq
    from cadquery import exporters
except ImportError:  # pragma: no cover
    sys.exit("Falta CadQuery.  Instalar con:  pip3 install cadquery")


# =============================================================================
# 1. PARAMETROS
# =============================================================================

@dataclass
class Parametros:
    """Tabla unica de cotas. Cambiar aqui, no dentro de las funciones."""

    # -- 1.1 BASTIDOR EXISTENTE (se conserva) --------------------------------
    # Portico de tubo cuadrado negro visto en las fotos.
    tubo: float = 40.0              # [FOTO] lado del tubo cuadrado
    tubo_esp: float = 2.0           # [FOTO] espesor de pared del tubo
    mesa_ancho: float = 450.0       # [FOTO] ancho de mesa (X)
    mesa_fondo: float = 450.0       # [FOTO] fondo de mesa (Y)
    mesa_altura: float = 720.0      # [FOTO] piso -> cara superior de la mesa
    travesano_z: float = 180.0      # [FOTO] altura del travesano inferior
    columna_alt_orig: float = 620.0 # [FOTO] mesa -> cara inferior del brazo
    brazo_largo: float = 350.0      # [FOTO] voladizo del brazo hacia el eje

    # -- 1.2 OLLA ORIGINAL (se retira, solo referencia) ----------------------
    olla_orig_d: float = 320.0      # [FOTO] diametro de la olla tamalera
    olla_orig_h: float = 350.0      # [FOTO] altura de la olla tamalera

    # -- 1.3 OLLA NUEVA, angosta y alta (NUEVA) ------------------------------
    # Geometria angosta a proposito: el calor entra por la pared lateral y el
    # tiempo de cuaje escala con R^2. Ver bloque de verificacion termica.
    olla_d_int: float = 200.0       # [DISENIO] diametro interior
    olla_h_int: float = 640.0       # [DISENIO] altura interior
    olla_esp: float = 1.5           # [NORMA] espesor chapa inox 304
    olla_fondo_esp: float = 2.0     # [NORMA] espesor del fondo (mas cargado)

    # -- 1.4 CAMISA DE AGUA / BANO MARIA (NUEVA) -----------------------------
    camisa_gap: float = 20.0        # [DISENIO] luz anular ocupada por el agua
    camisa_esp: float = 1.5         # [NORMA] espesor chapa exterior
    camisa_altura: float = 480.0    # [DISENIO] altura mojada de la camisa
    camisa_fondo_gap: float = 25.0  # [DISENIO] colchon de agua bajo el fondo
    venteo_d: float = 15.0          # [DISENIO] tubo de venteo (sistema ABIERTO)
    venteo_largo: float = 70.0      # [DISENIO]
    llenado_d: float = 20.0         # [DISENIO] boca de recarga de agua

    # -- 1.5 EJE E IMPULSOR TIPO ANCLA (NUEVO) -------------------------------
    # Ø40 y no Ø30: con Ø30 la flecha del voladizo dentro de la olla es de
    # 1.41 mm y la luz del raspador es de 1.50 mm -> el raspador rozaria la
    # pared. Ver verificacion [10]. Es el calculo el que fija el diametro.
    eje_d: float = 40.0             # [DISENIO] eje inox macizo
    ancla_barra_esp: float = 12.0   # [DISENIO] espesor radial de la barra
    ancla_barra_ancho: float = 25.0 # [DISENIO] ancho tangencial de la barra
    rasp_esp: float = 8.0           # [DISENIO] espesor del raspador PTFE
    rasp_gap: float = 1.5           # [DISENIO] luz raspador <-> pared
    ancla_fondo_gap: float = 6.0    # [DISENIO] luz raspador de fondo
    cubo_d: float = 85.0            # [DISENIO] cubo de acople al eje
    cubo_h: float = 60.0            # [DISENIO]

    # -- 1.6 MOTORREDUCTOR (NUEVO) -------------------------------------------
    # Envolvente simplificada: sirve para verificar interferencias y agujeros.
    motor_hp: float = 1.0           # [DISENIO] potencia nominal
    motor_rpm: float = 30.0         # [DISENIO] rpm de salida
    reductor_ratio: float = 58.0    # [NORMA] sinfin-corona 58:1
    motor_l: float = 260.0          # [NORMA] envolvente motor (largo)
    motor_d: float = 140.0          # [NORMA] envolvente motor (diametro)
    red_ancho: float = 160.0        # [NORMA] caja reductora
    red_fondo: float = 150.0        # [NORMA]
    red_alto: float = 170.0         # [NORMA]
    brida_d: float = 160.0          # [NORMA] brida de salida del reductor
    brida_esp: float = 14.0         # [NORMA]
    brida_pcd: float = 130.0        # [NORMA] circulo de pernos de la brida
    brida_perno: float = 11.0       # [NORMA] pasante para M10

    # -- 1.7 PIEZAS DE ADAPTACION ATORNILLADAS (NUEVAS) ----------------------
    # CAMBIO #2 - la altura se gana ABAJO, no arriba. La olla cuelga de la
    # mesa, asi que lo que hay que crear es luz LIBRE BAJO LA MESA para que
    # entren olla + camisa + quemador. Alargar la columna no resuelve eso.
    ext_patas: float = 250.0        # [DISENIO] alargue de las 4 patas
    # Se deja en 0: al subir la mesa 250 mm, la columna original de 620 mm ya
    # deja el brazo mas alto de lo necesario. Alargarla mas solo alarga el eje
    # en voladizo, que es justo lo que hay que evitar. Se conserva el
    # parametro por si al medir el bastidor real hiciera falta.
    ext_columna: float = 0.0        # [DISENIO] alargue de columna
    placa_esp: float = 12.0         # [DISENIO] espesor placas de acero
    placa_motor: float = 250.0      # [DISENIO] lado de la placa del motor
    placa_perno: float = 13.0       # [DISENIO] pasante para M12
    empalme_placa: float = 120.0    # [DISENIO] lado de las placas del empalme
    soporte_rod_d: float = 100.0    # [DISENIO] alojamiento de rodamiento
    soporte_rod_h: float = 70.0     # [DISENIO]
    cuna_esp: float = 8.0           # [DISENIO] espesor de la cuna de la olla
    cuna_holgura: float = 3.0       # [DISENIO] holgura radial de apoyo

    # -- 1.8 QUEMADOR GLP EXISTENTE (se conserva, baja de posicion) ----------
    quemador_d: float = 180.0       # [FOTO] diametro del anillo quemador
    quemador_tubo: float = 14.0     # [FOTO] diametro del tubo del anillo
    quemador_gap: float = 90.0      # [DISENIO] separacion fondo camisa->quemador
    quemador_kbtu: float = 20.0     # [FOTO] potencia nominal del quemador

    # -- 1.9 TAPA PARTIDA (NUEVA) --------------------------------------------
    tapa_esp: float = 2.0           # [DISENIO]
    tapa_boca: float = 90.0         # [DISENIO] boca de carga

    # -- 1.10 PROPIEDADES DE PROCESO (para el bloque de verificacion) --------
    # OJO: estimadas de pastas de almidon. NO medidas en la receta real.
    lote_kg: float = 15.0           # [DISENIO] lote objetivo
    rho_masa: float = 1150.0        # [ESTIMADO] kg/m3
    cp_masa: float = 2800.0         # [ESTIMADO] J/kg.K
    k_masa: float = 0.45            # [ESTIMADO] W/m.K
    t_inicial: float = 20.0         # [DISENIO] C
    t_cuaje: float = 72.0           # [ESTIMADO] C  <-- A VALIDAR EN CAMPO
    t_camisa: float = 90.0          # [DISENIO] C
    t_costra: float = 120.0         # [NORMA] C umbral de costra
    u_pared: float = 250.0          # [ESTIMADO] W/m2.K coef. global con ancla
    rend_quemador: float = 0.40     # [ESTIMADO] rendimiento a la camisa

    # -- Derivados ------------------------------------------------------------
    def __post_init__(self) -> None:
        self.olla_r_int = self.olla_d_int / 2.0
        self.olla_r_ext = self.olla_r_int + self.olla_esp
        self.camisa_r_int = self.olla_r_ext + self.camisa_gap
        self.camisa_r_ext = self.camisa_r_int + self.camisa_esp
        # Altura de mesa EFECTIVA tras alargar las patas. mesa_altura sigue
        # siendo el valor medido del bastidor original; mesa_z es donde queda
        # la mesa una vez montadas las extensiones atornilladas.
        self.mesa_z = self.mesa_altura + self.ext_patas
        self.brazo_z = self.mesa_z + self.columna_alt_orig + self.ext_columna
        # Nivel de masa alcanzado por el lote
        vol_masa_m3 = self.lote_kg / self.rho_masa
        self.h_masa = (vol_masa_m3 * 1e9) / (math.pi * self.olla_r_int ** 2)
        self.vol_olla_l = math.pi * (self.olla_r_int / 1000.0) ** 2 * \
            (self.olla_h_int / 1000.0) * 1000.0
        self.vol_masa_l = vol_masa_m3 * 1000.0


P = Parametros()


# -----------------------------------------------------------------------------
# Posicionamiento vertical de la olla
# -----------------------------------------------------------------------------
# La olla se apoya por su borde (pestania) sobre la cuna atornillada a la mesa,
# es decir cuelga hacia abajo dentro del vano del bastidor. Se recalcula aqui
# para que quede explicito y trazable.
OLLA_Z_BORDE = P.mesa_z                                   # borde superior
OLLA_Z_FONDO_INT = OLLA_Z_BORDE - P.olla_h_int            # fondo interior
OLLA_Z_FONDO_EXT = OLLA_Z_FONDO_INT - P.olla_fondo_esp    # fondo exterior
CAMISA_Z_FONDO = OLLA_Z_FONDO_EXT - P.camisa_fondo_gap - P.camisa_esp
QUEMADOR_Z = CAMISA_Z_FONDO - P.quemador_gap


# =============================================================================
# 2. UTILIDADES DE GEOMETRIA
# =============================================================================

def tubo_cuadrado(largo: float, lado: float = None, esp: float = None,
                  eje: str = "Z") -> cq.Workplane:
    """
    Tramo de tubo estructural cuadrado hueco.

    Convencion fija: arranca en el ORIGEN y crece en el sentido POSITIVO del
    eje indicado, con la seccion centrada en los otros dos. Se construye
    siempre en XY y se rota, en vez de cambiar de plano de trabajo: los
    planos "XZ"/"YZ" de CadQuery extruyen hacia -Y y centran en Z, y eso ya
    dejo el brazo descolocado una vez.
    """
    lado = P.tubo if lado is None else lado
    esp = P.tubo_esp if esp is None else esp
    interior = lado - 2.0 * esp
    t = (cq.Workplane("XY")
         .rect(lado, lado)
         .rect(interior, interior)
         .extrude(largo))
    if eje == "Z":
        return t
    if eje == "X":                       # +Z -> +X
        return t.rotate((0, 0, 0), (0, 1, 0), 90)
    if eje == "Y":                       # +Z -> +Y
        return t.rotate((0, 0, 0), (1, 0, 0), -90)
    raise ValueError(f"eje no valido: {eje}")


def placa_con_pernos(lado_x: float, lado_y: float, esp: float,
                     pcd_x: float, pcd_y: float, d_perno: float,
                     d_central: float = 0.0) -> cq.Workplane:
    """Placa rectangular con 4 pasantes en las esquinas y agujero central."""
    pl = cq.Workplane("XY").box(lado_x, lado_y, esp)
    pl = (pl.faces(">Z").workplane()
            .rect(pcd_x, pcd_y, forConstruction=True)
            .vertices().hole(d_perno))
    if d_central > 0.0:
        pl = pl.faces(">Z").workplane().hole(d_central)
    return pl


def anillo(r_ext: float, r_int: float, altura: float) -> cq.Workplane:
    """Cilindro hueco (anillo extruido)."""
    return (cq.Workplane("XY")
            .circle(r_ext)
            .circle(r_int)
            .extrude(altura))


def toro(r_medio: float, r_tubo: float) -> cq.Workplane:
    """Toro solido, util para el anillo del quemador."""
    return cq.Workplane(obj=cq.Solid.makeTorus(r_medio, r_tubo))


# =============================================================================
# 3. PIEZAS QUE SE CONSERVAN DEL PROTOTIPO ACTUAL
# =============================================================================

def bastidor_existente() -> cq.Workplane:
    """
    Bastidor tipo portico de tubo cuadrado, tal como esta hoy en el taller.
    Se reutiliza SIN modificaciones: patas, travesanos, marco de mesa y
    columna vertical original. Lo unico que se le hace es atornillar piezas.
    """
    t = P.tubo
    x = P.mesa_ancho / 2.0 - t / 2.0
    y = P.mesa_fondo / 2.0 - t / 2.0
    h_pata = P.mesa_altura - t     # las patas llegan bajo el marco de mesa

    partes = []

    # --- 4 patas ---
    for sx in (-1, 1):
        for sy in (-1, 1):
            partes.append(tubo_cuadrado(h_pata).translate((sx * x, sy * y, 0)))

    # --- marco de mesa (perimetro superior) ---
    for sy in (-1, 1):
        partes.append(tubo_cuadrado(P.mesa_ancho - t, eje="X")
                      .translate((-(P.mesa_ancho - t) / 2.0, sy * y,
                                  h_pata + t / 2.0)))
    for sx in (-1, 1):
        largo_y = P.mesa_fondo - 3 * t
        partes.append(tubo_cuadrado(largo_y, eje="Y")
                      .translate((sx * x, -largo_y / 2.0, h_pata + t / 2.0)))

    # --- travesanos inferiores (rigidizan las patas) ---
    for sy in (-1, 1):
        partes.append(tubo_cuadrado(P.mesa_ancho - t, eje="X")
                      .translate((-(P.mesa_ancho - t) / 2.0, sy * y,
                                  P.travesano_z + t / 2.0)))

    # --- columna vertical original, en el borde trasero ---
    partes.append(tubo_cuadrado(P.columna_alt_orig)
                  .translate((0, y, P.mesa_altura)))

    res = partes[0]
    for p in partes[1:]:
        res = res.union(p)
    # El bastidor original no cambia: sube en bloque sobre las extensiones
    # de pata. Por eso se traslada, en vez de re-cotarlo.
    return res.translate((0, 0, P.ext_patas))


def brazo_superior() -> cq.Workplane:
    """
    Brazo en voladizo que sostiene el motor. Pieza EXISTENTE: se conserva y
    se reubica arriba del empalme de columna. Aqui se le agregan los 4
    pasantes para atornillar la placa del motor (cambio #1 y #3).
    """
    y_col = P.mesa_fondo / 2.0 - P.tubo / 2.0
    largo = P.brazo_largo
    # Arranca sobre la columna (y = y_col) y avanza hacia el eje de la olla.
    # Cara inferior apoyada en brazo_z, por eso el +tubo/2 en Z.
    brazo = (tubo_cuadrado(largo, eje="Y")
             .translate((0, y_col - largo, P.brazo_z + P.tubo / 2.0)))
    # Pasantes M12 para la placa del motor, sobre la cara superior del brazo.
    paso = P.placa_motor - 60.0
    brazo = (brazo.faces(">Z").workplane(centerOption="CenterOfBoundBox")
             .pushPoints([(0, -paso / 2.0), (0, paso / 2.0)])
             .hole(P.placa_perno))
    return brazo


def quemador_glp() -> cq.Workplane:
    """
    Quemador de anillo GLP EXISTENTE. No cambia la pieza: cambia su altura,
    porque ahora calienta el fondo de la CAMISA DE AGUA y no la olla.
    Ese solo cambio de posicion es lo que elimina la costra.
    """
    r_med = P.quemador_d / 2.0
    anillo_q = toro(r_med, P.quemador_tubo / 2.0)
    # Tubo de alimentacion hacia el lateral (manguera amarilla de GLP).
    alim = (cq.Workplane("YZ")
            .circle(P.quemador_tubo / 2.0)
            .extrude(r_med + 120.0))
    return anillo_q.union(alim).translate((0, 0, QUEMADOR_Z))


# =============================================================================
# 4. PIEZAS NUEVAS - CAMBIO #2 : ALTURA LIBRE BAJO LA MESA
# =============================================================================

def extension_patas() -> cq.Workplane:
    """
    CAMBIO #2 (pieza principal). Cuatro alargues de pata de +ext_patas mm con
    el MISMO tubo 40x40 del bastidor, unidos por placas atornilladas.

    POR QUE ABAJO Y NO ARRIBA. La olla cuelga de la mesa hacia abajo. Con la
    olla nueva de 640 mm hay que alojar bajo la mesa:

        olla 640 + fondo 2 + colchon de agua 25 + chapa 1.5 + luz de
        quemador 90  =  758.5 mm

    La mesa original esta a 720 mm: el quemador quedaria BAJO EL PISO. Por eso
    el alargue va en las patas. De paso la boca de carga sube a altura de codo,
    que es donde conviene cargar 15 kg de maicena.
    """
    t = P.tubo
    x = P.mesa_ancho / 2.0 - t / 2.0
    y = P.mesa_fondo / 2.0 - t / 2.0
    e = P.placa_esp
    lado = P.empalme_placa
    pcd = lado - 34.0

    partes = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            # Placa de piso (asiento y punto de nivelacion).
            partes.append(placa_con_pernos(lado, lado, e, pcd, pcd,
                                           P.placa_perno)
                          .translate((sx * x, sy * y, e / 2.0)))
            # Tramo de tubo del alargue.
            partes.append(tubo_cuadrado(P.ext_patas - 2.0 * e)
                          .translate((sx * x, sy * y, e)))
            # Placa de union con la pata original del bastidor.
            partes.append(placa_con_pernos(lado, lado, e, pcd, pcd,
                                           P.placa_perno)
                          .translate((sx * x, sy * y, P.ext_patas - e / 2.0)))

    res = partes[0]
    for p in partes[1:]:
        res = res.union(p)
    return res



def empalme_columna() -> cq.Workplane:
    """
    CAMBIO #2 (complemento). Alargue de columna con el MISMO perfil de tubo
    40x40, unido por dos placas atornilladas (4x M12). No aporta espacio para
    la olla (esa altura la dan las extensiones de pata): aporta la holgura
    vertical para montar y desmontar el conjunto eje + cubo del ancla sin
    tener que bajar el motorreductor. Union reversible, sin corte ni
    soldadura sobre el bastidor original.
    """
    y_col = P.mesa_fondo / 2.0 - P.tubo / 2.0
    z0 = P.mesa_z + P.columna_alt_orig
    e = P.placa_esp
    lado = P.empalme_placa
    pcd = lado - 34.0

    placa_inf = placa_con_pernos(lado, lado, e, pcd, pcd, P.placa_perno)
    placa_sup = placa_con_pernos(lado, lado, e, pcd, pcd, P.placa_perno)

    tramo = tubo_cuadrado(P.ext_columna)

    conj = (placa_inf.translate((0, 0, z0 + e / 2.0))
            .union(tramo.translate((0, 0, z0 + e)))
            .union(placa_sup.translate((0, 0, z0 + e + P.ext_columna + e / 2.0))))
    return conj.translate((0, y_col, 0))


# =============================================================================
# 5. PIEZAS NUEVAS - CAMBIO #1 : MOTORREDUCTOR SOBRE SOPORTE EXISTENTE
# =============================================================================

def placa_adaptadora_motor() -> cq.Workplane:
    """
    CAMBIO #1. Placa de acero de 12 mm que se atornilla al brazo EXISTENTE por
    abajo y recibe la brida del motorreductor por arriba. Es la pieza que
    permite montar un motor real sin tocar el bastidor.
    """
    e = P.placa_esp
    lado = P.placa_motor
    z = P.brazo_z + P.tubo

    # Placa base con los 4 pasantes hacia la brida del reductor.
    pl = cq.Workplane("XY").box(lado, lado, e)
    pl = (pl.faces(">Z").workplane()
          .polygon(4, P.brida_pcd * math.sqrt(2.0), forConstruction=True)
          .vertices().hole(P.brida_perno))
    # Los 2 pasantes que bajan al brazo (coinciden con brazo_superior()).
    paso = lado - 60.0
    pl = (pl.faces(">Z").workplane()
          .pushPoints([(0, -paso / 2.0), (0, paso / 2.0)])
          .hole(P.placa_perno))
    # Paso del eje.
    pl = pl.faces(">Z").workplane().hole(P.eje_d + 14.0)
    return pl.translate((0, 0, z + e / 2.0))


def soporte_rodamiento() -> cq.Workplane:
    """
    Alojamiento de rodamiento bajo la placa. El motorreductor no debe tomar la
    carga radial del ancla: el ancla trabaja excentrica contra masa espesa y
    flexiona el eje. Este soporte descarga esa reaccion en el bastidor.

    Se construye uniendo primero los macizos y taladrando despues. Taladrar al
    final evita caras coincidentes entre el agujero del cuerpo y el de la
    brida, que es lo que produce solidos no validos.
    """
    z_top = P.brazo_z + P.tubo          # cara inferior de la placa del motor
    h = P.soporte_rod_h
    z0 = z_top - h
    lado_brida = P.soporte_rod_d + 40.0
    esp_brida = 10.0

    cuerpo = (cq.Workplane("XY").circle(P.soporte_rod_d / 2.0)
              .extrude(h).translate((0, 0, z0)))
    brida = (cq.Workplane("XY").box(lado_brida, lado_brida, esp_brida)
             .translate((0, 0, z_top - esp_brida / 2.0)))
    conj = cuerpo.union(brida)

    # Taladro pasante del eje, con holgura para el rodamiento.
    paso_eje = (cq.Workplane("XY").circle((P.eje_d + 2.0) / 2.0)
                .extrude(h + 40.0).translate((0, 0, z0 - 20.0)))
    conj = conj.cut(paso_eje)

    # Cuatro pasantes M8 de sujecion a la placa del motor.
    pcd = P.soporte_rod_d + 20.0
    for sx in (-1, 1):
        for sy in (-1, 1):
            perno = (cq.Workplane("XY").circle(4.5)
                     .extrude(esp_brida + 20.0)
                     .translate((sx * pcd / 2.0, sy * pcd / 2.0,
                                 z_top - esp_brida - 10.0)))
            conj = conj.cut(perno)
    return conj


def motorreductor() -> cq.Workplane:
    """
    Envolvente del motorreductor 1 HP / 30 RPM (sinfin-corona 58:1).
    Reemplaza al motor Hubbell de placa HP .125 (1/8 HP) del prototipo actual.
    Modelado como envolvente: sirve para verificar interferencia y altura.
    """
    z0 = P.brazo_z + P.tubo + P.placa_esp

    brida = (cq.Workplane("XY").circle(P.brida_d / 2.0)
             .extrude(P.brida_esp).translate((0, 0, z0)))
    caja = (cq.Workplane("XY").box(P.red_ancho, P.red_fondo, P.red_alto)
            .translate((0, 0, z0 + P.brida_esp + P.red_alto / 2.0)))
    # Motor electrico acostado, saliendo hacia atras del reductor.
    motor = (cq.Workplane("XZ").circle(P.motor_d / 2.0).extrude(P.motor_l)
             .translate((0, P.red_fondo / 2.0,
                         z0 + P.brida_esp + P.red_alto * 0.6)))
    return brida.union(caja).union(motor)


# =============================================================================
# 6. PIEZAS NUEVAS - OLLA ANGOSTA + CAMISA DE AGUA
# =============================================================================

def olla_interior() -> cq.Workplane:
    """
    Olla de proceso, inox 304, angosta y alta (Ø200 x 640).
    La relacion angosta no es estetica: el calor entra solo por la pared
    lateral y el tiempo de cuaje del centro escala con R^2. Duplicar el radio
    cuadruplica el tiempo. Ver bloque de verificacion termica.
    """
    pared = anillo(P.olla_r_ext, P.olla_r_int, P.olla_h_int)
    fondo = (cq.Workplane("XY").circle(P.olla_r_ext)
             .extrude(P.olla_fondo_esp)
             .translate((0, 0, -P.olla_fondo_esp)))
    # Pestania de apoyo: la olla cuelga de la cuna por este reborde.
    pestania = anillo(P.olla_r_ext + 18.0, P.olla_r_ext, 4.0) \
        .translate((0, 0, P.olla_h_int - 4.0))
    return (pared.union(fondo).union(pestania)
            .translate((0, 0, OLLA_Z_FONDO_INT)))


def camisa_agua() -> cq.Workplane:
    """
    CAMISA DE AGUA (bano maria). Es la pieza que hace fisicamente imposible
    quemar la masa: el quemador calienta AGUA, no la olla. A presion
    atmosferica el agua no pasa de 100 C, y el vapor escapa por el venteo.
    La masa recibe como maximo ~85-90 C desde la pared, muy por debajo del
    umbral de costra (~120 C). Es una garantia fisica, no de control: aunque
    falle el termostato, el agua sigue sin poder pasar de 100 C.

    SISTEMA ABIERTO. El venteo superior NO lleva valvula ni tapon: si se
    cierra, deja de ser un bano maria y pasa a ser un recipiente a presion.
    """
    z0 = CAMISA_Z_FONDO
    alt = OLLA_Z_FONDO_EXT + P.camisa_altura - z0

    envolvente = anillo(P.camisa_r_ext, P.camisa_r_int, alt)
    fondo = (cq.Workplane("XY").circle(P.camisa_r_ext)
             .extrude(P.camisa_esp).translate((0, 0, -P.camisa_esp)))
    # Corona superior que cierra el anular contra la pared de la olla.
    corona = anillo(P.camisa_r_ext, P.olla_r_ext, P.camisa_esp) \
        .translate((0, 0, alt))

    conj = envolvente.union(fondo).union(corona).translate((0, 0, z0))

    # Venteo (obligatorio) y boca de llenado de agua.
    z_top = z0 + alt
    venteo = (cq.Workplane("XY").circle(P.venteo_d / 2.0)
              .extrude(P.venteo_largo)
              .translate((P.camisa_r_int + P.camisa_gap / 2.0 - 8.0, 0, z_top)))
    llenado = (cq.Workplane("XY").circle(P.llenado_d / 2.0)
               .extrude(P.venteo_largo * 0.7)
               .translate((-(P.camisa_r_int + P.camisa_gap / 2.0 - 8.0), 0,
                           z_top)))
    return conj.union(venteo).union(llenado)


def cuna_olla() -> cq.Workplane:
    """
    CAMBIO #3. Cuna atornillada: placa que centra la olla en el vano de la
    mesa y la sostiene por la pestania. Se saca con 4 tornillos M12 para
    extraer la olla completa y lavarla.
    """
    lado = P.mesa_ancho - 2.0 * P.tubo
    r_paso = P.camisa_r_ext + P.cuna_holgura
    pcd = lado - 50.0
    pl = cq.Workplane("XY").box(lado, lado, P.cuna_esp)
    pl = (pl.faces(">Z").workplane()
          .rect(pcd, pcd, forConstruction=True)
          .vertices().hole(P.placa_perno))
    pl = pl.faces(">Z").workplane().hole(2.0 * r_paso)
    return pl.translate((0, 0, P.mesa_z + P.cuna_esp / 2.0))


def apoyo_guia_eje() -> cq.Workplane:
    """
    Segundo apoyo del eje, en la boca de la olla.

    Sin el, el eje trabaja en voladizo puro desde el motor: 1.3 m de brazo de
    palanca contra masa espesa. Con el, el tramo motor-boca queda entre dos
    apoyos y solo vuela el tramo sumergido. Es lo que hace que la luz de
    1.5 mm del raspador se mantenga durante la mezcla.

    Puente de pletina atornillado a la cuna, con buje de PTFE en el centro.
    La carga va por el puente al bastidor, no al reductor.
    """
    r_ext = P.camisa_r_ext + P.cuna_holgura
    z_base = P.mesa_z + P.cuna_esp
    esp = 12.0
    ancho = 50.0
    alto_pie = 45.0
    z_barra = z_base + alto_pie

    # Pletina que cruza la boca de lado a lado.
    barra = (cq.Workplane("XY").box(2.0 * r_ext, ancho, esp)
             .translate((0, 0, z_barra + esp / 2.0)))
    # Dos pies que la apoyan en la cuna, fuera del paso de la olla.
    pies = []
    for sx in (-1, 1):
        pies.append(cq.Workplane("XY")
                    .box(40.0, ancho, alto_pie)
                    .translate((sx * (r_ext - 20.0), 0,
                                z_base + alto_pie / 2.0)))
    # Cubo del buje.
    cubo = (cq.Workplane("XY").circle((P.eje_d + 30.0) / 2.0)
            .extrude(esp + 26.0)
            .translate((0, 0, z_barra - 13.0)))

    conj = barra.union(pies[0]).union(pies[1]).union(cubo)
    # Taladro del buje, al final, para no dejar caras coincidentes.
    paso = (cq.Workplane("XY").circle((P.eje_d + 1.0) / 2.0)
            .extrude(esp + 80.0).translate((0, 0, z_barra - 40.0)))
    return conj.cut(paso)


def tapa_partida() -> cq.Workplane:
    """
    Tapa PARTIDA en dos medias lunas. Reduce perdida de calor y salpicadura, y
    da un punto fijo para el termometro de la masa.

    Va partida a proposito: el eje pasa por el centro y el cubo del ancla
    (Ø60) no cabe por el agujero de paso del eje (Ø42). Una tapa entera
    obligaria a desmontar el motorreductor para taparla. Partida, entra y sale
    con el eje montado.
    """
    r_ext = P.camisa_r_ext + P.cuna_holgura
    r_int = P.eje_d / 2.0 + 6.0
    gap = 3.0                      # junta entre las dos mitades
    z = P.mesa_z + P.cuna_esp + 6.0

    mitades = []
    for sy in (-1, 1):
        media = (anillo(r_ext, r_int, P.tapa_esp)
                 .cut(cq.Workplane("XY")
                      .box(2.2 * r_ext, 2.2 * r_ext, 3.0 * P.tapa_esp)
                      .translate((0, -sy * (1.1 * r_ext + gap / 2.0), 0))))
        mitades.append(media)

    tapa = mitades[0].union(mitades[1])

    # Boca de carga en una de las mitades.
    boca = (cq.Workplane("XY").circle(P.tapa_boca / 2.0)
            .extrude(3.0 * P.tapa_esp)
            .translate((P.olla_r_int * 0.55, r_ext * 0.45, -P.tapa_esp)))
    return tapa.cut(boca).translate((0, 0, z))


# =============================================================================
# 7. PIEZAS NUEVAS - EJE E IMPULSOR TIPO ANCLA
# =============================================================================

def _radio_ancla() -> float:
    """Radio exterior de la barra del ancla, dejando sitio al raspador."""
    return P.olla_r_int - P.rasp_gap - P.rasp_esp


def eje_vertical() -> cq.Workplane:
    """Eje inox macizo Ø30, del acople del reductor al cubo del ancla."""
    z_top = P.brazo_z + P.tubo + P.placa_esp + P.brida_esp
    z_bot = OLLA_Z_FONDO_INT + P.ancla_fondo_gap
    return (cq.Workplane("XY").circle(P.eje_d / 2.0)
            .extrude(z_top - z_bot).translate((0, 0, z_bot)))


def impulsor_ancla() -> cq.Workplane:
    """
    IMPULSOR TIPO ANCLA. Reemplaza al batidor globo de alambre del prototipo
    actual.

    El batidor globo falla por dos razones simultaneas: en masa espesa no
    desplaza volumen (la atraviesa cortando) y no toca la pared, asi que la
    capa pegada se sigue cocinando sin renovarse -> costra. El ancla hace las
    dos cosas que faltan: mueve TODO el volumen a baja velocidad y renueva la
    pelicula de pared en cada vuelta.
    """
    ra = _radio_ancla()
    w = P.ancla_barra_esp
    b = P.ancla_barra_ancho
    z_bot = OLLA_Z_FONDO_INT + P.ancla_fondo_gap
    z_top = z_bot + P.h_masa + 120.0     # sobrepasa el nivel de masa

    largo_vert = z_top - z_bot - b

    partes = []
    # Dos brazos verticales pegados al contorno.
    for sx in (-1, 1):
        partes.append(cq.Workplane("XY")
                      .box(w, b, largo_vert)
                      .translate((sx * (ra - w / 2.0), 0, z_bot + b + largo_vert / 2.0)))
    # Barra de fondo que barre el fondo de la olla.
    partes.append(cq.Workplane("XY")
                  .box(2.0 * ra, b, w)
                  .translate((0, 0, z_bot + w / 2.0)))
    # Cubo de acople al eje.
    partes.append(anillo(P.cubo_d / 2.0, P.eje_d / 2.0, P.cubo_h)
                  .translate((0, 0, z_top - P.cubo_h)))
    # Brazos horizontales cubo -> brazos verticales.
    partes.append(cq.Workplane("XY")
                  .box(2.0 * (ra - w / 2.0), b, w)
                  .translate((0, 0, z_top - w / 2.0)))
    # Travesano intermedio: rigidiza y arrastra el nucleo de la masa.
    partes.append(cq.Workplane("XY")
                  .box(2.0 * (ra - w), b * 0.8, w * 0.8)
                  .translate((0, 0, z_bot + P.h_masa * 0.45)))

    res = partes[0]
    for p in partes[1:]:
        res = res.union(p)
    return res


def raspadores_ptfe() -> cq.Workplane:
    """
    Raspadores de PTFE (teflon) con luz de 1.5 mm a la pared. Son la pieza de
    desgaste: se cambian, no se rectifica la olla. Hacen automatico lo que hoy
    se hace a mano con espatula.
    """
    ra = _radio_ancla()
    b = P.ancla_barra_ancho
    z_bot = OLLA_Z_FONDO_INT + P.ancla_fondo_gap
    z_top = z_bot + P.h_masa + 120.0
    largo_vert = z_top - z_bot - b

    partes = []
    for sx in (-1, 1):
        partes.append(cq.Workplane("XY")
                      .box(P.rasp_esp, b, largo_vert)
                      .translate((sx * (ra + P.rasp_esp / 2.0), 0,
                                  z_bot + b + largo_vert / 2.0)))
    # Raspador de fondo.
    partes.append(cq.Workplane("XY")
                  .box(2.0 * ra, b, P.rasp_esp)
                  .translate((0, 0, z_bot - P.rasp_esp / 2.0)))

    res = partes[0]
    for p in partes[1:]:
        res = res.union(p)
    return res


# =============================================================================
# 8. VERIFICACION DE INGENIERIA
# =============================================================================

def verificar() -> list[str]:
    """
    Calculos de comprobacion que acompanian a la geometria. La geometria sin
    numeros es decoracion; esto es lo que justifica cada cota.
    """
    L: list[str] = []
    ad = L.append

    ad("")
    ad("=" * 78)
    ad(" VERIFICACION DE INGENIERIA")
    ad("=" * 78)

    # --- 8.1 Capacidad ------------------------------------------------------
    llenado = 100.0 * P.h_masa / P.olla_h_int
    ad("")
    ad("[1] CAPACIDAD")
    ad(f"    Volumen util de la olla .......... {P.vol_olla_l:7.2f} L")
    ad(f"    Volumen del lote de {P.lote_kg:.0f} kg ........ {P.vol_masa_l:7.2f} L")
    ad(f"    Altura de masa en la olla ........ {P.h_masa:7.1f} mm")
    ad(f"    Grado de llenado ................. {llenado:7.1f} %")
    ad(f"    Resguardo libre sobre la masa .... {P.olla_h_int - P.h_masa:7.1f} mm")
    if llenado > 80.0:
        ad("    [ALERTA] Llenado alto: riesgo de derrame al agitar.")
    else:
        ad("    [OK] Resguardo suficiente para agitacion sin derrame.")

    # --- 8.2 Termica: por que angosta --------------------------------------
    alfa = P.k_masa / (P.rho_masa * P.cp_masa)          # m2/s
    R = P.olla_r_int / 1000.0
    t_cond = 0.4 * R * R / alfa                          # s, orden de magnitud
    R_ancha = P.olla_orig_d / 2000.0
    t_cond_ancha = 0.4 * R_ancha * R_ancha / alfa
    ad("")
    ad("[2] TERMICA - POR QUE OLLA ANGOSTA Y NO ANCHA")
    ad(f"    Difusividad termica alfa ......... {alfa:.3e} m2/s")
    ad(f"    Olla NUEVA  R = {R*1000:5.1f} mm  -> t_conduccion ~ {t_cond/60:7.1f} min")
    ad(f"    Olla ACTUAL R = {R_ancha*1000:5.1f} mm  -> t_conduccion ~ "
       f"{t_cond_ancha/60:7.1f} min")
    ad(f"    Relacion (R^2) ................... {t_cond_ancha/t_cond:7.2f} x")
    ad("    NOTA: estos son tiempos por CONDUCCION PURA, sin agitar. Son")
    ad("    horas, no minutos. Conclusion de disenio importante: el ancla no")
    ad("    es un accesorio de mezclado, ES el mecanismo de transferencia de")
    ad("    calor. Sin agitacion esta olla no cuaja el centro en ningun")
    ad("    tiempo util, por angosta que sea.")

    # --- 8.3 Termica: con agitacion ----------------------------------------
    area_lat = math.pi * (2.0 * P.olla_r_ext / 1000.0) * (P.h_masa / 1000.0)
    area_fondo = math.pi * (P.olla_r_ext / 1000.0) ** 2
    area = area_lat + area_fondo
    q_sens = P.lote_kg * P.cp_masa * (P.t_cuaje - P.t_inicial)     # J
    dt1 = P.t_camisa - P.t_inicial
    dt2 = P.t_camisa - P.t_cuaje
    lmtd = (dt1 - dt2) / math.log(dt1 / dt2)
    q_dot = P.u_pared * area * lmtd                                # W
    t_calent = q_sens / q_dot                                      # s
    ad("")
    ad("[3] TERMICA - CON AGITACION (regimen real de trabajo)")
    ad(f"    Area de intercambio mojada ....... {area:7.4f} m2")
    ad(f"    Salto medio logaritmico .......... {lmtd:7.1f} K")
    ad(f"    Calor a entregar al lote ......... {q_sens/1e6:7.3f} MJ")
    ad(f"    Potencia transferida a la masa ... {q_dot:7.0f} W")
    ad(f"    Tiempo de calentamiento .......... {t_calent/60:7.1f} min")
    ad("    (U estimado con ancla y raspadores; a recalibrar en campo)")

    # --- 8.4 Quemador -------------------------------------------------------
    q_quem_in = P.quemador_kbtu * 1000.0 * 0.293071      # W entrada
    q_quem_util = q_quem_in * P.rend_quemador            # W a la camisa
    ad("")
    ad("[4] QUEMADOR GLP")
    ad(f"    Potencia nominal de entrada ...... {q_quem_in:7.0f} W "
       f"({P.quemador_kbtu:.0f} kBTU/h)")
    ad(f"    Potencia util a la camisa ........ {q_quem_util:7.0f} W "
       f"(rend. {P.rend_quemador*100:.0f} %)")
    ad(f"    Potencia demandada por el proceso  {q_dot:7.0f} W")
    if q_quem_util < q_dot:
        falta = q_dot / P.rend_quemador / 1000.0 / 0.293071
        ad(f"    [ALERTA] El quemador queda corto. Se necesitan >= "
           f"{falta:.0f} kBTU/h")
        ad("    para sostener el ritmo de calentamiento calculado. Con el")
        ad("    quemador actual el lote igual cuaja, pero mas lento: la camisa")
        ad("    tarda mas en llegar y sostener los 90 C.")
    else:
        ad("    [OK] Margen de potencia suficiente.")

    # --- 8.5 Seguridad termica: por que no se quema -------------------------
    ad("")
    ad("[5] SEGURIDAD TERMICA - GARANTIA CONTRA COSTRA")
    ad(f"    Temperatura de camisa (consigna) . {P.t_camisa:7.1f} C")
    ad("    Tope fisico del agua abierta ..... 100.0 C")
    ad(f"    Umbral de costra ................. {P.t_costra:7.1f} C")
    ad(f"    Margen en el peor caso ........... {P.t_costra - 100.0:7.1f} K")
    ad("    El peor caso es termostato pegado en abierto: el agua hierve y")
    ad("    ventea, pero no sube de 100 C. La masa nunca ve 120 C. Esto es")
    ad("    lo que el fuego directo del prototipo actual no puede garantizar:")
    ad("    la chapa sobre la llama pasa de 300 C sin dificultad.")
    if P.t_cuaje >= P.t_camisa:
        ad("    [ALERTA CRITICA] T_cuaje >= T_camisa: con esta consigna la")
        ad("    masa NO cuaja nunca. Subir t_camisa (manteniendo margen")
        ad("    contra 120 C) o replantear el metodo de calentamiento.")

    # --- 8.6 Mecanica: torque ----------------------------------------------
    omega = 2.0 * math.pi * P.motor_rpm / 60.0           # rad/s
    p_nuevo = P.motor_hp * 745.7
    t_nuevo = p_nuevo / omega
    p_viejo = 0.125 * 745.7                              # placa Hubbell
    t_viejo = p_viejo / omega
    # Demanda estimada por energia especifica de mezclado en pasta viscosa.
    w_por_kg = 10.0                                      # [ESTIMADO] W/kg
    p_req = P.lote_kg * w_por_kg
    factor_pico = 3.0                                    # pico en el cuaje
    p_req_pico = p_req * factor_pico
    t_req_pico = p_req_pico / omega
    ad("")
    ad("[6] MECANICA - TORQUE EN EL EJE")
    ad(f"    Velocidad de trabajo ............. {P.motor_rpm:7.1f} RPM "
       f"({omega:.2f} rad/s)")
    ad(f"    Motor ACTUAL  0.125 HP ........... {t_viejo:7.1f} N.m disponibles")
    ad(f"    Motor NUEVO   {P.motor_hp:.2f} HP ............. {t_nuevo:7.1f} "
       f"N.m disponibles")
    ad(f"    Demanda estimada en el pico ...... {t_req_pico:7.1f} N.m")
    ad(f"    Factor de seguridad con motor nuevo {t_nuevo/t_req_pico:6.2f}")
    if t_viejo < t_req_pico:
        ad("    [CONFIRMADO] El motor de placa HP .125 no alcanza. Coincide")
        ad("    con la falla reportada de recalentamiento: el motor trabaja")
        ad("    frenado, y un motor frenado disipa en el bobinado.")
    ad("    (w/kg es ESTIMADO; la prueba de campo con dinamometro o llave")
    ad("     dinamometrica es la que cierra esta cifra)")

    # --- 8.7 Geometria de raspado ------------------------------------------
    ra = _radio_ancla()
    barrido = 2.0 * math.pi * (ra + P.rasp_esp) / 1000.0 * P.motor_rpm
    ad("")
    ad("[7] RASPADO DE PARED")
    ad(f"    Radio exterior del raspador ...... {ra + P.rasp_esp:7.2f} mm")
    ad(f"    Radio interior de la olla ........ {P.olla_r_int:7.2f} mm")
    ad(f"    Luz raspador-pared ............... {P.rasp_gap:7.2f} mm")
    ad(f"    Longitud de pared barrida ........ {barrido:7.2f} m/min")
    ad(f"    Renovacion de pelicula de pared .. cada {60.0/P.motor_rpm:.1f} s")

    # --- 8.7b Flexion del eje ----------------------------------------------
    # Es la comprobacion que fija el diametro del eje. Si el eje flexiona mas
    # que la luz del raspador, el raspador roza la pared de la olla: se come
    # el PTFE, raya el inox y sube el torque.
    E_inox = 193e9                                   # Pa
    r_ancla_m = _radio_ancla() / 1000.0
    f_total = t_req_pico / r_ancla_m                 # N, empuje tangencial
    # El ancla de 2 brazos opuestos genera un PAR: la fuerza radial NETA sale
    # de la asimetria de carga, no del par. Se toma un 25%.
    asimetria = 0.25                                 # [ESTIMADO]
    f_radial = asimetria * f_total
    z_apoyo = P.mesa_z + P.cuna_esp + 45.0           # buje de la guia
    z_centro_masa = OLLA_Z_FONDO_INT + P.h_masa / 2.0
    voladizo = (z_apoyo - z_centro_masa) / 1000.0    # m
    inercia = math.pi * (P.eje_d / 1000.0) ** 4 / 64.0
    flecha = f_radial * voladizo ** 3 / (3.0 * E_inox * inercia) * 1000.0

    # Y sin el apoyo guia: el voladizo arranca en el rodamiento superior.
    voladizo_sin = ((P.brazo_z + P.tubo) - z_centro_masa) / 1000.0
    flecha_sin = f_radial * voladizo_sin ** 3 / (3.0 * E_inox * inercia) * 1000.0

    ad("")
    ad("[8] FLEXION DEL EJE  (fija el diametro)")
    ad(f"    Empuje tangencial en el ancla .... {f_total:7.0f} N")
    ad(f"    Fuerza radial neta ({asimetria*100:.0f}% asimetria) {f_radial:7.0f} N")
    ad(f"    Diametro de eje adoptado ......... Ø{P.eje_d:.0f} mm")
    ad(f"    Voladizo CON apoyo guia .......... {voladizo*1000:7.0f} mm")
    ad(f"    Flecha CON apoyo guia ............ {flecha:7.2f} mm")
    ad(f"    Voladizo SIN apoyo guia .......... {voladizo_sin*1000:7.0f} mm")
    ad(f"    Flecha SIN apoyo guia ............ {flecha_sin:7.2f} mm")
    ad(f"    Luz disponible del raspador ...... {P.rasp_gap:7.2f} mm")
    if flecha >= P.rasp_gap:
        ad("    [ALERTA] El raspador roza la pared. Subir eje_d o acortar el")
        ad("    voladizo bajando el apoyo guia.")
    else:
        ad(f"    [OK] Margen {P.rasp_gap - flecha:.2f} mm. El raspador no roza.")
    if flecha_sin >= P.rasp_gap:
        ad("    [NOTA] Sin el apoyo guia de la boca el eje NO cumple. Esa")
        ad("    pieza no es un extra: es lo que sostiene la luz de 1.5 mm.")

    # --- 8.8 Interferencias -------------------------------------------------
    ad("")
    ad("[9] INTERFERENCIAS Y ALTURAS")
    alto_total = P.brazo_z + P.tubo + P.placa_esp + P.brida_esp + P.red_alto
    luz_libre = P.brazo_z - P.mesa_z
    ad(f"    Altura total de la maquina ....... {alto_total:7.0f} mm")
    ad(f"    Luz mesa -> brazo ................ {luz_libre:7.0f} mm")
    # Chequeo del cambio #2: cuanto alargue de pata hace falta realmente.
    # El criterio que manda es dejar el quemador a una altura de trabajo.
    quemador_z_min = 200.0            # [DISENIO] altura minima de servicio
    apilado = (P.olla_h_int + P.olla_fondo_esp + P.camisa_fondo_gap +
               P.camisa_esp + P.quemador_gap)
    ext_patas_min = quemador_z_min + apilado - P.mesa_altura
    ad(f"    Apilado bajo la mesa (olla+camisa+luz) {apilado:7.1f} mm")
    ad(f"    Alargue de pata MINIMO requerido . {ext_patas_min:7.1f} mm")
    ad(f"    Alargue de pata adoptado ......... {P.ext_patas:7.1f} mm")
    if P.ext_patas < ext_patas_min:
        ad(f"    [ALERTA] Faltan {ext_patas_min - P.ext_patas:.0f} mm de pata: "
           f"el quemador queda")
        ad("    por debajo de la altura de servicio. Subir ext_patas.")
    else:
        ad(f"    [OK] Margen de {P.ext_patas - ext_patas_min:.0f} mm sobre el "
           f"minimo.")
    ad(f"    Mesa original (medida) ........... {P.mesa_altura:7.0f} mm")
    ad(f"    Alargue de patas (cambio #2) ..... {P.ext_patas:7.0f} mm")
    ad(f"    Mesa resultante = boca de carga .. {P.mesa_z:7.0f} mm")
    ad(f"    Columna original ................. {P.columna_alt_orig:7.0f} mm")
    ad(f"    Alargue de columna (cambio #2) ... {P.ext_columna:7.0f} mm")
    ad(f"    Fondo de camisa sobre el piso .... {CAMISA_Z_FONDO:7.0f} mm")
    ad(f"    Quemador sobre el piso ........... {QUEMADOR_Z:7.0f} mm")
    if QUEMADOR_Z < 150.0:
        ad("    [ALERTA] Quemador demasiado bajo: dificulta encendido y")
        ad("    mantenimiento. Revisar mesa_altura o camisa_fondo_gap.")
    else:
        ad("    [OK] Quemador accesible para encendido y regulacion.")
    if alto_total > 2000.0:
        ad("    [ALERTA] Supera 2 m: revisar altura de techo del local.")
    else:
        ad("    [OK] Altura compatible con local de techo estandar.")

    # --- 8.9 Agua de camisa -------------------------------------------------
    r_i = P.camisa_r_int / 1000.0
    r_o = P.olla_r_ext / 1000.0
    h_j = (OLLA_Z_FONDO_EXT + P.camisa_altura - CAMISA_Z_FONDO) / 1000.0
    v_anular = math.pi * (r_i ** 2 - r_o ** 2) * h_j
    v_fondo = math.pi * r_i ** 2 * (P.camisa_fondo_gap / 1000.0)
    v_agua = (v_anular + v_fondo) * 1000.0
    ad("")
    ad("[10] CARGA DE AGUA DE LA CAMISA")
    ad(f"    Volumen anular ................... {v_anular*1000:7.2f} L")
    ad(f"    Colchon de fondo ................. {v_fondo*1000:7.2f} L")
    ad(f"    CARGA TOTAL DE AGUA .............. {v_agua:7.2f} L")
    ad("    Sistema ABIERTO: el venteo superior no lleva tapon ni valvula.")
    ad("    Reponer agua entre lotes; nunca operar la camisa en seco.")

    return L


# =============================================================================
# 9. ENSAMBLE Y EXPORTACION
# =============================================================================

def construir_ensamble() -> tuple[cq.Assembly, dict]:
    """Arma el ensamble completo y devuelve tambien el diccionario de piezas."""
    # Paleta RGBA explicita (0-1). No se usan nombres de color: el catalogo
    # de nombres de OCCT es limitado y varia entre versiones.
    GRIS_BASTIDOR = (0.35, 0.35, 0.38, 1.0)   # tubo negro existente
    NARANJA_FUEGO = (0.85, 0.45, 0.10, 1.0)   # quemador GLP
    AZUL_NUEVO    = (0.20, 0.45, 0.70, 1.0)   # pieza nueva de acero
    GRIS_COMPRA   = (0.45, 0.45, 0.45, 1.0)   # componente comercial
    INOX          = (0.72, 0.76, 0.82, 1.0)   # acero inoxidable 304
    AGUA          = (0.55, 0.78, 0.90, 0.55)  # camisa de agua (semitransp.)
    PTFE          = (0.95, 0.95, 0.92, 1.0)   # raspadores de teflon

    piezas = {
        # --- se conservan del prototipo actual ---
        "01_bastidor_existente":   (bastidor_existente(),     GRIS_BASTIDOR, "REUSO"),
        "02_brazo_superior":       (brazo_superior(),         GRIS_BASTIDOR, "REUSO"),
        "03_quemador_glp":         (quemador_glp(),           NARANJA_FUEGO, "REUSO"),
        # --- cambio #2: altura de columna ---
        "04_extension_patas":      (extension_patas(),        AZUL_NUEVO,    "NUEVA"),
        "05_apoyo_guia_eje":       (apoyo_guia_eje(),         AZUL_NUEVO,    "NUEVA"),
        # --- cambio #1: motorreductor sobre soporte existente ---
        "06_placa_motor":          (placa_adaptadora_motor(), AZUL_NUEVO,    "NUEVA"),
        "07_soporte_rodamiento":   (soporte_rodamiento(),     AZUL_NUEVO,    "NUEVA"),
        "08_motorreductor":        (motorreductor(),          GRIS_COMPRA,   "COMPRA"),
        # --- proceso: olla angosta + camisa de agua ---
        "09_olla_interior":        (olla_interior(),          INOX,          "NUEVA"),
        "10_camisa_agua":          (camisa_agua(),            AGUA,          "NUEVA"),
        "11_cuna_olla":            (cuna_olla(),              AZUL_NUEVO,    "NUEVA"),
        "12_tapa_partida":         (tapa_partida(),           INOX,          "NUEVA"),
        # --- agitacion: eje + ancla + raspadores ---
        "13_eje_vertical":         (eje_vertical(),           INOX,          "NUEVA"),
        "14_impulsor_ancla":       (impulsor_ancla(),         INOX,          "NUEVA"),
        "15_raspadores_ptfe":      (raspadores_ptfe(),        PTFE,          "NUEVA"),
    }

    # El empalme de columna solo se fabrica si ext_columna > 0. Con la mesa ya
    # subida no hace falta, y una pieza de longitud cero seria geometria
    # degenerada.
    if P.ext_columna > 0.0:
        piezas["05b_empalme_columna"] = (empalme_columna(), AZUL_NUEVO, "NUEVA")

    assy = cq.Assembly(name="mezcladora_cocedora_rediseno")
    for nombre, (shape, color, _) in piezas.items():
        assy.add(shape, name=nombre, color=cq.Color(*color))
    return assy, piezas


def validar_solidos(piezas: dict) -> list[str]:
    """Comprueba que cada pieza sea un solido valido y con volumen > 0."""
    L = ["", "=" * 78, " VALIDACION GEOMETRICA DE SOLIDOS", "=" * 78, ""]
    L.append(f"    {'PIEZA':<26}{'ORIGEN':<8}{'VOLUMEN cm3':>14}  {'VALIDO':>7}")
    L.append("    " + "-" * 60)
    todo_ok = True
    for nombre, (shape, _, origen) in piezas.items():
        try:
            solido = shape.val()
            vol = solido.Volume() / 1000.0
            valido = solido.isValid()
        except Exception as exc:                      # pragma: no cover
            L.append(f"    {nombre:<26}{origen:<8}{'ERROR':>14}  {str(exc)[:20]}")
            todo_ok = False
            continue
        if vol <= 0.0 or not valido:
            todo_ok = False
        L.append(f"    {nombre:<26}{origen:<8}{vol:>14.1f}  "
                 f"{'si' if valido else 'NO':>7}")
    L.append("")
    L.append(f"    RESULTADO: {'todos los solidos son validos' if todo_ok else 'HAY SOLIDOS INVALIDOS'}")
    return L


def exportar(assy: cq.Assembly, piezas: dict, destino: str = "output") -> list[str]:
    """Exporta ensamble y piezas a STEP y STL, y vistas a SVG."""
    L = ["", "=" * 78, " EXPORTACION", "=" * 78, ""]
    d_piezas = os.path.join(destino, "piezas")
    d_vistas = os.path.join(destino, "vistas")
    for d in (destino, d_piezas, d_vistas):
        os.makedirs(d, exist_ok=True)

    # Se limpian los STEP/STL de piezas de corridas anteriores. Si no, al
    # renumerar o renombrar una pieza quedan huerfanos en el directorio y el
    # taller termina fabricando una version vieja.
    borrados = 0
    vigentes = set(piezas.keys())
    for f in os.listdir(d_piezas):
        base, ext = os.path.splitext(f)
        if ext.lower() in (".step", ".stl") and base not in vigentes:
            os.remove(os.path.join(d_piezas, f))
            borrados += 1
    if borrados:
        L.append(f"    [LIMPIEZA] {borrados} archivos de piezas obsoletas "
                 f"eliminados")

    compuesto = assy.toCompound()

    # --- ensamble completo ---
    f_step = os.path.join(destino, "maquina_completa.step")
    assy.save(f_step)
    L.append(f"    [STEP] {f_step}")

    f_stl = os.path.join(destino, "maquina_completa.stl")
    exporters.export(compuesto, f_stl, tolerance=0.1, angularTolerance=0.2)
    L.append(f"    [STL ] {f_stl}")

    # --- piezas sueltas ---
    for nombre, (shape, _, _) in piezas.items():
        p_step = os.path.join(d_piezas, f"{nombre}.step")
        p_stl = os.path.join(d_piezas, f"{nombre}.stl")
        exporters.export(shape.val(), p_step)
        exporters.export(shape.val(), p_stl, tolerance=0.1, angularTolerance=0.2)
    L.append(f"    [STEP/STL] {len(piezas)} piezas sueltas en {d_piezas}/")

    # --- vistas ortogonales ---
    vistas = {
        "frontal":  (0.0, -1.0, 0.0),
        "lateral":  (1.0, 0.0, 0.0),
        "isometrica": (1.0, -1.0, 0.6),
    }
    for nombre, direccion in vistas.items():
        f_svg = os.path.join(d_vistas, f"{nombre}.svg")
        try:
            exporters.export(compuesto, f_svg,
                             opt={"width": 900, "height": 1100,
                                  "marginLeft": 30, "marginTop": 30,
                                  "projectionDir": direccion,
                                  "showAxes": False,
                                  "strokeWidth": 0.5})
            L.append(f"    [SVG ] {f_svg}")
        except Exception as exc:                      # pragma: no cover
            L.append(f"    [SVG ] {nombre}: omitida ({str(exc)[:40]})")

    # --- tamanios ---
    L.append("")
    for f in (f_step, f_stl):
        L.append(f"    {os.path.basename(f):<28}{os.path.getsize(f)/1024:>10.1f} kB")
    return L


# =============================================================================
# 9b. VISTA PREVIA RENDERIZADA
# =============================================================================

def _leer_stl_binario(ruta: str):
    """Lee un STL binario y devuelve un array (n, 3, 3) de triangulos."""
    import struct
    import numpy as np
    with open(ruta, "rb") as fh:
        fh.read(80)
        (n_tri,) = struct.unpack("<I", fh.read(4))
        datos = fh.read(n_tri * 50)
    tris = np.zeros((n_tri, 3, 3), dtype=float)
    for i in range(n_tri):
        base = i * 50 + 12          # se saltan los 3 float de la normal
        vals = struct.unpack("<9f", datos[base:base + 36])
        tris[i] = np.array(vals).reshape(3, 3)
    return tris


def vista_previa(piezas: dict, destino: str = "output") -> list[str]:
    """
    Render rapido del ensamble a PNG. No sustituye al STEP: sirve para mirar
    de un vistazo que las piezas nuevas quedan donde deben, sin abrir un CAD.
    """
    L = ["", "=" * 78, " VISTA PREVIA", "=" * 78, ""]
    try:
        import numpy as np
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    except Exception as exc:                          # pragma: no cover
        L.append(f"    Omitida: falta matplotlib/numpy ({exc})")
        return L

    d_piezas = os.path.join(destino, "piezas")
    d_vistas = os.path.join(destino, "vistas")
    os.makedirs(d_vistas, exist_ok=True)

    vistas = {"iso": (22, -58), "frontal": (12, -90), "lateral": (12, 0)}
    generadas = []

    for nombre_vista, (elev, azim) in vistas.items():
        fig = plt.figure(figsize=(7.5, 10.5), dpi=110)
        ax = fig.add_subplot(111, projection="3d")
        todos = []
        for nombre, (_, color, _) in piezas.items():
            ruta = os.path.join(d_piezas, f"{nombre}.stl")
            if not os.path.exists(ruta):
                continue
            tris = _leer_stl_binario(ruta)
            if len(tris) == 0:
                continue
            todos.append(tris.reshape(-1, 3))
            col = Poly3DCollection(tris, facecolor=color[:3],
                                   edgecolor=(0, 0, 0, 0.10), linewidths=0.15,
                                   alpha=color[3])
            ax.add_collection3d(col)

        pts = np.vstack(todos)
        centro = (pts.max(axis=0) + pts.min(axis=0)) / 2.0
        radio = (pts.max(axis=0) - pts.min(axis=0)).max() / 2.0
        for eje, c in zip("xyz", centro):
            getattr(ax, f"set_{eje}lim")(c - radio, c + radio)
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(elev=elev, azim=azim)
        ax.set_axis_off()
        ax.set_title(f"Redisenio evolutivo - vista {nombre_vista}\n"
                     f"gris = se conserva   |   azul = pieza nueva",
                     fontsize=9)
        f_png = os.path.join(d_vistas, f"preview_{nombre_vista}.png")
        fig.savefig(f_png, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        generadas.append(f_png)
        L.append(f"    [PNG ] {f_png}")

    return L


# =============================================================================
# 10. LISTA DE MATERIALES
# =============================================================================

def bom(piezas: dict) -> list[str]:
    """Separa lo que se reutiliza de lo que hay que fabricar o comprar."""
    L = ["", "=" * 78, " LISTA DE MATERIALES DEL REDISENIO", "=" * 78, ""]
    grupos: dict[str, list[str]] = {"REUSO": [], "NUEVA": [], "COMPRA": []}
    for nombre, (_, _, origen) in piezas.items():
        grupos[origen].append(nombre)

    titulos = {
        "REUSO":  "SE CONSERVA DEL PROTOTIPO ACTUAL (no se fabrica nada)",
        "NUEVA":  "A FABRICAR EN TALLER",
        "COMPRA": "A COMPRAR",
    }
    for clave in ("REUSO", "NUEVA", "COMPRA"):
        L.append(f"    {titulos[clave]}")
        for n in grupos[clave]:
            L.append(f"       - {n}")
        L.append("")

    L.append("    NOTA DE APROVECHAMIENTO:")
    L.append(f"       {len(grupos['REUSO'])} de {len(piezas)} conjuntos se")
    L.append("       reutilizan. El bastidor completo, el brazo y el quemador")
    L.append("       siguen siendo los mismos: el redisenio se atornilla")
    L.append("       encima. No hay corte ni soldadura sobre el equipo actual.")
    return L


# =============================================================================
# 11. PROGRAMA PRINCIPAL
# =============================================================================

def main() -> int:
    t0 = time.time()
    salida: list[str] = []
    ad = salida.append

    ad("=" * 78)
    ad(" REDISENIO EVOLUTIVO - MEZCLADORA-COCEDORA DE PORCELANA FRIA")
    ad(" Quito, Ecuador")
    ad("=" * 78)
    ad("")
    ad(" PUNTO DE PARTIDA (prototipo fisico existente, segun fotos):")
    ad("    - Bastidor portico de tubo cuadrado negro ........... SE CONSERVA")
    ad("      (sube en bloque sobre las extensiones de pata, sin cortes)")
    ad("    - Brazo superior en voladizo ........................ SE CONSERVA")
    ad("    - Quemador GLP de anillo ............................ SE CONSERVA")
    ad(f"    - Olla de pared simple Ø{P.olla_orig_d:.0f} x {P.olla_orig_h:.0f} "
       f"mm ............. SE REEMPLAZA")
    ad("    - Batidor globo de alambre .......................... SE REEMPLAZA")
    ad("    - Motor Hubbell, placa HP .125 (1/8 HP, 115 V) ...... SE REEMPLAZA")
    ad("")
    ad(" LOS TRES CAMBIOS DE ESTE REDISENIO:")
    ad(f"    #1 MOTOR   Placa adaptadora atornillada al brazo existente;")
    ad(f"               motorreductor {P.motor_hp:.0f} HP a {P.motor_rpm:.0f} RPM "
       f"(ratio {P.reductor_ratio:.0f}:1)")
    ad(f"               reemplaza al de 0.125 HP. Sin cortes en el bastidor.")
    ad(f"    #2 ALTURA  Empalmes atornillados de tubo {P.tubo:.0f}x{P.tubo:.0f}: "
       f"+{P.ext_patas:.0f} mm en las 4 patas.")
    ad(f"               La olla cuelga de la mesa, asi que la luz hace falta")
    ad(f"               BAJO la mesa, no arriba. Deja entrar la olla "
       f"Ø{P.olla_d_int:.0f} x {P.olla_h_int:.0f} mm")
    ad(f"               con camisa, y sube la boca de carga a "
       f"{P.mesa_z:.0f} mm (altura de codo).")
    ad(f"    #3 UNIONES Cuna de olla, placa de motor y empalme pasan a ser")
    ad(f"               uniones atornilladas de desmontaje rapido.")
    ad("")
    ad(" CAMBIOS DE FISICA QUE ACOMPANAN (sin ellos el redisenio no sirve):")
    ad(f"    + Camisa de agua de {P.camisa_gap:.0f} mm (bano maria) -> tope "
       f"fisico de 100 C")
    ad(f"    + Impulsor tipo ancla con raspadores PTFE -> reemplaza el batidor")

    ad("")
    ad("=" * 78)
    ad(" CONSTRUYENDO GEOMETRIA...")
    ad("=" * 78)
    assy, piezas = construir_ensamble()
    ad(f"    {len(piezas)} piezas construidas.")

    salida += validar_solidos(piezas)
    salida += verificar()
    salida += bom(piezas)
    salida += exportar(assy, piezas)
    salida += vista_previa(piezas)

    ad("")
    ad("=" * 78)
    ad(" PENDIENTE DE VALIDAR EN CAMPO (bloquea los planos definitivos)")
    ad("=" * 78)
    ad("    a) Temperatura real de cuaje de la masa. Todo el disenio de la")
    ad(f"       camisa asume que cuaja a {P.t_cuaje:.0f} C. Si necesita mas de")
    ad(f"       {P.t_camisa:.0f} C, la camisa a {P.t_camisa:.0f} C no cocina "
       f"nunca.")
    ad("    b) Torque real en el punto mas espeso. Define si 1 HP alcanza.")
    ad("    c) Cotas [FOTO] del bastidor con flexometro. Son las unicas que")
    ad("       pueden mover las interfaces atornilladas de este modelo.")
    ad("")
    ad(f" Tiempo de proceso: {time.time() - t0:.1f} s")
    ad("=" * 78)

    texto = "\n".join(salida)
    print(texto)

    os.makedirs("output", exist_ok=True)
    with open(os.path.join("output", "reporte_rediseno.txt"), "w",
              encoding="utf-8") as fh:
        fh.write(texto + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
