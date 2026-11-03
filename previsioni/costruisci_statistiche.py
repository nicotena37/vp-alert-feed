"""Prepara il documento dati/statistiche per la pagina Statistiche e previsioni.
Uso: python costruisci_statistiche.py <archivio/storico> <risultati_backtest.json> <manuali_2_43.json> <iter3.json> <sanzioni2.json> <uscita.json>
"""
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ARCH, RIS, MAN, ITER, SANZ, OUT = map(Path, sys.argv[1:7])
QUI = Path(__file__).parent
CONF = json.loads((QUI / "temi_indicatori.json").read_text(encoding="utf-8"))
TEMI = [t["tema"] for t in CONF["temi"]]
AREA = {t["tema"]: t["area"] for t in CONF["temi"]}


def mesi_tra(a, b):
    y, m = map(int, a.split("-"))
    out = []
    while f"{y}-{m:02d}" <= b:
        out.append(f"{y}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


MESI = mesi_tra("2016-01", "2026-10")


def serie(nome, tipi=None):
    f = ARCH / f"{nome}.csv"
    if not f.exists():
        return None, None
    val, tot = defaultdict(float), defaultdict(float)
    for r in csv.DictReader(f.open(encoding="utf-8")):
        if tipi and r["tipo"] not in tipi:
            continue
        if r["tema"]:
            val[(r["mese"], r["tema"])] += float(r["valore"] or 0)
        if r["totale_fonte"]:
            tot[r["mese"]] += float(r["totale_fonte"])
    per_tema = {t: [round(val.get((m, t), 0.0), 3) for m in MESI] for t in TEMI}
    totali = [round(tot.get(m, 0.0)) for m in MESI]
    if not any(any(v) for v in per_tema.values()):
        return None, None
    return per_tema, totali


FONTI = {"eurlex": ("eurlex", None), "atti": ("eurlex", {"atto"}), "proposte": ("eurlex", {"proposta", "comunicazione"}),
         "ddl": ("senato", None), "politica": ("camera", None), "bce": ("bce_discorsi", None), "media": ("mediacloud", None),
         "studi": ("openalex", None)}
S = {}
TOT = {}
for k, (nome, tipi) in FONTI.items():
    s, t = serie(nome, tipi)
    if s:
        S[k], TOT[k] = s, t
print("fonti disponibili:", list(S))

# ---- VP Alert: alert manuali della banca (settimane 2026) per tema, con la Tematica del VP Alert come guida
sys.path.insert(0, str(Path("/home/claude/vp-alert-feed")))
import indicatori as I  # noqa: E402
TEMATICA = {
    "Fisco": "Fisco per banca e clienti", "Mercati finanziari": "Servizi di investimento e mercati",
    "Gestione collettiva": "Servizi di investimento e mercati", "Emittenti": "Servizi di investimento e mercati",
    "Benchmark finanziari": "Servizi di investimento e mercati", "Economia e finanza": "Economia, tassi e politica monetaria",
    "Economia e Finanza": "Economia, tassi e politica monetaria", "Economia  e finanza": "Economia, tassi e politica monetaria",
    "Politica monetaria": "Economia, tassi e politica monetaria", "Banche e intermediari": "Sistema bancario e vigilanza",
    "Banche": "Sistema bancario e vigilanza", "Banche e inetrmediari": "Sistema bancario e vigilanza",
    "Informativa finanziaria (reporting)": "Segnalazioni e reporting di vigilanza", "Segnalazioni di Vigilanza": "Segnalazioni e reporting di vigilanza",
    "Codifiche": "Segnalazioni e reporting di vigilanza", "Note tecniche": "Segnalazioni e reporting di vigilanza", "Manuale": "Segnalazioni e reporting di vigilanza",
    "Credito": "Credito e finanziamenti", "Finanziarie": "Credito e finanziamenti", "Diritto del lavoro": "Contratto, stipendio e rapporto di lavoro",
    "Antitrust": "Trasparenza e tutela della clientela", "Trasparenza e tutela del consumatore": "Trasparenza e tutela della clientela",
    "Usura": "Trasparenza e tutela della clientela", "Gestione reclami": "Trasparenza e tutela della clientela",
    "Vigilanza prudenziale (Basilea)": "Vigilanza prudenziale e capitale", "Vigilanza prudenziale": "Vigilanza prudenziale e capitale",
    "Affari legali e societari": "Governance, controlli e organizzazione", "Governance": "Governance, controlli e organizzazione",
    "Responsabilità amministrativa delle persone giuridiche - D. Lgs. 231/01": "Governance, controlli e organizzazione",
    "Imprese e intermediari": "Assicurazioni e bancassicurazione", "Distribuzione assicurativa": "Assicurazioni e bancassicurazione",
    "Antiriciclaggio": "Antiriciclaggio e sanzioni finanziarie", "IT e Digital": "Cybersicurezza, ICT e DORA",
    "Privacy": "Privacy e protezione dei dati", "Incassi e pagamenti": "Pagamenti, conti e moneta",
    "ESG e Sostenibilità": "Finanza sostenibile ed ESG", "Sicurezza sui luoghi di lavoro": "Salute e sicurezza sul lavoro",
}
man = json.loads(MAN.read_text(encoding="utf-8"))
settimane = sorted({x["sett"] for x in man})
vp = {t: [0] * len(settimane) for t in TEMI}
vp_tot = [0] * len(settimane)
for x in man:
    k = settimane.index(x["sett"])
    vp_tot[k] += 1
    temi = I.temi_di(str(x.get("Riferimento normativo", "")), f"{x.get('Descrizione', '')} {x.get('Argomento', '')}")
    prim = TEMATICA.get(str(x.get("Tematica", "")).strip())
    scelti = set([prim] if prim else []) | set(list(temi)[:1])
    for t in scelti:
        if t in vp:
            vp[t][k] += 1

# ---- sezioni della banca: peso di ogni tema per funzione (1 = tema centrale, 0,5 = tema collegato)
SEZ = {
    "Compliance": {"Trasparenza e tutela della clientela": 1, "Servizi di investimento e mercati": 1, "Truffe e frodi ai clienti": 1, "Misure restrittive e sanzioni internazionali": .5,
                   "Assicurazioni e bancassicurazione": .7, "Privacy e protezione dei dati": .5, "Governance, controlli e organizzazione": .5,
                   "Credito e finanziamenti": .5, "Pagamenti, conti e moneta": .5, "Cripto-attività e finanza digitale": .5,
                   "Intelligenza artificiale e innovazione": .5, "Educazione e inclusione finanziaria": .5, "Finanza sostenibile ed ESG": .5},
    "Antiriciclaggio": {"Antiriciclaggio e sanzioni finanziarie": 1, "Misure restrittive e sanzioni internazionali": 1, "Cripto-attività e finanza digitale": .5, "Pagamenti, conti e moneta": .3,
                        "Truffe e frodi ai clienti": .3},
    "Vigilanza e segnalazioni": {"Segnalazioni e reporting di vigilanza": 1, "Sistema bancario e vigilanza": 1, "Vigilanza prudenziale e capitale": .7,
                                 "Crisi bancarie, risoluzione e garanzia dei depositi": .5},
    "Risk management": {"Vigilanza prudenziale e capitale": 1, "Crisi bancarie, risoluzione e garanzia dei depositi": .7, "Finanza sostenibile ed ESG": .7,
                        "Economia, tassi e politica monetaria": .7, "Credito e finanziamenti": .5, "Cybersicurezza, ICT e DORA": .5,
                        "Intelligenza artificiale e innovazione": .3},
    "IT, sicurezza e dati": {"Cybersicurezza, ICT e DORA": 1, "Privacy e protezione dei dati": 1, "Intelligenza artificiale e innovazione": 1,
                             "Pagamenti, conti e moneta": .3, "Cripto-attività e finanza digitale": .3},
    "Legale e societario": {"Governance, controlli e organizzazione": 1, "Crisi bancarie, risoluzione e garanzia dei depositi": .5,
                            "Trasparenza e tutela della clientela": .3},
    "Commerciale e prodotti": {"Credito e finanziamenti": 1, "Pagamenti, conti e moneta": 1, "Servizi di investimento e mercati": .7,
                               "Assicurazioni e bancassicurazione": .7, "Previdenza complementare": .7, "Cripto-attività e finanza digitale": .5,
                               "Educazione e inclusione finanziaria": .5},
    "Risorse umane": {"Contratto, stipendio e rapporto di lavoro": 1, "Pensioni, previdenza e welfare": 1, "Salute e sicurezza sul lavoro": 1,
                      "Formazione e competenze del personale": 1, "Previdenza complementare": .5},
    "Fiscale": {"Fisco per banca e clienti": 1},
    "Sostenibilità": {"Finanza sostenibile ed ESG": 1},
}

# ---- scadenze future degli iter (pipeline) per tema
ITER_TEMA = {"MiFID II / MiFIR": ["Servizi di investimento e mercati"], "CSRD": ["Finanza sostenibile ed ESG"],
             "AI Act": ["Intelligenza artificiale e innovazione"], "DORA": ["Cybersicurezza, ICT e DORA"],
             "AML": ["Antiriciclaggio e sanzioni finanziarie"], "PSD3": ["Pagamenti, conti e moneta", "Truffe e frodi ai clienti"],
             "MiCAR": ["Cripto-attività e finanza digitale"], "CRR3/CRD6": ["Vigilanza prudenziale e capitale"],
             "NIS2": ["Cybersicurezza, ICT e DORA"], "RIS": ["Servizi di investimento e mercati", "Trasparenza e tutela della clientela"],
             "CCD2": ["Credito e finanziamenti", "Trasparenza e tutela della clientela"], "CSDR": ["Servizi di investimento e mercati"],
             "FiDA": ["Pagamenti, conti e moneta", "Privacy e protezione dei dati"], "Instant Payments": ["Pagamenti, conti e moneta", "Truffe e frodi ai clienti"]}
iter = json.loads(ITER.read_text(encoding="utf-8"))["iter"]
scad = defaultdict(list)
for it in iter:
    for f in it.get("futuro", []):
        for t in ITER_TEMA.get(it["norma"], []):
            scad[t].append({"data": f["data"], "evento": f["evento"], "stato": f["stato"], "iter": it["nome"]})

# ---- pressione sanzionatoria per tema (ultimi 3 anni)
VIOL_TEMA = {"Antiriciclaggio": "Antiriciclaggio e sanzioni finanziarie", "Trasparenza e correttezza": "Trasparenza e tutela della clientela",
             "Governo dei rischi e controlli interni": "Governance, controlli e organizzazione", "Responsabilità degli esponenti": "Governance, controlli e organizzazione",
             "Remunerazioni": "Governance, controlli e organizzazione", "Governo societario": "Governance, controlli e organizzazione",
             "Rischio di credito e governo dei rischi": "Credito e finanziamenti", "Servizi di investimento e gestione collettiva (TUF)": "Servizi di investimento e mercati",
             "Servizi di investimento (TUF)": "Servizi di investimento e mercati", "Segnalazioni di vigilanza": "Segnalazioni e reporting di vigilanza",
             "Comunicazioni alla vigilanza": "Segnalazioni e reporting di vigilanza", "Fondi propri": "Vigilanza prudenziale e capitale",
             "Requisiti di capitale": "Vigilanza prudenziale e capitale", "Grandi esposizioni": "Vigilanza prudenziale e capitale",
             "Grandi esposizioni e segnalazioni": "Vigilanza prudenziale e capitale", "Liquidità": "Vigilanza prudenziale e capitale",
             "Partecipazioni qualificate": "Sistema bancario e vigilanza", "Segnalazioni e informativa al pubblico": "Segnalazioni e reporting di vigilanza"}
sz = json.loads(SANZ.read_text(encoding="utf-8"))["righe"]
sanz = defaultdict(int)
for r in sz:
    if r.get("data", "") >= "2023-11" and r["violazione"] in VIOL_TEMA:
        sanz[VIOL_TEMA[r["violazione"]]] += 1

ris = json.loads(RIS.read_text(encoding="utf-8"))
out = {"aggiornato": "2026-11-03", "mesi": MESI, "temi": [{"tema": t, "area": AREA[t]} for t in TEMI],
       "serie": S, "totali": TOT, "vp": {"settimane": settimane, "temi": vp, "totale": vp_tot, "nota": "Alert manuali della banca, settimane 2026 (mancano 32-41)"},
       "sezioni": SEZ, "scadenze": scad, "sanzioni": sanz,
       "metodi": {"classifica": ris["classifica"], "risultati": ris["risultati"], "calibrazione": ris["calibrazione"],
                  "orizzonte": ris["orizzonte_mesi"], "origini": ris["origini"], "inizio_test": ris["inizio_test"],
                  "banco_vp": ris.get("banco_vp")},
       "modello_globale": ris.get("modello_globale"),
       "previsioni_script": {n: ris.get("previsioni_attuali", {}).get(n) for n in ris["classifica"][:2]},
       "fuori_campione": ris.get("fuori_campione"),
       "fonti": [
           {"nome": "EUR-Lex (Ufficio pubblicazioni UE)", "cosa": "Atti, proposte e comunicazioni UE per tema, mese per mese dal 2016", "url": "https://publications.europa.eu/webapi/rdf/sparql"},
           {"nome": "Senato (dati.senato.it)", "cosa": "Disegni di legge presentati", "url": "https://dati.senato.it/"},
           {"nome": "Camera (dati.camera.it)", "cosa": "Interrogazioni e mozioni", "url": "https://dati.camera.it/"},
           {"nome": "BCE", "cosa": "Archivio completo dei discorsi", "url": "https://www.ecb.europa.eu/press/key/html/downloads.en.html"},
           {"nome": "Media Cloud", "cosa": "Articoli dei giornali online italiani (collezione Italy - National)", "url": "https://search.mediacloud.org/"},
           {"nome": "OpenAlex", "cosa": "Studi pubblicati", "url": "https://openalex.org/"},
           {"nome": "VP Alert", "cosa": "Alert manuali della banca 2026 e voci pubblicate", "url": ""},
           {"nome": "Iter normativi e sanzioni", "cosa": "Scadenze future (pagina Iter) e provvedimenti sanzionatori (pagina Sanzioni)", "url": ""},
       ]}
def pulisci(x):
    if isinstance(x, float) and not np.isfinite(x):
        return None
    if isinstance(x, dict):
        return {k: pulisci(v) for k, v in x.items()}
    if isinstance(x, list):
        return [pulisci(v) for v in x]
    return x


CHIAVE = {"Senato (dati.senato.it)": "ddl", "Camera (dati.camera.it)": "politica", "BCE": "bce", "Media Cloud": "media", "OpenAlex": "studi"}
out["fonti_in_arrivo"] = [f["nome"] for f in out["fonti"] if f["nome"] in CHIAVE and CHIAVE[f["nome"]] not in S]
out["fonti"] = [f for f in out["fonti"] if not (f["nome"] in CHIAVE and CHIAVE[f["nome"]] not in S)]
OUT.write_text(json.dumps(pulisci(out), ensure_ascii=False, separators=(",", ":"), allow_nan=False), encoding="utf-8")
print("byte", OUT.stat().st_size)
