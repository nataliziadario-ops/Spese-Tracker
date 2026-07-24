#!/usr/bin/env python3
# Robot prezzi Spendy: legge tickers.json, scarica prezzi e storico
# (Twelve Data) e i cambi valuta (BCE via Frankfurter), aggiorna prezzi.json.
# La PRIMA volta per ogni asset scarica ~1 anno di storico giornaliero;
# dai giorni successivi aggiunge solo il prezzo del giorno.
# Nessuna dipendenza esterna: solo libreria standard di Python.
import json, os, sys, time, urllib.request, urllib.parse, datetime, ssl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TICKERS = os.path.join(ROOT, "tickers.json")
PREZZI  = os.path.join(ROOT, "prezzi.json")
KEY = os.environ.get("TWELVE_DATA_KEY", "").strip()
MAX_HISTORY = 400          # quanti punti tenere al massimo
BACKFILL_IF_UNDER = 250    # se lo storico ha meno punti di cosi', scarica 1 anno
PAUSA = 8                  # secondi tra le richieste (limite gratuito: 8/minuto)
CTX = ssl.create_default_context()

def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "spendy-price-bot"})
    with urllib.request.urlopen(req, timeout=30, context=CTX) as r:
        return json.loads(r.read().decode("utf-8"))

def _params(asset):
    p = {"symbol": asset.get("apiSymbol") or asset["symbol"], "apikey": KEY}
    if asset.get("exchange"): p["exchange"] = asset["exchange"]
    if asset.get("mic"):      p["mic_code"] = asset["mic"]
    return p

def fetch_price(asset):
    """Prezzo attuale (float) o None."""
    if not KEY: return None
    url = "https://api.twelvedata.com/price?" + urllib.parse.urlencode(_params(asset))
    try:
        d = get_json(url)
        if isinstance(d, dict) and "price" in d:
            return float(d["price"])
        print("  ! %s: risposta senza prezzo: %s" % (asset["symbol"], str(d)[:120]))
    except Exception as e:
        print("  ! %s: errore %s" % (asset["symbol"], e))
    return None

def fetch_series(asset):
    """~1 anno di chiusure giornaliere: [[data, prezzo], ...] crescente, o None."""
    if not KEY: return None
    p = _params(asset); p["interval"] = "1day"; p["outputsize"] = "380"
    url = "https://api.twelvedata.com/time_series?" + urllib.parse.urlencode(p)
    try:
        d = get_json(url)
        vals = d.get("values") if isinstance(d, dict) else None
        if not vals:
            print("  ! %s: nessuno storico: %s" % (asset["symbol"], str(d)[:120]))
            return None
        out = []
        for v in reversed(vals):
            try: out.append([str(v["datetime"])[:10], float(v["close"])])
            except Exception: pass
        return out or None
    except Exception as e:
        print("  ! %s: errore storico %s" % (asset["symbol"], e))
    return None

def fetch_fx(currencies):
    fx = {"EUR": 1.0}
    others = sorted(c for c in currencies if c and c != "EUR")
    if not others: return fx
    url = "https://api.frankfurter.app/latest?base=EUR&symbols=" + ",".join(others)
    try:
        d = get_json(url); rates = d.get("rates", {})
        for c in others:
            r = rates.get(c)
            if r: fx[c] = round(1.0 / float(r), 8)   # 1 c = 1/r EUR
    except Exception as e:
        print("  ! FX errore %s" % e)
    return fx

def main():
    tick = json.load(open(TICKERS, encoding="utf-8"))
    assets = tick.get("assets", [])
    today = datetime.date.today().isoformat()

    prev = {}
    if os.path.exists(PREZZI):
        try: prev = json.load(open(PREZZI, encoding="utf-8")).get("prices", {})
        except Exception: prev = {}

    prices = {}
    for a in assets:
        sym = a["symbol"].upper()
        old = prev.get(sym, {})
        hist = list(old.get("history", []))
        asof = old.get("asof")
        price = old.get("price")
        done = False

        # Prima volta (o storico corto): scarica ~1 anno in un colpo solo
        if KEY and len(hist) < BACKFILL_IF_UNDER:
            series = fetch_series(a); time.sleep(PAUSA)
            if series:
                merged = {p[0]: p[1] for p in hist}
                for p in series: merged[p[0]] = p[1]
                hist = [[d, merged[d]] for d in sorted(merged)][-MAX_HISTORY:]
                price = hist[-1][1]; asof = hist[-1][0]; done = True
                print("  \u21ba %s: storico scaricato (%d punti, fino al %s)" % (sym, len(hist), asof))

        # Giorni normali: solo il prezzo di oggi
        if not done:
            p = fetch_price(a); time.sleep(PAUSA)
            if p is None:
                print("  = %s: prezzo non aggiornato (uso ultimo noto: %s)" % (sym, price))
            else:
                price = p
                if hist and hist[-1][0] == today: hist[-1] = [today, price]
                else: hist.append([today, price])
                hist = hist[-MAX_HISTORY:]; asof = today
                print("  + %s: %s %s" % (sym, price, a.get("currency", "")))

        prices[sym] = {"price": price, "currency": a.get("currency", "EUR"), "asof": asof, "history": hist}

    fx = fetch_fx(set(a.get("currency", "EUR") for a in assets))
    catalog = [{"symbol": a["symbol"], "name": a.get("name", ""), "kind": a.get("kind", "other"),
                "currency": a.get("currency", "EUR"), "desc": a.get("desc", "")} for a in assets]
    out = {"updatedAt": today, "fxToEur": fx, "catalog": catalog, "prices": prices}
    json.dump(out, open(PREZZI, "w", encoding="utf-8"), ensure_ascii=False, separators=(',', ':'))
    print("OK: prezzi.json aggiornato (%d asset, valute %s)" % (len(prices), ",".join(sorted(fx.keys()))))

if __name__ == "__main__":
    main()
