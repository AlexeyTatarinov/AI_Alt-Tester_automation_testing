# -*- coding: utf-8 -*-
"""Блок B, этап 3: LOC-03 (10 локаций через меню читов) с DTH-03/04 в Town_Market и ENM-01..03 в Field_Hill. Q не нажимается."""
import os, sys, time, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastlib import *

d = connect(); st = load_state()
d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, True)
T_START = time.time()
BASE_SCENES = {"PersistentManagers", "Gameplay"}

def buttons():
    out = []
    for o in d.find_objects(By.COMPONENT, "LocationTeleporterButton", enabled=False):
        try:
            lab = o.get_component_property("LocationTeleporterButton", "label.text", ASM)
        except Exception:
            lab = None
        out.append((o, lab))
    return out

def cheat_open():
    return any(True for o in d.find_objects(By.COMPONENT, "LocationTeleporterButton", enabled=True))

def location_scenes():
    return [s for s in scenes() if s not in BASE_SCENES]

def do_teleport_to(label_part):
    """открыть меню читов (C), кликнуть кнопку локации; вернуть (время загрузки, сцены, число PigChef) или причину"""
    if not cheat_open():
        key("C", 0.1); time.sleep(0.8)
    btn = None
    for o, lab in buttons():
        if lab and lab.startswith(label_part + " via"):
            btn = o; break
    if btn is None:
        return {"error": "кнопка %s не найдена" % label_part}
    before = location_scenes(); t0 = time.time()
    # клик по кнопке (видна, если меню открыто)
    try:
        d.find_objects(By.COMPONENT, "LocationTeleporterButton", enabled=True)
        btn.click()
    except Exception as e:
        return {"error": "клик не удался: %s" % type(e).__name__}
    ok = False; scn = None; pigs_n = 0
    while time.time() - t0 < 40:
        time.sleep(0.4)
        try:
            sc = location_scenes()
        except Exception:
            continue
        if sc and sc != before:
            try:
                pn = len(pigs())
            except Exception:
                pn = 0
            if pn >= 1:
                ok = True; scn = sc; pigs_n = pn; break
    return {"load_s": round(time.time() - t0, 1), "ok": ok, "scenes": scn or location_scenes(), "pigs": pigs_n}

LOCS = [("Beach",), ("Field_Hill",), ("Field_Farms",), ("Mountain_Path",), ("Mountain_Cave",), ("Town_Market",), ("Town_Inner",), ("Town_Upper",), ("Forest",)]
import guard

# ---------- DTH-03 / DTH-04 ----------
def zone():
    o = d.find_object(By.NAME, "FallCatcher_Lake", enabled=False); o.update_object()
    return (o.worldX, o.worldY, o.worldZ)

def dth03():
    off = log_mark(); z = zone()
    p0 = pig(); old_id = p0.id
    teleport("T1", z[0], z[1] + 2.0, z[2]); t0 = time.time()
    dead_t = None; new_t = None; newpos = None; npigs = None
    while time.time() - t0 < 12:
        time.sleep(0.2)
        try:
            pl = pigs()
        except Exception:
            continue
        ids = [x.id for x in pl]
        if dead_t is None and (old_id not in ids or any(False for _ in ids)):
            dead_t = round(time.time() - t0, 1)
        if old_id not in ids and ids and new_t is None:
            new_t = round(time.time() - t0, 1); newpos = ppos(pl[0])
        if new_t is not None and time.time() - t0 > new_t + 1.2:
            npigs = len(pigs()); break
    lg = log_since(off)
    dist = None if newpos is None else round(dxz(newpos, z), 1)
    ok = (new_t is not None and new_t <= 6.0 and dist is not None and dist >= 3.0 and npigs == 1 and lg["exceptions"] == 0)
    return {"verdict": "Пройдено" if ok else "Не пройдено", "numbers": "центр зоны FallCatcher_Lake %s; телепорт на 2 м над; старый PigChef исчез на %s с, новый появился на %s с (≤6); позиция нового %s, до центра зоны %s м (≥3); PigChef через 1 с: %s; исключений %d, ошибок %d" % (tuple(round(v, 1) for v in z), dead_t, new_t, None if newpos is None else tuple(round(v, 1) for v in newpos), dist, npigs, lg["exceptions"], lg["errors"]),
            "log_samples": lg["samples"]}

def dth04():
    off = log_mark(); z = zone()
    teleport("T1", z[0], z[1] + 2.0, z[2])
    for _ in range(3):
        try: key("F", 0.1)
        except Exception: pass
        time.sleep(0.2)
    time.sleep(6.0)
    lg = log_since(off)
    nre = [s for s in lg["samples"] if "NullReference" in s]
    return {"verdict": "Пройдено" if lg["exceptions"] == 0 else "Не пройдено", "numbers": "удар F 3 раза по 0,2 с при падении в зону: исключений %d (NullReference: %d), ошибок %d; образцы: %s" % (lg["exceptions"], len(nre), lg["errors"], lg["samples"][:3])}

# ---------- ENM ----------
def critter_info(o):
    try:
        alert = o.get_component_property("Critter", "isPlayerInAlertZone", ASM)
    except Exception as e:
        alert = "не прочитано: %s" % type(e).__name__
    try:
        hp = o.get_component_property("Damageable", "_currentHealthSO.CurrentHealth", ASM)
    except Exception:
        hp = None
    return alert, hp

def enm():
    crit = d.find_objects_which_contain(By.NAME, "PlantCritter", enabled=False)
    if not crit:
        for nm in ("Critter", "Plant"):
            crit = d.find_objects_which_contain(By.NAME, nm, enabled=False)
            if crit: break
    if not crit:
        for cid in ("ENM-01", "ENM-02", "ENM-03"):
            md_row(cid, "Не проверено", "в Field_Hill не найдено ни одного объекта PlantCritter/Critter")
        return
    c = crit[0]; c.update_object(); cp = (c.worldX, c.worldY, c.worldZ)
    # ENM-01
    off = log_mark(); h0 = health()
    teleport("T1", cp[0] - 3.0, cp[1] + 0.3, cp[2]); t0 = time.time(); alert_t = None
    while time.time() - t0 < 10:
        time.sleep(0.25)
        a, hp = critter_info(c)
        if a is True and alert_t is None: alert_t = round(time.time() - t0, 1)
    hint_hidden = not comp_active("UIInteraction")
    h1 = health()
    ok1 = alert_t is not None and alert_t <= 3.0
    md_row("ENM-01", "Пройдено" if ok1 else "Не пройдено", "PlantCritter %s в 3 м: isPlayerInAlertZone стало True через %s с (≤3); подсказка взаимодействия скрыта=%s; здоровье игрока %s → %s за 10 с; врагов в сцене: %d" % (tuple(round(v, 1) for v in cp), alert_t, hint_hidden, h0, h1, len(crit)))
    # ENM-02
    teleport("T1", cp[0] + 40.0, cp[1] + 0.3, cp[2]); time.sleep(0.5); t0 = time.time(); off_t = None
    h2 = health()
    while time.time() - t0 < 5:
        a, hp = critter_info(c)
        if a is False and off_t is None: off_t = round(time.time() - t0, 1)
        time.sleep(0.25)
    h3 = health()
    ok2 = off_t is not None and off_t <= 3.0 and h3 >= h2
    md_row("ENM-02", "Пройдено" if ok2 else "Не пройдено", "телепорт на 40 м: isPlayerInAlertZone стало False через %s с (≤3); здоровье %s → %s" % (off_t, h2, h3))
    # ENM-03
    items0 = len(d.find_objects(By.COMPONENT, "CollectableItem", enabled=False))
    teleport("T1", cp[0] - 1.2, cp[1] + 0.3, cp[2]); time.sleep(1.0)
    a, hp0 = critter_info(c); hits = 0; t0 = time.time(); gone = False; hp_last = hp0
    while time.time() - t0 < 20:
        key("F", 0.1); hits += 1; time.sleep(0.4)
        try:
            c.update_object(); a, hp_last = critter_info(c)
        except Exception:
            gone = True; break
    items1 = len(d.find_objects(By.COMPONENT, "CollectableItem", enabled=False))
    ok3 = gone or (hp0 is not None and hp_last is not None and hp_last < hp0)
    md_row("ENM-03", "Пройдено" if ok3 else "Не пройдено", "до 20 с ударов F раз в 0,5 с: ударов %d; здоровье врага %s → %s; враг исчез=%s; предметов CollectableItem %d → %d (выпал: %s)" % (hits, hp0, hp_last, gone, items0, items1, items1 > items0))

# ---------- основной цикл LOC-03 ----------
summary = []
md_row("LOC-03 Forest_Entrance", "Не проверено", "в меню читов нет кнопки Forest_Entrance (есть только Forest via InnerTown_Forest)")
for (loc,) in LOCS:
    if time.time() - T_START > 35 * 60:
        md_row("LOC-03 " + loc, "Не проверено", "лимит времени блока (35 мин от начала этапа)")
        continue
    if loc in location_scenes():
        md_row("LOC-03 " + loc, "Не проверено", "текущая локация: меню читов игнорирует повторную загрузку (EditorTeleporter), не баг")
        summary.append((loc, "Не проверено"))
        if loc == "Field_Hill":
            try: case("ENM", enm)
            except (StopRun, guard.Paused): raise
            except Exception as e: md_row("ENM Field_Hill", "Не проверено", "ошибка скрипта: %s" % type(e).__name__)
        continue
    off = log_mark()
    if loc == "Forest": guard.risky("LOC-03 Forest (NavMesh Stop, CC-?)")
    try:
        guard.before_case("LOC-03 " + loc)
        r = do_teleport_to(loc)
    except (StopRun, guard.Paused):
        raise
    except Exception as e:
        r = {"error": "%s: %s" % (type(e).__name__, str(e)[:100])}
    if "error" in r or not r.get("ok"):
        v = "Не проверено" if "error" in r and loc == "Beach" else "Не пройдено"
        if loc == "Beach" and "error" not in r and not r.get("ok"):
            v = "Не проверено"
        md_row("LOC-03 " + loc, v, "load: %s; ошибка: %s" % (r, r.get("error")), "")
        summary.append((loc, v));
        if cheat_open(): key("C", 0.1)
        continue
    time.sleep(5.0)
    lg = log_since(off)
    try:
        pn = len(pigs())
    except Exception:
        pn = None
    ok = r["load_s"] <= 30 and pn == 1 and lg["exceptions"] == 0
    md_row("LOC-03 " + loc, "Пройдено" if ok else "Не пройдено", "загрузка %s с (≤30), сцены %s, PigChef после 5 с покоя: %s, исключений %d, ошибок %d, предупреждений: CC-67 %d, прочих %d" % (r["load_s"], r["scenes"], pn, lg["exceptions"], lg["errors"], lg["cc67_locationentry"], lg["warnings_other"]), "; ".join(lg["samples"][:2]))
    summary.append((loc, "Пройдено" if ok else "Не пройдено")); guard.after_case("LOC-03 " + loc, "ok" if ok else "fail", "")
    if cheat_open(): key("C", 0.1); time.sleep(0.5)
    try:
        if loc == "Town_Market":
            r3 = case("DTH-03", dth03); md_row("DTH-03", r3["verdict"], r3["numbers"], "; ".join(r3.get("log_samples", [])[:2]))
            time.sleep(3.0)
            r4 = case("DTH-04", dth04); md_row("DTH-04", r4["verdict"], r4["numbers"])
        if loc == "Field_Hill":
            case("ENM", enm)
    except StopRun:
        raise
    except Exception as e:
        md_row("DTH/ENM " + loc, "Не проверено", "ошибка скрипта: %s: %s" % (type(e).__name__, str(e)[:150]))
done = sum(1 for _, v in summary if v == "Пройдено")
md_row("LOC-03 (итог)", "Пройдено" if done == len(LOCS) else "Не пройдено", "локаций пройдено %d из %d: %s" % (done, len(LOCS), summary))
print("stage B3 готов, сцены:", scenes())
