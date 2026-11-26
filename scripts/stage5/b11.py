# IT-08 a) Esc во время загрузки LocationExit; b) Esc в инвентаре готовки
from s3blib import *
R = {"a": [], "b": []}
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
hyg_tick(R, "b11"); prestage("b11")
print("goto", goto("Beach"), flush=True); time.sleep(2); wait_play_ready()
autosync(True)
try:
    T[0] = time.time(); S("a", "до")
    lg = log_mark(); T[0] = time.time()
    teleport("T1", EXIT[0], EXIT[1] + 0.3, EXIT[2]); time.sleep(0.15)
    R["esc_at"] = round(time.time() - T[0], 2); key("Escape", 0.1)
    S("a", "сразу после Esc")
    for i in range(8): time.sleep(1.0); S("a", "+%d" % (i + 1))
    R["a_log"] = log_since(lg); p0 = ppos(); key("W", 0.3); time.sleep(1.0); R["a_w_moved"] = round(dxz(p0, ppos()), 2)
    key("Escape", 0.1); time.sleep(1.5); S("a", "второй Esc (проверка паузы)")
    key("Escape", 0.1); time.sleep(1.5); S("a", "третий Esc (закрыть)")
    print("a w", R["a_w_moved"], "esc_at", R["esc_at"], R["a_log"], flush=True); dump()
    # b
    print("goto", goto("Beach"), flush=True); time.sleep(2); wait_play_ready(); autosync(True)
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
