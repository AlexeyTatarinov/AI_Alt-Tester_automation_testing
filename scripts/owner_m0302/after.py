# -*- coding: utf-8 -*-
from s3blib import *
autosync(False)
print(st_now("после перехода", critters=len(d.find_objects(By.COMPONENT, "Critter", enabled=True))))
u = first("UIManager")
for i in range(3): print(i, str(rd(u, "UIManager", "_gameStateManager._alertEnemies[%d].name" % i, 1))[:140])
d.get_png_screenshot(os.path.join(R2, "shots", "prep_after.png"))
