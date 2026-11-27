import sys; sys.path.insert(0, r"Test_Ai\scripts\modules")
from mlib import *
from alttester.commands.Notifications.notification_type import NotificationType
ROWS = []


def rec(pid, call, ok, resp, s, note=""):
    ROWS.append({"id": pid, "call": call, "ok": ok, "resp": str(resp)[:300], "s": s, "note": note})
    print(pid, "OK " if ok else "ERR", call, "|", str(resp)[:140], "|", s, note, flush=True)


def P(pid, o, comp, prop, asm=ASM, depth=2, note=""):
    r = sget(o, comp, prop, asm, depth)
    rec(pid, r["call"], r["ok"], r["resp"], r["s"], note)
    return r


def first(comp):
    l = d.find_objects(By.COMPONENT, comp, enabled=False)
    return l[0] if l else None


def gstate():
    u = first("UIManager")
    r = sget(u, "UIManager", "_gameStateManager._currentGameState")
    return r.get("raw") if r["ok"] else None


def wait_state(sub="Gameplay", t=60):
    t0 = time.time()
    while time.time() - t0 < t:
        s = gstate()
        if s is not None and sub.lower() in str(s).lower():
            return round(time.time() - t0, 1), s
        time.sleep(1)
    return None, gstate()


print("hash_eq_backup", save_hashes() == bk_hashes())
d.set_static_property("UnityEngine.Application", "runInBackground", CORE, True)
off0 = log_mark()
# ---------- MainMenu: P07, P08 ----------
prestage("B_mainmenu")
sg = first("StartGame")
for dep in (2, 4):
    P("P07", sg, "StartGame", "_saveSystem.saveData._locationId", depth=dep)
    P("P07", sg, "StartGame", "_saveSystem.saveData._finishedQuestlineItemsGUIds", depth=dep)
P("P07", sg, "StartGame", "_saveSystem.saveData._itemStacks", depth=4, note="stacks")
try:
    j = json.load(open(SAVE0F, encoding="utf-8"))
    rec("P07", "save.chop file", True, "loc=%s finished=%d stacks=%d" % (j.get("_locationId"), len(j.get("_finishedQuestlineItemsGUIds", [])), len(j.get("_itemStacks", []))), 0, "file compare")
except Exception as e:
    rec("P07", "save.chop file", False, e, 0)
am = first("AudioManager")
for g in ("MasterVolume", "MusicVolume", "SFXVolume"):
    t = time.time()
    try:
        v = am.call_component_method("AudioManager", "GetGroupVolume", ASM, [g], ["System.String"])
        rec("P08", "GetGroupVolume(%s)" % g, True, v, round(time.time() - t, 2))
    except Exception as e:
        rec("P08", "GetGroupVolume(%s)" % g, False, "%s %s" % (type(e).__name__, e), round(time.time() - t, 2))
for p in ("_masterVolume", "_musicVolume", "_sfxVolume"):
    P("P08", am, "AudioManager", p)
# ---------- New Game ----------
print("scenes before", scenes())
t0 = time.time()
d.find_object(By.NAME, "Button New Game", enabled=False).click()
for _ in range(15):
    time.sleep(0.4)
    try:
        d.find_object(By.NAME, "PopupButton - 1", enabled=False).click()
        break
    except Exception:
        pass
tp = None
while time.time() - t0 < 60:
    try:
        if "Beach" in scenes() and pig():
            tp = round(time.time() - t0, 1)
            break
    except Exception:
        pass
    time.sleep(0.2)
print("beach at", tp)
t_ng = time.time()


def p09(tag):
    cm = first("CutsceneManager")
    if not cm:
        rec("P09", "CutsceneManager find (%s)" % tag, False, "not found", 0)
        return
    for pr in ("_activePlayableDirector", "_activePlayableDirector.state", "_activePlayableDirector.time"):
        P("P09", cm, "CutsceneManager", pr, ASM, 2, note=tag)
    P("P09", cm, "CutsceneManager", "_activePlayableDirector.state", ASM, 4, note=tag + " d4")


p09("t=0 after New Game")
# ---------- P01 ----------
prestage("B_beach")
pc = pig()
try:
    t = time.time()
    cl = pc.get_all_components()
    rec("P01", "get_all_components(PigChef(Clone))", True, [c.get("componentName") if isinstance(c, dict) else str(c) for c in cl], round(time.time() - t, 2))
except Exception as e:
    rec("P01", "get_all_components", False, "%s %s" % (type(e).__name__, e), 0)
while time.time() - t_ng < 30:
    time.sleep(0.5)
p09("t=30s after New Game")
w = wait_state("Gameplay", 60)
print("wait gameplay", w)
# ---------- P02 / P03 ----------
u = first("UIManager")
P("P02", u, "UIManager", "_gameStateManager._currentGameState", note="Gameplay")
r = P("P02", u, "UIManager", "_gameStateManager.CurrentGameState", note="Gameplay public")
ROWS[-1]["pytype"] = type(r.get("raw")).__name__
key("Escape", 0.1)
time.sleep(1.5)
print("pause open", pause_open())
P("P02", u, "UIManager", "_gameStateManager._currentGameState", note="Esc open")
pr = first("Protagonist")
for mp in ("Gameplay", "Menus", "Dialogues"):
    P("P03", pr, "Protagonist", "_inputReader._gameInput.%s.enabled" % mp, note="Esc open")
key("Escape", 0.1)
time.sleep(1.5)
print("pause open after close", pause_open())
for mp in ("Gameplay", "Menus", "Dialogues"):
    P("P03", pr, "Protagonist", "_inputReader._gameInput.%s.enabled" % mp, note="Gameplay")
key("Tab", 0.1)
time.sleep(1.5)
print("inv", inv())
P("P02", u, "UIManager", "_gameStateManager._currentGameState", note="Tab open")
for mp in ("Gameplay", "Menus"):
    P("P03", pr, "Protagonist", "_inputReader._gameInput.%s.enabled" % mp, note="Tab open")
key("Tab", 0.1)
time.sleep(1.2)
print("inv after", inv())
P("P02", u, "UIManager", "_gameStateManager._currentGameState", note="after Tab close")
# ---------- P04 ----------
im = first("InventoryManager")
for dep in (2, 4):
    P("P04", im, "InventoryManager", "_currentInventory._items", depth=dep)
P("P04", im, "InventoryManager", "_currentInventory._items[0]._amount")
P("P04", im, "InventoryManager", "_currentInventory._items[0]._item.name")
P("P04", im, "InventoryManager", "_currentInventory._items[0].Amount", note="public variant")
P("P04", im, "InventoryManager", "_currentInventory._items[0].Item.name", note="public variant")
P("P04", im, "InventoryManager", "_currentInventory.Items", depth=4, note="public variant")
# ---------- P05 ----------
for p in ("_currentHealthSO._currentHealth", "_currentHealthSO.CurrentHealth", "_currentHealthSO._maxHealth"):
    P("P05", pig(), "Damageable", p)
# ---------- P06 ----------
gm = first("GameManager")
for p in ("_questManager._currentQuestlineIndex", "_questManager._currentStepIndex", "_questManager._currentStep", "_questManager._currentStep.name"):
    P("P06", gm, "GameManager", p)
P("P06", gm, "GameManager", "_questManager", depth=2, note="whole")
# ---------- P15 ----------
t = time.time()
al_all = d.find_objects(By.COMPONENT, "AudioListener", enabled=False)
al_en = d.find_objects(By.COMPONENT, "AudioListener", enabled=True)
rec("P15", "find_objects(COMPONENT,AudioListener,enabled=False)", True, "all=%d active=%d names=%s" % (len(al_all), len(al_en), [(o.name, o.enabled) for o in al_all]), round(time.time() - t, 2))
try:
    rec("P15", "AudioListener.enabled per object", True, [(o.name, o.get_component_property("UnityEngine.AudioListener", "enabled", "UnityEngine.AudioModule")) for o in al_all], 0)
except Exception as e:
    rec("P15", "AudioListener.enabled per object", False, e, 0)
# ---------- P11-P13 transition ----------
prestage("B_transition")
LOGM = []
SC = []


def cb_log(n):
    try:
        LOGM.append((round(time.time(), 2), getattr(n, "level", None), str(getattr(n, "message", n))[:200]))
    except Exception as e:
        LOGM.append((time.time(), "cberr", str(e)))


def cb_load(n):
    SC.append((round(time.time(), 2), "LOAD", str(n)))


def cb_unload(n):
    SC.append((round(time.time(), 2), "UNLOAD", str(n)))


for nt, cb in ((NotificationType.LOG, cb_log), (NotificationType.LOADSCENE, cb_load), (NotificationType.UNLOADSCENE, cb_unload)):
    try:
        d.add_notification_listener(nt, cb, True)
    except Exception as e:
        rec("P11/12", "add_notification_listener(%s)" % nt, False, e, 0)
key("C", 0.1)
time.sleep(1.2)
btn = d.find_objects(By.PATH, "//CheatMenu/*", enabled=False)[1]
print("btn text", d.find_objects(By.PATH, "//CheatMenu/%s/Text" % btn.name, enabled=False)[0].get_text())
off = log_mark()
tc = time.time()
btn.click()
errs = []
seq = []
while time.time() - tc < 60:
    t = time.time()
    try:
        sc = scenes()
        seq.append((round(t - tc, 1), "ok", sc))
        if "Field_Hill" in sc and pig() and t - tc > 2:
            break
    except Exception as e:
        errs.append((round(t - tc, 1), type(e).__name__))
        seq.append((round(t - tc, 1), type(e).__name__))
    time.sleep(0.5)
time.sleep(3)
load_s = round(time.time() - tc, 1)
err_types = {}
for t_, n in errs:
    err_types[n] = err_types.get(n, 0) + 1
rec("P13", "get_all_loaded_scenes every 0.5s after click", True, "load_s=%s errors=%d types=%s first_err=%s last_err=%s" % (load_s, len(errs), err_types, errs[0] if errs else None, errs[-1] if errs else None), load_s, "err span s=%s" % ((errs[-1][0] - errs[0][0]) if errs else 0))
jdump(OUT + "/p13_seq.json", seq)
for nt in (NotificationType.LOG, NotificationType.LOADSCENE, NotificationType.UNLOADSCENE):
    try:
        d.remove_notification_listener(nt)
    except Exception:
        pass
rec("P12", "LOADSCENE/UNLOADSCENE notifications", bool(SC), SC[:12], 0, "count=%d; click at %.2f" % (len(SC), tc))
with open(EDLOG, "rb") as f:
    f.seek(off)
    txt = f.read().decode("utf-8", "replace").splitlines()
ed = [l for l in txt if l.strip() and "AltTester|" not in l and "audio listener" not in l]
ed_err = [l for l in ed if re.search(r"(?i)exception|error|warning", l)]
lv = {}
for m in LOGM:
    lv[str(m[1])] = lv.get(str(m[1]), 0) + 1
rec("P11", "LOG notification vs Editor.log", bool(LOGM), "notif_total=%d levels=%s sample=%s | editor_lines=%d editor_err/warn=%d sample=%s" % (len(LOGM), lv, [m[2][:80] for m in LOGM[:3]], len(ed), len(ed_err), [l[:80] for l in ed_err[:3]]), 0)
jdump(OUT + "/p11_log_notifications.json", {"notif": LOGM[:300], "editor_err": ed_err[:100]})
if len(d.find_objects(By.NAME, "CheatMenu", enabled=True)):
    key("C", 0.1)
    time.sleep(1)
# ---------- Field_Hill: P10, P14 ----------
prestage("B_fieldhill")
pc_ = d.find_objects(By.COMPONENT, "PlantCritter", enabled=False)
print("PlantCritter n", len(pc_))
if pc_:
    o = pc_[0]
    try:
        rec("P10", "get_all_components(PlantCritter)", True, [c.get("componentName") for c in o.get_all_components()], 0)
    except Exception as e:
        rec("P10", "get_all_components", False, e, 0)
    for p in ("isStopped", "remainingDistance", "velocity", "speed", "hasPath"):
        P("P10", o, "UnityEngine.AI.NavMeshAgent", p, "UnityEngine.AIModule")
    P("P10", o, "Critter", "isPlayerInAlertZone")
else:
    rec("P10", "find PlantCritter", False, "no component PlantCritter; Critter n=%d" % len(d.find_objects(By.COMPONENT, "Critter", enabled=False)), 0)
t = time.time()
a = d.find_objects(By.PATH, "//*[@component=Critter]", enabled=False)
t1 = round(time.time() - t, 2)
b = d.find_objects(By.COMPONENT, "Critter", enabled=False)
rec("P14", "PATH //*[@component=Critter] vs COMPONENT Critter", True, "path=%d component=%d names_path=%s" % (len(a), len(b), [o.name for o in a][:8]), t1, "equal=%s" % (len(a) == len(b)))
jdump(OUT + "/probe.json", {"rows": ROWS, "made": time.strftime("%Y-%m-%d %H:%M:%S")})
print("hash now eq backup", save_hashes() == bk_hashes(), "exceptions", exc_summary(off0)["total"])
