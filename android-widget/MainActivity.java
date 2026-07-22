package io.github.nataliziadario.spendy;

import android.os.Bundle;

import com.getcapacitor.BridgeActivity;

/**
 * Sostituisce la MainActivity generata da Capacitor.
 *
 * L'unica differenza rispetto a quella standard e' la registrazione del
 * plugin SpendyWidget, che DEVE avvenire PRIMA di super.onCreate(...).
 */
public class MainActivity extends BridgeActivity {

    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(SpendyWidgetPlugin.class);
        super.onCreate(savedInstanceState);
    }
}
