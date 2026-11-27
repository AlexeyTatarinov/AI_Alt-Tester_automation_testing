# -*- coding: utf-8 -*-
"""stage8: из MainMenu начать новую игру, чтобы collect.py мог ходить по меню читов."""
import os, sys, time
os.environ.setdefault("MOD_OUT", r"Test_Ai\Reports_2026-11-21\results\stage8_levels")
sys.path.insert(0, r"Test_Ai\scripts\modules")
from elib import *

new_game_from_menu()
time.sleep(25)   # интро на пляже
print(scenes())
