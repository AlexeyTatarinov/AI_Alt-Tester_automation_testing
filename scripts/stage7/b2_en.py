from g7 import *
prestage("ui_restore")
LOC = "UnityEngine.Localization.Settings.LocalizationSettings"
def code(): return str(sg(LOC, "SelectedLocale.Identifier.Code", "Unity.Localization"))
print("before", code(), scenes())
if not d.find_objects(By.NAME, "Settings_Panel_PR", enabled=True):
    d.find_object(By.NAME, "Button Settings ", enabled=False).click(); time.sleep(1.5)
d.find_object(By.NAME, "Language_Tab", enabled=False).click(); time.sleep(1.0)
for i in range(6):
    if code().startswith("en"): break
    d.find_objects(By.NAME, "ButtonPrevious", enabled=True)[0].click(); time.sleep(1.2); print("prev ->", code())
assert code().startswith("en")
d.find_object(By.NAME, "SaveButton", enabled=False).click(); time.sleep(1.5)
if d.find_objects(By.NAME, "Settings_Panel_PR", enabled=True):
    d.find_object(By.NAME, "Button Close", enabled=True).click(); time.sleep(1.5)
print("after", code())
d.get_png_screenshot(os.path.join(R7, "shots", "ui_restored_en.png"))
