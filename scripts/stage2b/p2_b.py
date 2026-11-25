# -*- coding: utf-8 -*-
from s2blib import *
R = json.load(open(os.path.join(R2, "p2_a.json"), encoding="utf-8")); off = R["off"]
def dump(): jdump(os.path.join(R2, "p2_b.json"), R)
def to_hare():
    for dist in (1.3, 1.0, 0.8):
        tp_hare(dist)
        for i in range(6):
            if hint(): return True
            step_towards(HARE, 0.2); time.sleep(0.4)
    return False
autosync(True)
try:
    R["hint3"] = to_hare(); assert R["hint3"]
    sp = snap("перед повтором", off); R["snap_before_again"] = sp
    key("E", 0.1); t0 = time.time()
    while time.time() - t0 < 3 and not dlg(): time.sleep(0.1)
    R["again_open"] = dlg(); assert dlg(), "диалог не открылся"
    R["again_first_line"] = line(); n = 0
    while n < 4:
        key("Space", 0.1); n += 1; time.sleep(1.0)
        if choices() or not dlg(): break
    R["again"] = {"N_space": n, "choices": choices(), "line": line()}
    if choices():
        texts = [o.get_text() for o in d.find_objects(By.NAME, "TextChoice", enabled=True)]
        R["again"]["texts"] = texts; print("choices", texts, flush=True)
        yi = [i for i, t in enumerate(texts) if t.strip().lower() == "yes"]; assert yi
        bn = "ButtonChoice%d" % (yi[0] + 1); R["again"]["clicked"] = bn
        d.find_object(By.NAME, bn, enabled=True).click(); time.sleep(2.0)
        lines = []
        for _ in range(14):
            if not dlg(): break
            l = line()
            if l and (not lines or lines[-1] != l): lines.append(l)
            key("Space", 0.1); time.sleep(1.2)
        R["again"]["after_yes_lines"] = lines; time.sleep(2.5)
    R["again"]["dlg_closed"] = not dlg()
    s2 = snap("после Yes", off); R["snap_after_yes"] = s2; R["diff_yes"] = diff(sp, s2); R["save_info_yes"] = save_info()
    R["exc_detail"] = exc_summary(off)
    print("YES diff", json.dumps(R["diff_yes"], ensure_ascii=False), "closed", R["again"]["dlg_closed"], "exc", s2["exc"], flush=True)
    print(json.dumps(R["again"], ensure_ascii=False)[:600]); dump()
finally:
    autosync(False); dump()
