# -*- coding: utf-8 -*-
from s2lib import *
R = json.load(open(os.path.join(R2, "p1_a.json"), encoding="utf-8")); off = R["off"]; s0 = R["snap_before"]
autosync(True)
try:
    assert hint(), "нет подсказки"
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
        R["second"]["texts"] = texts; R["second"]["shot"] = shot("p1_choices"); print("choices", texts, flush=True)
        yes_i = [i for i, t in enumerate(texts) if t.strip().lower() == "yes"]
        bn = "ButtonChoice%d" % (yes_i[0] + 1 if yes_i else 1); R["second"]["clicked"] = bn
        d.find_object(By.NAME, bn, enabled=True).click(); time.sleep(2.0)
        lines = []
        for _ in range(14):
            if not dlg(): break
            l = line()
            if l and (not lines or lines[-1] != l): lines.append(l)
            key("Space", 0.1); time.sleep(1.2)
        R["second"]["after_yes_lines"] = lines
        time.sleep(2.5)
    R["second"]["dlg_closed"] = not dlg()
    s2 = snap("IT-03 после", off); R["snap_after"] = s2; R["diff"] = diff(s0, s2)
    R["diff_second_only"] = diff(s_pre2, s2)
    R["save_info_after"] = save_info()
    print("AFTER", json.dumps(s2, ensure_ascii=False)); print("DIFF", json.dumps(R["diff"], ensure_ascii=False)); print("SECOND", json.dumps(R["second"], ensure_ascii=False)[:1500])
    R["exc_detail"] = exc_summary(off)
    jdump(os.path.join(R2, "p1_b.json"), R)
finally:
    autosync(False)
