import json,sys
P=r"C:\Users\Aotat\Desktop\Test_Ai\Reports_2026-11-21\results\opus_review_20261124\cases_state.json"
j=json.load(open(P,encoding="utf-8"))
M={"TP-00":("T01","L1"),"TP-01":("T01","L1"),"TP-02":("M07","L1"),"CON-01":("M01","L1"),
"INT-01":("M11","L1"),"INT-02":("M11","L1"),"INT-03":("M14","L2"),"INT-04":("M11","L1"),"INT-05":("M11","L1"),
"INT-06":("M12","L2"),"INT-07":("M11","L1"),
"DTH-01":("M09","L1"),"DTH-02":("M09","L1"),"DTH-03":("M09","L1"),"DTH-04":("M09","L1"),
"ENM-01":("M10","L1"),"ENM-02":("M10","L1"),"ENM-03":("M10","L2"),
"BND-00":("M06","L1"),"BND-01":("M06","L1"),"BND-02":("M06","L1"),"BND-03":("M06","L1"),"BND-04":("M06","L1"),
"BND-05":("M06","L1"),"BND-05b":("M06","L1"),"BND-06":("M06","L1"),"BND-07":("M06","L1"),
"LOC-01":("M08","L1"),"LOC-02":("M08","L1"),"LOC-03":("M08","L1"),"LOAD-00":("M01","L1"),
"INV-10":("M12","L1"),"INV-11":("M12","L1"),"INV-12":("M12","L1"),"INV-13":("M13","L1"),"COOK-01":("M13","L2"),
"SET-01":("M17","L1"),"DLG-10":("M14","L2"),"DLG-10b":("M14","L2"),"DLG-10b-No":("M14","L1"),"DLG-11":("M03","L2"),
"QST-10":("M15","L2"),"SAVE-05":("M04","L1"),"SAVE-06":("M04","L1"),"GUARD-01":("T01","L1"),
"PAUSE-01":("M02","L1"),"MENU-08":("M01","L1"),"L10N-01":("M17","L1"),"L10N-02":("M17","L1"),"Forest_Entrance":("T01","L1")}
miss=[c["id"] for c in j["cases"] if c["id"] not in M]
assert not miss,miss
for c in j["cases"]:
    c["module"],c["level"]=M[c["id"]]
j["_meta"]["fields_added_2026-11-25"]={"module":"M01..M19 or T01: module id from modules-decomposition-2026-11-25.md section 2","level":"L1 module / L2 integration chain IT-xx / L3 e2e (decomposition sections 3-4)","assignment_notes":"CON-01->M01, MENU-08->M01 (loop Back to menu/New Game), INT-06->M12 L2 (IT-05), INT-07->M11, INV-13->M13 (cooking button), COOK-01->M13 L2 (IT-04), DLG-11->M03 L2 (IT-09), TP-01->T01 (teleport tool), Forest_Entrance->T01"}
json.dump(j,open(P,"w",encoding="utf-8"),ensure_ascii=False,indent=2)
print(len(j["cases"]),"ok")
