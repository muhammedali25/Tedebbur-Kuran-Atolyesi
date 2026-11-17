"""Mektûbât dağıtım sürümleri: mektubat/site + mektubat/fonts ->

  dist/assets/www/     APK'nın içine giren sayfa (yazı tipleri yerel)
  dist/Mektubat.html   tek dosya; sunucu gerekmez, bilgisayarda tarayıcıyla açılır
  dist/web/            web adresine konacak klasör; iPhone/iPad'de ana ekrana eklenir,
                       ilk açılıştan sonra internetsiz çalışır

Kullanım: python3 mektubat/build/derle.py
"""
import base64, hashlib, json, os, re, shutil

BUILD = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(BUILD)
DIST = os.path.join(KOK, "dist")
WWW = os.path.join(DIST, "assets", "www")
APK_URL = "https://github.com/muhammedali25/Tedebbur-Kuran-Atolyesi/releases/download/mektubat-apk/Mektubat.apk"

for d in (os.path.join(DIST, "assets"), os.path.join(DIST, "web")):
    if os.path.isdir(d): shutil.rmtree(d)
os.makedirs(WWW)

# ---- 1. APK içi sayfa
html = open(os.path.join(KOK, "site", "index.html"), encoding="utf-8").read()
html, n = re.subn(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/[^"]*">',
                  '<link rel="stylesheet" href="fonts/fonts.css">', html)
assert n == 1, "Google Fonts bağlantısı bulunamadı"
HEAD = """<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<style>
:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
body{margin:0;font:14px system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
img{max-width:100%}
[hidden]{display:none!important}
</style>
"""
page = HEAD + html + "\n</html>\n"
open(os.path.join(WWW, "index.html"), "w", encoding="utf-8").write(page)
shutil.copytree(os.path.join(KOK, "site", "data"), os.path.join(WWW, "data"))
shutil.copytree(os.path.join(KOK, "fonts"), os.path.join(WWW, "fonts"))

# ---- 2. tek dosya
css = open(os.path.join(WWW, "fonts", "fonts.css"), encoding="utf-8").read()
css = re.sub(r"url\(\./([^)]+\.woff2)\)",
             lambda m: "url(data:font/woff2;base64,%s)" % base64.b64encode(open(os.path.join(WWW, "fonts", m.group(1)), "rb").read()).decode(), css)
one = page.replace('<link rel="stylesheet" href="fonts/fonts.css">', "<style>\n" + css + "\n</style>")
data = {"data/" + f: json.load(open(os.path.join(WWW, "data", f), encoding="utf-8")) for f in sorted(os.listdir(os.path.join(WWW, "data")))}
blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
assert one.count("<script>\n(() => {") == 1
one = one.replace("<script>\n(() => {", "<script>window.__MK_DATA=" + blob + ";</script>\n<script>\n(() => {")
open(os.path.join(DIST, "Mektubat.html"), "w", encoding="utf-8").write(one)

# ---- 3. web klasörü
WEB = os.path.join(DIST, "web")
shutil.copytree(WWW, WEB)
for nm in ("simge-180.png", "simge-512.png"):
    shutil.copy(os.path.join(BUILD, "webicon", nm), os.path.join(WEB, nm))
WEBHEAD = """<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Mektûbât">
<meta name="theme-color" content="#f8f3e6" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#151d40" media="(prefers-color-scheme: dark)">
<meta name="format-detection" content="telephone=no">
<link rel="apple-touch-icon" href="simge-180.png">
<link rel="icon" type="image/png" href="simge-180.png">
<link rel="manifest" href="manifest.webmanifest">
<script>
// Eski tarayıcı denetimi: sayfa, Safari 16.4 (iOS 16.4) ve sonrasının tanıdığı düzenli ifadeleri kullanır.
try { new RegExp("(?<=a)b"); } catch (e) { window.__eski = true; document.addEventListener("DOMContentLoaded", function () {
  document.body.innerHTML = '<div style="max-width:520px;margin:15vh auto;padding:24px;font:17px/1.5 system-ui">Bu sayfa için daha yeni bir tarayıcı gerekiyor: iPhone ve iPad\\'de iOS 16.4 ya da sonrası, Mac\\'te Safari 16.4 ya da sonrası. Ayarlar > Genel > Yazılım Güncelleme\\'den güncelleyebilirsiniz.</div>'; }); }
</script>
"""
a = '<meta name="color-scheme" content="light dark">'
web = page.replace(a, a + "\n" + WEBHEAD, 1)
kur = open(os.path.join(BUILD, "kurulum.html"), encoding="utf-8").read()
web = web.rstrip()[:-len("</html>")] + kur + "\n</html>\n"
open(os.path.join(WEB, "index.html"), "w", encoding="utf-8").write(web)
json.dump({"name": "Mektûbât-ı Rabbânî", "short_name": "Mektûbât", "lang": "tr", "start_url": "./", "scope": "./",
           "display": "standalone", "background_color": "#22336b", "theme_color": "#22336b",
           "icons": [{"src": "simge-180.png", "sizes": "180x180", "type": "image/png"},
                     {"src": "simge-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}]},
          open(os.path.join(WEB, "manifest.webmanifest"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
files = []; h = hashlib.sha256()
for d, _, fs in sorted(os.walk(WEB)):
    for f in sorted(fs):
        rel = os.path.relpath(os.path.join(d, f), WEB).replace(os.sep, "/")
        h.update(rel.encode()); h.update(open(os.path.join(d, f), "rb").read())
        if rel != "index.html": files.append(rel)
sw = open(os.path.join(BUILD, "sw.js"), encoding="utf-8").read().replace("@SURUM@", h.hexdigest()[:12]).replace("@DOSYA@", json.dumps(["./"] + files, ensure_ascii=False))
open(os.path.join(WEB, "sw.js"), "w", encoding="utf-8").write(sw)

mb = lambda p: round(sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(p) for f in fs) / 1e6, 1) if os.path.isdir(p) else round(os.path.getsize(p) / 1e6, 1)
print("dist/assets/www", mb(WWW), "MB | dist/Mektubat.html", mb(os.path.join(DIST, "Mektubat.html")), "MB | dist/web", mb(WEB), "MB, sürüm", h.hexdigest()[:12])
