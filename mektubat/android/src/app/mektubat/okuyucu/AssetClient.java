package app.mektubat.okuyucu;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.net.Uri;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;

/**
 * Sayfayı ve verileri assets/www altından, Android'in bu iş için ayırdığı
 * https://appassets.androidplatform.net adresiyle sunar; böylece fetch() çalışır ve
 * uygulama internetsiz açılır. Başka adreslere giden bağlantılar telefonun tarayıcısında açılır.
 */
public final class AssetClient extends WebViewClient {
    public static final String HOST = "appassets.androidplatform.net";
    private final Activity activity;

    public AssetClient(Activity activity) {
        this.activity = activity;
    }

    @Override
    public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest req) {
        Uri u = req.getUrl();
        if (!HOST.equals(u.getHost())) return null;
        String path = u.getPath();
        if (path == null || path.isEmpty() || path.equals("/")) path = "/index.html";
        try {
            InputStream in = activity.getAssets().open("www" + path);
            String mime = mimeOf(path);
            String enc = mime.startsWith("font/") ? null : "utf-8";
            WebResourceResponse r = new WebResourceResponse(mime, enc, in);
            Map<String, String> h = new HashMap<String, String>();
            h.put("Cache-Control", "no-cache");
            r.setResponseHeaders(h);
            return r;
        } catch (IOException e) {
            return new WebResourceResponse("text/plain", "utf-8", 404, "Not Found", null, null);
        }
    }

    @Override
    public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest req) {
        Uri u = req.getUrl();
        if (HOST.equals(u.getHost())) return false;
        try {
            activity.startActivity(new Intent(Intent.ACTION_VIEW, u));
        } catch (ActivityNotFoundException ignored) {
            // Bağlantıyı açacak uygulama yoksa bir şey yapma
        }
        return true;
    }

    static String mimeOf(String p) {
        if (p.endsWith(".html")) return "text/html";
        if (p.endsWith(".json")) return "application/json";
        if (p.endsWith(".css")) return "text/css";
        if (p.endsWith(".js")) return "text/javascript";
        if (p.endsWith(".woff2")) return "font/woff2";
        if (p.endsWith(".png")) return "image/png";
        return "application/octet-stream";
    }
}
