# Configurare Firebase per la sincronizzazione

Questa guida ti serve una sola volta, per creare il "database cloud" gratuito che farà sincronizzare i tuoi dati tra telefono e PC. Richiede circa 5 minuti..

## 1. Crea il progetto Firebase

1. Vai su [console.firebase.google.com](https://console.firebase.google.com) e accedi con un account Google
2. Clicca **"Aggiungi progetto"**
3. Dai un nome al progetto (es. "spese-tracker") e continua
4. Puoi disattivare Google Analytics (non serve per questa app) e cliccare **"Crea progetto"**

## 2. Attiva Firestore Database

1. Nel menu a sinistra, vai su **Build → Firestore Database**
2. Clicca **"Crea database"**
3. Scegli la location più vicina a te (es. `europe-west`) e clicca **Avanti**
4. Seleziona **"Avvia in modalità produzione"** e clicca **Crea**

## 3. Imposta le regole di sicurezza

Le regole di sicurezza garantiscono che solo tu possa leggere e scrivere i tuoi dati, anche se qualcun altro scoprisse la configurazione dell'app.

1. Nella sezione Firestore Database, vai sulla scheda **"Regole"**
2. Cancella il contenuto e incolla questo al suo posto:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /syncedState/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

3. Clicca **"Pubblica"**

## 4. Attiva l'accesso con email e password

1. Nel menu a sinistra, vai su **Build → Authentication**
2. Clicca **"Inizia"**
3. Nella lista dei provider, scegli **"Email/Password"**
4. Attiva il primo interruttore ("Email/Password") e clicca **Salva**

## 5. Registra l'app e copia la configurazione

1. Torna alla panoramica del progetto (icona a forma di casa, in alto a sinistra)
2. Clicca l'icona **"</>"** (Aggiungi un'app web)
3. Dai un nickname all'app (es. "Spese") — non serve configurare l'hosting Firebase, salta pure quel passaggio
4. Clicca **"Registra app"**
5. Comparirà un blocco di codice con `const firebaseConfig = { ... }`: copia **solo la parte tra graffe**, cioè l'oggetto che inizia con `{ apiKey: ...` e finisce con `}`
6. Clicca **"Vai alla console"** per finire

## 6. Incolla la configurazione nell'app

1. Apri l'app, vai su **Conti → Configura sincronizzazione**
2. Incolla l'oggetto copiato al passo precedente
3. Nella schermata successiva, scegli **"Crea account"** e inserisci l'email e una password a tua scelta (minimo 6 caratteri) — questo account serve solo per questa app, non è collegato al tuo account Google
4. Fatto: i tuoi dati sono ora sincronizzati

## Sul secondo dispositivo

Ripeti solo il **Passo 6**: apri l'app, incolla la **stessa identica configurazione**, ma questa volta scegli **"Accedi"** invece di "Crea account", usando la stessa email e password. Se su quel dispositivo avevi già inserito dei dati, l'app ti chiederà quali tenere (quelli del cloud o quelli locali) prima di collegare la sincronizzazione.

## Limiti del piano gratuito

Il piano gratuito di Firebase ("Spark") include 50.000 letture e 20.000 scritture al giorno e 1 GB di spazio — per un uso personale, anche intenso, è praticamente impossibile raggiungere questi limiti. Non serve inserire una carta di credito.

## Cosa fare se qualcosa non funziona

- **"Configurazione non valida"**: assicurati di aver copiato l'intero oggetto, comprese le parentesi graffe `{ }`
- **"Password errata" pur essendo sicuro che sia giusta**: controlla di aver scritto l'email esattamente come al momento della creazione dell'account (maiuscole/minuscole non contano, ma spazi accidentali sì)
- **I dati non si aggiornano sull'altro dispositivo**: verifica che entrambi i dispositivi mostrino "Connesso come [la tua email]" nella schermata Conti, e che ci sia connessione internet
