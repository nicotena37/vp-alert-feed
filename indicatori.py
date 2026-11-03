"""Indicatori di attenzione per tema (pagina "Temi attuali" del VP Alert).

Ogni giorno raccoglie da fonti istituzionali e dai media quante volte si parla di ciascun tema
(temi_indicatori.json) e tiene un archivio settimanale in archivio/.

Misure e fonti:
  politica     Parlamento UE (interrogazioni), Camera (interrogazioni e mozioni)
  legislatore  EUR-Lex (atti e avvisi UE), Senato (disegni di legge)
  autorita     discorsi BCE, discorsi dei banchieri centrali (BIS), notizie delle autorità lette dal giro VP Alert
  media        Media Cloud (giornali nazionali italiani), ANSA Economia, Sole 24 Ore Finanza
  studiosi     OpenAlex (studi pubblicati)

Uso:  python indicatori.py [--storico N]     (N = settimane da ricostruire all'indietro, dove la fonte lo permette)
Uscite in archivio/:
  elementi/AAAA-MM.jsonl   ogni voce letta (con i temi trovati; per le voci senza tema solo l'identificativo)
  conteggi.csv             conteggi già aggregati dalle fonti che li forniscono (Media Cloud, OpenAlex)
  settimanale.csv          per settimana, tema, misura e fonte: numero di voci e totale della fonte
  indice_temi.csv          per settimana e tema: indice di attenzione (100 = normale) e tendenza
  ultime_voci.json         ultime voci per tema (per la pagina del sito)
  stato_indicatori.json    esito dell'ultimo giro per fonte
Rispetta robots.txt (leggi_feed.robots) e fa una pausa tra due richieste allo stesso sito.
"""
from __future__ import annotations

import csv
import html
import io
import json
import os
import re
import sys
import time
import unicodedata
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

import leggi_feed as L

QUI = Path(__file__).parent
ARCH = QUI / "archivio"
CONF = json.loads((QUI / "temi_indicatori.json").read_text(encoding="utf-8"))
MEDIACLOUD_ITALIA = 34412372          # collezione "Italy - National" (144 testate)
MISURE = ["politica", "legislatore", "autorita", "media", "studiosi"]
SITI_UE = {"BCE", "BCE - Vigilanza bancaria", "EBA", "ESMA", "ESRB", "Commissione europea", "Consiglio UE",
           "Parlamento europeo", "EDPB", "EIOPA"}
SITI_MONDO = {"BIS", "FSB"}
SITI_MEDIA = {"Teleborsa"}
# testate giornalistiche e specializzate attendibili (solo feed RSS pubblici; robots.txt rispettato da prendi())
MEDIA_AFFIDABILI = [
    ("Il Sole 24 Ore - Economia", "https://www.ilsole24ore.com/rss/economia.xml", "Italia"),
    ("Il Sole 24 Ore - Norme e tributi", "https://www.ilsole24ore.com/rss/norme-e-tributi.xml", "Italia"),
    ("Corriere della Sera - Economia", "https://xml2.corriereobjects.it/rss/economia.xml", "Italia"),
    ("la Repubblica - Economia", "https://www.repubblica.it/rss/economia/rss2.0.xml", "Italia"),
    ("ANSA - Europa", "https://www.ansa.it/europa/notizie/rss.xml", "UE"),
    ("FIRSTonline", "https://www.firstonline.info/feed/", "Italia"),
    ("Agenda Digitale", "https://www.agendadigitale.eu/feed/", "Italia"),
    ("DirittoBancario", "https://www.dirittobancario.it/feed/", "Italia"),
    ("Euractiv - Economia", "https://www.euractiv.com/sections/economy-jobs/feed/", "UE"),
    ("Politico Europe - Servizi finanziari", "https://www.politico.eu/section/financial-services/feed/", "UE"),
]


# ---------------------------------------------------------------- temi
def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", (s or "").replace("’", "'")).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s.lower())


def _rx(termini: list[str]) -> re.Pattern | None:
    parti = []
    for t in termini:
        t = norm(t).strip()
        if not t:
            continue
        coda = r"\w*" if t.endswith("*") else ""
        t = re.escape(t.rstrip("*")).replace(r"\ ", r"[\s\-]+")
        parti.append(t + coda)
    return re.compile(r"(?<!\w)(?:" + "|".join(parti) + r")(?!\w)") if parti else None


def _rx_sigle(sigle: list[str]) -> re.Pattern | None:
    if not sigle:
        return None
    # una sigla non conta se è attaccata ad altre parole tutte maiuscole (titoli in maiuscolo: "DECISIONE AI SENSI")
    return re.compile(r"(?<![\w])(?<![A-Z]{2} )(?:" + "|".join(re.escape(s) for s in sigle) + r")(?![\w])(?! [A-Z]{2})")


CTX_BANCA = _rx(CONF["contesto_banca"])
TEMI = []
for t in CONF["temi"]:
    ctx = t.get("contesto")
    TEMI.append({**t, "_rx": _rx(t["it"] + t["en"]), "_sig": _rx_sigle(t.get("sigle", [])),
                 "_ctx": CTX_BANCA if ctx is True else (_rx(ctx) if ctx else None)})


def temi_di(titolo: str, testo: str = "") -> dict[str, str]:
    """{tema: parola che l'ha fatto scattare}"""
    grezzo = f"{titolo} {testo}"
    n = norm(grezzo)
    out = {}
    for t in TEMI:
        m = (t["_rx"] and t["_rx"].search(n)) or (t["_sig"] and t["_sig"].search(grezzo))
        if m and (t["_ctx"] is None or t["_ctx"].search(n)):
            out[t["tema"]] = m.group(0)
    return out


# ---------------------------------------------------------------- date
def lunedi(d: date) -> date:
    return d - timedelta(days=d.weekday())


def sett(d: date) -> str:
    a, s, _ = d.isocalendar()
    return f"{a}-W{s:02d}"


def ita(d: date) -> str:
    return d.strftime("%d/%m/%Y")


def a_data(s: str) -> date | None:
    s = (s or "").strip()
    if re.fullmatch(r"\d{8}", s):
        s = f"{s[:4]}-{s[4:6]}-{s[6:]}"
    iso = L.data_iso(s) or s[:10]
    try:
        return date.fromisoformat(iso)
    except ValueError:
        return None


# ---------------------------------------------------------------- scarico
def prendi(url: str, accetta: str | None = None, timeout: int = 60) -> bytes:
    ok, motivo = L.robots(url)
    if not ok:
        raise PermissionError(motivo)
    L.TIMEOUT = timeout
    for tentativo in range(3):
        stato, c = L.scarica(url, accetta)
        if stato == 200:
            return c
        if stato in (429, 502, 503, 504) and tentativo < 2:
            time.sleep(20 * (tentativo + 1))
            continue
        raise RuntimeError(f"HTTP {stato}")
    raise RuntimeError("nessuna risposta")


def sparql(endpoint: str, q: str, formato: str = "application/sparql-results+json", timeout: int = 120) -> list[dict]:
    c = prendi(f"{endpoint}?query={quote(q, safe='')}&format={quote(formato, safe='')}", "application/sparql-results+json, application/json", timeout)
    return [{k: v["value"] for k, v in b.items()} for b in json.loads(c)["results"]["bindings"]]


def voce(fonte, misura, area, ident, d, titolo, testo="", link=""):
    return {"fonte": fonte, "misura": misura, "area": area, "id": str(ident), "data": d.isoformat() if d else "",
            "titolo": L.pulisci(titolo)[:300], "link": link, "_testo": testo}


# ---------------------------------------------------------------- fonti a voci
def pe_interrogazioni(dal: date, al: date) -> list[dict]:
    tf = "one-week" if (date.today() - dal).days <= 8 else "one-month"
    c = prendi(f"https://data.europarl.europa.eu/api/v2/parliamentary-questions/feed?timeframe={tf}",
               "application/atom+xml", 240)
    from lxml import etree
    radice = etree.fromstring(c, etree.XMLParser(recover=True, huge_tree=True, resolve_entities=False, no_network=True))
    ns = {"a": "http://www.w3.org/2005/Atom"}
    out = []
    for e in radice.findall("a:entry", ns):
        tit = (e.findtext("a:title", "", ns) or "").strip()
        cat = " ".join(x.get("term", "") + x.get("scheme", "") for x in e.findall("a:category", ns))
        if tit.lower().startswith("answer for question") or "ANSWER" in cat:
            continue
        ident = (e.findtext("a:id", "", ns) or "").rsplit("/", 1)[-1]
        d = a_data(e.findtext("a:updated", "", ns))
        out.append(voce("Parlamento UE - interrogazioni", "politica", "UE", ident, d, tit,
                        link=f"https://www.europarl.europa.eu/doceo/document/{ident}_IT.html"))
    return out


def camera_interrogazioni(dal: date, al: date) -> list[dict]:
    dal = min(dal, date.today() - timedelta(days=60))       # i dati della Camera arrivano con qualche settimana di ritardo
    q = f"""PREFIX dc: <http://purl.org/dc/elements/1.1/> PREFIX dct: <http://purl.org/dc/terms/>
SELECT ?s ?d ?t (SAMPLE(?ds) AS ?desc) (SAMPLE(?rl) AS ?rel) WHERE {{
 ?s a <http://dati.camera.it/ocd/aic> ; dc:date ?d ; dc:title ?t .
 OPTIONAL {{ ?s dc:description ?ds }} OPTIONAL {{ ?s dc:relation ?rl }}
 FILTER(?d >= "{dal:%Y%m%d}" && ?d <= "{al:%Y%m%d}") }} GROUP BY ?s ?d ?t LIMIT 10000"""
    out = []
    for r in sparql("https://dati.camera.it/sparql", q, "application/json"):
        desc = html.unescape(r.get("desc", ""))
        corpo = re.split(r"seduta n\. ?\d+", desc, maxsplit=1)[-1].strip()
        corpo = re.sub(r"^[A-ZÀ-Ü' ]+\s*\.\s*[—-]\s*", "", corpo)          # toglie "COGNOME . —"
        tipo = re.match(r"[A-ZÀ-Ü' ]+?(?= \d)", r["t"])
        titolo = f"{(tipo.group(0).capitalize() if tipo else 'Atto')} {(re.search(r"\d+/\d+", r["t"]) or re.search(r"", "")).group(0)}: {corpo[:220]}"
        out.append(voce("Camera - interrogazioni e mozioni", "politica", "Italia", r["s"].rsplit("/", 1)[-1],
                        a_data(r["d"]), titolo, corpo[:600], r.get("rel") or r["s"]))
    return out


def senato_ddl(dal: date, al: date) -> list[dict]:
    dal = min(dal, date.today() - timedelta(days=60))
    q = f"""PREFIX osr: <http://dati.senato.it/osr/>
SELECT ?s ?d ?t WHERE {{ ?s a osr:Ddl ; osr:dataPresentazione ?d ; osr:titolo ?t .
 FILTER(STR(?d) >= "{dal.isoformat()}" && STR(?d) <= "{al.isoformat()}") }} LIMIT 5000"""
    return [voce("Senato - disegni di legge", "legislatore", "Italia", r["s"].rsplit("/", 1)[-1], a_data(r["d"]),
                 r["t"], link=r["s"]) for r in sparql("https://dati.senato.it/sparql", q)]


def eurlex(dal: date, al: date) -> list[dict]:
    out, visti = [], set()
    inizio = dal
    while inizio <= al:
        fine = min(inizio + timedelta(days=6), al)
        q = f"""PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT ?w ?d ?t WHERE {{ ?w cdm:work_date_document ?d .
 FILTER(?d >= "{inizio.isoformat()}"^^<http://www.w3.org/2001/XMLSchema#date> && ?d <= "{fine.isoformat()}"^^<http://www.w3.org/2001/XMLSchema#date>)
 ?e cdm:expression_belongs_to_work ?w ; cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ITA> ;
    cdm:expression_title ?t . }} LIMIT 10000"""
        for r in sparql("https://publications.europa.eu/webapi/rdf/sparql", q, timeout=240):
            if r["w"] in visti or re.match(r"tassi di cambio dell", norm(r["t"])):
                continue
            visti.add(r["w"])
            out.append(voce("EUR-Lex - atti e avvisi UE", "legislatore", "UE", r["w"].rsplit("/", 1)[-1],
                            a_data(r["d"]), r["t"], link=r["w"]))
        inizio = fine + timedelta(days=1)
    return out


def bce_discorsi(dal: date, al: date, stato: dict) -> list[dict]:
    ultimo = stato.get("bce_discorsi_scaricato", "")
    if ultimo and (date.today() - date.fromisoformat(ultimo)).days < 6 and (date.today() - dal).days <= 15:
        return []                                             # archivio completo: basta scaricarlo una volta a settimana
    c = prendi("https://www.ecb.europa.eu/press/key/shared/data/all_ECB_speeches.csv", "text/csv, */*", 240)
    stato["bce_discorsi_scaricato"] = date.today().isoformat()
    out = []
    csv.field_size_limit(10**8)
    for r in csv.DictReader(io.StringIO(c.decode("utf-8", "replace")), delimiter="|"):
        d = a_data(r.get("date", ""))
        if d and dal <= d <= al:
            out.append(voce("BCE - discorsi", "autorita", "UE", f"{d}|{r.get('title', '')[:120]}", d,
                            r.get("title", ""), f"{r.get('subtitle', '')} {r.get('contents', '')[:20000]}"))
    return out


def rss(fonte: str, url: str, misura: str, area: str) -> list[dict]:
    c = prendi(url)
    sito = {"sito": fonte}
    out = []
    for n in L.leggi_rss(sito, {"nome": fonte, "categoria": ""}, c):
        out.append(voce(fonte, misura, area, n["link"] or n["titolo"], a_data(n["data"]), n["titolo"], n["descrizione"],
                        n["link"]))
    return out


def feed_vpalert(dal: date, al: date) -> list[dict]:
    out = []
    for f in sorted((QUI / "dati").glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if not isinstance(d, dict) or "notizie" not in d:
            continue
        for n in d["notizie"]:
            sito = n.get("sito", d.get("sito", ""))
            area = "UE" if sito in SITI_UE else "Mondo" if sito in SITI_MONDO else "Italia"
            misura = "media" if sito in SITI_MEDIA else "autorita"
            out.append(voce(f"Autorità (giro VP Alert) - {sito}", misura, area, n.get("link") or n.get("titolo"),
                            a_data(n.get("data", "")), n.get("titolo", ""), n.get("descrizione", ""), n.get("link", "")))
    return out


# ---------------------------------------------------------------- fonti a conteggi
def mediacloud(dal: date, al: date) -> list[dict]:
    chiave = os.environ.get("MEDIACLOUD_API_KEY", "").strip()
    if not chiave:
        raise RuntimeError("manca il segreto MEDIACLOUD_API_KEY")
    import mediacloud.api as mc
    s = mc.SearchApi(chiave)
    righe = []
    for t in TEMI:
        if not t.get("mc"):
            continue
        punti = s.story_count_over_time(t["mc"], dal, al, collection_ids=[MEDIACLOUD_ITALIA])
        per_sett = defaultdict(lambda: [0, 0])
        for p in punti:
            k = lunedi(p["date"])
            per_sett[k][0] += p.get("count", 0)
            per_sett[k][1] += p.get("total_count", 0)
        for k, (n, tot) in per_sett.items():
            righe.append({"settimana": sett(k), "dal": k.isoformat(), "fonte": "Media Cloud - giornali italiani",
                          "misura": "media", "area": "Italia", "tema": t["tema"], "valore": n, "totale": tot})
    return righe


def openalex(settimane: list[date]) -> list[dict]:
    righe = []
    for k in settimane:
        for t in TEMI:
            if not t.get("oa"):
                continue
            chiave = os.environ.get("OPENALEX_API_KEY", "").strip()
            url = (f"https://api.openalex.org/works?search={quote(t['oa'])}&per-page=1&select=id"
                   f"&filter=from_publication_date:{k},to_publication_date:{k + timedelta(days=6)}"
                   + (f"&api_key={chiave}" if chiave else ""))
            n = json.loads(prendi(url, "application/json", 60))["meta"]["count"]
            righe.append({"settimana": sett(k), "dal": k.isoformat(), "fonte": "OpenAlex - studi", "misura": "studiosi",
                          "area": "Mondo", "tema": t["tema"], "valore": n, "totale": ""})
    return righe


# ---------------------------------------------------------------- archivio
def carica_elementi() -> dict[tuple, dict]:
    tutti = {}
    for f in sorted((ARCH / "elementi").glob("*.jsonl")):
        for riga in f.read_text(encoding="utf-8").splitlines():
            if riga.strip():
                e = json.loads(riga)
                tutti[(e["fonte"], e["id"])] = e
    return tutti


def salva_elementi(tutti: dict[tuple, dict]) -> None:
    per_mese = defaultdict(list)
    for e in tutti.values():
        per_mese[(e.get("data") or "0000-00")[:7]].append(e)
    (ARCH / "elementi").mkdir(parents=True, exist_ok=True)
    for mese, el in per_mese.items():
        el.sort(key=lambda e: (e.get("data", ""), e["fonte"], e["id"]))
        (ARCH / "elementi" / f"{mese}.jsonl").write_text(
            "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in el), encoding="utf-8")


def unisci_conteggi(nuove: list[dict]) -> list[dict]:
    f = ARCH / "conteggi.csv"
    righe = {}
    if f.exists():
        for r in csv.DictReader(f.open(encoding="utf-8")):
            righe[(r["settimana"], r["fonte"], r["tema"])] = r
    for r in nuove:
        righe[(r["settimana"], r["fonte"], r["tema"])] = {k: str(v) for k, v in r.items()}
    campi = ["settimana", "dal", "fonte", "misura", "area", "tema", "valore", "totale"]
    with f.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, campi)
        w.writeheader()
        for k in sorted(righe):
            w.writerow({c: righe[k].get(c, "") for c in campi})
    return list(righe.values())


def calcola(tutti: dict[tuple, dict], conteggi: list[dict], oggi: date) -> None:
    corrente = lunedi(oggi)
    val = defaultdict(int)          # (sett, tema, misura, fonte, area) -> n
    tot = defaultdict(int)          # (sett, fonte) -> totale voci della fonte
    info = {}
    for e in tutti.values():
        d = a_data(e.get("data", ""))
        if not d:
            continue
        k = lunedi(d)
        tot[(k, e["fonte"])] += 1
        for tema in e.get("temi", []):
            val[(k, tema, e["misura"], e["fonte"], e["area"])] += 1
    for r in conteggi:
        k = date.fromisoformat(r["dal"])
        val[(k, r["tema"], r["misura"], r["fonte"], r["area"])] += int(r["valore"] or 0)
        if r.get("totale"):
            tot[(k, r["fonte"])] = int(r["totale"])
    with (ARCH / "settimanale.csv").open("w", encoding="utf-8", newline="") as h:
        w = csv.writer(h)
        w.writerow(["settimana", "dal", "al", "in_corso", "tema", "area_tema", "misura", "fonte", "area_geografica",
                    "valore", "totale_fonte"])
        area_tema = {t["tema"]: t["area"] for t in TEMI}
        for (k, tema, mis, fonte, area), n in sorted(val.items()):
            w.writerow([sett(k), ita(k), ita(k + timedelta(days=6)), "sì" if k == corrente else "", tema,
                        area_tema.get(tema, ""), mis, fonte, area, n, tot.get((k, fonte), "")])
    # indice: per tema e misura, settimana confrontata con la media delle 8 precedenti (100 = normale)
    per_mis = defaultdict(int)
    for (k, tema, mis, _f, _a), n in val.items():
        per_mis[(k, tema, mis)] += n
    settimane = sorted({k for k, *_ in per_mis})
    righe = []
    for tema in [t["tema"] for t in TEMI]:
        for k in settimane:
            if k > corrente:
                continue
            rapporti, dett = [], {}
            for mis in MISURE:
                if mis == "studiosi" and k > corrente - timedelta(weeks=4):
                    dett[mis] = str(per_mis.get((k, tema, mis), 0)) + " (in indicizzazione)"
                    continue                                 # gli studi arrivano con settimane di ritardo
                prec = [per_mis.get((k - timedelta(weeks=i), tema, mis), 0) for i in range(1, 9)
                        if (k - timedelta(weeks=i)) in settimane]
                v = per_mis.get((k, tema, mis), 0)
                attiva = any(per_mis.get((s, tema, mis), 0) for s in settimane)
                if len(prec) >= 3 and attiva:
                    r = (v + 3) / (sum(prec) / len(prec) + 3)          # +3: pochi casi non fanno impennare l indice
                    rapporti.append(r)
                    dett[mis] = f"{v} ({round(100 * r)})"
                else:
                    dett[mis] = str(v) if attiva else ""
            indice = round(100 * sum(rapporti) / len(rapporti)) if rapporti else ""
            tend = ("Dati insufficienti" if indice == "" else "In forte crescita" if indice >= 150 else
                    "In crescita" if indice >= 115 else "In calo" if indice <= 70 else "Stabile")
            righe.append([sett(k), ita(k), "sì" if k == corrente else "", tema, indice, tend,
                          sum(per_mis.get((k, tema, m), 0) for m in MISURE if m != "studiosi")] + [dett[m] for m in MISURE])
    with (ARCH / "indice_temi.csv").open("w", encoding="utf-8", newline="") as h:
        w = csv.writer(h)
        w.writerow(["settimana", "dal", "in_corso", "tema", "indice_attenzione", "tendenza", "voci_totali (senza studi)"]
                   + [f"{m} (voci e indice)" for m in MISURE])
        w.writerows(righe)
    # ultime voci per tema (ultime 3 settimane)
    limite = (oggi - timedelta(days=21)).isoformat()
    ultime = defaultdict(list)
    for e in sorted(tutti.values(), key=lambda e: e.get("data", ""), reverse=True):
        if e.get("data", "") >= limite:
            for tema in e.get("temi", []):
                if len(ultime[tema]) < 25:
                    ultime[tema].append({k: e[k] for k in ("data", "fonte", "misura", "area", "titolo", "link")})
    (ARCH / "ultime_voci.json").write_text(json.dumps(ultime, ensure_ascii=False, indent=1), encoding="utf-8")


# ---------------------------------------------------------------- giro
def main() -> int:
    oggi = date.today()
    storico = int(sys.argv[sys.argv.index("--storico") + 1]) if "--storico" in sys.argv else 0
    dal = lunedi(oggi) - timedelta(weeks=max(storico, 2))
    al = oggi
    ARCH.mkdir(exist_ok=True)
    f_stato = ARCH / "stato_indicatori.json"
    stato = json.loads(f_stato.read_text(encoding="utf-8")) if f_stato.exists() else {}
    esito = {}
    tutti = carica_elementi()
    nuove = 0

    def raccogli(nome, funzione):
        nonlocal nuove
        t0 = time.time()
        try:
            voci = funzione()
        except Exception as e:  # noqa: BLE001
            esito[nome] = {"ok": False, "errore": f"{type(e).__name__}: {str(e)[:300]}"}
            print(f"!! {nome}: {esito[nome]['errore']}", flush=True)
            return
        con_tema = 0
        for v in voci:
            testo = v.pop("_testo", "")
            trovati = temi_di(v["titolo"], testo)
            v["temi"], v["parole"] = list(trovati), list(trovati.values())
            con_tema += bool(v["temi"])
            k = (v["fonte"], v["id"])
            if k not in tutti:
                nuove += 1
            tutti[k] = v if v["temi"] else {c: v[c] for c in ("fonte", "misura", "area", "id", "data", "temi")}
            if not v["temi"]:
                v.pop("parole", None)
        esito[nome] = {"ok": True, "voci": len(voci), "con_tema": con_tema, "secondi": round(time.time() - t0)}
        print(f"{nome}: {len(voci)} voci, {con_tema} con tema", flush=True)

    raccogli("Parlamento UE - interrogazioni", lambda: pe_interrogazioni(dal, al))
    raccogli("Camera - interrogazioni", lambda: camera_interrogazioni(dal, al))
    raccogli("Senato - disegni di legge", lambda: senato_ddl(dal, al))
    raccogli("EUR-Lex", lambda: eurlex(dal, al))
    raccogli("BCE - discorsi", lambda: bce_discorsi(dal, al, stato))
    raccogli("BIS - discorsi", lambda: rss("BIS - discorsi dei banchieri centrali",
                                           "https://www.bis.org/doclist/cbspeeches.rss", "autorita", "Mondo"))
    raccogli("ANSA Economia", lambda: rss("ANSA - Economia", "https://www.ansa.it/sito/notizie/economia/economia_rss.xml",
                                          "media", "Italia"))
    raccogli("Sole 24 Ore Finanza", lambda: rss("Il Sole 24 Ore - Finanza", "https://www.ilsole24ore.com/rss/finanza.xml",
                                                "media", "Italia"))
    for nome, url, area in MEDIA_AFFIDABILI:                  # testate attendibili (economia, finanza, diritto, UE)
        raccogli(nome, lambda nome=nome, url=url, area=area: rss(nome, url, "media", area))
    raccogli("Autorità (giro VP Alert)", lambda: feed_vpalert(dal, al))

    conteggi = []
    try:
        conteggi += mediacloud(dal, oggi - timedelta(days=1))
        esito["Media Cloud"] = {"ok": True, "righe": len(conteggi)}
    except Exception as e:  # noqa: BLE001
        esito["Media Cloud"] = {"ok": False, "errore": f"{type(e).__name__}: {str(e)[:300]}"}
    print("Media Cloud:", esito["Media Cloud"], flush=True)
    # OpenAlex: settimane complete; nel giro normale solo le ultime 2 (gli studi vengono indicizzati con ritardo)
    sett_oa = [lunedi(oggi) - timedelta(weeks=i) for i in range(1, (storico or 2) + 1)]
    if not storico and oggi.weekday() != 0:
        sett_oa = []                                         # nel giro normale: una volta a settimana (lunedì)
    try:
        r = openalex(sett_oa)
        conteggi += r
        esito["OpenAlex"] = {"ok": True, "righe": len(r)}
    except Exception as e:  # noqa: BLE001
        esito["OpenAlex"] = {"ok": False, "errore": f"{type(e).__name__}: {str(e)[:300]}"}
    print("OpenAlex:", esito["OpenAlex"], flush=True)

    salva_elementi(tutti)
    tutti_conteggi = unisci_conteggi(conteggi)
    calcola(tutti, tutti_conteggi, oggi)
    stato.update({"ultimo_giro": datetime.now(timezone.utc).isoformat(timespec="seconds"), "dal": dal.isoformat(),
                  "voci_nuove": nuove, "voci_in_archivio": len(tutti), "fonti": esito})
    f_stato.write_text(json.dumps(stato, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(stato, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
