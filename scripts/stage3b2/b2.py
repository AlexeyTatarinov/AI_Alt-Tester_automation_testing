# -*- coding: utf-8 -*-
# 4.2 E2E-01b: Ayud
from s3blib import *
R = {}
def dump(): jdump(os.path.join(R2, "b2.json"), R)
off = json.load(open(os.path.join(R2, "b1.json"), encoding="utf-8"))["off"]; R["off"] = off
prestage("b2"); autosync(True)
try:
    hyg_tick(R, "b2")
    R["start"] = full_snap("E2E-01b старт", off); print(R["start"], flush=True)
    R["S1"] = converse(off, "S1-Q1-QL2", "Ayud"); print("S1", brief(R["S1"]), R["S1"].get("seq"), flush=True); dump()
    R["S2"] = converse(off, "S2-Q1-QL2", "Ayud"); print("S2", brief(R["S2"]), R["S2"].get("seq"), flush=True); dump()
    g = first("GameManager"); nx = {}
    for p in ("_name", "name", "Actor.name", "Type", "Item.name", "IsDone"):
        nx[p] = str(rd(g, "GameManager", "_questManager._currentQuestline.Quests[1].Steps[0]." + p, 1))[:120]
    nx["quest1_done"] = str(rd(g, "GameManager", "_questManager._currentQuestline.Quests[0].IsDone", 1))[:80]
    nx["questline"] = str(rd(g, "GameManager", "_questManager._currentQuestline.name", 1))[:80]
    R["next_step"] = nx; R["end"] = full_snap("E2E-01b конец", off); R["save_info"] = save_info(); R["exc"] = exc_summary(off)
    print("NEXT", nx, "\nEND", R["end"], "exc", R["exc"]["total"], flush=True)
finally:
    autosync(False); dump()
