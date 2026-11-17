package io.github.muhammedali25.tedebbur;

import android.app.Activity;
import android.content.Intent;
import android.content.res.Configuration;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

/** Tek ekran: uygulamaya gömülü sayfayı (assets/index.html) bir WebView içinde gösterir. */
public class MainActivity extends Activity {
    private static final String SAYFA = "file:///android_asset/index.html";
    private WebView web;

    @Override
    protected void onCreate(Bundle kayit) {
        super.onCreate(kayit);
        web = new WebView(this);
        WebSettings a = web.getSettings();
        a.setJavaScriptEnabled(true);
        a.setDomStorageEnabled(true);          // hatırlanan tercih (ikinci meal) için
        a.setAllowFileAccess(true);
        a.setTextZoom(100);
        if (Build.VERSION.SDK_INT >= 33) a.setAlgorithmicDarkeningAllowed(false);
        else if (Build.VERSION.SDK_INT >= 29) {
            boolean gece = (getResources().getConfiguration().uiMode & Configuration.UI_MODE_NIGHT_MASK) == Configuration.UI_MODE_NIGHT_YES;
            a.setForceDark(gece ? WebSettings.FORCE_DARK_AUTO : WebSettings.FORCE_DARK_OFF);
        }
        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest istek) {
                Uri u = istek.getUrl();
                if ("file".equals(u.getScheme())) return false;
                try { startActivity(new Intent(Intent.ACTION_VIEW, u)); } catch (Exception e) { /* açacak uygulama yok */ }
                return true;
            }
        });
        setContentView(web);
        if (kayit != null) web.restoreState(kayit); else web.loadUrl(SAYFA);
    }

    @Override
    protected void onSaveInstanceState(Bundle kayit) {
        super.onSaveInstanceState(kayit);
        web.saveState(kayit);
    }

    @Override
    public void onBackPressed() {
        if (web.canGoBack()) web.goBack(); else super.onBackPressed();
    }
}
