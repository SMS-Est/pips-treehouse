/* Pip's Treehouse service worker v1.6.0
   Offline-first: every file the app needs is saved on the device the first time
   it opens online. After that it always opens instantly from the saved copy (no
   waiting on a weak car hotspot) and quietly checks for a newer version in the
   background; a new version shows up the next time the app is opened. */
const CACHE = 'pips-treehouse-v1.6.0';
const CORE = ["./", "index.html", "manifest.webmanifest", "fonts/fonts.css", "fonts/andika-latin-400-normal.woff2", "fonts/andika-latin-700-normal.woff2", "fonts/grandstander-latin-600-normal.woff2", "fonts/grandstander-latin-700-normal.woff2", "fonts/grandstander-latin-800-normal.woff2", "fonts/grandstander-latin-900-normal.woff2", "icons/icon-192.png", "icons/icon-512.png", "icons/apple-touch-icon.png"];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys()
    .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  const key = req.mode === 'navigate' ? 'index.html' : req;
  e.respondWith(caches.open(CACHE).then((c) => c.match(key, { ignoreSearch: true }).then((hit) => {
    const fresh = fetch(req).then((res) => {
      if (res && res.ok) c.put(key, res.clone());
      return res;
    });
    if (hit) { e.waitUntil(fresh.catch(() => {})); return hit; }
    return fresh.catch(() => c.match('index.html'));
  })));
});
