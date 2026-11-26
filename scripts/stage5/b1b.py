from s3blib import *
R = {}
f0 = d.get_static_property("UnityEngine.Time", "frameCount", CORE); t0 = d.get_static_property("UnityEngine.Time", "time", CORE)
time.sleep(3)
R["frames_3s"] = d.get_static_property("UnityEngine.Time", "frameCount", CORE) - f0; R["time_3s"] = round(d.get_static_property("UnityEngine.Time", "time", CORE) - t0, 2)
R["timeScale"] = d.get_static_property("UnityEngine.Time", "timeScale", CORE); R["state"] = sname(gstate()); R["pig"] = [round(v, 2) for v in ppos()]
R["talkingTo"] = {}
for o in d.find_objects(By.COMPONENT, "NPCMovement", enabled=False):
    R["talkingTo"][o.name] = [str(rd(o, "NPC", "talkingTo.Length", 1))[:20], str(rd(o, "UnityEngine.AI.NavMeshAgent", "isOnNavMesh", 1, "UnityEngine.AIModule"))[:20]]
print(json.dumps(R, ensure_ascii=False)); jdump(os.path.join(R2, "b1b.json"), R)
