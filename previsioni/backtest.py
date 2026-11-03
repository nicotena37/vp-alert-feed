"""Prova di 39 metodi di previsione sui temi normativi (backtest a origine mobile, senza sbirciare il futuro).

Bersaglio: quanti atti, proposte e comunicazioni UE (EUR-Lex) per tema usciranno nei prossimi H mesi.
Ogni metodo, a ogni origine t, vede solo i mesi < t. Si misura:
  - errore scalato (MASE): errore assoluto sul totale dei prossimi H mesi / errore del metodo di riferimento (media 12 mesi)
  - Spearman: quanto bene il metodo ordina i temi dal più al meno caldo
  - Top-5: quanti dei 5 temi davvero più caldi il metodo mette tra i suoi primi 5
  - copertura dell'intervallo 80% (calibrazione), calcolata dopo dagli errori passati
Uso: python backtest.py <cartella archivio/storico> <uscita.json>
"""
from __future__ import annotations

import csv
import json
import math
import sys
import warnings
from collections import defaultdict
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")
H = 6                      # orizzonte: prossimi 6 mesi
INIZIO_TEST = "2019-01"    # prime origini di prova
ARCH = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("archivio/storico")
USCITA = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("risultati_backtest.json")


# ---------------------------------------------------------------- dati
def leggi(nome, tipi=None):
    f = ARCH / f"{nome}.csv"
    if not f.exists():
        return {}, {}
    val, tot = defaultdict(float), defaultdict(float)
    for r in csv.DictReader(f.open(encoding="utf-8")):
        if tipi and r["tipo"] not in tipi:
            continue
        if r["tema"]:
            val[(r["mese"], r["tema"])] += float(r["valore"] or 0)
        if r["totale_fonte"]:
            tot[r["mese"]] += float(r["totale_fonte"])
    return val, tot


def mesi_tra(a, b):
    y, m = map(int, a.split("-"))
    out = []
    while f"{y}-{m:02d}" <= b:
        out.append(f"{y}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


TEMI = [t["tema"] for t in json.loads(Path(__file__).with_name("temi_indicatori.json").read_text(encoding="utf-8"))["temi"]]
y_val, y_tot = leggi("eurlex")                                   # bersaglio: tutti i documenti UE con tema
prop_val, _ = leggi("eurlex", {"proposta", "comunicazione"})     # segnale anticipatore: proposte e comunicazioni
FONTI_X = {"media": "mediacloud", "politica": "camera", "ddl": "senato", "bce": "bce_discorsi", "studi": "openalex"}
X = {k: leggi(v) for k, v in FONTI_X.items()}
MESI = mesi_tra("2016-01", "2026-10")                            # 2026-11 è in corso: escluso
T = len(MESI)
Y = np.array([[y_val.get((m, t), 0.0) for m in MESI] for t in TEMI])          # temi x mesi
P = np.array([[prop_val.get((m, t), 0.0) for m in MESI] for t in TEMI])


def quota(nome):
    v, tot = X[nome]
    if not v:
        return None
    a = np.array([[v.get((m, t), 0.0) for m in MESI] for t in TEMI])
    tt = np.array([tot.get(m, 0.0) for m in MESI])
    if tt.sum() == 0:                                     # fonti senza totale (OpenAlex): quota sul totale dei temi
        tt = a.sum(0)
    disponibile = tt > 0
    q = np.where(disponibile, a / np.maximum(tt, 1), np.nan)
    return q


XQ = {k: quota(k) for k in FONTI_X}


# ---------------------------------------------------------------- metodi univariati: f(storia) -> totale prossimi H mesi
def m_media(k):
    return lambda s, mesi: H * s[-k:].mean()


def m_mediana(k):
    return lambda s, mesi: H * float(np.median(s[-k:]))


def naive(s, mesi):
    return H * s[-1]


def stag_naive(s, mesi):
    return s[-12:-12 + H].sum() if len(s) >= 12 else H * s.mean()


def stag_media2(s, mesi):
    if len(s) < 24:
        return H * s.mean()
    return 0.5 * (s[-12:-12 + H].sum() + s[-24:-24 + H].sum())


def drift(s, mesi):
    w = s[-24:]
    slope = (w[-1] - w[0]) / (len(w) - 1)
    return max(0.0, sum(w[-1] + slope * h for h in range(1, H + 1)))


def trend_ols(k):
    def f(s, mesi):
        w = s[-k:]
        x = np.arange(len(w))
        b, a = np.polyfit(x, w, 1)
        return max(0.0, sum(a + b * (len(w) - 1 + h) for h in range(1, H + 1)))
    return f


def ses(alpha):
    def f(s, mesi):
        lv = s[0]
        for v in s[1:]:
            lv = alpha * v + (1 - alpha) * lv
        return H * lv
    return f


def ses_ott(s, mesi):
    best, bl = None, 1e18
    for a in np.linspace(0.05, 0.9, 18):
        lv, err = s[0], 0.0
        for v in s[1:]:
            err += (v - lv) ** 2
            lv = a * v + (1 - a) * lv
        if err < bl:
            bl, best = err, lv
    return H * best


def _sm(fn):
    def f(s, mesi):
        try:
            return max(0.0, float(np.sum(fn(s))))
        except Exception:  # noqa: BLE001
            return H * s[-12:].mean()
    return f


def _holt(s, damped):
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    return ExponentialSmoothing(s[-60:] + 0.0, trend="add", damped_trend=damped, initialization_method="estimated").fit().forecast(H)


def _hw(s):
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    w = s[-72:] + 0.0
    return ExponentialSmoothing(w, trend="add", damped_trend=True, seasonal="add", seasonal_periods=12,
                                initialization_method="estimated").fit().forecast(H)


def _theta(s):
    from statsmodels.tsa.forecasting.theta import ThetaModel
    return ThetaModel(s[-72:] + 0.0, period=12, deseasonalize=False).fit().forecast(H)


def _arima(s, order):
    from statsmodels.tsa.arima.model import ARIMA
    w = np.log1p(s[-72:])
    return np.expm1(ARIMA(w, order=order, trend="c" if order[1] == 0 else "n").fit().forecast(H))


def _ets_auto(s):
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    w = s[-72:] + 0.0
    migliore, aic = None, 1e18
    for tr, dp in ((None, False), ("add", False), ("add", True)):
        try:
            m = ExponentialSmoothing(w, trend=tr, damped_trend=dp, initialization_method="estimated").fit()
            if m.aic < aic:
                aic, migliore = m.aic, m
        except Exception:  # noqa: BLE001
            pass
    return migliore.forecast(H)


def _auto_arima(s):
    from statsmodels.tsa.arima.model import ARIMA
    w = np.log1p(s[-48:])
    migliore, aic = None, 1e18
    for o in ((1, 0, 0), (0, 1, 1), (1, 0, 1)):
        try:
            m = ARIMA(w, order=o, trend="c" if o[1] == 0 else "n").fit()
            if m.aic < aic:
                aic, migliore = m.aic, m
        except Exception:  # noqa: BLE001
            pass
    return np.expm1(migliore.forecast(H))


def croston(variante, alpha=0.1, beta=0.1):
    def f(s, mesi):
        nz = np.nonzero(s)[0]
        if len(nz) == 0:
            return 0.0
        if variante == "tsb":
            p, z = (s > 0).mean(), s[nz].mean()
            for v in s:
                p = beta * (v > 0) + (1 - beta) * p
                if v > 0:
                    z = alpha * v + (1 - alpha) * z
            return H * p * z
        z, q, ultimo = s[nz[0]], max(nz[0], 1), nz[0]
        for i in nz[1:]:
            z = alpha * s[i] + (1 - alpha) * z
            q = alpha * (i - ultimo) + (1 - alpha) * q
            ultimo = i
        r = z / q
        return H * (r * (1 - alpha / 2) if variante == "sba" else r)
    return f


def poisson_trend(stag):
    def f(s, mesi):
        import statsmodels.api as sm
        w = s[-36:]
        x = np.arange(len(w)) / 12
        cols = [np.ones_like(x), x]
        if stag:
            mm = np.array([int(m[5:]) for m in mesi[-36:]])
            cols += [np.sin(2 * np.pi * mm / 12), np.cos(2 * np.pi * mm / 12)]
        try:
            res = sm.GLM(w, np.column_stack(cols), family=sm.families.Poisson()).fit()
            out = 0.0
            for h in range(1, H + 1):
                xx = (len(w) - 1 + h) / 12
                riga = [1, xx]
                if stag:
                    mf = (int(mesi[-1][5:]) + h - 1) % 12 + 1
                    riga += [math.sin(2 * math.pi * mf / 12), math.cos(2 * math.pi * mf / 12)]
                out += min(math.exp(min(20, float(np.dot(res.params, riga)))), 50 * max(1.0, w.max()))
            return out
        except Exception:  # noqa: BLE001
            return H * w.mean()
    return f


def eb_k(k, finestra=12):
    """Gamma-Poisson: tasso degli ultimi mesi ridotto verso la media lunga; k = forza del richiamo (in mesi)"""
    def f(s, mesi):
        return H * (s[-finestra:].sum() + k * s.mean()) / (finestra + k)
    return f


eb_shrink = eb_k(6.0)


UNIV = {
    "Ultimo mese": naive, "Media 3 mesi": m_media(3), "Media 6 mesi": m_media(6), "Media 12 mesi": m_media(12),
    "Media 24 mesi": m_media(24), "Mediana 12 mesi": m_mediana(12), "Stagionale ingenuo": stag_naive,
    "Stagionale media 2 anni": stag_media2, "Deriva": drift, "Tendenza lineare 24 mesi": trend_ols(24),
    "Tendenza lineare 12 mesi": trend_ols(12), "Livellamento esp. 0,1": ses(0.1), "Livellamento esp. 0,2": ses(0.2),
    "Livellamento esp. 0,3": ses(0.3), "Livellamento esp. 0,5": ses(0.5), "Livellamento esp. ottimizzato": ses_ott,
    "Holt lineare": _sm(lambda s: _holt(s, False)), "Holt smorzato": _sm(lambda s: _holt(s, True)),
    "Holt-Winters stagionale": _sm(_hw), "ETS scelto con AIC": _sm(_ets_auto), "Theta": _sm(_theta),
    "ARIMA(1,0,0) su log": _sm(lambda s: _arima(s, (1, 0, 0))), "ARIMA scelto con AIC": _sm(_auto_arima),
    "Croston": croston("croston"), "Croston SBA": croston("sba"), "TSB": croston("tsb"),
    "Poisson con tendenza": poisson_trend(False), "Poisson tendenza e stagione": poisson_trend(True),
    "Bayes empirico (richiamo alla media)": eb_shrink,
    "Bayes empirico, richiamo debole (k=3)": eb_k(3.0), "Bayes empirico, richiamo forte (k=12)": eb_k(12.0),
    "Bayes empirico, richiamo molto forte (k=24)": eb_k(24.0), "Bayes empirico su 6 mesi (k=6)": eb_k(6.0, 6),
    "Insieme: Bayes empirico + TSB": lambda s, mesi: 0.5 * (eb_shrink(s, mesi) + croston("tsb")(s, mesi)),
}


# ---------------------------------------------------------------- metodi globali (tutti i temi insieme, con segnali anticipatori)
def caratteristiche(i, t, con_segnali):
    """feature del tema i all'origine t (solo mesi < t)"""
    s = Y[i, :t]
    f = [np.log1p(s[-3:].sum()), np.log1p(s[-6:].sum()), np.log1p(s[-12:].sum()), np.log1p(s[-24:].sum() / 2),
         np.log1p(s.mean() * 12), np.log1p(P[i, t - 6:t].sum()), np.log1p(P[i, t - 12:t].sum())]
    if con_segnali:
        for k in ("media", "politica", "ddl", "bce", "studi"):
            q = XQ.get(k)
            if q is None:
                f += [0.0, 0.0]
                continue
            r6, r24 = q[i, t - 6:t], q[i, t - 30:t - 6]
            a, b = np.nanmean(r6) if np.isfinite(r6).any() else np.nan, np.nanmean(r24) if np.isfinite(r24).any() else np.nan
            if np.isnan(a) or np.isnan(b):
                f += [0.0, 0.0]
            else:
                f += [math.log((a + 1e-4) / (b + 1e-4)), math.log1p(a * 1000)]
    return f


def globale(tipo, con_segnali):
    cache = {}

    def prevedi(t):                       # restituisce previsioni per tutti i temi all'origine t
        if t in cache:
            return cache[t]
        Xtr, ytr = [], []
        for tt in range(30, t - H + 1, 1):          # addestramento: solo origini il cui futuro è già noto a t
            for i in range(len(TEMI)):
                Xtr.append(caratteristiche(i, tt, con_segnali))
                ytr.append(Y[i, tt:tt + H].sum())
        Xte = [caratteristiche(i, t, con_segnali) for i in range(len(TEMI))]
        Xtr, ytr, Xte = np.array(Xtr), np.array(ytr), np.array(Xte)
        if tipo == "poisson":
            from sklearn.linear_model import PoissonRegressor
            m = PoissonRegressor(alpha=1e-3, max_iter=1000).fit(Xtr, ytr)
            p = m.predict(Xte)
        elif tipo == "ridge":
            from sklearn.linear_model import Ridge
            m = Ridge(alpha=1.0).fit(Xtr, np.log1p(ytr))
            p = np.expm1(m.predict(Xte))
        elif tipo == "gb":
            from sklearn.ensemble import HistGradientBoostingRegressor
            m = HistGradientBoostingRegressor(loss="poisson", max_iter=200, learning_rate=0.05, max_leaf_nodes=15,
                                              random_state=0).fit(Xtr, ytr)
            p = m.predict(Xte)
        else:
            from sklearn.ensemble import RandomForestRegressor
            m = RandomForestRegressor(n_estimators=200, min_samples_leaf=5, random_state=0, n_jobs=-1).fit(Xtr, ytr)
            p = m.predict(Xte)
        cache[t] = np.maximum(p, 0)
        return cache[t]
    return prevedi


GLOBALI = {
    "Regressione di Poisson globale (storia e proposte)": globale("poisson", False),
    "Regressione di Poisson globale + segnali": globale("poisson", True),
    "Ridge su log + segnali": globale("ridge", True),
    "Gradient boosting + segnali": globale("gb", True),
    "Foresta casuale + segnali": globale("rf", True),
    "Gradient boosting (storia e proposte)": globale("gb", False),
}


def eb_proposte(t):
    """Bayes empirico corretto con le proposte UE degli ultimi 12 mesi (le proposte di oggi sono gli atti di domani)"""
    out = []
    for i in range(len(TEMI)):
        base = eb_shrink(Y[i, :t], MESI[:t])
        rapporto = (P[i, t - 12:t].sum() + 1) / (P[i, t - 36:t - 12].sum() / 2 + 1)
        out.append(base * rapporto ** ESP_PROP)
    return np.array(out)


ESP_PROP = 0.5


# ---------------------------------------------------------------- backtest
def _uno(arg):
    nome, t = arg
    f = UNIV[nome]
    return np.array([f(Y[i, :t], MESI[:t]) for i in range(len(TEMI))])


def banco_vp(classifica):
    """seconda prova: gli alert manuali della banca (settimane 2-31 del 2026), orizzonte 4 settimane"""
    import importlib.util
    man = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    if not man or not man.exists():
        return None
    spec = importlib.util.spec_from_file_location("cs", Path(__file__).with_name("serie_vp.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    V = m.serie_vp(man, TEMI)                      # temi x settimane (2..31)
    global H
    H0, H = H, 4
    out = {}
    try:
        orig = list(range(12, V.shape[1] - H + 1))
        from scipy.stats import spearmanr
        for nome, f in UNIV.items():
            if any(k in nome for k in ("Stagionale", "Holt-Winters", "ARIMA", "ETS", "Theta", "Holt", "Poisson")):
                continue
            ae, ar, sp, top = [], [], [], []
            for t in orig:
                v = V[:, t:t + H].sum(1)
                pr = np.array([f(V[i, :t], [""] * t) for i in range(len(TEMI))])
                rf = np.array([H * V[i, max(0, t - 12):t].mean() for i in range(len(TEMI))])
                ae.append(np.abs(pr - v).sum()); ar.append(np.abs(rf - v).sum())
                if v.std() > 0 and pr.std() > 0:
                    c = spearmanr(pr, v).correlation
                    if np.isfinite(c):
                        sp.append(c)
                top.append(len(set(np.argsort(-pr)[:5]) & set(np.argsort(-v)[:5])) / 5)
            out[nome] = {"MASE": float(np.sum(ae) / np.sum(ar)), "Spearman": float(np.mean(sp)), "Top5": float(np.mean(top))}
    finally:
        H = H0
    nomi = sorted(out, key=lambda n: (out[n]["MASE"] - out[n]["Spearman"] - out[n]["Top5"]))
    return {"risultati": out, "ordine": nomi, "origini": len(orig)}


def modelli_finali():
    """coefficienti dei modelli globali addestrati su tutti i dati e previsioni attuali di tutti i metodi (all'ultimo mese)"""
    from sklearn.linear_model import PoissonRegressor, Ridge
    t = T
    G = {}
    for nome, seg, tipo in (("Regressione di Poisson globale (storia e proposte)", False, "poisson"),
                            ("Regressione di Poisson globale + segnali", True, "poisson"), ("Ridge su log + segnali", True, "ridge")):
        Xtr, ytr = [], []
        for tt in range(30, t - H + 1):
            for i in range(len(TEMI)):
                Xtr.append(caratteristiche(i, tt, seg)); ytr.append(Y[i, tt:tt + H].sum())
        Xtr, ytr = np.array(Xtr), np.array(ytr)
        if tipo == "poisson":
            m = PoissonRegressor(alpha=1e-3, max_iter=1000).fit(Xtr, ytr)
            G[nome] = {"coef": m.coef_.tolist(), "intercetta": float(m.intercept_), "segnali": seg, "log": False}
        else:
            m = Ridge(alpha=1.0).fit(Xtr, np.log1p(ytr))
            G[nome] = {"coef": m.coef_.tolist(), "intercetta": float(m.intercept_), "segnali": seg, "log": True}
    attuali = {}
    for nome, f in UNIV.items():
        attuali[nome] = {TEMI[i]: float(f(Y[i, :t], MESI[:t])) for i in range(len(TEMI))}
    for nome, f in GLOBALI.items():
        v = f(t) if "Gradient" in nome or "Foresta" in nome else None
        if v is not None:
            attuali[nome] = {TEMI[i]: float(v[i]) for i in range(len(TEMI))}
    return G, attuali


def valuta():
    origini = [k for k, m in enumerate(MESI) if m >= INIZIO_TEST and k + H <= T]
    vero = {t: Y[:, t:t + H].sum(1) for t in origini}
    previsioni = defaultdict(dict)
    from multiprocessing import Pool
    with Pool(2) as pool:
        for nome in UNIV:
            res = pool.map(_uno, [(nome, t) for t in origini])
            for t, v in zip(origini, res):
                previsioni[nome][t] = v
            print("fatto", nome, flush=True)
    for nome, f in GLOBALI.items():
        for t in origini:
            previsioni[nome][t] = f(t)
        print("fatto", nome, flush=True)
    for t in origini:
        previsioni["Bayes empirico + proposte UE"][t] = eb_proposte(t)
        globals()["ESP_PROP"] = 0.2
        previsioni["Bayes empirico + proposte UE (peso leggero)"][t] = eb_proposte(t)
        globals()["ESP_PROP"] = 0.5
        q = XQ.get("media")
        if q is not None:
            adj = []
            for i in range(len(TEMI)):
                r6, r24 = q[i, t - 6:t], q[i, t - 30:t - 6]
                ok = np.isfinite(r6).any() and np.isfinite(r24).any()
                rap = (np.nanmean(r6) + 1e-4) / (np.nanmean(r24) + 1e-4) if ok else 1.0
                adj.append(previsioni["Bayes empirico (richiamo alla media)"][t][i] * min(2.0, max(0.5, rap)) ** 0.3)
            previsioni["Bayes empirico + attenzione dei giornali"][t] = np.array(adj)
        u = [previsioni[n][t] for n in ("Livellamento esp. 0,3", "Theta", "Holt smorzato")]
        previsioni["Insieme: media di 3 classici"][t] = np.mean(u, 0)
        previsioni["Insieme: mediana di tutti gli univariati"][t] = np.median([previsioni[n][t] for n in UNIV], 0)
        previsioni["Insieme: Bayes empirico + gradient boosting"][t] = 0.5 * (previsioni["Bayes empirico (richiamo alla media)"][t]
                                                                               + previsioni["Gradient boosting + segnali"][t])
    rif = "Media 12 mesi"
    risultati = {}
    from scipy.stats import spearmanr
    for nome, pr in previsioni.items():
        ae, ae_rif, sp, top, logerr = [], [], [], [], []
        for t in origini:
            v, p, r = vero[t], pr[t], previsioni[rif][t]
            ae.append(np.abs(p - v).sum())
            ae_rif.append(np.abs(r - v).sum())
            logerr.append(np.abs(np.log1p(p) - np.log1p(v)).mean())
            if v.std() > 0 and p.std() > 0:
                c = spearmanr(p, v).correlation
                if np.isfinite(c):
                    sp.append(c)
            top.append(len(set(np.argsort(-p)[:5]) & set(np.argsort(-v)[:5])) / 5)
        risultati[nome] = {"MASE": float(np.sum(ae) / np.sum(ae_rif)), "Spearman": float(np.mean(sp)),
                           "Top5": float(np.mean(top)), "ErroreLog": float(np.mean(logerr)), "origini": len(origini)}
    # punteggio: media dei ranghi delle quattro misure (1 = migliore)
    nomi = list(risultati)
    for chiave, verso in (("MASE", 1), ("Spearman", -1), ("Top5", -1), ("ErroreLog", 1)):
        ordine = sorted(nomi, key=lambda n: verso * risultati[n][chiave])
        for k, n in enumerate(ordine):
            risultati[n]["rango_" + chiave] = k + 1
    for n in nomi:
        risultati[n]["rango_medio"] = float(np.mean([risultati[n]["rango_" + c] for c in ("MASE", "Spearman", "Top5", "ErroreLog")]))
    classifica = sorted(nomi, key=lambda n: risultati[n]["rango_medio"])

    def classifica_su(sotto):
        mis = {}
        for nome, pr in previsioni.items():
            ae, ar, sp, top = [], [], [], []
            for t in sotto:
                v, p, r = vero[t], pr[t], previsioni[rif][t]
                ae.append(np.abs(p - v).sum()); ar.append(np.abs(r - v).sum())
                if v.std() > 0 and p.std() > 0:
                    c = spearmanr(p, v).correlation
                if np.isfinite(c):
                    sp.append(c)
                top.append(len(set(np.argsort(-p)[:5]) & set(np.argsort(-v)[:5])) / 5)
            mis[nome] = (np.sum(ae) / np.sum(ar), np.mean(sp), np.mean(top))
        rg = defaultdict(list)
        for j, verso in ((0, 1), (1, -1), (2, -1)):
            for k, n in enumerate(sorted(mis, key=lambda n: verso * mis[n][j])):
                rg[n].append(k + 1)
        return sorted(mis, key=lambda n: np.mean(rg[n])), mis
    prima = [t for t in origini if MESI[t] < "2023-01"]
    dopo = [t for t in origini if MESI[t] >= "2023-01"]
    cl_prima, _ = classifica_su(prima)
    cl_dopo, mis_dopo = classifica_su(dopo)
    fuori_campione = {"scelti_sul_periodo_2019_2022": cl_prima[:2],
                      "posizione_nel_2023_2026": {n: cl_dopo.index(n) + 1 for n in cl_prima[:5]},
                      "migliori_2023_2026": cl_dopo[:5], "origini_prima": len(prima), "origini_dopo": len(dopo),
                      "metodi": len(cl_dopo)}
    # calibrazione: quantili degli errori relativi dei due migliori (servono per l'intervallo 80% sul sito)
    calib = {}
    for n in classifica[:2]:
        rel = []
        for t in origini:
            v, p = vero[t], previsioni[n][t]
            rel += list(np.log1p(v) - np.log1p(p))
        calib[n] = {"q10": float(np.quantile(rel, 0.1)), "q90": float(np.quantile(rel, 0.9))}
    vp = banco_vp(classifica)
    G, attuali = modelli_finali()
    for t in origini[-1:]:
        pass
    sintesi_vp = None
    if vp:
        pos = {n: k + 1 for k, n in enumerate(vp["ordine"])}
        parti = [f"{n}: {pos[n]}° su {len(pos)}" for n in classifica[:2] if n in pos]
        sintesi_vp = ("sui dati settimanali della banca (" + str(vp["origini"]) + " prove) " + "; ".join(parti)) if parti else None
    USCITA.write_text(json.dumps({"orizzonte_mesi": H, "inizio_test": INIZIO_TEST, "origini": len(origini),
                                  "temi": TEMI, "fonti_segnali": {k: XQ[k] is not None for k in XQ},
                                  "classifica": classifica, "risultati": risultati, "calibrazione": calib,
                                  "banco_vp": sintesi_vp, "vp_dettaglio": vp, "fuori_campione": fuori_campione, "modello_globale": G, "previsioni_attuali": attuali},
                                 ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{'metodo':55s} MASE  Spear  Top5  ErrLog  rango")
    for n in classifica:
        r = risultati[n]
        print(f"{n:55s} {r['MASE']:.3f} {r['Spearman']:.3f} {r['Top5']:.3f} {r['ErroreLog']:.3f} {r['rango_medio']:.1f}")


if __name__ == "__main__":
    valuta()
