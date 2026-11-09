"""Elabora un pacchetto di pagine EUR-Lex scaricate dal browser ([{id, celex, html}]) con le stesse regole di biblioteca.scarica_ue.
Uso: python biblioteca_pack_eurlex.py <pacchetto.json>"""
import json, re, sys
from biblioteca import pulisci, impronta, salva

def dividi_ue(html):
    t = pulisci(html)
    t = re.sub(r"(?m)^(Articolo \d+(?: ?(?:bis|ter|quater|quinquies|sexies|[a-z]))?)[ .]*$", r"\1", t)
    parti = re.split(r"\n(?=Articolo \d+(?: ?(?:bis|ter|quater|quinquies|sexies|[a-z]))?\n)", "\n" + t)
    arts = []
    for p in parti[1:]:
        m = re.match(r"Articolo (\d+(?: ?(?:bis|ter|quater|quinquies|sexies|[a-z]))?)\n(.*?)\n", p)
        if not m: continue
        testo = p.strip(); fine = re.search(r"\n(ALLEGATO|Allegato [IVX]+\n|Fatto a )", testo)
        if fine: testo = testo[:fine.start()]
        arts.append({"num": m.group(1).replace(" ", "-"), "rubrica": m.group(2)[:200], "testo": testo, "hash": impronta(testo)})
    if not arts and len(t) > 500:
        arts = [{"num": "Testo", "rubrica": "testo integrale (atto non diviso in articoli)", "testo": t, "hash": impronta(t)}]
    return list({a["num"]: a for a in arts}.values())

if __name__ == "__main__":
    corpus = {v["id"]: v for v in json.load(open("biblioteca/corpus_completo.json", encoding="utf-8"))}
    ok = 0
    for it in json.load(open(sys.argv[1], encoding="utf-8")):
        arts = dividi_ue(it["html"])
        if not arts: print("VUOTO", it["id"]); continue
        url = f"https://eur-lex.europa.eu/legal-content/IT/TXT/HTML/?uri=CELEX:{it['celex']}"
        salva(corpus[it["id"]], {"celex_consolidato": it["celex"], "url": url}, arts, url); ok += 1
    print("salvati", ok)
