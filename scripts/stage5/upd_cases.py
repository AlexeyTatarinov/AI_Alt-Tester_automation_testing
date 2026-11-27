# -*- coding: utf-8 -*-
import json, shutil
B = r"Test_Ai\Reports_2026-11-21\results\opus_review_20261124"
F = B + r"\cases_state.json"
shutil.copy2(F, B + r"\cases_state.before_stage5.json")
raw = open(F, "rb").read(); bom = raw.startswith(b"\xef\xbb\xbf"); crlf = b"\r\n" in raw
data = json.loads(raw.decode("utf-8-sig"))
SRC = "Reports_2026-11-21/results/modules_stage5_20261126/report.md"
def put(cid, verdict, module, level, clean, method, dep, notes, until, jira=None):
    rec = {"id": cid, "verdict": verdict, "date": "2026-11-26", "run": "modules_stage5", "source": SRC, "method": method, "needs_clean_play": clean,
           "depends_on": dep, "do_not_repeat_until": until, "jira": jira, "notes": notes, "module": module, "level": level}
    old = [x for x in data["cases"] if x["id"] == cid]
    if old:
        if old[0].get("notes"): rec["notes"] += " | ранее (%s, %s): %s" % (old[0].get("verdict"), old[0].get("date"), old[0]["notes"])
        rec["jira"] = jira or old[0].get("jira"); old[0].update(rec)
    else: data["cases"].append(rec)
    print(cid, verdict, "updated" if old else "added")
put("M16-01b", "PASS", "M16", "L1", True, "M-PD1: PlayableDirector state/time at 0,2,5,10 s after Beach", [], "1 из 1. BeachIntroCutscene state Playing, time 1.69/4.67/9.69 на 2/5/10 с (в 0 с директоры не найдены). GameState всё время Gameplay, _activePlayableDirector None. Расходится с M16-01 (stage1b): тот оракул не видел запуск мимо CutsceneManager.", "изменения CutsceneTrigger или сцены Beach")
put("IT-01", "PASS", "M02", "L2", True, "M-PD1,M-EXC", ["M16-01b"], "1 из 1. save.chop: GUID квестов 5->0; PersistentManagers+Gameplay+Beach; PigChef у DefaultSpawnLocation (разница y 0.08 м); предупреждение CC-67 есть (1); quest 0/0; исключений 0.", "изменения цепочки New Game", "CC-67")
put("REG-90-a", "FAIL", "M12", "L2", True, "M-TP1,M-DLG2; 3x Back to menu->New Game", [], "1 из 1, базовый замер до исправления CC-90. Разговор 1 с BardHare после 3 выходов: Seed 20->8 (-12), 19 реплик, диалог не закрылся за 60 Space, шаг 0->1, исключений 0. Разговор 2 не выполнялся (правило 2a), награда не измерена.", "исправление CC-90", "CC-90")
put("M19-01", "OBSERVATION", "M19", "L1", False, "позиции NPCMovement 7 раз за 30 с", [], "Town_Market: 0 из 18 сдвинулись; npcState Idle у всех; NavMeshAgent.isOnNavMesh False у всех. По коду в Walk переводят только финальные катсцены; стоит ли это по замыслу, решает владелец.", "ответ владельца или изменения NPC")
put("M19-02", "NOT_APPLICABLE", "M19", "L1", False, "M-TP1,M-DLG2", ["M19-01"], "Townsfolk_F (4): разговор есть (1 реплика, закрылся, 0 исключений), но житель не шёл ни до, ни после, поэтому остановку и продолжение пути проверить не на чем.", "жители начнут ходить")
put("M08-01c", "PASS", "M08", "L1", False, "M-TP1; пол по Physics.Raycast", [], "2 из 2 выходов, по 1 образцу. Slope: коллайдер y 19.72..27.78, пол 21.81, T1 -> Town_Inner. ToForest: y 7.70..15.82, пол 10.21, T1 -> Forest. Прежние BLOCKED - ошибка метода. Пешком не проверено. Отклонение: сброс из y=29 задел ToInnerTown_FallDown (1).", "изменения этих выходов", "CC-67")
put("IT-08", "PASS", "M03", "L2", False, "M-TP1", [], "а) Esc через 0.27 с после входа в LocationExit Beach->Field_Hill: загрузка прошла, timeScale 1, паузы нет, Gameplay. б) Esc в инвентаре готовки: инвентарь закрылся, паузы нет, timeScale 1, Gameplay. По 1 образцу. Диалог не проверялся.", "изменения UIManager/SceneLoader")
put("IT-06", "PASS", "M09", "L2", False, "M-TP1; камера по M07-01", [], "1 из 1. Klipper, Mountain_Cave: HP 50->0 за 8.7 с, новый PigChef через 5.8 с после смерти, HP 50, 5 полных сердец, камера 9.85 м на +2 и +5 с, Gameplay, Count 0, Tab открывается, исключений 0.", "изменения смерти/респавна")
s = json.dumps(data, ensure_ascii=False, indent=1)
if crlf: s = s.replace("\n", "\r\n")
open(F, "wb").write((b"\xef\xbb\xbf" if bom else b"") + s.encode("utf-8"))
chk = json.loads(open(F, "rb").read().decode("utf-8-sig"))
ids = [c["id"] for c in chk["cases"]]; print("JSON ok, cases", len(ids), "dup", len(ids) - len(set(ids)))
