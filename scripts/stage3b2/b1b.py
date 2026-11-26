# -*- coding: utf-8 -*-
# Play B, часть 1 (продолжение после ошибки подсказки у котла): котёл, разговор 4
from s3blib import *
R = json.load(open(os.path.join(R2, "b1.json"), encoding="utf-8")); off = R["off"]
def dump(): jdump(os.path.join(R2, "b1.json"), R)
prestage("b1b"); autosync(True)
try:
    p = ppos(); print("pos", [round(v, 2) for v in p], "pot", POT, "d", round(dxz(p, POT), 2), sname(gstate()), "hint", hint(), flush=True)
    ok = hint() and dxz(p, POT) < 2.5; tries = []
    for dist in (1.5, 1.3, 1.0):
        if ok: break
        away_then_tp(POT, dist)
        for i in range(6):
            tries.append((dist, round(dxz(ppos(), POT), 2), hint()))
            if hint(): ok = True; break
            step_towards(POT, 0.15); time.sleep(0.5)
    print("tries", tries, flush=True); R["pot_tries"] = tries
    s2 = full_snap("3 котёл до", off); R["pot_before"] = s2
    R["pot_hint"] = ok; R["pot_dist"] = round(dxz(ppos(), POT), 2)
    assert ok, "нет подсказки у котла"
    key("E", 0.1); time.sleep(1.5); assert inv(), "UI не открылся"
    sl = [x for x in slots() if "SweetCream" in x[1]]; assert sl, "нет рецепта"
    sl[0][0].click(); time.sleep(1.0)
    cook = None
    for o in d.find_objects(By.NAME, "Text (TMP)", enabled=True):
        try:
            if o.get_text().strip() == "Cook": cook = o.get_parent()
        except Exception: pass
    assert cook is not None, "нет Cook"
    guard.risky("b1 cook"); cook.click(); time.sleep(3.0)
    if inv(): key("Tab", 0.1); time.sleep(1.5)
    s3 = full_snap("3 котёл после", off); R["pot_after"] = s3; R["pot_diff"] = diff(s2, s3); R["state_after_pot"] = sname(gstate())
    print("POT", R["pot_diff"], R["state_after_pot"], flush=True); dump()
    storm_check(off, "pot")
    R["step4"] = conv_yes(off, "4"); r = R["step4"]
    print("STEP4", r["first_line"], r["replies"], r["closed"], r["diff"], flush=True); dump()
    sf = full_snap("после E2E-01", off); R["snap_e2e01"] = sf; R["diff_total"] = diff(R["snap_start"], sf); R["save_info"] = save_info()
    g = first("GameManager"); cs = {}
    for p in ("_questManager._currentStep", "_questManager._currentStep.name", "_questManager._currentQuest", "_questManager._currentQuest.name"):
        cs[p] = str(rd(g, "GameManager", p, 1))[:300]
    R["currentStep_raw"] = cs; R["exc"] = exc_summary(off); dump()
    print("TOTAL", R["diff_total"], "exc", R["exc"]["total"], sf["inv"], sf["quest"], flush=True)
    for k, v in cs.items(): print(k, "=>", v)
finally:
    autosync(False); dump()
