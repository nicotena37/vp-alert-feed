"""Unisce i risultati della lettura per articolo (art_*.jsonl) in biblioteca/ambiti_articoli.json.
- riunisce i pezzi dei testi lunghi (id__N) in un'unica norma;
- allinea le parti alle intestazioni "=== [etichetta]" del testo: le parti saltate dagli assistenti
  diventano "Indice" se senza testo, altrimenti "Da rileggere";
- le parti senza testo (voci di sommario, titoli di Capo/Sezione) diventano sempre "Indice";
- scarta i codici di ambito/processo inesistenti e li conta.
Uso: python unisci_articoli.py"""
import json, re, glob, collections
from pathlib import Path

L = Path(__file__).parent
CA = json.loads((L / "codici_ambiti.json").read_text(encoding="utf-8"))
CP = json.loads((L / "codici_processi.json").read_text(encoding="utf-8"))
NA_OK = {"Definizioni", "Ambito di applicazione", "Disposizioni finali", "Obblighi di altri soggetti", "Abrogato", "Indice", "Da rileggere"}

def parti_testo(f):
    t = Path(f).read_text(encoding="utf-8")
    pezzi = re.split(r"(?m)^=== \[(.*?)\][^\n]*\n", t)
    return [(pezzi[i], len(pezzi[i + 1].strip())) for i in range(1, len(pezzi), 2)]

def main():
    righe = {}
    for f in sorted(glob.glob(str(L / "art_*.jsonl"))):
        for r in Path(f).read_text(encoding="utf-8").splitlines():
            r = r.strip()
            if not r: continue
            try: d = json.loads(r)
            except Exception: print("riga non valida in", f); continue
            righe[d["id"].removesuffix(".txt")] = d          # l'ultima riga scritta vince (correzioni)
    norme = collections.defaultdict(lambda: {"parti": [], "nota": []})
    stat = collections.Counter()
    for pid in sorted(righe, key=lambda x: (x.split("__")[0], int(x.split("__")[1]) if "__" in x else 0)):
        d = righe[pid]; nid = pid.split("__")[0]
        f = L / ("testi_pezzi" if "__" in pid else "testi") / f"{pid}.txt"
        sorg = parti_testo(f)
        date = collections.defaultdict(list)
        for p in d.get("parti", []): date[str(p.get("e", "")).strip()].append(p)
        uso = collections.Counter()
        for e, lung in sorg:
            k = uso[e]; uso[e] += 1
            tot = sum(1 for x, _ in sorg if x == e)
            # voci di sommario: l'etichetta compare più volte nel testo e l'assistente ne ha letta solo una
            p = date[e][k - (tot - len(date[e]))] if date[e] and k >= tot - len(date[e]) else None
            if lung < 40 or (p is None and (date[e] or date.get(e + " (2)"))):                                    # parte senza testo
                q = {"e": e, "a": [], "p": [], "na": "Indice"}; stat["indice"] += 1
            elif p is None:
                q = {"e": e, "a": [], "p": [], "na": "Da rileggere"}; stat["mancanti"] += 1
            else:
                a = [c for c in p.get("a", []) if c in CA][:4]; pr = [c for c in p.get("p", []) if c in CP][:4]
                stat["codici_scartati"] += len(p.get("a", [])) - len([c for c in p.get("a", []) if c in CA]) + \
                                           len(p.get("p", [])) - len([c for c in p.get("p", []) if c in CP])
                q = {"e": e, "a": a, "p": pr}
                if not a:
                    q["na"] = p.get("na") if p.get("na") in NA_OK else ("Da rileggere" if not p.get("n") else None)
                    if q["na"] is None: q.pop("na")
                if p.get("n"): q["n"] = p["n"]; stat["proposte"] += 1
            stat["parti"] += 1; stat["con_ambiti"] += bool(q["a"])
            norme[nid]["parti"].append(q)
        if d.get("nota"): norme[nid]["nota"].append(d["nota"])
    out = {}
    for nid, v in norme.items():
        amb = collections.defaultdict(list); pro = collections.defaultdict(list)
        for q in v["parti"]:
            for c in q["a"]: amb[" > ".join(CA[c])].append(q["e"])
            for c in q["p"]: pro[CP[c]["p"]].append(q["e"])
        out[nid] = {"ambiti": dict(amb), "processi": dict(pro), "parti": v["parti"], "nota": " | ".join(v["nota"])}
    (L.parent / "ambiti_articoli.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    prop = collections.Counter(q["n"] for v in out.values() for q in v["parti"] if q.get("n"))
    print(f"norme {len(out)}; parti {stat['parti']} (con ambiti {stat['con_ambiti']}, indice {stat['indice']}, "
          f"da rileggere {stat['mancanti']}); codici scartati {stat['codici_scartati']}; proposte nuove {stat['proposte']}")
    for k, n in prop.most_common(): print("  proposta:", k, n)

if __name__ == "__main__":
    main()
