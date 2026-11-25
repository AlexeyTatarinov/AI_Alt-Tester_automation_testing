import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); pre = preflight("t_guard"); print(pre.get("window_restore"), pre.get("game_pause_menu"))
print("pause before", guard.game_pause_menu())
key("Escape", 0.1); time.sleep(1.5); print("after esc (expect True)", guard.game_pause_menu())
print("before_case", guard.before_case("t"), "pause after", guard.game_pause_menu())
print(guard._state().get("game_pause_closed"), guard._state().get("window_restores"))
