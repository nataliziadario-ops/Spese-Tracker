# Spese — Tracker (versione GitHub Pages / PWA)

Questa cartella contiene tutto il necessario per pubblicare l'app su GitHub Pages e installarla come app vera sia da telefono che da PC. Nessuna conoscenza di programmazione richiesta..

## Cosa contiene la cartella

```
spese-tracker-pwa/
├── index.html            → l'app vera e propria (con sincronizzazione cloud opzionale)
├── manifest.json         → dice al telefono/PC come installare l'app (nome, icona, colori)
├── service-worker.js     → permette all'app di funzionare anche offline
├── GUIDA-FIREBASE.md     → come attivare la sincronizzazione tra dispositivi (opzionale)
├── .nojekyll             → dice a GitHub Pages di servire i file così come sono
├── favicon.png           → icona piccola del sito
├── icon-192.png          → icona per Android
├── icon-512.png          → icona per Android (alta risoluzione)
├── icon-512-maskable.png → icona adattiva per Android
└── apple-touch-icon.png  → icona per iPhone/iPad
```

Tutti i file sono singoli, nessuna cartella da caricare: eliminiamo così qualunque problema di trascinamento di cartelle nel browser.

## Passo 1 — Crea un repository su GitHub

1. Vai su [github.com](https://github.com) e crea un account gratuito, se non ne hai già uno
2. Clicca su **"New repository"** (in alto a destra, icona **+**)
3. Dai un nome al repository, ad esempio `spese-tracker`
4. Lascialo **pubblico** (necessario per usare GitHub Pages gratis — non preoccuparti, i tuoi dati restano solo sul tuo dispositivo, il repository contiene solo il codice dell'app, non le tue spese)
5. Clicca **"Create repository"**

## Passo 2 — Carica i file

1. Nella pagina del repository appena creato, clicca **"uploading an existing file"** (o il pulsante **"Add file" → "Upload files"**)
2. Trascina dentro **tutti i file** che trovi in questa cartella, tutti insieme, in un'unica sessione (sono tutti file singoli, nessuna cartella)
3. Scorri in basso e clicca **"Commit changes"**

## Passo 3 — Attiva GitHub Pages

1. Nel repository, vai su **Settings** (in alto)
2. Nel menu a sinistra clicca **Pages**
3. Sotto "Build and deployment", alla voce **Branch** scegli `main` e la cartella `/ (root)`
4. Clicca **Save**
5. Aspetta circa un minuto, poi ricarica la pagina: comparirà un link tipo `https://tuonome.github.io/spese-tracker/`

Quello è l'indirizzo della tua app, sempre raggiungibile e aggiornato ogni volta che modifichi i file nel repository.

## Passo 4 — Installa l'app

**Da iPhone (Safari):**
Apri il link → icona di condivisione (il quadrato con la freccia in su) → **"Aggiungi a Home"**

**Da Android (Chrome):**
Apri il link → menu (i tre puntini in alto a destra) → **"Installa app"** (o "Aggiungi a schermata Home")

**Da PC (Chrome/Edge):**
Apri il link → icona di installazione nella barra degli indirizzi (di solito a destra, un piccolo schermo con freccia) → **"Installa"**

In tutti e tre i casi ottieni un'icona vera, che apre l'app a schermo intero senza barra del browser — a tutti gli effetti identica a un'app scaricata da uno store.

## Aggiornare l'app in futuro

Ogni volta che vuoi aggiungere una funzionalità o correggere qualcosa, basta caricare la nuova versione di `index.html` (o degli altri file) nello stesso repository, sostituendo quello vecchio. GitHub Pages si aggiorna da solo in un minuto, e l'app che hai già installata sul telefono si aggiornerà automaticamente alla prossima apertura.

## Nota sui dati

Di base, i tuoi dati (spese, entrate, conti, tag...) sono salvati **solo sul tuo dispositivo**, nella memoria locale del browser. Non vengono mai inviati a GitHub né a nessun altro server: il repository contiene solo il codice dell'app, non le tue informazioni finanziarie.

## Sincronizzare i dati tra telefono e PC

L'app include una sincronizzazione opzionale tramite Firebase (il servizio cloud gratuito di Google): una volta configurata, ogni spesa o entrata inserita su un dispositivo appare in pochi secondi anche sull'altro, senza bisogno di esportare o importare nulla a mano.

Per attivarla, segui la **[GUIDA-FIREBASE.md](GUIDA-FIREBASE.md)** inclusa in questa cartella — richiede circa 5 minuti ed è completamente gratuita per uso personale. Se preferisci non configurarla, l'app funziona comunque normalmente, semplicemente ogni dispositivo terrà la propria copia separata dei dati.

## Risoluzione problemi comuni

**"L'unica cosa che riesco a scaricare è GitHub Desktop / uno zip"**
Stai probabilmente guardando la pagina del repository (`github.com/tuonome/spese-tracker`), dove il pulsante verde "Code" serve per modificare il codice, non per usare l'app. L'app si trova invece a un indirizzo diverso, quello generato da GitHub Pages (`tuonome.github.io/spese-tracker/`) — vedi il passo successivo per trovarlo. Lì non c'è nulla da scaricare: la pagina si apre come un sito web normale, poi la installi con "Aggiungi a Home".

**"In Settings → Pages non compare nessun link"**
Controlla in ordine:
1. Hai effettivamente cliccato **Save** dopo aver scelto branch e cartella?
2. Il branch selezionato è quello giusto? Alcuni account creano repository con branch principale `master` invece di `main` — controlla quale dei due esiste nel tuo repository (si vede in alto a sinistra nella pagina principale) e selezionalo in Pages
3. Aspetta 1-2 minuti e ricarica la pagina delle impostazioni: la primissima pubblicazione richiede un attimo
4. Vai sulla scheda **Actions** in alto nel repository: se vedi una ❌ rossa invece di una ✅ verde, la pubblicazione è fallita — cliccaci sopra per vedere il dettaglio dell'errore

**Ho caricato i file ma sembra che non sia cambiato nulla**
Molto probabilmente manca l'ultimo passaggio: dopo aver trascinato i file, bisogna scorrere fino in fondo alla pagina e cliccare il pulsante verde **"Commit changes"** — senza quel click, GitHub non salva nulla, anche se il file sembrava caricato. Per verificare che il salvataggio sia andato a buon fine, torna sulla pagina principale del repository e controlla il numero accanto a "History": deve aumentare a ogni commit riuscito (se dice ancora "1 Commit" dopo aver caricato più file in momenti diversi, nessuno dei caricamenti è stato effettivamente salvato).

**La pagina si apre ma è vuota o mostra un elenco di file invece dell'app**
Significa che `index.html` non si trova nella cartella principale (root) del repository, ma dentro una sottocartella. Controlla nella pagina principale del repository: se vedi una cartella tipo `spese-tracker-pwa` che contiene a sua volta `index.html`, sposta tutti i file **fuori** da quella cartella, direttamente nella root del repository (puoi trascinarli di nuovo con "Add file → Upload files" e poi eliminare la cartella vuota).

## Prossimi passi


Quando deciderai di trasformarla in un'app vera e propria da pubblicare su App Store e Play Store, questi stessi file saranno il punto di partenza per un progetto Capacitor — il lavoro fatto qui non va perso, si riusa quasi interamente.
