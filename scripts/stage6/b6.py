from g6 import *
off = json.load(open(os.path.join(R2, "b1.json"), encoding="utf-8"))["off"]
R = []
for i in range(3):
    s = {"t": now(), "scenes": scenes()}
    pl = pigs(); s["pigs"] = len(pl)
    s["pigs_active"] = len(d.find_objects(By.NAME, "PigChef(Clone)", enabled=True))
    if pl:
        o = pl[0]; s["pig"] = [o.id, round(o.worldX, 2), round(o.worldY, 2), round(o.worldZ, 2), o.enabled]
    try: s["state"] = sname(gstate())
    except Exception as e: s["state"] = type(e).__name__
    sl = first("SceneLoader"); s["_isLoading"] = rd(sl, "SceneLoader", "_isLoading", 1) if sl else None
    pr = first("Protagonist"); s["map"] = str(rd(pr, "Protagonist", "_inputReader._gameInput.Gameplay.enabled", 2))[:80] if pr else None
    s["hp"] = hp_now(); e = exc_summary(off); s["exc"] = e["by_type"]
    R.append(s); print(json.dumps(s, ensure_ascii=False), flush=True); time.sleep(5)
    if i == 0: d.get_png_screenshot(os.path.join(R2, "shots", "b6_jumpdown.png"))
jdump(os.path.join(R2, "b6.json"), R)
