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

if __name__ == "__main__":
    modo = (Path("catalogo/avvia.txt").read_text().split() or ["prova"])[0]
    log("modo:", modo)
    if modo == "prova": prova()
    (OUT / "log.txt").write_text("\n".join(LOG), encoding="utf-8")
