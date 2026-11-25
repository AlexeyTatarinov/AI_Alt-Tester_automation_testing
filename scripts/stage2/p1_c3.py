from s2lib import *
R = json.load(open(os.path.join(R2, "p1_c1.json"), encoding="utf-8")); off = R["off"]; s0 = R["snap_before"]
autosync(True)
try:
    assert inv()
    # рецепт по имени предмета
    sl = [x for x in slots() if "SweetCream" in x[1]]; assert sl
    sl[0][0].click(); time.sleep(1.0)
    # кнопка по тексту "Cook"
    cook = None
    for o in d.find_objects(By.NAME, "Text (TMP)", enabled=True):
        try:
            if o.get_text().strip() == "Cook":
                p = o.get_parent()
                cook = p; R["cook_parent"] = p.name
        except Exception: pass
    assert cook is not None
    R["action_interactable_before"] = action_button()[1]
    print("cook btn", cook.name, "interactable", R["action_interactable_before"], shot("p1_pot_selected"), flush=True)
    st0 = save_info()
    guard.risky("p1 cook")
    cook.click(); time.sleep(3.0)
    st1 = save_info()
    R["save_changed"] = st0["hash"] != st1["hash"]
    print("inv open", inv(), "state", sname(gstate()), flush=True)
    if inv():
        key("Tab", 0.1); time.sleep(1.5)
    s2 = snap("IT-04 после", off); R["snap_after"] = s2; R["diff"] = diff(s0, s2)
    R["exc_detail"] = exc_summary(off)
    R["shot_after"] = shot("p1_after_cook")
    print("AFTER", json.dumps(s2, ensure_ascii=False)); print("DIFF", json.dumps(R["diff"], ensure_ascii=False)); print("exc", json.dumps(R["exc_detail"], ensure_ascii=False)[:800])
    jdump(os.path.join(R2, "p1_c1.json"), R)
finally:
    autosync(False)
