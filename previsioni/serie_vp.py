import json, sys
from pathlib import Path
import numpy as np
TEMATICA = None
def serie_vp(man, temi):
    sys.path.insert(0, "/home/claude/vp-alert-feed")
    import indicatori as I
    spec = Path(__file__).with_name("costruisci_statistiche.py").read_text()
    i0 = spec.index("TEMATICA = {"); i1 = spec.index("}", i0)
    tem = eval(spec[i0 + len("TEMATICA = "):i1 + 1])
    d = json.loads(Path(man).read_text(encoding="utf-8"))
    sett = list(range(2, 32))
    V = np.zeros((len(temi), len(sett)))
    for x in d:
        if x["sett"] not in sett:
            continue
        k = sett.index(x["sett"])
        t = I.temi_di(str(x.get("Riferimento normativo", "")), f"{x.get('Descrizione', '')} {x.get('Argomento', '')}")
        prim = tem.get(str(x.get("Tematica", "")).strip())
        for tt in set([prim] if prim else []) | set(list(t)[:1]):
            if tt in temi:
                V[temi.index(tt), k] += 1
    return V
