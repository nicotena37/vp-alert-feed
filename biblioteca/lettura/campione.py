"""Metodo v3: unisce accordo + arbitro nel risultato finale della tappa (finale.json) e
prepara il campione per il giudice (giudice_input.txt), stratificato per tipo di esito.
Uso: python campione.py <tappa> <serie della lettura singola da valutare> [n per strato]"""
import json, sys, random, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import confronta as C
L = Path(__file__).parent

def main(tappa, serie, n="45"):
    n = int(n); d = L / "v3" / tappa; random.seed(5)
    acc = {int(k): v for k, v in json.loads((d / "accordo.json").read_text()).items()}
    arb, _ = C.leggi(tappa, "ARB"); sing, _ = C.leggi(tappa, serie)
    parti = json.loads((d / "parti.json").read_text())
    fin = {}
    for p in parti:
        k = p["k"]
        if k in acc: fin[k] = dict(acc[k])
        elif k in arb: fin[k] = {"a": arb[k]["a"], "na": C.SIGLE.get(arb[k]["na"]) if not arb[k]["a"] else None, "fonte": "arbitro", "dubbio": arb[k]["dubbio"], "nuovo": arb[k]["nuovo"]}
        else: fin[k] = {"a": [], "na": "Da rileggere", "fonte": "mancante"}
    (d / "finale.json").write_text(json.dumps(fin, ensure_ascii=False), encoding="utf-8")
    T = C.testo_parti(tappa)
    strati = {s: [k for k, v in fin.items() if v["fonte"] == s] for s in ("accordo", "principale", "arbitro")}
    scelta = []
    for s, ks in strati.items(): scelta += [(s, k) for k in random.sample(ks, min(len(ks), n if s != "principale" else n // 2))]
    random.shuffle(scelta)
    f = lambda z: (",".join(z["a"]) if z and z["a"] else "nessun ambito (" + str((z or {}).get("na")) + ")")
    righe, chiave = [], {}
    for s, k in scelta:
        pz = T.get(k, {}); testo = "\n".join(pz[j][1] for j in sorted(pz))[:9000]; norma = pz[min(pz)][0] if pz else ""
        x = sing.get(k); y = fin[k]
        sx = f(x); sy = f({"a": y["a"], "na": {v: kk for kk, v in C.SIGLE.items()}.get(y["na"], y["na"])})
        righe.append(f"{norma}\n{testo}\n>>> CLASSIFICAZIONE X: {sx}\n>>> CLASSIFICAZIONE Y: {sy}\n")
        chiave[k] = s
    (d / "giudice_input.txt").write_text("\n".join(righe), encoding="utf-8")
    (d / "giudice_strati.json").write_text(json.dumps(chiave))
    print({s: len(v) for s, v in strati.items()}, "campione", len(scelta), "caratteri", sum(len(r) for r in righe))

if __name__ == "__main__":
    main(*sys.argv[1:])
