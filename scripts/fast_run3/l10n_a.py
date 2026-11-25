# -*- coding: utf-8 -*-
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from l10n_lib import *
d = connect()
print("lang", lang_cur(), "texts", [t for n, t in read_texts()])
seen = []
for i in range(6):
    b = [o for o in d.find_objects(By.NAME, "ButtonNext", enabled=True)]
    print("ButtonNext enabled count", len(b))
    b[0].click(); time.sleep(1.0)
    cur = lang_cur(); tx = read_texts(); seen.append(cur)
    print(i, cur, [t for n, t in tx])
    if cur == "English": break
shot("settings_language_cycle")
json.dump(seen, open(os.path.join(REPO_RES, "l10n_cycle.json"), "w", encoding="utf-8"), ensure_ascii=False)
