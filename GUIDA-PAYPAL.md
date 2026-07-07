# Guida – Pagamenti PayPal in Spese Tracker

Questa guida spiega la nuova funzione che registra automaticamente i pagamenti PayPal,
con il **nome della persona** come esercente e il **messaggio del pagamento** nella nota.

---

## 1. Cosa fa la nuova funzione

Quando arriva una ricevuta PayPal, l'app crea un movimento e compila da sola:

- **Esercente** = la persona a cui hai inviato (o da cui hai ricevuto) il denaro.
  Esempio: *Marco Piras*.
- **Nota** = il messaggio che hai scritto al pagamento.
  Esempio: *Test conto PayPal*.
- **Conto** = dipende da come hai pagato (vedi punto 3).

Distingue i **due casi** che mi hai descritto:

1. **Pagamento con il saldo PayPal** → il movimento va sul conto **PayPal**.
2. **Pagamento dalla banca tramite PayPal** → il movimento va sul tuo **conto bancario**.
   In questo caso arrivano **due notifiche** (una di PayPal e una della banca):
   l'app **tiene solo quella di PayPal** ed **elimina il doppione della banca**,
   così la spesa **non viene contata due volte**.

---

## 2. Il conto "PayPal" e i due conti nelle impostazioni

- Alla prima apertura della versione aggiornata, l'app **crea da sola un conto chiamato "PayPal"**
  (non devi fare niente). I tuoi dati e i movimenti esistenti restano intatti.
- In **Impostazioni → Registrazione da notifiche**, in fondo trovi il riquadro
  **💸 Pagamenti PayPal** con due menu a tendina:
  - **Conto per i pagamenti col saldo PayPal** → di solito il conto "PayPal".
  - **Conto per i pagamenti dalla banca tramite PayPal** → scegli qui il tuo conto bancario
    (es. il tuo *conto trade*).

Puoi cambiarli quando vuoi.

---

## 3. ⚠️ Importante: serve la MAIL COMPLETA, non l'anteprima

Come hai notato tu stesso, **il messaggio e la fonte di pagamento** (saldo o banca)
**non si leggono nell'anteprima pop-up** della notifica: compaiono **solo dentro la mail**
che PayPal ti manda a ogni pagamento.

Quindi, perché l'app possa scrivere il messaggio nella nota e capire da quale conto è
uscito il denaro, deve ricevere il **testo completo della mail**, non solo l'anteprima.

- Se all'app arriva **solo l'anteprima**: registra comunque persona e importo, ma
  **senza messaggio** e mettendo il movimento sul conto **PayPal** (caso 1) come ripiego.
- Se all'app arriva la **mail completa**: registra **tutto correttamente**, messaggio incluso,
  e mette il movimento sul conto giusto.

---

## 4. Come far arrivare la mail all'app (iPhone)

Su iPhone un'app non può leggere le notifiche di altre app. La via affidabile è far
**leggere la mail a Google (Gmail) e inoltrarne il testo all'app**. Si imposta una volta sola
e poi funziona da solo, anche a telefono spento.

### Passo 1 – Copia l'indirizzo dell'app
Nell'app, vai in **Impostazioni → Registrazione da notifiche** e premi **Copia indirizzo**.
Otterrai un indirizzo lungo che inizia con `https://firestore.googleapis.com/...`.
Tienilo da parte (incollalo in una nota).

### Passo 2 – Crea lo script su Google
1. Dal computer, apri **script.google.com** e accedi con lo **stesso account Gmail** che riceve
   le mail di PayPal.
2. Clicca **Nuovo progetto**.
3. Cancella il testo che vedi e **incolla lo script qui sotto**.
4. Nella riga `var URL_APP = "...";` **incolla tra le virgolette l'indirizzo copiato al Passo 1**.
5. In alto premi **Salva** (icona del dischetto).

```javascript
// Incolla qui tra le virgolette l'indirizzo copiato dall'app:
var URL_APP = "INCOLLA_QUI_INDIRIZZO";

function inoltraPayPal() {
  // Cerca le mail PayPal non ancora inoltrate (ultimi 2 giorni)
  var query = 'from:(paypal.it OR paypal.com) newer_than:2d -label:inviato-a-spese';
  var threads = GmailApp.search(query, 0, 20);
  var etichetta = GmailApp.getUserLabelByName('inviato-a-spese')
                  || GmailApp.createLabel('inviato-a-spese');

  threads.forEach(function (t) {
    var msgs = t.getMessages();
    msgs.forEach(function (m) {
      var titolo = m.getSubject() || 'PayPal';
      var testo  = m.getPlainBody() || '';           // testo completo della mail
      testo = testo.replace(/\s+/g, ' ').substring(0, 4000);

      var payload = { fields: {
        title: { stringValue: titolo },
        text:  { stringValue: testo  }
      }};

      UrlFetchApp.fetch(URL_APP, {
        method: 'post',
        contentType: 'application/json',
        payload: JSON.stringify(payload),
        muteHttpExceptions: true
      });
    });
    t.addLabel(etichetta);   // segna il thread come già inviato
  });
}
```

### Passo 3 – Fai partire lo script in automatico
1. A sinistra clicca l'icona **Attivatori** (la sveglia ⏰).
2. Premi **Aggiungi attivatore** (in basso a destra).
3. Imposta:
   - Funzione da eseguire: **inoltraPayPal**
   - Origine evento: **Basato sul tempo**
   - Tipo: **Timer a intervalli di minuti** → **Ogni 5 minuti**
4. Premi **Salva** e autorizza l'accesso a Gmail quando richiesto
   (è il tuo account, serve solo per leggere le mail PayPal).

Fatto. Da ora, a ogni pagamento, entro pochi minuti il movimento comparirà nell'app.

> Se preferisci confermare a mano ogni movimento, lascia **spento** l'interruttore
> "Registra automaticamente senza conferma": i pagamenti compariranno nel riquadro
> **📥 Dalle notifiche** in home, con persona, messaggio e importo, pronti da confermare.

---

## 5. Il doppione della banca

Nel caso "dalla banca" ti arriva anche la notifica della banca del tipo
`Spesi 0,01 € presso PAYPAL *m.piras96`.
L'app la **riconosce e la scarta** in automatico, perché la ricevuta PayPal è più completa
(contiene la persona e il messaggio). Così **non trovi la spesa due volte**.

Inoltre, se per qualsiasi motivo la stessa mail arrivasse due volte, l'app usa il
**Codice transazione** per **non registrare doppioni**.

---

## 6. Correzione manuale

Ogni movimento resta modificabile: aprilo con un tap. Nella schermata di modifica ora c'è
il campo **Esercente (opzionale)**, sopra la Nota. Puoi usarlo anche per le spese normali
(es. scrivere "Esselunga" come esercente e lasciare la nota per un dettaglio).

Nell'elenco, il **titolo** del movimento mostra l'esercente e, sotto, compare il messaggio
con l'icona 💬.

---

## 7. Aggiornare l'app su GitHub Pages

Carica **tutti e tre i file insieme, in un unico caricamento** (non uno alla volta):

- `index.html`
- `service-worker.js`  *(versione aggiornata a v7: forza il refresh sui dispositivi)*
- `GUIDA-PAYPAL.md`

Ricorda:
- il file **`.nojekyll`** deve restare nella cartella (serve a GitHub Pages);
- dopo il caricamento, apri l'app e, se non vedi subito le novità, chiudila e riaprila
  (il service worker v7 aggiorna la cache da solo).

---

## 8. Limiti onesti

- **Il messaggio e la distinzione saldo/banca funzionano solo con la mail completa** (punto 3).
  Con la sola anteprima, il movimento viene registrato senza messaggio e sul conto PayPal.
- Il riconoscimento dei **pagamenti ricevuti** è previsto ma l'ho potuto provare solo su
  esempi ricostruiti (non ho una tua mail reale di "denaro ricevuto"): se ne ricevi una,
  mandamela e affino il riconoscimento.
- Se fai **più pagamenti dello stesso identico importo a pochi minuti di distanza**
  (come nei test da 0,01 €), la protezione anti-doppione si basa sul Codice transazione,
  che è diverso per ogni pagamento: quindi vengono registrati correttamente come movimenti
  distinti.

---

*Ho testato la funzione sui testi reali ricavati dalle tue schermate (pagamento col saldo,
pagamento dalla banca, doppione della banca, anteprima troncata): 28 controlli superati.*
