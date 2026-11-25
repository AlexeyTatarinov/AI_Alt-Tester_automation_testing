import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); preflight("q3")
print("inv open", inv(), "tab", tab_type(), "dlg", dlg())
if not inv(): key("Tab", 0.1); time.sleep(1.2)
for i in range(4):
    print(i, "tab", tab_type(), [(n,a,at) for _,n,a,at in slots()])
    key("Y", 0.1); time.sleep(0.8)
