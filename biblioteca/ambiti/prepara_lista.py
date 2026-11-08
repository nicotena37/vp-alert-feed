"""Prepara blocchi JSONL con testo più ampio per una lista di id (incerti, BCE, Consob). Uso: python prepara_lista.py <lista.json> <prefisso> [n_per_blocco]"""
import json, os, sys
B = "biblioteca"
ids = json.load(open(sys.argv[1])); ids = list(ids) if not isinstance(ids, dict) else list(ids.keys())
pref = sys.argv[2]; n = int(sys.argv[3]) if len(sys.argv) > 3 else 200
corpus = {v["id"]: v for v in json.load(open(f"{B}/corpus_completo.json")) + json.load(open(f"{B}/corpus_autorita.json"))}
voci = []
for i in ids:
    v = corpus.get(i); p = next((f"{B}/{d}/{i}.json" for d in ("testi", "testi_autorita") if os.path.exists(f"{B}/{d}/{i}.json")), None)
    if not v or not p: continue
    arts = json.load(open(p)).get("articoli", [])
    voci.append({"id": i, "titolo": v["titolo"][:300], "estremi": v.get("estremi", "")[:100],
                 "rubriche": "; ".join(f"{a['num']} {a.get('rubrica','')}"[:90] for a in arts)[:2500],
                 "testo": " ".join(a["testo"] for a in arts)[:4000]})
for k in range(0, len(voci), n):
    open(f"{B}/ambiti/{pref}_{k//n+1:02d}_input.jsonl", "w").write("\n".join(json.dumps(x, ensure_ascii=False) for x in voci[k:k+n]) + "\n")
print(len(voci), "atti in", (len(voci) + n - 1) // n, "blocchi")
