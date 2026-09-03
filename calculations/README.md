# Módulos de cálculo — FASE 4

**Vacío a propósito.** Los cálculos no arrancan hasta tener las mediciones.

Ejecutar `python3 config/check_parameters.py` para ver si ya se puede empezar.

## Módulos previstos

| Módulo | Calcula | Requiere |
|---|---|---|
| `motor.py` | Par y potencia requeridos vs. disponibles | `PAR-03`/`PAR-06`, `MOT-01`, `TRA-02` |
| `transmission.py` | Relación, rendimiento, factor de servicio | `TRA-01`, `TRA-02` |
| `agitator.py` | Tipo, geometría, patrón de flujo, régimen | `OLL-01`, `OLL-07`, `PRO-08` |
| `shaft.py` | Torsión, flexión, esfuerzo combinado, deflexión, velocidad crítica | `EJE-01`, `EJE-02`, `PAR-*` |
| `bearings.py` | Cargas, vida L10, selección comercial | `TRA-04`, `PAR-*` |
| `structure.py` | Cargas, esfuerzos, deformación del bastidor | `BAS-01`…`BAS-08`, `MAS-*` |
| `safety.py` | Guardas, estabilidad, riesgos | Transversal |
| `optimization.py` | Barrido RPM / par / Ø agitador / Ø eje | Todos |

## Reglas para todos los módulos

1. Leen de `config/design_parameters.yaml`. **Ningún número dentro del código.**
2. SI internamente; se muestra en unidades prácticas.
3. Todo resultado indica unidad y factor de seguridad.
4. Marcan explícitamente lo que **no cumple**.
5. Propagan la procedencia: un resultado que dependa de un `SUPUESTO` se
   etiqueta como tal. **No se presenta un cálculo sobre supuestos como si fuera
   un dato firme.**
6. Reejecutables al cambiar parámetros.
