# P04: Ayud S1-Q1-QL2 -> катсцена -> Gluecose
from g6 import *
R = {"samples": [], "poll": []}
off = json.load(open(os.path.join(R2, "a1.json"), encoding="utf-8"))["off"]; R["off"] = off
def dump(): jdump(os.path.join(R2, "a2.json"), R)
def directors():
    out = []
    for o in d.find_objects(By.COMPONENT, PD, enabled=False):
        e = {"name": o.name, "id": o.id, "go_active": go_active(o)}
        for p in ("state", "time", "duration", "playableAsset.name"):
            try: e[p] = o.get_component_property(PD, p, DM, max_depth=1)
            except Exception as ex: e[p] = "ERR " + type(ex).__name__
        out.append(e)
    return out
def glue():
    out = []
    for n in ("Gluecose_FarmAttack", "CutGluecose_FarmAttack"):
        objs = [o for o in d.find_objects_which_contain(By.NAME, n, enabled=False) if o.name.startswith(n)]
        for o in objs:
            e = {"name": o.name, "id": o.id, "active": go_active(o), "pos": [round(o.worldX, 2), round(o.worldY, 2), round(o.worldZ, 2)]}
            a = rd(o, "Critter", "isPlayerInAlertZone", 1)
            e["critter"] = not str(a).startswith("ERR"); e["alert"] = a if e["critter"] else None
            out.append(e)
    return out
def sample(tag, t_end):
    s = {"tag": tag, "dt": round(time.time() - t_end, 2), "t": now(), "state": sname(gstate())}
    s["directors"] = directors(); c = first("CutsceneManager")
    s["_activePlayableDirector"] = str(rd(c, "CutsceneManager", "_activePlayableDirector.name", 1))[:80]
    s["glue"] = glue(); s["count"] = alert_count(); s["dlg"] = dlg()
    s["dt_end"] = round(time.time() - t_end, 2)
    R["samples"].append(s); dump(); print(json.dumps(s, ensure_ascii=False), flush=True); return s
prestage("a2"); autosync(True)
try:
    hyg_tick(R, "a2")
    if "Field_Farms" not in scenes():
        try: print("goto", goto("Field_Farms"), flush=True)
        except Exception as e:
            print("ERR", e); goto("Field_Hill"); time.sleep(2); print("goto", goto("Field_Farms"))
    time.sleep(2); wait_play_ready()
    R["exits"] = exits(); R["glue_before"] = glue(); R["directors_before"] = directors()
    print("EXITS", R["exits"], "\nGLUE", R["glue_before"], "\nDIR", R["directors_before"], flush=True)
    ay = pos_of("Ayud"); R["ayud"] = ay; R["exit_hits_near_ayud"] = [hits_exit(R["exits"], ay[0] - k, ay[2]) for k in (10, 1.5, 1.3, 1.1, 1.0)]
    print("AYUD", ay, R["exit_hits_near_ayud"], flush=True)
    assert not any(R["exit_hits_near_ayud"]), "точка у Ayud пересекает выход"
    R["q_before"] = qdetail(); R["before"] = full_snap("S1-Q1-QL2 до", off); print(R["q_before"], R["before"]["state"], flush=True)
    ok, tries = approach("Ayud"); R["hint"] = ok; assert ok, "нет подсказки"
    step0 = quest()["step"]; fin0 = len(save_info().get("finished", [])); R["fin0"] = fin0; key("E", 0.1); time.sleep(1.0); assert dlg(), "диалог не открылся"
    seq = []; sp = 0; t0 = time.time(); t_end = None
    while time.time() - t0 < 90:
        l = line()
        if l and (not seq or seq[-1] != l): seq.append(l)
        st = gstate(); q = len(save_info().get("finished", []))
        R["poll"].append((round(time.time() - t0, 1), sname(st), q, quest()["step"], dlg()))
        if st == 4 or q > fin0: t_end = time.time(); break
        if dlg() and choices(): R["choices"] = True; break
        if dlg() and sp < 40: key("Space", 0.1); sp += 1
        time.sleep(0.9)
    R["seq"] = seq; R["space"] = sp; R["step"] = [step0, quest()["step"]]; R["fin"] = [fin0, len(save_info().get("finished", []))]; print("dialog", sp, len(seq), R["step"], R["fin"], sname(gstate()), "t_end", bool(t_end), flush=True)
    if t_end:
        sample("0s", t_end)
        d.get_png_screenshot(os.path.join(R2, "shots", "a2_0s.png"))
        for at in (5, 10, 20):
            while time.time() - t_end < at: time.sleep(0.2)
            sample("%ds" % at, t_end)
            d.get_png_screenshot(os.path.join(R2, "shots", "a2_%ds.png" % at))
    R["q_after"] = qdetail(); R["after"] = full_snap("S1-Q1-QL2 после", off); R["exc"] = exc_summary(off)
    print("AFTER", R["q_after"], R["after"]["state"], R["after"]["save_finished"], "exc", R["exc"]["total"], R["exc"]["by_type"], flush=True)
finally:
    autosync(False); dump()
