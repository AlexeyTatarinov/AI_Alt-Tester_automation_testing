# -*- coding: utf-8 -*-
# Play B, часть 1 (продолжение): разговор 4. Ошибка скрипта b1b: hint() был от котла, телепорта к BardHare не было
from s3blib import *
R = json.load(open(os.path.join(R2, "b1.json"), encoding="utf-8")); off = R["off"]
def dump(): jdump(os.path.join(R2, "b1.json"), R)
prestage("b1c"); autosync(True)
try:
    print("state", sname(gstate()), "inv_open", inv(), "dlg", dlg(), flush=True)
    if inv(): key("Tab", 0.1); time.sleep(1.5)
    snow = full_snap("перед разговором 4", off); print("now", snow["inv"], snow["quest"], snow["state"], flush=True)
    R["pre4_after_script_error"] = snow
    assert to_hare(), "нет подсказки у BardHare"
    R["step4"] = conv_yes(off, "4"); r = R["step4"]
    print("STEP4", r["first_line"], r["replies"], r["closed"], r["diff"], flush=True); dump()
    sf = full_snap("после E2E-01", off); R["snap_e2e01"] = sf; R["diff_total"] = diff(R["snap_start"], sf); R["save_info"] = save_info()
    g = first("GameManager"); cs = {}
    for p in ("_questManager._currentStep", "_questManager._currentStep.name", "_questManager._currentQuest", "_questManager._currentQuest.name"):
        cs[p] = str(rd(g, "GameManager", p, 1))[:300]
    R["currentStep_raw"] = cs; R["exc"] = exc_summary(off); dump()
    print("TOTAL", R["diff_total"], "exc", R["exc"]["total"], sf["inv"], sf["quest"], flush=True)
    for k, v in cs.items(): print(k, "=>", v)
finally:
    autosync(False); dump()
