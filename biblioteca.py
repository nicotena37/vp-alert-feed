"""Biblioteca normativa (Compliance dyAInamic): scarica il testo vigente delle norme, diviso per articolo, dalle fonti ufficiali.
- Italia: API dati aperti di Normattiva (un articolo per richiesta, testo vigente con data di inizio vigenza).
- UE: EUR-Lex, ultima versione consolidata (CELEX 0...) o, se manca, il testo originale.
Salva biblioteca/testi/<id>.json e aggiorna biblioteca/indice.json. Ogni articolo ha un'impronta (hash) per riconoscere le modifiche."""
import hashlib, html, json, re, time
from datetime import datetime, timezone
from pathlib import Path
import requests

B = Path("biblioteca"); T = B / "testi"; T.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "compliaince-biblioteca/1.0 (biblioteca normativa; contatto via GitHub)"}
NA = "https://api.normattiva.it/t/normattiva.api/bff-opendata/v1/api/v1"
SPARQL = "https://publications.europa.eu/webapi/rdf/sparql"
SUFF = ["bis", "ter", "quater", "quinquies", "sexies", "septies", "octies", "novies", "decies", "undecies", "duodecies", "terdecies",
        "quaterdecies", "quinquiesdecies", "sexiesdecies", "septiesdecies", "octiesdecies"]
LOG = []

def log(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); LOG.append(s)

def pulisci(h):
    h = re.sub(r"<(br|/p|/div|/h\d|/li)[^>]*>", "\n", h or "", flags=re.I)
    t = html.unescape(re.sub(r"<[^>]+>", " ", h))
    t = re.sub(r"[ \t\xa0\u202f\u2009\u2007\u200b]+", " ", t)
    t = "\n".join(l.strip() for l in t.splitlines())
    return re.sub(r"\n\s*\n+", "\n", t).strip()

def impronta(t): return hashlib.sha256(t.encode("utf-8")).hexdigest()[:16]

# ------------------------------------------------------------------ Normattiva
def art_na(urn, a):
    for t in range(3):
        try:
            r = requests.post(NA + "/atto/dettaglio-atto-urn", json={"urn": f"{urn}~art{a}"},
                              headers={**UA, "Content-Type": "application/json", "Accept": "application/json", "Origin": "https://dati.normattiva.it"}, timeout=60)
            if r.status_code == 404: return None
            if r.status_code in (429, 500, 502, 503, 504): log(f"  {urn}~art{a}: HTTP {r.status_code}"); time.sleep(10 * (t + 1)); continue
            d = r.json(); at = ((d or {}).get("data") or {}).get("atto") or {}
            if not at.get("articoloHtml"): return None
            return at
        except Exception as e:
            log(f"  {urn}~art{a}: {e}"); time.sleep(3)
    return None

def scarica_na(voce):
    urn = voce["urn"]; arts = []; mancanti = 0; meta = None
    da, a_max = voce.get("da", 1), voce.get("a", 2000)
    for u in ([] if voce.get("_ripresa") else [urn] + voce.get("urn_alt", [])):   # prova le varianti di URN sui primi articoli
        if any(art_na(u, x) for x in (da, da + 1, da + 2)): urn = u; break
    else:
        if voce.get("_ripresa"): urn = voce["_ripresa"]["urn"]
        else: log(f"  {voce['id']}: nessuna variante di URN risponde"); return None, []
    voce["_urn"] = urn
    log(f"  {voce['id']}: uso {urn}")
    n = da
    if voce.get("_ripresa"):                                    # ripresa di un atto interrotto
        arts = voce["_ripresa"]["articoli"]; n = voce["_ripresa"]["da"]; meta = voce["_ripresa"].get("meta")
    while n <= a_max and mancanti < voce.get("stop", 15):
        if voce.get("_scadenza") and time.time() > voce["_scadenza"]:
            voce["_interrotto"] = n; break
        at = art_na(urn, n); time.sleep(0.4)
        if at:
            mancanti = 0; meta = meta or at
            arts.append(_art(n, at))
        else:
            mancanti += 1
        for s in SUFF:                                      # 120-bis, 120-ter... (anche se l'articolo base è abrogato)
            at2 = art_na(urn, f"{n}{s}"); time.sleep(0.4)
            if not at2: break
            mancanti = 0; arts.append(_art(f"{n}-{s}", at2))
        n += 1
    return meta, arts

def _art(num, at):
    t = pulisci(at.get("articoloHtml"))
    m = re.match(r"Art\.\s*[\w\-]+\s*(.{0,200}?)\s*(?=\n|1\.\s|\(\(1\.)", t)
    rubrica = (m.group(1).strip(" ()") if m else "")[:200]
    return {"num": str(num), "rubrica": rubrica, "testo": t, "vigente_dal": at.get("articoloDataInizioVigenza"),
            "vigente_al": at.get("articoloDataFineVigenza"), "hash": impronta(t)}

# ------------------------------------------------------------------ EUR-Lex
def consolidato(celex):
    q = f"""PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
    SELECT ?c WHERE {{ ?w cdm:resource_legal_id_celex ?c . FILTER(STRSTARTS(STR(?c), "0{celex[1:]}-")) }} ORDER BY DESC(?c) LIMIT 1"""
    try:
        r = requests.post(SPARQL, data={"query": q, "format": "application/sparql-results+json"}, headers=UA, timeout=120)
        b = r.json()["results"]["bindings"]
        return b[0]["c"]["value"] if b else None
    except Exception as e:
        log(f"  consolidato {celex}: {e}"); return None

def scarica_ue(voce):
    celex = voce["celex"]; c = consolidato(celex) or celex
    for cc in dict.fromkeys([c, celex]):                       # se il consolidato non ha l'HTML, usa il testo originale
        url = f"https://eur-lex.europa.eu/legal-content/IT/TXT/HTML/?uri=CELEX:{cc}"
        r = requests.get(url, headers=UA, timeout=180)
        if r.status_code == 200 and len(pulisci(r.text)) > 800: c = cc; break
        log(f"  {cc}: HTTP {r.status_code}, {len(r.text)} caratteri, inizio: {pulisci(r.text)[:120]!r}")
    else:
        return None, []
    t = pulisci(r.text)
    t = re.sub(r"(?m)^(Articolo \d+(?: ?(?:bis|ter|quater|quinquies|sexies|[a-z]))?)[ .]*$", r"\1", t)
    parti = re.split(r"\n(?=Articolo \d+(?: ?(?:bis|ter|quater|quinquies|sexies|[a-z]))?\n)", "\n" + t)
    if len(parti) < 2:                                      # struttura diversa: salva un campione per capire
        i = t.find("Articolo 1"); (B / f"debug_{c}.txt").write_text(repr(t[max(0, i-300):i+1500]), encoding="utf-8")
    arts = []
    for p in parti[1:]:
        m = re.match(r"Articolo (\d+(?: ?(?:bis|ter|quater|quinquies|sexies|[a-z]))?)\n(.*?)\n", p)
        if not m: continue
        testo = p.strip()
        fine = re.search(r"\n(ALLEGATO|Allegato [IVX]+\n|Fatto a )", testo)
        if fine: testo = testo[:fine.start()]
        arts.append({"num": m.group(1).replace(" ", "-"), "rubrica": m.group(2)[:200], "testo": testo, "hash": impronta(testo)})
    if not arts and len(t) > 500:                           # raccomandazioni e decisioni senza articoli: testo intero
        arts = [{"num": "Testo", "rubrica": "testo integrale (atto non diviso in articoli)", "testo": t, "hash": impronta(t)}]
    vista = {}
    for a in arts: vista[a["num"]] = a                     # in caso di doppioni tiene l'ultimo (testo consolidato)
    return {"celex_consolidato": c, "url": url}, list(vista.values())

# ------------------------------------------------------------------ corpus
def salva(voce, meta, arts, fonte_url):
    rec = {"id": voce["id"], "titolo": voce["titolo"], "estremi": voce.get("estremi", ""), "fonte": voce["fonte"], "url": fonte_url,
           "area": voce.get("area", []), "scaricato_il": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "n_articoli": len(arts), "articoli": arts}
    if meta: rec["meta"] = {k: meta.get(k) for k in ("titolo", "sottoTitolo", "celex_consolidato", "url") if meta.get(k)}
    p = T / f"{voce['id']}.json"
    vecchio = json.loads(p.read_text(encoding="utf-8")) if p.exists() else None
    if vecchio:
        h_old = {a["num"]: a["hash"] for a in vecchio.get("articoli", [])}
        rec["cambiati_dall_ultimo_scarico"] = [a["num"] for a in arts if h_old.get(a["num"]) not in (None, a["hash"])]
    p.write_text(json.dumps(rec, ensure_ascii=False, indent=0), encoding="utf-8")
    return rec

def scarica(corpus_file="biblioteca/corpus_pilota.json", solo=None):
    corpus = json.loads(Path(corpus_file).read_text(encoding="utf-8"))
    if solo: corpus = [v for v in corpus if any(v["id"].startswith(x) for x in solo)]
    idx_p = B / "indice.json"; indice = json.loads(idx_p.read_text(encoding="utf-8")) if idx_p.exists() else {}
    for v in corpus:
        t0 = time.time()
        try:
            if v["fonte"] == "normattiva":
                meta, arts = scarica_na(v); url = f"https://www.normattiva.it/uri-res/N2Ls?{v['urn']}"
            elif v["fonte"] == "eurlex":
                meta, arts = scarica_ue(v); url = (meta or {}).get("url", "")
            else:
                continue
        except Exception as e:
            log(f"ERRORE {v['id']}: {e}"); continue
        if not arts: log(f"VUOTO {v['id']}"); continue
        rec = salva(v, meta, arts, url)
        indice[v["id"]] = {k: rec[k] for k in ("titolo", "estremi", "fonte", "url", "area", "scaricato_il", "n_articoli")}
        idx_p.write_text(json.dumps(indice, ensure_ascii=False, indent=1), encoding="utf-8")
        log(f"{v['id']}: {len(arts)} articoli in {time.time()-t0:.0f}s")
    (B / "log.txt").write_text("\n".join(LOG), encoding="utf-8")
