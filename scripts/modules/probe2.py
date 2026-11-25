import sys; sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\modules")
from mlib import *
from alttester.commands.Notifications.notification_type import NotificationType
ROWS = []


def rec(pid, call, ok, resp, s, note=""):
    ROWS.append({"id": pid, "call": call, "ok": ok, "resp": str(resp)[:300], "s": s, "note": note})
    print(pid, "OK " if ok else "ERR", call, "|", str(resp)[:200], "|", s, note, flush=True)


def P(pid, o, comp, prop, asm=ASM, depth=2, note=""):
    r = sget(o, comp, prop, asm, depth)
    rec(pid, r["call"], r["ok"], r["resp"], r["s"], note)
    return r


def first(comp):
    l = d.find_objects(By.COMPONENT, comp, enabled=False)
    return l[0] if l else None


off0 = log_mark()
prestage("B2_fieldhill")
print("scenes", scenes())
# ---- P10 retry: PlantCritter = имя объекта, компонент Critter ----
crit = d.find_objects(By.COMPONENT, "Critter", enabled=False)
o = [c for c in crit if c.name == "PlantCritter"][0]
print("critter obj", o.name, o.worldX, o.worldY, o.worldZ)
try:
    rec("P10", "get_all_components(PlantCritter obj)", True, [c.get("componentName") for c in o.get_all_components()], 0)
except Exception as e:
    rec("P10", "get_all_components", False, e, 0)
for dep in (2, 4):
    for p in ("isStopped", "remainingDistance", "velocity"):
        P("P10", o, "UnityEngine.AI.NavMeshAgent", p, "UnityEngine.AIModule", dep)
P("P10", o, "Critter", "isPlayerInAlertZone")
P("P10", o, "UnityEngine.AI.NavMeshAgent", "hasPath", "UnityEngine.AIModule")
# ---- P11/P12/P13 retry: Field_Hill -> Beach, правильные атрибуты ----
LOGM = []
SC = []


def cb_log(n):
    LOGM.append((round(time.time(), 2), getattr(n, "type", None), str(getattr(n, "message", n))[:300]))


def cb_load(n):
    SC.append((round(time.time(), 2), "LOAD", getattr(n, "scene_name", None), str(getattr(n, "loadSceneMode", None))))


def cb_unload(n):
    SC.append((round(time.time(), 2), "UNLOAD", n if isinstance(n, str) else getattr(n, "scene_name", str(n))))


for nt, cb in ((NotificationType.LOG, cb_log), (NotificationType.LOADSCENE, cb_load), (NotificationType.UNLOADSCENE, cb_unload)):
    d.add_notification_listener(nt, cb, True)
key("C", 0.1)
time.sleep(1.2)
btn = d.find_objects(By.PATH, "//CheatMenu/*", enabled=False)[0]
print("btn", d.find_objects(By.PATH, "//CheatMenu/%s/Text" % btn.name, enabled=False)[0].get_text())
off = log_mark()
tc = time.time()
btn.click()
errs = []
while time.time() - tc < 60:
    t = time.time()
    try:
        sc = scenes()
        if "Beach" in sc and pig() and t - tc > 2:
            break
    except Exception as e:
        errs.append((round(t - tc, 1), type(e).__name__))
    time.sleep(0.5)
time.sleep(3)
load_s = round(time.time() - tc, 1)
for nt in (NotificationType.LOG, NotificationType.LOADSCENE, NotificationType.UNLOADSCENE):
    try:
        d.remove_notification_listener(nt)
    except Exception:
        pass
rec("P13", "get_all_loaded_scenes 0.5s after click (2nd sample Field_Hill->Beach)", True, "load_s=%s errors=%d %s" % (load_s, len(errs), errs[:5]), load_s)
rec("P12", "LOADSCENE/UNLOADSCENE (fields scene_name)", bool(SC), [(round(x[0] - tc, 2),) + tuple(x[1:]) for x in SC], 0, "relative to click")
with open(EDLOG, "rb") as f:
    f.seek(off)
    txt = f.read().decode("utf-8", "replace").splitlines()
ed = [l for l in txt if l.strip() and "AltTester|" not in l and "audio listener" not in l]
game_notif = [m for m in LOGM if "AltTester|" not in m[2]]
types = {}
for m in LOGM:
    types[str(m[1])] = types.get(str(m[1]), 0) + 1
rec("P11", "LOG notification (type field) vs Editor.log", bool(LOGM), "notif_total=%d types=%s non_AltTester_notif=%d sample=%s | editor_lines_excl_AltTester_audio=%d sample=%s" % (len(LOGM), types, len(game_notif), [m[2][:90] for m in game_notif[:6]], len(ed), [l[:90] for l in ed[:6]]), 0)
jdump(OUT + "/p11_retry.json", {"notif_non_alttester": game_notif[:200], "editor_lines": ed[:200], "types": types})
if len(d.find_objects(By.NAME, "CheatMenu", enabled=True)):
    key("C", 0.1)
    time.sleep(1)
# ---- P04 full list vs inventory screen ----
prestage("B2_beach")
im = first("InventoryManager")
items = []
for i in range(40):
    a = sget(im, "InventoryManager", "_currentInventory._items[%d].Amount" % i)
    if not a["ok"]:
        rec("P04", "_items[%d].Amount" % i, False, a["resp"], a["s"], "end of list")
        break
    n = sget(im, "InventoryManager", "_currentInventory._items[%d].Item.name" % i)
    items.append((n.get("raw"), a.get("raw")))
rec("P04", "iterate _items[i].Item.name/.Amount", True, items, 0, "count=%d" % len(items))
for p in ("_currentInventory._items.Count", "_currentInventory._items.Length"):
    P("P04", im, "InventoryManager", p, note="length")
snap = inv_snapshot()
screen = []
for tab, lst in snap.items():
    for n, a, at in lst:
        screen.append((n, a))
rec("P04", "inventory screen (Tab, all tabs) via UIInventoryItem", True, screen, 0, "tabs=%s" % list(snap.keys()))
same = sorted((str(a), b) for a, b in items) == sorted((str(a), b) for a, b in screen)
rec("P04", "compare list vs screen", True, "same=%s list=%d screen=%d" % (same, len(items), len(screen)), 0)
print("pause", pause_open(), "inv", inv())
jdump(OUT + "/probe2.json", {"rows": ROWS})
print("exceptions", exc_summary(off0))
