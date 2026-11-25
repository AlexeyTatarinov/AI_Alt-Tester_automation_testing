import sys; sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\modules")
from elib import *

AUD = "UnityEngine.AudioModule"


def counts():
    p = pigs()
    return {"SceneLoader": count_comp("SceneLoader"), "AudioManager": count_comp("AudioManager"), "EventSystem(name)": count_name("EventSystem"),
            "AudioListener_all": count_comp("AudioListener", False), "AudioListener_active": count_comp("AudioListener", True), "PigChef(Clone)": len(p)}


def music(scene):
    r = {"scene": scene, "playing": []}
    mp = first("MusicPlayer")
    r["MusicPlayer._thisSceneSO.name"] = rd(mp, "MusicPlayer", "_thisSceneSO.name")
    r["MusicPlayer._thisSceneSO.musicTrack.name"] = rd(mp, "MusicPlayer", "_thisSceneSO.musicTrack.name")
    srcs = d.find_objects(By.COMPONENT, "UnityEngine.AudioSource", enabled=False)
    r["audiosources_total"] = len(srcs)
    for o in srcs:
        try:
            pl = o.get_component_property("UnityEngine.AudioSource", "isPlaying", AUD)
            if pl:
                clip = o.get_component_property("UnityEngine.AudioSource", "clip.name", AUD)
                lp = o.get_component_property("UnityEngine.AudioSource", "loop", AUD)
                r["playing"].append({"obj": o.name, "clip": clip, "loop": lp})
        except Exception as e:
            r.setdefault("errors", []).append("%s: %s" % (o.name, type(e).__name__))
    return r


off0 = log_mark()
res = {"M01-02": {"steps": []}, "M18-01": {"scenes": {}}}
prestage("E1_start")
print("scenes", scenes())
if "MainMenu" in scenes():
    print("new game", new_game_from_menu())
    time.sleep(3)
autosync(True)
tp(-195.58, -9.42, -376.9, 0.5) if False else None
print("scenes", scenes(), "pigs", len(pigs()))
res["M01-02"]["steps"].append({"at": "Beach(NewGame)", "counts": counts()})
res["M18-01"]["scenes"]["Beach_first"] = music("Beach")
chain = [("Field_Hill", 1), ("Town_Market", 3), ("Beach", 0)]
for name, _ in chain:
    off = log_mark()
    info = goto(name)
    time.sleep(4)
    c = counts()
    st = {"at": name, "go": info, "scenes": scene_now(), "counts": c, "log": log_since(off)}
    res["M01-02"]["steps"].append(st)
    print(name, info, c, flush=True)
    res["M18-01"]["scenes"][name if name != "Beach" else "Beach_after_chain"] = music(name)
jdump(OUT + "/m01_02_m18_01.json", res)
# вердикты
bad = []
for st in res["M01-02"]["steps"]:
    c = st["counts"]
    for k in ("SceneLoader", "AudioManager", "EventSystem(name)", "PigChef(Clone)"):
        if c[k] != 1:
            bad.append((st["at"], k, c[k]))
al = [(st["at"], st["counts"]["AudioListener_all"], st["counts"]["AudioListener_active"]) for st in res["M01-02"]["steps"]]
al_not1 = [a for a in al if a[2] != 1]
exc = exc_summary(off0)
num = "после 3 переходов (Beach->Field_Hill->Town_Market->Beach): SceneLoader/AudioManager/EventSystem/PigChef = 1 везде: %s; нарушения %s; AudioListener (всего объектов, активных) по шагам %s; исключений %s" % (not bad, bad, al, exc["total"])
if bad:
    v = "FAIL"
elif al_not1:
    v = "OBSERVATION"
else:
    v = "PASS"
save_er("M01-02", {"verdict": v, "numbers": num, "source": "m01_02_m18_01.json"})
ms_ = res["M18-01"]["scenes"]
tr = {k: (v_["MusicPlayer._thisSceneSO.musicTrack.name"], [p["clip"] for p in v_["playing"] if p["loop"]]) for k, v_ in ms_.items()}
tracks = {str(v_[0]) for k, v_ in tr.items() if k in ("Beach_first", "Field_Hill", "Town_Market")}
clips = {tuple(sorted(set(map(str, v_[1])))) for k, v_ in tr.items() if k in ("Beach_first", "Field_Hill", "Town_Market")}
v2 = "PASS" if (len(tracks) == 3 or len(clips) == 3) else "OBSERVATION"
save_er("M18-01", {"verdict": v2, "numbers": "музыкальный трек сцены (MusicPlayer) и играющие зацикленные клипы: %s; различных треков %d из 3, наборов клипов %d из 3" % (tr, len(tracks), len(clips)), "source": "m01_02_m18_01.json"})
