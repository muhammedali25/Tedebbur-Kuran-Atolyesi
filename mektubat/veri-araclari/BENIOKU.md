# Veri araçları (arşiv)

`mektubat/site/data/*.json` dosyalarını üreten betikler ve sınamalar. Geliştirildikleri ortamın
mutlak yollarını (`/home/user/...`) taşırlar; yeniden çalıştırmak için yolların düzeltilmesi gerekir.
Sayfanın ve APK'nın derlenmesi bunlara bağlı değildir: `mektubat/build/derle.py` ve `apk.sh` yeter.

- `bok2json.py`, `segment.py`: Şamile `.bok` dosyalarından Farsça ve Arapça mektup metinleri.
- `trparse.py`, `derle_metin.py`: Türkçe tercüme sayfalarının ayrıştırılması ve dört metnin birleştirilmesi.
- `people.py`: alıcılar. `atlas.py`, `features.py`, `glossary.py`: kavram sayımları, Kur'ân atıfları, beyitler, tayf, kelime açıklamaları.
- `align_lib.py`, `build_align.py`, `align_eval*.py`, `align_tune.py`: cümle eşleştirmesi ve doğruluk ölçümü.
- `testler/`: veri, arayüz, tarama, özellik, erişilebilirlik ve web yayını sınamaları (Playwright).

Sonuçlar `mektubat/TEST-RAPORU.md` dosyasındadır.
