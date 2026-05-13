#!/usr/bin/env python3
"""
Vectra C Auto Lights — KiCad 10 Schematic Generator
Generates: vectra-auto-lights.kicad_sch

Usage:
    cd hardware/kicad
    python3 generate_kicad.py
    # → отвори vectra-auto-lights.kicad_sch в KiCad 10

Схемата използва net labels за всички връзки.
След отваряне в KiCad: свържи всеки пин с nearby label (5-10 мин работа).
"""

import uuid
import os

OUT = os.path.join(os.path.dirname(__file__), "vectra-auto-lights.kicad_sch")

# ── Helpers ───────────────────────────────────────────────────────────

def uid():
    return str(uuid.uuid4())

def prop(name, val, x=0, y=0, rot=0, hide=False):
    h = " hide" if hide else ""
    return (f'    (property "{name}" "{val}" (at {x:.4f} {y:.4f} {rot})\n'
            f'      (effects (font (size 1.27 1.27)){h})\n'
            f'    )')

def label(net, x, y, rot=0):
    return (f'  (label "{net}" (at {x:.4f} {y:.4f} {rot})\n'
            f'    (effects (font (size 1.27 1.27)) (justify left))\n'
            f'    (uuid "{uid()}")\n'
            f'  )')

def wire(x1, y1, x2, y2):
    return (f'  (wire (pts (xy {x1:.4f} {y1:.4f}) (xy {x2:.4f} {y2:.4f}))\n'
            f'    (stroke (width 0) (type default))\n'
            f'    (uuid "{uid()}")\n'
            f'  )')

def no_connect(x, y):
    return f'  (no_connect (at {x:.4f} {y:.4f}) (uuid "{uid()}"))'

def power_symbol(name, x, y):
    """Power rail symbol (+12V, +5V, GND)"""
    return (f'  (symbol (lib_id "power:{name}") (at {x:.4f} {y:.4f} 0) (unit 1)\n'
            f'    (exclude_from_sim no) (in_bom yes) (on_board yes)\n'
            f'    (uuid "{uid()}")\n'
            f'{prop("Reference", f"#{name}", x, y-2.54, 0, True)}\n'
            f'{prop("Value", name, x, y+2.54, 0)}\n'
            f'    (pin "1" (uuid "{uid()}"))\n'
            f'  )')

# ── Component factory ─────────────────────────────────────────────────

class Comp:
    """Builds a KiCad symbol instance."""
    def __init__(self, lib_id, ref, value, x, y, rot=0, footprint="", datasheet="~"):
        self.lib_id    = lib_id
        self.ref       = ref
        self.value     = value
        self.x         = x
        self.y         = y
        self.rot       = rot
        self.footprint = footprint
        self.datasheet = datasheet
        self.pins      = {}   # name → (dx, dy)  offsets relative to component center
        self.labels    = []   # (net, dx, dy) for auto-labels

    def pin_label(self, net, dx, dy):
        """Add a net label near a pin."""
        self.labels.append((net, dx, dy))
        return self

    def render(self):
        lines = [
            f'  (symbol (lib_id "{self.lib_id}") (at {self.x:.4f} {self.y:.4f} {self.rot}) (unit 1)',
            f'    (exclude_from_sim no) (in_bom yes) (on_board yes)',
            f'    (uuid "{uid()}")',
            prop("Reference", self.ref,    self.x+1,   self.y-2.54, 0),
            prop("Value",     self.value,  self.x+1,   self.y+2.54, 0),
            prop("Footprint", self.footprint, self.x, self.y, 0, True),
            prop("Datasheet", self.datasheet, self.x, self.y, 0, True),
        ]
        # Generic pin UUIDs (1..8)
        for i in range(1, 9):
            lines.append(f'    (pin "{i}" (uuid "{uid()}"))')
        lines.append('  )')
        # Net labels near pins
        for (net, dx, dy) in self.labels:
            lines.append(label(net, self.x + dx, self.y + dy))
        return "\n".join(lines)


# ── Net definitions ───────────────────────────────────────────────────
# Naming convention:
#   PWR_12V, PWR_5V, GND      — power rails
#   KL18_RAW, AUTO_RAW        — 12V raw car signals (before optocouplers)
#   UNLOCK_RAW                — 12V unlock pulse
#   ACC_GPIO, AUTO_GPIO       — 3.3V signals to ESP32 (after optocouplers)
#   UNLOCK_GPIO               — 3.3V unlock to ESP32
#   VBAT_ADC                  — voltage divider output to ESP32 ADC
#   GPIO13..GPIO35            — ESP32 GPIO outputs/inputs
#   XENON_GATE                — 2N7000 drain / IRF4905 gate
#   XENON_SW                  — IRF4905 drain (our xenon output, before diode)
#   BCM_XENON                 — BCM xenon output (before diode)
#   XENON_BALLAST             — final +12V to xenon ballast
#   GABARI_SW                 — relay K1 NO contact
#   BCM_GABARI                — BCM gabari output
#   GABARI_WIRE               — final gabari output to car
#   FOG_SW                    — relay K2 NO contact
#   BCM_FOG                   — BCM fog output
#   FOG_WIRE                  — final fog output to car
#   ILLUM_SW                  — our illumination transistor output
#   BCM_ILLUM                 — BCM illumination output
#   ILLUM_WIRE                — final illumination to radio
#   XENON_PWR                 — +12V fused 15A (xenon power)
#   RELAY_PWR                 — +12V fused 5A (relay power)
#   RELAY_K1_COIL_N           — K1 coil negative (collector Q3)
#   RELAY_K2_COIL_N           — K2 coil negative (collector Q4)


# ── Build component list ──────────────────────────────────────────────

components = []

# ═══════════════════════════════════════════════════════════════════════
# БЛОК A — ЗАХРАНВАНЕ  (x: 15-110, y: 15-55)
# ═══════════════════════════════════════════════════════════════════════

# J1 — КL30 + GND вход (2-pin)
j1 = Comp("Connector:Conn_01x02_Pin", "J1", "KL30+GND", 18, 28,
           footprint="Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical")
j1.pin_label("PWR_12V",  5,  -2.54)
j1.pin_label("GND",      5,   2.54)
components.append(j1)

# F1 — предпазител 1A (MCU)
f1 = Comp("Device:Fuse", "F1", "1A", 38, 20,
          footprint="Fuse:Fuseholder_Littelfuse_64900001039_1x1_P5.08mm_Vertical")
f1.pin_label("PWR_12V",  -5,  0)
f1.pin_label("PWR_12V_1A", 5,  0)
components.append(f1)

# F2 — предпазител 15A (ксенон)
f2 = Comp("Device:Fuse", "F2", "15A", 38, 30,
          footprint="Fuse:Fuseholder_Littelfuse_64900001039_1x1_P5.08mm_Vertical")
f2.pin_label("PWR_12V",    -5, 0)
f2.pin_label("XENON_PWR",   5, 0)
components.append(f2)

# F3 — предпазител 5A (релета)
f3 = Comp("Device:Fuse", "F3", "5A", 38, 40,
          footprint="Fuse:Fuseholder_Littelfuse_64900001039_1x1_P5.08mm_Vertical")
f3.pin_label("PWR_12V",  -5, 0)
f3.pin_label("RELAY_PWR", 5, 0)
components.append(f3)

# D1 — 1N4007 реверсна защита
d1 = Comp("Device:D", "D1", "1N4007", 62, 20,
          footprint="Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal")
d1.pin_label("PWR_12V_1A", -5, 0)
d1.pin_label("PWR_12V_PROT", 5, 0)
components.append(d1)

# D12 — TVS P6KE15A
d12 = Comp("Device:TVS", "D12", "P6KE15A", 62, 32,
           footprint="Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal")
d12.pin_label("PWR_12V_PROT", -5, 0)
d12.pin_label("GND",           5, 0)
components.append(d12)

# U2 — LM7805
u2 = Comp("Regulator_Linear:LM7805", "U2", "LM7805", 85, 25,
          footprint="Package_TO_SOT_THT:TO-220-3_Vertical")
u2.pin_label("PWR_12V_PROT", -7.62, 0)
u2.pin_label("GND",           0,    7.62)
u2.pin_label("PWR_5V",        7.62, 0)
components.append(u2)

# C1 — 100µF
c1 = Comp("Device:C", "C1", "100uF/25V", 105, 20,
          footprint="Capacitor_THT:C_Radial_D8.0mm_H11.5mm_P3.50mm")
c1.pin_label("PWR_5V", 0, -5)
c1.pin_label("GND",    0,  5)
components.append(c1)

# C2 — 100nF
c2 = Comp("Device:C", "C2", "100nF", 113, 20,
          footprint="Capacitor_THT:C_Disc_D3.8mm_W2.6mm_P2.50mm")
c2.pin_label("PWR_5V", 0, -5)
c2.pin_label("GND",    0,  5)
components.append(c2)

# ═══════════════════════════════════════════════════════════════════════
# БЛОК B — VOLTAGE DIVIDER  (x: 15-55, y: 65-105)
# ═══════════════════════════════════════════════════════════════════════

# R1 — 47kΩ (горе)
r1 = Comp("Device:R", "R1", "47k", 30, 72, rot=0,
          footprint="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal")
r1.pin_label("XENON_PWR",  0, -5)   # top → 12V (sense от F2 или акумулатор)
r1.pin_label("VBAT_ADC",   0,  5)   # bottom → to R2 junction
components.append(r1)

# R2 — 10kΩ (долу)
r2 = Comp("Device:R", "R2", "10k", 30, 87, rot=0,
          footprint="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal")
r2.pin_label("VBAT_ADC", 0, -5)   # top → to R1 junction
r2.pin_label("GND",       0,  5)  # bottom → GND
components.append(r2)

# ═══════════════════════════════════════════════════════════════════════
# БЛОК C — ОПТРОНИ  (x: 25-95, y: 110-185)
# ═══════════════════════════════════════════════════════════════════════

opto_data = [
    # (ref, y, net_anode_resistor, net_input, net_output, gpio_net)
    ("OK1", 118, "KL18_RAW",   "ACC_LED_K",   "ACC_GPIO",    "GPIO35"),
    ("OK2", 143, "AUTO_RAW",   "AUTO_LED_K",  "AUTO_GPIO",   "GPIO32"),
    ("OK3", 168, "UNLOCK_RAW", "UNLOCK_LED_K","UNLOCK_GPIO", "GPIO33"),
]

for i, (ref, y, net_in, led_k, out_net, gpio) in enumerate(opto_data):
    ri = i + 3  # R3, R5, R7
    rp = i * 2 + 4  # R4, R6, R8

    # Input resistor (4.7kΩ)
    rx = Comp("Device:R", f"R{ri*2-3}", "4k7", 35, y, rot=0,
              footprint="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal")
    rx.pin_label(net_in,  0, -5)
    rx.pin_label(led_k,   0,  5)
    components.append(rx)

    # PC817 optocoupler
    ok = Comp("Isolator:PC817", ref, "PC817", 58, y,
              footprint="Package_DIP:DIP-4_W7.62mm")
    ok.pin_label(led_k,  -7.62, -2.54)  # Anode
    ok.pin_label("GND",  -7.62,  2.54)  # Cathode
    ok.pin_label("PWR_3V3", 7.62, -2.54)  # Collector (via pullup)
    ok.pin_label(out_net, 7.62,  2.54)  # Emitter
    components.append(ok)

    # Pull-up resistor (10kΩ) — collector to 3.3V
    rpu = Comp("Device:R", f"R{rp}", "10k", 82, y - 5, rot=0,
               footprint="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal")
    rpu.pin_label("PWR_3V3", 0, -5)
    rpu.pin_label(out_net,   0,  5)
    components.append(rpu)

# Car input connector J2 (5-pin: KL18, AUTO, UNLOCK, GND, +12V)
j2 = Comp("Connector:Conn_01x05_Pin", "J2", "CAR_INPUTS", 18, 145,
          footprint="Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical")
j2.pin_label("KL18_RAW",   5, -5.08)
j2.pin_label("AUTO_RAW",   5, -2.54)
j2.pin_label("UNLOCK_RAW", 5,  0)
j2.pin_label("PWR_12V",    5,  2.54)
j2.pin_label("GND",        5,  5.08)
components.append(j2)

# ═══════════════════════════════════════════════════════════════════════
# БЛОК D — ESP32  (x: 110-215, y: 50-230)
# ═══════════════════════════════════════════════════════════════════════

esp = Comp("MCU_Module:ESP32_DevKitC_V4", "U1", "ESP32_DevKit_v1", 163, 140,
           footprint="Module:ESP32_DevKitC_v4")
# Outputs
esp.pin_label("GPIO26",   -30,  -55)   # Xenon MOSFET drive
esp.pin_label("GPIO27",   -30,  -50)   # Gabari relay
esp.pin_label("GPIO14",   -30,  -45)   # Fog relay
esp.pin_label("GPIO13",   -30,  -40)   # Illumination
# Inputs
esp.pin_label("GPIO34",    30,  -55)   # VBAT ADC
esp.pin_label("GPIO35",    30,  -50)   # ACC optocoupler
esp.pin_label("GPIO32",    30,  -45)   # AUTO optocoupler
esp.pin_label("GPIO33",    30,  -40)   # UNLOCK optocoupler (interrupt)
# Power
esp.pin_label("PWR_5V",   -30,   60)
esp.pin_label("GND",      -30,   65)
components.append(esp)

# 3.3V power label (ESP32 internal regulator output)
# PWR_3V3 is referenced by optocoupler pull-ups but sourced from ESP32 3V3 pin

# ═══════════════════════════════════════════════════════════════════════
# БЛОК E — КСЕНОН ИЗХОД  (x: 225-340, y: 20-70)
# ═══════════════════════════════════════════════════════════════════════

# R10 — 1kΩ, 2N7000 gate
r10 = Comp("Device:R", "R10", "1k", 230, 35, rot=0,
           footprint="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal")
r10.pin_label("GPIO26",     0, -5)
r10.pin_label("Q2_GATE",    0,  5)
components.append(r10)

# Q2 — 2N7000 (N-FET, IRF4905 gate driver)
q2 = Comp("Transistor_FET:2N7000", "Q2", "2N7000", 248, 35,
          footprint="Package_TO_SOT_THT:TO-92_Inline")
q2.pin_label("Q2_GATE",   -5,  2.54)   # Gate
q2.pin_label("XENON_GATE", 5, -2.54)   # Drain → IRF4905 gate
q2.pin_label("GND",        5,  2.54)   # Source
components.append(q2)

# R9 — 10kΩ, IRF4905 gate pull-up to 12V
r9 = Comp("Device:R", "R9", "10k", 265, 25, rot=0,
          footprint="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal")
r9.pin_label("XENON_PWR",  0, -5)
r9.pin_label("XENON_GATE", 0,  5)
components.append(r9)

# Q1 — IRF4905 (P-MOSFET, high-side xenon switch)
q1 = Comp("Transistor_FET:IRF4905", "Q1", "IRF4905", 283, 35,
          footprint="Package_TO_SOT_THT:TO-220-3_Vertical")
q1.pin_label("XENON_GATE", -5,  0)     # Gate
q1.pin_label("XENON_PWR",   0, -5.08)  # Source → fused 15A
q1.pin_label("XENON_SW",    5,  0)     # Drain → to D2
components.append(q1)

# D2 — 1N5408, our xenon decoupling diode (anode → XENON_SW, cathode → XENON_BALLAST)
d2 = Comp("Device:D", "D2", "1N5408", 305, 25,
          footprint="Diode_THT:D_DO-201AD_P15.24mm_Horizontal")
d2.pin_label("XENON_SW",       -5, 0)
d2.pin_label("XENON_BALLAST",   5, 0)
components.append(d2)

# D3 — 1N5408, BCM xenon decoupling diode (anode → BCM_XENON, cathode → XENON_BALLAST)
d3 = Comp("Device:D", "D3", "1N5408", 305, 38,
          footprint="Diode_THT:D_DO-201AD_P15.24mm_Horizontal")
d3.pin_label("BCM_XENON",     -5, 0)
d3.pin_label("XENON_BALLAST",  5, 0)
components.append(d3)

# J3 — ксенон конектори (3-pin: наш изход, BCM изход, кола)
j3 = Comp("Connector:Conn_01x03_Pin", "J3", "J_XENON", 330, 30,
          footprint="Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical")
j3.pin_label("XENON_BALLAST",  -5,  -2.54)
j3.pin_label("BCM_XENON",      -5,   0)
j3.pin_label("GND",            -5,   2.54)
components.append(j3)

# ═══════════════════════════════════════════════════════════════════════
# БЛОК F — ГАБАРИТИ РЕЛЕ  (x: 225-340, y: 80-120)
# ═══════════════════════════════════════════════════════════════════════

# R11 — 1kΩ, BC547 base (gabari)
r11 = Comp("Device:R", "R11", "1k", 230, 92, rot=0,
           footprint="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal")
r11.pin_label("GPIO27",      0, -5)
r11.pin_label("Q3_BASE",     0,  5)
components.append(r11)

# Q3 — BC547 (gabari relay driver)
q3 = Comp("Transistor_BJT:BC547", "Q3", "BC547", 248, 92,
          footprint="Package_TO_SOT_THT:TO-92_Inline")
q3.pin_label("Q3_BASE",           -5,  0)
q3.pin_label("RELAY_K1_COIL_N",    0, -5)
q3.pin_label("GND",                0,  5)
components.append(q3)

# K1 — реле габарити (SPDT 12V)
k1 = Comp("Relay:G5V-1", "K1", "Relay_12V", 270, 90,
          footprint="Relay_THT:Relay_SPDT_Omron_G5V-1")
k1.pin_label("RELAY_PWR",        -8, -5)  # Coil +
k1.pin_label("RELAY_K1_COIL_N",  -8,  5)  # Coil -
k1.pin_label("RELAY_PWR",         8, -5)  # NO → 12V за габарити
k1.pin_label("GABARI_SW",         8,  0)  # COM → our output
k1.pin_label("GND",               8,  5)  # NC → GND
components.append(k1)

# D8 — flyback диод K1
d8 = Comp("Device:D", "D8", "1N4007", 270, 107,
          footprint="Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal")
d8.pin_label("RELAY_K1_COIL_N", -5, 0)
d8.pin_label("RELAY_PWR",        5, 0)
components.append(d8)

# D4 — decoupling наш изход (anode → GABARI_SW, cathode → GABARI_WIRE)
d4 = Comp("Device:D", "D4", "1N4007", 305, 83,
          footprint="Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal")
d4.pin_label("GABARI_SW",   -5, 0)
d4.pin_label("GABARI_WIRE",  5, 0)
components.append(d4)

# D5 — decoupling BCM изход
d5 = Comp("Device:D", "D5", "1N4007", 305, 95,
          footprint="Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal")
d5.pin_label("BCM_GABARI",  -5, 0)
d5.pin_label("GABARI_WIRE",  5, 0)
components.append(d5)

# J4 — габарити конектор
j4 = Comp("Connector:Conn_01x03_Pin", "J4", "J_GABARI", 330, 90,
          footprint="Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical")
j4.pin_label("GABARI_WIRE", -5, -2.54)
j4.pin_label("BCM_GABARI",  -5,  0)
j4.pin_label("GND",         -5,  2.54)
components.append(j4)

# ═══════════════════════════════════════════════════════════════════════
# БЛОК G — МЪГЛА РЕЛЕ  (x: 225-340, y: 125-165)
# ═══════════════════════════════════════════════════════════════════════

r12 = Comp("Device:R", "R12", "1k", 230, 132, rot=0,
           footprint="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal")
r12.pin_label("GPIO14",   0, -5)
r12.pin_label("Q4_BASE",  0,  5)
components.append(r12)

q4 = Comp("Transistor_BJT:BC547", "Q4", "BC547", 248, 132,
          footprint="Package_TO_SOT_THT:TO-92_Inline")
q4.pin_label("Q4_BASE",           -5,  0)
q4.pin_label("RELAY_K2_COIL_N",    0, -5)
q4.pin_label("GND",                0,  5)
components.append(q4)

k2 = Comp("Relay:G5V-1", "K2", "Relay_12V", 270, 130,
          footprint="Relay_THT:Relay_SPDT_Omron_G5V-1")
k2.pin_label("RELAY_PWR",        -8, -5)
k2.pin_label("RELAY_K2_COIL_N",  -8,  5)
k2.pin_label("RELAY_PWR",         8, -5)
k2.pin_label("FOG_SW",            8,  0)
k2.pin_label("GND",               8,  5)
components.append(k2)

d9 = Comp("Device:D", "D9", "1N4007", 270, 147,
          footprint="Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal")
d9.pin_label("RELAY_K2_COIL_N", -5, 0)
d9.pin_label("RELAY_PWR",        5, 0)
components.append(d9)

d6 = Comp("Device:D", "D6", "1N4007", 305, 123,
          footprint="Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal")
d6.pin_label("FOG_SW",    -5, 0)
d6.pin_label("FOG_WIRE",   5, 0)
components.append(d6)

d7 = Comp("Device:D", "D7", "1N4007", 305, 135,
          footprint="Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal")
d7.pin_label("BCM_FOG",  -5, 0)
d7.pin_label("FOG_WIRE",  5, 0)
components.append(d7)

j5 = Comp("Connector:Conn_01x03_Pin", "J5", "J_FOG", 330, 130,
          footprint="Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical")
j5.pin_label("FOG_WIRE",  -5, -2.54)
j5.pin_label("BCM_FOG",   -5,  0)
j5.pin_label("GND",       -5,  2.54)
components.append(j5)

# ═══════════════════════════════════════════════════════════════════════
# БЛОК H — ILLUMINATION  (x: 225-340, y: 170-200)
# ═══════════════════════════════════════════════════════════════════════

r13 = Comp("Device:R", "R13", "1k", 230, 175, rot=0,
           footprint="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal")
r13.pin_label("GPIO13",   0, -5)
r13.pin_label("Q5_BASE",  0,  5)
components.append(r13)

q5 = Comp("Transistor_BJT:BC547", "Q5", "BC547", 248, 175,
          footprint="Package_TO_SOT_THT:TO-92_Inline")
q5.pin_label("Q5_BASE",   -5,  0)
q5.pin_label("ILLUM_SW",   0, -5)
q5.pin_label("GND",        0,  5)
components.append(q5)

# D10 — decoupling наш illumination изход
d10 = Comp("Device:D", "D10", "1N4007", 305, 168,
           footprint="Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal")
d10.pin_label("ILLUM_SW",    -5, 0)
d10.pin_label("ILLUM_WIRE",   5, 0)
components.append(d10)

# D11 — decoupling BCM illumination изход
d11 = Comp("Device:D", "D11", "1N4007", 305, 180,
           footprint="Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal")
d11.pin_label("BCM_ILLUM",  -5, 0)
d11.pin_label("ILLUM_WIRE",  5, 0)
components.append(d11)

j6 = Comp("Connector:Conn_01x03_Pin", "J6", "J_ILLUM", 330, 175,
          footprint="Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical")
j6.pin_label("ILLUM_WIRE", -5, -2.54)
j6.pin_label("BCM_ILLUM",  -5,  0)
j6.pin_label("GND",        -5,  2.54)
components.append(j6)

# ── Power symbols (GND и +12V навсякъде) ─────────────────────────────

pwr_syms = [
    ("GND",  18,  36),
    ("GND",  85,  35),
    ("GND", 105,  30),
    ("GND", 113,  30),
    ("GND",  30, 100),
    ("GND", 163, 210),
    ("GND", 248,  45),
    ("GND", 248, 102),
    ("GND", 248, 142),
    ("GND", 248, 185),
    ("+12V", 18,  20),
    ("+12V", 85,  17),
    ("+12V", 163, 55),
]

# ── Generate schematic ────────────────────────────────────────────────

def generate():
    lines = []
    lines.append("(kicad_sch")
    lines.append("  (version 20231120)")
    lines.append('  (generator "vectra_generate_kicad")')
    lines.append('  (generator_version "1.0")')
    lines.append('  (paper "A3")')
    lines.append("  (title_block")
    lines.append('    (title "Vectra C Auto Lights Controller")')
    lines.append('    (date "2026-05-07")')
    lines.append('    (rev "1.0")')
    lines.append('    (company "kkuninski-ops/vectra-c-auto-lights")')
    lines.append('    (comment 1 "MCU: ESP32 DevKit v1 — BLE via Nordic UART Service")')
    lines.append('    (comment 2 "Target: Opel Vectra C 2008 — D1S xenon")')
    lines.append("  )")
    lines.append("")
    lines.append("  (lib_symbols)")
    lines.append("")

    # Components
    for comp in components:
        lines.append(comp.render())
        lines.append("")

    # Power symbols
    for (name, x, y) in pwr_syms:
        lines.append(power_symbol(name, x, y))
        lines.append("")

    lines.append(")")
    return "\n".join(lines)

if __name__ == "__main__":
    content = generate()
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✓ Generated: {OUT}")
    print("  → Отвори в KiCad 10")
    print("  → Symbols → Update Symbols from Library")
    print("  → Свържи всеки пин с близкия net label")
