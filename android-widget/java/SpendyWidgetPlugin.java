package io.github.nataliziadario.spendy;

import android.content.SharedPreferences;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

/**
 * Ponte fra la web app e i widget.
 *
 * Dalla pagina si chiama:
 *   window.Capacitor.Plugins.SpendyWidget.update({ ...dati... })
 * (in pratica passa da www/native-bridge.js -> NativeBridge.updateWidget)
 *
 * Qui NON si fanno calcoli: i valori arrivano gia' formattati dall'app,
 * cosi' la logica resta tutta in un posto solo (www/index.html).
 */
@CapacitorPlugin(name = "SpendyWidget")
public class SpendyWidgetPlugin extends Plugin {

    private String s(PluginCall call, String key) {
        String v = call.getString(key, "");
        return v == null ? "" : v;
    }

    @PluginMethod
    public void update(PluginCall call) {
        try {
            SharedPreferences.Editor e = WidgetStore.prefs(getContext()).edit();

            Boolean premium = call.getBoolean("premium", Boolean.FALSE);
            Integer pct = call.getInt("budgetPct", 0);

            e.putBoolean("premium", premium != null && premium);
            e.putString("balance", s(call, "balance"));
            e.putString("spent", s(call, "spent"));
            e.putString("monthLabel", s(call, "monthLabel"));
            e.putString("budgetLabel", s(call, "budgetLabel"));
            e.putInt("budgetPct", pct == null ? 0 : pct);
            e.putString("r1", s(call, "r1"));
            e.putString("r1a", s(call, "r1a"));
            e.putString("r2", s(call, "r2"));
            e.putString("r2a", s(call, "r2a"));
            e.putString("r3", s(call, "r3"));
            e.putString("r3a", s(call, "r3a"));
            // Categorie mostrate dal widget "spesa rapida"
            e.putString("q1n", s(call, "q1n"));
            e.putString("q1i", s(call, "q1i"));
            e.putString("q2n", s(call, "q2n"));
            e.putString("q2i", s(call, "q2i"));
            e.putLong("updatedAt", System.currentTimeMillis());
            e.apply();

            WidgetStore.refreshAll(getContext());

            JSObject ret = new JSObject();
            ret.put("ok", true);
            call.resolve(ret);
        } catch (Exception ex) {
            call.reject("Aggiornamento widget non riuscito: " + ex.getMessage());
        }
    }

    /**
     * Restituisce (una sola volta) l'azione richiesta toccando un tasto del
     * widget "spesa rapida", e poi la cancella. L'app la chiama all'avvio e
     * ogni volta che torna in primo piano.
     *
     * Risposta: { action: "add_expense" | "", cat: "<id categoria>" | "" }
     */
    @PluginMethod
    public void consumeAction(PluginCall call) {
        JSObject ret = new JSObject();
        try {
            SharedPreferences p = WidgetStore.prefs(getContext());
            String action = p.getString("pendingAction", "");
            String cat = p.getString("pendingCat", "");
            if (action != null && action.length() > 0) {
                p.edit().remove("pendingAction").remove("pendingCat").apply();
            }
            ret.put("action", action == null ? "" : action);
            ret.put("cat", cat == null ? "" : cat);
        } catch (Exception ex) {
            ret.put("action", "");
            ret.put("cat", "");
        }
        call.resolve(ret);
    }
}
