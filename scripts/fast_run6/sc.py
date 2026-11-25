import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect()
print("scenes", scenes(), "pigs", len(pigs()), "dlg", dlg(), "pause", pause_open())
print(shot("after_r2_now"))
