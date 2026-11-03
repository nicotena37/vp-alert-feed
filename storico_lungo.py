"""Storico lungo mensile per la pagina Statistiche e previsioni del VP Alert.

Ricostruisce, mese per mese dal 2016, quanto si è parlato di ciascun tema (temi_indicatori.json) in fonti ufficiali
e verificabili, così da poter provare i metodi di previsione su molti anni di dati veri:

  legislatore  EUR-Lex (Ufficio pubblicazioni UE, endpoint SPARQL ufficiale): atti adottati e proposte della Commissione
               Senato (dati.senato.it): disegni di legge presentati
  politica     Camera (dati.camera.it): interrogazioni e mozioni
  autorita     BCE: archivio completo dei discorsi (file CSV pubblicato dalla BCE)
  media        Media Cloud (archivio dei giornali online italiani, collezione Italy - National)
  studiosi     OpenAlex (studi pubblicati)

Uso:  python storico_lungo.py [--dal 2016-01] [--solo eurlex,camera,...]
Uscite in archivio/storico/:
  <fonte>.csv            mese, tema, tipo, valore, totale_fonte   (una riga per mese e tema; totale = voci lette nel mese)
  eurlex_voci.jsonl      atti e proposte UE con almeno un tema (data, tipo, titolo, link, temi): servono per spiegare le previsioni
  stato_<fonte>.json     esito per fonte
Si riprende da dove si era fermato: i mesi già scaricati non si riscaricano (tranne gli ultimi due).
"""
from __future__ import annotations

import csv
import io
import json
import os
import sys
import time
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote

import indicatori as I

QUI = Path(__file__).parent
OUT = QUI / "archivio" / "storico"
RT = "http://publications.europa.eu/resource/authority/resource-type/"
TIPI_ATTO = {"REG", "REG_IMPL", "REG_DEL", "DIR", "DIR_IMPL", "DIR_DEL", "DEC", "DEC_IMPL", "DEC_DEL", "REG_FINANC"}
TIPI_PROP = {"PROP_REG", "PROP_DIR", "PROP_DEC", "PROP_REG_IMPL", "PROP_DIR_IMPL", "PROP_DEC_IMPL"}
TIPI_COM = {"COMMUNIC", "WHITE_PAPER", "GREEN_PAPER", "REPORT", "STAFF_WORK_DOC"}


def mesi(dal: str, al: date) -> list[str]:
    a, m = map(int, dal.split("-"))
    out = []
    while (a, m) <= (al.year, al.month):
        out.append(f"{a}-{m:02d}")
        a, m = (a + 1, 1) if m == 12 else (a, m + 1)
    return out


def limiti(mese: str) -> tuple[date, date]:
    a, m = map(int, mese.split("-"))
    inizio = date(a, m, 1)
    fine = (date(a + 1, 1, 1) if m == 12 else date(a, m + 1, 1)) - timedelta(days=1)
    return inizio, fine


class Serie:
    """righe (mese, tema, tipo) -> valore, più il totale della fonte per mese; salvate in <fonte>.csv"""

    def __init__(self, nome: str):
        self.f = OUT / f"{nome}.csv"
        self.val, self.tot = defaultdict(int), {}
        if self.f.exists():
            for r in csv.DictReader(self.f.open(encoding="utf-8")):
                self.val[(r["mese"], r["tema"], r["tipo"])] = int(r["valore"])
                if r["totale_fonte"]:
                    self.tot[(r["mese"], r["tipo"])] = int(r["totale_fonte"])

    def fatti(self) -> set[str]:
        return {m for (m, _t) in self.tot}

    def azzera(self, mese: str) -> None:
        for k in [k for k in self.val if k[0] == mese]:
            del self.val[k]
        for k in [k for k in self.tot if k[0] == mese]:
            del self.tot[k]

    def salva(self) -> None:
        with self.f.open("w", encoding="utf-8", newline="") as h:
            w = csv.writer(h)
            w.writerow(["mese", "tema", "tipo", "valore", "totale_fonte"])
            chiavi = set(self.val) | {(m, "", t) for (m, t) in self.tot}
            for (m, tema, tipo) in sorted(chiavi):
                if tema == "" and (m, tema, tipo) not in self.val:
                    w.writerow([m, "", tipo, 0, self.tot.get((m, tipo), "")])
                elif tema:
                    w.writerow([m, tema, tipo, self.val[(m, tema, tipo)], self.tot.get((m, tipo), "")])


def da_rifare(s: Serie, lista: list[str]) -> list[str]:
    fatti = s.fatti()
    return [m for m in lista if m not in fatti or m >= lista[-2]]


# ---------------------------------------------------------------- EUR-Lex
def eurlex(lista: list[str]) -> None:
    s = Serie("eurlex")
    voci_f = OUT / "eurlex_voci.jsonl"
    voci = {}
    if voci_f.exists():
        for riga in voci_f.open(encoding="utf-8"):
            v = json.loads(riga)
            voci[v["id"]] = v
    tipi = " ".join(f"<{RT}{t}>" for t in sorted(TIPI_ATTO | TIPI_PROP | TIPI_COM))
    for mese in da_rifare(s, lista):
        inizio, fine = limiti(mese)
        q = f"""PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT ?w ?d ?t ?rt WHERE {{ ?w cdm:work_date_document ?d ; cdm:work_has_resource-type ?rt .
 VALUES ?rt {{ {tipi} }}
 FILTER(?d >= "{inizio.isoformat()}"^^<http://www.w3.org/2001/XMLSchema#date> && ?d <= "{fine.isoformat()}"^^<http://www.w3.org/2001/XMLSchema#date>)
 ?e cdm:expression_belongs_to_work ?w ; cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ITA> ;
    cdm:expression_title ?t . }} LIMIT 20000"""
        righe = I.sparql("https://publications.europa.eu/webapi/rdf/sparql", q, timeout=300)
        s.azzera(mese)
        visti = set()
        tot = defaultdict(int)
        for r in righe:
            if r["w"] in visti:
                continue
            visti.add(r["w"])
            rt = r["rt"].rsplit("/", 1)[-1]
            tipo = "atto" if rt in TIPI_ATTO else "proposta" if rt in TIPI_PROP else "comunicazione"
            tot[tipo] += 1
            temi = I.temi_di(r["t"])
            for tema in temi:
                s.val[(mese, tema, tipo)] += 1
            if temi:
                ident = r["w"].rsplit("/", 1)[-1]
                voci[ident] = {"id": ident, "data": r["d"][:10], "tipo": tipo, "rt": rt, "titolo": I.L.pulisci(r["t"])[:400],
                               "link": r["w"], "temi": sorted(temi)}
        for tipo in ("atto", "proposta", "comunicazione"):
            s.tot[(mese, tipo)] = tot[tipo]
        print(f"EUR-Lex {mese}: {len(visti)} documenti", flush=True)
        s.salva()
        with voci_f.open("w", encoding="utf-8") as h:
            for v in sorted(voci.values(), key=lambda v: v["data"]):
                h.write(json.dumps(v, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------- Camera e Senato
def camera(lista: list[str]) -> None:
    s = Serie("camera")
    errori = 0
    for mese in da_rifare(s, lista):
        inizio, fine = limiti(mese)
        voci, ok = [], True
        d = inizio
        while d <= fine:                      # settimana per settimana: la query sul mese intero va in errore (HTTP 502)
            f = min(d + timedelta(days=6), fine)
            q = f"""PREFIX dc: <http://purl.org/dc/elements/1.1/>
SELECT ?s ?t ?ds WHERE {{
 ?s a <http://dati.camera.it/ocd/aic> ; dc:date ?d ; dc:title ?t . OPTIONAL {{ ?s dc:description ?ds }}
 FILTER(?d >= "{d:%Y%m%d}" && ?d <= "{f:%Y%m%d}") }} LIMIT 20000"""
            try:
                righe = I.sparql("https://dati.camera.it/sparql", q, "application/json", timeout=180)
            except Exception as e:  # noqa: BLE001
                print(f"Camera {d}: {e}", flush=True)
                ok = False
                break
            visti = {}
            for r in righe:
                visti.setdefault(r["s"], {"titolo": r["t"], "_testo": r.get("ds", "")[:2000]})
            voci += visti.values()
            d = f + timedelta(days=1)
            time.sleep(1)
        if not ok:
            errori += 1
            if errori >= 15:
                raise RuntimeError("troppi errori dalla Camera")
            continue
        s.azzera(mese)
        for v in voci:
            for tema in I.temi_di(v["titolo"], v.get("_testo", "")):
                s.val[(mese, tema, "interrogazione")] += 1
        s.tot[(mese, "interrogazione")] = len(voci)
        print(f"Camera {mese}: {len(voci)}", flush=True)
        if mese.endswith("06") or mese.endswith("12") or mese == lista[-1]:
            s.salva()
    s.salva()


def senato(lista: list[str]) -> None:
    s = Serie("senato")
    for mese in da_rifare(s, lista):
        inizio, fine = limiti(mese)
        q = f"""PREFIX osr: <http://dati.senato.it/osr/>
SELECT ?s ?t WHERE {{ ?s a osr:Ddl ; osr:dataPresentazione ?d ; osr:titolo ?t .
 FILTER(STR(?d) >= "{inizio.isoformat()}" && STR(?d) <= "{fine.isoformat()}") }} LIMIT 20000"""
        voci = I.sparql("https://dati.senato.it/sparql", q)
        s.azzera(mese)
        for v in voci:
            for tema in I.temi_di(v["t"]):
                s.val[(mese, tema, "ddl")] += 1
        s.tot[(mese, "ddl")] = len(voci)
        print(f"Senato {mese}: {len(voci)}", flush=True)
    s.salva()


# ---------------------------------------------------------------- BCE discorsi (archivio completo)
def bce(lista: list[str]) -> None:
    s = Serie("bce_discorsi")
    c = I.prendi("https://www.ecb.europa.eu/press/key/shared/data/all_ECB_speeches.csv", "text/csv, */*", 300)
    csv.field_size_limit(10**8)
    for m in lista:
        s.azzera(m)
    tot = defaultdict(int)
    for r in csv.DictReader(io.StringIO(c.decode("utf-8", "replace")), delimiter="|"):
        d = I.a_data(r.get("date", ""))
        if not d:
            continue
        mese = f"{d.year}-{d.month:02d}"
        if mese not in lista:
            continue
        tot[mese] += 1
        for tema in I.temi_di(r.get("title", ""), f"{r.get('subtitle', '')} {r.get('contents', '')[:20000]}"):
            s.val[(mese, tema, "discorso")] += 1
    for m in lista:
        s.tot[(m, "discorso")] = tot[m]
    s.salva()
    print(f"BCE: {sum(tot.values())} discorsi", flush=True)


# ---------------------------------------------------------------- Media Cloud e OpenAlex (conteggi)
def mediacloud(lista: list[str]) -> None:
    chiave = os.environ.get("MEDIACLOUD_API_KEY", "").strip()
    if not chiave:
        raise RuntimeError("manca il segreto MEDIACLOUD_API_KEY")
    import mediacloud.api as mc
    api = mc.SearchApi(chiave)
    s = Serie("mediacloud")
    rifare = da_rifare(s, lista)
    if not rifare:
        return
    for anno in sorted({m[:4] for m in rifare}):
        mm = [m for m in rifare if m.startswith(anno)]
        dal, al = limiti(mm[0])[0], min(limiti(mm[-1])[1], date.today() - timedelta(days=1))
        for t in I.TEMI:
            if not t.get("mc"):
                continue
            for tentativo in range(3):
                try:
                    punti = api.story_count_over_time(t["mc"], dal, al, collection_ids=[I.MEDIACLOUD_ITALIA])
                    break
                except Exception as e:  # noqa: BLE001
                    if tentativo == 2:
                        raise
                    print(f"Media Cloud {anno} {t['tema']}: {e}; riprovo", flush=True)
                    time.sleep(30)
            per_m = defaultdict(lambda: [0, 0])
            for p in punti:
                d = p["date"] if isinstance(p["date"], date) else date.fromisoformat(str(p["date"])[:10])
                k = f"{d.year}-{d.month:02d}"
                per_m[k][0] += p.get("count", 0)
                per_m[k][1] += p.get("total_count", 0)
            for k in mm:
                s.val[(k, t["tema"], "articolo")] = per_m[k][0]
                if per_m[k][1]:
                    s.tot[(k, "articolo")] = per_m[k][1]
            time.sleep(1.5)
        s.salva()
        print(f"Media Cloud {anno}: fatto", flush=True)


def openalex(lista: list[str]) -> None:
    s = Serie("openalex")
    chiave = os.environ.get("OPENALEX_API_KEY", "").strip()
    for mese in da_rifare(s, lista):
        inizio, fine = limiti(mese)
        for t in I.TEMI:
            if not t.get("oa"):
                continue
            url = (f"https://api.openalex.org/works?search={quote(t['oa'])}&per-page=1&select=id"
                   f"&filter=from_publication_date:{inizio},to_publication_date:{fine}"
                   + (f"&api_key={chiave}" if chiave else "&mailto=vp-alert-feed@users.noreply.github.com"))
            s.val[(mese, t["tema"], "studio")] = json.loads(I.prendi(url, "application/json", 60))["meta"]["count"]
            time.sleep(0.15)
        s.tot[(mese, "studio")] = 0
        if mese.endswith("12") or mese == lista[-1]:
            s.salva()
        print(f"OpenAlex {mese}", flush=True)
    s.salva()


FONTI = {"eurlex": eurlex, "bce": bce, "senato": senato, "camera": camera, "mediacloud": mediacloud, "openalex": openalex}


def main() -> int:
    dal = sys.argv[sys.argv.index("--dal") + 1] if "--dal" in sys.argv else "2016-01"
    solo = sys.argv[sys.argv.index("--solo") + 1].split(",") if "--solo" in sys.argv else list(FONTI)
    OUT.mkdir(parents=True, exist_ok=True)
    oggi = date.today()
    lista = mesi(dal, oggi)
    for nome in solo:
        f_stato = OUT / f"stato_{nome}.json"
        stato = {}
        t0 = time.time()
        try:
            FONTI[nome](lista)
            stato[nome] = {"ok": True, "quando": oggi.isoformat(), "dal": dal, "secondi": round(time.time() - t0)}
        except Exception as e:  # noqa: BLE001
            stato[nome] = {"ok": False, "quando": oggi.isoformat(), "errore": f"{type(e).__name__}: {str(e)[:300]}",
                           "secondi": round(time.time() - t0)}
            print(f"ERRORE {nome}: {e}", flush=True)
        f_stato.write_text(json.dumps(stato, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
