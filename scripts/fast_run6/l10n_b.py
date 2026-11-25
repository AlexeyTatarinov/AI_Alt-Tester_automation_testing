import os, sys, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
from l10n_lib import read_texts, audit, lang_cur
d = connect(); preflight("l10n02b")
R = {}
def snap(tag):
    tx = read_texts(); R[tag] = tx; shot("l10n02_" + tag)
    print("==", tag, "lang:", lang_cur()); 
    for n, t in tx: print("   ", n, "|", repr(t))
    print("   AUDIT:", audit(tx), flush=True)
d.find_object(By.NAME, "Button Settings ", enabled=False).click(); time.sleep(1.5)
d.find_object(By.NAME, "Language_Tab", enabled=False).click(); time.sleep(1.0)
snap("settings_en")
print("buttons:", sorted(set(o.name for o in d.get_all_elements(enabled=True) if "button" in o.name.lower() or "next" in o.name.lower())))
for i in range(2):
    d.find_objects(By.NAME, "ButtonNext", enabled=True)[0].click(); time.sleep(1.0); print("next ->", lang_cur(), flush=True)
snap("settings_it")
d.find_object(By.NAME, "SaveButton", enabled=False).click(); time.sleep(1.5)
d.find_object(By.NAME, "Button Close", enabled=True).click(); time.sleep(1.5)
snap("mainmenu_it")
json.dump(R, open("l10n02_texts.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
