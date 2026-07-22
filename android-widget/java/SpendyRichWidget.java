package io.github.nataliziadario.spendy;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.Context;
import android.content.SharedPreferences;
import android.view.View;
import android.widget.RemoteViews;

/**
 * WIDGET COMPLETO (4x2) — patrimonio, speso nel mese, avanzamento del budget
 * piu' "caldo" e ultimi 3 movimenti.
 *
 * Nota tecnica: le righe dei movimenti sono TRE caselle fisse, non una lista
 * scorrevole. Una lista vera in un widget richiede un servizio dedicato
 * (RemoteViewsService), molto piu' complesso e fragile: per tre righe non vale
 * il rischio.
 */
public class SpendyRichWidget extends AppWidgetProvider {

    private void row(RemoteViews v, int rowId, int nameId, int amountId, String name, String amount) {
        if (name == null || name.length() == 0) {
            v.setViewVisibility(rowId, View.GONE);
        } else {
            v.setViewVisibility(rowId, View.VISIBLE);
            v.setTextViewText(nameId, name);
            v.setTextViewText(amountId, amount == null ? "" : amount);
        }
    }

    @Override
    public void onUpdate(Context context, AppWidgetManager manager, int[] widgetIds) {
        if (widgetIds == null) return;

        for (int id : widgetIds) {
            try {
                RemoteViews v = new RemoteViews(context.getPackageName(), R.layout.widget_rich);
                SharedPreferences p = WidgetStore.prefs(context);

                boolean premium = p.getBoolean("premium", false);
                String balance = p.getString("balance", "");

                if (!premium || balance == null || balance.length() == 0) {
                    v.setTextViewText(R.id.wr_label, "Spendy");
                    v.setTextViewText(R.id.wr_balance, premium ? "—" : "Premium");
                    v.setTextViewText(R.id.wr_spent, premium
                            ? "Apri l'app per aggiornare"
                            : "Attiva Premium per il widget");
                    v.setViewVisibility(R.id.wr_budget_box, View.GONE);
                    v.setViewVisibility(R.id.wr_row1, View.GONE);
                    v.setViewVisibility(R.id.wr_row2, View.GONE);
                    v.setViewVisibility(R.id.wr_row3, View.GONE);
                } else {
                    v.setTextViewText(R.id.wr_label, p.getString("monthLabel", ""));
                    v.setTextViewText(R.id.wr_balance, balance);
                    String spent = p.getString("spent", "");
                    v.setTextViewText(R.id.wr_spent, spent.length() > 0 ? ("Speso: " + spent) : "");

                    String budgetLabel = p.getString("budgetLabel", "");
                    if (budgetLabel != null && budgetLabel.length() > 0) {
                        v.setViewVisibility(R.id.wr_budget_box, View.VISIBLE);
                        v.setTextViewText(R.id.wr_budget_label, budgetLabel);
                        int pct = p.getInt("budgetPct", 0);
                        if (pct < 0) pct = 0;
                        if (pct > 100) pct = 100;
                        v.setProgressBar(R.id.wr_budget_bar, 100, pct, false);
                    } else {
                        v.setViewVisibility(R.id.wr_budget_box, View.GONE);
                    }

                    row(v, R.id.wr_row1, R.id.wr_row1_name, R.id.wr_row1_amt,
                            p.getString("r1", ""), p.getString("r1a", ""));
                    row(v, R.id.wr_row2, R.id.wr_row2_name, R.id.wr_row2_amt,
                            p.getString("r2", ""), p.getString("r2a", ""));
                    row(v, R.id.wr_row3, R.id.wr_row3_name, R.id.wr_row3_amt,
                            p.getString("r3", ""), p.getString("r3a", ""));
                }

                PendingIntent pi = WidgetStore.openAppIntent(context);
                if (pi != null) v.setOnClickPendingIntent(R.id.wr_root, pi);

                manager.updateAppWidget(id, v);
            } catch (Exception e) {
                // Un errore su un widget non deve propagarsi.
            }
        }
    }
}
