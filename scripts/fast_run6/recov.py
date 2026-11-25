import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect()
print("pigs", len(pigs()), "pos", ppos() if pigs() else None, "scenes", scenes(), "pause", pause_open(), "dlg", dlg())
print("flags", guard.read_console_flags(), "alive", guard.alive())
