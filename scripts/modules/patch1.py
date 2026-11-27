import sys; sys.path.insert(0, r"Test_Ai\scripts\modules")
from elib import *
r=load_er(); x=r["M01-02"]
x["verdict"]="OBSERVATION"
x["numbers"]+=" | AudioListener: объектов с компонентом 2 (Field_Hill, Town_Market) и 5 (Beach), активных всегда 1; по критерию «если 2 — OBSERVATION»; в логе за переход 51 сообщение «2 audio listeners» (P11). Остальные объекты ровно по 1."
save_er("M01-02",x)
