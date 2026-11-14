"""Aggiunge gli ALLEGATI ai testi UE già in biblioteca (Compliance dyAInamic).
Molti regolamenti di esecuzione e RTS hanno il contenuto negli allegati, che il primo scarico tagliava.
Riscarica la pagina EUR-Lex di ogni atto UE, aggiunge le parti "Allegato ..." in coda agli articoli (gli articoli restano invariati).
Si ferma se EUR-Lex risponde 202 (filtro anti-bot) 5 volte di fila: non lo aggira.
Uso: python biblioteca_allegati.py <minuti_max>"""
import json, re, sys, time
from pathlib import Path
import requests
import biblioteca as b

FATTI = b.B / "allegati_fatti.json"
RX = re.compile(r"(?m)^(ALLEGATO(?:\s+[IVXLC]+|\s+\d+|\s+[A-Z])?|Allegato\s+[IVXLC]+)\s*$")

def allegati(testo):
    pos = [m for m in RX.finditer(testo)]
    out = []
    for i, m in enumerate(pos):
        fine = pos[i + 1].start() if i + 1 < len(pos) else len(testo)
        t = testo[m.start():fine].strip()
        if len(t) < 80: continue
        parti = m.group(1).split(); num = "Allegato" + (" " + parti[1].upper() if len(parti) > 1 else "")
        out.append({"num": num, "rubrica": t.split("\n")[1][:200] if "\n" in t else "", "testo": t[:200000], "hash": b.impronta(t[:200000])})
    return list({a["num"]: a for a in out}.values())

def main(minuti=80):
    t_fine = time.time() + float(minuti) * 60
    fatti = json.loads(FATTI.read_text(encoding="utf-8")) if FATTI.exists() else {}
    corpus = [v for v in json.loads((b.B / "corpus_completo.json").read_text(encoding="utf-8")) if v["fonte"] == "eurlex"]
    n202 = n_ok = n_all = 0
    for v in corpus:
        p = b.T / f"{v['id']}.json"
        if v["id"] in fatti or not p.exists(): continue
        if time.time() > t_fine: break
        rec = json.loads(p.read_text(encoding="utf-8"))
        cx = (rec.get("meta") or {}).get("celex_consolidato") or v["celex"]
        url = f"https://publications.europa.eu/resource/celex/{cx}"      # CELLAR: servizio ufficiale per l'accesso automatico
        try:
            r = requests.get(url, headers={**b.UA, "Accept": "application/xhtml+xml, text/html;q=0.9", "Accept-Language": "ita"}, timeout=180)
            if r.status_code in (404, 406) and cx != v["celex"]:
                r = requests.get(f"https://publications.europa.eu/resource/celex/{v['celex']}", headers={**b.UA, "Accept": "application/xhtml+xml, text/html;q=0.9", "Accept-Language": "ita"}, timeout=180)
        except Exception as e:
            b.log(f"{v['id']}: {e}"); time.sleep(5); continue
        if r.status_code in (202, 429) or (r.status_code == 200 and len(r.text) < 1000):
            n202 += 1; b.log(f"{v['id']}: risposta vuota ({r.status_code})")
            if n202 >= 5: b.log("EUR-Lex filtra le richieste: mi fermo"); break
            time.sleep(30); continue
        n202 = 0
        if r.status_code != 200: fatti[v["id"]] = f"HTTP {r.status_code}"; continue
        al = allegati(b.pulisci(r.text))
        if al:
            nums = {a["num"] for a in rec["articoli"]}
            rec["articoli"] += [a for a in al if a["num"] not in nums]
            rec["n_articoli"] = len(rec["articoli"]); rec["allegati"] = len(al)
            p.write_text(json.dumps(rec, ensure_ascii=False, indent=0), encoding="utf-8"); n_all += 1
        fatti[v["id"]] = len(al); n_ok += 1
        if n_ok % 20 == 0: FATTI.write_text(json.dumps(fatti), encoding="utf-8")
        time.sleep(1.5)
    FATTI.write_text(json.dumps(fatti), encoding="utf-8")
    resto = sum(1 for v in corpus if v["id"] not in fatti and (b.T / f"{v['id']}.json").exists())
    b.log(f"ALLEGATI: controllati {n_ok}, con allegati {n_all}; restano {resto}")
    with open(b.B / "log_allegati.txt", "a", encoding="utf-8") as f: f.write("\n".join(b.LOG[-50:]) + "\n")

if __name__ == "__main__":
    main(*sys.argv[1:])
