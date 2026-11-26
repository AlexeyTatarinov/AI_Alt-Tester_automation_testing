# P04: ENM на одном Gluecose, затем CMB-05 (#426)
from g6 import *
R = {"trace": [], "hits": []}
off = json.load(open(os.path.join(R2, "a1.json"), encoding="utf-8"))["off"]
def dump(): jdump(os.path.join(R2, "a4.json"), R)
def G(oid):
    for o in d.find_objects(By.COMPONENT, "Critter", enabled=True):
        if o.id == oid: return o
    return None
def prop(o, comp, p):
    try: return o.get_component_property(comp, p, ASM)
    except Exception as e: return "ERR " + type(e).__name__
def S(label, c=None):
    s = {"label": label, "t": now(), "state": sname(gstate()), "count": alert_count(), "hp": hp_now(), "pos": [round(v, 2) for v in ppos()]}
    if c is not None:
        try:
            cp = cpos(c); s.update(enemy=[round(v, 2) for v in cp], dist=round(dxz(ppos(), cp), 2), alert=prop(c, "Critter", "isPlayerInAlertZone"),
                attack=prop(c, "Critter", "isPlayerInAttackZone"), ehp=prop(c, "Damageable", "_currentHealthSO.CurrentHealth"), edead=prop(c, "Damageable", "IsDead"))
        except Exception as e: s["enemy"] = "ERR " + type(e).__name__
    R["trace"].append(s); dump(); print(json.dumps(s, ensure_ascii=False), flush=True); return s
def near(c, dist):
    cp = cpos(c); pp = ppos(); vx, vz = pp[0] - cp[0], pp[2] - cp[2]; n = math.hypot(vx, vz) or 1
    x, z = cp[0] + vx / n * dist, cp[2] + vz / n * dist
    assert not hits_exit(EX, x, z), "точка в выходе"
    teleport("T1", x, cp[1] + 0.3, z)
prestage("a4"); hyg_tick(R, "a4"); autosync(True)
try:
    EX = exits(); live = [g for g in glue() if g["active"]]; R["live"] = live; assert len(live) >= 2
    start = ppos(); live.sort(key=lambda g: dxz(start, g["pos"]))
    c = G(live[0]["id"]); R["target"] = live[0]; S("до", c)
    # тревога
    near(c, 3.0); t0 = time.time()
    while time.time() - t0 < 8:
        time.sleep(1.0); s = S("тревога %.1f" % (time.time() - t0), c); storm_check(off, "alert")
        if s.get("alert") is True: R["alert_s"] = round(time.time() - t0, 1); break
    # атака: стоим, без ударов, до 15 с или первого урона
    if dxz(ppos(), cpos(c)) > 1.5: near(c, 1.1)
    t0 = time.time(); hp0 = hp_now(); R["hp_before_attack"] = hp0
    while time.time() - t0 < 15:
        time.sleep(1.0); s = S("атака %.1f" % (time.time() - t0), c); storm_check(off, "attack")
        if isinstance(s["hp"], int) and s["hp"] < hp0: R["damaged_s"] = round(time.time() - t0, 1); break
        if s.get("dist", 0) > 2.0: near(c, 1.1)
    R["hp_after_attack"] = hp_now()
    # урон врагу и смерть
    R["items_before"] = {str(i): v[2] for i, v in collectables().items()}
    t0 = time.time(); n = 0; dead = False
    while time.time() - t0 < 25 and n < 24:
        try:
            if dxz(ppos(), cpos(c)) > 1.6: near(c, 1.1); time.sleep(0.4)
            step_towards(cpos(c), 0.08)
        except Exception as e: R["gone"] = type(e).__name__; break
        key("F", 0.1); n += 1; time.sleep(0.9)
        s = S("удар %d" % n, c); R["hits"].append((n, s.get("ehp"), s.get("edead"), s.get("hp"))); storm_check(off, "hit")
        if s.get("edead") is True: dead = True; break
        if isinstance(s.get("enemy"), str): R["gone"] = s["enemy"]; break
    R["n_hits"] = n; R["dead"] = dead
    time.sleep(5)
    R["enemy_present"] = G(live[0]["id"]) is not None
    cl = collectables(); R["new_items"] = [(v[2], v[1]) for i, v in cl.items() if str(i) not in R["items_before"]]
    S("через 5 с")
    print("ENM", R.get("alert_s"), R.get("damaged_s"), R["hp_before_attack"], R["hp_after_attack"], n, dead, "present", R["enemy_present"], "new", R["new_items"], flush=True)
    dump()
finally:
    autosync(False); dump()
    R["exc"] = exc_summary(off); dump(); print("exc", R["exc"]["total"], R["exc"]["by_type"], flush=True)
