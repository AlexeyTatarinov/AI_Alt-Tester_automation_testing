# -*- coding: utf-8 -*-
import os, sys, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("s1_inv")
off = log_mark()
if not len(d.find_objects(By.NAME, "CheatMenu", enabled=True)): key("C", 0.1); time.sleep(1)
b = d.find_objects(By.PATH, "//CheatMenu/*", enabled=False)[0]; b.click(); t0 = time.time(); time.sleep(4)
while time.time() - t0 < 60:
    try:
        if "Beach" in scenes() and pig(): break
    except Exception: pass
    time.sleep(1)
time.sleep(3); print("scenes", scenes(), "pos", ppos())
if len(d.find_objects(By.NAME, "CheatMenu", enabled=True)): key("C", 0.1); time.sleep(1)
print("cheat open:", len(d.find_objects(By.NAME, "CheatMenu", enabled=True)))
key("Tab", 0.1); time.sleep(1.5); print("inv open", inv(), "tab", tab_type())
print(shot("s1_inv_open"))
print("tabs", json.dumps(all_tabs(), ensure_ascii=False))
print("action button", action_button()[1])
print("save", save_info())
key("Tab", 0.1); time.sleep(1); print("inv open after close", inv())
print(log_since(off))
