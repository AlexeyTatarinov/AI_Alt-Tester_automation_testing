# Модули Chop Chop, этап 3 — отчёт (25.11.2026)

**Итог: выполнен только Play A (IT-02c2 и IT-10). Play B (E2E-01b, E2E-02 с IT-05 и M03-02b, IT-11) НЕ выполнен: после перезапуска редактора Unity Play перестал запускаться.** Игра НЕ в MainMenu, Play остановлен, запустить его должен владелец. save.chop и .bak в обеих папках равны копии `20261122_122526` (проверено `cmp`, 4 файла). `Physics.autoSyncTransforms` сброшен остановкой Play.

## 1. Таблица вердиктов

| ID | Вердикт | Суть |
|---|---|---|
| IT-02c2 (Continue после первого разговора) | **FAIL** | Диалог закрылся, но Seed 20→**12** (−8, а не −1), RockCandy_Recipe +1 лишний, квест (0,1)→(1,2), в логе 22 исключения |
| IT-10 (настройки после Continue) | **OBSERVATION** | Язык сохраняется всегда. Громкость сохраняется, только если нажать Save на вкладке Audio до перехода к языку. Один Save на вкладке Language громкость теряет |
| E2E-01b (Ayud) | **BLOCKED** | Play B не начат (п.3) |
| IT-05 | **BLOCKED** | то же |
| E2E-02 | **BLOCKED** | то же |
| M03-02b | **NOT_RUN** | то же; в `cases_state.json` дописано |
| IT-11 | **BLOCKED** | то же |
| IT-07 | **OBSERVATION (составной, без прогона)** | M08-01 OBSERVATION, M18-01 PASS, M07-01 PASS, LOC-01 PASS, LOC-02 PASS |
| IT-09 | **OBSERVATION (по ссылке)** | закрыт ссылкой на M03-01 (OBSERVATION) |

## 2. Play A: снимки «до/после»

Перезапуск: `--restore-save` дал код 4, затем `--start-only` ×3 (4, 4, **0**), см. п.4. New Game 1 раз. Json: `a1.json`, `a2.json`, `a2b.json`; вывод скриптов `a1.out`, `a1b.out`, `a2.out`, `a2b.out`.

`_alertEnemies.Count`: до всех действий **5**, после Continue **5** (врагов в Play A не трогали). Считался на снимках разговора (п.2.1), на снимках IT-10 не писался.

### 2.1. IT-02c2

| Шаг | Seed | Прочее | Квест (line,step) | save.chop | save_finished | Состояние / Count |
|---|---|---|---|---|---|---|
| старт после New Game | 20 | PhoenixChick 1, три вида яиц по 20, SpecialSpoon 1 | 0,0 | 628fab9e | 0 | Gameplay / 5 |
| первый разговор (18 Space, **17 реплик**, закрылся) | 20 | — | 0,**1** | 8d5f8004 | 1 | Gameplay / 5 |
| Back to menu → **Continue** (загрузка 3,4 с) | 20 | то же | 0,1 | 8d5f8004 | 1 | Gameplay / 5 |
| Разговор после Continue: «Did you gather the seeds from the Groens up the hill?», Yes/No, нажат Yes | **12** | SweetCream_Recipe +1, **RockCandy_Recipe +1** | **1,2** | f2d39958 | **5** | Gameplay / 5 |

Разница «после Continue» с «до выхода»: пусто (инвентарь, квест, save равны). Диалог закрылся (Gameplay, панели нет 4 опроса подряд, 11 реплик).

Критерии PASS: диалог закрылся — да; Seed −1 ровно раз — **нет (−8)**; SweetCream_Recipe +1 ровно раз — да; шаг 1→2 — **нет, квест прыгнул на (1,2)**; исключений 0 — **нет (22)**.

Исключения (Editor.log, `a1.json` → `exc`):
- `NullReferenceException` ×1: `QuestManagerSO.EndDialogue`, `QuestManagerSO.cs:235`, вызван из `IntEventChannelSO.RaiseEvent` (`IntEventChannelSO.cs:17`) и `DialogueManager.DialogueEndedAndCloseDialogueUI` (`DialogueManager.cs:167`).
- `ArgumentOutOfRangeException` ×21: `DialogueManager.get__reachedEndOfLine`, `DialogueManager.cs:31`, из `DialogueManager.OnAdvance`, `DialogueManager.cs:77`.

Вывод по фактам: после Continue одно действие даёт многократную обработку (Seed −8, пять завершённых шагов вместо одного). Это согласуется с гипотезой «повторные подписки после Continue» (природа CC-90), но причину в коде я не проверял. Решение о баге за владельцем. Это была попытка 1 из 2; повтор невозможен: нужен чистый Play, а Play не запускается.

### 2.2. IT-10

Play грязный (после п.2.1). В save.chop `_currentLocale` хранится как `{instanceID: N}`: English 48776, français 46952, в копии 0.

**Попытка 1 (как в задании: Master Previous, язык Next, один Save на вкладке Language)**, `a2.json`:

| Момент | GetGroupVolume Master | save `_masterVolume` | язык | save `_currentLocale` |
|---|---|---|---|---|
| старт | 1.0 | 1.0 | English | 0 |
| после Previous (до Save) | 0.9 | — | — | — |
| после Save | **1.0** | **1.0** | français | 46952 |
| в MainMenu | 1.0 | 1.0 | меню: CONTINUER, NOUVELLE PARTIE, PARAMETRE, CREDITS, QUITTER | 46952 |
| после Continue | 1.0 | 1.0 | français | 46952 |
| возврат (Next, Previous до English, Save) | 1.0 | 1.0 | English | 48776 |

Громкость 0.9, выставленная до перехода на вкладку Language, не сохранилась. Язык сохранился. Текст одной кнопки: «CONTINUER» (MainMenu, французский).

**Попытка 2 (Save на вкладке Audio до перехода к языку)**, `a2b.json`:

| Момент | Master | save `_masterVolume` | язык | save `_currentLocale` |
|---|---|---|---|---|
| после Previous + Save (Audio) | 0.9 | 0.8999999761581421 | English | 48776 |
| после смены языка + Save | 0.9 | 0.8999999761581421 | français | 46952 |
| в MainMenu | 0.9 | 0.89999997 | меню по-французски | 46952 |
| после Continue | **0.9** | 0.89999997 | **français** | 46952 |

Критерий PASS («после Continue громкость и язык те же, что выставлены») выполнен в попытке 2, не выполнен по громкости в попытке 1. Пункт 4 (вернуть English и сверить save с копией) выполнен только в попытке 1 (громкость 1.0, English). В попытке 2 на шаге возврата связь с игрой пропала (см. п.3). Равенства save.chop копии в грязном Play быть не может: в save уже есть шаги квеста. Его сверил финальный `cmp` после остановки Play (равны).

Исключений: попытка 1 — 0; попытка 2 — не сверено, скрипт оборван.

Наблюдение для владельца: изменение громкости теряется, если уйти с вкладки Audio на Language без Save. Это может быть задумано.

## 3. Play B: BLOCKED

Во время попытки 2 IT-10 (Play A) связь с игрой оборвалась (`CommandResponseTimeoutException`, затем «No app connected»). Редактор Unity оказался перезапущенным: PID главного окна **13604 → 11708**, появился `Assets/_Recovery/0.unity`. Я его не перезапускал. После этого Play не запускается: Ctrl+P отправляется, в Editor.log Play входит («Reloading assemblies for play mode») и сразу выходит («Loaded scene Temp/__Backupscenes/0.backup»), AltTester не отвечает. В логе также «Missing Prefab Asset» для 4 префабов в `MainMenu.unity` (Ground_Path_Level3, Rocks_Path_BackSide, Ground_Path_Level2, Rocks_Path_Divider). Связь этого с отказом Play не доказана. Проект и игру не менял.

Все вызовы после перезапуска редактора дали код 3 (не 4, поэтому п.2.1 про код 4 к ним формально не относится; повторял так же, с паузами). Дальше всё BLOCKED: E2E-01b, IT-05, E2E-02 (+M03-02b), IT-11 не начаты.

## 4. Перезапуски Play

| № | Команда | Код | Результат |
|---|---|---|---|
| 1 | `--restore-save` (перед Play A) | **4** | Play остановлен, Ctrl+P не отправлен; `restart1.out` |
| 2 | `--start-only` (через 2 мин) | 4 | `restart1_so1.out` |
| 3 | `--start-only` (через 2 мин) | 4 | `restart1_so2.out` |
| 4 | `--start-only` (через 2 мин) | **0** | MainMenu, Play A; `restart1_so3.out` |
| 5 | `--start-only --restore-save` (перед Play B) | **3** | Ctrl+P отправлен, AltTester за 120 с не ответил; `restart2.out`, `restart2_last.json`; save возвращён к копии |
| 6 | `--start-only` | 3 | `restart2_so1.out` |
| 7 | `--start-only` | 3 | `restart2_so2.out` |
| 8 | `--start-only` | не получен | процесс оборвало моё ограничение времени фонового запуска; Ctrl+P отправлен в 22:36:30; `restart2_so3.out` (неполный) |
| 9 | `--start-only` | 3 | `restart2_so4.out`, `restart2_so4_last.json` |

Всего вызовов 9 из 12; плановых `--restore-save` 2 из 3 (вызовы 1 и 5). Три оставшихся вызова не тратил: четыре попытки подряд дали одну картину (Play входит и сразу выходит), повтор без вмешательства владельца ничего не меняет. Финальный `--restore-save` (раздел 5 задания) сделать нельзя: нужен идущий Play. save.chop возвращён вызовом 5 и проверен `cmp`.

## 5. Ошибки скриптов (отдельно от игры)

- `a1.py`, первый запуск: подсказка E у BardHare не появилась. Причина: телепорт на 1,3 м стоит у границы триггера (подсказка видна на ~1,1 м и пропадает при выходе из него). Исправлено в `s3lib.to_hare()` (1,3 / 1,1 / 1,0 м, подсказка проверяется после каждого шага). New Game не повторял: продолжил в том же Play (`resumed_after_script_error: true` в `a1.json`).
- Python запускался без `-I` (иначе не находятся мои библиотеки `s3lib` и `elib`); скрипты лежат в `scripts\stage3\`, данные не читал.
- `a2.py`: кнопки меню искал по неверным именам (`ResumeButton`), текст кнопки паузы не прочитан; в `a2b.py` взят `menu_texts()` (в паузе прочитан только «/»), текст кнопки взят из MainMenu («CONTINUER»).
- Фоновый запуск цикла `--start-only` оборвало моё ограничение времени (вызов 8).
- Инструмент: `restart_play.py` коды 4 (×3 в начале) и 3 (×4 после перезапуска редактора).

## 6. Баг-кандидаты (без Jira)

1. **После Continue один Yes в разговоре даёт многократную награду.** Шаги: New Game → первый разговор с BardHare → Back to menu → Continue → разговор → Yes. Результат: Seed −8, пять шагов квеста вместо одного, 22 исключения. Частота 1 из 1. `QuestManagerSO.cs:235` (NRE), `DialogueManager.cs:31`, `:77` (ArgumentOutOfRange ×21), `DialogueManager.cs:167`.
2. **Громкость теряется при смене вкладки Settings без Save.** Шаги: Pause → Settings → Audio, Master Previous → Language_Tab → язык Next → Save. Результат: язык сохранён, громкость вернулась к 1.0. Частота 1 из 1 (при Save на вкладке Audio громкость сохранилась и пережила Continue). Исключений нет.
3. **`_alertEnemies.Count` = 5 в начале Play A** (как в stage2b), 0 не наблюдался ни разу.

## 7. Что осталось без вердикта

Из таблицы раздела 3 модульного документа без вердикта остались: **E2E-01b, IT-05, E2E-02 (M03-02b), IT-11**. Причина: Play B не запускается после перезапуска редактора Unity (п.3). IT-07 и IT-09 закрыты составным вердиктом и ссылкой без прогона, как велит задание.

## 8. Что нужно от владельца

1. Запустить Play вручную. Редактор перезапущен, Play входит и сразу выходит; посмотреть Console и сцену `MainMenu` («Missing Prefab Asset» в `MainMenu.unity`). Я проект не менял.
2. После этого Play B (п.4 задания) выполнить отдельным заданием.

## 9. Состояние на завершение

- Игра **не в MainMenu**: Play остановлен, Unity (PID 11708) работает.
- save.chop и .bak в обеих папках равны копии (`cmp`). `autoSyncTransforms` = False (Play остановлен).
- Не нарушены: мышь, computer use, Ctrl+Shift+P, Jira, Confluence, Initialization, второй драйвер, игра и проект. Ctrl+P отправлял только `restart_play.py`.
- Обновлено: `cases_state.json` (копия «до»: `opus_review_20261124\cases_state.before_stage3.json`): IT-02c FAIL, IT-10 OBSERVATION, E2E-01b / IT-05 / E2E-02 / IT-11 BLOCKED, M03-02 допись, IT-07 и IT-09 составные.
- Скрипты: `scripts\stage3\` (`s3lib.py`, `a1.py`, `a2.py`, `a2b.py`).
