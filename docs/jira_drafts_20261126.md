# Jira drafts (26.11.2026). NOT posted; owner approval required.

## 1. CC-90: append comment
**Reproduces via Continue too (2/2).**
Path: New Game, first BardHare conversation, Back to menu, Continue, talk to BardHare/NPC.
- Sample 1 (stage3, IT-02c2): one Yes answer after Continue gave Seed 20 -> 12 (-8 instead of -1), unexpected RockCandy_Recipe, quest (0,1) -> (1,2), `save_finished` 5 instead of 2. Exceptions: 1x NullReferenceException `QuestManagerSO.EndDialogue` (`QuestManagerSO.cs:235`) via `DialogueManager.DialogueEndedAndCloseDialogueUI` (`DialogueManager.cs:167`); 21x ArgumentOutOfRangeException `DialogueManager.get__reachedEndOfLine` (`DialogueManager.cs:31`) from `OnAdvance` (`DialogueManager.cs:77`).
- Sample 2 (stage3b, E2E-02): after Continue a 2-line BardHare conversation closes but the game stays in state Dialogue (150 s). Tab and conversations do not work; movement and pause work. 0 exceptions.
- Same path, different symptom. Code: `QuestManagerSO.StartGame()` re-subscribes on every game start and unsubscribes only in `OnDisable` (`QuestManagerSO.cs:45`). A double subscription in `DialogueManager` is a hypothesis only.
Evidence: `Reports_2026-11-21/results/modules_stage3_20261125/report.md` (section 2.1), `.../modules_stage3b_20261126/report.md` (section 3).

## 2. New bug: M03-02
**Title:** Combat game state stays stuck after changing location while an enemy is alert
Steps: New Game; get to the Mountain_Cave exit with an enemy alert active (Count 1, state Combat); walk into the `LocationExit` (`MountainCave_MountainPath_BottomExit`).
Expected: after the scene change the alert list is empty and the state is Gameplay.
Actual (stage4): in Mountain_Path there are 0 enemies, but state stays Combat and `_alertEnemies.Count` stays 1 for at least 15 s (last reading ~50 s after the transition). Tab does not open the inventory. W and Esc work. 0 exceptions, HP 50 -> 50. Reading the list gives "The object of type 'UnityEngine.Transform' has been destroyed": a reference to an object of the unloaded scene stays in the list. (Earlier runs, stage1b/stage2, also saw: cheat menu not opening and conversations blocked in this state; Back to menu -> New Game clears it.)
Cause (code reading + counts): `GameStateSO._alertEnemies`; Gameplay returns only when the list is empty (`GameStateSO.cs:44-52`); an enemy destroyed on scene change is never removed. Count was 0 before the test alert.
Reproduced: 1/1 (`Reports_2026-11-21/results/modules_stage4_20261126/report.md`). Caveats: the alert was triggered by a test teleport 3 m before the exit trigger, then the exit was entered on foot; the alert source is not identified; chase was not shown. The owner can re-check by hand in a minute: approach an enemy and walk into the exit.
Note: in the Editor the ScriptableObject list also survives Stop/Play (counts 4-5 at Play start, 0 after an editor restart); likely editor-only, not verified in a build.

## 3. IT-10 (minor / UX), compare with CC-86 and CC-89 first to avoid a duplicate
**Title:** Master volume is not saved if Language tab is opened before Save
Steps: Pause -> Settings -> Audio, lower Master volume; open Language tab, change language, Save. Result: language saved, volume back to 1.0. Saving on the Audio tab first keeps the volume and it survives Continue. Maybe by design.

## 4. Labels / components
Proposal from `modules-decomposition-2026-11-25.md`, section 6: component = module (M01..M19), labels = `continue-flow`, `dialogue`, `combat-state`, `settings`. Owner decides.
