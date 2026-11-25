import sys; sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\modules")
from elib import *
try: autosync(False)
except Exception as e: print("autosync err", e)
print("autoSync now", d.get_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS))
print("runInBackground", d.get_static_property("UnityEngine.Application","runInBackground",CORE))
try:
    to_gameplay(2)
except Exception as e: print("tg", e)
print("to_menu", to_menu()); time.sleep(3)
print("restore ok:", restore())
print("hashes == backup:", save_hashes()==bk_hashes())
print(scenes(), "window iconic", guard.unity_window().get("iconic"), "consoleFlags ok")
st=guard._state(); print("window_restores", st.get("window_restores"), "unpause", st.get("unpause_attempts"))
