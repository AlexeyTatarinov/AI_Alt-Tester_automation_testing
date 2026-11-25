from s2lib import *
R = json.load(open(os.path.join(R2, "p1_d.json"), encoding="utf-8")); off = R["off"]; s0 = R["snap_before"]
autosync(True)
try:
    assert choices()
    texts = [o.get_text() for o in d.find_objects(By.NAME, "TextChoice", enabled=True)]; R["choice_texts"] = texts; print(texts)
    yes_i = [i for i, t in enumerate(texts) if t.strip().lower() == "yes"]
    bn = "ButtonChoice%d" % (yes_i[0] + 1); R["clicked"] = bn
    d.find_object(By.NAME, bn, enabled=True).click(); time.sleep(2.0)
    seq = []
    for _ in range(25):
        if not dlg(): break
        l = line()
        if l and (not seq or seq[-1] != l): seq.append(l)
        key("Space", 0.1); time.sleep(1.2)
    time.sleep(2.5)
    R["after_yes_lines"] = seq; R["closed"] = not dlg()
    s2 = snap("IT-12 после", off); R["snap_after"] = s2; R["diff"] = diff(s0, s2)
    R["save_info"] = save_info()
    g = first("GameManager"); R["next_step_name"] = rd(g, "GameManager", "_questManager._currentStep.name")
    R["exc_detail"] = exc_summary(off)
    print(seq, "closed", R["closed"]); print("AFTER", json.dumps(s2, ensure_ascii=False)); print("DIFF", json.dumps(R["diff"], ensure_ascii=False)); print("next", R["next_step_name"])
    jdump(os.path.join(R2, "p1_d.json"), R)
finally:
    autosync(False)
