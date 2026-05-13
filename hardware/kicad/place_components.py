"""
Vectra C Auto Lights — PCB Component Placer
============================================
Пусни в KiCad 10 Scripting Console:

  exec(open('/Users/kaloyank/Documents/vectra-c-auto-lights/hardware/kicad/place_components.py').read())

Или от PCB Editor: Tools → Scripting Console → paste горния ред → Enter
"""

import pcbnew
import os

board = pcbnew.GetBoard()

# ─── KiCad footprint libraries (macOS KiCad 10) ──────────────────────────────
FP_BASE = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/"

def mm(v):
    return pcbnew.FromMM(v)

def add(lib, fp_name, ref, value, x, y, rot=0):
    """Load footprint from library and place it on the board."""
    path = os.path.join(FP_BASE, lib + ".pretty")
    fp = pcbnew.FootprintLoad(path, fp_name)
    if not fp:
        print(f"  ⚠ MISSING: {lib}:{fp_name}  ({ref})")
        return None
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    if rot:
        fp.SetOrientationDegrees(rot)
    board.Add(fp)
    print(f"  ✓ {ref:5s} {value:20s}  ({lib}:{fp_name})")
    return fp

# ─── Footprint shortcuts ──────────────────────────────────────────────────────
R_LIB   = "Resistor_THT"
R_FP    = "R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal"

D_LIB   = "Diode_THT"
D41_FP  = "D_DO-41_SOD81_P10.16mm_Horizontal"
D201_FP = "D_DO-201AD_P12.70mm_Horizontal"

TO_LIB  = "Package_TO_SOT_THT"
TO92_FP = "TO-92_Inline"
TO220FP = "TO-220-3_Vertical"

DIP_LIB = "Package_DIP"
DIP4_FP = "DIP-4_W7.62mm"

CAP_LIB = "Capacitor_THT"
CP_FP   = "CP_Radial_D8.0mm_P3.50mm"
C_FP    = "C_Disc_D5.0mm_W2.5mm_P2.50mm"

REL_LIB = "Relay_THT"
REL_FP  = "Relay_SPDT_SANYOU_SRD_Series_RM5"

CON_LIB = "Connector_PinHeader_2.54mm"
FUS_LIB = "Fuse"
MOD_LIB = "Module"
MH_LIB  = "MountingHole"

print("\n── Vectra C Auto Lights — placing components ──────────────────────────")

# ═══════════════════════════════════════════════════════════════════════════════
# КОНЕКТОРИ (ляв ръб, x=5)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Connectors]")
add(CON_LIB, "PinHeader_1x02_P2.54mm_Vertical", "J1", "KL30+GND",    5,  8)
add(CON_LIB, "PinHeader_1x04_P2.54mm_Vertical", "J2", "CAR_INPUTS",  5, 22)
add(CON_LIB, "PinHeader_1x03_P2.54mm_Vertical", "J3", "J_XENON",     5, 36)
add(CON_LIB, "PinHeader_1x03_P2.54mm_Vertical", "J4", "J_GABARI",    5, 46)
add(CON_LIB, "PinHeader_1x03_P2.54mm_Vertical", "J5", "J_FOG",       5, 56)
add(CON_LIB, "PinHeader_1x03_P2.54mm_Vertical", "J6", "J_ILLUM",     5, 66)

# ═══════════════════════════════════════════════════════════════════════════════
# ЗАХРАНВАНЕ (горе-ляво, x=20-60, y=5-22)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Power]")
add(FUS_LIB, "Fuseholder_Cylinder_5x20mm_Schurter_0031_8201_Horizontal_Open", "F1", "1A",   22,  7)
add(FUS_LIB, "Fuseholder_Cylinder_5x20mm_Schurter_0031_8201_Horizontal_Open", "F2", "15A",  22, 13)
add(FUS_LIB, "Fuseholder_Cylinder_5x20mm_Schurter_0031_8201_Horizontal_Open", "F3", "5A",   22, 19)
add(D_LIB,   D41_FP,  "D1",  "1N4007",    36,  7)
add(D_LIB,   D201_FP, "D12", "P6KE15A",   36, 13)
add(TO_LIB,  TO220FP, "U2",  "LM7805",    48, 11)
add(CAP_LIB, CP_FP,   "C1",  "100uF/25V", 58,  7)
add(CAP_LIB, C_FP,    "C2",  "100nF",     58, 13)

# ═══════════════════════════════════════════════════════════════════════════════
# VBAT ДЕЛИТЕЛ (x=22, y=28-40)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Vbat divider]")
add(R_LIB, R_FP, "R1", "47k", 22, 30)
add(R_LIB, R_FP, "R2", "10k", 22, 39)

# ═══════════════════════════════════════════════════════════════════════════════
# ОПТРОНИ OK1/OK2/OK3 (x=28-56, y=48-70)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Optocouplers]")
opto_rows = [
    ("R3", "OK1", "R4", 48),
    ("R5", "OK2", "R6", 59),
    ("R7", "OK3", "R8", 70),
]
for r_in, ok_ref, r_pu, y in opto_rows:
    add(R_LIB, R_FP,   r_in,  "4k7",  30, y)
    add(DIP_LIB, DIP4_FP, ok_ref, "PC817", 43, y)
    add(R_LIB, R_FP,   r_pu, "10k",  56, y)

# ═══════════════════════════════════════════════════════════════════════════════
# ESP32 DevKit (център, x=72, y=40)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[ESP32]")
add(MOD_LIB, "ESP32_DevKitC_v4", "U1", "ESP32_DevKit_v1", 72, 40)

# ═══════════════════════════════════════════════════════════════════════════════
# ILLUMINATION (x=63-75, y=5-25)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Illumination]")
add(R_LIB, R_FP,  "R13", "1k",     63,  7)
add(TO_LIB, TO92_FP, "Q5", "BC547",    70,  7)
add(D_LIB, D41_FP, "D10", "1N4007",   63, 14)
add(D_LIB, D41_FP, "D11", "1N4007",   63, 21)

# ═══════════════════════════════════════════════════════════════════════════════
# КСЕНОН MOSFET (горе-дясно, x=93-116, y=5-30)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Xenon MOSFET]")
add(R_LIB,  R_FP,   "R10", "1k",      93,  7)
add(TO_LIB, TO92_FP,"Q2",  "2N7000",  100,  7)
add(R_LIB,  R_FP,   "R9",  "10k",     108,  7)
add(TO_LIB, TO220FP,"Q1",  "IRF4905", 114, 13)
add(D_LIB,  D201_FP,"D2",  "1N5408",   93, 18)
add(D_LIB,  D201_FP,"D3",  "1N5408",   93, 25)

# ═══════════════════════════════════════════════════════════════════════════════
# РЕЛЕ K1 — ГАБАРИТИ (x=88-116, y=38-56)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Relay K1 - Gabari]")
add(R_LIB,   R_FP,  "R11", "1k",       88, 40)
add(TO_LIB, TO92_FP,"Q3",  "BC547",    95, 40)
add(REL_LIB, REL_FP,"K1",  "Relay_12V",106, 46)
add(D_LIB,   D41_FP,"D8",  "1N4007",   88, 49)
add(D_LIB,   D41_FP,"D4",  "1N4007",   96, 52)
add(D_LIB,   D41_FP,"D5",  "1N4007",  108, 52)

# ═══════════════════════════════════════════════════════════════════════════════
# РЕЛЕ K2 — МЪГЛА (x=88-116, y=58-76)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[Relay K2 - Fog]")
add(R_LIB,   R_FP,  "R12", "1k",       88, 58)
add(TO_LIB, TO92_FP,"Q4",  "BC547",    95, 58)
add(REL_LIB, REL_FP,"K2",  "Relay_12V",106, 64)
add(D_LIB,   D41_FP,"D9",  "1N4007",   88, 67)
add(D_LIB,   D41_FP,"D6",  "1N4007",   96, 70)
add(D_LIB,   D41_FP,"D7",  "1N4007",  108, 70)

# ═══════════════════════════════════════════════════════════════════════════════
# REFRESH
# ═══════════════════════════════════════════════════════════════════════════════
pcbnew.Refresh()
print("\n✓ Всички компоненти добавени!")
print("  → Запиши: Cmd+S")
print("  → После: Route → Interactive Router за trace-овете")
