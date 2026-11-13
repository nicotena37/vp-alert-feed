"""Censimento (sola lettura): quali atti della biblioteca ne modificano altri e se l'atto modificato e' presente con testo aggiornato.
Legge testi/UE-*.json (titolo, url) e scrive biblioteca/censimento_modifiche.json. Non modifica i testi.
Uso: python censimento_modifiche.py"""
import json, glob, re, collections
from pathlib import Path
B = Path(__file__).parent
atti = {}
for f in glob.glob(str(B / "testi" / "UE-*.json")):
    x = json.loads(Path(f).read_text(encoding="utf-8"))
    atti[x["id"]] = {"titolo": x["titolo"], "url": x.get("url", ""), "cons": bool(re.search(r"CELEX:0\d{4}[A-Z]\d{4}-\d{8}", x.get("url", ""))), "testo": f}

def celex(tipo, a, n):
    t = tipo.lower()
    if t.startswith("reg"): return f"UE-3{a}R{int(n):04d}"
    if t.startswith("dir"): return f"UE-3{a}L{int(n):04d}"
    return None

RX = re.compile(r"(regolamento|direttiva|decisione)(?: delegat\w+| di esecuzione)?\s*\((?:UE|CE|CEE|Euratom)\)\s*(?:n\.\s*)?(\d{1,4})/(\d{2,4})|(regolamento|direttiva)\s*(?:\((?:UE|CE|CEE)\))?\s*(?:n\.\s*)?(\d{1,4})/(\d{4})/?(?:UE|CE)?|(direttiva)\s+(\d{4})/(\d{1,3})/(?:UE|CE)", re.I)
def bersagli(testo):
    t = re.sub(r"\s+", " ", testo); out = []
    for g in re.finditer(r"(regolament\w+|direttiv\w+|decision\w+)(?: delegat\w+| di esecuzione)?\s*\((UE|CE|CEE|Euratom)\)?\s*(n\.\s*)?(\d{1,4})/(\d{2,4})|(direttiv\w+)\s+(\d{4})/(\d{1,3})/(UE|CE|CEE)", t, re.I):
        if g.group(1):
            tipo, x, y = g.group(1), g.group(4), g.group(5)
            anno_prima = not g.group(3) and len(x) == 4 and 1950 <= int(x) <= 2030
            a, n = (x, y) if anno_prima else (y, x)
        else:
            tipo, a, n = g.group(6), g.group(7), g.group(8)
        if len(a) == 2: a = ("20" if int(a) < 50 else "19") + a
        if not (1950 <= int(a) <= 2030): continue
        c = celex(tipo, a, n)
        if c: out.append(c)
    return list(dict.fromkeys(out))

ris = {}
for i, a in atti.items():
    x = json.loads(Path(a["testo"]).read_text(encoding="utf-8"))
    mod = {}
    m = re.search(r"\b(che modifica|recante modifica|che rettifica|e che modifica|che modifica e)\b(.*)", re.sub(r"\s+", " ", a["titolo"]), re.I)
    if m:
        for t in bersagli(m.group(2)): mod.setdefault(t, [])
    for art in x.get("articoli", []):
        if re.match(r"\s*Modific\w+ (del|dei|della|delle|al|alla|agli|alle|all)", art.get("rubrica") or "", re.I):
            for t in bersagli(art["rubrica"]): mod.setdefault(t, []).append(art["num"])
    if mod:
        ris[i] = {"titolo": a["titolo"][:140], "modifica": [{"id": t, "articoli": arts, "in_biblioteca": t in atti, "consolidato": atti[t]["cons"] if t in atti else None} for t, arts in mod.items() if t != i]}
ris = {k: v for k, v in ris.items() if v["modifica"]}
(B / "censimento_modifiche.json").write_text(json.dumps(ris, ensure_ascii=False, indent=1), encoding="utf-8")
st = collections.Counter()
for r in ris.values():
    for m in r["modifica"]:
        st["bersagli"] += 1; st["in biblioteca" if m["in_biblioteca"] else "NON in biblioteca"] += 1
        if m["in_biblioteca"]: st["consolidato" if m["consolidato"] else "NON consolidato"] += 1
print(len(ris), "atti modificanti con bersaglio riconosciuto;", dict(st))
