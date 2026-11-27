import sys; sys.path.insert(0, r"Test_Ai\scripts\modules")
from elib import *

F = OUT + "/m16_01.json"
off_all = log_mark()
prestage("m16_01")
ok, _ = to_gameplay(2)
D = {"start_scenes": scenes()}
print("to_menu", to_menu(), flush=True)
time.sleep(3)
prestage("m16_01_menu")
off = log_mark()
t0 = time.time()
d.find_object(By.NAME, "Button New Game", enabled=False).click()
for _ in range(15):
    time.sleep(0.4)
    try:
        d.find_object(By.NAME, "PopupButton - 1", enabled=False).click()
        break
    except Exception:
        pass
series = []
placeholder_seen = []
moves = []
first_cutscene = None
back_to_gameplay = None
last_move = 0
first_move_ok = None
i = 0
while time.time() - t0 < 40:
    t = round(time.time() - t0, 1)
    row = {"t": t}
    try:
        sc = scenes()
        row["gameplay_loaded"] = "Gameplay" in sc
        u = first("UIManager")
        row["state"] = sname(rd(u, "UIManager", "_gameStateManager._currentGameState")) if u else None
        cm = first("CutsceneManager")
        row["director"] = rd(cm, "CutsceneManager", "_activePlayableDirector") if cm else "no CutsceneManager"
    except Exception as e:
        row["err"] = type(e).__name__
    if row.get("state") == "Cutscene" and first_cutscene is None:
        first_cutscene = t
    if first_cutscene is not None and row.get("state") == "Gameplay" and back_to_gameplay is None:
        back_to_gameplay = t
    if i % 4 == 0:
        try:
            txt = [(o.name, o.get_component_property("TMPro.TextMeshProUGUI", "text", "Unity.TextMeshPro")) for o in d.find_objects(By.COMPONENT, "TMPro.TextMeshProUGUI", enabled=True)]
            ph = [x for x in txt if x[1] and "PLACEHOLDER" in x[1].upper()]
            row["placeholder"] = bool(ph)
            if ph:
                placeholder_seen.append(t)
                row["placeholder_obj"] = ph[0][0]
        except Exception as e:
            row["ph_err"] = type(e).__name__
    if time.time() - last_move >= 5 and row.get("gameplay_loaded") and pigs():
        last_move = time.time()
        try:
            p0 = ppos()
            key("W", 0.3)
            time.sleep(0.4)
            mv = round(dxz(p0, ppos()), 2)
            moves.append((t, mv))
            row["move_m"] = mv
            if mv >= 0.3 and first_move_ok is None:
                first_move_ok = t
        except Exception as e:
            row["move_err"] = type(e).__name__
    series.append(row)
    i += 1
    time.sleep(0.5)
D.update(series=series, moves=moves, first_cutscene_s=first_cutscene, back_to_gameplay_s=back_to_gameplay, first_move_ok_s=first_move_ok, placeholder_t=placeholder_seen, log=log_since(off))
exc = exc_summary(off)
D["exc"] = exc
jdump(F, D)
states = sorted({r.get("state") for r in series if r.get("state")})
dirs = sorted({str(r.get("director")) for r in series})
cs_dur = None if (first_cutscene is None or back_to_gameplay is None) else round(back_to_gameplay - first_cutscene, 1)
fail = first_move_ok is None or exc["total"] > 0
v = "FAIL" if fail else "PASS"
save_er("M16-01", {"verdict": v, "numbers": "40 с после New Game: состояния %s; директор катсцены %s; состояние Cutscene впервые на %s с, возврат в Gameplay %s с (длительность %s с); управление вернулось (W сдвинул ≥ 0,3 м) на %s с; сдвиги W (t,м) %s; PLACEHOLDER виден в моменты %s (известный CC-85); исключений %d %s" % (states, dirs, first_cutscene, back_to_gameplay, cs_dur, first_move_ok, moves, placeholder_seen[:6], exc["total"], exc["by_type"]), "source": "m16_01.json"})
print("exceptions", exc_summary(off_all))
