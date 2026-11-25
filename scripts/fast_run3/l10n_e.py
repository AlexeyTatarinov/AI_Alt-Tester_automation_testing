# -*- coding: utf-8 -*-
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from l10n_lib import *
d = connect(); R = {}
LOG0 = log_mark(); BK = r"C:\Users\Aotat\Desktop\Test_Ai\Reports_2026-11-21\evidence\save_backup\20261122_122526\Unity_Technologies\save.chop"
# Settings в MainMenu: язык
d.find_object(By.NAME, "Button Settings ", enabled=False).click(); time.sleep(1.5)
R["menu_settings_texts"] = read_texts(); print("MENU settings:", [t for n, t in R["menu_settings_texts"]]); shot("l10n_menu_settings")
try:
    d.find_object(By.NAME, "Language_Tab", enabled=False).click(); time.sleep(1.0)
    R["menu_lang_cur"] = lang_cur(); print("язык в Settings меню:", R["menu_lang_cur"])
except Exception as e: print("language tab err", type(e).__name__)
try: d.find_object(By.NAME, "Button Close", enabled=True).click(); time.sleep(1.0)
except Exception as e: print("close err", type(e).__name__)
print("settings closed:", not any(True for _ in d.find_objects(By.NAME, "Settings_Panel_PR", enabled=True)))
# New Game
R["hash_before_newgame"] = sha(r"C:\Users\Aotat\AppData\LocalLow\Unity Technologies\Chop Chop\save.chop"); R["hash_backup"] = sha(BK)
print("хеш save.chop перед New Game", R["hash_before_newgame"], "копия", R["hash_backup"], "равны:", R["hash_before_newgame"] == R["hash_backup"], "(отличие ожидаемо: Save языка + Back to menu)")
t0 = time.time(); d.find_object(By.NAME, "Button New Game", enabled=False).click()
for _ in range(15):
    time.sleep(0.4)
    try: d.find_object(By.NAME, "PopupButton - 1", enabled=False).click(); break
    except Exception: pass
seen = {}; found = None
while time.time() - t0 < 60:
    try:
        sc = scenes()
        for n in ("PersistentManagers", "Gameplay", "Beach"):
            if n in sc and n not in seen: seen[n] = round(time.time() - t0, 1)
        if "Beach" in sc and pig(): found = round(time.time() - t0, 1); break
    except Exception: pass
    time.sleep(0.3)
print("New Game: игрок через", found, seen, "сцены", scenes())
time.sleep(4.0)
R["ng_hud"] = read_texts(); print("HUD после New Game:", [t for n, t in R["ng_hud"]])
key("Tab", 0.1); time.sleep(1.2); R["ng_inv"] = read_texts(); shot("l10n_ng_inventory"); key("Tab", 0.1); time.sleep(1.0)
print("INV:", [t for n, t in R["ng_inv"]][:25])
key("Escape", 0.1); time.sleep(1.5); R["ng_pause"] = read_texts(); print("PAUSE:", [t for n, t in R["ng_pause"]])
d.find_object(By.NAME, "SettingsButton", enabled=False).click(); time.sleep(1.2)
d.find_object(By.NAME, "Language_Tab", enabled=False).click(); time.sleep(1.0)
R["ng_lang_cur"] = lang_cur(); print("язык после New Game:", R["ng_lang_cur"]); shot("l10n_ng_settings")
d.find_object(By.NAME, "Button Close", enabled=True).click(); time.sleep(1.0)
key("Escape", 0.1); time.sleep(1.2)
print("меню закрыто:", not any(True for _ in d.find_objects(By.NAME, "Pause_Screen", enabled=True)), "ts", d.get_static_property("UnityEngine.Time","timeScale",CORE))
a = approach_step("W", 0.3, 0.6); print("шаг после закрытия", a["moved_m"])
R["ng_step"] = a["moved_m"]; R["log"] = log_since(LOG0); print("log:", R["log"]); R["new_game_s"] = found
json.dump(R, open(os.path.join(REPO_RES, "l10n_newgame.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
