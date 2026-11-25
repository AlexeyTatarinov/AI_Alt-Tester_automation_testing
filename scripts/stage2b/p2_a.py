# -*- coding: utf-8 -*-
from s2blib import *
R = {}
def dump(): jdump(os.path.join(R2, "p2_a.json"), R)
def talk_first(off, tag):
    n = 0; seq = []
    while n < 25:
        key("Space", 0.1); n += 1; time.sleep(1.0)
        l = line()
        if l and (not seq or seq[-1] != l): seq.append(l)
        if choices() or not dlg(): break
    time.sleep(1.5)
    return {"N_space": n, "closed": not dlg(), "replies": len(seq), "choices": choices(), "seq": seq}
def to_hare():
    for dist in (1.3, 1.0, 0.8):
        tp_hare(dist)
        for i in range(6):
            if hint(): return True
            step_towards(HARE, 0.2); time.sleep(0.4)
    return False
prestage("p2a")
R["frameCount0"] = d.get_static_property("UnityEngine.Time", "frameCount", CORE); assert R["frameCount0"] < 3000
assert "MainMenu" in scenes()
autosync(True)
try:
    guard.risky("p2 a")
    print("new_game", new_game(), now(), flush=True)
    for _ in range(20):
        time.sleep(1.5)
        try: ppos(); break
        except Exception: pass
    time.sleep(2)
    R["count_initial"] = alert_count_snap(); R["state_after_ng"] = sname(gstate()); print("COUNT", R["count_initial"], R["state_after_ng"], flush=True); dump()
    for _ in range(30):
        if gstate() == 0: break
        time.sleep(1)
    off = log_mark(); R["off"] = off
    s0 = snap("DLG-10b до", off); R["snap_start"] = s0; print(json.dumps(s0, ensure_ascii=False), flush=True)
    R["hint1"] = to_hare(); print("hint", R["hint1"], flush=True)
    key("E", 0.1); time.sleep(1.0); assert dlg(), "диалог не открылся"
    R["first"] = talk_first(off, "first")
    s1 = snap("после первого", off); R["snap_after_first"] = s1
    print("FIRST", {k: v for k, v in R["first"].items() if k != "seq"}, s1["quest"], s1["exc"], flush=True); dump()
    # второй: No
    R["hint2"] = to_hare(); print("hint2", R["hint2"], flush=True)
    sp = snap("перед вторым (No)", off); R["snap_before_no"] = sp
    key("E", 0.1); t0 = time.time()
    while time.time() - t0 < 3 and not dlg(): time.sleep(0.1)
    assert dlg(), "второй диалог не открылся"
    R["second_first_line"] = line(); n2 = 0
    while n2 < 4:
        key("Space", 0.1); n2 += 1; time.sleep(1.0)
        if choices() or not dlg(): break
    R["second"] = {"N_space": n2, "choices": choices(), "line": line()}
    assert choices(), "нет Yes/No"
    texts = [o.get_text() for o in d.find_objects(By.NAME, "TextChoice", enabled=True)]
    R["second"]["texts"] = texts; R["second"]["shot"] = shot("p2_choices"); print("choices", texts, flush=True)
    no_i = [i for i, t in enumerate(texts) if t.strip().lower() == "no"]; assert no_i, "нет кнопки No"
    bn = "ButtonChoice%d" % (no_i[0] + 1); R["second"]["clicked"] = bn
    d.find_object(By.NAME, bn, enabled=True).click(); time.sleep(2.0)
    lines = []
    for _ in range(10):
        if not dlg(): break
        l = line()
        if l and (not lines or lines[-1] != l): lines.append(l)
        key("Space", 0.1); time.sleep(1.2)
    R["second"]["after_no_lines"] = lines; time.sleep(2.0)
    R["second"]["dlg_closed"] = not dlg()
    sn = snap("после No", off); R["snap_after_no"] = sn; R["diff_no"] = diff(sp, sn); R["save_info_no"] = save_info()
    R["exc_no"] = exc_summary(off)
    print("NO diff", json.dumps(R["diff_no"], ensure_ascii=False), "closed", R["second"]["dlg_closed"], "state", sn["state"], flush=True); dump()
finally:
    autosync(False); dump()
