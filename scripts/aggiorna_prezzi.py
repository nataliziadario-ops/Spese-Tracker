#!/usr/bin/env python3
# Robot prezzi Spendy: legge tickers.json, scarica i prezzi (Twelve Data)
# e i cambi valuta (BCE via Frankfurter), aggiorna prezzi.json alla radice.
# Nessuna dipendenza esterna: usa solo la libreria standard di Python.
import json, os, sys, time, urllib.request, urllib.parse, datetime, ssl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TICKERS = os.path.join(ROOT, "tickers.json")
PREZZI  = os.path.join(ROOT, "prezzi.json")
KEY = os.environ.get("TWELVE_DATA_KEY", "").strip()
MAX_HISTORY = 400
CTX = ssl.create_default_context()

def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "spendy-price-bot"})
    with urllib.request.urlopen(req, timeout=30, context=CTX) as r:
        return json.loads(r.read().decode("utf-8"))

def fetch_price(asset):
    """Ritorna il prezzo (float) o None se non disponibile."""
    if not KEY:
        return None
    params = {"symbol": asset.get("apiSymbol") or asset["symbol"], "apikey": KEY}
    if asset.get("exchange"): params["exchange"] = asset["exchange"]
    if asset.get("mic"):      params["mic_code"] = asset["mic"]
    url = "https://api.twelvedata.com/price?" + urllib.parse.urlencode(params)
    try:
        d = get_json(url)
        if isinstance(d, dict) and "price" in d:
            return float(d["price"])
        print("  ! %s: risposta senza prezzo: %s" % (asset["symbol"], str(d)[:120]))
    except Exception as e:
        print("  ! %s: errore %s" % (asset["symbol"], e))
    return None

def fetch_fx(currencies):
    fx = {"EUR": 1.0}
    others = sorted(c for c in currencies if c and c != "EUR")
    if not others:
        return fx
    url = "https://api.frankfurter.app/latest?base=EUR&symbols=" + ",".join(others)
    try:
        d = get_json(url)
        rates = d.get("rates", {})
        for c in others:
            r = rates.get(c)
            if r:  # 1 EUR = r unita' di c  ->  1 c = 1/r EUR
                fx[c] = round(1.0 / float(r), 8)
    except Exception as e:
        print("  ! FX errore %s" % e)
    return fx

def main():
    tick = json.load(open(TICKERS, encoding="utf-8"))
    assets = tick.get("assets", [])
    today = datetime.date.today().isoformat()

    prev = {}
    if os.path.exists(PREZZI):
        try:
            prev = json.load(open(PREZZI, encoding="utf-8")).get("prices", {})
        except Exception:
            prev = {}

    prices = {}
    for a in assets:
        sym = a["symbol"].upper()
        old = prev.get(sym, {})
        hist = list(old.get("history", []))
        price = fetch_price(a)
        if price is None:
            # nessun prezzo oggi: mantengo l'ultimo noto, non aggiungo punti sbagliati
            price = old.get("price")
            print("  = %s: prezzo non aggiornato (uso ultimo noto: %s)" % (sym, price))
        else:
            # aggiorno/aggiungo il punto di oggi
            if hist and hist[-1][0] == today:
                hist[-1] = [today, price]
            else:
                hist.append([today, price])
            hist = hist[-MAX_HISTORY:]
            print("  + %s: %s %s" % (sym, price, a.get("currency", "")))
        prices[sym] = {"price": price, "currency": a.get("currency", "EUR"), "history": hist}
        time.sleep(8)  # rispetta il limite gratuito (max 8 richieste/minuto)

    currencies = set(a.get("currency", "EUR") for a in assets)
    fx = fetch_fx(currencies)

    catalog = [{"symbol": a["symbol"], "name": a.get("name", ""),
                "kind": a.get("kind", "other"), "currency": a.get("currency", "EUR")}
               for a in assets]

    out = {"updatedAt": today, "fxToEur": fx, "catalog": catalog, "prices": prices}
    json.dump(out, open(PREZZI, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("OK: prezzi.json aggiornato (%d asset, valute %s)" % (len(prices), ",".join(sorted(fx.keys()))))

if __name__ == "__main__":
    main()
