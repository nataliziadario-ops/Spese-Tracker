#!/usr/bin/env python3
# Robot prezzi Spendy — DUE FONTI FUSE
#
#   • Twelve Data   → azioni USA, ETF USA e cripto. Aggiornati OGNI GIORNO.
#                     Piano gratuito: 8 richieste/minuto, 800/giorno.
#   • Alpha Vantage → azioni ed ETF EUROPEI. Aggiornati OGNI GIORNO.
#                     Piano gratuito: 25 richieste/giorno, 5/minuto.
#                     Il listino europeo e' stato ridotto a 24 asset con
#                     simbolo Alpha Vantage GIA' FISSATO in tickers.json
#                     (campo "avSymbol"): una richiesta a testa, nessuna
#                     ricerca sprecata, tutti aggiornati tutti i giorni.
#                     Gli asset con "source":"alphavantage" vanno dritti qui
#                     senza passare da Twelve Data (che non li copre).
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
TD_PAUSA          = 9      # 9s = poco sotto il limite di 8 richieste/minuto
TD_ATTESA_LIMITE  = 65     # attesa quando il servizio dice "limite raggiunto"
TD_BUDGET         = int(os.environ.get("TD_BUDGET", "700"))
AV_PAUSA          = 13
AV_BUDGET         = int(os.environ.get("AV_BUDGET", "25"))
MODO              = os.environ.get("MODO", "completo").strip().lower()   # 'veloce' | 'completo'
SOLO_MANCANTI     = os.environ.get("SOLO_MANCANTI", "0").strip() == "1"
CTX = ssl.create_default_context()

def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "spendy-price-bot"})
    with urllib.request.urlopen(req, timeout=30, context=CTX) as r:
        return json.loads(r.read().decode("utf-8"))

def td_limit_hit(d):
    """Twelve Data segnala il limite con code 429 o un messaggio esplicito."""
    if not isinstance(d, dict): return False
    if str(d.get("code")) == "429": return True
    m = str(d.get("message", "")).lower()
    return "api credits" in m or "rate limit" in m

def merge_hist(old, new):
    m = {p[0]: p[1] for p in (old or []) if p and len(p) == 2}
    for p in (new or []):
        if p and len(p) == 2:
            m[p[0]] = p[1]
    return [[d, m[d]] for d in sorted(m)][-MAX_HISTORY:]

# ---------------------------------------------------------------- TWELVE DATA
def td_varianti(a):
    """Combinazioni da provare, in ordine: con la borsa indicata, poi senza,
    poi eventuali simboli alternativi. Serve perche' alcuni codici di borsa
    non sono riconosciuti dal servizio."""
    base = a.get("apiSymbol") or a["symbol"]
    simboli = [base] + [x for x in (a.get("alt") or []) if x != base]
    out = []
    for sim in simboli:
        b = {"symbol": sim, "apikey": TD_KEY}
        if a.get("exchange"):     out.append(dict(b, exchange=a["exchange"]))       # borsa USA
        if a.get("mic"):          out.append(dict(b, mic_code=a["mic"]))            # codice MIC
        if a.get("exchangeName"): out.append(dict(b, exchange=a["exchangeName"]))   # nome borsa
        if a.get("country"):      out.append(dict(b, country=a["country"]))         # paese
        out.append(dict(b))                                                          # solo simbolo
    # elimina i doppioni mantenendo l'ordine
    viste, uniche = set(), []
    for p in out:
        k = (p.get("symbol"), p.get("exchange"), p.get("mic_code"))
        if k not in viste: viste.add(k); uniche.append(p)
    return uniche

def descrivi(p):
    if p.get("mic_code"):  return "borsa " + p["mic_code"]
    if p.get("exchange"):  return "borsa " + p["exchange"]
    if p.get("country"):   return "paese " + p["country"]
    return "solo sigla"

def valuta_ok(a, trovata):
    """Se il servizio dice in che valuta quota, controlla che sia quella attesa:
    evita di prendere un titolo omonimo su un'altra borsa."""
    attesa = (a.get("currency") or "").upper()
    return (not trovata) or (not attesa) or (str(trovata).upper() == attesa)

def td_quote_una(a, params):
    """Una singola richiesta 'quote': ritorna (prezzo, richieste_usate) oppure (None, n)."""
    url = "https://api.twelvedata.com/quote?" + urllib.parse.urlencode(params)
    usate = 0
    for n in range(3):
        try:
            d = get_json(url); usate += 1
            if isinstance(d, dict) and d.get("close") not in (None, ""):
                if not valuta_ok(a, d.get("currency")):
                    print("  ! %s (TD): valuta %s diversa da %s, scarto"
                          % (a["symbol"], d.get("currency"), a.get("currency")))
                    return None, usate
                return float(d["close"]), usate
            if td_limit_hit(d) and n < 2:
                print("  ~ limite Twelve Data: attendo %ds e riprovo" % TD_ATTESA_LIMITE)
                time.sleep(TD_ATTESA_LIMITE); continue
            return None, usate
        except Exception as e:
            print("  ! %s (TD): errore %s" % (a["symbol"], e)); return None, usate
    return None, usate

def td_price(a, cache=None):
    """Prova le varianti finche' una risponde. Ritorna (prezzo, variante, richieste)."""
    varianti = td_varianti(a)
    if cache is not None and 0 <= cache < len(varianti):
        varianti = [varianti[cache]] + [v for i, v in enumerate(varianti) if i != cache]
    tot = 0
    for i, p in enumerate(varianti):
        v, u = td_quote_una(a, p); tot += u
        if v is not None:
            idx = td_varianti(a).index(p)
            if i > 0: print("  \u21bb %s: riuscito con %s (%s)" % (a["symbol"], descrivi(p), p.get("symbol")))
            return v, idx, tot
        time.sleep(TD_PAUSA)
    print("  ! %s (TD): nessuna variante ha funzionato" % a["symbol"])
    return None, None, tot

def td_series_una(a, params):
    p = dict(params); p["interval"] = "1day"; p["outputsize"] = "380"
    url = "https://api.twelvedata.com/time_series?" + urllib.parse.urlencode(p)
    usate = 0
    for n in range(3):
        try:
            d = get_json(url); usate += 1
            vals = d.get("values") if isinstance(d, dict) else None
            if vals:
                meta = d.get("meta") or {}
                if not valuta_ok(a, meta.get("currency")):
                    print("  ! %s (TD): valuta %s diversa da %s, scarto"
                          % (a["symbol"], meta.get("currency"), a.get("currency")))
                    return None, usate
                out = []
                for v in reversed(vals):
                    try: out.append([str(v["datetime"])[:10], float(v["close"])])
                    except Exception: pass
                return (out or None), usate
            if td_limit_hit(d) and n < 2:
                print("  ~ limite Twelve Data: attendo %ds e riprovo" % TD_ATTESA_LIMITE)
                time.sleep(TD_ATTESA_LIMITE); continue
            return None, usate
        except Exception as e:
            print("  ! %s (TD): errore storico %s" % (a["symbol"], e)); return None, usate
    return None, usate

def td_series(a, cache=None):
    varianti = td_varianti(a)
    if cache is not None and 0 <= cache < len(varianti):
        varianti = [varianti[cache]] + [v for i, v in enumerate(varianti) if i != cache]
    tot = 0
    for i, p in enumerate(varianti):
        s, u = td_series_una(a, p); tot += u
        if s:
            idx = td_varianti(a).index(p)
            if i > 0: print("  \u21bb %s: storico riuscito con %s (%s)" % (a["symbol"], descrivi(p), p.get("symbol")))
            return s, idx, tot
        time.sleep(TD_PAUSA)
    print("  ! %s (TD): nessuna variante ha funzionato per lo storico" % a["symbol"])
    return None, None, tot

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
        attesa = (a.get("currency") or "").upper()
        for m in (d.get("bestMatches") or []):
            sym = m.get("1. symbol", "")
            reg = m.get("4. region", "")
            cur = (m.get("8. currency", "") or "").upper()
            # scarta chi quota in una valuta diversa da quella attesa
            if attesa and cur and cur != attesa:
                continue
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

def av_quote(sym):
    """Solo il prezzo di oggi: 1 richiesta invece dello storico."""
    url = ("https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol="
           + urllib.parse.quote(sym) + "&apikey=" + AV_KEY)
    try:
        d = get_json(url)
        if av_limit_hit(d): return "LIMIT"
        q = d.get("Global Quote") or {}
        pr = q.get("05. price"); day = q.get("07. latest trading day")
        if pr and day:
            return [[str(day)[:10], float(pr)]]
        print("  ! %s (AV): quotazione non disponibile" % sym)
    except Exception as e:
        print("  ! %s (AV): errore %s" % (sym, e))
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
            "tdVar":    old.get("tdVar"),
            "history":  list(old.get("history", [])),
        }

    def priorita(a):
        e = prices[a["symbol"].upper()]
        manca = 0 if not isinstance(e.get("price"), (int, float)) else 1
        return (manca, e.get("asof") or "0000-00-00")

    td = [a for a in assets if a.get("source", "twelvedata").startswith("twelvedata")]
    # Europei "diretti": Twelve Data non li copre, si va subito su Alpha Vantage.
    av_diretti = [a for a in assets if a.get("source", "") == "alphavantage"]
    if SOLO_MANCANTI:
        td = [a for a in td if not isinstance(prices[a["symbol"].upper()].get("price"), (int, float))
              or prices[a["symbol"].upper()].get("asof") != today]
    td.sort(key=priorita)
    av_riserva = []   # asset europei per cui Twelve Data non ha dato prezzo
    print("== MODALITA': %s%s ==" % (MODO, " (solo mancanti/non aggiornati)" if SOLO_MANCANTI else ""))
    print("== Twelve Data: %d asset da lavorare (prima quelli senza prezzo) ==" % len(td))
    used = 0
    if not TD_KEY:
        print("  (TWELVE_DATA_KEY assente: salto, mantengo i prezzi esistenti)")
    else:
        for a in td:
            if used >= TD_BUDGET:
                print("  (budget giornaliero Twelve Data esaurito)"); break
            sym = a["symbol"].upper(); e = prices[sym]
            if MODO != "veloce" and len(e["history"]) < BACKFILL_IF_UNDER:
                s, var, u = td_series(a, e.get("tdVar")); used += u; time.sleep(TD_PAUSA)
                if s:
                    e["tdVar"] = var
                    e["history"] = merge_hist(e["history"], s)
                    e["price"], e["asof"] = e["history"][-1][1], e["history"][-1][0]
                    print("  \u21ba %s: storico (%d punti, fino al %s)" % (sym, len(e["history"]), e["asof"]))
                    continue
                if "alphavantage" in a.get("source", ""):
                    av_riserva.append(a); print("  \u2192 %s: Twelve Data non copre, provo con Alpha Vantage" % sym)
                    continue
            p, var, u = td_price(a, e.get("tdVar")); used += u; time.sleep(TD_PAUSA)
            if p is not None: e["tdVar"] = var
            if p is None:
                if "alphavantage" in a.get("source", ""):
                    av_riserva.append(a)
                    print("  \u2192 %s: Twelve Data non copre, provo con Alpha Vantage" % sym)
                else:
                    print("  = %s: invariato (ultimo noto %s)" % (sym, e["price"]))
            else:
                e["history"] = merge_hist(e["history"], [[today, p]])
                e["price"], e["asof"] = p, today
                print("  + %s: %s %s" % (sym, p, a.get("currency", "")))
    print("   richieste Twelve Data usate: %d" % used)

    visti = set()
    av = []
    for a in av_diretti + av_riserva:
        s = a["symbol"].upper()
        if s not in visti:
            visti.add(s); av.append(a)
    print("== Alpha Vantage (Europa): %d asset (%d diretti + %d di riserva), budget %d/giorno =="
          % (len(av), len(av_diretti), len(av_riserva), AV_BUDGET))
    if len(av) > AV_BUDGET:
        print("  ATTENZIONE: piu' asset che richieste disponibili: gli ultimi slittano a domani.")
    if not av:
        print("  (nessuno da lavorare)")
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
            # Simbolo fissato a mano in tickers.json: vale piu' della ricerca
            # automatica (che a volte agganciava il titolo sbagliato) e non
            # costa richieste.
            if a.get("avSymbol"): e["avSymbol"] = a["avSymbol"]
            if not e.get("avSymbol"):
                r = av_resolve(a); used += 1; time.sleep(AV_PAUSA)
                if r == "LIMIT":
                    print("  (limite Alpha Vantage raggiunto)"); break
                if not r: continue
                e["avSymbol"] = r
                if used >= AV_BUDGET: continue
            s = (av_quote(e["avSymbol"]) if MODO == "veloce" else av_series(e["avSymbol"]))
            used += 1; time.sleep(AV_PAUSA)
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
                "currency": a.get("currency", "EUR"), "desc": a.get("desc", ""),
                "isin": a.get("isin", "")} for a in assets]
    out = {"updatedAt": today, "fxToEur": fx, "catalog": catalog, "prices": prices}
    json.dump(out, open(PREZZI, "w", encoding="utf-8"), ensure_ascii=False, separators=(',', ':'))

    agg = sum(1 for v in prices.values() if v.get("asof") == today)
    vuoti = sum(1 for v in prices.values() if v.get("price") is None)
    print("OK: prezzi.json scritto - %d asset (%d aggiornati oggi, %d senza prezzo), valute %s"
          % (len(prices), agg, vuoti, ",".join(sorted(fx.keys()))))
    mancanti = sorted(s for s, v in prices.items() if v.get("price") is None)
    if mancanti:
        print("ANCORA SENZA PREZZO (%d): %s" % (len(mancanti), ", ".join(mancanti)))
    senza_storico = sorted(s for s, v in prices.items() if len(v.get("history", [])) < 5)
    if senza_storico:
        print("SENZA STORICO (%d): serve un giro in modalita' completa" % len(senza_storico))

if __name__ == "__main__":
    main()
