package io.github.nataliziadario.spendy;

import android.content.Intent;
import android.os.Bundle;

import com.getcapacitor.BridgeActivity;

/**
 * Sostituisce la MainActivity generata da Capacitor.
 *
 * Fa due cose in piu' di quella standard:
 *  1. registra il plugin SpendyWidget (PRIMA di super.onCreate, come richiesto);
 *  2. se l'app e' stata aperta da un tasto del widget "spesa rapida", mette da
 *     parte l'azione richiesta, che la pagina web legge poi con consumeAction().
 */
public class MainActivity extends BridgeActivity {

    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(SpendyWidgetPlugin.class);
        super.onCreate(savedInstanceState);
        stashWidgetAction(getIntent());
    }

    /** Chiamata quando l'app era gia' aperta e si tocca un tasto del widget. */
    @Override
    public void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        stashWidgetAction(intent);
    }

    private void stashWidgetAction(Intent intent) {
        try {
            if (intent == null) return;
            String action = intent.getStringExtra(SpendyQuickWidget.EXTRA_ACTION);
            if (action == null || action.length() == 0) return;
            String cat = intent.getStringExtra(SpendyQuickWidget.EXTRA_CAT);
            WidgetStore.savePendingAction(this, action, cat);
            // Consumato: evita che riaprendo l'app si ripeta la stessa azione.
            intent.removeExtra(SpendyQuickWidget.EXTRA_ACTION);
            intent.removeExtra(SpendyQuickWidget.EXTRA_CAT);
        } catch (Exception e) {
            // Un problema qui non deve impedire l'avvio dell'app.
        }
    }
}
