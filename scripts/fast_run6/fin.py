import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); pre = preflight("finish")
print("до возврата:", save_hashes() == bk_hashes())
ok = restore(); print("возврат из копии, хеши совпали:", ok, save_hashes())
d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, False)
asy = d.get_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS)
loc = None
for asm in ("Unity.Localization", "UnityEngine.Localization"):
    for path in ("SelectedLocale.Identifier.Code", "SelectedLocale.LocaleName"):
        try: loc = d.get_static_property("UnityEngine.Localization.Settings.LocalizationSettings", path, asm); break
        except Exception as e: pass
    if loc: break
try: j = json.load(open(SAVE0F, encoding="utf-8")); sloc = j.get("_currentLocale")
except Exception as e: sloc = str(e)
print("autoSync", asy, "locale runtime", loc, "save _currentLocale", sloc)
print("scenes", scenes(), "pigs", len(pigs()), "ts", d.get_static_property("UnityEngine.Time","timeScale",CORE), "pause", pause_open(), "inv", inv(), "dlg", dlg(), "runInBg", d.get_static_property("UnityEngine.Application","runInBackground",CORE))
print("flags", guard.read_console_flags(), "alive", guard.alive(), "window", {k: guard.unity_window().get(k) for k in ("iconic","responding")})
OFF = int(open("log_off_int03.txt").read()); lg = log_since(OFF); print("Editor.log за прогон:", {k: lg[k] for k in ("lines","exceptions","errors")})
st = json.load(open(guard.STATE_F, encoding="utf-8")); print("unpause_attempts", st.get("unpause_attempts"))
json.dump({"equal": ok, "hashes": save_hashes(), "autoSync": asy, "locale": loc, "save_locale": sloc, "log_run": lg}, open("final_state.json","w"), ensure_ascii=False, default=str, indent=1)
