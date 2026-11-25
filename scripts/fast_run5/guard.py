# -*- coding: utf-8 -*-
"""guard.py: страховки от паузы Unity (CC-83). Игру и проект не меняет, Unity не запускает и не сворачивает.
Читает только Editor.log, процесс Unity и (только на чтение) LogEntries.consoleFlags.
Ctrl+Shift+P из этого модуля НЕ отправляется: запасной вариант делает Claude через computer use (см. stall_action),
модуль считает попытки (не более 2 за прогон) и пишет отчёт остановки.
Подключение: `import time, guard` (fastlib.case() уже вызывает before_case / after_case)."""
import os, re, json, time, socket, subprocess, datetime, shutil

EDLOG = r"C:\Users\Aotat\AppData\Local\Unity\Editor\Editor.log"
RES = "C:/Users/Aotat/Desktop/Test_Ai/Reports_2026-11-21/results/run5_new3_20261123"
STATE_F = os.path.join(RES, "run5_state.json")
STALL_F = os.path.join(RES, "stall_report.json")
TAILS = os.path.join(RES, "log_tails")
SHOTS = os.path.join(RES, "shots")
os.makedirs(TAILS, exist_ok=True); os.makedirs(SHOTS, exist_ok=True)
MAX_UNPAUSE = 2
EDITOR_ASM = ("UnityEditor.CoreModule", "UnityEditor", "UnityEditor.dll")


class Paused(Exception):
    """игра стоит (пауза редактора или блокировка); .report содержит классификацию"""
    def __init__(self, report):
        super().__init__(report.get("klass", "?")); self.report = report


class ErrorPauseOn(Exception):
    pass


def now(): return datetime.datetime.now().strftime("%H:%M:%S")

def _state():
    try: return json.load(open(STATE_F, encoding="utf-8"))
    except Exception: return {}

def _save_state(s):
    json.dump(s, open(STATE_F, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


# ---------------- процесс и окно Unity ----------------
_PS_WIN = r'''
Add-Type -AssemblyName System.Drawing
Add-Type -Namespace W -Name P -MemberDefinition '[DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint f); [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r); [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h); [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow(); public struct RECT{public int L,T,R,B;}'
$p = Get-Process Unity -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
if (-not $p) { '{"found": false}'; exit }
$c0 = $p.CPU; Start-Sleep -Milliseconds 1500; $p.Refresh()
$info = @{found=$true; pid=$p.Id; responding=$p.Responding; cpu_delta_1_5s=[math]::Round($p.CPU-$c0,3); title=$p.MainWindowTitle;
  iconic=[W.P]::IsIconic($p.MainWindowHandle); foreground=([W.P]::GetForegroundWindow() -eq $p.MainWindowHandle)}
$shot = $env:GUARD_SHOT
if ($shot -and -not $info.iconic) {
  $r = New-Object W.P+RECT; [W.P]::GetWindowRect($p.MainWindowHandle, [ref]$r) | Out-Null
  $bmp = New-Object Drawing.Bitmap ($r.R-$r.L), ($r.B-$r.T); $g = [Drawing.Graphics]::FromImage($bmp); $dc = $g.GetHdc()
  [W.P]::PrintWindow($p.MainWindowHandle, $dc, 2) | Out-Null; $g.ReleaseHdc($dc); $bmp.Save($shot); $info.shot = $shot
}
$info | ConvertTo-Json -Compress
'''

def unity_window(shot_name=None):
    """процесс/окно Unity и (по желанию) снимок окна через PrintWindow. Окно не трогает."""
    env = dict(os.environ)
    if shot_name: env["GUARD_SHOT"] = os.path.join(SHOTS, shot_name + ".png")
    else: env.pop("GUARD_SHOT", None)
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command", _PS_WIN], capture_output=True, text=True, timeout=30, env=env).stdout.strip()
        return json.loads(out.splitlines()[-1])
    except Exception as e:
        return {"found": None, "error": "%s: %s" % (type(e).__name__, str(e)[:100])}


# ---------------- Editor.log ----------------
def log_mark():
    return os.path.getsize(EDLOG) if os.path.exists(EDLOG) else 0

def log_tail_lines(n=5, bytes_=20000):
    try:
        with open(EDLOG, "rb") as f:
            f.seek(max(0, os.path.getsize(EDLOG) - bytes_))
            txt = f.read().decode("utf-8", "replace")
        return [l[:200] for l in txt.splitlines() if l.strip() and "audio listener" not in l][-n:]
    except Exception:
        return []

_ERR = re.compile(r"(?i)(\b[A-Za-z0-9_.]*Exception\b|while executing '|can only be called on an active agent|Problem detected while opening|Missing Prefab|^\s*error\b|\[error\])")
_RECV = re.compile(r'AltTester\|DEBUG\|command received: (\{.*)')
_SENT = re.compile(r'AltTester\|DEBUG\|response sent')

def classify(offset, block=8_000_000):
    """сканирует Editor.log с конца блоками до точки отсчёта (спам про audio listener пропускается).
    Находит: последнюю команду драйвера без ответа, последний ответ, последнюю строку уровня Error/Exception.
    klass: 'пауза редактора' (самое новое событие AltTester - «command received» без «response sent») / 'причина неизвестна'."""
    first = None          # что встретилось раньше при обходе с конца: 'recv' или 'sent'
    recv_line = None; last_err = None
    try:
        size = os.path.getsize(EDLOG); lo = offset if offset <= size else 0
        pos = size
        with open(EDLOG, "rb") as f:
            while pos > lo and (first is None or last_err is None):
                start = max(lo, pos - block); f.seek(start)
                lines = f.read(pos - start).decode("utf-8", "replace").splitlines()
                for l in reversed(lines):
                    if "audio listener" in l or not l.strip(): continue
                    if first is None:
                        m = _RECV.search(l)
                        if m and '"messageId":null' not in m.group(1).replace(" ", ""):
                            first = "recv"; recv_line = l[:200]
                        elif _SENT.search(l):
                            first = "sent"
                    if last_err is None and _ERR.search(l) and "AltTester|" not in l and not l.startswith(("UnityEngine.", "System.", "NLog.", "AltTester.", "AltWebSocketSharp.", "  at ")):
                        last_err = l.strip()[:220]
                    if first is not None and last_err is not None: break
                pos = start
    except Exception as e:
        return {"klass": "причина неизвестна", "error": "лог не читается: %s" % e}
    paused = first == "recv"
    return {"klass": "пауза редактора" if paused else "причина неизвестна", "recv_without_sent": paused,
            "last_command_received": recv_line, "last_error": last_err,
            "probable_cause": ("вероятная причина: " + last_err) if last_err else "ошибок после точки отсчёта в логе нет",
            "log_size": os.path.getsize(EDLOG) if os.path.exists(EDLOG) else None}

def save_log_tail(label, lines=300):
    """копия хвоста Editor.log (последние ~lines строк без спама про audio listener) в папку результатов"""
    p = os.path.join(TAILS, "%s_%s.txt" % (datetime.datetime.now().strftime("%H%M%S"), re.sub(r"[^\w.-]+", "_", label)))
    try:
        with open(EDLOG, "rb") as f:
            f.seek(max(0, os.path.getsize(EDLOG) - 3_000_000))
            txt = f.read().decode("utf-8", "replace").splitlines()
        txt = [l for l in txt if "audio listener" not in l]
        open(p, "w", encoding="utf-8").write("\n".join(txt[-lines:]))
    except Exception as e:
        open(p, "w", encoding="utf-8").write("не удалось: %s" % e)
    return p


# ---------------- SDK: проба и preflight ----------------
def port_open(host="127.0.0.1", port=13000, t=3.0):
    try:
        with socket.create_connection((host, port), timeout=t): return True
    except Exception:
        return False

SHARED = None   # основной драйвер сценария: второе подключение к 13000 даёт NoAppConnected, поэтому проба идёт через него

def _probe_driver():
    if SHARED is not None: return SHARED
    from alttester import AltDriver
    return AltDriver(host="127.0.0.1", port=13000, enable_logging=False, timeout=5)

def frames(drv, core="UnityEngine.CoreModule"):
    return drv.get_static_property("UnityEngine.Time", "frameCount", core)

def _alive(wait=1.0, limit=5.0):
    """проба «живости»: frameCount, пауза wait с, снова. Растёт - жива. Не изменился за limit с - стоит.
    Возвращает (bool, подробности). Использует отдельное подключение с тайм-аутом 5 с."""
    t0 = time.time()
    try:
        drv = _probe_driver()
    except Exception as e:
        return False, "подключение не удалось: %s" % type(e).__name__
    try:
        a = frames(drv); time.sleep(wait)
        while True:
            b = frames(drv)
            if b != a: return True, "frameCount %s -> %s" % (a, b)
            if time.time() - t0 > limit: return False, "frameCount не меняется %.0f с (%s)" % (time.time() - t0, a)
            time.sleep(0.5)
    except Exception as e:
        return False, "%s" % type(e).__name__
    finally:
        if drv is not SHARED:
            try:
                if drv is not SHARED: drv.stop()
            except Exception: pass

def _read_flags():
    """только чтение UnityEditor.LogEntries.consoleFlags. Возвращает (значение|None, как прочиталось)"""
    drv = None
    try:
        drv = _probe_driver()
    except Exception as e:
        return None, "нет подключения: %s" % type(e).__name__
    notes = []
    try:
        for asm in EDITOR_ASM:
            try:
                v = drv.get_static_property("UnityEditor.LogEntries", "consoleFlags", asm)
                return int(v), "прочиталось (assembly %s)" % asm
            except Exception as e:
                notes.append("%s: %s" % (asm, type(e).__name__))
        return None, "не читается (%s)" % "; ".join(notes)
    finally:
        try:
            if drv is not SHARED: drv.stop()
        except Exception: pass

def _is_play():
    try:
        drv = _probe_driver()
        try:
            for asm in EDITOR_ASM:
                try: return bool(drv.get_static_property("UnityEditor.EditorApplication", "isPlaying", asm)), "isPlaying прочитан"
                except Exception: pass
            return bool(drv.get_all_loaded_scenes()), "по сценам (isPlaying не читается)"
        finally:
            try:
                if drv is not SHARED: drv.stop()
            except Exception: pass
    except Exception as e:
        return False, type(e).__name__

def preflight(label="run"):
    """до первого кейса. Возвращает словарь; бросает ErrorPauseOn, если Error Pause включена."""
    st = _state(); r = {"time": now(), "label": label}
    r["port_13000"] = port_open()
    r["window"] = unity_window("preflight_%s" % label)
    flags, how = read_console_flags()
    r["consoleFlags"] = flags; r["consoleFlags_note"] = how
    r["error_pause"] = None if flags is None else bool(flags & 4)
    r["play"] = is_play()
    r["log_offset"] = log_mark(); r["log_last_lines"] = log_tail_lines(5)
    ok, det = alive(); r["alive"] = ok; r["alive_detail"] = det
    st["preflight"] = r; st["guard_offset"] = r["log_offset"]; st.setdefault("unpause_attempts", 0)
    _save_state(st)
    if r["error_pause"]:
        raise ErrorPauseOn("Error Pause включена, выключите кнопку в Console")
    return r


# ---------------- остановка: отчёт и запасной вариант ----------------
def stall_report(case_id="", offset=None, why=""):
    """классификатор + снимок окна + состояние процесса; пишет stall_report.json и копию хвоста лога.
    Возвращает отчёт. Ничего не нажимает."""
    st = _state()
    off = st.get("guard_offset", 0) if offset is None else offset
    rep = {"time": now(), "case": case_id, "why": why}
    rep.update(classify(off))
    rep["window"] = unity_window("stall_%s_%s" % (re.sub(r"\W+", "_", case_id or "x"), datetime.datetime.now().strftime("%H%M%S")))
    rep["log_tail_copy"] = save_log_tail("stall_" + (case_id or "x"))
    rep["unpause_attempts_used"] = st.get("unpause_attempts", 0)
    allrep = []
    try: allrep = json.load(open(STALL_F, encoding="utf-8"))
    except Exception: pass
    allrep.append(rep); json.dump(allrep, open(STALL_F, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return rep

def unpause_budget():
    """сколько попыток Ctrl+Shift+P (computer use) осталось в этом прогоне"""
    return MAX_UNPAUSE - _state().get("unpause_attempts", 0)

def note_unpause_attempt(result=""):
    """вызывать после КАЖДОЙ нажатой комбинации (делает Claude через computer use): считает попытки, пишет в состояние"""
    st = _state(); st["unpause_attempts"] = st.get("unpause_attempts", 0) + 1
    st.setdefault("unpause_log", []).append({"time": now(), "result": result}); _save_state(st)
    return MAX_UNPAUSE - st["unpause_attempts"]

def before_case(case_id):
    """проба «живости» перед шагом; если стоит - классификатор и исключение Paused"""
    ok, det = alive()
    t0 = time.time()
    # NoAppConnected / обрыв связи после загрузки сцены - не пауза: ждём до 90 с, пока игра переподключится
    while not ok and ("NoAppConnected" in det or "Connection" in det) and time.time() - t0 < 90:
        time.sleep(3.0); ok, det = alive()
    if not ok:
        raise Paused(stall_report(case_id, why="перед кейсом: " + det))
    return det

def after_case(case_id, status, note=""):
    """heartbeat в run5_state.json: время, номер кейса, статус"""
    st = _state(); st["heartbeat"] = {"time": now(), "ts": time.time(), "case": case_id, "status": status, "note": str(note)[:200]}
    st.setdefault("heartbeats", []).append(st["heartbeat"]); st["heartbeats"] = st["heartbeats"][-200:]
    _save_state(st)

def risky(name):
    """перед рисковым шагом (ошибки: Q, Space в диалоге, Forest, MainMenu): чекпойнт состояния"""
    import hashlib
    st = _state(); h = {}
    for sd in (r"C:\Users\Aotat\AppData\LocalLow\Unity Technologies\Chop Chop", r"C:\Users\Aotat\AppData\LocalLow\Unity Open Projects\Chop Chop"):
        p = os.path.join(sd, "save.chop")
        h[p] = hashlib.sha256(open(p, "rb").read()).hexdigest()[:16] if os.path.exists(p) else None
    st["risky_checkpoint"] = {"time": now(), "step": name, "log_size": log_mark(), "save_hashes": h}
    _save_state(st)

def end_block(label):
    """в конце блока: копия хвоста Editor.log (~300 строк)"""
    p = save_log_tail("block_" + label); after_case("block:" + label, "end", p); return p


# ---------- жёсткий тайм-аут для проб: на паузе вызов SDK (и подключение) может висеть дольше заявленных 5 с ----------
import threading

def _hard(fn, t, default, *a):
    box = {}
    def run():
        try: box["v"] = fn(*a)
        except Exception as e: box["v"] = default if not isinstance(default, tuple) else (default[0], "%s: %s" % (type(e).__name__, str(e)[:80]))
    th = threading.Thread(target=run, daemon=True); th.start(); th.join(t)
    return box["v"] if "v" in box else default

def alive(wait=1.0, limit=5.0):
    """(bool, подробности); на всё не более limit+6 с"""
    return _hard(_alive, limit + 6, (False, "проба не завершилась за %.0f с (SDK не отвечает)" % (limit + 6)), wait, limit)

def read_console_flags():
    return _hard(_read_flags, 25, (None, "не читается (SDK не ответил за 25 с)"))

def is_play():
    return _hard(_is_play, 15, (False, "не определено (SDK не ответил за 15 с)"))



# ================= GUARD-01 (прогон 3): «замороженный» игрок не даёт «Passed» =================
MIN_APPROACH_M = 0.3      # шаг подхода обязан сдвинуть игрока минимум на 0,3 м (XZ)
SLIDING_LIMIT_S = 3.0     # Sliding дольше этого помечается флагом
PASS_WORDS = ("Пройдено", "PASS", "Passed")

class SlideWatch:
    """накапливает непрерывное время в состоянии Sliding; flag=True, если оно > SLIDING_LIMIT_S"""
    def __init__(self): self.since = None; self.max_s = 0.0; self.flag = False
    def tick(self, state, t=None):
        t = time.time() if t is None else t
        if state == "Sliding":
            if self.since is None: self.since = t
            self.max_s = max(self.max_s, t - self.since)
            if self.max_s > SLIDING_LIMIT_S: self.flag = True
        else:
            self.since = None
        return self.flag

def judge(verdict, moved_m, slide=None):
    """итоговый вердикт: если шаг подхода сдвинул < 0,3 м, «Passed» заменяется на «Invalid» (кейс не засчитан)"""
    inv = moved_m is None or moved_m < MIN_APPROACH_M
    out = verdict
    if inv and any(w in str(verdict) for w in PASS_WORDS): out = "Invalid"
    return {"verdict": out, "approach_moved_m": None if moved_m is None else round(moved_m, 2), "invalid_frozen": inv,
            "sliding_gt3s": bool(slide.flag) if slide else False, "sliding_max_s": round(slide.max_s, 1) if slide else 0.0}
