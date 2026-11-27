import os, sys, json
sys.path.insert(0, r"Test_Ai\scripts\fast_run7")
from r4lib import *
OUT = r"Test_Ai\Reports_2026-11-21\results\run11_reg_20261124"
d = connect(); preflight("s16"); R = {}
phase = sys.argv[1] if len(sys.argv) > 1 else "set"
def vals(): return [o.get_text() for o in d.find_objects(By.PATH, "//Audio_Panel//CurrentOption", enabled=True)]
def open_settings():
    d.find_object(By.NAME, "Button Settings ", enabled=False).click(); time.sleep(1.5)
if phase == "set":
    open_settings(); R["before"] = vals()
    prev = d.find_objects(By.PATH, "//Audio_Panel//ButtonPrevious", enabled=True)
    for _ in range(5): prev[0].click(); time.sleep(0.3)
    for _ in range(3): prev[1].click(); time.sleep(0.3)
    R["after_change"] = vals(); shot("s16_changed")
    d.find_object(By.NAME, "SaveButton", enabled=True).click(); time.sleep(1.0)
    d.find_object(By.NAME, "Button Close", enabled=True).click(); time.sleep(1.0)
    open_settings(); R["reopened_same_session"] = vals(); shot("s16_reopened")
else:
    open_settings(); R["after_restart"] = vals(); shot("s16_after_restart")
    d.find_object(By.NAME, "Button Close", enabled=True).click()
R["save_hash"] = save_info().get("hash")
json.dump(R, open(os.path.join(OUT, "s16_%s.json" % phase), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(R)
