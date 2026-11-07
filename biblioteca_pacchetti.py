"""Biblioteca: elabora i pacchetti raccolti dal browser del PC (Banca d'Italia, IVASS, Garante, UIF).
Ogni pacchetto è un JSON [{url, src, pdf (base64) | testo}]. Collega ogni voce a corpus_autorita.json tramite l'url,
estrae il testo (OCR se il PDF è una scansione), divide in parti e salva in biblioteca/testi_autorita/.
Uso: python biblioteca_pacchetti.py <cartella_pacchetti> [prefisso]"""
import base64, json, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path
import biblioteca_pdf as bp

B = Path("biblioteca"); T = B / "testi_autorita"; T.mkdir(parents=True, exist_ok=True)

def main(cartella, prefisso="bibl_pack_"):
    corpus = {v["url"]: v for v in json.loads((B / "corpus_autorita.json").read_text(encoding="utf-8"))}
    extra_p = B / "corpus_autorita_extra.json"
    extra = {v["url"]: v for v in (json.loads(extra_p.read_text(encoding="utf-8")) if extra_p.exists() else [])}
    ip = B / "indice_autorita_browser.json"; indice = json.loads(ip.read_text(encoding="utf-8")) if ip.exists() else {}
    fatti = vuoti = 0
    for f in sorted(Path(cartella).glob(prefisso + "*.json")):
        for it in json.loads(f.read_text(encoding="utf-8")):
            v = corpus.get(it["url"]) or extra.get(it["url"])
            if not v: print("  senza voce:", it["url"]); continue
            if it.get("pdf"):
                with tempfile.NamedTemporaryFile(suffix=".pdf") as tf:
                    tf.write(base64.b64decode(it["pdf"])); tf.flush(); t = bp.testo_pdf(tf.name)
            else:
                t = "\n".join(l.strip() for l in (it.get("testo") or "").splitlines() if l.strip())
            arts = bp.dividi(t) if len(t) > 200 else []
            if not arts: vuoti += 1; print("  VUOTO", v["id"], it["src"][-70:]); continue
            rec = {"id": v["id"], "titolo": v["titolo"], "estremi": v.get("estremi", ""), "fonte": v["fonte"], "url": it["src"], "pagina": it["url"],
                   "area": v.get("area", []), "data": v.get("data", ""), "scaricato_il": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   "n_articoli": len(arts), "articoli": arts}
            p = T / f"{v['id']}.json"
            if p.exists():
                old = {a["num"]: a["hash"] for a in json.loads(p.read_text(encoding="utf-8")).get("articoli", [])}
                rec["cambiati_dall_ultimo_scarico"] = [a["num"] for a in arts if old.get(a["num"]) not in (None, a["hash"])]
            p.write_text(json.dumps(rec, ensure_ascii=False, indent=0), encoding="utf-8")
            indice[v["id"]] = {k: rec[k] for k in ("titolo", "estremi", "fonte", "url", "area", "scaricato_il", "n_articoli")}
            fatti += 1
        print(f"{f.name}: elaborato")
    ip.write_text(json.dumps(indice, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"salvati {fatti}, vuoti {vuoti}")

if __name__ == "__main__":
    main(*sys.argv[1:])
