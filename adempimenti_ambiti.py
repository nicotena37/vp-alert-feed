"""Costruisce gli adempimenti della legal inventory per gli ambiti antiriciclaggio, nei tre livelli:
sintetico = macro-requisiti, standard = obblighi operativi, analitico = punti normativi (articolo/comma/lettera) col testo vigente della biblioteca."""
import json, re, sys
from pathlib import Path
SP = Path(__file__).parent; sys.path.insert(0, str(SP))
from parse_art import estratto, pulisci
BIB = SP / "biblioteca" / "testi"
def carica(i):
    d = json.loads((BIB / f"{i}.json").read_text(encoding="utf-8")); return d, {a["num"]: a["testo"] for a in d["articoli"]}
SRC = {}
for k, i, nome in [("L", "IT-decreto.legislativo-2007-11-21-231", "d.lgs. 231/2007"), ("F", "IT-decreto.legislativo-2007-06-22-109", "d.lgs. 109/2007"), ("U", "UE-32024R1624", "Reg. (UE) 2024/1624 (AMLR)")]:
    d, A = carica(i); SRC[k] = {"id": i, "nome": nome, "A": A, "url": d.get("url", ""), "scaricato": d.get("scaricato_il", "")[:10]}
B = None
if (BIB / "BDI-AV-2019.json").exists():
    d = json.loads((BIB / "BDI-AV-2019.json").read_text(encoding="utf-8"))
    if d["n_articoli"] > 15: B = d
def P(k, art, c=None, l=None, sintesi=""):
    s = SRC[k]; rif = (f"art. {art}" if k != "U" else f"art. {art}") + (f", {'c.' if k != 'U' else 'par.'} {c}" if c else "") + (f", lett. {l}" if l else "")
    e = estratto(s["A"], art, c, l)
    if not e and c: e = estratto(s["A"], art)
    return {"norma": s["nome"], "rif": rif, "testo": sintesi, "estratto": e[:1500], "url": s["url"], "fonte_id": s["id"]}
PARTI = ["Parte prima"]*3 + ["Parte seconda"]*8 + ["Parte terza"]*2 + ["Parte quarta"]*6 + ["Parte quinta"]*2
def PB(chiave, sintesi, ultima=False):
    U = "https://www.bancaditalia.it/compiti/vigilanza/normativa/archivio-norme/disposizioni/20190730-dispo/Disposizioni.pdf"
    if not B: return {"norma": "Disposizioni Banca d'Italia sull'adeguata verifica (30/7/2019)", "rif": chiave, "testo": sintesi, "estratto": "", "url": U, "fonte_id": "BDI-AV-2019"}
    vere = [a for a in B["articoli"] if re.fullmatch(r"Sezione [IVX]+(?: \(\d+\))?", a["num"]) and "...." not in a.get("rubrica", "") and len(a["testo"]) > 300]
    NOMI = ["Parte prima", "Parte seconda", "Parte terza", "Parte quarta", "Parte quinta", "Parte sesta"]; pp, PARTI = -1, []
    for v in vere:
        if re.sub(r" \(\d+\)", "", v["num"]) == "Sezione I": pp += 1
        PARTI.append(NOMI[max(0, pp)])
    rx = re.compile(chiave, re.I); ii = [k for k, a in enumerate(vere) if rx.search(a.get("rubrica", ""))]; i = (ii[-1] if ultima else ii[0]) if ii else None
    if i is None: return {"norma": "Disposizioni Banca d'Italia sull'adeguata verifica (30/7/2019)", "rif": chiave, "testo": sintesi, "estratto": "", "url": U, "fonte_id": "BDI-AV-2019"}
    a = vere[i]; sez = re.sub(r" \(\d+\)", "", a["num"]); parte = "Parte quarta" if ultima else PARTI[i]
    return {"norma": "Disposizioni Banca d'Italia sull'adeguata verifica (30/7/2019)", "rif": f"{parte}, {sez} – {a.get('rubrica','').strip()}", "testo": sintesi, "estratto": pulisci(a["testo"])[:1500], "url": B["url"], "fonte_id": "BDI-AV-2019"}
LIB = {}
def lib(amb, sigla, macro, ad): LIB[amb] = {"ambito": amb, "sigla": sigla, "versione": "2026-11-27", "macro": [{"id": m, "titolo": t} for m, t in macro], "adempimenti": ad}
def A(i, m, tit, parole, sost, punti, testo=""):
    return {"id": i, "macro": m, "titolo": tit, "testo": testo, "norma": "; ".join(dict.fromkeys(p["norma"] for p in punti)), "articolo": "; ".join(p["rif"] for p in punti), "parole": parole, "sostituisce": sost, "punti": punti}

lib("Antiriciclaggio||Gestione di adeguata verifica", "AV", [
  ("AV-M1", "Quando e quanto: approccio basato sul rischio"), ("AV-M2", "Identificazione del cliente e dell'esecutore"), ("AV-M3", "Titolare effettivo"),
  ("AV-M4", "Scopo, natura e profilo di rischio"), ("AV-M5", "Misure rafforzate, PEP e paesi ad alto rischio"), ("AV-M6", "Misure semplificate e ricorso a terzi"),
  ("AV-M7", "Controllo costante"), ("AV-M8", "Impossibilità di completare la verifica"), ("AV-M9", "Nuove regole UE (AMLR, dal 10 luglio 2027)")], [
  A("AV-01", "AV-M1", "Svolgere l'adeguata verifica nei casi previsti, anche sui clienti già acquisiti", "identifica cliente|revisione periodica", [], [
     P("L", "17", "1", "a", "Adeguata verifica all'instaurazione di un rapporto continuativo"), P("L", "17", "1", "b", "Adeguata verifica sulle operazioni occasionali da 15.000 euro (o trasferimenti di fondi oltre 1.000 euro)"),
     P("L", "17", "2", "a", "Adeguata verifica in ogni caso se c'è sospetto di riciclaggio o finanziamento del terrorismo"), P("L", "17", "2", "b", "Adeguata verifica in ogni caso se ci sono dubbi sui dati già ottenuti"),
     P("L", "17", "4", None, "Applicare l'adeguata verifica anche ai clienti già acquisiti quando cambia il livello di rischio")]),
  A("AV-02", "AV-M1", "Graduare le misure in base al rischio e poterlo dimostrare all'autorità", "profilo di rischio", ["ADE-05"], [
     P("L", "17", "3", None, "Misure proporzionate al rischio, dimostrabili all'autorità, con i criteri relativi al cliente e all'operazione"), PB(r"approccio basato sul rischio", "Approccio basato sul rischio secondo le Disposizioni Banca d'Italia")]),
  A("AV-03", "AV-M2", "Identificare il cliente e verificarne l'identità con un documento valido", "identifica cliente", ["ADE-01"], [
     P("L", "18", "1", "a", "Identificare il cliente e verificarne l'identità con documenti, dati o informazioni da fonte affidabile e indipendente"),
     P("L", "19", "1", "a", "Identificazione in presenza, con documento d'identità in corso di validità di cui si acquisisce copia"),
     P("L", "18", "2", None, "Identificare e verificare prima di instaurare il rapporto o eseguire l'operazione"), PB(r"identificazione del cliente e dell", "Modalità di identificazione del cliente e dell'esecutore (Disposizioni Banca d'Italia)"), PB(r"La verifica dei dati", "Verifica dei dati di cliente, esecutore e titolare effettivo (Disposizioni Banca d'Italia)")]),
  A("AV-04", "AV-M2", "Identificare l'esecutore e verificarne il potere di rappresentanza", "esecutore", ["ADE-01"], [
     P("L", "18", "1", "a", "Stesse misure verso l'esecutore, compresa la verifica dell'esistenza e dell'ampiezza del potere di rappresentanza")]),
  A("AV-05", "AV-M2", "Identificare a distanza solo nei casi ammessi", "identifica cliente", ["ADE-01"], [
     P("L", "19", "1", "a", "Identificazione senza presenza fisica solo nei casi previsti (atti pubblici, firma digitale, identità digitale, cliente già identificato, bonifico in casi limitati)"), PB(r"operativit. a distanza", "Operatività a distanza: cautele e controlli (Disposizioni Banca d'Italia)")]),
  A("AV-06", "AV-M2", "Posticipare la verifica solo con basso rischio e completarla entro 30 giorni", "completezza dei dati", [], [P("L", "18", "3", None, "Verifica posticipata solo a basso rischio, con acquisizione immediata dei dati e completamento entro 30 giorni")]),
  A("AV-07", "AV-M3", "Individuare e verificare il titolare effettivo", "titolare effettivo", ["ADE-02"], [
     P("L", "18", "1", "b", "Identificare il titolare effettivo e verificarne l'identità con misure proporzionate al rischio, ricostruendo l'assetto proprietario e di controllo"),
     P("L", "20", "1", None, "Titolare effettivo = persona fisica a cui è attribuibile in ultima istanza la proprietà o il controllo"), P("L", "20", "2", None, "Società di capitali: partecipazione oltre il 25% (proprietà diretta o indiretta)"),
     P("L", "20", "3", None, "Se la proprietà non basta: chi esercita il controllo"), P("L", "20", "5", None, "In via residuale: chi ha poteri di rappresentanza legale, amministrazione o direzione"),
     P("L", "20", "6", None, "Conservare traccia delle verifiche fatte per individuare il titolare effettivo"), PB(r"identificazione del titolare effettivo", "Identificazione del titolare effettivo (Disposizioni Banca d'Italia)")]),
  A("AV-08", "AV-M3", "Ottenere dal cliente, per iscritto, le informazioni sul titolare effettivo", "titolare effettivo|questionario", ["ADE-02"], [
     P("L", "22", "1", None, "Il cliente fornisce per iscritto, sotto la propria responsabilità, le informazioni necessarie e aggiornate"), P("L", "19", "1", "a", "Il cliente fornisce sotto la propria responsabilità le informazioni per identificare il titolare effettivo")]),
  A("AV-09", "AV-M3", "Consultare il Registro dei titolari effettivi", "registro", ["ADE-03"], [P("L", "21-ter", None, None, "Accedere tempestivamente alle informazioni sul titolare effettivo nel Registro delle imprese")]),
  A("AV-10", "AV-M4", "Acquisire e valutare scopo e natura del rapporto", "questionario", ["ADE-04"], [
     P("L", "18", "1", "c", "Informazioni su scopo e natura del rapporto: relazioni cliente-esecutore e cliente-titolare effettivo, attività lavorativa; altre in funzione del rischio"), PB(r"acquisizione e la valutazione delle informazioni", "Informazioni su scopo e natura (Disposizioni Banca d'Italia)")]),
  A("AV-11", "AV-M4", "Profilare il cliente e attribuirgli una classe di rischio", "profilo di rischio|revisione periodica", ["ADE-05"], [
     P("L", "17", "3", "a", "Criteri relativi al cliente: natura giuridica, attività, comportamento, area geografica"), P("L", "17", "3", "b", "Criteri relativi all'operazione o al rapporto: tipologia, modalità, importo, frequenza, ragionevolezza, area geografica"),
     PB(r"Profilatura della clientela", "Profilatura e classi di rischio (Disposizioni Banca d'Italia)")]),
  A("AV-12", "AV-M5", "Applicare misure rafforzate quando il rischio è elevato", "rafforzata|valuta la pratica", ["ADE-06"], [
     P("L", "24", "1", None, "Misure rafforzate in presenza di rischio elevato"), P("L", "24", "2", None, "Fattori di rischio elevato relativi al cliente, ai prodotti e servizi, alle aree geografiche"),
     P("L", "24", "3", None, "Esaminare contesto e finalità delle operazioni complesse o di importo insolitamente elevato"), P("L", "25", "1", None, "Come: più informazioni su cliente e titolare effettivo, approfondire scopo e natura, controllo costante più frequente"),
     PB(r"Misure rafforzate di adeguata verifica", "Misure rafforzate (Disposizioni Banca d'Italia)"), PB(r"importi insolitamente", "Operazioni di importo insolitamente elevato (Disposizioni Banca d'Italia)", True)]),
  A("AV-13", "AV-M5", "Applicare sempre le misure rafforzate nei casi previsti dalla legge", "rafforzata", ["ADE-06"], [
     P("L", "24", "5", None, "Casi in cui le misure rafforzate sono sempre obbligatorie"), P("L", "25", "4-bis", None, "Paesi terzi ad alto rischio: misure aggiuntive"), PB(r"paesi terzi ad alto rischio", "Rapporti con paesi terzi ad alto rischio (Disposizioni Banca d'Italia)")]),
  A("AV-14", "AV-M5", "Persone politicamente esposte: individuarle, far autorizzare il rapporto, verificare l'origine dei fondi", "PEP|autorizza", ["ADE-07"], [
     P("L", "24", "5", "c", "Misure rafforzate sempre obbligatorie con le persone politicamente esposte"), P("L", "25", "4", None, "Procedure per individuare le PEP; autorizzazione dell'alta dirigenza, origine del patrimonio e dei fondi, controllo costante rafforzato"),
     P("L", "24", "6", None, "Ex PEP che hanno lasciato la carica da più di un anno: misure rafforzate se il rischio resta elevato"), PB(r"Persone politicamente esposte", "Persone politicamente esposte (Disposizioni Banca d'Italia)")]),
  A("AV-15", "AV-M6", "Applicare misure semplificate solo con basso rischio e mai in caso di sospetto", "", ["ADE-13"], [
     P("L", "23", "1", None, "Misure semplificate solo in presenza di basso rischio"), P("L", "23", "2", None, "Fattori di basso rischio da considerare"), P("L", "23", "4", None, "Mai misure semplificate se c'è sospetto"), PB(r"Misure semplificate di adeguata verifica", "Misure semplificate (Disposizioni Banca d'Italia)")]),
  A("AV-16", "AV-M6", "Ricorrere a terzi per l'adeguata verifica restando responsabili", "", [], [P("L", "26", "1", None, "Possibile ricorrere a terzi, ma la responsabilità resta della banca"), PB(r"Contenuto e modalit. di esecuzione degli obblighi", "Esecuzione da parte di terzi (Disposizioni Banca d'Italia)")]),
  A("AV-17", "AV-M7", "Svolgere il controllo costante del rapporto", "allert|revisione periodica", ["ADE-11"], [
     P("L", "18", "1", "d", "Controllo costante per tutta la durata del rapporto: esame dell'operatività, aggiornamento di dati e informazioni"), PB(r"controllo costante nel corso", "Controllo costante e aggiornamento (Disposizioni Banca d'Italia)")]),
  A("AV-18", "AV-M8", "Astenersi se l'adeguata verifica non è possibile e valutare la segnalazione", "astensione", ["ADE-09"], [
     P("L", "42", "1", None, "Impossibilità oggettiva di fare l'adeguata verifica: astenersi e valutare la segnalazione di operazione sospetta"), P("L", "42", "2", None, "Astenersi anche in presenza di società fiduciarie, trust o società anonime di paesi terzi ad alto rischio"),
     P("L", "42", "4", None, "Salvo i casi in cui l'operazione va eseguita per obbligo di legge")]),
  A("AV-19", "AV-M9", "Prepararsi alle nuove misure di adeguata verifica del Regolamento AMLR", "", ["ADE-14"], [
     P("U", "19", None, None, "Applicazione delle misure di adeguata verifica (dal 10 luglio 2027)"), P("U", "21", None, None, "Incapacità di applicare le misure: astensione e valutazione della segnalazione"),
     P("U", "22", None, None, "Identificazione e verifica di cliente e titolare effettivo"), P("U", "23", None, None, "Tempi della verifica"), P("U", "26", None, None, "Controllo costante del rapporto d'affari")]),
])
lib("Antiriciclaggio||Obblighi di conservazione", "CO", [("CO-M1", "Conservazione di documenti, dati e informazioni")], [
  A("CO-01", "CO-M1", "Conservare documenti, dati e informazioni dell'adeguata verifica e delle operazioni", "conserva", ["ADE-10"], [P("L", "31", "1", None, "Conservare quanto utile a prevenire, individuare o accertare riciclaggio e finanziamento del terrorismo"), P("L", "31", "2", None, "Conservare copia dei documenti dell'adeguata verifica e le scritture delle operazioni")]),
  A("CO-02", "CO-M1", "Conservare per 10 anni dalla fine del rapporto", "conserva", ["ADE-10"], [P("L", "31", "3", None, "Conservazione per 10 anni dalla cessazione del rapporto o dall'esecuzione dell'operazione")]),
  A("CO-03", "CO-M1", "Usare sistemi di conservazione che garantiscano integrità e ricostruzione dell'operatività", "conserva", [], [P("L", "32", "1", None, "Sistemi idonei a rispettare anche la normativa privacy e a consentire l'utilizzo dei dati"), P("L", "32", "2", None, "Prevenire la perdita dei dati e garantire la ricostruzione dell'operatività"), P("L", "32", "3", None, "Centri di servizi esterni: la responsabilità resta della banca")]),
])
lib("Antiriciclaggio||Gestione Operazioni Sospette", "SOS", [("SOS-M1", "Segnalazione delle operazioni sospette")], [
  A("SOS-01", "SOS-M1", "Segnalare alla UIF le operazioni sospette prima di eseguirle", "segnalazione di operazione sospetta|astensione e valutazione", ["ADE-12"], [P("L", "35", "1", None, "Segnalare senza ritardo alla UIF, prima di compiere l'operazione"), P("L", "35", "2", None, "Non compiere l'operazione finché non è stata segnalata, salvo i casi previsti"), P("L", "35", "3", None, "Contenuto della segnalazione e collaborazione con la UIF")]),
  A("SOS-02", "SOS-M1", "Non comunicare al cliente o a terzi l'avvenuta segnalazione", "segnalazione di operazione sospetta", ["ADE-12"], [P("L", "39", "1", None, "Divieto di comunicare la segnalazione o le informazioni trasmesse"), P("L", "39", "3", None, "Eccezione: comunicazione tra intermediari dello stesso gruppo")]),
  A("SOS-03", "SOS-M1", "Tutelare la riservatezza del segnalante", "segnalazione di operazione sospetta", [], [P("L", "38", "1", None, "Misure per assicurare la riservatezza dell'identità di chi effettua la segnalazione")]),
])
lib("Antiriciclaggio||Contrasto al finanziamento del terrorismo", "FT", [("FT-M1", "Congelamento di fondi e risorse dei soggetti designati")], [
  A("FT-01", "FT-M1", "Congelare i fondi e non metterli a disposizione dei soggetti designati", "liste", ["ADE-08"], [P("F", "5", "1", None, "I fondi congelati non possono essere trasferiti, disposti o utilizzati"), P("F", "5", "4", None, "Divieto di mettere fondi o risorse a disposizione dei soggetti designati"), P("F", "5", "5", None, "Divieto di aggirare le misure di congelamento")]),
  A("FT-02", "FT-M1", "Comunicare alla UIF le misure di congelamento e le operazioni dei soggetti designati", "liste", ["ADE-08"], [P("F", "7", "1", None, "Comunicare alla UIF le misure di congelamento applicate"), P("F", "7", "2", None, "Comunicare tempestivamente operazioni, rapporti e informazioni riconducibili ai soggetti designati")]),
])
out = SP / "biblioteca" / "adempimenti_ambiti"; out.mkdir(exist_ok=True); indice = {"aggiornato": "2026-11-27", "ambiti": []}
for amb, L in LIB.items():
    f = f"legal_{L['sigla'].lower()}.json"; (out / f).write_text(json.dumps(L, ensure_ascii=False), encoding="utf-8")
    vuoti = [(a["id"], p["rif"]) for a in L["adempimenti"] for p in a["punti"] if not p["estratto"]]
    fonti = sorted({p["norma"] for a in L["adempimenti"] for p in a["punti"]})
    indice["ambiti"].append({"ambito": amb, "file": f, "n": len(L["adempimenti"]), "punti": sum(len(a["punti"]) for a in L["adempimenti"]), "macro": len(L["macro"]), "fonti": fonti})
    print(amb, len(L["macro"]), len(L["adempimenti"]), sum(len(a["punti"]) for a in L["adempimenti"]), "senza testo:", vuoti)
(out / "legal_indice.json").write_text(json.dumps(indice, ensure_ascii=False, indent=1), encoding="utf-8")
