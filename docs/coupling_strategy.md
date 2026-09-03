# Estrategia de acople  P1 → P2 (30 kg)

**Estado:** concepto. Se apoya en cotas `[SUPUESTO]` del bastidor. Se recorta
con las medidas reales (BAS-01…BAS-08) en cuanto lleguen.

---

## 1. El hallazgo que decide todo: hay dos cargas, no una

A 30 kg la máquina tiene **dos caminos de carga de naturaleza distinta**, y
mezclarlos en la misma estructura es lo que rompe el bastidor.

| | CAMINO A — recipiente | CAMINO B — accionamiento |
|---|---|---|
| Qué lleva | Lote 30 kg + agua 11 kg + chapa 19 kg + ancla 10 kg | Motorreductor 65 kg |
| Magnitud | **≈ 70 kg**, 685 N | 65 kg **+ 548 N·m de par de reacción** |
| Naturaleza | Estática, vertical, repartida en el perímetro del vano | **Torsión + flexión, pulsante** |
| ¿Lo aguanta una mesa soldada? | **Sí.** Es justo para lo que sirve | **No.** Ni de lejos |

El par de reacción es el que hace daño y es el que se suele olvidar: el par
que el reductor entrega al eje **se lo devuelve a su soporte**, con el mismo
valor y sentido contrario. Sale por los pernos del motor, torsiona el brazo y
flexiona la columna. Y es pulsante, porque el ancla encuentra resistencia
distinta en cada vuelta.

### Lo que dice el cálculo sobre tu bastidor

Con el tubo `[SUPUESTO]` de 40×40×2:

| | Capacidad | Requerido | Veredicto |
|---|---|---|---|
| Flexión | 367 N·m | 548 N·m | **No** |
| Torsión | 347 N·m | 548 N·m | **No** |

Se queda en unos dos tercios, sin ningún margen. Haría falta 50×50×2 solo para
empatar, y 60×60×3 para tener margen. **Esto se confirma o se descarta con
BAS-01 y BAS-02** — la tabla completa está en `reports/sizing_30kg.txt` §6.

---

## 2. La solución: separar los caminos, no reforzar

> **Arquitectura adoptada: "torre nueva sobre base existente".**

En vez de reforzar el bastidor para que lleve una carga para la que no fue
concebido, se le deja **solo lo que ya sabe hacer** y se añade una estructura
nueva que se lleva lo demás **directamente al piso**.

```
                    ┌─ motorreductor 2.2 kW ─┐
                    │      548 N·m           │
                    ▼                        │
        ╔═══════════════════════╗            │  CAMINO B
        ║   VIGA SUPERIOR       ║            │  torsión + flexión
        ║   torre nueva 75×75   ║            │  va DIRECTO al piso
        ╚═══════╦═══════╦═══════╝            │  por la torre nueva
                ║       ║                    │
        ┌───────╫───────╫───────┐            │
        │  ARO DE CUNA  1006 mm │◄───────────┘
        │  cuelga el recipiente │
        └───────╫───────╫───────┘   CAMINO A
                ║       ║           70 kg estáticos
     ┌──────────╫───────╫──────────┐
     │  BASTIDOR EXISTENTE  720 mm │  ← se conserva entero
     │  · arriostra la torre       │
     │  · sostiene el quemador     │
     │  · el recipiente lo ATRAVIESA
     └──────────╫───────╫──────────┘
                ║       ║
              PISO — placas ancladas
```

### Reparto de funciones

| Elemento | Función en el P2 | ¿Se toca? |
|---|---|---|
| **Bastidor existente** | Sostiene el quemador. Arriostra lateralmente la torre. Da el plano de trabajo | **Se conserva entero.** Un solo corte: el brazo en voladizo |
| **Columna original** | Pasa a soportar el panel de control y la válvula de gas | Se conserva, ya sin carga |
| **Torre nueva** 75×75×4 | Lleva recipiente **y** accionamiento al piso | Nueva |
| **Aro de cuna** a 1006 mm | Del que cuelga el recipiente. Es también la boca de carga | Nueva |
| **Arriostre** a 720 mm | Atornilla torre y bastidor. El viejo impide que la torre cabecee | Nueva |

### Por qué esto es mejor que reforzar

1. **No se suelda sobre estructura de origen desconocido.** No sabemos el
   acero ni la calidad de las soldaduras del bastidor. Reforzar exige confiar
   en lo que no se puede verificar.
2. **Es reversible.** El acople es atornillado. Si algo sale mal, se
   desmonta.
3. **Cada estructura trabaja donde es buena.** La mesa en compresión y
   flexión suave; la torre en torsión, para la que se dimensiona.
4. **Se puede fabricar y probar la torre sin parar la producción actual.**

---

## 3. El punto crítico del acople: el vano

**El recipiente atraviesa el vano del bastidor.** Ahí es donde el acople vive
o muere.

| | mm |
|---|---|
| Ø exterior del recipiente con camisa | **328** |
| Vano necesario (12 mm de luz por lado) | **352** |
| Vano `[SUPUESTO]` del bastidor actual | 300 |
| **Faltan** | **52** |

Con el vano supuesto **no pasa**. Tres salidas, en orden de preferencia:

1. **Agrandar el vano** recortando el marco superior, con refuerzo
   perimetral. Es un corte limpio y localizado. *Recomendada.*
2. **Bajar el recipiente a Ø250.** Cuesta ~1.4 min más de cocción y obliga a
   cinta helicoidal en vez de ancla — bastante más caro de fabricar.
3. **Colgar el recipiente por encima de la mesa**, sin atravesarla. Sube la
   boca de carga por encima de la altura de codo y estorba al operario.

> **BAS-06 (lado del vano) es, después de PRO-05, la medida que más decide.**
> Si el vano real resulta ≥ 352 mm, no hay nada que cortar.

---

## 4. Interfaces del acople

| ID | Interfaz | Cómo se resuelve | Requiere |
|---|---|---|---|
| AC-01 | Torre ↔ bastidor | 4 uniones atornilladas M12 a la altura de la mesa | BAS-03, BAS-04, BAS-05 |
| AC-02 | Recipiente ↔ vano | Atraviesa el vano; cuelga del aro de cuna | **BAS-06** |
| AC-03 | Quemador ↔ bastidor | Sobre el soporte existente, bajado a 230 mm | BAS-10 |
| AC-04 | Torre ↔ piso | 4 placas base con anclaje químico o expansivo | SEG-05 |
| AC-05 | Motorreductor ↔ viga | Placa adaptadora atornillada | Catálogo del reductor |
| AC-06 | Eje ↔ aro de cuna | Apoyo guía con buje de PTFE | — |

**AC-04 no es opcional.** Con 548 N·m pulsantes y ~150 kg de máquina cargada,
sin anclaje al piso la torre camina. El bastidor actual no está anclado; el
P2 tiene que estarlo.

---

## 5. Qué NO resuelve todavía este esquema

Honestidad sobre los huecos:

- **La descarga de 30 kg.** Con la olla llena el conjunto pasa de 55 kg y la
  boca es de 280 mm. No se vuelca a mano. Hay que resolverlo *en* el diseño:
  volteo con muñones, extracción con polipasto, o válvula de fondo. **Sin
  esto el P2 no es utilizable en producción.**
- **La limpieza.** El recipiente atraviesa el vano, así que para sacarlo hay
  que subirlo ~700 mm. Eso condiciona la altura libre del local (SEG-04).
- **La guarda del eje.** 1.4 m de eje girando en zona de trabajo. Va en el
  diseño desde el principio, no al final.
- **Toda la parte térmica** depende de PRO-05. Ver §7 de
  `reports/sizing_30kg.txt`.

---

## 6. Decisión que conviene tomar ya

**Diseñar la camisa como camisa, no como "camisa de agua".**

La misma envolvente de chapa admite agua (hasta ~85 °C útiles en Quito) o
aceite térmico (hasta 150 °C, con termostato). Cambia el fluido y el control;
**no cambia el recipiente**.

Así la medición de PRO-05 no puede obligarte a rehacer la chapa, que es lo
caro. Es la forma de no quedar atrapado por un dato que aún no tienes.

La contrapartida, dicha claramente: con agua, la física impide pasarse de
temperatura. Con aceite, solo lo impide el termostato — y un termostato se
avería.
