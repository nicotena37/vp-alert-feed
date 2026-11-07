"""Biblioteca normativa (compliAInce Dynamic): testi delle autorità (Banca d'Italia, CICR, IVASS, Consob, EBA) da PDF ufficiali.
Divide il testo in parti (Sezione / paragrafo / articolo) e salva biblioteca/testi/<id>.json nello stesso formato di biblioteca.py.
Uso: python biblioteca_pdf.py <cartella_pdf> [corpus_pdf.json]"""
import json, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from biblioteca import impronta, B, T

# riconosce le intestazioni delle parti: Articolo 5 / Art. 5 / SEZIONE II / Sezione XI / 1. Titolo (paragrafi numerati) / Paragrafo 3
HDR = re.compile(r"^(?:(?:Articolo|Art\.)\s+(\d+(?:[- ]?(?:bis|ter|quater|quinquies|sexies|septies|octies))?)\b\.?\s*(.*)"
                 r"|(SEZIONE|Sezione)\s+([IVXL]+(?:-bis)?)\b\.?\s*(.*)"
                 r"|(?:Orientamento|Guideline|Linea guida)\s+(\d+)\b\.?\s*(.*))$")

TESSDATA = __import__("os").environ.get("TESSDATA", "/home/claude/tesseract-ocr/tessdata_fast")

def ocr(p):
    """PDF scansionato: immagini delle pagine a 300 dpi e OCR in italiano."""
    import tempfile, glob
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["pdftoppm", "-r", "300", "-gray", "-png", str(p), f"{d}/p"], check=True)
        out = []
        for img in sorted(glob.glob(f"{d}/p*.png")):
            r = subprocess.run(["tesseract", img, "-", "-l", "ita", "--tessdata-dir", TESSDATA], capture_output=True, text=True)
            out.append(r.stdout)
        return "\n".join(out)

def testo_pdf(p):
    r = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", str(p), "-"], capture_output=True, text=True)
    t = r.stdout.replace("\f", "\n")
    if len(re.sub(r"\s", "", t)) < 500: t = ocr(p); print(f"  OCR su {Path(p).name}")
    t = re.sub(r"[ \t]+", " ", t)
    righe = [l.strip() for l in t.splitlines()]
    # toglie numeri di pagina e intestazioni ripetute
    conta = {}
    for l in righe:
        if 5 < len(l) < 90: conta[l] = conta.get(l, 0) + 1
    ripetute = {l for l, n in conta.items() if n >= 6 and not HDR.match(l)}
    return "\n".join(l for l in righe if l and l not in ripetute and not re.fullmatch(r"(-\s*)?\d{1,3}(\s*-)?|Pagina \d+( di \d+)?", l))

# paragrafo numerato con titolo breve: "1.1 Finalità e ambito", "3. Fogli informativi"
PAR = re.compile(r"^(\d{1,2}(?:\.\d{1,2}){0,2})\.?\s+([A-ZÀ-Ü][^.;:]{2,85})$")

def dividi(t):
    parti, cur, sez = [], None, ""
    for l in t.splitlines():
        m = HDR.match(l); mp = PAR.match(l)
        if mp and len(mp.group(2).split()) <= 12 and not m and not (cur and "Art." in cur["num"]):
            if cur: parti.append(cur)
            cur = {"num": f"{sez + ' - ' if sez else ''}par. {mp.group(1)}", "rubrica": mp.group(2).strip(), "righe": [l]}
            continue
        if m and len(l) < 200:
            if m.group(3):                                   # Sezione: diventa contesto e parte a sé
                sez = f"Sezione {m.group(4)}"
                num, rub = sez, m.group(5)
            elif m.group(1):
                num, rub = (f"{sez} - Art. {m.group(1)}" if sez else f"Art. {m.group(1)}"), m.group(2)
            else:
                num, rub = f"Orientamento {m.group(6)}", m.group(7)
            if cur: parti.append(cur)
            cur = {"num": num.replace(" ", " "), "rubrica": (rub or "")[:200], "righe": [l]}
        else:
            if cur is None: cur = {"num": "Premessa", "rubrica": "", "righe": []}
            cur["righe"].append(l)
            if not cur["rubrica"] and len(cur["righe"]) == 2 and len(l) < 160: cur["rubrica"] = l
    if cur: parti.append(cur)
    out, visti = [], {}
    for p in parti:
        testo = "\n".join(p["righe"]).strip()
        if len(testo) < 40: continue
        k = p["num"]
        if k in visti:                                       # stesso numero ripetuto (indice iniziale): numerazione progressiva
            visti[k] += 1; k = f"{k} ({visti[k]})"
        else: visti[k] = 1
        out.append({"num": k, "rubrica": p["rubrica"], "testo": testo, "hash": impronta(testo)})
    return out

def main(cartella, corpus_file="biblioteca/corpus_pdf.json"):
    corpus = json.loads(Path(corpus_file).read_text(encoding="utf-8"))
    idx_p = B / "indice.json"; indice = json.loads(idx_p.read_text(encoding="utf-8")) if idx_p.exists() else {}
    for v in corpus:
        f = Path(cartella) / v["file"]
        if not f.exists(): print("MANCA", v["file"]); continue
        arts = dividi(testo_pdf(f))
        if not arts: print("VUOTO", v["id"]); continue
        rec = {"id": v["id"], "titolo": v["titolo"], "estremi": v.get("estremi", ""), "fonte": v["fonte"], "url": v["url"], "area": v.get("area", []),
               "scaricato_il": datetime.now(timezone.utc).isoformat(timespec="seconds"), "n_articoli": len(arts), "articoli": arts,
               "nota": "testo estratto dal PDF ufficiale, diviso per sezione/articolo/paragrafo"}
        p = T / f"{v['id']}.json"
        if p.exists():
            h_old = {a["num"]: a["hash"] for a in json.loads(p.read_text(encoding="utf-8")).get("articoli", [])}
            rec["cambiati_dall_ultimo_scarico"] = [a["num"] for a in arts if h_old.get(a["num"]) not in (None, a["hash"])]
        p.write_text(json.dumps(rec, ensure_ascii=False, indent=0), encoding="utf-8")
        indice[v["id"]] = {k: rec[k] for k in ("titolo", "estremi", "fonte", "url", "area", "scaricato_il", "n_articoli")}
        print(f"{v['id']}: {len(arts)} parti, {sum(len(a['testo']) for a in arts)//1000} mila caratteri")
    idx_p.write_text(json.dumps(indice, ensure_ascii=False, indent=1), encoding="utf-8")

if __name__ == "__main__":
    main(*sys.argv[1:])
