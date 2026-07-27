package io.github.nataliziadario.spendy;

import android.content.Intent;
import android.os.Bundle;
import android.webkit.ValueCallback;
import android.webkit.WebView;

import androidx.activity.OnBackPressedCallback;

import com.getcapacitor.BridgeActivity;

/**
 * Sostituisce la MainActivity generata da Capacitor.
 *
 * Fa tre cose in piu' di quella standard:
 *  1. registra il plugin SpendyWidget (PRIMA di super.onCreate, come richiesto);
 *  2. se l'app e' stata aperta da un tasto del widget "spesa rapida", mette da
 *     parte l'azione richiesta, che la pagina web legge poi con consumeAction();
 *  3. gestisce il tasto e il gesto INDIETRO di Android.
 *
 * Sul punto 3. Senza il plugin @capacitor/app, Capacitor non chiede niente alla
 * pagina quando si preme indietro: chiude direttamente l'app. Qui invece
 * CHIEDIAMO ALLA PAGINA cosa fare, eseguendo window.spendyHandleBack():
 * risponde "1" se ha chiuso un livello (e allora restiamo dentro), "0" se non
 * c'era niente da chiudere (e allora si esce davvero).
 *
 * Attenzione a DOVE si registra il gestore. Android consulta i gestori
 * dall'ultimo registrato al primo. Registrandolo una sola volta all'avvio, al
 * ritorno da un'altra app il gestore di Capacitor finiva davanti al nostro e
 * l'app tornava a chiudersi: e' il motivo per cui prima funzionava solo alla
 * prima apertura. Per questo lo registriamo di nuovo a OGNI ritorno in primo
 * piano (onResume), togliendo prima quello vecchio: cosi' il nostro e' sempre
 * l'ultimo, quindi sempre il primo a essere consultato.
 */
public class MainActivity extends BridgeActivity {

    /** Codice eseguito dentro la pagina: risponde "1" se ha chiuso qualcosa. */
    private static final String ASK_PAGE =
        "(function(){try{return (window.spendyHandleBack && window.spendyHandleBack())?'1':'0';}catch(e){return '0';}})()";

    private OnBackPressedCallback backCallback;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(SpendyWidgetPlugin.class);
        super.onCreate(savedInstanceState);
        stashWidgetAction(getIntent());
        installBackHandler();
    }

    @Override
    public void onResume() {
        super.onResume();
        // Rimette il nostro gestore in cima alla pila a ogni ritorno nell'app.
        installBackHandler();
    }

    private void installBackHandler() {
        try {
            if (backCallback != null) {
                backCallback.remove();
                backCallback = null;
            }
            backCallback = new OnBackPressedCallback(true) {
                @Override
                public void handleOnBackPressed() {
                    handleBack();
                }
            };
            // Senza LifecycleOwner: la gestiamo noi in onResume, cosi' nessuno
            // puo' toglierla o rimetterla in coda a nostra insaputa.
            getOnBackPressedDispatcher().addCallback(backCallback);
        } catch (Exception e) {
            // Se qualcosa va storto resta il comportamento standard.
        }
    }

    private void handleBack() {
        WebView found = null;
        try {
            if (getBridge() != null) found = getBridge().getWebView();
        } catch (Exception e) {
            found = null;
        }
        if (found == null) {
            exitApp();
            return;
        }
        final WebView webView = found;
        try {
            webView.evaluateJavascript(ASK_PAGE, new ValueCallback<String>() {
                @Override
                public void onReceiveValue(String value) {
                    if (value != null && value.contains("1")) {
                        // La pagina ha chiuso un livello: restiamo nell'app.
                        return;
                    }
                    // Riserva: se la pagina non risponde ma ha una cronologia,
                    // torniamo indietro di una tappa.
                    if (webView.canGoBack()) {
                        webView.goBack();
                        return;
                    }
                    exitApp();
                }
            });
        } catch (Exception e) {
            if (webView.canGoBack()) {
                webView.goBack();
            } else {
                exitApp();
            }
        }
    }

    /**
     * Uscita vera dall'app. Si chiude direttamente l'activity invece di
     * disattivare il gestore e ripassare la palla: disattivarlo lo avrebbe
     * messo fuori gioco anche per le volte successive.
     */
    private void exitApp() {
        try {
            finish();
        } catch (Exception e) {
            // Nulla da fare: meglio non chiudere che schiantarsi.
        }
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
