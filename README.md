# AI game testing with AltTester

Automated testing of a real Unity game (**Chop Chop**, Unity Open Project #1) driven by AI models through **AltTester** (Python SDK). The work is a portfolio project: can an AI model do the routine part of game testing reliably, report honestly, assign severity and priority, and file bugs, while a human keeps the decisions?

> **Status: work in progress** (month-long project started 16 Nov 2026, last update 25 Nov 2026). Working logs and most reports are written in Russian by the project owner's choice; this README, the bug tickets and the case study draft are in English.
>
> The game itself is **not included**. Chop Chop belongs to Unity Technologies ([open-project-1](https://github.com/UnityTechnologies/open-project-1)); nothing in the game or its Unity project was modified by these tests.

## What is in this repository

| Folder | Content |
|---|---|
| `scripts/` | Python test scripts per run (`fast_run1` ... `fast_run9`), the new module-level suite (`modules`), the guard and helper libraries (`fast_run7/guard.py`, `fastlib.py`, `r4lib.py`), the scripted Stop/Play tool (`play_control`), the file-queue watcher (`queue/watcher.ps1`) |
| `reports/` | Run reports (Markdown), numeric results (JSON), selected screenshots, bug reports, the metrics summary |
| `cases/cases_state.json` | The ledger: one record per test case with verdict, run, source report, method version and a "do not repeat until" condition (50 cases) |
| `docs/` | Severity and priority scale, known game behaviours, test-case design, the module decomposition and the AltTester capability notes, audit and analysis notes |
| `task-prompts/`, `queue-task-drafts/` | The task files that were given to the AI test runner |
| `data/` | List of known upstream bugs (benchmark), collision inventory of the Beach scene |

## How it works

1. A human (or a reviewer model) writes a task file; a PowerShell watcher started by Windows Task Scheduler picks it up and runs Claude Code in the background (`claude -p`), then writes `result.json` and a log.
2. The runner reads data from the running game through the AltTester Python SDK (about 22 ms per call), presses keys, teleports the player (`Physics.autoSyncTransforms` + `Transform.position`), and compares numbers against written criteria.
3. A **guard** runs before every step: editor not paused (Console Error Pause bit read through `LogEntries.consoleFlags`), window alive, game answering, in-game pause menu closed.
4. The game save is restored from a hash-checked backup after every run.
5. Verdicts are decided by numbers in scripts (Passed / Failed / Not confirmed), not by the model's opinion. Bugs are filed in Jira after human approval, with severity S1-S5 and priority P1-P4 from a written scale.

## Results so far (24 Nov 2026)

- **Test ledger:** 50 cases: 36 passed, 3 failed (real defects), 5 observations, 1 not implemented in the game, 1 blocked by a dev-tool limit, 3 not run.
- **Bugs:** 11 filed in Jira (10 found by the AI, 1 by the owner), 8 independent root causes. Examples:
  - Beach: walking off the sea-bed edge gives an endless fall with no death or respawn (y reaches -2600).
  - Italian: all main menu buttons show `No translation found for '...' in UI Misc`.
  - Quest and dialogue state is not reliably reset after Back to menu -> New Game (wrong dialogue, `NullReferenceException` in `QuestManagerSO.cs:235`, or a hang on the last reply).
  - Cooking works (recipe 3 x Seed, dish +1) but throws a `NullReferenceException` in `UIActionButton.cs:42`.
  - Audio settings: after Save and reopen, the Music value shows in the Sound FX row.
- **Known upstream bugs** (10 chosen issues): 2 reproduced, 3 partly or weakly, 3 not reproduced, 2 not checked.
- **Speed:** a clean dialogue -> recipe -> cooking chain runs in 7 min 34 s by script.
- **Independent review:** a second model (Opus) reviewed all runs; blind severity agreement between two models: 64% exact, 82% within one level (11 bugs). A human blind rating is still pending.
- See `reports/metrics_cc31_32_33_20261124.md` and `docs/case_study_draft_20261124.md`.

## What went wrong (kept on purpose)

- 7 of 50 case verdicts and 3 of 11 filed bugs were corrected later. Causes: tool errors of my own (an in-game pause menu mistaken for a freeze, teleports that silently did nothing without `autoSyncTransforms`, key taps that were too short), a "dirty" Play session that changes game state between runs, and the editor's Error Pause mistaken for a game freeze.
- About 8 hours were lost in one run to editor pauses before the cause was found.
- The same dialogue was re-tested in 7 of 8 runs because results were not kept in one place. This led to the ledger with "do not repeat until" conditions, a clean-Play precondition and a scripted Stop/Play restart.

## Requirements to run (not included)

Unity 6000.3 with the Chop Chop project, AltTester Desktop 2.4.x with the Unity SDK, Python 3.14 with the `AltTester-Driver` package (2.4.1), Windows 11. The scripts use local absolute paths (`C:\Users\...\Test_Ai`) and a local save backup; adjust them before running.

## Notes

- Mouse control of the Unity window is deliberately not used; everything is done through the SDK, files and keyboard events.
- The AltTester Pro trial was used for the CLI; the SDK scripts are the main tool.

## License

MIT, see `LICENSE`. This covers the test scripts, reports and documents in this repository only; the Chop Chop game and the AltTester software have their own licenses.
