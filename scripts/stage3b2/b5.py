# -*- coding: utf-8 -*-
# 4.3.4 записи в Beach после пешего перехода
from s3blib import *
R = {}
def dump(): jdump(os.path.join(R2, "b5.json"), R)
off = json.load(open(os.path.join(R2, "b1.json"), encoding="utf-8"))["off"]
prestage("b5"); hyg_tick(R, "b5"); autosync(True)
try:
    R["arrive"] = full_snap("Beach после пешего перехода", off); R["hp"] = hp_now(); print(R["arrive"], R["hp"], flush=True)
    key("Tab", 0.1); time.sleep(1.5); R["tab_opens"] = inv(); R["state_in_tab"] = sname(gstate())
    if inv(): key("Tab", 0.1); time.sleep(1.5)
    print("tab", R["tab_opens"], R["state_in_tab"], flush=True)
    R["talk"] = converse(off, "Beach BardHare"); r = R["talk"]
    print("TALK", brief(r), r.get("seq"), flush=True)
    R["end"] = full_snap("после разговора", off); R["save_info"] = save_info(); R["exc"] = exc_summary(off); print("exc", R["exc"]["total"], flush=True)
finally:
    autosync(False); dump()
