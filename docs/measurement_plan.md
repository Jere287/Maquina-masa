# Plan de medición — Prototipo 1

**Estado:** FASE 2. Este documento es la lista de trabajo de campo.

**Cómo usarlo:** cada medida tiene un **ID**. Al medir, anota `ID = valor`. Con
esa lista vuelco los valores a `config/design_parameters.yaml` y arrancan los
cálculos de FASE 4.

**Prioridades:**
- 🔴 **CRÍTICA** — sin ella **no se puede** ejecutar un cálculo. Bloquea.
- 🟡 **IMPORTANTE** — el cálculo corre, pero con supuestos que debilitan el resultado.
- 🟢 **SECUNDARIA** — mejora la documentación; no bloquea nada.

---

## Instrumentos necesarios

| Instrumento | Para qué | ¿Imprescindible? |
|---|---|---|
| Flexómetro (5 m) | Cotas del bastidor y de la olla | Sí |
| Calibrador / pie de rey | Espesores, diámetros de eje y tubo | Sí |
| Báscula (hasta ~50 kg) | Masas de lote y componentes | Sí |
| **Pinza amperimétrica** | Corriente del motor bajo carga → **par real** | Sí — es la que desbloquea el motor |
| Termómetro de pincho | Temperatura de la masa | Sí |
| Termómetro infrarrojo | Temperatura de la **pared** de la olla | Muy recomendable |
| Cronómetro (el del móvil) | RPM y tiempos de ciclo | Sí |
| Báscula de gancho / dinamómetro | Método alternativo de par | Opcional |

> Si solo puedes conseguir **un** instrumento nuevo, que sea la **pinza
> amperimétrica**. Es la que convierte "el motor no tiene fuerza" en un número.

---

## BLOQUE 1 — Referencia dimensional para las fotos 🔴

Es lo primero, cuesta 5 minutos y revaloriza todo el material que ya tenemos.

| ID | Qué hacer |
|---|---|
| REF-01 | Apoyar un flexómetro **extendido y visible** sobre la mesa del bastidor y repetir la foto **frontal** |
| REF-02 | Ídem en el plano lateral → foto **lateral** |
| REF-03 | Apoyar el flexómetro **cruzando la boca de la olla** → foto **cenital** |
| REF-04 | Tomarlas lo más **perpendiculares** posible al plano, desde lejos y con zoom |

Habilita cotas **aproximadas** por escalado, útiles para verificación cruzada.
**Nunca** para cerrar planos de taller.

---

## BLOQUE 2 — Bastidor 🔴

Desbloquea: `structure.py`, y la decisión CONSERVA / MODIFICA del bastidor.

| ID | Medida | Prioridad | Cómo |
|---|---|---|---|
| BAS-01 | **Sección del tubo** (lado × lado) | 🔴 | Calibrador |
| BAS-02 | **Espesor de pared del tubo** | 🔴 | Calibrador en un extremo o boca de corte |
| BAS-03 | Altura del piso a la **cara superior de la mesa** | 🔴 | Flexómetro |
| BAS-04 | Ancho exterior de la mesa | 🔴 | |
| BAS-05 | Fondo exterior de la mesa | 🔴 | |
| BAS-06 | **Lado del vano** donde entra la olla | 🔴 | Es cota de interfaz congelada |
| BAS-07 | Altura de la **columna** (mesa → cara inferior del brazo) | 🔴 | |
| BAS-08 | **Voladizo del brazo** (eje de columna → eje de la olla) | 🔴 | Determina el momento flector |
| BAS-09 | Posición de la columna respecto al marco | 🟡 | |
| BAS-10 | Altura de los travesaños inferiores | 🟡 | |
| BAS-11 | Separación entre patas (entre ejes) | 🟡 | |
| BAS-12 | ¿Perfil hueco o macizo? ¿Costura visible? | 🟡 | Confirma BAS-02 |
| BAS-13 | Estado de las soldaduras: fisuras, poros, falta de penetración | 🟡 | Inspección visual |
| BAS-14 | ¿El bastidor cojea? ¿Se mueve al agitar? | 🟡 | Empujar y observar |
| BAS-15 | Masa total del bastidor | 🟢 | Estimable por longitudes y perfil |

## BLOQUE 3 — Recipiente 🔴

Desbloquea: `agitator.py`, capacidad real, geometría del agitador.

| ID | Medida | Prioridad |
|---|---|---|
| OLL-01 | **Diámetro interior** en la boca | 🔴 |
| OLL-02 | Diámetro exterior | 🟡 |
| OLL-03 | **Altura interior total** | 🔴 |
| OLL-04 | **Espesor de pared** | 🟡 |
| OLL-05 | Espesor del fondo | 🟡 |
| OLL-06 | **Capacidad hasta el borde**, en litros — llenar con agua y medir | 🔴 |
| OLL-07 | **Altura que alcanza la mezcla** en un lote normal | 🔴 |
| OLL-08 | Masa de la olla vacía | 🟡 |
| OLL-09 | ¿Fondo plano o con radio? Radio si lo tiene | 🟡 |
| OLL-10 | ¿Cuánto sobresale y cuánto se hunde en el vano? | 🔴 |
| OLL-11 | Marcas de grado de inox (304 / 430 / imán) | 🟢 |

> **Truco para OLL-11:** el 304 es **no magnético**; el 430 y el acero al carbono
> sí. Un imán de nevera lo distingue en un segundo.

## BLOQUE 4 — Eje y agitador 🔴

Desbloquea: `shaft.py`, `agitator.py`, `bearings.py`.

| ID | Medida | Prioridad |
|---|---|---|
| EJE-01 | **Diámetro del eje** | 🔴 |
| EJE-02 | **Longitud libre**: último apoyo → agarre del agitador | 🔴 | 
| EJE-03 | Longitud total | 🟡 |
| EJE-04 | Profundidad de inmersión en la mezcla | 🔴 |
| EJE-05 | ¿Macizo o tubular? Si es tubo, espesor | 🟡 |
| EJE-06 | Material (imán: inox 304 no pega) | 🟡 |
| EJE-07 | ¿Está recto? Girarlo a mano y ver si cabecea | 🟡 |
| AGI-01 | **Diámetro exterior del batidor** | 🔴 |
| AGI-02 | Altura del batidor | 🔴 |
| AGI-03 | Diámetro del alambre | 🟡 |
| AGI-04 | **Holgura batidor → pared** | 🔴 |
| AGI-05 | **Holgura batidor → fondo** | 🔴 |
| AGI-06 | ¿Alambres deformados o abiertos por el uso? | 🟡 |

## BLOQUE 5 — Motor y transmisión 🔴

Desbloquea: `motor.py`, `transmission.py`. **Es el bloque más importante.**

### 5.1 Placa de características

| ID | Dato | Prioridad |
|---|---|---|
| MOT-01 | **RPM** (en la foto es ilegible) | 🔴 |
| MOT-02 | Modelo / `MODEL NO` completo | 🔴 |
| MOT-03 | **Amperios nominales** | 🔴 |
| MOT-04 | Frecuencia (Hz) | 🟡 |
| MOT-05 | Monofásico o trifásico | 🟡 |
| MOT-06 | Confirmar `HP .125` y `115 V` | 🟡 |
| MOT-07 | Factor de servicio (`SF`) si aparece | 🟢 |

> Foto de la placa **de frente, con buena luz y enfocada**. Con `MODEL NO` puedo
> buscar la hoja de datos y sacar par de arranque y curva par-velocidad.

### 5.2 Transmisión

| ID | Medida | Prioridad | Cómo |
|---|---|---|---|
| TRA-01 | **¿Existe reducción?** | 🔴 | Ver 5.3 |
| TRA-02 | **Relación de reducción** | 🔴 | Ver 5.3 |
| TRA-03 | Qué es el manguito entre motor y eje | 🔴 | Desmontar y fotografiar |
| TRA-04 | **¿Hay rodamientos aparte del motor?** | 🔴 | Desmontar y mirar |
| TRA-05 | Si los hay: marcación del rodamiento | 🟡 | Suele ir grabada en el aro |
| TRA-06 | Diámetro del eje de salida del motor | 🟡 | Calibrador |
| TRA-07 | Patrón de pernos del motor: nº, Ø, círculo | 🔴 | Cota de interfaz congelada |
| TRA-08 | Dimensiones envolventes del motor | 🟡 | |
| TRA-09 | **Masa del motor** | 🟡 | Báscula |

### 5.3 Cómo medir RPM y relación de reducción sin instrumentos

**RPM de salida (el eje del agitador), en vacío:**
1. Pegar un trozo de **cinta de color** en el eje.
2. Grabar **vídeo en cámara lenta** con el móvil, 10 segundos.
3. Contar las vueltas de la marca y dividir por el tiempo. → `TRA-02a`

**Relación de reducción:**
1. Motor **desconectado**.
2. Marcar el ventilador del motor y el eje de salida.
3. Girar el ventilador a mano contando vueltas hasta que el eje de salida dé
   **una vuelta completa**.
4. Ese número **es** la relación. → `TRA-02`

## BLOQUE 6 — Calentamiento 🟡

| ID | Medida | Prioridad |
|---|---|---|
| QUE-01 | Tipo de quemador y diámetro del anillo | 🟡 |
| QUE-02 | **Potencia nominal** (kBTU/h o kW), de etiqueta o factura | 🔴 |
| QUE-03 | Marcación del inyector | 🟢 |
| QUE-04 | Distancia del quemador al fondo de la olla | 🟡 |
| QUE-05 | Presión del regulador | 🟢 |
| QUE-06 | Consumo de GLP por lote (pesar el cilindro antes y después) | 🟡 |

> **QUE-06** da el rendimiento real del sistema de calentamiento sin necesidad
> de instrumentación: es una resta de dos pesadas.

## BLOQUE 7 — Proceso y producto 🔴

Desbloquea: `agitator.py`, `motor.py` y todo el diseño térmico.

| ID | Medida | Prioridad |
|---|---|---|
| PRO-01 | **Masa cargada** por lote, por ingrediente | 🔴 |
| PRO-02 | **Masa de producto terminado** por lote | 🔴 |
| PRO-03 | **Tiempo total de ciclo** actual | 🔴 |
| PRO-04 | Tiempo hasta que empieza a espesar | 🔴 |
| PRO-05 | **Temperatura de la masa cuando cuaja** (termómetro de pincho, al centro) | 🔴 |
| PRO-06 | **Temperatura de la pared** de la olla en operación (infrarrojo) | 🔴 |
| PRO-07 | Temperatura de la masa al descargar | 🟡 |
| PRO-08 | Densidad de la masa terminada: pesar 1 L | 🔴 |
| PRO-09 | ¿Dónde se quema primero: fondo, pared o ambos? | 🟡 |
| PRO-10 | Masa que queda pegada en la pared (raspar y pesar) | 🟡 |

> **PRO-05 es la medida más crítica de todo el proyecto.** Toda decisión sobre el
> método de calentamiento depende de ella. Ahora mismo es un `[SUPUESTO]` de
> 72 °C que **nadie ha verificado**.
>
> **PRO-06** convierte "se quema" en un número: si la pared pasa de ~120 °C,
> queda demostrado que la causa es la llama directa.

## BLOQUE 8 — Par real 🔴 — LA MEDIDA CLAVE

Sin esto **no se puede seleccionar el motor** (regla 9: comparar par requerido
contra par disponible). Tres métodos, de mejor a peor:

### Método A — Pinza amperimétrica (recomendado)

| ID | Medida |
|---|---|
| PAR-01 | Corriente **en vacío**, sin mezcla, girando libre |
| PAR-02 | Corriente **al inicio**, mezcla líquida |
| PAR-03 | **Corriente máxima**, en el punto más espeso |
| PAR-04 | ¿Llega a **calarse** el motor? ¿En qué momento? |
| PAR-05 | ¿Salta la protección térmica? ¿A los cuántos minutos? |

De ahí sale la potencia mecánica real y, con las RPM, el **par requerido**.

### Método B — Brazo de palanca (si no hay pinza)

1. Motor **desconectado**, mezcla en el punto más espeso.
2. Acoplar una **llave o tubo** al eje, de longitud conocida `L`.
3. Tirar del extremo con una **báscula de gancho** hasta que el eje gire despacio.
4. `PAR-06` = fuerza medida `F` · longitud `L`. **Es el par requerido, medido.**

### Método C — Referencia cualitativa (último recurso)

`PAR-07`: comparar el esfuerzo de menear a mano contra una referencia conocida
(masa de pan / plastilina / mortero). Da un orden de magnitud, nada más.

## BLOQUE 9 — Masas 🟡

| ID | Componente |
|---|---|
| MAS-01 | Motor |
| MAS-02 | Olla vacía |
| MAS-03 | Eje + agitador |
| MAS-04 | Lote completo de mezcla |
| MAS-05 | Bastidor (estimable) |

## BLOQUE 10 — Seguridad y entorno 🟢

| ID | Dato |
|---|---|
| SEG-01 | ¿Hay diferencial o térmico en la instalación? |
| SEG-02 | ¿Hay toma de tierra efectiva? |
| SEG-03 | ¿Hay ventilación en el local? (hay gas) |
| SEG-04 | Altura libre del techo |
| SEG-05 | Espacio libre alrededor de la máquina |
| SEG-06 | ¿Quién opera y con qué formación? |

---

## Orden de trabajo sugerido

| Sesión | Bloques | Tiempo | Instrumento |
|---|---|---|---|
| **1** | REF + BAS + OLL + EJE + AGI | ~1 h | Flexómetro, calibrador, imán |
| **2** | MOT + TRA (máquina parada) | ~45 min | Cámara, calibrador, herramienta |
| **3** | **PRO + PAR, durante un lote real** | 1 lote | Pinza, termómetros, cronómetro, báscula |
| **4** | QUE + MAS + SEG | ~30 min | Báscula |

> **La sesión 3 es la que más vale.** Hay que hacerla durante una producción
> real, no en una prueba en seco. Si solo puedes hacer una sesión, haz esa.

---

## Qué desbloquea cada bloque

| Bloque | Módulo de cálculo | Decisión que permite cerrar |
|---|---|---|
| BAS | `structure.py` | ¿Se conserva el bastidor? |
| OLL + AGI | `agitator.py` | Tipo y geometría del agitador |
| **PAR + PRO** | `motor.py`, `transmission.py` | **Selección de motor y reducción** |
| EJE + PAR | `shaft.py` | Diámetro del eje |
| TRA + PAR | `bearings.py` | Rodamientos y apoyos |
| PRO | térmico | Método de calentamiento |
| MAS | `structure.py`, `safety.py` | Cargas y estabilidad |

---

## Mínimo indispensable para arrancar FASE 4

Si el tiempo es corto, estos **12 datos** ya permiten empezar a calcular:

```
BAS-01  seccion del tubo
BAS-02  espesor del tubo
BAS-03  altura de mesa
BAS-08  voladizo del brazo
OLL-01  diametro interior de la olla
OLL-06  capacidad en litros
OLL-07  altura de mezcla en un lote
EJE-01  diametro del eje
EJE-02  longitud libre del eje
MOT-01  RPM del motor
PAR-03  corriente maxima  (o PAR-06, par por palanca)
PRO-05  temperatura de cuaje
```

Con esos doce se ejecuta el primer `run_analysis.py` completo.
