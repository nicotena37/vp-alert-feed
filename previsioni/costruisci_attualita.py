"""Attualità per tema (ultime 12 settimane) dal giro quotidiano degli indicatori: serve al sito per «oggi» e «da leggere».
Uso: python previsioni/costruisci_attualita.py <uscita.json>
Legge archivio/settimanale.csv, archivio/conteggi.csv (Media Cloud) e archivio/ultime_voci.json.
"""
import csv
import json
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

QUI = Path(__file__).resolve().parent.parent
ARCH = QUI / "archivio"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else QUI / "previsioni" / "attualita.json"
CONF = json.loads((QUI / "temi_indicatori.json").read_text(encoding="utf-8"))
TEMI = [t["tema"] for t in CONF["temi"]]


def sett(d):
    a, s, _ = d.isocalendar()
    return f"{a}-W{s:02d}"


oggi = date.today()
lun = oggi - timedelta(days=oggi.weekday())
SETT = [sett(lun - timedelta(weeks=i)) for i in range(12, 0, -1)]      # 12 settimane complete, la corrente esclusa
val = defaultdict(lambda: defaultdict(float))                          # misura -> (tema, settimana) -> valore
tot_mc = defaultdict(float)
for r in csv.DictReader((ARCH / "settimanale.csv").open(encoding="utf-8")):
    if r["settimana"] in SETT and not r["fonte"].startswith("Media Cloud") and "teleborsa" not in r["fonte"].lower():
        val[r["misura"]][(r["tema"], r["settimana"])] += float(r["valore"] or 0)
for r in csv.DictReader((ARCH / "conteggi.csv").open(encoding="utf-8")):
    if r["settimana"] in SETT and r["fonte"].startswith("Media Cloud"):
        val["mediacloud"][(r["tema"], r["settimana"])] += float(r["valore"] or 0)
        if r["totale"]:
            tot_mc[r["settimana"]] = float(r["totale"])
serie = {m: {t: [v.get((t, s), 0.0) for s in SETT] for t in TEMI} for m, v in val.items()}

PRI = {"media": 0, "legislatore": 1, "politica": 2, "autorita": 3}
voci = {}
uv = json.loads((ARCH / "ultime_voci.json").read_text(encoding="utf-8"))
for t, xs in uv.items():
    xs = [x for x in xs if not x["titolo"].startswith("ESMA Q&A") and "teleborsa" not in x["fonte"].lower()]   # niente Q&A tecniche né aggregatori
    xs.sort(key=lambda x: (PRI.get(x["misura"], 9), x["data"]), reverse=False)
    xs = sorted(xs, key=lambda x: x["data"], reverse=True)
    scelti = [x for x in xs if x["misura"] == "media"][:6] + [x for x in xs if x["misura"] != "media"][:6]
    voci[t] = sorted(scelti, key=lambda x: x["data"], reverse=True)

stato = json.loads((ARCH / "stato_indicatori.json").read_text(encoding="utf-8"))
fonti_ok = sorted(k for k, v in stato.get("fonti", {}).items() if v.get("ok") and v.get("voci", v.get("righe", 0)))
out = {"aggiornato": oggi.isoformat(), "settimane": SETT, "serie": serie, "mediacloud_totale": [tot_mc.get(s, 0) for s in SETT],
       "voci": voci, "fonti_lette": fonti_ok, "ultimo_giro": stato.get("ultimo_giro", "")}
OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(OUT, OUT.stat().st_size, "byte;", len(fonti_ok), "fonti lette;", {m: sum(sum(v) for v in s.values()) for m, s in serie.items()})
