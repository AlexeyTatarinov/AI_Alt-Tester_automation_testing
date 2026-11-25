import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("state")
print("dlg", dlg(), "choices", choices(), "line", line(), "pause", pause_open(), "state", pstate(), "ts", d.get_static_property("UnityEngine.Time","timeScale",CORE))
print(shot("state_now"))
for o in d.find_objects(By.COMPONENT, "TMPro.TextMeshProUGUI", enabled=True):
    try:
        t = o.get_component_property("TMPro.TextMeshProUGUI","text","Unity.TextMeshPro")
        if t and t.strip(): print(o.name, "|", t.strip()[:80])
    except Exception: pass
print(exc_summary(json.load(open("s6_before.json"))["log0"]))
