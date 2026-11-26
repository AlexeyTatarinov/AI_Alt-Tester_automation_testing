# -*- coding: utf-8 -*-
import json
F = r"C:\Users\Aotat\Desktop\Test_Ai\Reports_2026-11-21\results\opus_review_20261124\cases_state.json"
raw = open(F, "rb").read(); bom = raw.startswith(b"\xef\xbb\xbf"); crlf = b"\r\n" in raw
data = json.loads(raw.decode("utf-8-sig"))
cases = data["cases"]
SRC = "Reports_2026-11-21/results/modules_stage3b_20261126/report.md"
def get(i):
    c = [x for x in cases if x["id"] == i]; assert len(c) == 1, (i, len(c)); return c[0]
def put(i, verdict, note, append=False):
    c = get(i)
    if verdict: c["verdict"] = verdict
    c["date"] = "2026-11-26"; c["run"] = "modules_stage3b_retry"; c["source"] = SRC
    c["notes"] = (c.get("notes", "") + " | " + note) if append else note
put("E2E-01b", "PASS", "Ayud (Field_Farms, не Town_Market): S1-Q1-QL2 13 реплик, save_finished 5->6; S2-Q1-QL2 (CheckItem SpecialSpoon) Yes, 4 реплики, 6->8, Quest Q1-QL2 IsDone; исключений 0; инвентарь не менялся. Следующий шаг S1-Q2-QL2, Dialogue, Terra, без предмета (не выполнялся). До этого E2E-01: Seed 20->19->16, Dish +1, RockCandy_Recipe +1, questline 0->1, исключений 0.")
put("IT-05", "PASS", "PlantCritter убит (1 удар F), враг исчез, CollectableItem Seed; подбор E: Seed 16->17; Count 1->0, Combat->Gameplay; исключений 0.")
put("E2E-02", "FAIL", "IT-05 PASS; после Continue инвентарь равен save.chop, локация Mountain_Cave, Count 0, Gameplay, Tab открывается; разговор с BardHare после Continue: 2 реплики, панель закрылась, но состояние осталось Dialogue (>150 с и после смены локации), Tab и разговор с Ayud не работают, движение и Esc работают, ошибок в логе 0. Тот же разговор до Continue закрылся. 1 из 1.")
put("M03-02", None, "stage3b_retry (M03-02b): в начале Play Count=0. Выход пешком на Beach НЕ уходя из зоны выполнить нельзя: PlantCritter (4) не двигается, тревога снимается примерно на 7,4 м, до выхода не меньше 19 м (XZ). При выходе из зоны Count 1->0, Combat->Gameplay. Пеший переход на Beach после этого: Count 0, Gameplay, Tab открывается, разговор с BardHare закрылся. Залипания Combat не было.", append=True)
put("IT-11", "PASS", "Урон от Klipper (Mountain_Cave, <=2 с): 50->35. Инвентарь, SweetCream_Dish, кнопка Eat: здоровье 35->50 (+15, потолок max), блюдо 1->0, исключений 0.")
put("IT-02c", None, "Образец 2 (IT-02c3, stage3b_retry): НЕ засчитан: после Continue _currentStep пуст, следующий шаг у Terra, а не у Ayud/BardHare. Разговор с BardHare (без шага): инвентарь/квест не менялись, исключений 0, но состояние залипло в Dialogue (см. E2E-02). Итог CC-90 через Continue по засчитанным образцам: 1 из 1.", append=True)
s = json.dumps(data, ensure_ascii=False, indent=1)
if crlf: s = s.replace("\n", "\r\n")
open(F, "wb").write((b"\xef\xbb\xbf" if bom else b"") + s.encode("utf-8"))
print("ok", bom, crlf, len(raw), len(s.encode("utf-8")))
