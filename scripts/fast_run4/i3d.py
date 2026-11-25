import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("int03d")
OFF = log_mark(); H_before = json.load(open("int03_h0.json"))["h0"]
def line():
    try:
        o = d.find_object(By.NAME, "DialogueLine", enabled=True); return o.get_component_property("TMPro.TextMeshProUGUI","text","Unity.TextMeshPro")
    except Exception: return None
def press(method):
    if method == "Space": key("Space", 0.05)
    elif method == "Space0.1": key("Space", 0.1)
    elif method == "Enter": key("Return", 0.1)
    elif method == "E": key("E", 0.1)
    elif method == "click": d.find_object(By.NAME, "Dialogue_Panel", enabled=False).click()
guard.risky("INT-03 листание")
print("start line:", line(), "dlg", dlg())
T0 = time.time(); log = []; N = 0; used = None; closed = False; per_method = {}
for method in ("Space", "Space0.1", "Enter", "E", "click"):
    if closed: break
    cnt = 0; changed = False
    while cnt < 40 and time.time() - T0 < 60:
        if not dlg(): closed = True; break
        if choices(): log.append("выбор Yes/No появился"); break
        before = line(); press(method); cnt += 1; time.sleep(0.3)
        after = line()
        log.append((method, cnt, before, after, dlg()))
        if after != before or not dlg(): changed = True
        if not changed and cnt >= 5: break
    per_method[method] = {"presses": cnt, "changed": changed}
    if changed: used = method; N = cnt
    if closed or not dlg(): closed = not dlg(); break
    if time.time() - T0 >= 60: break
print("closed", closed, "used", used, "N", N, "per_method", per_method, "elapsed", round(time.time()-T0,1))
for l in log: print(l)
print(shot("int03_after"))
json.dump({"used": used, "N": N, "closed": closed, "per_method": per_method, "log": log}, open("int03_res.json","w"), ensure_ascii=False, default=str)
