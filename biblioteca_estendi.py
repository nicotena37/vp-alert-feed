"""Completa gli atti italiani troncati: lo scarico Normattiva si fermava dopo 15 articoli mancanti di fila
(vuoti di numerazione o risposte rallentate). Per ogni atto prova alcuni articoli oltre l'ultimo scaricato;
se esistono, riprende lo scarico da lì con una soglia più alta. Uso: python biblioteca_estendi.py <minuti>"""
import json, re, sys, time
import biblioteca as b

FATTI = b.B / "estesi_fatti.json"

def num(n):
    m = re.match(r"(\d+)", str(n)); return int(m.group(1)) if m else None

def main(minuti=80, priorita=None):
    fine = time.time() + float(minuti) * 60
    fatti = json.loads(FATTI.read_text(encoding="utf-8")) if FATTI.exists() else {}
    corpus = [v for v in json.loads((b.B / "corpus_completo.json").read_text(encoding="utf-8")) if v["fonte"] == "normattiva"]
    if priorita:                                  # atti da fare per primi (es. le norme della prova)
        pri = json.loads(open(priorita, encoding="utf-8").read())
        for i in pri: fatti.pop(i, None)
        corpus.sort(key=lambda v: (v["id"] not in pri,))
    for i in [k for k, x in fatti.items() if str(x).startswith("esteso a")]: fatti.pop(i)   # rifai quelli non salvati
    est = 0
    for v in corpus:
        p = b.T / f"{v['id']}.json"
        if v["id"] in fatti or not p.exists(): continue
        if time.time() > fine: break
        rec = json.loads(p.read_text(encoding="utf-8")); arts = rec["articoli"]
        nums = [num(a["num"]) for a in arts if num(a["num"]) is not None]
        if not nums: fatti[v["id"]] = "senza numeri"; continue
        ultimo = max(nums); amax = v.get("a", 2000)
        if ultimo >= amax: fatti[v["id"]] = "completo"; continue
        urn = (rec.get("meta") or {}).get("urn") or v.get("_urn") or v["urn"]
        trovato = None
        for k in range(ultimo + 1, min(amax, ultimo + 80) + 1, 4):        # sonda oltre l'ultimo articolo
            at = b.art_na(urn, k); time.sleep(0.8)
            if not at and urn != v["urn"]: at = b.art_na(v["urn"], k); time.sleep(0.8)
            if at: trovato = k; break
        if not trovato: fatti[v["id"]] = f"completo ({ultimo})"; continue
        voce = dict(v); voce["stop"] = 60
        voce["_ripresa"] = {"urn": urn if b.art_na(urn, trovato) else v["urn"], "da": ultimo + 1, "articoli": list(arts), "meta": None}
        meta, nuovi = b.scarica_na(voce)
        if len(nuovi) > len(arts):
            rec["articoli"] = nuovi; rec["n_articoli"] = len(nuovi); rec["esteso_il"] = time.strftime("%Y-%m-%d")
            p.write_text(json.dumps(rec, ensure_ascii=False, indent=0), encoding="utf-8"); est += 1
            b.log(f"ESTESO {v['id']}: da {len(arts)} a {len(nuovi)} articoli")
        fatti[v["id"]] = f"esteso a {len(nuovi)}"
        FATTI.write_text(json.dumps(fatti, ensure_ascii=False), encoding="utf-8")
    FATTI.write_text(json.dumps(fatti, ensure_ascii=False), encoding="utf-8")
    resto = sum(1 for v in corpus if v["id"] not in fatti and (b.T / f"{v['id']}.json").exists())
    b.log(f"ESTENDI: atti estesi {est}; restano {resto}")
    with open(b.B / "log_estendi.txt", "a", encoding="utf-8") as f: f.write("\n".join(b.LOG[-80:]) + "\n")

if __name__ == "__main__":
    main(*sys.argv[1:])
