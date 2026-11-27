import json
P = r"Test_Ai\Reports_2026-11-21\results\opus_review_20261124\cases_state.json"
j = json.load(open(P, encoding="utf-8"))
SRC = "Reports_2026-11-21/results/modules_stage2_20261125/report.md"
U = {
 "IT-03": ("PASS", "Чистый Play №1. Первый разговор: 18 Space, 17 реплик, закрылся, 0 исключений; шаг 0→1. Второй: Yes/No после 1 Space; Yes: Seed 20→19, SweetCream_Recipe 0→1, шаг 1→2; save.chop изменился (628fab9e→a995c076), в нём 2 GUID пройденных шагов. После первого разговора подсказка E пропала на 0,97 м, пришлось повторить телепорт (ошибка скрипта, не игры).", None),
 "IT-04": ("PASS", "Котёл Beach: подсказка E только с -X стороны на 1,5 м. Выбран рецепт SweetCream (вкладка Recipe), нажата кнопка с текстом Cook: Seed 19→16, SweetCream_Dish 0→1, рецепт остался, 0 исключений, состояние Gameplay. Клик по Cook не дал NRE, который давала клавиша Q в run8 (UIActionButton.cs:42).", None),
 "IT-12": ("OBSERVATION", "Шаг S3-Q1-QL1 = CheckItem на SweetCream_Dish. Разговор: Yes/No, Yes, ~29 реплик. Блюдо НЕ списалось (1→1), questline 0→1, _currentStepIndex остался 2, награда RockCandy_Recipe +1, save_finished 2→5, 0 исключений. Ожидание задания «Dish −1» не подтвердилось: CheckItem только проверяет предмет. Решение за владельцем.", None),
 "IT-02": ("OBSERVATION", "CC-90 в форме NRE QuestManagerSO.cs:235 НЕ воспроизведён: Back to menu→New Game сбросил квест (0,0) и инвентарь, 0 исключений. Но повторный первый разговор: 18 реплик, диалог не закрылся за 45 Space (завис на последней реплике), Seed 20→18, шаг 0→1. Та же картина, что в run8_d01 (1 выборка там, 1 здесь).", None),
 "M03-02": ("OBSERVATION", "Залипший Combat. _alertEnemies.Count в Beach (Gameplay, врагов нет) уже был 4. A: 4→5 (тревога) →4 (ушёл), состояние осталось Combat. B: 4→5, смена локации через меню читов (C открывается и в Combat) → Count 5 в Beach, Combat. C: убийство врага 6→5, Combat. D: Back to menu→New Game вернул Gameplay, но Count остался 5; подход и уход: 6→5, Combat. Вывод: Gameplay возвращается только при пустом списке, а в списке есть чужие записи; ни один из случаев A–D список не опустошил. Гипотеза по счётчику подтверждена числами; откуда исходные 4 записи, не установлено.", None),
 "DLG-10b-No": ("BLOCKED", "Play №2 не начат: restart_play.py --restore-save перед ним вернул код 4 (Play остановлен, Ctrl+P не отправлен: окно Unity не стало активным). По п.1.3 дальше всё BLOCKED.", None),
 "IT-02c": ("BLOCKED", "Play №2 не начат: restart_play.py вернул код 4 (см. DLG-10b-No).", None),
 "E2E-01": ("NOT_RUN", "Play №3 не начат: 2.1 и 2.2 были PASS, но после кода 4 от restart_play.py (перед Play №2) по п.1.3 всё BLOCKED, новых перезапусков не делали.", None),
}
for x in j["cases"]:
    if x["id"] in U:
        v, n, _ = U[x["id"]]
        x["verdict"] = v; x["date"] = "2026-11-25"; x["run"] = "modules_stage2_retry"; x["source"] = SRC; x["notes"] = n
        x["needs_clean_play"] = x["id"] not in ("M03-02",) 
        if x["id"] == "IT-02": x["depends_on"] = ["IT-03"]
        if x["id"] == "M03-02": x["needs_clean_play"] = False
        if x["id"] == "IT-12": x["depends_on"] = ["IT-03", "IT-04"]
json.dump(j, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(j["cases"]), [(x["id"], x["verdict"]) for x in j["cases"] if x["id"] in U])
