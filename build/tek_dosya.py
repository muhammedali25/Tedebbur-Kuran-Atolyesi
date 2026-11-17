"""Dağıtım sürümleri: site/index.html + site/d/*.json ->

  dist/Tedebbur.html   tek dosya; sunucu gerekmez, Mac'te Safari'de dosyadan açılır
  dist/web/            bir web adresine konacak klasör; iPhone/iPad'de ana ekrana eklenir,
                       ilk açılıştan sonra internetsiz çalışır

Veri sayfanın içine JSON blokları olarak gömülür.
Kullanım: node build/simge.js 1 > build/simge.b64 && node build/simge.js 2.8445 > build/simge512.b64
          python3 build/tek_dosya.py
"""
import base64
import hashlib
import os

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(KOK, 'build')
sayfa = open(os.path.join(KOK, 'site', 'index.html'), encoding='utf8').read()
simge = open(os.path.join(BUILD, 'simge.b64')).read().strip()
simge512 = open(os.path.join(BUILD, 'simge512.b64')).read().strip()
kur = open(os.path.join(BUILD, 'kurulum.html'), encoding='utf8').read()

i = sayfa.index('<style>')
bas, govde = sayfa[:i].strip(), sayfa[i:]
j = govde.index('</style>') + len('</style>')
stil, govde = govde[:j], govde[j:]
k = govde.index('<script>')
veri = ''
for ad in ('core', 'ar', 'meal', 'meal2', 'morph', 'rel', 'ek'):
    t = open(os.path.join(KOK, 'site', 'd', ad + '.json'), encoding='utf8').read()
    t = t.replace('</', '<\\/').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    veri += '<script type="application/json" id="veri-%s">%s</script>\n' % (ad, t)

BASLIK = """<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Tedebbür">
<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#151d2e" media="(prefers-color-scheme: dark)">
<meta name="format-detection" content="telephone=no">
@SIMGE@
@BAS@
<style>
:root{color-scheme:light;padding:env(safe-area-inset-top,0px) 0 env(safe-area-inset-bottom,0px)}
html{-webkit-text-size-adjust:100%}
body{margin:0;font-size:14px;-webkit-tap-highlight-color:transparent;overscroll-behavior-y:none}
img{max-width:100%}
[hidden]{display:none!important}
</style>
"""


def uret(simge_etiketi):
    return (BASLIK.replace('@SIMGE@', simge_etiketi).replace('@BAS@', bas) + stil + '\n</head>\n<body>\n'
            + govde[:k] + veri + govde[k:] + '\n' + kur + '\n</body>\n</html>\n')


veri_simge = 'data:image/png;base64,' + simge
dist = os.path.join(KOK, 'dist')
web = os.path.join(dist, 'web')
os.makedirs(web, exist_ok=True)

open(os.path.join(dist, 'Tedebbur.html'), 'w', encoding='utf8').write(
    uret('<link rel="apple-touch-icon" href="%s">\n<link rel="icon" type="image/png" href="%s">' % (veri_simge, veri_simge)))

sayfa_web = uret('<link rel="apple-touch-icon" href="simge-180.png">\n<link rel="icon" type="image/png" href="simge-180.png">\n'
                 '<link rel="manifest" href="manifest.webmanifest">')
open(os.path.join(web, 'index.html'), 'w', encoding='utf8').write(sayfa_web)
open(os.path.join(web, 'simge-180.png'), 'wb').write(base64.b64decode(simge))
open(os.path.join(web, 'simge-512.png'), 'wb').write(base64.b64decode(simge512))
open(os.path.join(web, 'manifest.webmanifest'), 'w', encoding='utf8').write(
    '{\n  "name": "Tedebbür Kur\'an Atölyesi", "short_name": "Tedebbür", "lang": "tr", "start_url": "./", "scope": "./",\n'
    '  "display": "standalone", "background_color": "#14213d", "theme_color": "#14213d",\n'
    '  "icons": [{"src": "simge-180.png", "sizes": "180x180", "type": "image/png"},\n'
    '            {"src": "simge-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}]\n}\n')
surum = hashlib.sha256(sayfa_web.encode('utf8')).hexdigest()[:12]
sw = open(os.path.join(BUILD, 'sw.js'), encoding='utf8').read().replace('@SURUM@', surum)
open(os.path.join(web, 'sw.js'), 'w', encoding='utf8').write(sw)

for d_, _, fs in os.walk(dist):
    for f in sorted(fs):
        print(os.path.relpath(os.path.join(d_, f), KOK), round(os.path.getsize(os.path.join(d_, f)) / 1e6, 2), 'MB')
