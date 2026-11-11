"""Metodo v3: confronta le due letture indipendenti di una tappa.
Legge v3/<tappa>/out/<serie>_NNN.txt (righe K|codici|sigla|?|nuovo), unisce i pezzi della stessa parte,
e scrive:
 - letture.json: per ogni parte le due letture;
 - accordo.json: le parti dove le due letture coincidono (già definitive);
 - arbitro/NNN.txt: le parti dove divergono, con il testo, da far decidere a un modello più accurato.
Uso: python confronta.py <tappa> <serie1> <serie2>"""
import json, re, sys, glob, collections, textwrap
from pathlib import Path
L = Path(__file__).parent; B = L.parent
SIGLE = {"D": "Definizioni", "C": "Ambito di applicazione", "F": "Disposizioni finali", "O": "Obblighi di altri soggetti", "X": "Abrogato", "I": "Indice"}

def leggi(tappa, serie):
    out = collections.defaultdict(lambda: {"a": [], "na": None, "dubbio": False, "nuovo": None}); scarti = 0
    for f in sorted(glob.glob(str(L / "v3" / tappa / "out" / f"{serie}_*.txt"))):
        for riga in Path(f).read_text(encoding="utf-8").splitlines():
            m = re.match(r"\s*K(\d+)(?:\.\d+)?\s*\|([^|]*)\|([^|]*)\|([^|]*)\|?(.*)$", riga)
            if not m: scarti += bool(riga.strip()); continue
            k = int(m.group(1)); p = out[k]
            for c in re.findall(r"A\d{3}", m.group(2)):
                if c not in p["a"] and 1 <= int(c[1:]) <= 113: p["a"].append(c)
            s = m.group(3).strip().upper()[:1]
            if s in SIGLE and not p["na"]: p["na"] = s
            p["dubbio"] |= "?" in m.group(4)
            if m.group(5).strip(): p["nuovo"] = m.group(5).strip()
    for p in out.values():
        if p["a"]: p["na"] = None; p["a"] = p["a"][:3]
    return out, scarti

def testo_parti(tappa):
    t = {}
    for f in glob.glob(str(L / "v3" / tappa / "pacchetti_*" / "*.txt")):
        s = Path(f).read_text(encoding="utf-8").split("==================== TESTO DA CLASSIFICARE ====================")[-1]
        norma = ""
        for blocco in re.split(r"(?m)^(?==== K\d|######## NORMA)", s):
            if blocco.startswith("########"): norma = blocco.strip().splitlines()[0]; continue
            m = re.match(r"=== K(\d+)(?:\.(\d+))?", blocco)
            if m: t.setdefault(int(m.group(1)), {})[int(m.group(2) or 1)] = (norma, blocco)
        if len(t) > 5000: break
    return t

def main(tappa, s1, s2):
    d = L / "v3" / tappa
    parti = json.loads((d / "parti.json").read_text(encoding="utf-8"))
    a, sa = leggi(tappa, s1); b, sb = leggi(tappa, s2)
    let, acc, arb = {}, {}, []
    st = collections.Counter()
    for p in parti:
        k = p["k"]
        if p["codice"]: st["da codice"] += 1; acc[k] = {"a": [], "na": p["codice"], "fonte": "codice"}; continue
        x, y = a.get(k), b.get(k); let[k] = {s1: x, s2: y}
        if not x or not y: st["manca una lettura"] += 1; arb.append(k); continue
        if x["a"] and y["a"] and set(x["a"]) == set(y["a"]): st["identiche"] += 1; acc[k] = {"a": x["a"], "na": None, "fonte": "accordo"}
        elif not x["a"] and not y["a"]:
            st["identiche"] += 1; acc[k] = {"a": [], "na": SIGLE.get(x["na"] or y["na"], "Obblighi di altri soggetti"), "fonte": "accordo"}
            if x["na"] != y["na"]: st["  di cui sigla diversa"] += 1
        elif x["a"] and y["a"] and x["a"][0] == y["a"][0]:
            # stesso ambito principale, secondari diversi: tieni il principale e i secondari comuni
            st["stesso principale"] += 1; acc[k] = {"a": [x["a"][0]] + [c for c in x["a"][1:] if c in y["a"]], "na": None, "fonte": "principale"}
            acc[k]["solo_uno"] = [c for c in set(x["a"]) ^ set(y["a"])]
        else: st["divergenti"] += 1; arb.append(k)
    (d / "letture.json").write_text(json.dumps(let, ensure_ascii=False), encoding="utf-8")
    (d / "accordo.json").write_text(json.dumps(acc, ensure_ascii=False), encoding="utf-8")
    # file per l'arbitro
    T = testo_parti(tappa); (d / "arbitro").mkdir(exist_ok=True)
    for f in (d / "arbitro").glob("*.txt"): f.unlink()
    gloss = (L / "glossario_ambiti.txt").read_text(encoding="utf-8")
    pac, cur, n = [], [], 0
    for k in arb:
        pezzi = T.get(k, {}); testo = "\n".join(pezzi[j][1] for j in sorted(pezzi))[:12000]; norma = pezzi[min(pezzi)][0] if pezzi else ""
        x, y = a.get(k), b.get(k); f = lambda z: "non letta" if not z else (",".join(z["a"]) or "nessun ambito, sigla " + str(z["na"]))
        blocco = f"{norma}\n{testo}\n>>> LETTURA 1: {f(x)}\n>>> LETTURA 2: {f(y)}\n"
        if cur and n + len(blocco) > 70000: pac.append(cur); cur, n = [], 0
        cur.append(blocco); n += len(blocco)
    if cur: pac.append(cur)
    for i, p in enumerate(pac, 1): (d / "arbitro" / f"{i:03d}.txt").write_text("\n".join(p), encoding="utf-8")
    print(dict(st), "| righe non valide:", sa, sb, "| pacchetti per l'arbitro:", len(pac), "| parti da arbitrare:", len(arb))

if __name__ == "__main__":
    main(*sys.argv[1:])
