# Spendy su iPhone — app nativa iOS (senza pubblicare sullo store)

Questa guida spiega come avere Spendy come **vera app iPhone**, senza metterla
sull'App Store. Leggi prima "In due parole": iOS funziona in modo diverso da
Android, ed è giusto che tu sappia perché *prima* di iniziare.

---

## In due parole (importante)

Su Android è facile: GitHub compila un file `.apk` e tu lo installi. Fine.

Su iPhone Apple mette **due muri**. Li superiamo tutti e due, ma è utile capirli:

1. **Muro 1 — per COSTRUIRE un'app iPhone serve un computer Mac.**
   Non si può fare su Windows o Linux: lo vieta Apple.
   → *Come lo superiamo:* usiamo un **Mac "in affitto" gratuito di GitHub**
   (nel cloud). Non ti serve possedere un Mac. Ci pensa il nuovo file
   `build-ios.yml` che ho aggiunto: costruisce l'app da solo, come già fa
   quello di Android.

2. **Muro 2 — su iPhone non si installa niente che non sia "firmato" da Apple.**
   Su Android basta "consentire origini sconosciute"; su iPhone **ogni** app
   deve essere firmata con un ID Apple. Il file che esce da GitHub è quindi
   **non firmato**: da solo non parte.
   → *Come lo superiamo:* la firma la mette **il tuo iPhone**, gratis, con il
   **tuo ID Apple**, tramite un'app che si chiama **SideStore**. È il metodo
   gratuito, senza Mac, e funziona bene qui in Italia (siamo in UE).

Riassunto del percorso: **GitHub costruisce l'app → tu la scarichi → SideStore
la firma con il tuo ID Apple e la installa sull'iPhone.**

---

## Cosa ti serve

- Il tuo iPhone.
- Un **ID Apple** (quello che già usi, va benissimo — è gratis).
- Una connessione Wi‑Fi.
- (Consigliato per la prima installazione di SideStore) un PC Windows o un Mac,
  anche di un amico, da usare **una volta sola**. Esiste anche la via "senza
  PC", ma è un po' più capricciosa: la trovi più sotto.

Nessun acquisto è necessario per questa strada. (Se poi vorrai togliere i piccoli
limiti del metodo gratuito, c'è l'opzione a pagamento — la spiego in fondo.)

---

## PARTE A — Far costruire l'app iPhone a GitHub

Questo è il pezzo automatico. Lo fai **una volta**, poi si ripete da solo a ogni
aggiornamento.

1. Carica sul ramo `Capacitor-Fase-1` i file che ti ho consegnato (c'è il nuovo
   `build-ios.yml` dentro `.github/workflows/`).
2. Su GitHub apri la scheda **Actions**.
3. Vedrai partire **"Build iOS (non firmato, per SideStore)"**. La prima volta
   può durare **10–20 minuti** (i Mac di GitHub sono più lenti a partire).
   Aspetta la **spunta verde**.
4. Apri l'esecuzione con la spunta verde. In fondo, nella sezione **Artifacts**,
   c'è **`spendy-unsigned-ipa`**. Scaricalo: dentro c'è il file
   **`Spendy-unsigned.ipa`**.

> Se compare una **X rossa** invece della spunta verde: apri l'esecuzione,
> guarda quale passo è fallito e mandami lo screenshot dell'errore. La prima
> compilazione iPhone a volte va sistemata (versione di Xcode del Mac di GitHub);
> è normale, si aggiusta in un colpo.

Trasferisci poi il file `.ipa` **sull'iPhone** (via AirDrop se hai un Mac, o
salvandolo nell'app **File** dell'iPhone, o inviandotelo su Telegram/email e
aprendolo dall'iPhone). Ti servirà nella Parte C.

---

## PARTE B — Installare SideStore sull'iPhone (una volta sola)

SideStore è l'app gratuita che **firma** Spendy con il tuo ID Apple e la
installa. Va preparata una volta sola.

SideStore cambia ogni tanto i propri passaggi, quindi ti do le **due strade** e
il **link ufficiale** (segui sempre quello per i dettagli aggiornati):
sito ufficiale → **https://sidestore.io** · guida → **https://docs.sidestore.io**

**Strada 1 — con un PC (la più stabile, consigliata la prima volta)**
Colleghi l'iPhone al PC una volta, un programmino di nome **AltServer** installa
SideStore sull'iPhone usando il tuo ID Apple. Dopodiché il PC non serve più:
SideStore si "rinnova" da solo via Wi‑Fi.

**Strada 2 — senza PC**
Dall'iPhone: installi dall'App Store l'app **"Local Dev VPN"**, poi da Safari usi
il **"Side Installer"** ufficiale, inserisci il tuo ID Apple e accoppi dalle
Impostazioni. È comoda perché non serve il cavo, ma i link dei certificati
cambiano spesso e a volte va ritentata. Se ti si blocca, usa la Strada 1.

In entrambi i casi, quando SideStore chiede l'**ID Apple e la password**, è
normale: servono **solo** per firmare le app sul *tuo* telefono (è lo stesso
meccanismo che Apple offre agli sviluppatori). Se hai la verifica in due
passaggi, ti chiederà il codice.

Dopo l'installazione, sul telefono attiva anche:
**Impostazioni → Privacy e sicurezza → Modalità sviluppatore → ON** (riavvia se
lo chiede), e "fidati" del tuo certificato quando te lo chiede.

---

## PARTE C — Installare Spendy con SideStore

1. Apri **SideStore** sull'iPhone.
2. Tocca **"+"** e scegli il file **`Spendy-unsigned.ipa`** (quello della Parte A).
3. SideStore lo **firma con il tuo ID Apple** e lo installa. Dopo qualche
   secondo trovi l'icona di **Spendy** nella schermata Home, come un'app vera.

Fatto: Spendy è ora un'app nativa iPhone. 🎉

---

## Cosa aspettarti (limiti onesti del metodo gratuito)

- **Scadenza 7 giorni.** Con l'ID Apple gratuito, l'app "scade" ogni 7 giorni.
  SideStore la **rinnova da sola** via Wi‑Fi (tiene acceso un piccolo "VPN"
  locale apposta). In pratica: tieni l'app SideStore installata e ogni tanto
  aprila. Se la lasci scadere, basta ri‑firmarla da SideStore (i tuoi dati
  restano, sono salvati nel telefono/nel cloud).
- **Massimo 3 app** firmabili con un ID Apple gratuito. Se usi SideStore solo
  per Spendy, non è un problema.
- **Aggiornamenti di iOS** possono ogni tanto rompere SideStore e costringere a
  rifarne il setup. Capita raramente ma può capitare.
- **Accesso con Google:** dentro l'app nativa (sia iPhone sia Android) il login
  con Google **per ora non funziona** — è previsto nella Fase 2, con il login
  nativo. Nel frattempo su iPhone usi **email + password** per la sincronizzazione
  (funziona già, la configurazione Firebase è incorporata: non devi incollare
  niente). Tutto il resto — registrare spese, salvadanai, import/export, foglio
  saldi — funziona come sull'APK Android di oggi.

---

## Per vedere una modifica futura sull'iPhone: 3 passi (come per l'APK)

Uguale ad Android, cambia solo l'ultimo passo:
1. Aggiorno il codice in **`www/`**.
2. GitHub ricompila da solo → aspetti la **spunta verde** in Actions.
3. Scarichi il nuovo `.ipa` e lo **re‑installi con SideStore** (al posto del
   "reinstalla APK" di Android). I dati restano.

> Ricorda: l'app compila **solo da `www/`**. I file nella radice servono a
> GitHub Pages (la versione web), non all'app iPhone.

---

## Opzione a pagamento (facoltativa, per togliere i limiti)

Se in futuro i limiti "7 giorni / 3 app" ti danno fastidio, con un account
**Apple Developer (99 €/anno)** l'app dura **365 giorni** e sparisce il limite
delle 3 app. In quel caso **non serve più SideStore**: GitHub può produrre un
`.ipa` **già firmato** e lo installi direttamente.

Non è necessario ora, e non c'entra con la pubblicazione sullo store (quella è
un'altra scelta, la Fase 4). Se deciderai per questa strada, **dimmelo e
modifico io il workflow** per firmare l'app con le tue chiavi (serve caricare i
certificati Apple come "segreti" su GitHub: ti guido passo‑passo).

---

## Riepilogo

| | Android (oggi) | iPhone (questa guida) |
|---|---|---|
| Chi costruisce l'app | GitHub (Linux) | GitHub (Mac nel cloud) |
| File prodotto | `.apk` | `.ipa` non firmato |
| Come si installa | "Origini sconosciute" | SideStore firma col tuo ID Apple |
| Costo | 0 € | 0 € |
| Limiti | nessuno | scade a 7 giorni (rinnovo automatico), max 3 app |
