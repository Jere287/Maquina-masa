# Rediseño evolutivo — Máquina mezcladora-cocedora de porcelana fría

Modelo CAD paramétrico del prototipo **que ya existe en el taller**, con las
modificaciones del rediseño. No se parte de cero: el bastidor, el brazo superior
y el quemador GLP se conservan y el rediseño se **atornilla encima**.

```bash
pip3 install cadquery
python3 rediseno_prototipo.py
```

Salidas en `output/`: STEP y STL del ensamble y de cada pieza, vistas SVG/PNG y
el reporte de verificación.

---

## 1. Estado real del prototipo (según las fotos del Drive)

El documento de proyecto describía una máquina con camisa de agua, impulsor tipo
ancla y motorreductor de 1 HP. **La máquina física no tiene nada de eso todavía.**

| Documento de proyecto | Máquina real en el taller |
|---|---|
| Olla doble pared, baño maría | Olla **de pared simple**, **fuego directo** al fondo |
| Impulsor tipo ancla + raspadores PTFE | **Batidor globo de alambre** |
| Motorreductor 1 HP, 30 RPM | Motor Hubbell, placa **HP .125** (1/8 HP ≈ 93 W), 115 V |
| Olla angosta Ø200 × 640 | Olla tipo tamalera, ancha, proporción ≈ 1:1 |

Las tres fallas del proceso son consecuencia directa de esas tres ausencias:

| Falla | Causa en la máquina actual | Qué la corrige |
|---|---|---|
| Se quema / hace costra | Llama directa sobre la chapa (>300 °C) | Camisa de agua: tope físico de 100 °C |
| El motor no mueve la masa | 1/8 HP → 29.7 N·m disponibles | Motorreductor 1 HP → 237 N·m |
| Cocción despareja, hay que raspar | El globo atraviesa la masa y no toca la pared | Ancla + raspadores PTFE a 1.5 mm |

## 2. Los tres cambios

**#1 Motor.** Placa adaptadora de 12 mm atornillada al brazo existente; recibe la
brida del motorreductor. Se añade soporte de rodamiento para que el reductor no
tome la carga radial del ancla. **Sin cortes ni soldadura en el bastidor.**

**#2 Altura.** Empalmes atornillados con el **mismo tubo 40×40**: **+250 mm en las
cuatro patas**. La altura hace falta *abajo*, no arriba — la olla cuelga de la
mesa y necesita 758 mm libres bajo ella. Con la mesa original de 720 mm el
quemador quedaba **bajo el piso**. De paso la boca de carga sube a 970 mm, altura
de codo.

**#3 Uniones atornilladas.** Cuna de olla, placa de motor, extensiones de pata y
apoyo guía son uniones de desmontaje rápido: la olla y el ancla salen para
limpieza entre lotes.

Acompañan dos cambios de física sin los cuales el rediseño no sirve: **camisa de
agua** de 20 mm e **impulsor tipo ancla** con raspadores de PTFE.

## 3. Qué encontró la verificación

El script no solo dibuja: comprueba. Cuatro hallazgos que cambiaron el diseño:

1. **La olla alta no cabía.** Con la mesa a 720 mm el quemador quedaba a −38 mm,
   bajo el piso. De ahí el alargue de patas (cambio #2), y no de columna.
2. **El eje de Ø30 no servía.** Flecha de 1.41 mm en el voladizo con una luz de
   raspador de 1.50 mm: el raspador rozaría la pared. **Se subió a Ø40** (flecha
   0.62 mm). El cálculo fija el diámetro, no el catálogo.
3. **El apoyo guía no es un extra.** Sin él el voladizo es de 1092 mm y la flecha
   de 7.09 mm. Es la pieza que sostiene la luz de 1.5 mm.
4. **El quemador de 20 kBTU/h queda corto.** El proceso pide 2844 W útiles y el
   quemador entrega ~2345 W. Hacen falta ≥ 24 kBTU/h, o el lote tarda más.

Además, un resultado que conviene tener presente: por **conducción pura** el
centro de la olla tardaría ~477 min en cuajar. El ancla no es un accesorio de
mezclado — **es el mecanismo de transferencia de calor**.

## 4. Piezas

| Se conserva | Se fabrica | Se compra |
|---|---|---|
| 01 bastidor | 04 extensión de patas, 05 apoyo guía del eje, 06 placa de motor, 07 soporte de rodamiento, 09 olla interior, 10 camisa de agua, 11 cuna de olla, 12 tapa partida, 13 eje, 14 impulsor ancla, 15 raspadores PTFE | 08 motorreductor |
| 02 brazo superior | | |
| 03 quemador GLP | | |

## 5. Cotas por confirmar

Los parámetros marcados `[FOTO]` en `Parametros` están escalados desde las
fotografías y son los únicos que pueden mover las interfaces atornilladas.
**Medirlos con flexómetro antes de cortar**: sección de tubo, ancho y fondo de
mesa, altura de mesa, altura de columna y voladizo del brazo.

Sigue pendiente de la prueba de campo, y bloquea los planos definitivos:

- **Temperatura real de cuaje.** Todo el diseño asume 72 °C. Si la masa necesita
  más de 90 °C, la camisa a 90 °C no cocina nunca.
- **Torque real** en el punto más espeso: define si 1 HP alcanza.

## 6. Seguridad

La camisa es un sistema **abierto**. El venteo superior no lleva tapón ni
válvula: si se cierra, deja de ser un baño maría y pasa a ser un recipiente a
presión. Nunca operar la camisa en seco.
