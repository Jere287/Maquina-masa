# Rediseño de mezcladora de porcelana fría — P1 → P2

Rediseño evolutivo de una mezcladora de porcelana fría existente y funcional.
El **Prototipo 1 físico es la baseline**: su arquitectura se conserva y se
rediseñan los componentes, no la máquina.

**Fase actual: 1 (ingeniería inversa) — completada.**
**Estado: esperando las mediciones físicas del P1.**

```bash
pip3 install pyyaml
python3 config/check_parameters.py            # ¿qué datos tenemos?
python3 config/check_parameters.py --faltantes
```

## Regla que gobierna el proyecto

Todo dato lleva su procedencia: `[OBSERVADO]` `[MEDIDO]` `[PROPORCIONADO]`
`[CALCULADO]` `[SUPUESTO]` `[PENDIENTE]`.

**Nunca se presenta una estimación como si fuera un dato real.** Las fotografías
no se usan para obtener dimensiones, porque ninguna tiene referencia
dimensional conocida.

Hoy: **24 de 92 parámetros conocidos (26 %)**, y **ninguna dimensión**.

## Estructura

```
config/     design_parameters.yaml   fuente única de verdad
            check_parameters.py      auditoría de completitud
docs/       prototipo_1.md           ingeniería inversa del P1
            component_inventory.md   qué se conserva y qué se rediseña
            measurement_plan.md      qué medir, cómo y en qué orden
            interface_control.md     contrato geométrico P1 → P2
calculations/  FASE 4 — vacío
cad/        prototipo_1/  prototipo_2/   FASE 7 — vacíos
            exploratorio/              CAD previo, NO fabricable
reports/       FASE 8 — vacío
manufacturing/ FASE 9 — vacío
```

## Fases

| # | Fase | Estado |
|---|---|---|
| 1 | Ingeniería inversa | ✅ **Completada** |
| 2 | Plan de medición | ✅ **Entregado** — pendiente de ejecutar en campo |
| 3 | Requisitos | ⏸ Requiere mediciones |
| 4 | Cálculos preliminares | ⏸ Bloqueada: faltan los 12 datos mínimos |
| 5–10 | Concepto, rediseño, CAD, validación, manufactura, documentación | ⏸ |

## Qué se sabe hoy del P1

**Confirmado por observación:** bastidor soldado de tubo cuadrado con mesa,
pórtico y brazo en voladizo · motor Hubbell `HP .125` a 115 V · agitador de
**globo de alambre** sin rascadores · olla de **pared simple** · **llama directa
de GLP** al fondo · **sin control de temperatura** · **sin guarda de eje, sin
paro de emergencia, sin anclaje**.

**No determinable por foto:** absolutamente ninguna dimensión, las RPM del
motor, si existe reducción, y si el eje tiene algún apoyo aparte del motor.

Las cuatro fallas reportadas por el usuario tienen explicación coherente en lo
observado. Ninguna exige invocar una causa no identificada.

## Siguiente paso

Ejecutar `docs/measurement_plan.md`. Con **12 medidas** arranca FASE 4; la
sesión de medición durante un lote real (bloques PRO y PAR) es la que más vale.
