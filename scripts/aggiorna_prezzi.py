#!/usr/bin/env python3
# Robot prezzi Spendy — DUE FONTI FUSE
#
#   • Twelve Data   → azioni USA, ETF USA e cripto. Aggiornati OGNI GIORNO.
#                     Piano gratuito: 8 richieste/minuto, 800/giorno.
#   • Alpha Vantage → azioni ed ETF EUROPEI. Aggiornati A ROTAZIONE.
#                     Piano gratuito: 25 richieste/giorno, 5/minuto.
#                     Ogni giorno tocca i 25 più "vecchi": con 50 asset
#                     europei ognuno viene rinfrescato ogni ~2 giorni.
#   • Frankfurter (BCE) → cambi valuta. Gratuito, senza chiave.
#
# Il robot scrive un unico prezzi.json che l'app legge. Alla prima esecuzione
# scarica lo storico; poi aggiunge solo il punto del giorno.
#
# Chiavi (segreti del repository): TWELVE_DATA_KEY, ALPHA_VANTAGE_KEY
import json, os, sys, time, urllib.request, urllib.parse, datetime, ssl

ROOT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TICKERS = os.path.join(ROOT, "tickers.json")
PREZZI  = os.path.join(ROOT, "prezzi.json")

TD_KEY = os.environ.get("TWELVE_DATA_KEY", "").strip()
AV_KEY = os.environ.get("ALPHA_VANTAGE_KEY", "").strip()

MAX_HISTORY       = 400
BACKFILL_IF_UNDER = 250
TD_PAUSA          = 8
TD_BUDGET         = int(os.environ.get("TD_BUDGET", "700"))
AV_PAUSA          = 13
AV_BUDGET         = int(os.environ.get("AV_BUDGET", "25"))
CTX = ssl.create_default_context()

def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "spendy-price-bot"})
    with urllib.request.urlopen(req, timeout=30, context=CTX) as r:
        return json.loads(r.read().decode("utf-8"))

def merge_hist(old, new):
    m = {p[0]: p[1] for p in (old or []) if p and len(p) == 2}
    for p in (new or []):
        if p and len(p) == 2:
            m[p[0]] = p[1]
    return [[d, m[d]] for d in sorted(m)][-MAX_HISTORY:]

# ---------------------------------------------------------------- TWELVE DATA
def td_params(a):
    p = {"symbol": a.get("apiSymbol") or a["symbol"], "apikey": TD_KEY}
    if a.get("exchange"): p["exchange"] = a["exchange"]
    if a.get("mic"):      p["mic_code"] = a["mic"]
    return p

def td_price(a):
    url = "https://api.twelvedata.com/price?" + urllib.parse.urlencode(td_params(a))
    try:
        d = get_json(url)
        if isinstance(d, dict) and "price" in d:
            return float(d["price"])
        print("  ! %s (TD): risposta senza prezzo: %s" % (a["symbol"], str(d)[:110]))
    except Exception as e:
        print("  ! %s (TD): errore %s" % (a["symbol"], e))
    return None

def td_series(a):
    p = td_params(a); p["interval"] = "1day"; p["outputsize"] = "380"
    url = "https://api.twelvedata.com/time_series?" + urllib.parse.urlencode(p)
    try:
        d = get_json(url)
        vals = d.get("values") if isinstance(d, dict) else None
        if not vals:
            print("  ! %s (TD): nessuno storico: %s" % (a["symbol"], str(d)[:110]))
            return None
        out = []
        for v in reversed(vals):
            try: out.append([str(v["datetime"])[:10], float(v["close"])])
            except Exception: pass
        return out or None
    except Exception as e:
        print("  ! %s (TD): errore storico %s" % (a["symbol"], e))
    return None

# -------------------------------------------------------------- ALPHA VANTAGE
def av_limit_hit(d):
    if not isinstance(d, dict): return False
    for k in ("Note", "Information"):
        if k in d and ("limit" in str(d[k]).lower() or "frequency" in str(d[k]).lower()):
            return True
    return False

def av_resolve(a):
    kw = a.get("avQuery") or a.get("name") or a["symbol"]
    url = ("https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords="
           + urllib.parse.quote(kw) + "&apikey=" + AV_KEY)
    try:
        d = get_json(url)
        if av_limit_hit(d): return "LIMIT"
        best, score = None, -1
        for m in (d.get("bestMatches") or []):
            sym = m.get("1. symbol", "")
            reg = m.get("4. region", "")
            cur = m.get("8. currency", "")
            try: ms = float(m.get("9. matchScore", 0))
            except Exception: ms = 0
            s = ms
            if a.get("region") and a["region"].lower()[:4] in reg.lower(): s += 1.0
            if cur and cur == a.get("currency"): s += 0.5
            if sym.upper().startswith(a["symbol"].upper()): s += 0.3
            if s > score: best, score = sym, s
        if best:
            print("  \u21aa %s (AV): simbolo trovato -> %s" % (a["symbol"], best))
        else:
            print("  ! %s (AV): nessun simbolo trovato per '%s'" % (a["symbol"], kw))
        return best
    except Exception as e:
        print("  ! %s (AV): errore ricerca %s" % (a["symbol"], e))
    return None

def av_series(sym):
    url = ("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol="
           + urllib.parse.quote(sym) + "&outputsize=compact&apikey=" + AV_KEY)
    try:
        d = get_json(url)
        if av_limit_hit(d): return "LIMIT"
        ts = d.get("Time Series (Daily)") if isinstance(d, dict) else None
        if not ts:
            print("  ! %s (AV): nessuno storico: %s" % (sym, str(d)[:110]))
            return None
        out = []
        for day, row in ts.items():
            try: out.append([str(day)[:10], float(row["4. close"])])
            except Exception: pass
        out.sort()
        return out or None
    except Exception as e:
        print("  ! %s (AV): errore %s" % (sym, e))
    return None

# ------------------------------------------------------------------------ FX
def fetch_fx(currencies):
    fx = {"EUR": 1.0}
    others = sorted(c for c in currencies if c and c != "EUR")
    if not others: return fx
    url = "https://api.frankfurter.app/latest?base=EUR&symbols=" + ",".join(others)
    try:
        d = get_json(url)
        for c, r in (d.get("rates") or {}).items():
            if r: fx[c] = round(1.0 / float(r), 8)
    except Exception as e:
        print("  ! FX errore %s" % e)
    return fx

# ---------------------------------------------------------------------- MAIN
def main():
    assets = json.load(open(TICKERS, encoding="utf-8")).get("assets", [])
    today  = datetime.date.today().isoformat()

    prev = {}
    if os.path.exists(PREZZI):
        try: prev = json.load(open(PREZZI, encoding="utf-8")).get("prices", {})
        except Exception: prev = {}

    prices = {}
    for a in assets:
        old = prev.get(a["symbol"].upper(), {})
        prices[a["symbol"].upper()] = {
            "price":    old.get("price"),
            "currency": a.get("currency", "EUR"),
            "asof":     old.get("asof"),
            "avSymbol": old.get("avSymbol"),
            "history":  list(old.get("history", [])),
        }

    td = [a for a in assets if a.get("source", "twelvedata") == "twelvedata"]
    print("== Twelve Data: %d asset ==" % len(td))
    used = 0
    if not TD_KEY:
        print("  (TWELVE_DATA_KEY assente: salto, mantengo i prezzi esistenti)")
    else:
        for a in td:
            if used >= TD_BUDGET:
                print("  (budget giornaliero Twelve Data esaurito)"); break
            sym = a["symbol"].upper(); e = prices[sym]
            if len(e["history"]) < BACKFILL_IF_UNDER:
                s = td_series(a); used += 1; time.sleep(TD_PAUSA)
                if s:
                    e["history"] = merge_hist(e["history"], s)
                    e["price"], e["asof"] = e["history"][-1][1], e["history"][-1][0]
                    print("  \u21ba %s: storico (%d punti)" % (sym, len(e["history"])))
                    continue
            p = td_price(a); used += 1; time.sleep(TD_PAUSA)
            if p is None:
                print("  = %s: invariato (ultimo noto %s)" % (sym, e["price"]))
            else:
                e["history"] = merge_hist(e["history"], [[today, p]])
                e["price"], e["asof"] = p, today
                print("  + %s: %s %s" % (sym, p, a.get("currency", "")))
    print("   richieste Twelve Data usate: %d" % used)

    av = [a for a in assets if a.get("source") == "alphavantage"]
    print("== Alpha Vantage (Europa): %d asset, budget %d/giorno ==" % (len(av), AV_BUDGET))
    if not AV_KEY:
        print("  (ALPHA_VANTAGE_KEY assente: salto, mantengo i prezzi esistenti)")
    else:
        av.sort(key=lambda a: (prices[a["symbol"].upper()].get("asof") or "0000-00-00"))
        used = 0
        for a in av:
            if used >= AV_BUDGET:
                print("  (budget Alpha Vantage esaurito: gli altri toccheranno domani)"); break
            sym = a["symbol"].upper(); e = prices[sym]
            if e.get("asof") == today: continue
            if not e.get("avSymbol"):
                r = av_resolve(a); used += 1; time.sleep(AV_PAUSA)
                if r == "LIMIT":
                    print("  (limite Alpha Vantage raggiunto)"); break
                if not r: continue
                e["avSymbol"] = r
                if used >= AV_BUDGET: continue
            s = av_series(e["avSymbol"]); used += 1; time.sleep(AV_PAUSA)
            if s == "LIMIT":
                print("  (limite Alpha Vantage raggiunto)"); break
            if not s:
                print("  = %s: invariato (ultimo noto %s)" % (sym, e["price"])); continue
            e["history"] = merge_hist(e["history"], s)
            e["price"], e["asof"] = e["history"][-1][1], e["history"][-1][0]
            print("  + %s (%s): %s %s" % (sym, e["avSymbol"], e["price"], a.get("currency", "")))
        print("   richieste Alpha Vantage usate: %d" % used)

    fx = fetch_fx(set(a.get("currency", "EUR") for a in assets))
    catalog = [{"symbol": a["symbol"], "name": a.get("name", ""), "kind": a.get("kind", "other"),
                "currency": a.get("currency", "EUR"), "desc": a.get("desc", "")} for a in assets]
    out = {"updatedAt": today, "fxToEur": fx, "catalog": catalog, "prices": prices}
    json.dump(out, open(PREZZI, "w", encoding="utf-8"), ensure_ascii=False, separators=(',', ':'))

    agg = sum(1 for v in prices.values() if v.get("asof") == today)
    vuoti = sum(1 for v in prices.values() if v.get("price") is None)
    print("OK: prezzi.json scritto - %d asset (%d aggiornati oggi, %d senza prezzo), valute %s"
          % (len(prices), agg, vuoti, ",".join(sorted(fx.keys()))))

if __name__ == "__main__":
    main()
