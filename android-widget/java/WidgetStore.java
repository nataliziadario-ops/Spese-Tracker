package io.github.nataliziadario.spendy;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Build;

/**
 * Magazzino condiviso dei dati del widget.
 *
 * Il widget gira FUORI dalla pagina web e non puo' leggere i dati dell'app
 * (che stanno nel localStorage della WebView). Percio' l'app, quando salva,
 * manda qui una "fotografia" gia' formattata, che viene conservata nelle
 * SharedPreferences e letta dai widget quando si disegnano.
 */
public class WidgetStore {

    public static final String PREFS = "SpendyWidgetPrefs";

    public static SharedPreferences prefs(Context c) {
        return c.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    /** Intent che riapre l'app quando si tocca il widget. */
    public static PendingIntent openAppIntent(Context c) {
        try {
            Intent i = c.getPackageManager().getLaunchIntentForPackage(c.getPackageName());
            if (i == null) return null;
            i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
            int flags = PendingIntent.FLAG_UPDATE_CURRENT;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                flags = flags | PendingIntent.FLAG_IMMUTABLE;
            }
            return PendingIntent.getActivity(c, 0, i, flags);
        } catch (Exception e) {
            return null;
        }
    }

    /** Ridisegna tutti i widget presenti in schermata Home. */
    public static void refreshAll(Context c) {
        try {
            AppWidgetManager m = AppWidgetManager.getInstance(c);
            if (m == null) return;

            int[] simple = m.getAppWidgetIds(new ComponentName(c, SpendySimpleWidget.class));
            if (simple != null && simple.length > 0) {
                new SpendySimpleWidget().onUpdate(c, m, simple);
            }
            int[] rich = m.getAppWidgetIds(new ComponentName(c, SpendyRichWidget.class));
            if (rich != null && rich.length > 0) {
                new SpendyRichWidget().onUpdate(c, m, rich);
            }
        } catch (Exception e) {
            // Un widget che non si aggiorna non deve mai far crashare l'app.
        }
    }
}
