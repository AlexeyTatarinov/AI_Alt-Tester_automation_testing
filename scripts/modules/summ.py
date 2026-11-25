import json,sys
O=r"C:\Users\Aotat\Desktop\Test_Ai\Reports_2026-11-21\results\modules_stage1_20261125"
for s in ("MainMenu","Beach","Field_Hill","Town_Market"):
    S=json.load(open(O+"/module_snapshot_%s.json"%s,encoding="utf-8"))
    print("=====",s,S["loaded_scenes"])
    for m,cs in S["modules"].items():
        print(m," ".join("%s=%s%s"%(c.split('.')[-1],v["count"],"!" if v.get("error") else "") for c,v in cs.items()))
    print("oracles",json.dumps(S["oracles"],ensure_ascii=False)[:900])
    print("exits",[(e["name"],e["to"],e["path"]) for e in S["location_exits"]])
    print("entr",[(e["name"],e["path"]) for e in S["location_entrances"]])
    print("critters",S["critter_kinds"],S.get("critter_navmesh_search"))
    print("critter comps",S.get("critter_components_first"))
    print("listeners",S.get("audio_listeners"))
    print("tagged",{k:[x["name"] for x in v] for k,v in S.get("tagged",{}).items()})
