import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect()
try:
    d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, False)
    print("autoSync", d.get_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS))
except Exception as e: print("autoSync err", type(e).__name__, str(e)[:100])
try: print("lang", lang_cur() if 'lang_cur' in globals() else None, "dlg", dlg(), "pause", pause_open(), "scenes", scenes())
except Exception as e: print("state err", type(e).__name__)
print("hash live before restore", save_hashes() == bk_hashes())
print("restore ok:", restore())
print("live", save_hashes()); print("bk", bk_hashes())
