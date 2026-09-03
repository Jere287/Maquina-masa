# Control de interfaces (ICD) — Contrato geométrico P1 → P2

**Estado:** FASE 1. Estructura definida; **valores pendientes de medición**.

Este documento es el **contrato** entre el Prototipo 1 y el Prototipo 2. Define
qué cotas **no pueden cambiar**, para que todo componente nuevo se diseñe *para
adaptarse* al bastidor existente, y no al revés.

**Regla de uso:** cualquier propuesta de P2 que viole una cota `CONGELADA` debe
justificarse técnicamente por escrito y quedar registrada en la sección 5.

---

## 1. Clasificación

| Clase | Significado | Quién puede cambiarla |
|---|---|---|
| 🔒 **CONGELADA** | No cambia. El diseño de P2 se adapta a ella | Solo con justificación técnica documentada |
| 🔧 **AJUSTABLE** | Puede cambiar dentro de un rango, sin tocar el bastidor | El diseño de P2 |
| 🆓 **LIBRE** | Sin restricción por parte de P1 | El diseño de P2 |
| ❓ **POR DEFINIR** | Se clasifica cuando haya medición | — |

---

## 2. Interfaces congeladas 🔒

Son las que definen la arquitectura que el proyecto se compromete a conservar.

### 2.1 Bastidor — envolvente general

| ID | Cota | Valor | Fuente | Por qué se congela |
|---|---|---|---|---|
| ICD-01 | Ancho exterior de la mesa | `UNKNOWN` | `BAS-04` | Define la huella de la máquina |
| ICD-02 | Fondo exterior de la mesa | `UNKNOWN` | `BAS-05` | Ídem |
| ICD-03 | **Altura del piso a la mesa** | `UNKNOWN` | `BAS-03` | Altura de trabajo del operario. La filosofía del proyecto la conserva |
| ICD-04 | Sección del tubo estructural | `UNKNOWN` | `BAS-01` | Todo perfil añadido debe **coincidir** con el existente |
| ICD-05 | Espesor de pared del tubo | `UNKNOWN` | `BAS-02` | Determina la resistencia de las uniones nuevas |

### 2.2 Interfaz del recipiente

| ID | Cota | Valor | Fuente | Por qué se congela |
|---|---|---|---|---|
| ICD-10 | **Lado del vano del marco** | `UNKNOWN` | `BAS-06` | Es el hueco físico donde entra la olla. **La interfaz más restrictiva de la máquina** |
| ICD-11 | Cota Z del plano de apoyo de la olla | `UNKNOWN` | `BAS-03` | Fija la posición vertical de todo el tren de mezcla |
| ICD-12 | Posición X-Y del eje de la olla en el marco | `UNKNOWN` | `BAS-09` | Debe coincidir con el eje del motor |

> **ICD-10 manda sobre el diámetro exterior del recipiente de P2**, camisa o
> aislamiento incluidos. Cualquier propuesta que no pase por ese vano exige
> modificar el marco, y eso es modificación estructural.

### 2.3 Interfaz del accionamiento

| ID | Cota | Valor | Fuente | Por qué se congela |
|---|---|---|---|---|
| ICD-20 | **Altura del brazo en voladizo** | `UNKNOWN` | `BAS-07` | Fija la longitud disponible del eje |
| ICD-21 | **Voladizo del brazo** (columna → eje de olla) | `UNKNOWN` | `BAS-08` | Fija el brazo de palanca sobre la columna |
| ICD-22 | Concentricidad eje del motor ↔ eje de la olla | `UNKNOWN` | `BAS-09`, `BAS-06` | Una excentricidad genera carga radial parásita |
| ICD-23 | Patrón de pernos del motor en el brazo | `UNKNOWN` | `TRA-07` | Si P2 lo respeta, el motor se cambia **sin tocar el brazo** |

> **ICD-23 es la interfaz de mayor valor económico del proyecto.** Si el motor
> nuevo se monta sobre una **placa adaptadora** que reproduce este patrón, el
> cambio de motor no requiere corte ni soldadura sobre el bastidor.

### 2.4 Concepto de funcionamiento

| ID | Característica | Estado |
|---|---|---|
| ICD-30 | Eje **vertical** único | 🔒 CONGELADA |
| ICD-31 | Accionamiento **superior** (motor arriba, agitador abajo) | 🔒 CONGELADA |
| ICD-32 | Recipiente **cilíndrico vertical** | 🔒 CONGELADA |
| ICD-33 | Calentamiento **desde abajo** | 🔒 CONGELADA — *el medio de transmisión del calor es 🔧 AJUSTABLE* |
| ICD-34 | Proceso **por lotes** (batch) | 🔒 CONGELADA |
| ICD-35 | Carga **manual por la boca** superior | 🔧 AJUSTABLE |

> **Matiz importante sobre ICD-33:** se congela *que el calor entre por abajo*,
> no *que sea llama directa sobre la olla*. Interponer un medio (baño maría,
> difusor, placa) **respeta** esta interfaz. Es una distinción deliberada: separa
> la arquitectura, que se conserva, del mecanismo, que está a discusión en FASE 5.

---

## 3. Interfaces ajustables 🔧

Pueden cambiar sin tocar el bastidor.

| ID | Elemento | Límite |
|---|---|---|
| ICD-40 | Diámetro del eje | Limitado por ICD-23 y por el paso disponible |
| ICD-41 | Longitud del eje | Limitada por ICD-20 e ICD-11 |
| ICD-42 | Tipo y geometría del agitador | Limitado por ICD-10 y por el Ø interior del recipiente |
| ICD-43 | Motor y reductor | Limitados por ICD-23 (o por placa adaptadora) y por la masa admisible en el voladizo |
| ICD-44 | Rodamientos y soportes de eje | Libres, si se apoyan en estructura existente o en piezas atornilladas |
| ICD-45 | Recipiente | **Ø exterior limitado por ICD-10** |
| ICD-46 | Quemador y tren de gas | Libre bajo el plano de la mesa |
| ICD-47 | Guardas, paro de emergencia, instrumentación | Libres |

---

## 4. Interfaces libres 🆓

Sin restricción impuesta por P1: sistema de descarga, ayuda de elevación,
tapa, aislamiento térmico, instrumentación y control, anclaje al piso,
protección eléctrica.

---

## 5. Registro de violaciones autorizadas

Ninguna hasta la fecha.

| Fecha | ICD | Justificación técnica | Autorizado por |
|---|---|---|---|
| — | — | — | — |

> **Precedente a registrar cuando corresponda:** el modelo de
> `cad/exploratorio/` proponía alargar las patas +250 mm, lo que **viola
> ICD-03** (altura de trabajo). El argumento era geométrico —hacer sitio bajo la
> mesa para un recipiente más alto— pero se apoyaba en cotas estimadas de foto,
> así que **no es una justificación válida** bajo las reglas actuales. Queda
> anulado hasta que existan mediciones.

---

## 6. Verificación

Cuando exista el CAD de P2, cada cota 🔒 se comprueba automáticamente contra
este documento. Una cota congelada que no coincida es un **fallo de diseño**, no
una variante.

Implementación prevista: `calculations/interface_check.py` en FASE 7.

---

## 7. Estado

| Métrica | Valor |
|---|---|
| Interfaces definidas | 24 |
| Con valor numérico | **0** |
| Pendientes de medición | **24** |

**El ICD no es operativo hasta que se completen las medidas del BLOQUE 2 del
plan de medición.** Hasta entonces solo fija *qué* se congela, no *en cuánto*.
