import sys, json
sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\fast_run7")
from r4lib import *
d=connect(); guard.restore_window("c5"); preflight("d01c5")
assert inv()
off=log_mark()
print("action btn before select", action_button()[1])
s=[x for x in slots() if x[1]=="SweetCream_Recipe"][0][0]
s.click(); time.sleep(1.0)
print("action btn after select", action_button()[1], shot("d01_pot_selected"))
st0 = save_info(); print("save0", st0["hash"], st0["stacks"])
guard.risky("d01 cook Q"); 
key("Q",0.1); time.sleep(3.0)
st1 = save_info(); print("save1", st1["hash"], st1["stacks"], "changed", st0["hash"]!=st1["hash"])
print("inv open", inv(), "exc", json.dumps(exc_summary(off), ensure_ascii=False)[:600], shot("d01_after_Q"))
