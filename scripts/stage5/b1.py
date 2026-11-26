# Play B: New Game, Town_Market, M19-01
from s3blib import *
R = {}
def dump(): jdump(os.path.join(R2, "b1.json"), R)
prestage("b1")
R["frameCount0"] = d.get_static_property("UnityEngine.Time", "frameCount", CORE); assert "MainMenu" in scenes()
R["save_eq"] = save_hashes() == bk_hashes()
hyg_start("b1", R); guard.risky("b1"); R["off"] = off = log_mark()
print("ng", new_game(), R["save_eq"], flush=True); wait_play_ready(); time.sleep(16)
R["start"] = st_now("после New Game")
print("goto", goto("Town_Market"), flush=True); time.sleep(2); wait_play_ready()
def allnpc():
    return {o.id: o for o in d.find_objects(By.COMPONENT, "NPCMovement", enabled=False)}
def P(o): return [round(o.worldX, 2), round(o.worldY, 2), round(o.worldZ, 2)]
series = []
t0 = time.time()
for at in (0, 5, 10, 15, 20, 25, 30):
    while time.time() - t0 < at: time.sleep(0.1)
    a = allnpc(); series.append({"dt": round(time.time() - t0, 2), "pos": {str(i): P(o) for i, o in a.items()}})
R["series"] = series
active = [o.id for o in d.find_objects(By.COMPONENT, "NPCMovement", enabled=True)]
info = {}
for i, o in allnpc().items():
    e = {"name": o.name, "active": i in active}
    e["config"] = str(rd(o, "NPCMovement", "_npcMovementConfig.name", 1))[:80]
    e["speed"] = str(rd(o, "NPCMovement", "_npcMovementConfig.Speed", 1))[:40]
    e["stop"] = str(rd(o, "NPCMovement", "_npcMovementConfig.StopDuration", 1))[:40]
    e["npcState"] = str(rd(o, "NPC", "npcState", 1))[:40]
    e["actor"] = str(rd(o, "StepController", "_actor.name", 1))[:60]
    e["dialogue"] = str(rd(o, "StepController", "_defaultDialogue.name", 1))[:60]
    e["agent"] = str(rd(o, "UnityEngine.AI.NavMeshAgent", "enabled", 1, "UnityEngine.AIModule"))[:60]
    e["sm"] = str(rd(o, "UOP1.StateMachine.StateMachine", "_currentState._originSO.name", 1, "UOP1.StateMachine"))[:60]
    p = [s["pos"].get(str(i)) for s in series]
    e["p0"] = p[0]; e["p30"] = p[-1]
    e["d0_30"] = round(dist3(p[0], p[-1]), 2); e["path_sum"] = round(sum(dist3(p[k], p[k + 1]) for k in range(len(p) - 1)), 2)
    e["maxd"] = round(max(dist3(p[0], q) for q in p), 2)
    info[str(i)] = e
    print(i, json.dumps(e, ensure_ascii=False), flush=True)
R["npc"] = info; R["n"] = len(info); R["exc"] = exc_summary(off); print("n", len(info), "exc", R["exc"]["total"]); dump()
d.get_png_screenshot(os.path.join(R2, "shots", "b1_market.png"))
