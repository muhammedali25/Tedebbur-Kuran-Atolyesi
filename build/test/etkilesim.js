// Etkileşim sınaması: tıklama, arama, süzme ve gezinme yollarını gerçek tarayıcıda dener.
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const kok = path.join(__dirname, '..', '..', 'site');
const srv = http.createServer((q, r) => {
  let p = decodeURIComponent(q.url.split('?')[0]); if (p === '/') p = '/index.html';
  const f = path.join(kok, p); if (!f.startsWith(kok) || !fs.existsSync(f)) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'content-type': p.endsWith('.json') ? 'application/json' : 'text/html; charset=utf-8' });
  if (p === '/index.html') r.end('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' + fs.readFileSync(f)); else fs.createReadStream(f).pipe(r);
});
const hata = []; let pg;
const bekle = (ms = 250) => pg.waitForTimeout(ms);
const ac = async (h) => { await pg.goto('http://localhost:8766/#' + h); await pg.reload(); await pg.waitForSelector('.sec', { timeout: 20000 }); await bekle(400); };
const um = (kosul, ad) => { if (!kosul) hata.push(ad); };
const metin = (s) => pg.locator(s).first().innerText();
(async () => {
  await new Promise((ok) => srv.listen(8766, ok));
  const b = await chromium.launch();
  for (const [ad, w, h] of [['masa', 1280, 900], ['tel', 400, 800]]) {
    pg = await b.newPage({ viewport: { width: w, height: h }, hasTouch: ad === 'tel' });
    pg.on('pageerror', (e) => hata.push(ad + ' JS: ' + e.message)); pg.on('console', (m) => { if (m.type() === 'error') hata.push(ad + ' konsol: ' + m.text()); });
    const U = (k, a) => um(k, ad + ': ' + a);
    // oku: kelime paneli, akraba ayet, iki meal, gezinme
    await ac('oku-1'); await pg.click('#a2 .w >> nth=0'); await bekle();
    U((await metin('#panel')).includes('Fâtiha 2'), 'kelime paneli Fâtiha 2 göstermiyor');
    U((await metin('#panel')).includes('ح م د'), 'el-hamdü kökü hmd değil');
    U((await pg.locator('#a1').innerText()).includes('besmele'), 'besmele notu yok');
    U((await pg.locator('#a3').innerText()).includes('birlikte verilmiş'), 'birleşik meal notu yok');
    if (ad === 'tel') { await pg.click('#pk'); U(await pg.locator('#panel.kapali').count() === 1, 'panel kapanmadı'); }
    await pg.click('#oku-iki'); await bekle(); U(await pg.locator('.meal-ad').count() > 4, 'ikinci meal açılmadı');
    U((await pg.locator('#a1').innerText()).includes('Rahmân ve Rahîm'), 'Elmalılı besmelesi yok');
    await pg.click('#oku-iki'); await bekle(); U(await pg.locator('.meal-ad').count() === 0, 'ikinci meal kapanmadı');
    await ac('oku-37-130'); U(await pg.locator('#a130 .w').count() === 3, '37:130 üç kelime değil: ' + await pg.locator('#a130 .w').count());
    await pg.click('#a130 .w >> nth=2'); await bekle(); U((await metin('#panel')).includes('3. kelime'), '37:130 son kelime paneli');
    await ac('oku-2-286'); U(await pg.locator('#a286').count() === 1, 'Bakara 286 çizilmedi');
    await pg.fill('#oku-ayet', '255'); await pg.click('#oku-git'); await bekle(500); U(await pg.locator('#a255.hedef').count() === 1, 'ayete git çalışmadı');
    await pg.click('details.akr[data-gi="261"] summary'); await bekle(); const akr = await pg.locator('details.akr[data-gi="261"] .akr-i').count(); U(akr > 0, 'Âyetü\'l-Kürsî akrabası yok');
    await pg.selectOption('#oku-sure', '114'); await bekle(500); U((await metin('h1')).includes('Nâs'), 'sure seçici çalışmadı');
    await ac('oku-999'); U((await metin('h1')).includes('Nâs'), 'geçersiz sure 114\'e sıkışmadı');
    await ac('oku-'); U((await metin('h1')).includes('Fâtiha'), '#oku- Fâtiha açmadı');
    // kök
    await ac('kok'); U((await metin('.kok-buyuk')).replace(/\s/g, '') === 'رحم', 'varsayılan kök rhm değil');
    await pg.fill('#kok-q', 'sabır'); await bekle(); await pg.click('.sonuc button >> nth=0'); await bekle(500);
    U((await metin('.kok-buyuk')).replace(/\s/g, '') === 'صبر', 'sabır araması sbr kökünü açmadı');
    const tum = await pg.locator('#kok-gec .gecis').count(); await pg.click('#kok-lem [data-l] >> nth=1'); await bekle();
    U(await pg.locator('#kok-gec .gecis mark, #kok-gec .sec-w').count() > 0, 'türev süzünce vurgu yok'); U(tum === 25, 'geçiş listesi 25 değil: ' + tum);
    await pg.click('#kok-sira [data-v=nuzul]'); await pg.click('#kok-olcu [data-v=binde]'); await bekle(); U((await metin('#kok-grafik')).includes('binde'), 'binde ölçüsü çizilmedi');
    await pg.fill('#kok-q', 'رحم'); await bekle(); U(await pg.locator('.sonuc button').count() >= 1, 'Arapça kök araması boş');
    await pg.fill('#kok-q', 'zzzz'); await bekle(); U((await pg.locator('#kok-s').innerText()).includes('bulunamadı'), 'boş arama iletisi yok');
    await pg.click('#kok-kav'); await bekle(500); U((await pg.evaluate(() => location.hash)).startsWith('#kavram-'), 'kavrama ekle yönlendirmedi');
    // kavram
    await ac('kavram'); U(await pg.locator('.mini').count() === 3, 'kavram varsayılan 3 kök değil');
    await pg.click('[data-cik] >> nth=0'); await bekle(500); U(await pg.locator('.mini').count() === 2, 'kök çıkarma çalışmadı');
    await pg.fill('#kav-q', 'sabır'); await bekle(); await pg.click('#kav-s .sonuc button >> nth=0'); await bekle(500); U(await pg.locator('.mini').count() === 3, 'kök ekleme çalışmadı');
    await ac('kavram-'); U(await pg.locator('.mini').count() >= 1, '#kavram- boş');
    // sure, harita
    await ac('sure-55'); U((await metin('.fas')).length > 70, 'Rahmân fâsıla şeridi eksik'); await pg.click('.fas span >> nth=4'); await bekle(500); U((await pg.evaluate(() => location.hash)) === '#oku-55-5', 'fâsıla tıklaması ayete gitmedi');
    await ac('harita'); await pg.selectOption('#h-y', 'emir'); await pg.selectOption('#h-x', 'mushaf'); await bekle(); U(await pg.locator('#h-g circle').count() > 100, 'harita daireleri eksik');
    await pg.locator('#h-b [data-h] >> nth=0').click(); await bekle(); U(await pg.locator('#h-g line[stroke="var(--gold)"]').count() >= 1, 'komşu çizgileri yok');
    // harita'dan sonra başka ekranda tıklama sızıntısı
    await ac('harita'); await pg.evaluate(() => { location.hash = 'nida'; }); await bekle(600); await pg.click('tr[data-sec] >> nth=3'); await bekle(400); U(await pg.locator('tr.secili').count() === 1 && (await pg.locator('#ni-l .gecis').count()) > 0, 'haritadan sonra nidâ satırı bozuldu');
    // efendimiz
    await ac('ef'); U((await metin('.stats')).includes('332'), 'kul 332 değil'); U(await pg.locator('#ef-l .gecis').count() === 20, 'kul ayet listesi');
    U(await pg.locator('#ef-l .gecis >> nth=0 >> .sec-w').count() >= 1, 'kul vurgusu yok');
    await ac('ef-1'); const s1 = await pg.locator('tr[data-sec]').count(); await pg.click('#ef-g'); await bekle(500); const s2 = await pg.locator('tr[data-sec]').count(); U(s2 > s1, 'aktarım süzgeci satır sayısını değiştirmedi');
    await pg.click('tr[data-sec] >> nth=4'); await bekle(500); U(await pg.locator('tr.secili').count() === 1 && await pg.locator('#ef-l .sec-w').count() >= 1, 'emir satırı seçimi');
    for (const k of [2, 3, 4, 5]) { await ac('ef-' + k); U(await pg.locator('.sec').count() >= 2, 'ef-' + k + ' boş'); }
    await ac('ef-3'); U(await pg.locator('#ef-n0 .sec-w').count() >= 2, 'sesleniş vurgusu');
    await ac('ef-9'); U(await pg.locator('.alt a[aria-current]').count() === 1, 'ef-9 geçersiz bölüm');
    // keşif
    await ac('esma'); const e1 = await pg.locator('.kalip').count(); await pg.click('#es-t [data-v="1"]'); await bekle(500); U(await pg.locator('.kalip').count() > e1, 'tüm çiftler süzgeci');
    await pg.click('details.akr >> nth=0 >> summary'); await bekle(); U(await pg.locator('details.akr >> nth=0 >> .sec-w').count() === 20, 'çift vurgusu son iki kelime değil');
    await ac('soru'); await pg.click('.bar-row[data-sec="5"]'); await bekle(500); U((await metin('#so-l')).length > 50, 'soru türü seçimi');
    await ac('dua'); U(await pg.locator('#du-l .gecis >> nth=0 >> .sec-w').count() === 2, 'dua vurgusu iki kelime değil');
    await ac('dogum'); await pg.locator('[data-d] >> nth=0').click({ force: true }); await bekle(500); U((await metin('main')).includes('Alak ile gelen'), 'doğum: ilk sure Alak değil');
    await ac('isim-1'); U((await metin('main')).includes('Mûsâ'), 'isim-1 Mûsâ değil'); 
    await ac('kalip'); await pg.click('#kal-sira [data-v=uzun]'); await bekle(500); await pg.click('details.akr >> nth=0 >> summary'); await bekle(); U(await pg.locator('details.akr >> nth=0 >> .chip').count() >= 2, 'kalıp yerleri');
    await ac('sayim'); U(await pg.locator('.tutan').count() >= 8, 'sayım işaretleri eksik');
    // ara
    await ac('ara'); await pg.fill('#ara-q', "Allah'ın"); await bekle(600); U(await pg.locator('#ara-s mark').count() > 0, 'kesmeli Türkçe aramada vurgu yok');
    U((await metin('#ara-s mark')).toLowerCase().replace(/[’']/g, '') === 'allahın', 'vurgu yanlış yerde: ' + await metin('#ara-s mark'));
    await pg.fill('#ara-q', 'rahmân'); await bekle(600); U(await pg.locator('#ara-s mark').count() > 0, 'şapkalı arama');
    await pg.selectOption('#ara-m', '2'); await bekle(600); U((await metin('#ara-o')).includes('bulundu'), 'Elmalılı araması');
    await pg.fill('#ara-q', 'الصراط المستقيم'); await bekle(600); const v = await pg.locator('#ara-s .gecis >> nth=0 >> .sec-w').count(); U(v === 2, 'Arapça ifade vurgusu 2 kelime değil: ' + v);
    await pg.fill('#ara-q', 'x'); await bekle(400); U((await metin('#ara-o')).includes('iki harf'), 'kısa arama uyarısı');
    // inceleme bulgularının geri dönmemesi için
    await ac('ara'); await pg.fill('#ara-q', 'ــ'); await bekle(600); U((await metin('#ara-o')).includes('iki harf'), 'yalnız uzatma işaretiyle arama donuyor/eşleşiyor');
    await pg.fill('#ara-q', "''"); await bekle(600); U((await metin('#ara-o')).includes('iki harf'), 'yalnız kesme işaretiyle arama her şeyi buluyor');
    await ac('oku-2-255'); await bekle(1500); const ust = await pg.evaluate(() => document.querySelector('#a255').getBoundingClientRect().top); U(ust > -5 && ust < 200, 'doğrudan bağlantı 255. ayete oturmadı: ' + Math.round(ust));
    // düğme sayfanın başında olduğu için tıklama anında görünen ilk ayet korunmalı, yüklenen ayetler de kalmalı
    await ac('oku-2'); await pg.click('#oku-daha'); await bekle(); await pg.click('#oku-iki'); await bekle(500);
    U(await pg.locator('#a40').count() === 1, 'meal değişince yüklenen ayetler kayboldu'); await pg.click('#oku-iki'); await bekle(300);
    await ac('oku-2-255'); await bekle(800); await pg.evaluate(() => scrollTo({ top: 0, behavior: 'instant' })); await bekle(); await pg.click('#oku-iki'); await bekle(500);
    U(await pg.evaluate(() => scrollY) < 400, 'meal değişince sayfa hedef ayete sıçradı'); await pg.click('#oku-iki'); await bekle(300);
    await ac('kok-318'); const gen = await pg.evaluate(() => [...document.querySelectorAll('.cift .bar-iz span')].map((x) => parseFloat(x.style.width))); U(gen.length > 0 && Math.max(...gen) <= 100, 'iz çubukları %100\'ü aşıyor');
    await ac('kok'); await pg.evaluate(() => scrollTo(0, 2500)); await pg.evaluate(() => { location.hash = 'nida'; }); await bekle(700); U(await pg.evaluate(() => scrollY) < 50, 'yeni ekran sayfanın ortasında açıldı');
    await ac('kok'); await pg.locator('#kok-gec .sec-w').first().click(); await bekle(800); U((await pg.evaluate(() => location.hash)).startsWith('#oku-') && await pg.locator('#panel:not(.kapali)').count() === 1, 'kök sayfasından kelimeye gidince panel açılmadı');
    await ac('isim-0'); U((await metin('main')).includes('Kök sayfasını aç'), 'Lafzatullah için kök sayfası yönlendirmesi yok');
    await ac('yontem'); U((await metin('main')).includes('6.236'), 'yöntem sayımları');
    await ac('olmayan'); U((await metin('h1')).includes('Fâtiha'), 'bilinmeyen adres');
    await pg.close();
  }
  await b.close(); srv.close();
  console.log(hata.length ? 'HATA (' + hata.length + ')\n' + hata.join('\n') : 'TEMİZ'); process.exit(hata.length ? 1 : 0);
})();
