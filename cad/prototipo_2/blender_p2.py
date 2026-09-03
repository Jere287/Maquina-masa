#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
 MODELO BLENDER - PROTOTIPO 2 PARA 30 kg
 Mezcladora-cocedora de porcelana fria  ·  Quito, Ecuador
=============================================================================

QUE MUESTRA
-----------
Modelo conceptual del P2 y de COMO SE ACOPLA con el bastidor existente.
La arquitectura sale de calculations/sizing_30kg.py, no al reves.

ARQUITECTURA:  "torre nueva sobre base existente"

  El hallazgo que la justifica: a 30 kg hay DOS caminos de carga muy
  distintos, y meterlos por la misma estructura es lo que rompe el bastidor.

    CAMINO A  recipiente lleno, ~70 kg, carga estatica y vertical
    CAMINO B  motorreductor 65 kg MAS 548 N.m de par de reaccion,
              que es torsion pulsante, no peso

  El bastidor actual lleva bien A y no lleva B ni de lejos. Asi que se
  separan: el bastidor viejo se queda con lo que ya sabe hacer (sostener
  el quemador y dar arriostramiento lateral) y una torre nueva de tubo
  75x75x4 se lleva el recipiente y el accionamiento directamente al piso.

  El recipiente ATRAVIESA el vano del bastidor viejo. Por eso BAS-06 (el
  lado del vano) es la medida que decide si este acople es posible.

UNIDADES: metros en Blender, milimetros en los parametros.

USO
---
    pip3 install bpy
    python3 cad/prototipo_2/blender_p2.py

Salidas en output_blender/: renders PNG, escena .blend y malla .glb
=============================================================================
"""

from __future__ import annotations

import math
import os
import sys

try:
    import bpy
    import bmesh
    from mathutils import Vector
except ImportError:
    sys.exit("Falta bpy.  Instalar con:  pip3 install bpy")

MM = 0.001
RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SALIDA = os.path.join(RAIZ, "output_blender")


# =============================================================================
# PARAMETROS   (mm)
# =============================================================================

class P:
    # --- bastidor EXISTENTE  [SUPUESTO de foto, pendiente BAS-01..BAS-08] ---
    v_tubo = 40.0
    v_mesa_x = 450.0
    v_mesa_y = 450.0
    v_mesa_z = 720.0
    v_vano = 300.0          # lado del vano  [SUPUESTO] <- BAS-06 lo confirma
    v_travesano_z = 180.0
    v_columna_h = 620.0     # columna que se conserva como soporte de panel

    # --- torre NUEVA  [DISENIO, del bloque 6 de sizing_30kg.py] -------------
    n_tubo = 75.0           # patas 75x75x4 -> 2553 N.m adm, frente a 548
    # Travesanos en 60x60x3 (1238 N.m adm, sigue holgado). No es solo peso:
    # si los horizontales fueran del mismo lado que las patas, sus caras
    # quedarian COINCIDENTES con las de la pata y el render sale con parches
    # negros por z-fighting. Seccion distinta = caras distintas.
    n_tubo_h = 60.0
    n_pata_x = 330.0        # separacion de patas en X (fuera del bastidor)
    n_pata_y = 330.0        # separacion en Y
    n_altura = 1750.0       # cara superior de las patas
    n_viga = 75.0
    n_placa_base = 220.0
    n_placa_esp = 12.0

    # --- recipiente  [CALCULADO en sizing_30kg.py] --------------------------
    r_d_int = 280.0
    r_h_int = 652.0
    r_esp = 2.0
    r_gap_camisa = 20.0
    r_h_masa = 424.0        # altura del lote de 30 kg
    r_cradle_z = 1006.0     # cota del aro de cuna = boca de carga
    # La camisa debe cubrir TODO el nivel de masa mas un margen. Si se queda
    # corta, la franja superior del lote no recibe calor por la pared y es
    # justo donde se queda cruda.
    r_camisa_h = 490.0      # altura mojada de la camisa

    # --- agitador y eje  [DISENIO] ------------------------------------------
    eje_d = 50.0            # Ø50: flecha 0.49 mm < luz de raspador 1.5 mm
    ancla_barra = 30.0
    ancla_esp = 14.0
    rasp_esp = 10.0
    rasp_gap = 1.5
    ancla_fondo = 8.0
    cubo_d = 95.0

    # --- motorreductor  [SUPUESTO, envolvente NMRV110 + 2.2 kW] -------------
    red_x = 230.0
    red_y = 210.0
    red_z = 240.0
    mot_d = 165.0
    mot_l = 330.0

    # --- quemador  [DISENIO, 31 kBTU/h de anillo industrial] ----------------
    q_d = 240.0
    q_tubo = 18.0
    q_z = 230.0

    # --- derivados -----------------------------------------------------------
    @classmethod
    def calc(cls):
        cls.r_r_int = cls.r_d_int / 2
        cls.r_r_ext = cls.r_r_int + cls.r_esp
        cls.c_r_int = cls.r_r_ext + cls.r_gap_camisa
        cls.c_r_ext = cls.c_r_int + cls.r_esp
        cls.r_z_fondo = cls.r_cradle_z - cls.r_h_int      # fondo interior
        cls.c_z_fondo = cls.r_z_fondo - 30.0 - cls.r_esp  # fondo de camisa
        cls.eje_z_top = cls.n_altura + cls.n_viga + cls.n_placa_esp + 40
        cls.eje_z_bot = cls.r_z_fondo + cls.ancla_fondo


P.calc()


def comprobar_vano() -> dict:
    """
    El recipiente ATRAVIESA el vano del bastidor viejo. Si no pasa, este
    esquema de acople no funciona. Es la comprobacion que decide todo.
    """
    d_ext = 2 * P.c_r_ext
    holgura = 12.0                      # luz de montaje por lado
    necesario = d_ext + 2 * holgura
    pasa = P.v_vano >= necesario
    return {"d_ext": d_ext, "necesario": necesario,
            "vano_supuesto": P.v_vano, "pasa": pasa}


# =============================================================================
# UTILIDADES
# =============================================================================

def limpiar():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def material(nombre, color, metal=0.0, rug=0.5, alpha=1.0, emision=0.0):
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, alpha)
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["Roughness"].default_value = rug
    if "Alpha" in bsdf.inputs:
        bsdf.inputs["Alpha"].default_value = alpha
    if emision > 0 and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emision
    if alpha < 1.0:
        m.blend_method = 'BLEND' if hasattr(m, "blend_method") else m.blend_method
    return m


def poner_mat(ob, mat):
    ob.data.materials.clear()
    ob.data.materials.append(mat)


def caja(nombre, sx, sy, sz, x, y, z, mat):
    """Prisma recto. sx,sy,sz son dimensiones completas en mm."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x * MM, y * MM, z * MM))
    ob = bpy.context.object
    ob.name = nombre
    ob.scale = (sx * MM, sy * MM, sz * MM)
    bpy.ops.object.transform_apply(scale=True)
    poner_mat(ob, mat)
    return ob


def cilindro(nombre, r, h, x, y, z, mat, verts=64):
    """Cilindro con la BASE en z (no centrado)."""
    bpy.ops.mesh.primitive_cylinder_add(radius=r * MM, depth=h * MM,
                                        vertices=verts,
                                        location=(x * MM, y * MM,
                                                  (z + h / 2) * MM))
    ob = bpy.context.object
    ob.name = nombre
    poner_mat(ob, mat)
    return ob


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
    m = objetivo.modifiers.new("bool", 'BOOLEAN')
    m.operation = op
    m.object = herramienta
    m.solver = 'EXACT'
    bpy.context.view_layer.objects.active = objetivo
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(herramienta, do_unlink=True)
    return objetivo


def unir(objs, nombre):
    """Une una lista de objetos en uno solo."""
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    ob = bpy.context.object
    ob.name = nombre
    return ob


def sector_anular(nombre, r_ext, r_int, h, z, a0, a1, mat, n=48):
    """
    Sector anular solido, construido vertice a vertice.

    Para la vista en corte NO se usa booleano: un booleano sobre mallas que
    ya vienen de otros booleanos degenera y llega a borrar la pieza entera
    (paso con la camisa y con el agua). Una seccion se construye como
    seccion, y ademas asi las caras de corte quedan planas y limpias.

    a0 y a1 en grados. Se conserva el semiespacio y > 0, que es el que la
    camara ve por dentro cuando mira desde -Y.
    """
    vs, fs = [], []
    for i in range(n + 1):
        ang = math.radians(a0 + (a1 - a0) * i / n)
        ca, sa = math.cos(ang), math.sin(ang)
        for r, zz in ((r_ext, z), (r_int, z), (r_ext, z + h), (r_int, z + h)):
            vs.append((r * ca * MM, r * sa * MM, zz * MM))
    for i in range(n):
        ob, ib, ot, it = 4 * i, 4 * i + 1, 4 * i + 2, 4 * i + 3
        ob2, ib2, ot2, it2 = ob + 4, ib + 4, ot + 4, it + 4
        fs.append((ob, ob2, ot2, ot))        # cara exterior
        fs.append((ib, it, it2, ib2))        # cara interior
        fs.append((ot, ot2, it2, it))        # tapa superior
        fs.append((ob, ib, ib2, ob2))        # tapa inferior
    ult = 4 * n
    fs.append((0, 2, 3, 1))                                  # cara de corte a0
    fs.append((ult, ult + 1, ult + 3, ult + 2))              # cara de corte a1

    me = bpy.data.meshes.new(nombre)
    me.from_pydata(vs, [], fs)
    me.validate()
    me.update()
    ob = bpy.data.objects.new(nombre, me)
    bpy.context.collection.objects.link(ob)
    poner_mat(ob, mat)
    return ob


def anillo(nombre, r_ext, r_int, h, z, mat, verts=64):
    """Cilindro hueco: se hace por diferencia para que quede solido real."""
    ext = cilindro(nombre, r_ext, h, 0, 0, z, mat, verts)
    hueco = cilindro(nombre + "_h", r_int, h + 20, 0, 0, z - 10,
                     mat, verts)
    return booleano(ext, hueco)


# =============================================================================
# MATERIALES
# =============================================================================

class M:
    pass


def crear_materiales():
    # Contraste alto y deliberado: de un vistazo hay que distinguir lo que
    # se conserva de lo que se fabrica. En seccion, los fluidos van OPACOS:
    # una seccion tecnica con transparencias no se lee.
    M.viejo = material("bastidor_existente", (0.045, 0.045, 0.05), 0.5, 0.60)
    M.nuevo = material("torre_nueva", (0.09, 0.34, 0.62), 0.5, 0.35)
    M.inox = material("inox_304", (0.62, 0.65, 0.70), 1.0, 0.18)
    M.agua = material("agua_camisa", (0.05, 0.38, 0.72), 0.0, 0.65)
    M.masa = material("masa", (0.93, 0.71, 0.30), 0.0, 0.90)
    M.ptfe = material("ptfe", (0.95, 0.95, 0.93), 0.0, 0.35)
    M.motor = material("motorreductor", (0.28, 0.29, 0.30), 0.8, 0.45)
    M.fuego = material("quemador", (0.95, 0.42, 0.10), 0.3, 0.50, emision=2.0)
    M.piso = material("piso", (0.55, 0.53, 0.50), 0.0, 0.85)
    # Verde para la circulacion de la masa: sobre masa beige, agua azul y
    # calor rojo, es el unico color que no se confunde con nada.
    M.flecha_masa = material("flecha_masa", (0.04, 0.45, 0.20), 0.0, 0.4,
                             emision=0.9)
    M.flecha_calor = material("flecha_calor", (0.90, 0.15, 0.10), 0.0, 0.4,
                              emision=1.2)


# =============================================================================
# GEOMETRIA
# =============================================================================

def bastidor_existente():
    """
    SE CONSERVA. Pasa a ser el modulo base: sostiene el quemador y arriostra
    lateralmente la torre nueva. El recipiente lo ATRAVIESA por el vano.
    Unico corte: el brazo original en voladizo, que estorba al eje nuevo.
    """
    t = P.v_tubo
    x = P.v_mesa_x / 2 - t / 2
    y = P.v_mesa_y / 2 - t / 2
    h = P.v_mesa_z - t
    partes = []

    for sx in (-1, 1):
        for sy in (-1, 1):
            partes.append(caja(f"vp{sx}{sy}", t, t, h, sx * x, sy * y, h / 2,
                               M.viejo))
    # marco superior
    for sy in (-1, 1):
        partes.append(caja(f"vmx{sy}", P.v_mesa_x, t, t, 0, sy * y,
                           P.v_mesa_z - t / 2, M.viejo))
    for sx in (-1, 1):
        partes.append(caja(f"vmy{sx}", t, P.v_mesa_y - 2 * t, t, sx * x, 0,
                           P.v_mesa_z - t / 2, M.viejo))
    # travesanos inferiores
    for sy in (-1, 1):
        partes.append(caja(f"vt{sy}", P.v_mesa_x, t, t, 0, sy * y,
                           P.v_travesano_z, M.viejo))
    # columna original: se conserva, ahora soporta el panel de control
    partes.append(caja("vcol", t, t, P.v_columna_h, 0, y,
                       P.v_mesa_z + P.v_columna_h / 2, M.viejo))
    # soporte del quemador
    for sy in (-1, 1):
        partes.append(caja(f"vq{sy}", P.v_mesa_x - 2 * t, t, t, 0,
                           sy * (P.v_vano / 2 + t), P.q_z - 60, M.viejo))

    return unir(partes, "01_bastidor_EXISTENTE")


def torre_nueva():
    """
    NUEVA. Tubo 75x75x4. Cuatro patas al piso, viga superior para el
    motorreductor y aro de cuna a 1006 mm del que cuelga el recipiente.
    Se atornilla al bastidor viejo a la altura de la mesa: el viejo le da
    arriostramiento lateral y ella le lleva la carga al piso.
    """
    t = P.n_tubo
    x, y = P.n_pata_x, P.n_pata_y
    partes = []

    # 4 patas + placas de base ancladas al piso
    for sx in (-1, 1):
        for sy in (-1, 1):
            partes.append(caja(f"np{sx}{sy}", t, t, P.n_altura,
                               sx * x, sy * y, P.n_altura / 2, M.nuevo))
            partes.append(caja(f"nb{sx}{sy}", P.n_placa_base, P.n_placa_base,
                               P.n_placa_esp, sx * x, sy * y,
                               P.n_placa_esp / 2, M.nuevo))

    # NOTA DE MODELADO: cada travesano se hace de largo 2*x, de modo que sus
    # extremos quedan DENTRO del volumen de las patas. Si se hicieran a ras,
    # las caras coincidirian con las de la pata y el render sale con parches
    # negros por z-fighting. Es un detalle de modelado, no de diseno.
    largo_x, largo_y = 2 * x, 2 * y
    th = P.n_tubo_h
    zc = P.r_cradle_z
    z_arr = P.v_mesa_z - P.v_tubo / 2

    # Los miembros del plano DELANTERO (y = -330) van a un objeto aparte:
    # se ocultan en la vista en seccion para dejar ver el interior, igual
    # que en un dibujo tecnico se retira lo que esta delante del corte.
    frente = []

    # viga superior: largueros en Y + travesano central donde va el motor
    for sx in (-1, 1):
        partes.append(caja(f"nv{sx}", th, largo_y, th, sx * x, 0,
                           P.n_altura + t / 2, M.nuevo))
    partes.append(caja("nvc", largo_x, th, th, 0, 0,
                       P.n_altura + t / 2, M.nuevo))

    # marco del aro de cuna, a la altura de la boca de carga
    partes.append(caja("ncx_pos", largo_x, th, th, 0, y, zc, M.nuevo))
    frente.append(caja("ncx_neg", largo_x, th, th, 0, -y, zc, M.nuevo))
    for sx in (-1, 1):
        partes.append(caja(f"ncy{sx}", th, largo_y, th, sx * x, 0, zc,
                           M.nuevo))

    # arriostramiento a la altura de la mesa: aqui se atornilla al viejo
    partes.append(caja("nax_pos", largo_x, th, th, 0, y, z_arr, M.nuevo))
    frente.append(caja("nax_neg", largo_x, th, th, 0, -y, z_arr, M.nuevo))

    torre = unir(partes, "02_torre_NUEVA")
    unir(frente, "02b_torre_frente")

    # aro de cuna: placa con agujero por el que cuelga el recipiente
    aro = caja("aro", 2 * x, 2 * y, 14.0, 0, 0, zc + t / 2 + 7, M.nuevo)
    hueco = cilindro("aro_h", P.c_r_ext + 4, 60, 0, 0, zc, M.nuevo)
    aro = booleano(aro, hueco)
    return unir([torre, aro], "02_torre_NUEVA")


def recipiente():
    """Olla interior de proceso, inox 304, Ø280 x 652 interior."""
    olla = anillo("olla", P.r_r_ext, P.r_r_int, P.r_h_int, P.r_z_fondo, M.inox)
    fondo = cilindro("olla_f", P.r_r_ext, P.r_esp, 0, 0,
                     P.r_z_fondo - P.r_esp, M.inox)
    pest = anillo("olla_p", P.c_r_ext + 22, P.r_r_ext, 12,
                  P.r_cradle_z - 12, M.inox)
    return unir([olla, fondo, pest], "03_olla_interior")


def camisa():
    """
    CAMISA. Envolvente del bano. Se disena como camisa, no como 'camisa de
    agua': la misma chapa admite agua (hasta ~85 degC utiles en Quito) o
    aceite termico si la medida de PRO-05 obliga a subir de temperatura.
    Esa es la decision reversible del bloque 7 del dimensionamiento.
    """
    h = P.r_camisa_h
    env = anillo("cam", P.c_r_ext, P.c_r_int, h, P.c_z_fondo, M.inox)
    fondo = cilindro("cam_f", P.c_r_ext, P.r_esp, 0, 0,
                     P.c_z_fondo - P.r_esp, M.inox)
    corona = anillo("cam_c", P.c_r_ext, P.r_r_ext, P.r_esp,
                    P.c_z_fondo + h, M.inox)
    # venteo: OBLIGATORIO y sin tapon. Sin el, esto deja de ser bano maria
    # abierto y pasa a ser un recipiente a presion.
    vent = cilindro("vent", 9, 110, P.c_r_int + P.r_gap_camisa / 2 - 4, 0,
                    P.c_z_fondo + h, M.inox, 24)
    llen = cilindro("llen", 12, 80, -(P.c_r_int + P.r_gap_camisa / 2 - 4), 0,
                    P.c_z_fondo + h, M.inox, 24)
    return unir([env, fondo, corona, vent, llen], "04_camisa")


def fluido_camisa():
    """El agua del bano, para que se vea el circuito."""
    h = P.r_camisa_h - 40
    ag = anillo("agua", P.c_r_int, P.r_r_ext, h, P.c_z_fondo, M.agua)
    base = cilindro("agua_b", P.c_r_int, 30, 0, 0, P.c_z_fondo - 30, M.agua)
    return unir([ag, base], "05_agua_camisa")


def masa():
    """El lote de 30 kg, a su altura real de llenado."""
    m = cilindro("masa", P.r_r_int - 1, P.r_h_masa, 0, 0, P.r_z_fondo, M.masa)
    return m


def eje():
    largo = P.eje_z_top - P.eje_z_bot
    return cilindro("06_eje", P.eje_d / 2, largo, 0, 0, P.eje_z_bot,
                    M.inox, 32)


def ancla():
    """
    ANCLA CON TRAVESANO INTERMEDIO.
    Con h/D = 1.51 el ancla simple deja el nucleo girando como un tapon, que
    es justo el defecto que hoy produce 'centro crudo'. El travesano a media
    altura arrastra ese nucleo.
    """
    ra = P.r_r_int - P.rasp_gap - P.rasp_esp
    w, b = P.ancla_esp, P.ancla_barra
    zb = P.r_z_fondo + P.ancla_fondo
    zt = zb + P.r_h_masa + 110
    partes = []
    for sx in (-1, 1):
        partes.append(caja(f"av{sx}", w, b, zt - zb - b,
                           sx * (ra - w / 2), 0, (zb + b + zt) / 2, M.inox))
    partes.append(caja("ab", 2 * ra, b, w, 0, 0, zb + w / 2, M.inox))
    partes.append(caja("at", 2 * (ra - w / 2), b, w, 0, 0, zt - w / 2, M.inox))
    # travesano intermedio: el que arrastra el nucleo
    partes.append(caja("ai", 2 * (ra - w), b * 0.8, w * 0.8, 0, 0,
                       zb + P.r_h_masa * 0.45, M.inox))
    cubo = anillo("acubo", P.cubo_d / 2, P.eje_d / 2, 70, zt - 70, M.inox, 32)
    partes.append(cubo)
    return unir(partes, "07_ancla")


def raspadores():
    """PTFE con luz de 1.5 mm. Pieza de desgaste: se cambia, no se rectifica."""
    ra = P.r_r_int - P.rasp_gap - P.rasp_esp
    b = P.ancla_barra
    zb = P.r_z_fondo + P.ancla_fondo
    zt = zb + P.r_h_masa + 110
    partes = []
    for sx in (-1, 1):
        partes.append(caja(f"rv{sx}", P.rasp_esp, b, zt - zb - b,
                           sx * (ra + P.rasp_esp / 2), 0,
                           (zb + b + zt) / 2, M.ptfe))
    partes.append(caja("rb", 2 * ra, b, P.rasp_esp, 0, 0,
                       zb - P.rasp_esp / 2, M.ptfe))
    return unir(partes, "08_raspadores_PTFE")


def motorreductor():
    z0 = P.n_altura + P.n_viga
    placa = caja("mplaca", 300, 300, P.n_placa_esp, 0, 0,
                 z0 + P.n_placa_esp / 2, M.nuevo)
    z1 = z0 + P.n_placa_esp
    red = caja("mred", P.red_x, P.red_y, P.red_z, 0, 0,
               z1 + P.red_z / 2, M.motor)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=P.mot_d / 2 * MM, depth=P.mot_l * MM, vertices=32,
        rotation=(math.pi / 2, 0, 0),
        location=(0, (P.red_y / 2 + P.mot_l / 2) * MM,
                  (z1 + P.red_z * 0.6) * MM))
    mot = bpy.context.object
    mot.name = "mmot"
    poner_mat(mot, M.motor)
    return unir([placa, red, mot], "09_motorreductor")


def guia_eje():
    """
    Segundo apoyo del eje, en el aro de cuna. Sin el, el eje vuela 1.4 m
    desde el motor y la flecha se come la luz de 1.5 mm del raspador.
    """
    zc = P.r_cradle_z + P.n_tubo / 2 + 14
    barra = caja("gb", 2 * (P.c_r_ext + 10), 60, 14, 0, 0, zc + 55, M.nuevo)
    pies = []
    for sx in (-1, 1):
        pies.append(caja(f"gp{sx}", 50, 60, 48,
                         sx * (P.c_r_ext - 10), 0, zc + 24, M.nuevo))
    cubo = anillo("gc", (P.eje_d + 38) / 2, (P.eje_d + 1) / 2, 60,
                  zc + 32, M.nuevo, 32)
    return unir([barra] + pies + [cubo], "10_apoyo_guia_eje")


def quemador():
    """Anillo industrial de ~31 kBTU/h, con inyector para altura."""
    an = toro("q_anillo", P.q_d / 2, P.q_tubo / 2, P.q_z, M.fuego)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=P.q_tubo / 2 * MM, depth=320 * MM, vertices=16,
        rotation=(0, math.pi / 2, 0),
        location=(-(P.q_d / 2 + 160) * MM, 0, P.q_z * MM))
    al = bpy.context.object
    poner_mat(al, M.fuego)
    return unir([an, al], "11_quemador")


def flechas():
    """
    Flechas de proceso: naranja = circulacion de la masa,
    rojo = entrada de calor. Solo para el corte explicativo.
    """
    out = []

    def flecha(x, y, z, dz, mat, r=9.0, nombre="f"):
        cuerpo = cilindro(nombre, r, abs(dz), x, y, z if dz > 0 else z + dz,
                          mat, 16)
        bpy.ops.mesh.primitive_cone_add(
            radius1=r * 2.2 * MM, depth=34 * MM, vertices=16,
            rotation=(0 if dz > 0 else math.pi, 0, 0),
            location=(x * MM, y * MM, ((z + dz) if dz > 0 else z) * MM))
        p = bpy.context.object
        poner_mat(p, mat)
        return unir([cuerpo, p], nombre)

    # Todas las flechas van a y = -45 mm, POR DELANTE del plano de corte:
    # si van en y = 0 quedan medio enterradas en la cara de seccion.
    yf = -45.0

    # masa: sube pegada a la pared, que es donde entra el calor
    out.append(flecha(P.r_r_int * 0.70, yf, P.r_z_fondo + 50, 300,
                      M.flecha_masa, nombre="fm1"))
    # masa: baja por el centro, arrastrada por el travesano intermedio
    out.append(flecha(P.r_r_int * 0.20, yf, P.r_z_fondo + 380, -300,
                      M.flecha_masa, nombre="fm2"))
    # calor: del quemador al agua de la camisa
    out.append(flecha(P.c_r_int - 6, yf, P.c_z_fondo - 90, 170,
                      M.flecha_calor, r=8, nombre="fc1"))
    # calor: del agua a la masa, radial hacia dentro
    for i, zz in enumerate((0.28, 0.58, 0.85)):
        z = P.r_z_fondo + P.r_h_masa * zz
        cuerpo = cilindro(f"fcr{i}", 7, 46, 0, 0, 0, M.flecha_calor, 12)
        cuerpo.rotation_euler = (0, math.pi / 2, 0)
        cuerpo.location = ((P.r_r_int + 24) * MM, yf * MM, z * MM)
        out.append(cuerpo)
    return unir(out, "12_flechas_proceso")


def proceso_en_seccion():
    """
    Reconstruye olla, camisa, agua y masa como medias piezas (0..180 grados),
    dejando a la vista la cara de corte. Eje, ancla y raspadores NO se
    seccionan: en dibujo tecnico los ejes y las nervaduras nunca se cortan,
    y ademas asi se entiende mejor lo que hacen.
    """
    piezas = []
    a0, a1 = 0.0, 180.0

    # olla de proceso
    piezas.append(sector_anular("s_olla", P.r_r_ext, P.r_r_int, P.r_h_int,
                                P.r_z_fondo, a0, a1, M.inox))
    piezas.append(sector_anular("s_olla_f", P.r_r_ext, 1.0, P.r_esp,
                                P.r_z_fondo - P.r_esp, a0, a1, M.inox))
    # camisa
    piezas.append(sector_anular("s_cam", P.c_r_ext, P.c_r_int, P.r_camisa_h,
                                P.c_z_fondo, a0, a1, M.inox))
    piezas.append(sector_anular("s_cam_f", P.c_r_ext, 1.0, P.r_esp,
                                P.c_z_fondo - P.r_esp, a0, a1, M.inox))
    # agua del bano
    # Medio milimetro de retranqueo a cada lado: si el agua compartiera
    # superficie con la chapa, las dos caras coincidirian y el render las
    # mezcla. Es el mismo problema de z-fighting de los travesanos.
    piezas.append(sector_anular("s_agua", P.c_r_int - 0.5, P.r_r_ext + 0.5,
                                P.r_camisa_h - 30, P.c_z_fondo,
                                a0, a1, M.agua))
    piezas.append(sector_anular("s_agua_f", P.c_r_int, 1.0, 30.0,
                                P.c_z_fondo - 30, a0, a1, M.agua))
    # el lote de 30 kg
    piezas.append(sector_anular("s_masa", P.r_r_int - 1, 1.0, P.r_h_masa,
                                P.r_z_fondo, a0, a1, M.masa))
    return piezas


def piso():
    bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, -0.002))
    ob = bpy.context.object
    ob.name = "00_piso"
    poner_mat(ob, M.piso)
    return ob


# =============================================================================
# ESCENA Y RENDER
# =============================================================================

def luces_y_mundo():
    mundo = bpy.data.worlds.new("W")
    bpy.context.scene.world = mundo
    mundo.use_nodes = True
    mundo.node_tree.nodes["Background"].inputs[0].default_value = \
        (0.92, 0.93, 0.95, 1)
    mundo.node_tree.nodes["Background"].inputs[1].default_value = 0.7

    bpy.ops.object.light_add(type='AREA', location=(2.2, -2.6, 3.4))
    k = bpy.context.object
    k.data.energy = 900
    k.data.size = 3.0
    k.rotation_euler = (0.72, 0.0, 0.75)

    bpy.ops.object.light_add(type='AREA', location=(-2.6, -1.4, 2.2))
    f = bpy.context.object
    f.data.energy = 320
    f.data.size = 3.5
    f.rotation_euler = (1.15, 0, -1.05)

    bpy.ops.object.light_add(type='SUN', location=(0, 3, 5))
    s = bpy.context.object
    s.data.energy = 1.6
    s.rotation_euler = (-0.5, 0.3, 0)


def camara(loc, mira, lente=50, orto=None):
    """orto = ancho de encuadre en metros -> camara ortografica."""
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
    sc.render.film_transparent = False
    os.makedirs(SALIDA, exist_ok=True)
    sc.render.filepath = os.path.join(SALIDA, nombre)
    bpy.ops.render.render(write_still=True)
    print(f"  render -> {nombre}.png")


def cortar_mitad(objs):
    """Corta y > 0 para dejar la seccion a la vista. Falla ruidosamente."""
    for ob in objs:
        if ob is None or ob.type != 'MESH':
            print(f"  [corte] omitido: {ob}")
            continue
        n_antes = len(ob.data.vertices)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 1.5, 1.2))
        cuchilla = bpy.context.object
        cuchilla.scale = (4.0, 3.0, 5.0)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.select_all(action='DESELECT')
        booleano(ob, cuchilla)
        n_despues = len(ob.data.vertices)
        estado = "cortado" if n_despues != n_antes else "SIN EFECTO"
        print(f"  [corte] {ob.name:<26} {n_antes:>5} -> {n_despues:>5} verts"
              f"  {estado}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print(" MODELO BLENDER - PROTOTIPO 2 PARA 30 kg")
    print("=" * 70)
    # --- comprobacion que decide si el acople es posible ---
    v = comprobar_vano()
    print("")
    print(" COMPATIBILIDAD CON EL VANO DEL BASTIDOR EXISTENTE")
    print(" " + "-" * 60)
    print(f"   Diametro exterior del recipiente con camisa .. {v['d_ext']:6.0f} mm")
    print(f"   Vano necesario (con 12 mm de luz por lado) ... {v['necesario']:6.0f} mm")
    print(f"   Vano SUPUESTO del bastidor actual ............ {v['vano_supuesto']:6.0f} mm")
    if not v["pasa"]:
        falta = v["necesario"] - v["vano_supuesto"]
        print(f"   >> NO PASA. Faltan {falta:.0f} mm de vano.")
        print("   Tres salidas, en orden de preferencia:")
        print("     1. Agrandar el vano recortando el marco. Es un corte")
        print("        limpio en el marco superior, con refuerzo perimetral.")
        print("     2. Bajar el diametro del recipiente a 250 mm. Cuesta")
        print("        ~1.4 min mas de coccion y obliga a cinta helicoidal.")
        print("     3. Colgar el recipiente POR ENCIMA de la mesa, sin")
        print("        atravesarla. Sube la boca de carga y estorba.")
        print("   BAS-06 decide. Si el vano real es mayor, no hay problema.")
    else:
        print(f"   >> PASA, con {v['vano_supuesto'] - v['necesario']:.0f} mm de margen.")
    print(" " + "-" * 60)
    print("")

    limpiar()
    crear_materiales()
    os.makedirs(SALIDA, exist_ok=True)

    print(" construyendo geometria...")
    piso()
    o_viejo = bastidor_existente()
    o_torre = torre_nueva()
    o_olla = recipiente()
    o_cam = camisa()
    o_agua = fluido_camisa()
    o_masa = masa()
    o_eje = eje()
    o_ancla = ancla()
    o_rasp = raspadores()
    o_motor = motorreductor()
    o_guia = guia_eje()
    o_quem = quemador()
    print(f"  {len(bpy.data.objects)} objetos")

    luces_y_mundo()

    # --- guardar escena completa antes de cortar ---
    bpy.ops.wm.save_as_mainfile(
        filepath=os.path.join(SALIDA, "prototipo_2_30kg.blend"))
    try:
        bpy.ops.export_scene.gltf(
            filepath=os.path.join(SALIDA, "prototipo_2_30kg.glb"),
            export_format='GLB')
        print("  exportado GLB")
    except Exception as e:
        print(f"  GLB omitido: {e}")

    # --- vista 1: conjunto en perspectiva ---
    print(" render 1/4  conjunto...")
    camara((2.9, -3.3, 2.1), (0, 0, 1.00), lente=42)
    render("01_conjunto", res=(1100, 1400))

    # --- vista 2: alzado ortografico, para leer proporciones y alturas ---
    print(" render 2/4  alzado...")
    camara((0, -6.0, 1.05), (0, 0, 1.05), orto=2.5)
    render("02_alzado", res=(1000, 1400))

    # --- vista 3: acople del bastidor viejo con la torre nueva ---
    print(" render 3/4  detalle de acople...")
    camara((1.7, -2.2, 1.05), (0, 0, 0.76), lente=50)
    render("03_acople_base", res=(1300, 1050))

    # --- vista 4: SECCION, con las flechas de proceso ---
    print(" render 4/4  seccion de proceso...")
    for ob in (o_olla, o_cam, o_agua, o_masa):
        bpy.data.objects.remove(ob, do_unlink=True)
    # Se retira todo lo que queda delante del plano de corte. El bastidor
    # viejo tambien: su papel en el acople ya se explica en la vista 03, y
    # aqui solo taparia el proceso, que es lo que esta vista tiene que
    # contar.
    for nombre in ("02b_torre_frente", "01_bastidor_EXISTENTE"):
        ob = bpy.data.objects.get(nombre)
        if ob:
            bpy.data.objects.remove(ob, do_unlink=True)
    proceso_en_seccion()
    flechas()
    # seccion tecnica: de frente y en ortografica
    camara((0, -6.0, 0.70), (0, 0, 0.70), orto=0.92)
    render("04_seccion_proceso", res=(1050, 1450), muestras=64)

    bpy.ops.wm.save_as_mainfile(
        filepath=os.path.join(SALIDA, "prototipo_2_corte.blend"))

    print("=" * 70)
    print(f" Listo. Salidas en {os.path.relpath(SALIDA, RAIZ)}/")
    print("=" * 70)


if __name__ == "__main__":
    main()
