#!/usr/bin/env bash
# Mektûbât APK derlemesi (Gradle'sız, doğrudan Android SDK araçlarıyla). Çıktı: mektubat/dist/Mektubat.apk
# Gerekenler: ANDROID_HOME (build-tools ve bir platform kurulu), JDK, python3, zip.
# İmza: ANAHTAR_DEPOSU (.jks yolu) ve ANAHTAR_PAROLA verilirse onunla; verilmezse geçici bir anahtar üretilir.
# Geçici anahtarla derlenen sürüm, öncekinin üstüne kurulamaz (önce eskisi kaldırılır).
set -euo pipefail
cd "$(dirname "$0")/.."
SDK=${ANDROID_HOME:?ANDROID_HOME tanımlı değil}
BT=$(ls -d "$SDK"/build-tools/* | sort -V | tail -1)
JAR=$(ls -d "$SDK"/platforms/android-* | sort -V | tail -1)/android.jar
SURUM_KODU=${SURUM_KODU:-1}
SURUM_ADI=${SURUM_ADI:-1.0}

python3 build/derle.py
W=dist/apk-is
mkdir -p "$W"
find "$W" -mindepth 1 -delete
mkdir -p "$W/gen" "$W/classes" "$W/dex"

"$BT/aapt2" compile --dir android/res -o "$W/res.zip"
"$BT/aapt2" link -o "$W/base.apk" -I "$JAR" --manifest android/AndroidManifest.xml -A dist/assets \
  --java "$W/gen" --min-sdk-version 24 --target-sdk-version 34 \
  --version-code "$SURUM_KODU" --version-name "$SURUM_ADI" -0 woff2 "$W/res.zip"
javac -nowarn -Xlint:-options -source 8 -target 8 -encoding UTF-8 -cp "$JAR" -d "$W/classes" \
  $(find android/src "$W/gen" -name '*.java')
"$BT/d8" --min-api 24 --lib "$JAR" --output "$W/dex" $(find "$W/classes" -name '*.class')
(cd "$W/dex" && zip -q -u ../base.apk classes.dex)
"$BT/zipalign" -f -p 4 "$W/base.apk" "$W/aligned.apk"

KS=${ANAHTAR_DEPOSU:-}
PW=${ANAHTAR_PAROLA:-mektubat}
if [ -z "$KS" ]; then
  KS=$W/gecici.jks
  keytool -genkeypair -keystore "$KS" -storepass "$PW" -keypass "$PW" -alias mektubat \
    -keyalg RSA -keysize 2048 -validity 10000 -dname "CN=Mektubat Okuyucu" >/dev/null 2>&1
  echo "UYARI: geçici imza anahtarı kullanıldı"
fi
"$BT/apksigner" sign --ks "$KS" --ks-pass "pass:$PW" --key-pass "pass:$PW" --ks-key-alias mektubat \
  --out dist/Mektubat.apk "$W/aligned.apk"
"$BT/apksigner" verify --print-certs dist/Mektubat.apk | grep -E "SHA-256" | head -1
ls -l dist/Mektubat.apk
