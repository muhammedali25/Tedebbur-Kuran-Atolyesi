package app.mektubat.okuyucu;

import android.app.Activity;
import android.content.ContentValues;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.provider.MediaStore;
import android.speech.tts.TextToSpeech;
import android.speech.tts.UtteranceProgressListener;
import android.util.Base64;
import android.webkit.JavascriptInterface;
import android.webkit.WebView;
import android.widget.Toast;

import java.io.OutputStream;
import java.util.Locale;

/**
 * Sayfanın telefon özelliklerine erişimi: paylaşma ve sesli okuma.
 * WebView'de tarayıcıların speechSynthesis ve dosya indirme özellikleri bulunmadığı için gerekir.
 * Yalnız paket içindeki sayfa bu arayüzü görür; dış bağlantılar WebView'de açılmaz.
 */
public final class NativeBridge implements TextToSpeech.OnInitListener {
    private final Activity activity;
    private final WebView web;
    private TextToSpeech tts;
    private boolean ttsReady;
    private String pending;

    public NativeBridge(Activity activity, WebView web) {
        this.activity = activity;
        this.web = web;
    }

    @JavascriptInterface
    public void shareText(String text, String title) {
        Intent i = new Intent(Intent.ACTION_SEND);
        i.setType("text/plain");
        i.putExtra(Intent.EXTRA_TEXT, text);
        i.putExtra(Intent.EXTRA_SUBJECT, title);
        activity.startActivity(Intent.createChooser(i, "Paylaş"));
    }

    /** PNG görseli Resimler/Mektubat klasörüne kaydeder ve paylaşma menüsünü açar (Android 10 ve üstü). */
    @JavascriptInterface
    public void shareImage(String base64Png, String name) {
        if (Build.VERSION.SDK_INT < 29) {
            toast("Görsel kaydetme Android 10 ve üstünde çalışır");
            return;
        }
        try {
            byte[] data = Base64.decode(base64Png, Base64.DEFAULT);
            ContentValues v = new ContentValues();
            v.put(MediaStore.Images.Media.DISPLAY_NAME, name);
            v.put(MediaStore.Images.Media.MIME_TYPE, "image/png");
            v.put(MediaStore.Images.Media.RELATIVE_PATH, "Pictures/Mektubat");
            Uri uri = activity.getContentResolver().insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, v);
            if (uri == null) throw new IllegalStateException("kayıt açılamadı");
            OutputStream out = activity.getContentResolver().openOutputStream(uri);
            out.write(data);
            out.close();
            Intent i = new Intent(Intent.ACTION_SEND);
            i.setType("image/png");
            i.putExtra(Intent.EXTRA_STREAM, uri);
            i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
            activity.startActivity(Intent.createChooser(i, "Kartı paylaş"));
        } catch (Exception e) {
            toast("Görsel kaydedilemedi");
        }
    }

    @JavascriptInterface
    public void speak(String text) {
        if (tts == null) {
            pending = text;
            tts = new TextToSpeech(activity.getApplicationContext(), this);
            return;
        }
        if (!ttsReady) {
            pending = text;
            return;
        }
        tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, "mk");
    }

    @JavascriptInterface
    public void stopSpeak() {
        pending = null;
        if (tts != null) tts.stop();
    }

    @Override
    public void onInit(int status) {
        if (status != TextToSpeech.SUCCESS) {
            toast("Sesli okuma başlatılamadı");
            done();
            return;
        }
        int r = tts.setLanguage(new Locale("tr", "TR"));
        if (r == TextToSpeech.LANG_MISSING_DATA || r == TextToSpeech.LANG_NOT_SUPPORTED) {
            toast("Telefonda Türkçe ses yüklü değil (Ayarlar > Metin okuma)");
            done();
            return;
        }
        tts.setOnUtteranceProgressListener(new TtsListener(this));
        ttsReady = true;
        if (pending != null) {
            String t = pending;
            pending = null;
            tts.speak(t, TextToSpeech.QUEUE_FLUSH, null, "mk");
        }
    }

    public void shutdown() {
        if (tts != null) {
            tts.stop();
            tts.shutdown();
            tts = null;
        }
    }

    void done() {
        web.post(new UiRun(web));
    }

    private void toast(String msg) {
        activity.runOnUiThread(new UiRun(activity, msg));
    }
}
