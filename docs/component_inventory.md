# Inventario de componentes — Prototipo 1

**Estado:** FASE 1. Sin dimensiones: ninguna foto tiene referencia dimensional.

**Leyenda de procedencia:** `[OBSERVADO]` foto · `[MEDIDO]` medido físicamente ·
`[PROPORCIONADO]` dato del usuario · `[CALCULADO]` · `[SUPUESTO]` · `[PENDIENTE]`

**Leyenda de decisión:**
- **CONSERVA** — se mantiene sin cambios
- **CONSERVA-COND** — se conserva salvo que el cálculo demuestre lo contrario
- **REDISEÑA** — hay evidencia observada suficiente para rediseñar
- **PENDIENTE** — no hay datos para decidir

> Ninguna decisión de esta tabla es definitiva. Se cierran en FASE 4 (cálculos)
> y FASE 6 (rediseño mecánico).

---

## A. Estructura

| ID | Componente | Función | Material | Dimensiones | Datos conocidos | Datos pendientes | Decisión | Justificación |
|---|---|---|---|---|---|---|---|---|
| E-01 | Bastidor, patas | Soporte y altura de trabajo | Acero al carbono `[SUPUESTO]` | `[PENDIENTE]` | Tubo cuadrado, soldado, pintado `[OBSERVADO]` | Sección, espesor, longitud, escuadría | **CONSERVA-COND** | Filosofía del proyecto: se conserva salvo que el análisis de cargas (FASE 4) lo desapruebe |
| E-02 | Marco superior con vano | Recibe y centra la olla | Acero al carbono `[SUPUESTO]` | `[PENDIENTE]` | Vano cuadrado central `[OBSERVADO]` | Lado del vano, sección del perfil | **CONSERVA-COND** | Define la interfaz de la olla. Es cota congelada del ICD |
| E-03 | Travesaños inferiores | Arriostran las patas | Acero al carbono `[SUPUESTO]` | `[PENDIENTE]` | Presentes `[OBSERVADO]` | Sección, altura sobre el piso | **CONSERVA-COND** | — |
| E-04 | Columna posterior | Soporta el brazo del motor | Acero al carbono `[SUPUESTO]` | `[PENDIENTE]` | Vertical, lado posterior derecho `[OBSERVADO]` | Altura, sección | **CONSERVA-COND** | Fija la altura del eje. Cota congelada del ICD |
| E-05 | Brazo en voladizo | Sostiene el motor sobre el eje de la olla | Acero al carbono `[SUPUESTO]` | `[PENDIENTE]` | Horizontal, atornillado al motor `[OBSERVADO]` | Longitud del voladizo, sección | **CONSERVA-COND** | Su flexión bajo el peso del motor P2 se verifica en FASE 4 |
| E-06 | Apoyo del quemador | Sostiene el quemador bajo la olla | Acero `[SUPUESTO]` | `[PENDIENTE]` | Estructura bajo el vano `[OBSERVADO]` | Configuración, fijación | **PENDIENTE** | Depende de la decisión sobre calentamiento (FASE 5) |
| E-07 | Interfaz bastidor–piso | Apoyo | — | `[PENDIENTE]` | **Sin placas ni nivelación** `[OBSERVADO]` | — | **REDISEÑA** | P-09: máquina sin anclar. Con un motor mayor sube el par de reacción y la vibración |

## B. Accionamiento

| ID | Componente | Función | Material | Dimensiones | Datos conocidos | Datos pendientes | Decisión | Justificación |
|---|---|---|---|---|---|---|---|---|
| A-01 | Motor Hubbell | Acciona el eje | Carcasa de aluminio `[OBSERVADO]` | `[PENDIENTE]` | `HUBBELL SPECIAL PRODUCTS`, `115 V`, **`HP .125`**, térmicamente protegido `[OBSERVADO]` | **RPM** (ilegible), A, Hz, fases, modelo, patrón de pernos, masa | **PENDIENTE** | 1/8 HP es muy bajo para masa espesa, pero **el motor definitivo no se elige hasta medir el par real** (FASE 4) |
| A-02 | Acoplamiento / manguito | Une motor y eje | `[PENDIENTE]` | `[PENDIENTE]` | Tramo cilíndrico entre motor y eje `[OBSERVADO]` | Tipo, si es acople o reducción, capacidad de par | **PENDIENTE** | No se puede decidir sin saber qué es |
| A-03 | Reductor | Reducir RPM / aumentar par | — | — | **Sin transmisión externa visible** `[OBSERVADO]` | ¿Existe reducción integrada? ¿Relación? | **PENDIENTE** | Determinante para el par disponible. Método de medida en el plan |
| A-04 | Soporte de rodamiento del eje | Tomar carga radial y momento | — | — | **Ninguno visible** `[OBSERVADO]` | Confirmar si existe | **PENDIENTE** | Si se confirma la ausencia (P-06), es un hallazgo estructural de primer orden |

## C. Mezcla

| ID | Componente | Función | Material | Dimensiones | Datos conocidos | Datos pendientes | Decisión | Justificación |
|---|---|---|---|---|---|---|---|---|
| M-01 | Eje vertical | Transmite par al agitador | Acero `[SUPUESTO]` | `[PENDIENTE]` | Vertical, del motor al interior de la olla `[OBSERVADO]` | Diámetro, longitud libre, inmersión, material, macizo o hueco | **PENDIENTE** | No se asume que el diámetro actual sea correcto: se calcula y luego se compara (regla 11) |
| M-02 | Batidor de globo | Agitar | Alambre de acero `[OBSERVADO]` | `[PENDIENTE]` | Tipo globo de repostería; holgura amplia a la pared; no toca fondo ni pared `[OBSERVADO]` | Diámetro, altura, diámetro de alambre, holguras | **REDISEÑA** | P-01 y P-02. Un globo de alambre no desplaza masa espesa ni renueva la película de pared. Evidencia observada suficiente |
| M-03 | Elemento rascador | Renovar película de pared | — | — | **No existe** `[OBSERVADO]` | — | **REDISEÑA** (añadir) | P-02 explica directamente R-02 y R-04 |

## D. Recipiente

| ID | Componente | Función | Material | Dimensiones | Datos conocidos | Datos pendientes | Decisión | Justificación |
|---|---|---|---|---|---|---|---|---|
| R-01 | Olla | Contiene el lote | Inox `[SUPUESTO]`, por aspecto | `[PENDIENTE]` | **Pared simple**, cilíndrica, fondo plano, proporción ≈1:1 `[OBSERVADO]` | Ø ext/int, altura, espesor, capacidad, grado de inox, masa | **PENDIENTE** | Depende de la decisión sobre calentamiento (FASE 5) |
| R-02 | Asas laterales | Manipulación | Inox `[SUPUESTO]` | `[PENDIENTE]` | Dos, remachadas `[OBSERVADO]` | Capacidad de carga | **PENDIENTE** | Relevante para P-11: hoy se levanta la olla cargada y caliente a mano |
| R-03 | Asa de arco | Manipulación | Alambre `[OBSERVADO]` | `[PENDIENTE]` | Abatible, tipo balde `[OBSERVADO]` | — | **PENDIENTE** | Posible punto de enganche para elevación asistida |
| R-04 | Tapa | Contención, pérdidas térmicas | — | — | **No existe** `[OBSERVADO]` | — | **PENDIENTE** | Evaluar en FASE 5 |
| R-05 | Fijación de la olla | Retener la olla | — | — | **Solo apoyo por gravedad** `[OBSERVADO]` | — | **PENDIENTE** | Con más par, el rozamiento del agitador puede arrastrar la olla. A verificar en FASE 4 |

## E. Calentamiento

| ID | Componente | Función | Material | Dimensiones | Datos conocidos | Datos pendientes | Decisión | Justificación |
|---|---|---|---|---|---|---|---|---|
| C-01 | Quemador GLP | Aportar calor | — | `[PENDIENTE]` | Bajo el fondo, **llama directa** `[OBSERVADO]` | Tipo, Ø, potencia nominal, marcación del inyector | **PENDIENTE** | El método de calentamiento se decide en FASE 5 |
| C-02 | Válvula de bola azul | Corte manual de gas | — | `[PENDIENTE]` | Montada en el bastidor `[OBSERVADO]` | Diámetro, norma | **CONSERVA-COND** | Cumple su función |
| C-03 | Manguera GLP | Conducción de gas | Elastómero `[OBSERVADO]` | `[PENDIENTE]` | Amarilla, **tendida por el piso** `[OBSERVADO]` | Longitud, norma, fecha de caducidad | **REDISEÑA** (recorrido) | P-10: cruza zona de paso. Riesgo de tropiezo y de daño mecánico |
| C-04 | Regulador GLP | Regular presión | — | `[PENDIENTE]` | Conector amarillo en el extremo `[OBSERVADO]` | Presión de salida, caudal | **PENDIENTE** | — |
| C-05 | Control de temperatura | Regular el proceso | — | — | **No existe** `[OBSERVADO]` | — | **REDISEÑA** (añadir) | P-04. Sin medida no hay proceso repetible |

## F. Seguridad

| ID | Componente | Función | Material | Dimensiones | Datos conocidos | Datos pendientes | Decisión | Justificación |
|---|---|---|---|---|---|---|---|---|
| S-01 | Guarda del eje | Evitar atrapamiento | — | — | **No existe** `[OBSERVADO]` | — | **REDISEÑA** (añadir) | P-07. Eje rotativo accesible durante la operación |
| S-02 | Parada de emergencia | Corte inmediato | — | — | **No visible** `[OBSERVADO]` | Confirmar | **REDISEÑA** (añadir) | P-08 |
| S-03 | Protección eléctrica | Diferencial / térmico | — | — | **No visible** `[OBSERVADO]` | Confirmar instalación | **REDISEÑA** (añadir) | P-08. Entorno húmedo con gas y agua |
| S-04 | Anclaje al piso | Estabilidad | — | — | **No existe** `[OBSERVADO]` | — | **REDISEÑA** (añadir) | P-09 |
| S-05 | Protección térmica al operario | Evitar quemaduras | — | — | **No existe** `[OBSERVADO]` | — | **PENDIENTE** | Olla y quemador accesibles durante la operación |

---

## Resumen de decisiones de FASE 1

| Decisión | Nº | Componentes |
|---|---|---|
| **CONSERVA-COND** | 6 | E-01, E-02, E-03, E-04, E-05, C-02 |
| **REDISEÑA** | 9 | E-07, M-02, M-03, C-03, C-05, S-01, S-02, S-03, S-04 |
| **PENDIENTE** | 14 | E-06, A-01…A-04, M-01, R-01…R-05, C-01, C-04, S-05 |

**Nota sobre los REDISEÑA:** ninguno se basa en una dimensión. Todos se apoyan en
**ausencias** o en **inadecuación de tipo**, que sí son determinables por foto.
Ningún componente cuyo rediseño dependa de una dimensión se ha marcado todavía.

**Nota sobre el motor:** A-01 queda **PENDIENTE**, no REDISEÑA, pese a que 1/8 HP
parece claramente insuficiente. La regla 9 exige comparar par requerido contra
par disponible, y el par requerido aún no está medido.
