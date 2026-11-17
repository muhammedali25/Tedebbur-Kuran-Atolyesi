// Arayüz testleri: her görünüm, her rota, rastgele 40 mektup, köprü, murâkabe, arama, gezinme kutusu.
// Kullanım: node test_ui.js <sayfa adresi>   (ör. http://localhost:8765/index.html)
const { chromium } = require('playwright');
const URL = process.argv[2] || 'http://localhost:8765/index.html';
const R = []; const res = (name, ok, detail = '') => { R.push(ok); console.log(`[${ok ? 'GEÇTİ' : 'KALDI'}] ${name}${detail ? '\n        ' + detail : ''}`); };
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1400, height: 950 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto(URL); await p.waitForFunction(() => document.querySelector('#loading').hidden, { timeout: 90000 });
  await p.waitForTimeout(800);

  // rotalar
  const routes = { 'ag': 'v-ag', 'k-numan': 'v-ag', 'm-1-1': 'v-m', 'm-3-124': 'v-m', 'atlas': 'v-atlas', 'atlas-zill': 'v-atlas', 'kuran': 'v-kuran', 'kuran-18': 'v-kuran', 'seyr': 'v-seyr', 'seyr-s_imkan': 'v-seyr', 'tayf': 'v-tayf', 'tayf-kalb': 'v-tayf', 'divan': 'v-divan', 'bozuk-rota': 'v-ag', 'm-9-999': 'v-ag' };
  const bad = [];
  for (const [h, v] of Object.entries(routes)) { await p.evaluate(h => location.hash = h, h); await p.waitForTimeout(400); const vis = await p.evaluate(() => [...document.querySelectorAll('.view')].find(x => !x.hidden)?.id); if (vis !== v) bad.push(`${h}→${vis}`); }
  res(`Rotalar doğru görünümü açıyor (${Object.keys(routes).length})`, !bad.length, bad.join(', '));

  // rastgele 40 mektup: dört sütun dolu mu, köprü her dilde karşılık buluyor mu
  const keys = await p.evaluate(() => { const o = MK.IDX.order; const out = []; let s = 7; for (let i = 0; i < 40; i++) { s = (s * 1103515245 + 12345) % 2147483648; out.push(o[s % o.length]); } return out; });
  const empty = [], nobridge = [];
  await p.click('#t-hk'); // Hakikat sütununu aç
  for (const k of keys) {
    await p.evaluate(k => location.hash = 'm-' + k, k); await p.waitForTimeout(250);
    const info = await p.evaluate(() => ({ cols: [...document.querySelectorAll('.col')].map(c => [c.dataset.l, c.querySelectorAll('.s').length, c.textContent.length]) }));
    for (const [l, n, len] of info.cols) if (l && n === 0 && len > 200) empty.push(`${k}/${l}`);
    const r = await p.evaluate(() => { const ss = [...document.querySelectorAll('.col.ak .s')]; if (!ss.length) return null; const s = ss[Math.floor(ss.length / 2)]; s.click();
      return [...document.querySelectorAll('#bridge .bi')].map(x => [x.className.split(' ')[1], x.querySelector('.t').textContent.includes('bulunamadı')]); });
    if (r) for (const [l, none] of r) if (none && l !== 'hk') nobridge.push(`${k}/${l}`);
  }
  res('Rastgele 40 mektupta bütün sütunlar cümlelere bölünmüş', !empty.length, empty.join(', '));
  res('Köprü, Türkçe cümleden Farsça ve Arapça karşılığı buluyor', nobridge.length <= 2, nobridge.join(', '));

  // köprü önceden hesaplanmış hizalamayı kullanıyor mu (536 mektubun hepsinde cümle sayıları tutuyor mu)
  const pre = await p.evaluate(() => { let ok = 0, bad = []; for (const k of MK.IDX.order) { const A = MK.ALIGN[k]; for (const l of ['fa', 'ar', 'ak', 'hk']) { const u = MK.units(k, l); const n = u ? u.flat.length : 0; if (A.n[l] === n) ok++; else bad.push(`${k}/${l}:${A.n[l]}≠${n}`); } } return { ok, bad: bad.slice(0, 8), tot: MK.IDX.order.length * 4 }; });
  res(`Köprü hazır hizalamayı kullanıyor: cümle sayıları ${pre.ok}/${pre.tot} metinde tutuyor`, pre.ok === pre.tot, pre.bad.join(', '));

  // köprü simetrisi: Farsça cümle → Türkçe → geri Farsça aynı gruba dönüyor mu
  await p.evaluate(() => location.hash = 'm-2-1'); await p.waitForTimeout(500);
  const sym = await p.evaluate(() => { let ok = 0, n = 0; const fa = [...document.querySelectorAll('.col.fa .s')];
    for (const s of fa.slice(0, 60)) { s.click(); const lit = [...document.querySelectorAll('.col.ak .s.lit')]; if (!lit.length) continue; n++;
      lit[0].click(); if ([...document.querySelectorAll('.col.fa .s.lit')].some(x => x === s)) ok++; } return [ok, n]; });
  res(`Köprü simetrik (FA→TR→FA aynı cümleye dönüyor: ${sym[0]}/${sym[1]})`, sym[1] > 0 && sym[0] >= 0.95 * sym[1]);

  // murâkabe
  await p.click('#murbtn'); await p.waitForTimeout(300);
  const m1 = await p.textContent('#mur .mh'); const total = +m1.match(/\/ (\d+)/)[1];
  for (let i = 0; i < 5; i++) await p.keyboard.press('ArrowRight'); await p.waitForTimeout(200);
  const m2 = await p.textContent('#mur .mh'); await p.keyboard.press('ArrowLeft'); await p.waitForTimeout(100);
  const m3 = await p.textContent('#mur .mh'); await p.keyboard.press('Escape'); await p.waitForTimeout(100);
  const closed = await p.evaluate(() => document.querySelector('#mur').hidden);
  res(`Murâkabe: ilerleme, geri, kapatma (${total} adım)`, /6 \//.test(m2) && /5 \//.test(m3) && closed && total > 5, `${m1} → ${m2} → ${m3}`);

  // arama: sonuç sayısı, gerçek metinde bulunan terimle tutarlı
  const sr = await p.evaluate(async () => { const q = document.querySelector('#q'); q.value = 'فنا'; document.querySelector('#slang').value = 'fa'; MK.search();
    const n = +document.querySelector('.rsum').textContent.match(/^(\d+)/)[1];
    const direct = MK.IDX.order.filter(k => MK.DATA.fa.L[k] && MK.norm(MK.flat('fa', MK.DATA.fa.L[k])).includes(MK.norm('فنا'))).length;
    q.value = 'xqzwv'; MK.search(); const none = document.querySelector('.results').textContent.includes('sonuç yok');
    q.value = '"tecelli" zuhur'; document.querySelector('#slang').value = 'ak'; MK.search(); const n2 = +document.querySelector('.rsum').textContent.match(/^(\d+)/)[1];
    q.value = ''; document.querySelector('#slang').value = 'all'; return { n, direct, none, n2 }; });
  res(`Arama sonuç sayısı doğrudan sayımla aynı (فنا: ${sr.n}/${sr.direct}), boş sonuç ve ifade arama`, sr.n === sr.direct && sr.none && sr.n2 > 0, JSON.stringify(sr));
  await p.evaluate(() => location.hash = 'ag'); await p.waitForTimeout(300);

  // gezinme kutusu
  const go = async v => { await p.fill('#go', v); await p.click('#gform button'); await p.waitForTimeout(400); return p.evaluate(() => location.hash); };
  const g1 = await go('3/40'), g2 = await go('451'), g3 = await go('2.17'), g4 = await go('999');
  res('Gezinme kutusu: 3/40, 451 (Akçiçek), 2.17, geçersiz 999', g1 === '#m-3-40' && g2 === '#m-3-40' && g3 === '#m-2-17' && g4 === '#m-2-17', [g1, g2, g3, g4].join(' '));

  // Kur'ân: yay sayısı = atıf sayısı, sûre paneli toplamı
  await p.evaluate(() => location.hash = 'kuran'); await p.waitForTimeout(700);
  const q = await p.evaluate(() => ({ arcs: document.querySelectorAll('#qsvg .arc').length, refs: MK.QURAN.refs.length }));
  await p.evaluate(() => location.hash = 'kuran-2'); await p.waitForTimeout(500);
  const qb = await p.evaluate(() => ({ chips: document.querySelectorAll('#qpanel a[data-q]').length, refs: MK.QURAN.refs.filter(r => r[1] === 2).length }));
  res(`Kur'ân: her atıf bir yay (${q.arcs}/${q.refs}); Bakara panelinde her atıf bir çip (${qb.chips}/${qb.refs})`, q.arcs === q.refs && qb.chips === qb.refs);

  // seyr ve atlas: panel sayıları veriyle aynı
  await p.evaluate(() => location.hash = 'seyr-s_nubuvvet'); await p.waitForTimeout(400);
  const sy = await p.evaluate(() => ({ li: document.querySelectorAll('#spanel .thread li').length, n: MK.ATLAS.counts.s_nubuvvet.fa.filter(x => x).length }));
  res(`Seyr: kemâlât-ı nübüvvet listesi veriyle aynı (${sy.li}/${sy.n})`, sy.li === sy.n);
  await p.evaluate(() => location.hash = 'atlas-fena'); await p.waitForTimeout(500);
  const at = await p.evaluate(() => document.querySelector('.stats b').textContent);
  const atn = await p.evaluate(() => String(MK.ATLAS.byId.fena.tfa));
  res(`Atlas: fenâ sayısı panelde doğru (${at}/${atn})`, at === atn);

  // divan arama
  await p.evaluate(() => location.hash = 'divan'); await p.waitForTimeout(500);
  const all = await p.$$eval('.beyit', x => x.length); await p.fill('#dq', 'aşk'); await p.waitForTimeout(400);
  const some = await p.$$eval('.beyit', x => x.length);
  res(`Divan: ${all} beyit, "aşk" araması daraltıyor (${some})`, all > 250 && some > 0 && some < all);

  // telefon genişliği
  await p.setViewportSize({ width: 380, height: 800 });
  const wide = [];
  for (const h of ['ag', 'm-1-23', 'atlas', 'kuran-2', 'seyr', 'tayf-fena', 'divan']) { await p.evaluate(h => location.hash = h, h); await p.waitForTimeout(500); const w = await p.evaluate(() => document.documentElement.scrollWidth); if (w > 380) wide.push(`${h}:${w}`); }
  res('Telefon genişliğinde (380 px) yatay kayma yok', !wide.length, wide.join(', '));

  res('Konsolda hata yok', !errs.length, errs.slice(0, 5).join(' | '));
  console.log(`\nÖZET: ${R.filter(x => x).length} geçti, ${R.filter(x => !x).length} kaldı`);
  await b.close();
})();
