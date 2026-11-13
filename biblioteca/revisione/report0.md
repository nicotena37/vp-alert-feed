# Revisione indipendente chunk0 - report

Norme riviste: 18 (tutte quelle di chunk0.json). Articoli complessivi esaminati: circa 1.720 (BDI-bf7944b2b0 502, BDI-7b2991ba7f 254, IVASS-f4c0570fe5 128, UE-32017R0565 96, CONSOB-4ed95447f9 69, IT-DLGS-2010-11 64, UE-DIR-2014-17 55, EBA-f0d621a5b3 43, IT-DL-2016-237 32, GPDP-cfa4e536d1 34, UE-32017R0584 25, UE-32017L0593 15, UE-32022L2556 11, UE-32024R1773 11, EBA-c77302e20a 21, UE-32025R0301 7, EIOPA 3+2).
Divergenze/casi dubbi riportati: 791 voci in report0.json (772 su `per`, 19 su `ambito`, nessuna su `processo`). Certezza alta: 640; media: 123; bassa: 28 (valori indicativi) (casi BORDER).

Metodo: il perimetro e stato riletto dal testo (destinatari/ambito di applicazione e soggetto grammaticale degli obblighi). Ambito e processi sono stati controllati a campione/per coerenza con la rubrica e il testo: nessuna divergenza sistematica trovata, salvo i casi sotto. Per le norme molto grandi (BDI-bf7944b2b0, BDI-7b2991ba7f) la verifica dell'ambito e per gruppi omogenei, non voce per voce.

## Divergenze principali (per)
- BDI-bf7944b2b0 (Circ. 148 Banca d'Italia, segnalazioni SIM): attuale banca+sgr+sim, proposto `sim`. L'art. «Destinatari» dice «si applicano alle SIM ... e ai gruppi di SIM»; l'art. Destinatari stesso ha per vuoto (proposto `sim`). 492 voci, alta.
- BDI-7b2991ba7f (Regolamento vigilanza SIM): attuale banca+sim, proposto `sim` (destinatari: SIM classe 1-minus/2/3, succursali paesi terzi, imprese di investimento UE). 114 voci alta + 23 frammenti con per vuoto e testo sostanziale (media).
- UE-32017R0584 (RTS 7 algoritmi): obblighi tutti in capo alle «sedi di negoziazione»: attuale banca+sgr+sim, proposto `sedi` (23 alta).
- UE-32022L2556 (direttiva DORA di modifica): art. 1-8 attuale `tutti`, proposto per settore modificato (OICVM->sgr, Solvency II->assicurazione, AIFMD->sgr, CRD->banca, BRRD->banca+sim, MiFID II->sim+banca+sedi, PSD2->banca+intermediari, IORP II->fondi_pensione).
- CONSOB-4ed95447f9 (Delibera 20197): attuale solo `banca`; destinatari sono SIM, banche, SGR, SICAV/SICAF, imprese di assicurazione (distribuzione prodotti finanziari assicurativi). 63 voci, media (assegnazione per gruppi di articoli: schemi intermediari, schemi imprese assicurative, flussi fondi).
- EBA-f0d621a5b3 (POG prodotti bancari retail): attuale `tutti`, proposto banca+intermediari (CRD, PSD, EMD, MCD, CCD); par. 6 (scopo) con per vuoto. 21 voci media.
- UE-32017R0565: art. 1 e 30 senza per (-> banca/sim/sgr); art. 78-83, 90 e All. III rivolti ai gestori di sedi di negoziazione (-> `sedi`); art. 12-16 internalizzatori sistematici (bassa).
- UE-DIR-2014-17 (MCD): art. 29-32 e 35 riguardano intermediari del credito/enti non creditizi, non banche (proposto `intermediari`, media).
- IVASS-f4c0570fe5: art. 3 (ambito di applicazione) senza per -> `assicurazione` (alta).
- UE-32017L0593: art. 1 senza per.
- IT-DLGS-2010-11: art. 2 senza per; art. 33 istituti di pagamento (bassa).

## Casi BORDER / dubbi
- Se `intermediari` indichi anche istituti di pagamento/IMEL e intermediari del credito (D.Lgs. 11/2010, MCD, EBA POG): assunto di si, da confermare.
- UE-32017R0565 art. 78-83, 90, All. III: ambito vuoto per scelta («Obblighi di altri soggetti»); proposto A076 solo come dubbio (bassa). Art. 12-20: ambito A080 (bassa).
- IVASS: art. 3 senza ambito antiriciclaggio; art. 58 transitoria (bassa).
- IT-DL 2016/237 art. 11 (per vuoto, escussione garanzia su banca).
- GPDP-cfa4e536d1, EBA-c77302e20a (solo autorita ESA/CA, per vuoto corretto), UE-32024R1773, UE-32025R0301 (DORA, `tutti`), EIOPA-00dd5da7ca/EIOPA-cca79f5445 (pagine web senza testo operativo): nessuna divergenza.
- Molti frammenti di estrazione PDF (titoli, indici) con ambito/per vuoti sono stati lasciati invariati.

File: /home/claude/vp-alert-feed/biblioteca/revisione/report0.json (lista di oggetti norma, articolo, campo, attuale, proposto, motivo, certezza). Nessun file esistente modificato.
