// SAMRIDH-AI Mobile PWA Service Worker
const CACHE_NAME = 'samridh-v1';
const ASSETS = [
  './index.html',
  './manifest.json',
  './assets/samridh_logo.png',
  './assets/twinbit_logo.jpg'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
});

self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((res) => res || fetch(e.request))
  );
});
