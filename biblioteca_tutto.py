"""Scarico dell'intera biblioteca a blocchi (compliAInce Dynamic).
Uso: python biblioteca_tutto.py <blocco> <n_blocchi> [minuti_max]
Ogni blocco prende le voci di corpus_completo.json con indice % n_blocchi == blocco, salta quelle già scaricate,
si ferma dopo minuti_max e salva un indice e un log propri (nessun conflitto tra blocchi paralleli)."""
import json, sys, time
from pathlib import Path
import biblioteca as b

def main(k, n, minuti=100):
    k, n, t_fine = int(k), int(n), time.time() + float(minuti) * 60
    corpus = json.loads(Path("biblioteca/corpus_completo.json").read_text(encoding="utf-8"))
    mie = [v for i, v in enumerate(corpus) if i % n == k]
    idx_p = b.B / f"indice_blocco{k}.json"
    indice = json.loads(idx_p.read_text(encoding="utf-8")) if idx_p.exists() else {}
    falliti_p = b.B / f"falliti_blocco{k}.json"
    falliti = json.loads(falliti_p.read_text(encoding="utf-8")) if falliti_p.exists() else {}
    fatte = 0
    for v in mie:
        if (b.T / f"{v['id']}.json").exists() or v["id"] in falliti: continue
        if time.time() > t_fine: b.log(f"tempo esaurito: restano voci da scaricare"); break
        t0 = time.time()
        rp = b.T / f"{v['id']}.parziale.json"
        if rp.exists(): v["_ripresa"] = json.loads(rp.read_text(encoding="utf-8"))
        v["_scadenza"] = t_fine
        try:
            if v["fonte"] == "normattiva":
                meta, arts = b.scarica_na(v); url = f"https://www.normattiva.it/uri-res/N2Ls?{v['urn']}"
                if v.get("_interrotto"):
                    rp.write_text(json.dumps({"urn": v.get("_urn"), "da": v["_interrotto"], "articoli": arts,
                                              "meta": {x: (meta or {}).get(x) for x in ("titolo", "sottoTitolo")}}, ensure_ascii=False), encoding="utf-8")
                    b.log(f"{v['id']}: interrotto all'articolo {v['_interrotto']} ({len(arts)} articoli salvati), riprende alla prossima esecuzione"); break
            else:
                meta, arts = b.scarica_ue(v); url = (meta or {}).get("url", "")
        except Exception as e:
            b.log(f"ERRORE {v['id']}: {e}"); falliti[v["id"]] = str(e)[:200]; continue
        if not arts:
            b.log(f"VUOTO {v['id']}"); falliti[v["id"]] = "nessun articolo"; 
        else:
            rec = b.salva(v, meta, arts, url)
            if rp.exists(): rp.rename(rp.with_suffix(".completato"))
            indice[v["id"]] = {x: rec[x] for x in ("titolo", "estremi", "fonte", "url", "area", "scaricato_il", "n_articoli")}
            b.log(f"{v['id']}: {len(arts)} articoli in {time.time()-t0:.0f}s"); fatte += 1
        if fatte % 10 == 0:
            idx_p.write_text(json.dumps(indice, ensure_ascii=False, indent=0), encoding="utf-8")
            falliti_p.write_text(json.dumps(falliti, ensure_ascii=False, indent=0), encoding="utf-8")
    idx_p.write_text(json.dumps(indice, ensure_ascii=False, indent=0), encoding="utf-8")
    falliti_p.write_text(json.dumps(falliti, ensure_ascii=False, indent=0), encoding="utf-8")
    resto = sum(1 for v in mie if not (b.T / f"{v['id']}.json").exists() and v["id"] not in falliti)
    for v in corpus: v.pop("_scadenza", None)
    b.log(f"BLOCCO {k}: scaricate {fatte} in questa esecuzione; mancano {resto}; non riuscite {len(falliti)}")
    with open(b.B / f"log_blocco{k}.txt", "a", encoding="utf-8") as f: f.write("\n".join(b.LOG) + "\n")

if __name__ == "__main__":
    main(*sys.argv[1:])
