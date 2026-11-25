import sys; sys.path.insert(0, r"C:\Users\Aotat\Desktop\Test_Ai\scripts\modules")
from elib import *
goto("Field_Farms"); time.sleep(2)
for o in d.find_objects(By.COMPONENT,"Critter",enabled=False)[:8]:
    print(o.name, o.id, o.enabled, round(o.worldX), round(o.worldZ))
    for pth in ["_currentHealthSO.CurrentHealth","_currentHealthSO._currentHealth","_currentHealthSO._maxHealth","_currentHealthSO","IsDead","_getHit","GetHit"]:
        r=sget(o,"Damageable",pth,depth=2); print("   ",pth,r["ok"],r["resp"][:120])
