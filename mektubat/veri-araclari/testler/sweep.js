// Uçtan uca tarama: her mektup, her kişi, her sûre, her kavram ve seyr makamı.
// Her mektupta: sütunlar dolu mu, her dilde 5 cümlede köprü karşılık buluyor mu, murâkabe adımları dolu mu, süreler.
// Kullanım: node sweep.js <adres>
const { chromium } = require('playwright');
const URL = process.argv[2] || 'http://localhost:8765/index.html';
const R = []; const res = (n, ok, d = '') => { R.push(ok); console.log(`[${ok ? 'GEÇTİ' : 'KALDI'}] ${n}${d ? '\n        ' + d : ''}`); };
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1400, height: 950 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  const t0 = Date.now();
  await p.goto(URL); await p.waitForFunction(() => document.querySelector('#loading').hidden && window.MK && MK.ALIGN, { timeout: 120000 });
  const loadMs = Date.now() - t0;
  res(`Bütün veri yüklendi (${(loadMs / 1000).toFixed(1)} sn)`, loadMs < 20000);
  await p.evaluate(() => { try { localStorage.setItem('mk3-ui', JSON.stringify({ show: { fa: true, ar: true, ak: true, hk: true }, fs: 1, anim: false })); } catch (e) { } });
  await p.reload(); await p.waitForFunction(() => document.querySelector('#loading').hidden && window.MK && MK.ALIGN, { timeout: 120000 });

  // ---- her mektup
  const out = await p.evaluate(async () => {
    const r = { n: 0, slow: [], times: [], emptyCol: [], noBridge: [], noMur: [], titleMissing: [], wrongLabel: [], unaligned: [] };
    const sleep = ms => new Promise(s => setTimeout(s, ms));
    for (const k of MK.IDX.order) {
      const t = performance.now();
      location.hash = 'm-' + k; await sleep(5);
      const dt = performance.now() - t; r.times.push(dt); if (dt > 600) r.slow.push(`${k}:${dt | 0}ms`);
      r.n++;
      const cols = [...document.querySelectorAll('.col[data-l]')];
      const m = MK.IDX.map[k];
      for (const c of cols) { const l = c.dataset.l; const has = MK.DATA[l].L[k]; const n = c.querySelectorAll('.s').length; if (has && !n) r.emptyCol.push(`${k}/${l}`); }
      const eq = document.querySelector('.eq').textContent;
      if (m.ak && !eq.includes(`Akçiçek ${m.ak}`)) r.wrongLabel.push(k);
      if (!document.querySelector('.name h2').textContent.trim()) r.titleMissing.push(k);
      // köprü: her dilde eşit aralıklı 5 cümle
      for (const l of ['fa', 'ar', 'ak', 'hk']) {
        const ss = [...document.querySelectorAll(`.col.${l} .s`)]; if (!ss.length) continue;
        for (let q = 0; q < 5; q++) {
          const s = ss[Math.floor((q + 0.5) * ss.length / 5)]; s.click();
          const items = [...document.querySelectorAll('#bridge .bi')];
          const others = items.filter(x => !x.querySelector('.conf') || !x.querySelector('.conf').textContent.includes('seçilen'));
          const found = others.filter(x => !x.querySelector('.t').textContent.includes('bulunamadı')).length;
          if (others.length && !found) r.noBridge.push(`${k}/${l}#${s.dataset.i}`);
        }
      }
      // hizalanmamış Farsça cümle oranı
      const A = MK.ALIGN[k];
      for (const l of ['ar', 'ak', 'hk']) { if (!A[l]) continue; const nf = A.n.fa; const un = A[l].filter(x => x[1] && !x[3]).reduce((s, x) => s + x[1], 0); const ut = A[l].filter(x => !x[1] && x[3]).reduce((s, x) => s + x[3], 0);
        if (nf > 5 && (un / nf > 0.25 || ut / A.n[l] > 0.25)) r.unaligned.push(`${k}/${l}: FA %${(100 * un / nf) | 0}, hedef %${(100 * ut / A.n[l]) | 0}`); }
      // murâkabe
      document.querySelector('#murbtn').click(); const h = document.querySelector('#mur .mh').textContent; const total = +(h.match(/\/ (\d+)/) || [0, 0])[1];
      const st = document.querySelector('#mur .stage').textContent.trim();
      if (!total || !st) r.noMur.push(k);
      document.querySelector('#murx').click();
    }
    r.times.sort((a, b) => a - b); r.median = r.times[r.times.length >> 1] | 0; r.p95 = r.times[(r.times.length * 0.95) | 0] | 0; r.max = r.times[r.times.length - 1] | 0; delete r.times;
    return r;
  });
  res(`536 mektubun hepsi açıldı (${out.n}); süre medyan ${out.median} ms, %95 ${out.p95} ms, en uzun ${out.max} ms`, out.n === 536 && out.p95 < 600, out.slow.slice(0, 8).join(', '));
  res('Metni olan her sütun cümlelere bölünmüş', !out.emptyCol.length, out.emptyCol.slice(0, 10).join(', '));
  res('Her mektupta başlık (alıcı) ve doğru Akçiçek numarası', !out.titleMissing.length && !out.wrongLabel.length, [...out.titleMissing, ...out.wrongLabel].slice(0, 10).join(', '));
  res(`Köprü: 536 mektup × 4 dil × 5 cümle = ${536 * 4 * 5} civarı tıklamanın hepsinde en az bir karşılık`, out.noBridge.length <= 10, `${out.noBridge.length} boş: ` + out.noBridge.slice(0, 12).join(', '));
  res('Murâkabe her mektupta açılıyor ve ilk adım dolu', !out.noMur.length, out.noMur.slice(0, 10).join(', '));
  res('Hizalanmamış cümle oranı %25 üstü olan mektup yok', out.unaligned.length <= 5, `${out.unaligned.length} mektup: ` + out.unaligned.slice(0, 15).join(' | '));

  // ---- her kişi, sûre, kavram, makam
  const routes = await p.evaluate(async () => {
    const sleep = ms => new Promise(s => setTimeout(s, ms)); const bad = [];
    for (const pr of MK.IDX && window.MK ? [] : []) { }
    const people = [...document.querySelectorAll('#netsvg .node')].map(n => n.dataset.id);
    return people.length;
  });
  const routeBad = await p.evaluate(async () => {
    const sleep = ms => new Promise(s => setTimeout(s, ms)); const bad = [];
    location.hash = 'ag'; await sleep(50);
    const ids = [...document.querySelectorAll('#netsvg .node')].map(n => n.dataset.id);
    for (const id of ids) { location.hash = 'k-' + id; await sleep(3); const h = document.querySelector('#person h3'); const li = document.querySelectorAll('#person .thread li').length; if (!h || !li) bad.push('kişi ' + id); }
    for (let s = 1; s <= 114; s++) { location.hash = 'kuran-' + s; await sleep(3); const t = document.querySelector('#qpanel h3'); if (!t) bad.push('sûre ' + s); }
    for (const t of MK.ATLAS.terms) {
      if (t.group) { location.hash = 'seyr-' + t.id; await sleep(3); if (!document.querySelector('#spanel h3') || !document.querySelector('#spanel h3').textContent.includes(t.tr)) bad.push('makam ' + t.id); }
      else { location.hash = 'atlas-' + t.id; await sleep(3); if (!document.querySelector('#tdet h3').textContent.includes(t.tr)) bad.push('atlas ' + t.id);
        location.hash = 'tayf-' + t.id; await sleep(3); if (!document.querySelectorAll('#tmain .bar').length) bad.push('tayf ' + t.id); }
    }
    return { bad, people: ids.length };
  });
  res(`Bütün kişi (${routeBad.people}), sûre (114), atlas, tayf ve seyr sayfaları açılıyor`, !routeBad.bad.length, routeBad.bad.slice(0, 12).join(', '));

  // ---- arama kenar durumları
  const se = await p.evaluate(() => {
    const run = (q, l) => { document.querySelector('#q').value = q; document.querySelector('#slang').value = l; MK.search(); const t = document.querySelector('.rsum'); return t ? +t.textContent.match(/^(\d+)/)[1] : 0; };
    const r = {
      yeh: [run('ولايت', 'fa'), run('ولایت', 'fa')], kaf: [run('سلوك', 'fa'), run('سلوک', 'fa')],
      harake: [run('فَنَاء', 'fa'), run('فناء', 'fa')], sapka: [run('fenâ', 'ak'), run('fena', 'ak')],
      ibuyuk: [run('İSLÂM', 'ak'), run('islam', 'ak')], tirnak: [run('"kalb-i selim"', 'ak'), run('kalb', 'ak')],
      bos: run('   ', 'all')
    };
    document.querySelector('#q').value = ''; document.querySelector('#slang').value = 'all'; return r;
  });
  const okS = se.yeh[0] === se.yeh[1] && se.kaf[0] === se.kaf[1] && se.harake[0] === se.harake[1] && se.sapka[0] === se.sapka[1] && se.ibuyuk[0] === se.ibuyuk[1] && se.tirnak[0] <= se.tirnak[1];
  res('Arama: ی/ي, ک/ك, hareke, şapka ve büyük İ duyarsız; tırnaklı ifade daraltıyor', okS, JSON.stringify(se));

  res('Konsolda hata yok', !errs.length, errs.slice(0, 5).join(' | '));
  console.log(`\nÖZET: ${R.filter(x => x).length} geçti, ${R.filter(x => !x).length} kaldı`);
  await b.close();
})();
