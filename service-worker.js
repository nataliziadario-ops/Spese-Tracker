// Service worker minimale: mette in cache i file principali dell'app
// così si apre anche offline e si installa correttamente come PWA.
// Cambia CACHE_NAME quando aggiorni index.html per forzare il refresh
// della cache sui dispositivi già installati.
var CACHE_NAME = 'spese-tracker-v10';
var FILES_TO_CACHE = [
  './index.html',
  './registra.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
  './apple-touch-icon.png'
];

self.addEventListener('install', function(event){
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache){
      return cache.addAll(FILES_TO_CACHE);
    }).then(function(){
      return self.skipWaiting();
    })
  );
});

self.addEventListener('activate', function(event){
  event.waitUntil(
    caches.keys().then(function(keys){
      return Promise.all(
        keys.filter(function(k){ return k !== CACHE_NAME; })
            .map(function(k){ return caches.delete(k); })
      );
    }).then(function(){
      return self.clients.claim();
    })
  );
});

// Strategia: prova la rete per avere sempre l'ultima versione quando c'è
// connessione; se offline, usa la cache. Così l'app resta aggiornabile
// ma funziona anche senza internet.
self.addEventListener('fetch', function(event){
  if (event.request.method !== 'GET') return;
  event.respondWith(
    fetch(event.request).then(function(response){
      var copy = response.clone();
      caches.open(CACHE_NAME).then(function(cache){ cache.put(event.request, copy); });
      return response;
    }).catch(function(){
      return caches.match(event.request).then(function(cached){
        return cached || caches.match('./index.html');
      });
    })
  );
});
