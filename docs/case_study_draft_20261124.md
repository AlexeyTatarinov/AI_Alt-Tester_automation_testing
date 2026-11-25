# Case study draft (CC-34): Can an AI model test a real Unity game?

Draft of 24 Nov 2026. Numbers marked (TBD) wait for the owner: manual time and the human blind severity rating. Source of every number: `Reports_2026-11-21/metrics_cc31_32_33_20261124.md` and the run reports.

## Problem
Manual game testing is repetitive. The question: can an AI model do the routine part reliably, report honestly and leave the decisions to a human?

## Setup
Chop Chop (Unity Open Project #1, Unity 6000.3), driven through the AltTester Python SDK (about 22 ms per call). Claude models run the tests: Sonnet in background runs started from a file queue, Opus for a review of the whole process. Results go to Jira (project CC) and Confluence. The game and the Unity project are never modified; every run starts and ends from the same saved game (hash checked).

## Method
Data first, walking only to confirm. One script per suite. Verdicts are decided by numbers in scripts (Passed / Failed / Not confirmed), not by the model's opinion. A guard script checks before every step that the editor is not paused, the window is alive and the game answers. Bugs are filed only after human approval; severity and priority follow a written S1-S5 / P1-P4 scale.

## Results (24 Nov, nine automated runs plus regression)
- 50 test cases in a ledger: 36 passed, 3 failed (real defects), 5 observations, 1 not implemented in the game, 1 blocked by a dev-tool limit, 3 not run.
- 11 bugs in Jira: 10 found by the AI, 1 by the owner; 8 independent root causes. Examples: endless fall off the edge of Beach with no respawn; Italian main menu showing "No translation found"; exceptions in the quest and dialogue code; an exception while cooking although the dish is cooked.
- Known upstream bugs (10 chosen issues): 2 reproduced, 3 partly or weakly, 3 not reproduced, 2 not checked.
- Time: a clean dialogue-to-cooking chain runs in 7 min 34 s by script; manual time for the same cases (TBD).
- Severity agreement: AI against an independent AI (Opus, blind) 64% exact, 82% within one level; human against AI (TBD).

## What went wrong (the honest part)
1. 7 of 50 case verdicts and 3 of 11 filed bugs were later corrected. Causes: our own method errors (an in-game pause menu mistaken for a freeze, teleports that silently did nothing, key taps too short), a "dirty" Play session that changes game state between runs, and the editor's Error Pause mistaken for a game freeze.
2. About 8 hours were lost in one run to editor pauses before the cause was found and a preflight check was added.
3. The same dialogue was re-tested in 7 of 8 runs because results were not kept in one ledger. The fix: a single case ledger with "do not repeat until" conditions, a clean-Play precondition and a scripted Stop/Play restart.

## What it shows
The AI is fast and tireless at routine checks and at turning logs into structured reports, and it finds real defects. It is not reliable alone: it needs written rules, numeric criteria, a guard against its own tooling errors and a human (or a stronger model) who reviews verdicts and severity.

## Next step
Second game or engine, deeper coverage of combat and save/load, a regression suite after the quest-state bug is fixed.
