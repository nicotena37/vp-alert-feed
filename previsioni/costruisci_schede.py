"""Schede tema e previsioni dettagliate (testo con citazioni [n] alle fonti della scheda). Uscita: schede.json"""
import json
from pathlib import Path

EL = lambda c: f"https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:{c}"


def F(titolo, editore, data, url, tipo="Ufficiale"):
    return {"titolo": titolo, "editore": editore, "data": data, "url": url, "tipo": tipo}


def P(titolo, direzione, cosa, quando, data, prob, perche, fonti, dati=(), funzioni=()):
    return {"titolo": titolo, "direzione": direzione, "cosa": cosa, "quando": quando, "data": data, "probabilita": prob,
            "perche": perche, "fonti": list(fonti), "dati": [{"etichetta": d[0], "valore": d[1], "fonte": d[2]} for d in dati],
            "funzioni": list(funzioni)}


S = []

# ---------------------------------------------------------------- 1 Vigilanza prudenziale
fv = [F("Communication on the competitiveness of the EU banking sector, COM(2026) 615", "Commissione europea", "2026-07-17",
        "https://finance.ec.europa.eu/document/download/ffc0d009-f49c-4b79-b100-93a2cd7a27eb_en?filename=260717-banking-sector-competitiveness-communication_en.pdf"),
      F("European Commission Outlines Banking Reform Agenda", "Sullivan & Cromwell", "2026-08-26", "https://www.sullcrom.com/insights/memo/2026/August/EU-Banking-Competitiveness-Cross-Border-MA", "Studio legale"),
      F("Governing Council proposes simplification of EU banking rules", "BCE", "2025-12-11", "https://www.ecb.europa.eu/press/pr/date/2025/html/ecb.pr251211~aa5c9271b8.en.html"),
      F("Commission adopts delegated regulation amending market risk requirements", "Regulation Tomorrow (Eversheds Sutherland)", "2026-06", "https://www.regulationtomorrow.com/2026/06/commission-adopts-delegated-regulation-amending-market-risk-requirements/", "Studio legale"),
      F("European Parliament and Council reach agreement on securitisation framework review", "Regulation Tomorrow (Eversheds Sutherland)", "2026-10", "https://www.regulationtomorrow.com/2026/10/european-parliament-and-council-reach-agreement-on-securitisation-framework-review/", "Studio legale"),
      F("Commission welcomes political agreement on the review of the Securitisation Framework", "Commissione europea", "2026-10-22", "https://finance.ec.europa.eu/news/commission-welcomes-political-agreement-reached-review-securitisation-framework-2026-10-22_en"),
      F("Resilience, integration and competitiveness: building the future of European banking", "BCE (discorso)", "2026-10-02", "https://www.ecb.europa.eu/press/key/date/2026/html/ecb.sp261002_1~419efe18e0.en.html"),
      F("Regolamento (UE) 2024/1623 (CRR3)", "EUR-Lex", "2024-06-19", EL("32024R1623")),
      F("In GU il recepimento della CRD VI e l'adeguamento al CRR III (D.Lgs. 208/2025)", "DirittoBancario", "2026-01-09", "https://www.dirittobancario.it/art/in-gu-il-decreto-di-recepimento-della-crd-vi-e-di-adeguamento-al-crr-iii/", "Stampa specializzata")]
S.append({"tema": "Vigilanza prudenziale e capitale", "iter": ["CRR3 / CRD6"],
 "visione": "Le regole di capitale delle banche europee sono quelle di Basilea 3 nella versione finale (CRR3/CRD6), applicate dal 2025 con l'output floor che sale gradualmente fino al 2030 [8]. Dopo anni di irrigidimento, il 2026 segna un'inversione di rotta: Commissione e BCE hanno messo nero su bianco un programma di semplificazione che tocca riserve di capitale, leva finanziaria, MREL e segnalazioni [1][3].",
 "contesto": "La spinta viene dal tema della competitività: le banche UE finanziano meno l'economia rispetto ai concorrenti e i costi di conformità sono alti. La Comunicazione della Commissione del 17 luglio 2026 parla di regole più proporzionate e di un mercato bancario più integrato [1][2]; la BCE, a dicembre 2025, ha proposto di accorpare le riserve di capitale e di semplificare la leva [3]. In Italia CRD6 è stata recepita con il D.Lgs. 208/2025 [9].",
 "evoluzione": "CRR3 si applica dal 1° gennaio 2025 [8]; la parte sul rischio di mercato (FRTB) è stata rinviata e poi accompagnata da misure temporanee per tre anni dal 2027 [4]. A ottobre 2026 è arrivato l'accordo politico sulla riforma della cartolarizzazione, con requisiti di capitale più bassi per le operazioni meno rischiose [5][6].",
 "attuale": "Oggi le regole in vigore non cambiano: fino a nuove leggi restano requisiti, riserve e limiti attuali [2]. Ma il calendario è chiaro: la Commissione presenterà le proposte legislative entro la fine del primo trimestre 2027 [2]. Nel frattempo la BCE insiste su integrazione e semplificazione della vigilanza [7].",
 "possibili": "Le misure più probabili sono: meno riserve di capitale (da sei a due blocchi), eliminazione del Pillar 2 sulla leva, ricalibrazione dell'output floor per mutui e imprese senza rating, regole più leggere per le banche piccole [2][3]. Restano incerti tempi e portata, che dipenderanno dal negoziato con Parlamento e Consiglio [2].",
 "previsioni": [
  P("Riserve di capitale accorpate in due blocchi", "Allentamento",
    "Le attuali riserve (conservazione, anticiclica, rischio sistemico, G-SII/O-SII) verrebbero fuse in una riserva «non rilasciabile» e una «rilasciabile» che le autorità possono abbassare nelle fasi di crisi. Effetto atteso: struttura più semplice e capitale più utilizzabile, senza riduzione formale del livello complessivo.",
    "Proposta attesa entro marzo 2027", "2027-03-31", "Media",
    "Lo chiede la BCE e la Commissione parla di «meno riserve»: due fonti istituzionali allineate, ma serve ancora il testo legislativo.", [3, 1, 2],
    [("Riserve oggi / proposte", "6 elementi → 2 blocchi", 3)], ["Risk management", "Vigilanza e segnalazioni"]),
  P("Leva finanziaria: niente più requisito di Pillar 2", "Allentamento",
    "Il quadro della leva passerebbe da quattro elementi a due: minimo del 3% più una sola riserva, che per le banche piccole potrebbe essere pari a zero; sparirebbe il requisito di Pillar 2 sulla leva.",
    "Proposta attesa entro marzo 2027", "2027-03-31", "Media",
    "Misura indicata sia dalla BCE (dicembre 2025) sia dalla Commissione (luglio 2026).", [3, 2],
    [("Minimo di leva", "3% (invariato)", 3)], ["Risk management"]),
  P("Output floor ricalibrato per mutui e imprese senza rating", "Allentamento",
    "Il limite minimo ai risultati dei modelli interni (oggi in salita fino al 72,5% nel 2030) verrebbe ricalibrato, con regimi transitori per esposizioni verso imprese senza rating e mutui; possibile revisione anche delle deduzioni per il software.",
    "Proposta attesa entro marzo 2027", "2027-03-31", "Media",
    "Annunciato nella Comunicazione sulla competitività; impatto maggiore per le banche con modelli interni.", [2, 1, 8],
    [("Output floor a regime", "72,5% nel 2030", 8)], ["Risk management"]),
  P("Requisiti più bassi sulle cartolarizzazioni meno rischiose", "Allentamento",
    "Ricalibrazione dei requisiti di capitale in base al rischio, con un floor di ponderazione del 5% per le classi più sicure e una nuova categoria di cartolarizzazioni «resilienti».",
    "Dopo l'adozione formale (2027)", "2027-06-30", "Alta",
    "C'è già l'accordo politico del 21 ottobre 2026: resta solo l'adozione formale.", [5, 6],
    [("Floor di ponderazione per le classi più sicure", "5%", 5)], ["Risk management", "Commerciale e prodotti"]),
  P("Correttivi temporanei FRTB dal 2027", "Allentamento",
    "Dal 1° gennaio 2027, per tre anni, applicazione attenuata del nuovo rischio di mercato: test dei modelli interni meno severi e un moltiplicatore che riporta i requisiti FRTB a livelli pre-FRTB.",
    "1 gennaio 2027", "2027-01-01", "Alta",
    "Regolamento delegato adottato il 4 giugno 2026; manca solo la fine dello scrutinio di Parlamento e Consiglio.", [4], [], ["Risk management"]),
 ],
 "fonti": fv, "letture": [2, 3, 5, 7]})

# ---------------------------------------------------------------- 2 Segnalazioni
fs = [F("EBA consults on simplifying supervisory reporting under CRR", "Regulation Tomorrow (Eversheds Sutherland)", "2026-04", "https://www.regulationtomorrow.com/2026/04/eba-consults-on-simplifying-supervisory-reporting-under-crr/", "Studio legale"),
      F("Consultation paper on revised ITS on supervisory reporting (EBA/CP/2026/07)", "EBA", "2026-04", "https://www.eba.europa.eu/sites/default/files/2026-04/ec63db1e-39b5-4c78-9e20-71bdfb0eed85/EBA%20CP%202026%2007%20(Consultation%20paper%20on%20revised%20ITS%20on%20supervisory%20reporting).pdf"),
      F("European Commission Outlines Banking Reform Agenda", "Sullivan & Cromwell", "2026-08-26", "https://www.sullcrom.com/insights/memo/2026/August/EU-Banking-Competitiveness-Cross-Border-MA", "Studio legale"),
      F("Governing Council proposes simplification of EU banking rules", "BCE", "2025-12-11", "https://www.ecb.europa.eu/press/pr/date/2025/html/ecb.pr251211~aa5c9271b8.en.html"),
      F("Efficient reporting: simpler, smarter, proportionate", "EBA", "2026", "https://www.eba.europa.eu/publications-and-media/publications/efficient-reporting-simpler-smarter-proportionate")]
S.append({"tema": "Segnalazioni e reporting di vigilanza", "iter": ["CRR3 / CRD6"],
 "visione": "Le segnalazioni di vigilanza sono il punto in cui la semplificazione europea è più concreta: l'EBA ha messo in consultazione la revisione degli standard di reporting con meno dati e meno prospetti [1][2], e la Commissione punta a dimezzare i punti dati [3].",
 "contesto": "Secondo l'EBA il reporting costa al settore circa 11,2 miliardi di euro l'anno [3]. La BCE propone di segnalare una volta sola per fini statistici, prudenziali e di risoluzione, di rivedere tutti gli obblighi ogni 3-5 anni e di ricavare l'informativa di Pillar 3 dalle segnalazioni [4].",
 "evoluzione": "Dopo anni di aggiunte (CRR2, CRR3, ESG, IFRS 9) il 2026 è il primo anno di vera riduzione: due consultazioni EBA chiuse il 10 luglio 2026, con una parte FINREP legata all'IFRS 18 [1].",
 "attuale": "In attesa della versione finale degli standard, gli obblighi attuali restano tutti in vigore; le banche devono comunque prepararsi ai cambi di tassonomia legati all'IFRS 18 [1][5].",
 "possibili": "Riduzione dei punti dati e dei prospetti, soglie di materialità per le richieste di nuovo invio, segnalazione integrata BCE-EBA [3][4]. I tempi esatti di applicazione non sono ancora noti [1].",
 "previsioni": [
  P("Dimezzamento dei punti dati segnalati", "Semplificazione",
    "Obiettivo indicato dalla Commissione: circa metà dei punti dati in meno nelle segnalazioni di vigilanza; l'EBA ha già proposto di togliere prospetti e portafogli di benchmarking.",
    "Standard finali attesi nel 2027", "2027-06-30", "Media",
    "Obiettivo politico dichiarato e consultazioni EBA già concluse; la percentuale finale dipende dagli standard definitivi.", [3, 1, 2],
    [("Costo annuo del reporting (stima EBA)", "11,2 mld €", 3), ("Riduzione obiettivo dei punti dati", "circa 50%", 3)], ["Vigilanza e segnalazioni"]),
  P("Soglia di materialità per le richieste di nuovo invio", "Allentamento",
    "Le correzioni di dati poco rilevanti non dovrebbero più richiedere un nuovo invio completo delle segnalazioni.",
    "2027-2028", "2027-12-31", "Media", "Proposta della BCE, coerente con la linea della Commissione.", [4], [], ["Vigilanza e segnalazioni"]),
  P("Segnalazione unica per statistica, vigilanza e risoluzione", "Semplificazione",
    "Un sistema integrato in cui i dati si inviano una volta e vengono condivisi tra autorità europee, tramite il comitato congiunto sul reporting bancario.",
    "Oltre il 2028", "2029-06-30", "Bassa", "Progetto di lungo periodo: richiede accordo tra più autorità e cambi normativi.", [4], [], ["Vigilanza e segnalazioni"]),
 ],
 "fonti": fs, "letture": [1, 2, 5]})

# ---------------------------------------------------------------- 3 Crisi bancarie
fc = [F("EU reforms to the CMDI framework published in OJ", "A&O Shearman", "2026-04", "https://finreg.aoshearman.com/eu-reforms-to-the-cmdi-framework-published-in-oj", "Studio legale"),
      F("EU resolution framework reform: key changes for banks under the CMDI package", "Ashurst", "2026", "https://www.ashurst.com/en/insights/eu-resolution-framework-reform-key-changes-for-banks-under-the-cmdi-package/", "Studio legale"),
      F("European Commission Outlines Banking Reform Agenda", "Sullivan & Cromwell", "2026-08-26", "https://www.sullcrom.com/insights/memo/2026/August/EU-Banking-Competitiveness-Cross-Border-MA", "Studio legale"),
      F("Memoria della Banca d'Italia del 29 ottobre 2026", "Banca d'Italia", "2026-10-29", "https://www.bancaditalia.it/pubblicazioni/memorie/memorie-2026/Memoria-29.10.2026.pdf?language_id=1")]
S.append({"tema": "Crisi bancarie, risoluzione e garanzia dei depositi", "iter": [],
 "visione": "La riforma CMDI (gestione delle crisi e garanzia dei depositi) è stata pubblicata in Gazzetta UE il 20 aprile 2026: estende gli strumenti di risoluzione anche alle banche piccole e medie e permette di usare i fondi del settore per «colmare il divario» [1].",
 "contesto": "L'obiettivo è ridurre il ricorso a denaro pubblico quando una banca fallisce, usando prima le risorse della banca e poi le reti di sicurezza finanziate dal settore (fondi di risoluzione e fondo unico) [1][2].",
 "evoluzione": "Dopo il varo del 2014 (BRRD, SRMR, DGSD), la revisione è stata adottata nel 2026 [1]; la Commissione ha poi annunciato un sistema europeo dei depositi semplificato al posto della proposta EDIS del 2015 [3].",
 "attuale": "Il recepimento delle direttive va completato entro l'11 maggio 2028; le nuove regole si applicano da maggio 2028 [1]. La Banca d'Italia ne ha parlato al Parlamento il 29 ottobre 2026 [4].",
 "possibili": "Nel 2027 sono attese le proposte per un quadro semplificato di garanzia dei depositi europea e per un MREL più vicino al TLAC e più automatico [3].",
 "previsioni": [
  P("Recepimento italiano della riforma CMDI", "Nuovo obbligo",
    "Modifiche al TUB e ai decreti sulla risoluzione e sui sistemi di garanzia: uso dei fondi di garanzia per misure alternative, nuove condizioni per la risoluzione, trasparenza verso i depositanti.",
    "Entro 11 maggio 2028", "2028-05-11", "Alta", "Termine fissato dalle direttive pubblicate in Gazzetta UE.", [1, 2], [], ["Legale e societario", "Risk management"]),
  P("MREL più vicino al TLAC e più automatico", "Allentamento",
    "Calibrazione dell'MREL più automatica e allineata al TLAC, permessi di riacquisto più rapidi, piani di risoluzione più proporzionati.",
    "Proposta attesa entro marzo 2027", "2027-03-31", "Media", "Annunciato nella Comunicazione sulla competitività del luglio 2026.", [3], [], ["Risk management"]),
 ],
 "fonti": fc, "letture": [1, 2, 4]})

# ---------------------------------------------------------------- 4 Governance
fg = [F("EBA and ESMA consult on the revised suitability assessment framework", "Regulation Tomorrow (Eversheds Sutherland)", "2026-02", "https://www.regulationtomorrow.com/2026/02/eba-and-esma-consult-on-the-revised-suitability-assessment-framework-for-banks-and-investment-firms/", "Studio legale"),
      F("Consultation paper on joint guidelines on suitability", "EBA - ESMA", "2026-02-25", "https://www.eba.europa.eu/sites/default/files/2026-02/cd383d03-0d19-49a6-81f0-3b5a554886fc/CP%20on%20Joint%20GLs%20on%20suitability.pdf"),
      F("In GU il recepimento della CRD VI e l'adeguamento al CRR III (D.Lgs. 208/2025)", "DirittoBancario", "2026-01-09", "https://www.dirittobancario.it/art/in-gu-il-decreto-di-recepimento-della-crd-vi-e-di-adeguamento-al-crr-iii/", "Stampa specializzata"),
      F("Revisione art. 26 TUB con il d.lgs. 208/2025", "Fondazione Luzzatti", "2026-02", "https://www.luigiluzzatti.it/news/recepimento-della-direttiva-ue-2024-1619-crd-vi-modifiche-al-testo-unico-bancario-apportate-dal-d-lgs-31-dicembre-2025-n-208-02-2026/", "Stampa specializzata"),
      F("Governing Council proposes simplification of EU banking rules", "BCE", "2025-12-11", "https://www.ecb.europa.eu/press/pr/date/2025/html/ecb.pr251211~aa5c9271b8.en.html")]
S.append({"tema": "Governance, controlli e organizzazione", "iter": ["CRR3 / CRD6"],
 "visione": "La governance delle banche è al centro del recepimento di CRD6: il D.Lgs. 208/2025 ha riscritto le regole del TUB su idoneità di esponenti e responsabili delle funzioni chiave [3][4]. A livello europeo EBA ed ESMA stanno aggiornando le linee guida sull'idoneità [1][2].",
 "contesto": "Le nuove regole chiedono valutazioni più strutturate di competenza, correttezza e indipendenza, estese ai responsabili delle funzioni chiave nelle banche grandi [1][4]. Insieme, la BCE chiede di armonizzare in Europa licenze, governance e operazioni con parti correlate [5].",
 "evoluzione": "Il D.Lgs. 208/2025 è in Gazzetta dall'8 gennaio 2026, con regimi transitori [3]. Le linee guida congiunte EBA-ESMA sono state in consultazione fino al 25 maggio 2026 [1].",
 "attuale": "Le banche stanno adeguando processi di nomina e autovalutazione; si attendono le disposizioni attuative della Banca d'Italia e la versione finale delle linee guida europee [1][3].",
 "possibili": "Linee guida finali con alcune semplificazioni per ridurre gli oneri, ma con più attenzione ai responsabili delle funzioni chiave [1]; nel medio periodo, regole di governance armonizzate a livello UE [5].",
 "previsioni": [
  P("Linee guida EBA-ESMA finali sull'idoneità", "Nuovo obbligo",
    "Testo definitivo delle linee guida per membri degli organi e responsabili delle funzioni chiave, con misure di semplificazione e regole per le succursali di paesi terzi.",
    "2027", "2027-03-31", "Alta", "Consultazione conclusa a maggio 2026: la versione finale è il passo successivo.", [1, 2], [], ["Legale e societario", "Compliance"]),
  P("Aggiornamento della Circolare 285 su governo societario e idoneità", "Nuovo obbligo",
    "Disposizioni attuative della Banca d'Italia dopo il D.Lgs. 208/2025 (procedure di valutazione, ruolo dei responsabili delle funzioni chiave).",
    "2026-2027", "2027-03-31", "Media", "Il decreto rinvia a norme attuative; le tempistiche non sono ancora note.", [3, 4], [], ["Legale e societario"]),
 ],
 "fonti": fg, "letture": [1, 3, 4]})

# ---------------------------------------------------------------- 5 AML
fa = [F("What's done, what's due: the AML countdown", "Herbert Smith Freehills Kramer", "2026-07-14", "https://www.hsfkramer.com/notes/fsrandcorpcrime/2026-posts/whats-done-whats-due-the-aml-countdown", "Studio legale"),
      F("AMLA finalises key standards for the private sector", "Regulation Tomorrow (Eversheds Sutherland)", "2026-10-01", "https://www.regulationtomorrow.com/2026/10/amla-finalises-key-standards-for-the-private-sector/", "Studio legale"),
      F("Regolamento (UE) 2024/1624 (AMLR)", "EUR-Lex", "2024-06-19", EL("32024R1624")),
      F("Provvedimenti sanzionatori (pagina Sanzioni del sito)", "Banca d'Italia", "2026", "https://www.bancaditalia.it/compiti/vigilanza/provvedimenti-sanzionatori/")]
S.append({"tema": "Antiriciclaggio e sanzioni finanziarie", "iter": ["Pacchetto antiriciclaggio (AMLR, AMLD6, AMLA)"],
 "visione": "Il nuovo corpo unico europeo antiriciclaggio si applica dal 10 luglio 2027 [3]. Il 1° ottobre 2026 l'AMLA ha finalizzato i primi standard tecnici su adeguata verifica, soglie e requisiti di gruppo [2].",
 "contesto": "Le regole diventano direttamente applicabili e uguali in tutta l'UE: adeguata verifica, titolare effettivo al 25%, limite al contante di 10.000 euro [3]. È anche l'area dove la Banca d'Italia sanziona di più dopo il governo dei rischi (dati della pagina Sanzioni) [4].",
 "evoluzione": "Pacchetto adottato a maggio 2024; AMLA operativa dal 2025; 2026 dedicato al secondo livello con consultazioni e audizioni [1].",
 "attuale": "Gli RTS finali su adeguata verifica, soglie e requisiti di gruppo sono stati inviati alla Commissione per l'adozione [2]. L'AMLA ha individuato i soggetti potenzialmente idonei alla vigilanza diretta entro fine settembre 2026 [1].",
 "possibili": "Adozione degli RTS da parte della Commissione, revisione del D.Lgs. 231/2007 e delle disposizioni della Banca d'Italia, prima selezione dei soggetti vigilati direttamente nel 2027 [1][2].",
 "previsioni": [
  P("Nuove regole di adeguata verifica uguali in tutta l'UE", "Irrigidimento",
    "RTS AMLA: informazioni da raccogliere per verifica ordinaria, semplificata e rafforzata; requisiti per l'identità digitale; soglie più basse per settori ad alto rischio; regole di gruppo e per le filiali in paesi terzi.",
    "10 luglio 2027", "2027-07-10", "Alta", "RTS finalizzati dall'AMLA e data di applicazione fissata dal regolamento.", [2, 3, 1], [], ["Antiriciclaggio", "Compliance"]),
  P("Prima selezione dei gruppi vigilati direttamente dall'AMLA", "Nuovo obbligo",
    "Fino a 40 soggetti transfrontalieri ad alto rischio passeranno alla vigilanza diretta dell'AMLA dal 2028.",
    "2027 (selezione), luglio 2028 (avvio)", "2027-06-30", "Alta", "Scadenze del regolamento AMLA e programma pubblicato.", [1], [("Soggetti selezionabili", "fino a 40", 1)], ["Antiriciclaggio"]),
  P("Revisione del D.Lgs. 231/2007", "Nuovo obbligo", "Adeguamento della legge italiana al regolamento AMLR e recepimento degli articoli della AMLD6.",
    "2027", "2027-06-30", "Media", "Necessaria prima dell'applicazione dell'AMLR; tempi italiani non ancora annunciati.", [1, 3], [], ["Antiriciclaggio", "Legale e societario"]),
 ],
 "fonti": fa, "letture": [1, 2]})

# ---------------------------------------------------------------- 6 Misure restrittive
fm = [F("EU Council adopts 21st sanctions package against Russia", "Steptoe", "2026-07-23", "https://www.steptoe.com/en/news-publications/international-compliance-blog/eu-council-adopts-21st-sanctions-package-against-russia.html", "Studio legale"),
      F("20th package of EU sanctions against Russia", "DLA Piper", "2026-04", "https://www.dlapiper.com/en-pt/insights/publications/global-sanctions-alert/2026/20th-package-of-eu-sanctions-against-russia", "Studio legale"),
      F("EU's 21st sanctions package on Russia clamps down on energy, fisheries, defence trade", "Brussels Times", "2026-07", "https://www.brusselstimes.com/2181224/eus-21st-sanctions-package-on-russia-clamps-down-on-energy-fisheries-defence-trade", "Stampa")]
S.append({"tema": "Misure restrittive e sanzioni internazionali", "iter": [],
 "visione": "Le sanzioni UE contro la Russia sono arrivate al 21° pacchetto (23 luglio 2026) e colpiscono sempre di più il settore finanziario: divieti di operazioni con banche russe e di paesi terzi, prestatori di cripto-attività e intermediari di pagamento [1][2].",
 "contesto": "Per le banche il rischio è soprattutto di elusione: operazioni indirette tramite paesi terzi, sistemi di messaggistica alternativi (SPFS), cripto [1][2]. Il volume di atti UE su questo tema è il più alto di tutti (vedi grafico).",
 "evoluzione": "Il 20° pacchetto (23 aprile 2026) ha aggiunto 20 banche russe ai divieti e ha usato per la prima volta lo strumento anti-elusione [2]; il 21° ha esteso i divieti a 33 banche russe e 14 prestatori di cripto [1].",
 "attuale": "Divieto per cittadini russi di avere ruoli nei CASP autorizzati MiCAR dal 25 agosto 2026; possibilità di vietare operazioni con cripto di paesi terzi indicati [1].",
 "possibili": "Nuovi pacchetti con altre banche di paesi terzi e attivazione del divieto sui prestatori cripto di paesi terzi [1].",
 "previsioni": [
  P("Altre banche di paesi terzi nella lista dei divieti", "Irrigidimento",
    "Estensione dei divieti di operazione a istituti di paesi terzi coinvolti nell'elusione o collegati a SPFS; aggiornamento dei controlli sui pagamenti e sulle banche corrispondenti.",
    "Prossimo pacchetto (2026-2027)", "2027-01-31", "Alta", "Ogni pacchetto del 2026 ha aggiunto banche di paesi terzi.", [1, 2],
    [("Banche russe con divieto (21° pacchetto)", "33", 1), ("Banche russe aggiunte (20° pacchetto)", "20", 2)], ["Antiriciclaggio", "Compliance"]),
  P("Divieto di operare con cripto di paesi terzi indicati", "Irrigidimento",
    "Lo strumento già previsto dal 21° pacchetto verrebbe applicato a paesi specifici.", "2027", "2027-06-30", "Media",
    "Base giuridica già adottata, ma nessun paese ancora indicato.", [1], [], ["Antiriciclaggio"]),
 ],
 "fonti": fm, "letture": [1, 2, 3]})

# ---------------------------------------------------------------- 7 Servizi di investimento
fi = [F("Provisional agreement on the Retail Investment Strategy", "Loyens & Loeff", "2025-12", "https://www.loyensloeff.com/insights/news--events/news/provisional-agreement-on-the-retail-investment-strategy---what-fund-managers-need-to-know/", "Studio legale"),
      F("Council position on the market integration and supervision package", "Lovguiden", "2026-10-09", "https://www.lovguiden.dk/en/det-offentlige/raadet-for-den-europaeiske-union/2026-10-09-raadet-vil-flytte-tilsyn-med-store-handelspladser-til-esma", "Stampa specializzata"),
      F("TUF: pubblicato il decreto di adeguamento alle riforme UE (D.Lgs. 28/2026)", "Edotto", "2026-03", "https://www.edotto.com/articolo/tuf-pubblicato-il-decreto-di-adeguamento-alle-riforme-ue", "Stampa specializzata"),
      F("Consultazione Consob sulle modifiche ai regolamenti Mercati, Intermediari ed Emittenti", "Consob", "2026-07-17", "https://www.consob.it/web/consob/w/consultazione-consob-sulle-modifiche-regolamentari-regolamenti-mercati-intermediari-ed-emittenti-17-luglio-2026"),
      F("Regulation to shorten settlement cycle to T+1 published in OJ", "A&O Shearman", "2025-10", "https://finreg.aoshearman.com/Regulation-to-shorten-settlement-cycle-to-T1-publ", "Studio legale")]
S.append({"tema": "Servizi di investimento e mercati", "iter": ["MiFID II / MiFIR", "Retail Investment Strategy", "CSDR - disciplina di regolamento"],
 "visione": "Tre cantieri insieme: la Retail Investment Strategy (accordo di dicembre 2025) che cambia incentivi e adeguatezza [1], il pacchetto sull'integrazione dei mercati che sposta parte della vigilanza all'ESMA [2], il passaggio al regolamento T+1 nell'ottobre 2027 [5].",
 "contesto": "In Italia il TUF è stato adeguato alla revisione MiFID/MiFIR con il D.Lgs. 28/2026 [3] e la Consob ha in consultazione modifiche ai suoi regolamenti [4].",
 "evoluzione": "MiFID II si applica dal 2018; la revisione 2024 ha introdotto nastro consolidato e divieto del pagamento per il flusso ordini; l'accordo RIS del 18 dicembre 2025 ha rinunciato al divieto degli incentivi a favore di benchmark di costo [1][3].",
 "attuale": "Il Consiglio ha fissato il 9 ottobre 2026 la sua posizione sul pacchetto vigilanza: ESMA diretta su grandi sedi di negoziazione, depositari centrali, controparti centrali e grandi prestatori di cripto [2].",
 "possibili": "Testo finale RIS e applicazione verso fine 2028; nuovi regolamenti Consob; negoziato con il Parlamento sul pacchetto ESMA entro il 2027 [1][2][4].",
 "previsioni": [
  P("Value for money: i prodotti troppo costosi non si potranno vendere ai clienti al dettaglio", "Irrigidimento",
    "Costi da quantificare e confrontare con gruppi di prodotti simili; se non giustificati, il prodotto non va approvato per la clientela al dettaglio. Incentivi ammessi solo se a beneficio del cliente e indicati a parte.",
    "Pubblicazione 2027, applicazione circa fine 2028", "2028-12-31", "Alta", "C'è l'accordo politico; manca l'adozione formale.", [1], [("Recepimento", "24 mesi dalla pubblicazione", 1)], ["Compliance", "Commerciale e prodotti"]),
  P("Adeguatezza semplificata per i prodotti semplici e poco costosi", "Allentamento",
    "Per prodotti non complessi ed efficienti nei costi non servirà più valutare conoscenza ed esperienza del cliente nella consulenza; soglie più basse per passare a cliente professionale (portafoglio da 500.000 a 250.000 euro).",
    "Circa fine 2028", "2028-12-31", "Alta", "Contenuto dell'accordo RIS.", [1], [("Soglia portafoglio per cliente professionale", "500.000 € → 250.000 €", 1)], ["Compliance", "Commerciale e prodotti"]),
  P("Regolamento delle operazioni in T+1", "Nuovo obbligo", "Le operazioni in titoli si regoleranno un giorno dopo la negoziazione: da rivedere processi di post-trading, cambi e prestito titoli.",
    "11 ottobre 2027", "2027-10-11", "Alta", "Data fissata dal Regolamento (UE) 2025/2075.", [5], [], ["Commerciale e prodotti", "Risk management"]),
  P("Vigilanza ESMA su grandi sedi e infrastrutture", "Nuovo obbligo", "Passaggio all'ESMA della vigilanza su sedi di negoziazione, CSD e CCP più rilevanti e sui grandi prestatori di cripto; passaporto del depositario facoltativo.",
    "Entro fine 2027 (obiettivo)", "2027-12-31", "Media", "Posizione del Consiglio fissata; manca quella del Parlamento.", [2], [], ["Compliance"]),
 ],
 "fonti": fi, "letture": [1, 2, 4]})

# ---------------------------------------------------------------- 8 Trasparenza
ft = [F("CCD 2: in GU il decreto del CICR in materia di credito ai consumatori", "DirittoBancario", "2026-08", "https://www.dirittobancario.it/art/ccd-2-in-gu-il-decreto-del-cicr-in-materia-di-credito-ai-consumatori/", "Stampa specializzata"),
      F("DECRETO LEGISLATIVO 31 dicembre 2025, n. 212", "Normattiva", "2026-01-09", "https://www.normattiva.it/eli/id/2026/01/09/26G00009/ORIGINAL"),
      F("Provisional agreement on the Retail Investment Strategy", "Loyens & Loeff", "2025-12", "https://www.loyensloeff.com/insights/news--events/news/provisional-agreement-on-the-retail-investment-strategy---what-fund-managers-need-to-know/", "Studio legale"),
      F("PSD3 e PSR, pagamenti UE verso la svolta", "Jamma", "2026-08-18", "https://www.jamma.it/attualita/psd3-e-psr-pagamenti-ue-verso-la-svolta-nuove-regole-e-scadenza-nel-2028-357298", "Stampa"),
      F("Provvedimenti sanzionatori", "Banca d'Italia", "2026", "https://www.bancaditalia.it/compiti/vigilanza/provvedimenti-sanzionatori/")]
S.append({"tema": "Trasparenza e tutela della clientela", "iter": ["Credito ai consumatori (CCD2)", "Retail Investment Strategy", "PSD3 e Regolamento servizi di pagamento (PSR)"],
 "visione": "La tutela del cliente è il terreno dove arrivano più obblighi nuovi: credito ai consumatori dal 20 novembre 2026 [1][2], prodotti di investimento con la RIS [3], pagamenti con PSD3/PSR [4].",
 "contesto": "Le sanzioni della Banca d'Italia per trasparenza riguardano spesso oneri non dovuti e carenze di organizzazione e controlli (vedi pagina Sanzioni) [5]. Il decreto CICR del 9 luglio 2026 ha riscritto pubblicità, informativa e contratti nel credito ai consumatori [1].",
 "evoluzione": "D.Lgs. 212/2025 in vigore dal 10 gennaio 2026 [2]; decreto CICR in GU il 17 agosto 2026 [1].",
 "attuale": "Mancano le disposizioni attuative della Banca d'Italia su pubblicità, informativa precontrattuale, merito creditizio e contratti [1].",
 "possibili": "Nuove disposizioni di trasparenza della Banca d'Italia, rimborsi più ampi nelle frodi di pagamento con PSR, regole sul value for money [1][3][4].",
 "previsioni": [
  P("Pubblicità del credito con avviso obbligatorio e TAEG non in evidenza", "Irrigidimento",
    "Le pubblicità devono dire che «prendere denaro in prestito costa denaro»; se citano un costo devono riportare le informazioni base, senza dare al TAEG più risalto delle altre voci; vietate alcune affermazioni ingannevoli.",
    "Con le disposizioni Banca d'Italia (fine 2026)", "2026-12-31", "Alta", "Già previsto dal decreto CICR in Gazzetta.", [1], [], ["Compliance", "Commerciale e prodotti"]),
  P("Esenzioni per crediti sotto 200 euro e a interessi zero", "Allentamento",
    "Nuova esenzione per crediti sotto 200 euro, senza interessi o rimborsati entro tre mesi con commissioni non significative.",
    "Con l'applicazione della CCD2", "2026-11-20", "Alta", "Previsto dal decreto CICR.", [1], [("Soglia di esenzione", "200 €", 1)], ["Commerciale e prodotti"]),
  P("Banche responsabili nelle frodi da impersonificazione", "Irrigidimento",
    "Con il PSR la responsabilità si sposta verso il prestatore di pagamento, salvo dolo o colpa grave del cliente; verifica IBAN-nome prima di ogni bonifico.",
    "Circa 2028", "2028-09-30", "Alta", "Testi finali del Consiglio pubblicati ad aprile 2026.", [4], [], ["Compliance", "IT, sicurezza e dati"]),
 ],
 "fonti": ft, "letture": [1, 2, 4]})

# ---------------------------------------------------------------- 9 Credito
fcr = [F("CCD 2: in GU il decreto del CICR in materia di credito ai consumatori", "DirittoBancario", "2026-08", "https://www.dirittobancario.it/art/ccd-2-in-gu-il-decreto-del-cicr-in-materia-di-credito-ai-consumatori/", "Stampa specializzata"),
       F("Direttiva (UE) 2023/2225 (CCD2)", "EUR-Lex", "2023-10-30", EL("32023L2225")),
       F("European Commission Outlines Banking Reform Agenda", "Sullivan & Cromwell", "2026-08-26", "https://www.sullcrom.com/insights/memo/2026/August/EU-Banking-Competitiveness-Cross-Border-MA", "Studio legale"),
       F("AI Act implications for the EU banking sector", "EBA", "2025-11", "https://www.eba.europa.eu/sites/default/files/2025-11/d8b999ce-a1d9-4964-9606-971bbc2aaf89/AI%20Act%20implications%20for%20the%20EU%20banking%20sector.pdf"),
       F("EU AI Omnibus enters into force, amending the AI Act", "White & Case", "2026-07", "https://www.whitecase.com/insight-alert/eu-ai-omnibus-enters-force-amending-ai-act", "Studio legale")]
S.append({"tema": "Credito e finanziamenti", "iter": ["Credito ai consumatori (CCD2)"],
 "visione": "Il credito alle famiglie cambia dal 20 novembre 2026 con la nuova direttiva sul credito ai consumatori [2]; il merito creditizio con IA diventa sistema ad alto rischio dal dicembre 2027 [5].",
 "contesto": "Il decreto CICR chiede una valutazione del merito creditizio approfondita e rimanda alla Banca d'Italia i fattori da considerare [1]. Sul fronte prudenziale la Commissione vuole ricalibrare l'output floor per mutui e imprese senza rating [3].",
 "evoluzione": "CCD2 pubblicata nel 2023, recepita con D.Lgs. 212/2025, attuata con decreto CICR del 9 luglio 2026 [1][2].",
 "attuale": "Si attendono le disposizioni della Banca d'Italia su merito creditizio e scoperti «regolari» [1].",
 "possibili": "Regole uniche UE sul merito creditizio, obblighi AI Act sui modelli di scoring, capitale più leggero su mutui con modelli interni [3][4][5].",
 "previsioni": [
  P("Merito creditizio: valutazione approfondita con fattori fissati dalla Banca d'Italia", "Irrigidimento",
    "Valutazione basata su informazioni pertinenti e accurate su reddito e spese; la Banca d'Italia indicherà i fattori; accesso non discriminatorio alle banche dati per i creditori di altri Paesi UE.",
    "Fine 2026 - 2027", "2027-03-31", "Alta", "Previsto dal decreto CICR e dalla direttiva.", [1, 2], [], ["Commerciale e prodotti", "Risk management"]),
  P("Scoring creditizio con IA come sistema ad alto rischio", "Nuovo obbligo",
    "Gestione dei rischi, qualità dei dati, documentazione, sorveglianza umana e registrazione per i modelli di IA che valutano il merito creditizio delle persone.",
    "2 dicembre 2027", "2027-12-02", "Alta", "Data fissata dal Digital Omnibus; l'EBA ha mappato le sovrapposizioni con le regole bancarie.", [5, 4], [], ["IT, sicurezza e dati", "Risk management"]),
 ],
 "fonti": fcr, "letture": [1, 4]})

# ---------------------------------------------------------------- 10 Pagamenti
fp = [F("PSD3 and PSR published: what's changing for EU payment services?", "Matheson", "2026-04", "https://www.matheson.com/insights/psd3-and-psr-published-whats-changing-for-eu-payment-services/", "Studio legale"),
      F("PSD3 e PSR, pagamenti UE verso la svolta", "Jamma", "2026-08-18", "https://www.jamma.it/attualita/psd3-e-psr-pagamenti-ue-verso-la-svolta-nuove-regole-e-scadenza-nel-2028-357298", "Stampa"),
      F("European Parliament backs digital euro legislation", "Brussels Signal", "2026-06-23", "https://brusselssignal.eu/2026/06/european-parliament-backs-digital-euro-legislation/", "Stampa"),
      F("Regolamento (UE) 2024/886 (Instant Payments)", "EUR-Lex", "2024-03-19", EL("32024R0886")),
      F("FiDA back in motion: from ambitious to workable", "Thede Consulting", "2026-07-16", "https://thede-consulting.com/en/payment-en/fida-back-in-motion-from-ambitious-to-workable/", "Consulenza")]
S.append({"tema": "Pagamenti, conti e moneta", "iter": ["PSD3 e Regolamento servizi di pagamento (PSR)", "Instant Payments", "Accesso ai dati finanziari (FiDA)"],
 "visione": "I pagamenti vivono la riforma più ampia dai tempi della PSD2: PSD3 e PSR attese in Gazzetta UE [1][2], euro digitale in negoziato finale [3], bonifici istantanei già obbligatori nell'area euro [4].",
 "contesto": "Le priorità sono frodi, open banking e parità di condizioni tra banche e operatori non bancari [1][2]. L'euro digitale è pensato con un limite di detenzione per persona (si discute tra 500 e 3.000 euro) per evitare fughe dai depositi [3].",
 "evoluzione": "Accordo politico PSD3/PSR a fine 2025 e testi finali del Consiglio il 23 aprile 2026 [1]; bonifici istantanei e verifica del beneficiario dal 9 ottobre 2025 [4].",
 "attuale": "Si attende la pubblicazione in Gazzetta di PSD3/PSR (attesa nel 2026) [2]; per l'euro digitale si è aperta la fase di trilogo dopo il voto della commissione ECON [3]; FiDA ha un nuovo non-paper della Commissione [5].",
 "possibili": "Applicazione PSR circa 21 mesi dopo l'entrata in vigore (indicativamente 2028), euro digitale pronto dal 2029 se la legge arriva in tempo, FiDA ridimensionata e per fasi [2][3][5].",
 "previsioni": [
  P("Capitale minimo rivisto e salvaguardia dei fondi più severa per gli istituti di pagamento", "Irrigidimento",
    "Capitale iniziale per le rimesse da 20.000 a 40.000 euro e per gli altri servizi da 125.000 a 150.000 euro (IMEL invece da 350.000 a 250.000); i fondi dei clienti non possono stare tutti presso una sola banca.",
    "Circa 2028", "2028-09-30", "Alta", "Testi finali pubblicati dal Consiglio.", [2, 1], [("Capitale per le rimesse", "20.000 € → 40.000 €", 2), ("Capitale IMEL", "350.000 € → 250.000 €", 2)], ["Commerciale e prodotti", "Compliance"]),
  P("Euro digitale con limite di detenzione per persona", "Nuovo obbligo",
    "Le banche dovranno distribuire l'euro digitale (online e offline) entro un limite per persona in discussione tra 500 e 3.000 euro; impatti su liquidità, sistemi e offerta.",
    "Legge 2026-2027, emissione dal 2029", "2029-06-30", "Media", "Posizione del Consiglio (dicembre 2025) e voto ECON (2026); manca l'accordo finale.", [3], [("Limite di detenzione in discussione", "500-3.000 €", 3)], ["Commerciale e prodotti", "IT, sicurezza e dati", "Risk management"]),
  P("FiDA ridimensionata e introdotta per fasi", "Allentamento", "Open finance in tre fasi in circa quattro anni, prima gli schemi di condivisione; possibili esclusioni di soggetti e dati e storico più breve.",
    "Accordo possibile nel 2027", "2027-06-30", "Bassa", "Negoziato fermo da giugno 2025, rilanciato da un non-paper di luglio 2026.", [5], [], ["IT, sicurezza e dati"]),
 ],
 "fonti": fp, "letture": [1, 2, 3]})

# ---------------------------------------------------------------- 11 Cripto
fk = [F("Fit for Purpose? European Commission Launches Review of MiCA", "Skadden", "2026-06", "https://www.skadden.com/insights/publications/2026/06/fit-for-purpose", "Studio legale"),
      F("ESMA responds to Commission's consultation on the review of MiCA", "Regulation Tomorrow (Eversheds Sutherland)", "2026-09", "https://www.regulationtomorrow.com/2026/09/esma-responds-to-commissions-consultation-on-the-review-of-mica/", "Studio legale"),
      F("EBA identifies priorities for the review of MiCA", "Regulation Tomorrow (Eversheds Sutherland)", "2026-09", "https://www.regulationtomorrow.com/2026/09/eba-identifies-priorities-for-the-review-of-mica/", "Studio legale"),
      F("Council position on the market integration and supervision package", "Lovguiden", "2026-10-09", "https://www.lovguiden.dk/en/det-offentlige/raadet-for-den-europaeiske-union/2026-10-09-raadet-vil-flytte-tilsyn-med-store-handelspladser-til-esma", "Stampa specializzata"),
      F("Comunicazione Consob n. 16/25 del 4 dicembre 2025", "Consob", "2025-12-04", "https://www.consob.it/web/consob-and-its-activities/-/consob-communication-no.-16/25-of-4-december-2025"),
      F("EU Council adopts 21st sanctions package against Russia", "Steptoe", "2026-07-23", "https://www.steptoe.com/en/news-publications/international-compliance-blog/eu-council-adopts-21st-sanctions-package-against-russia.html", "Studio legale")]
S.append({"tema": "Cripto-attività e finanza digitale", "iter": ["MiCAR"],
 "visione": "MiCAR è pienamente applicato e in Italia il regime transitorio è finito il 30 dicembre 2025 [5]. Ora si apre «MiCA 2»: la Commissione ha consultato il mercato fino al 31 agosto 2026 [1], ESMA ed EBA hanno indicato le loro priorità [2][3].",
 "contesto": "Nel registro ESMA ci sono circa 227 prestatori di servizi su cripto in 25 Paesi [1]. Il Consiglio vuole la vigilanza ESMA diretta solo sui prestatori più grandi e transfrontalieri [4]. Le sanzioni UE colpiscono anche le cripto collegate alla Russia [6].",
 "evoluzione": "Regolamento del 2023, stablecoin dal giugno 2024, tutto il resto dal dicembre 2024; consultazione sulla revisione aperta il 20 maggio 2026 [1].",
 "attuale": "Temi aperti: stablecoin emesse in più giurisdizioni, divieto di remunerare le stablecoin, prestito e staking, DeFi [1]; l'EBA chiede regole più severe su stablecoin e prestiti in cripto [3].",
 "possibili": "Proposta di revisione MiCA con regole più dure su stablecoin e nuove attività (prestito di cripto), passaggio dei grandi CASP all'ESMA [1][3][4].",
 "previsioni": [
  P("Regole più severe su stablecoin emesse in più Paesi", "Irrigidimento",
    "Diritti di rimborso più forti per chi detiene stablecoin nell'UE, requisiti di riserva e prudenziali rivisti, regime di equivalenza per emittenti di paesi terzi.",
    "Proposta 2027", "2027-06-30", "Media", "Temi centrali della consultazione e priorità indicate dall'EBA.", [1, 3], [("CASP nel registro ESMA", "circa 227", 1)], ["Compliance", "Commerciale e prodotti"]),
  P("Prestito e staking di cripto dentro il perimetro regolato", "Nuovo obbligo",
    "Possibile inclusione di prestito e indebitamento in cripto tra i servizi regolati e revisione del trattamento dello staking.", "Proposta 2027", "2027-06-30", "Media",
    "Temi esplicitamente in consultazione.", [1, 3], [], ["Compliance"]),
 ],
 "fonti": fk, "letture": [1, 2, 3]})

# ---------------------------------------------------------------- 12 Cyber / DORA
fd = [F("DORA update 7", "AFM (autorità olandese)", "2026-08-06", "https://www.afm.nl/en/sector/actueel/2026/aug/sb-dora-update-7"),
      F("ESAs designate critical ICT third-party providers under DORA", "EIOPA", "2025-11-18", "https://www.eiopa.europa.eu/european-supervisory-authorities-designate-critical-ict-third-party-providers-under-digital-2025-11-18_it"),
      F("ESAs Set Out 2026 Agenda with Focus on DORA Oversight", "GRC Report", "2026", "https://www.grcreport.com/post/esas-set-out-2026-agenda-with-focus-on-dora-oversight-consumer-protection-sustainability-simplification", "Stampa specializzata"),
      F("GDPR, AI and cookies: what the EU's data omnibus could change", "Heuking", "2026-09-24", "https://www.heuking.de/en/news-events/newsletter-articles/detail/gdpr-ai-and-cookies-what-the-eus-data-omnibus-could-change-for-companies.html", "Studio legale"),
      F("Scadenze NIS2: cosa devono fare le imprese entro ottobre 2026", "Namirial", "2026", "https://focus.namirial.com/it/nis2-scadenze-e-obblighi-2026/", "Stampa specializzata"),
      F("Regolamento (UE) 2022/2554 (DORA)", "EUR-Lex", "2022-12-27", EL("32022R2554"))]
S.append({"tema": "Cybersicurezza, ICT e DORA", "iter": ["DORA", "NIS2 (cibersicurezza)"],
 "visione": "DORA si applica dal 17 gennaio 2025 [6] e il 2026 è il primo ciclo completo di sorveglianza sui fornitori ICT critici designati dalle autorità europee [2][3].",
 "contesto": "La qualità dei dati è migliorata: le approvazioni del registro delle informazioni da parte dell'EBA sono passate dal 40% del 2025 al 94% del 2026 [1]. Le autorità segnalano però politiche non complete e meno notifiche di incidenti del previsto [1].",
 "evoluzione": "Designazione dei fornitori critici il 18 novembre 2025 [2]; nel 2026 piani di sorveglianza e prime ispezioni [3]. Per NIS2, in Italia, notifica degli incidenti dal 2026 e misure di base entro ottobre 2026 [5].",
 "attuale": "Le autorità controllano politiche ICT, documenti di gruppo e tempestività delle notifiche [1]; il Digital Omnibus propone un punto unico per notificare gli incidenti, ancora in discussione [4].",
 "possibili": "Prime raccomandazioni ai fornitori critici con effetti sui contratti delle banche, notifica unica degli incidenti DORA/NIS2/GDPR, ispezioni sulle politiche [1][3][4].",
 "previsioni": [
  P("Più controlli su politiche ICT e notifica degli incidenti", "Irrigidimento",
    "Le autorità hanno trovato politiche incomplete e poche notifiche: attese verifiche su classificazione e tempi di notifica degli incidenti e su documenti di gruppo.",
    "2027", "2027-03-31", "Alta", "Messaggio esplicito di un'autorità nazionale dopo le prime verifiche.", [1],
    [("Registri approvati dall'EBA", "40% (2025) → 94% (2026)", 1)], ["IT, sicurezza e dati", "Compliance"]),
  P("Notifica unica degli incidenti (DORA, NIS2, GDPR)", "Semplificazione",
    "Un solo punto per notificare incidenti informatici e violazioni di dati, invece di canali separati.", "Dopo il 2027", "2028-06-30", "Bassa",
    "Proposta nel Digital Omnibus ma contestata in Consiglio.", [4], [], ["IT, sicurezza e dati"]),
 ],
 "fonti": fd, "letture": [1, 3, 2]})

# ---------------------------------------------------------------- 13 IA
fai = [F("EU AI Omnibus enters into force, amending the AI Act", "White & Case", "2026-07", "https://www.whitecase.com/insight-alert/eu-ai-omnibus-enters-force-amending-ai-act", "Studio legale"),
       F("AI Act implications for the EU banking sector", "EBA", "2025-11", "https://www.eba.europa.eu/sites/default/files/2025-11/d8b999ce-a1d9-4964-9606-971bbc2aaf89/AI%20Act%20implications%20for%20the%20EU%20banking%20sector.pdf"),
       F("Italy enacts Law No. 132/2025 on artificial intelligence", "Norton Rose Fulbright", "2025-10", "https://www.nortonrosefulbright.com/en/knowledge/publications/9bfedfea/italy-enacts-law-no-132-2025-on-artificial-intelligence-sector-rules-and-next-steps", "Studio legale"),
       F("GDPR, AI and cookies: what the EU's data omnibus could change", "Heuking", "2026-09-24", "https://www.heuking.de/en/news-events/newsletter-articles/detail/gdpr-ai-and-cookies-what-the-eus-data-omnibus-could-change-for-companies.html", "Studio legale"),
       F("Regolamento (UE) 2024/1689 (AI Act)", "EUR-Lex", "2024-07-12", EL("32024R1689"))]
S.append({"tema": "Intelligenza artificiale e innovazione", "iter": ["AI Act e Digital Omnibus"],
 "visione": "L'AI Act è in vigore dal 2024 [5], ma il Digital Omnibus (Reg. 2026/1744) ha spostato gli obblighi più pesanti: per i sistemi ad alto rischio come il merito creditizio si parte dal 2 dicembre 2027 [1].",
 "contesto": "Per le banche l'EBA ha mappato l'AI Act rispetto alle regole bancarie esistenti [2]. In Italia la legge 132/2025 ha fissato principi e autorità nazionali [3].",
 "evoluzione": "Divieti e alfabetizzazione dal febbraio 2025, modelli generali dall'agosto 2025, trasparenza dall'agosto 2026 [1][5].",
 "attuale": "Dal 2 agosto 2026 valgono gli obblighi di trasparenza; per i sistemi già sul mercato la marcatura dei contenuti generati scatta il 2 dicembre 2026 [1]. Sull'uso dei dati personali per addestrare l'IA il negoziato del Digital Omnibus è ancora aperto [4].",
 "possibili": "Linee guida della Commissione sulla classificazione dei sistemi ad alto rischio e possibili esclusioni dove le norme di settore coprono già il rischio [1].",
 "previsioni": [
  P("Alfabetizzazione sull'IA meno vincolante", "Allentamento",
    "Il Digital Omnibus chiede di «favorire» un livello sufficiente di alfabetizzazione invece di «garantirlo»: obbligo meno rigido per banche e fornitori.",
    "Già in vigore (luglio 2026)", "2026-07-27", "Alta", "Modifica contenuta nel Reg. (UE) 2026/1744.", [1], [], ["Risorse umane", "IT, sicurezza e dati"]),
  P("Possibili esclusioni settoriali per le banche", "Allentamento",
    "Atti delegati della Commissione potrebbero limitare l'applicazione dell'AI Act dove le norme di settore hanno requisiti equivalenti sull'IA (es. modelli di rischio già vigilati).",
    "2027", "2027-06-30", "Bassa", "Possibilità prevista, senza tempi; l'EBA ha studiato le sovrapposizioni.", [1, 2], [], ["Risk management"]),
  P("Obblighi alto rischio per scoring e assicurazioni vita e salute", "Nuovo obbligo",
    "Sistema di gestione del rischio, governance dei dati, documentazione tecnica, sorveglianza umana, registrazione nella banca dati UE.", "2 dicembre 2027", "2027-12-02", "Alta",
    "Data fissata dal Reg. (UE) 2026/1744.", [1], [], ["IT, sicurezza e dati", "Compliance", "Risk management"]),
 ],
 "fonti": fai, "letture": [1, 2, 3]})

# ---------------------------------------------------------------- 14 Privacy
fpr = [F("GDPR, AI and cookies: what the EU's data omnibus could change", "Heuking", "2026-09-24", "https://www.heuking.de/en/news-events/newsletter-articles/detail/gdpr-ai-and-cookies-what-the-eus-data-omnibus-could-change-for-companies.html", "Studio legale"),
       F("EU regulators issue opinion on revisions of GDPR and other data laws", "Inside Privacy (Covington)", "2026-02", "https://www.insideprivacy.com/eu-data-protection/eu-regulators-issue-opinion-on-revisions-of-gdpr-and-other-data-laws/", "Studio legale")]
S.append({"tema": "Privacy e protezione dei dati", "iter": [],
 "visione": "Il GDPR potrebbe cambiare per la prima volta dal 2018: il Digital Omnibus propone modifiche su dati pseudonimizzati, addestramento dell'IA, cookie e notifica delle violazioni [1].",
 "contesto": "Le autorità europee per la protezione dei dati hanno espresso un parere critico su alcune modifiche [2]. In Consiglio gli Stati sono ancora divisi [1].",
 "evoluzione": "Proposta della Commissione del 19 novembre 2025; testo rivisto della presidenza irlandese a settembre 2026 [1].",
 "attuale": "Nessuna modifica adottata; Parlamento senza posizione e triloghi non iniziati; conclusione non prima del 2027 [1].",
 "possibili": "Dati pseudonimizzati non personali per chi non può identificare la persona, interesse legittimo per l'addestramento dell'IA con diritto di opposizione, notifica delle violazioni solo se ad alto rischio [1].",
 "previsioni": [
  P("Notifica al Garante solo per violazioni ad alto rischio", "Allentamento",
    "Niente notifica all'autorità per le violazioni che probabilmente non comportano un rischio elevato (resta l'obbligo di documentarle).",
    "Non prima del 2027", "2027-12-31", "Media", "Proposta nel Digital Omnibus; negoziato aperto.", [1], [], ["IT, sicurezza e dati", "Compliance"]),
  P("Consenso ai cookie tramite segnali del browser", "Semplificazione",
    "Le regole sui cookie passerebbero nel GDPR, con scelte trasmesse da browser o sistema operativo e un elenco di finalità senza consenso.", "Non prima del 2027", "2027-12-31", "Media",
    "Uno dei punti meno contestati secondo le cronache del negoziato.", [1], [], ["IT, sicurezza e dati", "Commerciale e prodotti"]),
 ],
 "fonti": fpr, "letture": [1, 2]})

# ---------------------------------------------------------------- 15 ESG
fe = [F("EU Sustainability Omnibus Published in the Official Journal", "Latham & Watkins", "2026-03", "https://www.lw.com/en/insights/eu-sustainability-omnibus-published-in-the-official-journal", "Studio legale"),
      F("SFDR 2.0 in trilogue: where the negotiations stand", "Clarity AI", "2026", "https://clarity.ai/research-and-insights/regulatory-compliance/sfdr-2-0-in-trilogue-where-the-negotiations-stand-and-when-the-rules-will-apply/", "Ricerca"),
      F("Council signs off simplification of sustainability reporting and due diligence", "Consiglio UE", "2026-02-24", "https://www.consilium.europa.eu/en/press/press-releases/2026/02/24/council-signs-off-simplification-of-sustainability-reporting-and-due-diligence-requirements-to-boost-eu-competitiveness/"),
      F("ESAs Set Out 2026 Agenda", "GRC Report", "2026", "https://www.grcreport.com/post/esas-set-out-2026-agenda-with-focus-on-dora-oversight-consumer-protection-sustainability-simplification", "Stampa specializzata")]
S.append({"tema": "Finanza sostenibile ed ESG", "iter": ["CSRD e ESRS (rendicontazione di sostenibilità)"],
 "visione": "La sostenibilità è il caso più netto di allentamento: l'Omnibus I ha ristretto la CSRD alle imprese con più di 1.000 dipendenti e 450 milioni di fatturato [1][3], e la SFDR 2.0 riscrive le regole per i prodotti finanziari [2].",
 "contesto": "Per le banche cambia sia il proprio bilancio di sostenibilità sia ciò che possono chiedere ai clienti: il tetto alla catena del valore limita le richieste di dati alle imprese sotto i 1.000 dipendenti [1].",
 "evoluzione": "Omnibus I in Gazzetta il 26 febbraio 2026, recepimento della parte CSRD entro il 19 marzo 2027 [1]. SFDR 2.0 proposta il 20 novembre 2025, posizione del Consiglio il 19 giugno 2026 [2].",
 "attuale": "Si attendono gli ESRS semplificati e i triloghi sulla SFDR 2.0 (avvio nel quarto trimestre 2026) [2]; le ESA non pubblicano nel 2026 il rapporto annuale sui PAI [4].",
 "possibili": "Accordo SFDR 2.0 verso metà 2027 con prime segnalazioni nel 2029-2030; recepimento italiano dell'Omnibus I entro marzo 2027 [1][2].",
 "previsioni": [
  P("Bilancio di sostenibilità solo per i grandi gruppi", "Allentamento",
    "CSRD solo per imprese/gruppi UE con più di 1.000 dipendenti e oltre 450 milioni di fatturato; tetto alle informazioni richieste alla catena del valore.",
    "Recepimento entro 19 marzo 2027", "2027-03-19", "Alta", "Direttiva già pubblicata in Gazzetta UE.", [1, 3], [("Nuove soglie CSRD", ">1.000 dipendenti e >450 mln € di fatturato", 1)], ["Sostenibilità", "Commerciale e prodotti"]),
  P("Nuove categorie di prodotti sostenibili (SFDR 2.0)", "Nuovo obbligo",
    "Categorie di prodotto con criteri minimi, esclusioni sui combustibili fossili e indicatori obbligatori secondo il Consiglio; disclaimer obbligatorio per i prodotti non categorizzati.",
    "Accordo verso metà 2027, applicazione 2029", "2029-07-01", "Media", "Posizione del Consiglio fissata, Parlamento in ritardo.", [2], [("Prima segnalazione con i nuovi modelli", "30 giugno 2029 o 2030", 2)], ["Sostenibilità", "Compliance"]),
 ],
 "fonti": fe, "letture": [1, 2]})

# ---------------------------------------------------------------- 16 Assicurazioni
fis = [F("The new EU Insurance Recovery and Resolution Directive", "Clifford Chance", "2025-01", "https://publisher-prod65.cliffordchance.com/content/dam/cliffordchance/briefings/2025/01/the-new-eu-insurance-recovery-and-resolution-directive-january-2025.pdf", "Studio legale"),
       F("New rules for the insurance sector: recovery and resolution planning and changes to Solvency II", "Loyens & Loeff", "2025", "https://loyensloeff.com/insights/news--events/news/new-rules-for-the-insurance-sector-recovery-and-resolution-planning-and-changes-to-solvency-ii", "Studio legale"),
       F("Provisional agreement on the Retail Investment Strategy", "Loyens & Loeff", "2025-12", "https://www.loyensloeff.com/insights/news--events/news/provisional-agreement-on-the-retail-investment-strategy---what-fund-managers-need-to-know/", "Studio legale"),
       F("EU AI Omnibus enters into force, amending the AI Act", "White & Case", "2026-07", "https://www.whitecase.com/insight-alert/eu-ai-omnibus-enters-force-amending-ai-act", "Studio legale")]
S.append({"tema": "Assicurazioni e bancassicurazione", "iter": ["Retail Investment Strategy"],
 "visione": "Per la bancassicurazione il 2027 è l'anno chiave: entrano in applicazione la revisione di Solvency II e la nuova direttiva su risanamento e risoluzione delle assicurazioni (IRRD) [1][2], mentre la RIS cambia la distribuzione dei prodotti di investimento assicurativi [3].",
 "contesto": "La RIS modifica anche l'IDD: value for money e KID PRIIPs più semplice valgono per i prodotti assicurativi di investimento [3]. L'IA usata per prezzare polizze vita e salute diventa ad alto rischio dal dicembre 2027 [4].",
 "evoluzione": "Revisione Solvency II e IRRD pubblicate in Gazzetta a gennaio 2025, con applicazione dal 2027 [1][2].",
 "attuale": "Imprese e IVASS stanno preparando l'applicazione delle nuove regole; si attende il recepimento italiano [1][2].",
 "possibili": "Piani di risanamento preventivi per più compagnie, requisiti di capitale ricalibrati, regole RIS sulla vendita di prodotti assicurativi di investimento [1][2][3].",
 "previsioni": [
  P("Revisione di Solvency II e piani di risanamento (IRRD)", "Nuovo obbligo",
    "Requisiti di capitale ricalibrati e più proporzionalità per le compagnie piccole; piani di risanamento preventivi e poteri di risoluzione dell'IVASS.",
    "Gennaio 2027", "2027-01-30", "Alta", "Date fissate dalle direttive pubblicate a gennaio 2025.", [1, 2], [], ["Commerciale e prodotti", "Risk management"]),
  P("Value for money anche per i prodotti assicurativi di investimento", "Irrigidimento",
    "Le regole RIS su costi, benchmark e incentivi si applicano anche ai prodotti venduti in bancassicurazione.",
    "Circa fine 2028", "2028-12-31", "Alta", "Contenuto dell'accordo RIS.", [3], [], ["Compliance", "Commerciale e prodotti"]),
 ],
 "fonti": fis, "letture": [1, 2, 3]})

out = {"aggiornato": "2026-11-03", "schede": S}
p = Path(__file__).with_name("schede.json")
p.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
# controlli: ogni [n] e ogni fonte di previsione esiste
import re
err = []
for s in S:
    n = len(s["fonti"])
    for k in ("visione", "contesto", "evoluzione", "attuale", "possibili"):
        for m in re.findall(r"\[(\d+)\]", s[k]):
            if not 1 <= int(m) <= n:
                err.append((s["tema"], k, m))
    for pr in s["previsioni"]:
        for f in pr["fonti"] + [d["fonte"] for d in pr["dati"]]:
            if not 1 <= f <= n:
                err.append((s["tema"], pr["titolo"], f))
    for f in s["letture"]:
        if not 1 <= f <= n:
            err.append((s["tema"], "letture", f))
print(len(S), "schede", sum(len(s["previsioni"]) for s in S), "previsioni", sum(len(s["fonti"]) for s in S), "fonti", "errori:", err, len(json.dumps(out)), "byte")
