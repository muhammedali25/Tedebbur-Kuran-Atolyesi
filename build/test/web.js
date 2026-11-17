// dist/web klasörünü yerel bir adresten sunar: iPhone Safari kimliğiyle kurulum kartını,
// uygulama (standalone) kipinde kartın çıkmadığını ve service worker ile internetsiz açılışı dener.
const { chromium, devices } = require('playwright'); const http = require('http'), fs = require('fs'), path = require('path');
const kok = path.join(__dirname, '..', '..', 'dist', 'web');
const tip = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.png': 'image/png', '.webmanifest': 'application/manifest+json' };
const srv = http.createServer((q, r) => { let p = q.url.split('?')[0]; if (p === '/') p = '/index.html'; const f = path.join(kok, p);
  if (!f.startsWith(kok) || !fs.existsSync(f)) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'content-type': tip[path.extname(f)] || 'text/plain' }); fs.createReadStream(f).pipe(r); });
(async () => {
  await new Promise((ok) => srv.listen(8767, ok)); const b = await chromium.launch(); const hata = [], out = process.argv[2];
  // 1) iPhone Safari: kart çıkar, kapatınca bir daha çıkmaz
  let cx = await b.newContext({ ...devices['iPhone 14'] }); let pg = await cx.newPage(); pg.on('pageerror', (e) => hata.push('JS: ' + e.message));
  await pg.goto('http://localhost:8767/'); await pg.waitForSelector('.sec'); await pg.waitForTimeout(500);
  if (!(await pg.locator('#kur').innerText()).includes('Ana Ekrana Ekle')) hata.push('iPhone kurulum kartı yok');
  if (out) await pg.screenshot({ path: out + '/kur-iphone.png' });
  await pg.click('#kur-k'); await pg.reload(); await pg.waitForSelector('.sec'); await pg.waitForTimeout(300);
  if (await pg.locator('#kur').count()) hata.push('kart kapatıldıktan sonra yine çıktı'); await cx.close();
  // 2) uygulama kipi: kart çıkmaz
  cx = await b.newContext({ ...devices['iPhone 14'] }); await cx.addInitScript(() => { Object.defineProperty(navigator, 'standalone', { get: () => true }); });
  pg = await cx.newPage(); await pg.goto('http://localhost:8767/#sure-36'); await pg.waitForSelector('.sec'); await pg.waitForTimeout(400);
  if (await pg.locator('#kur').count()) hata.push('uygulama kipinde kart çıktı'); if (out) await pg.screenshot({ path: out + '/kur-uygulama.png' }); await cx.close();
  // 3) internetsiz: service worker kurulduktan sonra sunucu kapalıyken açılır (localhost güvenli sayılır ama kayıt https ister; burada elle kaydedilir)
  cx = await b.newContext(); pg = await cx.newPage(); await pg.goto('http://localhost:8767/'); await pg.waitForSelector('.sec');
  await pg.evaluate(async () => { await navigator.serviceWorker.register('sw.js'); await navigator.serviceWorker.ready; }); await pg.waitForTimeout(1500);
  await cx.setOffline(true); await pg.goto('http://localhost:8767/#kok'); await pg.waitForSelector('.kok-buyuk', { timeout: 15000 }).catch(() => hata.push('internetsiz açılmadı'));
  await cx.close(); await b.close(); srv.close();
  console.log(hata.length ? 'HATA\n' + hata.join('\n') : 'TEMİZ'); process.exit(hata.length ? 1 : 0);
})();
