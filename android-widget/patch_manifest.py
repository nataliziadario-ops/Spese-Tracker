#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dichiara i due widget nell'AndroidManifest.xml generato da Capacitor.

Il progetto android/ viene ricreato a ogni build, quindi questa modifica va
riapplicata ogni volta. Lo script e' idempotente: se i widget risultano gia'
dichiarati non fa nulla e non duplica niente.

Uso:  python3 android-widget/patch_manifest.py [percorso_manifest]
"""
import io
import sys

DEFAULT_MANIFEST = "android/app/src/main/AndroidManifest.xml"

RECEIVERS = """
        <!-- Widget Spendy: dichiarati automaticamente dal workflow di build. -->
        <receiver
            android:name=".SpendySimpleWidget"
            android:exported="false">
            <intent-filter>
                <action android:name="android.appwidget.action.APPWIDGET_UPDATE" />
            </intent-filter>
            <meta-data
                android:name="android.appwidget.provider"
                android:resource="@xml/widget_simple_info" />
        </receiver>

        <receiver
            android:name=".SpendyRichWidget"
            android:exported="false">
            <intent-filter>
                <action android:name="android.appwidget.action.APPWIDGET_UPDATE" />
            </intent-filter>
            <meta-data
                android:name="android.appwidget.provider"
                android:resource="@xml/widget_rich_info" />
        </receiver>

        <receiver
            android:name=".SpendyQuickWidget"
            android:exported="false">
            <intent-filter>
                <action android:name="android.appwidget.action.APPWIDGET_UPDATE" />
            </intent-filter>
            <meta-data
                android:name="android.appwidget.provider"
                android:resource="@xml/widget_quick_info" />
        </receiver>

"""


def patch(path):
    try:
        src = io.open(path, encoding="utf-8").read()
    except IOError:
        print("ERRORE: Manifest non trovato: %s" % path)
        return 1

    if "SpendySimpleWidget" in src and "SpendyRichWidget" in src and "SpendyQuickWidget" in src:
        print("Widget gia' dichiarati nel Manifest: nessuna modifica.")
        return 0

    if "</application>" not in src:
        print("ERRORE: tag </application> non trovato nel Manifest.")
        return 1

    out = src.replace("</application>", RECEIVERS + "    </application>", 1)
    io.open(path, "w", encoding="utf-8").write(out)
    print("Widget dichiarati nel Manifest: %s" % path)
    return 0


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MANIFEST
    sys.exit(patch(target))
