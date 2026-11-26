# IT-08 a) Esc во время загрузки LocationExit; b) Esc в инвентаре готовки
from s3blib import *
R = json.load(open(os.path.join(os.environ["MOD_OUT"], "b11.json"), encoding="utf-8")); R["b"] = []
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
autosync(True)
try:
    # b
    st = st_now("перед goto", cheat=cheat_open(), pause=pause_open())
    if cheat_open(): key("C", 0.1); time.sleep(1)
    for loc in ("Town_Market", "Beach"):
        try: print("goto", goto(loc), flush=True)
        except Exception as e: print("ERR", e, flush=True)
        time.sleep(2); wait_play_ready()
    assert "Beach" in scenes(); autosync(True)
    away_then_tp(POT, 1.5); R["pot_hint"] = hint(); print("hint", R["pot_hint"], flush=True)
    lg = log_mark(); T[0] = time.time(); S("b", "у котла")
    key("E", 0.1); time.sleep(1.5); S("b", "после E"); d.get_png_screenshot(os.path.join(R2, "shots", "b11_cooking.png"))
    key("Escape", 0.1); time.sleep(1.5); S("b", "после Esc 1"); d.get_png_screenshot(os.path.join(R2, "shots", "b11_after_esc.png"))
    time.sleep(2); S("b", "ещё через 2 с")
    p0 = ppos(); key("W", 0.3); time.sleep(1.0); R["b_w_moved"] = round(dxz(p0, ppos()), 2)
    key("Escape", 0.1); time.sleep(1.5); S("b", "Esc 2")
    key("Escape", 0.1); time.sleep(1.5); S("b", "Esc 3")
    R["b_log"] = log_since(lg); R["exc"] = exc_summary(off)["total"]; print("b w", R["b_w_moved"], R["b_log"], "exc", R["exc"], flush=True)
finally:
    autosync(False); dump()
