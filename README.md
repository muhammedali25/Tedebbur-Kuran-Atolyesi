# Tedebbür — Kur'an-ı Kerim Analiz Atölyesi

Kur'an-ı Kerim'i kök, sure ve ayet düzeyinde **ölçen** bir inceleme aracı. Tarayıcıda
çalışır, sunucusu yoktur. Tefsir yapmaz, hüküm çıkarmaz; sayar ve oranlar. Her sayının
nasıl üretildiği uygulamanın "Yöntem" sayfasında yazılıdır.

**Aç:** https://muhammedali25.github.io/Tedebbur-Kuran-Atolyesi/

iPhone ve iPad'de Safari ile açın; sayfa ana ekrana nasıl ekleneceğini kendisi gösterir.
Eklendikten sonra uygulama gibi açılır ve internetsiz çalışır.

## İçinde ne var

- **Oku:** Arapça metin, Hasan Basri Çantay ve Elmalılı Hamdi Yazır mealleri; her kelimenin
  kökü ve Türkçe gramer çözümlemesi; kök ortaklığına göre "akraba ayetler".
- **Kök / Kavram:** 1.651 kökün dağılımı, türevleri, yoldaş kökleri, meallerdeki izi;
  birden çok kökün birlikte seyri.
- **Sure / Harita:** surenin parmak izi, fiil ve hitap profili, fâsıla şeridi, ayet ritmi,
  komşu sureler; Mekkî–Medenî kök kayması.
- **Efendimiz:** "De ki" atlası, tekil hitapla gelen emirler, "Rabbüke", doğrudan sesleniş,
  "Allah ve Resulü", peygamberler aynası.
- **Keşif:** esmâ çiftleri, nidâ, sorular, dualar, kelimelerin doğum tarihi, özel isimler,
  tekrarlanan ifadeler, sayım denetçisi.

## Derleme

```bash
python3 build/build_data.py          # kaynak/ -> site/d/*.json  (numpy gerekir)
node build/simge.js 1 > build/simge.b64 && node build/simge.js 2.8445 > build/simge512.b64
python3 build/tek_dosya.py           # dist/Tedebbur.html ve dist/web/
node build/test/smoke.js && node build/test/etkilesim.js && node build/test/tek.js && node build/test/web.js
```

Yayın, `dist/web/` içeriğinin `gh-pages` dalına konmasıyla yapılır. Sınamalar Playwright ister.
Tasarım kararları ve kapsam `PROMPT.md` dosyasındadır.

## Kaynaklar ve haklar

| Katman | Kaynak |
|---|---|
| Arapça metin ve kelime çözümlemesi | Quranic Arabic Corpus morfolojisi v0.4 (Kais Dukes, corpus.quran.com), mustafa0x/quran-morphology çatalı. GNU GPL; kaynağa atıf ve bağlantı şartıyla dağıtılır. |
| Meal | Hasan Basri Çantay, *Kur'ân-ı Hakîm ve Meâl-i Kerîm*; sayısal metin qurandatabase.org kaynaklı, fawazahmed0/quran-api derlemesinden. |
| Karşılaştırma meali | Elmalılı Muhammed Hamdi Yazır; tanzil.net'in dağıttığı sayısal metin, aynı derlemeden. |
| Sure üst verisi | quran-meta (Tanzil üst verisi), MIT. |

Meallerin hakları mütercimlerine ve hak sahiplerine aittir; Çantay mealinin telif süresi
dolmamış olabilir. Bu depo ticari amaç taşımaz. Hak sahibi talep ederse ilgili metin kaldırılır.
Kaynak dosyalar üzerinde yapılan düzeltmeler uygulamanın "Yöntem" sayfasında listelenir.
