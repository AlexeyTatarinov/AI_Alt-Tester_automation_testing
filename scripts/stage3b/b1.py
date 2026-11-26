# -*- coding: utf-8 -*-
# Play B, часть 1: New Game, E2E-01 до questline 1
from s3blib import *
R = {}
def dump(): jdump(os.path.join(R2, "b1.json"), R)
prestage("b1")
R["frameCount0"] = d.get_static_property("UnityEngine.Time", "frameCount", CORE); assert R["frameCount0"] < 3000
assert "MainMenu" in scenes()
autosync(True)
try:
    hyg_start("b1", R)
    guard.risky("b1")
    print("new_game", new_game(), now(), flush=True)
    wait_play_ready()
    hyg_start("b1_after_ng", R)
    off = log_mark(); R["off"] = off
    s0 = full_snap("B старт", off); R["snap_start"] = s0; print(json.dumps(s0, ensure_ascii=False), flush=True)
    # 1: первый разговор
    R["hint1"] = to_hare(); key("E", 0.1); time.sleep(1.0); assert dlg(), "не открылся"
    R["first"] = talk_first()
    s1 = full_snap("1 после первого", off); R["snap1"] = s1; R["diff1"] = diff(s0, s1)
    print("STEP1", {k: v for k, v in R["first"].items() if k != "seq"}, R["diff1"], flush=True); dump()
    storm_check(off, "step1")
    # 2: второй, Yes
    R["step2"] = conv_yes(off, "2"); r = R["step2"]
    print("STEP2", r["first_line"], r["replies"], r["closed"], r["diff"], flush=True); dump()
    storm_check(off, "step2")
    hyg_tick(R, "pre-pot")
    # 3: котёл
    s2 = full_snap("3 котёл до", off); R["pot_before"] = s2
    ok = False
    for dist in (1.5, 1.3, 1.7):
        away_then_tp(POT, dist)
        for i in range(4):
            if hint(): ok = True; break
            time.sleep(0.5)
        if ok: break
    R["pot_hint"] = ok; R["pot_dist"] = round(dxz(ppos(), POT), 2); print("pot hint", ok, R["pot_dist"], flush=True)
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
    # 4: разговор "Did you try the sweet cream", Yes
    R["step4"] = conv_yes(off, "4"); r = R["step4"]
    print("STEP4", r["first_line"], r["replies"], r["closed"], r["diff"], flush=True); dump()
    sf = full_snap("после E2E-01", off); R["snap_e2e01"] = sf; R["diff_total"] = diff(s0, sf); R["save_info"] = save_info()
    g = first("GameManager"); cs = {}
    for p in ("_questManager._currentStep", "_questManager._currentStep.name", "_questManager._currentStep.Type", "_questManager._currentStep.Item.name", "_questManager._currentStep.Actor.name", "_questManager._currentStep.Dialogue"):
        for dp in (2, 1):
            v = rd(g, "GameManager", p, dp); cs[p + " d%d" % dp] = str(v)[:300]
            if not str(v).startswith("ERR") and "Exception" not in str(v): break
    R["currentStep_raw"] = cs; R["exc"] = exc_summary(off); dump()
    print("TOTAL", R["diff_total"], "exc", R["exc"]["total"], flush=True)
    for k, v in cs.items(): print(k, "=>", v)
except Storm as e:
    R["STORM"] = str(e); print("STORM", e, flush=True)
finally:
    autosync(False); dump()
