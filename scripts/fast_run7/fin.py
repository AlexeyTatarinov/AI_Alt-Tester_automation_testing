import os, sys, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); pre = preflight("fin")
print("start", now(), "to_menu", to_menu(), scenes())
print("restore", restore(), "equal", save_hashes() == bk_hashes())
print(save_hashes())
time.sleep(1)
print("autoSync", d.get_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS))
print("pause open", pause_open(), "dlg", dlg(), "cheat", len(d.find_objects(By.NAME,"CheatMenu",enabled=True)))
try: print("lang", d.get_static_property("UnityEngine.Localization.Settings.LocalizationSettings", "SelectedLocale", "Unity.Localization"))
except Exception as e: print("lang err", type(e).__name__)
for o in d.find_objects(By.COMPONENT, "TMPro.TextMeshProUGUI", enabled=True)[:12]:
    try: print("txt", o.get_component_property("TMPro.TextMeshProUGUI","text","Unity.TextMeshPro")[:40])
    except Exception: pass
print("flags", guard.read_console_flags(), "window", guard.unity_window().get("iconic"))
