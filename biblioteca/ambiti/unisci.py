"""Unisce i risultati dell'associazione Tematica/Ambito: blocchi base, poi incerti e atti grandi (che li sostituiscono)."""
import json, glob, collections
tax = json.load(open("../tassonomia_estesa.json"))
err = {v["id"] for v in json.load(open("../corpus_completo.json")) if "celex_errato" in v}
tutti = {}
for pat in ("blocco_*_output.jsonl", "incerti_*_output.jsonl", "grandi_*_output.jsonl", "bce_*_output.jsonl", "consob_*_output.jsonl", "giganti_*_output.jsonl", "rev_*_output.jsonl", "fp_*_output.jsonl", "orfani_*_output.jsonl", "tesoreria_*_output.jsonl"):
    for f in sorted(glob.glob(pat)):
        for l in open(f):
            if l.strip():
                o = json.loads(l); o["_da"] = f.split("_")[0]
                if o["_da"] == "rev" and o.get("incerto") and o.get("ambiti"): o["incerto"] = False
                prev = tutti.get(o["id"])
                if o["_da"] == "rev" and prev and prev["_da"] in ("grandi", "giganti") and o.get("ambiti"):
                    m = {(a["t"], a["a"]): dict(a) for a in prev["ambiti"]}
                    for a in o["ambiti"]:
                        k = (a["t"], a["a"])
                        if k in m: m[k]["r"] = "P" if "P" in (a["r"], m[k]["r"]) else "S"
                        else: m[k] = a
                    o["ambiti"] = list(m.values())
                tutti[o["id"]] = o
for i in err:
    if tutti.get(i, {}).get("_da") != "bce": tutti.pop(i, None)
for f in sorted(glob.glob("intr_*_output.jsonl")):          # intrecci: ambiti vicini aggiunti, mai tolti
    for l in open(f):
        if not l.strip(): continue
        o = json.loads(l); t0 = tutti.get(o["id"])
        if not t0: continue
        have = {(a["t"], a["a"]) for a in t0["ambiti"]}
        for a in o.get("aggiunte", []):
            if (a.get("t"), a.get("a")) not in have: t0["ambiti"].append(a); have.add((a.get("t"), a.get("a")))
res, inc, fuori = {}, {}, []
for i, o in tutti.items():
    for a in o["ambiti"]:
        if a["t"] == "Mercati Finanziari": a["t"] = "Mercati finanziari"
    amb = [a for a in o["ambiti"] if a["a"] in tax.get(a["t"], {})]
    if o["incerto"]: inc[i] = o.get("nota", ""); continue
    if not amb: fuori.append(i); continue
    res[i] = {"ambiti": [{"tematica": a["t"], "ambito": a["a"], "ruolo": "principale" if a["r"] == "P" else "secondario",
                          "articoli": a.get("art", []), "motivo": a.get("m", "")} for a in amb], "fonte_classificazione": o["_da"], "abrogato": bool(o.get("abrogato"))}
for i in err:
    if i not in tutti: inc[i] = "testo BCE da riscaricare"
json.dump(res, open("../ambiti_atti.json", "w"), ensure_ascii=False, indent=0)
json.dump(inc, open("incerti.json", "w"), ensure_ascii=False, indent=1)
json.dump(fuori, open("fuori_perimetro.json", "w"), ensure_ascii=False)
c = collections.Counter((a["tematica"], a["ambito"]) for r in res.values() for a in r["ambiti"] if a["ruolo"] == "principale")
print(f"classificati {len(res)}; fuori perimetro {len(fuori)}; incerti {len(inc)}; ambiti principali usati {len(c)} di 125")
