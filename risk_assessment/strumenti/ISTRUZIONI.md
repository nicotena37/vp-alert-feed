# Istruzioni: creare gli adempimenti da parti di testo normativo (livello "elementi puntuali")

Contesto: risk assessment di una banca (con attività assicurativa) sul tema DORA. Leggi per intero il file di testo che ti è assegnato: ogni parte inizia con `[numero] rubrica`. Per ogni parte crea UNO O PIÙ adempimenti (livello puntuali: ogni comportamento richiesto distinto = un adempimento; una parte può darne più d'uno; una parte senza obbligo concreto per i soggetti vigilati non dà adempimenti: saltala).

Regole
- Solo obblighi, divieti o adempimenti concreti. Niente definizioni, ambito di applicazione, entrata in vigore, considerando.
- SOLO adempimenti delle BANCHE (enti creditizi e loro gruppi). NON creare adempimenti per: autorità, Stati membri, ESA, Commissione; fornitori TIC (i loro obblighi verso la banca diventano adempimenti della banca solo se la banca deve imporli o verificarli); depositari/CCP; intermediari finanziari (art. 106 TUB), Bancoposta, SIM/SGR, istituti di pagamento e di moneta elettronica, sedi di negoziazione, imprese di assicurazione, fondi pensione. Se una norma contiene solo obblighi di questi soggetti (es. lettere IVASS) non ha adempimenti per la banca: archiviala in `biblioteca/senza_adempimenti.json`, mai cancellarla. Gli obblighi generici di tutte le entità finanziarie DORA (che includono le banche) restano. `sogg` = "banca" sempre.
- NOTE: ignora le note ("Note all'art." delle leggi, note a piè di pagina dei PDF): non creano adempimenti e non vanno citate. Prima di leggere una parte togli le note con `risk_assessment/strumenti/pulisci.py`.
- Livelli alti (prescrizioni, obblighi, pilastri): gli adempimenti sono raggruppamenti e le descrizioni possono essere lunghe; elenca in `fonti` tutte le parti di testo da cui derivano (norma, art, comma, cit).
- `titolo`: frase breve che inizia con un verbo all'infinito (es. "Mantenere il registro degli accordi TIC").
- `desc`: 1-2 frasi in italiano, chiare, senza copiare tutto il testo.
- `dest`: a chi si rivolge (es. "banca", "impresa di assicurazione", "fornitore terzo TIC", "autorità").
- `termine`: scadenza o periodicità se il testo la indica, altrimenti "".
- `natura`: "obbligatorio" | "divieto" | "facoltativo".
- `cit`: citazione LETTERALE, copiata identica dal testo (massimo 200 caratteri, una sola frase o frammento continuo) che fonda l'adempimento. Non modificarla, non tradurla.
- `comma`: numero del paragrafo/comma se chiaro, altrimenti "".
- `f`: nove punteggi interi da 1 a 4 (1 = basso, 4 = alto) su: sanz (sanzionatorio), rep (reputazionale), oper (operativo), econ (economico e di rimedio), compl (complessità), freq (frequenza e volumi), nov (novità della norma: 4 = nuova o in arrivo, 3 = nell'ultimo anno), ctrl (esiti controlli passati: se non hai informazioni usa 2), att (attenzione dell'autorità: se non hai informazioni usa 2). Usa tutta la scala con buon senso, non mettere tutti uguali.
- `sanz_txt`: sanzioni applicabili. Leggi /home/claude/ra_el/SANZIONI.txt (estratto dell'art. 10 d.lgs. 23/2025: sanzioni amministrative italiane per inosservanza di articoli del Reg. UE 2022/2554 e delle relative norme tecniche). Se l'articolo del regolamento cui l'adempimento si riferisce (o il suo RTS/ITS) è richiamato in quell'estratto, riporta importi e categoria di soggetti (es. "banche e intermediari: da 30.000 € fino al 10% del fatturato"). Per le norme tecniche di attuazione/regolamentazione indica il regolamento base violato. Se non è richiamato, scrivi "Non indicate direttamente dalla norma; vigilanza e misure ai sensi del d.lgs. 23/2025." Non inventare importi.
- `S`: sanzione massima in euro come numero se ricavabile (es. 5000000 per "fino a 5 milioni"; con percentuale di fatturato e senza importo fisso: 0), altrimenti 0.

Output: scrivi con Write un file JSON (solo JSON valido, nessun testo attorno) in /home/claude/ra_el/out/<NOME>.json, dove <NOME> è il nome del file di input senza ".txt". Struttura: una lista di oggetti con i campi: norma, art, comma, titolo, desc, dest, termine, natura, sogg, cit, f (oggetto con le 9 chiavi), sanz_txt, S. `norma` = l'identificativo indicato nel prompt; `art` = il numero tra parentesi quadre della parte (stringa, identico).
Usa solo gli strumenti Read e Write (vietati Bash, mcp__*, send_later, trigger). Rispondi alla fine solo: "fatto, N adempimenti".

## Perimetri (campo `per`) — regole per le norme future
Ogni adempimento ha il campo `per`: lista di perimetri a cui si applica. Valori: `tutti` (obbligo trasversale di tutte le entità finanziarie, es. DORA), `banca`, `assicurazione`, `sim`, `sgr`, `intermediari` (art. 106 TUB), `bancoposta`, `sedi` (sedi di negoziazione), `fondi_pensione`, `ccp_csd`.
- Chi estrae gli adempimenti DEVE compilare `per`. Se manca, `build.py` lo deduce: atti UE DORA, d.lgs. 23/2025 ed EBA = `tutti`; testi con "ente creditizio / G-SII / O-SII / TUB" = `banca`; ogni altra norma = `banca` (prudente).
- Mai nel risk assessment, in nessun perimetro: adempimenti di autorità, Stati membri, ESA, Commissione e di QUALSIASI fornitore (non solo TIC: outsourcer, prestatori di servizi, terzi). Contano solo gli obblighi delle società dei perimetri; un obbligo della banca di verificare, imporre o controllare il fornitore resta un adempimento della banca (campo `dest` = banca). `build.py` esclude in automatico gli adempimenti il cui destinatario è un fornitore (restano solo nella lista `esclusi_ids.json`, tabella MAI di build.py).
- Gli adempimenti di altri perimetri non si cancellano mai: restano nei dati e la pagina li nasconde per perimetro. Un adempimento di soggetto diverso dal perimetro scelto non si vede.
- Controllo obbligatorio dopo ogni estrazione: `build.py` stampa "DA VERIFICARE" (testo con termini bancari classificato `tutti`) e il conteggio per perimetro. Rileggere a mano questi casi prima di pubblicare, in particolare prima di dare `per` specifico a un obbligo che potrebbe valere per tutti.
- I livelli aggregati (prescrizioni, obblighi, pilastri) si generano per ogni perimetro al momento della richiesta della RA: `build.py` produce `data/prescrizioni_<perimetro>.json` con i gruppi a mano ricalcolati sui soli adempimenti visibili per quel perimetro (trasversali + propri) e, per gli adempimenti propri non coperti, un gruppo per norma. I testi dei gruppi sono scritti per le banche e per gli altri perimetri 'banca' diventa 'entità'. Quando l'utente invia la richiesta copiare il file del suo perimetro in `data/adem_<id>.json`.
- Per un nuovo perimetro (SIM, SGR, assicurazioni…) serve una nuova estrazione delle norme specifiche; poi si assegna `per` e si rigenerano i gruppi per quel perimetro.

## Report di copertura per perimetro
`risk_assessment/copertura/` contiene `copertura.py` (calcolo: stato di ogni norma, perimetro stimato, adempimenti) e `xlsx.py` (crea `copertura_perimetri.xlsx`: Riepilogo, Per ambito, Adempimenti per norma, Norme, Da fare, Buchi noti). Rigenerarlo dopo ogni estrazione o attribuzione: `python3 copertura.py --scrivi-per` solo se si vuole riscrivere il campo `per` in `ambiti_articoli.json` (backup automatico `ambiti_articoli.bak_prima_perimetro.json`), poi `python3 xlsx.py`. Il perimetro delle norme è una stima da correggere man mano.

## Precisazione: "assicurazioni e IA sempre inclusi" vale SOLO per il VP Alert
Nel risk assessment non c'è nessuna inclusione automatica: assicurazioni e IA entrano solo se l'ambito soggettivo dell'articolo li riguarda, e il perimetro scelto decide cosa si vede. Nel dubbio: BORDER, analisi in più sul testo, decisione motivata per iscritto.

## Regole fissate dall'utente (13/11/2026)
- **xlsx di copertura**: si rigenera SOLO quando l'utente lo chiede.
- **Attribuzione del perimetro = parte dell'attribuzione**: quando si attribuiscono tematica, ambito e processo a una norma/articolo, si attribuisce nello stesso passaggio anche il perimetro (`per`), leggendo l'ambito soggettivo nel testo. Le regole automatiche (parole come "enti creditizi", TUB, G-SII/O-SII) servono solo come prima stima, mai come decisione.
- **Revisione indipendente obbligatoria per ogni ambito nuovo**: dopo l'attribuzione, un secondo revisore (subagente che non ha visto il lavoro) rilegge il testo dell'articolo e ricontrolla tematica/ambito/processo e `per`. Le divergenze si risolvono rileggendo il testo; il motivo si scrive in `per_stato`. Solo dopo l'adempimento entra nei dati.
- Così la copertura cresce ambito per ambito, con `per` già verificato.

## Perimetro `intermediari` (decisione 14/11/2026)
`intermediari` = SOLO intermediari finanziari art. 106 TUB. Non esistono perimetri per istituti di pagamento, IMEL o intermediari del credito (mediatori, agenti): se un articolo si rivolge solo a loro, `per` resta vuoto e non genera adempimenti. Nelle proposte dei revisori, `intermediari` generico va riletto: tenerlo solo se il testo parla di intermediari art. 106 TUB.

## Livelli per percentuale (14/11/2026)
I livelli si definiscono sul totale degli adempimenti puntuali del perimetro (100%), non più per numero di elementi raggruppati:
- puntuali 100%; prescrizioni 25–50% (oggi ~31%: gruppi di 2–5 puntuali, stessa norma e stesso articolo, spezzati se più di 5); obblighi 10–25% (oggi ~12%: i gruppi a mano di `gruppi.py`); pilastri 1–10% (oggi ~1,5%: le aree macro).
- Gerarchia: ogni prescrizione sta in un solo obbligo, ogni obbligo in un solo pilastro. In ogni livello `fonti` elenca i puntuali sottostanti.
- Le percentuali si scelgono in base a quanto si possono agglomerare e alla coerenza degli adempimenti; per norme future si rispettano gli stessi intervalli.
- `build.py` produce `data/prescrizioni_<p>.json`, `obblighi_<p>.json`, `pilastri_<p>.json` per ogni perimetro. I titoli delle prescrizioni sono ricavati dal puntuale principale ("… e obblighi connessi"): da rivedere a mano.
