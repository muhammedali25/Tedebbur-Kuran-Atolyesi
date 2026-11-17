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
import java.util.ArrayList;
import java.util.List;
import java.util.TimeZone;

/**
 * Ana ekran bileşeni: günün beyti. Yalnız Farsça asılda da bulunan beyitler gösterilir;
 * sırayla ilerler (rastgele değil). Bileşenlerde özel yazı tipi kullanılamadığı için beyit
 * telefonun kendi Arap harfli yazı tipiyle çizilir.
 */
public final class VerseWidget extends AppWidgetProvider {

    @Override
    public void onUpdate(Context ctx, AppWidgetManager mgr, int[] ids) {
        JSONObject v = today(ctx);
        for (int id : ids) mgr.updateAppWidget(id, views(ctx, v));
    }

    private static JSONObject today(Context ctx) {
        try {
            InputStream in = ctx.getAssets().open("www/data/verses.json");
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            byte[] buf = new byte[16384];
            int n;
            while ((n = in.read(buf)) > 0) out.write(buf, 0, n);
            in.close();
            JSONArray arr = new JSONArray(out.toString("UTF-8"));
            List<JSONObject> ok = new ArrayList<JSONObject>();
            for (int i = 0; i < arr.length(); i++) {
                JSONObject o = arr.getJSONObject(i);
                if (o.optBoolean("asil", false)) ok.add(o);
            }
            if (ok.isEmpty()) return null;
            long now = System.currentTimeMillis();
            long day = (now + TimeZone.getDefault().getOffset(now)) / 86400000L;
            return ok.get((int) (day % ok.size()));
        } catch (Exception e) {
            return null;
        }
    }

    private static RemoteViews views(Context ctx, JSONObject v) {
        RemoteViews rv = new RemoteViews(ctx.getPackageName(), R.layout.widget_verse);
        String key = "";
        if (v != null) {
            key = v.optString("k");
            String[] p = key.split("-");
            rv.setTextViewText(R.id.v_label, "GÜNÜN BEYTİ · " + (p.length == 2 ? p[0] + "/" + p[1] : ""));
            rv.setTextViewText(R.id.v_fa, v.optString("fa"));
            rv.setTextViewText(R.id.v_meal, v.optString("meal"));
        } else {
            rv.setTextViewText(R.id.v_label, "MEKTÛBÂT");
            rv.setTextViewText(R.id.v_meal, "Günün beyti yüklenemedi. Uygulamayı açın.");
        }
        Intent open = new Intent(ctx, MainActivity.class);
        open.setAction("app.mektubat.okuyucu.VERSE_" + key);
        open.putExtra("k", key);
        open.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent pi = PendingIntent.getActivity(ctx, 1, open, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        rv.setOnClickPendingIntent(R.id.v_root, pi);
        return rv;
    }
}
