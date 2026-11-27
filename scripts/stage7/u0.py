from g7 import *
prestage("ui0")
hyg_start("ui", {})
d.find_object(By.NAME, "Button Settings ", enabled=False).click(); time.sleep(1.5)
names = sorted({o.name for o in d.get_all_elements(enabled=True)})
print([n for n in names if any(k in n.lower() for k in ("tab", "button", "save", "close", "option", "settings"))])
for o in d.find_objects(By.COMPONENT, "UISettingTabFiller", enabled=True):
    print("tab", o.name, o.id)
print("code", sg("UnityEngine.Localization.Settings.LocalizationSettings", "SelectedLocale.Identifier.Code", "Unity.Localization"))
d.get_png_screenshot(os.path.join(R7, "shots", "ui_probe_settings.png"))
