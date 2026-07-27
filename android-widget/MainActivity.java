package io.github.nataliziadario.spendy;

import android.content.Intent;
import android.os.Bundle;
import android.webkit.WebView;

import androidx.activity.OnBackPressedCallback;

import com.getcapacitor.BridgeActivity;

/**
 * Sostituisce la MainActivity generata da Capacitor.
 *
 * Fa due cose in piu' di quella standard:
 *  1. registra il plugin SpendyWidget (PRIMA di super.onCreate, come richiesto);
 *  2. se l'app e' stata aperta da un tasto del widget "spesa rapida", mette da
 *     parte l'azione richiesta, che la pagina web legge poi con consumeAction();
 *  3. gestisce il tasto/gesto INDIETRO di Android.
 *
 * Sul punto 3: senza il plugin @capacitor/app, Capacitor NON guarda la
 * cronologia del WebView quando si preme indietro: chiude direttamente
 * l'activity, cioe' l'app. Per questo il gesto "torna indietro" usciva da
 * Spendy invece di chiudere il foglio aperto. Qui registriamo il nostro
 * gestore: se la pagina ha una cronologia (la crea la parte web ogni volta
 * che apre un foglio, una finestrella o una pagina) si torna indietro di un
 * passo; solo quando non c'e' piu' niente da chiudere si esce davvero.
 */
public class MainActivity extends BridgeActivity {

    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(SpendyWidgetPlugin.class);
        super.onCreate(savedInstanceState);
        stashWidgetAction(getIntent());
        installBackHandler();
    }

    /**
     * I gestori aggiunti dopo hanno la precedenza su quelli gia' presenti,
     * quindi questo viene consultato prima di quello standard di Capacitor.
     */
    private void installBackHandler() {
        getOnBackPressedDispatcher().addCallback(this, new OnBackPressedCallback(true) {
            @Override
            public void handleOnBackPressed() {
                WebView webView = null;
                try {
                    if (getBridge() != null) webView = getBridge().getWebView();
                } catch (Exception e) {
                    webView = null;
                }
                if (webView != null && webView.canGoBack()) {
                    // C'e' ancora qualcosa da chiudere dentro la pagina.
                    webView.goBack();
                    return;
                }
                // Niente da chiudere: lasciamo fare al comportamento normale
                // (cioe' uscire dall'app), disattivando prima questo gestore
                // per non entrare in un ciclo infinito.
                setEnabled(false);
                getOnBackPressedDispatcher().onBackPressed();
            }
        });
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
