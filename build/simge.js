// Ana ekran simgesini üretir (180×180 PNG, base64 olarak yazdırır).
const { chromium } = require('playwright');
(async () => {
  const olcek = Number(process.argv[2] || 1);
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 180, height: 180 }, deviceScaleFactor: olcek });
  await pg.setContent(`<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Amiri:wght@700&display=swap">
    <body style="margin:0;width:180px;height:180px;background:#14213d;display:flex;align-items:center;justify-content:center">
    <div style="width:150px;height:150px;border:2px solid #dcb75f;border-radius:30px;display:flex;align-items:center;justify-content:center">
    <span style="font-family:Amiri,serif;font-weight:700;font-size:104px;line-height:1;color:#dcb75f;margin-top:-34px">ق</span></div></body>`);
  await pg.evaluate(() => document.fonts.ready); await pg.waitForTimeout(400);
  process.stdout.write((await pg.screenshot({ type: 'png' })).toString('base64')); await b.close();
})();
