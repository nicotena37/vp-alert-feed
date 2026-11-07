"""Catalogo della legal inventory (compliAInce Dynamic): interroga le banche dati ufficiali e salva in dati/catalogo/.
Modo letto da catalogo/avvia.txt (prima parola): prova | ue | it | tutto."""
import json, sys, time, re
from pathlib import Path
import requests

OUT = Path("dati/catalogo"); OUT.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "compliaince-catalogo/1.0 (legal inventory; contatto via GitHub)"}
SPARQL = "https://publications.europa.eu/webapi/rdf/sparql"
NA = "https://api.normattiva.it/t/normattiva.api/bff-opendata/v1/api/v1"
LOG = []

def log(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); LOG.append(s)

def sparql(q, nome=None):
    for t in range(3):
        try:
            r = requests.post(SPARQL, data={"query": q, "format": "application/sparql-results+json"}, headers=UA, timeout=300)
            r.raise_for_status()
            b = r.json()["results"]["bindings"]
            rows = [{k: v["value"] for k, v in x.items()} for x in b]
            if nome: (OUT / f"{nome}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=0), encoding="utf-8")
            log(f"SPARQL {nome}: {len(rows)} righe"); return rows
        except Exception as e:
            log(f"SPARQL {nome} tentativo {t+1}: {e}"); time.sleep(10)
    return []

def na(metodo, path, body=None, nome=None):
    try:
        h = {**UA, "Accept": "application/json", "Content-Type": "application/json", "Origin": "https://dati.normattiva.it"}
        r = requests.request(metodo, NA + path, json=body, headers=h, timeout=120)
        log(f"NORMATTIVA {metodo} {path}: HTTP {r.status_code}, {len(r.content)} byte")
        try: d = r.json()
        except Exception: d = {"testo": r.text[:3000]}
        if nome: (OUT / f"{nome}.json").write_text(json.dumps(d, ensure_ascii=False, indent=0)[:3_000_000], encoding="utf-8")
        return d
    except Exception as e:
        log(f"NORMATTIVA {path}: {e}"); return None

PFX = """PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""

def prova():
    # 1. repertorio della legislazione in vigore: codici e conteggi
    sparql(PFX + """SELECT ?dc (SAMPLE(?lab) AS ?label) (COUNT(DISTINCT ?w) AS ?n) WHERE {
      ?w cdm:resource_legal_in-force "true"^^xsd:boolean ; cdm:resource_legal_is_about_concept_directory-code ?dc .
      OPTIONAL { ?dc skos:prefLabel ?lab FILTER(lang(?lab)="it") } } GROUP BY ?dc ORDER BY ?dc""", "prova_repertorio")
    # 2. atti BCE in vigore
    sparql(PFX + """SELECT DISTINCT ?celex ?tipo ?data ?tit WHERE {
      ?w cdm:resource_legal_id_celex ?celex ; cdm:resource_legal_in-force "true"^^xsd:boolean ;
         cdm:work_created_by_agent <http://publications.europa.eu/resource/authority/corporate-body/ECB> ;
         cdm:work_has_resource-type ?tipo . OPTIONAL { ?w cdm:work_date_document ?data }
      OPTIONAL { ?e cdm:expression_belongs_to_work ?w ; cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ITA> ; cdm:expression_title ?tit } }""", "prova_bce")
    # 3. Normattiva
    na("GET", "/tipologiche/denominazione-atto", nome="prova_na_denominazioni")
    na("GET", "/tipologiche/classe-provvedimento", nome="prova_na_classi")
    na("GET", "/collections/collection-predefinite", nome="prova_na_collezioni")
    na("POST", "/ricerca/avanzata", {"titoloRicerca": "testo unico bancario", "orderType": "recente",
        "paginazione": {"paginaCorrente": 1, "numeroElementiPerPagina": 10}}, nome="prova_na_ricerca")
    na("POST", "/atto/dettaglio-atto-urn", {"urn": "urn:nir:stato:decreto.legislativo:1993-09-01;385~art1"}, nome="prova_na_dettaglio")


# ------------------------------------------------------------------ UE e BCE
CORE = ["06202020", "06202025", "06202010", "062020", "06202080", "0610", "1020", "102010", "102020", "102030", "1040",
        "014075", "014095", "1007", "0950", "092030", "152040", "152010", "1710", "173010", "173020"]
FILTRATI = ["093010", "05202010", "05202020", "05203020", "05200510", "05200520", "132060", "1920", "193020", "103030", "151010", "0810", "0820", "082010", "0830"]
TIPI_OK = ("REG", "REG_DEL", "REG_IMPL", "DIR", "DIR_DEL", "DIR_IMPL", "DEC", "DEC_DEL", "DEC_IMPL", "GUIDELINE", "RECO", "REG_FINANC")

def q_codici(codici, nome):
    vals = " ".join(f"<http://publications.europa.eu/resource/authority/dir-eu-legal-act/{c}>" for c in codici)
    q = PFX + f"""SELECT ?celex (SAMPLE(?tp) AS ?tipo) (SAMPLE(?d) AS ?data) (SAMPLE(?t) AS ?tit) (GROUP_CONCAT(DISTINCT STRAFTER(STR(?dc),"dir-eu-legal-act/");separator=" ") AS ?codici)
      (GROUP_CONCAT(DISTINCT STRAFTER(STR(?au),"corporate-body/");separator=" ") AS ?autori) WHERE {{
      VALUES ?dc {{ {vals} }}
      ?w cdm:resource_legal_is_about_concept_directory-code ?dc ; cdm:resource_legal_in-force "true"^^xsd:boolean ;
         cdm:resource_legal_id_celex ?celex ; cdm:work_has_resource-type ?tp .
      FILTER(STRSTARTS(?celex,"3"))
      OPTIONAL {{ ?w cdm:work_date_document ?d }}
      OPTIONAL {{ ?w cdm:work_created_by_agent ?au }}
      OPTIONAL {{ ?e cdm:expression_belongs_to_work ?w ; cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ITA> ; cdm:expression_title ?t }}
    }} GROUP BY ?celex"""
    return sparql(q, nome)

def q_celex(lista, nome):
    vals = " ".join(f'"{c}"^^xsd:string' for c in lista)
    q = PFX + f"""SELECT ?celex (SAMPLE(?tp) AS ?tipo) (SAMPLE(?d) AS ?data) (SAMPLE(?t) AS ?tit) (SAMPLE(?f) AS ?vigore) WHERE {{
      VALUES ?celex {{ {vals} }} ?w cdm:resource_legal_id_celex ?celex ; cdm:work_has_resource-type ?tp .
      OPTIONAL {{ ?w cdm:resource_legal_in-force ?f }} OPTIONAL {{ ?w cdm:work_date_document ?d }}
      OPTIONAL {{ ?e cdm:expression_belongs_to_work ?w ; cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ITA> ; cdm:expression_title ?t }}
    }} GROUP BY ?celex"""
    return sparql(q, nome)

def q_basati(base, nome):
    vals = " ".join(f'"{c}"^^xsd:string' for c in base)
    q = PFX + f"""SELECT DISTINCT ?celex ?base ?tipo ?data ?tit WHERE {{
      VALUES ?base {{ {vals} }} ?b cdm:resource_legal_id_celex ?base .
      ?w cdm:resource_legal_based_on_resource_legal ?b ; cdm:resource_legal_in-force "true"^^xsd:boolean ; cdm:resource_legal_id_celex ?celex ; cdm:work_has_resource-type ?tipo .
      OPTIONAL {{ ?w cdm:work_date_document ?data }}
      OPTIONAL {{ ?e cdm:expression_belongs_to_work ?w ; cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ITA> ; cdm:expression_title ?tit }} }}"""
    return sparql(q, nome)

def q_sanzioni(nome):
    q = PFX + """SELECT DISTINCT ?celex ?tipo ?data ?tit WHERE {
      ?w cdm:resource_legal_in-force "true"^^xsd:boolean ; cdm:resource_legal_id_celex ?celex ; cdm:work_has_resource-type ?tipo .
      FILTER(STRSTARTS(?celex,"3"))
      ?e cdm:expression_belongs_to_work ?w ; cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ITA> ; cdm:expression_title ?tit .
      FILTER(CONTAINS(LCASE(?tit),"misure restrittive")) OPTIONAL { ?w cdm:work_date_document ?data } }"""
    return sparql(q, nome)

# atti base da cui ricavare tutti gli atti delegati e di esecuzione (FAMIGLIE)
BASI = ["32013R0575", "32013L0036", "32014L0059", "32014R0806", "32014L0065", "32014R0600", "32014R0596", "32012R0648",
        "32014R0909", "32014R1286", "32015L2366", "32022R2554", "32023R1114", "32016R1011", "32019R2088", "32020R0852",
        "32022L2464", "32017R2402", "32015L0849", "32024R1624", "32024L1640", "32024R1620", "32016L0097", "32009L0065",
        "32011L0061", "32017R1129", "32015R2365", "32012R0236", "32016R0679", "32024R1689", "32022L2555", "32014L0017",
        "32008L0048", "32023L2225", "32014L0092", "32012R0260", "32014L0049", "32009L0110", "32017R1131", "32015R0760"]
INCLUDI = ["32016R0679", "32024R1689", "32022L2555", "32022L2556", "32024R2847", "32023R2854", "32014R0910", "32024R1183",
           "32019L1937", "32019L0882", "32019L2161", "32023L2673", "32023L0970", "32024L1760", "32023R2631", "32024L1275",
           "32006L0112", "32010R0904", "32023L2226", "32003R0001", "32002L0058", "32002L0087", "32023R1113", "32016R1675",
           "32022R0858", "32020R1503", "32021L2167", "32019L0713", "32018L1673", "32017L1371", "32024R0886", "32021R1230",
           "32015R0751", "32013R1024", "32024R1623", "32024L1619", "32019R0876", "32019L0878", "32019L0879", "32024R2987",
           "32023R2845", "32024R2809", "32024L2811", "32024L0927", "32023R0606", "32013L0034", "32002R1606", "32023R1803",
           "32023R2772", "32021R2139", "32021R2178", "32022R1288", "32004L0109", "32007L0036", "32017L0828", "32017R0565",
           "32017L0593", "32017R0653", "32018R0389", "32015R0061", "32021R0923", "32017R2358", "32017R2359", "32021R0451"]

def ue():
    q_codici(CORE, "ue_core")
    q_codici(FILTRATI, "ue_filtrati")
    sparql(PFX + """SELECT DISTINCT ?celex ?tipo ?data ?tit WHERE {
      ?w cdm:resource_legal_id_celex ?celex ; cdm:resource_legal_in-force "true"^^xsd:boolean ;
         cdm:work_created_by_agent <http://publications.europa.eu/resource/authority/corporate-body/ECB> ; cdm:work_has_resource-type ?tipo .
      OPTIONAL { ?w cdm:work_date_document ?data }
      OPTIONAL { ?e cdm:expression_belongs_to_work ?w ; cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ITA> ; cdm:expression_title ?tit } }""", "ue_bce")
    q_basati(BASI, "ue_famiglie")
    q_celex(INCLUDI, "ue_includi")
    q_sanzioni("ue_sanzioni")

# ------------------------------------------------------------------ Italia (Normattiva)
CHIAVI_IT = ["bancario", "banche", "credito", "creditizi", "intermediari", "finanziari", "finanza", "risparmio", "riciclaggio",
    "terrorismo", "usura", "pagamento", "moneta elettronica", "assicurazioni", "assicurativa", "consumatori", "consumo", "trasparenza",
    "valori mobiliari", "strumenti finanziari", "mercati", "investimento", "fondi", "previdenza complementare", "dati personali",
    "cibernetica", "cybersicurezza", "intelligenza artificiale", "sicurezza sul lavoro", "salute e sicurezza", "responsabilita' amministrativa",
    "crisi d'impresa", "insolvenza", "sovraindebitamento", "garanzia", "cartolarizzazione", "obbligazioni", "assegno", "cambiale",
    "imposte sui redditi", "imposta sul valore aggiunto", "bollo", "accertamento", "riscossione", "anagrafe tributaria", "redditi di natura finanziaria",
    "societa'", "concorrenza", "lavoro", "lavoratori", "pari opportunita'", "disabili", "previdenza", "pensioni", "mutui", "fallimento",
    "titolari effettivi", "segnalazione", "whistleblowing", "appalti", "amministrazione digitale", "firma elettronica", "conti correnti",
    "deposito", "carte di pagamento", "cripto", "sostenibilita'", "direttiva (UE)", "direttiva 20", "regolamento (UE)"]
TIPI_IT = ["LEGGE", "DECRETO LEGISLATIVO", "DECRETO-LEGGE", "DECRETO DEL PRESIDENTE DELLA REPUBBLICA", "DECRETO", "DECRETO MINISTERIALE", "REGIO DECRETO"]

def it(max_pag=8):
    oggi = time.strftime("%Y-%m-%d"); atti = {}
    for k in CHIAVI_IT:
        for tipo in TIPI_IT:
            for pag in range(1, max_pag + 1):
                body = {"denominazioneAtto": tipo, "titoloRicerca": k, "orderType": "recente", "vigenza": oggi,
                        "paginazione": {"paginaCorrente": pag, "numeroElementiPerPagina": 100}}
                try:
                    r = requests.post(NA + "/ricerca/avanzata", json=body, headers={**UA, "Content-Type": "application/json", "Accept": "application/json", "Origin": "https://dati.normattiva.it"}, timeout=120)
                    d = r.json()
                except Exception as e:
                    log(f"IT {k}/{tipo}/{pag}: {e}"); break
                la = d.get("listaAtti") or []
                for a in la:
                    key = a.get("codiceRedazionale") or f"{a.get('denominazioneAtto')}|{a.get('annoProvvedimento')}|{a.get('numeroProvvedimento')}"
                    x = atti.setdefault(key, {c: a.get(c) for c in ("denominazioneAtto", "numeroProvvedimento", "giornoProvvedimento", "meseProvvedimento",
                        "annoProvvedimento", "dataGU", "numeroGU", "codiceRedazionale", "titoloAtto", "descrizioneEmettitore")})
                    x.setdefault("chiavi", []); x["chiavi"].append(k) if k not in x["chiavi"] else None
                if pag >= (d.get("numeroPagine") or 0) or not la: break
                time.sleep(0.15)
        log(f"IT chiave {k}: totale atti {len(atti)}")
        (OUT / "it_normattiva.json").write_text(json.dumps(list(atti.values()), ensure_ascii=False, indent=0), encoding="utf-8")
    (OUT / "it_normattiva.json").write_text(json.dumps(list(atti.values()), ensure_ascii=False, indent=0), encoding="utf-8")
    log(f"IT totale: {len(atti)}")

if __name__ == "__main__":
    modo = (Path("catalogo/avvia.txt").read_text().split() or ["prova"])[0]
    log("modo:", modo)
    if modo == "prova": prova()
    if modo in ("ue", "tutto"): ue()
    if modo == "ue2": q_basati(BASI, "ue_famiglie"); q_celex(INCLUDI, "ue_includi")
    if modo in ("it", "tutto"): it()
    (OUT / "log.txt").write_text("\n".join(LOG), encoding="utf-8")
