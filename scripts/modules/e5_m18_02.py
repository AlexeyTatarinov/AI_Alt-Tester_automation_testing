import sys; sys.path.insert(0, r"Test_Ai\scripts\modules")
from elib import *

F = OUT + "/m18_02.json"
D = {"steps": []}
off_all = log_mark()
prestage("m18_02")
if "Beach" not in scenes():
    goto("Beach")
SAVE_F = SAVE0F


def vols():
    am = first("AudioManager")
    out = {}
    for g in ("MasterVolume", "MusicVolume", "SFXVolume"):
        try:
            out[g] = am.call_component_method("AudioManager", "GetGroupVolume", ASM, [g], ["System.String"])
        except Exception as e:
            out[g] = "ERR " + type(e).__name__
    return out


def step(name, **kw):
    kw["name"] = name
    kw["vols"] = vols()
    try:
        kw["save_hash"] = sha(SAVE_F)
    except Exception:
        pass
    D["steps"].append(kw)
    jdump(F, D)
    print(name, kw, flush=True)


ok, _ = to_gameplay(2)
step("start", gameplay=ok)
key("Escape", 0.1)
time.sleep(1.5)
d.find_object(By.NAME, "SettingsButton", enabled=False).click()
time.sleep(1.5)
tabs = [o.name for o in d.find_objects(By.PATH, "//Settings_Panel_PR//*", enabled=True) if "Tab" in o.name]
print("tabs", tabs)
D["tabs"] = tabs
try:
    d.find_object(By.NAME, "Audio_Tab", enabled=False).click()
except Exception as e:
    print("Audio_Tab err", type(e).__name__)
    cand = [t for t in tabs if "udio" in t]
    if cand:
        d.find_object(By.NAME, cand[0], enabled=False).click()
time.sleep(1.2)
fillers = d.find_objects(By.COMPONENT, "UISettingItemFiller", enabled=True)
print("fillers", len(fillers), [f.name for f in fillers])
D["fillers"] = [(f.name, round(f.worldY, 1)) for f in fillers]
v0 = vols()
step("settings_audio_open")
# какой филлер отвечает за Master: нажать Previous один раз и посмотреть, какая громкость изменилась
master = None
prevs_all = d.find_objects(By.NAME, "ButtonPrevious", enabled=True)
print("ButtonPrevious count", len(prevs_all), [(p.name, round(p.worldY, 1)) for p in prevs_all])
D["prev_buttons"] = [(p.name, round(p.worldY, 1)) for p in prevs_all]
mapping = {}
for i, pb in enumerate(prevs_all):
    before = vols()
    pb.click()
    time.sleep(0.6)
    after = vols()
    changed = [g for g in before if before[g] != after[g]]
    mapping[i] = changed
    # вернуть шаг: Next этой же строки
    nxt = d.find_objects(By.NAME, "ButtonNext", enabled=True)
    if len(nxt) == len(prevs_all):
        nxt[i].click()
        time.sleep(0.6)
    print("prev", i, changed, flush=True)
D["mapping_prev_to_group"] = mapping
step("mapping_done")
midx = [i for i, ch in mapping.items() if "MasterVolume" in ch]
if not midx:
    save_er("M18-02", {"verdict": "BLOCKED", "numbers": "кнопки ButtonPrevious не меняют MasterVolume по GetGroupVolume (сопоставление %s)" % mapping, "source": "m18_02.json"})
    to_gameplay(3)
    raise SystemExit(0)
mi = midx[0]
# Master -> 0 (до 10 нажатий)
for n in range(10):
    prevs = d.find_objects(By.NAME, "ButtonPrevious", enabled=True)
    if mi >= len(prevs):
        break
    prevs[mi].click()
    time.sleep(0.35)
time.sleep(0.8)
step("master_down_unsaved")
# Save
d.find_objects(By.NAME, "SaveButton", enabled=True)[0].click()
time.sleep(1.5)
v_saved0 = vols()
step("saved_master_zero")
# вернуть как было: Next 10 раз, Save
for n in range(10):
    nx = d.find_objects(By.NAME, "ButtonNext", enabled=True)
    if mi >= len(nx):
        break
    nx[mi].click()
    time.sleep(0.35)
time.sleep(0.8)
d.find_objects(By.NAME, "SaveButton", enabled=True)[0].click()
time.sleep(1.5)
v_back = vols()
step("restored_saved")
try:
    d.find_object(By.NAME, "Button Close", enabled=True).click()
except Exception:
    pass
time.sleep(1.2)
ok2, n = to_gameplay(2)
step("closed", gameplay=ok2, presses=n)
changed = v_saved0.get("MasterVolume") != v0.get("MasterVolume")
returned = v_back.get("MasterVolume") == v0.get("MasterVolume")
save_changed = D["steps"][-3]["save_hash"] != D["steps"][0]["save_hash"] if False else None
hs = [s.get("save_hash") for s in D["steps"]]
save_changed = len(set(hs)) > 1
exc = exc_summary(off_all)
v = "PASS" if changed and returned and save_changed else "FAIL"
save_er("M18-02", {"verdict": v, "numbers": "Master 0: MasterVolume микшера %s → %s (после Save) → %s (после возврата и Save); изменилось=%s, вернулось=%s; save.chop менялся=%s (хеши %s); сопоставление кнопок %s; исключений %d" % (v0.get("MasterVolume"), v_saved0.get("MasterVolume"), v_back.get("MasterVolume"), changed, returned, save_changed, hs, mapping, exc["total"]), "source": "m18_02.json"})
