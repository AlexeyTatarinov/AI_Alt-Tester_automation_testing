import sys
sys.path.insert(0, r"Test_Ai\scripts\play_control")
import restart_play as rp
d = rp.driver()
try:
    print("locale", d.get_static_property("UnityEngine.Localization.Settings.LocalizationSettings", "SelectedLocale.Identifier.Code", "Unity.Localization"))
finally:
    d.stop()
