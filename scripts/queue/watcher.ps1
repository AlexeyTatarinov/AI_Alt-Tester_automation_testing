# Наблюдатель очереди заданий Test_Ai. Только PowerShell, без внешних модулей.
$ErrorActionPreference = "Continue"
$Root   = "C:\Users\Aotat\Desktop\Test_Ai"
$Q      = Join-Path $Root "queue"
$Inbox  = Join-Path $Q "inbox"; $Run = Join-Path $Q "running"; $Done = Join-Path $Q "done"; $Fail = Join-Path $Q "failed"; $Logs = Join-Path $Q "logs"
$Lock   = Join-Path $Q "watcher.lock"
$HB     = Join-Path $Q "watcher_heartbeat.json"
$WLog   = Join-Path $Logs "watcher.log"
$Claude = Join-Path $env:APPDATA "npm\claude.cmd"
$TimeoutMin = 120
foreach ($d in $Inbox,$Run,$Done,$Fail,$Logs) { if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d | Out-Null } }
function Log($m) { Add-Content -Path $WLog -Value ("[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $m) -Encoding UTF8 }
function Beat($state, $task) {
    $o = [ordered]@{ time = (Get-Date).ToString("s"); state = $state; current_task = $task }
    ($o | ConvertTo-Json) | Set-Content -Path $HB -Encoding UTF8
}
# lock: если владелец жив - выходим, если мёртв - снимаем
if (Test-Path $Lock) {
    $old = (Get-Content $Lock -ErrorAction SilentlyContinue | Select-Object -First 1) -as [int]
    if ($old -and (Get-Process -Id $old -ErrorAction SilentlyContinue)) { exit 0 }
    Remove-Item $Lock -Force -ErrorAction SilentlyContinue
    Log "снят устаревший lock (pid $old)"
}
Set-Content -Path $Lock -Value $PID -Encoding ASCII
Log "наблюдатель запущен, pid $PID"
$lastBeat = Get-Date "2000-01-01"; $curTask = $null; $warned = @{}
try {
    while ($true) {
        if (((Get-Date) - $lastBeat).TotalSeconds -ge 30) { Beat "idle" $null; $lastBeat = Get-Date }
        $items = Get-ChildItem $Inbox -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime
        foreach ($o in ($items | Where-Object { $_.Extension -ne ".md" })) {
            if (-not $warned[$o.Name]) { Log ("игнорирую не .md файл: " + $o.Name); $warned[$o.Name] = $true }
        }
        $f = $items | Where-Object { $_.Extension -eq ".md" } | Select-Object -First 1
        if ($f) {
            $name = $f.BaseName
            $dst = Join-Path $Run $f.Name
            Move-Item -Path $f.FullName -Destination $dst -Force
            $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
            $log = Join-Path $Logs ("{0}_{1}.log" -f $name, $stamp)
            $started = Get-Date; $curTask = $f.Name
            Beat "running" $curTask; Log ("старт: " + $f.Name)
            $prompt = "Прочитай файл $dst и выполни задание из него полностью. Все правила и ограничения в файле обязательны."
            $errLog = $log + ".err"
            $timedOut = $false; $code = -1
            try {
                $p = Start-Process -FilePath $Claude -ArgumentList @("-p", ('"' + $prompt + '"'), "--dangerously-skip-permissions", "--model", "sonnet", "--output-format", "json") `
                     -WorkingDirectory $Root -WindowStyle Hidden -PassThru `
                     -RedirectStandardOutput $log -RedirectStandardError $errLog
                $null = $p.Handle
                $deadline = $started.AddMinutes($TimeoutMin)
                while (-not $p.HasExited) {
                    if ((Get-Date) -gt $deadline) { $timedOut = $true; break }
                    if (((Get-Date) - $lastBeat).TotalSeconds -ge 30) { Beat "running" $curTask; $lastBeat = Get-Date }
                    Start-Sleep -Seconds 2
                }
                if ($timedOut) { & taskkill.exe /PID $p.Id /T /F | Out-Null; $code = -2 }
                else { $p.WaitForExit(); $code = $p.ExitCode }
            } catch { Log ("ошибка запуска: " + $_.Exception.Message); $code = -3 }
            # учёт расхода: разбор JSON-вывода claude и запись строки в queue\usage_log.csv
            try {
                $UL = Join-Path $Q "usage_log.csv"
                if (-not (Test-Path $UL)) {
                    Set-Content -Path $UL -Encoding UTF8 -Value "task,started,finished,duration_s,exit_code,model,num_turns,input_tokens,output_tokens,cache_creation_tokens,cache_read_tokens,total_tokens,cost_usd"
                }
                $j = $null
                if (Test-Path $log) { $raw = Get-Content $log -Raw -Encoding UTF8; if ($raw) { try { $j = $raw | ConvertFrom-Json } catch { $j = $null } } }
                $dur = [math]::Round(((Get-Date) - $started).TotalSeconds)
                if ($j -and $j.usage) {
                    $in = [int]$j.usage.input_tokens; $out = [int]$j.usage.output_tokens
                    $cc = [int]$j.usage.cache_creation_input_tokens; $cr = [int]$j.usage.cache_read_input_tokens
                    $mdl = ""; if ($j.modelUsage) { $mdl = (($j.modelUsage.PSObject.Properties.Name) -join "|") }
                    $row = "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12}" -f $f.Name, $started.ToString("s"), (Get-Date).ToString("s"), $dur, $code, $mdl, $j.num_turns, $in, $out, $cc, $cr, ($in+$out+$cc+$cr), $j.total_cost_usd
                } else {
                    $row = "{0},{1},{2},{3},{4},,,,,,,," -f $f.Name, $started.ToString("s"), (Get-Date).ToString("s"), $dur, $code
                }
                Add-Content -Path $UL -Value $row -Encoding UTF8
                Log ("usage записан: " + $row)
            } catch { Log ("ошибка учёта usage: " + $_.Exception.Message) }
            if (Test-Path $errLog) { Add-Content -Path $log -Value "`n--- stderr ---" -Encoding UTF8; Get-Content $errLog -ErrorAction SilentlyContinue | Add-Content -Path $log -Encoding UTF8; Remove-Item $errLog -Force -ErrorAction SilentlyContinue }
            $finished = Get-Date
            $target = if ($code -eq 0 -and -not $timedOut) { $Done } else { $Fail }
            Move-Item -Path $dst -Destination (Join-Path $target $f.Name) -Force
            $res = [ordered]@{ task = $f.Name; started = $started.ToString("s"); finished = $finished.ToString("s"); exit_code = $code; timed_out = $timedOut; log = $log }
            ($res | ConvertTo-Json) | Set-Content -Path (Join-Path $target ($name + ".result.json")) -Encoding UTF8
            Log ("конец: {0}, код {1}, тайм-аут {2}" -f $f.Name, $code, $timedOut)
            $curTask = $null; Beat "idle" $null; $lastBeat = Get-Date
        } else { Start-Sleep -Seconds 15 }
    }
} finally {
    if ((Get-Content $Lock -ErrorAction SilentlyContinue | Select-Object -First 1) -eq "$PID") { Remove-Item $Lock -Force -ErrorAction SilentlyContinue }
}
