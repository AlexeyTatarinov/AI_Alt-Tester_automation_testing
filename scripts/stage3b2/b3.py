# -*- coding: utf-8 -*-
# 4.3.2 IT-05: PlantCritter убить, подобрать выпавший предмет
from s3blib import *
R = {"trace": [], "kills": []}
def dump(): jdump(os.path.join(R2, "b3.json"), R)
off = json.load(open(os.path.join(R2, "b1.json"), encoding="utf-8"))["off"]; R["off"] = off
prestage("b3"); hyg_tick(R, "b3"); autosync(True)
def tr(label, **kw): R["trace"].append(st_now(label, **kw)); dump()
def kill(name):
    k = {"enemy": name}
    c = crit(name); assert c is not None, name
    k["items_before"] = {str(i): v[2] for i, v in collectables().items()}
    cp = cpos(c); teleport("T1", cp[0] - 3.0, cp[1] + 0.3, cp[2]); t0 = time.time(); al = None
    while time.time() - t0 < 10:
        time.sleep(1.0)
        if alert(c) is True: al = round(time.time() - t0, 1); break
    k["alert_s"] = al; tr(name + ": тревога", alert=alert(c))
    cp = cpos(c)
    if dxz(ppos(), cp) > 1.8: teleport("T1", cp[0] - 1.2, cp[1] + 0.3, cp[2]); time.sleep(1.0)
    hits = 0; gone = False; dead = False; t0 = time.time(); hps = []
    while time.time() - t0 < 25:
        try: cp2 = cpos(c); step_towards(cp2, 0.08)
        except Exception: gone = True; break
        key("F", 0.1); hits += 1; time.sleep(0.9); hps.append(hp_now())
        storm_check(off, "kill")
        try:
            c.update_object()
            if c.get_component_property("Damageable", "IsDead", ASM) is True: dead = True
        except Exception: gone = True; break
        if dead: break
        if hits % 5 == 0 and dxz(ppos(), cpos(c)) > 2.2:
            cp2 = cpos(c); teleport("T1", cp2[0] - 1.2, cp2[1] + 0.3, cp2[2]); time.sleep(0.5)
    k.update(hits=hits, dead=dead, player_hp=hps)
    time.sleep(5)
    k["enemy_still_present"] = crit(name) is not None
    cl = collectables()
    k["new_items"] = [{"id": i, "pos": v[1], "item": v[2]} for i, v in cl.items() if str(i) not in k["items_before"]]
    tr(name + ": через 5 с после удара", hits=hits, dead=dead, present=k["enemy_still_present"], new=[x["item"] for x in k["new_items"]])
    R["kills"].append(k); dump(); return k
def pickup(item):
    p = {"item": item}; iid = item["id"]
    p["before"] = full_snap("IT-05 до подбора", off)
    tries = []
    for i in range(14):
        cl = collectables()
        if iid not in cl: tries.append("исчез"); break
        pos = cl[iid][1]; dist = round(dxz(ppos(), pos), 2); h = hint(); tries.append((dist, h))
        if h: break
        if dist > 4: teleport("T1", pos[0] - 1.5, pos[1] + 1.0, pos[2]); time.sleep(1.5)
        else: step_towards(pos, 0.12); time.sleep(0.6)
    p["tries"] = tries; p["hint"] = hint()
    if p["hint"]: key("E", 0.1); time.sleep(3.0)
    p["gone_after"] = iid not in collectables()
    p["after"] = full_snap("IT-05 после подбора", off); p["diff"] = diff(p["before"], p["after"])
    return p
try:
    tr("Field_Hill: старт")
    for name in ("PlantCritter", "PlantCritter (2)"):
        k = kill(name)
        if k["new_items"]: break
    if R["kills"][-1]["new_items"]:
        R["pickup"] = pickup(R["kills"][-1]["new_items"][0])
        print("PICKUP", R["pickup"]["tries"], R["pickup"]["hint"], R["pickup"]["gone_after"], R["pickup"]["diff"], flush=True)
    tr("IT-05 конец"); R["save_info"] = save_info(); R["exc"] = exc_summary(off)
    print("exc", R["exc"]["total"], R["exc"]["by_type"], flush=True)
    for k in R["kills"]: print(k, flush=True)
finally:
    autosync(False); dump()
