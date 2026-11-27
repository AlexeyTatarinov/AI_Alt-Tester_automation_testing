# -*- coding: utf-8 -*-
import json, os
R = r"C:\Users\Aotat\Desktop\Test_Ai\Reports_2026-11-21\results\modules_stage7_20261126"
for f in ("perf", "mesh", "soak", "ui_text", "cc94_save"):
    json.load(open(os.path.join(R, f + ".json"), encoding="utf-8")); print(f, "ok")

HEAD = """**Итог: все блоки выполнены; геометрия Town_Market прочитана не полностью (573 из 723).** Утечек объектов нет; сохранение после зависания CC-94 цело; тексты UI — FAIL на всех трёх языках (en только по флагу переполнения).

| ID | Вердикт | Образцы |
|---|---|---|
| PERF-LEAK-01 (переходы) | PASS | 10 из 10 циклов |
| PERF-LEAK-02 (меню) | PASS | 5 из 5 циклов |
| UI-TXT-en | FAIL (по флагу) | 1 переполнение |
| UI-TXT-fr | FAIL | 4 ключа, 3 переполнения |
| UI-TXT-it | FAIL | 25 ключей |
| CC94-SAVE | PASS | 1 из 1 |
| производительность, геометрия | без вердикта | обзор |"""

TAIL = r"""
## 5. Play B (последним): сохранение после зависания CC-94 (`cc94_save.json`, `save_before.chop`, `save_after.chop`)

New Game → Town_Upper → T1 в (−34,2; 24,04; 14,3) → 30 с. Зависание воспроизведено (1 из 1): 1 `NullReferenceException`, `SceneLoader.LoadNewScene`, `SceneLoader.cs:171`; загружены только PersistentManagers и Gameplay, `_isLoading` True, PigChef нет, состояние Gameplay.

| | до | после (30 с) |
|---|---|---|
| хэш (sha256, 16 знаков) | 4a79e77c59ccffc4 | 4a79e77c59ccffc4 |
| размер, байт | 643 | 643 |
| JSON читается | да | да |
| `_locationId` | 0d5b48391ae82cb4aaeea96320eecaad (`Locations/Town_Upper.asset`) | то же |
| инвентарь | PhoenixChick 1, Seed 20, SlimeCritterEgg 20, GoldenEgg 20, RockCritterEgg 20, SpecialSpoon 1 | то же |
| шаги квеста | пусто | пусто |
| время изменения файла | 00:09:24 | 00:09:32 (момент телепорта) |

- **CC94-SAVE: PASS** — файл читается, `_locationId` указывает на существующую локацию (по ассету в проекте).
- Файл при срабатывании триггера **перезаписан** тем же содержимым; `.bak` после этого равен ему.
- `Continue` из этого сохранения не проверялся.

## 6. Конец

| № | Команда | Код |
|---|---|---|
| 1 | `--restore-save` перед Play A (`restart1.out`) | 0 |
| 2 | `--restore-save` перед Play B (`restart2.out`) | 0 |
| 3 | `--restore-save` финальный (`restart3.out`) | 0 |

- Финал (`final_check.out`): MainMenu и PersistentManagers, `autoSyncTransforms` = False, save.chop равен копии, локаль `en`.
- `cases_state.json`: добавлены PERF-LEAK-01, PERF-LEAK-02, UI-TXT-en, UI-TXT-fr, UI-TXT-it, CC94-SAVE. JSON читается. Копия «до»: `cases_state.before_stage7.json`.
- Прогон занял около 50 минут.

## Баг-кандидаты (в Jira не заведены; с существующими тикетами не сверял)

1. **Итальянский:** 23 отсутствующих ключа UI Misc — главное меню, Settings и пауза состоят из «No translation found».
2. **Французский:** нет `Volume_Master`, `ShadowDistance_Optimal`; длинная заглушка наезжает на соседние строки.
3. **fr и it:** у предмета Phoenix нет названия и описания.

Наблюдения, не баги: монотонный рост total allocated (редактор); в четырёх осмотренных сценах нет ни одного LODGroup.

## Ошибки скриптов и отклонения (не игры)

- **Затронуты файлы этапа 6.** Библиотека `s3blib.py` переназначает папку результатов на `modules_stage6_20261126`; я заметил это только после блока 2. Перезаписаны два служебных скриншота preflight (`preflight_a1_after.png`, `preflight_a2.png`), изменены `run_state.json` и `window_restores.txt` (добавлены 2 строки). Отчёт и данные этапа 6 (`a*.json`, `b*.json`, скриншоты результатов) не менялись. `perf.json` и `mesh.json` перенесены в папку этапа 7, пути исправлены в `g7.py`.
- Геометрия: первый запуск потерян по лимиту фоновой команды, поэтому блок вышел за свои 20 минут, а Town_Market прочитан не весь.
- Утечки: блок перезапущен из-за счёта `EventSystem`.

## Оговорки к правилам

- Массовое чтение шло ниже 20 вызовов в секунду (около 18 и меньше); Editor.log рос около 1 МБ/мин. Короткие циклы ожидания опрашивали игру чаще 1 раза в секунду (шаг 0,5 с по заданию и в старых библиотечных функциях).
- `Editor.log` сейчас больше 1,2 ГБ (накоплен за прошлые прогоны).
- Python для игровых скриптов запускался без `-I` (нужны свои библиотеки рядом).
- Окно Unity при preflight восстанавливалось без захвата фокуса; мышь и computer use не использовались. Игру и проект не менял; Jira, Confluence и Git не трогал. Скрипты: `scripts\stage7\`.
"""
P = os.path.join(R, "report.md")
s = open(P, encoding="utf-8").read()
assert "(отчёт пишется по ходу)" in s
s = s.replace("(отчёт пишется по ходу)", HEAD).rstrip() + "\n" + TAIL
open(P, "w", encoding="utf-8").write(s)
print("report ok")
