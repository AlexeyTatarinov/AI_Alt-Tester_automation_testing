# P04: дождаться конца катсцены; состояние, Tab, W, Gluecose
from g6 import *
R = {"trace": []}
off = json.load(open(os.path.join(R2, "a1.json"), encoding="utf-8"))["off"]
def dump(): jdump(os.path.join(R2, "a3.json"), R)
def dr():
    for o in d.find_objects(By.COMPONENT, PD, enabled=False):
        if o.name == "CutscenePlayableDirector (1)":
            return {"state": o.get_component_property(PD, "state", DM, max_depth=1), "time": round(float(o.get_component_property(PD, "time", DM, max_depth=1)), 2)}
    return "нет объекта"
def S(label):
    c = first("CutsceneManager")
    s = {"label": label, "t": now(), "state": sname(gstate()), "dlg": dlg(), "director": dr(), "count": alert_count(),
         "active_pd": str(rd(c, "CutsceneManager", "_activePlayableDirector.name", 1))[:60]}
    s["glue_active"] = [(g["name"], g["id"], g["active"], g["alert"]) for g in glue()]
    R["trace"].append(s); dump(); print(json.dumps(s, ensure_ascii=False), flush=True); return s
prestage("a3")
try:
    S("начало"); t0 = time.time(); sp = 0; seq = []; ok = 0; last = time.time()
    while time.time() - t0 < 90:
        l = line()
        if l and (not seq or seq[-1] != l): seq.append(l)
        x = dr()
        playing = isinstance(x, dict) and x["state"] == 1
        if dlg() and sp < 30: key("Space", 0.1); sp += 1
        if not playing and not dlg(): ok += 1
        else: ok = 0
        if ok >= 3: break
        if time.time() - last > 8: S("ждём %.0f" % (time.time() - t0)); last = time.time()
        time.sleep(1.0)
    R["seq"] = seq; R["space"] = sp; R["waited_s"] = round(time.time() - t0, 1)
    S("после катсцены"); d.get_png_screenshot(os.path.join(R2, "shots", "a3_after.png"))
    time.sleep(3); S("после +3 с")
    R["panels"] = panels(); key("Tab", 0.1); time.sleep(1.5); R["tab_opens"] = inv(); R["state_tab"] = sname(gstate())
    if inv(): key("Tab", 0.1); time.sleep(1.5)
    p0 = ppos(); key("W", 0.3); time.sleep(1.0); p1 = ppos(); R["w_moved"] = round(dxz(p0, p1), 2); R["pos"] = [round(v, 2) for v in p1]
    pr = first("Protagonist"); R["maps"] = {m: rd(pr, "Protagonist", "_inputReader._gameInput.%s.enabled" % m) for m in ("Gameplay", "Menus", "Dialogues")}
    S("конец"); R["glue_end"] = glue(); R["exc"] = exc_summary(off)
    print("tab", R["tab_opens"], R["state_tab"], "w", R["w_moved"], R["pos"], R["maps"], "\nGLUE", R["glue_end"], "\nexc", R["exc"]["total"], R["exc"]["by_type"], "seq", seq, flush=True)
finally:
    dump()
