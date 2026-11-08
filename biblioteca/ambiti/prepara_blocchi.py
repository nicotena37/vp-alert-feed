"""Prepara i blocchi per l'associazione Tematica/Ambito degli atti della biblioteca (input compatto per gli aiutanti)."""
import json, os, sys
B = "biblioteca"
tax = json.load(open(f"{B}/tassonomia.json"))
lista = [f"{t} > {a}: {', '.join(g for g in arg if g)[:300]}" for t, amb in tax.items() for a, arg in amb.items()]
open(f"{B}/ambiti/ambiti_elenco.txt", "w").write("\n".join(lista))
corpus = json.load(open(f"{B}/corpus_completo.json")) + json.load(open(f"{B}/corpus_autorita.json"))
fatti = set()
for f in os.listdir(f"{B}/ambiti"):
    if f.endswith("_output.json"): fatti |= {o["id"] for o in json.load(open(f"{B}/ambiti/{f}"))}
voci = []
for v in corpus:
    if v["id"] in fatti: continue
    p = next((f"{B}/{d}/{v['id']}.json" for d in ("testi", "testi_autorita") if os.path.exists(f"{B}/{d}/{v['id']}.json")), None)
    if not p: continue
    arts = json.load(open(p)).get("articoli", [])
    rub = "; ".join(f"{a['num']} {a.get('rubrica','')}"[:90] for a in arts)[:1500]
    voci.append({"id": v["id"], "titolo": v["titolo"][:300], "estremi": v.get("estremi", "")[:100],
                 "rubriche": rub, "inizio": " ".join(a["testo"] for a in arts[:2])[:900]})
n = int(sys.argv[1]) if len(sys.argv) > 1 else 250
k = 0
for i in range(0, len(voci), n):
    k += 1; json.dump(voci[i:i+n], open(f"{B}/ambiti/blocco_{k:03d}_input.json", "w"), ensure_ascii=False, separators=(",", ":"))
print(len(voci), "atti in", k, "blocchi;", len(lista), "ambiti")
