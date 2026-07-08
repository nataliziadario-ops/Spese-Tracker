# Guida all'aggiornamento — Restyling v10

## Cosa contiene questo pacchetto

| File | Cosa è cambiato |
|---|---|
| `index.html` | Tutte le novità: tema scuro, profilo, dashboard, slider, swipe, pull-to-refresh |
| `service-worker.js` | Cache portata a `spese-tracker-v10` (obbligatorio per vedere l'aggiornamento) |
| `manifest.json` | Colore di sfondo allineato alla nuova grafica |
| `favicon.png`, `icon-192.png`, `icon-512.png`, `icon-512-maskable.png`, `apple-touch-icon.png` | La nuova icona |

## Le novità in breve

1. **Tema scuro** — dal Profilo (cerchio in alto a destra) scegli Chiaro, Scuro o Automatico (segue il telefono).
2. **Sezione Profilo** — tocca il cerchio in alto a destra: nome, tema, e da lì si aprono Budget e Conti.
3. **Budget spostato nel Profilo** — non occupa più una scheda: si apre come pannello dal basso, e ora i limiti si impostano anche **trascinando lo slider**.
4. **Dashboard** — nuova scheda al posto di Budget: patrimonio complessivo, carosello dei conti, entrate/uscite del mese, media giornaliera, previsione di fine mese, grafico degli ultimi 6 mesi (tocca le barre per i valori), ripartizione per categoria e top spese.
5. **Swipe tra le schede** — scorri col dito a destra/sinistra sul contenuto per cambiare scheda.
6. **Rotellina di aggiornamento** — nelle schede, trascina verso il basso dalla cima della pagina e rilascia: la rotellina gira e l'app si aggiorna (se la sincronizzazione è attiva, riscarica anche i dati dal cloud).
7. **Nuova icona** — monogramma € su verde profondo, coerente in tutte le misure.

## Cosa NON è cambiato

Nessuna funzione è stata toccata: movimenti, conti, categorie, tag, ricerca, importazione CSV, sincronizzazione Firebase, registrazione da notifiche e inserimento manuale PayPal funzionano esattamente come prima. I dati salvati sul telefono e sul cloud restano identici.

## Come pubblicare su GitHub (passo per passo)

1. Apri il repository **Spese-Tracker** su GitHub e accedi.
2. Clicca **Add file → Upload files**.
3. Trascina **tutti i file di questo zip insieme** (index.html, service-worker.js, manifest.json e le 5 icone).
4. Scrivi un messaggio tipo "Restyling v10" e clicca **Commit changes**.
5. **Controllo importante** (lezione imparata l'altra volta): apri la lista dei file nel repository e verifica che `index.html` risulti di circa **156 KB** e `service-worker.js` di circa **1,7 KB**. Se uno risulta 0 byte, ricaricalo da solo.
6. Il file `.nojekyll` deve restare nel repository (non toccarlo).
7. Attendi 1–2 minuti, poi apri l'app. Se non vedi le novità: chiudi completamente l'app/scheda e riaprila (la cache v10 forza il refresh al secondo avvio). Per vedere subito la nuova icona su iPhone può servire rimuovere l'app dalla schermata Home e aggiungerla di nuovo da Safari.

## Verifiche consigliate dopo la pubblicazione

- Il cerchio del profilo in alto a destra si apre e il tema Scuro funziona.
- Dal Profilo → Budget mensili: gli slider muovono i limiti e il numero si aggiorna.
- La scheda Dashboard mostra i grafici con i tuoi dati reali.
- Swipe destra/sinistra cambia scheda; trascinando in giù compare la rotellina.
- Conto PayPal, campo Esercente e Nota: tutto come prima.
