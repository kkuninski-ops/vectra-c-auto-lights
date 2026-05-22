"""
Vectra C Auto Lights — подобрен авто-placer
Spacing: минимум 12mm между компоненти, 15mm между редове
Board: 160x120mm
"""
import pcbnew

board = pcbnew.GetBoard()

def mm(v):
    return int(v * 1e6)

# Build addr -> footprint map
addr_fp = {}
for fp in board.GetFootprints():
    addr = None
    try:
        addr = fp.GetField("atopile_address").GetText()
    except Exception:
        pass
    if not addr:
        try:
            for f in fp.GetFields():
                if f.GetName() == "atopile_address":
                    addr = f.GetText()
                    break
        except Exception:
            pass
    if addr:
        short = addr.replace("VectraAutoLights.", "")
        addr_fp[short] = fp
        addr_fp[addr]  = fp

print(f"Намерени: {len(addr_fp)//2} компонента")

def mv(addr, x, y, rot=0):
    short = addr.replace("VectraAutoLights.", "")
    fp = addr_fp.get(short) or addr_fp.get(addr)
    if fp:
        fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        fp.SetOrientationDegrees(rot)
    else:
        print(f"  NOT FOUND: {short}")

B = "VectraAutoLights."

# ── Row 1: Конектори (y=10) ────────────────────────────────────
# 1x2 и 1x4 pin headers — courtyard ~7x8mm
mv(B+"j1",   8,  10)          # 2-pin: KL30+GND
mv(B+"j2",  22,  10)          # 4-pin: входове
mv(B+"j3",  88,  10)          # 3-pin: XENON
mv(B+"j4", 103,  10)          # 3-pin: GABARI
mv(B+"j5", 118,  10)          # 3-pin: FOG
mv(B+"j6", 133,  10)          # 3-pin: ILLUM

# ── Row 2: Предпазители (y=18, rot=90) ───────────────────────
# Schurter 5x20mm at rot=90 → 20mm tall, courtyard y=8..28
# Следващите компоненти ТРЯБВА да са на y>=32
mv(B+"psu.f1",  33,  18, rot=90)
mv(B+"psu.f2",  58,  18, rot=90)
mv(B+"psu.f3",  83,  18, rot=90)

# ── Row 3: Захранване (y=36) ──────────────────────────────────
# Fuse courtyard ends at y=28, safe from y=32
mv(B+"psu.d1",   8,  36, rot=90)   # 1N4007 обратна защита
mv(B+"psu.d12", 20,  36, rot=90)   # P6KE15A TVS
mv(B+"psu.u2",  33,  36)           # LM7805

# ── Row 4: Кондензатори + делител (y=50) ─────────────────────
mv(B+"psu.c1",   8,  50)
mv(B+"psu.c2",  20,  50)
mv(B+"vbat_div.r1",  32,  50, rot=90)
mv(B+"vbat_div.r2",  42,  50, rot=90)

# ── Оптрони OK1/OK2/OK3 (x=52..80, y=36/52/68) ───────────────
# PC817 DIP-4: courtyard ~10x6mm. Spacing: 16mm между редове
for i, ch in enumerate(["ok1", "ok2", "ok3"]):
    y = 36 + i * 18
    mv(B+f"{ch}.r_in", 52, y, rot=90)   # входен резистор
    mv(B+f"{ch}.ok",   64, y)            # PC817
    mv(B+f"{ch}.r_pu", 77, y, rot=90)   # pull-up резистор

# ── ESP32 (y=52, x=108) ───────────────────────────────────────
# WROOM-32E: 25.5x18mm courtyard
mv(B+"u1", 108, 52)

# ── Ксенон MOSFET драйвер (y=82) ─────────────────────────────
# TO-220 (Q4) needs more space
mv(B+"xenon.r10",  8,  82, rot=90)   # 1kΩ gate R
mv(B+"xenon.q2",  20,  82)            # BC547 NPN
mv(B+"xenon.r9",  32,  82, rot=90)   # 10kΩ pull-down
mv(B+"xenon.q1",  44,  82, rot=90)   # IRF4905 TO-220
mv(B+"xenon.d2",  58,  82, rot=90)   # 1N5408
mv(B+"xenon.d3",  70,  82, rot=90)   # 1N5408

# ── Реле ГАБАРИ (y=98) ───────────────────────────────────────
mv(B+"gabari.r_base",  8,  98, rot=90)
mv(B+"gabari.q",      20,  98)
mv(B+"gabari.d_coil", 32,  98, rot=90)
mv(B+"gabari.relay",  46,  98)
mv(B+"gabari.d_no",   64,  98, rot=90)
mv(B+"gabari.d_com",  75,  98, rot=90)

# ── Реле МЪГЛА (y=98, дясна страна) ──────────────────────────
mv(B+"fog.r_base",  88,  98, rot=90)
mv(B+"fog.q",      100,  98)
mv(B+"fog.d_coil", 112,  98, rot=90)
mv(B+"fog.relay",  126,  98)
mv(B+"fog.d_no",   144,  98, rot=90)
mv(B+"fog.d_com",  144, 108, rot=90)

# ── Подсветка ILLUM (y=112) ───────────────────────────────────
mv(B+"illum.r13",  8, 112, rot=90)
mv(B+"illum.q5",  20, 112)
mv(B+"illum.d10", 32, 112, rot=90)
mv(B+"illum.d11", 44, 112, rot=90)

# ── Edge.Cuts outline 160x125mm ──────────────────────────────
for seg in list(board.GetDrawings()):
    if seg.GetLayer() == pcbnew.Edge_Cuts:
        board.Remove(seg)

corners = [(3, 3), (163, 3), (163, 123), (3, 123)]
for i in range(4):
    x1, y1 = corners[i]
    x2, y2 = corners[(i+1) % 4]
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetLayer(pcbnew.Edge_Cuts)
    seg.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
    seg.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
    seg.SetWidth(mm(0.05))
    board.Add(seg)

board.SetModified()
pcbnew.Refresh()
print("Done — board 160x120mm, generous spacing")
