"""Quadro a livelli per Framework e temi: aree -> temi -> framework -> atti, organizzazione e policy.
Uscite: quadro.json (aree, temi con parole chiave, framework descritti, tassonomia VP) e indice_1.json / indice_2.json (storico alert per la ricerca)."""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

QUI = Path(__file__).parent
EL = lambda c: f"https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:{c}"
NT = lambda tipo, data, n: f"https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:{tipo}:{data};{n}"
BDI_CIRC = "https://www.bancaditalia.it/compiti/vigilanza/normativa/archivio-norme/circolari/"


def F(titolo, url, editore="EUR-Lex", tipo="Atto ufficiale"):
    return {"titolo": titolo, "url": url, "editore": editore, "tipo": tipo}


# sigla -> descrizione. temi = temi del sito (livello 2); policy = documenti interni tipici da presidiare
FW = {
 "DORA": dict(temi=["Cybersicurezza, ICT e DORA"], vigila="BCE e Banca d'Italia; le autorità europee (ESA) sorvegliano i fornitori ICT critici",
   sintesi="Regolamento europeo sulla resilienza operativa digitale del settore finanziario. Fissa regole uguali in tutta l'UE per gestire il rischio informatico, notificare gli incidenti gravi, testare la resilienza e controllare i fornitori di servizi ICT. Si applica dal 17 gennaio 2025.",
   destinatari="Banche, imprese di investimento, istituti di pagamento e di moneta elettronica, assicurazioni, gestori di fondi e quasi tutti gli intermediari finanziari; in modo indiretto i loro fornitori ICT.",
   obblighi=["Quadro di gestione del rischio ICT approvato e controllato dall'organo di gestione", "Classificazione degli incidenti ICT e notifica di quelli gravi all'autorità (iniziale, intermedia, finale)", "Programma di test di resilienza; test di penetrazione basati sulle minacce (TLPT) per le entità più rilevanti", "Gestione del rischio dei fornitori ICT: registro delle informazioni, clausole contrattuali minime, strategie di uscita", "Piani di continuità operativa e di ripristino ICT"],
   policy=["Policy di gestione del rischio ICT e di sicurezza", "Piano di continuità operativa e di ripristino ICT", "Policy sui fornitori ICT ed esternalizzazioni", "Procedura di gestione e notifica degli incidenti", "Programma dei test di resilienza"],
   fonti=[F("Regolamento (UE) 2022/2554 (DORA)", EL("32022R2554"))]),
 "NIS2": dict(temi=["Cybersicurezza, ICT e DORA"], vigila="Agenzia per la Cybersicurezza Nazionale (ACN)",
   sintesi="Direttiva europea sulla cibersicurezza di soggetti essenziali e importanti, recepita in Italia con il D.Lgs. 138/2024. Per banche e intermediari prevale DORA, che è la norma speciale; NIS2 resta rilevante per società del gruppo non finanziarie e per i fornitori.",
   destinatari="Soggetti essenziali e importanti in settori critici (energia, trasporti, sanità, infrastrutture digitali, servizi ICT gestiti…). Il settore finanziario segue DORA.",
   obblighi=["Registrazione sulla piattaforma ACN", "Misure di gestione dei rischi di cibersicurezza", "Notifica degli incidenti significativi (preallarme, notifica, relazione finale)", "Responsabilità e formazione degli organi di amministrazione", "Sicurezza della catena di fornitura"],
   policy=["Policy di sicurezza delle informazioni", "Procedura di gestione degli incidenti", "Policy sui fornitori"],
   fonti=[F("Direttiva (UE) 2022/2555 (NIS2)", EL("32022L2555")), F("D.Lgs. 4 settembre 2024, n. 138", NT("decreto.legislativo", "2024-09-04", "138"), "Normattiva")]),
 "AI Act": dict(temi=["Intelligenza artificiale e innovazione"], vigila="In Italia AgID e ACN (legge 132/2025); per le banche anche le autorità di vigilanza di settore",
   sintesi="Regolamento europeo sull'intelligenza artificiale, con un approccio basato sul rischio: vieta alcune pratiche, impone obblighi pesanti ai sistemi ad alto rischio e regole di trasparenza. Per le banche il punto chiave è il merito creditizio delle persone fisiche, classificato ad alto rischio (obblighi dal 2 dicembre 2027 dopo il Digital Omnibus).",
   destinatari="Fornitori e utilizzatori (deployer) di sistemi di IA nell'UE; le banche sono soprattutto utilizzatori.",
   obblighi=["Alfabetizzazione sull'IA del personale che usa questi sistemi", "Divieto delle pratiche proibite (es. manipolazione, punteggio sociale)", "Per i sistemi ad alto rischio usati dalla banca: uso conforme alle istruzioni, sorveglianza umana, monitoraggio, conservazione dei log", "Valutazione d'impatto sui diritti fondamentali per chi usa l'IA per il merito creditizio o per assicurazioni vita e salute", "Trasparenza verso il cliente su chatbot e contenuti generati"],
   policy=["Policy sull'uso dell'intelligenza artificiale", "Inventario dei sistemi di IA", "Procedura di validazione dei modelli", "Piano di formazione sull'IA"],
   fonti=[F("Regolamento (UE) 2024/1689 (AI Act)", EL("32024R1689"))]),
 "GDPR": dict(temi=["Privacy e protezione dei dati"], vigila="Garante per la protezione dei dati personali",
   sintesi="Regolamento generale sulla protezione dei dati personali, applicato dal 25 maggio 2018 e coordinato in Italia con il Codice privacy (D.Lgs. 196/2003, modificato dal D.Lgs. 101/2018). Il Digital Omnibus propone modifiche ancora in negoziato.",
   destinatari="Chiunque tratti dati personali di persone nell'UE: per la banca clienti, dipendenti, fornitori.",
   obblighi=["Base giuridica per ogni trattamento e informative chiare", "Registro dei trattamenti", "Valutazione d'impatto (DPIA) per i trattamenti a rischio elevato", "Responsabile della protezione dei dati (DPO)", "Notifica delle violazioni al Garante entro 72 ore", "Protezione dei dati fin dalla progettazione e regole sui trasferimenti fuori UE"],
   policy=["Policy privacy e modello organizzativo", "Procedura di gestione delle violazioni (data breach)", "Procedura DPIA", "Procedura per i diritti degli interessati", "Policy di conservazione dei dati"],
   fonti=[F("Regolamento (UE) 2016/679 (GDPR)", EL("32016R0679")), F("D.Lgs. 30 giugno 2003, n. 196", NT("decreto.legislativo", "2003-06-30", "196"), "Normattiva")]),
 "Pacchetto AML": dict(temi=["Antiriciclaggio e sanzioni finanziarie"], vigila="Banca d'Italia, UIF; dal 2028 AMLA per i gruppi selezionati",
   sintesi="Nuove regole europee antiriciclaggio: un regolamento direttamente applicabile dal 10 luglio 2027 (AMLR), la sesta direttiva (AMLD6) e la nuova autorità europea (AMLA). Fino ad allora restano il D.Lgs. 231/2007 e le disposizioni della Banca d'Italia del 2019.",
   destinatari="Banche, intermediari finanziari, istituti di pagamento, prestatori di cripto-attività e gli altri soggetti obbligati.",
   obblighi=["Adeguata verifica della clientela (ordinaria, semplificata, rafforzata) e controllo costante", "Identificazione del titolare effettivo (soglia del 25% con l'AMLR)", "Conservazione dei dati e dei documenti", "Segnalazione delle operazioni sospette alla UIF", "Autovalutazione del rischio, funzione antiriciclaggio e formazione", "Limite ai pagamenti in contante di 10.000 euro (AMLR)"],
   policy=["Policy antiriciclaggio", "Manuale di adeguata verifica", "Procedura di segnalazione delle operazioni sospette", "Autovalutazione annuale del rischio di riciclaggio", "Piano di formazione antiriciclaggio"],
   fonti=[F("Regolamento (UE) 2024/1624 (AMLR)", EL("32024R1624")), F("Direttiva (UE) 2024/1640 (AMLD6)", EL("32024L1640")), F("D.Lgs. 21 novembre 2007, n. 231", NT("decreto.legislativo", "2007-11-21", "231"), "Normattiva")]),
 "Sanzioni finanziarie UE": dict(temi=["Misure restrittive e sanzioni internazionali", "Antiriciclaggio e sanzioni finanziarie"], vigila="Comitato di sicurezza finanziaria (MEF), UIF",
   sintesi="Misure restrittive dell'UE (congelamento di fondi, divieti di operazioni, restrizioni settoriali) decise dal Consiglio, in particolare verso la Russia (21 pacchetti al luglio 2026). In Italia l'attuazione è regolata dal D.Lgs. 109/2007.",
   destinatari="Tutte le persone e imprese UE, banche comprese, per qualsiasi operazione con soggetti o settori colpiti.",
   obblighi=["Controllo dei nominativi su liste UE e nazionali (screening) su clienti, controparti e operazioni", "Congelamento dei fondi e comunicazione alla UIF", "Rispetto dei divieti di operazioni con banche e soggetti elencati", "Controlli anti-elusione su operazioni indirette tramite paesi terzi"],
   policy=["Policy sulle sanzioni finanziarie ed embarghi", "Procedura di screening dei nominativi", "Procedura di congelamento e comunicazione alla UIF"],
   fonti=[F("Regolamento (UE) n. 833/2014 (misure restrittive Russia)", EL("32014R0833")), F("D.Lgs. 22 giugno 2007, n. 109", NT("decreto.legislativo", "2007-06-22", "109"), "Normattiva")]),
 "TFR / Travel rule": dict(temi=["Antiriciclaggio e sanzioni finanziarie", "Cripto-attività e finanza digitale"], vigila="Banca d'Italia, UIF",
   sintesi="Regolamento sui dati che devono accompagnare i trasferimenti di fondi e, dal 30 dicembre 2024, anche i trasferimenti di cripto-attività (travel rule).",
   destinatari="Prestatori di servizi di pagamento e prestatori di servizi per le cripto-attività.",
   obblighi=["Trasmettere i dati di ordinante e beneficiario con ogni trasferimento", "Controllare dati mancanti o incompleti e decidere se eseguire, sospendere o respingere", "Conservare i dati"],
   policy=["Procedura sui dati dei trasferimenti di fondi", "Policy antiriciclaggio"],
   fonti=[F("Regolamento (UE) 2023/1113", EL("32023R1113"))]),
 "CRR": dict(temi=["Vigilanza prudenziale e capitale", "Segnalazioni e reporting di vigilanza"], vigila="BCE (banche significative) e Banca d'Italia",
   sintesi="Regolamento europeo sui requisiti prudenziali delle banche (Basilea 3), aggiornato da CRR3 dal 2025 con l'output floor graduale fino al 2030. Fissa il capitale minimo per i rischi, la liquidità, la leva, le grandi esposizioni e l'informativa al pubblico.",
   destinatari="Banche e, in parte, imprese di investimento.",
   obblighi=["Requisiti di fondi propri per rischio di credito, di mercato e operativo", "Indicatori di liquidità (LCR e NSFR)", "Coefficiente di leva minimo del 3%", "Limiti alle grandi esposizioni", "Segnalazioni di vigilanza e informativa di Pillar 3"],
   policy=["Processi ICAAP e ILAAP", "Risk Appetite Framework", "Policy sulle grandi esposizioni", "Policy di informativa al pubblico (Pillar 3)"],
   fonti=[F("Regolamento (UE) n. 575/2013 (CRR)", EL("32013R0575")), F("Regolamento (UE) 2024/1623 (CRR3)", EL("32024R1623"))]),
 "CRD": dict(temi=["Governance, controlli e organizzazione", "Vigilanza prudenziale e capitale"], vigila="BCE e Banca d'Italia",
   sintesi="Direttiva su accesso all'attività bancaria, governo societario, remunerazioni, riserve di capitale e processo di revisione prudenziale (SREP). CRD6 è stata recepita con il D.Lgs. 208/2025, che ha rafforzato le regole su idoneità di esponenti e responsabili delle funzioni chiave.",
   destinatari="Banche e gruppi bancari; dal 2027 anche le succursali di banche di paesi terzi.",
   obblighi=["Assetti di governo societario e sistema dei controlli interni", "Valutazione di idoneità di esponenti e responsabili delle funzioni chiave", "Politiche di remunerazione", "Riserve di capitale e requisiti di Pillar 2 decisi nello SREP", "Gestione dei rischi ESG"],
   policy=["Regolamento degli organi e autovalutazione", "Politica di idoneità degli esponenti", "Politiche di remunerazione e incentivazione", "Regolamento del sistema dei controlli interni"],
   fonti=[F("Direttiva 2013/36/UE (CRD)", EL("32013L0036")), F("Direttiva (UE) 2024/1619 (CRD6)", EL("32024L1619"))]),
 "BRRD / SRMR": dict(temi=["Crisi bancarie, risoluzione e garanzia dei depositi"], vigila="Comitato di risoluzione unico (SRB) e Banca d'Italia come autorità di risoluzione",
   sintesi="Regole su risanamento e risoluzione delle banche in crisi (bail-in, MREL, piani di risanamento). In Italia D.Lgs. 180 e 181 del 2015. La riforma CMDI, pubblicata ad aprile 2026, si applica da maggio 2028.",
   destinatari="Banche e imprese di investimento rilevanti.",
   obblighi=["Piano di risanamento aggiornato", "Requisito minimo di fondi propri e passività ammissibili (MREL)", "Informativa ai clienti sul bail-in", "Collaborazione ai piani di risoluzione"],
   policy=["Piano di risanamento", "Policy sul MREL", "Procedura di informativa ai clienti sul bail-in"],
   fonti=[F("Direttiva 2014/59/UE (BRRD)", EL("32014L0059")), F("Regolamento (UE) n. 806/2014 (SRMR)", EL("32014R0806")), F("D.Lgs. 16 novembre 2015, n. 180", NT("decreto.legislativo", "2015-11-16", "180"), "Normattiva")]),
 "MiFID II / MiFIR": dict(temi=["Servizi di investimento e mercati", "Trasparenza e tutela della clientela"], vigila="Consob e Banca d'Italia (per le rispettive competenze)",
   sintesi="Regole europee sui servizi di investimento e sui mercati, recepite nel TUF. Il D.Lgs. 28/2026 ha adeguato il TUF alla revisione 2024; la Retail Investment Strategy cambierà incentivi e adeguatezza (applicazione attesa verso fine 2028).",
   destinatari="Banche e SIM che prestano servizi di investimento, sedi di negoziazione.",
   obblighi=["Classificazione e profilatura della clientela; valutazione di adeguatezza e appropriatezza", "Product governance (mercato di riferimento)", "Regole sugli incentivi e informativa su costi e oneri", "Best execution e gestione dei conflitti di interesse", "Registrazione delle comunicazioni e segnalazione delle operazioni (MiFIR)"],
   policy=["Policy di product governance", "Policy sui conflitti di interesse", "Strategia di esecuzione e trasmissione degli ordini", "Policy sugli incentivi", "Policy di classificazione e profilatura della clientela"],
   fonti=[F("Direttiva 2014/65/UE (MiFID II)", EL("32014L0065")), F("Regolamento (UE) n. 600/2014 (MiFIR)", EL("32014R0600"))]),
 "MAR": dict(temi=["Servizi di investimento e mercati"], vigila="Consob",
   sintesi="Regolamento europeo sugli abusi di mercato: vieta abuso di informazioni privilegiate e manipolazione del mercato e impone di segnalare le operazioni sospette.",
   destinatari="Chiunque operi su strumenti finanziari quotati; per le banche in particolare chi esegue o riceve ordini.",
   obblighi=["Sistemi per individuare e segnalare a Consob ordini e operazioni sospette (STOR)", "Elenchi delle persone con accesso a informazioni privilegiate", "Regole sui sondaggi di mercato e sulle raccomandazioni di investimento"],
   policy=["Procedura sugli abusi di mercato", "Procedura di segnalazione delle operazioni sospette (STOR)", "Procedura informazioni privilegiate"],
   fonti=[F("Regolamento (UE) n. 596/2014 (MAR)", EL("32014R0596"))]),
 "EMIR": dict(temi=["Servizi di investimento e mercati", "Segnalazioni e reporting di vigilanza"], vigila="Consob, Banca d'Italia, ESMA",
   sintesi="Regolamento sui derivati negoziati fuori borsa: segnalazione dei contratti ai repertori, compensazione obbligatoria per alcune classi e tecniche di mitigazione del rischio. EMIR 3 (Reg. 2024/2987) introduce l'obbligo di conto attivo presso controparti centrali UE.",
   destinatari="Controparti finanziarie e non finanziarie che usano derivati.",
   obblighi=["Segnalazione dei derivati ai repertori di dati", "Compensazione tramite controparte centrale per le classi soggette", "Scambio di garanzie e riconciliazioni per i derivati non compensati"],
   policy=["Procedura di segnalazione EMIR", "Policy sulla gestione delle garanzie"],
   fonti=[F("Regolamento (UE) n. 648/2012 (EMIR)", EL("32012R0648")), F("Regolamento (UE) 2024/2987 (EMIR 3)", EL("32024R2987"))]),
 "CSDR": dict(temi=["Servizi di investimento e mercati"], vigila="Consob e Banca d'Italia",
   sintesi="Regolamento sui depositari centrali e sulla disciplina di regolamento (penali per i mancati regolamenti). Dall'11 ottobre 2027 il regolamento delle operazioni passa a T+1.",
   destinatari="Depositari centrali, partecipanti ai sistemi di regolamento, intermediari.",
   obblighi=["Misure per prevenire i mancati regolamenti", "Gestione delle penali", "Adeguamento dei processi al ciclo T+1"],
   policy=["Procedura di regolamento titoli", "Piano di adeguamento al T+1"],
   fonti=[F("Regolamento (UE) n. 909/2014 (CSDR)", EL("32014R0909")), F("Regolamento (UE) 2025/2075 (T+1)", "https://finreg.aoshearman.com/Regulation-to-shorten-settlement-cycle-to-T1-publ", "A&O Shearman", "Studio legale")]),
 "PRIIPs": dict(temi=["Servizi di investimento e mercati", "Trasparenza e tutela della clientela"], vigila="Consob e IVASS",
   sintesi="Regolamento sul documento contenente le informazioni chiave (KID) per i prodotti d'investimento al dettaglio e assicurativi preassemblati. La Retail Investment Strategy lo renderà più semplice e leggibile dalle macchine.",
   destinatari="Ideatori e distributori di prodotti d'investimento al dettaglio, banche comprese.",
   obblighi=["Consegna del KID prima della sottoscrizione", "Controllo di qualità e aggiornamento dei KID dei prodotti distribuiti"],
   policy=["Procedura di gestione dei KID", "Policy di product governance"],
   fonti=[F("Regolamento (UE) n. 1286/2014 (PRIIPs)", EL("32014R1286"))]),
 "PSD2": dict(temi=["Pagamenti, conti e moneta", "Truffe e frodi ai clienti"], vigila="Banca d'Italia",
   sintesi="Direttiva sui servizi di pagamento (recepita con il D.Lgs. 11/2010 e successive modifiche): autenticazione forte, accesso ai conti da parte di terzi (open banking), responsabilità per le operazioni non autorizzate. Sarà sostituita da PSD3 e dal regolamento PSR (applicazione attesa nel 2028).",
   destinatari="Banche, istituti di pagamento e di moneta elettronica.",
   obblighi=["Autenticazione forte del cliente", "Interfacce di accesso per i prestatori terzi (open banking)", "Rimborso delle operazioni non autorizzate e regole di responsabilità", "Gestione degli incidenti operativi e di sicurezza"],
   policy=["Policy sulla sicurezza dei pagamenti", "Procedura per i disconoscimenti e i rimborsi", "Procedura di monitoraggio delle frodi"],
   fonti=[F("Direttiva (UE) 2015/2366 (PSD2)", EL("32015L2366"))]),
 "Instant Payments / SEPA": dict(temi=["Pagamenti, conti e moneta", "Truffe e frodi ai clienti"], vigila="Banca d'Italia",
   sintesi="Regole SEPA sui bonifici e addebiti in euro, aggiornate dal regolamento sui bonifici istantanei: ricezione dal 9 gennaio 2025 e invio con verifica del beneficiario dal 9 ottobre 2025 nell'area euro.",
   destinatari="Prestatori di servizi di pagamento che offrono bonifici in euro.",
   obblighi=["Offrire bonifici istantanei allo stesso prezzo dei bonifici ordinari", "Verifica della corrispondenza nome-IBAN prima del bonifico", "Controllo giornaliero dei clienti rispetto alle liste di sanzioni"],
   policy=["Procedura sui bonifici istantanei", "Procedura di verifica del beneficiario"],
   fonti=[F("Regolamento (UE) 2024/886 (Instant Payments)", EL("32024R0886")), F("Regolamento (UE) n. 260/2012 (SEPA)", EL("32012R0260"))]),
 "MiCAR": dict(temi=["Cripto-attività e finanza digitale"], vigila="Consob e Banca d'Italia; ESMA ed EBA per i soggetti significativi",
   sintesi="Regolamento europeo sulle cripto-attività: autorizzazione e regole per chi emette token e per chi presta servizi (CASP). Pienamente applicato dal 30 dicembre 2024; in Italia il regime transitorio è finito il 30 dicembre 2025. La revisione («MiCA 2») è in preparazione.",
   destinatari="Emittenti di token e prestatori di servizi per le cripto-attività; le banche possono prestare servizi con una notifica.",
   obblighi=["Autorizzazione o notifica per prestare servizi su cripto-attività", "Regole di condotta, custodia e separazione dei beni dei clienti", "Informativa (white paper) e regole sulle stablecoin", "Prevenzione degli abusi di mercato sulle cripto"],
   policy=["Policy sui servizi in cripto-attività", "Procedura di custodia", "Policy antiriciclaggio (travel rule)"],
   fonti=[F("Regolamento (UE) 2023/1114 (MiCAR)", EL("32023R1114"))]),
 "Credito ai consumatori": dict(temi=["Credito e finanziamenti", "Trasparenza e tutela della clientela"], vigila="Banca d'Italia",
   sintesi="Regole sul credito ai consumatori nel TUB. La nuova direttiva (CCD2) è recepita con il D.Lgs. 212/2025 e attuata dal decreto CICR del 9 luglio 2026; si applica dal 20 novembre 2026 ed estende le tutele a prestiti piccoli e al «compra ora, paga dopo».",
   destinatari="Banche e intermediari che concedono credito ai consumatori, intermediari del credito.",
   obblighi=["Pubblicità con avviso obbligatorio e informazioni di base", "Informativa precontrattuale (SECCI) e contenuto del contratto", "Valutazione approfondita del merito creditizio", "Diritto di recesso e rimborso anticipato", "Tolleranza verso i clienti in difficoltà prima di agire per il recupero"],
   policy=["Policy di valutazione del merito creditizio", "Procedura di pubblicità e informativa", "Policy di gestione dei clienti in difficoltà"],
   fonti=[F("Direttiva (UE) 2023/2225 (CCD2)", EL("32023L2225")), F("D.Lgs. 31 dicembre 2025, n. 212", "https://www.normattiva.it/eli/id/2026/01/09/26G00009/ORIGINAL", "Normattiva")]),
 "Credito immobiliare (MCD)": dict(temi=["Credito e finanziamenti", "Trasparenza e tutela della clientela"], vigila="Banca d'Italia",
   sintesi="Direttiva sul credito immobiliare ai consumatori, recepita nel TUB (articoli 120-quinquies e seguenti): regole su informativa, merito creditizio e condotta nei mutui per la casa.",
   destinatari="Banche e intermediari che concedono mutui ai consumatori.",
   obblighi=["Prospetto informativo europeo standardizzato (PIES)", "Valutazione del merito creditizio e della garanzia", "Periodo di riflessione e informazione sul rischio di cambio", "Competenze del personale"],
   policy=["Policy del credito immobiliare", "Procedura di valutazione degli immobili", "Piano di formazione del personale"],
   fonti=[F("Direttiva 2014/17/UE (MCD)", EL("32014L0017"))]),
 "IDD": dict(temi=["Assicurazioni e bancassicurazione"], vigila="IVASS (e Consob per alcuni prodotti)",
   sintesi="Direttiva sulla distribuzione assicurativa, recepita nel Codice delle assicurazioni private e nei regolamenti IVASS: regole di condotta per chi vende polizze, banche comprese. La Retail Investment Strategy la modifica per i prodotti di investimento assicurativi.",
   destinatari="Imprese di assicurazione e intermediari, comprese le banche che collocano polizze.",
   obblighi=["Valutazione delle richieste ed esigenze del cliente", "Adeguatezza e appropriatezza per i prodotti di investimento assicurativi", "Governo e controllo del prodotto", "Conflitti di interesse e incentivi", "Formazione e aggiornamento del personale"],
   policy=["Policy di distribuzione assicurativa", "Policy sui conflitti di interesse", "Piano di formazione IVASS"],
   fonti=[F("Direttiva (UE) 2016/97 (IDD)", EL("32016L0097")), F("D.Lgs. 7 settembre 2005, n. 209 (Codice delle assicurazioni)", NT("decreto.legislativo", "2005-09-07", "209"), "Normattiva")]),
 "Finanza sostenibile (SFDR/Tassonomia/CSRD)": dict(temi=["Finanza sostenibile ed ESG"], vigila="Consob, Banca d'Italia, BCE (rischi climatici)",
   sintesi="Insieme di regole sulla finanza sostenibile: informativa sui prodotti (SFDR, in revisione con la SFDR 2.0), classificazione delle attività sostenibili (Tassonomia), rendicontazione di sostenibilità delle imprese (CSRD, ridimensionata dall'Omnibus I del 2026). Le banche devono anche gestire i rischi climatici e ambientali.",
   destinatari="Banche, gestori, assicurazioni; per la CSRD le imprese con più di 1.000 dipendenti e 450 milioni di fatturato.",
   obblighi=["Informativa di sostenibilità su prodotti e servizi di investimento", "Rendicontazione di sostenibilità (se nel perimetro CSRD)", "Integrazione dei rischi ESG nella gestione dei rischi", "Raccolta delle preferenze di sostenibilità nella consulenza"],
   policy=["Policy di sostenibilità", "Policy di gestione dei rischi climatici e ambientali", "Procedura di informativa SFDR"],
   fonti=[F("Regolamento (UE) 2019/2088 (SFDR)", EL("32019R2088")), F("Regolamento (UE) 2020/852 (Tassonomia)", EL("32020R0852")), F("Direttiva (UE) 2022/2464 (CSRD)", EL("32022L2464"))]),
 "Accessibilità (EAA)": dict(temi=["Trasparenza e tutela della clientela"], vigila="AgID e autorità di vigilanza del mercato",
   sintesi="Atto europeo sull'accessibilità, recepito con il D.Lgs. 82/2022: dal 28 giugno 2025 i servizi bancari ai consumatori (siti, app, sportelli automatici, contratti) devono essere accessibili alle persone con disabilità.",
   destinatari="Banche che offrono servizi ai consumatori.",
   obblighi=["Siti e app conformi ai requisiti di accessibilità", "Sportelli e terminali accessibili", "Informazioni e documenti contrattuali comprensibili", "Dichiarazione di accessibilità"],
   policy=["Policy di accessibilità digitale", "Procedura di verifica dei canali digitali"],
   fonti=[F("Direttiva (UE) 2019/882 (EAA)", EL("32019L0882")), F("D.Lgs. 27 maggio 2022, n. 82", NT("decreto.legislativo", "2022-05-27", "82"), "Normattiva")]),
 "Whistleblowing": dict(temi=["Governance, controlli e organizzazione"], vigila="ANAC (canale esterno); per le banche anche Banca d'Italia",
   sintesi="Regole sulla protezione di chi segnala violazioni, recepite con il D.Lgs. 24/2023: canali interni riservati, divieto di ritorsioni, canale esterno presso l'ANAC. Per le banche si aggiunge l'articolo 52-bis del TUB.",
   destinatari="Imprese pubbliche e private con almeno 50 dipendenti o nei settori regolati, banche comprese.",
   obblighi=["Canale interno di segnalazione con riservatezza", "Riscontro al segnalante entro i termini", "Divieto di ritorsioni e tutela del segnalante", "Informazione chiara sui canali"],
   policy=["Policy di whistleblowing", "Procedura di gestione delle segnalazioni"],
   fonti=[F("Direttiva (UE) 2019/1937", EL("32019L1937")), F("D.Lgs. 10 marzo 2023, n. 24", NT("decreto.legislativo", "2023-03-10", "24"), "Normattiva")]),
 "IVA / CESOP": dict(temi=["Fisco per banca e clienti"], vigila="Agenzia delle Entrate",
   sintesi="Dal 1° gennaio 2024 i prestatori di servizi di pagamento devono comunicare all'Agenzia delle Entrate i dati sui pagamenti transfrontalieri (sistema europeo CESOP), per contrastare le frodi IVA nel commercio elettronico.",
   destinatari="Banche e prestatori di servizi di pagamento.",
   obblighi=["Registrazione dei pagamenti transfrontalieri", "Comunicazione trimestrale quando un beneficiario supera 25 pagamenti nel trimestre", "Conservazione dei dati"],
   policy=["Procedura di segnalazione CESOP"],
   fonti=[F("Direttiva (UE) 2020/284", EL("32020L0284"))]),
 "TUB": dict(temi=["Sistema bancario e vigilanza", "Trasparenza e tutela della clientela"], vigila="Banca d'Italia",
   sintesi="Testo unico bancario (D.Lgs. 385/1993): la legge base del sistema bancario italiano, su autorizzazione, vigilanza, trasparenza, credito ai consumatori, crisi e sanzioni. Viene modificato ogni volta che si recepisce una direttiva (da ultimo CRD6 e CCD2).",
   destinatari="Banche, intermediari finanziari, istituti di pagamento e di moneta elettronica.",
   obblighi=["Rispetto delle disposizioni di vigilanza della Banca d'Italia", "Trasparenza delle condizioni e correttezza verso la clientela (titolo VI)", "Requisiti degli esponenti e degli azionisti", "Regime sanzionatorio amministrativo"],
   policy=["Regolamento generale e organigramma", "Policy di trasparenza", "Policy di idoneità degli esponenti"],
   fonti=[F("D.Lgs. 1 settembre 1993, n. 385 (TUB)", NT("decreto.legislativo", "1993-09-01", "385"), "Normattiva")]),
 "TUF": dict(temi=["Servizi di investimento e mercati"], vigila="Consob e Banca d'Italia",
   sintesi="Testo unico della finanza (D.Lgs. 58/1998): regole su servizi di investimento, gestione collettiva, mercati ed emittenti, con i regolamenti Consob attuativi. Adeguato alla revisione MiFID/MiFIR con il D.Lgs. 28/2026.",
   destinatari="Banche e SIM che prestano servizi di investimento, SGR, emittenti quotati.",
   obblighi=["Regole di condotta nei servizi di investimento", "Requisiti organizzativi e controlli", "Obblighi verso il mercato e gli emittenti"],
   policy=["Policy sui servizi di investimento", "Regolamento Intermediari: procedure attuative"],
   fonti=[F("D.Lgs. 24 febbraio 1998, n. 58 (TUF)", NT("decreto.legislativo", "1998-02-24", "58"), "Normattiva")]),
 "D.Lgs. 231/2001": dict(temi=["Governance, controlli e organizzazione"], vigila="Autorità giudiziaria",
   sintesi="Responsabilità amministrativa degli enti per i reati commessi nel loro interesse da amministratori e dipendenti. Il modello di organizzazione, gestione e controllo e l'Organismo di vigilanza permettono di escludere o ridurre la responsabilità; l'elenco dei reati presupposto si allarga spesso.",
   destinatari="Società ed enti, banche comprese.",
   obblighi=["Modello di organizzazione, gestione e controllo aggiornato ai nuovi reati", "Organismo di vigilanza con poteri autonomi", "Codice etico e sistema disciplinare", "Formazione e flussi informativi verso l'Organismo"],
   policy=["Modello 231", "Codice etico", "Regolamento dell'Organismo di vigilanza"],
   fonti=[F("D.Lgs. 8 giugno 2001, n. 231", NT("decreto.legislativo", "2001-06-08", "231"), "Normattiva")]),
 "Codice del consumo": dict(temi=["Trasparenza e tutela della clientela"], vigila="AGCM; per le banche anche Banca d'Italia",
   sintesi="Codice del consumo (D.Lgs. 206/2005): pratiche commerciali scorrette, clausole vessatorie, contratti a distanza dei servizi finanziari. La direttiva (UE) 2023/2673 sui servizi finanziari a distanza ha aggiornato le regole, con applicazione dal 19 giugno 2026.",
   destinatari="Imprese che vendono a consumatori, banche comprese.",
   obblighi=["Evitare pratiche commerciali ingannevoli o aggressive", "Clausole contrattuali chiare e non vessatorie", "Informativa e diritto di recesso nei contratti a distanza"],
   policy=["Policy di marketing e comunicazione commerciale", "Procedura di revisione dei contratti"],
   fonti=[F("D.Lgs. 6 settembre 2005, n. 206", NT("decreto.legislativo", "2005-09-06", "206"), "Normattiva"), F("Direttiva (UE) 2023/2673", EL("32023L2673"))]),
 "Usura": dict(temi=["Credito e finanziamenti", "Trasparenza e tutela della clientela"], vigila="Banca d'Italia (rilevazione) e MEF (decreti trimestrali)",
   sintesi="Legge 108/1996 contro l'usura: ogni trimestre il MEF pubblica i tassi effettivi globali medi per categoria di operazione; i tassi applicati non possono superare la soglia derivata da quei valori.",
   destinatari="Banche e intermediari che concedono credito.",
   obblighi=["Controllo trimestrale dei tassi applicati rispetto alle soglie", "Segnalazione dei tassi alla Banca d'Italia", "Pubblicazione delle soglie in filiale e sul sito"],
   policy=["Procedura di controllo dei tassi soglia"],
   fonti=[F("Legge 7 marzo 1996, n. 108", NT("legge", "1996-03-07", "108"), "Normattiva")]),
 "Trasparenza bancaria": dict(temi=["Trasparenza e tutela della clientela"], vigila="Banca d'Italia",
   sintesi="Disposizioni della Banca d'Italia sulla trasparenza delle operazioni e dei servizi bancari e sulla correttezza delle relazioni con la clientela (provvedimento del 29 luglio 2009 e aggiornamenti). Saranno aggiornate per il nuovo credito ai consumatori.",
   destinatari="Banche e intermediari nei rapporti con la clientela.",
   obblighi=["Fogli informativi, documento di sintesi e comunicazioni periodiche", "Procedure di governo dei prodotti per la clientela al dettaglio", "Gestione dei reclami e adesione all'Arbitro Bancario Finanziario", "Controlli sulla correttezza degli oneri applicati"],
   policy=["Policy di trasparenza", "Procedura di gestione dei reclami", "Policy di governo dei prodotti bancari"],
   fonti=[F("Disposizioni di trasparenza delle operazioni e dei servizi bancari", "https://www.bancaditalia.it/compiti/vigilanza/normativa/archivio-norme/disposizioni/", "Banca d'Italia")]),
 "Circolare 285": dict(temi=["Governance, controlli e organizzazione", "Vigilanza prudenziale e capitale"], vigila="Banca d'Italia",
   sintesi="Disposizioni di vigilanza per le banche: attua CRR e CRD in Italia e regola governo societario, sistema dei controlli interni, esternalizzazione, continuità operativa, remunerazioni e rischi. Viene aggiornata più volte l'anno.",
   destinatari="Banche e gruppi bancari.",
   obblighi=["Funzioni di controllo (compliance, risk management, internal audit) indipendenti", "Regole su esternalizzazione e sistemi informativi", "Politiche di remunerazione", "Governo dei rischi e processo ICAAP/ILAAP"],
   policy=["Regolamento del sistema dei controlli interni", "Policy di esternalizzazione", "Politiche di remunerazione", "Regolamento delle funzioni di controllo"],
   fonti=[F("Circolare n. 285/2013 - Disposizioni di vigilanza per le banche", BDI_CIRC, "Banca d'Italia")]),
 "Circolare 288": dict(temi=["Governance, controlli e organizzazione", "Credito e finanziamenti"], vigila="Banca d'Italia",
   sintesi="Disposizioni di vigilanza per gli intermediari finanziari iscritti all'albo dell'articolo 106 TUB (finanziarie, società di leasing e factoring, servicer).",
   destinatari="Intermediari finanziari ex art. 106 TUB, anche del gruppo bancario.",
   obblighi=["Requisiti patrimoniali e organizzativi", "Sistema dei controlli interni", "Regole per i servicer nelle cartolarizzazioni"],
   policy=["Regolamento dei controlli interni dell'intermediario"],
   fonti=[F("Circolare n. 288/2015 - Disposizioni di vigilanza per gli intermediari finanziari", BDI_CIRC, "Banca d'Italia")]),
 "Segnalazioni di vigilanza (Circ. 272/286)": dict(temi=["Segnalazioni e reporting di vigilanza"], vigila="Banca d'Italia, BCE",
   sintesi="Istruzioni della Banca d'Italia per le segnalazioni statistiche e prudenziali (matrice dei conti, segnalazioni armonizzate COREP e FINREP). Nel 2026 l'EBA ha avviato la più ampia semplificazione degli ultimi anni.",
   destinatari="Banche e gruppi bancari.",
   obblighi=["Invio periodico delle segnalazioni statistiche e prudenziali", "Qualità dei dati e controlli", "Rettifiche tempestive"],
   policy=["Policy di data governance delle segnalazioni", "Procedura di produzione e controllo delle segnalazioni"],
   fonti=[F("Circolari n. 272/2008, 286/2013 e 154/1991", BDI_CIRC, "Banca d'Italia")]),
}

# aree (livello 1)
AREE = [
 {"area": "Banca", "nome": "Banca: capitale, controlli, crisi", "desc": "Regole prudenziali, governance, segnalazioni, antiriciclaggio e crisi bancarie."},
 {"area": "Mercati e investimenti", "nome": "Mercati e investimenti", "desc": "Servizi di investimento, mercati, cripto-attività, finanza sostenibile."},
 {"area": "Clientela e consumatori", "nome": "Clientela e consumatori", "desc": "Tutela del cliente, frodi, educazione finanziaria."},
 {"area": "Tecnologia e dati", "nome": "Tecnologia e dati", "desc": "Cybersicurezza, DORA, intelligenza artificiale, privacy."},
 {"area": "Assicurazioni", "nome": "Assicurazioni e previdenza", "desc": "Bancassicurazione e previdenza complementare."},
 {"area": "Fisco", "nome": "Fisco", "desc": "Fiscalità di banca e clienti."},
 {"area": "Lavoratori", "nome": "Lavoro e personale", "desc": "Rapporto di lavoro, welfare, sicurezza, formazione."},
 {"area": "Economia e contesto", "nome": "Economia e contesto", "desc": "Tassi, politica monetaria, quadro economico."},
]

conf = json.loads(Path("/home/claude/vp-alert-feed/temi_indicatori.json").read_text(encoding="utf-8"))
TEMI = [{"tema": t["tema"], "area": t["area"], "it": t.get("it", []), "en": t.get("en", []), "sigle": t.get("sigle", []),
         "contesto": t.get("contesto") is not None} for t in conf["temi"]]
TEMI.insert(1, {"tema": "Misure restrittive e sanzioni internazionali", "area": "Banca", "it": ["misure restrittive", "congelamento dei fondi", "sanzioni internazionali", "embargo", "pacchetto di sanzioni"],
                "en": ["restrictive measures", "asset freeze", "sanctions package"], "sigle": ["PESC"], "contesto": False})
nomi_temi = {t["tema"] for t in TEMI}
for k, v in FW.items():
    for t in v["temi"]:
        assert t in nomi_temi, (k, t)

fw_raw = json.loads(Path("/mnt/user-data/uploads/VP Alert/_automazione/lavoro/sito/framework.json").read_text(encoding="utf-8"))["righe"]
sigle = {r["sigla"] for r in fw_raw}
assert sigle == set(FW), (sigle ^ set(FW))

# tassonomia VP (livello «tematica»)
tax = json.loads(Path("/mnt/user-data/uploads/VP Alert/_automazione/lavoro/sito/tassonomia_vp.json").read_text(encoding="utf-8"))
tax = [list(x) for x in tax if x[0]]

# mappa Tematica VP -> tema del sito (stessa di costruisci_statistiche)
src = Path(QUI / "prev" / "costruisci_statistiche.py").read_text(encoding="utf-8")
i0 = src.index("TEMATICA = {"); i1 = src.index("}", i0)
TEMATICA = eval(src[i0 + len("TEMATICA = "):i1 + 1])

# indice storico per la ricerca: alert manuali 2026 (settimane 2-43)
man = json.loads(Path("/mnt/user-data/uploads/VP Alert/_automazione/lavoro/manuali/manuali_2_43.json").read_text(encoding="utf-8"))
key = {tuple(x): i for i, x in enumerate(tax)}
righe = []
for x in man:
    t = (str(x.get("Tematica", "")).strip(), str(x.get("Ambito", "")).strip(), str(x.get("Argomento", "")).strip())
    if not t[0]:
        continue
    k = key.get(t)
    if k is None:
        tax.append(list(t)); k = key[t] = len(tax) - 1
    desc = re.sub(r"\s+", " ", str(x.get("Descrizione", "")))[:160]
    righe.append([str(x.get("Riferimento normativo", ""))[:120], desc, str(x.get("Ente", ""))[:40], str(x.get("Data", ""))[:10], k])
quadro = {"aggiornato": "2026-11-03", "aree": AREE, "temi": TEMI, "framework": FW, "tassonomia": tax, "tematica_tema": TEMATICA,
          "legenda_affidabilita": {"Atto ufficiale": "Testo della norma o dell'autorità (EUR-Lex, Normattiva, Banca d'Italia, BCE, Consob…)",
                                   "Studio legale": "Analisi di grandi studi legali internazionali", "Stampa specializzata": "Riviste giuridiche e finanziarie specializzate",
                                   "Stampa": "Quotidiani e agenzie autorevoli"}}
(QUI / "quadro.json").write_text(json.dumps(quadro, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

P = 4
passo = -(-len(righe) // P)
for n, part in ((i + 1, righe[i * passo:(i + 1) * passo]) for i in range(P)):
    (QUI / f"indice_{n}.json").write_text(json.dumps({"aggiornato": "2026-11-03", "nota": "Alert manuali 2026 (settimane 2-43): riferimento, descrizione breve, ente, data, indice in quadro.tassonomia", "righe": part}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
for f in ["quadro.json"] + [f"indice_{i}.json" for i in range(1, P + 1)]:
    print(f, (QUI / f).stat().st_size)
print("righe indice", len(righe), "tassonomia", len(tax))
