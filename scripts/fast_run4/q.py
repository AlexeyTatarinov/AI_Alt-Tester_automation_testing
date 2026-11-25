import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect()
print("scenes", scenes(), "pause", pause_open(), "hash==bk", save_hashes()==bk_hashes())
print(save_hashes())
for n in ("Button New Game","Button Continue","BackToMenuButton","PopupButton - 1"):
    try: o=d.find_object(By.NAME,n,enabled=False); print(n,"found", o.enabled)
    except Exception as e: print(n,"no")
try: print("pos", ppos())
except Exception as e: print("pos err", e)
