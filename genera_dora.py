# Legal inventory DORA per il modulo Processi, generata dagli adempimenti del risk assessment DORA (livello «obblighi»).
# Ogni adempimento tiene il collegamento al risk assessment (campo «ra») così processi e risk assessment si leggono a vicenda.
import json, re
from pathlib import Path
SP = Path(__file__).resolve().parent; out = SP / "biblioteca" / "adempimenti_ambiti"
F = json.loads((out / "fonti" / "ra_dora_obblighi.json").read_text(encoding="utf-8"))
AMB = "IT e Digital||Resilienza operativa digitale (DORA)"
def nome(n):
    m = re.match(r"UE-3(\d{4})R(\d{4})$", n or "")
    if m: return ("Reg. (UE) " if m.group(1) + m.group(2) == "20222554" else "Reg. (UE) ") + f"{m.group(1)}/{int(m.group(2))}"
    if n == "IT-decreto.legislativo-2025-03-10-23": return "d.lgs. 23/2025"
    if (n or "").startswith("EBA-"): return "Orientamenti EBA"
    return n or ""
def url(n):
    m = re.match(r"UE-(3\d{4}R\d{4})$", n or "")
    return f"https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:{m.group(1)}" if m else ("https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2025-03-10;23" if "2025-03-10-23" in (n or "") else "")
PAROLE = [(r"incident|notific|classific|segnal", "incident|notific|classific|segnal|ticket"), (r"backup|ripristin|copie", "backup|ripristin"),
          (r"continuit|disaster|emergenz|crisi", "continuit|disaster|ripristin|DR\\b"), (r"fornitor|terz|contratt|registro|accord|subappalt|uscita", "fornitor|registro|contratt|clausol"),
          (r"test|vulnerab|penetra|TLPT|scansion", "test|vulnerab|scansion|patch"), (r"organo|consiglio|governance|approva|formazione", "approva|organo|direzione"),
          (r"rilev|anomal|monitor|SIEM|allarm", "correla|allarm|rilev|SIEM|EDR"), (r"patch|accessi|autentic|crittograf|protezion|rete", "patch|accessi|scansion"),
          (r"post-incidente|lezion|apprend|riesam", "revisione|lezion"), (r"comunic|client|pubblic", "comunica")]
macro = []; ad = []
for i, a in enumerate(F["adempimenti"], 1):
    if a["macro"] not in macro: macro.append(a["macro"])
    testo = (a["titolo"] + " " + (a["desc"] or ""))
    par = "|".join(sorted({p for k, p in PAROLE if re.search(k, testo, re.I)})) or "rischio TIC"
    punti = [{"norma": nome(f["norma"]), "rif": f"art. {f['art']}" + (f", par. {f['comma']}" if f.get("comma") else ""), "testo": f.get("titolo") or "", "estratto": f.get("cit") or "", "url": url(f["norma"]), "fonte_id": f["norma"], "ra_pid": f.get("pid", "")} for f in a["fonti"]]
    sintesi = (a["desc"] or "").split("\n\n")[0].strip()
    ad.append({"id": f"DO-{i:02d}", "macro": f"DO-M{macro.index(a['macro']) + 1}", "titolo": a["titolo"], "testo": "", "norma": "; ".join(sorted({p["norma"] for p in punti})),
               "articolo": "; ".join(dict.fromkeys(p["rif"] for p in punti if p["norma"] == "Reg. (UE) 2022/2554")) or punti[0]["rif"], "parole": par, "sostituisce": [], "punti": punti,
               "sintesi": sintesi, "ra": f"{F['ra']}/{a['_id']}", "sanzione": a.get("sanz_txt") or ""})
L = {"ambito": AMB, "sigla": "DORA", "versione": F["estratto"], "macro": [{"id": f"DO-M{k + 1}", "titolo": t} for k, t in enumerate(macro)], "adempimenti": ad}
(out / "legal_dora.json").write_text(json.dumps(L, ensure_ascii=False), encoding="utf-8")
I = json.loads((out / "legal_indice.json").read_text(encoding="utf-8")); I["ambiti"] = [x for x in I["ambiti"] if x["ambito"] != AMB]
I["ambiti"].append({"ambito": AMB, "file": "legal_dora.json", "n": len(ad), "punti": sum(len(a["punti"]) for a in ad), "macro": len(macro), "fonti": sorted({p["norma"] for a in ad for p in a["punti"]})})
(out / "legal_indice.json").write_text(json.dumps(I, ensure_ascii=False, indent=1), encoding="utf-8")
print(AMB, len(macro), "gruppi,", len(ad), "adempimenti,", sum(len(a["punti"]) for a in ad), "punti")
