"""Aggiunge a data/indice.json i processi ABI Lab (posizione 8) derivati dagli ambiti di ogni norma
tramite la tabella biblioteca/lettura/ambito_processi.json, e il flag 'senza adempimenti' (posizione 10)
dalla lista biblioteca/senza_adempimenti.json. Uso: python aggiungi_processi.py <cartella data>"""
import json, sys, collections
from pathlib import Path
B = Path(__file__).resolve().parent.parent / "biblioteca"
data = Path(sys.argv[1])
idx = json.loads((data / "indice.json").read_text(encoding="utf-8"))
tab = json.loads((B / "lettura/ambito_processi.json").read_text(encoding="utf-8"))
cp = json.loads((B / "lettura/codici_processi.json").read_text(encoding="utf-8"))
ca = json.loads((B / "lettura/codici_ambiti.json").read_text(encoding="utf-8"))
per_amb = {tuple(v): tab.get(c, []) for c, v in ca.items()}
sf = B / "senza_adempimenti.json"
senza = set(json.loads(sf.read_text(encoding="utf-8"))) if sf.exists() else set()
n_proc = n_senza = 0
for nid, v in idx.items():
    proc = collections.OrderedDict()
    for t, a, r, e in v[4]:
        for p in per_amb.get((t, a), []):
            nome = cp[p]["p"]
            x = proc.setdefault(nome, [nome, [], "S"])
            x[1] = sorted(set(x[1]) | set(map(str, e)), key=str)
            if r == "P": x[2] = "P"
    while len(v) < 11: v.append(0 if len(v) != 8 else [])
    v[8] = list(proc.values()); v[10] = 1 if nid in senza else 0
    n_proc += bool(proc); n_senza += v[10]
(data / "indice.json").write_text(json.dumps(idx, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print("norme", len(idx), "con processi", n_proc, "senza adempimenti", n_senza)
