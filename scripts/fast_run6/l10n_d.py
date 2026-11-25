import os, sys, json; sys.stdout.reconfigure(encoding="utf-8"); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
from l10n_lib import read_texts, audit, lang_cur
d = connect(); preflight("l10n02d")
d.find_object(By.NAME, "Button Settings ", enabled=False).click(); time.sleep(1.5)
d.find_object(By.NAME, "Language_Tab", enabled=False).click(); time.sleep(1.0)
print("lang on reopen:", lang_cur()); shot("l10n02_settings_reopen_it")
for i in range(3):
    if lang_cur() == "English": break
    d.find_objects(By.NAME, "ButtonPrevious", enabled=True)[0].click(); time.sleep(1.0); print("prev ->", lang_cur(), flush=True)
shot("l10n02_settings_en_back")
d.find_object(By.NAME, "SaveButton", enabled=False).click(); time.sleep(1.5)
d.find_object(By.NAME, "Button Close", enabled=True).click(); time.sleep(1.5)
tx = read_texts(); print("MENU after:", tx, "audit", audit(tx)); print(shot("l10n02_mainmenu_en_back"))
OFF = int(open("l10n_off.txt").read()); lg = log_since(OFF); print("log since l10n start:", {k: lg[k] for k in ("lines","exceptions","errors","warnings_other")}, lg["samples"])
print("ended", now())
