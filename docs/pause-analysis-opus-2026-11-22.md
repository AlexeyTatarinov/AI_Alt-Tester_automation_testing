# Почему Unity «зависает» во время автотестов и как это убрать

Дата: 22.11.2026. Автор: Opus (анализ только по файлам, ничего не запускалось и не менялось).
Проект: AI game testing portfolio, Chop Chop, Unity 6000.3.28f1, AltTester 2.4.1/2.4.2, Python SDK 2.4.1.

---

## 1. Резюме

1. **Вероятнее всего (≈ 90 %), игра не зависает: Unity ставит Play на паузу сам, потому что в Console включена кнопка «Error Pause».** Каждая остановка в логах начинается сразу после строки уровня «ошибка».
2. Доказательство из трёх снимков окна (16:35, 16:37, 18:34): у кнопки Error Pause фон светлее, чем у соседних (цвет 64 против 48 у Clear, Collapse и Editor). Так Unity рисует **включённую** кнопку. Раньше в отчёте прогона 2 было записано «Error Pause не включён». Скорее всего, это ошибка чтения снимка.
3. В Editor.log при каждой остановке видно одно и то же. Команды AltTester приходят («command received»), но ответов нет («response sent» не пишется). Значит, главный цикл игры стоит, а процесс жив.
4. Что вызывает ошибку перед паузой. **Q в инвентаре** (NullReferenceException, CC-81). **Space в диалоге** (MissingReferenceException, StepController). **Загрузка Forest**: враги пишут ошибку NavMeshAgent «Stop can only be called…». **Загрузка MainMenu**: «Problem detected while opening the Scene file…», это, скорее всего, и есть зависание меню из CC-70.
5. Гипотеза 2 (настоящая блокировка при загрузке Forest): ≈ 5 %. Forest загрузилась полностью, процесс отвечал Windows (Responding = True), CPU ≈ 1 %.
6. Гипотеза 3 (AltTester/Input System «ломаются» после исключения): как причина остановки ≈ 5 %. После снятия паузы SDK снова отвечал. Но исключение портит состояние игры: например, панель диалога остаётся висеть. Это отдельная проблема игры, а не пауза.
7. Вариант «окно Unity свёрнуто»: ≈ 15 % как дополнительный фактор в случае Forest. Окно было свёрнуто, но пауза объясняет всё и без этого.
8. **Первое действие:** владелец за 1 минуту выключает кнопку Error Pause в окне Console и не сворачивает Unity во время прогонов.
9. **Затем Code:** добавляет в fastlib/lib_sdk проверку «жива ли игра» и распознавание паузы по Editor.log, затем делает контрольный прогон MainMenu → Forest.
10. **Решить владельцу:** выключить Error Pause (рекомендую: да) и разрешить Code читать флаги Console через SDK (рекомендую: да). Нужны ли помощник в Editor и удалённый доступ, решить после контрольного прогона.

---

## 2. Хронология и данные

### Что было доступно

- `Editor.log` (383 МБ). В 16:31:58 файл перезаписал короткий посторонний запуск Unity.exe (лицензия и выход). Работающий редактор продолжил писать в него со своего места, поэтому первые ≈ 343 МБ файла — нулевые байты. **Лог с 10:42 до 16:33 22.11 потерян**: случаи INV-10 (15:23) и Forest (≈16:00) видны только по отчёту, `INV-10_exception_editor_log.txt` и снимкам. Читаемая часть — с 16:33:26 до 18:51.
- `Editor-prev.log` — сессия 21.11, 19:05–21:28, включая зависание меню перед созданием CC-70 (19:44).
- Отчёт прогона 2, json, скрипты, снимки окна Unity, Jira CC-70/81/82, Confluence 327707.

### Как я отличал «паузу» от «блокировки»

AltTester пишет в лог две строки. «command received» пишется из сетевого потока и появляется всегда. «response sent» пишется из `AltRunner.Update` → `AltResponseQueue.Cycle`: это видно по стеку в логе, то есть строка пишется из обычного кадра игры. Есть «received», но нет «sent» — кадры не идут. Растёт ли лог при этом, ничего не говорит: в Beach Unity пишет предупреждение «There are 2 audio listeners…» (≈ 33 КБ/с) и во время паузы.

### Таблица остановок

| № | Время | Что делали | Что в логе перед остановкой | Во время остановки | Чем закончилось | Вывод |
|---|---|---|---|---|---|---|
| 0 | 21.11 19:36:06 → 19:37:56 (109 с) | Ручная игра/тест, выход в главное меню | `Problem detected while opening the Scene file: 'Assets/Scenes/Menus/MainMenu.unity'` + 4 строки `Prefab instance problem. Missing Prefab Asset` | Запрос getAllLoadedScenes без ответа 109 с | Ответ пришёл в 19:37:56 (вероятно, ручной Pause/Unpause). В 19:44 создана CC-70 | Пауза после ошибки загрузки MainMenu. Совпадает с жалобой в CC-70 |
| 1 | 22.11 15:21:38 → 15:49+ | INV-10: Q в открытом инвентаре | `NullReferenceException … UIActionButton.cs:42`, затем `Debug.LogError` «…while executing 'performed' callbacks of 'Menus/InventoryActionButton…'» (файл INV-10_exception_editor_log.txt) | SDK: CommandResponseTimeoutException. Лог в этот момент не рос (0 байт за 5 с) | Ждали владельца | Пауза после ошибки. Сам лог за это время потерян |
| 2 | 22.11 ≈15:59:52 → 16:35:07 | LOC-03: клик Forest в меню читов (C) | В Console на снимке 16:35: «[15:59:52] "Stop" can only be called on an active agent that has been placed on a NavMesh» (ошибка уровня Error из `StopAgentSO.cs:32`, враги Forest) | Окно Unity было свёрнуто, Responding = True, CPU ≈ 1 % | Окно развернули, нажали Ctrl+Shift+P в 16:35:07: запросы сразу получили ответы. В 16:35:08 снова ошибка «Stop…», и Play снова на паузе. Второе Ctrl+Shift+P в 16:36:06 снова запустило игру | Пауза после ошибки NavMesh при загрузке Forest. «Первое нажатие поставило паузу» — на самом деле первое сняло паузу, а новая ошибка через 1 с поставила её снова |
| 3 | 22.11 16:36:49 → 18:27:29 | Возврат из Forest в главное меню (clickElement) | `Problem detected while opening the Scene file: …MainMenu.unity` + Missing Prefab ×4 | Подключения в 16:36:57, 16:37:43, 17:11:53, 18:25:59 — только «received» | Владелец снял паузу ≈ 18:27:29 | Как №0: пауза после загрузки MainMenu |
| 4 | 22.11 18:28:25 → 18:31:15 | stage0 (New Game прошёл), затем INT-03: Space в диалоге Maqam | `Uploading Crash Report`, `MissingReferenceException: … 'StepController' has been destroyed` (StepController.cs:128 ← DialogueManager.OnAdvance ← InputReader.OnAdvanceDialogue), затем `Debug.LogError` «…'performed' callbacks of 'Dialogues/AdvanceDialogue…'» | Ответа на нажатие Space нет | Владелец снял паузу ≈ 18:31:15 | Пауза после ошибки |
| 5 | 22.11 18:31:32 → сейчас | Повторное Space/Return для закрытия диалога | То же исключение StepController + LogError | С 18:32 только «received». На снимке 18:34 кнопка Pause нажата | Не снято | Пауза после ошибки |

Вывод по таблице: **все 6 остановок начинаются сразу после строки уровня Error.** Ни одна не началась без такой строки. Прогон 1 (11:47–12:04) прошёл без остановок: в нём были загрузки Field_Hill и Beach, а ошибок в логе было 0 (run1_loc01.json, run1_loc02.json).

Побочные наблюдения (не баг-кандидаты, просто факты из лога):
- Строка «Uploading Crash Report» стоит перед каждым исключением в Input System. Это служебная запись Unity, а не падение редактора.
- В MainMenu не хватает 4 префабов (Missing Prefab). При загрузке Beach через New Game ошибок нет.
- Editor.log раздувают отладочные строки AltTester (у каждой полный стек) и спам «2 audio listeners».

---

## 3. Проверка гипотез

### Гипотеза 1: включена Error Pause, и Unity ставит паузу после ошибки

**За:**
- Документация Unity 6000.3: Error Pause «Pauses playback when you call Debug.LogError from a script» ([Console window reference 6000.3](https://docs.unity.com/en-us/engine/6000.3/manual/unity-editor/editor-windows-views-reference/console-window/console.md)). Input System при исключении в callback сам вызывает `Debug.LogError(...while executing 'performed' callbacks...)`, это видно в стеке случаев 1, 4 и 5.
- Все 6 остановок начинаются сразу после ошибки (таблица выше).
- Пиксели снимков: фон кнопки Error Pause — (64,64,64), фон Clear/Collapse/Editor — (48,48,48). Так на всех трёх снимках, которые сняты с разницей в 2 часа, поэтому это не наведение мыши. Вырезки сохранены в `/mnt/user-data/outputs/claude/pause-analysis-errorpause-crops.png`.
- Случай Forest объясняется без натяжек: после снятия паузы через 1 с пришла новая ошибка NavMesh, и Play снова встал.

**Против:**
- Агент прогона 2 дважды записал «Error Pause не включён». Но он не сравнивал цвет с соседними кнопками.
- Для MainMenu не доказано, что строка «Problem detected…» имеет уровень Error, а не Warning. Это видно только по иконке в Console.

**Минимальная проверка (владелец, 1 минута, без запуска чего-либо):** открыть в Unity вкладку Console. Посмотреть, выделена ли (светлее соседних) кнопка «Error Pause». Заодно посмотреть, красная или жёлтая иконка у строки «Problem detected while opening the Scene file…MainMenu». Если кнопка выделена, нажать её один раз, чтобы выключить.

**Вероятность: ≈ 90 %** для случаев 1, 3, 4, 5. Для случая 2 — ≈ 80 %, для CC-70 (меню) — ≈ 80 %.

### Гипотеза 2: настоящая блокировка главного потока при загрузке Forest

**За:** SDK не отвечал, причина не была записана, лог за 15:59–16:25 потерян.

**Против:**
- При блокировке главного потока Windows показывает «Не отвечает» (Responding = False), а здесь было True. CPU ≈ 1 %: это не похоже на зависшую загрузку или вечный цикл.
- На снимке 16:35 Forest полностью загружена: в иерархии PersistentManagers, Gameplay, Forest.
- Сразу после Ctrl+Shift+P накопленные запросы получили ответы (16:35:07).
- Forest.unity весит 4,8 МБ, это меньше Beach (5,6 МБ). Beach и Field_Hill грузились за 1,0–1,8 с.

**Проверка:** повторить клик Forest с выключенной Error Pause и диагностикой (раздел 6).

**Вероятность: ≈ 5 %.**

### Гипотеза 3: AltTester/Input System остаются в плохом состоянии после исключения

**За:** после исключения от Q панель диалога осталась на экране и не листалась (CC-81, INT-03 «Не проверено»).

**Против:** после снятия паузы SDK отвечал: 18:27–18:28 больше 130 ответов, 18:31 ещё 29, до следующего исключения. Значит, AltTester и связь в порядке. Зависшая панель — это полусделанная работа игрового кода, который прервало исключение (DialogueManager, UIActionButton). Она остаётся и без паузы.

**Вероятность как причины «зависания»: ≈ 5 %.** Как причины испорченного состояния игры после исключения — да, но это отдельная тема (дефект игры).

### Гипотеза 4 (новая): окно Unity было свёрнуто

**За:** в 16:33 окно было свёрнуто (IsIconic = True), и запросы получили ответы ровно в момент разворота и нажатия.

**Против:** развёртывание и Ctrl+Shift+P совпали по времени, их нельзя разделить. Документация говорит, что в Play Mode Unity игнорирует ограничение частоты кадров редактора ([Preferences → General, Interaction Mode, 6000.3](https://docs.unity.com/en-us/engine/6000.3/manual/unity-editor/editor-settings-reference/preferences/general)). Но про свёрнутое окно там ничего нет.

**Вероятность: ≈ 15 %** как дополнительного фактора. Мера та же, что и без доказательства: не сворачивать окно Unity во время прогонов.

### Гипотеза 5 (снята): runInBackground

По CC-70 при runInBackground = выкл и потере фокуса игра встаёт. Сейчас runInBackground = 1 и в ProjectSettings.asset (строка 91), и в рантайме (run2_state.json: `runInBackground_now: true`). К случаям 22.11 это не относится.

---

## 4. Где Unity хранит Error Pause

- Флаг хранится не в файлах проекта. В исходниках Unity (UnityCsReference, `Editor/Mono/ConsoleWindow.cs`) Error Pause — это бит `ConsoleFlags.ErrorPause = 1 << 2` (значение 4) в `LogEntries.consoleFlags`. Чтение: `HasFlag(...)`, запись: `LogEntries.SetConsoleFlag(...)`. Есть и обёртки `ConsoleWindow.GetConsoleErrorPause()` / `SetConsoleErrorPause(bool)`, но класс `ConsoleWindow` — `internal` ([исходник](https://raw.githubusercontent.com/Unity-Technologies/UnityCsReference/master/Editor/Mono/ConsoleWindow.cs)).
- Сам `LogEntries` реализован в движке. Где именно он сохраняет флаги между сессиями, в открытом коде не видно. Скорее всего, в EditorPrefs. На Windows EditorPrefs лежат в реестре `HKCU\Software\Unity Technologies\Unity Editor 5.x` ([EditorPrefs](https://docs.unity3d.com/ScriptReference/EditorPrefs.html)). Это мой вывод, точное имя ключа не подтверждено.
- Проверил файлы: `UserSettings\EditorUserSettings.asset`, `UserSettings\Layouts\default-6000.dwlt` (окно Console там есть, но без флагов), `CurrentMaximizeLayout.dwlt`, `ProjectSettings\EditorSettings.asset`. **Значения Error Pause в них нет.** Реестр через мост читать нельзя.
- **Итог: из файлов значение прочитать нельзя.** Косвенно, по снимкам окна, — **включено** (раздел 3).
- Так это можно будет проверить автоматически (требует 1 пробного вызова и разрешения владельца, раздел 5б): прочитать `UnityEditor.LogEntries.consoleFlags` через SDK, пока игра идёт.
- Известно, что Error Pause могут включить и не руками: на форуме Unity описано, что запуск Test Runner меняет «Run in background» и «Error Pause» и не возвращает их обратно ([discussions.unity.com](https://discussions.unity.com/t/running-tests-sets-run-in-background-and-error-pause-but-does-not-revert/762580)).

---

## 5. Решение для нашего процесса (по слоям)

### а) Настройки Editor (убирают причину)

| Что | Где | Как проверить | Простота | Надёжность | Риск | Стоимость | От владельца |
|---|---|---|---|---|---|---|---|
| **Выключить Error Pause** | Окно Console → кнопка «Error Pause» на панели (рядом с Collapse) | Кнопка не светлее соседних. При первой ошибке Play не встаёт | 5 | 5 | Ошибки больше не останавливают игру. Их надо ловить по логу, наш `log_since` это уже делает | 0 € | 1 клик |
| Не сворачивать окно Unity во время прогона (можно не в фокусе) | Привычка, плюс пункт в чек-листе перед прогоном | Code перед стартом проверяет, что окно не свёрнуто (IsIconic = False) | 5 | 4 | Нет | 0 € | Не сворачивать |
| Не запускать второй Unity.exe во время прогона | Правило для Code | — | 5 | 5 | Иначе Editor.log затирается, и улики теряются (так было в 16:31:58) | 0 € | — |
| Оставить runInBackground = вкл (уже так) | Пролог скриптов уже ставит True | `runInBackground_now: true` | 5 | 5 | — | 0 € | — |
| (по желанию) Меньше мусора в Editor.log: в Console → ⋮ → Stack Trace Logging → для «Log» поставить None | Меняет настройки проекта (PlayerSettings) | Лог растёт медленнее | 4 | — | **Изменение проекта, требует решения.** Exception и Error не трогать | 0 € | Решение |

### б) Страховки в нашем Python-коде (lib_sdk.py / fastlib.py)

1. **Предстартовая проверка (preflight)**, до первого кейса:
   - `runInBackground` = True (уже есть).
   - Попытаться прочитать флаги Console: `d.get_static_property("UnityEditor.LogEntries", "consoleFlags", "UnityEditor.CoreModule")`. Если вызов работает и `flags & 4 != 0`, Error Pause включена: остановиться и написать владельцу. Сам флаг не менять без разрешения. Если AltTester не найдёт внутренний класс (он `internal`), записать «не читается» и полагаться на п. 2–3. Нужен 1 пробный вызов. Запись (`call_static_method("UnityEditor.LogEntries","SetConsoleFlag",...,["4","false"],["System.Int32","System.Boolean"])`) делать только с согласия владельца: она меняет настройку его редактора.
   - Окно Unity не свёрнуто.
2. **«Жива ли игра» перед каждым кейсом и после каждого рискового шага:** отдельное короткое подключение с маленьким тайм-аутом (например, `AltDriver(..., timeout=5)`). Два чтения `Time.frameCount` с промежутком 0,5 с. Кадры растут — жива. Если `CommandResponseTimeoutException` или кадры не растут, игра стоит.
3. **Распознавание причины по Editor.log (без SDK):** запомнить размер лога перед шагом. После тайм-аута прочитать новый хвост:
   - есть «command received» и нет «response sent» → кадры не идут (пауза или блокировка);
   - последняя строка уровня ошибки перед этим (`Exception`, `while executing 'performed' callbacks`, `can only be called on an active agent`, `Problem detected while opening the Scene file`) → почти наверняка **пауза после ошибки**. Записать эту строку в отчёт;
   - ошибок нет → «неизвестная остановка», сделать снимок экрана окна, собрать CPU/Responding процесса.
   - Важно: проверять не только `^...Exception`. Наш `log_since` сейчас не считает ошибками строки «"Stop" can only be called…» и «Problem detected…», поэтому в прогоне 1 «ошибок 0» могло быть неполным.
4. **Автоматически снять паузу через SDK нельзя.** Все команды AltTester выполняются в `AltRunner.Update`, а на паузе Update не вызывается: запрос `set_static_property("UnityEditor.EditorApplication","isPaused",...,False)` просто встанет в ту же очередь. `EditorApplication.isPaused` можно менять из скрипта ([isPaused, 6000.6](https://docs.unity.com/en-us/engine/6000.6/script-reference/unityeditor/editorapplication/ispaused)), но только из кода, который работает в редакторе, а не в игре.
5. **Снять паузу нажатием клавиш (Ctrl+Shift+P) из скрипта Windows** (PowerShell: развернуть окно Unity, вывести на передний план, отправить сочетание):
   - Ограничения: сочетание **переключает** паузу. Если игра не на паузе, оно её поставит. Поэтому нажимать только после того, как п. 2–3 показали «стоит», и сразу проверять кадры. Нужен передний план: можно попасть в чужое окно. Система безопасности Claude уже один раз заблокировала третью отправку клавиш (отчёт прогона 2, 16:38).
   - При включённой Error Pause и повторяющейся ошибке (Forest, StepController) снятие паузы ничего не даст: через кадр снова пауза.
   - Правило: не больше 2 попыток на одну остановку. После каждой — снимок окна и проверка кадров. Если не помогло, остановиться и записать в отчёт.
   - Простота 3, надёжность 3, стоимость 0 €. От владельца — разрешение на такие действия.
6. **Тайм-аут и повтор:** у кейса один повтор (всего ≤ 2 попытки), только если причина остановки — «пауза после ошибки» и пауза снята. Если ошибка случилась внутри проверки, кейс помечается «Не пройдено/Не проверено» с текстом ошибки, а не повторяется до бесконечности. Утверждённые пороги не меняются.
7. **Помощник в Editor (только предложение — изменение проекта, требует решения владельца).** Один файл `Assets/Editor/TestRunGuard.cs`, исключённый из git (`.git/info/exclude`). В сборку игры не попадает (папка Editor). Делает три вещи:
   - при входе в Play выключает Error Pause (`LogEntries.SetConsoleFlag(4,false)` через отражение) и пишет об этом в лог;
   - подписывается на `EditorApplication.pauseStateChanged` ([документация](https://docs.unity3d.com/ScriptReference/EditorApplication-pauseStateChanged.html)) и пишет в файл `Test_Ai\...\pause_events.log`: время, новое состояние, последнюю ошибку;
   - раз в секунду в `EditorApplication.update` (он работает и на паузе) проверяет файл-запрос `unpause.request`. Если файл есть, ставит `isPaused = false` и удаляет файл. Так Python снимает паузу без клавиш и фокуса.
   - Простота 3, надёжность 5, риск: добавленный код в проекте (CC-70 шаг 4), стоимость 0 €. Нужно решение владельца.

### в) Разделение рисковых кейсов

Рисковые шаги — те, что заведомо пишут ошибку в лог:

| Шаг | Какая ошибка | Что делать |
|---|---|---|
| Загрузка MainMenu (старт Play, выход в меню) | Problem detected… / Missing Prefab | Чекпойнт «до выхода в меню». Проба кадров через 5 с после загрузки |
| Смена локации на Forest (и, вероятно, другие локации с врагами) через меню читов | "Stop" can only be called on an active agent… | Отдельный блок в конце прогона. Проба кадров через 5 и 30 с |
| Space/E в диалоге после смены шага квеста | MissingReferenceException StepController | Диалоговые кейсы — отдельным блоком. После каждого — проба |
| Q (InventoryActionButton) | NullReferenceException UIActionButton | Не нажимать (решение принято) |

Порядок и чекпойнты:
1. Перед каждым рисковым шагом записать в `runN_state.json`: кейс, шаг, время, размер Editor.log, хеш save.chop.
2. После шага — проба «жива ли» (п. б2). Если стоит — распознать причину (п. б3) и записать её одной строкой в отчёт.
3. Восстановление без человека:
   - если пауза снята (Error Pause выключена или сработал помощник/клавиши), но игра в плохом состоянии (висит панель диалога): выйти в главное меню через меню паузы игры, затем New Game;
   - если выйти нельзя: остановить Play. Это возможно только клавишами Ctrl+P или через помощника. При остановке Play игра перезаписывает save.chop, поэтому после остановки восстановить его из копии. Сцену Initialization не открывать: Play запускать с той сцены, что уже открыта.
4. Рисковые блоки ставить в конец прогона, чтобы остановка не съедала безопасные кейсы.

### г) Если ничего не помогло: удалённое нажатие Pause

| Вариант | Как | Простота | Надёжность | Риск | Стоимость | От владельца |
|---|---|---|---|---|---|---|
| Chrome Remote Desktop (неконтролируемый доступ с PIN) | Телефон → приложение → окно Unity → Pause | 4 | 4 | Доступ к ПК по PIN | 0 € | Установить один раз (≈ 10 мин), задать PIN |
| Доступ Claude к экрану через Claude Desktop (computer use) | Агент сам делает снимок и нажатие | 3 | 3 | Нужно разрешение на каждое приложение. Нажатия может блокировать система безопасности | 0 € (в подписке) | Разрешить доступ к окну Unity |
| Быстрая помощь Windows (Quick Assist) | Нужен человек у ПК, чтобы принять код | 1 | 1 | — | 0 € | Не подходит для работы без владельца |
| Удалённый рабочий стол Windows (RDP; Windows 11 Pro есть — видно по логу) | Подключение по RDP | 3 | 2 | RDP забирает сеанс у консоли, Unity может перестать рисовать | 0 € | Не рекомендую |
| Планировщик задач + скрипт, который нажимает Ctrl+Shift+P | См. б5 | 3 | 3 | Переключает паузу вслепую | 0 € | Разрешение |

### д) Надзорный слой (кто замечает остановку)

- **Пульс.** Каждый кейс раз в ≤ 30 с пишет в `runN_state.json` поле `heartbeat` (время) и `case`.
- **Сторож** (маленький Python-скрипт рядом с прогоном или проверка самого Claude Code между шагами), каждые 60 с:
  1. `heartbeat` старше 90 с — тревога;
  2. в новом хвосте Editor.log за 60 с есть «command received», но нет «response sent» — кадры стоят;
  3. найти последнюю строку уровня ошибки перед остановкой и записать в `stall_report.json`: время, кейс, строку, размер лога, состояние окна (свёрнуто/нет), Responding/CPU процесса Unity.
- **Что делать первым:**
  - если причина — «пауза после ошибки» и есть помощник (б7), создать `unpause.request`, через 5 с проверить кадры. Не больше 2 раз;
  - если помощника нет, остановить прогон, оставить в отчёте одну строку «нужна помощь: снимите Pause» и причину;
  - если ошибки нет и Responding = False — это настоящая блокировка: ничего не нажимать, собрать данные, остановиться.
- **Облачный агент** (запланированная задача Claude) видит файлы ПК только когда Claude Desktop запущен и подключён. Поэтому надзор лучше держать локально (Claude Code или скрипт), а облако использовать для сводки. Стоимость 0 € сверх текущих подписок.
- Сторож **копирует** хвост Editor.log (последние 2 МБ) в папку отчёта при каждой тревоге. Тогда улики не пропадут, даже если лог перезапишется.

---

## 6. Расследование «Forest hang»

Что уже известно: Forest загрузилась. В Console есть ошибка NavMesh в 15:59:52 и такая же в 16:35:08, сразу после снятия паузы. Лог за 15:59–16:25 потерян.

**Безопасный повторный прогон с диагностикой (после выключения Error Pause):**
1. Подготовка: копия save.chop. Окно Unity не свёрнуто. Записать размер Editor.log и время.
2. Игра в Beach (после New Game). Открыть меню читов (C) **и дождаться**, когда кнопки получат подписи: в прогоне 2 кнопка Forest_Entrance «не найдена», потому что подписи читались до открытия меню.
3. Клик Forest. Затем 60 с раз в секунду: `Time.frameCount`, `get_all_loaded_scenes()`, позиция PigChef, время ответа SDK.
4. После этого прочитать хвост Editor.log от отметки:
   - есть ли `Loaded scene 'Assets/Scenes/Locations/Forest.unity'` и время загрузки (`Total Operation Time`);
   - сколько строк `"Stop" can only be called on an active agent` (и от каких объектов: следующая строка стека — `StopAgentSO.cs:32`);
   - идут ли пары «command received» → «response sent» без разрыва;
   - размер прироста лога за 60 с.
5. Ожидаемый результат при гипотезе 1: Forest загружается за ≤ 30 с (утверждённый порог), кадры растут, в логе N ошибок NavMesh, остановки нет. Тогда «Forest hang» закрывается как пауза по ошибке. Сами ошибки NavMesh — наблюдение о качестве игры: записать, баг не заводить.
6. Если кадры всё же встанут: снимок окна, Responding и CPU процесса Unity (не убивать), последние 200 строк лога.
   - Responding = False и CPU высокий → блокировка главного потока, это гипотеза 2. Отчёт без нажатий.
   - Responding = True и CPU ≈ 0 → пауза. Посмотреть кнопку Pause на снимке.
7. EditorTeleporter не влияет на зависание: он только вызывает обычное событие загрузки локации (`_loadLocationRequest.RaiseEvent`). Повторную загрузку той же локации он молча пропускает, в комментарии кода сказано, что иначе была бы ошибка. Размер сцены обычный (Forest.unity 4,8 МБ против Beach 5,6 МБ).

Время: ≈ 10 мин работы Code, 0 мин владельца (если Error Pause уже выключена).

---

## 7. Тексты для документации и Jira (черновики, на английском; ничего не отправлено)

**Comment for CC-70:**
> Root cause candidate (high confidence, pending one owner check): the Unity Console "Error Pause" toggle appears to be ON (its button background is lighter than Clear/Collapse in three Unity window screenshots taken 16:35, 16:37 and 18:34 on 22 Nov). Every stall in Editor.log starts right after an error-level message, and AltTester then logs "command received" without "response sent" (AltRunner.Update not running = Editor paused). The original menu freeze matches this: on 21 Nov 19:36:06, loading MainMenu logged "Problem detected while opening the Scene file: Assets/Scenes/Menus/MainMenu.unity" plus four "Missing Prefab Asset" lines, and the next SDK request was answered only 109 s later. The same pattern repeated on 22 Nov 16:36:49. Fix to try first: turn Error Pause off in the Console toolbar, then run Play → MainMenu → New Game unattended 3 times. Analysis: claude/pause-analysis-opus-2026-11-22.md.

**Comment for CC-81:**
> The freeze part is most likely an Editor artifact, not a game hang: the Input System logs the exception with Debug.LogError ("...while executing 'performed' callbacks..."), and with Console "Error Pause" on, the Editor pauses Play on that error. After unpausing, the SDK answered again until the next exception. The NullReferenceException itself remains a real defect. Its side effect is also real: the dialogue panel stayed on screen and could not be advanced. Severity should be judged on the exception and the broken dialogue state, not on the freeze. To confirm: owner checks the Error Pause button; reproduction with Error Pause off is NOT planned (Q is excluded from automated runs).

**Row for Confluence "AltTester: notes and pitfalls"** (add at the top):

| Date | Topic | Finding | What to do |
|---|---|---|---|
| 22 Nov 2026 | "Freezes" = Editor Error Pause | With Console "Error Pause" on, any error-level log (exception in an input callback, NavMesh "Stop" error on Forest load, "Problem detected while opening the Scene file" on MainMenu load) pauses Play. SDK requests then time out: Editor.log shows "command received" but no "response sent". The SDK cannot unpause, because commands run in AltRunner.Update. | Keep Error Pause off during runs. Do not minimise the Unity window. Detect stalls by received-without-sent in Editor.log and record the last error line. Never start a second Unity.exe during a run: it overwrites Editor.log. |

**New task (proposal):**
- Summary: *Make unattended runs pause-proof: preflight checks, stall detection and recovery*
- Description: (1) Preflight: Error Pause off (read LogEntries.consoleFlags via SDK if possible), runInBackground on, Unity window not minimised. (2) Liveness probe before each case and after risky steps (frameCount with a 5 s timeout). (3) Stall classifier from Editor.log (received-without-sent + last error line), written to stall_report.json with a log-tail copy. (4) Risky steps (MainMenu load, Forest teleport, dialogue advance) grouped at the end with checkpoints. (5) Optional, owner decision: git-excluded Editor helper that disables Error Pause on Play, logs pause changes and unpauses on a file request. Done when: 3 unattended runs of the fast suite finish with zero human actions, or stop with a correct one-line cause.
- Priority: High (it blocks every unattended run).

---

## 8. План на 3 шага

| Шаг | Кто | Что | Время |
|---|---|---|---|
| 1 | Владелец | Открыть Console в Unity. Посмотреть, выделена ли «Error Pause», и выключить её одним кликом. Посмотреть цвет иконки у строки «Problem detected while opening the Scene file…MainMenu» (красная/жёлтая). Снять текущую паузу (Unity сейчас стоит на паузе в Beach с 18:31). Окно Unity не сворачивать. Сообщить результат одной фразой | **2–3 мин** |
| 2 | Code | Добавить в fastlib/lib_sdk: preflight (включая пробное чтение `LogEntries.consoleFlags`), пробу «жива ли», распознавание остановки по Editor.log, пульс и копию хвоста лога. Затем контрольный прогон без владельца: Stop/Play не трогать; выход в меню → New Game → Forest через меню читов (раздел 6) → диалог Maqam (Space). Сохранения восстановить из копии | ≈ 60–90 мин |
| 3 | Я (Opus) | Разобрать результат контрольного прогона. Подтвердить или опровергнуть гипотезу 1 цифрами. Подготовить итоговые тексты для CC-70/CC-81/Confluence на утверждение владельцу. Решить, нужен ли помощник в Editor | ≈ 20–30 мин |

---

## 9. Решения владельцу

1. **Выключить Error Pause в Console и держать выключенной на время прогонов?** Рекомендую: **да**. Ошибки всё равно попадают в лог и в отчёт.
2. **Разрешить Code читать флаги Console через SDK перед прогоном (только чтение)?** Рекомендую: **да**. Менять флаг через SDK — только если вы отдельно разрешите.
3. **Добавить в проект помощник `TestRunGuard.cs` (код только для редактора, исключён из git)?** Рекомендую: **пока нет**. Вернуться к вопросу, если после шага 1 остановки останутся.
4. **Разрешить автоматическое Ctrl+Shift+P в окне Unity (не больше 2 раз, со снимком до и после)?** Рекомендую: **только как запасной вариант**, если не будет помощника.
5. **Поставить Chrome Remote Desktop (бесплатно), чтобы снимать паузу с телефона?** Рекомендую: **да**, это 10 минут один раз и страховка на все случаи.
6. **Правило: во время прогона окно Unity не сворачивать и второй Unity не запускать?** Рекомендую: **да**.

---

## 10. Что не удалось проверить и почему

- **Значение Error Pause из файлов:** его нет в файлах проекта (проверены UserSettings, Layouts, ProjectSettings). Предположительно оно в реестре (EditorPrefs), а реестр читать нельзя. Значение определено только по снимкам окна (включено, высокая уверенность).
- **Editor.log за 10:42–16:33 22.11 потерян:** его перезаписал посторонний запуск Unity.exe в 16:31:58. Поэтому случаи INV-10 (15:21) и Forest (≈15:59) восстановлены по отчёту, файлу INV-10_exception_editor_log.txt и снимкам Console, а не по полному логу.
- **Уровень сообщения «Problem detected while opening the Scene file»** (Error или Warning) по тексту лога не определить. Нужен взгляд на иконку в Console.
- **Поведение AltTester с внутренним классом `UnityEditor.LogEntries`** (найдёт ли `get_static_property`/`call_static_method`) не проверено: нужен 1 пробный вызов при работающей игре.
- **Влияние свёрнутого окна на Play Mode** в 6000.3 в документации не описано. Отделить его от паузы по имеющимся данным нельзя.
- **Файлы `pause_diag_CC70.*`** в рабочей копии worktree не читал. Их итог есть в комментариях CC-70, этого хватило.
- **Confluence «Setup: Python SDK environment» (327732)** не читал: для этой задачи не понадобилось.
- **Ничего не запускалось и не менялось:** Unity, настройки, проект, Jira и Confluence не тронуты.

Источники: [Console window reference 6000.3](https://docs.unity.com/en-us/engine/6000.3/manual/unity-editor/editor-windows-views-reference/console-window/console.md) · [Preferences → General 6000.3](https://docs.unity.com/en-us/engine/6000.3/manual/unity-editor/editor-settings-reference/preferences/general) · [EditorApplication.isPaused](https://docs.unity.com/en-us/engine/6000.6/script-reference/unityeditor/editorapplication/ispaused) · [EditorApplication.pauseStateChanged](https://docs.unity3d.com/ScriptReference/EditorApplication-pauseStateChanged.html) · [Application.runInBackground](https://docs.unity.com/en-us/engine/6000.6/script-reference/unityengine/application/runinbackground) · [EditorPrefs](https://docs.unity3d.com/ScriptReference/EditorPrefs.html) · [UnityCsReference ConsoleWindow.cs](https://raw.githubusercontent.com/Unity-Technologies/UnityCsReference/master/Editor/Mono/ConsoleWindow.cs) · [Форум: Test Runner меняет Error Pause](https://discussions.unity.com/t/running-tests-sets-run-in-background-and-error-pause-but-does-not-revert/762580) · [AltTester Known Issues](https://alttester.com/docs/sdk/pages/known-issues.html)
