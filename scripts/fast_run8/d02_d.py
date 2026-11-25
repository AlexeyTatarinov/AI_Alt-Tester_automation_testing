# -*- coding: utf-8 -*-
# d02 этап 3б: CONTINUE, диалог у BardHare
import os, sys, json
sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\fast_run7")
from r4lib import *
OUT = r"C:\Users\Aotat\Desktop\Test_Ai\Reports_2026-11-21\results\run8_d02_20261124"
d = connect(); pre = preflight("d02d"); R = {"start": now()}
def dump(): json.dump(R, open(os.path.join(OUT, "d02_d.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
d.set_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS,True)
def seeds(): return save_info().get("stacks", {}).get("42396f")
try:
    assert "MainMenu" in scenes()
    R["save_before"] = save_info(); off = log_mark()
    t0 = time.time(); d.find_object(By.NAME, "Button Continue", enabled=False).click()
    for _ in range(10):
        time.sleep(0.4)
        try: d.find_object(By.NAME, "PopupButton - 1", enabled=False).click(); R["popup_clicked"] = True; break
        except Exception: pass
    found = None
    while time.time() - t0 < 60:
        try:
            if "Beach" in scenes() and pig(): found = round(time.time() - t0, 1); break
        except Exception: pass
        time.sleep(0.3)
    R["load_s"] = found; R["scenes"] = scenes(); print("continue loaded", found, R["scenes"], flush=True)
    time.sleep(3)
    for _ in range(20):
        try: R["pos"] = ppos(); break
        except Exception: time.sleep(1.5)
    R["spawn_dist_to_hare"] = round(dxz(R["pos"], HARE), 1) if R.get("pos") else None
    R["save_after_load"] = save_info(); R["exc_load"] = exc_summary(off); R["inv_after_load"] = inv_snapshot()
    print("pos", R.get("pos"), "finished", R["save_after_load"]["finished"], "stacks", R["save_after_load"]["stacks"], "exc", R["exc_load"]["total"], flush=True)
    print("inv", R["inv_after_load"], flush=True); dump()
    if not found: raise SystemExit("игра не загрузилась")
    tp_hare(1.3)
    for i in range(12):
        if hint(): break
        step_towards(HARE, 0.2); time.sleep(0.4)
    R["hint"] = hint(); print("hint", R["hint"], round(dxz(ppos(), HARE), 2), flush=True)
    guard.risky("d02 continue conv"); off2 = log_mark()
    key("E", 0.1); time.sleep(1.0); R["open"] = dlg(); R["first_line"] = line(); print("open", R["open"], R["first_line"], flush=True)
    assert dlg()
    n = 0; seq = []
    while n < 45:
        key("Space", 0.1); n += 1; time.sleep(1.0)
        l = line()
        if l and (not seq or seq[-1] != l): seq.append(l)
        if choices() or not dlg(): break
    R["conv"] = {"N": n, "replies": len(seq), "closed": not dlg(), "choices": choices(), "seq": seq}
    if choices(): R["conv"]["texts"] = [o.get_text() for o in d.find_objects(By.NAME, "TextChoice", enabled=True)]
    print("conv", {k: v for k, v in R["conv"].items() if k != "seq"}, flush=True)
    for s in seq: print("  -", s[:100])
    time.sleep(2)
    R["exc_conv"] = exc_summary(off2); R["exc_all"] = exc_summary(off); R["save_after_conv"] = save_info()
    print("exc", R["exc_all"]["total"], R["exc_all"]["by_type"], "finished", R["save_after_conv"]["finished"], flush=True)
    for k, v in R["exc_all"]["first_stacks"].items(): print(k, v[:4])
finally:
    d.set_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS,False); dump()
