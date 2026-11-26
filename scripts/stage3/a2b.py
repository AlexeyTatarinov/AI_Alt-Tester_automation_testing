# -*- coding: utf-8 -*-
from s3lib import *
sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\fast_run3")
R = {"steps": []}
def dump(): jdump(os.path.join(R2, "a2b.json"), R)
def vol():
    am = first("AudioManager")
    return am.call_component_method("AudioManager", "GetGroupVolume", ASM, ["MasterVolume"], ["System.String"])
def lang_cur():
    for o in d.find_objects(By.NAME, "CurrentOption", enabled=True):
        try: return o.get_component_property("TMPro.TextMeshProUGUI", "text", "Unity.TextMeshPro")
        except Exception: pass
def sfields():
    try:
        j = json.load(open(SAVE0F, encoding="utf-8")); return {"_masterVolume": j.get("_masterVolume"), "_currentLocale": j.get("_currentLocale"), "hash": sha(SAVE0F)}
    except Exception as e: return {"err": str(e)[:80]}
def btn_text():
    out = {}
    for n in ("ResumeButton", "SettingsButton", "BackToMenuButton"):
        try:
            for t in d.find_objects(By.PATH, "//%s//Text (TMP)" % n, enabled=False)[:1]: out[n] = t.get_text()
        except Exception as e: out[n] = "ERR"
    return out
def menu_texts():
    out = []
    for o in d.find_objects(By.NAME, "Text (TMP)", enabled=True):
        try:
            t = o.get_text().strip()
            if t: out.append(t)
        except Exception: pass
    return out[:12]
def step(n, **kw):
    kw.update(name=n, vol=vol() if first("AudioManager") else None, save=sfields(), lang=None); R["steps"].append(kw); dump(); print(n, kw, flush=True)
def master_idx():
    prevs = d.find_objects(By.NAME, "ButtonPrevious", enabled=True)
    for i, pb in enumerate(prevs):
        b = vol(); pb.click(); time.sleep(0.6); a = vol()
        nxt = d.find_objects(By.NAME, "ButtonNext", enabled=True)
        if len(nxt) == len(prevs): nxt[i].click(); time.sleep(0.6)
        if a != b: return i
    return None
def open_settings(tab):
    if not pause_open(): key("Escape", 0.1); time.sleep(1.5)
    d.find_object(By.NAME, "SettingsButton", enabled=False).click(); time.sleep(1.5)
    d.find_object(By.NAME, tab, enabled=False).click(); time.sleep(1.2)
def close_settings():
    try: d.find_object(By.NAME, "Button Close", enabled=True).click()
    except Exception: pass
    time.sleep(1.2)
autosync(True)
try:
    off = log_mark(); R["off"] = off
    ok, _ = to_gameplay(2); R["gameplay_start"] = ok
    bk = json.load(open(os.path.join(BK, "Unity_Technologies", "save.chop"), encoding="utf-8"))
    R["backup_fields"] = {"_masterVolume": bk.get("_masterVolume"), "_currentLocale": bk.get("_currentLocale")}
    step("0 старт (Gameplay)")
    open_settings("Audio_Tab")
    mi = master_idx(); R["master_idx"] = mi; print("master idx", mi, flush=True); assert mi is not None
    v0 = vol()
    d.find_objects(By.NAME, "ButtonPrevious", enabled=True)[mi].click(); time.sleep(1.0)
    R["vol_after_prev"] = vol()
    d.find_objects(By.NAME, "SaveButton", enabled=True)[0].click(); time.sleep(1.5)
    R["vol_after_audio_save"] = vol(); R["save_after_audio_save"] = sfields()
    d.find_object(By.NAME, "Language_Tab", enabled=False).click(); time.sleep(1.0)
    R["lang_before"] = lang_cur()
    d.find_objects(By.NAME, "ButtonNext", enabled=True)[0].click(); time.sleep(1.5)
    R["lang_after_next"] = lang_cur()
    d.find_objects(By.NAME, "SaveButton", enabled=True)[0].click(); time.sleep(1.5)
    close_settings()
    key("Escape", 0.1); time.sleep(1.5); R["texts_set"] = menu_texts(); to_gameplay(2)
    step("1 после Save", lang=R["lang_after_next"], btn=btn_text(), texts=R["texts_set"])
    # Back to menu -> Continue
    ok, _ = to_gameplay(2)
    guard.risky("a2 back to menu")
    R["to_menu_s"] = to_menu()
    for _ in range(20):
        time.sleep(1.5)
        if "MainMenu" in scenes() and d.find_objects(By.NAME, "Button Continue", enabled=False): break
    time.sleep(1); guard.restore_window("a2 continue")
    R["menu_texts_in_menu"] = menu_texts()
    step("2 в MainMenu")
    t0 = time.time(); d.find_object(By.NAME, "Button Continue", enabled=False).click()
    for _ in range(10):
        time.sleep(0.4)
        try: d.find_object(By.NAME, "PopupButton - 1", enabled=False).click(); break
        except Exception: pass
    found = None
    while time.time() - t0 < 60:
        try:
            if "Beach" in scenes() and pig(): found = round(time.time() - t0, 1); break
        except Exception: pass
        time.sleep(0.3)
    R["load_s"] = found; assert found
    time.sleep(3)
    for _ in range(30):
        if gstate() == 0: break
        time.sleep(1)
    open_settings("Language_Tab"); lc = lang_cur(); R["lang_after_continue"] = lc
    d.find_object(By.NAME, "Audio_Tab", enabled=False).click(); time.sleep(1.0)
    close_settings(); to_gameplay(2)
    key("Escape", 0.1); time.sleep(1.5); bt = menu_texts(); to_gameplay(2)
    step("3 после Continue", lang=lc, btn=bt)
    # возврат
    open_settings("Audio_Tab")
    d.find_objects(By.NAME, "ButtonNext", enabled=True)[mi].click(); time.sleep(1.0)
    d.find_object(By.NAME, "Language_Tab", enabled=False).click(); time.sleep(1.0)
    for _ in range(4):
        if lang_cur() == "English": break
        d.find_objects(By.NAME, "ButtonPrevious", enabled=True)[0].click(); time.sleep(1.2)
    d.find_objects(By.NAME, "SaveButton", enabled=True)[0].click(); time.sleep(1.5)
    close_settings(); to_gameplay(2)
    open_settings("Language_Tab"); lg = lang_cur(); d.find_object(By.NAME, "Audio_Tab", enabled=False).click(); time.sleep(1.0); close_settings(); to_gameplay(2)
    step("4 возврат на English", lang=lg)
    R["vol_restored"] = vol(); R["vol_orig"] = v0
    R["exc"] = exc_summary(off); dump(); print("exc", R["exc"]["total"], R["exc"]["by_type"])
finally:
    autosync(False); dump()
