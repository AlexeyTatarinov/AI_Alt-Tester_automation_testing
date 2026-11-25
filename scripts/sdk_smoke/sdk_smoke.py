# -*- coding: utf-8 -*-
"""Дымовая проверка Python SDK AltTester на Chop Chop (127.0.0.1:13000)."""
import math
import sys
import time

from alttester import AltDriver, AltKeyCode, By

HOST, PORT = "127.0.0.1", 13000
PLAYER = "PigChef(Clone)"   # объект игрока (в CLI-тестах: find "PigChef(Clone)"), на нём компонент Protagonist


def pos(obj):
    return (obj.worldX, obj.worldY, obj.worldZ)


def main():
    driver = None
    try:
        driver = AltDriver(host=HOST, port=PORT, timeout=20)
        print("Подключено к %s:%d" % (HOST, PORT))
        print("Сцена:", driver.get_current_scene())

        has_player = True
        try:
            player = driver.find_object(By.NAME, PLAYER, enabled=False)
            print("Protagonist (%s) позиция: %s" % (PLAYER, tuple(round(v, 2) for v in pos(player))))
        except Exception as e:
            has_player = False
            print("Protagonist не найден (%s): игра не в уровне, шаги с игроком пропущены" % type(e).__name__)

        times = []
        for _ in range(20):
            t = time.perf_counter()
            driver.get_current_scene()
            times.append((time.perf_counter() - t) * 1000)
        print("20 вызовов get_current_scene(): среднее %.1f мс, мин %.1f мс, макс %.1f мс"
              % (sum(times) / len(times), min(times), max(times)))

        if not has_player:
            return 2
        tf = []
        for _ in range(5):
            t = time.perf_counter()
            driver.find_object(By.NAME, PLAYER, enabled=False)
            tf.append((time.perf_counter() - t) * 1000)
        print("5 вызовов find_object (get object): среднее %.1f мс, мин %.1f, макс %.1f" % (sum(tf) / 5, min(tf), max(tf)))
        t = time.perf_counter()
        driver.key_down(AltKeyCode.F12)   # безопасная клавиша: замер времени вызова key_down
        tkd = (time.perf_counter() - t) * 1000
        t = time.perf_counter()
        driver.key_up(AltKeyCode.F12)
        tku = (time.perf_counter() - t) * 1000
        print("key_down: %.1f мс, key_up: %.1f мс" % (tkd, tku))
        before = pos(driver.find_object(By.NAME, PLAYER, enabled=False))
        t = time.perf_counter()
        driver.press_key(AltKeyCode.W, power=1, duration=0.3, wait=True)   # как CLI: press W --duration 0.3
        print("press_key(W, 0.3 с, wait=True): %.0f мс" % ((time.perf_counter() - t) * 1000))
        time.sleep(0.4)
        after = pos(driver.find_object(By.NAME, PLAYER, enabled=False))
        d = math.hypot(after[0] - before[0], after[2] - before[2])
        print("Позиция до:    ", tuple(round(v, 2) for v in before))
        print("Позиция после: ", tuple(round(v, 2) for v in after))
        print("Смещение по XZ: %.2f м" % d)
        return 0
    except Exception as e:
        print("ОШИБКА: %s: %s" % (type(e).__name__, e))
        return 1
    finally:
        if driver is not None:
            try:
                driver.stop()
                print("Соединение закрыто (driver.stop())")
            except Exception as e:
                print("Ошибка при закрытии:", e)


if __name__ == "__main__":
    sys.exit(main())
