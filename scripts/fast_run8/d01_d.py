import sys, json
sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\fast_run7")
from r4lib import *
d=connect(); print("rw", guard.restore_window("d")); preflight("d01d")
d.set_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS,True)
R={}
try:
    guard.risky("d01 back to menu"); off=log_mark()
    print("to_menu", to_menu(), flush=True)
    for _ in range(20):
        time.sleep(1.5)
        if "MainMenu" in scenes() and d.find_objects(By.NAME,"Button New Game",enabled=False): break
    time.sleep(1); guard.restore_window("d ng")
    print("new_game", new_game(), flush=True)
    for _ in range(20):
        time.sleep(1.5)
        try: ppos(); break
        except Exception: pass
    time.sleep(2); R["finished_after_ng"]=save_info()["finished"]
    tp_hare(1.3)
    for i in range(12):
        if hint(): break
        step_towards(HARE,0.2); time.sleep(0.4)
    print("hint", hint(), flush=True)
    key("E",0.1); time.sleep(1.0); print("dlg", dlg())
    n=0; seq=[]
    while n<45 and dlg():
        key("Space",0.1); n+=1; time.sleep(1.0); l=line()
        if l and (not seq or seq[-1]!=l): seq.append(l)
        if choices(): R["choices"]=True; break
    time.sleep(2); R.update(N=n, closed=not dlg(), seq=seq, exc=exc_summary(off))
    print(json.dumps(R, ensure_ascii=False)[:3000])
    json.dump(R, open(r"C:\Users\Aotat\Desktop\Test_Ai\Reports_2026-11-21\results\run8_d01_20261124\d01_d.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
finally:
    d.set_static_property("UnityEngine.Physics","autoSyncTransforms",PHYS,False)
