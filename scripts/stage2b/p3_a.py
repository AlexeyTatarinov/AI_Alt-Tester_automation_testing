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
prestage("p3a")
R["frameCount0"] = d.get_static_property("UnityEngine.Time", "frameCount", CORE); assert R["frameCount0"] < 3000
assert "MainMenu" in scenes()
autosync(True)
try:
    guard.risky("p3 a")
    print("new_game", new_game(), now(), flush=True)
    for _ in range(20):
        time.sleep(1.5)
        try: ppos(); break
        except Exception: pass
    time.sleep(2)
    R["count_initial"] = alert_count_snap(); print("COUNT", R["count_initial"], flush=True); dump()
    for _ in range(30):
        if gstate() == 0: break
        time.sleep(1)
    off = log_mark(); R["off"] = off
    s0 = snap("E2E старт", off); R["snap_start"] = s0; print(json.dumps(s0, ensure_ascii=False), flush=True)
    # 1 первый разговор
    to_hare(); key("E", 0.1); time.sleep(1.0); assert dlg()
    n = 0; seq = []
    while n < 25:
        key("Space", 0.1); n += 1; time.sleep(1.0)
        l = line()
        if l and (not seq or seq[-1] != l): seq.append(l)
        if choices() or not dlg(): break
    time.sleep(1.5)
    s1 = snap("1 после первого", off); R["step1"] = {"N": n, "replies": len(seq), "closed": not dlg(), "snap": s1}
    print("STEP1", n, len(seq), not dlg(), s1["quest"], s1["save_hash"], s1["save_finished"], s1["exc"], flush=True); dump()
    # 2 второй, Yes
    R["step2"] = conv_yes(off, "2"); r = R["step2"]
    print("STEP2", r["replies"], r["closed"], r["diff"], flush=True); dump()
    R["exc"] = exc_summary(off); dump()
finally:
    autosync(False); dump()
