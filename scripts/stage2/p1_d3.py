from s2lib import *
R = json.load(open(os.path.join(R2, "p1_d.json"), encoding="utf-8")); off = R["off"]; s0 = R["snap_before"]
autosync(True)
try:
    seq = []; n = 0
    for _ in range(30):
        l = line()
        print(n, sname(gstate()), dlg(), choices(), (l or "")[:70], flush=True)
        if l and (not seq or seq[-1] != l): seq.append(l)
        if not dlg() and sname(gstate()) != "Dialogue": break
        if choices(): print("choices again"); break
        key("Space", 0.1); n += 1; time.sleep(1.3)
    time.sleep(3)
    R["after_yes_lines"] += [x for x in seq if x not in R["after_yes_lines"]]; R["closed"] = not dlg()
    s2 = snap("IT-12 после", off); R["snap_after"] = s2; R["diff"] = diff(s0, s2)
    R["save_info"] = save_info()
    g = first("GameManager"); R["quest_after"] = quest(); R["next_step_name"] = rd(g, "GameManager", "_questManager._currentStep.name")
    R["exc_detail"] = exc_summary(off)
    print("AFTER", json.dumps(s2, ensure_ascii=False)); print("DIFF", json.dumps(R["diff"], ensure_ascii=False)); print("next", R["next_step_name"], R["quest_after"])
    jdump(os.path.join(R2, "p1_d.json"), R)
finally:
    autosync(False)
