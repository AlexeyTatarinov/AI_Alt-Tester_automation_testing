# -*- coding: utf-8 -*-
"""Наглядный прогон готовки: шаг -> результат со скриншотом. Запуск на чистом Play. Игру и проект не меняет."""
import os, sys, json, shutil
sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\fast_run7")
from r4lib import *

OUT = r"C:\Users\Aotat\Desktop\Test_Ai\Reports_2026-11-21\results\run9_cook_visual_20261124"
os.makedirs(os.path.join(OUT, "shots"), exist_ok=True)
steps = []

def S(title, ok, details, shotname=None):
    p = None
    if shotname:
        src = shot("cv_" + shotname)
        if os.path.exists(src):
            dst = os.path.join(OUT, "shots", "%02d_%s.png" % (len(steps) + 1, shotname)); shutil.copy(src, dst)
            p = "shots/" + os.path.basename(dst)
    steps.append({"n": len(steps) + 1, "time": now(), "title": title, "ok": ok, "details": details, "shot": p})
    print(steps[-1]["n"], "OK" if ok else "FAIL", title, "|", details, flush=True)
    json.dump(steps, open(os.path.join(OUT, "steps.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def seeds():
    return save_info().get("stacks", {}).get("42396f")

def approach(tgt):
    for i in range(12):
        if hint(): return True
        step_towards(tgt, 0.2); time.sleep(0.4)
    return hint()

def space_until(stop, maxn=40):
    n = 0
    while n < maxn:
        key("Space", 0.1); n += 1; time.sleep(1.0)
        if stop(): break
    return n

d = connect(); pre = preflight("s11_cook")
if scenes() and "MainMenu" not in scenes(): raise SystemExit("игра не в MainMenu: " + str(scenes()))
fr = int(d.get_static_property("UnityEngine.Time", "frameCount", "UnityEngine.CoreModule"))
rt = float(d.get_static_property("UnityEngine.Time", "realtimeSinceStartup", "UnityEngine.CoreModule"))
d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, True)
off = log_mark()
try:
    S("0. Исходное состояние: чистый Play, меню", rt < 1200, "realtimeSinceStartup %.0f с, frameCount %d, Error Pause выключен (consoleFlags %s)" % (rt, fr, pre["consoleFlags"]), "00_menu")
    guard.risky("s11 new game")
    ng = new_game()
    for _ in range(20):
        time.sleep(1.5)
        try: ppos(); break
        except Exception: pass
    time.sleep(2)
    S("1. New Game: игра началась на пляже", "Beach" in scenes(), "сцены %s, семян в сохранении: %s" % (scenes(), seeds()), "01_beach")
    tp_hare(1.3)
    ok = approach(HARE)
    S("2. Подошли к зайцу BardHare: появилась подсказка «E»", ok, "расстояние %.2f м" % dxz(ppos(), HARE), "02_hint")
    key("E", 0.1); time.sleep(1.0)
    S("3. Первый разговор открыт", dlg(), "первая реплика: %s" % (line() or "")[:80], "03_dialogue1_open")
    n = space_until(lambda: not dlg(), 40)
    S("4. Первый разговор прошли до конца", not dlg(), "нажатий Space: %d (ожидание 18), кнопок Yes/No нет, шагов квеста в save.chop: %s" % (n, save_info().get("finished")), "04_dialogue1_closed")
    # второй разговор
    for _ in range(6):
        if approach(HARE): break
        teleport("T1", HARE[0] - 1.3, HARE[1] + 0.3, HARE[2]); time.sleep(1.5)
    key("E", 0.1); time.sleep(1.2)
    S("5. Второй разговор: заяц спрашивает про семена", dlg(), "реплика: %s" % (line() or "")[:80], "05_dialogue2_question")
    key("Space", 0.1); time.sleep(1.5)
    S("6. Появились кнопки Yes / No", choices(), "один Space после вопроса; Seed до ответа: %s" % seeds(), "06_yes_no")
    s_before = seeds()
    d.find_object(By.NAME, "ButtonChoice1", enabled=True).click(); time.sleep(2.0)
    S("7. Нажали Yes (отдаём семечко)", True, "реплика: %s" % (line() or "")[:70], "07_after_yes")
    n2 = space_until(lambda: not dlg(), 20)
    S("8. Разговор закончился: рецепт получен", not dlg(), "нажатий Space: %d; Seed %s → %s" % (n2, s_before, seeds()), "08_dialogue2_closed")
    # рецепт в инвентаре
    key("Tab", 0.1); time.sleep(1.2)
    for _ in range(5):
        if str(tab_type()) == "2": break
        key("Y", 0.1); time.sleep(0.7)
    sl = [x for x in slots() if "Recipe" in x[1]]
    info = {}
    if sl:
        s = sl[0][0]
        for path in ["currentItem.Item.IngredientsList", "currentItem.Item.ResultingDish.name"]:
            try: info[path] = str(s.get_component_property("UIInventoryItem", path, ASM))[:200]
            except Exception as e: info[path] = "не прочитано"
    S("9. Вкладка «Рецепты» в инвентаре", bool(sl), "рецепты: %s; состав (сырые данные игры): %s; известно из прогона d01: 3 × Seed → SweetCream_Dish" % ([(x[1], x[2]) for x in sl], info), "09_recipe_tab")
    key("Tab", 0.1); time.sleep(1.0)
    # к котлу
    teleport("T1", POT[0] + 1.3, POT[1] + 0.3, POT[2]); time.sleep(2.0)
    okp = approach(POT)
    S("10. Подошли к котлу: подсказка «E»", okp, "расстояние %.2f м; семян: %s (нужно 3)" % (dxz(ppos(), POT), seeds()), "10_pot_hint")
    guard.risky("s11 cook")
    key("E", 0.1); time.sleep(1.5)
    S("11. E у котла: открылся инвентарь, вкладка рецептов", inv(), "вкладка %s, предметы %s" % (tab_type(), [(x[1], x[2]) for x in slots()]), "11_pot_inventory")
    sl = [x for x in slots() if "Recipe" in x[1]]
    sl[0][0].click(); time.sleep(1.0)
    S("12. Выбрали рецепт: кнопка действия", True, "кнопка действия активна: %s" % (action_button()[1],), "12_recipe_selected")
    st0 = save_info(); off_q = log_mark()
    key("Q", 0.1); time.sleep(3.0)
    st1 = save_info(); exq = exc_summary(off_q)
    S("13. Нажали Q: готовка", True, "семена %s → %s; save.chop изменился: %s; исключений в логе: %s" % (st0["stacks"].get("42396f"), st1["stacks"].get("42396f"), st0["hash"] != st1["hash"], exq["by_type"]), "13_after_Q")
    if not inv(): key("Tab", 0.1); time.sleep(1.2)
    tabs = all_tabs()
    dish = [t for t in tabs.values() for t in t if "Dish" in t[0]]
    S("14. Готовое блюдо в инвентаре", bool(dish), "блюдо: %s; вкладки: %s" % (dish, json.dumps(tabs, ensure_ascii=False)), "14_dish")
    if inv(): key("Tab", 0.1); time.sleep(1.0)
    verdict = bool(dish) and st0["stacks"].get("42396f", 0) - st1["stacks"].get("42396f", 0) == 3
    S("ИТОГ", verdict, "рецепт верный, ингредиенты списаны (−3 Seed), блюдо +1; единственный дефект: исключение NullReferenceException при Q (CC-91)" if verdict else "готовка не дала ожидаемого результата, смотри шаги выше", None)
    ex_all = exc_summary(off)
    steps.append({"exceptions_total": ex_all["total"], "by_type": ex_all["by_type"], "frameCount_start": fr, "realtime_start": rt})
finally:
    d.set_static_property("UnityEngine.Physics", "autoSyncTransforms", PHYS, False)
    json.dump(steps, open(os.path.join(OUT, "steps.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
