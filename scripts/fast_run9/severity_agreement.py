# -*- coding: utf-8 -*-
"""Считает согласие серьёзности и приоритета: человек против ИИ (CC-31). Запуск: python severity_agreement.py answers.json
Оценки ИИ читаются только ПОСЛЕ получения ответов человека; хеш проверяется, чтобы убедиться, что их не меняли."""
import json, sys, hashlib, os
D = r"C:\Users\Aotat\Desktop\Test_Ai\Reports_2026-11-21\severity_blind_20261124"
raw = open(os.path.join(D, "AI_SEALED_ratings.json"), encoding="utf-8").read()
assert hashlib.sha256(raw.encode()).hexdigest() == open(os.path.join(D, "AI_SEALED_ratings.sha256")).read().strip(), "оценки ИИ изменены после запечатывания"
ai = {i["id"]: i for i in json.loads(raw)["items"]}
hu = {i["id"]: i for i in json.load(open(sys.argv[1], encoding="utf-8"))["items"] if i["severity"] and i["priority"]}
n = len(hu); sev_eq = sev_1 = pri_eq = pri_1 = 0
for k, h in hu.items():
    a = ai[k]; ds = abs(int(h["severity"][1]) - int(a["severity"][1])); dp = abs(int(h["priority"][1]) - int(a["priority"][1]))
    sev_eq += ds == 0; sev_1 += ds <= 1; pri_eq += dp == 0; pri_1 += dp <= 1
    print(k, a["jira"], "человек", h["severity"], h["priority"], "| ИИ", a["severity"], a["priority"], "| разница S", ds, "P", dp)
print("оценено", n, "из", len(ai))
print("Severity: точное совпадение %d/%d = %.0f%%; в пределах ±1: %d/%d = %.0f%%" % (sev_eq, n, 100 * sev_eq / n, sev_1, n, 100 * sev_1 / n))
print("Priority: точное совпадение %d/%d = %.0f%%; в пределах ±1: %d/%d = %.0f%%" % (pri_eq, n, 100 * pri_eq / n, pri_1, n, 100 * pri_1 / n))
