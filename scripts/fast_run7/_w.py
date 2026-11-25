import os, sys, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import guard
w = guard.unity_window("state_check6"); print(json.dumps(w, ensure_ascii=False)); print("port", guard.port_open())
