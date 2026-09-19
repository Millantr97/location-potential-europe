const BASE = self.registration.scope;
const VERSION = "location-potential-europe-pwa-v2";
const CORE = [
  BASE, BASE+"index.html", BASE+"manifest.webmanifest", BASE+"offline.html",
  BASE+"styles.css?v=38", BASE+"cities.js?v=10", BASE+"app.js?v=35",
  BASE+"report.js?v=21", BASE+"extras.js?v=21",
  BASE+"tabs.js?v=22", BASE+"leads.js?v=20",
  BASE+"assets/favicon.svg", BASE+"assets/icons/icon-192.png",
  BASE+"assets/icons/icon-512.png", BASE+"assets/icons/apple-touch-icon.png",
  BASE+"assets/icons/maskable-192.png", BASE+"assets/icons/maskable-512.png"
];

self.addEventListener("install", event => {
  event.waitUntil(caches.open(VERSION).then(cache => cache.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(key => key !== VERSION).map(key => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", event => {
  if (event.request.method !== "GET") return;
  const url = new URL(event.request.url);

  if (event.request.mode === "navigate") {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          const copy = response.clone();
          caches.open(VERSION).then(cache => cache.put(event.request, copy));
          return response;
        })
        .catch(async () => (await caches.match(event.request)) || (await caches.match(BASE)) || caches.match(BASE+"offline.html"))
    );
    return;
  }

  if (url.origin === self.location.origin) {
    event.respondWith(
      caches.match(event.request).then(cached => cached || fetch(event.request).then(response => {
        if (response.ok) {
          const copy = response.clone();
          caches.open(VERSION).then(cache => cache.put(event.request, copy));
        }
        return response;
      }))
    );
  }
});
