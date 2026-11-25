# -*- coding: utf-8 -*-
import re, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastlib import *
BAD = re.compile(r"(?i)(no translation found|missing entry|missing translation|key not found|^\s*$|\{.*\}|\bnull\b|\bnone\b)")
def read_texts():
    """все видимые (active) TMP/UI.Text: [(имя, текст)]"""
    d = connect(); out = []
    for comp, asm in (("TMPro.TextMeshProUGUI", "Unity.TextMeshPro"), ("TMPro.TMP_Text", "Unity.TextMeshPro"), ("UnityEngine.UI.Text", "UnityEngine.UI")):
        try: objs = d.find_objects(By.COMPONENT, comp, enabled=True)
        except Exception: continue
        for o in objs:
            try: out.append((o.name, o.get_component_property(comp, "text", asm), o.id))
            except Exception as e: out.append((o.name, None, o.id))
    seen = set(); res = []
    for n, t, i in out:
        if i in seen: continue
        seen.add(i); res.append((n, t))
    return res
def audit(tx):
    bad = [(n, t) for n, t in tx if t is None or BAD.search(t or "")]
    return bad
def lang_cur():
    d = connect()
    for o in d.find_objects(By.NAME, "CurrentOption", enabled=True):
        try: return o.get_component_property("TMPro.TextMeshProUGUI", "text", "Unity.TextMeshPro")
        except Exception: pass
