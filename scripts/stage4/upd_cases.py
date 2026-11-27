# -*- coding: utf-8 -*-
import json
F = r"Test_Ai\Reports_2026-11-21\results\opus_review_20261124\cases_state.json"
raw = open(F, "rb").read(); bom = raw.startswith(b"\xef\xbb\xbf"); crlf = b"\r\n" in raw
data = json.loads(raw.decode("utf-8-sig"))
c = [x for x in data["cases"] if x["id"] == "M03-02"]; assert len(c) == 1; c = c[0]
c.update(verdict="FAIL", date="2026-11-26", run="modules_stage4", source="Reports_2026-11-21/results/modules_stage4_20261126/report.md")
c["notes"] += " | stage4, сценарий B честно (смена локации пешком через LocationExit при тревоге): FAIL, 1 из 1. Чистый Play, Count 0 после New Game. Mountain_Cave, T1 в 3 м перед триггером, тревога (Count 1, Combat), вход пешком в Mountain_Path: через 5 и 15 с Count 1, Combat, врагов в сцене 0, Tab не открывает инвентарь, HP 50->50, исключений 0. В _alertEnemies ссылка на уничтоженный Transform. W и Esc работают. Какой именно Klipper дал тревогу, не установлено."
s = json.dumps(data, ensure_ascii=False, indent=1)
if crlf: s = s.replace("\n", "\r\n")
open(F, "wb").write((b"\xef\xbb\xbf" if bom else b"") + s.encode("utf-8"))
json.loads(open(F, "rb").read().decode("utf-8-sig")); print("ok", bom, crlf, len(raw), len(s.encode("utf-8")))
