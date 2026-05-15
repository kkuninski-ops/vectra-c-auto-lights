import pcbnew

board = pcbnew.GetBoard()

def mm(v):
    return int(v * 1e6)

# Build addr -> footprint map from atopile_address field
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
        addr_fp[addr] = fp

print(f"Found {len(addr_fp)//2} components")

def mv(addr, x, y, rot=0):
    fp = addr_fp.get(addr) or addr_fp.get("VectraAutoLights." + addr)
    if fp:
        fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        fp.SetOrientationDegrees(rot)
        return True
    print("NOT FOUND:", addr)
    return False

# ── Connectors (top edge) ──────────────────────────
mv("j1", 10, 10)
mv("j2", 22, 10)
mv("j3", 34, 10)
mv("j4", 46, 10)
mv("j5", 58, 10)
mv("j6", 70, 10)

# ── Fuses ─────────────────────────────────────────
mv("psu.f1", 10, 22, 90)
mv("psu.f2", 22, 22, 90)

# ── 7805 voltage regulator + caps ─────────────────
mv("psu.u2",  35, 22)
mv("psu.c1",  45, 20, 90)
mv("psu.c2",  45, 25, 90)

# ── ESP32 ─────────────────────────────────────────
mv("u1", 80, 22)

# ── Bat voltage divider ───────────────────────────
mv("vbat_divr1", 60, 20, 90)
mv("vbat_divr2", 60, 25, 90)

# ── Optocouplers ──────────────────────────────────
for i, ch in enumerate(["ok1", "ok2", "ok3"]):
    y = 40 + i * 14
    mv(f"{ch}.r_in", 10, y, 90)
    mv(f"{ch}.ok",   20, y)
    mv(f"{ch}.r_pu", 32, y, 90)

# ── Fog relay channel ─────────────────────────────
mv("fog.r_base",  45, 40, 90)
mv("fog.q",       53, 40)
mv("fog.relay",   63, 40)
mv("fog.d_coil",  75, 38, 90)
mv("fog.d_no",    75, 43, 90)
mv("fog.d_com",   83, 40, 90)

# ── Gabari relay channel ──────────────────────────
mv("gabari.r_base",  45, 54, 90)
mv("gabari.q",       53, 54)
mv("gabari.relay",   63, 54)
mv("gabari.d_no",    75, 52, 90)
mv("gabari.d_com",   75, 57, 90)

# ── Xenon ballast driver ──────────────────────────
mv("xenon.r0",  45, 68, 90)
mv("xenon.q1",  53, 68)
mv("xenon.q2",  63, 68)
mv("xenon.d2",  75, 66, 90)
mv("xenon.d3",  75, 71, 90)

# ── Illumination channel ──────────────────────────
mv("illum.r13", 45, 82, 90)
mv("illum.q5",  53, 82)
mv("illum.d10", 63, 80, 90)
mv("illum.d11", 63, 85, 90)

# ── Edge.Cuts outline (100 x 100 mm) ─────────────
for seg in list(board.GetDrawings()):
    if seg.GetLayer() == pcbnew.Edge_Cuts:
        board.Remove(seg)

corners = [(5, 5), (105, 5), (105, 105), (5, 105)]
for i in range(4):
    x1, y1 = corners[i]
    x2, y2 = corners[(i + 1) % 4]
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetLayer(pcbnew.Edge_Cuts)
    seg.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
    seg.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
    seg.SetWidth(mm(0.05))
    board.Add(seg)

board.SetModified()
pcbnew.Refresh()
print("Done — layout 100x100mm applied")
