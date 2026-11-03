"""Sanzioni da fonti ufficiali per la pagina Sanzioni del VP Alert.

  BCE - Vigilanza bancaria   tabella "Published sanctions" (bankingsupervision.europa.eu)
  Consob                     pagina dei provvedimenti sanzionatori (se il sito la rende leggibile)
Banca d'Italia NON si legge da qui: si legge solo dal browser del PC (regola del progetto).
Uscite in archivio/sanzioni/: <fonte>.json (righe) e <fonte>_pagina.html (copia della pagina, per controllo).
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup

import indicatori as I

QUI = Path(__file__).parent
OUT = QUI / "archivio" / "sanzioni"


def testo(x) -> str:
    return re.sub(r"\s+", " ", x.get_text(" ", strip=True)) if x else ""


def importo(s: str) -> float | None:
    v = [float(n.replace(",", "")) for n in re.findall(r"\d[\d,]*(?:\.\d+)?", s.replace("\xa0", " "))]
    return sum(v) if v else None


def bce_vigilanza() -> list[dict]:
    url = "https://www.bankingsupervision.europa.eu/framework/sanctions/html/index.en.html"
    c = I.prendi(url, "text/html", 90)
    (OUT / "bce_vigilanza_pagina.html").write_bytes(c)
    s = BeautifulSoup(c, "lxml")
    righe, ultima = [], None
    for tab in s.find_all("table"):
        intest = [testo(th).lower() for th in tab.find_all("th")]
        if not any("imposed on" in h for h in intest):
            continue
        for tr in tab.find_all("tr"):
            celle = tr.find_all(["th", "td"])
            if len(celle) < 4 or not tr.find("td"):
                continue
            v = [testo(td) for td in celle]
            link = ""
            for a in tr.find_all("a", href=True):
                if "publication" in a["href"].lower() or a["href"].lower().endswith(".pdf"):
                    link = a["href"] if a["href"].startswith("http") else "https://www.bankingsupervision.europa.eu" + a["href"]
                    break
            m = re.match(r"(\d{2})/(\d{2})/(\d{4})", v[0])
            if m:
                d = f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
                riga = {"data": d, "autorita": "BCE - Vigilanza bancaria", "area": "UE", "soggetto": v[1], "impostaDa": v[2],
                        "importo": importo(v[3]), "importoTesto": v[3], "violazione_en": v[4] if len(v) > 4 else "",
                        "esito": v[6] if len(v) > 6 else "", "link": link, "fonte": url}
                righe.append(riga)
                ultima = riga
            elif ultima is not None:      # riga di continuazione: altro importo della stessa decisione
                extra = importo(" ".join(v))
                if extra:
                    ultima["importo"] = (ultima["importo"] or 0) + extra
                    ultima["importoTesto"] += " + " + " ".join(x for x in v if re.search(r"\d", x))
    return righe


MESI_IT = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre",
           "novembre", "dicembre"]


def consob() -> list[dict]:
    url = "https://www.consob.it/web/area-pubblica/sanzioni"
    c = I.prendi(url, "text/html", 90)
    (OUT / "consob_pagina.html").write_bytes(c)
    s = BeautifulSoup(c, "lxml")
    righe, mese, visti = [], "", set()
    for el in s.find_all(["strong", "a"]):
        t = testo(el)
        m = re.fullmatch(r"(" + "|".join(MESI_IT) + r") (\d{4})", t.lower())
        if el.name == "strong" and m:
            mese = f"{m.group(2)}-{MESI_IT.index(m.group(1)) + 1:02d}"
            continue
        if el.name == "a" and "dettaglio-sanzione" in el.get("href", "") and el["href"] not in visti:
            visti.add(el["href"])
            tit = el.get("title") or t
            n = re.search(r"Delibera n\.? ?(\d+)", tit)
            righe.append({"mese": mese, "data": mese + "-15" if mese else "", "autorita": "Consob", "area": "Italia",
                          "delibera": n.group(1) if n else "", "titolo": tit[:500],
                          "link": "https://www.consob.it" + el["href"] if el["href"].startswith("/") else el["href"]})
    return righe


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    stato = {}
    for nome, f in (("bce_vigilanza", bce_vigilanza), ("consob", consob)):
        try:
            r = f()
            (OUT / f"{nome}.json").write_text(json.dumps({"aggiornato": date.today().isoformat(), "righe": r},
                                                         ensure_ascii=False, indent=1), encoding="utf-8")
            stato[nome] = {"ok": True, "righe": len(r)}
        except Exception as e:  # noqa: BLE001
            stato[nome] = {"ok": False, "errore": f"{type(e).__name__}: {str(e)[:300]}"}
        print(nome, stato[nome], flush=True)
    (OUT / "stato.json").write_text(json.dumps(stato, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
