from g7 import *
import re
F = os.path.join(R7, "ui_text.json")
R = {"note": "редактор Unity; Game view см. screen", "screen": [sg("UnityEngine.Screen", "width"), sg("UnityEngine.Screen", "height")], "languages": {}}
def dump(): jdump(F, R)
prestage("ui")
off = log_mark(); START = time.time()
NT = re.compile(r"(?i)no translation found")
LOC = "UnityEngine.Localization.Settings.LocalizationSettings"
def code(): return str(sg(LOC, "SelectedLocale.Identifier.Code", "Unity.Localization"))
def scan(lang, screen):
    time.sleep(1.2)
    rows = []; seen = set()
    for comp in ("TMPro.TextMeshProUGUI", "TMPro.TextMeshPro"):
        for o in d.find_objects(By.COMPONENT, comp, enabled=True):
            if o.id in seen: continue
            seen.add(o.id)
            r = {"name": o.name, "id": o.id, "x": o.x, "y": o.y}
            for p in ("text", "isTextOverflowing", "isTextTruncated"):
                try: r[p] = o.get_component_property(comp, p, "Unity.TextMeshPro")
                except Exception as e: r[p] = "ERR " + type(e).__name__
            try: r["parent"] = o.get_parent().name
            except Exception: r["parent"] = None
            rows.append(r)
    f = {"overflow": [r for r in rows if r["isTextOverflowing"] is True], "truncated": [r for r in rows if r["isTextTruncated"] is True],
         "no_translation": [r for r in rows if isinstance(r["text"], str) and NT.search(r["text"])],
         "read_errors": [r for r in rows if any(str(r[p]).startswith("ERR ") for p in ("isTextOverflowing", "isTextTruncated"))]}
    shot_name = "ui_%s_%s.png" % (lang, screen)
    d.get_png_screenshot(os.path.join(R7, "shots", shot_name))
    R["languages"].setdefault(lang, {})[screen] = {"locale": code(), "count": len(rows), "rows": rows, "shot": shot_name,
                                                   "counts": {k: len(v) for k, v in f.items()}}
    dump()
    print(lang, screen, code(), "texts", len(rows), {k: len(v) for k, v in f.items()}, flush=True)
    for k, v in f.items():
        for r in v: print("    ", k, "|", r["parent"], "/", r["name"], "|", repr(r["text"])[:90], flush=True)
def open_settings():
    d.find_object(By.NAME, "Button Settings ", enabled=False).click(); time.sleep(1.5)
def close_settings():
    d.find_object(By.NAME, "Button Close", enabled=True).click(); time.sleep(1.5)
def set_lang(prefix):
    open_settings(); d.find_object(By.NAME, "Language_Tab", enabled=False).click(); time.sleep(1.0)
    for i in range(6):
        if code().startswith(prefix): break
        d.find_objects(By.NAME, "ButtonNext", enabled=True)[0].click(); time.sleep(1.2)
    assert code().startswith(prefix), "язык не выбран: " + code()
    d.find_object(By.NAME, "SaveButton", enabled=False).click(); time.sleep(1.5)
    if d.find_objects(By.NAME, "Settings_Panel_PR", enabled=True): close_settings()
    return code()
for lang, prefix in (("en", "en"), ("fr", "fr"), ("it", "it")):
    try:
        hyg_tick(R, lang)
        if time.time() - START > 11 * 60:
            R["stopped"] = "лимит времени перед " + lang; break
        print("set", set_lang(prefix), flush=True); time.sleep(1)
        scan(lang, "mainmenu")
        open_settings()
        for tab, nm in (("Audio_Tab", "settings_audio"), ("Graphic_Tab", "settings_graphics"), ("Language_Tab", "settings_language")):
            d.find_object(By.NAME, tab, enabled=False).click(); scan(lang, nm)
        close_settings()
        guard.restore_window("ui new game")
        print("new game", new_game(), "ready", wait_ready(45), flush=True); time.sleep(2)
        key("Escape", 0.1); time.sleep(1.0); assert pause_open(), "пауза не открылась"
        scan(lang, "pause")
        key("Escape", 0.1); time.sleep(1.5)
        key("Tab", 0.1); time.sleep(1.2); assert inv_open(), "инвентарь не открылся"
        scan(lang, "inventory")
        key("Tab", 0.1); time.sleep(1.5)
        print("to menu", to_menu(), flush=True); time.sleep(2)
    except Exception as e:
        R["languages"].setdefault(lang, {})["error"] = "%s: %s" % (type(e).__name__, str(e)[:200]); dump()
        print("ERR", lang, e, flush=True); break
# вернуть English
try:
    if "MainMenu" not in scenes(): to_menu(); time.sleep(2)
    R["restored_locale"] = set_lang("en")
except Exception as e:
    R["restore_error"] = str(e)[:200]
R["exceptions"] = exc_summary(off); R["seconds"] = round(time.time() - START); dump()
print("restored", R.get("restored_locale"), R.get("restore_error"), R["exceptions"]["by_type"], R["exceptions"]["first_stacks"], R["seconds"])
