# -*- coding: utf-8 -*-
"""Уход за консолью Unity во время прогонов (25.11.2026). Причина: каждая команда AltTester пишет в Console/Editor.log запись со стеком,
консоль росла до сотен тысяч записей, Editor.log до ~180 МБ, редактор зависал. Только вызовы через AltTester, проект не меняется; сбрасывается каждым Play.
Использование (из своих скриптов, драйвер уже открыт):
    import sys; sys.path.insert(0, r"C:\\Users\\Aotat\\Desktop\\Test_Ai\\scripts\\play_control")
    import housekeeping as hk
    hk.setup(d)            # в начале Play: стек у Log отключить, Warning = ScriptOnly, очистить консоль
    hk.tick(d)             # раз в ~10 минут и перед тяжёлой серией: очистить консоль, если записей > 20000
    hk.console_count(d)    # сколько записей в консоли (или None)
Опрос делать не чаще 1 раза в секунду (мера д)."""
import time

_LE = ("UnityEditor.LogEntries", "UnityEditor.CoreModule")
_last_clear = [0.0]

def _call(d, typ, asm, method, params=None, ptypes=None):
    try:
        if params is None:
            return True, d.call_static_method(typ, method, asm, [])
        return True, d.call_static_method(typ, method, asm, params, ptypes)
    except Exception as e:
        return False, "%s: %s" % (type(e).__name__, str(e)[:120])

def console_count(d):
    ok, v = _call(d, _LE[0], _LE[1], "GetCount")
    try: return int(v) if ok else None
    except Exception: return None

def clear_console(d):
    ok, v = _call(d, _LE[0], _LE[1], "Clear")
    if ok: _last_clear[0] = time.time()
    return ok, v

def set_stack_trace(d):
    """Log -> None (самый частый), Warning -> ScriptOnly (стек полезен для CC-67). Error/Exception не трогаем.
    Возвращает словарь результатов; если AltTester не передаёт enum-параметры, будет ok=False (мера «CANNOT»)."""
    res = {}
    for lt, st, key in (("Log", "None", "log"), ("Warning", "ScriptOnly", "warning")):
        res[key] = _call(d, "UnityEngine.Application", "UnityEngine.CoreModule", "SetStackTraceLogType",
                         [lt, st], ["UnityEngine.LogType, UnityEngine.CoreModule", "UnityEngine.StackTraceLogType, UnityEngine.CoreModule"])
    return res

def setup(d):
    r = {"clear": clear_console(d), "stack": set_stack_trace(d), "count": console_count(d)}
    return r

def tick(d, every_s=600, limit=20000):
    """раз в every_s секунд или если записей больше limit: очистить консоль. Возвращает (сделано, число записей до)"""
    n = console_count(d)
    if (n is not None and n > limit) or time.time() - _last_clear[0] > every_s:
        clear_console(d); return True, n
    return False, n
