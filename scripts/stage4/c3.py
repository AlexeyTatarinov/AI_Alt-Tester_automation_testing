# -*- coding: utf-8 -*-
# доп. чтения в залипшем состоянии: кто в списке, держится ли дольше, Tab/Esc/W
from s3blib import *
R = {}
off = json.load(open(os.path.join(R2, "c1.json"), encoding="utf-8"))["off"]
prestage("c3")
u = first("UIManager")
for p in ("_gameStateManager._alertEnemies", "_gameStateManager._alertEnemies[0]", "_gameStateManager._alertEnemies[0].name", "_gameStateManager._alertEnemies[0].position"):
    R[p] = str(rd(u, "UIManager", p, 1))[:300]; print(p, "=>", R[p], flush=True)
R["later"] = st_now("позже"); R["critters"] = len(d.find_objects(By.COMPONENT, "Critter", enabled=False))
p0 = ppos(); key("W", 0.3); time.sleep(1.2); R["w_moved"] = round(dxz(p0, ppos()), 2)
time.sleep(1.0); key("Tab", 0.1); time.sleep(1.5); R["tab_opens"] = inv(); R["state_after_tab"] = sname(gstate())
if R["tab_opens"]: key("Tab", 0.1); time.sleep(1.5)
key("Escape", 0.1); time.sleep(1.5); R["esc_pause"] = pause_open()
key("Escape", 0.1); time.sleep(1.5); R["after_esc"] = st_now("после Esc", pause=pause_open())
R["exc"] = exc_summary(off); R["console"] = hk.console_count(d)
print("critters", R["critters"], "w", R["w_moved"], "tab", R["tab_opens"], "esc", R["esc_pause"], "exc", R["exc"]["total"], "console", R["console"], flush=True)
jdump(os.path.join(R2, "c3.json"), R)
