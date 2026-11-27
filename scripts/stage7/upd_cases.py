# -*- coding: utf-8 -*-
import json, shutil, os
B = r"C:\Users\Aotat\Desktop\Test_Ai\Reports_2026-11-21\results\opus_review_20261124"
F = B + r"\cases_state.json"
BEFORE = B + r"\cases_state.before_stage7.json"
if not os.path.exists(BEFORE):
    shutil.copy2(F, BEFORE)
raw = open(F, "rb").read(); bom = raw.startswith(b"\xef\xbb\xbf"); crlf = b"\r\n" in raw
data = json.loads(raw.decode("utf-8-sig"))
SRC = "Reports_2026-11-21/results/modules_stage7_20261126/report.md"
def put(cid, verdict, module, level, clean, method, dep, notes, until, jira=None):
    rec = {"id": cid, "verdict": verdict, "date": "2026-11-27", "run": "modules_stage7", "source": SRC, "method": method, "needs_clean_play": clean,
           "depends_on": dep, "do_not_repeat_until": until, "jira": jira, "notes": notes, "module": module, "level": level}
    old = [x for x in data["cases"] if x["id"] == cid]
    if old:
        if old[0].get("notes"): rec["notes"] += " | ранее (%s, %s): %s" % (old[0].get("verdict"), old[0].get("date"), old[0]["notes"])
        rec["jira"] = jira or old[0].get("jira"); old[0].update(rec)
    else: data["cases"].append(rec)
    print(cid, verdict, "updated" if old else "added")
put("PERF-LEAK-01", "PASS", "M01", "L2", False, "меню читов, 10 циклов Beach<->Field_Hill; счёт объектов", [], "Редактор. Число AudioListener/Camera/EventSystem(по имени)/InventoryManager/UIManager/Protagonist постоянно 10 из 10. Total allocated 1695->1782 МБ (монотонно), Mono 840->829 МБ; по памяти вердикта нет. Исключений 0.", "изменения загрузки сцен")
put("PERF-LEAK-02", "PASS", "M02", "L2", False, "5 циклов пауза -> Back to menu -> New Game; счёт объектов", [], "Редактор. Число объектов не растёт 5 из 5. Total allocated 1782->1853 МБ (монотонно), Mono 845->827 МБ; по памяти вердикта нет. Исключений 0.", "изменения меню/загрузки")
put("UI-TXT-en", "FAIL", "M17", "L1", True, "все активные TMP: isTextOverflowing/Truncated/No translation; 6 экранов", [], "Редактор 980x379. 1 переполненный по флагу (инвентарь, ItemName 'Phoenix Chick'), на скриншоте видимого дефекта нет. Обрезанных 0, отсутствующих переводов 0.", "изменения UI или таблиц локализации")
put("UI-TXT-fr", "FAIL", "M17", "L1", True, "как UI-TXT-en", [], "4 отсутствующих ключа (Volume_Master, ShadowDistance_Optimal, Phoenix name/description); 3 переполнения, в Graphics видно наложение на соседнюю строку. Обрезанных 0.", "изменения UI или таблиц локализации")
put("UI-TXT-it", "FAIL", "M17", "L1", True, "как UI-TXT-en", [], "25 отсутствующих ключей (23 UI Misc + Phoenix name/description); переполнения на 5 из 6 экранов, все на заглушках. Обрезанных 0.", "изменения UI или таблиц локализации")
put("CC94-SAVE", "PASS", "M04", "L2", False, "New Game, Town_Upper, T1 в ToForestEntrance_FallDown, 30 с; сравнение save.chop", ["M08-02"], "1 из 1. Зависание воспроизведено (NRE SceneLoader.cs:171, _isLoading True, игрока нет). save.chop читается, тот же хэш и размер (643), _locationId = Town_Upper, инвентарь и шаги (пусто) не изменились; файл при переходе перезаписан (mtime). Continue из этого сейва не проверялся.", "исправление CC-94 или SaveSystem")
s = json.dumps(data, ensure_ascii=False, indent=1)
if crlf: s = s.replace("\n", "\r\n")
open(F, "wb").write((b"\xef\xbb\xbf" if bom else b"") + s.encode("utf-8"))
chk = json.loads(open(F, "rb").read().decode("utf-8-sig"))
ids = [c["id"] for c in chk["cases"]]; print("JSON ok, cases", len(ids), "dup", len(ids) - len(set(ids)))
