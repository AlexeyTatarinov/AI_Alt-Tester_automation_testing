# -*- coding: utf-8 -*-
from s2lib import *
F = os.path.join(R2, "m03_02.json")
try: D = json.load(open(F, encoding="utf-8"))
except Exception: D = {"trace": []}
PH = sys.argv[1]
autosync(True)

def tr(label, **kw):
    r = {"t": now(), "label": label, "count": alert_count(), "state": sname(gstate()), "scenes": scene_now()}
    r.update(kw); D["trace"].append(r); print(json.dumps(r, ensure_ascii=False), flush=True); jdump(F, D); return r

def crit():
    for c in d.find_objects(By.COMPONENT, "Critter", enabled=False):
        if c.name.startswith("PlantCritter"):
            try: c.update_object(); return c
            except Exception: pass
    return None
def alert(c):
    try: return c.get_component_property("Critter", "isPlayerInAlertZone", ASM)
    except Exception as e: return "ERR " + type(e).__name__
def cpos(c):
    c.update_object(); return (c.worldX, c.worldY, c.worldZ)
def approach(c, dist=3.0, wait=10):
    cp = cpos(c); teleport("T1", cp[0] - dist, cp[1] + 0.3, cp[2]); t0 = time.time()
    while time.time() - t0 < wait:
        time.sleep(0.25)
        if alert(c) is True: return round(time.time() - t0, 1)
    return None
def to_fieldhill():
    if scene_now() == ["Field_Hill"]: return "already"
    if not cheat_open():
        if gstate() == 0:
            return goto("Field_Hill")
        key("C", 0.1); time.sleep(1.2)
        if not cheat_open():
            return "CHEAT_BLOCKED state=" + sname(gstate())
    return goto("Field_Hill")
def walk_away(c, maxn=60):
    cp = cpos(c); n = 0
    while n < maxn:
        p = ppos()
        if alert(c) is False: break
        away = (p[0] + (p[0] - cp[0]), p[1], p[2] + (p[2] - cp[2]))
        step_towards(away, 0.3); n += 1; time.sleep(0.15)
    return n, round(dxz(ppos(), cp), 1), alert(c)

try:
    off = log_mark()
    if PH == "A":
        D["setup"] = to_fieldhill(); time.sleep(3); print("setup", D["setup"])
        tr("Field_Hill: до начала")
        c = crit(); assert c is not None; D["critter"] = c.name; D["critter_pos"] = cpos(c)
        t = approach(c); tr("A: подошёл, тревога", alert_s=t, alert=alert(c))
        n, dist, a = walk_away(c); tr("A: ушёл пешком", steps=n, dist=dist, alert=a)
        time.sleep(10); tr("A: через 10 с", alert=alert(c))
        D["exc_A"] = exc_summary(off)["total"]
    if PH == "B":
        c = crit(); assert c is not None, "нет PlantCritter (сцена %s)" % scene_now()
        tr("B: до подхода")
        t = approach(c); tr("B: подошёл, тревога", alert_s=t, alert=alert(c))
        # смена локации через меню читов, не выходя из зоны
        key("C", 0.1); time.sleep(1.2); D["B_cheat_opened_in_combat"] = cheat_open(); tr("B: C в тревоге", cheat=cheat_open())
        if cheat_open():
            r = goto("Beach"); tr("B: после смены локации (Beach)", goto=str(r))
        else:
            D["B_fallback"] = "меню читов не открылось в Combat"
        time.sleep(3); tr("B: в новой сцене +3 с")
        D["exc_B"] = exc_summary(off)["total"]
    if PH == "C":
        if scene_now() != ["Field_Hill"]:
            key("C", 0.1); time.sleep(1.2); D["C_setup"] = str(goto("Field_Hill")); time.sleep(3)
        tr("C: до подхода")
        c = crit(); assert c is not None
        t = approach(c); tr("C: подошёл, тревога", alert_s=t, alert=alert(c))
        cp = cpos(c); teleport("T1", cp[0] - 1.2, cp[1] + 0.3, cp[2]); time.sleep(1.0)
        for _ in range(3): step_towards(cp, 0.08)
        hits = 0; gone = False; dead = False; t0 = time.time()
        while time.time() - t0 < 20:
            key("F", 0.1); hits += 1; time.sleep(0.4)
            try:
                c.update_object()
                if c.get_component_property("Damageable", "IsDead", ASM) is True: dead = True
            except Exception:
                gone = True; break
            if dead: break
            if hits % 6 == 0:
                try:
                    cp2 = (c.worldX, c.worldY, c.worldZ)
                    if dxz(ppos(), cp2) > 2.2: teleport("T1", cp2[0] - 1.2, cp2[1] + 0.3, cp2[2]); time.sleep(0.5)
                    step_towards(cp2, 0.08)
                except Exception: pass
        tr("C: сразу после удара", hits=hits, gone=gone, dead=dead)
        time.sleep(5); tr("C: через 5 с")
        D["exc_C"] = exc_summary(off)["total"]
    if PH == "D":
        tr("D: до Back to menu")
        guard.risky("m0302 D back to menu"); r = to_menu(); print("to_menu", r)
        for _ in range(20):
            time.sleep(1.5)
            if "MainMenu" in scenes() and d.find_objects(By.NAME, "Button New Game", enabled=False): break
        time.sleep(1); tr("D: в MainMenu")
        guard.restore_window("m0302 D ng"); print("new_game", new_game())
        for _ in range(20):
            time.sleep(1.5)
            try: ppos(); break
            except Exception: pass
        time.sleep(3); tr("D: после New Game (Beach)")
        D["D_setup"] = str(goto("Field_Hill")); time.sleep(3)
        tr("D: Field_Hill, до подхода")
        c = crit(); assert c is not None
        t = approach(c); tr("D: подошёл, тревога", alert_s=t, alert=alert(c))
        n, dist, a = walk_away(c); tr("D: ушёл", steps=n, dist=dist, alert=a)
        time.sleep(10); tr("D: через 10 с")
        D["exc_D"] = exc_summary(off)["total"]
    jdump(F, D)
finally:
    autosync(False)
