package io.github.nataliziadario.spendy;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.Context;
import android.content.SharedPreferences;
import android.view.View;
import android.widget.RemoteViews;

/**
 * WIDGET SPESA RAPIDA — tre scorciatoie per registrare una spesa al volo.
 *
 * Come funziona: un widget Android NON puo' contenere campi di testo, quindi
 * non si puo' digitare l'importo direttamente li'. Il widget apre percio' l'app
 * gia' sul modulo "nuova spesa", con la categoria gia' scelta: restano da
 * digitare solo l'importo e premere Salva.
 *
 * I primi due tasti mostrano le categorie di spesa piu' usate (le manda l'app);
 * il terzo apre il modulo senza categoria preselezionata.
 */
public class SpendyQuickWidget extends AppWidgetProvider {

    /** Chiave letta poi dall'app tramite SpendyWidgetPlugin.consumeAction(). */
    public static final String EXTRA_ACTION = "spendy_action";
    public static final String EXTRA_CAT = "spendy_cat";
    public static final String ACTION_ADD_EXPENSE = "add_expense";

    private PendingIntent buttonIntent(Context c, int requestCode, String categoryId) {
        return WidgetStore.actionIntent(c, requestCode, ACTION_ADD_EXPENSE, categoryId);
    }

    @Override
    public void onUpdate(Context context, AppWidgetManager manager, int[] widgetIds) {
        if (widgetIds == null) return;

        for (int id : widgetIds) {
            try {
                RemoteViews v = new RemoteViews(context.getPackageName(), R.layout.widget_quick);
                SharedPreferences p = WidgetStore.prefs(context);
                boolean premium = p.getBoolean("premium", false);

                if (!premium) {
                    v.setTextViewText(R.id.wq_title, "Spendy Premium");
                    v.setViewVisibility(R.id.wq_b1, View.GONE);
                    v.setViewVisibility(R.id.wq_b2, View.GONE);
                    v.setTextViewText(R.id.wq_b3_label, "Attiva");
                    v.setViewVisibility(R.id.wq_b3, View.VISIBLE);
                    // Senza Premium il tasto apre semplicemente l'app.
                    PendingIntent open = WidgetStore.openAppIntent(context);
                    if (open != null) {
                        v.setOnClickPendingIntent(R.id.wq_b3, open);
                        v.setOnClickPendingIntent(R.id.wq_root, open);
                    }
                    manager.updateAppWidget(id, v);
                    continue;
                }

                String n1 = p.getString("q1n", "");
                String i1 = p.getString("q1i", "");
                String n2 = p.getString("q2n", "");
                String i2 = p.getString("q2i", "");

                if (n1 != null && n1.length() > 0) {
                    v.setViewVisibility(R.id.wq_b1, View.VISIBLE);
                    v.setTextViewText(R.id.wq_b1_label, n1);
                    v.setOnClickPendingIntent(R.id.wq_b1, buttonIntent(context, 101, i1));
                } else {
                    v.setViewVisibility(R.id.wq_b1, View.GONE);
                }

                if (n2 != null && n2.length() > 0) {
                    v.setViewVisibility(R.id.wq_b2, View.VISIBLE);
                    v.setTextViewText(R.id.wq_b2_label, n2);
                    v.setOnClickPendingIntent(R.id.wq_b2, buttonIntent(context, 102, i2));
                } else {
                    v.setViewVisibility(R.id.wq_b2, View.GONE);
                }

                v.setViewVisibility(R.id.wq_b3, View.VISIBLE);
                v.setOnClickPendingIntent(R.id.wq_b3, buttonIntent(context, 103, ""));

                manager.updateAppWidget(id, v);
            } catch (Exception e) {
                // Un widget che non si aggiorna non deve far crashare nulla.
            }
        }
    }
}
