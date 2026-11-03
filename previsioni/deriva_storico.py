"""storico2 = storico con gli atti UE di misure restrittive (sanzioni internazionali, Russia ecc.) separati dall'antiriciclaggio:
sono migliaia di atti PESC che altrimenti schiacciano tutti gli altri temi."""
import csv, json, re, shutil, sys
from collections import defaultdict
from pathlib import Path
SRC, DST = Path(sys.argv[1]), Path(sys.argv[2])
DST.mkdir(exist_ok=True)
for f in SRC.glob("*.csv"):
    if f.name != "eurlex.csv":
        shutil.copy(f, DST / f.name)
AML, MR = "Antiriciclaggio e sanzioni finanziarie", "Misure restrittive e sanzioni internazionali"
RX = re.compile(r"misure restrittive|restrictive measures|congelamento|PESC|alla luce della situazione|azioni che destabilizzano|sanzioni nei confronti", re.I)
val = defaultdict(int)
for l in (SRC / "eurlex_voci.jsonl").open(encoding="utf-8"):
    v = json.loads(l)
    m = v["data"][:7]
    for t in v["temi"]:
        if t == AML and RX.search(v["titolo"]):
            t = MR
        val[(m, t, v["tipo"])] += 1
tot = {}
for r in csv.DictReader((SRC / "eurlex.csv").open(encoding="utf-8")):
    if r["totale_fonte"]:
        tot[(r["mese"], r["tipo"])] = r["totale_fonte"]
with (DST / "eurlex.csv").open("w", encoding="utf-8", newline="") as h:
    w = csv.writer(h); w.writerow(["mese", "tema", "tipo", "valore", "totale_fonte"])
    for (m, tp), n in sorted(tot.items()):
        w.writerow([m, "", tp, 0, n])
    for (m, t, tp), n in sorted(val.items()):
        w.writerow([m, t, tp, n, tot.get((m, tp), "")])
conf = json.loads(Path("/home/claude/vp-alert-feed/temi_indicatori.json").read_text(encoding="utf-8"))
if not any(t["tema"] == MR for t in conf["temi"]):
    conf["temi"].insert(1, {"tema": MR, "area": "Banca", "it": [], "en": [], "sigle": []})
Path(__file__).with_name("temi_indicatori.json").write_text(json.dumps(conf, ensure_ascii=False, indent=1), encoding="utf-8")
print("ok", sum(n for (m, t, tp), n in val.items() if t == MR), "atti di misure restrittive")
