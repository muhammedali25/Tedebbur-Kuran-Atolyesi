// Tarayıcıdaki cümle bölme koduyla Python'daki (align_lib.py) birebir aynı sonucu verdiğini sınar.
// Kodu doğrudan okuyucunun HTML'inden alır; Python sayılarını build/py_units.json'dan okur.
const fs = require('fs');
const html = fs.readFileSync('/home/user/mektubat-okuyucu.html', 'utf8');
const start = html.indexOf('const ABBR='), end = html.indexOf('function phi(');
if (start < 0 || end < 0) { console.log('[KALDI] cümle bölme kodu HTML içinde bulunamadı'); process.exit(1); }
const DATA = {};
for (const l of ['fa', 'ar', 'ak', 'hk']) DATA[l] = JSON.parse(fs.readFileSync(`/home/user/mektubat/data/${l}.json`, 'utf8'));
const code = html.slice(start, end) + '\n;return {splitSents, units};';
const { units } = new Function('DATA', code)(DATA);
const py = JSON.parse(fs.readFileSync(__dirname + '/tests/py_units.json', 'utf8'));
let same = 0, diff = [];
for (const k of Object.keys(py)) for (const l of ['fa', 'ar', 'ak', 'hk']) {
  const U = units(k, l); const js = U ? U.flat : null; const p = py[k][l];
  if (!js && !p) { same++; continue; }
  if (js && p && js.length === p.length && js.every((s, i) => s === p[i])) same++;
  else diff.push(`${k}/${l}: JS ${js ? js.length : 0} cümle, Python ${p ? p.length : 0}` + (js && p ? ` · ilk fark #${js.findIndex((s, i) => s !== p[i])}` : ''));
}
console.log(`[${diff.length ? 'KALDI' : 'GEÇTİ'}] Tarayıcı ve Python aynı cümleleri üretiyor: ${same}/${same + diff.length}`);
diff.slice(0, 15).forEach(d => console.log('        ' + d));
