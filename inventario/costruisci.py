"""Legal inventory compliAInce Dynamic: unisce i cataloghi (UE, BCE, Italia, Banca d'Italia, UIF, IVASS, Consob)
in un elenco unico con fonte, tipologia, obbligatorietà (OBBL = la banca deve; BP = è bene fare) e rilevanza per la banca."""
import json, re, sys, html
from pathlib import Path

D = Path(__file__).parent
CAT = Path(sys.argv[1]) if len(sys.argv) > 1 else D / "catalogo"   # dati/catalogo di GitHub
R = []   # record: fonte, sezione, tipologia, obbl, rilevanza, estremi, titolo, data, link, note

def rec(**k):
    k.setdefault("note", ""); k.setdefault("data", ""); k.setdefault("link", ""); k.setdefault("estremi", "")
    k["titolo"] = re.sub(r"\s+", " ", html.unescape(k.get("titolo") or "")).strip(" []")
    R.append(k)

MESI = {m: i for i, m in enumerate(["gennaio","febbraio","marzo","aprile","maggio","giugno","luglio","agosto","settembre","ottobre","novembre","dicembre"], 1)}
def data_it(s):
    m = re.search(r"(\d{1,2})[°º]?\s+([A-Za-zàèé]+)\s+(\d{4})", s or "")
    if m and m.group(2).lower() in MESI: return f"{m.group(3)}-{MESI[m.group(2).lower()]:02d}-{int(m.group(1)):02d}"
    return ""

STRETTO = re.compile(r"banc|enti creditizi|credito|finanziari|servizi di pagamento|assicura|investiment|valori mobiliari|strumenti finanziari|riciclagg|"
    r"terroris|consumator|dati personali|ciber|cyber|resilienza operativa|intelligenza artificiale|lavorator|parità di trattamento|retribu|"
    r"sicurezza e (della )?salute|imposta sul valore aggiunto|fatturazione|evasione|elusione|contabil|revisione legale|società|whistle|"
    r"segnalano violazioni|accessibilità|identificazione elettronica|firma elettronica|dati (non personali)?|mercato unico digitale|sostenibil|"
    r"tassonomia|indici di riferimento|banconote|monete metalliche|\beuro\b|insolvenz|ristrutturazion|recupero crediti|contratti", re.I)
BANCA_RX = re.compile(r"banc|credit|finanz|pagament|monet|assicur|investiment|mercat|valori mobiliari|strumenti finanziari|riciclagg|terroris|"
                      r"consumator|dati personali|protezione dei dati|ciber|cyber|informatic|digital|intelligenza artificiale|lavorator|lavoro|parità|"
                      r"retribu|sicurezza e (la )?salute|salute e (della )?sicurezza|società|impres|contabil|bilanc|revision|fiscal|impost|tribut|iva\b|"
                      r"valore aggiunto|risparmi|fondi|deposit|garanzi|cartolarizz|obbligazion|derivat|controparti|benchmark|indici di riferimento|"
                      r"sostenibil|clima|ambiental|whistleblow|segnalazion|crypto|cripto|euro\b|banconot|moneta|antitrust|concorrenza|intese|"
                      r"posizione dominante|accessibilità|commercio elettronico|contratti|insolvenz|ristrutturazion|identificazione elettronica|firma", re.I)

# ------------------------------------------------------------------ UE
TIPO_UE = {"REG": "Regolamento", "REG_DEL": "Regolamento delegato", "REG_IMPL": "Regolamento di esecuzione", "DIR": "Direttiva",
           "DIR_DEL": "Direttiva delegata", "DIR_IMPL": "Direttiva di esecuzione", "DEC": "Decisione", "DEC_DEL": "Decisione delegata",
           "DEC_IMPL": "Decisione di esecuzione", "GUIDELINE": "Indirizzo", "RECO": "Raccomandazione", "REG_FINANC": "Regolamento finanziario",
           "DEC_ENTSCHEID": "Decisione", "AGREE": "Accordo", "AGREE_INTERINSTIT": "Accordo interistituzionale", "AGREE_INTERNATION": "Accordo internazionale",
           "PROC_INTERNAL": "Regolamento interno"}
def ue():
    def load(n):
        p = CAT / f"{n}.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
    visti = {}
    def add(x, sezione, filtro=False, nota=""):
        c = x["celex"]; tp = x.get("tipo", "").rsplit("/", 1)[-1]; tit = x.get("tit") or ""
        if c in visti or not c.startswith("3"): return
        bce = "ECB" in (x.get("autori") or "") or "(BCE/" in tit or "Banca centrale europea" in tit[:120]
        if tp not in TIPO_UE or tp in ("AGREE_INTERINSTIT", "PROC_INTERNAL", "AGREE", "AGREE_INTERNATION") and not bce: return
        if re.search(r"relativa? ad? una procedura|procedimento a norma dell.articolo|mobilitazione del|Fondo europeo di adeguamento|impresa comune|"
                     r"posizione (da adottare|della Comunità|dell.Unione)|che respinge|aiut[oi] di Stato|concentrazione|nomina|immunit", tit, re.I) and not bce: return
        if filtro and not STRETTO.search(tit): return
        if tp in ("DEC", "DEC_IMPL") and not bce and not re.search(r"equivalen|adeguatezza della protezione|elenco|paesi terzi|norme tecniche|modell|formati", tit, re.I) and sezione.startswith("Repertorio EUR-Lex (filtrato)"): return
        if sezione.startswith("Misure restrittive") and re.search(r"che modifica|che attua|di esecuzione", tit, re.I): return
        if filtro and not BANCA_RX.search(tit): return
        if re.search(r"che autorizza (la|il|l'|i|le)\s*[A-Z]", tit) and tp in ("DEC_IMPL", "DEC") and "Italia" not in tit: return   # deroghe a singoli Stati
        if re.search(r"^Decisione.{0,80}(concernente|relativa) (la|il) (nomina|sostituzione)", tit): return
        obbl = "BP" if tp == "RECO" else "OBBL"
        tipologia = ("BCE - " if bce else "") + TIPO_UE.get(tp, tp)
        ril = "BANCA"
        if bce and tp in ("DEC", "GUIDELINE", "DEC_ENTSCHEID") and not re.search(r"vigilanz|enti creditizi|segnalazion|riserv|statistic|garanzi|operazioni di politica monetaria|stanziabil|MVU|soggetti vigilati|contributi", tit, re.I):
            ril = "INDIRETTA (rivolto a BCN/organi BCE)"
        visti[c] = 1
        rec(fonte="Gazzetta ufficiale UE" + (" - atti BCE" if bce else ""), sezione=sezione, tipologia=tipologia, obbl=obbl, rilevanza=ril,
            estremi=f"CELEX {c}", titolo=tit, data=(x.get("data") or "")[:10], link=f"https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:{c}", note=nota)
    for x in load("ue_includi"):
        if (x.get("vigore") or "true") != "false": add(x, "Atti base selezionati")
    for x in load("ue_core"): add(x, "Repertorio EUR-Lex: " + (x.get("codici") or ""))
    for x in load("ue_famiglie"): add(x, "Atti delegati/esecuzione basati su " + x.get("base", ""))
    for x in load("ue_bce"): add({**x, "autori": "ECB"}, "Atti della BCE in vigore")
    for x in load("ue_filtrati"): add(x, "Repertorio EUR-Lex (filtrato): " + (x.get("codici") or ""), filtro=True)
    for x in load("ue_sanzioni"): add(x, "Misure restrittive (sanzioni finanziarie)", nota="obblighi di congelamento e divieti")
    CARDINE_UE = {"32013R0575": ("Regolamento", "Regolamento (UE) n. 575/2013 - requisiti prudenziali per gli enti creditizi (CRR)"),
        "32013L0036": ("Direttiva", "Direttiva 2013/36/UE - accesso all'attività degli enti creditizi e vigilanza prudenziale (CRD)"),
        "32014L0059": ("Direttiva", "Direttiva 2014/59/UE - risanamento e risoluzione degli enti creditizi e delle imprese di investimento (BRRD)"),
        "32014R0806": ("Regolamento", "Regolamento (UE) n. 806/2014 - Meccanismo di risoluzione unico (SRMR)"),
        "32014L0049": ("Direttiva", "Direttiva 2014/49/UE - sistemi di garanzia dei depositi"),
        "32014L0065": ("Direttiva", "Direttiva 2014/65/UE - mercati degli strumenti finanziari (MiFID II)"),
        "32014R0600": ("Regolamento", "Regolamento (UE) n. 600/2014 - mercati degli strumenti finanziari (MiFIR)"),
        "32015L0849": ("Direttiva", "Direttiva (UE) 2015/849 - prevenzione del riciclaggio (AMLD4)"),
        "32015L2366": ("Direttiva", "Direttiva (UE) 2015/2366 - servizi di pagamento nel mercato interno (PSD2)"),
        "32022R2554": ("Regolamento", "Regolamento (UE) 2022/2554 - resilienza operativa digitale (DORA)"),
        "32016R0679": ("Regolamento", "Regolamento (UE) 2016/679 - protezione dei dati personali (GDPR)"),
        "32024R1689": ("Regolamento", "Regolamento (UE) 2024/1689 - intelligenza artificiale (AI Act)"),
        "32024R1624": ("Regolamento", "Regolamento (UE) 2024/1624 - antiriciclaggio (AMLR)"),
        "32016L0097": ("Direttiva", "Direttiva (UE) 2016/97 - distribuzione assicurativa (IDD)")}
    for c, (tp, t) in CARDINE_UE.items():
        if c not in visti:
            visti[c] = 1
            rec(fonte="Gazzetta ufficiale UE", sezione="Norme cardine (elenco di base)", tipologia=tp, obbl="OBBL", rilevanza="BANCA", estremi=f"CELEX {c}",
                titolo=t, link=f"https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:{c}", note="norma cardine non restituita dalla banca dati: inserita dall'elenco di base")

# ------------------------------------------------------------------ Italia (Normattiva)
IT_RX = re.compile(r"banc(a|he|ario|aria|ari)\b|credito|creditizi|intermediari finanziari|risparmio|riciclaggio|terrorismo|usura|servizi di pagamento|"
    r"moneta elettronica|assicurazion|consumator|trasparenza|valori mobiliari|strumenti finanziari|mercati finanziari|servizi di investimento|"
    r"previdenza complementare|forme pensionistiche complementari|dati personali|sicurezza cibernetica|cybersicurezza|intelligenza artificiale|"
    r"sicurezza (sul|nei luoghi di) lavoro|salute e (della )?sicurezza|responsabilita' amministrativa (degli enti|delle persone giuridiche)|"
    r"crisi d'impresa|insolvenza|sovraindebitamento|cartolarizzazione|assegn[oi] bancar|cambial|imposte sui redditi|imposta sul valore aggiunto|"
    r"imposta di bollo|accertamento delle imposte|anagrafe tributaria|redditi di natura finanziaria|titolar[ei] effettiv|whistleblowing|"
    r"segnalano violazioni|firma elettronica|amministrazione digitale|conti di pagamento|carte di pagamento|cripto|sostenibilita'|statuto dei lavoratori|"
    r"rapporto di lavoro|contratti di lavoro|orario di lavoro|maternita'|pari opportunita'|persone con disabilita'|lavoro agile|societa' per azioni|"
    r"codice civile|concorrenza e del mercato|mutu[io]|fondo di garanzia|confidi|microcredito|agenti in attivita' finanziaria|mediatori creditizi|"
    r"gestione collettiva|organismi di investimento|fondi comuni|obbligazioni bancarie garantite|garanzie finanziarie|contratti di garanzia finanziaria|"
    r"Testo unico delle leggi in materia bancaria|codice del consumo|codice delle assicurazioni|intermediazione finanziaria|scambio automatico di informazioni|cooperazione amministrativa nel settore fiscale", re.I)
UE_RIF = re.compile(r"(direttiva|regolamento)\s*(?:\((?:UE|CE)\)\s*)?(?:n\.\s*)?(\d{2,4}/\d{1,4})", re.I)
WHITE_RD = re.compile(r"1933, n\. 1736|1933, n\. 1669|1942, n\. 262|1942, n\. 267|1940, n\. 1443|1941, n\. 12", re.I)
TIPO_IT = {"LEGGE": "Legge", "DECRETO LEGISLATIVO": "Decreto legislativo", "DECRETO-LEGGE": "Decreto-legge", "DECRETO DEL PRESIDENTE DELLA REPUBBLICA": "D.P.R.",
           "DECRETO": "Decreto", "DECRETO MINISTERIALE": "Decreto ministeriale", "REGIO DECRETO": "Regio decreto"}

BASE_IT = [  # norme cardine: entrano comunque (alcune non escono dalle ricerche di Normattiva)
 ("Decreto legislativo", "1993-09-01", "385", "Testo unico delle leggi in materia bancaria e creditizia (TUB)"),
 ("Decreto legislativo", "1998-02-24", "58", "Testo unico delle disposizioni in materia di intermediazione finanziaria (TUF)"),
 ("Regio decreto", "1942-03-16", "262", "Codice civile"),
 ("Regio decreto", "1933-12-21", "1736", "Disposizioni sull'assegno bancario, sull'assegno circolare e su alcuni titoli speciali dell'Istituto di emissione"),
 ("Regio decreto", "1933-12-14", "1669", "Modificazioni alle norme sulla cambiale e sul vaglia cambiario (legge cambiaria)"),
 ("Legge", "1974-06-07", "216", "Conversione del D.L. 95/1974 - legge istitutiva della Consob"),
 ("Legge", "1990-10-10", "287", "Norme per la tutela della concorrenza e del mercato"),
 ("Legge", "1990-12-15", "386", "Nuova disciplina sanzionatoria degli assegni bancari (Centrale d'allarme interbancaria)"),
 ("Legge", "1999-04-30", "130", "Disposizioni sulla cartolarizzazione dei crediti"),
 ("Legge", "2005-12-28", "262", "Disposizioni per la tutela del risparmio e la disciplina dei mercati finanziari"),
 ("Decreto legislativo", "2004-05-21", "170", "Attuazione della direttiva 2002/47/CE sui contratti di garanzia finanziaria"),
 ("Decreto legislativo", "2005-03-07", "82", "Codice dell'amministrazione digitale"),
 ("Decreto legislativo", "2005-12-05", "252", "Disciplina delle forme pensionistiche complementari"),
 ("Decreto legislativo", "2005-05-30", "142", "Attuazione della direttiva 2002/87/CE sui conglomerati finanziari"),
 ("Decreto legislativo", "2007-06-22", "109", "Misure per prevenire, contrastare e reprimere il finanziamento del terrorismo"),
 ("Decreto legislativo", "2015-11-16", "180", "Attuazione della direttiva 2014/59/UE (risanamento e risoluzione - BRRD)"),
 ("Decreto legislativo", "2016-02-15", "30", "Attuazione della direttiva 2014/49/UE sui sistemi di garanzia dei depositi"),
 ("Decreto legislativo", "2015-08-18", "136", "Bilanci d'esercizio e consolidati delle banche e degli intermediari finanziari"),
 ("Decreto legislativo", "2005-02-28", "38", "Esercizio delle opzioni sui principi contabili internazionali"),
 ("D.P.R.", "1973-09-29", "600", "Disposizioni comuni in materia di accertamento delle imposte sui redditi"),
 ("D.P.R.", "1973-09-29", "605", "Anagrafe tributaria e codice fiscale (archivio dei rapporti finanziari)"),
 ("D.P.R.", "1972-10-26", "642", "Disciplina dell'imposta di bollo"),
 ("Decreto legislativo", "1997-11-21", "461", "Riordino della disciplina dei redditi di capitale e dei redditi diversi"),
 ("Decreto legislativo", "1996-04-01", "239", "Imposta sostitutiva su interessi e premi di obbligazioni e titoli similari"),
 ("Legge", "2015-06-18", "95", "Ratifica ed esecuzione dell'Accordo FATCA Italia-Stati Uniti"),
 ("Decreto legislativo", "2020-07-30", "100", "Attuazione della direttiva (UE) 2018/822 (DAC6 - meccanismi transfrontalieri)"),
 ("Legge", "2000-07-27", "212", "Statuto dei diritti del contribuente"),
 ("Decreto legislativo", "2000-03-10", "74", "Nuova disciplina dei reati in materia di imposte sui redditi e sul valore aggiunto"),
 ("Legge", "2012-11-06", "190", "Disposizioni per la prevenzione e la repressione della corruzione"),
 ("Decreto legislativo", "2015-06-15", "81", "Disciplina organica dei contratti di lavoro"),
 ("Decreto legislativo", "2022-06-27", "104", "Condizioni di lavoro trasparenti e prevedibili"),
 ("Decreto legislativo", "2001-03-26", "151", "Testo unico a tutela della maternità e della paternità"),
 ("Decreto legislativo", "2006-04-11", "198", "Codice delle pari opportunità tra uomo e donna"),
 ("Legge", "1992-02-05", "104", "Legge quadro per l'assistenza, l'integrazione sociale e i diritti delle persone handicappate"),
 ("Legge", "1999-03-12", "68", "Norme per il diritto al lavoro dei disabili"),
 ("Legge", "2017-05-22", "81", "Tutela del lavoro autonomo non imprenditoriale e lavoro agile"),
 ("Legge", "2012-06-28", "92", "Riforma del mercato del lavoro"),
 ("Decreto legislativo", "2007-08-02", "145", "Pubblicità ingannevole e comparativa"),
 ("Legge", "2018-01-11", "5", "Registro pubblico delle opposizioni e telemarketing"),
 ("Decreto legislativo", "2010-03-04", "28", "Mediazione finalizzata alla conciliazione delle controversie civili e commerciali"),
 ("Decreto legislativo", "2016-04-21", "72", "Attuazione della direttiva 2014/17/UE (credito immobiliare ai consumatori)"),
 ("Decreto legislativo", "2017-03-15", "37", "Attuazione della direttiva 2014/92/UE (conti di pagamento e conto di base)"),
 ("Decreto legislativo", "2017-12-15", "218", "Recepimento della direttiva (UE) 2015/2366 (PSD2)"),
 ("Decreto legislativo", "2024-09-06", "125", "Attuazione della direttiva (UE) 2022/2464 (rendicontazione di sostenibilità)"),
 ("Decreto-legge", "2000-12-29", "394", "Interpretazione autentica della legge 108/1996 sull'usura"),
 ("Decreto-legge", "2011-12-06", "201", "Disposizioni urgenti (art. 36: divieto di interlocking)"),
 ("Decreto-legge", "2012-03-15", "21", "Poteri speciali (golden power)"),
 ("Decreto-legge", "2019-09-21", "105", "Perimetro di sicurezza nazionale cibernetica"),
 ("Legge", "2024-06-28", "90", "Disposizioni in materia di rafforzamento della cybersicurezza nazionale"),
 ("D.P.R.", "2001-06-06", "380", "Testo unico dell'edilizia"),
 ("Decreto legislativo", "2005-08-19", "192", "Rendimento energetico nell'edilizia"),
 ("Legge", "1978-07-27", "392", "Disciplina delle locazioni di immobili urbani"),
 ("Decreto legislativo", "2023-03-31", "36", "Codice dei contratti pubblici"),
 ("Legge", "2010-08-13", "136", "Piano straordinario contro le mafie (art. 3: tracciabilità dei flussi finanziari)"),
 ("Decreto legislativo", "2013-03-14", "33", "Obblighi di pubblicità, trasparenza e diffusione di informazioni delle PA"),
 ("Legge", "1990-08-07", "241", "Nuove norme sul procedimento amministrativo"),
]

def italia():
    p = CAT / "it_normattiva.json"
    if not p.exists(): return
    nums_ue = set()
    for r in R:
        if r["fonte"].startswith("Gazzetta ufficiale UE"):
            for m in re.finditer(r"(\d{2,4}/\d{1,4})", r["titolo"][:160]): nums_ue.add(m.group(1))
    for a in json.loads(p.read_text(encoding="utf-8")):
        tit = re.sub(r"\s+", " ", re.sub(r"\(\d{2}[A-Z]\d{5}\)|\(\d{3}[A-Z0-9]{5}\)", "", a.get("titoloAtto") or "")).strip(" []"); tp = a.get("denominazioneAtto") or ""
        anno = int(a.get("annoProvvedimento") or 0)
        mese = list(MESI)[int(a.get("meseProvvedimento") or 1) - 1]
        estremi = f"{TIPO_IT.get(tp, tp.title())} {a.get('giornoProvvedimento')} {mese} {anno}, n. {a.get('numeroProvvedimento')}"
        if tp == "REGIO DECRETO" and not WHITE_RD.search(estremi): continue
        if anno < 1942 and not WHITE_RD.search(estremi): continue
        if re.search(r"^\s*(Conversione in legge|Ratifica|Approvazione|Assegnazion|Stato di previsione|Rendiconto|Bilancio|Proroga del termine|Autorizzazione)", tit, re.I): continue
        if re.search(r"statuto (della|del|dell)|che approva|autorizza la societa'|esecuzione dell.accordo|finanza locale|enti locali|regione|provincia di|comune di|"
                     r"pensione (privilegiata|straordinaria)|ruoli organici|personale (civile|militare)|Cassa per il Mezzogiorno|calamit|sisma|terremot|alluvion", tit, re.I): continue
        if re.search(r"erezione in ente morale|ente morale|fondo di dotazione|assegno (integrativo|di superinvalidita|vitalizio|mensile)|invalid|"
                     r"Banco di Napoli|Banco di Sicilia|Carige|Monte dei Paschi|Popolare di Vicenza|Veneto Banca|Banca Etruria|carabinieri|forze armate|"
                     r"industrie (estrattive|siderurg)|miniere|cantieri|navi|pesca|agricol|zootecn|sanitari|ospedal|scuol|universit|teatr|sport|"
                     r"Cassa (comunale|rurale|di risparmio) di [A-Z]|accise|prodotti petroliferi|calzature|imposte di fabbricazione|Mostra d.oltremare|ente autonomo|tabacc|alcol|carburant|veicoli|autoveicoli|monte di credito su pegno di|personale (dipendente|della|del)|trattamento economico", tit, re.I): continue
        if anno < 1990 and not re.search(r"imposte sui redditi|valore aggiunto|imposta di bollo|accertamento delle imposte|anagrafe tributaria|riscossione delle imposte|"
                     r"statuto dei lavoratori|liberta' e dignita' dei lavoratori|Commissione nazionale per le societa' e la borsa|codice civile|assegn[oi] bancar|"
                     r"tutela del risparmio|fondi comuni|parita' di trattamento|lavoratrici madri|collocamento obbligatorio|disposizioni sulla tutela", tit, re.I): continue
        rif = [m.group(2) for m in UE_RIF.finditer(tit)]
        if rif:
            if not any(x in nums_ue for x in rif) and not IT_RX.search(re.sub(UE_RIF, "", tit)): continue
        elif not IT_RX.search(tit): continue
        d = f"{anno}-{int(a.get('meseProvvedimento') or 0):02d}-{int(a.get('giornoProvvedimento') or 0):02d}"
        rec(fonte="Gazzetta Ufficiale (Normattiva)", sezione="Atti vigenti", tipologia=TIPO_IT.get(tp, tp.title()), obbl="OBBL", rilevanza="BANCA",
            estremi=estremi, titolo=tit, data=d, link=f"https://www.normattiva.it/ (GU n. {a.get('numeroGU')} del {a.get('dataGU')})")
    presenti = {(r["data"][:4], r["estremi"].rsplit("n. ", 1)[-1]) for r in R if r["fonte"].startswith("Gazzetta Ufficiale")}
    for tp, d, n, t in BASE_IT:
        if (d[:4], n) in presenti: continue
        g, m = int(d[8:]), list(MESI)[int(d[5:7]) - 1]
        urn = {"Decreto legislativo": "decreto.legislativo", "Regio decreto": "regio.decreto", "Legge": "legge", "D.P.R.": "decreto.del.presidente.della.repubblica", "Decreto-legge": "decreto.legge"}[tp]
        rec(fonte="Gazzetta Ufficiale (Normattiva)", sezione="Norme cardine (elenco di base)", tipologia=tp, obbl="OBBL", rilevanza="BANCA",
            estremi=f"{tp} {g} {m} {d[:4]}, n. {n}", titolo=t, data=d, link=f"https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:{urn}:{d};{n}",
            note="norma cardine inserita dall'elenco di base: estremi da verificare con Normattiva")

# ------------------------------------------------------------------ Banca d'Italia
def bdi():
    b = json.loads((D / "bdi.json").read_text(encoding="utf-8"))
    CATS = [("Delibere del CICR e DM d’urgenza", "Delibera CICR / DM d'urgenza", "OBBL"), ("Contrasto del riciclaggio e del finanziamento del terrorismo", "Antiriciclaggio", "OBBL"),
            ("Contrasto dell'usura", "Usura", "OBBL"), ("Comunicazioni", "Comunicazione", "BP"), ("Disposizioni", "Disposizioni", "OBBL"),
            ("Circolari", "Circolare", "OBBL"), ("Regolamenti", "Regolamento", "OBBL")]
    for x in b["archivio"]:
        t = x["testo"]; tip, ob = "Altro", "OBBL"
        for c, n, o in CATS:
            if t.endswith(c): t, tip, ob = t[: -len(c)].strip(), n, o; break
        if re.match(r"(Documenti del Gruppo di azione finanziaria|Normativa dell'Unione europea|Normativa nazionale)", t): tip, ob = "Pagina di raccolta (rinvia ad altri atti)", "BP"
        if tip == "Comunicazione" and re.search(r"modifica|disposizioni|istruzioni|circolare n", t, re.I): ob = "OBBL/BP"
        rec(fonte="Banca d'Italia", sezione="Archivio norme di vigilanza", tipologia=tip, obbl=ob, rilevanza="BANCA", titolo=t, data=data_it(x["data"]), link=x["link"])
    for t, l in b["extra"]["orientamenti"]["link"]:
        if "orientamenti-vigilanza/" in l and len(t) > 25 and "elenco-esa" not in l and "Supervisory" not in t:
            t2 = re.sub(r"\s*(pdf|xlsx)\s+[\d.,]+\s*[KM]B\s*$", "", t)
            rec(fonte="Banca d'Italia", sezione="Orientamenti di vigilanza", tipologia="Orientamento / comunicazione al sistema", obbl="BP",
                rilevanza="BANCA", titolo=t2, link=l, note="ABROGATO" if "ABROGATO" in t else "")
    e = json.loads((D / "bdi_esa.json").read_text(encoding="utf-8"))
    aut = ""
    for r in e["tabs"][0][1:]:
        if len(r) == 1: aut = r[0]; continue
        if len(r) < 6: continue
        rec(fonte=f"{aut} (orientamenti recepiti dalla Banca d'Italia)", sezione="Orientamenti e raccomandazioni ESA", tipologia=f"Orientamenti {aut}",
            obbl="BP", rilevanza="BANCA" if re.search(r"banc|meno significativ|intermediari|SIM|IP|IMEL|enti", r[4], re.I) else "ALTRO",
            estremi=r[0], titolo=r[1], data=r[3], note=f"Conformità: {r[2]}; ambito: {r[4][:160]}; atto: {r[5]}")

# ------------------------------------------------------------------ UIF
def uif():
    u = json.loads((D / "uif.json").read_text(encoding="utf-8")); seen = set()
    for v in u.values():
        for m in re.finditer(r"((?:Provvedimento|Istruzioni|Comunicazione UIF|Decreto (?:MEF|del Ministro|del Ministero|28 settembre)|Schemi di comportamenti)[^\n]{20,240})", v["testo"]):
            s = re.sub(r"pdf\s*[\d.,]+\s*KB", " - ", m.group(1)).strip()
            s = re.sub(r"\(link esterno\)", "", s); k = s[:70]
            if k in seen or len(s) < 40: continue
            seen.add(k)
            tip = "Provvedimento/Istruzioni UIF" if re.match(r"Provvedimento|Istruzioni", s) else "Comunicazione UIF (schemi e prevenzione)" if s.startswith(("Comunicazione", "Schemi")) else "Decreto ministeriale"
            rec(fonte="UIF", sezione="Normativa antiriciclaggio UIF", tipologia=tip, obbl="BP" if tip.startswith("Comunicazione") else "OBBL", rilevanza="BANCA",
                titolo=s[:300], data=data_it(s), link="https://uif.bancaditalia.it/normativa/")

# ------------------------------------------------------------------ IVASS
IV_BANCA = re.compile(r"distribu|intermediar|banc|informativ|prodott|POG|reclam|riciclagg|abbinat|finanziament|mutu|vendita|colloca|sportell|"
                      r"formazione|aggiornamento professionale|conflitt|remunerazion|incentiv|registro unico|RUI|PPI|credit protection|IBIP|"
                      r"investimento assicurativ|pubblicit|preventiv|contratt|tutela|consumator|whistle|esternalizz|governo societario|frodi|bancassicurazion", re.I)
def ivass():
    iv = json.loads((D / "ivass.json").read_text(encoding="utf-8"))
    TIP = {"regolamenti": ("Regolamento IVASS/ISVAP", "OBBL"), "normativi-provv": ("Provvedimento IVASS (normativo)", "OBBL"),
           "comunicazioni": ("Comunicazione IVASS", "BP"), "lettere": ("Lettera al mercato", "BP"), "circolari": ("Circolare ISVAP", "OBBL")}
    for s, v in iv.items():
        for x in v:
            t = re.sub(r"\s*data:\s*\d.*$", "", x["riquadro"]).strip()
            if s == "lettere" and re.search(r"contributo di vigilanza|contributi di vigilanza", t, re.I): continue
            ril = "BANCA (distributore)" if IV_BANCA.search(t) else "ALTRO (imprese di assicurazione)"
            rec(fonte="IVASS", sezione=s, tipologia=TIP[s][0], obbl=TIP[s][1], rilevanza=ril, titolo=t, data=data_it(t), link=x["link"],
                note=_vig_isvap(t) if s == "circolari" else ("ABROGATO" if re.search(r"\babrogat", t, re.I) else ""))

def _vig_isvap(t):
    m = re.search(r"\(?(abrogat[ao][^)]{0,120})\)?", t, re.I)
    if m: return "ABROGATO - " + m.group(1).strip()
    if re.search(r"sostituit|superat", t, re.I): return "da verificare: il testo indica una sostituzione"
    return "ancora nell'elenco IVASS delle circolari ISVAP (nessuna abrogazione indicata)"

# ------------------------------------------------------------------ Consob
def consob():
    c = json.loads((D / "consob.json").read_text(encoding="utf-8"))
    for t, l in c["/web/area-pubblica/tuf-e-regolamenti-consob"]["links"]:
        if re.search(r"^(Regolamento Consob n\.|Provvedimento unico|Delibera Consob n\.|Linee guida)", t):
            rec(fonte="Consob", sezione="TUF e regolamenti attuativi", tipologia="Regolamento/Delibera Consob" if not t.startswith("Linee") else "Linee guida Consob",
                obbl="OBBL" if not t.startswith("Linee") else "BP", rilevanza="BANCA", titolo=t, data=data_it(t), link=l)
    cc = json.loads((D / "consob_com.json").read_text(encoding="utf-8")); seen = set()
    for x in cc["voci"]:
        t = x["titolo"]; k = x["link"].split("?")[0]
        if k in seen or re.search(r"^(Modulo|Modello|Template|Allegato|Relazione illustrativa|Guida operativa|Tabelle)", t): continue
        seen.add(k)
        if re.search(r"^Regolamento \(UE\)|^Direttiva|^Regolamento delegato|^Regolamento di esecuzione", t): tip, ob = "Normativa UE (richiamata da Consob)", "OBBL"
        elif re.search(r"Orientament|ESMA", t): tip, ob = "Orientamenti ESMA/Consob", "BP"
        elif re.search(r"^Comunicazione|^Richiamo|^Raccomandazione|^Avviso|Q&A|Domande", t): tip, ob = "Comunicazione / richiamo di attenzione / Q&A", "BP"
        elif re.search(r"^Regolamento Consob|^Delibera", t): tip, ob = "Regolamento/Delibera Consob", "OBBL"
        elif re.search(r"^(Provvedimento|Decreto|Legge|D\.\s?Lgs|Regolamento (della )?Banca d.Italia|Disposizioni)", t): tip, ob = "Provvedimento/legge richiamato da Consob", "OBBL"
        else: tip, ob = "Altro documento Consob", "BP"
        rec(fonte="Consob", sezione=x["pagina"], tipologia=tip, obbl=ob, rilevanza="BANCA (se presta servizi di investimento / emittente)" if x["pagina"] in ("Informazioni regolamentate", "Vendite allo scoperto", "EMIR") else "BANCA",
            titolo=t, data=data_it(t), link=x["link"])

# ------------------------------------------------------------------ Fase 1: nuove fonti
def _j(p):
    p = Path(p)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []

def _data_en(s):
    m = re.search(r"(\d{1,2})\s+([A-Z][a-z]+)\s+(\d{4})", s or "")
    EN = ["January","February","March","April","May","June","July","August","September","October","November","December"]
    if m and m.group(2) in EN: return f"{m.group(3)}-{EN.index(m.group(2))+1:02d}-{int(m.group(1)):02d}"
    m = re.search(r"\b(20\d\d|19\d\d)\b", s or ""); return m.group(1) if m else ""

def nuove_fonti():
    # EBA: elenco completo di orientamenti, raccomandazioni, opinioni (dal sito EBA, browser)
    for x in _j(D / "eba.json"):
        t = re.sub(r"^(Final [Rr]eport( on)?|Final draft)\s*", "", x["titolo"]).strip() or x["titolo"]
        rec(fonte="EBA", sezione="Orientamenti, raccomandazioni e opinioni EBA", tipologia=x.get("tipo") or "Orientamenti EBA",
            obbl="BP", rilevanza="BANCA", titolo=t, data=_data_en(x.get("data")), link=x.get("link", ""),
            note="ABROGATO" if re.search(r"repeal|abrogat", t, re.I) else "")
    # Garante privacy: linee guida, provvedimenti generali, autorizzazioni, codici di condotta, temi banche e credito
    SEZ = {"linee guida": "Linee guida", "provvedimenti a carattere generale": "Provvedimento a carattere generale", "Banche": "Provvedimento (tema banche)",
           "Credito": "Provvedimento (tema credito)", "autorizzazioni generali": "Autorizzazione generale", "codici di condotta": "Codice di condotta / regole deontologiche"}
    for x in _j(D / "garante.json"):
        chiave = x["sezione"].rstrip("/").split("/")[-1]
        tip = SEZ.get(chiave, "Provvedimento del Garante")
        t = re.sub(r"^\s*null\s+", "", x.get("contesto") or x["titolo"])
        t = re.split(r"\s+(?:\[doc\.? web|VEDI|Vedi anche|vedi anche|\*ATTENZIONE|L´INFOGRAFICA|versione italiana|English version|Documento sottoposto)", t)[0].strip()
        if len(t) < 15: t = x["titolo"]
        if re.match(r"(Social Media Policy|Guidelines|General Application|Implementing|Requirements|Simplified|GUIDELINES)", t): continue
        ril = "BANCA" if not re.search(r"pazient|sanitar|scuol|didattic|ospedal|vaccin|comune di|ASL|medic", t, re.I) or re.search(r"banc|credit", t, re.I) else "ALTRO (settori diversi)"
        rec(fonte="Garante privacy", sezione="Normativa e provvedimenti del Garante", tipologia=tip, obbl="BP" if tip == "Linee guida" else "OBBL",
            rilevanza=ril, titolo=t, data=data_it(t), link=x["link"])
    # GitHub fase 1 e 1b: ESMA, EIOPA, MEF, OAM, Agenzia delle Entrate, AGCM, COVIP
    F1 = {"esma": ("ESMA", "Orientamenti e Q&A ESMA", "Orientamenti / Q&A ESMA", "BP", "BANCA (se presta servizi di investimento)"),
          "eiopa": ("EIOPA", "Orientamenti EIOPA", "Orientamenti EIOPA", "BP", "BANCA (distributore assicurativo)"),
          "mef_reati_finanziari": ("MEF - Dipartimento del Tesoro", "Prevenzione dei reati finanziari", "Decreto / circolare MEF", "OBBL", "BANCA"),
          "oam": ("OAM", "Normativa OAM (agenti e mediatori)", "Circolare / disposizione OAM", "OBBL", "BANCA (rete esterna: agenti e mediatori)"),
          "ade_circolari": ("Agenzia delle Entrate", "Circolari", "Circolare AdE", "OBBL", "BANCA (sostituto d'imposta / intermediario)"),
          "ade_provvedimenti": ("Agenzia delle Entrate", "Provvedimenti del Direttore", "Provvedimento AdE", "OBBL", "BANCA (sostituto d'imposta / intermediario)"),
          "ade_risoluzioni": ("Agenzia delle Entrate", "Risoluzioni", "Risoluzione AdE", "BP", "BANCA (sostituto d'imposta / intermediario)"),
          "agcm": ("AGCM", "Normativa e regolamenti AGCM", "Regolamento / linee guida AGCM", "OBBL", "BANCA"),
          "covip": ("COVIP", "Normativa COVIP", "Deliberazione COVIP", "OBBL", "BANCA (collocatore di forme pensionistiche)")}
    presenti = set()
    for n, (fo, se, tp, ob, ri) in F1.items():
        for x in _j(GH / f"f1_{n}.json"):
            t = x["titolo"]
            if re.fullmatch(r"(pdf|PDF|scarica|download|leggi tutto|vai|dettaglio|more|read more)[\s\d.,KMB]*", t) and x.get("contesto"): t = x["contesto"][:300]
            if n == "esma": continue                                   # raccolta ESMA non riuscita (solo link di menu)
            if n.startswith("ade_") and len(t) < 40: t = re.sub(r"^(Intermediari\s*)+", "", x.get("contesto", ""))[:300] or t
            if n == "ade_risoluzioni" and re.search(r"codic[ei] tribut|causal[ei] contribut", t, re.I): continue
            if n == "mef_reati_finanziari" and re.search(r"^(Normativa sul Debito|Sottoscrizione)|tassi usura|contratti pubblici", t): continue
            if n == "agcm":
                if not re.match(r"(Regolamento|Linee guida|Delibera|Comunicazione|Decreto|Legge|D\.\s?Lgs|Decreto-legge)", t): continue
                if re.search(r"turismo|compagnie aeree|diritti audiovisivi|commercializzazione dei diritti|conflitt[oi] di interessi|profili professionali|raggruppamenti temporanei", t, re.I): continue
                if (fo, t[:120]) in presenti: continue
                presenti.add((fo, t[:120]))
            if len(t) < 15: continue
            ri_x = ri
            if n == "eiopa" and not re.search(r"distribut|POG|product oversight|IDD|insurance-based|complaint|reclam|cross-selling|conflict", t, re.I): ri_x = "ALTRO (imprese di assicurazione)"
            k = (fo, x["link"].split("#")[0])
            if k in presenti: continue
            presenti.add(k)
            rec(fonte=fo, sezione=se, tipologia=tp, obbl=ob, rilevanza=ri_x, titolo=t[:300], data=data_it(t + " " + x.get("contesto", "")) or _data_en(x.get("contesto")),
                link=x["link"], note="ABROGATO" if re.search(r"abrogat|repealed", t, re.I) else "")
    # COVIP e AGCM: atti cardine per la banca, inseriti a mano se le raccolte automatiche non hanno risultati
    if not _j(GH / "f1_covip.json"):
        for t, d in [("Regolamento sulle modalità di adesione alle forme pensionistiche complementari", ""),
                     ("Schema di Nota informativa e istruzioni di compilazione per le forme pensionistiche complementari", ""),
                     ("Istruzioni di vigilanza in materia di trasparenza delle forme pensionistiche complementari", "")]:
            rec(fonte="COVIP", sezione="Normativa COVIP", tipologia="Deliberazione COVIP", obbl="OBBL", rilevanza="BANCA (collocatore di forme pensionistiche)",
                titolo=t, data=d, link="https://www.covip.it/", note="elenco COVIP da completare: sito non raggiungibile in automatico; estremi da verificare")
    if not _j(GH / "f1_agcm.json"):
        for t in ["Regolamento sulle procedure istruttorie in materia di tutela del consumatore (pratiche commerciali scorrette e clausole vessatorie)",
                  "Linee guida sulla compliance antitrust", "Regolamento attuativo in materia di rating di legalità",
                  "Linee guida sulla modalità di applicazione dei criteri di quantificazione delle sanzioni amministrative pecuniarie"]:
            rec(fonte="AGCM", sezione="Normativa e regolamenti AGCM", tipologia="Regolamento / linee guida AGCM", obbl="OBBL" if t.startswith("Regolamento") else "BP",
                rilevanza="BANCA", titolo=t, link="https://www.agcm.it/", note="elenco AGCM da completare: estremi da verificare")

GH = Path("/home/claude/vp-alert-feed/dati/catalogo")

if __name__ == "__main__":
    ue(); italia(); bdi(); uif(); ivass(); consob(); nuove_fonti()
    out = D / "inventario.json"; out.write_text(json.dumps(R, ensure_ascii=False, indent=0), encoding="utf-8")
    from collections import Counter
    print(len(R)); print(Counter(r["fonte"] for r in R).most_common()); print(Counter((r["fonte"], r["obbl"]) for r in R).most_common(30))
