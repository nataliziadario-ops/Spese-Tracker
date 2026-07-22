package io.github.nataliziadario.spendy;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.Context;
import android.content.SharedPreferences;
import android.widget.RemoteViews;

/**
 * WIDGET SEMPLICE (2x1) — patrimonio totale + speso nel mese.
 * Volutamente minimale: meno elementi = meno cose che possono rompersi.
 */
public class SpendySimpleWidget extends AppWidgetProvider {

    @Override
    public void onUpdate(Context context, AppWidgetManager manager, int[] widgetIds) {
        if (widgetIds == null) return;

        for (int id : widgetIds) {
            try {
                RemoteViews v = new RemoteViews(context.getPackageName(), R.layout.widget_simple);
                SharedPreferences p = WidgetStore.prefs(context);

                boolean premium = p.getBoolean("premium", false);
                String balance = p.getString("balance", "");

                if (!premium) {
                    v.setTextViewText(R.id.ws_label, "Spendy");
                    v.setTextViewText(R.id.ws_balance, "Premium");
                    v.setTextViewText(R.id.ws_spent, "Attiva Premium per il widget");
                } else if (balance == null || balance.length() == 0) {
                    v.setTextViewText(R.id.ws_label, "Spendy");
                    v.setTextViewText(R.id.ws_balance, "—");
                    v.setTextViewText(R.id.ws_spent, "Apri l'app per aggiornare");
                } else {
                    v.setTextViewText(R.id.ws_label, p.getString("monthLabel", ""));
                    v.setTextViewText(R.id.ws_balance, balance);
                    String spent = p.getString("spent", "");
                    v.setTextViewText(R.id.ws_spent, spent.length() > 0 ? ("Speso: " + spent) : "");
                }

                PendingIntent pi = WidgetStore.openAppIntent(context);
                if (pi != null) v.setOnClickPendingIntent(R.id.ws_root, pi);

                manager.updateAppWidget(id, v);
            } catch (Exception e) {
                // Non blocchiamo gli altri widget se uno fallisce.
            }
        }
    }
}
