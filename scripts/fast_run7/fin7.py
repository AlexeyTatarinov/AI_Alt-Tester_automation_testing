import os, sys, json; sys.stdout.reconfigure(encoding="utf-8"); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); pre = preflight("finish")
print("до возврата равны копии:", save_hashes() == bk_hashes())
ok = restore(); print("возврат из копии, хеши совпали:", ok, save_hashes())
d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, False)
print("autoSync", d.get_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS))
loc = None
for asm in ("Unity.Localization", "UnityEngine.Localization"):
    for path in ("SelectedLocale.Identifier.Code", "SelectedLocale.LocaleName"):
        try: loc = d.get_static_property("UnityEngine.Localization.Settings.LocalizationSettings", path, asm); break
        except Exception: pass
    if loc: break
try: sloc = json.load(open(SAVE0F, encoding="utf-8")).get("_currentLocale")
except Exception as e: sloc = str(e)
print("locale runtime", loc, "save _currentLocale", sloc)
print("scenes", scenes(), "pause", pause_open(), "dlg", dlg(), "ts", d.get_static_property("UnityEngine.Time","timeScale",CORE))
print("flags", guard.read_console_flags()[0], "alive", guard.alive()[0], "iconic", guard.unity_window().get("iconic"))
OFF = int(open("l10n_off.txt").read()); lg = log_since(OFF); print("Editor.log с l10n:", {k: lg[k] for k in ("lines","exceptions","errors")})
