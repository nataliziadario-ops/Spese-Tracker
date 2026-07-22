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
}
