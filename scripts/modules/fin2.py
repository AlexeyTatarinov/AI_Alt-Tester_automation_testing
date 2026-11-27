import json, re
B=r"Test_Ai"
OUT=B+r"\Reports_2026-11-21\results\modules_stage1_20261125"
P=B+r"\Reports_2026-11-21\results\opus_review_20261124\cases_state.json"
RP="Reports_2026-11-21/results/modules_stage1_20261125/report.md"
E=json.load(open(OUT+"/results_E.json",encoding="utf-8"))
j=json.load(open(P,encoding="utf-8"))
ids={c["id"] for c in j["cases"]}
def add(cid,module,level,verdict,notes,dnr,jira=None,depends=None):
    if cid in ids: return
    j["cases"].append({"id":cid,"verdict":verdict,"date":"2026-11-25","run":"modules_stage1","source":RP,"method":"M-TP1","needs_clean_play":False,"depends_on":depends or [],"do_not_repeat_until":dnr,"jira":jira,"notes":notes,"module":module,"level":level})
add("M01-02","M01","L1",E["M01-02"]["verdict"],"3 transitions: SceneLoader/AudioManager/EventSystem/PigChef = 1 each time; AudioListener objects 2 (Field_Hill, Town_Market) / 5 (Beach), active always 1. See report.","never needed")
add("M18-01","M18","L1",E["M18-01"]["verdict"],"Music tracks differ: Music_Beach / Music_Glade (Field_Hill, MusicPlayer says Music_Field) / Music_Town.","audio change")
add("M08-01","M08","L1","FAIL","Partial: only Field_Hill exits tested. ToFarms PASS (0.00 m from entrance, no CC-67). ToBeach_JumpDown: Beach loaded in 0.9 s but no PigChef afterwards, then game stayed with scenes PersistentManagers+Gameplay only (black screen, cheat menu and Esc dead) = soft-lock; one sample, not reproduced (needs Stop/Play by owner). Other 8 locations not tested.","owner restarts Play; then rerun JumpDown first","CC-67",["LOC-01"])
for cid,m,l in (("M10-01","M10","L1"),("M10-02","M09+M10","L1"),("M07-01","M07","L1"),("M03-01","M03","L1"),("M18-02","M17+M18","L2"),("M16-01","M16","L1"),("M06-01","M06","L1")):
    add(cid,m,l,"BLOCKED","Not run: game soft-locked after M08-01 JumpDown test (no location scene, no player); recovery needs Stop/Play which the task forbids.","owner restarts Play")
j["_meta"]["modules_stage1_2026-11-25"]="added M01-02, M18-01, M08-01 (partial), and BLOCKED rows for the rest of stage E; fields module/level added to all older cases (stage A)"
json.dump(j,open(P,"w",encoding="utf-8"),ensure_ascii=False,indent=2)
print(len(j["cases"]))
