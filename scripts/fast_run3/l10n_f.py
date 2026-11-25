# -*- coding: utf-8 -*-
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from l10n_lib import *
d = connect(); R = {}
LOG0 = log_mark()
pre = guard.preflight("l10n_f"); print("preflight", {k: pre[k] for k in ("consoleFlags","error_pause","alive")}, "iconic", pre["window"].get("iconic"))
print("scenes", scenes(), "pos", ppos(), "pigs", len(pigs()))
R["ng_hud"] = read_texts(); print("HUD после New Game:", R["ng_hud"]); shot("l10n_ng_hud")
ph = d.find_objects(By.NAME, "Text (TMP)", enabled=True)
for o in d.find_objects(By.COMPONENT, "TMPro.TextMeshProUGUI", enabled=True):
    t = o.get_component_property("TMPro.TextMeshProUGUI", "text", "Unity.TextMeshPro")
    if t == "PLACEHOLDER":
        p = o.get_parent(); chain = []
        while p is not None and len(chain) < 6:
            chain.append(p.name); p = p.get_parent()
        print("PLACEHOLDER объект:", o.name, "родители:", chain)
key("Tab", 0.1); time.sleep(1.2); R["ng_inv"] = read_texts(); shot("l10n_ng_inventory"); key("Tab", 0.1); time.sleep(1.0)
print("INV:", [t for n, t in R["ng_inv"]][:25])
key("Escape", 0.1); time.sleep(1.5); R["ng_pause"] = read_texts(); print("PAUSE:", [t for n, t in R["ng_pause"]])
d.find_object(By.NAME, "SettingsButton", enabled=False).click(); time.sleep(1.2)
d.find_object(By.NAME, "Language_Tab", enabled=False).click(); time.sleep(1.0)
R["ng_lang_cur"] = lang_cur(); print("язык после New Game:", R["ng_lang_cur"]); shot("l10n_ng_settings")
d.find_object(By.NAME, "Button Close", enabled=True).click(); time.sleep(1.0)
key("Escape", 0.1); time.sleep(1.2)
print("меню закрыто:", not any(True for _ in d.find_objects(By.NAME, "Pause_Screen", enabled=True)), "ts", d.get_static_property("UnityEngine.Time","timeScale",CORE))
a = approach_step("W", 0.3, 0.6); print("шаг после закрытия", a["moved_m"]); R["ng_step"] = a["moved_m"]
R["log"] = log_since(LOG0); print("log:", R["log"])
json.dump(R, open(os.path.join(REPO_RES, "l10n_newgame.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
