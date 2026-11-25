# -*- coding: utf-8 -*-
"""Адаптер Python SDK (AltTester-Driver 2.4.1) для наборов TestAI.
Подменяет в модуле lib примитивы, которые в CLI-версии вызывают `alttester`: все остальные функции lib
(cam_state, Passive, Suite, математика) работают поверх них без изменений. Объекты ищутся с enabled=False.
Запуск: интерпретатором из scripts\sdk_smoke\.venv (там стоит пакет alttester).
"""
import atexit
import time

from alttester import AltDriver, AltKeyCode, By

import lib

_driver = AltDriver(host="127.0.0.1", port=13000, timeout=20)
atexit.register(lambda: _driver.stop())


def _obj(o):
    return {"name": o.name, "enabled": o.enabled, "worldX": o.worldX, "worldY": o.worldY, "worldZ": o.worldZ}


def find(name, by=None, wait=0):
    try:
        return _obj(_driver.find_object(By.NAME, name, enabled=False))
    except Exception:
        return None


def find_all(value=None, by=None, contains=None):
    if contains is not None:
        return [_obj(o) for o in _driver.find_objects_which_contain(By.NAME, contains, enabled=False)]
    return [_obj(o) for o in _driver.find_objects(By.NAME, value, enabled=False)]


def _key(k):
    return getattr(AltKeyCode, k)


def press(key, dur=0.1):
    return _driver.press_key(_key(key), power=1, duration=dur, wait=True)


def key_down(key):
    return _driver.key_down(_key(key))


def key_up(key):
    return _driver.key_up(_key(key))


def reset_input():
    try:
        _driver.reset_input()
    except Exception:
        pass


def set_time_scale(v):
    _driver.set_time_scale(float(v))


def get_prop(name, comp, prop, assembly="Assembly-CSharp"):
    try:
        o = _driver.find_object(By.NAME, name, enabled=False)
        v = o.get_component_property(comp, prop, assembly, max_depth=2)
        return {"success": True, "data": {"value": v}}
    except Exception as e:
        return {"success": False, "message": str(e)}


def scenes():
    return list(_driver.get_all_loaded_scenes())


def cur_scene():
    return _driver.get_current_scene()


def shot(path):
    return path


# подмена в lib: все функции lib используют эти глобальные имена
for _n in ("find", "find_all", "press", "key_down", "key_up", "reset_input", "set_time_scale", "get_prop", "scenes", "cur_scene", "shot"):
    setattr(lib, _n, globals()[_n])
# wpos/player_pos/health/is_dead/cam_state строятся на find/get_prop из lib - подмена выше достаточна


def move_mouse(x, y, duration=0.1):
    _driver.move_mouse({"x": int(x), "y": int(y)}, duration=duration, wait=True)


def tap_by_name(name):
    _driver.find_object(By.NAME, name, enabled=False).click()


def driver():
    return _driver
