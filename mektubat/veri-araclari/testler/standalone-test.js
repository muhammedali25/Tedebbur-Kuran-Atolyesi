// Tek dosyalık HTML'i file:// ile, bütün ağ istekleri kesilmiş hâlde dener.
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1400, height: 950 } });
  const errs = [], net = [];
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:') || u.startsWith('data:')) r.continue(); else { net.push(u); r.abort(); } });
  p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + __dirname + '/dist/Mektubat.html');
  await p.waitForFunction(() => document.querySelector('#loading').hidden, { timeout: 60000 });
  for (const h of ['ag', 'm-1-23', 'atlas-fena', 'kuran-2', 'seyr-s_kabe', 'tayf-kalb', 'divan']) {
    await p.evaluate(h => location.hash = h, h); await p.waitForTimeout(900);
    const vis = await p.evaluate(() => [...document.querySelectorAll('.view')].find(v => !v.hidden)?.id);
    console.log(h.padEnd(12), '→', vis);
  }
  const fonts = await p.evaluate(async () => { await document.fonts.ready; return [...new Set([...document.fonts].filter(f => f.status === 'loaded').map(f => f.family))]; });
  console.log('yazı tipleri:', fonts.join(', '));
  console.log('dış istek:', net.length ? net : 'yok'); console.log('hatalar:', errs.length ? errs : 'yok');
  await b.close();
})();
