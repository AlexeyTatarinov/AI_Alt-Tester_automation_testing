# -*- coding: utf-8 -*-
# d02 этап 3: restore save -> Back to menu -> CONTINUE
import os, sys, json
sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\fast_run7")
from r4lib import *
OUT = r"C:\Users\Aotat\Desktop\Test_Ai\Reports_2026-11-21\results\run8_d02_20261124"
d = connect(); pre = preflight("d02c"); R = {"start": now()}
def dump(): json.dump(R, open(os.path.join(OUT, "d02_c.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
assert not dlg()
R["save_before_restore"] = save_info()["hash"]
R["restore1"] = restore(); R["hash_after_restore1"] = save_info()["hash"]
off = log_mark()
R["to_menu_s"] = to_menu(); time.sleep(2.5); print("to_menu", R["to_menu_s"], flush=True)
R["hash_after_menu"] = save_info()["hash"]; R["finished_in_menu"] = save_info()["finished"]
R["restore2_in_menu"] = restore(); R["hash_after_restore2"] = save_info()["hash"]
btns = []
for o in d.find_objects(By.COMPONENT, "UnityEngine.UI.Button", enabled=False):
    try: btns.append((o.name, o.enabled))
    except Exception: pass
R["buttons"] = btns; print("buttons", btns, flush=True); dump()
