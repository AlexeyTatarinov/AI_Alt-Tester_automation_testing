p='m0302.py'
s=open(p,encoding='utf-8').read()
add='''    if PH == "C":
        if scene_now() != ["Field_Hill"]:
            key("C", 0.1); time.sleep(1.2); D["C_setup"] = str(goto("Field_Hill")); time.sleep(3)
        tr("C: до подхода")
        c = crit(); assert c is not None
        t = approach(c); tr("C: подошёл, тревога", alert_s=t, alert=alert(c))
        cp = cpos(c); teleport("T1", cp[0] - 1.2, cp[1] + 0.3, cp[2]); time.sleep(1.0)
        for _ in range(3): step_towards(cp, 0.08)
        hits = 0; gone = False; dead = False; t0 = time.time()
        while time.time() - t0 < 20:
            key("F", 0.1); hits += 1; time.sleep(0.4)
            try:
                c.update_object()
                if c.get_component_property("Damageable", "IsDead", ASM) is True: dead = True
            except Exception:
                gone = True; break
            if dead: break
            if hits % 6 == 0:
                try:
                    cp2 = (c.worldX, c.worldY, c.worldZ)
                    if dxz(ppos(), cp2) > 2.2: teleport("T1", cp2[0] - 1.2, cp2[1] + 0.3, cp2[2]); time.sleep(0.5)
                    step_towards(cp2, 0.08)
                except Exception: pass
        tr("C: сразу после удара", hits=hits, gone=gone, dead=dead)
        time.sleep(5); tr("C: через 5 с")
        D["exc_C"] = exc_summary(off)["total"]
    if PH == "D":
        tr("D: до Back to menu")
        guard.risky("m0302 D back to menu"); r = to_menu(); print("to_menu", r)
        for _ in range(20):
            time.sleep(1.5)
            if "MainMenu" in scenes() and d.find_objects(By.NAME, "Button New Game", enabled=False): break
        time.sleep(1); tr("D: в MainMenu")
        guard.restore_window("m0302 D ng"); print("new_game", new_game())
        for _ in range(20):
            time.sleep(1.5)
            try: ppos(); break
            except Exception: pass
        time.sleep(3); tr("D: после New Game (Beach)")
        D["D_setup"] = str(goto("Field_Hill")); time.sleep(3)
        tr("D: Field_Hill, до подхода")
        c = crit(); assert c is not None
        t = approach(c); tr("D: подошёл, тревога", alert_s=t, alert=alert(c))
        n, dist, a = walk_away(c); tr("D: ушёл", steps=n, dist=dist, alert=a)
        time.sleep(10); tr("D: через 10 с")
        D["exc_D"] = exc_summary(off)["total"]
'''
s=s.replace("    jdump(F, D)\nfinally:", add+"    jdump(F, D)\nfinally:")
open(p,'w',encoding='utf-8').write(s)
