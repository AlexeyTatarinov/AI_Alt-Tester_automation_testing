import sys; sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\modules")
from elib import *
for n in ("Field_Hill","Field_Farms","Field_Hill"):
    try: print(n, goto(n), scenes())
    except Exception as e: print(n,"ERR",e)
