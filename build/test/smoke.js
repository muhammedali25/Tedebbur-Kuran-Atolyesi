// Yerel duman sınaması: sayfayı gerçek tarayıcıda açar, her ekranı gezer, hataları toplar.
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const kok = path.join(__dirname, '..', '..', 'site');
const tip = { '.html': 'text/html; charset=utf-8', '.json': 'application/json' };
const srv = http.createServer((q, r) => {
  let p = decodeURIComponent(q.url.split('?')[0]); if (p === '/') p = '/index.html';
  const f = path.join(kok, p); if (!f.startsWith(kok) || !fs.existsSync(f)) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'content-type': tip[path.extname(f)] || 'text/plain' });
  if (p === '/index.html') r.end('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' + fs.readFileSync(f)); else fs.createReadStream(f).pipe(r);
});
(async () => {
  await new Promise((ok) => srv.listen(8765, ok));
  const b = await chromium.launch(); const hata = [];
  const out = process.argv[2];
  for (const [ad, w, h, tema] of [['masa', 1280, 900, 'light'], ['tel', 400, 800, 'dark']]) {
    const pg = await b.newPage({ viewport: { width: w, height: h }, colorScheme: tema });
    pg.on('pageerror', (e) => hata.push(ad + ' ' + e.message)); pg.on('console', (m) => { if (m.type() === 'error') hata.push(ad + ' console ' + m.text()); });
    for (const r of ['oku', 'oku-2-255', 'kok', 'sure-12', 'sure-112', 'harita', 'kavram', 'isim', 'isim-5', 'kalip', 'ef', 'ef-1', 'ef-2', 'ef-3', 'ef-4', 'ef-5', 'esma', 'nida', 'soru', 'dua', 'dogum', 'sayim', 'ara', 'yontem']) {
      await pg.goto('http://localhost:8765/#' + r); await pg.reload(); await pg.waitForSelector('.sec', { timeout: 20000 }); await pg.waitForTimeout(500);
      if (r === 'oku-2-255') { await pg.click('details.akr[data-gi="261"] summary'); await pg.click('#a255 .w >> nth=3'); }
      if (r === 'esma') { await pg.click('details.akr >> nth=0 >> summary'); }
      if (r === 'ef-1') { await pg.click('tr[data-sec] >> nth=2'); }
      if (r === 'kalip') { await pg.click('details.akr >> nth=0 >> summary'); }
      if (r === 'ara') { await pg.fill('#ara-q', 'sabredenler'); await pg.waitForTimeout(500); }
      const tasma = await pg.evaluate(() => document.documentElement.scrollWidth - innerWidth);
      if (tasma > 1) hata.push(`${ad} ${r} yatay taşma ${tasma}px`);
      if (out) await pg.screenshot({ path: `${out}/${ad}-${r}.png` });
    }
    if (ad === 'masa') { await pg.goto('http://localhost:8765/#kok'); await pg.reload(); await pg.waitForSelector('#kok-q'); await pg.fill('#kok-q', 'sabır'); const n = await pg.locator('.sonuc button').count(); if (!n) hata.push('kök araması boş'); await pg.fill('#kok-q', 'rhm'); if (!(await pg.locator('.sonuc button').count())) hata.push('latin kök araması boş'); }
    await pg.close();
  }
  await b.close(); srv.close();
  console.log(hata.length ? 'HATA\n' + hata.join('\n') : 'TEMİZ'); process.exit(hata.length ? 1 : 0);
})();
