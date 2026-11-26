from s3lib import *
autosync(True)
im = first("InteractionManager")
try:
    for i in range(8):
        print(step_towards(HARE, 0.2), "pot", rd(im,"InteractionManager","_potentialInteractions.Count"), "hint", hint())
        time.sleep(0.5)
    print("now", ppos(), dxz(ppos(), HARE))
finally: autosync(False)
