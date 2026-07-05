# Registrazione automatica dalle notifiche della banca

Questa guida spiega come far registrare all'app, in automatico, le spese e le entrate a partire dalle notifiche che la tua banca ti manda sul telefono.

## Come funziona (e i suoi limiti)

Una web app **non può leggere le notifiche di altre app**: è una protezione dei sistemi operativi, non aggirabile. La soluzione usa quindi un'app "ponte":

1. Sul telefono **Android**, un'app di automazione gratuita (**MacroDroid**) legge le notifiche della tua banca
2. MacroDroid inoltra il testo della notifica al tuo cloud Firebase (lo stesso della sincronizzazione)
3. L'app Spese, su qualunque dispositivo, riceve la notifica in pochi secondi, ne estrae **importo, descrizione e categoria**, e te la mostra in cima alla schermata Riepilogo, da confermare con un tap
4. Se preferisci, puoi attivare la **modalità automatica**: le notifiche riconosciute vengono registrate da sole, senza conferma

**Su iPhone questa funzione non è disponibile**: Apple non permette a nessuna app (nemmeno native) di leggere le notifiche di altre app. L'unica alternativa parziale, se paghi con Apple Pay, è un'automazione con l'app Comandi Rapidi (vedi in fondo).

**Prerequisito:** devi aver già configurato la sincronizzazione Firebase (vedi GUIDA-FIREBASE.md) ed essere connessa/o su almeno un dispositivo.

## Passo 1 — Aggiorna le regole di sicurezza Firebase

Serve permettere a MacroDroid di scrivere nella "casella" delle notifiche. La casella è protetta da un token segreto lungo e casuale, generato dall'app.

1. Vai su [console.firebase.google.com](https://console.firebase.google.com) → il tuo progetto → **Firestore Database** → scheda **Regole**
2. Sostituisci tutto il contenuto con questo e clicca **Pubblica**:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /syncedState/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    match /inbox/{token}/items/{itemId} {
      // Chi conosce il token (segreto, 24 caratteri casuali) può depositare notifiche
      allow create: if token.size() >= 20
                    && request.resource.data.keys().hasOnly(['title','text'])
                    && request.resource.data.text is string
                    && request.resource.data.text.size() < 2000;
      // Solo un utente autenticato dell'app può leggerle ed eliminarle
      allow read, delete: if request.auth != null;
    }
  }
}
```

## Passo 2 — Recupera indirizzo e corpo della richiesta dall'app

1. Apri l'app Spese → **Conti**
2. Nella card **"🔔 Registrazione da notifiche"** trovi due campi già pronti:
   - **Indirizzo** (contiene il tuo token segreto)
   - **Corpo della richiesta**
3. Usa i pulsanti **Copia** per copiarli — ti serviranno al passo successivo. Puoi mandarteli via email/note per averli sul telefono se stai configurando da PC

⚠️ L'indirizzo contiene il token segreto: non condividerlo pubblicamente. Chi lo conosce potrebbe inviare notifiche fasulle alla tua app (ma non leggere i tuoi dati).

## Passo 3 — Configura MacroDroid (Android)

1. Installa **MacroDroid** dal Play Store (gratuito)
2. Alla prima apertura, concedi il permesso di **accesso alle notifiche** quando richiesto
3. Crea una nuova macro (**+ Aggiungi macro**):

**Trigger (attivazione):**
- Scegli **Notifica → Notifica ricevuta**
- Seleziona **l'app della tua banca** dall'elenco (solo quella: eviterai di inoltrare notifiche di altre app)

**Azione:**
- Scegli **Connettività → Richiesta HTTP**
- Metodo: **POST**
- URL: incolla l'**indirizzo** copiato dall'app
- Content type: `application/json`
- Corpo della richiesta: incolla il **corpo** copiato dall'app. Contiene i segnaposto `{not_title}` e `{notification}` che MacroDroid sostituisce da solo con titolo e testo della notifica

**Vincolo (facoltativo ma consigliato):** nessuno.

4. Dai un nome alla macro (es. "Spese da banca") e salvala

## Passo 4 — Prova

Fai un piccolo pagamento (o aspetta la prossima notifica della banca). Entro pochi secondi, aprendo l'app Spese, in cima al Riepilogo comparirà la card **"📥 Dalle notifiche"** con il movimento già interpretato: importo, descrizione, categoria proposta. Tocca **Registra** per confermarlo o **Ignora** per scartarlo.

Se il riconoscimento funziona bene con le notifiche della tua banca, puoi attivare **"Registra automaticamente senza conferma"** nella card in Conti: da quel momento i movimenti riconosciuti si registrano da soli (quelli non riconosciuti restano comunque in attesa di revisione).

## Cosa viene riconosciuto

L'app estrae:
- **Importo**: cerca formati come `10,00 €`, `EUR 23,50`, `€7.80`
- **Tipo**: parole come "accredito", "bonifico ricevuto", "stipendio", "rimborso" → entrata; tutto il resto → spesa
- **Descrizione**: il testo dopo "presso ..." o "da ...", altrimenti il titolo della notifica
- **Categoria**: proposta in base a parole chiave nella descrizione (es. "Esselunga" → Cibo), sempre modificabile dopo

Le notifiche senza un importo riconoscibile (es. "il tuo saldo è stato aggiornato") compaiono come "Importo non riconosciuto", da ignorare con un tap.

## iPhone: l'alternativa Apple Pay

Se paghi con Apple Pay, l'app **Comandi Rapidi** di iOS ha un'automazione "Transazione" che si attiva ad ogni pagamento con una carta di Wallet:

1. Comandi Rapidi → Automazioni → **+** → **Transazione** → scegli la carta → "Esegui immediatamente"
2. Come azione, aggiungi **"Ottieni contenuto di URL"**: metodo POST, lo stesso indirizzo del Passo 2, corpo JSON in cui inserisci le variabili dell'automazione (importo e commerciante) nel campo `text`

Copre solo i pagamenti Apple Pay, non i bonifici né i pagamenti con carta fisica non collegata a Wallet — ma per chi usa molto Apple Pay è comunque una copertura significativa.

## Risoluzione problemi

- **La notifica non arriva nell'app**: verifica in MacroDroid il registro delle macro eseguite (menu → Registro macro) per vedere se la macro si è attivata e la richiesta HTTP è andata a buon fine (codice 200)
- **Errore 403 nella richiesta HTTP**: le regole del Passo 1 non sono state pubblicate correttamente — ricontrolla di aver sostituito tutto il testo e cliccato Pubblica
- **La card "Registrazione da notifiche" non compare in Conti**: compare solo quando la sincronizzazione è connessa (pallino verde 🟢)
- **Importo sbagliato o categoria errata**: registra comunque e poi correggi il movimento con un tap dallo storico — e se capita spesso con la tua banca, scrivimi il formato esatto della notifica per migliorare il riconoscimento
