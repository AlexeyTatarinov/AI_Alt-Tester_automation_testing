import sys, json
sys.path.insert(0, r"Test_Ai\scripts\fast_run7")
from r4lib import *
d=connect(); guard.restore_window("q1")
print("dlg", dlg(), "choices", choices(), "line", line(), "inv", inv())
print(json.dumps(json.load(open(r"Test_Ai\Reports_2026-11-21\results\run8_d01_20261124\d01_a.json",encoding="utf-8")).get("after_click_lines")), save_info())
