# -*- coding: utf-8 -*-
"""Готовит слепой экспорт для CC-31: форма для человека (без оценок ИИ и без Jira-ключей) и запечатанные оценки ИИ с хешем."""
import json, hashlib, html, os
D = r"Test_Ai\Reports_2026-11-21\severity_blind_20261124"
os.makedirs(D, exist_ok=True)
bugs = [
 ("CC-67", "New Game writes a console warning \"The player tried to spawn in an LocationEntry that doesn't exist, returning the default one.\" on every start (3 times per session).",
  "Steps: Play from MainMenu, click New Game, confirm, wait until the player appears on Beach, look at the Console.",
  "Actual: the warning is logged; the player still spawns at the default spawn point (0.00 m off), gameplay is not affected. Expected: no warning. Seen 2 of 2 runs.", ("S5", "P4")),
 ("CC-81", "Pressing Q while a BardHare dialogue is open throws NullReferenceException in the InventoryActionButton input callback; the owner reported that the game stopped responding until Pause was pressed in the Editor.",
  "Steps: New Game, go to BardHare, press E, press Q while the dialogue window is open.",
  "Actual: exception in the Console; the owner saw a freeze (once, manually). Expected: Q ignored in dialogue. Not reproduced by the automated check (0 exceptions, no freeze).", ("S3", "P3")),
 ("CC-82", "Beach: walking off the edge of the sea-bed floor leads to an endless fall with no death or respawn.",
  "Steps: New Game, walk west along the sea bed (about -29 m) roughly 60 m from the spawn and keep walking off the floor edge.",
  "Actual: the player falls without limit (y reaches -2600 m in about 85 s), no death, no respawn, no exception; the game must be restarted. Reachable on foot, but the edge is on the sea bed (not an obvious route). Expected: kill zone or invisible wall (Town_Market has a FallCatcher, Beach has none). Seen on 3 edges (west, east, south), every time.", ("S2", "P2")),
 ("CC-84", "NullReferenceException when attacking (F) while falling into the FallCatcher_Lake death zone in Town_Market.",
  "Steps: load Town_Market, fall into FallCatcher_Lake, press F three times while falling.",
  "Actual: 1 NullReferenceException in the Console (FallCatcher.cs line 13); the game keeps running. Expected: no exception. Reproduced once by script, not manually.", ("S4", "P3")),
 ("CC-85", "A large red \"PLACEHOLDER\" text stays on a black screen for 12+ seconds after every New Game.",
  "Steps: MainMenu -> New Game; watch the screen after Beach loads.",
  "Actual: 0.1-0.6 s after Beach loads, the red text appears on black and stays for 12+ s, then disappears. Seen 5 of 5. Expected: no unfinished placeholder visible to the player. The owner said it is the current state of the game.", ("S4", "P3")),
 ("CC-86", "Missing translations: Italian Settings screen, French inventory item names/descriptions, empty text in inventory.",
  "Steps: Settings -> Language -> italiano or francais, then look at Settings and the inventory.",
  "Actual: Italian Settings shows \"No translation found for 'Audio'/'Graphics'/'Language'/'Save'/'Reset' in UI Misc\"; French inventory shows \"No translation found for 'Phoenix' in Inventory Item Name/Description\"; one text next to the item name is empty in every language. Expected: translated text or English fallback.", ("S4", "P3")),
 ("CC-87", "Pressing Space in a BardHare dialogue throws ArgumentOutOfRangeException in DialogueManager when the reply does not advance.",
  "Steps: New Game, talk to BardHare, press Space repeatedly (tap 0.05 s, 0.3 s apart).",
  "Actual: in one session 55 exceptions in 62 presses; the reply does not change during scripted pauses. A later check on a clean Play session: 0 exceptions, the dialogue pages normally (18 presses). The exceptions appeared in a Play session where New Game had already been used several times.", ("S4", "P3")),
 ("CC-88", "Exceptions at the end of a dialogue: MissingReferenceException (StepController destroyed) and NullReferenceException in QuestManagerSO.EndDialogue.",
  "Steps: New Game, talk to BardHare, page through the dialogue with Space until it closes.",
  "Actual: when the dialogue ends the Console shows 5 MissingReferenceException and 2 NullReferenceException (QuestManagerSO.cs line 235) in one session; 0 in the next. A later clean Play session gives 0 exceptions at the end of the first dialogue.", ("S4", "P3")),
 ("CC-89", "Italian: all main menu buttons show \"No translation found for '...' in UI Misc\".",
  "Steps: MainMenu -> Settings -> Language -> Italiano, look at the main menu and Settings.",
  "Actual: all 5 menu buttons (Continue, New Game, Settings, Credits, Exit) show the error text instead of labels; Settings shows 11 such strings. English restores everything. Expected: Italian labels or English fallback.", ("S3", "P3")),
 ("CC-90", "Quest progress is not reliably reset by Back to menu -> New Game: BardHare plays a later-step dialogue, ends with exceptions, or hangs on the last reply.",
  "Steps: in one Play session finish the first and second BardHare conversations, then Esc -> Back to menu -> New Game, talk to BardHare again.",
  "Actual (3 outcomes seen): a later-step dialogue (1-4 replies, or the cooking hint) with NullReferenceException (QuestManagerSO.cs line 235) and ArgumentOutOfRange; or the full first dialogue that hangs on its last reply (45 Space presses do not close it). A fresh Play session always gives the normal first dialogue. Expected: New Game always starts the first quest step.", ("S3", "P3")),
 ("CC-91", "Cooking at the cauldron (Q on a recipe) throws NullReferenceException in UIActionButton.ClickActionButton although the dish is cooked.",
  "Steps: get SweetCream_Recipe (3 Seed needed), go to the cauldron, press E, select the recipe, press Q.",
  "Actual: the dish is cooked (+1), 3 Seed are spent, the inventory closes; 1 NullReferenceException (UIActionButton.cs line 42) is logged. Expected: no exception.", ("S4", "P3")),
]
ai = {"made": "2026-11-24", "scale": "severity_priority_chopchop.md v1.1",
      "note": "Sealed AI ratings made before the human answers. Do not show to the human until answers.json is submitted.",
      "items": [{"id": "B%d" % (i + 1), "jira": b[0], "severity": b[4][0], "priority": b[4][1]} for i, b in enumerate(bugs)]}
raw = json.dumps(ai, ensure_ascii=False, indent=1)
open(os.path.join(D, "AI_SEALED_ratings.json"), "w", encoding="utf-8").write(raw)
h = hashlib.sha256(raw.encode()).hexdigest()
open(os.path.join(D, "AI_SEALED_ratings.sha256"), "w").write(h + "\n")
cards = []
for i, b in enumerate(bugs):
    n = "B%d" % (i + 1)
    cards.append('<section data-id="%s"><h2>%s. %s</h2><p class="st">%s</p><p>%s</p><div class="row"><label>Severity <select class="sev"><option value="">-</option><option>S1</option><option>S2</option><option>S3</option><option>S4</option><option>S5</option></select></label><label>Priority <select class="pri"><option value="">-</option><option>P1</option><option>P2</option><option>P3</option><option>P4</option></select></label></div><textarea class="note" placeholder="Note (optional)"></textarea></section>' % (n, n, html.escape(b[1]), html.escape(b[2]), html.escape(b[3])))
page = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Blind severity rating</title>
<style>:root{--bg:#fff;--fg:#1d2230;--mut:#5b6478;--card:#f4f6fa;--acc:#2457c5}@media(prefers-color-scheme:dark){:root{--bg:#14171f;--fg:#e8ebf2;--mut:#9aa3b8;--card:#1d2230;--acc:#7aa2ff}}
body{background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,sans-serif;max-width:860px;margin:0 auto;padding:16px}section,.intro{background:var(--card);border-radius:10px;padding:12px 16px;margin:14px 0}
h1{font-size:22px}h2{font-size:17px;margin:0 0 6px}.st{color:var(--mut);margin:2px 0}.row{display:flex;gap:16px;flex-wrap:wrap;margin:8px 0}select,textarea,button{font:inherit;padding:6px 8px;border-radius:6px;border:1px solid var(--mut);background:var(--bg);color:var(--fg)}textarea{width:100%;box-sizing:border-box;min-height:44px}
button{background:var(--acc);color:#fff;border:0;padding:10px 18px;cursor:pointer}#cnt{color:var(--mut);margin-left:10px}table{border-collapse:collapse;font-size:14px}td,th{border:1px solid var(--mut);padding:3px 8px;text-align:left}</style></head><body>
<h1>Blind severity and priority rating (11 bugs)</h1>
<div class="intro"><p><b>Rate each bug WITHOUT opening Jira</b> (Jira already shows priorities). Use the scale in <code>severity_priority_chopchop.md</code> v1.1. Main rule: can the player continue the game by another route? Crash, freeze or no way on = S1; continue by a workaround = S2; key function broken without lost progress = S3; works with a visible defect = S4; cosmetic = S5. Priority: P1 urgent, P2 high, P3 medium, P4 low. If unsure pick the higher severity and say why in the note.</p>
<table><tr><th>S1</th><th>S2</th><th>S3</th><th>S4</th><th>S5</th></tr><tr><td>Blocker</td><td>Critical</td><td>Major</td><td>Minor</td><td>Trivial</td></tr></table></div>
__CARDS__
<p><button id="dl">Download answers.json</button><span id="cnt"></span></p>
<script>
const KEY="blind_sev_chopchop";let saved={};try{saved=JSON.parse(localStorage.getItem(KEY)||"{}")}catch(e){}
document.querySelectorAll("section").forEach(s=>{const id=s.dataset.id,v=saved[id]||{};s.querySelector(".sev").value=v.s||"";s.querySelector(".pri").value=v.p||"";s.querySelector(".note").value=v.n||"";
 s.addEventListener("input",()=>{saved[id]={s:s.querySelector(".sev").value,p:s.querySelector(".pri").value,n:s.querySelector(".note").value};try{localStorage.setItem(KEY,JSON.stringify(saved))}catch(e){};upd()})});
function upd(){const n=Object.values(saved).filter(v=>v.s&&v.p).length;document.getElementById("cnt").textContent=" "+n+" of 11 rated"}upd();
document.getElementById("dl").onclick=()=>{const out=[...document.querySelectorAll("section")].map(s=>({id:s.dataset.id,severity:s.querySelector(".sev").value,priority:s.querySelector(".pri").value,note:s.querySelector(".note").value}));
 const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([JSON.stringify({rated:new Date().toISOString(),items:out},null,1)],{type:"application/json"}));a.download="answers.json";a.click()};
</script></body></html>""".replace("__CARDS__", "\n".join(cards))
open(os.path.join(D, "blind_rating.html"), "w", encoding="utf-8").write(page)
print("ok", h[:16], len(page) // 1024, "KB")
