"""Biblioteca: testi dell'ambito Antiriciclaggio > Gestione di adeguata verifica (27/11/2026).
1) D.Lgs. 231/2007 e D.Lgs. 109/2007 da Normattiva (testo vigente per articolo) con biblioteca.py
2) Disposizioni Banca d'Italia sull'adeguata verifica (30/7/2019) dal PDF ufficiale, divise per parte/sezione con biblioteca_pdf.py"""
import json, re, sys
from pathlib import Path
import requests
import biblioteca, biblioteca_pdf

import os
if os.environ.get("SOLO_BDI") != "1": biblioteca.scarica("biblioteca/corpus_av.json")
P = Path("biblioteca/pdf_av"); P.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (compliaince-biblioteca)"}
pagina = "https://www.bancaditalia.it/compiti/vigilanza/normativa/archivio-norme/disposizioni/20190730-dispo/index.html"
log = []
try:
    rr = requests.get(pagina, headers=UA, timeout=60); h = rr.text; (P / "pagina.html").write_text(h, encoding="utf-8"); log.append(f"pagina {rr.status_code} {len(h)} caratteri")
    pdf = list(dict.fromkeys(requests.compat.urljoin(pagina, x) for x in re.findall(r'href=["\']([^"\']+?\.pdf[^"\']*)["\']', h, re.I)))
    log.append("PDF nella pagina: " + " | ".join(pdf))
    scelto = next((u for u in pdf if re.search(r"dispo|disposizioni|adeguata", u, re.I) and not re.search(r"relazione|analisi|resoconto|consultaz", u, re.I)), pdf[0] if pdf else None)
    if scelto:
        r = requests.get(scelto, headers=UA, timeout=120); (P / "bibl_BDI-AV-2019.pdf").write_bytes(r.content); log.append(f"scaricato {scelto} ({len(r.content)//1024} KB)")
        Path("biblioteca/corpus_av_pdf.json").write_text(json.dumps([{"id": "BDI-AV-2019", "fonte": "Banca d'Italia", "titolo": "Disposizioni in materia di adeguata verifica della clientela per il contrasto del riciclaggio e del finanziamento del terrorismo", "estremi": "Provv. Banca d'Italia 30 luglio 2019 e succ. mod.", "url": scelto, "area": ["Antiriciclaggio"], "file": "bibl_BDI-AV-2019.pdf"}], ensure_ascii=False), encoding="utf-8")
        biblioteca_pdf.main(str(P), "biblioteca/corpus_av_pdf.json")
except Exception as e:
    log.append(f"ERRORE Banca d'Italia: {e}")
Path("biblioteca/log_av.txt").write_text("\n".join(log + biblioteca.LOG), encoding="utf-8")
print("\n".join(log))
