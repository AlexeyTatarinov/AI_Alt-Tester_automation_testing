# -*- coding: utf-8 -*-
from s2blib import *
R = {}
def dump(): jdump(os.path.join(R2, "p2_d.json"), R)
autosync(True)
try:
    off = log_mark(); R["off"] = off
    R["dlg_before"] = dlg(); R["choices_before"] = choices(); R["line_before"] = line(); R["state_before"] = sname(gstate())
    s0 = snap("DLG-11 до", off); R["snap_before"] = s0; print("before", R["dlg_before"], R["choices_before"], R["line_before"], R["state_before"], flush=True)
    guard.risky("p2 Q dialog")
    steps = []
    for i in range(3):
        key("Q", 0.1); time.sleep(1.2)
        steps.append({"i": i + 1, "dlg": dlg(), "choices": choices(), "line": line(), "state": sname(gstate()), "pause": pause_open(), "inv": inv_open()})
        print(steps[-1], flush=True)
    R["steps"] = steps; time.sleep(1.5)
    s1 = snap("DLG-11 после", off); R["snap_after"] = s1; R["diff"] = diff(s0, s1)
    R["exc"] = exc_summary(off)
    # поиск UIActionButton в логе
    f = open(EDLOG, "rb"); f.seek(off); t = f.read().decode("utf-8", "replace"); f.close()
    R["uiaction_in_log"] = "UIActionButton" in t; R["nre_in_log"] = "NullReferenceException" in t
    print("diff", R["diff"], "exc", R["exc"]["total"], R["exc"]["by_type"], "UIActionButton", R["uiaction_in_log"], flush=True)
    for k, v in R["exc"]["first_stacks"].items(): print(k, v[:5])
    R["shot"] = shot("p2_after_q")
finally:
    autosync(False); dump()
