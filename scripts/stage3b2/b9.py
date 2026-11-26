# -*- coding: utf-8 -*-
# после Continue: разговор с BardHare и с Ayud (E2E-02 «разговор работает», IT-02c3 факты)
from s3blib import *
R = {}
def dump(): jdump(os.path.join(R2, "b9.json"), R)
b8 = json.load(open(os.path.join(R2, "b8.json"), encoding="utf-8")); off = json.load(open(os.path.join(R2, "b1.json"), encoding="utf-8"))["off"]; off2 = b8["off_after_continue"]
prestage("b9"); hyg_tick(R, "b9")
try:
    for who, loc, name in (("BardHare", "Beach", None), ("Ayud", "Field_Farms", "Ayud")):
        if loc not in scenes(): print("goto", goto(loc), flush=True); time.sleep(2); wait_play_ready()
        autosync(True)
        R[who] = converse(off, "после Continue: " + who, name); r = R[who]
        print(who, brief(r), r.get("seq"), flush=True); autosync(False); dump()
    R["exc_after_continue"] = exc_summary(off2); R["exc_total"] = exc_summary(off); R["save"] = save_items(); R["end"] = full_snap("конец Play B", off)
    print("exc after continue", R["exc_after_continue"]["total"], "total", R["exc_total"]["total"], R["end"], flush=True)
except Storm as e:
    R["STORM"] = str(e); print("STORM", e, flush=True)
finally:
    autosync(False); dump()
