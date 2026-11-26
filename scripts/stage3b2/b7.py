# -*- coding: utf-8 -*-
# 4.4 IT-11: съесть SweetCream_Dish
from s3blib import *
R = {}
def dump(): jdump(os.path.join(R2, "b7.json"), R)
off = json.load(open(os.path.join(R2, "b1.json"), encoding="utf-8"))["off"]
prestage("b7"); autosync(True)
try:
    R["before"] = full_snap("IT-11 до", off); R["hp_before"] = hp_now(); print(R["before"], R["hp_before"], flush=True)
    assert R["before"]["state"] == "Gameplay"
    key("Tab", 0.1); time.sleep(1.5); R["tab_opens"] = inv(); assert inv(), "инвентарь не открылся"
    found = None; seen = []
    for i in range(5):
        sl = slots(); seen.append([x[1] for x in sl])
        m = [x for x in sl if x[1] == "SweetCream_Dish"]
        if m: found = m[0]; break
        key("Y", 0.1); time.sleep(1.0)
    R["tabs_seen"] = seen; assert found, "нет SweetCream_Dish в UI: %s" % seen
    found[0].click(); time.sleep(1.0)
    b, inter = action_button(); texts = []
    try:
        for o in d.find_objects(By.PATH, "//ActionButton//*", enabled=True):
            try: texts.append(o.get_text())
            except Exception: pass
    except Exception as e: texts.append("ERR " + type(e).__name__)
    R["button"] = {"interactable": inter, "texts": texts}; print("button", R["button"], flush=True)
    d.get_png_screenshot(os.path.join(R2, "shots", "it11_before_eat.png"))
    assert b is not None and inter is True
    b.click(); time.sleep(2.0)
    R["hp_after_click"] = hp_now()
    d.get_png_screenshot(os.path.join(R2, "shots", "it11_after_eat.png"))
    if inv(): key("Tab", 0.1); time.sleep(1.5)
    R["after"] = full_snap("IT-11 после", off); R["hp_after"] = hp_now(); R["diff"] = diff(R["before"], R["after"])
    R["save_info"] = save_info(); R["exc"] = exc_summary(off)
    print("hp", R["hp_before"], R["hp_after"], R["diff"], R["after"]["state"], "exc", R["exc"]["total"], flush=True)
finally:
    autosync(False); dump()
