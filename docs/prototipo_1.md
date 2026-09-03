# Prototipo 1 — Ingeniería inversa

**Estado:** FASE 1 completada. Documento basado **exclusivamente en observación
fotográfica**. No contiene ninguna dimensión.

**Fuente:** 9 fotografías distintas del prototipo físico (carpeta de Drive del
proyecto, 2026-09-02). Ver `docs/measurement_plan.md` para lo que falta medir.

---

## 0. Advertencia sobre las tres máquinas de este proyecto

Conviene no confundirlas, porque en la documentación previa aparecían mezcladas:

| # | Qué es | Estado |
|---|---|---|
| **P1** | La máquina **física** de las fotos. Batidor de globo, olla simple, fuego directo, motor 1/8 HP | **Existe y funciona.** Es la baseline de este proyecto |
| "Proto Nivel 1" | Propuesta **en papel** del `CLAUDE.md`: olla Ø200×640 con camisa de agua, ancla, motorreductor 1 HP | Nunca se construyó. Es una propuesta previa |
| `cad/exploratorio/` | Modelo CAD que generé antes de fijar estas reglas | **Contiene cotas estimadas de foto. No fabricable.** Ver su README |

Cuando este documento dice "Prototipo 1" se refiere **siempre** a la máquina
física de las fotografías.

---

## 1. Descripción general

`[OBSERVADO]`

Mezcladora vertical de un solo eje, de construcción artesanal, montada sobre un
bastidor de tubo estructural pintado de negro. Un motor eléctrico en voladizo
sobre el bastidor acciona un eje vertical que baja al interior de una olla de
acero inoxidable. La olla se calienta por **llama directa de GLP** desde abajo.

La máquina está instalada en lo que parece un espacio doméstico o taller
pequeño, apoyada libremente en el piso junto a una pared, sin anclaje visible.

## 2. Principio de funcionamiento inferido

`[OBSERVADO]` + `[PROPORCIONADO]`

1. Se carga la mezcla líquida (cola vinílica, maicena, glicerina, vaselina,
   vinagre, benzoato) en la olla.
2. Se enciende el quemador de GLP bajo el fondo de la olla.
3. El motor gira el eje con el batidor de globo, agitando mientras se calienta.
4. El almidón gelatiniza y la mezcla pasa de líquida a masa plástica.
5. Se apaga, se retira la olla y se descarga la masa manualmente.

El calentamiento es por **conducción desde el fondo**, con la llama incidiendo
directamente sobre la chapa de la olla. No hay ningún elemento intermedio.

## 3. Sistemas visibles

### 3.1 Sistema estructural — bastidor

`[OBSERVADO]`

- Tubo estructural de sección **cuadrada**, pintado de negro.
- Construcción **soldada** (no se ven uniones atornilladas en el bastidor).
- Arquitectura tipo **mesa con pórtico**: cuatro patas verticales, un marco
  superior horizontal, y travesaños inferiores que arriostran las patas.
- Del lado **posterior derecho** sube una **columna** vertical que termina en un
  **brazo horizontal en voladizo** que cruza por encima del centro de la olla.
- El marco superior tiene un **vano central** (abertura cuadrada) donde se
  asienta la olla. La olla queda parcialmente **descolgada** dentro del vano.
- Bajo el vano se ve estructura adicional que sirve de soporte al quemador.
- Apoyo directo en el piso, **sin placas de base ni nivelación visibles**.

### 3.2 Sistema de accionamiento — motor

`[OBSERVADO]`

- Motor eléctrico de carcasa de **aluminio fundido**, montaje vertical con el
  eje hacia abajo, atornillado al extremo del brazo en voladizo.
- Placa de características parcialmente legible:
  - `HUBBELL SPECIAL PRODUCTS INC — KENOSHA, WI 53144`
  - `THERMALLY PROTECTED`
  - `WARNING: MOTOR TO BE PROPERLY GROUNDED... TO REDUCE THE RISK OF ELECTRICAL
     SHOCK, DISCONNECT SUPPLY BEFORE SERVICING UNIT`
  - `VOLTS 115`
  - **`HP .125`**  ← el único dato numérico de potencia que se lee con certeza
  - `RPM 4__` — los dígitos siguientes **no son legibles**
- Tapa cilíndrica negra en la parte superior (probable cubierta de ventilador o
  de caja de conexiones).
- Caja negra auxiliar montada al costado — **no identificable**; podría ser caja
  de bornes, condensador o interruptor.
- Cableado a la vista, sin canalización ni prensaestopas visibles.

> `HP .125` = 1/8 HP ≈ 93 W nominales. Es el único dato de potencia confirmado.

### 3.3 Sistema de transmisión

`[OBSERVADO]`

- Entre el motor y el eje de mezcla se aprecia un tramo cilíndrico que **podría**
  ser un acoplamiento, un manguito o una reducción integrada.
- **No se observan** poleas, correas, cadenas ni engranajes externos.
- **No se observa** ningún soporte de rodamiento independiente del motor. El eje
  parece colgar directamente del motor, en **voladizo puro**.

> Es la observación de mayor consecuencia estructural del prototipo, y está
> **pendiente de confirmar** físicamente.

### 3.4 Sistema de mezcla — agitador

`[OBSERVADO]`

- **Batidor tipo globo** (balloon whisk) de alambre, del tipo de repostería.
- Alambres de sección delgada formando lazos.
- Diámetro claramente **menor** que el diámetro interior de la olla: se aprecia
  una holgura anular amplia entre el globo y la pared.
- **No hay rascadores** ni ningún elemento que toque la pared o el fondo.
- El globo ocupa solo la zona **inferior** del volumen de la olla.

### 3.5 Recipiente

`[OBSERVADO]`

- Olla de **acero inoxidable**, cilíndrica de pared recta y fondo plano.
- Proporción aproximadamente **1:1** (diámetro y altura de orden similar); es
  ancha y baja, del tipo olla tamalera / caldero industrial.
- **Dos asas laterales** remachadas, más un **asa de arco tipo balde** abatible.
- **Pared simple.** No hay ningún indicio de doble pared ni de camisa.
- Se asienta en el vano del marco superior del bastidor.
- **Sin tapa.**

### 3.6 Sistema de calentamiento

`[OBSERVADO]`

- Quemador de GLP situado **bajo el fondo de la olla**, dentro del bastidor.
- **Manguera amarilla de GLP** que sale del bastidor, recorre el piso y termina
  en un **conector/regulador amarillo**.
- **Válvula de bola de maneral azul** montada en el bastidor, del lado
  izquierdo — control manual del gas.
- **No se observa** termostato, sonda de temperatura, termómetro, válvula
  termostática ni ningún elemento de regulación automática.

> El control de temperatura es **enteramente manual y a criterio del operario**.

### 3.7 Sistemas de seguridad

`[OBSERVADO]` — **ausencias**, todas relevantes:

- **Sin guarda** en el eje rotativo ni en el acoplamiento. El eje queda expuesto
  entre el motor y la boca de la olla.
- **Sin parada de emergencia** visible.
- **Sin protección eléctrica** visible (ni diferencial, ni térmico, ni tablero).
- **Sin anclaje al piso.** La máquina se apoya libremente.
- **Manguera de gas tendida por el suelo**, cruzando la zona de paso.
- Cableado eléctrico **en la proximidad de la zona del quemador**.
- La olla, caliente y con masa, se manipula a mano por las asas.

## 4. Flujo de potencia

```
Red eléctrica 115 V
   ↓
Motor Hubbell  [HP .125]   ← ¿RPM? ¿reducción? PENDIENTE
   ↓
Acoplamiento / manguito    ← naturaleza PENDIENTE
   ↓
Eje vertical               ← ¿apoyado o en voladizo? PENDIENTE
   ↓
Batidor de globo
   ↓
Mezcla (par resistente)
```

**Sin punto de apoyo intermedio identificado.** Si se confirma, toda la carga
radial y el momento flector del agitador los toma el rodamiento interno del
motor, que no está diseñado para eso.

## 5. Flujo de material

```
Carga manual de líquidos + maicena por la boca (abierta, sin tapa)
   ↓
Mezcla y cocción en la misma olla — un solo lote
   ↓
Descarga: se retira la olla del bastidor y se vacía a mano
   ↓
Limpieza manual de olla y batidor
```

Sin válvula de descarga, sin sistema de volteo y sin ayuda de elevación.

## 6. Puntos de montaje observados

| Interfaz | Cómo se resuelve hoy | Observación |
|---|---|---|
| Motor ↔ brazo | Atornillado al extremo del voladizo | Patrón de pernos PENDIENTE |
| Motor ↔ eje | Manguito / acoplamiento | Tipo PENDIENTE |
| Olla ↔ bastidor | Asentada en el vano del marco | Sin fijación positiva: la olla solo se apoya |
| Quemador ↔ bastidor | Alojado bajo el vano | Fijación PENDIENTE |
| Bastidor ↔ piso | Apoyo libre | Sin anclaje ni nivelación |

## 7. Problemas identificados

Se separa lo que se **observa** de lo que el usuario **reporta**.

### 7.1 Confirmados por observación directa

| # | Problema | Evidencia |
|---|---|---|
| P-01 | **Agitador inadecuado para masa espesa.** Un globo de alambre corta la masa en vez de desplazarla, y su rigidez es baja | Foto del interior de la olla |
| P-02 | **No hay renovación de la película de pared.** Ningún elemento toca la pared ni el fondo | Holgura anular visible |
| P-03 | **Calentamiento por llama directa.** Sin elemento intermedio entre la llama y la chapa | Quemador bajo el fondo |
| P-04 | **Sin control de temperatura.** Ni sonda, ni termostato, ni termómetro | Solo válvula manual |
| P-05 | **Motor de 1/8 HP.** Potencia muy baja para agitar masa espesa | Placa `HP .125` |
| P-06 | **Eje probablemente en voladizo puro** desde el motor | Sin soporte intermedio visible |
| P-07 | **Eje rotativo sin guarda.** Riesgo de atrapamiento | Eje expuesto |
| P-08 | **Sin parada de emergencia ni protección eléctrica visible** | — |
| P-09 | **Máquina sin anclar** | Apoyo libre en el piso |
| P-10 | **Manguera de gas por zona de paso** | Recorrido por el suelo |
| P-11 | **Descarga y limpieza totalmente manuales**, con olla caliente y cargada | Sin volteo ni elevación |

### 7.2 Reportados por el usuario

`[PROPORCIONADO]` — pendientes de correlacionar con medición:

| # | Problema reportado | Hipótesis a verificar |
|---|---|---|
| R-01 | El motor se recalienta y no tiene fuerza | Consistente con P-05. Verificar con **amperímetro de pinza** en el punto más espeso |
| R-02 | Se quema / hace costra | Consistente con P-03. Verificar **temperatura de pared** con termómetro infrarrojo |
| R-03 | Cocción despareja: bordes quemados, centro crudo | Consistente con P-01 + P-02 + P-03 |
| R-04 | La masa se pega a las paredes y se desperdicia | Consistente con P-02 |

> Las cuatro fallas reportadas tienen explicación coherente en lo observado.
> Ninguna requiere invocar una causa no identificada.

## 8. Oportunidades de mejora (sin comprometer todavía ninguna solución)

Se listan como **líneas a evaluar en fases posteriores**, no como decisiones.

| Sistema | Oportunidad | Fase donde se decide |
|---|---|---|
| Agitador | Geometría que barra pared y fondo y desplace volumen | FASE 5–6 |
| Transmisión | Reducir RPM y aumentar par si el cálculo lo exige | FASE 4 |
| Eje | Añadir un segundo apoyo para eliminar el voladizo puro | FASE 6 |
| Calentamiento | Interponer un medio entre llama y producto | FASE 5 |
| Control | Instrumentar temperatura | FASE 5 |
| Descarga | Facilitar la extracción de la olla cargada | FASE 6 |
| Seguridad | Guarda de eje, paro de emergencia, protección eléctrica, anclaje | Transversal, desde FASE 3 |

## 9. Qué NO puede determinarse de las fotografías

Ninguna de las fotos contiene una **referencia dimensional conocida**. Por tanto
**no se declara ninguna dimensión** en este documento.

No determinable por foto:

- Toda dimensión lineal, sin excepción.
- Sección y espesor de pared del tubo estructural.
- Diámetro, altura, espesor y capacidad de la olla.
- Diámetro, longitud libre y material del eje.
- Diámetro del batidor y sus holguras a pared y fondo.
- Si existe reductor y su relación.
- RPM del motor (dígitos ilegibles), amperaje, frecuencia, fases, modelo.
- Si hay rodamientos independientes y de qué tipo.
- Potencia y tipo del quemador.
- Masa de los componentes.
- Materiales exactos (el inoxidable se infiere del aspecto, no está confirmado).

### 9.1 Cómo habilitar el uso dimensional de las fotos

Existe una vía barata para convertir las fotos en material aprovechable:

1. Colocar un **flexómetro extendido** apoyado en el plano de interés.
2. Repetir las mismas 3 tomas (frontal, lateral, cenital), lo más
   perpendicular posible al plano y desde lejos con zoom, para reducir la
   distorsión de perspectiva.

Con esa referencia se podrán obtener cotas **aproximadas** por escalado —
suficientes para verificación cruzada, **nunca** para cerrar planos de taller.

---

## 10. Conclusión de FASE 1

El Prototipo 1 es una mezcladora vertical funcional cuya arquitectura general —
**bastidor de tubo con mesa y pórtico, accionamiento superior en voladizo, olla
en el vano, calentamiento por debajo** — es **razonable y se conserva** como
baseline.

Los problemas se concentran en los **componentes**, no en la arquitectura:
agitador, transmisión, apoyo del eje, método de calentamiento, control y
seguridad. Eso es exactamente lo que hace viable un rediseño evolutivo.

**No se propone ninguna modificación estructural en esta fase.** La decisión
sobre el bastidor corresponde a FASE 4, tras el análisis de cargas, y requiere
las medidas de `docs/measurement_plan.md`.
