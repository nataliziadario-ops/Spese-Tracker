# Pagamenti PayPal in Spese Tracker

## In breve

I pagamenti PayPal si registrano **a mano**, dentro l'app, senza installare né
configurare nulla di esterno. L'app ti mette a disposizione tutto il necessario:

- un **conto "PayPal"** già creato in automatico;
- il campo **Esercente** (la persona a cui hai pagato);
- il campo **Nota** (il messaggio che hai scritto al pagamento).

## Perché a mano e non in automatico (su iPhone)

La registrazione automatica avrebbe richiesto uno **script Google esterno** che legge
le tue email e le inoltra all'app. Hai chiesto di **non** dipendere da strumenti esterni,
e in effetti **su iPhone non c'è alternativa possibile**: nessuna app (nemmeno nativa) può
leggere le email o le notifiche di un'altra app. Il messaggio del pagamento, poi, esiste
**solo dentro la mail** di PayPal, mai nell'anteprima della notifica.

Per questo ho **rimosso** la sincronizzazione automatica delle note e lo script Google.
È il motivo per cui i tuoi due pagamenti di prova non comparivano: su iPhone non esiste
un canale che porti da solo un pagamento PayPal dentro l'app.

## Come registrare un pagamento PayPal (10 secondi)

1. Apri l'app e premi **＋** (Nuova spesa).
2. Digita l'importo.
3. Come **Conto**, scegli **PayPal** (o il tuo conto bancario, se hai pagato dalla banca).
4. In **Esercente** scrivi il nome della persona (es. *Marco Piras*).
5. In **Nota** scrivi il messaggio del pagamento (es. *Test conto PayPal*).
6. Salva.

Nell'elenco vedrai il nome della persona come titolo e, sotto, il messaggio con l'icona 💬.
La ricerca trova i movimenti anche per nome dell'esercente.

## Da fare una volta sola: disattiva lo script Google

Visto che non serve più, elimina il progetto creato in precedenza così non gira a vuoto:

1. Vai su **script.google.com**, apri il progetto che avevi creato.
2. A sinistra apri **Attivatori** (l'icona ⏰), elimina l'attivatore "inoltraPayPal".
3. Puoi anche eliminare del tutto il progetto (menu **⋮ → Rimuovi**).

Non è obbligatorio, ma evita che provi a inviare dati che l'app ora ignora.

## Aggiornare l'app su GitHub Pages

Carica **tutti e due i file insieme, in un unico caricamento**:

- `index.html`
- `service-worker.js`  *(versione v8: forza l'aggiornamento sui dispositivi)*

Ricorda: il file **`.nojekyll`** deve restare nella cartella. Dopo il caricamento, chiudi
e riapri l'app: la nuova versione si attiva da sola.

## Cosa è rimasto e cosa no

Rimasto:
- conto **PayPal** creato in automatico;
- campo **Esercente** (anche per le spese normali: es. "Esselunga");
- campo **Nota** per il messaggio;
- esercente mostrato come titolo e messaggio come riga 💬 nell'elenco.

Rimosso:
- la lettura automatica delle mail PayPal e lo script Google;
- la distinzione automatica saldo/banca e il filtro anti-doppione
  (servivano solo alla parte automatica).
