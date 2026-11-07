"""Biblioteca: testi delle autorità scaricati da GitHub (EBA, EIOPA, Consob, Agenzia delle Entrate, MEF, AGCM).
Per ogni voce di biblioteca/corpus_autorita.json: se il link è un PDF lo scarica; se è una pagina cerca il PDF principale,
altrimenti usa il testo della pagina. Divide in parti (biblioteca_pdf.dividi) e salva in biblioteca/testi_autorita/.
Rispetta robots.txt. Uso: python autorita.py dominio1,dominio2 [minuti_max]"""
import json, re, sys, time, tempfile, hashlib
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib import robotparser
import requests
from bs4 import BeautifulSoup
import biblioteca_pdf as bp
from biblioteca import impronta

B = Path("biblioteca"); T = B / "testi_autorita"; T.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "compliaince-biblioteca/1.0 (biblioteca normativa; contatto via GitHub)"}
LOG = []; ROB = {}
def log(*a): s = " ".join(map(str, a)); print(s, flush=True); LOG.append(s)

def robots_ok(u):
    b = f"{urlparse(u).scheme}://{urlparse(u).netloc}"
    if b not in ROB:
        rp = robotparser.RobotFileParser()
        try:
            r = requests.get(b + "/robots.txt", headers=UA, timeout=30); rp.parse(r.text.splitlines() if r.status_code == 200 else [])
        except Exception: rp.parse([])
        ROB[b] = rp
    return ROB[b].can_fetch(UA["User-Agent"], u)

def prendi(u):
    if not robots_ok(u): raise RuntimeError("robots.txt vieta")
    r = requests.get(u, headers=UA, timeout=120)
    r.raise_for_status(); return r

def testo_da(u, titolo):
    r = prendi(u)
    if r.content[:4] == b"%PDF" or "pdf" in r.headers.get("content-type", ""):
        return pdf_testo(r.content), u
    so = BeautifulSoup(r.text, "lxml")
    main = so.select_one("main, #main-content, #content, article, .journal-content-article") or so.body
    cand = []
    for a in main.find_all("a", href=True):
        h = urljoin(u, a["href"]); t = " ".join(a.get_text(" ").split())
        if re.search(r"\.pdf($|\?)|/documents/.+\.pdf|dotcmsdoc", h, re.I) and not re.search(r"social|privacy|cookie|English|_EN\b|\bEN\.pdf|relazione illustrativa|esiti della consultazione|resoconto", t + h, re.I):
            sim = len(set(re.findall(r"\w{5,}", t.lower())) & set(re.findall(r"\w{5,}", titolo.lower())))
            cand.append((sim + (2 if re.search(r"testo|delibera|regolamento|provvedimento|circolare|risoluzione|guidelines|orientamenti", t, re.I) else 0), h))
    if cand:
        cand.sort(key=lambda x: -x[0]); h = cand[0][1]
        try:
            r2 = prendi(h)
            if r2.content[:4] == b"%PDF": return pdf_testo(r2.content), h
        except Exception as e: log(f"   pdf {h}: {e}")
    for x in main.select("nav, header, footer, script, style, .breadcrumb, .menu"): x.decompose()
    t = "\n".join(l.strip() for l in main.get_text("\n").splitlines() if l.strip())
    return t, u

def pdf_testo(b):
    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        f.write(b); f.flush(); return bp.testo_pdf(f.name)

def main(domini, minuti=100):
    domini = domini.split(","); fine = time.time() + float(minuti) * 60
    corpus = [v for v in json.loads((B / "corpus_autorita.json").read_text(encoding="utf-8")) if v["dominio"] in domini]
    fp = B / "falliti_autorita.json"; falliti = json.loads(fp.read_text(encoding="utf-8")) if fp.exists() else {}
    ip = B / "indice_autorita_github.json"; indice = json.loads(ip.read_text(encoding="utf-8")) if ip.exists() else {}
    n = 0
    for v in corpus:
        if (T / f"{v['id']}.json").exists() or v["id"] in falliti: continue
        if time.time() > fine: log("tempo esaurito"); break
        try:
            t, src = testo_da(v["url"], v["titolo"]); time.sleep(1)
        except Exception as e:
            falliti[v["id"]] = str(e)[:200]; log(f"ERRORE {v['id']} {v['url']}: {e}"); continue
        arts = bp.dividi(t) if len(t) > 200 else []
        if not arts: falliti[v["id"]] = "testo vuoto"; log(f"VUOTO {v['id']}"); continue
        rec = {"id": v["id"], "titolo": v["titolo"], "estremi": v["estremi"], "fonte": v["fonte"], "url": src, "pagina": v["url"], "area": v["area"],
               "data": v.get("data", ""), "scaricato_il": datetime.now(timezone.utc).isoformat(timespec="seconds"), "n_articoli": len(arts), "articoli": arts}
        (T / f"{v['id']}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=0), encoding="utf-8")
        indice[v["id"]] = {k: rec[k] for k in ("titolo", "estremi", "fonte", "url", "area", "scaricato_il", "n_articoli")}
        n += 1; log(f"{v['id']}: {len(arts)} parti")
        if n % 20 == 0: ip.write_text(json.dumps(indice, ensure_ascii=False, indent=0), encoding="utf-8"); fp.write_text(json.dumps(falliti, ensure_ascii=False, indent=0), encoding="utf-8")
    ip.write_text(json.dumps(indice, ensure_ascii=False, indent=0), encoding="utf-8"); fp.write_text(json.dumps(falliti, ensure_ascii=False, indent=0), encoding="utf-8")
    resto = sum(1 for v in corpus if not (T / f"{v['id']}.json").exists() and v["id"] not in falliti)
    log(f"AUTORITA {','.join(domini)}: scaricati {n}; mancano {resto}; non riusciti {sum(1 for v in corpus if v['id'] in falliti)}")
    with open(B / "log_autorita.txt", "a", encoding="utf-8") as f: f.write("\n".join(LOG) + "\n")

if __name__ == "__main__":
    main(*sys.argv[1:])
