# -*- coding: utf-8 -*-
"""Перезапуск Play in Editor без мыши и без computer use.
НАПИСАН 24.11.2026 аудитом (Opus). НА ЖИВОЙ ИГРЕ НЕ ПРОВЕРЯЛСЯ (аудиту запрещено подключаться к порту 13000).
Запуск: scripts\\sdk_smoke\\.venv\\Scripts\\python.exe scripts\\play_control\\restart_play.py [--dry-run] [--check] [--restore-save]
Коды выхода: 0 успех; 2 предусловие не выполнено (ничего не менялось); 3 Play остановлен, но не запущен (СТОП, мышью не лечить);
             4 клавиша не отправлена (окно Unity не стало активным), Play остановлен; 5 Play запустился, но не MainMenu/не «чистый»;
             6 рабочий стол заблокирован (GetForegroundWindow()==0 или OpenInputDesktop не открывается): клавиша не отправлена.
Режим --start-only (25.11.2026, координатор): Play НЕ идёт -> только фокус, Ctrl+P, ожидание MainMenu, проверка frameCount (с --restore-save сначала вернёт save.chop).
Фокус: до 3 циклов по 6 попыток с паузой 20 с между циклами.
Что делает: (1) читает frameCount, realtimeSinceStartup, consoleFlags, сцены; (2) EditorApplication.isPlaying=False через AltTester;
(3) ждёт закрытия порта 13000; (4) по флагу --restore-save возвращает save.chop из копии (Play не идёт, игра файл не перепишет);
(5) активирует окно Unity и шлёт Ctrl+P (keybd_event, без мыши); (6) ждёт AltTester и MainMenu, проверяет frameCount < MAX_FRAMES.
Проект и игру не меняет. Второй Unity.exe не запускает, окно не сворачивает и не закрывает."""
import sys, os, time, json, socket, subprocess, hashlib, shutil, ctypes, datetime
from ctypes import wintypes

TESTAI = r"C:\Users\Aotat\Desktop\Test_Ai"
BK = os.path.join(TESTAI, r"Reports_2026-11-21\evidence\save_backup\20261122_122526")
SAVE_DIRS = {"Unity_Technologies": r"C:\Users\Aotat\AppData\LocalLow\Unity Technologies\Chop Chop",
             "Unity_Open_Projects": r"C:\Users\Aotat\AppData\LocalLow\Unity Open Projects\Chop Chop"}
LOGF = os.path.join(TESTAI, r"scripts\play_control\restart_play_last.json")
MAX_FRAMES = 3000          # «чистый» Play: счётчик кадров после старта мал (7b: чистый Play = frame < 700 при подключении)
EDITOR_ASM = ["UnityEditor.CoreModule", "UnityEditor"]
CORE = "UnityEngine.CoreModule"
DRY = "--dry-run" in sys.argv; CHECK = "--check" in sys.argv; RESTORE = "--restore-save" in sys.argv
START_ONLY = "--start-only" in sys.argv
rep = {"time": None, "steps": []}

def now(): return datetime.datetime.now().strftime("%H:%M:%S")
def step(msg, **kw):
    rep["steps"].append(dict(t=now(), msg=msg, **kw)); print("[%s] %s %s" % (now(), msg, kw if kw else ""), flush=True)
def done(code, why):
    rep["exit"] = code; rep["why"] = why
    json.dump(rep, open(LOGF, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("ИТОГ код %d: %s" % (code, why), flush=True); sys.exit(code)

def port_open(t=1.5):
    s = socket.socket(); s.settimeout(t)
    try: s.connect(("127.0.0.1", 13000)); return True
    except Exception: return False
    finally: s.close()

def game_alive(t=6):
    """True, если игра (приложение) подключена к AltTester. Порт 13000 держит AltTesterServer.exe, он открыт всегда, поэтому порт не годится."""
    d = None
    try:
        d = driver(timeout=t); d.get_all_loaded_scenes(); return True
    except Exception:
        return False
    finally:
        try:
            if d: d.stop()
        except Exception: pass

def driver(timeout=10):
    from alttester import AltDriver
    return AltDriver(host="127.0.0.1", port=13000, enable_logging=False, timeout=timeout)

def read_static(d, cls, prop, asms):
    last = None
    for a in asms:
        try: return d.get_static_property(cls, prop, a)
        except Exception as e: last = e
    raise last

def snapshot(d):
    s = {}
    s["frameCount"] = int(read_static(d, "UnityEngine.Time", "frameCount", [CORE]))
    try: s["realtime"] = float(read_static(d, "UnityEngine.Time", "realtimeSinceStartup", [CORE]))
    except Exception as e: s["realtime"] = None
    try: s["consoleFlags"] = int(read_static(d, "UnityEditor.LogEntries", "consoleFlags", EDITOR_ASM))
    except Exception: s["consoleFlags"] = None
    try: s["isPlaying"] = bool(read_static(d, "UnityEditor.EditorApplication", "isPlaying", EDITOR_ASM))
    except Exception: s["isPlaying"] = None
    s["scenes"] = list(d.get_all_loaded_scenes())
    return s

def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16] if os.path.exists(p) else None
def save_equal():
    return all(sha(os.path.join(SAVE_DIRS[k], f)) == sha(os.path.join(BK, k, f)) for k in SAVE_DIRS for f in ("save.chop", "save.chop.bak"))
def restore_save():
    for k, dst in SAVE_DIRS.items():
        for f in ("save.chop", "save.chop.bak"):
            s = os.path.join(BK, k, f)
            if os.path.exists(s): shutil.copy2(s, os.path.join(dst, f))
    return save_equal()

# ---- окно Unity и клавиши (только клавиатура) ----
u32 = ctypes.windll.user32; k32 = ctypes.windll.kernel32
def unity_windows():
    ps = ("Get-Process Unity -ErrorAction SilentlyContinue | ForEach-Object { '{0}|{1}|{2}' -f $_.Id,$_.MainWindowHandle,$_.MainWindowTitle }")
    out = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=20).stdout.strip().splitlines()
    allp = [tuple(l.split("|", 2)) for l in out if l.strip()]
    # AssetImportWorker и др. дочерние процессы редактора окна не имеют: редакторами считаем только процессы с главным окном
    return [p for p in allp if p[1] not in ("", "0")]
def focus(h, tries=6):
    """вывести окно Unity на передний план (только клавиатура/WinAPI); несколько попыток, Alt-трюк снимает блокировку SetForegroundWindow"""
    for i in range(tries):
        fg = u32.GetForegroundWindow()
        if fg == h: return True
        cur = u32.GetWindowThreadProcessId(fg, None); tgt = u32.GetWindowThreadProcessId(h, None)
        if u32.IsIconic(h): u32.ShowWindow(h, 9)  # SW_RESTORE
        u32.keybd_event(0x12, 0, 0, 0); u32.keybd_event(0x12, 0, 2, 0)  # Alt нажать/отпустить
        u32.AttachThreadInput(cur, tgt, True)
        u32.BringWindowToTop(h); u32.SetForegroundWindow(h)
        u32.AttachThreadInput(cur, tgt, False)
        time.sleep(0.8)
        if u32.GetForegroundWindow() == h: return True
    return False
def desktop_locked():
    """True, если рабочий стол заблокирован или нет активного окна (ввод с клавиатуры невозможен)"""
    try:
        hd = u32.OpenInputDesktop(0, False, 0x0100)  # DESKTOP_SWITCHDESKTOP
        if not hd: return True
        u32.CloseDesktop(hd)
    except Exception: return True
    return u32.GetForegroundWindow() == 0
def focus_robust(h, cycles=3, tries=6, pause=20):
    """3 цикла по 6 попыток, пауза 20 с между циклами. Возвращает 'ok' / 'locked' / 'fail'"""
    for c in range(cycles):
        if desktop_locked():
            step("рабочий стол заблокирован или нет активного окна", cycle=c + 1)
            if c == cycles - 1: return "locked"
        elif focus(h, tries): return "ok"
        else: step("окно Unity не стало активным", cycle=c + 1)
        if c < cycles - 1: time.sleep(pause)
    return "locked" if desktop_locked() else "fail"
MINIMIZE_AFTER = "--keep-window" not in sys.argv  # по умолчанию после запуска Play окно Unity сворачивается
def snapshot_focus(h):
    """запомнить, что было на переднем плане и было ли окно Unity свёрнуто, чтобы вернуть всё как было"""
    return {"prev": u32.GetForegroundWindow(), "iconic": bool(u32.IsIconic(h))}
def give_back(h, st):
    """вернуть фокус прежнему окну владельца; если Unity было свёрнуто, снова свернуть БЕЗ активации (SW_SHOWMINNOACTIVE).
    Игра при свёрнутом окне идёт (runInBackground = True, проверено 24.11)."""
    try:
        if st.get("iconic") or MINIMIZE_AFTER: u32.ShowWindow(h, 7)  # свернуть без активации (по просьбе владельца окно сворачивается само после запуска)
        prev = st.get("prev")
        if prev and prev != h and u32.IsWindow(prev): u32.SetForegroundWindow(prev)
    except Exception: pass
def menu_play(h):
    """Edit > Play Mode > Play через WM_COMMAND окну Unity: без фокуса и без разворачивания окна (идея Opus 25.11).
    Возвращает True, если команда отправлена. ID пункта ищется по имени в меню, не зашит."""
    try:
        u32.GetMenu.restype = ctypes.c_void_p; u32.GetSubMenu.restype = ctypes.c_void_p
        u32.GetMenu.argtypes = [ctypes.c_void_p]; u32.GetSubMenu.argtypes = [ctypes.c_void_p, ctypes.c_int]
        u32.GetMenuItemCount.argtypes = [ctypes.c_void_p]; u32.GetMenuItemID.argtypes = [ctypes.c_void_p, ctypes.c_int]
        u32.GetMenuStringW.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_wchar_p, ctypes.c_int, ctypes.c_uint]
        def nm(menu, i):
            b = ctypes.create_unicode_buffer(256); u32.GetMenuStringW(menu, i, b, 256, 0x400)
            return b.value.replace("&", "").split("\t")[0].strip()
        def find(menu, title):
            for i in range(u32.GetMenuItemCount(menu)):
                if nm(menu, i) == title: return i
            return -1
        top = u32.GetMenu(h)
        if not top: step("menu_play: у окна нет меню"); return False
        ie = find(top, "Edit")
        if ie < 0: step("menu_play: нет меню Edit"); return False
        edit = u32.GetSubMenu(top, ie)
        ip = find(edit, "Play Mode")
        if ip < 0: step("menu_play: нет подменю Play Mode"); return False
        pm = u32.GetSubMenu(edit, ip)
        ipl = find(pm, "Play")
        if ipl < 0: step("menu_play: нет пункта Play"); return False
        cid = u32.GetMenuItemID(pm, ipl)
        if cid in (0, -1, 0xFFFFFFFF): step("menu_play: у пункта нет ID", id=cid); return False
        u32.PostMessageW(h, 0x0111, cid, 0)  # WM_COMMAND
        step("WM_COMMAND Edit>Play Mode>Play отправлен", cmd_id=cid)
        return True
    except Exception as e:
        step("menu_play: ошибка", err=type(e).__name__ + ": " + str(e)[:100]); return False
def ctrl_p():
    VK_CONTROL, VK_P, UP = 0x11, 0x50, 0x2
    u32.keybd_event(VK_CONTROL, 0, 0, 0); time.sleep(0.08)
    u32.keybd_event(VK_P, 0, 0, 0); time.sleep(0.08)
    u32.keybd_event(VK_P, 0, UP, 0); time.sleep(0.08)
    u32.keybd_event(VK_CONTROL, 0, UP, 0)

def main():
    rep["time"] = now(); rep["dry"] = DRY
    if START_ONLY:
        if game_alive(4): done(2, "--start-only: Play уже идёт (игра отвечает AltTester). Ничего не менялось.")
        wins = unity_windows(); step("окна Unity", wins=wins)
        if len(wins) != 1: done(2, "нужен ровно один Unity.exe с главным окном (найдено %d). Ничего не менялось." % len(wins))
        if CHECK or DRY: done(0, "--start-only: проверка пройдена, Play не идёт; изменений нет")
        if RESTORE: step("save.chop возвращён из копии", equal=restore_save())
        before = {"frameCount": 10 ** 9, "consoleFlags": None, "scenes": []}
        return start_phase(wins, before)
    # --- предусловия
    if not port_open(): done(2, "порт 13000 закрыт: Play не идёт или AltTester не подключён. Ничего не менялось.")
    d = driver()
    before = snapshot(d); step("до", **before)
    if before["consoleFlags"] is not None and (before["consoleFlags"] & 4): done(2, "Error Pause включена (consoleFlags %s). Выключить в Console, ничего не менялось." % before["consoleFlags"])
    if before["isPlaying"] is False: done(2, "isPlaying=False, но порт отвечает: странное состояние, ничего не менялось.")
    wins = unity_windows(); step("окна Unity", wins=wins)
    if len(wins) != 1 or wins[0][1] in ("", "0"): done(2, "нужен ровно один Unity.exe с главным окном (найдено %d). Ничего не менялось." % len(wins))
    if RESTORE and "MainMenu" not in before["scenes"] and "Gameplay" in before["scenes"]:
        step("внимание: игра в Gameplay; Stop сам перезапишет save.chop, поэтому --restore-save выполнится ПОСЛЕ остановки")
    if CHECK or DRY: done(0, "проверка предусловий пройдена; изменений нет" + (" (dry-run: Stop/Play не вызывались)" if DRY else ""))
    # --- Stop через AltTester
    try:
        d.set_static_property("UnityEditor.EditorApplication", "isPlaying", "UnityEditor.CoreModule", False)
        step("isPlaying=False отправлено")
    except Exception as e:
        step("ответ на set isPlaying не пришёл (ожидаемо, сервер гаснет)", err=type(e).__name__)
    try: d.stop()
    except Exception: pass
    t0 = time.time()
    while time.time() - t0 < 40 and game_alive(4): time.sleep(1.0)
    if game_alive(4):
        step("порт ещё открыт через 30 с: AltTester не смог остановить Play; пробую Ctrl+P как запасной Stop")
        if not focus(int(wins[0][1])): done(4, "окно Unity не стало активным, клавиша не отправлена. Play НЕ остановлен.")
        ctrl_p(); t0 = time.time()
        while time.time() - t0 < 40 and game_alive(4): time.sleep(1.0)
        if game_alive(4): done(2, "Play не остановился ни через AltTester, ни через Ctrl+P. Ничего больше не делаю.")
    step("Play остановлен (игра отключилась от AltTester)", sec=round(time.time() - t0, 1))
    time.sleep(3)  # даём редактору вернуться в Edit mode и записать сохранения
    if RESTORE:
        step("save.chop возвращён из копии", equal=restore_save())
    start_phase(wins, before)

def start_phase(wins, before):
    # --- Start: Ctrl+P
    h = int(wins[0][1]); fst = snapshot_focus(h)
    via_menu = False
    LOG = os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Unity\Editor\Editor.log")
    def log_size():
        try: return os.path.getsize(LOG)
        except Exception: return 0
    def log_tail_from(pos):
        try:
            with open(LOG, "rb") as f:
                f.seek(pos); return f.read().decode("utf-8", "replace")
        except Exception: return ""
    rep["start_path"] = None
    if "--no-menu" not in sys.argv:
        pos = log_size()
        if menu_play(h):
            rep["start_path"] = "menu"
            t0 = time.time(); last_sz = log_size(); last_change = time.time(); signs = False
            while time.time() - t0 < 120 and not via_menu:
                time.sleep(2)
                try: via_menu = game_alive(3)
                except Exception: via_menu = False
                sz = log_size()
                if sz != last_sz: last_sz = sz; last_change = time.time()
                if not signs:
                    tl = log_tail_from(pos)
                    signs = any(k in tl for k in ("Reloading Domain", "EnteredPlayMode", "Entering Playmode", "Entering playmode"))
            if not via_menu and signs:
                step("есть признаки входа в Play в Editor.log, Ctrl+P не шлю; жду ещё до 120 с")
                t1 = time.time()
                while time.time() - t1 < 120 and not via_menu:
                    time.sleep(2)
                    try: via_menu = game_alive(3)
                    except Exception: via_menu = False
                if not via_menu: done(3, "WM_COMMAND отправлен, признаки входа в Play есть, но AltTester не отвечает 240 с. Состояние неизвестно: СТОП, Ctrl+P не слался, чтобы не выключить Play.")
            elif not via_menu and time.time() - last_change < 30:
                step("Editor.log менялся в последние 30 с: Unity занят, Ctrl+P не шлю; жду ещё до 120 с")
                t1 = time.time()
                while time.time() - t1 < 120 and not via_menu:
                    time.sleep(2)
                    try: via_menu = game_alive(3)
                    except Exception: via_menu = False
                if not via_menu: done(3, "WM_COMMAND отправлен, Unity занят (лог менялся), но AltTester не отвечает. Состояние неизвестно: СТОП, Ctrl+P не слался.")
            step("после WM_COMMAND игра отвечает" if via_menu else "после WM_COMMAND нет ответа и нет признаков входа в Play; запасной путь: фокус и Ctrl+P", sec=round(time.time() - t0, 1), signs=signs)
            if not via_menu: rep["start_path"] = "ctrl_p"
    if not via_menu and rep["start_path"] is None: rep["start_path"] = "ctrl_p"
    if not via_menu:
        fr = focus_robust(h)
        if fr == "locked": give_back(h, fst); done(6, "Play остановлен, рабочий стол заблокирован: Ctrl+P НЕ отправлен. Повторить --start-only позже или нужен владелец. Мышью не лечить.")
        if fr != "ok": give_back(h, fst); done(4, "Play остановлен, но окно Unity не стало активным: Ctrl+P НЕ отправлен. Можно повторить: restart_play.py --start-only. Мышью не лечить.")
        ctrl_p(); step("Ctrl+P отправлен"); time.sleep(1.0); give_back(h, fst); step("фокус возвращён прежнему окну", was_iconic=fst["iconic"])
    # --- ждём игру
    t0 = time.time(); d2 = None; after = None
    while time.time() - t0 < 120:
        time.sleep(2)
        try:
            d2 = driver(timeout=8); after = snapshot(d2)
            if "MainMenu" in after["scenes"]: break
        except Exception as e:
            d2 = None
    if after is None:
        # НИКАКОГО повторного Ctrl+P/WM_COMMAND: это переключатель, второй раз он ВЫКЛЮЧИТ только что запущенный Play (Opus, 25.11, stage3).
        step("игра не отвечает 120 с после запуска; жду ещё до 120 с, повторных нажатий нет")
        t0 = time.time()
        while time.time() - t0 < 120 and after is None:
            time.sleep(2)
            try:
                d2 = driver(timeout=8); a = snapshot(d2)
                if "MainMenu" in a["scenes"]: after = a
            except Exception: d2 = None
    if after is None: done(3, "Ctrl+P отправлен, но через 120 с AltTester не отвечает. Состояние неизвестно: СТОП, проверить окно Unity вручную (Play мог не запуститься).")
    step("после", **after)
    time.sleep(2.0); give_back(h, fst); step("окно Unity свёрнуто повторно после старта игры (редактор сам разворачивает окно при входе в Play)" if MINIMIZE_AFTER else "окно оставлено как есть")
    if "MainMenu" not in after["scenes"]: done(5, "Play запущен, но MainMenu не найден; сцены %s" % after["scenes"])
    fresh = after["frameCount"] < MAX_FRAMES and (after["frameCount"] < before["frameCount"] or before["frameCount"] < MAX_FRAMES)
    rep["frames_before"] = before["frameCount"]; rep["frames_after"] = after["frameCount"]
    if not fresh: done(5, "frameCount %s не сброшен (<%d): перезапуск не подтверждён" % (after["frameCount"], MAX_FRAMES))
    if after["consoleFlags"] is not None and (after["consoleFlags"] & 4): done(5, "после старта включена Error Pause (%s)" % after["consoleFlags"])
    done(0, "Play перезапущен: frameCount %s -> %s, сцены %s" % (before["frameCount"], after["frameCount"], after["scenes"]))

if __name__ == "__main__":
    try: main()
    except SystemExit: raise
    except Exception as e:
        done(3 if any(s["msg"].startswith("isPlaying=False") for s in rep["steps"]) else 2, "необработанная ошибка %s: %s" % (type(e).__name__, str(e)[:200]))
