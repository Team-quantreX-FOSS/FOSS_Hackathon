/* FinRisk Service Worker — PWA Offline Support */
const CACHE = 'finrisk-v1';
const STATIC = [
  '/',
  '/static/style.css',
  '/static/script.js',
  '/static/icon.png',
  '/static/manifest.json',
  'https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap',
  'https://cdn.jsdelivr.net/npm/chart.js'
];

self.addEventListener('install', function(e){
  e.waitUntil(
    caches.open(CACHE).then(function(cache){
      return cache.addAll(STATIC);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', function(e){
  e.waitUntil(
    caches.keys().then(function(keys){
      return Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)));
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', function(e){
  /* Never cache API calls — always fetch fresh */
  if(e.request.url.includes('/api/') ||
     e.request.url.includes('/get_status') ||
     e.request.url.includes('/users') ||
     e.request.method !== 'GET'){
    return;
  }
  e.respondWith(
    fetch(e.request).then(function(res){
      let clone = res.clone();
      caches.open(CACHE).then(function(cache){ cache.put(e.request, clone); });
      return res;
    }).catch(function(){
      return caches.match(e.request);
    })
  );
});
