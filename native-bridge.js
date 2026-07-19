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
    }
  };

  window.NativeBridge = bridge;
})();
