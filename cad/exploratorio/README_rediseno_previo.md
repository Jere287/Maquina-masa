# ⚠️ CAD exploratorio — NO FABRICABLE

**Estado: ANULADO como base de fabricación. Se conserva como registro.**

`rediseno_prototipo.py` se generó **antes** de establecer las reglas de
procedencia de datos del proyecto (regla 4). Sus cotas de bastidor están
**escaladas visualmente de las fotografías**, que es exactamente lo que esas
reglas prohíben.

## Por qué no sirve para fabricar

| Parámetro | En el script | Realidad |
|---|---|---|
| Sección del tubo | 40×40×2 mm | `[PENDIENTE]` — `BAS-01`, `BAS-02` |
| Altura de mesa | 720 mm | `[PENDIENTE]` — `BAS-03` |
| Mesa | 450×450 mm | `[PENDIENTE]` — `BAS-04`, `BAS-05` |
| Altura de columna | 620 mm | `[PENDIENTE]` — `BAS-07` |
| Voladizo del brazo | 350 mm | `[PENDIENTE]` — `BAS-08` |
| Olla | Ø320×350 mm | `[PENDIENTE]` — `OLL-01`, `OLL-03` |

Todas están marcadas `[FOTO]` en el propio script. Ninguna foto tenía
referencia dimensional, así que **ninguna es utilizable**.

Además propone alargar las patas +250 mm, lo que **viola ICD-03** (altura de
trabajo). El argumento geométrico era correcto en su lógica interna, pero
partía de cotas inventadas, así que no constituye justificación válida. Queda
registrado en `docs/interface_control.md` §5.

## Qué sí conserva valor

El **método**, no los números:

- Estructura de CAD paramétrico en CadQuery, con exportación a STEP/STL.
- Bloque de verificación que **detecta** incoherencias en vez de dibujarlas
  sin más: encontró el quemador bajo el piso y la flexión excesiva del eje.
- Separación explícita entre pieza reutilizada, fabricada y comprada.
- Render de vista previa y limpieza de exports obsoletos.

Ese esqueleto se reutilizará en **FASE 7**, realimentado con las medidas
reales. Los razonamientos físicos que contiene (escalado R² del tiempo de
cuaje, flexión del eje frente a la luz del rascador, balance del quemador)
siguen siendo válidos como **método**; sus resultados numéricos no, porque las
entradas eran inventadas.

## Cómo ejecutarlo, si hace falta consultarlo

```bash
pip3 install cadquery
python3 cad/exploratorio/rediseno_prototipo.py
```

Escribe en `output/`. **No usar esas salidas para cortar material.**
