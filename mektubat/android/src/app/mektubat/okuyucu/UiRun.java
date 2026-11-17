package app.mektubat.okuyucu;

import android.app.Activity;
import android.webkit.WebView;
import android.widget.Toast;

/** Arayüz iş parçacığında çalışacak iki küçük iş: sayfaya "okuma bitti" demek ya da kısa bir ileti göstermek. */
final class UiRun implements Runnable {
    private final WebView web;
    private final Activity activity;
    private final String msg;

    UiRun(WebView web) {
        this.web = web;
        this.activity = null;
        this.msg = null;
    }

    UiRun(Activity activity, String msg) {
        this.web = null;
        this.activity = activity;
        this.msg = msg;
    }

    @Override
    public void run() {
        if (web != null) web.evaluateJavascript("window.MK&&MK.ttsDone&&MK.ttsDone()", null);
        else Toast.makeText(activity, msg, Toast.LENGTH_LONG).show();
    }
}
