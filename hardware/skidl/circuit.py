"""
Vectra C Auto Lights — SKiDL netlist
=====================================
Генерира KiCad-совместим нетлист от Python.

Изисква: pip install skidl
Употреба: python3 circuit.py
"""

from skidl import *

# ─── Библиотеки ─────────────────────────────────────────────────────────────
# Използваме KiCad стандартни библиотеки (Device, Connector_Generic и т.н.)

@package
def esp32_devkit():
    """ESP32 DevKit v1 — само използваните пинове"""

# ─── Нетове ─────────────────────────────────────────────────────────────────

# Захранване
KL30    = Net('+12V')       # Постоянно +12V от акумулатор
GND     = Net('GND')
VCC5    = Net('+5V')        # LM7805 изход
VCC33   = Net('+3V3')       # ESP32 3.3V изход (за pull-up)

# Входни сигнали (кола)
KL18_CAR   = Net('KL18_CAR')   # ACC от запалване
AUTO_CAR   = Net('AUTO_CAR')   # AUTO превключвател
UNLOCK_CAR = Net('UNLOCK_CAR') # Отключване (12V pulse)
VBAT_CAR   = Net('VBAT_CAR')   # Акумулаторно напрежение

# GPIO сигнали (ESP32)
GPIO34 = Net('GPIO34_ADC')
GPIO35 = Net('GPIO35_ACC')
GPIO32 = Net('GPIO32_AUTO')
GPIO33 = Net('GPIO33_UNLOCK')
GPIO26 = Net('GPIO26_XENON')
GPIO27 = Net('GPIO27_GABARI')
GPIO14 = Net('GPIO14_FOG')
GPIO13 = Net('GPIO13_ILLUM')

# Вътрешни нетове
GATE_IRF    = Net('GATE_IRF')       # IRF4905 Gate
XENON_OUT   = Net('XENON_OUT')      # Xenon балаcт вход (след диоди)
GABARI_OUT  = Net('GABARI_OUT')     # Габарити (след диоди)
FOG_OUT     = Net('FOG_OUT')        # Мъгла (след диоди)
ILLUM_OUT   = Net('ILLUM_OUT')      # Illumination (след диоди)

BCM_XENON  = Net('BCM_XENON')      # BCM ксенон изход
BCM_GABARI = Net('BCM_GABARI')     # BCM габарити изход
BCM_FOG    = Net('BCM_FOG')        # BCM мъгла изход
BCM_ILLUM  = Net('BCM_ILLUM')      # BCM illumination изход

RELAY_K1_NO = Net('K1_NO')         # Реле K1 — нормално отворен
RELAY_K2_NO = Net('K2_NO')         # Реле K2 — нормално отворен
RELAY_K1_C  = Net('K1_COIL_NEG')   # Реле K1 — бобина (-)
RELAY_K2_C  = Net('K2_COIL_NEG')   # Реле K2 — бобина (-)

# ─── Компоненти ─────────────────────────────────────────────────────────────

# --- Секция 1: Захранване ---

F1 = Part('Device', 'Fuse', footprint='Fuse:Fuseholder_Cylinder_5x20mm_Schurter_0031_8201_Horizontal_Open')
F1['A'] += KL30
F1['K'] += Net('F1_OUT')
F1.value = '1A'
F1.ref = 'F1'

D1 = Part('Device', 'D', footprint='Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal')
D1['A'] += Net('F1_OUT')
D1['K'] += Net('D1_OUT')
D1.value = '1N4007'
D1.ref = 'D1'

# TVS диод
D12 = Part('Device', 'D_Zener', footprint='Diode_THT:D_DO-201AD_P12.70mm_Horizontal')
D12['A'] += GND
D12['K'] += Net('D1_OUT')
D12.value = 'P6KE15A'
D12.ref = 'D12'

U2 = Part('Regulator_Linear', 'LM7805_TO220', footprint='Package_TO_SOT_THT:TO-220-3_Vertical')
U2['VI'] += Net('D1_OUT')
U2['GND'] += GND
U2['VO'] += VCC5
U2.ref = 'U2'

C1 = Part('Device', 'CP', footprint='Capacitor_THT:CP_Radial_D8.0mm_P3.50mm')
C1['+'] += VCC5
C1['-'] += GND
C1.value = '100uF/25V'
C1.ref = 'C1'

C2 = Part('Device', 'C', footprint='Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm')
C2[1] += VCC5
C2[2] += GND
C2.value = '100nF'
C2.ref = 'C2'

# --- Секция 2: Vbat делител ---

R1 = Part('Device', 'R', footprint='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal')
R1[1] += VBAT_CAR
R1[2] += GPIO34
R1.value = '47k'
R1.ref = 'R1'

R2 = Part('Device', 'R', footprint='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal')
R2[1] += GPIO34
R2[2] += GND
R2.value = '10k'
R2.ref = 'R2'

# --- Секция 3: Оптрони ---

# OK1 — KL18/ACC
R3 = Part('Device', 'R', footprint='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal')
R3[1] += KL18_CAR
R3[2] += Net('OK1_A')
R3.value = '4k7'
R3.ref = 'R3'

OK1 = Part('Isolator', 'PC817', footprint='Package_DIP:DIP-4_W7.62mm')
OK1['A']  += Net('OK1_A')
OK1['K']  += GND
OK1['C']  += GPIO35
OK1['E']  += GND
OK1.ref = 'OK1'

R4 = Part('Device', 'R', footprint='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal')
R4[1] += VCC33
R4[2] += GPIO35
R4.value = '10k'
R4.ref = 'R4'

# OK2 — AUTO
R5 = Part('Device', 'R', footprint='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal')
R5[1] += AUTO_CAR
R5[2] += Net('OK2_A')
R5.value = '4k7'
R5.ref = 'R5'

OK2 = Part('Isolator', 'PC817', footprint='Package_DIP:DIP-4_W7.62mm')
OK2['A']  += Net('OK2_A')
OK2['K']  += GND
OK2['C']  += GPIO32
OK2['E']  += GND
OK2.ref = 'OK2'

R6 = Part('Device', 'R', footprint='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal')
R6[1] += VCC33
R6[2] += GPIO32
R6.value = '10k'
R6.ref = 'R6'

# OK3 — UNLOCK
R7 = Part('Device', 'R', footprint='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal')
R7[1] += UNLOCK_CAR
R7[2] += Net('OK3_A')
R7.value = '4k7'
R7.ref = 'R7'

OK3 = Part('Isolator', 'PC817', footprint='Package_DIP:DIP-4_W7.62mm')
OK3['A']  += Net('OK3_A')
OK3['K']  += GND
OK3['C']  += GPIO33
OK3['E']  += GND
OK3.ref = 'OK3'

R8 = Part('Device', 'R', footprint='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal')
R8[1] += VCC33
R8[2] += GPIO33
R8.value = '10k'
R8.ref = 'R8'

# --- Секция 4: ESP32 ---

U1 = Part('RF_Module', 'ESP32-WROOM-32', footprint='RF_Module:ESP32-WROOM-32')
# Захранване
U1['GND'] += GND
U1['3V3'] += VCC33

# Входове
U1['IO34'] += GPIO34
U1['IO35'] += GPIO35
U1['IO32'] += GPIO32
U1['IO33'] += GPIO33

# Изходи
U1['IO26'] += GPIO26
U1['IO27'] += GPIO27
U1['IO14'] += GPIO14
U1['IO13'] += GPIO13
U1.ref = 'U1'

# --- Секция 5: Ксенон MOSFET ---

F2 = Part('Device', 'Fuse', footprint='Fuse:Fuseholder_Cylinder_5x20mm_Schurter_0031_8201_Horizontal_Open')
F2['A'] += KL30
F2['K'] += Net('F2_OUT')
F2.value = '15A'
F2.ref = 'F2'

R9 = Part('Device', 'R', footprint='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal')
R9[1] += Net('F2_OUT')   # pull-up to KL30 (через F2)
R9[2] += GATE_IRF
R9.value = '10k'
R9.ref = 'R9'

Q2 = Part('Device', 'Q_NMOS_GDS', footprint='Package_TO_SOT_THT:TO-92_Inline')
Q2['G'] += GPIO26
Q2['D'] += GATE_IRF
Q2['S'] += GND
Q2.value = '2N7000'
Q2.ref = 'Q2'

R10 = Part('Device', 'R', footprint='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal')
R10[1] += GPIO26
R10[2] += Net('Q2_G_RES')  # между GPIO26 и Q2 Gate
R10.value = '1k'
R10.ref = 'R10'

# Поправка: R10 е серийно между GPIO и Gate на Q2
Q2['G'] += Net('Q2_G_RES')

Q1 = Part('Device', 'Q_PMOS_GDS', footprint='Package_TO_SOT_THT:TO-220-3_Vertical')
Q1['G'] += GATE_IRF
Q1['D'] += Net('IRF_DRAIN')
Q1['S'] += Net('F2_OUT')  # Source към KL30 (след F2)
Q1.value = 'IRF4905'
Q1.ref = 'Q1'

D2 = Part('Device', 'D', footprint='Diode_THT:D_DO-201AD_P12.70mm_Horizontal')
D2['A'] += Net('IRF_DRAIN')
D2['K'] += XENON_OUT
D2.value = '1N5408'
D2.ref = 'D2'

D3 = Part('Device', 'D', footprint='Diode_THT:D_DO-201AD_P12.70mm_Horizontal')
D3['A'] += BCM_XENON
D3['K'] += XENON_OUT
D3.value = '1N5408'
D3.ref = 'D3'

# --- Секция 6: Реле K1 (Габарити) ---

F3 = Part('Device', 'Fuse', footprint='Fuse:Fuseholder_Cylinder_5x20mm_Schurter_0031_8201_Horizontal_Open')
F3['A'] += KL30
F3['K'] += Net('F3_OUT')
F3.value = '5A'
F3.ref = 'F3'

R11 = Part('Device', 'R', footprint='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal')
R11[1] += GPIO27
R11[2] += Net('Q3_BASE')
R11.value = '1k'
R11.ref = 'R11'

Q3 = Part('Device', 'Q_NPN_BCE', footprint='Package_TO_SOT_THT:TO-92_Inline')
Q3['B'] += Net('Q3_BASE')
Q3['C'] += RELAY_K1_C
Q3['E'] += GND
Q3.value = 'BC547'
Q3.ref = 'Q3'

K1 = Part('Relay', 'G5V-1', footprint='Relay_THT:Relay_SPDT_SANYOU_SRD_Series_RM5')
K1['Coil+'] += Net('F3_OUT')
K1['Coil-'] += RELAY_K1_C
K1['NO']    += RELAY_K1_NO
K1['COM']   += Net('F3_OUT')   # COM напрежение от F3
K1.ref = 'K1'

D8 = Part('Device', 'D', footprint='Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal')
D8['A'] += RELAY_K1_C
D8['K'] += Net('F3_OUT')
D8.value = '1N4007'
D8.ref = 'D8'

D4 = Part('Device', 'D', footprint='Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal')
D4['A'] += RELAY_K1_NO
D4['K'] += GABARI_OUT
D4.value = '1N4007'
D4.ref = 'D4'

D5 = Part('Device', 'D', footprint='Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal')
D5['A'] += BCM_GABARI
D5['K'] += GABARI_OUT
D5.value = '1N4007'
D5.ref = 'D5'

# --- Секция 7: Реле K2 (Мъгла) ---

R12 = Part('Device', 'R', footprint='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal')
R12[1] += GPIO14
R12[2] += Net('Q4_BASE')
R12.value = '1k'
R12.ref = 'R12'

Q4 = Part('Device', 'Q_NPN_BCE', footprint='Package_TO_SOT_THT:TO-92_Inline')
Q4['B'] += Net('Q4_BASE')
Q4['C'] += RELAY_K2_C
Q4['E'] += GND
Q4.value = 'BC547'
Q4.ref = 'Q4'

K2 = Part('Relay', 'G5V-1', footprint='Relay_THT:Relay_SPDT_SANYOU_SRD_Series_RM5')
K2['Coil+'] += Net('F3_OUT')
K2['Coil-'] += RELAY_K2_C
K2['NO']    += RELAY_K2_NO
K2['COM']   += Net('F3_OUT')
K2.ref = 'K2'

D9 = Part('Device', 'D', footprint='Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal')
D9['A'] += RELAY_K2_C
D9['K'] += Net('F3_OUT')
D9.value = '1N4007'
D9.ref = 'D9'

D6 = Part('Device', 'D', footprint='Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal')
D6['A'] += RELAY_K2_NO
D6['K'] += FOG_OUT
D6.value = '1N4007'
D6.ref = 'D6'

D7 = Part('Device', 'D', footprint='Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal')
D7['A'] += BCM_FOG
D7['K'] += FOG_OUT
D7.value = '1N4007'
D7.ref = 'D7'

# --- Секция 8: Illumination ---

R13 = Part('Device', 'R', footprint='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal')
R13[1] += GPIO13
R13[2] += Net('Q5_BASE')
R13.value = '1k'
R13.ref = 'R13'

Q5 = Part('Device', 'Q_NPN_BCE', footprint='Package_TO_SOT_THT:TO-92_Inline')
Q5['B'] += Net('Q5_BASE')
Q5['C'] += Net('Q5_COL')
Q5['E'] += GND
Q5.value = 'BC547'
Q5.ref = 'Q5'

D10 = Part('Device', 'D', footprint='Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal')
D10['A'] += Net('Q5_COL')
D10['K'] += ILLUM_OUT
D10.value = '1N4007'
D10.ref = 'D10'

D11 = Part('Device', 'D', footprint='Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal')
D11['A'] += BCM_ILLUM
D11['K'] += ILLUM_OUT
D11.value = '1N4007'
D11.ref = 'D11'

# --- Конектори ---

# J1 — KL30/GND захранване
J1 = Part('Connector_Generic', 'Conn_01x03', footprint='Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical')
J1[1] += KL30
J1[2] += GND
J1[3] += VBAT_CAR
J1.ref = 'J1'
J1.value = 'PWR_IN'

# J2 — Входни сигнали от кола
J2 = Part('Connector_Generic', 'Conn_01x04', footprint='Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical')
J2[1] += KL18_CAR
J2[2] += AUTO_CAR
J2[3] += UNLOCK_CAR
J2[4] += GND
J2.ref = 'J2'
J2.value = 'INPUTS'

# J3 — BCM изходи (от кола)
J3 = Part('Connector_Generic', 'Conn_01x05', footprint='Connector_JST:JST_XH_B5B-XH-A_1x05_P2.50mm_Vertical')
J3[1] += BCM_XENON
J3[2] += BCM_GABARI
J3[3] += BCM_FOG
J3[4] += BCM_ILLUM
J3[5] += GND
J3.ref = 'J3'
J3.value = 'BCM_IN'

# J4 — Изходи към светлини
J4 = Part('Connector_Generic', 'Conn_01x05', footprint='Connector_JST:JST_XH_B5B-XH-A_1x05_P2.50mm_Vertical')
J4[1] += XENON_OUT
J4[2] += GABARI_OUT
J4[3] += FOG_OUT
J4[4] += ILLUM_OUT
J4[5] += GND
J4.ref = 'J4'
J4.value = 'LIGHTS_OUT'

# J5 — ESP32 захранване (5V от платката)
J5 = Part('Connector_Generic', 'Conn_01x02', footprint='Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical')
J5[1] += VCC5
J5[2] += GND
J5.ref = 'J5'
J5.value = 'ESP32_VIN'

# ─── Генерация ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    generate_netlist()
    print("✓ Нетлист генериран: vectra-auto-lights.net")
    print("  → Отвори в KiCad PCB Editor → File → Import Netlist")
