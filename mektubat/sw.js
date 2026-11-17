// Mektûbât: sayfayı, yazı tiplerini ve metinleri ilk açılışta saklar; sonra internetsiz de açılır.
// Aynı adresteki başka uygulamaların (Tedebbür) saklanmış dosyalarına dokunmaz: yalnız "mektubat-" ile başlayanları yönetir.
const AD = 'mektubat-1326b8b12991';
const DOSYA = ["./", "manifest.webmanifest", "simge-180.png", "simge-512.png", "data/ak.json", "data/align.json", "data/ar.json", "data/atlas.json", "data/fa.json", "data/glossary.json", "data/hk.json", "data/index.json", "data/people.json", "data/quran.json", "data/spectrum.json", "data/verses.json", "data/widget.json", "fonts/amiri-arabic-400-normal.woff2", "fonts/amiri-arabic-700-normal.woff2", "fonts/amiri-latin-400-normal.woff2", "fonts/amiri-latin-700-normal.woff2", "fonts/amiri-latin-ext-400-normal.woff2", "fonts/amiri-latin-ext-700-normal.woff2", "fonts/cormorant-garamond-latin-500-normal.woff2", "fonts/cormorant-garamond-latin-600-normal.woff2", "fonts/cormorant-garamond-latin-700-normal.woff2", "fonts/cormorant-garamond-latin-ext-500-normal.woff2", "fonts/cormorant-garamond-latin-ext-600-normal.woff2", "fonts/cormorant-garamond-latin-ext-700-normal.woff2", "fonts/fonts.css", "fonts/literata-latin-400-italic.woff2", "fonts/literata-latin-400-normal.woff2", "fonts/literata-latin-600-normal.woff2", "fonts/literata-latin-ext-400-italic.woff2", "fonts/literata-latin-ext-400-normal.woff2", "fonts/literata-latin-ext-600-normal.woff2", "fonts/noto-nastaliq-urdu-arabic-400-normal.woff2", "fonts/noto-nastaliq-urdu-arabic-600-normal.woff2", "fonts/noto-nastaliq-urdu-latin-400-normal.woff2", "fonts/noto-nastaliq-urdu-latin-600-normal.woff2", "fonts/noto-nastaliq-urdu-latin-ext-400-normal.woff2", "fonts/noto-nastaliq-urdu-latin-ext-600-normal.woff2", "fonts/vazirmatn-arabic-400-normal.woff2", "fonts/vazirmatn-arabic-600-normal.woff2", "fonts/vazirmatn-latin-400-normal.woff2", "fonts/vazirmatn-latin-600-normal.woff2", "fonts/vazirmatn-latin-ext-400-normal.woff2", "fonts/vazirmatn-latin-ext-600-normal.woff2"];
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
