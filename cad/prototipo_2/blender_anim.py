#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
 ANIMACIONES DEL PROTOTIPO 2  -  para ver la maquina funcionando
=============================================================================

Genera dos videos MP4 a partir del mismo modelo de blender_p2.py, para poder
ver el conjunto sin tener Blender instalado.

  A) seccion_girando.mp4   El ancla girando dentro del bano, en corte.
                           48 fotogramas a 24 fps = 2 s = UNA VUELTA COMPLETA
                           a 30 rpm. Es tiempo real: lo que ves es la
                           velocidad a la que va a girar de verdad.

  B) vuelta_maquina.mp4    Giro de camara alrededor del conjunto, para ver
                           como encaja la torre nueva con el bastidor actual.

NOTA DE ENTORNO: en este contenedor no hay GPU, asi que EEVEE y Workbench no
arrancan (les falta libEGL). Se usa Cycles en CPU con pocas muestras y
denoising: mas lento por fotograma, pero es el unico que funciona sin GPU.

USO
---
    python3 cad/prototipo_2/blender_anim.py

Salidas en output_blender/
=============================================================================
"""

from __future__ import annotations

import math
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

import bpy                                    # noqa: E402
import blender_p2 as m                        # noqa: E402

SALIDA = m.SALIDA
FPS = 24


# =============================================================================
def centrar_origen(objs):
    """
    Lleva el origen de cada objeto al eje de la maquina. Sin esto, girar un
    objeto lo hace alrededor de su propio centro y el ancla saldria orbitando
    en vez de rotando sobre el eje.
    """
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
    for ob in objs:
        if ob is None:
            continue
        bpy.ops.object.select_all(action='DESELECT')
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')


def interpolacion_lineal():
    """
    El eje gira a velocidad constante: no acelera ni frena. Se fija ANTES de
    insertar claves, en vez de recorrer las fcurves despues, porque en
    Blender 5 las acciones pasaron a ser "slotted" y ya no exponen .fcurves
    directamente.
    """
    bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'


def animar_giro(objs, n_frames):
    """Una vuelta completa repartida en n_frames."""
    interpolacion_lineal()
    for ob in objs:
        if ob is None:
            continue
        for f, ang in ((1, 0.0), (n_frames + 1, 2 * math.pi)):
            ob.rotation_euler = (0.0, 0.0, ang)
            ob.keyframe_insert("rotation_euler", frame=f)


def config_video(nombre, res, n_frames, muestras=10):
    """
    Configura render de SECUENCIA PNG, no de video.

    El bpy que se instala por pip viene compilado SIN soporte FFMPEG, asi que
    Blender no puede escribir MP4 directamente. Se renderizan fotogramas
    sueltos y se codifican despues con el ffmpeg que trae imageio-ffmpeg.
    """
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = muestras
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, n_frames
    sc.render.image_settings.file_format = 'PNG'
    carpeta = os.path.join(SALIDA, "_frames_" + nombre.replace(".mp4", ""))
    if os.path.isdir(carpeta):
        for f in os.listdir(carpeta):
            os.remove(os.path.join(carpeta, f))
    os.makedirs(carpeta, exist_ok=True)
    sc.render.filepath = os.path.join(carpeta, "f_")
    return carpeta


def codificar(carpeta, nombre):
    """Junta los PNG en un MP4 (H.264) y en un GIF de respaldo."""
    import subprocess
    import imageio_ffmpeg

    exe = imageio_ffmpeg.get_ffmpeg_exe()
    patron = os.path.join(carpeta, "f_%04d.png")
    mp4 = os.path.join(SALIDA, nombre)
    cmd = [exe, "-y", "-framerate", str(FPS), "-start_number", "1",
           "-i", patron, "-c:v", "libx264", "-pix_fmt", "yuv420p",
           "-crf", "20",
           # H.264 exige dimensiones pares
           "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
           "-movflags", "+faststart", mp4]
    subprocess.run(cmd, check=True, capture_output=True)

    # GIF de respaldo, por si el visor no reproduce MP4
    gif = mp4.replace(".mp4", ".gif")
    try:
        from PIL import Image
        archivos = sorted(f for f in os.listdir(carpeta) if f.endswith(".png"))
        ims = [Image.open(os.path.join(carpeta, f)).convert("P",
               palette=Image.ADAPTIVE, colors=128) for f in archivos]
        if ims:
            ims[0].save(gif, save_all=True, append_images=ims[1:],
                        duration=int(1000 / FPS), loop=0, optimize=True)
    except Exception as e:
        print(f"  GIF omitido: {e}")

    # limpieza de fotogramas sueltos
    for f in os.listdir(carpeta):
        os.remove(os.path.join(carpeta, f))
    os.rmdir(carpeta)
    return mp4


# =============================================================================
def escena_base():
    """Reconstruye el modelo completo usando el codigo de blender_p2."""
    m.limpiar()
    m.crear_materiales()
    m.piso()
    o = {
        "viejo": m.bastidor_existente(),
        "columna": m.columna_reforzada(),
        "collar": m.collar_par(),
        "topes": m.topes_antigiro(),
        "olla": m.recipiente(),
        "camisa": m.camisa(),
        "agua": m.fluido_camisa(),
        "masa": m.masa(),
        "eje": m.eje(),
        "cinta": m.cinta_helicoidal(),
        "rasp": m.raspadores(),
        "motor": m.motorreductor(),
        "boca": m.boca_carga(),
        "quemador": m.quemador(),
    }
    m.luces_y_mundo()
    return o


def anim_seccion(n_frames=48):
    """A) El ancla girando dentro del bano, en corte."""
    print("\n[A] seccion con el ancla girando...")
    o = escena_base()

    # pasar a vista de seccion: fuera lo que esta delante del plano de corte
    for k in ("olla", "camisa", "agua", "masa"):
        bpy.data.objects.remove(o[k], do_unlink=True)
    for nombre in ("02b_torre_frente", "01_bastidor_EXISTENTE"):
        ob = bpy.data.objects.get(nombre)
        if ob:
            bpy.data.objects.remove(ob, do_unlink=True)
    m.proceso_en_seccion()
    m.flechas()

    # lo unico que gira: eje, cinta helicoidal y raspadores
    giran = [o["eje"], o["cinta"], o["rasp"]]
    centrar_origen(giran)
    animar_giro(giran, n_frames)

    m.camara((0, -6.0, 0.78), (0, 0, 0.78), orto=0.98)
    carpeta = config_video("A_seccion_girando.mp4", (640, 900), n_frames)
    bpy.ops.render.render(animation=True)
    codificar(carpeta, "A_seccion_girando.mp4")
    print("  -> A_seccion_girando.mp4")


def anim_vuelta(n_frames=72):
    """B) Vuelta de camara alrededor del conjunto."""
    print("\n[B] vuelta alrededor de la maquina...")
    escena_base()

    # camara colgada de un vacio que gira: orbita limpia y estable
    bpy.ops.object.empty_add(location=(0, 0, 1.05))
    pivote = bpy.context.object
    cam = m.camara((2.9, -2.9, 1.95), (0, 0, 1.05), lente=42)
    cam.parent = pivote
    cam.matrix_parent_inverse = pivote.matrix_world.inverted()

    interpolacion_lineal()
    for f, ang in ((1, 0.0), (n_frames + 1, 2 * math.pi)):
        pivote.rotation_euler = (0.0, 0.0, ang)
        pivote.keyframe_insert("rotation_euler", frame=f)

    carpeta = config_video("B_vuelta_maquina.mp4", (720, 780), n_frames)
    bpy.ops.render.render(animation=True)
    codificar(carpeta, "B_vuelta_maquina.mp4")
    print("  -> B_vuelta_maquina.mp4")


def main():
    print("=" * 70)
    print(" ANIMACIONES - PROTOTIPO 2 PARA 30 kg")
    print("=" * 70)
    anim_seccion()
    anim_vuelta()
    print("=" * 70)
    for f in sorted(os.listdir(SALIDA)):
        if f.endswith((".mp4", ".gif")):
            kb = os.path.getsize(os.path.join(SALIDA, f)) / 1024
            print(f"  {f:<28}{kb:8.0f} kB")
    print("=" * 70)


if __name__ == "__main__":
    main()
