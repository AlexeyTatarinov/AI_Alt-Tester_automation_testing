# часть 2 E2E-01: разговор 4 (hint() у котла был ещё включён, поэтому E ушло в котёл)
from g6 import *
R = json.load(open(os.path.join(R2, "a1.json"), encoding="utf-8")); off = R["off"]
def dump(): jdump(os.path.join(R2, "a1.json"), R)
prestage("a1b"); autosync(True)
try:
    print("state", sname(gstate()), panels(), qdetail(), flush=True)
    if inv(): key("Tab", 0.1); time.sleep(1.5)
    assert gstate() == 0 and not dlg()
    assert to_hare(), "нет подсказки у BardHare"
    R["step4"] = conv_yes(off, "4"); r = R["step4"]
    print("STEP4", r["first_line"], r["replies"], r["closed"], r["diff"], flush=True)
    sf = full_snap("после E2E-01", off); R["snap_e2e01"] = sf; R["diff_total"] = diff(R["snap_start"], sf)
    R["q"] = qdetail(); R["exc"] = exc_summary(off); print("TOTAL", R["diff_total"], R["q"], "exc", R["exc"]["total"], flush=True)
finally:
    autosync(False); dump()
