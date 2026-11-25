# -*- coding: utf-8 -*-
# Play1: New Game (1 раз), IT-03
from s2lib import *
R = {}
prestage("p1a")
R["frameCount"] = d.get_static_property("UnityEngine.Time", "frameCount", CORE); assert R["frameCount"] < 3000
assert "MainMenu" in scenes()
autosync(True)
try:
    guard.risky("p1 a"); 
    print("new_game", new_game(), now(), flush=True)
    for _ in range(20):
        time.sleep(1.5)
        try: ppos(); break
        except Exception: pass
    time.sleep(3)
    print("state", sname(gstate()), scenes(), flush=True)
    # интро: ждём Gameplay
    for _ in range(30):
        if gstate() == 0: break
        time.sleep(1)
    R["intro_state_after"] = sname(gstate())
    off = log_mark(); R["off"] = off
    s0 = snap("IT-03 до", off); R["snap_before"] = s0; print(json.dumps(s0, ensure_ascii=False), flush=True)
    guard.restore_window("p1 tp"); tp_hare(1.3)
    for i in range(12):
        if hint(): break
        step_towards(HARE, 0.2); time.sleep(0.4)
    R["hint1"] = bool(hint()); R["dist1"] = round(dxz(ppos(), HARE), 2); print("hint", R["hint1"], R["dist1"], flush=True)
    key("E", 0.1); time.sleep(1.0); assert dlg(), "диалог не открылся"
    n = 0; seq = []
    while n < 25:
        key("Space", 0.1); n += 1; time.sleep(1.0)
        l = line()
        if l and (not seq or seq[-1] != l): seq.append(l)
        if choices(): R["choices_in_first"] = True; break
        if not dlg(): break
    time.sleep(1.5)
    R["first"] = {"N_space": n, "closed": not dlg(), "replies": len(seq), "seq": seq}
    s1 = snap("после первого разговора", off); R["snap_after_first"] = s1
    R["save_info_first"] = save_info()
    print("FIRST N", n, "closed", not dlg(), "replies", len(seq), "quest", s1["quest"], "exc", s1["exc"], flush=True)
    jdump(os.path.join(R2, "p1_a.json"), R)
    # второй разговор
    guard.restore_window("p1 second")
    for i in range(12):
        if hint(): break
        step_towards(HARE, 0.2); time.sleep(0.4)
    R["hint2"] = bool(hint())
    s_pre2 = snap("перед вторым", off); R["snap_before_second"] = s_pre2
    key("E", 0.1); t0 = time.time()
    while time.time() - t0 < 3 and not dlg(): time.sleep(0.1)
    assert dlg(), "второй диалог не открылся"
    R["second_first_line"] = line(); n2 = 0
    while n2 < 3:
        key("Space", 0.1); n2 += 1; time.sleep(1.0)
        if choices() or not dlg(): break
    R["second"] = {"N_space": n2, "choices": choices(), "line": line()}
    if choices():
        texts = [o.get_text() for o in d.find_objects(By.NAME, "TextChoice", enabled=True)]
        R["second"]["texts"] = texts
        R["second"]["shot"] = shot("p1_choices")
        print("choices", texts, flush=True)
        yes_i = [i for i, t in enumerate(texts) if t.strip().lower() == "yes"]
        bn = "ButtonChoice%d" % (yes_i[0] + 1 if yes_i else 1)
        R["second"]["clicked"] = bn
        d.find_object(By.NAME, bn, enabled=True).click(); time.sleep(2.0)
        for _ in range(12):
            if not dlg(): break
            key("Space", 0.1); time.sleep(1.2)
        time.sleep(2.5)
    R["second"]["dlg_closed"] = not dlg()
    s2 = snap("IT-03 после", off); R["snap_after"] = s2; R["diff"] = diff(s0, s2)
    R["save_info_after"] = save_info()
    print("AFTER", json.dumps(s2, ensure_ascii=False), flush=True); print("DIFF", json.dumps(R["diff"], ensure_ascii=False), flush=True)
    R["exc_detail"] = exc_summary(off)
    jdump(os.path.join(R2, "p1_a.json"), R)
finally:
    autosync(False)
