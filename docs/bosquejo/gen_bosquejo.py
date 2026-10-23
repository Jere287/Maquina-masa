# -*- coding: utf-8 -*-
import math, os

SP = "/tmp/claude-0/-home-user-Maquina-masa/c0272a51-3f26-55d1-b4ab-cd2c1175da8e/scratchpad"
cx = 250.0

# --- helice de la cinta en corte: dos hebras sinusoidales ---
y0, y1 = 212.0, 534.0
A, turns = 63.0, 2.25
def hebra(fase):
    pts = []
    n = 90
    for i in range(n + 1):
        t = i / n
        y = y0 + (y1 - y0) * t
        x = cx + A * math.sin(2 * math.pi * turns * t + fase)
        pts.append((x, y))
    return "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
hebra_a = hebra(0.0)
hebra_b = hebra(math.pi)

def flecha_v(x, ya, yb, color, w=7):
    # cuerpo + cabeza; yb es la punta
    head = 11
    dir_up = yb < ya
    yc = yb + (head if dir_up else -head)
    cuerpo = f'<line x1="{x}" y1="{ya}" x2="{x}" y2="{yc}" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>'
    if dir_up:
        tri = f'{x},{yb} {x-head*0.8},{yb+head} {x+head*0.8},{yb+head}'
    else:
        tri = f'{x},{yb} {x-head*0.8},{yb-head} {x+head*0.8},{yb-head}'
    return cuerpo + f'<polygon points="{tri}" fill="{color}"/>'

def flecha_h(ya, xa, xb, color, w=6):
    head = 10
    dir_left = xb < xa
    xc = xb + (head if dir_left else -head)
    cuerpo = f'<line x1="{xa}" y1="{ya}" x2="{xc}" y2="{ya}" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>'
    if dir_left:
        tri = f'{xb},{ya} {xb+head},{ya-head*0.8} {xb+head},{ya+head*0.8}'
    else:
        tri = f'{xb},{ya} {xb-head},{ya-head*0.8} {xb-head},{ya+head*0.8}'
    return cuerpo + f'<polygon points="{tri}" fill="{color}"/>'

# flujo de masa (verde): sube por la pared izquierda, baja por el centro
flujo = flecha_v(cx-50, 520, 372, "var(--flujo)")
flujo += flecha_v(cx+26, 372, 520, "var(--flujo)")
# calor (rojo) entrando del agua a la olla, lado derecho
calor = ""
for yy in (350, 430, 500):
    calor += flecha_h(yy, cx+96, cx+80, "var(--calor)", 5)
# calor del quemador hacia arriba al fondo de la camisa
calor += flecha_v(cx-30, 596, 556, "var(--calor)", 5)
calor += flecha_v(cx+30, 596, 556, "var(--calor)", 5)

def callout(n, x, y, tx, ty):
    # circulo numerado + linea guia a (tx,ty)
    return (f'<line x1="{x}" y1="{y}" x2="{tx}" y2="{ty}" stroke="var(--line-2)" stroke-width="1"/>'
            f'<circle cx="{x}" cy="{y}" r="12" fill="var(--panel)" stroke="var(--ink)" stroke-width="1.4"/>'
            f'<text x="{x}" y="{y+4}" text-anchor="middle" class="co">{n}</text>')

callouts = ""
callouts += callout(1, 470, 95, cx+40, 110)      # motor
callouts += callout(2, 470, 150, cx+118, 196)    # collar
callouts += callout(3, 470, 205, cx+86, 248)     # boca carga
callouts += callout(4, 30, 150, cx-7, 230)       # eje
callouts += callout(5, 30, 300, cx-55, 320)      # cinta
callouts += callout(6, 30, 360, cx-74, 430)      # raspadores
callouts += callout(7, 470, 360, cx+97, 400)     # olla+camisa
callouts += callout(8, 30, 470, cx-40, 480)      # masa
callouts += callout(9, 470, 470, cx+99, 250)     # topes antigiro
callouts += callout(10, 470, 575, cx+40, 585)    # quemador
callouts += callout(11, 30, 575, cx-120, 560)    # bastidor

# dimension vertical H interior (derecha) y Ø (abajo)
dim = f'''
<g class="dim">
  <line x1="520" y1="172" x2="520" y2="540"/>
  <line x1="514" y1="172" x2="526" y2="172"/>
  <line x1="514" y1="540" x2="526" y2="540"/>
  <text x="534" y="360" transform="rotate(90 534 360)" text-anchor="middle">650 mm int</text>
  <line x1="{cx-74}" y1="620" x2="{cx+74}" y2="620"/>
  <line x1="{cx-74}" y1="614" x2="{cx-74}" y2="626"/>
  <line x1="{cx+74}" y1="614" x2="{cx+74}" y2="626"/>
  <text x="{cx}" y="638" text-anchor="middle">Ø300 int · Ø328 c/camisa</text>
  <line x1="40" y1="110" x2="40" y2="858"/>
  <line x1="34" y1="110" x2="46" y2="110"/>
  <line x1="34" y1="858" x2="46" y2="858"/>
  <text x="26" y="480" transform="rotate(-90 26 480)" text-anchor="middle">~1 650 mm total</text>
</g>'''

svg = f'''<svg viewBox="0 0 580 900" class="plano" role="img" aria-label="Corte de la mezcladora">
  <!-- bastidor existente -->
  <g class="viejo">
    <rect x="{cx-150}" y="540" width="300" height="12" rx="2"/>
    <rect x="{cx-140}" y="552" width="16" height="300"/>
    <rect x="{cx+124}" y="552" width="16" height="300"/>
    <rect x="{cx-150}" y="792" width="300" height="12" rx="2"/>
  </g>
  <!-- camisa exterior + agua -->
  <rect x="{cx-99}" y="252" width="198" height="292" rx="4" class="steel"/>
  <rect x="{cx-95}" y="258" width="190" height="282" rx="3" class="agua"/>
  <!-- olla interior -->
  <path d="M {cx-74} 176 L {cx-74} 540 L {cx+74} 540 L {cx+74} 176" fill="none" class="steelw"/>
  <rect x="{cx-72}" y="360" width="144" height="180" class="masa"/>
  <!-- cinta helicoidal (dos hebras) -->
  <path d="{hebra_a}" class="cinta"/>
  <path d="{hebra_b}" class="cinta"/>
  <!-- eje -->
  <rect x="{cx-6}" y="150" width="12" height="372" class="steelf"/>
  <rect x="{cx-17}" y="214" width="34" height="26" rx="3" class="steelf"/>
  <!-- topes antigiro -->
  <rect x="{cx-103}" y="238" width="10" height="26" class="nuevo"/>
  <rect x="{cx+93}" y="238" width="10" height="26" class="nuevo"/>
  <!-- collar de par + plato + posts -->
  <g class="nuevo">
    <rect x="{cx-120}" y="238" width="240" height="16" rx="3"/>
    <rect x="{cx-120}" y="150" width="14" height="92"/>
    <rect x="{cx+106}" y="150" width="14" height="92"/>
    <rect x="{cx-120}" y="140" width="240" height="14" rx="3"/>
  </g>
  <!-- motorreductor -->
  <g class="motor">
    <rect x="{cx-46}" y="74" width="92" height="66" rx="4"/>
    <rect x="{cx+40}" y="88" width="54" height="38" rx="6"/>
  </g>
  <!-- boca de carga con tamiz -->
  <g class="nuevo">
    <rect x="{cx+60}" y="150" width="26" height="110" rx="4" transform="rotate(14 {cx+73} 205)"/>
  </g>
  <line x1="{cx+40}" y1="252" x2="{cx+86}" y2="252" stroke="var(--ink-3)" stroke-width="2" stroke-dasharray="3 3"/>
  <!-- quemador -->
  <g class="fuego">
    <ellipse cx="{cx}" cy="575" rx="86" ry="12"/>
    <path d="M {cx-60} 568 q 6 -16 12 0 q 6 -16 12 0" fill="none" stroke="var(--fuego)" stroke-width="3"/>
    <path d="M {cx+36} 568 q 6 -16 12 0 q 6 -16 12 0" fill="none" stroke="var(--fuego)" stroke-width="3"/>
    <line x1="{cx-86}" y1="575" x2="{cx-150}" y2="600" stroke="var(--fuego)" stroke-width="4"/>
  </g>
  <!-- piso -->
  <line x1="40" y1="858" x2="540" y2="858" stroke="var(--line-2)" stroke-width="2"/>
  {flujo}
  {calor}
  {dim}
  {callouts}
</svg>'''

open(os.path.join(SP, "_svg_plano.html"), "w", encoding="utf-8").write(svg)
print("svg generado", len(svg), "chars")
