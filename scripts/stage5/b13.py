# IT-08 a) Esc во время загрузки LocationExit; b) Esc в инвентаре готовки
from s3blib import *
R = json.load(open(os.path.join(os.environ["MOD_OUT"], "b11.json"), encoding="utf-8")); R["b_first_no_hint"] = json.load(open(os.path.join(os.environ["MOD_OUT"], "b11.json"), encoding="utf-8")).get("b", []); R["b"] = []
off = json.load(open(os.path.join(R2, "b1.json"), encoding="utf-8"))["off"]
def dump(): jdump(os.path.join(R2, "b11.json"), R)
def maps():
    p = first("Protagonist")
    if p is None: return "no Protagonist"
    return {m: str(rd(p, "Protagonist", "_inputReader._gameInput.%s.enabled" % m)) for m in ("Gameplay", "Menus", "Dialogues")}
def S(k, label):
    r = {"label": label, "t": round(time.time() - T[0], 2)}
    r["scenes"] = scene_now(); r["timeScale"] = d.get_static_property("UnityEngine.Time", "timeScale", CORE)
    r["pause"] = pause_open(); r["inventory"] = inv()
    try: r["state"] = sname(gstate())
    except Exception as e: r["state"] = "ERR " + type(e).__name__
    r["maps"] = maps()
    R[k].append(r); print(k, json.dumps(r, ensure_ascii=False), flush=True); return r
T = [time.time()]
if pause_open(): key("Escape", 0.1); time.sleep(1.5)
assert gstate() == 0 and "Beach" in scenes()
autosync(True)
try:
    ok = False; tries = []
    for dist in (1.5, 1.3, 1.0):
        away_then_tp(POT, dist)
        for i in range(6):
            tries.append((dist, round(dxz(ppos(), POT), 2), hint()))
            if hint(): ok = True; break
            step_towards(POT, 0.15); time.sleep(0.9)
        if ok: break
    R["pot_tries"] = tries; R["pot_hint"] = ok; print("tries", tries, flush=True)
    assert ok
    lg = log_mark(); T[0] = time.time(); S("b", "у котла")
    key("E", 0.1); time.sleep(1.5); S("b", "после E"); d.get_png_screenshot(os.path.join(R2, "shots", "b13_cooking.png"))
    assert inv(), "инвентарь не открылся"
    key("Escape", 0.1); time.sleep(1.5); S("b", "после Esc 1"); d.get_png_screenshot(os.path.join(R2, "shots", "b13_after_esc.png"))
    time.sleep(2); S("b", "ещё через 2 с")
    p0 = ppos(); key("W", 0.3); time.sleep(1.0); R["b_w_moved"] = round(dxz(p0, ppos()), 2)
    key("Escape", 0.1); time.sleep(1.5); S("b", "Esc 2")
    key("Escape", 0.1); time.sleep(1.5); S("b", "Esc 3")
    R["b_log"] = log_since(lg); R["exc"] = exc_summary(off)["total"]; R["items"] = inv_items(); print("b w", R["b_w_moved"], R["b_log"], "exc", R["exc"], R["items"], flush=True)
finally:
    autosync(False); dump()
