import json, re
from collections import Counter, defaultdict
from pathlib import Path
D = Path(__file__).parent
R = json.loads((D / "inventario.json").read_text(encoding="utf-8"))

TEM = [  # tematica della tassonomia -> parole chiave nel titolo
 ("Antiriciclaggio", r"riciclagg|terroris|adeguata verifica|titolar[ei] effettiv|operazioni sospette|anomali|trasferimenti di fondi|AMLA|misure restrittive|congelament|UIF\b|proliferazione"),
 ("Contrasto all'usura", r"usura|tassi effettivi globali"),
 ("Vigilanza prudenziale", r"prudenzial|requisiti di capitale|fondi propri|liquidit|leva finanziaria|grandi esposizioni|risanamento|risoluzione|\bSREP\b|\bMVU\b|vigilanza (bancaria|unico)|enti creditizi|ICAAP|ILAAP|rischio di credito|\bIRB\b|garanzia dei depositi|conglomerat|intermediari finanziari"),
 ("Segnalazioni di Vigilanza", r"segnalazion|reporting|matrice dei conti|centrale dei rischi|AnaCredit|statistic|informazioni (statistiche|di vigilanza)|norme tecniche di attuazione .{0,40}(segnal|modell|formati)"),
 ("Informativa finanziaria (reporting)", r"bilanc|contabil|\bIAS\b|\bIFRS\b|principi contabili|revisione legale|rendicontazione|informativa (al pubblico|finanziaria)|ESEF|ESRS"),
 ("Trasparenza e tutela del consumatore", r"trasparenz|consumator|credito ai consumatori|credito immobiliare|conto di base|conti di pagamento|pratiche commerciali|clausole|accessibilit|distanza|correttezza delle relazioni"),
 ("Gestione reclami", r"reclam|arbitro|risoluzione (alternativa|stragiudiziale)|mediazione|\bABF\b|\bACF\b"),
 ("Incassi e pagamenti", r"pagament|accordo monetario|convenzione monetaria|bonific|SEPA|moneta elettronica|carte di|assegn|cambial|interbancari|istantane|contante|banconot|monete metalliche"),
 ("Credito", r"credit|finanziament|mutu|garanzi|sofferenz|crediti deteriorati|cartolarizz|cessione del quinto|confidi|microcredito|fondo di garanzia|leasing|factoring"),
 ("Mercati finanziari", r"mercat|valori mobiliari|strumenti finanziari|servizi di investimento|MiFID|abusi di mercato|derivat|controparti centrali|depositari centrali|prospetto|vendite allo scoperto|negoziazion|consulenz|PRIIP|cripto|crowdfunding|\bDLT\b|post.trading"),
 ("Emittenti", r"emittent|quotat|parti correlate|offerte? pubblic|informazioni regolamentate|azionist|\bOPA\b"),
 ("Gestione collettiva", r"gestione collettiva|OICR|OICVM|fondi (comuni|di investimento alternativi|monetari)|ELTIF|\bSGR\b|\bSICAV\b|\bSICAF\b|gestori"),
 ("Distribuzione assicurativa", r"assicura|IVASS|ISVAP|polizz|\bIDD\b|\bIBIP\b|riassicura"),
 ("Benchmark finanziari", r"indici di riferimento|benchmark"),
 ("ESG e Sostenibilità", r"sostenibil|clima|ambiental|\bESG\b|tassonomia|obbligazioni verdi|dovere di diligenza|energetic"),
 ("IT e Digital", r"informatic|\bICT\b|ciber|cyber|resilienza operativa|digital|intelligenza artificiale|dati \(?non personali|cloud|identificazione elettronica|firma elettronica|esternalizz|continuit"),
 ("Privacy", r"dati personali|protezione dei dati|privacy|vita privata|Garante per la protezione|videosorveglianza|telemarketing|opposizioni"),
 ("Governance", r"governo societario|governance|organizzazione|controlli interni|esponenti|idoneit|amministrazione|whistleblow|segnalano violazioni|compliance|funzione di conformit"),
 ("Remunerazione e incentivazione", r"remunerazion|incentiv|retribuzion"),
 ("Conflitti di interesse", r"conflitt[oi] di interess|soggetti collegati|parti correlate|interlocking"),
 ("Sviluppo commerciale e Rete vendita", r"agenti in attivit|mediatori creditizi|consulenti finanziari|offerta fuori sede|pubblicit|collocamento|rete (di )?vendita|promotori"),
 ("Fisco", r"impost|tribut|fiscal|\bIVA\b|valore aggiunto|redditi|bollo|accertamento|riscossione|FATCA|scambio automatico|cooperazione amministrativa|evasione|elusione"),
 ("Diritto del lavoro", r"lavor|maternit|paternit|pari opportunit|parità di trattamento|disabil|previdenz|pension|contratti di lavoro|orario"),
 ("Sicurezza sui luoghi di lavoro", r"sicurezza (e (della )?salute|sul lavoro|nei luoghi)|salute e (della )?sicurezza|infortun|INAIL"),
 ("Responsabilità amministrativa delle persone giuridiche - D. Lgs. 231/01", r"responsabilit.{1,3} amministrativa|231/2001|corruzione|\breati\b"),
 ("Antitrust", r"concorrenza|intese|posizione dominante|antitrust|golden power|poteri speciali"),
 ("Gestione patrimonio immobiliare", r"edilizi|immobil|locazion|catast"),
 ("Affari legali e societari", r"societ|codice civile|insolvenz|crisi d.impresa|sovraindebitamento|fallim|contratti pubblici|appalti|procedimento amministrativo|codice di procedura"),
]
TEMRX = [(t, re.compile(r, re.I)) for t, r in TEM]
VP, MF, PG, IT_, AML = "Vigilanza prudenziale", "Mercati finanziari", "Incassi e pagamenti", "IT e Digital", "Antiriciclaggio"
BASE_TEM = {"32013R0575": VP, "32013L0036": VP, "32014L0059": VP, "32014R0806": VP, "32014L0049": VP, "32017R2402": "Credito",
    "32014L0065": MF, "32014R0600": MF, "32014R0596": MF, "32012R0648": MF, "32014R0909": MF, "32017R1129": MF, "32015R2365": MF,
    "32012R0236": MF, "32023R1114": MF, "32014R1286": MF, "32015L2366": PG, "32012R0260": PG, "32009L0110": PG, "32022R2554": IT_,
    "32022L2555": IT_, "32024R1689": IT_, "32016R1011": "Benchmark finanziari", "32019R2088": "ESG e Sostenibilità", "32020R0852": "ESG e Sostenibilità",
    "32022L2464": "ESG e Sostenibilità", "32015L0849": AML, "32024R1624": AML, "32024L1640": AML, "32024R1620": AML,
    "32016L0097": "Distribuzione assicurativa", "32009L0065": "Gestione collettiva", "32011L0061": "Gestione collettiva", "32017R1131": "Gestione collettiva",
    "32015R0760": "Gestione collettiva", "32016R0679": "Privacy", "32014L0017": "Trasparenza e tutela del consumatore", "32008L0048": "Trasparenza e tutela del consumatore",
    "32023L2225": "Trasparenza e tutela del consumatore", "32014L0092": "Trasparenza e tutela del consumatore"}
DIR_TEM = [("06202020", VP), ("06202025", MF), ("06202010", "Distribuzione assicurativa"), ("102010", "Politica monetaria e BCE (fuori tassonomia)"),
    ("102020", "Politica monetaria e BCE (fuori tassonomia)"), ("102030", "Politica monetaria e BCE (fuori tassonomia)"), ("1020", "Politica monetaria e BCE (fuori tassonomia)"),
    ("014075", "Politica monetaria e BCE (fuori tassonomia)"), ("014095", "Politica monetaria e BCE (fuori tassonomia)"), ("1007", "Segnalazioni di Vigilanza"),
    ("1040", PG), ("152040", "Trasparenza e tutela del consumatore"), ("152010", "Trasparenza e tutela del consumatore"), ("1710", "Affari legali e societari"),
    ("173010", "Affari legali e societari"), ("173020", "Affari legali e societari"), ("0950", "Fisco"), ("092030", "Fisco"), ("093010", "Fisco"),
    ("05202010", "Sicurezza sui luoghi di lavoro"), ("0520", "Diritto del lavoro"), ("132060", IT_), ("0810", "Antitrust"), ("0820", "Antitrust"),
    ("0830", "Antitrust"), ("151010", "ESG e Sostenibilità"), ("062020", VP), ("0610", VP)]
EXTRA = [  # regole aggiuntive per le voci senza tematica
 ("Incassi e pagamenti", r"\beuro\b|euro\)|\bECU\b|moneta unica|biglietti di banca|monete in euro|contraffazion|Pericle"),
 ("Politica monetaria e BCE (fuori tassonomia)", r"indirizzi di massima per le politiche economiche|politica monetaria|articolo 140, paragrafo 2"),
 ("Responsabilità amministrativa delle persone giuridiche - D. Lgs. 231/01", r"frode che lede gli interessi finanziari|contro le mafie"),
 ("Remunerazione e incentivazione", r"2021/923"),
 ("Incassi e pagamenti", r"2018/389"), ("Mercati finanziari", r"2017/565|Consob|2015/760"), ("Antiriciclaggio", r"2016/1675|tracciabilit"),
 ("IT e Digital", r"2023/2854|2019/1024|2018/1972|2022/2557|banche di dati|apertura dei dati|comunicazioni elettroniche|riutilizzo dell.informazione"),
 ("Privacy", r"conservazione dei dati generati"),
 ("Vigilanza prudenziale", r"obbligazioni (bancarie )?garantite|sistema bancario|tutela del risparmio|investitori in banche|vigilanza della Banca d.Italia"),
 ("Governance", r"onorabilit"),
 ("Informativa finanziaria (reporting)", r"revisori legali|revisioni legali|2014/95|78/660|2023/2864|punto di accesso unico"),
 ("Fisco", r"2006/112|buoni fruttiferi|contribuente|spesa pubblica"),
 ("Trasparenza e tutela del consumatore", r"codice del consumo|2019/771|85/374|danno da prodotti|vendita di beni"),
 ("Credito", r"aste giudiziarie|procedure esecutive"),
 ("Diritto del lavoro", r"persone handicappate|disabil"),
 ("Sicurezza sui luoghi di lavoro", r"2014/27/UE"),
 ("Affari legali e societari", r"segreti commerciali|2016/943|ordine europeo di indagine|2014/41|Eurojust|trasformazioni|fusioni e scissioni transfrontaliere|2019/2121|2019/1160|2024/505|2025/37|2017/1132"),
]
FUORI = (r"caffe'|cicoria|alimenti per lattanti|2013/46/UE|disposizioni anticipate di trattamento|banca dati nazionale del DNA|legge 30 giugno 2009, n\. 85|"
         r"apparecchiature radio|atmosfera potenzialmente esplosiva|direttiva 2014/34/UE|qualifiche professionali|test della proporzionalit|2024/782|pacchetti turistici|"
         r"93/109|procedimenti penali|2002/59|traffico navale|Regolamento \(CE\) n\. 261/2004|negato imbarco|Banche e a Fondi multilaterali|"
         r"Banche multilaterali|Fondi e Banche internazionali|Commissione parlamentare di inchiesta")
for r in R:
    s = f"{r['titolo']} {r.get('tipologia','')}"
    tem = [t for t, rx in TEMRX if rx.search(s)][:4]
    if not tem:
        sez = r.get("sezione", "")
        m = re.search(r"basati su (\d{5}[A-Z]\d{4})", sez)
        if m and m.group(1) in BASE_TEM: tem = [BASE_TEM[m.group(1)]]
        else:
            for code, t in DIR_TEM:
                if re.search(r"(^|[ :])" + code, sez): tem = [t]; break
        if not tem and r["fonte"].endswith("atti BCE"): tem = ["Politica monetaria e BCE (fuori tassonomia)"]
        if not tem and r["fonte"].startswith(("EBA", "ESMA")): tem = [VP if r["fonte"].startswith("EBA") else MF]
        if not tem and r["fonte"] == "Consob": tem = [MF]
        if not tem and r["fonte"] == "Banca d'Italia": tem = [VP]
        FT = {"Garante privacy": "Privacy", "AGCM": "Antitrust", "COVIP": "Diritto del lavoro", "OAM": "Sviluppo commerciale e Rete vendita",
              "Agenzia delle Entrate": "Fisco", "MEF - Dipartimento del Tesoro": AML, "EIOPA": "Distribuzione assicurativa", "UIF": AML, "IVASS": "Distribuzione assicurativa"}
        if not tem and r["fonte"] in FT: tem = [FT[r["fonte"]]]
        if not tem and r["fonte"].startswith("EIOPA"): tem = ["Distribuzione assicurativa"]
    if r["fonte"] == "Garante privacy" and "Privacy" not in tem: tem = ["Privacy"] + tem[:3]
    if r["fonte"] == "MEF - Dipartimento del Tesoro" and AML not in tem: tem = [AML] + tem[:3]
    if not tem:
        for t, rx in EXTRA:
            if re.search(rx, r["titolo"], re.I): tem = [t]; break
    r["tematiche"] = tem or ["Da classificare"]
n0 = len(R); R = [r for r in R if not re.search(FUORI, r["titolo"], re.I)]
print("esclusi perché estranei alla banca:", n0 - len(R))

ORD_FONTE = ["Gazzetta ufficiale UE", "Gazzetta ufficiale UE - atti BCE", "Gazzetta Ufficiale (Normattiva)", "Banca d'Italia",
             "EBA (orientamenti recepiti dalla Banca d'Italia)", "ESMA (orientamenti recepiti dalla Banca d'Italia)", "UIF", "MEF - Dipartimento del Tesoro",
             "IVASS", "Consob", "EBA", "ESMA", "EIOPA", "Garante privacy", "AGCM", "COVIP", "OAM", "Agenzia delle Entrate"]
PARTI = {"Gazzetta ufficiale UE": "PARTE 1 - GAZZETTE UFFICIALI", "Gazzetta ufficiale UE - atti BCE": "PARTE 1 - GAZZETTE UFFICIALI",
         "Gazzetta Ufficiale (Normattiva)": "PARTE 1 - GAZZETTE UFFICIALI", "Banca d'Italia": "PARTE 2 - BANCA D'ITALIA E UIF",
         "EBA (orientamenti recepiti dalla Banca d'Italia)": "PARTE 2 - BANCA D'ITALIA E UIF", "ESMA (orientamenti recepiti dalla Banca d'Italia)": "PARTE 2 - BANCA D'ITALIA E UIF",
         "UIF": "PARTE 2 - BANCA D'ITALIA E UIF", "MEF - Dipartimento del Tesoro": "PARTE 2 - BANCA D'ITALIA E UIF", "IVASS": "PARTE 3 - IVASS", "Consob": "PARTE 4 - CONSOB",
         "EBA": "PARTE 5 - AUTORITÀ EUROPEE (EBA, ESMA, EIOPA)", "ESMA": "PARTE 5 - AUTORITÀ EUROPEE (EBA, ESMA, EIOPA)", "EIOPA": "PARTE 5 - AUTORITÀ EUROPEE (EBA, ESMA, EIOPA)",
         "Garante privacy": "PARTE 6 - ALTRE AUTORITÀ ITALIANE", "AGCM": "PARTE 6 - ALTRE AUTORITÀ ITALIANE", "COVIP": "PARTE 6 - ALTRE AUTORITÀ ITALIANE",
         "OAM": "PARTE 6 - ALTRE AUTORITÀ ITALIANE", "Agenzia delle Entrate": "PARTE 6 - ALTRE AUTORITÀ ITALIANE"}
def k_ord(r):
    f = ORD_FONTE.index(r["fonte"]) if r["fonte"] in ORD_FONTE else 99
    sanz = r.get("sezione", "").startswith("Misure restrittive")
    return (f, sanz, r["tipologia"], -(int(r["data"][:4]) if r.get("data", "")[:4].isdigit() else 0), r["data"], r["titolo"])
R.sort(key=k_ord)

L = []
w = L.append
c_f = Counter(r["fonte"] for r in R); c_o = Counter(r["obbl"].split("/")[0] for r in R)
w("LEGAL INVENTORY - Compliance dyAInamic")
w("Normativa applicabile alla banca: norme, disposizioni delle autorità, orientamenti e comunicazioni")
w("Versione 2 - 07/11/2026 - costruita interrogando le banche dati ufficiali")
w("")
w("=" * 110)
w("RIEPILOGO")
w("=" * 110)
w(f"Voci totali: {len(R)}")
for f in ORD_FONTE: w(f"  {f:<55} {c_f.get(f, 0):>6}")
w("")
w("COME È STATA COSTRUITA")
w("  - Gazzetta ufficiale UE e atti BCE: banca dati ufficiale EUR-Lex/CELLAR, solo atti IN VIGORE, selezionati con il repertorio")
w("    della legislazione in vigore (banche, mercati mobiliari, assicurazioni, politica monetaria, capitali e pagamenti, consumatori,")
w("    diritto societario, fisco, lavoro, informatica e dati), più tutti gli atti delegati e di esecuzione collegati alle norme base")
w("    (CRR, CRD, BRRD, MiFID, MAR, EMIR, DORA, MiCA, PSD2, AMLR, SFDR, GDPR, AI Act...) e i regolamenti base sulle misure restrittive.")
w("  - Gazzetta Ufficiale italiana: API ufficiali di Normattiva, atti VIGENTI oggi, filtrati per materia bancaria e incrociati con le")
w("    direttive del catalogo UE (recepimenti); più un elenco di norme cardine (TUB, TUF, Codice civile...) segnate come tali.")
w("  - Banca d'Italia: archivio delle norme di vigilanza (tutte le categorie), orientamenti di vigilanza, elenco degli orientamenti")
w("    EBA/ESMA a cui la Banca d'Italia dichiara di conformarsi. UIF: provvedimenti, istruzioni, indicatori e schemi di anomalia.")
w("  - IVASS: regolamenti, provvedimenti normativi, comunicazioni, lettere al mercato, circolari ISVAP (con rilevanza per la banca).")
w("  - Consob: TUF e regolamenti attuativi, delibere, comunicazioni, richiami di attenzione, Q&A e orientamenti per area.")
w("")
w("LEGENDA")
w("  Rilevanza: BANCA = si applica alla banca; INDIRETTA = rivolta a banche centrali o organi BCE ma con effetti sulla banca;")
w("             BANCA (distributore) = norme IVASS che riguardano la banca come distributore di polizze; ALTRO = per completezza")
w("  Tematiche: assegnate in automatico con parole chiave sulla tassonomia (29 tematiche); da validare.")
w("")
w("NOVITÀ DELLA VERSIONE 2")
w("  - Parte 5: elenco completo di orientamenti, raccomandazioni e opinioni EBA (sito EBA) e, dove raggiungibili, ESMA ed EIOPA.")
w("  - Parte 6: Garante privacy (linee guida, provvedimenti generali, autorizzazioni, codici di condotta, temi banche e credito),")
w("    AGCM, COVIP, OAM, Agenzia delle Entrate (circolari, provvedimenti e risoluzioni su banche e intermediari).")
w("  - Parte 2: MEF - Dipartimento del Tesoro (prevenzione dei reati finanziari).")
w("  - Circolari ISVAP: segnata la vigenza secondo l'elenco IVASS (abrogata o ancora elencata).")
w("  - Ridotte le voci senza tematica.")
w("")
w("LIMITI NOTI")
w("  - Le tematiche e il filtro di pertinenza della Gazzetta italiana sono automatici: da validare.")
w("  - Dove un sito non è raggiungibile in automatico (vedi nota della voce) l'elenco è parziale e va completato.")
w("  - ESMA: l'elenco completo non è stato raccolto (pagina caricata via script); per ora valgono i 15 orientamenti ESMA recepiti")
w("    dalla Banca d'Italia e gli orientamenti ESMA citati da Consob. OAM: il sito rifiuta l'accesso automatico (HTTP 403).")
w("  - COVIP: sito non raggiungibile; inseriti 3 atti cardine con estremi da verificare.")
w("")
parte = fonte = tip = None
for r in R:
    p = PARTI.get(r["fonte"], "ALTRO")
    if p != parte:
        parte = p; fonte = tip = None
        w(""); w("#" * 110); w(p); w("#" * 110)
    sez = r["fonte"] + (" - MISURE RESTRITTIVE (SANZIONI FINANZIARIE)" if r.get("sezione", "").startswith("Misure restrittive") else "")
    if sez != fonte:
        fonte = sez; tip = None
        n = sum(1 for x in R if x["fonte"] == r["fonte"] and x.get("sezione", "").startswith("Misure restrittive") == r.get("sezione", "").startswith("Misure restrittive"))
        w(""); w("=" * 110); w(f"{sez}  ({n} voci)"); w("=" * 110)
    if r["tipologia"] != tip:
        tip = r["tipologia"]
        n = sum(1 for x in R if x["fonte"] == r["fonte"] and x["tipologia"] == tip and x.get("sezione", "").startswith("Misure restrittive") == r.get("sezione", "").startswith("Misure restrittive"))
        w(""); w(f"--- {tip} ({n}) ---")
    estr = f"{r['estremi']} - " if r.get("estremi") and r["estremi"] not in r["titolo"] else ""
    data = f" [{r['data']}]" if r.get("data") else ""
    w(f"{estr}{r['titolo'][:420]}{data}")
    extra = [f"tematiche: {', '.join(r['tematiche'])}"]
    if r.get("rilevanza") and r["rilevanza"] != "BANCA": extra.append(f"rilevanza: {r['rilevanza']}")
    if r.get("note"): extra.append(r["note"][:220])
    w("        " + " | ".join(extra))
    if r.get("link"): w("        " + r["link"])
(D / "legal_inventory.txt").write_text("\n".join(L) + "\n", encoding="utf-8")

# Excel
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
wb = Workbook(); ws = wb.active; ws.title = "Legal inventory"
H = ["Parte", "Fonte", "Sezione", "Tipologia", "Rilevanza", "Estremi", "Titolo", "Data", "Tematiche", "Link", "Note"]
ws.append(H)
for r in R:
    ws.append([PARTI.get(r["fonte"], ""), r["fonte"], r.get("sezione", ""), r["tipologia"],
               r.get("rilevanza", ""), r.get("estremi", ""), r["titolo"][:1000], r.get("data", ""), "; ".join(r["tematiche"]), r.get("link", ""), r.get("note", "")])
for c in ws[1]: c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="163F7A"); c.alignment = Alignment(vertical="center", wrap_text=True)
for i, wdt in enumerate([22, 30, 30, 26, 22, 30, 90, 11, 40, 50, 40], 1): ws.column_dimensions[get_column_letter(i)].width = wdt
ws.freeze_panes = "A2"; ws.auto_filter.ref = ws.dimensions
s2 = wb.create_sheet("Riepilogo")
s2.append(["Fonte", "Tipologia", "Voci"])
agg = defaultdict(Counter)
for r in R: agg[(r["fonte"], r["tipologia"])]["n"] += 1
for (f, t), c in sorted(agg.items(), key=lambda x: (ORD_FONTE.index(x[0][0]) if x[0][0] in ORD_FONTE else 99, -sum(x[1].values()))):
    s2.append([f, t, c["n"]])
for c in s2[1]: c.font = Font(bold=True)
s2.column_dimensions["A"].width = 50; s2.column_dimensions["B"].width = 45
s3 = wb.create_sheet("Per tematica")
s3.append(["Tematica", "Voci"])
ct = defaultdict(Counter)
for r in R:
    for t in r["tematiche"]: ct[t]["n"] += 1
for t, c in sorted(ct.items(), key=lambda x: -x[1]["n"]): s3.append([t, c["n"]])
for c in s3[1]: c.font = Font(bold=True)
s3.column_dimensions["A"].width = 60
wb.save(D / "legal_inventory.xlsx")
print(len(R), len(L), Counter(t for r in R for t in r["tematiche"]).most_common(32))
