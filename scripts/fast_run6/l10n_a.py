import os, sys, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
from l10n_lib import read_texts, audit, lang_cur
d = connect(); preflight("l10n02")
print("start", now(), flush=True)
OFF = log_mark(); open("l10n_off.txt","w").write(str(OFF))
guard.risky("L10N-02 to menu")
print("to_menu", to_menu()); time.sleep(4.0)
print("scenes", scenes())
tx = read_texts(); print("MENU EN:", tx); print(shot("l10n02_mainmenu_en"))
names = sorted(set(o.name for o in d.get_all_elements(enabled=True) if any(w in o.name.lower() for w in ("button","setting","lang","tab","option"))))
print("elements:", names)
