"""Aggiorna i dati della pagina del risk assessment (cartella data/ accanto a index.html).
- tax.json: tassonomia del risk assessment (biblioteca/tassonomia_rk.json);
- proc.json: sottoprocessi ABI Lab (biblioteca/processi_abi.json);
- indice.json: per ogni norma gli ambiti come [tematica, ambito, 'P'|'S', [parti]] e, in posizione 8,
  i processi come [processo, [parti]]. Per le norme lette per intero si usa biblioteca/ambiti_articoli.json
  (associazione per articolo); per le altre si traducono gli ambiti della vecchia tassonomia;
- shard dei testi: rifà quelli che contengono norme riscaricate o completate.
Uso: python costruisci_dati.py <cartella data> [id cambiati separati da virgola]"""
import json, re, sys, gzip, base64, collections
from pathlib import Path

B = Path(__file__).resolve().parent.parent / "biblioteca"

# vecchia tassonomia -> tassonomia del risk assessment, per gli ambiti che hanno cambiato nome
MAPPA = {
    "Obblighi informativi": ("Vigilanza prudenziale", "Obblighi informativi - Vigilanza"),
    "Disposizioni in ambito di partecipazioni detenibili": ("Governance", "Disposizioni in materia di azioni e partecipazioni"),
    "Rapporti con la clientela": ("Trasparenza e tutela del consumatore", "Tutela del consumatore"),
    "Fondi propri e requisiti patrimoniali": ("Vigilanza prudenziale", "Requisiti patrimoniali e di liquidità"),
    "Statistiche": ("Segnalazioni di Vigilanza", "Segnalazione all'autorità di vigilanza compente"),
    "Gestione operativa crediti": ("Credito", "Gestione operativa dei crediti"),
    "Riassicurazione e riserve tecniche": ("Vigilanza prudenziale", "Riserve tecniche e solvibilità assicurativa"),
    "Accessibilità dei servizi": ("Trasparenza e tutela del consumatore", "Accessibilità e inclusione finanziaria"),
    "Segnalazione all'autorità di vigilanza competente": ("Segnalazioni di Vigilanza", "Segnalazione all'autorità di vigilanza compente"),
    "Adempimenti": ("Privacy", "Disposizioni generali per il trattamento dei dati"),
    "Tutela della riservatezza": ("Privacy", "Disposizioni generali per il trattamento dei dati"),
    "Eurosistema": ("Vigilanza prudenziale", "Requisiti patrimoniali e di liquidità"),
    "Riserva obbligatoria": ("Vigilanza prudenziale", "Requisiti patrimoniali e di liquidità"),
    "Mercati digitali": ("IT e Digital", "Sistemi informativi"),
    "Obblighi in materia di reporting": ("Informativa finanziaria (reporting)", "Contabilità e bilancio"),
    "Servizi di pagamento": ("Incassi e pagamenti", "Sistemi e mezzi di pagamento"),
    "Transazioni elettroniche": ("Incassi e pagamenti", "Sistemi e mezzi di pagamento"),
    "Finanziamento": ("Credito", "Credito alle PMI/ finanziamenti agevolati"),
    "Investimento": ("Mercati finanziari", "Investimenti"),
    "Fondi di investimento alternativi": ("Gestione collettiva", "Disposizioni generali"),
    "Organismi di investimento": ("Gestione collettiva", "Disposizioni generali"),
    "Fondi aperti": ("Gestione collettiva", "Disposizioni generali"),
    "Fondi di investimento": ("Gestione collettiva", "Disposizioni generali"),
    "Disposizione in materia di fondi di pensione": ("Gestione collettiva", "Disposizioni in materia di fondi pensione"),
    "Sinistri e periti RC auto": ("Distribuzione assicurativa", "Gestione sinistri RC auto"),
}
CHIAVE = lambda s: re.sub(r"[^a-z]", "", s.lower())

def main(data, cambiati=""):
    data = Path(data)
    rk = json.loads((B / "tassonomia_rk.json").read_text(encoding="utf-8"))
    per_ambito = collections.defaultdict(list)
    for t, am in rk.items():
        for a in am: per_ambito[CHIAVE(a)].append((t, a))
    coppie = {(CHIAVE(t), CHIAVE(a)): (t, a) for t, am in rk.items() for a in am}

    def traduci(t, a):
        if (CHIAVE(t), CHIAVE(a)) in coppie: return coppie[(CHIAVE(t), CHIAVE(a))]
        if a in MAPPA and not (a == "Obblighi informativi" and t == "Emittenti"): return MAPPA[a]
        if t == "Emittenti" and a == "Obblighi informativi": return ("Emittenti", "Obblighi informativi - Emittenti")
        c = per_ambito.get(CHIAVE(a))
        return c[0] if c and len(c) == 1 else None

    idx = json.loads((data / "indice.json").read_text(encoding="utf-8"))
    art = json.loads((B / "ambiti_articoli.json").read_text(encoding="utf-8"))
    codici = json.loads((B / "lettura" / "codici_ambiti.json").read_text(encoding="utf-8"))
    persi = collections.Counter()
    for nid, v in idx.items():
        if nid in art:
            parti = art[nid]["parti"]; con = [q for q in parti if q["a"]]
            primo = collections.Counter(q["a"][0] for q in con); tutti = collections.defaultdict(list)
            for q in con:
                for c in q["a"]: tutti[c].append(q["e"])
            soglia = max(2, round(0.1 * len(con)))
            amb = [[*codici[c], "P" if primo[c] >= soglia or (primo[c] and len(con) <= 3) else "S", e] for c, e in tutti.items()]
            amb.sort(key=lambda x: (x[2] != "P", -len(x[3])))
            proc = [[p, e] for p, e in sorted(art[nid]["processi"].items(), key=lambda x: -len(x[1]))]
        else:
            amb, visti = [], {}
            for t, a, r, e in v[4]:
                n = traduci(t, a)
                if not n: persi[f"{t} > {a}"] += 1; continue
                k = tuple(n)
                if k in visti:                                   # due vecchi ambiti finiti nello stesso: unisci
                    x = visti[k]; x[2] = "P" if "P" in (x[2], r) else "S"; x[3] = sorted(set(x[3]) | set(e), key=str)
                else:
                    visti[k] = [n[0], n[1], r, list(e)]; amb.append(visti[k])
            proc = []
        v[4] = amb
        while len(v) < 9: v.append([])
        v[8] = proc
        if nid in art: v.append(1) if len(v) < 10 else None    # posizione 9: letta per intero articolo per articolo
    (data / "indice.json").write_text(json.dumps(idx, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (data / "tax.json").write_text(json.dumps(rk, ensure_ascii=False), encoding="utf-8")
    proc = [p["p"] for p in json.loads((B / "processi_abi.json").read_text(encoding="utf-8"))]
    (data / "proc.json").write_text(json.dumps(proc, ensure_ascii=False), encoding="utf-8")
    print("norme", len(idx), "lette per articolo", sum(1 for k in idx if k in art), "ambiti non tradotti", dict(persi))

    # shard dei testi cambiati
    ids = [i for i in cambiati.split(",") if i]
    per_shard = collections.defaultdict(list)
    for i in ids:
        if i in idx: per_shard[idx[i][5]].append(i)
    for s, lista in per_shard.items():
        f = data / "t" / f"{s:02d}.b64.txt"
        sh = json.loads(gzip.decompress(base64.b64decode(f.read_text())))
        for i in lista:
            p = B / "testi" / f"{i}.json"
            if not p.exists(): p = B / "testi_autorita" / f"{i}.json"
            if not p.exists(): continue
            r = json.loads(p.read_text(encoding="utf-8"))
            sh[i] = [[a["num"], a.get("rubrica", ""), a.get("testo", "")] for a in r["articoli"]]
            idx[i][6] = len(sh[i])
        f.write_text(base64.b64encode(gzip.compress(json.dumps(sh, ensure_ascii=False).encode(), 9)).decode())
        print("shard", s, "aggiornato:", ", ".join(lista))
    (data / "indice.json").write_text(json.dumps(idx, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

if __name__ == "__main__":
    main(*sys.argv[1:])
