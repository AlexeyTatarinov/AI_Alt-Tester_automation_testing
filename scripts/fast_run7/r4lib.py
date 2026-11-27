# -*- coding: utf-8 -*-
import os, sys, json, shutil, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inv_lib import *
BK = r"Test_Ai\Reports_2026-11-21\evidence\save_backup\20261122_122526"
MAP = {"Unity_Technologies": SAVE_DIRS[0], "Unity_Open_Projects": SAVE_DIRS[1]}
def bk_hashes():
    return {os.path.join(dst, f): sha(os.path.join(BK, sub, f)) for sub, dst in MAP.items() for f in ("save.chop", "save.chop.bak")}
def restore():
    for sub, dst in MAP.items():
        for f in ("save.chop", "save.chop.bak"):
            s = os.path.join(BK, sub, f)
            if os.path.exists(s): shutil.copy2(s, os.path.join(dst, f))
    return save_hashes() == bk_hashes()
def pause_open(): return any(True for _ in d.find_objects(By.NAME, "Pause_Screen", enabled=True))
def dlg(): return comp_active("UIDialogueManager")
def choices(): return comp_active("UIDialogueChoicesManager")
def to_menu():
    if not pause_open(): key("Escape", 0.1); time.sleep(1.5)
    d.find_object(By.NAME, "BackToMenuButton", enabled=False).click(); time.sleep(1.5)
    d.find_object(By.NAME, "PopupButton - 1", enabled=False).click()
    t0 = time.time()
    while time.time() - t0 < 40:
        try:
            if "MainMenu" in scenes(): return round(time.time() - t0, 1)
        except Exception: pass
        time.sleep(0.5)
    return None
def new_game():
    t0 = time.time(); d.find_object(By.NAME, "Button New Game", enabled=False).click()
    for _ in range(15):
        time.sleep(0.4)
        try: d.find_object(By.NAME, "PopupButton - 1", enabled=False).click(); break
        except Exception: pass
    found = None
    while time.time() - t0 < 60:
        try:
            if "Beach" in scenes() and pig(): found = round(time.time() - t0, 1); break
        except Exception: pass
        time.sleep(0.3)
    time.sleep(2.0)
    return found
def preflight(label):
    pre = guard.preflight(label)
    print("preflight", label, {k: pre[k] for k in ("consoleFlags", "error_pause", "play", "alive")}, "iconic", pre["window"].get("iconic"), flush=True)
    if pre["error_pause"] or not pre["alive"] or not pre["play"][0]:
        raise SystemExit("СТОП: " + json.dumps({k: pre[k] for k in ("error_pause", "play", "alive")}) + "")
    return pre
def dlg_texts():
    out = []
    for comp, asm in (("TMPro.TextMeshProUGUI", "Unity.TextMeshPro"),):
        for o in d.find_objects(By.COMPONENT, comp, enabled=True):
            try:
                t = o.get_component_property(comp, "text", asm)
                if t and t.strip(): out.append((o.name, t.strip()[:120]))
            except Exception: pass
    return out
def hint(): return comp_active("UIInteraction")
def tp_hare(dist=1.3):
    teleport("T1", HARE[0] - dist, HARE[1] + 0.3, HARE[2]); time.sleep(2.0)

SAVE0F = os.path.join(SAVE_DIRS[0], "save.chop")
def save_info():
    try:
        j = json.load(open(SAVE0F, encoding="utf-8"))
        return {"hash": sha(SAVE0F), "finished": list(j.get("_finishedQuestlineItemsGUIds", [])), "stacks": {s["itemGuid"][:6]: s["amount"] for s in j.get("_itemStacks", [])}}
    except Exception as e:
        return {"hash": sha(SAVE0F), "err": str(e)[:80]}
def line():
    try:
        o = d.find_object(By.NAME, "DialogueLine", enabled=True); return o.get_component_property("TMPro.TextMeshProUGUI", "text", "Unity.TextMeshPro")
    except Exception: return None
def press(method):
    if method == "Space": key("Space", 0.05)
    elif method == "Space0.1": key("Space", 0.1)
    elif method == "Enter": key("Return", 0.1)
    elif method == "E": key("E", 0.1)
    elif method == "click": d.find_object(By.NAME, "Dialogue_Panel", enabled=False).click()
def talk(max_total=60):
    """листание диалога тем же способом, что в INT-03: Space(тап 0,05 с, до 40) -> Space(удержание 0,1 с) -> Enter -> E -> клик; пауза 0,3 с"""
    T0 = time.time(); log = []; used = None; closed = False; per = {}
    for method in ("Space", "Space0.1", "Enter", "E", "click"):
        if closed: break
        cnt = 0; changed = False
        while cnt < 40 and time.time() - T0 < max_total:
            if not dlg(): closed = True; break
            if choices(): log.append("выбор Yes/No появился"); break
            before = line(); press(method); cnt += 1; time.sleep(0.3)
            after = line(); log.append((method, cnt, before, after, dlg(), round(time.time() - T0, 1)))
            if after != before or not dlg(): changed = True
            if not changed and cnt >= 5: break
        per[method] = {"presses": cnt, "changed": changed}
        if changed: used = method
        if not dlg(): closed = True
        if closed or time.time() - T0 >= max_total + 1000: break
    return {"closed": closed, "used": used, "per_method": per, "elapsed": round(time.time() - T0, 1), "log": log}
def lines_seq(log):
    seq = []
    for l in log:
        if isinstance(l, (list, tuple)):
            for v in (l[2], l[3]):
                if v and (not seq or seq[-1] != v): seq.append(v)
    return seq
def exc_summary(off):
    f = open(EDLOG, "rb"); f.seek(off); t = f.read().decode("utf-8", "replace").splitlines(); f.close()
    t = [l for l in t if "AltTester|" not in l]
    import collections
    c = collections.Counter(); wrap = 0
    for l in t:
        m = re.match(r"^\s*([A-Za-z0-9_.]*Exception)\b(?!.* while executing)", l)
        if m and "while executing" not in l: c[m.group(1)] += 1
    first = {}
    for i, l in enumerate(t):
        m = re.match(r"^\s*([A-Za-z0-9_.]*Exception)\b", l)
        if m and "while executing" not in l and m.group(1) not in first:
            first[m.group(1)] = [x[:200] for x in t[i:i + 7]]
    return {"by_type": dict(c), "total": sum(c.values()), "first_stacks": first}
def inv_snapshot():
    """открыть инвентарь, обойти вкладки, закрыть; вернуть {tab: [(имя, кол-во, тип)]}"""
    if not inv(): key("Tab", 0.1); time.sleep(1.2)
    t = all_tabs(); key("Tab", 0.1); time.sleep(1.0)
    return t
