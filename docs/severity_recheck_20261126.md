# Re-check of approved known-bug assessments against scale v1.1 (26 Nov 2026)

Proposal only. Jira and Confluence were not changed; a human decides.
Basis: bug titles from `known_bugs_chopchop.csv` and the definitions and examples in `severity_priority_chopchop.md`. The bugs were not re-reproduced for this check.

| Issue | Title | Approved | Proposed | Why |
|---|---|---|---|---|
| #519 | Character stuck inside the tree | S3 / P2 | **S2 / P2** | The S2 example in the scale is this case: stuck in a tree, gets out by jumping. If jumping or a restart does not free the character, re-assess. |
| #504 | First quest area to Field Hill can be missed | S3 / P2 | **S2 / P2** | The S2 example in the scale is this case: the quest area can be skipped and reached by another path. |
| #483 | 'E' to talk does nothing in conversations | S3 / P2 | S3 / P2 | Matches the S3 example. |
| #505 | No collider on oven | S4 / P3 | S4 / P3 | Matches the S4 example. |
| #502 | Jumping into wall adds excessive speed | S4 / P3 | S4 / P3 | Noticeable defect, easy to avoid. |
| #499 | Horizontal movement is stuck on rock | S4 / P3 | S4 / P3 | Matches the S4 example if the character is released after a second. A permanent stick would be S2. |
| #518 | Loading screen does not support 21:9 screens | S5 / P4 | S5 / P4 | Cosmetic. |

Priority P2 for #519 and #504 means "S2 outside the main path". If either is on the main path, the matrix gives P1.
