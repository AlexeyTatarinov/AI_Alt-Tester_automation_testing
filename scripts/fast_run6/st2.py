import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect()
print("dlg", dlg(), "choices", choices(), "line", line())
for n in ("Panel Choices","Dialogue_Panel","Choices","Panel Choices (1)"):
    for e in (True, False):
        try:
            o = d.find_object(By.NAME, n, enabled=e); print(n, "enabled=%s found"%e, o.enabled)
        except Exception as ex: print(n, "enabled=%s"%e, type(ex).__name__)
for o in d.find_objects(By.COMPONENT,"UIDialogueChoicesManager",enabled=False): print("mgr",o.name,o.enabled)
print([ (o.name) for o in d.find_objects(By.COMPONENT,"UnityEngine.UI.Button",enabled=True)])
