# VP Alert - lettura dei feed RSS

Questo archivio legge i feed RSS degli enti (e le pagine Consob) **dai server di GitHub**, così il giro del VP Alert
non dipende dal PC né dal browser.

- `fonti_rss.json` – elenco dei siti e dei feed (copia di quello in `_automazione`).
- `leggi_feed.py` – programma di lettura. Rispetta il robots.txt dei siti, si presenta con un nome chiaro e fa
  una richiesta ogni 3 secondi per sito.
- `dati/` – un file per sito con le notizie lette, nello stesso formato del browser (`vpalert_rss_...`);
  `dati/stato.json` riassume quali feed hanno funzionato.

**Quando gira:** ogni giorno feriale alle 06:17, oppure a mano (scheda *Actions* → *Leggi feed VP Alert* →
*Run workflow*), oppure quando Claude modifica `avvia.txt` prima di un giro.
