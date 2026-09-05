#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
 MODELO BLENDER - PROTOTIPO 2 PARA 30 kg   (rev. 2 - impulsor corregido)
 Mezcladora-cocedora de porcelana fria  ·  Quito, Ecuador
=============================================================================

QUE CAMBIO RESPECTO A LA rev. 1  (ver reports/mezclado.txt)

  1. IMPULSOR. Fuera el ancla con travesano. El criterio de arco de Jenike
     demostro que esta masa puentea cualquier abertura que quepa en la olla:
     el travesano se empaqueta y el conjunto gira como un tapon solido.
     Entra CINTA HELICOIDAL doble: helice abierta, sin travesanos, sin lazos
     cerrados, sin superficies horizontales. Bombea por desplazamiento
     positivo, como un tornillo.

  2. ESTRUCTURA. Fuera las torres grandes. El par de reaccion circula en
     lazo cerrado motor->eje->masa->olla->collar->motor. Se cierra ese lazo
     con un COLLAR DE PAR compacto que abraza la olla y sube en posts cortos
     al plato del motor. El bastidor existente vuelve a llevar SOLO PESO, y
     con peso va sobrado. La olla se apoya en la mesa, como en el proto real.

  3. TOPES ANTIGIRO. La olla se atornilla al collar con topes: sin ellos, con
     este par, la olla giraria con la masa. Obligatorio.

  4. BOCA DE CARGA DE SOLIDOS con tamiz: la maicena entra en frio, tamizada y
     bajo el nivel de liquido. A 30 rpm ningun impulsor deshace un grumo ya
     formado; solo cabe evitar que se forme.

UNIDADES: metros en Blender, milimetros en los parametros.

USO
---
    pip3 install bpy
    python3 cad/prototipo_2/blender_p2.py

Salidas en output_blender/
=============================================================================
"""

from __future__ import annotations

import math
import os
import sys

try:
    import bpy
    from mathutils import Vector
except ImportError:
    sys.exit("Falta bpy.  Instalar con:  pip3 install bpy")

MM = 0.001
RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SALIDA = os.path.join(RAIZ, "output_blender")


# =============================================================================
# PARAMETROS  (mm)
# =============================================================================

class P:
    # --- bastidor EXISTENTE  [SUPUESTO de foto, pendiente BAS-01..08] -------
    v_tubo = 40.0
    v_mesa_x = 450.0
    v_mesa_y = 450.0
    v_mesa_z = 720.0            # cara superior de la mesa = apoyo de la olla
    v_vano = 340.0             # abertura por la que el quemador ve la camisa
    v_travesano_z = 180.0

    # --- columna trasera reforzada  [DISENIO] -------------------------------
    # Se conserva el concepto de columna + brazo del proto real. Solo lleva
    # PESO del accionamiento (el par ya no pasa por aqui), asi que basta
    # subir un escalon de perfil: 50x50 en vez de 40x40.
    col_tubo = 50.0
    col_y = 225.0              # posicion trasera de la columna
    col_top = 1560.0          # cara superior del brazo del motor
    brazo_largo = 300.0

    # --- recipiente, angosto y alto  [DISENIO/CALCULADO] --------------------
    # D = 300 mm. Con la cinta haciendo circulacion axial forzada se relaja un
    # poco frente al ancla, pero se mantiene angosto por la termica.
    r_d_int = 300.0
    r_h_int = 650.0
    r_esp = 2.0
    r_gap_camisa = 20.0
    r_h_masa = 419.0          # lote de 30 kg de PRODUCTO (rev. carga pendiente)
    r_z_fondo = 726.0         # fondo interior; la olla se apoya en la mesa
    r_camisa_h = 470.0

    # --- cinta helicoidal  [DISENIO] ----------------------------------------
    eje_d = 45.0
    ci_vueltas = 1.6
    ci_ancho = 28.0           # ancho radial del fleje
    ci_esp = 6.0              # espesor del fleje
    ci_gap = 4.0              # luz fleje -> pared (antes del raspador)
    rasp_esp = 8.0
    rasp_gap = 1.5
    ci_z0_off = 12.0          # arranque sobre el fondo
    hub_d = 60.0
    brazo_ci = 16.0           # seccion de los brazos hub->fleje

    # --- collar de par  [DISENIO] -------------------------------------------
    collar_z = 1376.0         # abraza la olla cerca del borde
    collar_esp = 16.0
    collar_ext = 400.0
    post_n = 4
    post_sec = 40.0
    plato_z = 1500.0
    plato = 320.0
    plato_esp = 14.0

    # --- topes antigiro  [DISENIO] ------------------------------------------
    tope_n = 3
    tope_sec = 28.0

    # --- motorreductor  [SUPUESTO, 2.2 kW + NMRV110] ------------------------
    red_x = 230.0
    red_y = 210.0
    red_z = 235.0
    mot_d = 165.0
    mot_l = 320.0

    # --- boca de carga de solidos con tamiz  [DISENIO] ----------------------
    chute_d = 120.0
    chute_len = 260.0

    # --- quemador  [DISENIO, anillo industrial ~31 kBTU/h] ------------------
    q_d = 250.0
    q_tubo = 18.0

    @classmethod
    def calc(cls):
        cls.r_r_int = cls.r_d_int / 2
        cls.r_r_ext = cls.r_r_int + cls.r_esp
        cls.c_r_int = cls.r_r_ext + cls.r_gap_camisa
        cls.c_r_ext = cls.c_r_int + cls.r_esp
        cls.c_z_fondo = cls.r_z_fondo - cls.r_esp - 25.0 - cls.r_esp
        cls.q_z = cls.c_z_fondo - 80.0
        cls.rim_z = cls.r_z_fondo + cls.r_h_int
        cls.ci_z0 = cls.r_z_fondo + cls.ci_z0_off
        cls.ci_z1 = cls.r_z_fondo + cls.r_h_masa + 40.0
        cls.ci_r = cls.r_r_int - cls.ci_gap - cls.rasp_esp - cls.ci_ancho / 2
        cls.eje_z_top = cls.plato_z + cls.plato_esp + 30.0
        cls.eje_z_bot = cls.ci_z0


P.calc()


# =============================================================================
# MATERIALES
# =============================================================================

class M:
    pass


def material(nombre, color, metal=0.0, rug=0.5, alpha=1.0, emision=0.0):
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, alpha)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rug
    if "Alpha" in b.inputs:
        b.inputs["Alpha"].default_value = alpha
    if emision > 0 and "Emission Color" in b.inputs:
        b.inputs["Emission Color"].default_value = (*color, 1.0)
        b.inputs["Emission Strength"].default_value = emision
    return m


def crear_materiales():
    M.viejo = material("bastidor_existente", (0.045, 0.045, 0.05), 0.5, 0.60)
    M.nuevo = material("torque_frame", (0.09, 0.34, 0.62), 0.5, 0.35)
    M.inox = material("inox_304", (0.62, 0.65, 0.70), 1.0, 0.18)
    M.cinta = material("cinta_inox", (0.70, 0.73, 0.78), 1.0, 0.22)
    M.agua = material("agua_camisa", (0.05, 0.38, 0.72), 0.0, 0.65)
    M.masa = material("masa", (0.93, 0.71, 0.30), 0.0, 0.90)
    M.ptfe = material("ptfe", (0.95, 0.95, 0.93), 0.0, 0.35)
    M.motor = material("motorreductor", (0.28, 0.29, 0.30), 0.8, 0.45)
    M.fuego = material("quemador", (0.95, 0.42, 0.10), 0.3, 0.50, emision=2.0)
    M.piso = material("piso", (0.55, 0.53, 0.50), 0.0, 0.85)
    M.flujo = material("flecha_masa", (0.04, 0.45, 0.20), 0.0, 0.4, emision=0.9)
    M.calor = material("flecha_calor", (0.90, 0.15, 0.10), 0.0, 0.4, emision=0.9)


# =============================================================================
# UTILIDADES
# =============================================================================

def poner_mat(ob, mat):
    ob.data.materials.clear()
    ob.data.materials.append(mat)


def caja(nombre, sx, sy, sz, x, y, z, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x * MM, y * MM, z * MM))
    ob = bpy.context.object
    ob.name = nombre
    ob.scale = (sx * MM, sy * MM, sz * MM)
    bpy.ops.object.transform_apply(scale=True)
    poner_mat(ob, mat)
    return ob


def cilindro(nombre, r, h, x, y, z, mat, verts=64):
    bpy.ops.mesh.primitive_cylinder_add(radius=r * MM, depth=h * MM,
                                        vertices=verts,
                                        location=(x * MM, y * MM,
                                                  (z + h / 2) * MM))
    ob = bpy.context.object
    ob.name = nombre
    poner_mat(ob, mat)
    return ob


def tubo_v(nombre, lado, largo, x, y, z0, mat):
    """Tramo de tubo cuadrado hueco vertical, base en z0."""
    ext = caja(nombre, lado, lado, largo, x, y, z0 + largo / 2, mat)
    return ext


def toro(nombre, r_may, r_men, z, mat):
    bpy.ops.mesh.primitive_torus_add(major_radius=r_may * MM,
                                     minor_radius=r_men * MM,
                                     major_segments=48, minor_segments=16,
                                     location=(0, 0, z * MM))
    ob = bpy.context.object
    ob.name = nombre
    poner_mat(ob, mat)
    return ob


def booleano(objetivo, herramienta, op='DIFFERENCE'):
    md = objetivo.modifiers.new("bool", 'BOOLEAN')
    md.operation = op
    md.object = herramienta
    md.solver = 'EXACT'
    bpy.context.view_layer.objects.active = objetivo
    bpy.ops.object.modifier_apply(modifier=md.name)
    bpy.data.objects.remove(herramienta, do_unlink=True)
    return objetivo


def unir(objs, nombre):
    objs = [o for o in objs if o is not None]
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    ob = bpy.context.object
    ob.name = nombre
    return ob


def anillo(nombre, r_ext, r_int, h, z, mat, verts=64):
    ext = cilindro(nombre, r_ext, h, 0, 0, z, mat, verts)
    hueco = cilindro(nombre + "_h", r_int, h + 20, 0, 0, z - 10, mat, verts)
    return booleano(ext, hueco)


def sector_anular(nombre, r_ext, r_int, h, z, a0, a1, mat, n=48):
    vs, fs = [], []
    for i in range(n + 1):
        ang = math.radians(a0 + (a1 - a0) * i / n)
        ca, sa = math.cos(ang), math.sin(ang)
        for r, zz in ((r_ext, z), (r_int, z), (r_ext, z + h), (r_int, z + h)):
            vs.append((r * ca * MM, r * sa * MM, zz * MM))
    for i in range(n):
        b, b2 = 4 * i, 4 * i + 4
        fs += [(b, b2, b2 + 2, b + 2), (b + 1, b + 3, b2 + 3, b2 + 1),
               (b + 2, b2 + 2, b2 + 3, b + 3), (b, b + 1, b2 + 1, b2)]
    e = 4 * n
    fs += [(0, 2, 3, 1), (e, e + 1, e + 3, e + 2)]
    me = bpy.data.meshes.new(nombre)
    me.from_pydata(vs, [], fs)
    me.validate()
    me.update()
    ob = bpy.data.objects.new(nombre, me)
    bpy.context.collection.objects.link(ob)
    poner_mat(ob, mat)
    return ob


def helice(nombre, r_centro, ancho, esp, z0, z1, vueltas, fase, mat, n=180):
    """
    Fleje helicoidal solido. Se construye vertice a vertice: es la unica
    forma de tener una helice limpia, y ademas asi el fleje es una superficie
    ABIERTA sin lazos cerrados, que es justo lo que exige el criterio de arco.
    """
    vs, fs = [], []
    H = z1 - z0
    rin, rout = r_centro - ancho / 2, r_centro + ancho / 2
    for i in range(n + 1):
        f = i / n
        ang = fase + vueltas * 2 * math.pi * f
        z = z0 + H * f
        ca, sa = math.cos(ang), math.sin(ang)
        for r, dz in ((rin, -esp / 2), (rout, -esp / 2),
                      (rin, esp / 2), (rout, esp / 2)):
            vs.append((r * ca * MM, r * sa * MM, (z + dz) * MM))
    for i in range(n):
        b, b2 = 4 * i, 4 * i + 4
        fs += [(b, b + 1, b2 + 1, b2),          # cara inferior
               (b + 2, b2 + 2, b2 + 3, b + 3),  # cara superior
               (b + 1, b + 3, b2 + 3, b2 + 1),  # canto exterior
               (b, b2, b2 + 2, b + 2)]          # canto interior
    e = 4 * n
    fs += [(0, 1, 3, 2), (e, e + 2, e + 3, e + 1)]
    me = bpy.data.meshes.new(nombre)
    me.from_pydata(vs, [], fs)
    me.validate()
    me.update()
    ob = bpy.data.objects.new(nombre, me)
    bpy.context.collection.objects.link(ob)
    poner_mat(ob, mat)
    return ob


# =============================================================================
# PIEZAS
# =============================================================================

def piso():
    bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, -0.002))
    ob = bpy.context.object
    ob.name = "00_piso"
    poner_mat(ob, M.piso)
    return ob


def bastidor_existente():
    """SE CONSERVA. Ahora solo lleva PESO. La olla se apoya en la mesa y el
    quemador dispara por el vano, como en el proto real."""
    t = P.v_tubo
    x = P.v_mesa_x / 2 - t / 2
    y = P.v_mesa_y / 2 - t / 2
    h = P.v_mesa_z - t
    partes = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            partes.append(caja(f"p{sx}{sy}", t, t, h, sx * x, sy * y, h / 2,
                               M.viejo))
    for sy in (-1, 1):
        partes.append(caja(f"mx{sy}", P.v_mesa_x, t, t, 0, sy * y,
                           P.v_mesa_z - t / 2, M.viejo))
    for sx in (-1, 1):
        partes.append(caja(f"my{sx}", t, P.v_mesa_y - 2 * t, t, sx * x, 0,
                           P.v_mesa_z - t / 2, M.viejo))
    for sy in (-1, 1):
        partes.append(caja(f"tv{sy}", P.v_mesa_x, t, t, 0, sy * y,
                           P.v_travesano_z, M.viejo))
    # soporte del quemador bajo el vano
    for sx in (-1, 1):
        partes.append(caja(f"sq{sx}", t, P.v_mesa_y - 2 * t, t, sx * (P.v_vano / 2 + t),
                           0, P.q_z - 40, M.viejo))
    return unir(partes, "01_bastidor_EXISTENTE")


def columna_reforzada():
    """Columna trasera + brazo. Se conserva el concepto; sube un escalon de
    perfil (50x50) porque ahora solo carga el PESO del motor, no el par."""
    t = P.col_tubo
    col = tubo_v("col", t, P.col_top - P.v_mesa_z, 0, P.col_y,
                 P.v_mesa_z, M.nuevo)
    brazo = caja("brazo", t, P.col_y * 2 + t, t, 0, 0,
                 P.col_top - t / 2, M.nuevo)
    return unir([col, brazo], "02_columna_reforzada")


def collar_par():
    """
    COLLAR DE PAR. El corazon del rediseno estructural. Abraza la olla cerca
    del borde y sube en posts cortos al plato del motor. Cierra el lazo del
    par -motor->eje->masa->olla->collar->motor- en un recorrido corto y
    local, de modo que el par NUNCA sale a la estructura de peso.
    """
    partes = []
    # anillo que abraza la olla
    partes.append(anillo("collar", P.collar_ext / 2, P.c_r_ext + 3,
                         P.collar_esp, P.collar_z, M.nuevo))
    # plato del motor
    partes.append(caja("plato", P.plato, P.plato, P.plato_esp, 0, 0,
                       P.plato_z + P.plato_esp / 2, M.nuevo))
    # posts cortos collar -> plato (lo que reacciona el par)
    rp = (P.collar_ext / 2 - P.post_sec)
    for k in range(P.post_n):
        a = math.pi / 4 + k * math.pi / 2
        partes.append(caja(f"post{k}", P.post_sec, P.post_sec,
                           P.plato_z - (P.collar_z + P.collar_esp),
                           rp * math.cos(a), rp * math.sin(a),
                           (P.collar_z + P.collar_esp + P.plato_z) / 2,
                           M.nuevo))
    return unir(partes, "03_collar_de_par")


def topes_antigiro():
    """Topes que atornillan la olla al collar. Sin ellos la olla gira con la
    masa. Con este par, no son opcionales."""
    partes = []
    r = P.c_r_ext + 1.5
    for k in range(P.tope_n):
        a = k * 2 * math.pi / P.tope_n
        partes.append(caja(f"tope{k}", P.tope_sec, P.tope_sec, 55,
                           r * math.cos(a), r * math.sin(a),
                           P.collar_z + 27, M.nuevo))
    return unir(partes, "04_topes_antigiro")


def recipiente():
    olla = anillo("olla", P.r_r_ext, P.r_r_int, P.r_h_int, P.r_z_fondo, M.inox)
    fondo = cilindro("olla_f", P.r_r_ext, P.r_esp, 0, 0,
                     P.r_z_fondo - P.r_esp, M.inox)
    pest = anillo("olla_p", P.c_r_ext + 20, P.r_r_ext, 12,
                  P.rim_z - 12, M.inox)
    return unir([olla, fondo, pest], "05_olla_interior")


def camisa():
    h = P.r_camisa_h
    env = anillo("cam", P.c_r_ext, P.c_r_int, h, P.c_z_fondo, M.inox)
    fondo = cilindro("cam_f", P.c_r_ext, P.r_esp, 0, 0,
                     P.c_z_fondo - P.r_esp, M.inox)
    corona = anillo("cam_c", P.c_r_ext, P.r_r_ext, P.r_esp,
                    P.c_z_fondo + h, M.inox)
    vent = cilindro("vent", 9, 110, P.c_r_int + P.r_gap_camisa / 2 - 4, 0,
                    P.c_z_fondo + h, M.inox, 24)
    return unir([env, fondo, corona, vent], "06_camisa")


def fluido_camisa():
    h = P.r_camisa_h - 30
    ag = anillo("agua", P.c_r_int - 0.5, P.r_r_ext + 0.5, h, P.c_z_fondo,
                M.agua)
    base = cilindro("agua_b", P.c_r_int - 0.5, 25, 0, 0, P.c_z_fondo - 25,
                    M.agua)
    return unir([ag, base], "07_agua_camisa")


def masa():
    return cilindro("08_masa", P.r_r_int - 1, P.r_h_masa, 0, 0,
                    P.r_z_fondo, M.masa)


def eje():
    largo = P.eje_z_top - P.eje_z_bot
    return cilindro("09_eje", P.eje_d / 2, largo, 0, 0, P.eje_z_bot,
                    M.cinta, 32)


def cinta_helicoidal():
    """
    CINTA HELICOIDAL DOBLE. Reemplaza al ancla con travesano.

    Dos flejes opuestos, sin ningun travesano ni lazo cerrado: es la
    condicion que impone el criterio de arco. Unidos al cubo solo por brazos
    radiales arriba y abajo -brazos, no barras que crucen el volumen-. La
    helice bombea masa por la pared hacia arriba y la deja caer por el centro:
    desplazamiento positivo, no conveccion. No hay volumen que pueda quedarse
    quieto ni cavidad donde la masa haga arco.
    """
    partes = []
    for fase in (0.0, math.pi):
        partes.append(helice(f"fleje{fase:.0f}", P.ci_r, P.ci_ancho, P.ci_esp,
                             P.ci_z0, P.ci_z1, P.ci_vueltas, fase, M.cinta))
    # cubo
    partes.append(anillo("hub", P.hub_d / 2, P.eje_d / 2, 70,
                        P.ci_z1 - 70, M.cinta, 32))
    # brazos radiales cubo -> fleje, solo en los extremos
    for fase, z in ((0.0, P.ci_z1 - 20), (math.pi, P.ci_z1 - 20),
                    (0.0, P.ci_z0 + 10), (math.pi, P.ci_z0 + 10)):
        ca, sa = math.cos(fase), math.sin(fase)
        largo = P.ci_r
        bpy.ops.mesh.primitive_cube_add(size=1)
        b = bpy.context.object
        b.scale = (largo * MM, P.brazo_ci * MM, P.brazo_ci * MM)
        bpy.ops.object.transform_apply(scale=True)
        b.location = (largo / 2 * ca * MM, largo / 2 * sa * MM, z * MM)
        b.rotation_euler = (0, 0, fase)
        poner_mat(b, M.cinta)
        partes.append(b)
    return unir(partes, "10_cinta_helicoidal")


def raspadores():
    """Raspadores de PTFE: flejes helicoidales finos a 1.5 mm de la pared,
    siguiendo la misma helice que la cinta."""
    r = P.r_r_int - P.rasp_gap - P.rasp_esp / 2
    partes = []
    for fase in (0.0, math.pi):
        partes.append(helice(f"rasp{fase:.0f}", r, P.rasp_esp, P.rasp_esp,
                             P.ci_z0, P.ci_z1, P.ci_vueltas, fase, M.ptfe))
    return unir(partes, "11_raspadores_PTFE")


def motorreductor():
    z0 = P.plato_z + P.plato_esp
    red = caja("red", P.red_x, P.red_y, P.red_z, 0, 0, z0 + P.red_z / 2,
               M.motor)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=P.mot_d / 2 * MM, depth=P.mot_l * MM, vertices=32,
        rotation=(math.pi / 2, 0, 0),
        location=(0, (P.red_y / 2 + P.mot_l / 2) * MM,
                  (z0 + P.red_z * 0.6) * MM))
    mot = bpy.context.object
    poner_mat(mot, M.motor)
    return unir([red, mot], "12_motorreductor")


def boca_carga():
    """
    BOCA DE CARGA DE SOLIDOS con tamiz. La maicena entra por aqui, EN FRIO y
    tamizada, cayendo BAJO el nivel de liquido. Es la pieza que evita los
    grumos, que a 30 rpm ningun impulsor podria luego deshacer.
    """
    x = P.r_r_int * 0.5
    ztop = P.rim_z + 40
    tubo = cilindro("chute", P.chute_d / 2, P.chute_len, x, 0, ztop - 40,
                    M.nuevo, 24)
    tubo.rotation_euler = (math.radians(18), 0, 0)
    # rejilla del tamiz (disco fino)
    tamiz = cilindro("tamiz", P.chute_d / 2 - 2, 3, x, 0, ztop + 8, M.inox, 24)
    return unir([tubo, tamiz], "13_boca_carga")


def quemador():
    an = toro("q_an", P.q_d / 2, P.q_tubo / 2, P.q_z, M.fuego)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=P.q_tubo / 2 * MM, depth=320 * MM, vertices=16,
        rotation=(0, math.pi / 2, 0),
        location=(-(P.q_d / 2 + 160) * MM, 0, P.q_z * MM))
    al = bpy.context.object
    poner_mat(al, M.fuego)
    return unir([an, al], "14_quemador")


# =============================================================================
# SECCION Y FLECHAS
# =============================================================================

def proceso_en_seccion():
    a0, a1 = 0.0, 180.0
    pz = []
    pz.append(sector_anular("s_olla", P.r_r_ext, P.r_r_int, P.r_h_int,
                            P.r_z_fondo, a0, a1, M.inox))
    pz.append(sector_anular("s_olla_f", P.r_r_ext, 1.0, P.r_esp,
                            P.r_z_fondo - P.r_esp, a0, a1, M.inox))
    pz.append(sector_anular("s_cam", P.c_r_ext, P.c_r_int, P.r_camisa_h,
                            P.c_z_fondo, a0, a1, M.inox))
    pz.append(sector_anular("s_cam_f", P.c_r_ext, 1.0, P.r_esp,
                            P.c_z_fondo - P.r_esp, a0, a1, M.inox))
    pz.append(sector_anular("s_agua", P.c_r_int - 0.5, P.r_r_ext + 0.5,
                            P.r_camisa_h - 30, P.c_z_fondo, a0, a1, M.agua))
    pz.append(sector_anular("s_agua_f", P.c_r_int - 0.5, 1.0, 25.0,
                            P.c_z_fondo - 25, a0, a1, M.agua))
    pz.append(sector_anular("s_masa", P.r_r_int - 1, 1.0, P.r_h_masa,
                            P.r_z_fondo, a0, a1, M.masa))
    return pz


def flechas():
    out = []

    def flecha(x, y, z, dz, mat, r=9.0, nombre="f"):
        cuerpo = cilindro(nombre, r, abs(dz), x, y, z if dz > 0 else z + dz,
                          mat, 16)
        bpy.ops.mesh.primitive_cone_add(
            radius1=r * 2.2 * MM, depth=34 * MM, vertices=16,
            rotation=(0 if dz > 0 else math.pi, 0, 0),
            location=(x * MM, y * MM, ((z + dz) if dz > 0 else z) * MM))
        pt = bpy.context.object
        poner_mat(pt, mat)
        return unir([cuerpo, pt], nombre)

    yf = -45.0
    # la cinta sube masa por la pared...
    out.append(flecha(P.r_r_int * 0.72, yf, P.r_z_fondo + 40, 330,
                      M.flujo, nombre="fm1"))
    # ...y la deja caer por el centro
    out.append(flecha(P.r_r_int * 0.16, yf, P.r_z_fondo + 400, -330,
                      M.flujo, nombre="fm2"))
    # calor del quemador al agua
    out.append(flecha(P.c_r_int - 6, yf, P.c_z_fondo - 95, 175,
                      M.calor, r=8, nombre="fc1"))
    for i, zz in enumerate((0.30, 0.62)):
        z = P.r_z_fondo + P.r_h_masa * zz
        c = cilindro(f"fcr{i}", 7, 46, 0, 0, 0, M.calor, 12)
        c.rotation_euler = (0, math.pi / 2, 0)
        c.location = ((P.r_r_int + 24) * MM, yf * MM, z * MM)
        out.append(c)
    return unir(out, "15_flechas")


# =============================================================================
# ESCENA
# =============================================================================

def limpiar():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def luces_y_mundo():
    w = bpy.data.worlds.new("W")
    bpy.context.scene.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.92, 0.93, 0.95, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.7
    bpy.ops.object.light_add(type='AREA', location=(2.2, -2.6, 3.6))
    k = bpy.context.object
    k.data.energy = 1100
    k.data.size = 3.0
    k.rotation_euler = (0.7, 0, 0.75)
    bpy.ops.object.light_add(type='AREA', location=(-2.6, -1.4, 2.4))
    f = bpy.context.object
    f.data.energy = 380
    f.data.size = 3.5
    f.rotation_euler = (1.15, 0, -1.05)
    bpy.ops.object.light_add(type='SUN', location=(0, 3, 5))
    s = bpy.context.object
    s.data.energy = 1.6
    s.rotation_euler = (-0.5, 0.3, 0)


def camara(loc, mira, lente=50, orto=None):
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.object
    cam.data.lens = lente
    if orto is not None:
        cam.data.type = 'ORTHO'
        cam.data.ortho_scale = orto
    d = Vector(mira) - Vector(loc)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam


def render(nombre, res=(1100, 1400), muestras=48):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = muestras
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = res
    os.makedirs(SALIDA, exist_ok=True)
    sc.render.filepath = os.path.join(SALIDA, nombre)
    bpy.ops.render.render(write_still=True)
    print(f"  render -> {nombre}.png")


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print(" MODELO BLENDER - PROTOTIPO 2 (rev.2, cinta helicoidal)")
    print("=" * 70)
    limpiar()
    crear_materiales()
    os.makedirs(SALIDA, exist_ok=True)

    print(" construyendo geometria...")
    piso()
    o_viejo = bastidor_existente()
    columna_reforzada()
    collar_par()
    topes_antigiro()
    o_olla = recipiente()
    o_cam = camisa()
    o_agua = fluido_camisa()
    o_masa = masa()
    o_eje = eje()
    o_cinta = cinta_helicoidal()
    o_rasp = raspadores()
    motorreductor()
    boca_carga()
    quemador()
    print(f"  {len(bpy.data.objects)} objetos")

    luces_y_mundo()
    bpy.ops.wm.save_as_mainfile(
        filepath=os.path.join(SALIDA, "prototipo_2_30kg.blend"))
    try:
        bpy.ops.export_scene.gltf(
            filepath=os.path.join(SALIDA, "prototipo_2_30kg.glb"),
            export_format='GLB')
        print("  exportado GLB")
    except Exception as e:
        print(f"  GLB omitido: {e}")

    print(" render 1/4  conjunto...")
    camara((2.6, -3.0, 1.9), (0, 0, 0.95), lente=45)
    render("01_conjunto", res=(1100, 1400))

    print(" render 2/4  alzado...")
    camara((0, -6.0, 1.0), (0, 0, 1.0), orto=2.3)
    render("02_alzado", res=(1000, 1400))

    print(" render 3/4  detalle collar de par...")
    camara((1.5, -1.9, 1.45), (0, 0, 1.32), lente=52)
    render("03_collar_par", res=(1300, 1050))

    print(" render 4/4  seccion de proceso...")
    for ob in (o_olla, o_cam, o_agua, o_masa):
        bpy.data.objects.remove(ob, do_unlink=True)
    if o_viejo:
        bpy.data.objects.remove(o_viejo, do_unlink=True)
    proceso_en_seccion()
    flechas()
    camara((0, -6.0, 0.78), (0, 0, 0.78), orto=0.98)
    render("04_seccion_proceso", res=(1050, 1450), muestras=64)

    bpy.ops.wm.save_as_mainfile(
        filepath=os.path.join(SALIDA, "prototipo_2_corte.blend"))
    print("=" * 70)
    print(f" Listo. Salidas en {os.path.relpath(SALIDA, RAIZ)}/")
    print("=" * 70)


if __name__ == "__main__":
    main()
