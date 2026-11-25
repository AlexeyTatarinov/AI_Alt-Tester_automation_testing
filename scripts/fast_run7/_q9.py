import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r4lib import *
d = connect(); print(scenes(), "frame", d.get_static_property("UnityEngine.Time","frameCount","UnityEngine.CoreModule"), "t", d.get_static_property("UnityEngine.Time","realtimeSinceStartup","UnityEngine.CoreModule"))
