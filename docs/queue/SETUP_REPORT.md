# Настройка очереди заданий — 23.11.2026

## Итог
Очередь работает. Самопроверка пройдена 23.11.2026 16:41 после входа владельца в CLI: `ping_20261123b.md` → `done\`, создан `done\ping_ok.txt` («связь есть»), `result.json` с exit_code 0, heartbeat идёт. (Первая попытка 11:32 упала на «Not logged in», это уже решено.)

## Что сделано
- CLI: `npm install -g @anthropic-ai/claude-code`, версия **2.1.330**, путь `C:\Users\Aotat\AppData\Roaming\npm\claude.cmd`. Предупреждение npm о postinstall-скрипте пакета не блокировало работу (`claude --version` отвечает).
- Папки: `queue\inbox, running, done, failed, logs`, схема в `queue\README.md`.
- Наблюдатель: `scripts\queue\watcher.ps1` (опрос 15 с, самый старый *.md, lock `queue\watcher.lock`, тайм-аут 120 мин, heartbeat 30 с `queue\watcher_heartbeat.json`, `result.json`, логи в `queue\logs`).
- Задача Task Scheduler `TestAi_QueueWatcher`: при входе пользователя + повтор каждые 5 мин, без дублей (IgnoreNew и lock), окно скрыто, обычные права. Запущена, State=Running.

## Самопроверка (ping_20261123.md)
- Прошло: файл взят из inbox, перенесён в running, затем в failed, создан `ping_*.result.json` и лог, heartbeat идёт (idle).
- Не прошло: `claude -p` ответил «Not logged in», файл `done\ping_ok.txt` не создан.
- Ошибка в `exit_code` (был null) исправлена, наблюдатель перезапущен. Повторно ping не клала: без входа он снова упадёт.

## Что нужно от владельца
Один раз выполнить в обычной консоли: `claude`, затем `/login` и войти в аккаунт (пароли я не ввожу). После этого положить ping в `queue\inbox` или сказать мне, я повторю самопроверку.

## Как остановить
```
Disable-ScheduledTask -TaskName TestAi_QueueWatcher; Stop-ScheduledTask -TaskName TestAi_QueueWatcher
```
Наблюдатель при этом завершается (lock снимется сам). Полностью удалить: `Unregister-ScheduledTask -TaskName TestAi_QueueWatcher -Confirm:$false`.

## Ограничения
- Запускает `claude -p --dangerously-skip-permissions`: ограничения держатся только в тексте файлов-заданий.
- Работает, пока вы вошли в Windows (задача Interactive).
- Задание выполняется до 120 минут, одно за раз.
- Пока Unity-прогон идёт в окне приложения, второй Claude через очередь может мешать (общие файлы Test_Ai).
