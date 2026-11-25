# -*- coding: utf-8 -*-
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from l10n_lib import *
d = connect(); R = {}
print("lang", lang_cur())
shot("l10n_italiano_settings")
R["it_settings"] = read_texts()
# закрыть настройки -> меню паузы на итальянском
d.find_object(By.NAME, "Button Close", enabled=True).click(); time.sleep(1.2)
R["it_pause"] = read_texts(); shot("l10n_italiano_pause")
print("IT pause:", [t for n, t in R["it_pause"]])
# закрыть меню паузы и прочитать HUD на итальянском (инвентарь Tab)
key("Escape", 0.1); time.sleep(1.2)
print("menu closed:", not any(True for _ in d.find_objects(By.NAME, "Pause_Screen", enabled=True)), "ts", d.get_static_property("UnityEngine.Time","timeScale",CORE))
R["it_hud"] = read_texts()
key("Tab", 0.1); time.sleep(1.2); R["it_inv"] = read_texts(); shot("l10n_italiano_inventory"); key("Tab", 0.1); time.sleep(1.0)
print("IT HUD:", [t for n, t in R["it_hud"]]); print("IT INV:", [t for n, t in R["it_inv"]][:25])
json.dump(R, open(os.path.join(REPO_RES, "l10n_italiano.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
