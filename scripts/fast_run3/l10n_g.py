# -*- coding: utf-8 -*-
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from l10n_lib import *
d = connect()
key("Escape", 0.1); time.sleep(1.5)
d.find_object(By.NAME, "SettingsButton", enabled=False).click(); time.sleep(1.2)
d.find_object(By.NAME, "Language_Tab", enabled=False).click(); time.sleep(1.0)
d.find_objects(By.NAME, "ButtonPrevious", enabled=True)[0].click(); time.sleep(1.0); print("язык:", lang_cur())
d.find_object(By.NAME, "SaveButton", enabled=False).click(); time.sleep(1.5)
d.find_object(By.NAME, "Button Close", enabled=True).click(); time.sleep(1.0)
print("pause texts:", [t for n, t in read_texts()])
key("Escape", 0.1); time.sleep(1.2)
print("меню закрыто:", not any(True for _ in d.find_objects(By.NAME, "Pause_Screen", enabled=True)), "ts", d.get_static_property("UnityEngine.Time","timeScale",CORE))
print("шаг", approach_step("W", 0.3, 0.6)["moved_m"])
