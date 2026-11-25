# Отчёт d01 (прогон 8): чистый Play, диалоги, рецепт, готовка
Дата: 24.11.2026. Скрипты: scripts\fast_run8\ (d01_a.py, d01_a2.py, d01_c1..c5.py, d01_d.py, fin.py). Сырые данные: d01_a.json, d01_d.json, inv_after_yes.json.

## Предусловие
- Чистый Play: realtimeSinceStartup 61,96 с, frameCount 4072 (порог 1200 с соблюдён). Перед этим `restart_play.py --check` (код 0): Play свежий, Error Pause выключен (7683).
- **Отклонение от буквы задания (прошу проверить).** До New Game в save.chop `_finishedQuestlineItemsGUIds` содержал 5 GUID. Это не «грязный Play»: файл по хешу (33c38933a6cb735c) равен эталонной копии save_backup\20261122_122526, а в игре сохранение показывает «остаток старого сохранения до New Game» (game_behaviors.md, SAVE-06). Буквальное чтение правила блокировало бы любой запуск (restart_play --restore-save даёт то же состояние), поэтому я его считал признаком грязи только при ином хеше. Полного разговора с BardHare с начала Play не было. После New Game список стал 0 (проверено).

## 1) INT-03: первый разговор — ПОДТВЕРЖДЕНО (PASS)
- New Game 3,5 с. Подсказка E на 0,81 м. Space (0,1 с, пауза 1 с): **N = 18, реплик 17, диалог закрылся, исключений 0, кнопок нет**. Ожидание (18) совпало.
- В save.chop шаг квеста: 0 → 1 (GUID 2187c1f1…).

## 2) DLG-10b: второй разговор, Yes — PASS
- E сразу, первая реплика «Did you gather the seeds from the Groens up the hill?», **один Space → кнопки Yes / No**.
- Клик по ButtonChoice1 (Yes): **Seed 20 → 19**, **SweetCream_Recipe +1 (0 → 1, вкладка Recipe, tab 2)**. Диалог после Yes ещё 8 реплик (последняя: «You can try cooking it yourself using the cauldron just here…»), закрылся после ещё 2 Space. Исключений 0. Шагов квеста стало 2.

## 3) COOK-01: готовка — PASS по результату, но с исключением
- Состав SweetCream_Recipe (из IngredientsList): **3 × Seed**; результат SweetCream_Dish. В инвентаре Seed 19 — хватает.
- Телепорт к PotOverFire (T1, autoSync=True), подсказка E, E → открылся инвентарь на вкладке Recipe. Клик по рецепту, кнопка действия активна, Q один раз.
- Итог: **SweetCream_Dish +1 (0 → 1), Seed 19 → 16 (списано 3)**, рецепт остался (1), save.chop изменился (a995c076… → 2ab4c2a1…), инвентарь закрылся.
- **Исключение: 1 × NullReferenceException в UIActionButton.ClickActionButton (UIActionButton.cs:42), вызов из InputReader.OnInventoryActionButton (InputReader.cs:100).** Готовка при этом сработала. Это то же место, что ранний FAIL INV-10 (run2, CC-79/CC-81) — теперь воспроизведено на чистом Play при нажатии Q на рецепте.

## 4) CC-90: Back to menu → New Game → разговор — НЕ ПОДТВЕРДИЛОСЬ в ожидаемой форме
- Back to menu 0,7 с, New Game 2,0 с, список шагов после New Game = [] (сброшен).
- Диалог **не короткий**: снова полная последовательность (18 реплик: «You made it! Welcome to Yolk island!» … «They are the key ingredient in my grandma's recipe for an amazing sweet cream.»), **исключений 0** (NRE QuestManagerSO.cs:235 и ArgumentOutOfRange НЕ было), ожидаемого «You can try cooking…» нет.
- Но диалог **завис на последней реплике**: после 45 Space (0,1 с, пауза 1 с) он остался открыт, кнопок Yes/No нет, меню паузы не открыто; повторная проверка без нажатий — то же состояние. Квест при этом записал 1 шаг (2187c1f1…). Дальше ничего не нажималось (по заданию).
- Факт: симптом после Back to menu → New Game в этом Play другой, чем в CC-90 (нет исключений, зависание на реплике про рецепт бабушки). Одна выборка; требует решения владельца, считать ли это подтверждением CC-90 («квест не сбрасывается»: в этот раз он сбросился до [] и диалог начался заново).

## Завершение
- save.chop и .bak (обе папки) возвращены из копии save_backup\20261122_122526, **хеши совпали** (33c38933a6cb735c, aa50702879c37079, и .bak).
- Physics.autoSyncTransforms = False (проверено).
- Игра и проект не менялись, Initialization не загружалась, мышь/computer use/Ctrl+Shift+P/Q в диалоге не использовались. Окно восстанавливалось через guard.restore_window (потребовалось 1 раз). Jira/Confluence не трогались.
- Замечание: скриншоты сохранялись скриптами в run7_new5_20261123\shots (путь guard/fastlib), не в папке этого отчёта.
- Play после этапа 4 снова «грязный» (диалог открыт, quest [] -> 1): перед следующим прогоном нужен Stop/Play.
