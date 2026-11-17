// Sürüm 1.4 özellik testleri. Kullanım: node features.js <adres>
const { chromium } = require('playwright');
const URL = process.argv[2] || 'http://localhost:8765/index.html';
const R = []; const res = (n, ok, d = '') => { R.push(ok); console.log(`[${ok ? 'GEÇTİ' : 'KALDI'}] ${n}${d ? '\n        ' + d : ''}`); };
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ viewport: { width: 1400, height: 950 } }); const p = await ctx.newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  const ready = () => p.waitForFunction(() => document.querySelector('#loading').hidden && window.MK && MK.ALIGN, { timeout: 120000 });
  await p.goto(URL); await ready();
  await p.evaluate(() => { localStorage.clear(); localStorage.setItem('mk3-ui', JSON.stringify({ anim: false, show: { fa: true, ar: true, ak: true, hk: true } })); });
  await p.reload(); await ready(); await p.waitForTimeout(600);
  const go = async h => { await p.evaluate(h => location.hash = h, h); await p.waitForTimeout(500); };

  // 1 okuma ilerlemesi ve kaldığın yer
  await go('m-1-5'); await p.click('#readbtn'); await go('m-1-7');
  const rd = await p.evaluate(() => ({ read: !!MK.READ['1-5'], dot: !!document.querySelector('#idx a.read'), sum: document.querySelector('#idx summary small').textContent }));
  await p.reload(); await ready(); await go('ag');
  const resume = await p.evaluate(() => (document.querySelector('.resume') || {}).textContent || '');
  res('Okudum işareti, defter sayacı ve kaldığın yer kalıcı', rd.read && rd.dot && rd.sum.includes('1/313') && resume.includes('1/7') && resume.includes('1/536'), JSON.stringify(rd) + ' | ' + resume);

  // 2 altını çizme ve not
  await go('m-1-5'); const ss = await p.$$('.col.ak .s'); await ss[3].click(); await p.waitForTimeout(200);
  await p.click('.bact [data-a="hl"]'); await p.waitForTimeout(200);
  const hl = await p.evaluate(() => ({ n: MK.HL.length, ak: document.querySelectorAll('.col.ak .s.hl').length, fa: document.querySelectorAll('.col.fa .s.hl').length, ar: document.querySelectorAll('.col.ar .s.hl').length }));
  await p.click('.bact [data-a="note"]'); await p.fill('#bnotet', 'deneme notu'); await p.click('#bnotes');
  await p.reload(); await ready(); await go('m-1-5');
  const hl2 = await p.evaluate(() => ({ ak: document.querySelectorAll('.col.ak .s.hl').length, note: MK.HL[0] && MK.HL[0].note }));
  await go('notlar'); const notesTxt = await p.textContent('#notes');
  await p.click('#nexp'); const exp = await p.inputValue('#expbody textarea'); await p.click('#expclose');
  res('Altını çizme karşılıklarıyla işaretliyor, not kalıcı, Notlarım ve dışa aktarma dolu', hl.n === 1 && hl.ak >= 1 && hl.fa >= 1 && hl2.ak >= 1 && hl2.note === 'deneme notu' && notesTxt.includes('deneme notu') && exp.includes('NOT: deneme notu') && exp.includes('FA:'), JSON.stringify(hl));

  // 13 hatalı eşleşme bildirimi
  await go('m-1-5'); await (await p.$$('.col.ak .s'))[6].click(); await p.click('.bact [data-a="rep"]'); await p.waitForTimeout(200);
  const rep = await p.evaluate(() => MK.REP.length);
  await go('notlar'); await p.click('#rexp'); const rj = await p.inputValue('#expbody textarea'); await p.click('#expclose');
  let rjOk = false; try { rjOk = JSON.parse(rj).length === 1; } catch (e) { }
  res('Hatalı eşleşme bildirimi kaydediliyor ve JSON olarak dışa aktarılıyor', rep === 1 && rjOk);

  // 9 kart
  await go('m-1-5'); await (await p.$$('.col.ak .s'))[3].click(); await p.click('.bact [data-a="card"]'); await p.waitForSelector('#expbody img', { timeout: 15000 });
  const card = await p.evaluate(async () => { const im = document.querySelector('#expbody img'); await im.decode(); return { w: im.naturalWidth, h: im.naturalHeight, len: im.src.length }; });
  await p.click('#expclose');
  res(`Cümle kartı üretiliyor (${card.w}×${card.h})`, card.w === 1080 && card.h === 1350 && card.len > 50000);

  // 12 kelime açıklaması
  await go('m-1-1'); await p.waitForTimeout(300);
  const gl = await p.evaluate(() => { const g = document.querySelector('.col.ak .gl'); if (!g) return null; g.click(); return { n: document.querySelectorAll('.col.ak .gl').length, word: g.textContent, pop: document.querySelector('#glpop').textContent, hidden: document.querySelector('#glpop').hidden }; });
  res('Kelime açıklamaları işaretli ve dokununca açılıyor', gl && gl.n >= 5 && !gl.hidden && gl.pop.length > gl.word.length + 5, JSON.stringify(gl));
  const par = await p.evaluate(() => { const u = MK.units('1-1', 'ak'); const dom = [...document.querySelectorAll('.col.ak .s')].map(e => e.textContent); return dom.length === u.flat.length && dom.every((t, i) => t === u.flat[i]); });
  res('Kelime işaretleme cümle metinlerini değiştirmiyor', par);

  // 3 senkron kaydırma
  await go('m-2-1'); await p.waitForTimeout(300);
  const sync = await p.evaluate(async () => { const a = document.querySelector('.col.ak .cb'), f = document.querySelector('.col.fa .cb'); const f0 = f.scrollTop;
    a.dispatchEvent(new WheelEvent('wheel')); a.scrollTop = a.scrollHeight * 0.5; await new Promise(r => setTimeout(r, 400));
    const top = f.scrollTop + f.offsetTop; let first = null; for (const e of f.querySelectorAll('.s')) { if (e.offsetTop + e.offsetHeight > top + 4) { first = +e.dataset.i; break; } }
    return { moved: f.scrollTop > f0 + 200, frac: first / f.querySelectorAll('.s').length }; });
  res(`Senkron kaydırma: Türkçe sütunu ortaya kaydırınca Farsça da ortaya geliyor (%${Math.round(sync.frac * 100)})`, sync.moved && sync.frac > 0.3 && sync.frac < 0.7);

  // 4 okuma ayarları
  await p.click('#openSet'); await p.click('#setdlg [data-set="theme"] [data-v="sepia"]'); await p.click('#setdlg [data-set="lh"] [data-v="1.18"]'); await p.click('#setdlg [data-set="trfont"] [data-v="sans"]'); await p.click('#setclose');
  const st = await p.evaluate(() => ({ theme: document.documentElement.getAttribute('data-theme'), bg: getComputedStyle(document.body).backgroundColor, lh: getComputedStyle(document.documentElement).getPropertyValue('--lh').trim(), ff: getComputedStyle(document.querySelector('.col.ak .cb')).fontFamily.slice(0, 12) }));
  await p.reload(); await ready(); const st2 = await p.evaluate(() => document.documentElement.getAttribute('data-theme'));
  await p.click('#openSet'); await p.click('#setdlg [data-set="theme"] [data-v="system"]'); await p.click('#setdlg [data-set="lh"] [data-v="1"]'); await p.click('#setdlg [data-set="trfont"] [data-v="serif"]'); await p.click('#setclose');
  res('Okuma ayarları: sepya tema, satır aralığı, Türkçe yazı; kalıcı', st.theme === 'sepia' && st.bg === 'rgb(232, 220, 193)' && st.lh === '1.18' && st.ff.startsWith('system-ui') && st2 === 'sepia', JSON.stringify(st));

  // 5 arama süzgeçleri ve üç dilde sonuç
  const sr = await p.evaluate(async () => { const cnt = () => +document.querySelector('.rsum').textContent.match(/^(\d+)/)[1];
    document.querySelector('#q').value = 'tecelli'; document.querySelector('#slang').value = 'ak'; MK.search(); const all = cnt();
    const sd = document.querySelector('#sdef'); sd.value = '2'; sd.dispatchEvent(new Event('change')); const d2 = cnt(); const ids = [...document.querySelectorAll('.resrow')].every(r => r.dataset.id.startsWith('2-'));
    const sw = document.querySelector('#swho'); sw.value = 'numan'; sw.dispatchEvent(new Event('change')); const dw = cnt();
    const btn = document.querySelector('.resrow [data-a="tri"]'); btn.click(); const tri = document.querySelector('.res3') ? document.querySelector('.res3').children.length : 0; const triFa = !!document.querySelector('.res3 .f');
    const sd2 = document.querySelector('#sdef'); sd2.value = '0'; sd2.dispatchEvent(new Event('change')); const sw2 = document.querySelector('#swho'); sw2.value = ''; sw2.dispatchEvent(new Event('change'));
    document.querySelector('#q').value = ''; document.querySelector('#slang').value = 'all'; return { all, d2, ids, dw, tri, triFa }; });
  res('Arama: defter ve alıcı süzgeci daraltıyor; sonuç üç dilde açılıyor', sr.d2 < sr.all && sr.d2 > 0 && sr.ids && sr.dw <= sr.d2 && sr.dw > 0 && sr.tri >= 2 && sr.triFa, JSON.stringify(sr));

  // 11 karşılaştırma
  await go('kars-1-45');
  const ks = await p.evaluate(() => { const rows = [...document.querySelectorAll('.krow')]; const txt = sel => rows.map(r => r.querySelector(sel).textContent).join(' ').replace(/\s+/g, ' ').trim();
    const ua = MK.units('1-45', 'ak').flat.join(' ').replace(/\s+/g, ' ').trim(), uh = MK.units('1-45', 'hk').flat.join(' ').replace(/\s+/g, ' ').trim();
    return { rows: rows.length, akAll: txt('.kak').replace(/—/g, '').replace(/\s+/g, ' ').trim().length, ua: ua.length, hkAll: txt('.khk').replace(/—/g, '').replace(/\s+/g, ' ').trim().length, uh: uh.length, diff: document.querySelectorAll('.krow .same').length }; });
  await go('kars-2-1'); const ks2 = await p.textContent('#v-kars');
  res(`Akçiçek ↔ Hakikat: ${ks.rows} satır, iki tercümenin bütün metni yer alıyor`, ks.rows > 5 && Math.abs(ks.akAll - ks.ua) < 0.02 * ks.ua && Math.abs(ks.hkAll - ks.uh) < 0.02 * ks.uh && ks.diff > 10 && ks2.includes('yalnız 1. defteri'), JSON.stringify(ks));

  // 10 birliktelik diyagramı
  await go('atlas-fena');
  const ch = await p.evaluate(() => ({ labels: document.querySelectorAll('#chord text').length, paths: document.querySelectorAll('#chord path').length, on: document.querySelectorAll('#chord path.on').length, chips: document.querySelector('#chordhost .chips') ? document.querySelector('#chordhost .chips').textContent : '' }));
  res(`Kavram birlikteliği: ${ch.labels} kavram, ${ch.paths} bağ; fenâ'nın en yakını listede`, ch.labels === 32 && ch.paths >= 70 && ch.on > 0 && ch.chips.includes('Bekâ'), ch.chips);

  // 7 ağın büyümesi, 6 mürekkep yolu
  await go('ag'); const n0 = await p.evaluate(() => document.querySelectorAll('#netsvg .node').length); await p.click('#netplay'); await p.waitForTimeout(900);
  const pl1 = await p.evaluate(() => ({ n: document.querySelectorAll('#netsvg .node').length, info: document.querySelector('#playinfo').textContent }));
  await p.waitForTimeout(1500); const pl2 = await p.evaluate(() => document.querySelectorAll('#netsvg .node').length);
  await p.click('#netplay'); await p.waitForTimeout(200); const pl3 = await p.evaluate(() => document.querySelectorAll('#netsvg .node').length);
  res(`Ağın büyümesi: ${pl1.n} → ${pl2} → durdurunca ${pl3} alıcı`, pl1.n > 0 && pl2 > pl1.n && pl3 === n0 && n0 > 150 && /defter/.test(pl1.info), pl1.info);
  await p.evaluate(() => localStorage.setItem('mk3-ui', JSON.stringify({ anim: true, show: { fa: true, ar: true, ak: true, hk: true } }))); await p.reload(); await ready();
  await go('k-said'); const ink = await p.evaluate(() => !!document.querySelector('#netsvg .inkflow')); await p.waitForTimeout(1700); const inkGone = await p.evaluate(() => !document.querySelector('#netsvg .inkflow'));
  res('Mürekkep yolu: kişi seçilince çizgi akıyor ve bitince kalkıyor', ink && inkGone);

  // 8 murâkabe girih
  await go('m-1-23'); await p.waitForTimeout(400); await p.click('#murbtn'); await p.waitForTimeout(500);
  const g1 = await p.evaluate(() => { const c = document.querySelector('#mur canvas.girih'); return c ? c.style.transform : null; }); await p.keyboard.press('ArrowRight'); await p.waitForTimeout(700);
  const g2 = await p.evaluate(() => { const c = document.querySelector('#mur canvas.girih'); return c ? c.style.transform : null; }); await p.keyboard.press('Escape');
  res('Murâkabe arka planı: girih deseni adımlar arasında kesintisiz dönüyor', !!g1 && !!g2 && g1 !== g2, `${g1} → ${g2}`);

  // 15 sesli okuma (tarayıcı sesi varsa)
  const tts = await p.evaluate(async () => { if (!('speechSynthesis' in window)) return 'yok'; document.querySelector('#saybtn').click(); await new Promise(r => setTimeout(r, 300)); const on = !!document.querySelector('.s.speaking'); const lab = document.querySelector('#saybtn').textContent; document.querySelector('#saybtn').click(); return { on, lab, off: !document.querySelector('.s.speaking') }; });
  const tmsg = await p.evaluate(() => document.querySelector('#toast').textContent);
  // Ses motoru olan cihazda okuma sürer; olmayan cihazda (bu test ortamı gibi) tek cümlede durup haber vermelidir
  res('Sesli okuma: ya okuyup işaretliyor ya da ses yoksa durup haber veriyor', tts === 'yok' || (tts.on && tts.lab === 'Durdur' && tts.off) || (!tts.on && tts.lab === 'Sesli oku' && /ses bulunamadı/.test(tmsg)), JSON.stringify(tts) + ' | ' + tmsg);

  // telefon genişliği ve hatalar
  await p.setViewportSize({ width: 380, height: 800 }); const wide = [];
  for (const h of ['notlar', 'kars-1-45', 'atlas-fena', 'm-1-5']) { await go(h); const w = await p.evaluate(() => document.documentElement.scrollWidth); if (w > 380) wide.push(`${h}:${w}`); }
  res('Yeni görünümlerde telefon genişliğinde yatay kayma yok', !wide.length, wide.join(', '));
  res('Konsolda hata yok', !errs.length, errs.slice(0, 5).join(' | '));
  console.log(`\nÖZET: ${R.filter(x => x).length} geçti, ${R.filter(x => !x).length} kaldı`);
  await b.close();
})();
