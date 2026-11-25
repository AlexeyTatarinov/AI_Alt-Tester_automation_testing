# -*- coding: utf-8 -*-
from s2blib import *
R = {}
def dump(): jdump(os.path.join(R2, "p3_a.json"), R)
def to_hare():
    for dist in (1.3, 1.0, 0.8):
        tp_hare(dist)
        for i in range(6):
            if hint(): return True
            step_towards(HARE, 0.2); time.sleep(0.4)
    return False
def conv_yes(off, tag, maxsp=30):
    ok = to_hare(); r = {"hint": ok}
    sp = snap(tag + " до", off); r["before"] = sp
    key("E", 0.1); t0 = time.time()
    while time.time() - t0 < 3 and not dlg(): time.sleep(0.1)
    assert dlg(), "диалог не открылся"
    n = 0; seq = []
    while n < 4:
        key("Space", 0.1); n += 1; time.sleep(1.0)
        l = line()
        if l and (not seq or seq[-1] != l): seq.append(l)
        if choices() or not dlg(): break
    r["first_line"] = seq[0] if seq else None
    assert choices(), "нет Yes/No"
    texts = [o.get_text() for o in d.find_objects(By.NAME, "TextChoice", enabled=True)]; r["texts"] = texts
    yi = [i for i, t in enumerate(texts) if t.strip().lower() == "yes"]; assert yi
    d.find_object(By.NAME, "ButtonChoice%d" % (yi[0] + 1), enabled=True).click(); time.sleep(2.0)
    k = 0
    while k < maxsp and dlg():
        l = line()
        if l and (not seq or seq[-1] != l): seq.append(l)
        key("Space", 0.1); time.sleep(1.2); k += 1
    time.sleep(2.5)
    r["replies"] = len(seq); r["seq"] = seq; r["closed"] = not dlg()
    sa = snap(tag + " после", off); r["after"] = sa; r["diff"] = diff(sp, sa)
    return r

R = json.load(open(os.path.join(R2, "p3_a.json"), encoding="utf-8")); off = R["off"]
def dump(): jdump(os.path.join(R2, "p3_c.json"), R)
autosync(True)
try:
    R["step4"] = conv_yes(off, "4"); r = R["step4"]
    print("STEP4", r["first_line"], r["replies"], r["closed"], r["diff"], flush=True); dump()
    time.sleep(1)
    g = first("GameManager"); cs = {}
    for p in ("_questManager._currentStep", "_questManager._currentStep.name", "_questManager._currentStep.Type", "_questManager._currentStep.type", "_questManager._currentStep.StepType", "_questManager._currentStep.Item.name", "_questManager._currentStep.Dialogue"):
        for dp in (2, 1):
            v = rd(g, "GameManager", p, dp); cs[p + " d%d" % dp] = str(v)[:300]
            if not str(v).startswith("ERR") and "Exception" not in str(v): break
    R["currentStep_raw"] = cs; R["quest_now"] = quest(); R["exc"] = exc_summary(off); dump()
    for k, v in cs.items(): print(k, "=>", v)
    print("quest", R["quest_now"], "exc", R["exc"]["total"], flush=True)
finally:
    autosync(False); dump()
