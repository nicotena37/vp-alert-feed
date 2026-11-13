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
