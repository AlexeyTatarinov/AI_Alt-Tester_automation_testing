# -*- coding: utf-8 -*-
# факты о залипшем Dialogue после Continue
from s3blib import *
import re
R = {}
def dump(): jdump(os.path.join(R2, "b10.json"), R)
b8 = json.load(open(os.path.join(R2, "b8.json"), encoding="utf-8")); off2 = b8["off_after_continue"]
prestage("b10")
def snapst(label):
    r = {"t": now(), "label": label, "state": sname(gstate()), "panel": dlg(), "choices": choices(), "hint": hint(), "pos": [round(v, 2) for v in ppos()], "scenes": scene_now()}
    R.setdefault("trace", []).append(r); print(r, flush=True); dump(); return r
try:
    snapst("сейчас")
    d.get_png_screenshot(os.path.join(R2, "shots", "stuck_dialogue.png"))
    autosync(True)
    ok, tries = approach("Ayud"); R["ayud_hint"] = ok; snapst("у Ayud")
    key("E", 0.1); time.sleep(2.0); snapst("после E")
    key("Space", 0.1); time.sleep(1.5); snapst("после Space")
    autosync(False)
    a = ppos(); key("W", 0.6); time.sleep(0.8); b = ppos(); R["moved_W"] = round(dxz(a, b), 2); snapst("после W")
    key("Tab", 0.1); time.sleep(1.5); R["tab_opens"] = inv(); snapst("после Tab")
    if inv(): key("Tab", 0.1); time.sleep(1.5); snapst("после 2-го Tab")
    key("Escape", 0.1); time.sleep(1.5); R["pause_opens"] = pause_open(); snapst("после Esc")
    if pause_open(): key("Escape", 0.1); time.sleep(1.5); snapst("после 2-го Esc")
finally:
    autosync(False)
    t = open(EDLOG, "rb"); t.seek(off2); L = t.read().decode("utf-8", "replace").splitlines(); t.close()
    err = [l[:200] for l in L if "AltTester" not in l and re.search(r"Exception|^\s*(Error|Assertion)|MissingReference|NullReference", l)]
    R["log_error_lines"] = err[:40]; R["log_error_n"] = len(err); dump()
    print("moved", R.get("moved_W"), "tab", R.get("tab_opens"), "pause", R.get("pause_opens"), "log errors", len(err), err[:8])
