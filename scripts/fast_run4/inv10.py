import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("inv10")
if dlg(): raise SystemExit("диалог ещё открыт")
if inv(): key("Tab", 0.1); time.sleep(1.0)   # Y на последней вкладке (Recipe) не листает дальше, поэтому закрыть и открыть заново: откроется на вкладке 1
key("Tab", 0.1); time.sleep(1.2)
o = {"inv_open": inv(), "tab": tab_type()}
tabs = all_tabs(); o["all_tabs"] = tabs; print("ALL TABS", json.dumps(tabs, ensure_ascii=False, default=str))
key("Tab", 0.1); time.sleep(1.0); key("Tab", 0.1); time.sleep(1.2)
use = None
for _ in range(6):
    time.sleep(0.5); sl = slots(); print("tab", tab_type(), [(n,a,at) for _,n,a,at in sl])
    cand = [x for x in sl if x[3] == 1 and x[2] >= 2]
    if cand: use = (cand[0], sl); break
    key("Y", 0.1); time.sleep(1.0)
if not use:
    key("Tab", 0.1); raise SystemExit("нет Use-предмета")
(slot, name, amt0, at), sl = use
others = [x for x in sl if x[0].id != slot.id]
for _ in range(2):
    if others: others[0][0].click(); time.sleep(0.5)
    slot.click(); time.sleep(0.5)
before = next((x[2] for x in slots() if x[1] == name), None)
print("item", name, "before", before, "tab", tab_type(), "others", len(others))
shot("inv10b_before_Q")
guard.risky("INV-10 Q (после диалога)")
h0 = save_hashes(); off = log_mark()
key("Q", 0.1); time.sleep(1.0)
a1 = next((x[2] for x in slots() if x[1] == name), None); time.sleep(2.0)
a3 = next((x[2] for x in slots() if x[1] == name), None)
lg = log_since(off); h1 = save_hashes(); al = guard.alive()
shot("inv10b_after_Q")
print("after 1s", a1, "after 3s", a3, "log", lg, "save changed", h0 != h1, "alive", al)
if inv(): key("Tab", 0.1); time.sleep(1.0)
print("inv closed", not inv())
a = approach_step("A", 0.3, 0.6); print("step", a["moved_m"])
json.dump({"item": name, "before": before, "a1": a1, "a3": a3, "log": lg, "tabs": tabs, "step": a["moved_m"], "closed": not inv(), "save_changed": h0 != h1, "alive": al[0]}, open("inv10_res.json","w"), ensure_ascii=False, default=str)
