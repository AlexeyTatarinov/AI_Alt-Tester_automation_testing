from s3blib import *
A = json.load(open(os.path.join(R2, "a2.json"), encoding="utf-8")); off = A["off"] if "off" in A else json.load(open(os.path.join(R2, "a1.json"), encoding="utf-8"))["off"]
t = A["talk1"]
for i, l in enumerate(t["seq"]): print(i, l)
print("before", t["before"]["inv"], t["before"]["state"], "after", t["after"]["inv"], t["after"]["state"], t["after"]["alert_count"])
R = {}
R["now"] = full_snap("после talk1", off); R["q"] = qdetail(); R["dlg"] = dlg(); R["choices"] = choices(); R["line"] = line()
time.sleep(5); R["now5"] = full_snap("через 5 с без ввода", off); R["dlg5"] = dlg(); R["line5"] = line()
d.get_png_screenshot(os.path.join(R2, "shots", "a3_stuck.png"))
print(json.dumps(R, ensure_ascii=False))
print("exit", to_menu()); time.sleep(3)
R["menu_scenes"] = scenes(); R["save"] = save_info(); R["exc"] = exc_summary(off); print(R["menu_scenes"], R["save"], R["exc"]["total"])
jdump(os.path.join(R2, "a3.json"), R)
