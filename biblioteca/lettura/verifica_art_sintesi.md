# Verifica indipendente classificazioni per ambito (campione di 100 parti)

## Conteggi per esito
Una riga puo' avere piu' esiti (es. SBAGLIATO + MANCANTE), quindi la somma supera 100.

| Esito | Righe |
|---|---|
| OK | 60 |
| MANCANTE | 15 |
| SBAGLIATO | 15 |
| NA_ERRATO | 7 |
| NON GIUDICABILE | 9 |

- Parti corrette (solo OK): **60/100 = 60%**.
- Sulle 91 parti giudicabili (esclusi i 9 casi di sola intestazione/indice): **60/91 = 66%**.
- Le 20 righe senza ambiti (etichette NA) sono quasi tutte corrette; gli errori si concentrano nelle righe con ambiti.

## I 5 errori piu' gravi
1. **CONSOB-25c3852612, Art. 18** (obblighi dei revisori legali): assegnato "Organizzazione e presidi antiriciclaggio", ma gli obblighi riguardano i revisori, non la banca. Andava senza ambiti ("Obblighi di altri soggetti").
2. **IT-decreto.legislativo-2005-09-07-209, art. 283** (Fondo vittime della strada): assegnato "Sistemi di garanzia" (ambito bancario) per un obbligo del Fondo CONSAP. Andava "Obblighi di altri soggetti".
3. **IT-decreto.legislativo-2005-09-07-209, art. 22** (sede secondaria in Stato terzo): assegnato "Succursali di paesi terzi", ma qui e' l'impresa italiana che apre all'estero. Mancano comunicazione all'Autorita e procedimento autorizzativo.
4. **UE-32016R0679, art. 83** (sanzioni GDPR): "Sanzioni amministrative e reati societari" non c'entra (diritto societario) e la norma disciplina il potere delle autorita, senza obblighi concreti per la banca.
5. **IT-decreto.legislativo-2005-12-05-252, art. 19** (compiti COVIP): classificato "Vigilanza" e "Fondi pensione" invece di "Obblighi di altri soggetti". Stesso problema per l'art. 311-ter del Codice delle assicurazioni (potere IVASS di ordinare di porre termine alle violazioni).

Altri casi rilevanti: art. 133 IVASS e art. 46-quaterdecies del Codice delle assicurazioni senza "Riserve tecniche e solvibilita assicurativa"; BDI par. 3 (polizza rischi operativi) con "Crowdfunding".

## Errori sistematici
1. **Ambiti attribuiti per parola chiave su titoli/voci di segnalazione BDI**: "Gestione dei rischi" (6 casi), "Investimenti" (3), "Partecipazioni", "Crowdfunding", "Gruppi e conglomerati" compaiono su sottovoci o titoli di voce senza alcun contenuto regolatorio. Per le istruzioni di compilazione della segnalazione basterebbe "Segnalazione all'autorita di vigilanza".
2. **Omissione di "Segnalazione all'autorita di vigilanza" sulle voci di segnalazione covered bond** (BDI Sezione II, 7 casi), mentre sulle altre voci BDI e' presente: incoerenza fra circolari.
3. **Norme su poteri/compiti di autorita e procedure (IVASS, COVIP, Garante, liquidazione coatta, Fondo CONSAP) classificate con ambiti invece che "Obblighi di altri soggetti"** (7 casi NA_ERRATO), spesso scegliendo "Sanzioni amministrative e reati societari", "Vigilanza" o "Sistemi di garanzia".
4. **Ambiti assicurativi non riconosciuti**: sulle norme IVASS/Codice assicurazioni a volte si usano ambiti bancari (Requisiti patrimoniali, Succursali di paesi terzi, Sistemi di garanzia) e si omette "Riserve tecniche e solvibilita assicurativa".
5. **Etichette NA mal applicate su intestazioni/indici** (9 casi): "Da rileggere" (non prevista), "Disposizioni finali" o "Ambito di applicazione" su solo titoli di articoli o sezioni. Testo troppo scarno per un giudizio; sarebbe meglio accorpare l'intestazione alla parte sostanziale.

## Note
- Il giudizio su testi di solo titolo (stub) si basa su tema e riferimenti normativi, non su obblighi leggibili.
- CONSOB par. 1.2.1 (valutazione interna dei rischi): giudicato OK; se fa parte di linee guida antiriciclaggio, mancherebbe "Organizzazione e presidi antiriciclaggio" (non verificabile dal solo testo).
- Dettaglio riga per riga: `verifica_art_output.jsonl`.
