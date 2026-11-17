// Sayfayı ilk açılışta saklar; sonra internetsiz de açılır. Sürüm değişince eski kopya silinir.
const AD = 'tedebbur-@SURUM@';
const DOSYA = ['./', 'manifest.webmanifest', 'simge-180.png', 'simge-512.png'];
self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(AD).then((c) => c.addAll(DOSYA)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== AD).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  e.respondWith(caches.match(e.request, { ignoreSearch: true }).then((r) => r || fetch(e.request).then((y) => {
    if (y.ok && /fonts\.(googleapis|gstatic)\.com/.test(e.request.url)) { const k = y.clone(); caches.open(AD).then((c) => c.put(e.request, k)); }
    return y;
  }).catch(() => caches.match('./'))));
});
