// Mektûbât: sayfayı, yazı tiplerini ve metinleri ilk açılışta saklar; sonra internetsiz de açılır.
// Aynı adresteki başka uygulamaların (Tedebbür) saklanmış dosyalarına dokunmaz: yalnız "mektubat-" ile başlayanları yönetir.
const AD = 'mektubat-@SURUM@';
const DOSYA = @DOSYA@;
self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(AD).then((c) => c.addAll(DOSYA)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k.startsWith('mektubat-') && k !== AD).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET' || !e.request.url.startsWith(self.registration.scope)) return;
  e.respondWith(caches.open(AD).then((c) => c.match(e.request, { ignoreSearch: true })).then((r) => r || fetch(e.request).catch(() => caches.open(AD).then((c) => c.match('./')))));
});
