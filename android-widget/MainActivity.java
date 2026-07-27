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
 * Sul punto 3. Senza il plugin @capacitor/app, Capacitor non chiede niente
 * alla pagina quando si preme indietro: chiude direttamente l'activity, cioe'
 * l'app. Per questo il gesto di sistema usciva da Spendy invece di chiudere il
 * foglio aperto.
 *
 * Qui registriamo il nostro gestore, che CHIEDE ALLA PAGINA cosa fare
 * eseguendo window.spendyHandleBack(). Quella funzione chiude un livello e
 * risponde "1"; se non c'era niente da chiudere risponde "0" e allora si esce
 * davvero. Non ci si affida piu' alla cronologia del WebView, che in alcune
 * configurazioni non risulta navigabile: si chiede direttamente all'app.
 */
public class MainActivity extends BridgeActivity {

    /** Codice eseguito nella pagina: risponde "1" se ha chiuso qualcosa. */
    private static final String ASK_PAGE =
        "(function(){try{return (window.spendyHandleBack && window.spendyHandleBack())?'1':'0';}catch(e){return '0';}})()";

    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(SpendyWidgetPlugin.class);
        super.onCreate(savedInstanceState);
        stashWidgetAction(getIntent());
        installBackHandler();
    }

    /**
     * I gestori aggiunti dopo hanno la precedenza su quelli gia' registrati,
     * quindi questo viene consultato prima di quello standard di Capacitor.
     */
    private void installBackHandler() {
        getOnBackPressedDispatcher().addCallback(this, new OnBackPressedCallback(true) {
            @Override
            public void handleOnBackPressed() {
                final OnBackPressedCallback self = this;
                WebView found = null;
                try {
                    if (getBridge() != null) found = getBridge().getWebView();
                } catch (Exception e) {
                    found = null;
                }
                if (found == null) {
                    exitApp(self);
                    return;
                }
                final WebView webView = found;
                try {
                    webView.evaluateJavascript(ASK_PAGE, new ValueCallback<String>() {
                        @Override
                        public void onReceiveValue(String value) {
                            if (value != null && value.contains("1")) {
                                // La pagina ha chiuso un livello: restiamo dentro l'app.
                                return;
                            }
                            // Riserva: se la pagina non risponde ma ha una
                            // cronologia, torniamo indietro di una tappa.
                            if (webView.canGoBack()) {
                                webView.goBack();
                                return;
                            }
                            exitApp(self);
                        }
                    });
                } catch (Exception e) {
                    if (webView.canGoBack()) {
                        webView.goBack();
                    } else {
                        exitApp(self);
                    }
                }
            }
        });
    }

    /**
     * Uscita vera: si disattiva il nostro gestore e si lascia proseguire il
     * comportamento normale, altrimenti si entrerebbe in un ciclo infinito.
     */
    private void exitApp(OnBackPressedCallback callback) {
        callback.setEnabled(false);
        getOnBackPressedDispatcher().onBackPressed();
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
