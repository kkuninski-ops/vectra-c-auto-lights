"""
Vectra C Auto Lights — auto-placer
Пусни от KiCad: Tools → Scripting Console → exec(open('/Users/kaloyank/Documents/vectra-c-auto-lights/hardware/atopile/place_components.py').read())
"""
import pcbnew

board = pcbnew.GetBoard()

# ── 1. Намери board origin от Edge.Cuts ────────────────────────────────────
ox = oy = 0.0
for d in board.GetDrawings():
    if d.GetLayer() == pcbnew.Edge_Cuts:
        bb = d.GetBoundingBox()
        ox = bb.GetLeft() / 1e6
        oy = bb.GetTop()  / 1e6
        break
print(f"Board origin: ({ox:.2f}, {oy:.2f}) mm")

# ── 2. Карта atopile_address → reference ──────────────────────────────────
addr_ref = {}
for fp in board.GetFootprints():
    # KiCad 7/8 — провери и двата начина
    try:
        addr = fp.GetField("atopile_address").GetText()
        if addr:
            addr_ref[addr] = fp.GetReference()
            continue
    except Exception:
        pass
    try:
        for f in fp.GetFields():
            if f.GetName() == "atopile_address":
                addr_ref[f.GetText()] = fp.GetReference()
                break
    except Exception:
        pass

print(f"\nНамерени компоненти: {len(addr_ref)}")
for a, r in sorted(addr_ref.items()):
    print(f"  {r:5s} ← {a.split('VectraAutoLights.')[-1]}")

# ── 3. Помощна функция за позициониране ───────────────────────────────────
def mv(addr, x, y, rot=0):
    short = addr.replace("VectraAutoLights.", "")
    ref = addr_ref.get(addr) or addr_ref.get(short)
    if not ref:
        print(f"  ? не е намерен: {short}")
        return
    fp = board.FindFootprintByReference(ref)
    if not fp:
        print(f"  ? ref не е намерен: {ref}")
        return
    fp.SetPosition(pcbnew.VECTOR2I(int((ox + x) * 1e6), int((oy + y) * 1e6)))
    fp.SetOrientationDegrees(rot)
    print(f"  ✓ {ref:4s} ({addr.split('.')[-1]:16s}) → ({x:5.1f}, {y:5.1f})")

print("\nПоставяне на компоненти...")

B = "VectraAutoLights."  # prefix shortcut

# ════════════════════════════════════════════════════════════════
# LAYOUT  (120 × 80 mm)
#
#   0        20        40        60        80       100       120
#   ├─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
# 0 │[J1][J2] [F1──────][F2──────][F3──────]  [J3][J4][J5][J6] │ 5
#10 │[D1][TVS][U2 LM7805]      [OK1─────────────────]           │
#20 │[C1][C2] [R47k][R10k]     [OK2─────────────────] [U1 ESP32]│
#30 │                           [OK3─────────────────] [ESP32   ]│
#40 │                                                  [ESP32   ]│
#50 │[R10][Q2][R9][Q1 IRF][D2────][D3────]                      │
#60 │[gabari: Rbase][Q3][D_c][K1─────────][D_no][D_com]         │
#70 │[fog:   Rbase][Q4][D_c][K2─────────][D_no][D_com]          │
#75 │[illum: R13][Q5][D10][D11]                                  │
# ════════════════════════════════════════════════════════════════

# ── Конектори (горен ред) ──────────────────────────────────────
mv(B+"j1",   5,  5)           # 2-pin: KL30 + GND
mv(B+"j2",  15,  5)           # 4-pin: KL18, AUTO, UNLOCK, GND
mv(B+"j3",  75,  5)           # 3-pin: XENON
mv(B+"j4",  87,  5)           # 3-pin: GABARI
mv(B+"j5",  99,  5)           # 3-pin: FOG
mv(B+"j6", 111,  5)           # 3-pin: ILLUM

# ── Предпазители (хоризонтално, горе) ─────────────────────────
mv(B+"psu.f1",  27, 10, rot=90)   # 1A  — MCU
mv(B+"psu.f2",  50, 10, rot=90)   # 15A — ксенон
mv(B+"psu.f3",  73, 10, rot=90)   # 5A  — релета

# ── Захранване (ляво) ─────────────────────────────────────────
mv(B+"psu.d1",   5, 18, rot=90)   # 1N4007 обратна защита
mv(B+"psu.d12", 15, 18, rot=90)   # P6KE15A TVS
mv(B+"psu.u2",  25, 18)           # LM7805
mv(B+"psu.c1",   5, 28)           # 100µF
mv(B+"psu.c2",  14, 28)           # 100nF

# ── VBAT делител ──────────────────────────────────────────────
mv(B+"vbat_div.r1", 24, 28, rot=90)   # 47kΩ
mv(B+"vbat_div.r2", 32, 28, rot=90)   # 10kΩ

# ── Оптрони (три канала) ──────────────────────────────────────
for i, ch in enumerate(["ok1", "ok2", "ok3"]):
    y = 15 + i * 10
    mv(B+f"{ch}.r_in", 42, y, rot=90)
    mv(B+f"{ch}.ok",   50, y)
    mv(B+f"{ch}.r_pu", 60, y, rot=90)

# ── ESP32 (дясно, центъра) ────────────────────────────────────
mv(B+"u1", 90, 28)    # 25.5×18mm — оставяме място

# ── Ксенон MOSFET драйвер ─────────────────────────────────────
mv(B+"xenon.r10",  5, 50, rot=90)   # 1kΩ — base Q2
mv(B+"xenon.q2",  13, 50)           # 2N7000
mv(B+"xenon.r9",  22, 50, rot=90)   # 10kΩ — gate pull-down
mv(B+"xenon.q1",  31, 50, rot=90)   # IRF4905 TO-220
mv(B+"xenon.d2",  42, 50, rot=90)   # 1N5408
mv(B+"xenon.d3",  54, 50, rot=90)   # 1N5408

# ── Реле ГАБАРИ ───────────────────────────────────────────────
mv(B+"gabari.r_base",  5, 62, rot=90)
mv(B+"gabari.q",      13, 62)
mv(B+"gabari.d_coil", 22, 62, rot=90)
mv(B+"gabari.relay",  32, 62)
mv(B+"gabari.d_no",   52, 62, rot=90)
mv(B+"gabari.d_com",  60, 62, rot=90)

# ── Реле МЪГЛА ────────────────────────────────────────────────
mv(B+"fog.r_base",  68, 62, rot=90)
mv(B+"fog.q",       76, 62)
mv(B+"fog.d_coil",  85, 62, rot=90)
mv(B+"fog.relay",   95, 62)
mv(B+"fog.d_no",   115, 62, rot=90)
mv(B+"fog.d_com",  115, 70, rot=90)

# ── Подсветка (ILLUM) ─────────────────────────────────────────
mv(B+"illum.r13",  5, 74, rot=90)
mv(B+"illum.q5",  13, 74)
mv(B+"illum.d10", 22, 74, rot=90)
mv(B+"illum.d11", 30, 74, rot=90)

# ── Edge.Cuts outline (130 × 90 mm) ──────────────────────────────
for seg in list(board.GetDrawings()):
    if seg.GetLayer() == pcbnew.Edge_Cuts:
        board.Remove(seg)

bw, bh = 130, 90
corners = [(ox, oy), (ox+bw, oy), (ox+bw, oy+bh), (ox, oy+bh)]
for i in range(4):
    x1, y1 = corners[i]
    x2, y2 = corners[(i+1) % 4]
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetLayer(pcbnew.Edge_Cuts)
    seg.SetStart(pcbnew.VECTOR2I(int(x1*1e6), int(y1*1e6)))
    seg.SetEnd(pcbnew.VECTOR2I(int(x2*1e6), int(y2*1e6)))
    seg.SetWidth(int(0.05*1e6))
    board.Add(seg)
print("Board outline 130x90mm added")

# ── Обнови дисплея ────────────────────────────────────────────
board.SetModified()
pcbnew.Refresh()
print("\n Done! Save with Cmd+S")
