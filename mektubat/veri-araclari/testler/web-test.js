// Web yayını testi: alt klasörden sunar (GitHub Pages gibi), iPhone Safari kimliğiyle açar;
// kurulum kartı, service worker, internetsiz yeniden açılış ve Tedebbür'ün saklı dosyalarına dokunmama.
const { chromium, devices } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, 'dist', 'web'), PRE = '/Tedebbur-Kuran-Atolyesi/mektubat/';
const MIME = { '.html': 'text/html; charset=utf-8', '.json': 'application/json', '.css': 'text/css', '.woff2': 'font/woff2', '.js': 'text/javascript', '.png': 'image/png', '.webmanifest': 'application/manifest+json' };
const R = []; const res = (n, ok, d = '') => { R.push(ok); console.log(`[${ok ? 'GEÇTİ' : 'KALDI'}] ${n}${d ? '\n        ' + d : ''}`); };
const srv = http.createServer((q, r) => {
  let u = decodeURIComponent(q.url.split('?')[0]); if (!u.startsWith(PRE)) { r.writeHead(404); r.end(); return; }
  u = u.slice(PRE.length) || 'index.html'; const f = path.join(ROOT, u);
  fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream' }); r.end(d); });
}).listen(8791, async () => {
  const URL = 'http://localhost:8791' + PRE;   // localhost güvenli bağlam sayılır: service worker çalışır
  const b = await chromium.launch();
  const ctx = await b.newContext({ ...devices['iPhone 14'] }); const p = await ctx.newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  // kurulum.html yalnız https'te kaydeder; testte elle kaydet
  await p.goto(URL); await p.waitForFunction(() => document.querySelector('#loading').hidden, { timeout: 120000 });
  const kart = await p.evaluate(() => { const k = document.querySelector('#kur'); return k ? k.textContent : ''; });
  res('iPhone Safari kimliğiyle kurulum kartı çıkıyor ve iki adımı anlatıyor', /ana ekrana ekleyin/.test(kart) && /Paylaş/.test(kart) && /Ana Ekrana Ekle/.test(kart), kart.slice(0, 90));
  await p.click('#kur-k'); await p.reload(); await p.waitForFunction(() => document.querySelector('#loading').hidden, { timeout: 120000 });
  res('Kart kapatılınca bir daha çıkmıyor', await p.evaluate(() => !document.querySelector('#kur')));
  const meta = await p.evaluate(() => ({ icon: !!document.querySelector('link[rel="apple-touch-icon"]'), man: !!document.querySelector('link[rel="manifest"]'), cap: !!document.querySelector('meta[name="apple-mobile-web-app-capable"]'), title: document.querySelector('meta[name="apple-mobile-web-app-title"]').content }));
  res('Ana ekran için simge, manifest ve başlık etiketleri var', meta.icon && meta.man && meta.cap && meta.title === 'Mektûbât');
  // başka uygulamanın saklı dosyası
  await p.evaluate(async () => { const c = await caches.open('tedebbur-test'); await c.put('/x', new Response('x')); });
  await p.evaluate(async () => { await navigator.serviceWorker.register('sw.js'); await navigator.serviceWorker.ready; });
  await p.waitForFunction(async () => (await caches.keys()).some(k => k.startsWith('mektubat-')) && navigator.serviceWorker.controller, { timeout: 120000 });
  const c = await p.evaluate(async () => { const ks = await caches.keys(); const mk = ks.find(k => k.startsWith('mektubat-')); const n = (await (await caches.open(mk)).keys()).length; return { ks, n }; });
  res(`Service worker bütün dosyaları sakladı (${c.n}); Tedebbür'ün saklı dosyasına dokunmadı`, c.n >= 45 && c.ks.includes('tedebbur-test'), c.ks.join(', '));
  await ctx.setOffline(true); await p.reload();
  await p.waitForFunction(() => document.querySelector('#loading').hidden && window.MK && MK.ALIGN, { timeout: 120000 });
  await p.evaluate(() => location.hash = 'm-2-17'); await p.waitForTimeout(800);
  const off = await p.evaluate(async () => { await document.fonts.ready; return { cols: document.querySelectorAll('.col .s').length, fonts: [...new Set([...document.fonts].filter(f => f.status === 'loaded').map(f => f.family))].length }; });
  res(`İnternet kapalıyken yeniden açılıyor (mektup ${off.cols} cümle, ${off.fonts} yazı tipi)`, off.cols > 20 && off.fonts >= 3);
  const w = await p.evaluate(() => document.documentElement.scrollWidth);
  res('iPhone genişliğinde yatay kayma yok', w <= 390, String(w));
  res('Sayfa hatası yok', !errs.length, errs.slice(0, 3).join(' | '));
  console.log(`ÖZET: ${R.filter(x => x).length} geçti, ${R.filter(x => !x).length} kaldı`);
  await b.close(); srv.close();
});
