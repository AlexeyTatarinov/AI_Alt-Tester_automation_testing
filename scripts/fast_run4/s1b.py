import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); pre = preflight("s1b")
print("scenes", scenes(), "pos", ppos())
print("hash==bk", save_hashes()==bk_hashes())
t = to_menu(); print("to_menu", t, scenes()); time.sleep(4.0)
for n in ("Button New Game","Button Continue"):
    try: o=d.find_object(By.NAME,n,enabled=False); print(n,"found")
    except Exception as e: print(n,"no")
print(shot("s1b_menu"))
