# Mektûbât okuyucu: eşleştirme doğruluğu ve test raporu

Sürüm 1.4 · 16 Kasım 2026

## Sürüm 1.4: on beş yeni özellik

| Özellik | Test |
|---|---|
| Okuma ilerlemesi, kaldığın yer | geçti (yeniden yüklemede kalıcı) |
| Altını çizme (karşılıklarıyla), not, Notlarım, dışa aktarma | geçti |
| Senkron kaydırma | geçti (Türkçe ortaya gelince Farsça %52'de) |
| Okuma ayarları: sepya tema, satır aralığı, yazı tipi | geçti; sepya karşıtlıkları ≥ 5,0 (hesapla) |
| Arama: defter ve alıcı süzgeci, sonucu üç dilde açma | geçti |
| Mürekkep yolu, ağın büyümesi | geçti |
| Murâkabe girih arka planı; isteğe bağlı sesler (varsayılan kapalı) | girih geçti; sesler kulakla denenmedi |
| Cümle kartı (1080×1350 PNG) | üretim geçti; APK'da paylaşma telefonda denenmedi |
| Kavram birlikteliği diyagramı | geçti (fenâ'nın en yakını bekâ: 66 ortak mektup) |
| Akçiçek ↔ Hakikat karşılaştırması | geçti (iki tercümenin bütün metni satırlarda) |
| Kelime açıklamaları (136 terim, bu uygulama için yazıldı) | geçti; cümle metinlerini değiştirmiyor |
| Hatalı eşleşme bildirimi (cihazda saklanır, JSON dışa aktarılır) | geçti |
| İkinci ana ekran bileşeni: günün beyti | derleniyor ve kayıtlı; telefonda denenmedi |
| Sesli okuma | tarayıcıda: ses yoksa durup haber veriyor (test ortamında ses yok); APK'daki telefon sesi denenmedi |

Toplam: özellik testleri 17/17, arayüz 14/14, tarama 10/10 (tek dosyalık HTML üzerinde), erişilebilirlik 0 ihlal, veri 21 geçti / 3 uyarı.
Yerel test sunucusu süre sınırında durdurulduğu için bu turda testler tek dosyalık HTML ve APK içeriği üzerinde koşuldu; yayınlanan web sayfası aynı kaynaktan üretilir.

Bu turda bulunan ve düzeltilenler: ses motoru olmayan cihazda sesli okuma bütün cümleleri hata vererek geçiyordu (artık duruyor); üç alıcının Türkçe adı Arap harfli kalmıştı (1/30, 2/15, 2/53); karşılaştırmada farklı kelimeleri işaretlemek metnin neredeyse tamamını boyuyordu (artık ortak kelimeler işaretli).

## Sürüm 1.3

## 0. Sürüm 1.3'te eklenen testler ve düzeltmeler

| Test | Sonuç |
|---|---|
| Uçtan uca tarama: 536 mektubun hepsi; her dilde 5 cümlede köprü (≈10.700 tıklama); murâkabe; 198 kişi, 114 sûre, bütün atlas/tayf/seyr sayfaları; arama kenar durumları | 10/10 (web ve tek dosya) |
| Mektup açma süresi | medyan 36 ms, %95 83 ms, en uzun 249 ms |
| axe-core WCAG 2.1 AA, açık ve koyu tema, 8 görünüm | 0 ihlal (önce 5 tür) |
| Klavye: odak görünürlüğü, ağ/seyr Enter, köprü ↑↓ + Enter | geçti |
| APK: izin yok (internet dahil), v2/v3 imza, zipalign, bileşen kaydı, günün cümlesi saat dilimi | geçti |

Düzeltmeler:
- **Karşılıksız cümle kalmadı.** Akçiçek tek bir Farsça cümleyi 7-9 cümleye bölebildiği için 182 Türkçe grup karşılıksız kalıyordu; bunlar sözcük benzerliği yüksek komşu gruba katılıyor (Arapça 15, Hakikat 2). Köprü artık hiçbir tıklamada boş dönmüyor; otomatik doğruluk ölçütleri değişmedi.
- **Erişilebilirlik:** açık temada altın yazı rengi koyulaştırıldı (karşıtlık 3,2 → 5,1); sayfa dili Türkçe bildiriliyor; ağ ve seyr çizimleri "grup" rolünde; metin sütunları klavyeyle odaklanabiliyor ve ↑/↓ ile cümleler arasında gezinilip Enter ile köprü açılıyor.
- **Telefon:** ayarlar "Ayarlar" düğmesinin arkasına katlanıyor; ağ, Kur'ân ve seyr çizimlerinin yazıları ekran genişliğine göre büyüyor; kavram listeleri yatay şerit ve seçili kavram ortalanıyor; ağdaki etiketler çizim kenarından taşmıyor.
- Köprü panelinin başlığı yeni yöntemi yansıtıyor.

## 1. Cümle eşleştirmesi (hangi cümle hangisinin tercümesi)

### Ölçüt

Elle konmuş, eşleştirmeden bağımsız işaretler kullanıldı:

| Ölçüt | Ne | Çift |
|---|---|---|
| Kur'ân atıfları | Farsçada `[sûre: âyet]`, Akçiçek'te `(sûre/âyet)` aynı âyeti gösteriyorsa iki cümle birbirinin karşılığıdır | 503 |
| Beyitler | Akçiçek'in aynen aktardığı Farsça beyit, Farsça asılda tek bir cümlede geçiyorsa | 209 |
| Arapça âyet metinleri | Farsçadaki `{âyet}` alıntısının ilk 4 kelimesi Arapça tercümede tek bir cümlede geçiyorsa | 541 |

"Tam isabet": Farsça cümlenin bağlandığı grupta doğru hedef cümle var. "±1": bir cümle yakınında.

### Sonuçlar

| Yöntem | FA↔Akçiçek (Kur'ân) | FA↔Akçiçek (beyit) | FA↔Arapça |
|---|---|---|---|
| Önceki sürüm (yalnız uzunluk) | %24,0 tam · %39,6 ±1 | %17,7 tam · %36,4 ±1 | %54,5 tam · %75,7 ±1 |
| Cümle bölme düzeltmeleri sonrası, yalnız uzunluk | %35,8 · %51,7 | – | %60,1 · %81,5 |
| + öğrenilmiş sözlük, atıflar kullanılmadan (dürüst ölçüm) | **%86,3 · %96,2** | %33,0 · %78,0 | – |
| Üretim: + sözlük + atıflar + Farsça satır eşleşmesi | %98,2 · %99,0 ¹ | %94,3 · %98,1 ² | **%87,6 · %99,4** |

¹ Atıflar hem girdi hem ölçüt olduğu için bu sayı kendini doğrular; dürüst değer bir üst satırdaki %86,3'tür.
² Farsça satır eşleşmesi beyitleri doğrudan gördüğü için kısmen kendini doğrular.

### Elle denetim (âyet ve beyit içermeyen sıradan cümleler, rastgele, sabit tohum)

| Dil | Güven | Doğru | Kısmen | Yanlış | Grupların payı |
|---|---|---|---|---|---|
| Akçiçek | güçlü | 10 | 0 | 0 | %58 |
| Akçiçek | orta | 9 | 1 | 0 | %28 |
| Akçiçek | zayıf | 7 | 2 | 1 | %14 |
| Arapça | güçlü | 6 | 1 | 0 | %72 |
| Arapça | orta | 6 | 1 | 0 | %24 |
| Arapça | zayıf | 6 | 0 | 1 | %4 |
| Hakikat (düzeltme sonrası) | güçlü | 6 | 0 | 0 | %48 |
| Hakikat (düzeltme sonrası) | orta | 5 | 1 | 0 | %28 |
| Hakikat (düzeltme sonrası) | zayıf | 6 | 0 | 0 | %23 |

Örnek sayısı küçük (dil ve düzey başına 6-10); oranlar kaba bir göstergedir.

### Bulunan ve düzeltilen hatalar

1. **Türkçe âyet atıfları kopuyordu.** Akçiçek'in `(59/22)` atıflarının 827/864'ü ayrı bir "cümle" olarak bölünüyordu. Atıf artık önündeki meal cümlesine bağlı.
2. **3. defterde Farsça nokta çok seyrek.** 3/93'te 6.000 karakter 13 cümleydi. Uzun cümleler önce noktalama, sonra "و" bağlacından bölünüyor; Arapçada da aynısı.
3. **3/38'in Farsça metni hizalamaya girmiyordu.** Başlığın ikinci satırı sanılan paragraf aslında mektubun tamamıydı. Kural: yalnız 300 karakterden kısa ikinci satır başlık sayılır.
4. **Musahhih tercümeleri.** 23 mektupta "[ترجمه از مصحح]" başlığıyla gelen Farsça tercümeler (İmâm'ın metni değil) eşleştirmeden çıkarıldı ve ayrı gösteriliyor.
5. **Hakikat Kitabevi'nin "Bu mektûb, … yazılmışdır" girişi** besmeleyle eşleşiyor ve sözlüğe yanlış karşılık öğretiyordu. Giriş eşleştirmeden çıkarıldı.
6. **Grup boyutu.** Akçiçek ortalamada iki kat fazla cümle kurduğu için bir Farsça cümleye 6 Türkçe cümleye kadar bağlanabiliyor (önce 4'tü).
7. **Güven eşikleri** dile göre ayarlandı (Hakikat'in sözlüğü 313 mektuptan öğrenildiği için daha küçük).

Tarayıcıdaki ve Python'daki cümle bölme 2.144 metnin hepsinde cümle cümle aynı; eşleştirme önceden hesaplanıp sayfaya veri olarak konuyor.

## 2. Veri testleri (`test_data.py`): 22 geçti, 2 uyarı

- Mektup sayıları (313/99/124; 534; 534; 313), boş metin, HTML artığı, yinelenen metin, dizin tutarlılığı: **geçti**.
- Mektup eşlemesi âyetlerle çapraz: 144/148 mektupta Farsça ve Akçiçek atıfları uyuşuyor; bir mektup kaydırınca yalnız 2. **Geçti.**
- Farsçadaki âyet alıntılarının %91,4'ü aynı numaralı Arapça mektupta bulunuyor. **Geçti.**
- Alıcılar: Farsça başlıktan çıkarılan alıcı, Akçiçek'in notuyla 433/445'te uyuşuyor. Uyuşmayanların çoğunda Farsça başlık açık, Akçiçek'in notu farklı (1/44, 1/184, 1/301, 3/71). **Geçti.**
- Âyet numaraları: 9 atıf Sâd sûresinin 88 âyetini aşıyordu (`[ص: 148]` gibi); bunlar sayfa göndermesi, âyet değil. Çıkarıldı, kalan 788 atfın hepsi geçerli. **Düzeltildi.**
- Akçiçek'te 830 atıftan 12'si geçersiz (kaynaktaki yazım hatası, ör. 53/287). Eşleştirmede kullanılmıyor. **Uyarı.**
- Beyitler: 291 beytin 246'sı Farsça asılda aynı mektupta bulunuyor. 45'i Amritsar baskısında hiç yok; divanda "Farsça asılda bulunamadı" notuyla gösteriliyor. **Uyarı, işaretlendi.**
- Atlas: 21 kalıp birim testi geçti (ör. "ظل" kalıbı "ظلمت"i saymıyor). Farsça ve Arapça sayımlar mektup bazında r ≥ 0,80 uyumlu; yalnız "Abdiyet" 0,77. **Uyarı.**

## 3. Arayüz testleri (`test_ui.js`): 14/14 geçti

Hem web sayfasında hem tek dosyalık HTML'de: 15 rota, rastgele 40 mektup, köprünün hazır eşleştirmeyi kullanması (2.144/2.144), köprü simetrisi (60/60), murâkabe, arama sayısının doğrudan sayımla aynı olması, gezinme kutusu, Kur'ân yay ve çip sayıları, seyr ve atlas panelleri, divan araması, 380 px genişlikte yatay kayma olmaması, konsolda hata olmaması.

## 4. Bilinen sınırlar

- Eşleştirme anlamı okumaz. Elle denetimde zayıf düzeyde 10 örnekten 1'i bir cümle kaymıştı.
- Akçiçek ve Hakikat yer yer açıklama ekler; bu cümleler Farsça bir gruba eklenir.
- Elle denetim örnekleri küçük.
- Ana ekran bileşeni derleniyor, ama telefonda denenemedi (ortamda emülatör yok).
