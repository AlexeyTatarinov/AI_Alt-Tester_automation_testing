# Очередь заданий для Claude Code

Схема: файл-задание `*.md` кладут в `queue\inbox\`. Наблюдатель (`scripts\queue\watcher.ps1`, задача Task Scheduler `TestAi_QueueWatcher`) раз в 15 с берёт самый старый файл, переносит в `running\` и запускает из `Test_Ai` команду `claude -p ... --dangerously-skip-permissions`. Весь вывод идёт в `logs\<имя>_<дата-время>.log`. Тайм-аут 120 минут.
После завершения файл уходит в `done\` (код выхода 0) или `failed\`, рядом лежит `<имя>.result.json` {task, started, finished, exit_code, timed_out, log}.
`watcher_heartbeat.json` обновляется каждые 30 с: {time, state: idle|running, current_task}. Один запуск за раз (`watcher.lock`). Другие расширения в inbox игнорируются (запись в лог).
Ограничения безопасности задаются в самих файлах-заданиях. Наблюдатель работает только внутри Test_Ai.
