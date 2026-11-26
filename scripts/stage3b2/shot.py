# -*- coding: utf-8 -*-
from s3blib import *
import sys
d.get_png_screenshot(os.path.join(R2, "shots", sys.argv[1] + ".png"))
print([round(v, 2) for v in ppos()], sname(gstate()), alert_count(), scene_now())
for o in d.find_objects(By.COMPONENT, "Critter", enabled=True): print(o.name, [round(o.worldX, 2), round(o.worldZ, 2)])
