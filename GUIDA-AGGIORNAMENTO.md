# Guida all'aggiornamento — v11 (ricorrenti, home, fix)

## File del pacchetto
index.html · service-worker.js (cache **spese-tracker-v11**) · manifest.json · le 5 icone · questa guida.

## Cosa cambia in questa versione

### Correzioni
1. **Fogli chiudibili con lo swipe verso il basso** — quando un menù/foglio è aperto e già in cima, puoi trascinarlo verso il basso col dito per chiuderlo (oltre a toccare fuori). Vale per spesa, budget, profilo, ricorrenti, sincronizzazione e importazione.
2. **Budget non "sfarfalla" più** — muovendo lo slider o scrivendo l'importo, ora si aggiorna solo la barra della categoria toccata: niente ricaricamento dell'intera pagina né scroll che salta.

### Novità
3. **Nuova categoria al volo mentre crei una spesa** — nella schermata della spesa, accanto alle categorie c'è il chip **"+ Nuova"**: aggiungi nome, emoji e colore senza uscire (come già facevi per i tag). La stessa cosa è disponibile anche quando crei un pagamento ricorrente.
4. **Home = Dashboard + Riepilogo (prima pagina)** — la prima scheda ora mostra in un colpo solo: patrimonio complessivo, conti scorrevoli, prossimi pagamenti ricorrenti, media giornaliera e previsione di fine mese, grafico degli ultimi 6 mesi e, sotto, il riepilogo Mensile/Annuale con donut, avvisi budget e movimenti (tutto quello che c'era prima nel "Riepilogo").
5. **Nuova scheda "Ricorrenti"** — per abbonamenti, rate, tasse e bollette fisse. Ogni voce mostra categoria, frequenza, prossima scadenza, importo e stato (con badge **SCADUTA** in rosso). Filtri Tutti / Attivi / In pausa. In alto la spesa ricorrente stimata al mese e all'anno.
   - Tocca **"Segna pagato"** (o **"Registra"** se è scaduto): l'app **crea un vero movimento** sul conto scelto — quindi entra in saldi, totali e storico — con associata la data di ricorrenza, e sposta la scadenza a quella successiva. I movimenti creati così hanno un piccolo simbolo ↻ nello storico.

Nuova barra in basso: **Home · Storico · (+) · Ricorrenti · Conti**. Il Budget resta nel Profilo (in alto a destra).

## Cosa NON è cambiato
Dati, conti, categorie, tag, ricerca, importazione CSV, sincronizzazione Firebase, notifiche e inserimento manuale PayPal funzionano come prima. I dati già salvati (telefono e cloud) restano intatti: i ricorrenti sono un elenco nuovo che parte vuoto.

## Pubblicazione su GitHub (passo per passo)
1. Repository **Spese-Tracker** → **Add file → Upload files**.
2. Trascina **tutti i file insieme** (index.html, service-worker.js, manifest.json, le 5 icone).
3. Messaggio "v11 ricorrenti" → **Commit changes**.
4. **Controllo dimensioni** (lezione delle volte scorse): `index.html` deve pesare circa **180 KB**, `service-worker.js` ~1,7 KB. Se uno risulta 0 byte, ricaricalo da solo.
5. Lascia il file `.nojekyll` dov'è.
6. Riapri l'app: se non vedi le novità, chiudila del tutto e riaprila (la cache v11 forza il refresh al secondo avvio).

## Verifiche consigliate
- Barra: Home · Storico · Ricorrenti · Conti.
- In un foglio aperto, trascina in giù dall'alto: si chiude.
- Budget (Profilo → Budget): muovi uno slider, la pagina non sfarfalla.
- Nuova spesa → "+ Nuova" categoria: si aggiunge e resta selezionata.
- Ricorrenti → aggiungi un abbonamento → "Segna pagato": compare un movimento nello storico e la scadenza avanza.
