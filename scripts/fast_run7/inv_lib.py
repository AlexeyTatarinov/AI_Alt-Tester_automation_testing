# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastlib import *
d = connect()
def hint(): return comp_active("UIInteraction")
def inv(): return comp_active("UIInventory")
def INV(): return ui_obj("UIInventory")
def tab_type():
    try: return INV().get_component_property("UIInventory", "_selectedTab.TabType", ASM)
    except Exception: return None
def slots():
    out = []
    for s in d.find_objects(By.COMPONENT, "UIInventoryItem", enabled=True):
        try:
            out.append((s, s.get_component_property("UIInventoryItem", "currentItem.Item.name", ASM),
                        s.get_component_property("UIInventoryItem", "currentItem.Amount", ASM),
                        s.get_component_property("UIInventoryItem", "currentItem.Item.ItemType.ActionType", ASM)))
        except Exception: pass
    return [x for x in out if x[1]]
def all_tabs():
    """обойти вкладки клавишей Y; вернуть {TabType: [(имя, кол-во, ActionType)]}; вернуться на исходную"""
    res = {}; start = tab_type()
    for _ in range(5):
        t = tab_type(); res[str(t)] = [(n, a, at) for _, n, a, at in slots()]
        key("Y", 0.1); time.sleep(0.7)
        if str(tab_type()) == str(start): break
    return res
def action_button():
    try:
        b = d.find_object(By.NAME, "ActionButton", enabled=False)
        return b, b.get_component_property("UnityEngine.UI.Button", "interactable", "UnityEngine.UI")
    except Exception as e:
        return None, "не прочитано: %s" % type(e).__name__
