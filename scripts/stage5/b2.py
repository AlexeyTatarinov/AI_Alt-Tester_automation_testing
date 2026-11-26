from s3blib import *
R = {}
off = json.load(open(os.path.join(R2, "b1.json"), encoding="utf-8"))["off"]
N = "Townsfolk_F (4)"
def npc():
    o = d.find_object(By.NAME, N, enabled=True)
    return {"t": now(), "pos": [round(o.worldX, 2), round(o.worldY, 2), round(o.worldZ, 2)], "npcState": str(rd(o, "NPC", "npcState", 1)), "isInDialogue": str(rd(o, "StepController", "isInDialogue", 1)), "sm": str(rd(o, "UOP1.StateMachine.StateMachine", "_currentState._originSO.name", 1, "UOP1.StateMachine"))}
autosync(True)
try:
    R["before"] = npc(); ok, tries = approach(N); R["hint"] = ok; R["tries"] = tries; print("hint", ok, tries, R["before"], flush=True)
    if ok:
        key("E", 0.1); time.sleep(1.5); R["opened"] = dlg(); R["line"] = line(); R["during"] = []
        for i in range(3): R["during"].append(npc()); time.sleep(1.5)
        R["state_during"] = sname(gstate()); d.get_png_screenshot(os.path.join(R2, "shots", "b2_talk.png"))
        n = 0; good = 0; seq = [R["line"]]
        while n < 20 and good < 4:
            if dlg(): key("Space", 0.1); n += 1; good = 0
            elif gstate() == 0: good += 1
            time.sleep(1.2)
            l = line()
            if l and l != seq[-1]: seq.append(l)
        R["closed"] = good >= 4; R["space"] = n; R["seq"] = seq
        R["after"] = []
        for i in range(4): R["after"].append(npc()); time.sleep(3)
    R["state_end"] = sname(gstate()); R["exc"] = exc_summary(off)
    print(json.dumps(R, ensure_ascii=False), flush=True)
finally:
    autosync(False); jdump(os.path.join(R2, "b2.json"), R)
