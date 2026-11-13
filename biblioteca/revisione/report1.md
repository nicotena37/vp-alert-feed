# Revisione indipendente chunk1 (17 norme) - report1

Norme riviste: tutte le 17 elencate in chunk1.json. Confronto articolo per articolo (perimetro `per`, ambito, processo) con il testo. Totale record in report1.json: 871 (di cui 49 BORDER con certezza bassa).
Nota di metodo: dato il volume (circa 1.500 articoli) i campi `per` sono stati verificati su ogni articolo; gli ambiti sono stati ricontrollati su titoli e testo (divergenze solo dove manca l'ambito); i processi seguono la mappatura ambito->processo e non si sono rilevate divergenze indipendenti, quindi non ci sono record di campo `processo`.

## Divergenze principali (n. record)

- IT-decreto.legislativo-2005-09-07-209 (Codice assicurazioni, 581 parti): 397 record. Il perimetro `assicurazione, banca` e assegnato a tutti gli articoli con ambito, ma banca e destinataria solo nella distribuzione assicurativa (artt. 107-121-septies, art. 109 c.2 lett. d). Proposto `assicurazione` per tutto il resto (solvibilita, governance, gruppi, liquidazione, RC auto, sanzioni). Articoli solo-autorita (203-bis, 205, 205-ter, 216-bis; 108-bis, 116-septies/decies, 121-quater) proposti con per vuoto (media/bassa). Cinque articoli senza ambito (106, 173, 175, 180, 181): BORDER.
- IVASS-cb4461f658 (Reg. 38/2018 governo societario): 96 record, `banca` da togliere (art. 3: solo imprese di assicurazione/riassicurazione; il testo non cita banche). Art. 66 (poteri IVASS): per vuoto.
- IVASS-a0b3bd2818 (Reg. ISVAP 21/2008): 67 record, stessa correzione (solo imprese di assicurazione).
- IVASS-f6eff6e4df (Reg. 45/2020 POG): 6 record, perimetro da ampliare a `banca` per il Capo III sui distributori (art. 14 esplicito sulle banche).
- CONSOB-15c17347b3 (Linee guida ESMA controlli interni): 78 record, `tutti` da svuotare: destinatari BMA, CRA, DRSP, repertori (nessun perimetro ammesso). Media.
- CONSOB-784dd884b2 (Reg. Mercati 20249): 99 record. (a) 12 articoli con `banca,sgr,sim` errato: sedi di negoziazione (12, 66), `banca,sim` (13, 14, 48-50, 72; SGR mai citata), mix sedi/banca/sim (68, 70, 71). (b) 45 articoli operativi dei gestori di sedi (3-11, 19-47, 60-bis, 61, 64, 67, 69) senza `per` e senza ambito: proposto `sedi` e ambito per analogia (A078/A080/A083/A053/A055), ambito con certezza media/bassa.
- UE-32020R1503 (Crowdfunding): 29 record, `banca,sgr,sim` da svuotare (destinatari i fornitori di servizi di crowdfunding; artt. 15, 17, 30, 39, 46 solo autorita/Stati/modifiche: alta).
- IT-decreto.legge-2020-04-08-23: 24 record. Misure fiscali/societarie/fallimentari generali (artt. 6-11, 18-24, 26, 28, 29-bis) con `banca` -> `tutti`; artt. 15-17 (poteri speciali/Consob) -> vuoto; art. 37-bis -> banca+intermediari; casi bassi: 4, 13, 13-ter, 14.
- UE-32013R0153 (RTS CCP): 63 record, tutti gli articoli rivolti alle CCP restano senza perimetro: proposto `ccp_csd` (alta). Nessun ambito assegnato: BORDER (A079, nota esplicita della scelta precedente).
- IT-decreto.legislativo-2025-03-10-23 (DORA): 8 record. Art. 6 -> `intermediari`, art. 7 -> `bancoposta`, art. 11 -> `sedi`, art. 12 -> `assicurazione`, art. 13 -> `fondi_pensione`, art. 14 -> `banca,sim`; BORDER art. 10 (multi-settore) e art. 15 (Bancoposta/NIS2).
- AGCM-488af56b0c (Reg. UE 2018/302 geoblocking): 4 record, artt. 3-6 destinati al "professionista": `banca` -> `tutti`.

## Senza divergenze
IVASS-22f87cfee4 (lettera DORA registro, solo assicurazione: corretto), UE-32024R1502, UE-32024R2956, EBA-8edbe0bc94 (`tutti`/vuoto coerenti con DORA e ESA), CONSOB-55ae317240 (aste quote di emissione: `tutti` accettabile, soggetti autorizzati ex art. 20-ter TUF).

## Casi dubbi (BORDER, certezza bassa)
- Codice assicurazioni: banca dovrebbe forse restare anche per artt. 182-187 (documentazione informativa distribuita anche da banche); ho tolto `banca` perche il testo parla di "imprese".
- Reg. Mercati: gli ambiti proposti per i 45 articoli senza ambito sono per analogia, da validare.
- Linee guida ESMA 15c17: i paragrafi di "Feedback statement" (consultazione) hanno ambito assegnato pur non essendo normativi; non toccati.
- Crowdfunding: se si volesse un perimetro, le banche/SIM sono soggetti solo se autorizzate come CSP.
