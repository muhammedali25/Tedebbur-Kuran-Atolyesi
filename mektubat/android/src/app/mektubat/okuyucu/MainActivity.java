package app.mektubat.okuyucu;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.Window;
import android.webkit.WebSettings;
import android.webkit.WebView;

/** Okuyucuyu paket içinden açan tek ekranlı uygulama. */
public class MainActivity extends Activity {
    private static final String BASE = "https://" + AssetClient.HOST + "/index.html";
    private WebView web;
    private NativeBridge bridge;

    @Override
    protected void onCreate(Bundle saved) {
        super.onCreate(saved);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        web = new WebView(this);
        setContentView(web);

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(false);
        s.setTextZoom(100);
        s.setMediaPlaybackRequiresUserGesture(true);
        web.setWebViewClient(new AssetClient(this));
        bridge = new NativeBridge(this, web);
        web.addJavascriptInterface(bridge, "MKNative");

        String k = letterFrom(getIntent());
        if (k != null) web.loadUrl(BASE + "#m-" + k);
        else if (saved != null) web.restoreState(saved);
        else web.loadUrl(BASE);
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        String k = letterFrom(intent);
        if (k != null && web != null) web.loadUrl(BASE + "#m-" + k);
    }

    /** Ana ekran bileşeninden gelen mektup anahtarı ("1-45" biçiminde), yoksa null. */
    private static String letterFrom(Intent i) {
        if (i == null) return null;
        String k = i.getStringExtra("k");
        return (k != null && k.matches("\\d-\\d{1,3}")) ? k : null;
    }

    @Override
    public void onBackPressed() {
        // Görünümler adres sonundaki #… ile tutulur; geri tuşu önceki görünüme döner
        if (web != null && web.canGoBack()) web.goBack();
        else super.onBackPressed();
    }

    @Override
    protected void onSaveInstanceState(Bundle out) {
        super.onSaveInstanceState(out);
        if (web != null) web.saveState(out);
    }

    @Override
    protected void onPause() {
        super.onPause();
        if (bridge != null) bridge.stopSpeak();
    }

    @Override
    protected void onDestroy() {
        if (bridge != null) bridge.shutdown();
        super.onDestroy();
    }
}
