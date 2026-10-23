"""Prova Media Cloud: chiave dal segreto MEDIACLOUD_API_KEY, collezioni italiane, conteggio articoli su un tema."""
import json
import os
from datetime import date, timedelta
from pathlib import Path

import mediacloud.api as mc

chiave = os.environ.get("MEDIACLOUD_API_KEY", "").strip()
import re, requests
out = {"chiave_presente": bool(chiave), "lunghezza": len(chiave),
       "solo_esadecimale": bool(re.fullmatch(r"[0-9a-fA-F]+", chiave)),
       "spazi_o_a_capo": bool(re.search(r"\s", os.environ.get("MEDIACLOUD_API_KEY", ""))),
       "inizia_con_token": chiave.lower().startswith("token"),
       "impronta": __import__("hashlib").sha256(chiave.encode()).hexdigest()[:12]}
r = requests.get("https://search.mediacloud.org/api/auth/profile", headers={"Authorization": f"Token {chiave}"}, timeout=30)
out["profilo_http"] = r.status_code
out["profilo_risposta"] = r.text[:200] if r.status_code != 200 else "ok"
try:
    d, s = mc.DirectoryApi(chiave), mc.SearchApi(chiave)
    out["profilo_ok"] = bool(s.user_profile())
    colls = d.collection_list(name="Italy", limit=20)["results"]
    out["collezioni_italia"] = [{"id": c["id"], "nome": c["name"], "fonti": c.get("source_count")} for c in colls]
    naz = next((c for c in colls if "national" in c["name"].lower()), colls[0] if colls else None)
    fine = date.today() - timedelta(days=1)
    out["collezione_usata"] = naz and naz["name"]
    out["conteggi"] = {}
    for q in ['"euro digitale"', '"antiriciclaggio"', '"Basilea 3" OR "Basilea III"', '"MiCA" OR "cripto-attività"']:
        tot = s.story_count(q, fine - timedelta(days=90), fine, collection_ids=[naz["id"]])
        out["conteggi"][q] = tot
    serie = s.story_count_over_time('"euro digitale"', fine - timedelta(days=60), fine, collection_ids=[naz["id"]])
    out["serie_euro_digitale_ultimi"] = [{"data": str(p["date"]), "n": p["count"]} for p in serie[-10:]]
except Exception as e:  # noqa: BLE001
    out["errore"] = f"{type(e).__name__}: {str(e)[:400]}"
Path("dati").mkdir(exist_ok=True)
Path("dati/prova_mediacloud.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
print(json.dumps(out, ensure_ascii=False, indent=1, default=str)[:3000])
