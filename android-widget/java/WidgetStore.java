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

    /**
     * Intent che riapre l'app chiedendole di eseguire un'azione (es. aprire il
     * modulo "nuova spesa" con una categoria gia' scelta).
     * requestCode DEVE essere diverso per ogni tasto: con lo stesso codice
     * Android riuserebbe lo stesso intent e tutti i tasti farebbero la stessa cosa.
     */
    public static PendingIntent actionIntent(Context c, int requestCode, String action, String categoryId) {
        try {
            Intent i = c.getPackageManager().getLaunchIntentForPackage(c.getPackageName());
            if (i == null) return null;
            i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
            i.putExtra(SpendyQuickWidget.EXTRA_ACTION, action);
            i.putExtra(SpendyQuickWidget.EXTRA_CAT, categoryId == null ? "" : categoryId);
            // Rende l'intent unico anche per il sistema (senza questo, extra diversi
            // non bastano a distinguere due PendingIntent).
            i.setAction("io.github.nataliziadario.spendy.WIDGET_" + requestCode);
            int flags = PendingIntent.FLAG_UPDATE_CURRENT;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                flags = flags | PendingIntent.FLAG_IMMUTABLE;
            }
            return PendingIntent.getActivity(c, requestCode, i, flags);
        } catch (Exception e) {
            return null;
        }
    }

    /** Memorizza l'azione richiesta dal widget, che l'app leggera' all'apertura. */
    public static void savePendingAction(Context c, String action, String categoryId) {
        try {
            prefs(c).edit()
                    .putString("pendingAction", action == null ? "" : action)
                    .putString("pendingCat", categoryId == null ? "" : categoryId)
                    .apply();
        } catch (Exception e) {
            // ignorato di proposito
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

            int[] quick = m.getAppWidgetIds(new ComponentName(c, SpendyQuickWidget.class));
            if (quick != null && quick.length > 0) {
                new SpendyQuickWidget().onUpdate(c, m, quick);
            }
        } catch (Exception e) {
            // Un widget che non si aggiorna non deve mai far crashare l'app.
        }
    }
}
