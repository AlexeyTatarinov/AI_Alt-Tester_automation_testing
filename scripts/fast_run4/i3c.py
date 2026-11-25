import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("int03c")
print("hint", hint(), "dxz", round(dxz(ppos(),HARE),2))
t0 = time.time(); key("E", 0.1); op=None
while time.time()-t0 < 2.0:
    if dlg(): op = round(time.time()-t0,2); break
    time.sleep(0.05)
print("dialog opened s:", op); time.sleep(0.6)
print(shot("int03_dlg_open"))
for t in dlg_texts(): print("T", t)
print("choices", choices(), "state", pstate())
m = ui_obj("UIDialogueManager")
for pth in ("_dialogueText","_actorNameText","_lineText"):
    try: print(pth, m.get_component_property("UIDialogueManager", pth+".text", ASM))
    except Exception as e: print(pth, "err", type(e).__name__)
