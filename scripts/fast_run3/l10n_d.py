# -*- coding: utf-8 -*-
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from l10n_lib import *
d = connect(); R = {}
pre = guard.preflight("l10n_d"); print("preflight", {k: pre[k] for k in ("consoleFlags","error_pause","play","alive")}, "iconic", pre["window"].get("iconic"))
if pre["window"].get("iconic") or pre["error_pause"]: raise SystemExit("стоп")
guard.risky("L10N: Back to menu / New Game")
LOG0 = log_mark(); R["log0"] = LOG0; R["save_before"] = save_hashes()
def pause_open(): return any(True for _ in d.find_objects(By.NAME, "Pause_Screen", enabled=True))
if not pause_open(): key("Escape", 0.1); time.sleep(1.5)
d.find_object(By.NAME, "BackToMenuButton", enabled=False).click(); time.sleep(1.5)
d.find_object(By.NAME, "PopupButton - 1", enabled=False).click()
t0 = time.time(); ok = False
while time.time() - t0 < 40:
    try:
        sc = scenes()
        if "MainMenu" in sc: ok = True; break
    except Exception as e: pass
    time.sleep(1.0)
R["to_menu_s"] = round(time.time() - t0, 1); print("в MainMenu:", ok, R["to_menu_s"])
time.sleep(4.0)
R["menu_scenes"] = scenes(); R["menu_texts"] = read_texts(); shot("l10n_mainmenu_fr")
print("MENU texts:", R["menu_texts"]); print("audit:", audit(R["menu_texts"]))
names = sorted(set(o.name for o in d.get_all_elements(enabled=True) if "button" in o.name.lower() or "setting" in o.name.lower() or "lang" in o.name.lower()))
print("menu elements:", names)
R["log_menu"] = log_since(LOG0); print("log:", R["log_menu"])
json.dump(R, open(os.path.join(REPO_RES, "l10n_menu.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
