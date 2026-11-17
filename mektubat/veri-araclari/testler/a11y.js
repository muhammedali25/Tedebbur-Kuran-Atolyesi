// Erişilebilirlik: axe-core (WCAG 2.1 A/AA) her görünümde, açık ve koyu temada; klavye gezinmesi.
const { chromium } = require('playwright');
const fs = require('fs');
const URL = process.argv[2] || 'http://localhost:8765/index.html';
const AXE = fs.readFileSync(__dirname + '/node_modules/axe-core/axe.min.js', 'utf8');
(async () => {
  const b = await chromium.launch();
  const summary = {};
  for (const scheme of ['light', 'dark']) {
    const p = await b.newPage({ viewport: { width: 1300, height: 900 }, colorScheme: scheme });
    await p.goto(URL); await p.evaluate(() => { try { localStorage.setItem('mk3-ui', JSON.stringify({ anim: false })); } catch (e) { } }); await p.reload();
    await p.waitForFunction(() => document.querySelector('#loading').hidden, { timeout: 120000 });
    for (const h of ['ag', 'k-numan', 'm-1-23', 'atlas-fena', 'kuran-2', 'seyr-s_kabe', 'tayf-fena', 'divan']) {
      await p.evaluate(h => location.hash = h, h); await p.waitForTimeout(700);
      await p.addScriptTag({ content: AXE });
      const r = await p.evaluate(async () => {
        const out = await axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa'] }, resultTypes: ['violations'] });
        return out.violations.map(v => ({ id: v.id, impact: v.impact, n: v.nodes.length, help: v.help, ex: v.nodes.slice(0, 2).map(n => n.target.join(' ') + ' :: ' + (n.failureSummary || '').split('\n')[1]) }));
      });
      for (const v of r) { const key = `${v.id}`; summary[key] = summary[key] || { impact: v.impact, help: v.help, where: new Set(), n: 0, ex: v.ex }; summary[key].where.add(`${scheme}:${h}`); summary[key].n += v.n; }
    }
    await p.close();
  }
  const keys = Object.keys(summary);
  console.log(`[${keys.length ? 'UYARI' : 'GEÇTİ'}] axe-core WCAG 2.1 AA denetimi: ${keys.length} kural ihlali türü`);
  for (const k of keys) { const s = summary[k]; console.log(`   - ${k} (${s.impact}, ${s.n} öğe): ${s.help}\n       yerler: ${[...s.where].join(', ')}\n       örnek: ${s.ex.join(' | ')}`); }

  // klavye
  const p = await b.newPage({ viewport: { width: 1300, height: 900 } });
  await p.goto(URL + '#ag'); await p.waitForFunction(() => document.querySelector('#loading').hidden, { timeout: 120000 });
  let invisible = 0, total = 0;
  for (let i = 0; i < 40; i++) {
    await p.keyboard.press('Tab');
    const vis = await p.evaluate(() => { const e = document.activeElement; if (!e || e === document.body) return null; const cs = getComputedStyle(e); return (cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) > 0) || cs.boxShadow !== 'none'; });
    if (vis === null) continue; total++; if (!vis) invisible++;
  }
  console.log(`[${invisible ? 'UYARI' : 'GEÇTİ'}] Tab ile gezinmede odak görünür (${total - invisible}/${total})`);
  await p.focus('#netsvg .node[data-id="said"]'); await p.keyboard.press('Enter'); await p.waitForTimeout(300);
  const h1 = await p.evaluate(() => location.hash);
  await p.evaluate(() => location.hash = 'seyr'); await p.waitForTimeout(300);
  await p.focus('#ssvg .ring[data-id="s_kabe"]'); await p.keyboard.press('Enter'); await p.waitForTimeout(300);
  const h2 = await p.evaluate(() => location.hash);
  console.log(`[${h1 === '#k-said' && h2 === '#seyr-s_kabe' ? 'GEÇTİ' : 'KALDI'}] Ağ düğümü ve seyr halkası Enter ile açılıyor (${h1}, ${h2})`);
  await p.evaluate(() => location.hash = 'm-1-1'); await p.waitForTimeout(500);
  await p.focus('.col.ak .cb'); await p.keyboard.press('ArrowDown'); await p.keyboard.press('ArrowDown'); await p.keyboard.press('Enter'); await p.waitForTimeout(300);
  const kb = await p.evaluate(() => ({ open: !document.querySelector('#bridge').hidden, focused: document.activeElement.classList.contains('s') }));
  console.log(`[${kb.open && kb.focused ? 'GEÇTİ' : 'KALDI'}] Köprü klavyeyle kullanılabiliyor (sütuna odaklan, ↓, Enter): ${JSON.stringify(kb)}`);
  await b.close();
})();
