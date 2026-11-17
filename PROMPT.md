# Tedebbür — Kur'an-ı Kerim Analiz Atölyesi · Yapım İstemi

> Bu belge uygulamanın şartnamesidir. Önce bu yazıldı, uygulama buna göre yapıldı.

## 1. Amaç

Kur'an-ı Kerim'i **okumayı değil, incelemeyi** kolaylaştıran, tarayıcıda çalışan,
sunucusuz bir analiz atölyesi yap. Mevcut uygulamalar ya mushaf okuyucusudur ya da
kelime-kelime sözlüktür. Bu çalışma üçüncü bir şey yapar: **metnin bütününü ölçer** ve
her ölçümü ayete, köke ve Türkçe meale bağlar. Okuyucu bir kelimeye dokunduğunda
"bu kök başka nerede geçiyor, hangi köklerle birlikte yürüyor, hangi sureye rengini
veriyor, mealde nasıl karşılanmış, bu ayetin akrabaları hangileri" sorularının
cevabını tek yerde görür.

## 2. Değişmez kurallar

1. **Kaynağı olmayan sayı yazılmaz.** Her sayı ya kaynak veriden sayılmıştır ya da
   formülü "Yöntem" sayfasında yazılı bir hesabın sonucudur. Hesaplanamayan şey
   gösterilmez.
2. **Yorum yok, ölçüm var.** Uygulama tefsir yapmaz, hüküm çıkarmaz. İstatistiksel
   yakınlık "anlam aynı" demek değildir; her ekranda bu ayrım açıkça yazılır.
3. **Sayı mistisizmi yok.** Ebced, 19 sistemi, "mucize sayım" türü iddialar kapsam
   dışıdır. Yalnız tekrar üretilebilir dilbilim ve istatistik.
4. **Metne dokunulmaz.** Arapça metin ve meal kaynaktan geldiği gibi gösterilir.
   Yapılan her düzeltme (ör. kaynak dosyadaki ayet kayması) kanıtıyla listelenir.
5. **Meal: Hasan Basri Çantay.** Mealin kendi yapısı korunur: birlikte çevrilmiş
   ayetler birlikte gösterilir, parantez içi açıklamalar meale aittir.

## 3. Veri

| Katman | Kaynak | Not |
|---|---|---|
| Arapça metin + kelime çözümlemesi | Quranic Arabic Corpus morfolojisi v0.4 (mustafa0x çatalı) | 77.429 kelime, 130.030 parça; kök, lemma, kelime türü, çekim |
| Türkçe meal | Hasan Basri Çantay (qurandatabase.org → fawazahmed0/quran-api) | 6.236 ayet kaydı |
| Sure üst verisi | quran-meta (Tanzil üst verisi) | ayet sayısı, Mekkî/Medenî, geleneksel nüzul sırası |

Derleme tek betikle (`build/build_data.py`) yapılır, girdiler denetlenir (114 sure,
6.236 ayet, nüzul sırası bir permütasyon), çıktı statik JSON'dur.

## 4. Analizler (hepsi derleme anında hesaplanır)

- **Kök dizini:** her kökün geçtiği her kelime; sure sure dağılım; mushaf ve nüzul
  sırasına göre iki ayrı şerit.
- **Sure parmak izi:** bir sureyi Kur'an'ın geri kalanından ayıran kökler
  (log-olabilirlik G², yalnız beklenenden sık olanlar).
- **Kök yoldaşlığı:** aynı ayette tesadüften sık birlikte geçen kök çiftleri (G²).
- **Ayet akrabalığı:** her ayet için kök ortaklığına göre en yakın ayetler
  (IDF ağırlıklı kosinüs). "Kur'an'ı Kur'an'la okuma"nın hesaplanmış hâli.
- **Kök → meal karşılığı:** bir kökün geçtiği ayetlerin mealinde tesadüften sık
  görülen Türkçe kelime gövdeleri. Çeviri sözlüğü değil, mealin o kökü nasıl
  karşıladığının istatistik izi.
- **Sure haritası:** 114 sure, eksenleri seçilebilen ölçülmüş büyüklükler üzerinde
  (nüzul/mushaf sırası × ayet uzunluğu, emir payı, hitap payı…). Her surenin kök
  dağılımına göre en yakın komşuları (TF-IDF, kosinüs) çizgiyle bağlanır.
  *Not: ilk tasarımdaki iki boyutlu MDS yerleşimi denendi; ilk iki eksen yapının
  yalnız %10,7'sini taşıdığı için yanıltıcı bulundu ve çıkarıldı.*
- **Hitap ve fiil profili:** surede fiillerin zamanı (mâzî/muzâri/emir), şahsı
  (1./2./3.), meçhul oranı.
- **Fâsıla şeridi:** her ayetin son harfi, sure boyunca renkli bir şerit; ses
  örgüsünün nerede değiştiği gözle görülür.
- **Ayet ritmi:** ayet başına kelime sayısı.
- **Tek geçen kökler (hapax):** Kur'an'da yalnız bir kez geçen kökler ve yerleri.

## 5. Ekranlar

1. **Oku** — sure seçici; ayet ayet Arapça + Çantay meali. Her kelime tıklanır:
   kök, lemma, Türkçe gramer çözümlemesi, kökün toplam geçişi. Her ayetin altında
   "akraba ayetler".
2. **Kök** — kök arama (Arapça, Latin harfli ya da Türkçe karşılıktan); dağılım
   şeridi (mushaf/nüzul), türevler, yoldaş kökler, meal karşılıkları, tüm geçişler.
3. **Sure** — parmak izi, fiil/hitap profili, fâsıla şeridi, ayet ritmi, komşu sureler.
4. **Harita** — sure haritası; eksenler seçilir, Mekkî/Medenî renkle ayrılır.
5. **Ara** — mealde ve Arapça metinde arama (şapka ve hareke duyarsız).
6. **Yöntem** — kaynaklar, formüller, yapılan düzeltmeler, bilinen sınırlar.

## 6. Tasarım

- Yazma eser geleneğinden iki renk: lacivert mürekkep ve tezhip altını; zemin
  nötr kâğıt. Arapça için Kur'an hattına uygun bir yüz, Türkçe için okunaklı bir
  serif + arayüz için sade bir sans.
- Telefon genişliğinde tam çalışır; açık ve koyu tema.
- Grafiklerde renk tek başına bilgi taşımaz; her işaretin üzerine gelince değeri okunur.

## 7. Kabul ölçütleri

- 114 sure, 6.236 ayet, 77.429 kelime eksiksiz yüklenir.
- Herhangi bir kelimeden köküne, kökten tüm geçişlerine, geçişten ayete iki
  dokunuşta gidilir.
- "Yöntem" sayfası, ekrandaki her sayının nasıl üretildiğini söyler.

## 8. İkinci tur (ilk sürümden sonra birlikte kararlaştırılanlar)

- **Kavram haritası:** en çok dört kök birlikte seçilir; sure sure seyirleri aynı
  ölçekte alt alta çizilir, buluştukları ayetler ve çiftlerin beklenen/gerçek
  birliktelik sayıları verilir.
- **Meal karşılaştırma:** Elmalılı Hamdi Yazır ikinci meal olarak eklenir; okuma
  ekranında yan yana açılır, kökün iki mealdeki izi ayrı ayrı hesaplanır.
- **Mekkî–Medenî kök kayması:** iki dönemde oranı en çok ayrışan kökler (G²).
- **Özel isimler:** özel isim işaretli 106 lemma; dağılım, birlikte anıldığı kökler,
  geçtiği ayetler.
- **Tekrarlanan ifadeler:** ayet içinde kalan, harekesiyle birebir aynı kelime dizileri.
- Mektubat köprüsü kapsam dışı bırakıldı.

## 9. Üçüncü tur

- **Efendimiz sekmesi:** De ki ("kul") atlası; tekil hitapla gelen emir ve yasaklar;
  "Rabbüke" haritası; doğrudan sesleniş (Ey Nebi, Ey Resul…); "Allah ve Resulü"
  birlikteliği; peygamberler aynası (hangi peygamber hangi dönemde anılmış).
  Tekil hitabın muhatabı veriyle ayrılamaz: bu her ekranda yazılır, "söz aktarımı"
  süzgeci yalnız yardımcıdır.
- **Keşif sekmesi:** Esmâ (ayet sonu) çiftleri, nidâ haritası, sorular, dualar,
  kelimelerin doğum tarihi, özel isimler, kalıplar, sayım denetçisi.
- **Sayım denetçisi hüküm vermez:** yaygın iddiadaki sayıyı, kökün bütün türev ve
  çekimlerinin açık sayımıyla yan yana koyar.
