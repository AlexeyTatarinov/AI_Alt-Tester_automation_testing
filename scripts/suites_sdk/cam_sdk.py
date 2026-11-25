# -*- coding: utf-8 -*-
"""Сверка эмулированной мыши AltTester (SDK) с калибровкой TestAI/calibration.md (CAM-01, CAM-02, CAM-03).
Игра в Beach. Расхождения только показываются. Запуск: .venv python TestAI/suites/cam_sdk.py"""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import lib_sdk  # noqa
from lib import *  # noqa

CX, CY, D = 553, 189, 200


def rd():
    st = cam_state()
    return st[0], st[1], st[2]


def drag(dx=0, dy=0, rmb=True):
    lib_sdk.move_mouse(CX - dx // 2, CY - dy // 2, 0.1)
    reset_input_noop = None
    time.sleep(1.0)
    yaw0, h0, off0 = rd()
    if rmb:
        key_down("Mouse1")
    lib_sdk.move_mouse(CX + dx // 2, CY + dy // 2, 0.3)
    if rmb:
        key_up("Mouse1")
    time.sleep(1.0)
    yaw1, h1, off1 = rd()
    fx, fz = cam_forward_from(off0)
    right = (fz, -fx)
    lat = (off1[0] - off0[0]) * right[0] + (off1[2] - off0[2]) * right[1]   # >0: камера ушла вправо от персонажа
    return round(yaw_diff(yaw0, yaw1), 1), round(h1 - h0, 2), round(lat, 2)


def cam_forward_from(off):
    n = math.hypot(off[0], off[2]) or 1.0
    return (-off[0] / n, -off[2] / n)


out = {"CAM-01": [], "CAM-02": [], "CAM-03": []}
for i in range(3):
    out["CAM-01"].append({"мышь вправо +200px": drag(dx=D), "мышь влево -200px": drag(dx=-D)})
for i in range(3):
    out["CAM-02"].append({"y +200 (вверх на экране, если y снизу)": drag(dy=D), "y -200": drag(dy=-D)})
for i in range(3):
    out["CAM-03"].append({"без ПКМ вправо": drag(dx=D, rmb=False), "без ПКМ влево": drag(dx=-D, rmb=False)})
reset_input()
json.dump(out, open(os.path.join(RESULTS_DIR, "CAM_sdk_calibration_check.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in out.items():
    print(k)
    for r in v:
        print("  ", r)
