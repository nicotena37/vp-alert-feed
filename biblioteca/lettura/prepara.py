"""Prepara la lettura per articolo (metodo v3) di un elenco di norme.
1) divide ogni norma nelle sue parti (articoli, paragrafi, allegati) dai testi della biblioteca;
2) etichetta DA CODICE, senza modello, le parti che non hanno obblighi (sommari, definizioni,
   entrata in vigore, abrogazioni, articoli abrogati, tavole di concordanza);
3) mette le parti restanti in pacchetti di testo di dimensione limitata, numerati, da far leggere.
Uso: python prepara.py <tappa> <file con gli id, uno per riga> [caratteri per pacchetto] [serie]
Crea v3/<tappa>/parti.json (tutte le parti, con l'etichetta da codice se c'è) e v3/<tappa>/pacchetti/NNN.txt"""
import json, re, sys, textwrap
from pathlib import Path

L = Path(__file__).parent; B = L.parent
MAXPARTE = 45000      # una parte più lunga viene divisa in pezzi (stessa parte, più letture)

FINALI = re.compile(r"^(entrata in vigore|abrogazion|norme? abrogat|destinatari$|recepimento|attuazione$|clausola di invarianza|"
                    r"copertura finanziaria|disposizion[ei] finanziari|esercizio della delega|procedura di comitato|"
                    r"riesame|relazion[ei]$|valutazione$|modifiche? (al|alla|del|della|dei|degli|all')|tavola di concordanza)", re.I)
DEFIN = re.compile(r"^definizion", re.I)
ABROG = re.compile(r"abrogat|soppress", re.I)

def carica(i):
    for d in ("testi", "testi_autorita"):
        p = B / d / f"{i}.json"
        if p.exists(): return json.loads(p.read_text(encoding="utf-8"))

def da_codice(a, etichette):
    t = (a.get("testo") or "").strip(); r = (a.get("rubrica") or "").strip(); e = str(a["num"])
    if len(t) < 40: return "Indice"
    if f"{e} (2)" in etichette and len(t) < 400: return "Indice"          # voce di sommario ripetuta nel corpo
    if len(t) < 400 and ABROG.search(t) and not re.search(r"\b(deve|devono|è tenut|sono tenut|obblig)", t, re.I): return "Abrogato"
    if DEFIN.match(r): return "Definizioni"
    if FINALI.match(r) and not re.match(r"modific", r, re.I): return "Disposizioni finali"
    if re.match(r"tavola di concordanza", r, re.I) or (t.count("\n") > 5 and len(re.findall(r"(?m)^Articolo \d+", t)) > 0.6 * (t.count("\n") + 1)):
        return "Disposizioni finali"
    return None

def main(tappa, elenco, maxp="48000", serie="A"):
    MAXP = int(maxp)
    testa = (L / "prompt3.txt").read_text(encoding="utf-8") + (L / "glossario_ambiti.txt").read_text(encoding="utf-8") + "\n==================== TESTO DA CLASSIFICARE ====================\n"
    ids = [x.strip() for x in Path(elenco).read_text().split() if x.strip()]
    out = L / "v3" / tappa; (out / f"pacchetti_{serie}").mkdir(parents=True, exist_ok=True)
    parti, da_leggere = [], []
    for nid in ids:
        r = carica(nid)
        if not r: print("manca il testo:", nid); continue
        arts = r.get("articoli", []); etichette = {str(a["num"]) for a in arts}
        tit = re.sub(r"\s+", " ", r.get("titolo") or nid)[:160]
        for a in arts:
            lab = da_codice(a, etichette)
            k = len(parti)
            parti.append({"k": k, "id": nid, "e": str(a["num"]), "r": (a.get("rubrica") or "")[:120], "n": len(a.get("testo") or ""), "codice": lab})
            if lab is None:
                t = (a.get("testo") or "").strip()
                pezzi = [t[i:i + MAXPARTE] for i in range(0, len(t), MAXPARTE)] or [""]
                for j, pz in enumerate(pezzi):
                    da_leggere.append((k, nid, tit, str(a["num"]), (a.get("rubrica") or "")[:120], pz, j, len(pezzi)))
    # pacchetti: norme intere finché ci stanno, senza superare MAXP
    pac, cur, n = [], [], 0
    for x in da_leggere:
        if cur and n + len(x[5]) > MAXP: pac.append(cur); cur, n = [], 0
        cur.append(x); n += len(x[5])
    if cur: pac.append(cur)
    for i, p in enumerate(pac, 1):
        righe, ultimo = [], None
        for k, nid, tit, e, r, t, j, tot in p:
            if nid != ultimo: righe += ["", f"######## NORMA: {tit}  (id {nid})", ""]; ultimo = nid
            righe.append(f"=== K{k}" + (f".{j + 1}" if tot > 1 else "") + f" | [{e}] {r}" + (f" (pezzo {j + 1} di {tot})" if tot > 1 else ""))
            for riga in t.split("\n"): righe += textwrap.wrap(riga, 200) or [""]
            righe.append("")
        (out / f"pacchetti_{serie}" / f"{i:03d}.txt").write_text(testa + "\n".join(righe), encoding="utf-8")
    (out / "parti.json").write_text(json.dumps(parti, ensure_ascii=False), encoding="utf-8")
    import collections
    c = collections.Counter(p["codice"] or "da leggere" for p in parti)
    car = sum(p["n"] for p in parti); letti = sum(len(x[5]) for x in da_leggere)
    print(f"norme {len(ids)}, parti {len(parti)}, {dict(c)}; caratteri {car} di cui da leggere {letti} ({round(100*letti/max(car,1))}%); pacchetti {len(pac)}")

if __name__ == "__main__":
    main(*sys.argv[1:])
