"""VP ALERT - lettura dei feed RSS degli enti dai server di GitHub (al posto del browser del PC).

Legge fonti_rss.json e scrive in dati/ un file per sito, nello stesso formato che produce leggi_rss.js nel browser
(campi nome_file, sito, origine, letto_il, feed, allarmi, notizie): rss.py li usa senza modifiche.
Regole di cortesia verso i siti:
  - rispetta il robots.txt di ogni sito (se vieta il feed, il feed non viene letto e lo segnala);
  - si presenta con un nome chiaro (User-Agent) e non si spaccia per un browser;
  - una sola richiesta alla volta e 3 secondi di pausa tra due richieste allo stesso sito.
Uso:  python leggi_feed.py [--solo "Banca d'Italia,UIF"]
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.request
import urllib.robotparser
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from lxml import etree

QUI = Path(__file__).parent
DATI = QUI / "dati"
AGENTE = "Mozilla/5.0 (compatible; VP-Alert-Feed/1.0; lettore RSS per monitoraggio normativo)"
PAUSA = 3.0
TIMEOUT = 25
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre",
        "novembre", "dicembre"]

_ultima: dict[str, float] = {}
_robots: dict[str, tuple[urllib.robotparser.RobotFileParser | None, str]] = {}


def pulisci(s: str | None) -> str:
    s = re.sub(r"<[^>]+>", " ", s or "").replace("&nbsp;", " ").replace("\xa0", " ")
    return re.sub(r"\s+", " ", s).strip()


def scarica(url: str, accetta: str | None = None) -> tuple[int, bytes]:
    host = urlparse(url).netloc
    attesa = _ultima.get(host, 0) + PAUSA - time.time()
    if attesa > 0:
        time.sleep(attesa)
    req = urllib.request.Request(url, headers={"User-Agent": AGENTE, "Accept": accetta or "application/rss+xml, "
                                 "application/xml, text/xml, application/atom+xml, text/html;q=0.8, */*;q=0.5"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    finally:
        _ultima[host] = time.time()


def robots(url: str) -> tuple[bool, str]:
    """(si può leggere?, motivo). Se il sito non risponde nemmeno al robots.txt lo dice."""
    p = urlparse(url)
    base = f"{p.scheme}://{p.netloc}"
    if base not in _robots:
        try:
            stato, testo = scarica(base + "/robots.txt")
        except Exception as e:  # noqa: BLE001
            _robots[base] = (None, f"sito non raggiungibile ({type(e).__name__}: {e})")
        else:
            if True:   # RFC 9309: robots.txt 4xx/assente = nessun divieto; il blocco vero si vede sul feed (HTTP 403)
                rp = urllib.robotparser.RobotFileParser()
                rp.parse(testo.decode("utf-8", "replace").splitlines() if stato == 200 else [])
                _robots[base] = (rp, "")
    rp, motivo = _robots[base]
    if rp is None:
        return False, motivo
    if not rp.can_fetch(AGENTE, url):
        return False, "vietato dal robots.txt del sito"
    return True, ""


def data_iso(s: str) -> str:
    s = (s or "").strip().replace("T ", "T")
    if not s:
        return ""
    try:
        return parsedate_to_datetime(s).date().isoformat()
    except (TypeError, ValueError, IndexError):
        pass
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        pass
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return m.group(0)
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}" if m else ""


def gma(s: str) -> str:
    m = re.search(r"(\d{2})/(\d{2})/(\d{4})", s or "")
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else ""


def _nome(el) -> str:
    return etree.QName(el).localname if isinstance(el.tag, str) else ""


def _testo(voce, nomi: list[str]) -> str:
    figli = [c for c in voce if isinstance(c.tag, str)]
    for n in nomi:
        pref, _, loc = n.rpartition(":")
        for c in figli:
            q = etree.QName(c)
            if q.localname == loc and (not pref or voce.nsmap.get(pref) == q.namespace or c.prefix == pref):
                t = "".join(c.itertext()).strip()
                if t:
                    return t
    return ""


def leggi_rss(sito: dict, f: dict, contenuto: bytes) -> list[dict]:
    radice = etree.fromstring(contenuto, etree.XMLParser(recover=True, resolve_entities=False, no_network=True,
                                                          huge_tree=True))
    if radice is None:
        raise ValueError("XML non valido (feed cambiato?)")
    if not re.fullmatch(r"rss|feed|RDF", _nome(radice), re.I):
        raise ValueError(f"non è un feed RSS/Atom (radice <{_nome(radice)}>)")
    out = []
    for v in radice.iter():
        if _nome(v) not in ("item", "entry"):
            continue
        link = _testo(v, ["link", "guid"])
        if not link:
            l = next((c for c in v if _nome(c) == "link" and c.get("href")), None)
            link = l.get("href") if l is not None else ""
        data = _testo(v, ["pubDate", "pubdate", "date", "updated", "published"]).replace("T ", "T")
        out.append({"sito": sito["sito"], "feed": f["nome"], "categoria": f["categoria"],
                    "titolo": pulisci(_testo(v, ["title"])), "link": link.strip(), "data_originale": data,
                    "data": data_iso(data),
                    "descrizione": pulisci(_testo(v, ["description", "summary", "content", "encoded"]))[:700]})
    return out


def leggi_pagina(sito: dict, f: dict, contenuto: bytes) -> list[dict]:
    """Pagine senza RSS (stessa logica di leggi_rss.js)."""
    out = []
    if f["tipo"] == "ifrs_json":                  # IFRS: l'elenco news è un JSON (resultList: title, date, description, uri)
        mesi_en = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
        for v in json.loads(contenuto).get("resultList", []):
            if v.get("title") in f.get("salta", []):
                continue
            m = re.search(r"(\d{1,2}) (\w{3}) (\d{4})", v.get("date") or "")
            data = f"{m.group(3)}-{mesi_en.index(m.group(2).lower()) + 1:02d}-{int(m.group(1)):02d}" if m else ""
            uri = v.get("uri") or ""
            link = uri if uri.startswith("http") else "https://www.ifrs.org" + uri + ("" if re.search(r"\.\w+$", uri) else ".html")
            out.append({"sito": sito["sito"], "feed": f["nome"], "categoria": f["categoria"],
                        "titolo": pulisci(f"{v.get('title')}: {v.get('description')}"), "link": link,
                        "data_originale": v.get("date"), "data": data, "descrizione": pulisci(v.get("description"))[:700]})
        return out
    d = BeautifulSoup(contenuto, "html.parser")

    def metti(titolo, link, data, descr, **extra):
        out.append({"sito": sito["sito"], "feed": f["nome"], "categoria": f["categoria"], "titolo": pulisci(titolo),
                    "link": re.sub(r"\?redirect=.*$", "", urljoin(f["url"], link or "")), "data_originale": data,
                    "data": gma(data), "descrizione": pulisci(descr)[:700], **extra})

    if f["tipo"] == "consob_sanzioni":
        for e in d.select("div.news-entry"):
            a = e.find("a")
            if not a:
                continue
            t = pulisci(e.get_text(" "))
            m = re.search(r"Data Pubblicazione:\s*([\d/]+)", t, re.I)
            ad = re.search(r"Data adozione:\s*([\d/]+)", t, re.I)
            metti(a.get("title") or a.get_text(" "), a.get("href"), m.group(1) if m else "", t, sanzione=True,
                  data_adozione=gma(ad.group(1)) if ad else "",
                  impugnato=bool(re.search(r"opposizione|ricorso|impugn", t, re.I)))
    elif f["tipo"] == "consob_bollettino":
        for a in d.select('a[href*="/-/delibera"], a[href*="/-/provvedimento"], a[href*="/-/decisione"]'):
            c = a
            for _ in range(4):
                if c is None or re.search(r"Data di pubblicazione", c.get_text(" "), re.I):
                    break
                c = c.parent
            t = pulisci((c or a).get_text(" "))
            m = re.search(r"Data di pubblicazione:\s*([\d/]+)", t, re.I)
            metti(a.get_text(" "), a.get("href"), m.group(1) if m else "", t)
    elif f["tipo"] == "consob_schede":
        for w in d.select(".card-bianca-wrapper"):
            link = next((x for x in w.find_all("a") if re.search(r"comunicato|consultazione|leggi|vai",
                         x.get_text(" ") + (x.get("href") or ""), re.I)), None) or w.find("a")
            el = w.select_one(".immagine-con-testo .text")
            dt = pulisci(el.get_text(" ") if el else "")
            m = re.search(r"(\d{1,2})\s+(\w+)\s+(\d{4})", dt)
            data = ""
            if m and m.group(2).lower() in MESI:
                data = f"{int(m.group(1)):02d}/{MESI.index(m.group(2).lower()) + 1:02d}/{m.group(3)}"
            el_t, el_x = w.select_one(".card .title"), w.select_one(".card .text")
            tit, txt = pulisci(el_t.get_text(" ") if el_t else ""), pulisci(el_x.get_text(" ") if el_x else "")
            if len(tit) < 40 and txt:
                tit = f"{tit}: {txt[:220]}"
            metti(tit, link.get("href") if link else "", data, txt)
    elif f["tipo"] == "consob_newsletter":         # Consob Informa: ultimo numero con le notizie della settimana
        visti = set()
        for a in d.select('a[href*="/-/consob-informa-"]'):
            tit = pulisci(a.get_text(" "))
            base = re.sub(r"[?#].*$", "", a.get("href") or "")
            if not re.match(r"Consob Informa", tit, re.I) or base in visti:
                continue
            visti.add(base)
            m = re.search(r"(\d{1,2})\s+(\w+)\s+(\d{4})", tit)
            data = (f"{int(m.group(1)):02d}/{MESI.index(m.group(2).lower()) + 1:02d}/{m.group(3)}"
                    if m and m.group(2).lower() in MESI else "")
            notizie = [pulisci(x.get_text(" ")) for x in d.find_all("a")
                       if re.sub(r"[?#].*$", "", x.get("href") or "") == base and "#notizia" in (x.get("href") or "")]
            metti(f"Newsletter {tit}", base, data, "Le notizie della settimana: " + "; ".join(notizie))
    elif f["tipo"] == "pagina_aggiornamenti":      # pagina senza RSS con "(aggiornamento del 19 ottobre 2026)"
        corpo = d.select_one("#main-content, main, .journal-content-article") or d
        m = re.search(r"aggiornament[oi]\s+(?:del|al)\s+(\d{1,2})\s+(\w+)\s+(\d{4})", pulisci(corpo.get_text(" ")), re.I)
        if m and m.group(2).lower() in MESI:
            data = f"{int(m.group(1)):02d}/{MESI.index(m.group(2).lower()) + 1:02d}/{m.group(3)}"
            a = next((x for x in corpo.find_all("a") if x.parent is not None
                      and re.search(r"aggiornament", x.parent.get_text(" "), re.I)
                      and not (x.get("href") or "").lower().endswith(".jnlp")), None)
            metti(f"{f.get('titolo') or f['nome']} - aggiornamento del {m.group(1)} {m.group(2)} {m.group(3)}",
                  a.get("href") if a else f"{f['url']}#{data}", data, f.get("descrizione", ""))
    elif f["tipo"] == "consob_comunicati":         # pagina /web/consob/comunicati-stampa (ultimi comunicati)
        anno = datetime.now().year
        for a in d.find_all("a", string=re.compile(r"Leggi il comunicato", re.I)):
            c = a
            for _ in range(6):
                c = c.parent
                if c is None or len(c.get_text(" ", strip=True)) > 80:
                    break
            if c is None:
                continue
            el_t = c.select_one(".title")
            testo = pulisci(c.get_text(" ")).replace("Leggi il comunicato", "").strip()
            tit = pulisci(el_t.get_text(" ")) if el_t else testo[:160]
            m = re.search(r"del-(\d{1,2})-([a-z]+)(?:-(\d{4}))?", a.get("href") or "")
            data = ""
            if m and m.group(2) in MESI:
                data = f"{int(m.group(1)):02d}/{MESI.index(m.group(2)) + 1:02d}/{m.group(3) or anno}"
            metti(tit, a.get("href"), data, testo)
    elif f["tipo"] == "elenco_link":               # pagina elenco: link che corrispondono a f["schema"], data nel riquadro
        schema = re.compile(f["schema"], re.I)
        assoluto = lambda h: re.sub(r"#.*$", "", urljoin(f["url"], h or ""))   # noqa: E731
        radice = (d.select_one(f["dentro"]) if f.get("dentro") else None) or d
        visti: set[str] = set()
        for a in radice.find_all("a", href=True):
            href = assoluto(a["href"])
            if not schema.search(href) or href in visti:
                continue
            c, data = a, ""
            for _ in range(6):                         # si sale finché il contenitore ha un solo link della lista
                p = c.parent
                if p is None or len({assoluto(x["href"]) for x in p.find_all("a", href=True)
                                     if schema.search(assoluto(x["href"]))}) > 1:
                    break
                c = p
                data = data or data_in_testo(pulisci(c.get_text(" ")))   # la prima data trovata salendo
            if not data:
                continue
            tit = pulisci(a.get_text(" "))
            if len(tit) < 15 or re.match(r"(read more|leggi|continua|scopri|dettagli|vai)", tit, re.I):
                alt = sorted((pulisci(x.get_text(" ")) for x in c.find_all("a", href=True)
                              if schema.search(assoluto(x["href"]))), key=len, reverse=True)
                breve = tit
                tit = alt[0] if alt and len(alt[0]) >= 15 else pulisci(a.get("title"))
                if len(tit) < 15:                      # titolo non in un link (es. Assilea: il link è la data)
                    tit = pulisci(c.get_text(" ")).replace(breve, "", 1).strip()[:200]
            txt = pulisci(c.get_text(" "))
            if f.get("titolo") == "riquadro":
                tit = re.sub(r"\s*read more\s*", " ", txt, flags=re.I)[:250]
            if len(tit) < 10:
                continue
            descr = txt[250:850] if f.get("titolo") == "riquadro" else re.sub(r"\s*read more\s*", " ", txt.replace(tit, ""), flags=re.I).strip()[:600]
            visti.add(href)
            metti(f.get("prefisso", "") + tit, href, data, descr)
    return out


MESI_EN = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
           "november", "december"]


def data_in_testo(s: str) -> str:
    """Prima data trovata nel testo, in gg/mm/aaaa (19 ottobre 2026, 19 October 2026, 19 Oct 2026, 19/10/2026, 2026-10-19)."""
    m = re.search(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-zÀ-ú]+)\.?,?\s+(\d{4})\b", s)
    if m:
        w = m.group(2).lower()
        i = MESI.index(w) if w in MESI else MESI_EN.index(w) if w in MESI_EN else \
            [x[:3] for x in MESI_EN].index(w[:3]) if w[:3] in [x[:3] for x in MESI_EN] else -1
        if i >= 0:
            return f"{int(m.group(1)):02d}/{i + 1:02d}/{m.group(3)}"
    m = re.search(r"\b(\d{1,2})[/.](\d{1,2})[/.](20\d\d)\b", s)
    if m:
        return f"{int(m.group(1)):02d}/{int(m.group(2)):02d}/{m.group(3)}"
    m = re.search(r"\b(20\d\d)-(\d{2})-(\d{2})\b", s)
    return f"{m.group(3)}/{m.group(2)}/{m.group(1)}" if m else ""


def leggi_sito(sito: dict) -> dict:
    ora = datetime.now(timezone.utc)
    slug = re.sub(r"[^A-Za-z0-9]+", "-", sito["sito"]).strip("-")
    ris = {"nome_file": f"vpalert_rss_{slug}_{ora.strftime('%Y-%m-%dT%H-%M-%S')}.json", "sito": sito["sito"],
           "origine": "github-actions", "letto_il": ora.isoformat(timespec="seconds").replace("+00:00", "Z"),
           "feed": [], "allarmi": [], "notizie": []}
    for f in sito["feed"]:
        if f.get("tipo") == "bce_wfs":       # situazione contabile settimanale Eurosistema: nessun RSS, indirizzo per data
            n0 = len(ris["notizie"])
            oggi = datetime.now(timezone.utc).date()
            for g in range(14):
                x = oggi.fromordinal(oggi.toordinal() - g)
                if x.isoweekday() not in (2, 3, 4):
                    continue
                u = (f"https://www.ecb.europa.eu/press/annual-reports-financial-statements/wfs/{x.year}/html/"
                     f"ecb.fst{x.strftime('%y%m%d')}.en.html")
                try:
                    stato, c = scarica(u)
                except Exception:  # noqa: BLE001
                    continue
                if stato != 200:
                    continue
                d = BeautifulSoup(c, "html.parser")
                corpo = pulisci((d.find("main") or d).get_text(" "))
                m = re.search(r"Eurosystem\s+(\d{1,2} \w+ \d{4})", corpo)
                ris["notizie"].append({"sito": sito["sito"], "feed": f["nome"], "categoria": f["categoria"],
                                       "titolo": "Consolidated financial statement of the Eurosystem"
                                                 + (f" as at {m.group(1)}" if m else ""),
                                       "link": u, "data_originale": x.isoformat(), "data": x.isoformat(),
                                       "descrizione": corpo[:700]})
            ris["feed"].append({"nome": f["nome"], "url": f["url"], "voci": len(ris["notizie"]) - n0})
            continue
        ok, motivo = robots(f["url"])
        if not ok:
            ris["allarmi"].append(f"{f['nome']}: non letto, {motivo} - {f['url']}")
            ris["feed"].append({"nome": f["nome"], "url": f["url"], "voci": 0, "errore": True, "motivo": motivo})
            continue
        try:
            stato, contenuto = scarica(f["url"], f.get("accept"))
            if stato in (401, 403, 202, 429):
                raise ValueError(f"HTTP {stato}: il sito blocca le richieste dai server di GitHub")
            if stato != 200:
                raise ValueError(f"HTTP {stato}")
            if re.search(rb"<title>[^<]*captcha", contenuto[:20000], re.I):
                raise ValueError("il sito risponde con un CAPTCHA anti-bot ai server di GitHub (non si aggira)")
            voci = leggi_pagina(sito, f, contenuto) if f.get("tipo") else leggi_rss(sito, f, contenuto)
            if f.get("tipo") and not voci:
                raise ValueError("nessuna voce trovata nella pagina (struttura cambiata?)")
            ris["notizie"] += voci
            ris["feed"].append({"nome": f["nome"], "url": f["url"], "voci": len(voci)})
        except Exception as e:  # noqa: BLE001
            msg = "nessuna risposta in %d s" % TIMEOUT if "timed out" in str(e) else f"{type(e).__name__}: {e}"
            ris["allarmi"].append(f"{f['nome']}: feed non leggibile ({msg}) - {f['url']}")
            ris["feed"].append({"nome": f["nome"], "url": f["url"], "voci": 0, "errore": True, "motivo": msg})
    return ris


def main() -> int:
    solo = None
    if "--solo" in sys.argv:
        solo = {s.strip() for s in sys.argv[sys.argv.index("--solo") + 1].split(",")}
    siti = [s for s in json.loads((QUI / "fonti_rss.json").read_text(encoding="utf-8"))["siti"]
            if solo is None or s["sito"] in solo]
    alt = QUI / "alternative_github.json"          # indirizzi ufficiali alternativi per i feed bloccati a GitHub
    if alt.exists():
        alternative = json.loads(alt.read_text(encoding="utf-8"))["siti"]
        for s in siti:
            a = alternative.get(s["sito"])
            if a:
                s["feed"] = [f for f in s["feed"] if f["url"] not in a.get("togli", [])] + a.get("aggiungi", [])
    DATI.mkdir(exist_ok=True)
    stato = {"letto_il": datetime.now(timezone.utc).isoformat(timespec="seconds"), "siti": {}}
    for sito in siti:
        ris = leggi_sito(sito)
        slug = re.sub(r"[^A-Za-z0-9]+", "-", sito["sito"]).strip("-")
        (DATI / f"{slug}.json").write_text(json.dumps(ris, ensure_ascii=False, indent=0), encoding="utf-8")
        ok = sum(1 for f in ris["feed"] if not f.get("errore"))
        stato["siti"][sito["sito"]] = {"feed_ok": ok, "feed_totali": len(ris["feed"]), "notizie": len(ris["notizie"]),
                                       "allarmi": ris["allarmi"]}
        print(f"{sito['sito']}: {ok}/{len(ris['feed'])} feed, {len(ris['notizie'])} notizie"
              + (f"  ALLARMI: {ris['allarmi']}" if ris["allarmi"] else ""))
    vecchio = json.loads((DATI / "stato.json").read_text(encoding="utf-8")) if (DATI / "stato.json").exists() else {}
    if solo is not None:
        stato["siti"] = {**vecchio.get("siti", {}), **stato["siti"]}
    (DATI / "stato.json").write_text(json.dumps(stato, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
