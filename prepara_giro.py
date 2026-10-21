"""Prepara i feed letti da GitHub per il giro del VP Alert (si esegue nell'ambiente di Claude, non sul PC).

Uso:  python3 prepara_giro.py <cartella di uscita> [--ore 30]
  - copia dati/*.json nella cartella di uscita con il loro nome_file (vpalert_rss_...json): da lì vanno nella
    cartella Download del PC e rss.py li tratta come quelli del browser;
  - salta i file più vecchi di --ore ore (lettura GitHub troppo vecchia);
  - stampa in una riga i siti da leggere ancora col browser (feed bloccati per i server di GitHub).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

QUI = Path(__file__).parent


def main() -> int:
    uscita = Path(sys.argv[1])
    ore = float(sys.argv[sys.argv.index("--ore") + 1]) if "--ore" in sys.argv else 30
    uscita.mkdir(parents=True, exist_ok=True)
    adesso = datetime.now(timezone.utc)
    copiati, vecchi, browser, robots = [], [], [], []
    for f in sorted((QUI / "dati").glob("*.json")):
        if f.name == "stato.json":
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        if not isinstance(d, dict) or "nome_file" not in d:      # es. prova_url.json
            continue
        eta = (adesso - datetime.fromisoformat(d["letto_il"].replace("Z", "+00:00"))).total_seconds() / 3600
        if eta > ore:
            vecchi.append(d["sito"])
            continue
        errori = [x for x in d["feed"] if x.get("errore")]
        if any("robots" in x.get("motivo", "") for x in errori):
            robots.append(d["sito"])
        elif errori:
            browser.append(f"{d['sito']} ({len(errori)}/{len(d['feed'])})")
        if len(errori) < len(d["feed"]):          # almeno un feed letto: il file serve
            (uscita / d["nome_file"]).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
            copiati.append(d["sito"])
    print(json.dumps({"file_da_github": len(copiati), "letti_il": json.loads(
        (QUI / "dati" / "stato.json").read_text(encoding="utf-8"))["letto_il"][:16],
        "col_browser": browser, "robots_vieta": robots, "troppo_vecchi": vecchi}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
