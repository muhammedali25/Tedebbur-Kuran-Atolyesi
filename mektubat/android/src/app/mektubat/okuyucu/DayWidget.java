package app.mektubat.okuyucu;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.Context;
import android.content.Intent;
import android.widget.RemoteViews;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.util.TimeZone;

/**
 * Ana ekran bileşeni: her gün sıradaki cümle (Farsça aslı ve Akçiçek tercümesi).
 * Gün sırası okuyucudaki "Günün cümlesi" kartıyla aynı hesaplanır: yerel gün sayısı mod cümle sayısı.
 * Rastgele değildir; derlemede sırayla ilerler.
 */
public final class DayWidget extends AppWidgetProvider {

    @Override
    public void onUpdate(Context ctx, AppWidgetManager mgr, int[] ids) {
        JSONObject w = today(ctx);
        for (int id : ids) mgr.updateAppWidget(id, views(ctx, w));
    }

    private static JSONObject today(Context ctx) {
        try {
            InputStream in = ctx.getAssets().open("www/data/widget.json");
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            byte[] buf = new byte[16384];
            int n;
            while ((n = in.read(buf)) > 0) out.write(buf, 0, n);
            in.close();
            JSONArray arr = new JSONArray(out.toString("UTF-8"));
            long now = System.currentTimeMillis();
            long day = (now + TimeZone.getDefault().getOffset(now)) / 86400000L;
            return arr.getJSONObject((int) (day % arr.length()));
        } catch (Exception e) {
            return null;
        }
    }

    private static RemoteViews views(Context ctx, JSONObject w) {
        RemoteViews v = new RemoteViews(ctx.getPackageName(), R.layout.widget);
        String key = "";
        if (w != null) {
            key = w.optString("k");
            String[] p = key.split("-");
            String who = w.optString("who");
            v.setTextViewText(R.id.w_label, "GÜNÜN CÜMLESİ · " + (p.length == 2 ? p[0] + "/" + p[1] : ""));
            v.setTextViewText(R.id.w_fa, w.optString("fa"));
            v.setTextViewText(R.id.w_tr, w.optString("tr"));
            v.setTextViewText(R.id.w_who, who.isEmpty() ? "" : who + " için yazılan mektuptan");
        } else {
            v.setTextViewText(R.id.w_label, "MEKTÛBÂT");
            v.setTextViewText(R.id.w_tr, "Günün cümlesi yüklenemedi. Uygulamayı açın.");
        }
        Intent open = new Intent(ctx, MainActivity.class);
        open.setAction("app.mektubat.okuyucu.OPEN_" + key);
        open.putExtra("k", key);
        open.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent pi = PendingIntent.getActivity(ctx, 0, open, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        v.setOnClickPendingIntent(R.id.w_root, pi);
        return v;
    }
}
