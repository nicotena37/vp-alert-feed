"""Aggiunge a data/indice.json le informazioni sulle modifiche tra atti (da biblioteca/censimento_modifiche.json):
 posizione 11 = {"t":[id atti modificati], "a":[numeri delle parti che modificano altri atti]} per l'atto modificante;
 posizione 12 = [[id atto modificante, [parti]], ...] per l'atto modificato (elenco 'Modificata da').
Le parti modificanti non generano adempimenti. Scrive anche biblioteca/modifiche.json. Uso: python aggiungi_modifiche.py <cartella data>"""
import json, sys, re
from pathlib import Path
B = Path(__file__).resolve().parent.parent / "biblioteca"
data = Path(sys.argv[1])
idx = json.loads((data / "indice.json").read_text(encoding="utf-8"))
cens = json.loads((B / "censimento_modifiche.json").read_text(encoding="utf-8"))
MOD = re.compile(r"(è|sono) (così )?(modificat|sostituit|inserit|soppress|aggiunt|abrogat)|sono apportate le seguenti modifiche|è integrat|sono integrat|è modificat", re.I)
out = {}; da = {}
for mid, v in cens.items():
    if mid not in idx: continue
    t = json.loads((B / "testi" / f"{mid}.json").read_text(encoding="utf-8"))
    esplicite = {a for m in v["modifica"] for a in m.get("articoli", [])}
    arts = set(esplicite)
    for a in t.get("articoli", []):
        if str(a["num"]) in arts: continue
        if MOD.search((a.get("testo") or "")[:700]) and not re.search(r"entrata in vigore|disposizioni finali|abrogazione", a.get("rubrica") or "", re.I): arts.add(str(a["num"]))
    tg = [m["id"] for m in v["modifica"]]
    out[mid] = {"t": tg, "a": sorted(arts, key=lambda x: (len(x), x))}
    for m in v["modifica"]:
        if m["in_biblioteca"]: da.setdefault(m["id"], []).append([mid, sorted(m.get("articoli", []), key=lambda x: (len(x), x))])
for nid, v in idx.items():
    while len(v) < 13: v.append(0)
    v[11] = out.get(nid, 0); v[12] = da.get(nid, 0)
(B / "modifiche.json").write_text(json.dumps({"modificanti": out, "modificata_da": da}, ensure_ascii=False), encoding="utf-8")
(data / "indice.json").write_text(json.dumps(idx, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print("atti modificanti", len(out), "parti modificanti", sum(len(x["a"]) for x in out.values()), "atti modificati con elenco", len(da))
