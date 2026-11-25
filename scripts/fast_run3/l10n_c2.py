# -*- coding: utf-8 -*-
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from l10n_lib import *
d = connect(); R = {}
h0 = save_hashes()
key("Escape", 0.1); time.sleep(1.5)
d.find_object(By.NAME, "SettingsButton", enabled=False).click(); time.sleep(1.2)
d.find_object(By.NAME, "Language_Tab", enabled=False).click(); time.sleep(1.0)
print("lang now", lang_cur())
d.find_objects(By.NAME, "ButtonNext", enabled=True)[0].click(); time.sleep(1.0)
print("lang now", lang_cur())
R["fr_settings"] = read_texts(); print("FR settings", [t for n, t in R["fr_settings"]])
# кнопка Save
btn = None
for o in d.find_objects(By.NAME, "ButtonText", enabled=True):
    t = o.get_component_property("TMPro.TextMeshProUGUI", "text", "Unity.TextMeshPro")
    if t in ("Sauvegarder", "Save"): btn = o.get_parent(); print("save btn:", btn.name, "text", t)
btn.click(); time.sleep(1.5)
h1 = save_hashes(); R["save_changed_after_Save"] = h0 != h1; print("save.chop changed after Save:", h0 != h1)
d.find_object(By.NAME, "Button Close", enabled=True).click(); time.sleep(1.2)
R["fr_pause"] = read_texts(); print("FR pause", [t for n, t in R["fr_pause"]]); shot("l10n_francais2_pause")
key("Escape", 0.1); time.sleep(1.2)
print("closed:", not any(True for _ in d.find_objects(By.NAME, "Pause_Screen", enabled=True)), "ts", d.get_static_property("UnityEngine.Time","timeScale",CORE))
R["fr_hud"] = read_texts()
key("Tab", 0.1); time.sleep(1.2); R["fr_inv"] = read_texts(); shot("l10n_francais2_inventory"); key("Tab", 0.1); time.sleep(1.0)
print("FR HUD", [t for n, t in R["fr_hud"]]); print("FR INV", [t for n, t in R["fr_inv"]][:25])
json.dump(R, open(os.path.join(REPO_RES, "l10n_francais2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("hashes", h1)
