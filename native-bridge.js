// ============================================================
// native-bridge.js — UNICO punto di contatto con il codice nativo
// ============================================================
// Regola d'oro del progetto: tutta la logica dell'app vive in www/.
// Le differenze tra web, Android e iOS passano SOLO da qui, e ogni
// funzione ha SEMPRE un fallback web: la versione GitHub Pages
// continua a funzionare identica anche senza Capacitor.
//
// FASE 1 (attuale): questo file è volutamente "inerte".
// Espone solo window.NativeBridge con informazioni di piattaforma
// e segnaposto con fallback web. Nessun comportamento dell'app cambia.
// FASE 2: qui verranno collegati login Google/Apple nativi, backup su
// Preferences, Filesystem/Share per import-export, deep link spendy://.
(function () {
  'use strict';

  function hasCapacitor() {
    try {
      return !!(window.Capacitor && typeof window.Capacitor.isNativePlatform === 'function');
    } catch (e) { return false; }
  }

  // Plugin di login nativo (@capacitor-firebase/authentication). Esiste SOLO
  // dentro l'app Android/iOS: sul web resta null, così si usa il metodo web.
  function fbAuthPlugin() {
    try {
      return (window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.FirebaseAuthentication) || null;
    } catch (e) { return null; }
  }

  var bridge = {
    // true solo dentro il guscio Capacitor (Android/iOS)
    isNative: function () {
      return hasCapacitor() && window.Capacitor.isNativePlatform();
    },

    // 'web' | 'android' | 'ios'
    platform: function () {
      if (hasCapacitor() && typeof window.Capacitor.getPlatform === 'function') {
        return window.Capacitor.getPlatform();
      }
      return 'web';
    },

    // --- Segnaposto Fase 2 (per ora: solo fallback web) ---

    // Backup delle chiavi critiche su storage nativo (Capacitor Preferences).
    // Fallback web: non fa nulla, localStorage resta l'unica fonte.
    backupKey: function (key, value) {
      return Promise.resolve(false); // false = nessun backup nativo eseguito
    },
    restoreKey: function (key) {
      return Promise.resolve(null); // null = nessun backup nativo disponibile
    },

    // Condivisione/salvataggio file (export). Fallback web: null = usa il
    // percorso web già esistente nell'app (share {files:[file]} / download).
    shareFile: function (fileName, mimeType, blob) {
      return Promise.resolve(null);
    },

    // --- Login nativo (Fase 2) ---
    // Regola: se NON siamo in nativo (o il plugin non c'è) restituiamo null,
    // e l'app usa il metodo web di sempre (finestra/redirect). In nativo, il
    // plugin apre la schermata Google/Apple del telefono e ci ridà solo la
    // "credenziale" (idToken); poi ci pensa Firebase JS (signInWithCredential),
    // così la sincronizzazione resta identica.

    // → {idToken, accessToken} oppure null (usa il metodo web)
    signInWithGoogle: function () {
      if (!this.isNative()) return Promise.resolve(null);
      var fa = fbAuthPlugin();
      if (!fa || typeof fa.signInWithGoogle !== 'function') return Promise.resolve(null);
      return fa.signInWithGoogle({ skipNativeAuth: true }).then(function (res) {
        var c = (res && res.credential) || {};
        if (!c.idToken) return null;
        return { idToken: c.idToken, accessToken: c.accessToken || null };
      });
    },

    // → {idToken, nonce} oppure null. Attivo solo quando il Login con Apple
    // sarà configurato (account Apple Developer + build iOS firmata).
    signInWithApple: function () {
      if (!this.isNative()) return Promise.resolve(null);
      var fa = fbAuthPlugin();
      if (!fa || typeof fa.signInWithApple !== 'function') return Promise.resolve(null);
      return fa.signInWithApple({ skipNativeAuth: true }).then(function (res) {
        var c = (res && res.credential) || {};
        if (!c.idToken) return null;
        return { idToken: c.idToken, nonce: c.nonce || null };
      });
    },

    // --- Widget in schermata Home (Fase 3, solo Android) ---
    // Manda al codice nativo la "fotografia" gia' formattata da mostrare nel
    // widget. Fallback web: non fa nulla e restituisce false, cosi' la
    // versione GitHub Pages continua a funzionare identica.
    updateWidget: function (payload) {
      if (!this.isNative()) return Promise.resolve(false);
      var pl;
      try {
        pl = (window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.SpendyWidget) || null;
      } catch (e) { return Promise.resolve(false); }
      if (!pl || typeof pl.update !== 'function') return Promise.resolve(false);
      return pl.update(payload || {})
        .then(function () { return true; })
        .catch(function () { return false; });
    },

    // Legge (una sola volta) l'azione richiesta da un tasto del widget
    // "spesa rapida". Fallback web: null = nessuna azione in attesa.
    consumeWidgetAction: function () {
      if (!this.isNative()) return Promise.resolve(null);
      var pl;
      try {
        pl = (window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.SpendyWidget) || null;
      } catch (e) { return Promise.resolve(null); }
      if (!pl || typeof pl.consumeAction !== 'function') return Promise.resolve(null);
      return pl.consumeAction()
        .then(function (r) {
          if (!r || !r.action) return null;
          return { action: r.action, cat: r.cat || '' };
        })
        .catch(function () { return null; });
    },

    // Pulisce anche la sessione del plugin nativo, oltre a quella Firebase JS.
    // Fallback web: false (niente da pulire lato nativo).
    signOutNative: function () {
      var fa = fbAuthPlugin();
      if (!this.isNative() || !fa || typeof fa.signOut !== 'function') return Promise.resolve(false);
      return fa.signOut().then(function () { return true; }).catch(function () { return false; });
    }
  };

  window.NativeBridge = bridge;
})();
