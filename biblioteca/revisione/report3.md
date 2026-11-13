# Report revisione chunk3 (indipendente)

Norme riviste: 17 (tutte quelle di chunk3.json). Letti i testi (lettura/testi, testi/, testi_autorita/) e confrontati con ambiti_articoli.json. Nessun file esistente modificato.

Voci totali nel report: 358 (per: 349, ambito: 9, processo: 0). Casi BORDER/certezza bassa: 61.

## Divergenze per norma

- BDI-1a2064e6db: 131
- BDI-3b155c0457: 2
- CONSOB-66600a5332: 26
- IT-decreto.legislativo-2005-05-30-142: 5
- IT-decreto.legislativo-2005-12-05-252: 46
- IT-legge-2005-12-28-262: 22
- UE-32016R0679: 6
- UE-32017R0392: 93
- UE-32017R2358: 4
- UE-32022R2554: 9
- UE-32024R1774: 14

## Sintesi dei problemi principali

- UE-32017R0392 (RTS CSDR sui CSD): per attuale banca/sgr/sim su tutti gli articoli operativi; il destinatario e' il CSD -> ccp_csd (art. 92-93 anche banca, ente creditizio designato).
- IT-d.lgs. 252/2005 (previdenza complementare): per sgr -> fondi_pensione (con banca/assicurazione/sim/sgr per artt. 3, 6, 7, 12, 13; tutti per contributi datoriali; art. 19-quinquies solo COVIP).
- BDI-1a2064e6db (Circ. 286): per banca uniforme; per sezione cambia: BancoPosta (Sez. 4) -> bancoposta; Sez. 5 intermediari 106 -> intermediari; Sez. 6 IP/IMEL -> intermediari; Sez. 7 -> sgr; Sez. 9 e 11 -> banca/intermediari/sim. Un errore di ambito (parte 'Sezione II' #61 attribuita a Factoring).
- IT-legge 262/2005: per banca applicato a modifiche TUF/c.c. valide per societa' quotate e in generale -> tutti (media).
- UE-32016R0679 (GDPR): artt. 58, 60, 83, 87, 88 rivolti ad autorita'/Stati -> per vuoto.
- UE-32022R2554 (DORA): artt. 31, 42, 50 (ESA, fornitori critici, autorita') -> vuoto; artt. 59-63 (modifiche a CRA, EMIR, CSDR, MiFIR, BMR) per specifico o vuoto; art. 16 quadro semplificato non per enti creditizi.
- UE-32024R1774 artt. 28-41 (quadro semplificato): non banche -> sim/intermediari/fondi_pensione.
- IT-d.lgs. 142/2005 (FICOD): artt. 6, 16-18 rivolti alle autorita' -> vuoto; art. 19 solo assicurazione.
- CONSOB-66600a5332: destinatari revisori legali/societa' di revisione, non rientrano nei valori ammessi -> per vuoto (BORDER); le righe di indice 'Art. 6..17' duplicano le parti vere.
- BDI-3b155c0457 (POG): tutti -> banca, intermediari.
- UE-32017R2358 art. 2 per vuoto -> assicurazione (bassa); artt. 10-12 distributori: aggiungere banca (bassa).
- Norme senza divergenze rilevanti: UE-32024R1772, UE-32025R0532, IVASS-ee4a060251 (per assicurazione coerente; nota: la parte 'Art. 126' contiene anche gli artt. 127-128 sulla riassicurazione finite), IT-legge-2025-09-23-132, EIOPA-18340b1de7, EIOPA-3816d71f46 (pagine web/indici senza testo operativo).

## Casi dubbi (BORDER, certezza bassa)

- UE-32017R0392 art. 15 [ambito]: BORDER: riguarda "informazioni riservate" del CSD, non dati personali
- UE-32017R0392 art. 68 [ambito]: BORDER: RTS CSDR 2017, non DORA; "fornitori di utenze critiche e di servizi critici" = rischio operativo
- UE-32016R0679 art. 10 [ambito]: BORDER: art. su dati relativi a condanne penali e reati; il legame con adeguata verifica AML e' solo applicativo
- IT-decreto.legislativo-2005-12-05-252 art. 8 [per]: BORDER: contributi a carico di lavoratore/datore di lavoro, non soggetti vigilati specifici
- IT-decreto.legislativo-2005-12-05-252 art. 10 [per]: BORDER: "Il datore di lavoro e' esonerato dal versamento" - destinatari i datori di lavoro in generale
- IT-decreto.legislativo-2005-12-05-252 art. 16 [per]: BORDER: contributo di solidarieta' su somme a carico del datore di lavoro/lavoratore
- IT-legge-2005-12-28-262 art. 14 [per]: BORDER: modifiche TUF (albo promotori finanziari, intermediazione), non banche in senso stretto
- IT-legge-2005-12-28-262 art. 33 [per]: BORDER: reato di chi "fornisce dolosamente ad una banca notizie o dati falsi" (clienti), non obbligo della banca
- CONSOB-66600a5332 art. Art. 6 [per]: BORDER: destinatari sono "revisori legali e societa' di revisione", non banche/intermediari vigilati; nessun valore ammesso li comprende
- CONSOB-66600a5332 art. Art. 7 [per]: BORDER: destinatari sono "revisori legali e societa' di revisione", non banche/intermediari vigilati; nessun valore ammesso li comprende
- CONSOB-66600a5332 art. Art. 8 [per]: BORDER: destinatari sono "revisori legali e societa' di revisione", non banche/intermediari vigilati; nessun valore ammesso li comprende
- CONSOB-66600a5332 art. Art. 9 [per]: BORDER: destinatari sono "revisori legali e societa' di revisione", non banche/intermediari vigilati; nessun valore ammesso li comprende
- CONSOB-66600a5332 art. Art. 10 [per]: BORDER: destinatari sono "revisori legali e societa' di revisione", non banche/intermediari vigilati; nessun valore ammesso li comprende
- CONSOB-66600a5332 art. Art. 11 [per]: BORDER: destinatari sono "revisori legali e societa' di revisione", non banche/intermediari vigilati; nessun valore ammesso li comprende
- CONSOB-66600a5332 art. Art. 12 [per]: BORDER: destinatari sono "revisori legali e societa' di revisione", non banche/intermediari vigilati; nessun valore ammesso li comprende
- CONSOB-66600a5332 art. Art. 13 [per]: BORDER: destinatari sono "revisori legali e societa' di revisione", non banche/intermediari vigilati; nessun valore ammesso li comprende
- CONSOB-66600a5332 art. Art. 14 [per]: BORDER: destinatari sono "revisori legali e societa' di revisione", non banche/intermediari vigilati; nessun valore ammesso li comprende
- CONSOB-66600a5332 art. Art. 15 [per]: BORDER: destinatari sono "revisori legali e societa' di revisione", non banche/intermediari vigilati; nessun valore ammesso li comprende
- CONSOB-66600a5332 art. Art. 17 [per]: BORDER: destinatari sono "revisori legali e societa' di revisione", non banche/intermediari vigilati; nessun valore ammesso li comprende
- CONSOB-66600a5332 art. Art. 5 [per]: BORDER: destinatari sono "revisori legali e societa' di revisione", non banche/intermediari vigilati; nessun valore ammesso li comprende
- CONSOB-66600a5332 art. Art. 6 (2) [per]: BORDER: destinatari sono "revisori legali e societa' di revisione", non banche/intermediari vigilati; nessun valore ammesso li comprende
- CONSOB-66600a5332 art. Art. 7 (2) [per]: BORDER: destinatari sono "revisori legali e societa' di revisione", non banche/intermediari vigilati; nessun valore ammesso li comprende
- CONSOB-66600a5332 art. Art. 8 (2) [per]: BORDER: destinatari sono "revisori legali e societa' di revisione", non banche/intermediari vigilati; nessun valore ammesso li comprende
- CONSOB-66600a5332 art. Art. 9 (2) [per]: BORDER: destinatari sono "revisori legali e societa' di revisione", non banche/intermediari vigilati; nessun valore ammesso li comprende
- CONSOB-66600a5332 art. Art. 10 (2) [per]: BORDER: destinatari sono "revisori legali e societa' di revisione", non banche/intermediari vigilati; nessun valore ammesso li comprende
- CONSOB-66600a5332 art. Art. 11 (2) [per]: BORDER: destinatari sono "revisori legali e societa' di revisione", non banche/intermediari vigilati; nessun valore ammesso li comprende
- CONSOB-66600a5332 art. Art. 12 (2) [per]: BORDER: destinatari sono "revisori legali e societa' di revisione", non banche/intermediari vigilati; nessun valore ammesso li comprende
- CONSOB-66600a5332 art. Art. 13 (2) [per]: BORDER: destinatari sono "revisori legali e societa' di revisione", non banche/intermediari vigilati; nessun valore ammesso li comprende
- CONSOB-66600a5332 art. Art. 14 (2) [per]: BORDER: destinatari sono "revisori legali e societa' di revisione", non banche/intermediari vigilati; nessun valore ammesso li comprende
- CONSOB-66600a5332 art. Art. 15 (2) [per]: BORDER: destinatari sono "revisori legali e societa' di revisione", non banche/intermediari vigilati; nessun valore ammesso li comprende
- CONSOB-66600a5332 art. Art. 16 [per]: BORDER: destinatari sono "revisori legali e societa' di revisione", non banche/intermediari vigilati; nessun valore ammesso li comprende
- CONSOB-66600a5332 art. Art. 17 (2) [per]: BORDER: destinatari sono "revisori legali e societa' di revisione", non banche/intermediari vigilati; nessun valore ammesso li comprende
- CONSOB-66600a5332 art. Art. 18 [per]: BORDER: destinatari sono "revisori legali e societa' di revisione", non banche/intermediari vigilati; nessun valore ammesso li comprende
- BDI-1a2064e6db art. Sezione II - par. 1.2 (5) [#154] [per]: BORDER: Sezione 8 "fornitori specializzati di servizi di crowdfunding per imprese"; nessun valore esatto
- BDI-1a2064e6db art. Sezione II - par. 1.3 (4) [#155] [per]: BORDER: Sezione 8 "fornitori specializzati di servizi di crowdfunding per imprese"; nessun valore esatto
- BDI-1a2064e6db art. Sezione II - par. 1.4 (2) [#156] [per]: BORDER: Sezione 8 "fornitori specializzati di servizi di crowdfunding per imprese"; nessun valore esatto
- BDI-1a2064e6db art. Sezione II - par. 2 (7) [#157] [per]: BORDER: Sezione 8 "fornitori specializzati di servizi di crowdfunding per imprese"; nessun valore esatto
- BDI-1a2064e6db art. Sezione II - par. 2.1 (2) [#158] [per]: BORDER: Sezione 8 "fornitori specializzati di servizi di crowdfunding per imprese"; nessun valore esatto
- BDI-1a2064e6db art. Sezione II - par. 3 (6) [#159] [per]: BORDER: Sezione 8 "fornitori specializzati di servizi di crowdfunding per imprese"; nessun valore esatto
- BDI-1a2064e6db art. Sezione II - par. 3.1 [#160] [per]: BORDER: Sezione 8 "fornitori specializzati di servizi di crowdfunding per imprese"; nessun valore esatto
- BDI-1a2064e6db art. Sezione II - par. 3.2 [#161] [per]: BORDER: Sezione 8 "fornitori specializzati di servizi di crowdfunding per imprese"; nessun valore esatto
- BDI-1a2064e6db art. Sezione II - par. 3.3 [#162] [per]: BORDER: Sezione 8 "fornitori specializzati di servizi di crowdfunding per imprese"; nessun valore esatto
- BDI-1a2064e6db art. Sezione II - par. 4 (4) [#163] [per]: BORDER: Sezione 8 "fornitori specializzati di servizi di crowdfunding per imprese"; nessun valore esatto
- BDI-1a2064e6db art. Sezione II - par. 1 (7) [#164] [per]: BORDER: Sezione 8 "fornitori specializzati di servizi di crowdfunding per imprese"; nessun valore esatto
- BDI-1a2064e6db art. Sezione II - par. 2 (8) [#165] [per]: BORDER: Sezione 8 "fornitori specializzati di servizi di crowdfunding per imprese"; nessun valore esatto
- BDI-1a2064e6db art. Sezione II - par. 2.1 (3) [#166] [per]: BORDER: Sezione 8 "fornitori specializzati di servizi di crowdfunding per imprese"; nessun valore esatto
- BDI-1a2064e6db art. Sezione II - par. 2.2 [#167] [per]: BORDER: Sezione 8 "fornitori specializzati di servizi di crowdfunding per imprese"; nessun valore esatto
- BDI-1a2064e6db art. Sezione II - par. 2.3 [#168] [per]: BORDER: Sezione 8 "fornitori specializzati di servizi di crowdfunding per imprese"; nessun valore esatto
- BDI-1a2064e6db art. Sezione II - par. 3 (7) [#169] [per]: BORDER: Sezione 8 "fornitori specializzati di servizi di crowdfunding per imprese"; nessun valore esatto
- BDI-1a2064e6db art. Sezione II - par. 3.1 (2) [#170] [per]: BORDER: Sezione 8 "fornitori specializzati di servizi di crowdfunding per imprese"; nessun valore esatto
- BDI-1a2064e6db art. Sezione II - par. 3.2 (2) [#171] [per]: BORDER: Sezione 8 "fornitori specializzati di servizi di crowdfunding per imprese"; nessun valore esatto
- BDI-1a2064e6db art. Sezione II - par. 3.3 (2) [#172] [per]: BORDER: Sezione 8 "fornitori specializzati di servizi di crowdfunding per imprese"; nessun valore esatto
- BDI-1a2064e6db art. Sezione II - par. 4 (5) [#173] [per]: BORDER: Sezione 8 "fornitori specializzati di servizi di crowdfunding per imprese"; nessun valore esatto
- BDI-1a2064e6db art. Sezione II - par. 1.1 (2) [#80] [ambito]: BORDER: "Attivita' fiscali differite" come voce dei fondi propri, non materia fiscale
- BDI-1a2064e6db art. Sezione II - par. 1.2 (2) [#81] [ambito]: BORDER: "Attivita' fiscali differite" come voce dei fondi propri, non materia fiscale
- BDI-1a2064e6db art. Sezione II - par. 1.3 [#82] [ambito]: BORDER: "Attivita' fiscali differite" come voce dei fondi propri, non materia fiscale
- BDI-1a2064e6db art. Sezione II - par. 2.1 [#114] [ambito]: BORDER: "Attivita' fiscali differite" come voce dei fondi propri, non materia fiscale
- UE-32017R2358 art. 2 [per]: Articolo che individua i destinatari: "si applica alle imprese di assicurazione e agli intermediari assicurativi"
- UE-32017R2358 art. 10 [per]: BORDER: obblighi dei "distributori di prodotti assicurativi", tra cui le banche che distribuiscono polizze
- UE-32017R2358 art. 11 [per]: BORDER: obblighi dei "distributori di prodotti assicurativi", tra cui le banche che distribuiscono polizze
- UE-32017R2358 art. 12 [per]: BORDER: obblighi dei "distributori di prodotti assicurativi", tra cui le banche che distribuiscono polizze

Limiti: ambiti e processi sono stati controllati per coerenza generale (non articolo per articolo su ogni codice processo); le divergenze si concentrano sul perimetro.