import sys; sys.path.insert(0,r"Test_Ai\scripts\modules")
from mlib import *
print("hash_eq_backup", save_hashes()==bk_hashes())
try: d.set_static_property("UnityEngine.Application","runInBackground",CORE,True)
except Exception as e: print("rib",e)
R={}
def comps(name):
    l=d.find_objects(By.COMPONENT,name,enabled=False); return l
sg=comps("StartGame"); print("StartGame",[o.name for o in sg])
o=sg[0]
for p in ("_saveSystem.saveData._locationId","_saveSystem.saveData._finishedQuestlineItemsGUIds","_saveSystem.saveData"):
    for dep in (2,4):
        r=sget(o,"StartGame",p,ASM,dep); r.pop("raw",None); print(r)
am=comps("AudioManager"); print("AudioManager",[o.name for o in am])
a=am[0]
for g in ("MasterVolume","MusicVolume","SFXVolume"):
    t=time.time()
    try: v=a.call_component_method("AudioManager","GetGroupVolume",ASM,[g],["System.String"]); print(g,v,round(time.time()-t,2))
    except Exception as e: print(g,"ERR",type(e).__name__,str(e)[:200])
for p in ("_masterVolume","_musicVolume","_sfxVolume"):
    r=sget(a,"AudioManager",p); r.pop("raw",None); print(r)
print([ (c.name) for c in a.get_all_components()][:20] if hasattr(a,'get_all_components') else '')
