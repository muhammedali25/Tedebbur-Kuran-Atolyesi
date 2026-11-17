// Tek dosyalık sürümü ağ kapalıyken, doğrudan dosyadan açıp dener.
const { chromium, devices } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const hata = [];
  for (const [ad, ayar] of [['iphone', devices['iPhone 14']], ['mac', { viewport: { width: 1280, height: 850 } }]]) {
    const cx = await b.newContext({ ...ayar, offline: true }); const pg = await cx.newPage();
    pg.on('pageerror', (e) => hata.push(ad + ' JS: ' + e.message));
    const u = 'file://' + path.join(__dirname, '..', '..', 'dist', 'Tedebbur.html');
    for (const r of ['', '#oku-2-255', '#kok', '#kavram', '#sure-36', '#harita', '#ef', '#ef-1', '#esma', '#sayim', '#ara', '#yontem']) {
      await pg.goto(u + r); await pg.reload(); await pg.waitForSelector('.sec', { timeout: 20000 }); await pg.waitForTimeout(300);
      const t = await pg.evaluate(() => document.documentElement.scrollWidth - innerWidth); if (t > 1) hata.push(`${ad} ${r} taşma ${t}px`);
    }
    await pg.goto(u + '#oku-1'); await pg.reload(); await pg.waitForSelector('#a2 .w'); await pg.click('#a2 .w >> nth=0'); await pg.waitForTimeout(300);
    if (!(await pg.locator('#panel').innerText()).includes('ح م د')) hata.push(ad + ' kelime paneli');
    await pg.goto(u + '#ara'); await pg.reload(); await pg.waitForSelector('#ara-q'); await pg.fill('#ara-q', 'sabredenler'); await pg.waitForTimeout(600);
    if (!(await pg.locator('#ara-s .gecis').count())) hata.push(ad + ' arama');
    if (process.argv[2]) { await pg.goto(u + '#sure-36'); await pg.reload(); await pg.waitForSelector('.sec'); await pg.waitForTimeout(400); await pg.screenshot({ path: `${process.argv[2]}/tek-${ad}.png` }); }
    await cx.close();
  }
  await b.close(); console.log(hata.length ? 'HATA\n' + hata.join('\n') : 'TEMİZ'); process.exit(hata.length ? 1 : 0);
})();
