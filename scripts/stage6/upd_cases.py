# -*- coding: utf-8 -*-
import json
B = r"C:\Users\Aotat\Desktop\Test_Ai\Reports_2026-11-21\results\opus_review_20261124"
F = B + r"\cases_state.json"
raw = open(F, "rb").read(); bom = raw.startswith(b"\xef\xbb\xbf"); crlf = b"\r\n" in raw
data = json.loads(raw.decode("utf-8-sig"))
SRC = "Reports_2026-11-21/results/modules_stage6_20261126/report.md"
def put(cid, verdict, module, level, clean, method, dep, notes, until, jira=None):
    rec = {"id": cid, "verdict": verdict, "date": "2026-11-26", "run": "modules_stage6", "source": SRC, "method": method, "needs_clean_play": clean,
           "depends_on": dep, "do_not_repeat_until": until, "jira": jira, "notes": notes, "module": module, "level": level}
    old = [x for x in data["cases"] if x["id"] == cid]
    if old:
        if old[0].get("notes"): rec["notes"] += " | ранее (%s, %s): %s" % (old[0].get("verdict"), old[0].get("date"), old[0]["notes"])
        rec["jira"] = jira or old[0].get("jira"); old[0].update(rec)
    else: data["cases"].append(rec)
    print(cid, verdict, "updated" if old else "added")
put("M16-02", "PASS", "M16", "L2", True, "M-PD1; E2E-01 + Ayud S1-Q1-QL2", ["IT-01"], "1 из 1. SlimeCutscene Playing, time 1.8/6.8/11.7/21.7 с на 0/5/10/20 с; после конца Gameplay, Tab открывается, W 0.32 м, исключений 0. Во время катсцены GameState читался как Dialogue, не Cutscene (4 из 4 чтений). Конец катсцены при врагах в тревоге не проверен (Count 0).", "изменения CutsceneManager или S1-Q1-QL2")
put("M10-01g", "PASS", "M10", "L2", True, "M-TP1", ["M16-02"], "Gluecose_FarmAttack после катсцены активны (3), Cut* неактивны. Тревога 1.8 с, Combat, урон герою 50->35, смерть врага и SlimeCritterEgg (1 из 2 попыток: в 1-й за 8 F удар не засчитан, герой погибал). Здоровье врага 0/0 (InitialHealth 0).", "изменения Gluecose или боя")
put("CMB-05", "PASS", "M10", "L1", True, "M-TP1 + ходьба; y во время движения", ["M10-01g"], "#426: вплотную до 0.30 м, максимум y +0.05 м (порог 0.3), 14 замеров ближе 1 м; второй враг: 0.85 м, +0.04 м. Один заход с полным HP.", "изменения коллайдеров Gluecose/PigChef", "CC-27")
put("DTH-04n", "FAIL", "M09", "L1", False, "M-TP1, как DTH-04", ["DTH-04"], "NRE FallCatcher.cs:14 в 10 из 10 циклов смерти (FallCatcher_Lake + 3 F), по 1 на цикл; возрождение 10 из 10. Удары Klipper: NRE 0 из 10 (из них 2 смертельных).", "исправление FallCatcher", "CC-84")
put("M08-01d", "PASS", "M08", "L1", False, "T1 на 3 м выше триггера, гравитация", [], "9 из 9 выходов: переход на ожидаемую сцену и вход того же пути (<=0.01 м), CC-67 нет, HP 50, исключений 0. Дойти пешком не проверялось. JumpDown: после загрузки Beach снова играет интро, PigChef скрыт ~16 с (квестовых шагов 0).", "изменения этих выходов")
put("M08-02", "FAIL", "M08", "L1", False, "T1 (x, y+3, z), гравитация", [], "1 из 1. ToForestEntrance_FallDown: NRE SceneLoader.cs:171; на 5/15/30 с и позже: только PersistentManagers+Gameplay, _isLoading True, игрока нет, состояние Gameplay; меню читов открывается, но локацию не грузит. Нужен перезапуск Play.", "исправление ссылки _locationToLoad / SceneLoader")
s = json.dumps(data, ensure_ascii=False, indent=1)
if crlf: s = s.replace("\n", "\r\n")
open(F, "wb").write((b"\xef\xbb\xbf" if bom else b"") + s.encode("utf-8"))
chk = json.loads(open(F, "rb").read().decode("utf-8-sig"))
ids = [c["id"] for c in chk["cases"]]; print("JSON ok, cases", len(ids), "dup", len(ids) - len(set(ids)))
