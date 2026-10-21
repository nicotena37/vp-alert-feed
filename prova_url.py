"""Prova una lista di indirizzi (prova_url.txt, uno per riga) dai server di GitHub e scrive dati/prova_url.json.
Serve a cercare strade ufficiali alternative per i siti che bloccano i feed. Rispetta il robots.txt."""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

import leggi_feed as L

L.TIMEOUT = 60
QUI = Path(__file__).parent
out = []
for url in [u.strip() for u in (QUI / "prova_url.txt").read_text(encoding="utf-8").splitlines()
            if u.strip() and not u.startswith("#")]:
    ok, motivo = L.robots(url)
    r = {"url": url, "robots_ok": ok, "motivo": motivo}
    if ok:
        t0 = time.time()
        try:
            stato, c = L.scarica(url)
            r.update(stato=stato, byte=len(c), secondi=round(time.time() - t0, 1),
                     captcha=bool(re.search(rb"captcha", c[:20000], re.I)),
                     inizio=re.sub(r"\s+", " ", c[:600].decode("utf-8", "replace")))
        except Exception as e:  # noqa: BLE001
            r.update(errore=f"{type(e).__name__}: {e}", secondi=round(time.time() - t0, 1))
    out.append(r)
(QUI / "dati").mkdir(exist_ok=True)
(QUI / "dati" / "prova_url.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
