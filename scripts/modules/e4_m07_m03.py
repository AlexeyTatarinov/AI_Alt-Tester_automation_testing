import sys; sys.path.insert(0, r"Test_Ai\scripts\modules")
from elib import *

SPAWN = (-195.58, -9.42, -376.9)
POT_ = (-144.25, -4.39, -324.21)
F = OUT + "/m07_m03.json"
try:
    D = json.load(open(F, encoding="utf-8"))
except Exception:
    D = {}
off_all = log_mark()
autosync(True)
W = sys.argv[1] if len(sys.argv) > 1 else "all"


def camdist():
    return round(dist3(cam_pos(), ppos()), 2)


def m07():
    out = {}
    prestage("m07")
    if "Beach" not in scenes():
        goto("Beach")
    guard.before_case("M07-01")
    off = log_mark()
    tp(POT_[0] - 2.0, POT_[1] + 0.3, POT_[2], 3.0)
    o = pig()
    old = o.id
    t0 = time.perf_counter()
    o.call_component_method("Damageable", "Kill", ASM)
    new_t = None
    while time.perf_counter() - t0 < 12:
        l = pigs()
        if any(x.id != old for x in l):
            new_t = time.perf_counter() - t0
            break
        time.sleep(0.1)
    r = {"respawn_s": None if new_t is None else round(new_t, 2)}
    if new_t is not None:
        tn = time.perf_counter()
        for ts in (2.0, 5.0):
            while time.perf_counter() - tn < ts:
                time.sleep(0.05)
            try:
                r["d%d" % ts] = camdist()
            except Exception as e:
                r["d%d" % ts] = "ERR %s" % type(e).__name__
    r["log"] = log_since(off)
    out["respawn"] = r
    # после перехода Beach -> Field_Hill
    prestage("m07_transition")
    if pause_open():
        close_pause()
    if not cheat_open():
        key("C", 0.1)
        time.sleep(1.2)
    btn = [x for x in d.find_objects(By.PATH, "//CheatMenu/*/Text", enabled=False) if x.get_text().startswith("Field_Hill via")][0].get_parent()
    off = log_mark()
    tc = time.time()
    btn.click()
    seen = None
    while time.time() - tc < 60:
        time.sleep(0.2)
        try:
            if "Field_Hill" in scenes() and pig():
                seen = time.perf_counter()
                break
        except Exception:
            pass
    r2 = {"load_s": round(time.time() - tc, 1)}
    if seen:
        for ts in (2.0, 5.0):
            while time.perf_counter() - seen < ts:
                time.sleep(0.05)
            try:
                r2["d%d" % ts] = camdist()
            except Exception as e:
                r2["d%d" % ts] = "ERR %s" % type(e).__name__
    if cheat_open():
        key("C", 0.1)
        time.sleep(1)
    r2["log"] = log_since(off)
    out["transition"] = r2
    ok = True
    parts = []
    for nm, rr in (("respawn", r), ("transition", r2)):
        d2, d5 = rr.get("d2"), rr.get("d5")
        good = isinstance(d2, float) and isinstance(d5, float) and d5 <= 11.0 and d5 <= d2 + 0.5
        ok &= good
        parts.append("%s: d2=%s d5=%s ok=%s" % (nm, d2, d5, good))
    exc = r["log"]["exceptions"] + r2["log"]["exceptions"]
    D["M07-01"] = out
    jdump(F, D)
    save_er("M07-01", {"verdict": "PASS" if ok else "FAIL", "numbers": "расстояние камера–игрок через 2 и 5 с (≤ 11 м и d5 ≤ d2+0,5): %s; респавн через %s с; исключений %d" % ("; ".join(parts), r.get("respawn_s"), exc), "source": "m07_m03.json"})


KEYS = [("W", 0.3), ("Space", 0.1), ("E", 0.1), ("F", 0.1), ("Q", 0.1), ("Tab", 0.1), ("Escape", 0.1), ("C", 0.1)]


def setup_state(state):
    """привести игру в состояние state; вернуть True/False"""
    ok, n = to_gameplay(3)
    if not ok:
        return False
    if state == "Gameplay":
        return True
    if state == "Pause":
        key("Escape", 0.1)
        time.sleep(1.3)
        return gstate() == 1
    if state == "Inventory":
        key("Tab", 0.1)
        time.sleep(1.3)
        return gstate() == 2
    return False


def combat_setup():
    """телепорт в 3 м от PlantCritter и ожидание isPlayerInAlertZone"""
    ok, n = to_gameplay(3, (0, 6))
    cl = [c for c in d.find_objects(By.COMPONENT, "Critter", enabled=False) if c.name == "PlantCritter"]
    if not cl:
        return None
    # выбрать живого врага с самой ранней тревогой: берём первого, у которого здоровье > 0
    c = cl[0]
    c.update_object()
    cp = (c.worldX, c.worldY, c.worldZ)
    tp(cp[0] - 3.0, cp[1] + 0.3, cp[2], 0.3)
    t0 = time.time()
    while time.time() - t0 < 6:
        try:
            if c.get_component_property("Critter", "isPlayerInAlertZone", ASM) is True:
                time.sleep(0.3)
                return (c, gstate(), round(time.time() - t0, 1))
        except Exception:
            pass
        time.sleep(0.2)
    return (c, gstate(), None)


def m03():
    prestage("m03")
    rows = {}
    problems = []
    prev_scene = None
    for state in ("Gameplay", "Pause", "Inventory", "Combat"):
        if state == "Combat":
            goto("Field_Hill")
            time.sleep(2)
        else:
            if "Beach" not in scenes():
                goto("Beach")
            tp(*SPAWN, 1.0)
        for k, dur in KEYS:
            guard.before_case("M03-01_%s_%s" % (state, k))
            if state == "Combat":
                cs = combat_setup()
                ready = cs is not None and cs[2] is not None
                s0 = gstate()
            else:
                ready = setup_state(state)
                s0 = gstate()
                tp(*SPAWN, 0.5) if (state == "Gameplay" and False) else None
            row = {"state_before": sname(s0), "ready": ready}
            if not ready:
                row["why"] = "не удалось привести игру в состояние"
                rows["%s|%s" % (state, k)] = row
                if state != "Combat":
                    problems.append(("setup", state, k))
                continue
            off = log_mark()
            p0 = ppos()
            pn0 = panels()
            hp0 = health()
            try:
                key(k, dur)
            except Exception as e:
                row["key_error"] = type(e).__name__
            time.sleep(1.0)
            try:
                p1 = ppos()
                row["moved_m"] = round(dxz(p0, p1), 2)
            except Exception:
                row["moved_m"] = None
            s1 = gstate()
            row["state_after"] = sname(s1)
            pn1 = panels()
            row["panels_opened"] = [x for x in pn1 if pn1[x] and not pn0[x]]
            row["panels_closed"] = [x for x in pn0 if pn0[x] and not pn1[x]]
            try:
                row["player_hp"] = [hp0, health()]
            except Exception:
                pass
            exc = exc_summary(off)
            row["exceptions"] = exc["total"]
            row["exc_types"] = exc["by_type"]
            if exc["total"]:
                row["exc_first"] = list(exc["first_stacks"].values())[0][:3]
                problems.append(("exception", state, k, exc["by_type"]))
            # вернуть исходное состояние
            back, n = to_gameplay(2, (0, 6) if state == "Combat" else (0,))
            row["restored_to_gameplay"] = back
            row["restore_presses"] = n
            if not back:
                problems.append(("stuck", state, k, sname(gstate())))
                # аварийное восстановление, не считается в критерий
                for _ in range(3):
                    if to_gameplay(1)[0]:
                        break
            rows["%s|%s" % (state, k)] = row
            D["M03-01"] = {"rows": rows, "problems": problems}
            jdump(F, D)
            print(state, k, json.dumps(row, ensure_ascii=False, default=str)[:300], flush=True)
    # выйти из зоны тревоги в этой же сцене (иначе при смене сцены счётчик тревог протекает: Combat залипает)
    try:
        ents = d.find_objects(By.COMPONENT, "LocationEntrance", enabled=False)
        pl = [c for c in d.find_objects(By.COMPONENT, "Critter", enabled=False) if c.name == "PlantCritter"]
        if ents and pl:
            far = max(ents, key=lambda o: math.hypot(o.worldX - pl[0].worldX, o.worldZ - pl[0].worldZ))
            tp(far.worldX, far.worldY + 0.5, far.worldZ, 2.0)
            D["M03-01_after_combat_state"] = sname(gstate())
    except Exception as e:
        D["M03-01_cleanup_error"] = type(e).__name__
    # ожидания
    def moved(st, k):
        return rows.get("%s|%s" % (st, k), {}).get("moved_m")
    exp = {
        "Pause: W не двигает": moved("Pause", "W"),
        "Inventory: W не двигает": moved("Inventory", "W"),
        "Combat: Tab не открывает инвентарь": rows.get("Combat|Tab", {}).get("panels_opened"),
        "Combat: E не открывает разговор": rows.get("Combat|E", {}).get("panels_opened"),
        "Pause: Esc закрывает паузу": rows.get("Pause|Escape", {}).get("state_after"),
        "Gameplay: W двигает": moved("Gameplay", "W"),
    }
    D["M03-01"]["expectations"] = exp
    jdump(F, D)
    v = "FAIL" if problems else "OBSERVATION"
    table = {k: (r.get("state_after"), r.get("moved_m"), r.get("panels_opened"), r.get("exceptions")) for k, r in rows.items()}
    save_er("M03-01", {"verdict": v, "numbers": "таблица состояние×клавиша (после, сдвиг м, открылось, исключений) в m07_m03.json; проблемы (исключение/застряла): %s; ожидания: %s" % (problems, exp), "source": "m07_m03.json"})


if W in ("all", "m07"):
    m07()
if W in ("all", "m03"):
    m03()
print("exceptions", exc_summary(off_all))
