import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("s2_walk")
tgt = (HARE[0]-1.3, HARE[1], HARE[2]); T0 = time.time(); last = None; stuck = 0
for i in range(120):
    if time.time() - T0 > 240: break
    p = ppos(); dist = dxz(p, tgt)
    if dist < 2.5 or hint(): break
    k = choose_key(p, tgt); key(k, 1.0); time.sleep(0.2); p1 = ppos()
    mv = dxz(p, p1)
    if i % 5 == 0: print(i, k, round(mv,2), "dist", round(dist,1), tuple(round(v,1) for v in p1), flush=True)
    stuck = stuck + 1 if mv < 0.3 else 0
    if stuck >= 4: print("ЗАСТРЯЛ", p1); break
print("end pos", ppos(), "dist", round(dxz(ppos(), HARE),2), "hint", hint(), "t", round(time.time()-T0))
